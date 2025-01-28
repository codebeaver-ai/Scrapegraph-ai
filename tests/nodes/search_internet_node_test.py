import unittest
from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
from scrapegraphai.nodes import SearchInternetNode

class TestSearchInternetNode(unittest.TestCase):

    def setUp(self):
        # Configuration for the graph
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

        # Mock the BaseChatModel
        self.mock_llm = MagicMock(spec=BaseChatModel)
        
        # Mock the invoke method to return a string instead of a list
        self.mock_llm.invoke.return_value = "search query"

        # Initialize the SearchInternetNode with the mocked LLM
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.mock_llm,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"]
            }
        )

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    def test_execute_search_node(self, mock_prompt, mock_parser, mock_search_on_web):
        """
        Test the execution of the SearchInternetNode with a sample query.
        This test checks if the node can process a query and return search results.
        """
        # Mock the PromptTemplate and CommaSeparatedListOutputParser
        mock_prompt.return_value = MagicMock()
        mock_parser.return_value = MagicMock()
        mock_parser.return_value.invoke.return_value = ["search query"]

        # Mock the search_on_web function to return sample results
        mock_search_on_web.return_value = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
        ]

        # Initial state
        state = {
            "user_input": "What is the capital of France?"
        }

        # Execute the node
        result = self.search_node.execute(state)

        # Assert the results
        self.assertIn("search_results", result)
        self.assertIsInstance(result["search_results"], list)
        self.assertEqual(len(result["search_results"]), 3)
        self.assertEqual(result["search_results"], mock_search_on_web.return_value)

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    def test_execute_search_node_no_results(self, mock_prompt, mock_parser, mock_search_on_web):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
        # Mock the PromptTemplate and CommaSeparatedListOutputParser
        mock_prompt.return_value = MagicMock()
        mock_parser.return_value = MagicMock()
        mock_parser.return_value.invoke.return_value = ["search query"]

        # Configure the mock to return an empty list
        mock_search_on_web.return_value = []

        # Initial state
        state = {
            "user_input": "Non-existent topic that yields no search results"
        }

        # Execute the node and expect a ValueError
        with self.assertRaises(ValueError) as context:
            self.search_node.execute(state)

        # Check the error message
        self.assertEqual(str(context.exception), "Zero results found for the search query.")

        # Assert that search_on_web was called
        mock_search_on_web.assert_called_once()

if __name__ == "__main__":
    unittest.main()
