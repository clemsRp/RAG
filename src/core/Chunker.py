#!/usr/bin/env python3

from tqdm import tqdm
import ast
import re
from pathlib import Path
from typing import Any
from src.DataModels import MinimalSource
from src.Constants import VLLM_FOLDER, AST


class Chunker:
    '''
    Class for the chunking system
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
        Return the chunks of the files in the VLLM_FOLDER

        Args:
            max_chunk_size: int = The max size of a chunk
        Return:
            res: list[tuple[str, MinimalSource]] = The chunks
        '''
        files: list[Path] = self._get_files()
        res: list[tuple[str, MinimalSource]] = []

        for file in tqdm(files, desc="Chunking des fichiers"):
            content: str = self._get_content(file)

            if len(content) <= max_chunk_size:
                res.append((
                    content,
                    MinimalSource(
                        file_path=str(file),
                        first_character_index=0,
                        last_character_index=max(len(content) - 1, 0)
                    )
                ))
            elif file.suffix == ".py":
                res += self._chunk_code_file(
                    str(file),
                    content,
                    max_chunk_size
                )

            elif file.suffix == ".md":
                res += self._chunk_docs_file(
                    str(file),
                    content,
                    max_chunk_size
                )

        return res

    def _chunk_code_file(
                self,
                file: str,
                content: str,
                max_chunk_size: int
            ) -> list[tuple[str, MinimalSource]]:
        '''
        Chunk a code file

        Args:
            file: str = The path of the file
            content: str = The content of the given file
            max_chunk_size: int = The max size of a chunk
        Return:
            res: list[tuple[str, MinimalSource]] = The chunks
        '''
        if AST:
            return self._chunk_code_with_ast(file, content, max_chunk_size)
        return self._chunk_code_without_ast(file, content, max_chunk_size)

    def _chunk_code_with_ast(
                self,
                file: str,
                content: str,
                max_chunk_size: int
            ) -> list[tuple[str, MinimalSource]]:
        '''
        Chunk a code file

        Args:
            file: str = The path of the file
            content: str = The content of the given file
            max_chunk_size: int = The max size of a chunk
        Return:
            res: list[tuple[str, MinimalSource]] = The chunks
        '''
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        res: list[tuple[str, MinimalSource]] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_pre = f"# Context: class {node.name}\n"

                for item in node.body:
                    if isinstance(
                                item,
                                (ast.FunctionDef, ast.AsyncFunctionDef)
                            ):

                        start, end = self._get_node_span(
                            content,
                            item,
                            len(content) - 1
                        )
                        method_prefix = f"{class_pre}# Method: {item.name}\n"
                        self._add_smart_chunks(
                            res,
                            file,
                            content[start:end + 1],
                            start,
                            max_chunk_size,
                            method_prefix
                        )

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start, end = self._get_node_span(
                    content,
                    node,
                    len(content) - 1
                )
                prefix = f"# Context: def {node.name}\n"
                self._add_smart_chunks(
                    res,
                    file,
                    content[start:end+1],
                    start,
                    max_chunk_size,
                    prefix
                )

        return res

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
                    content[end] != "#" and content[end:end + 2] != "\n\n":
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

    def _get_breadcrumb(self, headers: dict) -> str:
        active = [v for k, v in headers.items() if v]
        if not active:
            return ""
        return "\n"

    def _add_smart_chunks(
                self,
                res_list: list[tuple[str, MinimalSource]],
                file: str,
                text: str,
                global_start: int,
                max_size: int,
                prefix: str
            ):
        '''
        Chunk a text and add it to the response

        Args:
            res_list: list[tuple[str, MinimalSource]] = The response
            file: str = The path of the current file
            text: str = The chunk of the file
            global_start: int = The start of the global chunk
            max_size: int = The max size of chunk
            prefix: str = The prefix to add
        Return:
            None
        '''
        prefix_len = len(prefix)
        effective_max = max_size - prefix_len
        overlap = int(effective_max * 0.15)

        if len(text) <= effective_max:
            res_list.append((
                prefix + text,
                MinimalSource(
                    file_path=file,
                    first_character_index=global_start,
                    last_character_index=global_start + len(text) - 1
                )
            ))
            return

        cursor = 0
        while cursor < len(text):
            end = min(cursor + effective_max, len(text))
            chunk_body = text[cursor:end]

            res_list.append((
                prefix + chunk_body,
                MinimalSource(
                    file_path=file,
                    first_character_index=global_start + cursor,
                    last_character_index=global_start + end - 1
                )
            ))

            cursor += (effective_max - overlap)
            if cursor >= len(text) - overlap and end == len(text):
                break

    def _get_node_span(
                self,
                content: str,
                node: Any,
                last_idx: int
            ) -> tuple[int, int]:
        '''
        Return the start and the end of chunk depending on the given node

        Args:
            content: str = The content of the file
            node: Any = The node to get the start and end
            last_idx: int = The last possible index for the chunk
        Return:
            None
        '''
        lines = content.splitlines(keepends=True)
        start = sum(len(i) for i in lines[:node.lineno - 1]) + node.col_offset
        end = int(
            sum(len(i) for i in lines[:node.end_lineno - 1]) +
            node.end_col_offset
        )
        return start, min(end, last_idx)

    def _get_files(self) -> list[Path]:
        '''
        Return the files to chunk

        Args:
            None
        Return:
            list[Path] = The files to chunk
        '''
        res: list[Path] = []
        folder_stack: list[Path] = [Path(VLLM_FOLDER)]
        while folder_stack:
            curr = folder_stack.pop()
            for item in curr.iterdir():
                if item.is_file() and item.suffix in [".py", ".md"]:
                    res.append(item)
                elif item.is_dir() and not item.name.startswith('.'):
                    folder_stack.append(item)
        return res

    def _get_content(self, file: Path) -> str:
        '''
        Return the content of the file of a given path

        Args:
            file: Path = The path of the file
        Return:
            res: str = The file content
        '''
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
