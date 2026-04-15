#!/usr/bin/env python3

from pathlib import Path
from src.DataModels import MinimalSource, FileError


class Chunker:
    '''
    Class for chunk a file
    '''

    def __init__(self) -> None:
        '''
        Initialize the chunker

        Args:
            None
        Return:
            None
        '''
        pass

    def chunk_file(
                self,
                file: Path
            ) -> list[MinimalSource]:
        '''
        Chunk a file

        Args:
            file: Path = The file to chunk
        Return:
            res: list[MinimalSource] =
                The classes to stock the chunk datas
        '''
        print(file.suffix)
        if file.suffix == ".py":
            return self._chunk_docs_file(file)
        elif file.suffix == ".md":
            return self._chunk_code_file(file)
        else:
            raise FileError("Invalid file type")

    def _chunk_docs_file(
                self,
                file: Path
            ) -> list[MinimalSource]:
        '''
        Return the chunked file

        Args:
            file: Path = The file to chunk
        Return:
            res: list[MinimalSource] =
                The classes to stock the chunk datas
        '''
