#!/usr/bin/env python3

import bm25s
from typing import Any

from src.DataModels import (
    MinimalSource
)
from src.Constants import BM25_OUTPUT_PATH


class Indexer:
    '''
    Class to index datas
    '''

    def __init__(self) -> None:
        '''
        Initialize the indexer class

        Args:
            None
        Return:
            None
        '''
        pass

    def index(
                self,
                chunks: list[tuple[str, MinimalSource]],
                sub_directory: str
            ) -> None:
        '''
        Index given datas in a given folder

        Args:
            chunks: list[tuple[str, MinimalSource]] =
                The datas to index and save
            sub_directory: str = The sub directory to save the datas
        Return:
            None
        '''
        # Get the content and the datas about the chunks
        texts: list[str] = [
            chunk[0] for chunk in chunks
        ]
        sources: list[dict[str, Any]] = [
            chunk[1].model_dump() for chunk in chunks
        ]

        # Tokenize the contents
        corpus_tokens = bm25s.tokenize(texts)

        # Link the contents with the datas
        retriever = bm25s.BM25(corpus=sources)
        retriever.index(corpus_tokens)

        # Save the datas
        retriever.save(BM25_OUTPUT_PATH + sub_directory, corpus=sources)
