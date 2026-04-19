#!/usr/bin/env python3

# Handle import error modifying the pyproject.toml
from tqdm import tqdm

from src.DataModels import (
    StudentSearchResults,
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResultsAndAnswer
)


class Answerer:
    '''
    Class to answer questions
    '''

    def __init__(self) -> None:
        '''
        Initialize the answerer

        Args:
            None
        Return:
            None
        '''
        pass

    def answer(
                self,
                student_search_results: StudentSearchResults
            ) -> StudentSearchResultsAndAnswer:
        '''
        Answer the given questions

        Args:
            student_search_results: StudentSearchResults =
                The retrieved sources and the questions
        Return:
            res: StudentSearchResultsAndAnswer =
                The search_results that contains the answers
        '''
        search_results: list[MinimalAnswer] = []

        # Handle the tqdm progress bars
        if len(student_search_results.search_results) > 1:
            for result in tqdm(student_search_results.search_results):
                self._answer_pipeline(
                    search_results,
                    result
                )

        else:
            for result in student_search_results.search_results:
                self._answer_pipeline(
                    search_results,
                    result
                )

        return StudentSearchResultsAndAnswer(
            search_results=search_results,
            k=student_search_results.k
        )

    def _answer_pipeline(
                self,
                search_results: list[MinimalAnswer],
                result: MinimalSearchResults
            ) -> None:
        '''
        Execute a pipeline on an answer

        Args:
            search_results: list[MinimalAnswer] =
                The list of the answers
            result: MinimalSearchResults =
                The student search results
        Return:
            None
        '''
        answer: str = self._get_answer(
            result
        )
        search_results.append(
            MinimalAnswer(
                question_id=result.question_id,
                question=result.question,
                answer=answer,
                retrieved_sources=result.retrieved_sources
            )
        )

    def _get_answer(self, result: MinimalSearchResults) -> str:
        '''
        Return the answer of the given question

        Args:
            result: MinimalSearchResults = The question datas
        Return:
            answer: str = The answer of the question
        '''
        return "salut c est paulo et bienvenue dans un placard"
