from langgraph.checkpoint.memory import InMemorySaver

def make_checkpointer() -> InMemorySaver:
    return InMemorySaver

def thread_config(thead_id: str) -> dict:
    return {
        "configurable" : {
            "thread_id" : thead_id
        }
    }