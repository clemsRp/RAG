#!/usr/bin/env python3

import uuid
from pydantic import BaseModel, Field


BM25_OUTPUT_PATH: str = "data/processed/bm25_index"


class MinimalSource(BaseModel):
    '''
    Manage the minimum needed sources

    Args:
        file_path: str = The path for the source file
        first_character_index: int = The index of the first character
        last_character_index: int = The index of the last character
    Return:
        None
    '''
    file_path: str
    first_character_index: int = Field(ge=0)
    last_character_index: int = Field(ge=0)


class UnansweredQuestion(BaseModel):
    '''
    Manage the unanswered questions

    Args:
        question_id: str = The id of the unanswered question
        question: str = The question
    Return:
        None
    '''
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    '''
    Manage the minimum needed sources

    Args:
        sources: list[MinimalSource] = The list of the sources
            used to answer the question
        answer: str = The answer for the question
    Return:
        None
    '''
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    '''
    Manage the RAG questions datasets

    Args:
        rag_questions: list[AnsweredQuestion | UnansweredQuestion] =
            The list of RAG questions
    Return:
        None
    '''
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    '''
    Manage the serch results

    Args:
        question_id: str = The question id
        question: str = The question
        retrieved_sources: list[MinimalSource] =
            The retrieved sources with the search result
    Return:
        None
    '''
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    '''
    Manage the answer result

    Args:
        answer: str = The answer
    Return:
        None
    '''
    answer: str


class StudentSearchResults(BaseModel):
    '''
    Manage the student search results

    Args:
        search_results: list[MinimalSearchResults] =
            The student search results
        k: int = The number of results requested
    Return:
        None
    '''
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    '''
    Manage the student search results and answers

    Args:
        search_results_and_answer: list[MinimalAnswer] =
            The search results and answers
    Return:
        None
    '''
    search_results: list[MinimalAnswer]
    k: int
