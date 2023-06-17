"""
提供
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.prompts.chat import (
    ChatPromptTemplate, ChatPromptValue,
)
from langchain.schema import SystemMessage, AIMessage, HumanMessage, BaseMessage

from document_process import TranslateContext


class TranslatePrompt(ChatPromptTemplate):

    def format_messages(self):
        pass


@dataclass
class Translate:
    source_lang: str
    target_lang: str
    source_path: Path
    target_path: Path
    file_format: str
    example: List[BaseMessage]
    prompt: SystemMessage
    option: Dict[str, str]


class ChatTranslator:
    llm: BaseChatModel

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def translate(self, text: str, options: TranslateContext) -> str:
        # TODO: 基于context 格式化Prompt
        #       few-shot 示例配置化

        pass

    @staticmethod
    def format_prompt(context: Translate) -> ChatPromptValue:
        ChatPromptTemplate()
        pass

        [
            SystemMessage(content="""
            你是一款专业的翻译程序，我需要协助翻译 英文技术文档为中文， 并使用风格转换使得翻译文本更符合中文习惯
            我会输入markdown格式的文本内容，翻译过程中需要保持markdown 格式不变，除翻译结果外，不需要额外的解释,如果输入内容为空，请返回空内容无需增加解释
            准备好了吗？
                    """),
            AIMessage(content="好了，请输入需要翻译的内容"),
            HumanMessage(content="hello"),
            AIMessage(content="你好"),
            HumanMessage(content="\n"),
            AIMessage(content="\n"),
            HumanMessage(content="""
            # Quickstart Guide


            This tutorial gives you a quick walkthrough about building an end-to-end language model application with LangChain.

                    """),
            AIMessage(content="""
            # 快速上手指南


            本教程将为您快速介绍如何使用LangChain构建一个端到端的语言模型应用程序。        
                    """),
            HumanMessage(content="")
        ]


class OpenAIChatTranslator(ChatTranslator):

    def __init__(self):
        self.llm = ChatOpenAI()

    def translate(self, text: str, options: Translate) -> str:
        return self.llm()


class Translator:

    def __init__(self, llm: BaseChatModel):
        self.llm = llm


    pass

    def translate(self, text, target_language=None, document_format=None, **kwargs):
        # kwargs 中可能包含context
        pass


def build_message(text, target_language="Chinese", content_format="Markdown"):
    return f"T:{target_language}\nF:{content_format}\nC:{text}"


if __name__ == '__main__':
    chat = ChatOpenAI()
    prompt = """你是一款非常专业的翻译助手，你需要帮助我翻译技术文档
翻译过程需要注意以下几点:
1. 只翻译文本内容，保持文本格式不变，可能会提供不完整的文本格式内容，不需要补全格式
2. 只输出翻译结果，不需要解释
3. 翻译过程保持专业性，对疑似专有名词的内容可以不翻译
4. 翻译的结果需要符合目标语言的阅读习惯，不能带有翻译腔
5. 遇到不包含有效内容的文本时，输出`NOT_FOUNT_CONTENT`


我会按照如下格式进行输入:
```
L: Chinese
F: Markdown
T: ... 
```  
其中`L`是要翻译的目标语言，`F`是输入内容的格式，`T`

下面让我们开始
"""
    user_message = build_message("""\n\n\n .               """, content_format="ipynb")
    # 是需要翻译的文本内容
    res = chat([SystemMessage(content=prompt), HumanMessage(content="""
L: Chinese
F: Markdown
C: Hello
"""), AIMessage(content="你好"), HumanMessage(content="""
L: Chinese
F: Markdown
C: # Quickstart Guide
          
This tutorial gives you a quick walkthrough about building an end-to-end language model application with LangChain.'
        
"""),
                AIMessage(content="""# 快速上手指南

本教程将为您快速介绍如何使用LangChain构建一个端到端的语言模型应用程序。'
       
"""),
                HumanMessage(content=build_message("\n")), AIMessage(content="NOT_FOUNT_CONTENT"),
                HumanMessage(content=build_message("===")), AIMessage(content="NOT_FOUNT_CONTENT"),
                HumanMessage(content=user_message)])
    print(res.content)
