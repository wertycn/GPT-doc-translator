import unittest
from pathlib import Path
from config import ConfigLoader, ContextOption, ContextConfig, PromptConfig, APIConfig, SystemMessage, HumanMessage, AIMessage


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.config_loader = ConfigLoader('sample/translator.yaml')
        self.config_loader.load()

    def test_prompt_loading(self):
        prompt_config = self.config_loader.prompt

        self.assertIsInstance(prompt_config, PromptConfig)
        self.assertEqual(SystemMessage(content="""你是一款专业的翻译程序，我需要协助翻译 {source_lang}技术文档为{target_lang}， 并使用风格转换使得翻译文本更符合{target_lang}语言的习惯
我会输入{file_format}格式的文本内容，翻译过程中需要保持{file_format}格式不变，除翻译结果外，不需要额外的解释; 如果输入格式不完整，请不要修复补充
{context}\n"""), prompt_config.system)
        self.assertTrue('global' in prompt_config.few_shot)
        self.assertTrue('markdown' in prompt_config.few_shot)
        self.assertEqual(prompt_config.few_shot['global'], [
            HumanMessage(content='你好'),
            AIMessage(content='Hello')
        ])
        # 请根据实际的文件内容进行更详细的断言检查

    def test_context_loading(self):
        context_config = self.config_loader.context

        self.assertIsInstance(context_config, ContextConfig)
        self.assertEqual(context_config.global_context, '')
        self.assertIsInstance(context_config.custom_context, list)
        # 请根据实际的文件内容进行更详细的断言检查

    def test_api_loading(self):
        api_config = self.config_loader.api

        self.assertIsInstance(api_config, APIConfig)
        # 请根据实际的文件内容进行更详细的断言检查

    def test_get_context_for_file(self):
        self.assertEqual('', self.config_loader.get_context_for_file('unknown/path'))
        self.assertEqual('test example 1 res', self.config_loader.get_context_for_file('test/example1'))
        self.assertEqual('test example 2 res', self.config_loader.get_context_for_file('test/'))
        self.assertEqual('test example 2 res', self.config_loader.get_context_for_file('test/example2'))
        self.assertEqual('test example 2 res', self.config_loader.get_context_for_file('test/example'))
        # 请根据实际的文件内容和你的业务逻辑，添加更多的测试用例，验证不同路径的情况


if __name__ == '__main__':
    unittest.main()
