#!/usr/bin/env python3

import bm25s
import json
from typing import Any
from pathlib import Path
from src.Chunker import Chunker
from src.Retriever import Retriever
from src.Evaluator import Evaluator
from src.DataModels import (
    MinimalSource, UnansweredQuestion, StudentSearchResults, BM25_PATH
)


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
        retriever.save(BM25_PATH, corpus=sources)

        print("Ingestion complete! Indices saved under data/processed/")

    def search(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the search flag

        Args:
            prompt: str = The prompt to search
            k: int = The number of search to retrieve
        Return
            None
        '''
        # Convert the prompt into an UnAnsweredQuestion
        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question=prompt
            )
        ]

        # Get the retrieved datas
        retriever: Retriever = Retriever()
        student_search_results: StudentSearchResults = (
            retriever.retrieve(questions, k)
        )

        # Print the results
        print(student_search_results.model_dump_json(indent=4))

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
            save_directory: str = The path for save the generated datas
            k: int = The number of answer to retrieve
        Return
            None
        '''
        # Get the prompts
        try:
            with open(dataset_path, 'r') as f:
                dataset: dict[str, Any] = json.load(f)

        except FileNotFoundError as e:
            raise Exception(
                f"{e}: Check that the file exist and the path is correct"
            )
        except PermissionError as e:
            raise Exception(
                f"{e}: You don't have the rights "
                f"for the file: '{dataset_path}'"
            )

        prompts: list[dict[str, str]] = dataset["rag_questions"]

        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question_id=prompt["question_id"],
                question=prompt["question"]
            ) for prompt in prompts
        ]
        # Get the retrieved datas (getting the prompts in the retriever)
        retriever: Retriever = Retriever()
        student_search_results: StudentSearchResults = (
            retriever.retrieve(questions, k)
        )

        # Save the results
        save_path: str = save_directory + "/" + Path(dataset_path).name
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            f.write(student_search_results.model_dump_json(indent=4))

        print(f"Saved student_search_results to {save_path}")

    def answer(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the answer flag

        Args:
            prompt: str = The prompt to answer
            k: int = The number of answer to retrieve
        Return
            None
        '''
        # TODO: Adapt search adding the answer system
        pass

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
        # TODO: Adapt search_dataset adding the answer system
        pass

    def evaluate(
                self,
                student_answer_path: str = (
                    "data/output/search_results/" +
                    "dataset_docs_public.json"
                ),
                dataset_path: str = (
                    "data/datasets/AnsweredQuestions/" +
                    "dataset_docs_public.json"
                ),
                k: int = 10,
                max_context_length: int = 2000
            ) -> None:
        '''
        Handle the evaluate flag

        Args:
            student_answer_path: str =
                The path for the answer generated
            dataset_path: str = The path to get the datasets
            k: int = The number of search to retrieve
            max_context_length: int = The max size of the context
        Return:
            None
        '''
        # Handle the max_context_length
        max_context_length = min([max_context_length, 2000])

        overlaps: list[int] = [1, 3, 5, 10]

        evaluater: Evaluator = Evaluator()
        evaluater.print_evaluation_results(overlaps)
