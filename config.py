from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml
from langchain.prompts import few_shot
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage


@dataclass
class APIConfig:
    key: str
    base_url: str


@dataclass
class ContextOption:
    path: str
    content: str


@dataclass
class ContextConfig:
    global_context: str
    custom_context: List[ContextOption]


@dataclass
class PromptConfig:
    system: BaseMessage

    # 文件类型对应的学习小样本
    few_shot: Dict[str, List[BaseMessage]]

    def get_global_prompt(self) -> List[BaseMessage]:
        return self.get_prompt('global')

    def get_prompt(self, file_type: str) -> List[BaseMessage]:
        if self.few_shot is not None and file_type in self.few_shot and self.few_shot[file_type] is not None:
            return self.few_shot[file_type]
        return []

    def is_exist_prompt(self, type: str):
        return type in self.few_shot and self.few_shot[type] is not None

@dataclass()
class TranslateConfig:
    source_lang: str
    target_lang: str
    split_length: int

class GlobalConfig:
    prompt_template: BaseMessage


class ConfigLoader:
    """
    配置加载类，负责配置文件读取，格式转换
    """
    prompt: PromptConfig
    context: ContextConfig
    api: APIConfig
    path: str
    split_length: int
    translate: TranslateConfig

    def __init__(self, path):
        self.path = path


    def load(self):
        p = Path(self.path)
        with open(p, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self._load_translate(data['translate'])
        #  prompt 处理
        self._load_prompt(data['prompt'])

        # 上下文处理
        self._load_context(data['context'])

        # API配置处理
        self._load_api(data['api'])



    def _load_prompt(self, data):
        shot: Dict = {}
        for key, item in data['few-shot'].items():
            shot[key] = self._format_prompt(item)
        self.prompt = PromptConfig(system=SystemMessage(content=data['system']), few_shot=shot)

    def _load_context(self, data):
        custom_context = [ContextOption(path=item['path'], content=item['content']) for item in data['custom']]
        self.context = ContextConfig(global_context=data['global'], custom_context=custom_context)

    def _load_api(self, data):
        self.api = APIConfig(key=data['key'], base_url=data['base_url'])
        self.split_length = data['split_length']

    def get_context_for_file(self, file_path: str) -> str:
        matched_contexts = [option for option in self.context.custom_context if file_path.startswith(option.path)]
        if matched_contexts:
            # 从所有匹配的上下文中，返回路径最长的那个上下文
            best_match = max(matched_contexts, key=lambda option: len(option.path))
            return best_match.content
        return self.context.global_context

    def get_prompt(self):
        return self.prompt

    def get_system_prompt(self):
        return self.prompt.system

    @staticmethod
    def _format_prompt(data: list) -> List[BaseMessage]:
        res: List[BaseMessage] = []
        for item in data:
            res.append(HumanMessage(content=item['user']))
            res.append(AIMessage(content=item['llm']))
        return res

    def get_split_length(self):
        return self.split_length;

    def _load_translate(self, data):
        self.translate = TranslateConfig(data['source_lang'],data['target_lang'],data['split_length'])
