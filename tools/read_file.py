"""
Tool: read_file
Reads a file's contents with line numbers for easy reference.
"""

from __future__ import annotations

from pathlib import Path


def read_file(file_path: str) -> str:
    """Read the contents of a file, returned with line numbers."""
    try:
        path = Path(file_path).resolve()
        if not path.is_file():
            return f"ERROR: '{file_path}' is not a file or does not exist."

        size_kb = path.stat().st_size / 1024
        if size_kb > 500:
            return (
                f"WARNING: File '{file_path}' is {size_kb:.0f} KB. "
                f"Reading first 500 lines only.\n"
                + _read_with_line_numbers(path, max_lines=500)
            )
        return _read_with_line_numbers(path)
    except Exception as e:
        return f"ERROR reading file: {e}"


def _read_with_line_numbers(path: Path, max_lines: int | None = None) -> str:
    """Helper: read a file and prepend line numbers."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if max_lines:
        lines = lines[:max_lines]
    numbered = [f"{i + 1:>4} | {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered)


# --- LLM Tool Schema ---
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the full contents of a file, returned with line numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read.",
                }
            },
            "required": ["file_path"],
        },
    },
}

READ_FILE_MAP = {"read_file": read_file}
