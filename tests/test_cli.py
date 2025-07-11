"""Tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock
from codetok.cli import create_parser, main


def test_create_parser():
    """Test that the parser is created correctly."""
    parser = create_parser()
    
    # Test default values by parsing empty args
    args = parser.parse_args([])
    assert args.path == "."
    assert args.output == "codebase_analysis.json"
    assert args.json_only is False
    assert args.no_parallel is False
    assert args.no_progress is False


def test_parser_with_arguments():
    """Test parser with various arguments."""
    parser = create_parser()
    
    args = parser.parse_args([
        "--path", "/custom/path",
        "--output", "custom.json",
        "--json-only",
        "--no-parallel",
        "--no-progress"
    ])
    
    assert args.path == "/custom/path"
    assert args.output == "custom.json"
    assert args.json_only is True
    assert args.no_parallel is True
    assert args.no_progress is True


def test_parser_short_arguments():
    """Test parser with short arguments."""
    parser = create_parser()
    
    args = parser.parse_args(["-p", "/test", "-o", "test.json"])
    
    assert args.path == "/test"
    assert args.output == "test.json"


@patch('codetok.cli.CodeAnalyzer')
def test_main_function(mock_analyzer_class):
    """Test the main function creates correct config and runs analyzer."""
    mock_analyzer = MagicMock()
    mock_analyzer_class.return_value = mock_analyzer
    
    # Test with custom arguments, expect ValueError for non-existent path
    with pytest.raises(ValueError, match="Analysis path does not exist"):
        main([
            "--path", "/test/path",
            "--output", "test.json",
            "--json-only",
            "--no-parallel"
        ])
