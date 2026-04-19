#!/usr/bin/env python3

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

        for result in student_search_results.search_results:
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

        return StudentSearchResultsAndAnswer(
            search_results=search_results,
            k=student_search_results.k
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
