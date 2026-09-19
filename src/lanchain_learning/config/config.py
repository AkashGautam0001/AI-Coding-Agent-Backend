import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT= Path(__file__).resolve().parent.parent.parent
PROMPT_DIR = PROJECT_ROOT / "prompts"

DEFAULT_WORK_DIR = PROJECT_ROOT / "workspace"

AGENT_NAME = "Akash Coding Agent"

MAX_MODEL_CALLS_PER_MIN = int(os.getenv("MAX_MODEL_CALLS_PER_MIN", "10"))
MAX_READ_BYTES = int(os.getenv("MAX_READ_BYTES", "1000000"))

def hitl_enabled() -> bool:
    return os.getenv("HITL_ENABLED", "true").lower() in {"1", "true", "yes"}

def get_work_dir() -> Path:
    override = os.getenv("WORK_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    return DEFAULT_WORK_DIR.resolve()