#!/usr/bin/env python3

# Handle import error modifying the pyproject.toml
import fire
from src.CliGestion import CliGestion


if __name__ == "__main__":
    fire.Fire(CliGestion)
