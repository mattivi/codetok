"""Command-line interface for codetok."""

import argparse
from typing import List, Optional

from .analyzer import CodeAnalyzer
from .config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="codetok",
        description="codetok: Analyze codebase for SLOC, comments, blank lines, and "
        "OpenAI tokens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codetok                              # Analyze current directory
  codetok --path /path/to/project      # Analyze specific directory
  codetok --json-only                  # Only generate JSON report
  codetok --output report.json         # Custom output file
  codetok --include-extensions .py .js # Only analyze Python and JS files
  codetok --exclude-patterns "*test*"  # Exclude files matching pattern
  codetok --max-workers 4              # Limit parallel workers
        """,
    )

    # Analysis settings
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        default=".",
        help="Path to the root of the codebase (default: current directory)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="codebase_analysis.json",
        help="Output JSON file for detailed report (default: codebase_analysis.json)",
    )

    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only output JSON report, suppress console summary",
    )

    # File filtering
    parser.add_argument(
        "--include-extensions",
        nargs="+",
        help="Only include files with these extensions (e.g., .py .js)",
    )

    parser.add_argument(
        "--exclude-patterns",
        nargs="+",
        help="Exclude files matching these glob patterns (e.g., *test* *.tmp)",
    )

    # Processing options
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing",
    )

    parser.add_argument(
        "--no-progress", action="store_true", help="Disable progress bar"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        help="Maximum number of parallel workers (default: system-dependent)",
    )

    parser.add_argument(
        "--generate-charts",
        action="store_true",
        help="Generate visual charts of the analysis (requires matplotlib)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Create configuration from parsed arguments
    config = Config(
        path=parsed_args.path,
        output_file=parsed_args.output,
        json_only=parsed_args.json_only,
        include_extensions=(
            set(parsed_args.include_extensions)
            if parsed_args.include_extensions
            else None
        ),
        exclude_patterns=parsed_args.exclude_patterns,
        parallel=not parsed_args.no_parallel,
        progress_bar=not parsed_args.no_progress,
        max_workers=parsed_args.max_workers,
        generate_charts=parsed_args.generate_charts,
    )

    # Run analysis
    analyzer = CodeAnalyzer(config)
    analyzer.analyze()


if __name__ == "__main__":
    main()
