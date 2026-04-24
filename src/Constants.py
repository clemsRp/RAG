#!/usr/bin/env python3

# Ingest system
VLLM_FOLDER: str = "./data/raw/vllm-0.10.1/"
BM25_OUTPUT_PATH: str = "data/processed/bm25_index/"

# Answerer system
LLM_MODEL: str = "qwen"
HOST: str = "http://localhost:11434"

# Bonus

#  1. AST
AST: bool = False

#  2. Query expansion
QUERY_SEMANTIC: bool = False

#  3. Hybrid retriaval
CODE_PATH: str = "code/"
DOCS_PATH: str = "docs/"

#  4. Multi-Threading
MULTI_THREADING: bool = False
