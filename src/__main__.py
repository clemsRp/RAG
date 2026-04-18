#!/usr/bin/env python3

import fire
from src.CliGestion import CliGestion


if __name__ == "__main__":
    try:
        fire.Fire(CliGestion)

    except Exception as e:
        print(e)
