from pathlib import Path
from fnmatch import fnmatch
from lanchain_learning.config.config import get_work_dir

BLOCKED_PATH_PATTERNS = [
    ".env",
    ".env.*",
    ".pem",
    ".key",
    ".secret",
    ".git",
    ".git/**",
    "*.log",
    ".p12"
]

def normalize_path(path: str) -> str:
    """
    Normalize a file path by replacing backslashes with forward slashes and removing redundant slashes.
    
    Args:
        path (str): The file path to normalize.
        
    Returns:
        str: The normalized file path.
    """
    # Replace backslashes with forward slashes

    normalized = Path(path).as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized

def is_path_blocked(path: str) -> bool:
    """
    Check if a given file path matches any of the blocked path patterns.
    
    Args:
        path (str): The file path to check.
    """
    normalized = normalize_path(path)
    return any(fnmatch(normalized, pattern) for pattern in BLOCKED_PATH_PATTERNS)

def resolve_work_path(path: str) -> Path:
    work_dir = get_work_dir()
    work_dir.mkdir(parents=True, exist_ok=True)
    candidate = (work_dir / path).resolve()
    try:
        candidate.relative_to(work_dir)
    except ValueError as e:
        raise ValueError(f"Path escapes working directory")
    return candidate
    