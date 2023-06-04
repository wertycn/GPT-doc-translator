# GPT-doc-translator
基于GPT的技术文档翻译程序，支持markdown, ipynb, rst 等文档格式

# 翻译程序

这是一个支持多种文件格式翻译的程序，包括纯文本文档、Markdown 文档和 Jupyter Notebook 文档。它可以将输入的文档翻译成多种语言，并提供了多种文档切分和组合策略，以适应不同的文件格式和翻译需求。

## 安装

该程序使用 Python 3 编写，需要安装以下依赖库：

- `googletrans==4.0.0-rc1`
- `nbformat==5.1.2`

您可以使用以下命令安装这些依赖库：

```bash
pip install googletrans==4.0.0-rc1 nbformat==5.1.2
```

## 使用

该程序提供了一个命令行接口，您可以使用以下命令运行该程序：

```bash
python translate.py input_file output_file source_lang target_lang [--splitter SPLITTER] [--combiner COMBINER]
```

其中，`input_file` 是输入文件的路径，`output_file` 是输出文件的路径，`source_lang` 是原始文档的语言，`target_lang` 是目标语言。可选参数 `--splitter` 和 `--combiner` 分别用于指定文档切分和组合策略，默认值为 `TextDocumentSplitter` 和 `TextDocumentCombiner`。

以下是一些示例：

```bash
# 将 input.txt 翻译成中文，并保存到 output.txt 中
python translate.py input.txt output.txt en zh-CN

# 将 input.md 翻译成法语，并保存到 output.md 中，使用 MarkdownDocumentSplitter 和 MarkdownDocumentCombiner 进行文档切分和组合
python translate.py input.md output.md en fr --splitter MarkdownDocumentSplitter --combiner MarkdownDocumentCombiner

# 将 input.ipynb 翻译成日语，并保存到 output.ipynb 中，使用 NotebookDocumentSplitter 和 NotebookDocumentCombiner 进行文档切分和组合
python translate.py input.ipynb output.ipynb en ja --splitter NotebookDocumentSplitter --combiner NotebookDocumentCombiner
```

## 文档切分和组合策略

该程序提供了以下文档切分和组合策略：

- `TextDocumentSplitter`：将纯文本文档按照指定长度切分成多个小片段；
- `MarkdownDocumentSplitter`：将 Markdown 文档按照标题和正文的结构切分成多个小片段；
- `NotebookDocumentSplitter`：将 Jupyter Notebook 文档按照代码单元格和 Markdown 单元格的结构切分成多个小片段；
- `TextDocumentCombiner`：将纯文本文档的翻译后的小片段按顺序组合成完整的文档；
- `MarkdownDocumentCombiner`：将 Markdown 文档的翻译后的小片段按照标题和正文的顺序组合成完整的文档；
- `NotebookDocumentCombiner`：将 Jupyter Notebook 文档的翻译后的小片段按照代码单元格和 Markdown 单元格的顺序组合成完整的文档。

您可以根据实际情况选择合适的文档切分和组合策略。如果您需要自定义文档切分和组合策略，可以继承 `DocumentSplitter` 和 `DocumentCombiner` 抽象类，并实现相应的方法。