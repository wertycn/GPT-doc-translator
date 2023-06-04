import unittest

from config import ConfigLoader


class MyTestCase(unittest.TestCase):
    def test_config_load(self):
        loader = ConfigLoader("sample/translator.yaml")
        loader.load()

if __name__ == '__main__':
    unittest.main()
