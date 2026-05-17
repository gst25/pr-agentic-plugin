"""
Tool: create_pull_request
Creates a Pull Request on GitHub via the API.
"""

from github import Github, GithubException
from config import Config


def create_pull_request(title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
    """Create a Pull Request on the configured GitHub repository."""
    try:
        gh = Github(Config.GITHUB_TOKEN)
        repo = gh.get_repo(Config.GITHUB_REPO)
        pr = repo.create_pull(
            title=title, body=body,
            head=head_branch, base=base_branch,
        )
        return f"SUCCESS: Pull Request created! URL: {pr.html_url}"
    except GithubException as e:
        return f"ERROR creating PR: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"ERROR: {e}"


# --- LLM Tool Schema ---
GIT_PR_TOOL = {
    "type": "function",
    "function": {
        "name": "create_pull_request",
        "description": "Create a Pull Request on GitHub linking the feature branch to the base branch.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "PR title."},
                "body": {"type": "string", "description": "PR body/description in Markdown."},
                "head_branch": {"type": "string", "description": "The feature branch name."},
                "base_branch": {
                    "type": "string",
                    "description": "The target branch to merge into (default: 'main').",
                    "default": "main",
                },
            },
            "required": ["title", "body", "head_branch"],
        },
    },
}

GIT_PR_MAP = {"create_pull_request": create_pull_request}
