"""
Tool: write_file
Writes content to a file, creating parent directories if needed.
"""

from pathlib import Path


def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates parent dirs if needed. Overwrites if exists."""
    try:
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"SUCCESS: File '{file_path}' written ({len(content)} chars)."
    except Exception as e:
        return f"ERROR writing file: {e}"


# --- LLM Tool Schema ---
WRITE_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file. Creates the file and parent directories if they don't exist. Overwrites if the file already exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "The full content to write to the file.",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}

WRITE_FILE_MAP = {"write_file": write_file}
