"""
Tools package — Each tool is in its own file.
This __init__ re-exports everything for convenience.
"""

from tools.git_branch import GIT_BRANCH_MAP, GIT_BRANCH_TOOL, git_create_branch
from tools.git_commit import (GIT_COMMIT_MAP, GIT_COMMIT_TOOL,
                              git_add_and_commit)
from tools.git_pr import GIT_PR_MAP, GIT_PR_TOOL, create_pull_request
from tools.git_push import GIT_PUSH_MAP, GIT_PUSH_TOOL, git_push
from tools.list_directory import (LIST_DIRECTORY_MAP, LIST_DIRECTORY_TOOL,
                                  list_directory)
from tools.read_file import READ_FILE_MAP, READ_FILE_TOOL, read_file
from tools.run_command import RUN_COMMAND_MAP, RUN_COMMAND_TOOL, run_command
from tools.write_file import WRITE_FILE_MAP, WRITE_FILE_TOOL, write_file

# Grouped collections for easy assignment to agents
FILE_TOOLS = [LIST_DIRECTORY_TOOL, READ_FILE_TOOL, WRITE_FILE_TOOL]
FILE_TOOL_MAP = {**LIST_DIRECTORY_MAP, **READ_FILE_MAP, **WRITE_FILE_MAP}

TERMINAL_TOOLS = [RUN_COMMAND_TOOL]
TERMINAL_TOOL_MAP = {**RUN_COMMAND_MAP}

GIT_TOOLS = [GIT_BRANCH_TOOL, GIT_COMMIT_TOOL, GIT_PUSH_TOOL, GIT_PR_TOOL]
GIT_TOOL_MAP = {**GIT_BRANCH_MAP, **GIT_COMMIT_MAP, **GIT_PUSH_MAP, **GIT_PR_MAP}
