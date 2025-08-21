"""Tools for extracting text from files."""

from pathlib import Path

def extract_text(path: str) -> str:
    """Read and return the text content of a file."""
    return Path(path).read_text(encoding="utf-8")
