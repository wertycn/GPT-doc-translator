import unittest
from langchain.document_loaders import NotebookLoader

class SpliterTestCase(unittest.TestCase):
    def test_loader(self):

        loader = NotebookLoader("./sample/ipynp/model_laboratory.ipynb")
        document = loader.load()
        documents = loader.load_and_split()
        print(document)



if __name__ == '__main__':
    unittest.main()
