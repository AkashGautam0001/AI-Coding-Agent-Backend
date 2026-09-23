from lanchain_learning.runtime import AgentTurnResult, format_interrupt, start_turn, resume_turn
from lanchain_learning.config.config import get_work_dir
from lanchain_learning.models import select_provider
from lanchain_learning.memory import thread_config, make_checkpointer
from lanchain_learning.agent import build_agent
from lanchain_learning.prompts import build_greeting

import uuid

def chat() -> None:
    work_dir = get_work_dir()