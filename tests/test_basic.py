import pytest
import os
import json
from codetok.analyzer import CodeAnalyzer
from codetok.config import Config

def test_analyze_codebase_creates_json(tmp_path):
    output_file = tmp_path / "report.json"
    config = Config(path=".", output_file=str(output_file), json_only=True)
    analyzer = CodeAnalyzer(config)
    analyzer.analyze()
    assert output_file.exists(), "Output JSON file was not created."
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Check for expected top-level keys
    assert "timestamp" in data
    assert "categories" in data
    assert "summary" in data
