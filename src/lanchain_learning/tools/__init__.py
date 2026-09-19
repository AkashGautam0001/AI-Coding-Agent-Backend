from lanchain_learning.tools import write_file, read_file, edit_file, list_files

ALL_TOOLS = [write_file, read_file, edit_file, list_files]

def tool_catalog() -> list[dict[str, str]]:
    """
    Returns a list of dictionaries containing the name and description of each tool.
    """
    return [{"name": tool.name, "description": tool.description} for tool in ALL_TOOLS]