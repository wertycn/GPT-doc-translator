"""
文档处理类：

加载器 DocumentLoader  读取文档内容，统一为Document对象
分片器 DocumentSpliter  支持将不同格式的文档切分为文档对象
组合器 DocumentCombiner  在翻译完成后需要能够重新组合为原始文档格式



切分原则：
1.主要用于分离文档中不需要翻译的部分，尽量减少无需翻译的内容去请求翻译接口
2.

"""
import json
from pathlib import Path

from abc import ABC, abstractmethod
from typing import List


class DocumentLoader(ABC):

    def __init__(self,document_path):
        self.document_path = document_path


    def loadPath(self) -> Path:
        return Path(self.document_path)
    @abstractmethod
    def loader(self):
        pass


class NotebookLoader(DocumentLoader):

    def __init__(self, document_path):
        super().__init__(document_path)


    def loader(self, path):
        path = self.loadPath()
        with open(path, encoding="utf8") as f:
            d = json.load(f)


class DocumentSplitter(ABC):
    @abstractmethod
    def split(self, document: str) -> List[str]:
        pass

class TextDocumentSplitter(DocumentSplitter):
    def __init__(self, max_length: int):
        self.max_length = max_length

    def split(self, document: str) -> List[str]:
        if len(document) <= self.max_length:
            return [document]
        else:
            chunks = []
            start = 0
            while start < len(document):
                end = start + self.max_length
                if end >= len(document):
                    end = len(document)
                chunks.append(document[start:end])
                start = end
            return chunks

class MarkdownDocumentSplitter(DocumentSplitter):
    def __init__(self, max_length: int):
        self.max_length = max_length

    def split(self, document: str) -> List[str]:
        lines = document.split("\n")
        chunks = []
        current_chunk = ""
        for line in lines:
            if line.startswith("#"):
                if current_chunk:
                    chunks.extend(TextDocumentSplitter(self.max_length).split(current_chunk))
                    current_chunk = ""
                chunks.append(line)
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.extend(TextDocumentSplitter(self.max_length).split(current_chunk))
        return chunks

class NotebookDocumentSplitter(DocumentSplitter):
    def __init__(self, max_length: int):
        self.max_length = max_length

    def split(self, document: str) -> List[str]:
        nb = json.loads(document)
        chunks = []
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                chunks.extend(TextDocumentSplitter(self.max_length).split(cell["source"]))
            elif cell["cell_type"] == "markdown":
                chunks.extend(MarkdownDocumentSplitter(self.max_length).split(cell["source"]))
        return chunks


# class DocumentChunk:


if __name__ == '__main__':


    pass
