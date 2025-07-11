"""codetok: A blazing-fast, extensible codebase analysis tool."""

from .analyzer import CodeAnalyzer
from .config import Config
from .formatters import CategoryStats
from .parser import FileStats

__version__ = "0.1.0"
__all__ = ["CodeAnalyzer", "Config", "FileStats", "CategoryStats"]
