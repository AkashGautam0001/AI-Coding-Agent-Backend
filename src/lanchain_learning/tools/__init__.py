from lanchain_learning.tools import write_file, read_file, edit_file, list_files
from lanchain_learning.tools.shell import run_command, list_jobs, stop_job

ALL_TOOLS = [write_file, read_file, edit_file, list_files, run_command, list_jobs, stop_job]

def tool_catalog() -> list[dict[str, str]]:
    """
    Returns a list of dictionaries containing the name and description of each tool.
    """
    return [{"name": tool.name, "description": tool.description} for tool in ALL_TOOLS]