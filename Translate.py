import argparse
import os
from typing import List

import yaml
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage


class Translator:
    few_shot_example: list[BaseMessage]

    def __init__(self, llm: BaseChatModel = None, config_path: str = None):
        self.llm = self.build_model(llm)
        self.config = self.load_config(config_path)
        self.default_language = "Chinese"
        self.default_format = "Markdown"
        self.few_shot_example = self.build_chat_sequence();

    @staticmethod
    def build_model(llm):
        if llm is None:
            llm = ChatOpenAI()
        return llm

    @staticmethod
    def load_config(path):
        if path is None:
            dir_path = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(dir_path, 'prompt.yaml')

        with open(path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def translate(self, text, target_language=None, document_format=None, context=None, **kwargs):
        # 如果没有需要翻译的文本，直接返回原文
        if not text.strip():
            return text

        system_message = self.build_system_message(context)
        user_message = self.build_user_message(document_format, target_language, text)
        result = self.llm([system_message] + self.few_shot_example + [user_message])

        if result.content.strip() == "NOT_FOUNT_CONTENT":
            return text
        return result.content

    def build_user_message(self, document_format, target_language, text) -> HumanMessage:
        return HumanMessage(
            content=(self.build_message_content(text, target_language=target_language, content_format=document_format))
        )

    def build_system_message(self, context) -> SystemMessage:
        context = self.build_context(context)
        system_message = SystemMessage(
            content=(self.config['system'].format(context=context)))
        return system_message

    def build_context(self, context: str) -> str:
        if context is None or context.strip():
            return ""
        return self.config.get('context', '').format(context=context)

    def build_message_content(self, text, target_language=None, content_format=None):
        if target_language is None:
            target_language = self.default_language
        if content_format is None:
            content_format = self.default_format
        return f"L:{target_language}\nF:{content_format}\nC:{text}"

    def build_chat_sequence(self) -> [BaseMessage]:
        """

        :rtype: [BaseMessage]
        """
        sequence = []
        for example in self.config.get('example', []):
            sequence.append(
                HumanMessage(
                    content=self.build_message_content(example['user'], example['language'], example['format']))
            )
            sequence.append(AIMessage(content=example['llm']))
        return sequence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Translation Configuration")
    parser.add_argument('--config', default='./prompt.yaml', type=str,
                        help='Path to the configuration file.')
    args = parser.parse_args()

    chat = ChatOpenAI(model="gpt-3.5-turbo-16k")
    translator = Translator(chat, args.config)
    res = translator.translate("用户输入的待翻译文本", target_language="English")
    print(res)
