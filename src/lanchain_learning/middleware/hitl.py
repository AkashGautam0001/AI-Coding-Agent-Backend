from langchain.agents.middleware import HumanInTheLoopMiddleware 

def build_human_middleware() -> HumanInTheLoopMiddleware:
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "read_file": False,
            "list_files": False,
            "write_file": {
                "allowed_decisions": ["approve", "reject", "edit"],
                "description": "The user can approve, reject, or edit the file content before writing it to disk."
            },
            "edit_file": {
                "allowed_decisions": ["approve", "reject", "edit"],
                "description": "The user can approve, reject, or edit the file content before editing it."
            }
        },
        description_prefix="Human-in-the-loop middleware for file operations. The user can approve, reject, or edit the file content before writing or editing it."
    )