"""
The Ralph Loop Engine — Fully agnostic. Config is injected, not imported.

Each agent can use a different LLM provider/model as defined in the
injected PluginConfig (which was resolved from the target repo's .agentic/ directory).
"""

from __future__ import annotations

import json
import os

from rich.console import Console
from rich.panel import Panel

from core.base_agent import AgentDefinition
from core.llm_client import get_llm_client, ModelConfig

console = Console()


class RalphLoop:
    """
    Executes an agent inside an iterative loop.
    Config is INJECTED (not read from a global), making the engine fully agnostic.
    """

    def __init__(self, agent: AgentDefinition, repo_path: str, config, context: str = ""):
        """
        Args:
            agent: The agent definition (persona + tools).
            repo_path: Absolute path to the target repository.
            config: PluginConfig resolved from the target repo.
            context: AGENT_CONTEXT.md content.
        """
        self.agent = agent
        self.repo_path = repo_path
        self.context = context

        # Get THIS agent's model config from the injected config
        self.model_config: ModelConfig = config.models.get(
            agent.role,
            ModelConfig(provider="openai", model="gpt-4o", temperature=0.2, max_tokens=4096),
        )

        # Set the API key for the provider in the environment
        # (SDKs read from env vars)
        if self.model_config.provider == "openai":
            os.environ["OPENAI_API_KEY"] = config.openai_api_key
        elif self.model_config.provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key
        elif self.model_config.provider == "google":
            os.environ["GOOGLE_API_KEY"] = config.google_api_key

        self.client = get_llm_client(self.model_config.provider)
        self.max_iterations = config.max_ralph_iterations

    def run(self, task_prompt: str) -> str:
        """Run the agent in a Ralph Loop until it signals completion."""
        console.print(Panel(
            f"[bold]🚀 Starting {self.agent.name}[/bold]\n"
            f"Model: [cyan]{self.model_config.provider}/{self.model_config.model}[/cyan]\n"
            f"Max iterations: {self.max_iterations}",
            style="cyan",
        ))

        for iteration in range(1, self.max_iterations + 1):
            console.print(f"\n[bold yellow]── Iteration {iteration}/{self.max_iterations} ──[/bold yellow]")

            result = self._execute_single_iteration(task_prompt, iteration)

            if self._is_complete(result):
                console.print(Panel(
                    f"[bold green]✅ {self.agent.name} completed in {iteration} iteration(s).[/bold green]",
                    style="green",
                ))
                return result

            console.print(f"[dim]Agent has not signaled completion. Continuing loop...[/dim]")

        console.print(Panel(
            f"[bold red]⚠️ {self.agent.name} hit max iterations ({self.max_iterations}). "
            f"Stopping and escalating to human.[/bold red]",
            style="red",
        ))
        return f"MAX_ITERATIONS_REACHED: {self.agent.name} could not complete the task."

    def _execute_single_iteration(self, task_prompt: str, iteration: int) -> str:
        """Execute one iteration with a fresh context."""
        messages = [
            {"role": "system", "content": self.agent.system_prompt},
            {
                "role": "user",
                "content": (
                    f"## Repository Context\n{self.context}\n\n"
                    f"## Your Task\n{task_prompt}\n\n"
                    f"## Current Iteration\n"
                    f"This is iteration {iteration} of {self.max_iterations}. "
                    f"If you have been given previous error output, focus on fixing that specific error."
                ),
            },
        ]

        max_tool_rounds = 15
        for tool_round in range(max_tool_rounds):
            response = self._call_llm(messages)
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    console.print(
                        f"  🔧 [cyan]{func_name}[/cyan]"
                        f"({', '.join(f'{k}={repr(v)[:60]}' for k, v in func_args.items())})"
                    )

                    tool_result = self._execute_tool(func_name, func_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    })

                    display_result = str(tool_result)[:200]
                    console.print(f"    → {display_result}")
            else:
                final_text = choice.message.content or ""
                console.print(f"\n  💬 [bold]{self.agent.name}:[/bold] {final_text[:300]}")
                return final_text

        return "MAX_TOOL_ROUNDS_REACHED"

    def _call_llm(self, messages: list[dict]):
        """Call the LLM using the correct provider SDK."""
        kwargs = {
            "model": self.model_config.model,
            "messages": messages,
            "temperature": self.model_config.temperature,
            "max_tokens": self.model_config.max_tokens,
        }
        if self.agent.tools:
            kwargs["tools"] = self.agent.tools

        if self.model_config.provider in ("openai", "ollama"):
            return self.client.chat.completions.create(**kwargs)
        elif self.model_config.provider == "anthropic":
            return self._call_anthropic(messages)
        else:
            return self.client.chat.completions.create(**kwargs)

    def _call_anthropic(self, messages: list[dict]):
        """Adapter for Anthropic's API."""
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        anthropic_tools = []
        for tool in self.agent.tools:
            func = tool["function"]
            anthropic_tools.append({
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"],
            })

        kwargs = {
            "model": self.model_config.model,
            "system": system_msg,
            "messages": user_messages,
            "max_tokens": self.model_config.max_tokens,
            "temperature": self.model_config.temperature,
        }
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = self.client.messages.create(**kwargs)
        return self._adapt_anthropic_response(response)

    def _adapt_anthropic_response(self, response):
        """Convert Anthropic response to OpenAI-like structure."""
        from types import SimpleNamespace

        text_content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_content = block.text
            elif block.type == "tool_use":
                tool_calls.append(SimpleNamespace(
                    id=block.id,
                    function=SimpleNamespace(
                        name=block.name,
                        arguments=json.dumps(block.input),
                    ),
                ))

        message = SimpleNamespace(
            content=text_content,
            tool_calls=tool_calls if tool_calls else None,
        )
        choice = SimpleNamespace(
            message=message,
            finish_reason="tool_calls" if tool_calls else "stop",
        )
        return SimpleNamespace(choices=[choice])

    def _execute_tool(self, func_name: str, func_args: dict) -> str:
        """Execute a tool, injecting repo_path where needed."""
        if func_name not in self.agent.tool_map:
            return f"ERROR: Unknown tool '{func_name}'"

        if func_name == "run_command":
            func_args["cwd"] = self.repo_path
        elif func_name == "list_directory":
            if func_args.get("path", ".") == ".":
                func_args["path"] = self.repo_path
            else:
                func_args["path"] = os.path.join(self.repo_path, func_args["path"])
        elif func_name in ("read_file", "write_file"):
            path_key = "file_path"
            if path_key in func_args and not os.path.isabs(func_args[path_key]):
                func_args[path_key] = os.path.join(self.repo_path, func_args[path_key])

        return self.agent.tool_map[func_name](**func_args)

    def _is_complete(self, result: str) -> bool:
        """Check if the agent's output signals completion."""
        completion_signals = [
            "BUILD_SUCCESS", "TESTS_PASSED", "CODE_BUG:",
            "BUILD_FAILED:", "MAX_ITERATIONS_REACHED",
            "MAX_TOOL_ROUNDS_REACHED", "PR created", "Pull Request created",
        ]
        return any(signal.lower() in result.lower() for signal in completion_signals)
