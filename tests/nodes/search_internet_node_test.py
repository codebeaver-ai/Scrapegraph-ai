from unittest.mock import patch, MagicMock
from scrapegraphai.nodes.search_internet_node import SearchInternetNode
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
import unittest

class TestSearchInternetNode(unittest.TestCase):

    def setUp(self):
        self.graph_config = {
            "llm": {
                "model": "llama2",
                "temperature": 0,
                "streaming": True
            },
            "search_engine": "google",
            "max_results": 3,
            "verbose": True
        }

        self.mock_ollama = MagicMock()
        self.mock_ollama.invoke.return_value = "mock search query"

        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.mock_ollama,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"]
            }
        )

    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node(self, mock_search_on_web, mock_prompt, mock_parser):
        """
        Test the execution of the SearchInternetNode with a sample query.
        This test checks if the node can process a query and return search results.
        """
        mock_parser.return_value.parse.return_value = ["mock search query"]
        mock_prompt.return_value.format.return_value = "formatted prompt"
        mock_search_on_web.return_value = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
        ]

        state = {
            "user_input": "What is the capital of France?"
        }

        result = self.search_node.execute(state)

        self.assertIn("search_results", result)
        self.assertIsInstance(result["search_results"], list)
        self.assertEqual(len(result["search_results"]), 3)
        self.assertEqual(result["search_results"], mock_search_on_web.return_value)

    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node_no_results(self, mock_search_on_web, mock_prompt, mock_parser):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
        mock_parser.return_value.parse.return_value = ["mock search query"]
        mock_prompt.return_value.format.return_value = "formatted prompt"
        mock_search_on_web.return_value = []

        state = {
            "user_input": "Non-existent topic that yields no search results"
        }

        with self.assertRaises(ValueError) as context:
            self.search_node.execute(state)

        self.assertEqual(str(context.exception), "Zero results found for the search query.")
        mock_search_on_web.assert_called_once()

if __name__ == "__main__":
    unittest.main()
