"""Utility functions for codetok."""

from pathlib import Path
from typing import Set


def format_number(num: int) -> str:
    """Format number with thousand separators."""
    return f"{num:,}"


def format_size(bytes_size: int) -> str:
    """Format file size in human readable format."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"


def should_exclude_directory(dir_path: Path, exclude_dirs: Set[str]) -> bool:
    """Check if directory should be excluded."""
    return any(excluded in dir_path.parts for excluded in exclude_dirs)
