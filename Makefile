# Project management tasks.

VENV = .venv
PYTHON = . $(VENV)/bin/activate && python
PYTEST = $(PYTHON) -m pytest


$(VENV)/.make-update: pyproject.toml
	python -m venv $(VENV)
	$(PYTHON) -m pip install -U pip -e .
	$(PYTHON) -m pip install ".[dev]"
	touch $@


.PHONY: dev
dev: $(VENV)/.make-update


.PHONY: test
test: dev
	$(PYTEST) tests/
