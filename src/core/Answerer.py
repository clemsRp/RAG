#!/usr/bin/env python3

# Handle import error modifying the pyproject.toml
from tqdm import tqdm
from transformers import pipeline


from src.DataModels import (
    StudentSearchResults,
    MinimalSource,
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResultsAndAnswer
)


class Answerer:
    '''
    Class to answer questions
    '''

    def __init__(self, model: str) -> None:
        '''
        Initialize the answerer

        Args:
            model: str = The LLM model to use
        Return:
            None
        '''
        self.generator = pipeline(
            "text-generation",
            model=model,
            dtype="auto",
            device_map="auto"
        )

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
        # Get all the student sources in one str
        all_sources: list[str] = []
        for source in result.retrieved_sources:
            all_sources.append(
                self._get_source_text(source)
            )

        llm_sources: str = "\n---\n".join(all_sources)

        # Format the message
        messages = [
            {
                "role": "system",
                "content": f"Answer using this: '{llm_sources}'"
            },
            {
                "role": "user",
                "content": result.question
            }
        ]

        # Get the answer
        outputs = self.generator(
            messages,
            max_new_tokens=128,
            do_sample=False
        )

        return str(outputs[0]['generated_text'][-1]['content'])

    def _get_source_text(
                self,
                source: MinimalSource
            ) -> str:
        '''
        Return the text of the corresponding source

        Args:
            source: MinimalSource = The source to get the text
        Return:
            None
        '''
        try:
            with open(source.file_path, 'r') as f:
                content: str = f.read()
                if source.first_character_index >= len(content) - 1 or \
                        source.first_character_index < 0:
                    raise Exception(
                        "Invalid source, invalid first_character_index "
                        f"({source.first_character_index}), "
                        f"source: (0-{len(content) - 1})"
                    )

                if source.last_character_index > len(content) - 1 or \
                        source.last_character_index < 0:
                    raise Exception(
                        "Invalid source, invalid last_character_index "
                        f"({source.last_character_index}), "
                        f"source: (0-{len(content) - 1})"
                    )

                return content[
                    source.first_character_index:
                    source.last_character_index + 1
                ]

        except FileNotFoundError as e:
            raise Exception(
                f"{e}: Check that the file exist and the path is correct"
            )
        except PermissionError as e:
            raise Exception(
                f"{e}: You don't have the rights "
                f"for the file: '{source.file_path}'"
            )
        except Exception as e:
            raise Exception(f"Error: {e}")
