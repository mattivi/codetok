"""codetok: A blazing-fast, extensible codebase analysis tool."""

from .analyzer import CodeAnalyzer
from .config import Config
from .parser import FileStats
from .formatters import CategoryStats

__version__ = "0.1.0"
__all__ = ["CodeAnalyzer", "Config", "FileStats", "CategoryStats"]
