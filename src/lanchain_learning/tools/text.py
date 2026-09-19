from pathlib import Path

_ESCAPE_MAP = (
    ("\\n", "\n"),
    ("\\t", "\t"),
    ("\\r", "\r"),
    ("\\b", "\b"),
    ("\\f", "\f"),
    ("\\v", "\v"),
    ("\\a", "\a"),
    ("\\0", "\0"),
)

_HTML_ENTITIES = (
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&amp;", "&"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&nbsp;", " "),
    ("&copy;", "©"),
    ("&reg;", "®"),
    ("&euro;", "€"),
    ("&pound;", "£"),
    ("&yen;", "¥"),
    ("&cent;", "¢"),
    ("&sect;", "§"),
    ("&deg;", "°"),
    ("&plusmn;", "±"),
    ("&micro;", "µ"),
    ("&para;", "¶"),
)

_MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext"}
_MARKUP_SUFFIXES = {".html", ".htm", ".xhtml", ".xml", ".xsl", ".xslt", ".svg", ".rss", ".atom"}

def looks_like_escaped_source(text: str) -> bool:
    """True when the payload is one logical line stuffed with \\n sequences"""

    if "\\n" not in text:
        return False

    return text.count("\\n") <= 1

def normalize_source_text(text: str) -> str:
    """Turn double escaped newlines/tabs into real ones."""
    if not looks_like_escaped_source(text):
        return text

    normalize = text
    for escaped, unescaped in _ESCAPE_MAP:
        normalize = normalize.replace(escaped, unescaped)
    return normalize

def unescape_html_entities(text: str) -> str:
    """Turn HTML entities into their corresponding characters."""
    if "&" not in text:
        return text
    unescaped = text
    for entity, char in _HTML_ENTITIES:
        unescaped = unescaped.replace(entity, char)
    return unescaped

def strip_markdown_fence(text: str) -> str:
    """Strip markdown code fences from the text."""

    if "```" not in text:
        return text
    
    lines = text.split("\n")
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().endswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)

def prepare_file_content(path: str, text: str) -> str:
    """Normalize a tool payload text into file bytes, independent of language
    1. Normalize escaped newlines/tabs into real ones
    2. Strip markdown fences if the file is not a markdown file
    3. Unescape HTML entities if the file is not a markup file

    """
    suffix = Path(path).suffix.lower()
    prepared = normalize_source_text(text)
    if suffix not in _MARKDOWN_SUFFIXES:
        prepared = strip_markdown_fence(prepared)
    if suffix not in _MARKUP_SUFFIXES:
        prepared = unescape_html_entities(prepared)
    return prepared