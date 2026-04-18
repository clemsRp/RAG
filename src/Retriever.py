#!/usr/bin/env python3

import bm25s
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
                k: int
            ) -> StudentSearchResults:
        '''
        Retrieve the datas for a given list of questions

        Args:
            questions: list[UnansweredQuestion] =
                The list of prompt to retrieve datas
            k: int = The number of search to retrieve
        Return:
            res: list[MinimalSearchResults] =
                The list of the datas of each questions
        '''
        search_results: list[MinimalSearchResults] = []

        for question in questions:

            # Tokenize the question
            query_tokens = bm25s.tokenize([question.question])

            # Get the k best results
            retriever = bm25s.BM25.load(
                BM25_OUTPUT_PATH,
                load_corpus=True
            )
            results: list[dict[str, str | int]] = (
                retriever.retrieve(query_tokens, k=k)[0][0]
            )

            search_results.append(self._convert_results(question, results))

        return StudentSearchResults(
            search_results=search_results,
            k=k
        )

    def _convert_results(
                self,
                question: UnansweredQuestion,
                results: list[dict[str, str | int]]
            ) -> MinimalSearchResults:
        '''
        Return the prompt results converted in MinimalSearchResults

        Args:
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
