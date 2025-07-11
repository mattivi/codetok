#!/bin/bash

set -e

MODE=${1:-format}

if [ "$MODE" = "check" ]; then
  echo "Running in CHECK mode (CI style)"
  black --check codetok tests examples
  isort --check-only codetok tests examples
else
  echo "Running in FORMAT mode (auto-fix)"
  black codetok tests examples
  isort codetok tests examples
fi

flake8 codetok tests examples
mypy codetok tests examples
bandit -r codetok

echo "\nAll checks passed!" 