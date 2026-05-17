"""
Tool: list_directory
Lists all files and subdirectories at a given path.
"""

from pathlib import Path


def list_directory(path: str = ".") -> str:
    """List all files and directories at the given path."""
    try:
        result_lines = []
        base = Path(path).resolve()

        for item in sorted(base.iterdir()):
            if item.name.startswith("."):
                continue
            prefix = "📁 " if item.is_dir() else "📄 "
            size = ""
            if item.is_file():
                size_bytes = item.stat().st_size
                if size_bytes < 1024:
                    size = f" ({size_bytes} B)"
                else:
                    size = f" ({size_bytes // 1024} KB)"
            result_lines.append(f"{prefix}{item.name}{size}")

        if not result_lines:
            return f"Directory '{path}' is empty."
        return f"Contents of '{path}':\n" + "\n".join(result_lines)
    except FileNotFoundError:
        return f"ERROR: Directory '{path}' not found."
    except Exception as e:
        return f"ERROR listing directory: {e}"


# --- LLM Tool Schema ---
LIST_DIRECTORY_TOOL = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List all files and subdirectories at a given path in the project.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list. Use '.' for the project root.",
                }
            },
            "required": ["path"],
        },
    },
}

LIST_DIRECTORY_MAP = {"list_directory": list_directory}
