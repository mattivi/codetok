# codetok

[![Build Status](https://github.com/riccardo/LoC/actions/workflows/ci.yml/badge.svg)](https://github.com/riccardo/LoC/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/codetok.svg)](https://badge.fury.io/py/codetok)
[![codecov](https://codecov.io/gh/riccardo/LoC/branch/main/graph/badge.svg)](https://codecov.io/gh/riccardo/LoC)
[![Downloads](https://pepy.tech/badge/codetok)](https://pepy.tech/project/codetok)

> **codetok** is a blazing-fast, extensible codebase analysis tool that counts lines of code, comments, blank lines, and OpenAI tokens across your project. Designed for developers, researchers, and open source maintainers who want deep insight into their codebase.

---

## Why Use codetok?

Unlike traditional tools like cloc or tokei, codetok:
- Integrates OpenAI token counting for AI-related workflows (e.g., estimating prompt costs).
- Uses advanced parsing (via Pygments) for accurate comment/code detection across 20+ languages.
- Provides categorized reports (code, docs, config) with JSON output for automation.
- Supports parallel processing and customizable filters for large codebases.
- Is lightweight, extensible, and Python-based for easy integration.

Perfect for auditing projects, estimating AI processing costs, or generating reports for stakeholders.

## 🚀 Features
- Counts SLOC (source lines of code), comments, blank lines, and OpenAI tokens (cl100k_base encoding).
- Supports 20+ languages/extensions including Python, JS/TS, HTML/CSS, Java, C++, and more.
- Automatic exclusion of common directories (e.g., node_modules, .git, build artifacts).
- Parallel processing with configurable workers for speed on large repos.
- Customizable filters: include/exclude by extension or glob patterns.
- Detailed console output with icons and summaries.
- JSON reports for scripting/integration, including breakdowns by category and extension.
- Progress bars (via tqdm) and verbose logging.
- Extensible: Add custom language support or parsers easily.

## 📦 Installation

Install from PyPI:

```bash
pip install codetok
```

Or clone and install locally:

```bash
git clone https://github.com/riccardo/LoC.git
cd LoC
pip install .
```

For development:

```bash
pip install -e .[dev]
```

Note: Token counting requires `tiktoken`; advanced parsing requires `pygments` (both installed automatically).

## 📝 Usage

Basic analysis of current directory:

```bash
codetok
```

Analyze a specific path:

```bash
codetok --path /path/to/project
```

Generate only JSON report:

```bash
codetok --json-only --output my_report.json
```

Filter by extensions and exclude patterns:

```bash
codetok --include-extensions .py .js --exclude-patterns "*test*" "*_backup*"
```

Limit parallel workers:

```bash
codetok --max-workers 4
```

Disable features:

```bash
codetok --no-parallel --no-progress
```

View help:

```bash
codetok --help
```

### Example Output

```
════════════════════════════════════════════════════════════════════════════════
🔍 CODEBASE ANALYSIS TOOL
════════════════════════════════════════════════════════════════════════════════
ℹ️ Scanning for files to analyze in: .
✅ Found 42 files to analyze
ℹ️ Excluded directories: .cache, .mypy_cache, ...
✅ File processing completed!
ℹ️ Categorizing files...

... [detailed stats] ...

✅ Detailed report saved to: codebase_analysis.json
```

See [examples/](examples/) for scripting usage and sample JSON output.

## Limitations

- Token counting uses OpenAI's cl100k_base (GPT-3.5/4 compatible); other models may vary.
- Binary files are skipped; only text files with supported extensions are analyzed.
- Comment detection falls back to simple rules if Pygments fails or is unavailable.
- Very large files (>10MB) may impact performance; use filters to optimize.

For issues or feature requests, open a GitHub issue.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, code style, and how to get started. Key areas:
- Adding language support (update parser.py and LEXER_MAPPING).
- Improving tests (aim for 90%+ coverage).
- Documentation enhancements.

Use pre-commit hooks for linting/formatting.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> Made with ❤️ by the codetok community.
