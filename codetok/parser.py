"""File parsing and line counting for codetok."""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Dict, Set

from .ui import Logger

try:
    import tiktoken

    openai_tokenizer = tiktoken.get_encoding("cl100k_base")
except ImportError:
    openai_tokenizer = None
    Logger.warning("tiktoken not available. Token counting will be disabled.")

try:
    from pygments import lex
    from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
    from pygments.token import Token

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False
    Logger.warning("pygments not available. Using simplified comment detection.")


@dataclass
class FileStats:
    """Statistics for a single file.

    Holds line counts, token count, and size for a file.
    """

    path: Path
    """File path."""

    extension: str
    """File extension (lowercase)."""

    lines_total: int
    """Total lines in file."""

    lines_code: int
    """Source lines of code (SLOC)."""

    lines_comments: int
    """Comment lines."""

    lines_blank: int
    """Blank lines."""

    tokens: int
    """OpenAI token count."""

    size_bytes: int
    """File size in bytes."""


# File type mappings
CODE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".sql": "SQL",
    ".sh": "Shell Script",
}
"""Mapping of code file extensions to language names."""

DOCUMENTATION_EXTENSIONS = {
    ".md": "Markdown",
    ".txt": "Plain Text",
    ".rst": "reStructuredText",
    ".adoc": "AsciiDoc",
    ".tex": "LaTeX",
}
"""Mapping of documentation file extensions to format names."""

CONFIG_EXTENSIONS = {
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".xml": "XML",
    ".env": "Environment",
    ".gitignore": "Git Ignore",
    ".dockerignore": "Docker Ignore",
}
"""Mapping of configuration file extensions to type names."""


# Mapping from extensions to Pygments lexer names
LEXER_MAPPING = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".kt": "kotlin",
    ".sql": "sql",
    ".sh": "bash",
    # Add more as needed
}
"""Mapping of file extensions to Pygments lexer names for parsing."""


def count_lines_by_type(
    content: str, extension: str, filename: str
) -> Tuple[int, int, int]:
    """
    Count different types of lines in content using Pygments if available.

    Falls back to simple heuristic-based detection if Pygments is not available
    or fails.

    Args:
        content: File content as string.
        extension: File extension (e.g., '.py').
        filename: Full filename for logging.

    Returns:
        Tuple of (code_lines, comment_lines, blank_lines)
    """
    lines = content.splitlines()
    code_lines = 0
    comment_lines = 0
    blank_lines = 0

    if HAS_PYGMENTS and extension in LEXER_MAPPING:
        try:
            lexer_name = LEXER_MAPPING[extension]
            lexer = get_lexer_by_name(lexer_name, stripall=True)
            tokens = lex(content, lexer)

            current_line = 1
            line_types = {}  # Track type per line: 'code', 'comment', 'blank'

            for ttype, value in tokens:
                lines_in_token = value.splitlines()
                for line_content in lines_in_token:
                    stripped = line_content.strip()
                    if not stripped:
                        line_types[current_line] = "blank"
                    elif ttype in Token.Comment:
                        line_types[current_line] = "comment"
                    else:
                        line_types[current_line] = "code"
                    current_line += 1

            # Count based on line types
            for line_type in line_types.values():
                if line_type == "code":
                    code_lines += 1
                elif line_type == "comment":
                    comment_lines += 1
                elif line_type == "blank":
                    blank_lines += 1

            # Adjust for any missed blank lines
            blank_lines = max(0, blank_lines + len(lines) - len(line_types))

            return code_lines, comment_lines, blank_lines

        except Exception as e:
            Logger.warning(
                f"Pygments error for {filename}: {e}. Falling back to simple detection."
            )

    # Fallback to simple detection
    # Comment patterns for different languages
    single_line_comments = {
        ".py": "#",
        ".js": "//",
        ".jsx": "//",
        ".ts": "//",
        ".tsx": "//",
        ".java": "//",
        ".cpp": "//",
        ".c": "//",
        ".h": "//",
        ".cs": "//",
        ".php": "//",
        ".go": "//",
        ".rs": "//",
        ".swift": "//",
        ".sql": "--",
        ".sh": "#",
    }

    single_comment = single_line_comments.get(extension, None)

    for line in lines:
        stripped = line.strip()

        # Blank line
        if not stripped:
            blank_lines += 1
            continue

        # Check for single-line comments
        if single_comment and stripped.startswith(single_comment):
            comment_lines += 1
        # Python docstrings (simplified detection)
        elif extension == ".py" and (
            stripped.startswith('"""') or stripped.startswith("'''")
        ):
            comment_lines += 1
        # HTML/XML comments (simplified)
        elif extension in {".html", ".htm", ".xml"} and stripped.startswith("<!--"):
            comment_lines += 1
        # CSS comments (simplified)
        elif extension in {".css", ".scss"} and stripped.startswith("/*"):
            comment_lines += 1
        # Documentation files - treat all non-blank lines as content
        elif extension in DOCUMENTATION_EXTENSIONS:
            code_lines += 1
        # Default: treat as code
        else:
            code_lines += 1

    return code_lines, comment_lines, blank_lines


def process_file(file_path: Path) -> FileStats:
    """Process a single file and return its statistics with error handling.

    Reads the file with encoding fallback, computes line counts and tokens,
    and handles errors gracefully.

    Args:
        file_path: Path to the file to process.

    Returns:
        FileStats object with computed statistics.
    """
    try:
        # Read file with proper error handling
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

        extension = file_path.suffix.lower()
        lines_total = len(content.splitlines())
        lines_code, lines_comments, lines_blank = count_lines_by_type(
            content, extension, str(file_path)
        )

        # Count tokens if tokenizer is available
        tokens = 0
        if openai_tokenizer:
            try:
                tokens = len(openai_tokenizer.encode(content))
            except Exception:
                tokens = 0

        # Get file size
        size_bytes = file_path.stat().st_size

        return FileStats(
            path=file_path,
            extension=extension,
            lines_total=lines_total,
            lines_code=lines_code,
            lines_comments=lines_comments,
            lines_blank=lines_blank,
            tokens=tokens,
            size_bytes=size_bytes,
        )

    except (PermissionError, FileNotFoundError, OSError) as e:
        Logger.warning(f"Error processing {file_path}: {e}")
        return FileStats(
            path=file_path,
            extension=file_path.suffix.lower(),
            lines_total=0,
            lines_code=0,
            lines_comments=0,
            lines_blank=0,
            tokens=0,
            size_bytes=0,
        )


def get_all_extensions() -> Set[str]:
    """Get all supported file extensions from mappings.

    Returns:
        Set of all supported lowercase extensions.
    """
    return (
        set(CODE_EXTENSIONS.keys())
        | set(DOCUMENTATION_EXTENSIONS.keys())
        | set(CONFIG_EXTENSIONS.keys())
    )
