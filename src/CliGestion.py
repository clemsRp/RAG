#!/usr/bin/env python3

from src.Chunker import Chunker


class CliGestion:
    '''
    Commande line gestion class using fire
    '''

    def index(self, max_chunk_size: int = 2000) -> None:
        '''
        Handle the index flag

        Args:
            max_chunk_size: int = The max size of a chunk
        Return:
            None
        '''
        if max_chunk_size > 2000:
            max_chunk_size = 2000

        chunker: Chunker = Chunker()

        chunker.chunk_files(max_chunk_size)

    def answer(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the answer flag

        Args:
            prompt: str = The prompt to answer
            k: int = The number of answer to retrieve
        Return
            None
        '''
        pass

    def answer_dataset(
                self,
                student_search_results_path: str = (
                    "data/output/search_results/dataset_docs_public.json"
                ),
                save_directory: str = (
                    "data/output/search_results_and_answer"
                )
            ) -> None:
        '''
        Handle the answer_dataset flag

        Args:
            student_search_results_path: str =
                The path to the student serach result
            save_directory: str = The directory to save the result
        Return
            None
        '''
        pass

    def search(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the search flag

        Args:
            prompt: str = The prompt to search
            k: int = The number of search to retrieve
        Return
            None
        '''
        pass

    def search_dataset(
                self,
                dataset_path: str = (
                    "data/datasets/UnansweredQuestions" +
                    "/dataset_docs_public.json"
                ),
                save_directory: str = "data/output/search_results",
                k: int = 10
            ) -> None:
        '''
        Handle the search_data flag

        Args:
            dataset_path: str = The path to get the datasets
        Return
            None
        '''
        pass

    def evaluate(self) -> None:
        '''
        Handle the evaluate flag

        Args:
            None
        Return:
            None
        '''
        pass
