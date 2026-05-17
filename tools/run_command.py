"""
Tool: run_command
Executes shell commands with safety guardrails (blocked commands, timeouts, truncation).
"""

import subprocess


BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf ~", "sudo", "curl", "wget",
    "ssh", "scp", "format", "mkfs", "dd if=", ":(){",
]


def run_command(command: str, cwd: str = ".", timeout: int = 120) -> str:
    """Execute a shell command in the project directory. Returns stdout + stderr."""
    cmd_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return f"BLOCKED: Command '{command}' is not allowed for safety reasons."

    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=timeout,
        )

        output_parts = []
        if result.stdout:
            output_parts.append(f"=== STDOUT ===\n{result.stdout.strip()}")
        if result.stderr:
            output_parts.append(f"=== STDERR ===\n{result.stderr.strip()}")

        exit_info = f"Exit Code: {result.returncode} ({'SUCCESS' if result.returncode == 0 else 'FAILED'})"
        output_parts.append(exit_info)
        full_output = "\n\n".join(output_parts)

        max_chars = 8000
        if len(full_output) > max_chars:
            full_output = full_output[:max_chars] + "\n\n... [OUTPUT TRUNCATED] ..."

        return full_output
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: Command '{command}' exceeded {timeout}s limit."
    except Exception as e:
        return f"ERROR running command: {e}"


# --- LLM Tool Schema ---
RUN_COMMAND_TOOL = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Run a shell command in the project directory. "
            "Use this to compile (e.g., 'mvn clean compile'), run tests (e.g., 'pytest'), "
            "or check project status. Do NOT use for destructive operations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                }
            },
            "required": ["command"],
        },
    },
}

RUN_COMMAND_MAP = {"run_command": run_command}
