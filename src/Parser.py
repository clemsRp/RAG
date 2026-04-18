#!/usr/bin/env python3

import json
from typing import Any

from src.DataModels import (
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
    RagDataset
)


class Parser:
    '''
    Class for parse the multiple files
    '''

    def __init__(self) -> None:
        '''
        Initialize the parser

        Args:
            None
        Return:
            None
        '''
        pass

    def get_student_search_results(
                    self,
                    student_search_results_path: str
                ) -> StudentSearchResults:
        '''
        Return the student_search_results of the student_search_results_path

        Args:
            student_search_results_path: str = The path for the file
                to get the student_search_results
        Return
            student_search_results: StudentSearchResults =
                The parsed student_search_results
        '''
        # Get the dataset of the file
        dataset: dict[str, Any] = self._get_dataset(
            student_search_results_path
        )

        student_search_results: StudentSearchResults = (
            StudentSearchResults(**dataset)
        )

        return student_search_results
    
    def get_student_search_results_and_answer(
                    self,
                    student_search_results_and_answer_path: str
                ) -> StudentSearchResultsAndAnswer:
        '''
        Return the student_search_results_and_answer of
            the student_search_results_and_answer_path

        Args:
            student_search_results_and_answer_path: str =
                The path for the file to
                get the student_search_results_and_answer
        Return
            student_search_results_and_answer:
                StudentSearchResultsAndAnswer =
                    The parsed student_search_results_and_answer
        '''
        # Get the dataset of the file
        dataset: dict[str, Any] = self._get_dataset(
            student_search_results_and_answer_path
        )

        student_search_results_and_answer: StudentSearchResultsAndAnswer = (
            StudentSearchResultsAndAnswer(**dataset)
        )

        return student_search_results_and_answer

    def get_rag_dataset(
                    self,
                    rag_dataset_path: str
                ) -> RagDataset:
        '''
        Return the rag_dataset of the rag_dataset_path

        Args:
            rag_dataset_path: str = The path for the file
                to get the rag_dataset
        Return
            rag_dataset: RagDataset = The parsed rag_dataset
        '''
        # Get the dataset of the file
        dataset: dict[str, Any] = self._get_dataset(rag_dataset_path)

        rag_dataset: RagDataset = (
            RagDataset(
                **dataset
            )
        )

        return rag_dataset
    
    def _get_dataset(self, file_path: str) -> dict[str, Any]:
        '''
        Return the dataset of a given file_path

        Args:
            file_path: str = The given file_path
        Return
            dataset: dict[str, Any] = The json content of the file_path
        '''
        try:
            with open(file_path, 'r') as f:
                dataset: dict[str, Any] = json.load(f)

                return dataset

        except FileNotFoundError as e:
            raise Exception(
                f"{e}: Check that the file exist and the path is correct"
            )
        except PermissionError as e:
            raise Exception(
                f"{e}: You don't have the rights "
                f"for the file: '{file_path}'"
            )
