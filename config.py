from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml
from langchain.prompts import few_shot
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage


@dataclass
class Config:
    global_option: dict
    file_option: dict


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


class GlobalConfig:
    prompt_template: BaseMessage


class ConfigLoader:
    """
    配置加载类，负责配置文件读取，格式转换
    """
    prompt: PromptConfig
    path: str

    def __init__(self, path):
        self.path = path

    def load(self):
        p = Path(self.path)
        with open(p, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        #  prompt 处理
        self._load_prompt(data['prompt'])
        print(self.prompt)

    def _load_prompt(self, data):
        few_shot: Dict = {}
        for key, item in data['few-shot'].items():
            few_shot[key] = self._format_prompt(item)
        self.prompt = PromptConfig(system=SystemMessage(content=data['system']), few_shot=few_shot)

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
