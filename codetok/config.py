"""Simplified configuration for codetok."""

import os
from dataclasses import dataclass, field
from typing import Set, Optional, List
from pathlib import Path


@dataclass
class Config:
    """Configuration for codetok analysis.
    
    This dataclass holds all configurable options for the analysis process,
    with defaults and validation.
    """
    
    # Analysis settings
    path: str = "."
    """Root path for analysis."""
    
    output_file: str = "codebase_analysis.json"
    """Path for JSON output report."""
    
    json_only: bool = False
    """If True, suppress console output."""
    
    # File filtering
    exclude_dirs: Set[str] = field(default_factory=lambda: {
        '.next', 'node_modules', '.git', '__pycache__', 'dist', 'build',
        '.turbo', 'out', '.venv', 'venv', '.env', 'env', '.pytest_cache',
        '.mypy_cache', '.tox', 'coverage', '.coverage', '.nyc_output',
        'logs', 'log', 'tmp', 'temp', '.tmp', '.temp', '.DS_Store',
        '.idea', '.vscode', '.cache', 'cache', 'vendor', 'target', 'bin', 'obj'
    })
    """Directories to exclude from analysis."""
    
    include_extensions: Optional[Set[str]] = None
    """If set, only include these file extensions."""
    
    exclude_patterns: Optional[List[str]] = None
    """Glob patterns to exclude files."""
    
    respect_gitignore: bool = True
    """If True, respect .gitignore files in the path."""
    
    # Processing options
    parallel: bool = True
    """Enable parallel processing."""
    
    progress_bar: bool = True
    """Show progress bar during processing."""
    
    max_workers: Optional[int] = None
    """Maximum parallel workers (defaults to system-dependent)."""
    
    generate_charts: bool = False
    """Generate visual charts (requires matplotlib)."""
    
    def __post_init__(self):
        """Initialize defaults and validate configuration."""
        if self.max_workers is None:
            self.max_workers = min(32, (os.cpu_count() or 1) + 4)

        if self.exclude_dirs is None:
            self.exclude_dirs = {
                '.next', 'node_modules', '.git', '__pycache__', 'dist', 'build',
                '.turbo', 'out', '.venv', 'venv', '.env', 'env', '.pytest_cache',
                '.mypy_cache', '.tox', 'coverage', '.coverage', '.nyc_output',
                'logs', 'log', 'tmp', 'temp', '.tmp', '.temp', '.DS_Store',
                '.idea', '.vscode', '.cache', 'cache', 'vendor', 'target', 'bin', 'obj'
            }

        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        if not Path(self.path).exists():
            raise ValueError(f"Analysis path does not exist: {self.path}")
