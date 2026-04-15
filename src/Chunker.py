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

    def chunk_files(
                self,
                max_chunk_size: int
            ) -> list[MinimalSource]:
        '''
        Chunk the files

        Args:
            max_chunk_size: int = The max size of a chunk
        Return:
            res: list[MinimalSource] =
                The classes to stock the chunk datas
        '''
        files: list[Path] = self._get_files()
        res: list[MinimalSource] = []

        for file in files:
            print(file.suffix)
            continue
            if file.suffix == ".py":
                res += self._chunk_docs_file(file, max_chunk_size)
            elif file.suffix == ".md":
                res += self._chunk_code_file(file, max_chunk_size)
            else:
                raise FileError("Invalid file type")

        return res

    def _get_files(self) -> list[Path]:
        '''
        Return the list of the files to chunk

        Args:
            None
        Return
            res: list[Path] = All the files to chunk
        '''
        res: list[Path] = []

        folder: Path = Path("./vllm-0.10.1/")
        for file in folder:
            if file.is_file() and file.suffix in [".py", ".md"]:
                res.append(file)

        return res

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
