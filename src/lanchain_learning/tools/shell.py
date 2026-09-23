import re
import sys
import shlex
import os
import subprocess
import time

from langchain.tools import tool
from lanchain_learning.config.config import get_work_dir
from lanchain_learning.tools.jobs import now_iso, register, stop_pid, read_log_tail, all_jobs, is_alive, BackgroundJob

MAX_OUTPUT_CHARS = 8000
DEFAULT_TIMEOUT = 30

BLOCKED_COMMAND_PATTERNS = (
    r"\bsudo\b",
    r"\brm\s+-rf\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bmkfs(?:\.[\w-]+)?\b",
    r"\bformat\b",
    r"\b(?:del|erase)\b",
)

SERVER_PATTERNS = (
    r"\bflask(\s+--app)?\s+run\b",
    r"\buvicorn\s+[\w.-]+(?::[\w.-]+)?\b",
    r"\bpython(?:3)?\s+-m\s+http\.server\b",
    r"\bnpm\s+(?:run\s+)?(?:dev|start)\b",
)

_PIP_PREFIX = re.compile(r"^pip(?:\.exe)?\s+")
_PYTHON_PREFIX = re.compile(r"^python(?:3)?(?:\.exe)?\s+")
_FLASK_PREFIX = re.compile(r"^flask(?:\.exe)?\s+")

def deny_command(command: str) -> str | None:
    stripped = command.strip()
    if not stripped:
        return "Blocked by middlware: command is empty"

    for pattern in BLOCKED_COMMAND_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            return f"Blocked by middleware: command matched a dangerous pattern {pattern}"

    return None

def looks_like_server(command: str) -> bool:
    return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in SERVER_PATTERNS)

def rewrite_command(command: str) -> str:
    exe = shlex.quote(sys.executable)

    stripped = command.strip()

    if _PIP_PREFIX.match(stripped):
        return _PIP_PREFIX.sub(f"{exe} -m pip", stripped, count=1)

    if _PYTHON_PREFIX.match(stripped):
        return _PYTHON_PREFIX.sub(exe + " ", stripped, count=1)

    if _FLASK_PREFIX.match(stripped):
        return _FLASK_PREFIX.sub(f"{exe} -m flask", stripped, count=1)

    return command

def _clip(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    
    return text[:MAX_OUTPUT_CHARS] + "\n... (truncated)"

def _run_foreground(command: str, timeout: int) -> str:
    cwd = get_work_dir()
    cwd.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    try:
        completed = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or "") + (e.stderr or "")
        return (
            f"Timed out after {timeout}s (process killed)."
            "If this is a server, rerun with background=true."
            f"{_clip(str(stdout))}"
        )

    chunks = []
    if completed.stdout:
        chunks.append(completed.stdout.rstrip())
    if completed.stderr:
        chunks.append(completed.stderr.rstrip())

    body = "\n".join(chunks) if chunks else "No output."
    return f"exit_code={completed.returncode}\ncwd={cwd}\n_{_clip(body)}"

def _run_background(command: str) -> str:
    cwd = get_work_dir()
    cwd.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    log_dir = cwd / ".agent_jobs"
    log_dir.mkdir(parents=True, exist_ok=True)

    stamp = now_iso().replace(":", "").replace("+", "")
    tmp_log = log_dir /f"pending-{stamp}.log"
    log_file = tmp_log.open("w", encoding="utf-8")

    try:
        proc = subprocess.Popen(
            ["/bin/bash", "-lc", command],
            cwd=cwd,
            env=env,
            stdout=subprocess.STDOUT,
            preexec_fn=os.setsid,
            start_new_session=True
        )

    finally:
        log_file.close()

    log_path = log_dir / f"{proc.pid}.log"
    tmp_log.rename(log_path)
    register(
        BackgroundJob(
            pid=proc.pid,
            command=command,
            log_path=log_path,
            started_at=now_iso(),
            proc=proc
        )
    )

    time.sleep()
    tail = read_log_tail(log_path)
    if proc.poll() is not None:
        stop_pid(proc.id)
        return (
            f"Background command exitted immediately (pid={proc.id})."
            f"exit_code={proc.returncode}.\n{_clip(tail)}"
        )

    # if the process is still running
    urls = re.findall(r"https?://[^\s]+", tail)
    url_line = f"Open in the browser: {urls[0]}\n" if urls else (
        "No url in the log yet - try http://127.0.0.1:3000"
        "and check list_jobs if it is blank.\n"
    )

    return (
        f"{url_line}\n{_clip(tail)}"
        f"Started background job (pid={proc.pid}).\n"
        f"Log: {log_path}\n"
        f"cwd={cwd}\n"
        f"Use list_jobs/stop_job to manage it.\n"
        f"------- output so far ----- \n {_clip(tail) or 'No output yet.'}"
    )


@tool
def stop_job(pid: int) -> str:
    """
    Stop a background job previously started by run_command.

    Args:
        pid: The process id of the job at stop
    """

    return stop_pid(pid)

@tool
def run_command(command: str, background: bool = False, timeout_seconds: int = 0) -> str:
    """
    Run a bash command in the working directory (host machine, not a sandbox).

    Foreground commands wait for completion. Set background=True for servers like (flask, uvicorn, npm start)
    so they keep running. Server-like commands are also backgrounded even if you forget the flag.

    Args:
        command: bash command to run, e.g. 'python app.py' or 'ls -la'.
        background: If true, start the process and return pid immediately..
        timeout_seconds: Maximum time to wait for the command to complete. This is for foreground timeout. O uses default (30s)

    """

    blocked = deny_command(command)
    if blocked:
        return blocked

    timeout = timeout_seconds if timeout_seconds > 0 else DEFAULT_TIMEOUT

    background = bool(background) or looks_like_server(command)

    command = rewrite_command(command)

    if background:
        return _run_background(command)
    else:
        return _run_foreground(command, timeout)


@tool
def list_jobs() -> str:
    """
    List background process started by run_command (servers, long jobs).
    """

    jobs = all_jobs()
    if not jobs:
        return "No background jobs running"

    lines = []
    for job in jobs:
        state = "running" if is_alive(job.pid) else "exited"
        lines.append(
            f"pid={job.pid} state={state} started={job.started_at} cmd={job.command}"
        )

        tail = read_log_tail(job.log_path, max_chars=800)

        if tail:
            lines.append(tail.rstrip())
            lines.append("----------------------------")

        return "\n".join(lines)
