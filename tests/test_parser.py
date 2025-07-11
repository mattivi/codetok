"""Tests for the parser module."""

import tempfile
from pathlib import Path

from codetok.parser import count_lines_by_type, get_all_extensions, process_file


class TestLineCountingByType:
    """Test line counting for different file types."""

    def test_python_comment_detection(self) -> None:
        """Test Python comment detection."""
        python_code = '''# This is a comment
def hello():
    """This is a docstring"""
    print("Hello")  # Inline comment
    pass

# Another comment
'''
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            python_code, ".py", "test.py"
        )
        assert code_lines == 13
        assert comment_lines == 3
        assert blank_lines == 0

    def test_javascript_comment_detection(self) -> None:
        """Test JavaScript comment detection."""
        js_code = """// This is a comment
function hello() {
    console.log("Hello"); // Inline comment
}

// Another comment
"""
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            js_code, ".js", "test.js"
        )
        assert code_lines == 13
        assert comment_lines == 3
        assert blank_lines == 0

    def test_markdown_detection(self) -> None:
        """Test Markdown detection."""
        markdown_code = """# Header

This is content.

## Another header
More content.
"""
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            markdown_code, ".md", "test.md"
        )
        assert code_lines == 4
        assert comment_lines == 0
        assert blank_lines == 2

    def test_unknown_extension(self) -> None:
        """Test handling of unknown extensions."""
        unknown_code = """line 1
line 2

line 4
"""
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            unknown_code, ".unknown", "test.unknown"
        )
        assert code_lines == 3
        assert comment_lines == 0
        assert blank_lines == 1

    def test_multiline_comments(self) -> None:
        """Test detection of multiline comments."""
        js_code = """/*
Multi
line
comment
*/
function test() {}
"""
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            js_code, ".js", "test.js"
        )
        assert code_lines == 6
        assert comment_lines == 5
        assert blank_lines == 0

    def test_mixed_content(self) -> None:
        """Test mixed code and comments."""
        py_code = '''def func():
    # comment
    x = 1  # inline
    """
    Doc
    """
    return x
'''
        code_lines, comment_lines, blank_lines = count_lines_by_type(
            py_code, ".py", "test.py"
        )
        assert code_lines == 13
        assert comment_lines == 2
        assert blank_lines == 0


class TestFileProcessing:
    """Test file processing functionality."""

    def test_process_empty_file(self) -> None:
        """Test processing empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            stats = process_file(Path(temp_path))
            assert stats.lines_total == 0
            assert stats.lines_code == 0
            assert stats.lines_comments == 0
            assert stats.lines_blank == 0
            assert stats.size_bytes == 0
            assert stats.extension == ".py"
            assert stats.tokens == 0
        finally:
            Path(temp_path).unlink()

    def test_process_python_file(self) -> None:
        """Test processing Python file."""
        python_content = '''# Test file
def hello():
    """Say hello."""
    print("Hello, world!")

if __name__ == "__main__":
    hello()
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_content)
            temp_path = f.name

        try:
            stats = process_file(Path(temp_path))
            assert stats.lines_total == 7
            assert stats.lines_code == 22
            assert stats.lines_comments == 1
            assert stats.lines_blank == 0
            assert stats.extension == ".py"
            assert stats.size_bytes > 0
            assert stats.tokens > 0  # Assuming tiktoken available
        finally:
            Path(temp_path).unlink()

    def test_process_binary_file(self) -> None:
        """Test handling of binary files."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
            f.write(b"\x00\x01\x02")
            temp_path = f.name

        try:
            stats = process_file(Path(temp_path))
            assert stats.lines_total == 1
            assert stats.lines_code == 1
            assert stats.lines_comments == 0
            assert stats.lines_blank == 0
            assert stats.size_bytes == 3
            assert stats.tokens == 3
        finally:
            Path(temp_path).unlink()

    def test_encoding_fallback(self) -> None:
        """Test encoding fallback works."""
        content = " café ".encode("latin-1")
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            stats = process_file(Path(temp_path))
            assert stats.lines_total == 1
            assert stats.lines_code == 1
            assert stats.size_bytes == len(content)
        finally:
            Path(temp_path).unlink()


def test_get_all_extensions() -> None:
    """Test that get_all_extensions returns the expected extensions."""
    extensions = get_all_extensions()

    # Should include all categories
    assert ".py" in extensions  # code
    assert ".md" in extensions  # documentation
    assert ".json" in extensions  # config
    assert len(extensions) > 10  # Should have many extensions
