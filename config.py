"""
Configuration Resolver — Finds and loads config from the TARGET REPO, not from the plugin.

The plugin is agnostic. All configuration lives in the repo that installs it.
When a user runs `agentic init`, config files are scaffolded into their repo.
When a user runs `agentic run`, the plugin looks for config in their repo.

Config files the plugin looks for (in the target repo root):
  .agentic/
  ├── models.yaml          # Which LLM to use for each agent
  ├── config.yaml          # API keys, GitHub settings, ralph loop limits
  └── AGENT_CONTEXT.md     # Repo-specific coding rules (optional but recommended)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


AGENTIC_DIR = ".agentic"
MODELS_FILE = "models.yaml"
CONFIG_FILE = "config.yaml"
AGENT_CONTEXT_FILE = "AGENT_CONTEXT.md"


@dataclass
class ModelConfig:
    """LLM configuration for a single agent."""
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.2
    max_tokens: int = 4096


@dataclass
class PluginConfig:
    """All configuration for a plugin run, resolved from the target repo."""
    # API Keys (from config.yaml or environment variables)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # GitHub
    github_token: str = ""
    github_repo: str = ""  # owner/repo

    # Ralph Loop
    max_ralph_iterations: int = 7
    max_dev_tester_cycles: int = 3

    # Per-agent model configs
    models: dict[str, ModelConfig] = field(default_factory=dict)

    # Repo context
    agent_context: str = ""

    # Resolved paths
    repo_path: str = ""


def resolve_config(repo_path: str) -> PluginConfig:
    """
    Resolve all plugin configuration from the target repository.

    Lookup order for each setting:
    1. .agentic/config.yaml in the repo (highest priority)
    2. Environment variables (fallback)
    3. Defaults (lowest priority)
    """
    repo = Path(repo_path).resolve()
    agentic_dir = repo / AGENTIC_DIR
    config = PluginConfig(repo_path=str(repo))

    # --- Load .agentic/config.yaml ---
    config_file = agentic_dir / CONFIG_FILE
    if config_file.exists():
        with open(config_file, "r") as f:
            raw = yaml.safe_load(f) or {}

        api_keys = raw.get("api_keys", {})
        github = raw.get("github", {})
        ralph = raw.get("ralph_loop", {})

        config.openai_api_key = api_keys.get("openai", os.getenv("OPENAI_API_KEY", ""))
        config.anthropic_api_key = api_keys.get("anthropic", os.getenv("ANTHROPIC_API_KEY", ""))
        config.google_api_key = api_keys.get("google", os.getenv("GOOGLE_API_KEY", ""))
        config.github_token = github.get("token", os.getenv("GITHUB_TOKEN", ""))
        config.github_repo = github.get("repo", os.getenv("GITHUB_REPO", ""))
        config.max_ralph_iterations = ralph.get("max_iterations", 7)
        config.max_dev_tester_cycles = ralph.get("max_dev_tester_cycles", 3)
    else:
        # Fall back to environment variables
        load_dotenv()
        config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        config.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        config.github_token = os.getenv("GITHUB_TOKEN", "")
        config.github_repo = os.getenv("GITHUB_REPO", "")

    # --- Load .agentic/models.yaml ---
    models_file = agentic_dir / MODELS_FILE
    if models_file.exists():
        with open(models_file, "r") as f:
            raw_models = yaml.safe_load(f) or {}
        for role, settings in raw_models.items():
            config.models[role] = ModelConfig(
                provider=settings.get("provider", "openai"),
                model=settings.get("model", "gpt-4o"),
                temperature=settings.get("temperature", 0.2),
                max_tokens=settings.get("max_tokens", 4096),
            )
    else:
        # Defaults: GPT-4o for all agents
        default = ModelConfig()
        for role in ["project_manager", "tech_lead", "developer", "tester", "release_engineer"]:
            config.models[role] = default

    # --- Load AGENT_CONTEXT.md ---
    context_file = agentic_dir / AGENT_CONTEXT_FILE
    if context_file.exists():
        config.agent_context = context_file.read_text(encoding="utf-8")
    else:
        # Also check repo root (legacy/convenience location)
        root_context = repo / AGENT_CONTEXT_FILE
        if root_context.exists():
            config.agent_context = root_context.read_text(encoding="utf-8")
        else:
            config.agent_context = "No AGENT_CONTEXT.md found. Infer conventions from the codebase."

    return config


def validate_config(config: PluginConfig) -> list[str]:
    """Validate that the resolved config has all required fields."""
    errors = []
    if not config.github_token:
        errors.append("GitHub token not set. Add to .agentic/config.yaml or set GITHUB_TOKEN env var.")
    if not config.github_repo:
        errors.append("GitHub repo not set. Add to .agentic/config.yaml or set GITHUB_REPO env var.")

    # Check that at least one LLM provider key is set
    has_any_key = any([config.openai_api_key, config.anthropic_api_key, config.google_api_key])
    if not has_any_key:
        errors.append("No LLM API key found. Set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY.")

    return errors
