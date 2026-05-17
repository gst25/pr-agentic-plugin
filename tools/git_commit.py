"""
Tool: git_add_and_commit
Stages all changes and creates a commit.
"""

import git


def git_add_and_commit(repo_path: str, message: str) -> str:
    """Stage all changes (git add -A) and commit with a message."""
    try:
        repo = git.Repo(repo_path)
        repo.git.add(A=True)
        if not repo.is_dirty(untracked_files=True):
            return "INFO: No changes to commit."
        repo.index.commit(message)
        return f"SUCCESS: Committed with message: '{message}'"
    except Exception as e:
        return f"ERROR committing: {e}"


# --- LLM Tool Schema ---
GIT_COMMIT_TOOL = {
    "type": "function",
    "function": {
        "name": "git_add_and_commit",
        "description": "Stage all changes (git add -A) and commit with a message.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The commit message.",
                }
            },
            "required": ["message"],
        },
    },
}

GIT_COMMIT_MAP = {"git_add_and_commit": git_add_and_commit}
