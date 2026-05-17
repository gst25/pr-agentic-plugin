"""
Tool: git_create_branch
Creates and checks out a new Git branch.
"""

import git


def git_create_branch(repo_path: str, branch_name: str) -> str:
    """Create and checkout a new branch from the current HEAD."""
    try:
        repo = git.Repo(repo_path)
        default_branch = repo.active_branch.name
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        return f"SUCCESS: Created and checked out branch '{branch_name}' (from '{default_branch}')."
    except git.exc.GitCommandError as e:
        return f"ERROR creating branch: {e}"
    except Exception as e:
        return f"ERROR: {e}"


# --- LLM Tool Schema ---
GIT_BRANCH_TOOL = {
    "type": "function",
    "function": {
        "name": "git_create_branch",
        "description": "Create and checkout a new Git branch from the current HEAD.",
        "parameters": {
            "type": "object",
            "properties": {
                "branch_name": {
                    "type": "string",
                    "description": "Name of the new branch (e.g., 'feat/forgot-password').",
                }
            },
            "required": ["branch_name"],
        },
    },
}

GIT_BRANCH_MAP = {"git_create_branch": git_create_branch}
