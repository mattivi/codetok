"""Output formatters for codetok."""

import json
from datetime import datetime
from typing import Dict, List
from dataclasses import asdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from .parser import (
    FileStats,
    CODE_EXTENSIONS,
    DOCUMENTATION_EXTENSIONS,
    CONFIG_EXTENSIONS,
)
from .ui import Logger, Icons, Colors
from .utils import format_number, format_size


class CategoryStats:
    """Aggregated statistics for a category of files."""

    def __init__(self, name: str, icon: str, files: List[FileStats]):
        self.name = name
        self.icon = icon
        self.files = files
        self.total_files = len(files)
        self.total_lines = sum(f.lines_total for f in files)
        self.total_sloc = sum(f.lines_code for f in files)
        self.total_comments = sum(f.lines_comments for f in files)
        self.total_blank = sum(f.lines_blank for f in files)
        self.total_tokens = sum(f.tokens for f in files)
        self.total_size_bytes = sum(f.size_bytes for f in files)

    @property
    def avg_lines_per_file(self) -> float:
        return self.total_lines / self.total_files if self.total_files > 0 else 0

    @property
    def avg_tokens_per_file(self) -> float:
        return self.total_tokens / self.total_files if self.total_files > 0 else 0


def categorize_files(file_stats: List[FileStats]) -> Dict[str, CategoryStats]:
    """Categorize files into code, documentation, and config."""
    code_files = []
    doc_files = []
    config_files = []
    other_files = []

    for stats in file_stats:
        if stats.extension in CODE_EXTENSIONS:
            code_files.append(stats)
        elif stats.extension in DOCUMENTATION_EXTENSIONS:
            doc_files.append(stats)
        elif stats.extension in CONFIG_EXTENSIONS:
            config_files.append(stats)
        else:
            other_files.append(stats)

    return {
        "code": CategoryStats("Code Files", Icons.CODE, code_files),
        "documentation": CategoryStats("Documentation Files", Icons.DOCS, doc_files),
        "config": CategoryStats("Configuration Files", Icons.CONFIG, config_files),
        "other": CategoryStats("Other Files", Icons.OTHER, other_files),
    }


class JSONFormatter:
    """Format results as JSON."""

    def format(self, categories: Dict[str, CategoryStats], output_file: str):
        """Save analysis results to JSON file."""
        timestamp = datetime.now().isoformat()

        report = {
            "timestamp": timestamp,
            "analysis_info": {
                "tokenizer": "cl100k_base",
                "excluded_directories": [],  # Could be populated from config
            },
            "summary": {
                "total_files": sum(cat.total_files for cat in categories.values()),
                "total_lines": sum(cat.total_lines for cat in categories.values()),
                "total_sloc": sum(cat.total_sloc for cat in categories.values()),
                "total_comments": sum(
                    cat.total_comments for cat in categories.values()
                ),
                "total_blank": sum(cat.total_blank for cat in categories.values()),
                "total_tokens": sum(cat.total_tokens for cat in categories.values()),
                "total_size_bytes": sum(
                    cat.total_size_bytes for cat in categories.values()
                ),
            },
            "categories": {},
        }

        for name, category in categories.items():
            # Calculate extension breakdown
            ext_breakdown = {}
            for file_stat in category.files:
                ext = file_stat.extension
                ext_name = (
                    CODE_EXTENSIONS.get(ext)
                    or DOCUMENTATION_EXTENSIONS.get(ext)
                    or CONFIG_EXTENSIONS.get(ext)
                    or ext
                )
                if ext not in ext_breakdown:
                    ext_breakdown[ext] = {
                        "name": ext_name,
                        "files": 0,
                        "lines": 0,
                        "tokens": 0,
                        "size_bytes": 0,
                    }
                ext_breakdown[ext]["files"] += 1
                ext_breakdown[ext]["lines"] += file_stat.lines_total
                ext_breakdown[ext]["tokens"] += file_stat.tokens
                ext_breakdown[ext]["size_bytes"] += file_stat.size_bytes

            report["categories"][name] = {
                "icon": category.icon,
                "total_files": category.total_files,
                "total_lines": category.total_lines,
                "total_sloc": category.total_sloc,
                "total_comments": category.total_comments,
                "total_blank": category.total_blank,
                "total_tokens": category.total_tokens,
                "total_size_bytes": category.total_size_bytes,
                "avg_lines_per_file": category.avg_lines_per_file,
                "avg_tokens_per_file": category.avg_tokens_per_file,
                "extension_breakdown": ext_breakdown,
                "files": [
                    {
                        "path": str(f.path),
                        "extension": f.extension,
                        "extension_name": CODE_EXTENSIONS.get(f.extension)
                        or DOCUMENTATION_EXTENSIONS.get(f.extension)
                        or CONFIG_EXTENSIONS.get(f.extension)
                        or f.extension,
                        "lines_total": f.lines_total,
                        "lines_code": f.lines_code,
                        "lines_comments": f.lines_comments,
                        "lines_blank": f.lines_blank,
                        "tokens": f.tokens,
                        "size_bytes": f.size_bytes,
                    }
                    for f in category.files
                ],
            }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


class ConsoleFormatter:
    """Format results for console output."""

    def format(self, categories: Dict[str, CategoryStats]):
        """Print analysis results to console."""
        self._print_token_analysis(categories)
        self._print_detailed_analysis(categories)

    def _print_token_analysis(self, categories: Dict[str, CategoryStats]):
        """Print detailed token analysis."""
        Logger.header("TOKEN ANALYSIS REPORT", Icons.TOKEN)

        total_tokens = sum(cat.total_tokens for cat in categories.values())

        Logger.info(
            f"OpenAI Tokenizer: {Colors.BOLD}cl100k_base{Colors.ENDC} (GPT-4/GPT-3.5-turbo compatible)"
        )

        # Token distribution by category
        Logger.section("Token Distribution by Category", Icons.CHART)

        for name, category in categories.items():
            if category.total_files > 0:
                percentage = (
                    (category.total_tokens / total_tokens * 100)
                    if total_tokens > 0
                    else 0
                )
                Logger.stat(
                    f"{category.icon} {category.name}",
                    f"{format_number(category.total_tokens)} tokens ({percentage:.1f}%)",
                )

    def _print_detailed_analysis(self, categories: Dict[str, CategoryStats]):
        """Print detailed category analysis."""
        Logger.header("DETAILED CATEGORY ANALYSIS", Icons.STATS)

        total_files = sum(cat.total_files for cat in categories.values())
        total_lines = sum(cat.total_lines for cat in categories.values())
        total_sloc = sum(cat.total_sloc for cat in categories.values())
        total_tokens = sum(cat.total_tokens for cat in categories.values())
        total_size = sum(cat.total_size_bytes for cat in categories.values())

        Logger.section("Overall Summary", Icons.SUMMARY)
        Logger.stat("Total Files", format_number(total_files), Icons.FILE)
        Logger.stat("Total Lines", format_number(total_lines), Icons.LINES)
        Logger.stat("Source Lines (SLOC)", format_number(total_sloc), Icons.CODE)
        Logger.stat("Total Tokens", format_number(total_tokens), Icons.TOKEN)
        Logger.stat("Total Size", format_size(total_size), Icons.SIZE)
        if total_lines > 0:
            Logger.stat(
                "Average Tokens per Line",
                f"{total_tokens / total_lines:.2f}",
                Icons.CHART,
            )

        for category in categories.values():
            self._print_category_stats(category)

    def _print_category_stats(self, category: CategoryStats):
        """Print comprehensive statistics for a category."""
        if category.total_files == 0:
            Logger.warning(f"No {category.name.lower()} found.", Icons.WARNING)
            return

        Logger.section(f"{category.icon} {category.name.upper()}", category.icon)

        # Basic stats
        Logger.stat("Total Files", format_number(category.total_files), Icons.FILE)
        Logger.stat("Total Lines", format_number(category.total_lines), Icons.LINES)
        Logger.stat(
            "Source Lines (SLOC)", format_number(category.total_sloc), Icons.CODE
        )
        Logger.stat("Comment Lines", format_number(category.total_comments), Icons.DOCS)
        Logger.stat("Blank Lines", format_number(category.total_blank), Icons.OTHER)
        Logger.stat("Total Tokens", format_number(category.total_tokens), Icons.TOKEN)
        Logger.stat("Total Size", format_size(category.total_size_bytes), Icons.SIZE)

        # Averages
        if category.total_files > 0:
            Logger.stat(
                "Avg Lines per File", f"{category.avg_lines_per_file:.1f}", Icons.CHART
            )
            Logger.stat(
                "Avg Tokens per File",
                f"{category.avg_tokens_per_file:.1f}",
                Icons.CHART,
            )


class ChartFormatter:
    """Generate visual charts for analysis results."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir).parent  # Save charts alongside JSON

    def format(self, categories: Dict[str, CategoryStats]):
        """Generate charts if matplotlib is available."""
        if not HAS_MATPLOTLIB:
            Logger.warning("matplotlib not installed. Skipping chart generation.")
            return

        Logger.info("Generating analysis charts...")

        # 1. Token Distribution Pie Chart
        labels = []
        sizes = []
        for name, cat in categories.items():
            if cat.total_tokens > 0:
                labels.append(f"{cat.icon} {name}")
                sizes.append(cat.total_tokens)

        if sizes:
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
            plt.title("Token Distribution by Category")
            plt.axis("equal")
            plt.savefig(self.output_dir / "token_distribution.png")
            plt.close()
            Logger.success("Generated token_distribution.png")

        # 2. Lines Breakdown Bar Chart
        categories_list = list(categories.keys())
        sloc = [cat.total_sloc for cat in categories.values()]
        comments = [cat.total_comments for cat in categories.values()]
        blanks = [cat.total_blank for cat in categories.values()]

        x = range(len(categories_list))
        width = 0.25

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x, sloc, width, label="SLOC")
        ax.bar([p + width for p in x], comments, width, label="Comments")
        ax.bar([p + width * 2 for p in x], blanks, width, label="Blanks")

        ax.set_ylabel("Lines")
        ax.set_title("Lines Breakdown by Category")
        ax.set_xticks([p + width for p in x])
        ax.set_xticklabels(categories_list)
        ax.legend()

        plt.savefig(self.output_dir / "lines_breakdown.png")
        plt.close()
        Logger.success("Generated lines_breakdown.png")

        Logger.success("All charts generated successfully!")
