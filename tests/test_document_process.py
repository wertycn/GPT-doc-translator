import unittest
from unittest.mock import Mock
from dataclasses import dataclass
from pathlib import Path

from document_process import TranslateContext, MarkdownProcessor, DocumentPiece


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

    def test_split_document(self):
        document = 'This is a simple test document.\n```python\ncode block\n```\nEnd of document.'
        pieces = self.processor.split_document(document, max_length=1000)
        self.assertEqual(len(pieces), 3)
        self.assertEqual(pieces[0].type, "text")
        self.assertEqual(pieces[1].type, "code")
        self.assertEqual(pieces[2].type, "text")
        self.assertTrue(pieces[0].text.endswith('\n'))  # Test that split pieces have newline at end
        self.assertTrue(pieces[1].text.endswith('\n'))
        self.assertTrue(pieces[2].text.endswith('\n'))

    def test_translate_pieces(self):
        pieces = [
            DocumentPiece('This is a simple test document.\n', 'text'),
            DocumentPiece('```python\ncode block\n```\n', 'code'),
            DocumentPiece('End of document.\n', 'text')
        ]
        translated_pieces = self.processor.translate_pieces(pieces)
        self.assertEqual(len(translated_pieces), 3)
        self.assertEqual(translated_pieces[0].text, "翻译后的文本\n")
        self.assertEqual(translated_pieces[1].text, '```python\ncode block\n```\n')  # code blocks are not translated
        self.assertEqual(translated_pieces[2].text, "翻译后的文本\n")

    def test_combine_pieces(self):
        pieces = [
            DocumentPiece('This is a simple test document.\n', 'text'),
            DocumentPiece('```python\ncode block\n```\n', 'code'),
            DocumentPiece('End of document.\n', 'text')
        ]
        combined = self.processor.combine_pieces(pieces)
        expected = 'This is a simple test document.\n```python\ncode block\n```\nEnd of document.\n'
        self.assertEqual(combined, expected)



if __name__ == "__main__":
    unittest.main()
