*This project has been created as part of the 42 curriculum by crappo.*

# RAG Against the Machine

## Description
This project is a **Retrieval-Augmented Generation (RAG)** system designed to answer technical questions specifically about the **vLLM repository**. The goal is to provide accurate, source-grounded answers by indexing the codebase and documentation, retrieving relevant snippets using BM25, and generating responses using the **Qwen/Qwen3-0.6B** language model.

## System Architecture
The pipeline follows the standard RAG workflow:
1.  **Ingestion:** Scans the vLLM repository, filters relevant files, and segments them into chunks.
2.  **Indexing:** Processes chunks into a searchable **BM25 index** stored locally.
3.  **Retrieval:** Matches user queries against the index to find the top-k most relevant code or documentation segments.
4.  **Augmentation:** Injects the retrieved context into a structured prompt for the LLM.
5.  **Generation:** The **Qwen** model generates a faithful answer based strictly on the provided context.

## Instructions
### Installation
This project uses `uv` as the package manager.
```bash
make install
```
### Execution
The system provides a CLI via Python Fire:

* **Index the repository:** `uv run python -m src index --max_chunk_size 2000`
* **Search for a query:** `uv run python -m src search "How to configure OpenAI server?" --k 5`
* **Generate an answer:** `uv run python -m src answer "How to configure OpenAI server?"`
* **Evaluate performance:** `uv run python -m moulinette evaluate_student_search_results --student_answer_path <path> --dataset_path <path>`

### Chunking Strategy
To ensure optimal context window usage, the system implements two distinct strategies:

* **Markdown/Text:** Chunked files by **paragraph** and **title** using `\n` and `#`
* **Python Code:** Intelligent segmentation that attempts to keep functions and classes intact while respecting the character limit + Implementation of **AST**.

### Retrieval Method
The primary retrieval mechanism is **BM25** (via the `bm25s` library), chosen for its high performance on technical keywords and code symbols compared to standard TF-IDF + Implementation of the **Query Semantic** system.

### Answerer System
The answerer system use ollama with the given model name.
To run the answer or answer_dataset command, you must execute this commands:
```bash
OLLAMA_NUM_PARALLEL=$(cat /sys/devices/system/cpu/cpu*/topology/core_id | sort -u | wc -l)
mkdir -p ~/ollama_models
export OLLAMA_MODELS=~/ollama_models
ollama serve
```

### Performance Analysis
The system targets the following mandatory thresholds:

* **Recall@5 (Docs):** > 80%
* **Recall@5 (Code):** > 50%

### Design Decisions
* **Pydantic Models:** Used for all data structures to ensure type safety and strict JSON output compliance.
* **Ollama Integration:** Utilized for local LLM inference to meet the 2-second per question generation constraint.
* **Tqdm:** Integrated in all batch operations (indexing, dataset answering) for real-time progress tracking.
* **NTLK** Integrated to implement the **Query semantic** system

### Challenges Faced
* **Path Normalization:** Ensuring file paths in the `MinimalSource` objects matched the ground truth exactly to avoid 0% recall scores.
* **Context Limits:** Balancing the number of retrieved segments ($k$) with the LLM's token limit and the 2-second response time requirement.

### Example usage
```bash
uv run -m src index <max_chunk_size>                                                 	# Ingestion
uv run -m src search <prompt> <k>                                                    	# Search one prompt
uv run -m src search_dataset <dataset_path> <save_directory> <k>                     	# Search a bunch of questions
uv run -m src answer <prompt> <k>                                                    	# Answer one prompt
uv run -m src answer_dataset <student_search_results_path> <save_directory>          	# Answer a bunch of questions
uv run -m src evaluate <student_answer_path> <dataset_path> <k> <max_content_length> 	# Evaluate
```

## Bonus

- 1. Implementation of a tree system for code chunking using **AST**.
- 2. Implementation of the **Query Semantic** system adding synonyms for the important words.
- 3. Implementation of a **multiple retriaval** method using 2 index for better performance.
- 4. Implemenation of a **Multi-Threading** system for a better answerer system performance.
- 5. **High performance** (94 Recall@k score > 80)

### Resources
* **vLLM Documentation:** Reference for the indexed knowledge base.
* **Transformers/HuggingFace:** Documentation for the Qwen model.
* **AI Use:** AI was used to understand key concepts, learn librairiesv with short tutos... All the code was review and in compliance with **flake8/mypy**.