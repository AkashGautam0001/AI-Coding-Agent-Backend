from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.structured_output import ProviderStrategy
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from lanchain_learning.config.config import MAX_MODEL_CALLS_PER_MIN, hitl_enabled
from lanchain_learning.middleware.audit import AuditMiddleware
from lanchain_learning.middleware.protection import ProtectionMiddleware
from lanchain_learning.middleware.hitl import build_human_middleware
from lanchain_learning.models import build_chat_model
from lanchain_learning.tools import ALL_TOOLS
from lanchain_learning.prompts import build_system_prompt
from lanchain_learning.schemas import TurnSummary
from lanchain_learning.memory import make_checkpointer

def build_middleware(
    *,
    enable_hitl = bool
) -> list:
    """Harness layers, outermost first.
    
    1. model-call cap
    2. Audit log
    3. payload guarding
    4. HITL on write/edit/run
    
    """

    layers: list = [
        ModelCallLimitMiddleware(
            run_limit = MAX_MODEL_CALLS_PER_MIN,
            exit_behavior = "end"
        ),
        AuditMiddleware(),
        ProtectionMiddleware()
    ]

    if enable_hitl:
        layers.append(build_human_middleware())

    return layers

def build_agent(
    *,
    checkpointer: InMemorySaver | None = None,
    enable_hitl : bool | None = None,
    extra_guidance: str = ""
):
    model, _provider = build_chat_model()
    use_hitl = hitl_enabled() if enable_hitl is None else enable_hitl
    return create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=build_system_prompt(extra_guidance=extra_guidance),
        middleware=build_middleware(enable_hitl=use_hitl),
        response_format=ProviderStrategy(TurnSummary),
        checkpointer=checkpointer or make_checkpointer(),
        name="CodingAgent"
    )