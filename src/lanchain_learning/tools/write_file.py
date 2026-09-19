from langchain.tools import tool
from lanchain_learning.tools.text import prepare_file_content, resolve_work_path

@tool
def write_file(path: str, content: str) -> str:
    """
    Write `content` to a file at `path`. Creates the file if it does not exist.
    Language agnostic : .js, .java, .py and other text file all use exact substring replace.
    `content` must use real newlines, and not the two-character sequence backslash-n.
    Do not wrap it in markdown fences, even if the file is a markdown file. The tool will strip them automatically.

    Args:
       path: Relative path of the file to write (e.g "README.md")
       content: Full file body with real newlines. No markdown fences. No backslash-n sequences. The tool will normalize escaped newlines/tabs into real ones.
    """

    if not path:
        return "Error: Path is empty."

    if not content:
        return "Error: Content is empty."
    
    content = prepare_file_content(path, content)

    try:
        file_path = resolve_work_path(path)  # we resolve the path to ensure it is within the working directory
    except ValueError as err:
        return f"Error: Path escapes working directory: {err}"

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the parent directory exists
        file_path.write_text(content, encoding="utf-8")

    except Exception as err:
        return f"Error: Failed to write to {file_path}: {err}"

    return f"Successfully wrote to {file_path}: {len(content)} bytes."