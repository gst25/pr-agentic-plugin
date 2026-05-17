"""
Agents package — Re-exports all agent definitions and the registry.
"""

from core.agents.project_manager import PROJECT_MANAGER
from core.agents.tech_lead import TECH_LEAD
from core.agents.developer import DEVELOPER
from core.agents.tester import TESTER
from core.agents.release_engineer import RELEASE_ENGINEER
from core.base_agent import AgentDefinition

# Registry of all agents for easy lookup by role
AGENT_REGISTRY = {
    "project_manager": PROJECT_MANAGER,
    "tech_lead": TECH_LEAD,
    "developer": DEVELOPER,
    "tester": TESTER,
    "release_engineer": RELEASE_ENGINEER,
}
