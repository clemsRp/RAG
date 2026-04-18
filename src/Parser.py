#!/usr/bin/env python3

import json
from typing import Any
from src.DataModels import (
    StudentSearchResults,
    StudentSearchResultsAndAnswer
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

    def get_student_search_results(self, file_path: str):
        '''
        Return the student_search_results

        Args:
            file_path: str = The path of the file to parse
        Return:
            res: StudentSearchResultsAndAnswer =
                The student_search_results
        '''
        try:
            with open(file_path, 'r') as f:
                dataset_search_json: dict[str, Any] = json.load(f)

        except FileNotFoundError as e:
            raise Exception(
                f"{e}: Check that the file exist and the path is correct"
            )
        except PermissionError as e:
            raise Exception(
                f"{e}: You don't have the rights "
                f"for the file: '{file_path}'"
            )

        dataset_search: StudentSearchResults = (
            StudentSearchResults(**dataset_search_json)
        )

        return dataset_search

    def get_student_search_results_and_answer(self, file_path: str):
        '''
        Return the student_search_results_and_answer

        Args:
            file_path: str = The path of the file to parse
        Return:
            res: StudentSearchResultsAndAnswer =
                The student_search_results_and_answer
        '''
        try:
            with open(file_path, 'r') as f:
                dataset_answer_json: dict[str, Any] = json.load(f)

        except FileNotFoundError as e:
            raise Exception(
                f"{e}: Check that the file exist and the path is correct"
            )
        except PermissionError as e:
            raise Exception(
                f"{e}: You don't have the rights "
                f"for the file: '{file_path}'"
            )

        dataset_answer: StudentSearchResultsAndAnswer = (
            StudentSearchResultsAndAnswer(**dataset_answer_json)
        )

        return dataset_answer
