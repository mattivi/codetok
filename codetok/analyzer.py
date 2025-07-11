"""Core analysis engine for codetok."""

import fnmatch
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

import pathspec

try:
    from tqdm import tqdm  # type: ignore

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

from .config import Config
from .formatters import (
    CategoryStats,
    ConsoleFormatter,
    JSONFormatter,
    categorize_files,
)
from .parser import FileStats, get_all_extensions, process_file
from .ui import Icons, Logger
from .utils import should_exclude_directory


class CodeAnalyzer:
    """Main analyzer class for counting lines of code and tokens.

    This class orchestrates the file discovery, processing, categorization,
    and output formatting for the codebase analysis.
    """

    def __init__(self, config: Config):
        """
        Initialize the analyzer with configuration.

        Args:
            config: Configuration object containing analysis settings.
        """
        self.config = config
        self.json_formatter = JSONFormatter()
        self.console_formatter = ConsoleFormatter()

    def analyze(self) -> Dict[str, CategoryStats]:
        """Perform the full codebase analysis.

        This method:
        1. Finds relevant files based on config
        2. Processes files to gather stats
        3. Categorizes results
        4. Generates console/JSON outputs
        5. Optionally generates charts

        Returns:
            Dictionary of category names to their statistics.

        Raises:
            ValueError: If configuration is invalid.
        """
        Logger.header("CODEBASE ANALYSIS TOOL", Icons.SEARCH)
        Logger.info(f"Scanning for files to analyze in: {self.config.path}")

        # Get all files to process
        files_to_process = self._find_files()

        if not files_to_process:
            Logger.error("No matching files found!")
            return {}

        Logger.success(f"Found {len(files_to_process):,} files to analyze")
        exclude_dirs = self.config.exclude_dirs or set()
        excluded_list = sorted(list(exclude_dirs)[:10])
        excluded_suffix = "..." if len(exclude_dirs) > 10 else ""
        Logger.info(
            f"Excluded directories: {', '.join(excluded_list)}{excluded_suffix}"
        )

        # Process files
        file_stats = self._process_files(files_to_process)

        # Categorize results
        Logger.info("Categorizing files...")
        categories = categorize_files(file_stats)

        # Output results
        if not self.config.json_only:
            self.console_formatter.format(categories)

        Logger.info("Saving detailed analysis report...")
        self.json_formatter.format(categories, self.config.output_file)
        Logger.success(
            f"Detailed report saved to: {self.config.output_file}"
        )

        # Generate charts if requested
        # if self.config.generate_charts:
        #     ChartFormatter(self.config.output_file).format(categories)

        Logger.header("ANALYSIS COMPLETE", Icons.SUCCESS)
        Logger.success(
            "Token counting and codebase analysis finished successfully!"
        )

        return categories

    def _find_files(self) -> List[Path]:
        """Discover files to analyze based on configuration filters.

        Respects excluded directories, gitignore (if present), extension filters,
        and exclude patterns.

        Returns:
            List of file paths to process.
        """
        all_extensions = get_all_extensions()
        files_to_process = []
        base_path = Path(self.config.path)

        # Load .gitignore if exists
        gitignore_path = base_path / ".gitignore"
        gitignore_spec = None
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore_spec = pathspec.PathSpec.from_lines(
                    "gitwildmatch", f
                )

        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)

            # Skip excluded directories
            if should_exclude_directory(
                root_path, self.config.exclude_dirs or set()
            ):
                dirs.clear()  # Prevent walking into excluded directories
                continue

            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(base_path)

                # Check gitignore
                if gitignore_spec and gitignore_spec.match_file(relative_path):
                    continue

                # Check extension filter
                ext = file_path.suffix.lower()
                if (
                    self.config.include_extensions
                    and ext not in self.config.include_extensions
                ):
                    continue

                # Check exclude patterns
                if self.config.exclude_patterns and any(
                    fnmatch.fnmatch(file, pattern)
                    for pattern in self.config.exclude_patterns
                ):
                    continue

                if ext in all_extensions:
                    files_to_process.append(file_path)

        return files_to_process

    def _process_files(self, files_to_process: List[Path]) -> List[FileStats]:
        """Process files to compute statistics.

        Uses parallel or sequential processing based on config.
        Shows progress bar if enabled.

        Args:
            files_to_process: List of file paths to analyze.

        Returns:
            List of FileStats objects for each processed file.
        """
        file_stats = []

        if self.config.parallel and len(files_to_process) > 1:
            # Use parallel processing
            Logger.info("Processing files in parallel...")

            if HAS_TQDM and self.config.progress_bar:
                # Use tqdm progress bar
                with ThreadPoolExecutor(
                    max_workers=self.config.max_workers
                ) as executor:
                    with tqdm(
                        total=len(files_to_process), desc="Processing files"
                    ) as pbar:
                        futures = [
                            executor.submit(process_file, file_path)
                            for file_path in files_to_process
                        ]
                        for future in futures:
                            file_stats.append(future.result())
                            pbar.update(1)
            else:
                # Parallel without progress bar
                with ThreadPoolExecutor(
                    max_workers=self.config.max_workers
                ) as executor:
                    file_stats = list(
                        executor.map(process_file, files_to_process)
                    )
        else:
            # Sequential processing
            Logger.info("Processing files sequentially...")

            if HAS_TQDM and self.config.progress_bar:
                # Use tqdm progress bar
                for file_path in tqdm(
                    files_to_process, desc="Processing files"
                ):
                    file_stats.append(process_file(file_path))
            else:
                # Sequential without progress bar
                for i, file_path in enumerate(files_to_process):
                    file_stats.append(process_file(file_path))
                    if (i + 1) % 10 == 0 or (i + 1) == len(files_to_process):
                        processed_count = f"{i + 1:,}/{len(files_to_process):,}"
                        Logger.info(f"Processed {processed_count} files")

        Logger.success("File processing completed!")
        return file_stats
