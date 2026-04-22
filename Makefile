
NAME = src
EXEC = python3
DEBUGER = pdb
OLLAMA_FOLDER = ~/ollama_models

install:
	uv sync

start:
	mkdir -p $(OLLAMA_FOLDER)
	export OLLAMA_MODELS=$(OLLAMA_FOLDER)
	ollama serve

run:
	uv run $(EXEC) -m $(NAME)

debug:
	uv run $(EXEC) -m $(DEBUGER) -m $(NAME)

lint:
	uv run flake8 . --exclude=.venv,vllm-0.10.1
	uv run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude "(\.venv|vllm-0.10.1)"

lint-strict:
	uv run flake8 . --exclude=.venv,vllm-0.10.1
	uv run mypy . --exclude "(\.venv|vllm-0.10.1)" --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf *.pyc
	rm -rf .venv .python-version main.py

.PHONY: install start run debug lint lint-strict clean