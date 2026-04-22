#!/usr/bin/env python3

# Handle import error modifying the pyproject.toml
import ollama
from tqdm import tqdm


from src.DataModels import (
    StudentSearchResults,
    MinimalSource,
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResultsAndAnswer,
    HOST
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
        self.model: str = model

        self.client: ollama.Client = ollama.Client(
            HOST,
            timeout=20.0
        )

    def answer(
                self,
                student_search_results: StudentSearchResults,
                is_dataset: bool = True
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
        if is_dataset:
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
        for i in range(min([len(result.retrieved_sources), 3])):
            source = result.retrieved_sources[i]
            all_sources.append(
                self._get_source_text(source)
            )

        llm_sources: str = "\n---\n".join(all_sources)[:500]

        context = f"""ONLY use this sources to answer the question
        Sources :
        {llm_sources}"""

        response = self.client.generate(
            model=self.model,
            prompt=result.question,
            system=context,
            options={
                "temperature": 0.1
            }
        )

        return str(response['response'])

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
                        f"source: (0-{len(content) - 1}) "
                        f"in '{source.file_path}'"
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
