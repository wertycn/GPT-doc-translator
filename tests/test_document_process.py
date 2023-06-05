import unittest
from unittest.mock import Mock
from dataclasses import dataclass
from pathlib import Path

import nbformat

from document_process import TranslateContext, MarkdownProcessor, DocumentPiece, NotebookProcessor


# Assuming the classes TranslateContext, DocumentPiece, DocumentProcessor and MarkdownProcessor
# are defined in a file named `processor.py`

@dataclass
class Config:
    pass  # Replace with actual Config class definition


class TestMarkdownProcessor(unittest.TestCase):
    def setUp(self):
        self.translator = Mock()
        self.translator.translate.return_value = "翻译后的文本\n"  # Mock now adds newline to translation
        self.context = TranslateContext(
            source_lang="en",
            target_lang="zh",
            source_path=Path("path/to/source.md"),
            target_path=Path("path/to/target.md"),
            option=Config()  # Replace with actual Config instance
        )
        self.processor = MarkdownProcessor(self.translator, self.context)
        self.maxDiff = None

    def test_split_document(self):
        document = 'This is a simple test document.\n```python\ncode block\n```\nEnd of document.'
        pieces = self.processor.split_document(document, max_length=1000)
        self.assertEqual(len(pieces), 3)
        self.assertEqual(pieces[0].type, "text")
        self.assertEqual(pieces[1].type, "code")
        self.assertEqual(pieces[2].type, "text")
        self.assertFalse(pieces[0].text.endswith('\n'))  # Test that split pieces have newline at end
        self.assertFalse(pieces[1].text.endswith('\n'))
        self.assertFalse(pieces[2].text.endswith('\n'))

    def test_split_document_max_length(self):
        document = self.processor.read_document("sample/markdown/langchain-readme.md")
        pieces = self.processor.split_document(document, max_length=1000)
        self.assertEqual(6,len(pieces))
        combine_document = self.processor.combine_pieces(pieces)
        self.assertEqual(document,combine_document)

    def test_split_document_code_block(self):
        document = self.processor.read_document("sample/markdown/getting_started.md")
        pieces = self.processor.split_document(document, max_length=1000)
        self.assertEqual(67, len(pieces))
        combine_document = self.processor.combine_pieces(pieces)
        # self.assertEqual(document, combine_document)

    def test_translate_pieces(self):
        pieces = [
            DocumentPiece('This is a simple test document.\n', 'text'),
            DocumentPiece('```python\ncode block\n```\n', 'code'),
            DocumentPiece('End of document.\n', 'text')
        ]
        translated_pieces = self.processor.translate_pieces(pieces)
        self.assertEqual(3, len(translated_pieces))
        self.assertEqual(translated_pieces[0].text, "翻译后的文本\n")
        self.assertEqual(translated_pieces[1].text, '```python\ncode block\n```\n')  # code blocks are not translated
        self.assertEqual(translated_pieces[2].text, "翻译后的文本\n")

    def test_combine_pieces(self):
        pieces = [
            DocumentPiece('This is a simple test document.', 'text'),
            DocumentPiece('```python\ncode block\n```', 'code'),
            DocumentPiece('End of document.', 'text')
        ]
        combined = self.processor.combine_pieces(pieces)
        expected = 'This is a simple test document.\n```python\ncode block\n```\nEnd of document.'
        self.assertEqual(combined, expected)


class MockTranslator:
    def translate(self, text, source_language, target_language, options):
        # For test purposes, just return the text unchanged.
        # Replace with a real translator for actual use.
        return text


class NotebookProcessorTest(unittest.TestCase):
    def setUp(self):
        self.translator = MockTranslator()
        self.context = TranslateContext(
            source_lang="en",
            target_lang="zh",
            source_path=Path("sample/notebook/model_laboratory.ipynb"),
            target_path=Path("sample/notebook/test_model_laboratory.ipynb"),
            option=None,
        )
        self.processor = NotebookProcessor(self.translator, self.context)

    def test_notebook_processor(self):
        # Note: This test requires a real notebook file at the specified path.
        document = self.processor.read_document(self.context.source_path)
        pieces = self.processor.split_document(document, max_length=1000)
        translated_pieces = self.processor.translate_pieces(pieces)
        translated_document = self.processor.combine_pieces(translated_pieces)
        self.processor.save_document(translated_document)

        # Read the saved translated document.
        with open(self.context.target_path, 'r', encoding='utf-8') as f:
            translated_content = f.read()

        # Read the original source document.
        with open(self.context.source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()

        # For test purposes, we only check the text contents without considering metadata.
        # So, we parse the notebooks and compare the 'source' field of each cell.
        translated_nb = nbformat.reads(translated_content, as_version=4)
        source_nb = nbformat.reads(source_content, as_version=4)
        self.assertEqual(len(translated_nb.cells), len(source_nb.cells))
        for t_cell, s_cell in zip(translated_nb.cells, source_nb.cells):
            self.assertEqual(t_cell.source, s_cell.source)


if __name__ == "__main__":
    unittest.main()
