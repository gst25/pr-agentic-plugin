"""
agentic init — Scaffolds the .agentic/ configuration directory into a target repo.

This is the "installation" step. When a user runs `agentic init` inside their repo,
it creates the .agentic/ folder with template config files they can customize.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

# ── Template: config.yaml ──────────────────────

CONFIG_YAML_TEMPLATE = """\
# ============================================
# Agentic Plugin — Project Configuration
# ============================================
# This file configures the AI agents for YOUR repository.
# All values here override environment variables.

# --- API Keys ---
# You can set these here OR as environment variables.
# Environment variables take lower priority than this file.
# TIP: Add .agentic/config.yaml to .gitignore to keep keys out of version control.
api_keys:
  openai: ""        # or set OPENAI_API_KEY env var
  anthropic: ""     # or set ANTHROPIC_API_KEY env var
  google: ""        # or set GOOGLE_API_KEY env var

# --- GitHub ---
github:
  token: ""          # or set GITHUB_TOKEN env var (needs repo, project permissions)
  repo: "{repo_name}"  # owner/repo format

# --- Ralph Loop (Execution Engine) ---
ralph_loop:
  max_iterations: 7              # Max retries per agent before escalating to human
  max_dev_tester_cycles: 3       # Max Developer↔Tester feedback loops per ticket
"""

# ── Template: models.yaml ──────────────────────

MODELS_YAML_TEMPLATE = """\
# ============================================
# Agentic Plugin — Model Configuration
# ============================================
# Assign a specific LLM provider and model to each agent.
# This lets you use powerful models for coding and cheaper ones for simple tasks.
#
# Supported providers: openai, anthropic, google, ollama
#
# Supported models (examples):
#   openai:    gpt-4o, gpt-4o-mini, gpt-4-turbo
#   anthropic: claude-sonnet-4-20250514, claude-3-5-haiku-20241022
#   google:    gemini-2.5-pro, gemini-2.5-flash
#   ollama:    llama3, codellama, deepseek-coder (requires local Ollama)

project_manager:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.3
  max_tokens: 4096

tech_lead:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.2
  max_tokens: 4096

developer:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.1
  max_tokens: 8192

tester:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.2
  max_tokens: 4096

release_engineer:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 2048
"""

# ── Template: AGENT_CONTEXT.md ─────────────────

AGENT_CONTEXT_TEMPLATE = """\
# AGENT_CONTEXT.md — Repository Onboarding for AI Agents

> This file teaches AI agents how to work in YOUR repository.
> Fill in the sections below with your project's specific details.
> The more detail you provide, the better the agents will perform.

## Project Overview
- **Name:** [Your Project Name]
- **Language:** [e.g., Java 17, Python 3.12, TypeScript 5.x]
- **Framework:** [e.g., Spring Boot 3.x, FastAPI, Next.js 14]
- **Build Tool:** [e.g., Maven, Gradle, npm, pip]
- **Database:** [e.g., PostgreSQL, MongoDB, SQLite]

## Build & Test Commands
```bash
# Compile / build the project
[e.g., mvn clean compile]

# Run all tests
[e.g., mvn test]

# Run a specific test
[e.g., mvn test -Dtest=ClassName]

# Start the application locally
[e.g., mvn spring-boot:run]
```

## Project Structure
```
[Describe your folder layout here, for example:]
src/
├── main/java/com/example/
│   ├── controllers/    # REST controllers
│   ├── services/       # Business logic
│   ├── repositories/   # Data access
│   ├── models/         # Domain entities
│   └── dto/            # Request/Response DTOs
└── test/java/com/example/
    └── ...             # Test mirrors of above
```

## Coding Standards & Rules
1. [e.g., Use constructor injection, not field injection]
2. [e.g., Never return JPA entities directly, always use DTOs]
3. [e.g., Use SLF4J for logging, never System.out.println]
4. [e.g., All public methods must have Javadoc comments]

## Dependencies Already Available
- [e.g., Spring Web, Spring Data JPA, Lombok]
- [e.g., JUnit 5, Mockito]

## Things to Avoid
- [e.g., Do not use var keyword in Java]
- [e.g., Do not add new dependencies without approval]
"""

# ── Template: .gitignore addition ──────────────

GITIGNORE_ADDITION = """\

# Agentic Plugin — keep API keys out of version control
.agentic/config.yaml
"""


def init_agentic(repo_path: str):
    """
    Scaffold the .agentic/ directory in the target repo.
    Creates template config files that the user can customize.
    """
    repo = Path(repo_path).resolve()
    agentic_dir = repo / ".agentic"

    if agentic_dir.exists():
        console.print(
            f"[yellow]⚠️  .agentic/ already exists in {repo}. Skipping init.[/yellow]"
        )
        console.print("[dim]Delete .agentic/ and run init again to regenerate.[/dim]")
        return

    # Try to detect repo name from git remote
    repo_name = _detect_repo_name(repo) or "owner/repo-name"

    # Create .agentic/ directory
    agentic_dir.mkdir(parents=True, exist_ok=True)

    # Write config.yaml
    config_path = agentic_dir / "config.yaml"
    config_path.write_text(
        CONFIG_YAML_TEMPLATE.format(repo_name=repo_name), encoding="utf-8"
    )

    # Write models.yaml
    models_path = agentic_dir / "models.yaml"
    models_path.write_text(MODELS_YAML_TEMPLATE, encoding="utf-8")

    # Write AGENT_CONTEXT.md
    context_path = agentic_dir / "AGENT_CONTEXT.md"
    context_path.write_text(AGENT_CONTEXT_TEMPLATE, encoding="utf-8")

    # Add config.yaml to .gitignore (it contains API keys)
    gitignore_path = repo / ".gitignore"
    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding="utf-8")
        if ".agentic/config.yaml" not in existing:
            with open(gitignore_path, "a") as f:
                f.write(GITIGNORE_ADDITION)
    else:
        gitignore_path.write_text(GITIGNORE_ADDITION.strip() + "\n", encoding="utf-8")

    # Print success
    console.print(
        Panel(
            "[bold green]✅ Agentic Plugin initialized![/bold green]\n\n"
            f"Created in: [cyan]{agentic_dir}[/cyan]\n\n"
            "Files created:\n"
            f"  📄 .agentic/config.yaml      — API keys & GitHub settings\n"
            f"  📄 .agentic/models.yaml      — LLM model per agent\n"
            f"  📄 .agentic/AGENT_CONTEXT.md  — Your repo's coding rules\n\n"
            "[bold]Next steps:[/bold]\n"
            "  1. Fill in your API keys in .agentic/config.yaml\n"
            "  2. Choose your models in .agentic/models.yaml\n"
            "  3. Describe your repo in .agentic/AGENT_CONTEXT.md\n"
            "  4. Run: [cyan]agentic run --prd path/to/prd.md[/cyan]",
            style="green",
        )
    )


def _detect_repo_name(repo: Path) -> str | None:
    """Try to extract owner/repo from the git remote URL."""
    try:
        import git

        r = git.Repo(repo)
        remote_url = r.remotes.origin.url
        # Handle both HTTPS and SSH formats
        # https://github.com/owner/repo.git -> owner/repo
        # git@github.com:owner/repo.git    -> owner/repo
        if "github.com" in remote_url:
            parts = remote_url.rstrip(".git").split("github.com")[-1]
            parts = parts.lstrip(":/")
            return parts
    except Exception:
        pass
    return None
