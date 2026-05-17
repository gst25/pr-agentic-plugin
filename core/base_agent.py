"""
Base Agent Definition.
All agent files import this dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentDefinition:
    """Defines an agent's identity, tools, and behavior."""
    name: str
    role: str          # Must match the key in models.yaml
    system_prompt: str
    tools: list[dict] = field(default_factory=list)
    tool_map: dict = field(default_factory=dict)
