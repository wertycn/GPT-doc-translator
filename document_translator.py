from pathlib import Path
from typing import Dict

from langchain.chat_models.base import BaseChatModel

from config import ConfigLoader
from document_process import TranslateContext, MarkdownProcessor, NotebookProcessor, DocumentProcessor
from translator import ChatTranslator, OpenAIChatTranslator


class DocumentProcessorFactory:

    def get_processor(self, filetype, translator, context):
        if filetype == 'markdown' or filetype == 'md':
            return MarkdownProcessor(translator, context)
        elif filetype == 'notebook' or filetype == 'ipynb':
            return NotebookProcessor(translator, context)
        # elif filetype == 'rst':
        #     return RstProcessor(translator, context)
        else:
            raise ValueError(f'Unsupported file type: {filetype}')


class DocumentTranslator:
    """
    文档翻译者
    """

    def __init__(self, llm : BaseChatModel, config_path: str):
        self.llm = llm
        self.config_loader = ConfigLoader(config_path)
        self.config_loader.load()

    def translate(self, context: TranslateContext):
        processor = DocumentProcessorFactory.get_processor(context.source_path.suffix[1:], self.llm, context)
        processor.process_document(self.config_loader.get_split_length())


if __name__ == '__main__':

    context = TranslateContext(
        source_lang="en",
        target_lang="zh",
        source_path=Path("tests/sample/markdown/getting_started.md"),
        target_path=Path("tests/_temp/sample/markdown/getting_started.md"),
        option=None,  # Optional, add your own context if needed
    )
    DocumentTranslator(OpenAIChatTranslator(), "translator.yaml")
