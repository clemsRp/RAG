#!/usr/bin/env python3

import bm25s
from typing import Any
from src.Chunker import Chunker
from src.DataModels import MinimalSource


class CliGestion:
    '''
    Commande line gestion class using fire
    '''

    def index(self, max_chunk_size: int = 2000) -> None:
        '''
        Handle the index flag

        Args:
            max_chunk_size: int = The max size of a chunk
        Return:
            None
        '''
        # Handle the max_chunk_size
        max_chunk_size = min([max_chunk_size, 2000])

        # Chunk the files
        chunker: Chunker = Chunker()
        chunks: list[tuple[str, MinimalSource]] = (
            chunker.chunk_files(max_chunk_size)
        )

        # Get the content and the datas about the chunks
        texts: list[str] = [
            chunk[0] for chunk in chunks
        ]
        sources: list[dict[str, Any]] = [
            chunk[1].model_dump() for chunk in chunks
        ]

        # Tokenize the contents
        corpus_tokens = bm25s.tokenize(texts)

        # Link the contents with the datas
        retriever = bm25s.BM25(corpus=sources)
        retriever.index(corpus_tokens)

        # Save the datas
        retriever.save("data/processed/", corpus=sources)

        print("Ingestion complete! Indices saved under data/processed/")

    def search(self, prompt: str, k: int = 10) -> list[dict[str, str | int]]:
        '''
        Handle the search flag

        Args:
            prompt: str = The prompt to search
            k: int = The number of search to retrieve
        Return
            results: list[dict[str, str | int]] =
                The top k best results
        '''
        query_tokens = bm25s.tokenize([prompt])

        # Get the k best results
        retriever = bm25s.BM25.load("data/processed/", load_corpus=True)
        results = retriever.retrieve(query_tokens, k=k)[0]

        # Print the results
        start: str = "first_character_index"
        end: str = "last_character_index"

        print(f"Top {k} best results:\n")

        for (i, r) in enumerate(results[0]):
            complete: int = (len(str(k)) - len(str(i + 1)))
            print(
                    f"{" " * complete}{i + 1}. "
                    f"{r["file_path"]}: {r[start]} -> {r[end]}"
                )

    def search_dataset(
                self,
                dataset_path: str = (
                    "data/datasets/UnansweredQuestions" +
                    "/dataset_docs_public.json"
                ),
                save_directory: str = "data/output/search_results",
                k: int = 10
            ) -> None:
        '''
        Handle the search_data flag

        Args:
            dataset_path: str = The path to get the datasets
        Return
            None
        '''
        pass

    def answer(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the answer flag

        Args:
            prompt: str = The prompt to answer
            k: int = The number of answer to retrieve
        Return
            None
        '''
        query_tokens = bm25s.tokenize([prompt])

        # Get the k best results
        retriever = bm25s.BM25.load("data/processed/", load_corpus=True)
        results = retriever.retrieve(query_tokens, k=k)[0]

        # Print the results
        start: str = "first_character_index"
        end: str = "last_character_index"

        print(f"Top {k} best results:\n")

        for (i, r) in enumerate(results[0]):
            complete: int = (len(str(k)) - len(str(i + 1)))
            print(
                    f"{" " * complete}{i + 1}. "
                    f"{r["file_path"]}: {r[start]} -> {r[end]}"
                )

        answer: str = "crappo"

        print(f"\nAnswer: '{answer}'")

    def answer_dataset(
                self,
                student_search_results_path: str = (
                    "data/output/search_results/dataset_docs_public.json"
                ),
                save_directory: str = (
                    "data/output/search_results_and_answer"
                )
            ) -> None:
        '''
        Handle the answer_dataset flag

        Args:
            student_search_results_path: str =
                The path to the student serach result
            save_directory: str = The directory to save the result
        Return
            None
        '''
        pass

    def evaluate(self) -> None:
        '''
        Handle the evaluate flag

        Args:
            None
        Return:
            None
        '''
        pass
