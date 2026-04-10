
install:
	uv sync

run:
	uv run python3 -m src

debug:
	uv run python3 -m pdb -m src

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf .mypy_cache
	rm -rf .venv
	rm -rf src/__pycache__
	rm -rf __pycache__
	rm -rf .vscode

.PHONY: install run debug lint clean fclean