"""Tests for the config module."""

import pytest
from codetok.config import Config


def test_config_default_values():
    """Test that config has sensible default values."""
    config = Config()
    
    assert config.path == "."
    assert config.output_file == "codebase_analysis.json"
    assert config.json_only is False
    assert config.parallel is True
    assert config.progress_bar is True
    assert config.exclude_dirs is not None
    assert len(config.exclude_dirs) > 0
    assert 'node_modules' in config.exclude_dirs
    assert '.git' in config.exclude_dirs
    assert config.include_extensions is None
    assert config.exclude_patterns is None
    assert config.respect_gitignore is True
    assert config.generate_charts is False
    assert config.max_workers > 0


def test_config_custom_values():
    """Test config with custom values and non-existent path raises ValueError."""
    custom_excludes = {'.custom', 'build'}
    with pytest.raises(ValueError, match="Analysis path does not exist"):
        Config(
            path="/custom/path",
            output_file="custom.json",
            json_only=True,
            parallel=False,
            progress_bar=False,
            exclude_dirs=custom_excludes,
            include_extensions={'.py', '.js'},
            exclude_patterns=["*test*", "*.tmp"],
            respect_gitignore=False,
            generate_charts=True,
            max_workers=8
        )


def test_config_exclude_dirs_none():
    """Test that exclude_dirs gets populated when None."""
    config = Config(exclude_dirs=None)
    
    # Should be populated in __post_init__
    assert config.exclude_dirs is not None
    assert len(config.exclude_dirs) > 0


def test_config_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError, match="max_workers must be at least 1"):
        Config(max_workers=0)
    
    with pytest.raises(ValueError, match="Analysis path does not exist"):
        Config(path="/non/existent/path")
