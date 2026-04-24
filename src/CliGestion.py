#!/usr/bin/env python3

# External imports
from pathlib import Path
from pydantic import ValidationError

# Project imports
from src.core.Chunker import Chunker
from src.core.Indexer import Indexer
from src.core.Retriever import Retriever
from src.core.Parser import Parser
from src.core.Answerer import Answerer
from src.core.Evaluator import Evaluator

# Project DataModels imports
from src.DataModels import (
    MinimalSource, UnansweredQuestion, AnsweredQuestion,
    StudentSearchResults, StudentSearchResultsAndAnswer,
    RagDataset
)
from src.Constants import LLM_MODEL, CODE_PATH, DOCS_PATH


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
        # Handle the max_chunk_size
        max_chunk_size = min([max_chunk_size, 2000])

        # Chunk the files
        chunker: Chunker = Chunker()
        chunks: list[tuple[str, MinimalSource]] = (
            chunker.chunk_files(max_chunk_size)
        )

        # Index the .py and .md
        indexer: Indexer = Indexer()

        # Filter chunks in code and docs
        docs_chunks: list[tuple[str, MinimalSource]] = [
            chunk for chunk in chunks
            if Path(chunk[1].file_path).suffix == ".md"
        ]
        code_chunks: list[tuple[str, MinimalSource]] = [
            chunk for chunk in chunks
            if Path(chunk[1].file_path).suffix == ".py"
        ]

        # Save the chunks
        indexer.index(docs_chunks, "docs")
        indexer.index(code_chunks, "code")

        print("Ingestion complete! Indices saved under data/processed/")

    def search(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the search flag

        Args:
            prompt: str = The prompt to search
            k: int = The number of search to retrieve
        Return
            None
        '''
        # Convert the prompt into an UnAnsweredQuestion
        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question=prompt
            )
        ]

        sub_directories: list[str] = [CODE_PATH, DOCS_PATH]

        # Get the retrieved datas
        retriever: Retriever = Retriever()
        student_search_results: StudentSearchResults = (
            retriever.retrieve(questions, sub_directories, k, is_dataset=False)
        )

        # Print the results
        print(student_search_results.model_dump_json(indent=4))

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
            save_directory: str = The path for save the generated datas
            k: int = The number of answer to retrieve
        Return
            None
        '''
        # Get the rag_questions
        parser: Parser = Parser()
        dataset: RagDataset = (
            parser.get_rag_dataset(dataset_path)
        )

        prompts: list[
            AnsweredQuestion | UnansweredQuestion
        ] = dataset.rag_questions

        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question_id=prompt.question_id,
                question=prompt.question
            ) for prompt in prompts
        ]

        sub_directories: list[str] = []
        if "docs" in dataset_path:
            sub_directories.append(DOCS_PATH)
        if "code" in dataset_path:
            sub_directories.append(CODE_PATH)

        # Get the retrieved datas (getting the prompts in the retriever)
        retriever: Retriever = Retriever()
        student_search_results: StudentSearchResults = (
            retriever.retrieve(questions, sub_directories, k)
        )

        # Save the results
        save_path: str = save_directory + "/" + Path(dataset_path).name
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            f.write(student_search_results.model_dump_json(indent=4))

        print(f"Saved student_search_results to {save_path}")

    def answer(self, prompt: str, k: int = 10) -> None:
        '''
        Handle the answer flag

        Args:
            prompt: str = The prompt to answer
            k: int = The number of answer to retrieve
        Return
            None
        '''
        # Convert the prompt into an UnAnsweredQuestion
        questions: list[UnansweredQuestion] = [
            UnansweredQuestion(
                question=prompt
            )
        ]

        sub_directories: list[str] = [CODE_PATH, DOCS_PATH]

        # Get the retrieved datas
        retriever: Retriever = Retriever()
        student_search_results: StudentSearchResults = (
            retriever.retrieve(questions, sub_directories, k, is_dataset=False)
        )

        # Answer the question
        answerer: Answerer = Answerer(LLM_MODEL)
        student_search_results_and_answer: StudentSearchResultsAndAnswer = (
            answerer.answer(student_search_results, is_dataset=False)
        )

        # Print the results
        print(student_search_results_and_answer.model_dump_json(indent=4))

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
        # Get the student_search_results
        parser: Parser = Parser()
        student_search_results: StudentSearchResults = (
            parser.get_student_search_results(student_search_results_path)
        )

        # Answer the question
        answerer: Answerer = Answerer(LLM_MODEL)
        student_search_results_and_answer: StudentSearchResultsAndAnswer = (
            answerer.answer(student_search_results)
        )

        # Save the results
        save_path: str = str(
            save_directory + "/" +
            Path(student_search_results_path).name
        )
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            f.write(
                student_search_results_and_answer.model_dump_json(indent=4)
            )

        nb_questions: int = len(student_search_results.search_results)

        print(
            f"Loaded {len(student_search_results.search_results)} questions "
            f"from {student_search_results_path}\n"
            f"Processed {nb_questions} of {nb_questions} questions\n"
            f"Saved student_search_results_and_answer to {save_path}"
        )

    def evaluate(
                self,
                student_answer_path: str = (
                    "data/output/search_results_and_answer/" +
                    "dataset_docs_public.json"
                ),
                dataset_path: str = (
                    "data/datasets/AnsweredQuestions/" +
                    "dataset_docs_public.json"
                ),
                k: int = 10,
                max_context_length: int = 2000
            ) -> None:
        '''
        Handle the evaluate flag

        Args:
            student_answer_path: str =
                The path for the answer generated
            dataset_path: str = The path to get the datasets
            k: int = The number of search to retrieve
            max_context_length: int = The max size of the context
        Return:
            None
        '''
        # Initialize the variables
        parser: Parser = Parser()
        evaluater: Evaluator = Evaluator()

        nb_sources: list[int] = [
            num for num in [1, 3, 5, 10]
            if num <= k
        ]

        max_context_length = min([max_context_length, 2000])

        try:
            # Get the student answer
            student_answer: StudentSearchResultsAndAnswer = (
                parser.get_student_search_results_and_answer(
                    student_answer_path
                )
            )

        except ValidationError:
            print("Student data is valid: False")
            return

        try:
            # Get the dataset answer
            dataset_answer: RagDataset = (
                parser.get_rag_dataset(
                    dataset_path
                )
            )

        except ValidationError:
            print("Dataset is valid: False")
            return

        # Print the evaluation results
        evaluater.print_evaluation_results(
            student_answer,
            dataset_answer,
            nb_sources,
            max_context_length
        )
