#!/usr/bin/env python3

# Handle import error modifying the pyproject.toml
import bm25s

# External imports
from typing import Any
from pathlib import Path

# Project imports
from src.Chunker import Chunker
from src.Retriever import Retriever
from src.Parser import Parser
from src.Answerer import Answerer
from src.Evaluator import Evaluator

# Project DataModels imports
from src.DataModels import (
    MinimalSource, UnansweredQuestion, AnsweredQuestion,
    StudentSearchResults, StudentSearchResultsAndAnswer,
    RagDataset, BM25_OUTPUT_PATH
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
        retriever.save(BM25_OUTPUT_PATH, corpus=sources)

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
        # Get the rag_questions
        parser: Parser = Parser()
        dataset: RagDataset = (
            parser.get_rag_dataset(dataset_path)
        )

        prompts: list[
            AnsweredQuestion | UnansweredQuestion
        ] = dataset.rag_questions

        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question_id=prompt.question_id,
                question=prompt.question
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

        # Answer the question
        answerer: Answerer = Answerer()
        student_search_results_and_answer: StudentSearchResultsAndAnswer = (
            answerer.answer(student_search_results)
        )

        # Print the results
        print(student_search_results_and_answer.model_dump_json(indent=4))

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
        # Get the student_search_results
        parser: Parser = Parser()
        student_search_results: StudentSearchResults = (
            parser.get_student_search_results(student_search_results_path)
        )

        # Answer the question
        answerer: Answerer = Answerer()
        student_search_results_and_answer: StudentSearchResultsAndAnswer = (
            answerer.answer(student_search_results)
        )

        # Save the results
        save_path: str = str(
            save_directory + "/" +
            Path(student_search_results_path).name
        )
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            f.write(
                student_search_results_and_answer.model_dump_json(indent=4)
            )

        nb_questions: int = len(student_search_results.search_results)

        print(
            f"Loaded {len(student_search_results.search_results)} questions "
            f"from {student_search_results_path}\n"
            f"Processed {nb_questions} of {nb_questions} questions\n"
            f"Saved student_search_results_and_answer to {save_path}"
        )

    def evaluate(
                self,
                student_answer_path: str = (
                    "data/output/search_results_and_answer/" +
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
        # Initialize the variables
        parser: Parser = Parser()
        evaluater: Evaluator = Evaluator()
        overlaps: list[int] = [1, 3, 5, 10]
        max_context_length = min([max_context_length, 2000])

        # Get the student answer
        student_answer: StudentSearchResultsAndAnswer = (
            parser.get_student_search_results_and_answer(
                student_answer_path
            )
        )

        # Get the dataset answer
        dataset_answer: RagDataset = (
            parser.get_rag_dataset(
                dataset_path
            )
        )

        # Print the evaluation results
        evaluater.print_evaluation_results(
            student_answer,
            dataset_answer,
            overlaps
        )
