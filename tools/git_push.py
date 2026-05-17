"""
Tool: git_push
Pushes the current branch to the remote origin.
"""

import git


def git_push(repo_path: str) -> str:
    """Push the current branch to the remote origin."""
    try:
        repo = git.Repo(repo_path)
        branch = repo.active_branch.name
        origin = repo.remote(name="origin")
        origin.push(branch)
        return f"SUCCESS: Pushed branch '{branch}' to origin."
    except Exception as e:
        return f"ERROR pushing: {e}"


# --- LLM Tool Schema ---
GIT_PUSH_TOOL = {
    "type": "function",
    "function": {
        "name": "git_push",
        "description": "Push the current branch to the remote origin.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

GIT_PUSH_MAP = {"git_push": git_push}
