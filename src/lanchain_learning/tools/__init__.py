from lanchain_learning.tools.write_file import write_file
from lanchain_learning.tools.read_file import read_file
from lanchain_learning.tools.edit_file import edit_file
from lanchain_learning.tools.list_files import list_files
from lanchain_learning.tools.shell import run_command, list_jobs, stop_job

ALL_TOOLS = [write_file, read_file, edit_file, list_files, run_command, list_jobs, stop_job]

def tool_catalog() -> list[dict[str, str]]:
    """
    Returns a list of dictionaries containing the name and description of each tool.
    """
    return [{"name": tool.name, "description": tool.description} for tool in ALL_TOOLS]