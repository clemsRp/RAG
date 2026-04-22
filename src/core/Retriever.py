#!/usr/bin/env python3

# Handle import errors modifying the pyproject.toml
import bm25s
from tqdm import tqdm

from src.DataModels import (
    MinimalSource, UnansweredQuestion,
    MinimalSearchResults, StudentSearchResults,
    BM25_OUTPUT_PATH
)


class Retriever:
    '''
    Class for retrieve datas
    '''

    def __init__(self) -> None:
        '''
        Initialize the retriever

        Args:
            None
        Return:
            None
        '''
        pass

    def retrieve(
                self,
                questions: list[UnansweredQuestion],
                sub_directories: list[str],
                k: int,
                is_dataset: bool = True
            ) -> StudentSearchResults:
        '''
        Retrieve the datas for a given list of questions

        Args:
            questions: list[UnansweredQuestion] =
                The list of prompt to retrieve datas
            sub_directories: str = The sub directories to get the datas
            k: int = The number of search to retrieve
            is_dataset: bool = True if we need to save the results
        Return:
            res: list[MinimalSearchResults] =
                The list of the datas of each questions
        '''
        search_results: list[MinimalSearchResults] = []

        # Handle the tqdm progress bars
        if is_dataset:
            for question in tqdm(questions):
                self._question_pipeline(
                    search_results,
                    question,
                    sub_directories,
                    k
                )

        else:
            for question in questions:
                self._question_pipeline(
                    search_results,
                    question,
                    sub_directories,
                    k
                )

        return StudentSearchResults(
            search_results=search_results,
            k=k
        )

    def _question_pipeline(
                self,
                search_results: list[MinimalSearchResults],
                question: UnansweredQuestion,
                sub_directories: list[str],
                k: int = 10
            ) -> None:
        '''
        Execute a pipeline on a question

        Args:
            search_results: list[MinimalSearchResults] =
                The list of the retrieved sources
            question: UnansweredQuestion =
                The question to execute the pipeline on
            sub_directories: str = The sub directories to get the datas
            k: int = The number of search to retrieve
        Return:
            None
        '''
        # Modify the question
        modified_question: str = self._get_modified_question(question.question)

        # Tokenize the question
        query_tokens = bm25s.tokenize([modified_question])

        all_results: list[dict[str, str | int]] = []
        all_scores: list[float] = []

        # Get all the results
        for sub_directory in sub_directories:

            # Get the k best results
            retriever = bm25s.BM25.load(
                BM25_OUTPUT_PATH + sub_directory,
                load_corpus=True
            )
            result = retriever.retrieve(
                query_tokens, k=k
            )

            all_results.extend(result[0][0])
            all_scores.extend(result[1][0])

        # Filter the results
        all_datas: list[tuple[float, dict[str, str | int]]] = [
            (all_scores[i], all_results[i])
            for i in range(len(all_results))
        ]
        all_datas.sort(key=lambda data: data[0], reverse=True)

        results: list[dict[str, str | int]] = [
            all_datas[j][1] for j in range(min([k, len(all_datas)]))
        ]

        search_results.append(self._convert_results(question, results))

    def _get_modified_question(self, question: str) -> str:
        '''
        Return the modified question

        Args:
            question: str = The question to modify
        Return:
            None
        '''
        return question

    def _convert_results(
                self,
                question: UnansweredQuestion,
                results: list[dict[str, str | int]]
            ) -> MinimalSearchResults:
        '''
        Return the prompt results converted in MinimalSearchResults

        Args:
            question: UnansweredQuestion =
                The question to retrieved the sources
            results: list[dict[str, str | int]] =
                The retrieved datas/sources
        Return:
            res: MinimalSearchResults = The converted datas/sources
        '''
        retrieved_sources: list[MinimalSource] = []

        # Convert each result datas into a MinimalSource
        for result in results:
            retrieved_sources.append(
                MinimalSource(
                    file_path=str(result["file_path"]),
                    first_character_index=int(result["first_character_index"]),
                    last_character_index=int(result["last_character_index"])
                )
            )

        return MinimalSearchResults(
            question_id=question.question_id,
            question=question.question,
            retrieved_sources=retrieved_sources
        )
