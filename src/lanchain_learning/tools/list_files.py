import json
import os
from pathlib import Path
from langchain.tools import tool

from lanchain_learning.config.config import get_work_dir
from lanchain_learning.tools.paths import resolve_work_path, is_path_blocked

@tool
def list_files(path: str = ".") -> str:
    """
    Lists files in a directory within the working directory.

    Args:
        path: Relative path of the directory, e.g 'src' or 'data'
    """

    work_dir = get_work_dir()

    try:
        base_path = resolve_work_path(path)  # we resolve the path to ensure it is within the working directory
    except ValueError as err:
        raise ValueError(f"Path escapes working directory: {err}")

    if not base_path.exists():
        return json.dumps({"error" : f"Path {path!r} does not exist."})

    if not base_path.is_dir():
        return json.dumps({"error" : f"Path {path!r} is not a directory."})

    result : list[str] = []
    for root, dirs, files in os.walk(base_path):
        root_path = Path(root)
        rel_root = root_path.relative_to(work_dir)

        for dir_name in sorted(dirs):
            result.append(f"{(rel_root / dir_name).as_posix()}/")
        for file_name in sorted(files):
            result.append(f"{(rel_root / file_name).as_posix()}")

    return json.dumps(result)