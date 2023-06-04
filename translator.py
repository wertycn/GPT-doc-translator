"""
提供
"""

import os
from pathlib import Path

import requests
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain.chat_models.base import BaseChatModel
from langchain.llms import OpenAI, BaseLLM
from langchain.chat_models import ChatOpenAI

from langchain.prompts import PromptTemplate

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage, BaseMessage
)

from config import Config


class TranslatePrompt(ChatPromptTemplate):

    def format_messages(self):
        pass







@dataclass
class TranslateContext:
    source_lang: str
    target_lang: str
    source_path: Path
    target_path: Path
    option: Config


class ChatTranslator:
    llm: BaseChatModel

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def translate(self, text: str, context: TranslateContext) -> str:
        # TODO: 基于context 格式化Prompt
        #       few-shot 示例配置化
        pass

    def format_prompt(self,context: TranslateContext) -> ChatPromptTemplate:

        pass


