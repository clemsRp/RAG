#!/usr/bin/env python3

from src.DataModels import (
    MinimalAnswer,
    StudentSearchResultsAndAnswer,
    AnsweredQuestion,
    RagDataset
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

        # Calculate the questions stats
        total_questions: int = len(dataset_answer.rag_questions)
        sourced_questions: int = len([
            q for q in dataset_answer.rag_questions
            if len(q.sources) > 0
        ])
        sourced_student_questions: int = len([
            q for q in student_answer.search_results
            if len(q.retrieved_sources) > 0
        ])

        # Print the questions stats
        print(f"Total number of questions: {total_questions}")
        print(f"Total number of questions with sources: {sourced_questions}")
        print(
            "Total number of questions with "
            f"student sources: {sourced_student_questions}\n"
        )

        # Print Recall
        print(
            "Evaluation Results\n"
            "========================================"
        )

        # Calculate the evaluated questions
        evaluated_questions: list[tuple[
            MinimalAnswer, AnsweredQuestion
        ]] = []

        for student_q in student_answer.search_results:
            for dataset_q in dataset_answer.rag_questions:
                same_q: bool = student_q.question_id == dataset_q.question_id
                dataset_has_source: bool = len(dataset_q.sources) > 0
                if same_q and dataset_has_source:
                    evaluated_questions.append(
                        (student_q, dataset_q)
                    )

        print(f"Questions evaluated: {len(evaluated_questions)}")

        # Calculate and print the Recall@k scores
        for overlap in overlaps:
            score: float = self._get_score(
                evaluated_questions,
                overlap
            ) / len(evaluated_questions) * 100
            print(f"Recall@{overlap}: {score:.3f}")

    def _get_score(
                self,
                evaluated_questions: list[tuple[
                    MinimalAnswer, AnsweredQuestion
                ]],
                overlap: int
            ) -> float:
        '''
        Return the Recall@k score

        Args:
            evaluated_questions: list[tuple[
                MinimalAnswer, AnsweredQuestion
            ]] = The question to calculte the Recall@k score
            overlap: int = The current overlap for the Recall@k
        Return
            res: int = The Recall@k score
        '''
        res: float = 0

        for (student_q, dataset_q) in evaluated_questions:
            correcte_questions: int = 0
            for dataset_source in dataset_q.sources:
                for student_source in student_q.retrieved_sources:
                    if self._is_correcte_source(
                                    overlap,
                                    (
                                        student_source.first_character_index,
                                        student_source.last_character_index
                                    ),
                                    (
                                        dataset_source.first_character_index,
                                        dataset_source.last_character_index
                                    )
                            ):
                        correcte_questions += 1
                        break

            res += correcte_questions / len(dataset_q.sources)

        return res

    def _is_correcte_source(
                self,
                overlap: int,
                student_chunk: tuple[int, int],
                dataset_chunk: tuple[int, int]
            ) -> int:
        '''
        Return the Recall@k score

        Args:
            overlap: int = The current overlap for the Recall@k
            student_chunk: tuple[int, int] = The student_chunk chunk start/end
            dataset_chunk: tuple[int, int] = The dataset_chunk chunk start/end
        Return:
            res: int = The Recall@k score
        '''
        # Calculate the true overlap
        common_start: int = max([
            student_chunk[0], dataset_chunk[0]
        ])
        common_end: int = min([
            student_chunk[1], dataset_chunk[1]
        ])

        score: float = max([
            common_end - common_start, 0
        ]) / (dataset_chunk[1] - dataset_chunk[0]) * 100

        return score >= overlap
