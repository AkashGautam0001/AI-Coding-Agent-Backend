from pathlib import Path
from lanchain_learning.tools.paths import resolve_work_path, is_path_blocked
from langchain.tools import tool

@tool
def read_file(path: str) -> str:
    """
    Reads a UTF-8 text file from the working directory

    Args:
        path: Relative path of the file, e.g 'src/App.js' or 'README.md' or 'data/example.json'
    """

    try:
        file_path = resolve_work_path(path) # we resolve the path to ensure it is within the working directory
    except ValueError as err:
        raise ValueError(f"Path escapes working directory: {err}")

    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")
    except Exception as err:
        raise Exception(f"Error reading file {path}: {err}")