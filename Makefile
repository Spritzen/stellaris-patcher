# Day-to-day commands. `make check` must pass before a change is done.

PY := python3
export PYTHONPATH := src

.PHONY: check lint format test bench docs

check: lint test docs  ## Lint, type-check, test and check doc links

lint:           ## Ruff (lint + format check) and mypy
	ruff check .
	ruff format --check .
	mypy

format:         ## Fix formatting and safe lint issues
	ruff format .
	ruff check --fix .

test:           ## Run the tests (skips timing benchmarks)
	$(PY) -m pytest --benchmark-skip

bench:          ## Run only the timing benchmarks
	$(PY) -m pytest --benchmark-only

docs:           ## Check that every link in the docs resolves
	$(PY) tools/check_links.py
