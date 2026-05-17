"""
Tools package — Each tool is in its own file.
This __init__ re-exports everything for convenience.
"""

from tools.list_directory import list_directory, LIST_DIRECTORY_TOOL, LIST_DIRECTORY_MAP
from tools.read_file import read_file, READ_FILE_TOOL, READ_FILE_MAP
from tools.write_file import write_file, WRITE_FILE_TOOL, WRITE_FILE_MAP
from tools.run_command import run_command, RUN_COMMAND_TOOL, RUN_COMMAND_MAP
from tools.git_branch import git_create_branch, GIT_BRANCH_TOOL, GIT_BRANCH_MAP
from tools.git_commit import git_add_and_commit, GIT_COMMIT_TOOL, GIT_COMMIT_MAP
from tools.git_push import git_push, GIT_PUSH_TOOL, GIT_PUSH_MAP
from tools.git_pr import create_pull_request, GIT_PR_TOOL, GIT_PR_MAP

# Grouped collections for easy assignment to agents
FILE_TOOLS = [LIST_DIRECTORY_TOOL, READ_FILE_TOOL, WRITE_FILE_TOOL]
FILE_TOOL_MAP = {**LIST_DIRECTORY_MAP, **READ_FILE_MAP, **WRITE_FILE_MAP}

TERMINAL_TOOLS = [RUN_COMMAND_TOOL]
TERMINAL_TOOL_MAP = {**RUN_COMMAND_MAP}

GIT_TOOLS = [GIT_BRANCH_TOOL, GIT_COMMIT_TOOL, GIT_PUSH_TOOL, GIT_PR_TOOL]
GIT_TOOL_MAP = {**GIT_BRANCH_MAP, **GIT_COMMIT_MAP, **GIT_PUSH_MAP, **GIT_PR_MAP}
