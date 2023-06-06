from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List
import nbformat
from docutils import nodes
from docutils.parsers.rst import Parser
from docutils.utils import new_document

@dataclass
class TranslateContext:
    source_lang: str
    target_lang: str
    source_path: Path
    target_path: Path
    option: Any  # Replace with actual Config type


class DocumentPiece:
    def __init__(self, text, piece_type, metadata=None):
        self.text = text
        self.type = piece_type
        self.length = len(text)
        self.metadata = metadata if metadata else {}


class DocumentProcessor(ABC):
    def __init__(self, translator, context: TranslateContext):
        self.translator = translator
        self.context = context

    @abstractmethod
    def read_document(self, filepath):
        pass

    @abstractmethod
    def split_document(self, document, max_length):
        pass

    @abstractmethod
    def translate_pieces(self, pieces):
        pass

    @abstractmethod
    def combine_pieces(self, pieces):
        pass

    @abstractmethod
    def save_document(self, document):
        pass

    def process_document(self, max_length):
        document = self.read_document(self.context.source_path)
        pieces = self.split_document(document, max_length)
        translated_pieces = self.translate_pieces(pieces)
        translated_document = self.combine_pieces(translated_pieces)
        self.save_document(translated_document)


class MarkdownProcessor(DocumentProcessor):
    def read_document(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def split_document(self, document: str, max_length: int) -> List[DocumentPiece]:
        lines = document.split("\n")
        pieces = []
        buffer = ""
        in_code_block = False
        length = 0

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("    "):  # Check for start or end of a code block
                if in_code_block:  # Code block ends
                    pieces.append(DocumentPiece(buffer, "code"))
                    buffer = ""
                    in_code_block = False
                else:  # Code block starts
                    if buffer:  # Add the previous buffered text as a piece
                        pieces.append(DocumentPiece(buffer, "text"))
                        buffer = ""
                    buffer += line  # Don't add newline if buffer is empty
                    in_code_block = True
            elif in_code_block:  # Inside a code block
                buffer += "\n" + line
            else:  # Normal text
                temp_len = length + len(line) + 1  # +1 for the newline character
                if temp_len > max_length:  # current line would exceed the max_length
                    pieces.append(DocumentPiece(buffer, "text"))
                    buffer = line  # Don't add newline if buffer is empty
                    length = len(line)
                else:
                    buffer += "\n" + line if buffer else line  # Don't add newline if buffer is empty
                    length = temp_len

        if buffer:  # Remaining text
            pieces.append(DocumentPiece(buffer, "text" if not in_code_block else "code"))

        return pieces

    def translate_pieces(self, pieces):
        translated_pieces = []
        for piece in pieces:
            if piece.type == "code":  # skip code blocks
                translated_pieces.append(piece)
            else:
                translated_text = self.translator.translate(
                    piece.text,
                    source_language=self.context.source_lang,
                    target_language=self.context.target_lang,
                    options=self.context.option
                )
                translated_pieces.append(DocumentPiece(translated_text, "text"))
        return translated_pieces

    def combine_pieces(self, pieces):

        return "\n".join((piece.text for piece in pieces))

    def save_document(self, document):
        with open(self.context.target_path, 'w', encoding='utf-8') as f:
            f.write(document)


class NotebookProcessor(DocumentProcessor):
    def read_document(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def split_document(self, document: str, max_length: int) -> List[DocumentPiece]:
        notebook = nbformat.reads(document, as_version=4)
        pieces = []

        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                pieces.extend(self._split_markdown_cell(cell, max_length))
            elif cell.cell_type == "code":
                pieces.append(DocumentPiece(cell.source, "code", {"cell_type": cell.cell_type}))
            else:
                pieces.append(DocumentPiece(cell.source, "unknown", {"cell_type": cell.cell_type}))

        return pieces

    def _split_markdown_cell(self, cell, max_length):
        # Reuse the MarkdownProcessor's logic to split Markdown text
        markdown_processor = MarkdownProcessor(self.translator, self.context)
        return markdown_processor.split_document(cell.source, max_length)

    def translate_pieces(self, pieces):
        translated_pieces = []
        for piece in pieces:
            if piece.type == "code":  # skip code blocks
                translated_pieces.append(piece)
            else:
                translated_text = self.translator.translate(
                    piece.text,
                    source_language=self.context.source_lang,
                    target_language=self.context.target_lang,
                    options=self.context.option
                )
                translated_pieces.append(DocumentPiece(translated_text, "text"))
        return translated_pieces

    def combine_pieces(self, pieces):
        translated_notebook = nbformat.v4.new_notebook()
        for piece in pieces:
            if piece.type in ["code", "unknown"]:
                cell = nbformat.v4.new_code_cell(piece.text)
            else:
                cell = nbformat.v4.new_markdown_cell(piece.text)
            cell.cell_type = piece.metadata.get("cell_type", cell.cell_type)
            translated_notebook.cells.append(cell)

        return nbformat.writes(translated_notebook)

    def save_document(self, document):
        notebook = nbformat.reads(document, as_version=4)
        with open(self.context.target_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)





class RSTProcessor:
    def __init__(self):
        self.parser = Parser()

    def split_document(self, document: str, max_length: int):
        # 创建一个新的 RST 文档对象
        document_node = new_document('Document')
        # 解析文档
        self.parser.parse(document, document_node)

        # 存储分割的段落
        pieces = []
        current_piece = ''
        is_code = False  # 用于标记是否在处理代码块

        # 遍历文档的所有子节点
        for child in document_node.children:
            # 我们只关心段落节点
            if isinstance(child, nodes.paragraph):
                # 获取段落的文本内容
                paragraph_text = child.astext()

                # 检查是否遇到了代码块的开始标记
                if paragraph_text.strip().endswith('::'):
                    is_code = True

                # 如果是在处理代码块，或者如果添加这个段落会超过最大长度，那么就新开一个分片
                if is_code or len(current_piece) + len(paragraph_text) > max_length:
                    pieces.append(current_piece)
                    current_piece = paragraph_text
                else:
                    # 否则，将这个段落添加到当前的分片
                    current_piece += paragraph_text

                # 如果遇到了非缩进的段落，那么就结束代码块
                if is_code and not paragraph_text.startswith('    '):
                    is_code = False

        # 最后，记得将最后一个分片也添加到结果中
        pieces.append(current_piece)

        return pieces

    def combine_pieces(self, pieces: list[str]) -> str:
        # 将所有的分片连接成一个完整的文档
        return '\n'.join(pieces)



