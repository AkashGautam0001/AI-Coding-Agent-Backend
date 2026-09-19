from jinja2 import Environment, FileSystemBytecodeCache, select_autoescape
from lanchain_learning.config.config import PROMPT_DIR, AGENT_NAME, get_work_dir
from lanchain_learning.tools import tool_catalog

_env = Environment(
    loader=FileSystemBytecodeCache(PROMPT_DIR),
    auto_reload=select_autoescape(enabled_extensions=()),
    trim_blocks=True,
    lstrip_blocks=True
)

def render_template(name : str, **context) -> str:
    return _env.get_template(name).render(**context)

def build_system_prompt(*, agent_name: str = AGENT_NAME, extra_guidance: str = "") -> str:
    return render_template(
        "system.jinja", 
        agent_name=agent_name, 
        extra_guidance=extra_guidance, 
        work_dir=str(get_work_dir()),
        tools=tool_catalog()
    )

def build_greeting(*, agent_name: str = AGENT_NAME) -> str:
    return render_template(
        "greeting.jinja",
        agent_name=agent_name,
        work_dir=str(get_work_dir())
    )