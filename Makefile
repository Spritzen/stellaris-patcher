# Day-to-day commands. `make check` must pass before a change is done.

PY := python3
export PYTHONPATH := src

.PHONY: check lint format test docs

check: lint test docs  ## Lint, type-check, test and check doc links

lint:           ## Ruff (lint + format check) and mypy
	ruff check .
	ruff format --check .
	mypy

format:         ## Fix formatting and safe lint issues
	ruff format .
	ruff check --fix .

test:           ## Run the tests
	$(PY) -m pytest

docs:           ## Check that every link in the docs resolves
	$(PY) tools/check_links.py
