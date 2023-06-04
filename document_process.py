from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

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

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):  # Check for start or end of a code block
                if in_code_block:  # Code block ends
                    buffer += line + "\n\n"  # Include the code block delimiter line and add a newline
                    pieces.append(DocumentPiece(buffer, "code"))
                    buffer = ""
                    in_code_block = False
                else:  # Code block starts
                    if buffer:  # Add the previous buffered text as a piece
                        pieces.append(DocumentPiece(buffer + "\n", "text"))  # add newline for consistency
                        buffer = ""
                    buffer += line + "\n"  # Include the code block delimiter line
                    in_code_block = True
            elif in_code_block:  # Inside a code block
                buffer += line + "\n"
            else:  # Normal text
                if len(buffer) + len(line) + 1 > max_length:  # +1 for the newline character
                    pieces.append(DocumentPiece(buffer + "\n", "text"))  # add newline for consistency
                    buffer = line
                else:
                    buffer += line + "\n"

        if buffer:  # Remaining text
            pieces.append(DocumentPiece(buffer + "\n", "text" if not in_code_block else "code"))

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
                ) + '\n'  # Ensure a newline at the end
                translated_pieces.append(DocumentPiece(translated_text, "text"))
            return translated_pieces

    def combine_pieces(self, pieces):
        return ''.join(piece.text for piece in pieces)

    def save_document(self, document):
        with open(self.context.target_path, 'w', encoding='utf-8') as f:
            f.write(document)
