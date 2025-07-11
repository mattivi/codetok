#!/bin/bash

set -e

# Formatters
black codetok tests examples
isort codetok tests examples

# Linters
flake8 codetok tests examples
mypy codetok tests examples
bandit -r codetok

echo "\nAll checks passed!" 