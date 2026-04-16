#!/usr/bin/env python3

import ast
from pathlib import Path
from src.DataModels import MinimalSource


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
            ) -> list[tuple[str, MinimalSource]]:
        '''
        Chunk the files

        Args:
            max_chunk_size: int = The max size of a chunk
        Return:
            res: list[tuple[str, MinimalSource]] =
                The classes to stock the chunk datas
        '''
        files: list[Path] = self._get_files()
        res: list[tuple[str, MinimalSource]] = []

        for file in files:
            # Get the content of the file
            content: str = self._get_content(file)

            # Handle the case where file <= 1 chunk
            if len(content) <= max_chunk_size:
                res += [(
                    content,
                    MinimalSource(
                        file_path=str(file),
                        first_character_index=0,
                        last_character_index=max([
                            len(content) - 1,
                            0
                        ])
                    )
                )]

            # Handle the code files
            elif file.suffix == ".py":
                res += self._chunk_code_file(
                    str(file), content, max_chunk_size
                )

            # Handle the docs files
            elif file.suffix == ".md":
                res += self._chunk_docs_file(
                    str(file), content, max_chunk_size
                )

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

        # Init of the starting folder and the stack of folder
        folder: Path = Path("./vllm-0.10.1/")
        folder_stack: list[Path] = [folder]

        # Iter on the root folder with recurcion
        while folder_stack != []:
            for file in folder_stack.pop().iterdir():
                if file.is_file() and file.suffix in [".py", ".md"]:
                    res.append(file)
                elif file.is_dir():
                    folder_stack.append(file)

        return res

    def _get_content(self, file: Path) -> str:
        '''
        Return the content of a given file

        Args:
            file: Path = The file to get the content
        Return:
            content: str = The content of the file
        '''
        with open(file, 'r') as f:
            content: str = f.read()
            return content

    def _chunk_docs_file(
                self,
                file: str,
                content: str,
                max_chunk_size: int
            ) -> list[tuple[str, MinimalSource]]:
        '''
        Return the chunked docs file

        Args:
            file: str = The path of the file to chunk
            content: str = The content of the docs file to chunk
            max_chunk_size: int = The max size of the chunk
        Return:
            res: list[tuple[str, MinimalSource]] =
                The classes to stock the chunk datas
        '''
        res: list[tuple[str, MinimalSource]] = []

        start: int = 0
        end: int = 0

        state: bool = True
        while state:
            # Update the end index
            end = start + max_chunk_size - 1

            # Stop the while loop
            if end >= len(content):
                state = False
                end = len(content) - 1

            # Skip the characters in descending order
            while end > start + 1 and \
                    content[end] != "#" and content[end] != "\n":
                end -= 1

            # Go to the first # or \n
            char: str = content[end]
            while end > start + 1 and content[end] == char:
                end -= 1

            # Add the chunk to the result
            res.append((
                content[start:end + 1],
                MinimalSource(
                    file_path=file,
                    first_character_index=start,
                    last_character_index=end
                )
            ))

            # Update the start index
            start = end + 1

        return res

    def _chunk_code_file(
                self,
                file: str,
                content: str,
                max_chunk_size: int
            ) -> list[tuple[str, MinimalSource]]:
        '''
        Return the chunked code file

        Args:
            file: str = The path of the file to chunk
            content: str = The content of the code file to chunk
            max_chunk_size: int = The max size of the chunk
        Return:
            res: list[tuple[str, MinimalSource]] =
                The classes to stock the chunk datas
        '''
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        res: list[tuple[str, MinimalSource]] = []

        for node in tree.body:
            if isinstance(
                    node,
                    (
                        ast.ClassDef, ast.FunctionDef, ast.Assign,
                        ast.Import, ast.ImportFrom
                    )):
                # Get the start and end index of the chunk
                node_span: tuple[int, int] = self._get_node_span(content, node)
                start_index: int = node_span[0]
                end_index: int = node_span[1]

                # Check the chunk size
                if len(content[start_index:end_index]) <= max_chunk_size:
                    res.append((
                        content[start_index:end_index],
                        MinimalSource(
                            file_path=file,
                            first_character_index=start_index,
                            last_character_index=end_index
                        )
                    ))

                else:
                    # Split the chunk to get correct sized chunks
                    sub_chunks = self._split_large_text(
                        content[start_index:end_index],
                        start_index, max_chunk_size
                    )

                    # Add the chunks to the result
                    for text, s_start, s_end in sub_chunks:
                        res.append((
                            text,
                            MinimalSource(
                                file_path=file,
                                first_character_index=s_start,
                                last_character_index=s_end
                            )
                        ))

        return res

    def _get_node_span(
                self, content: str, node: ast.AST
            ) -> tuple[int, int]:
        '''
        Return the start and the end index of the chunk

        Args:
            content: str = The content of the file to chunk
            node: ast.AST = The node containing the chunk
        Return:
            res: tuple[int, int] = The start and end index of the chunk
        '''
        lines = content.splitlines(keepends=True)

        # Calculate the start index with the previous lines and columns
        start: int = sum([
            len(line) for line in lines[:node.lineno - 1]
        ]) + node.col_offset

        # Calculate the end index with the previous lines and columns
        end: int = sum([
            len(line) for line in lines[:node.end_lineno - 1]
        ]) + node.end_col_offset

        return start, end

    def _split_large_text(
                self,
                global_chunk_content: str,
                global_start: int,
                max_chunk_size: int
            ) -> list[tuple[str, int, int]]:
        '''
        Split the chunk according to the max_chunk_size

        Args:
            global_chunk_content: str = The chunk's content
            global_start: int = The start of the 'current' chunk
            max_chunk_size: int = The max size of the chunk
        Return:
            res: list[tuple[str, int, int]] = The list of the chunks's datas
        '''
        sub_chunks: list[tuple[str, int, int]] = []
        cursor: int = 0

        state: bool = True
        while state:
            if cursor >= len(global_chunk_content):
                cursor = len(global_chunk_content) - 1
                state = False

            chunk: str = global_chunk_content[cursor:cursor + max_chunk_size]
            start: int = global_start + cursor
            end: int = start + len(chunk)
            sub_chunks.append((chunk, start, end))
            cursor += max_chunk_size

        return sub_chunks
