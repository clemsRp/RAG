#!/usr/bin/env python3

from src.DataModels import (
    RagDataset,
    StudentSearchResultsAndAnswer
)


class Evaluator:
    '''
    Class for evaluate the datas
    '''

    def __init__(self) -> None:
        '''
        Initialize the evaluater

        Args:
            None
        Return:
            None
        '''
        pass

    def print_evaluation_results(
                self,
                student_answer: StudentSearchResultsAndAnswer,
                dataset_answer: RagDataset,
                overlaps: list[int]
            ) -> None:
        '''
        Print the evaluation results

        Args:
            overlaps: list[int] = The different overlap to check
        Return:
            None
        '''
        # Handle invalid overlaps
        if any(ov > 100 or ov < 0 for ov in overlaps):
            raise Exception("Invalid overlap value")

        # Print datas
        is_valid_data: bool = True
        print(f"Student data is valid: {is_valid_data}")

        nb_questions: int = 100
        print(f"Total number of questions: {nb_questions}")
        print(f"Total number of questions with sources: {nb_questions}")
        print(
            "Total number of questions with "
            f"student sources: {nb_questions}\n"
        )

        # Print Recall
        print(
            "Evaluation Results\n"
            "========================================"
        )

        print(f"Questions evaluated: {nb_questions}")

        for overlap in overlaps:
            score: float = self._get_score(
                overlap
            ) / nb_questions * 100
            print(f"Recall@{overlap}: {score:.3f}")

    def _get_score(self, overlap: int) -> int:
        '''
        Return the Recall@k score

        Args:
            overlap: int = The current overlap for the Recall@k
        Return
            res: int = The Recall@k score
        '''
        res: int = 0

        # TODO: Iter the questions and get their scores

        return res

    def _get_chunk_score(
                self,
                overlap: int,
                generated: tuple[int, int],
                needed: tuple[int, int]
            ) -> int:
        '''
        Return the Recall@k score

        Args:
            overlap: int = The current overlap for the Recall@k
            generated: tuple[int, int] = The generated chunk start/end
            needed: tuple[int, int] = The needed chunk start/end
        Return:
            res: int = The Recall@k score
        '''
        # Calculate the true overlap
        common_start: int = max([
            generated[0], needed[0]
        ])
        common_end: int = min([
            generated[1], needed[1]
        ])

        score: float = max([
            common_end - common_start, 0
        ]) / (needed[1] - needed[0]) * 100

        return int(score >= overlap)
