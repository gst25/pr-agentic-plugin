"""
LLM Client Factory — Creates the right LLM client based on models.yaml config.

Supports multiple providers (OpenAI, Anthropic, Google, Ollama) so each agent
can use a different model. The factory reads models.yaml and returns a
configured client + model name for any given agent role.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ModelConfig:
    """Configuration for a single agent's LLM."""

    provider: str
    model: str
    temperature: float
    max_tokens: int


def load_model_configs(config_path: str = "models.yaml") -> dict[str, ModelConfig]:
    """
    Load the models.yaml file and return a dict of agent_role -> ModelConfig.
    Falls back to defaults if the file doesn't exist.
    """
    path = Path(config_path)
    if not path.exists():
        # Default: use gpt-4o for everything
        default = ModelConfig(
            provider="openai", model="gpt-4o", temperature=0.2, max_tokens=4096
        )
        return {
            "project_manager": default,
            "tech_lead": default,
            "developer": default,
            "tester": default,
            "release_engineer": default,
        }

    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    configs = {}
    for role, settings in raw.items():
        configs[role] = ModelConfig(
            provider=settings.get("provider", "openai"),
            model=settings.get("model", "gpt-4o"),
            temperature=settings.get("temperature", 0.2),
            max_tokens=settings.get("max_tokens", 4096),
        )
    return configs


def get_llm_client(provider: str):
    """
    Return an LLM client for the given provider.
    Each provider has a different SDK, so we abstract that here.
    """
    if provider == "openai":
        from openai import OpenAI

        return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    elif provider == "anthropic":
        try:
            from anthropic import Anthropic

            return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")

    elif provider == "google":
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))
            return genai
        except ImportError:
            raise ImportError(
                "Install google-generativeai: pip install google-generativeai"
            )

    elif provider == "ollama":
        # Ollama uses the OpenAI-compatible API
        from openai import OpenAI

        return OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",  # Ollama doesn't need a real key
        )

    else:
        raise ValueError(
            f"Unknown provider: '{provider}'. Supported: openai, anthropic, google, ollama"
        )
