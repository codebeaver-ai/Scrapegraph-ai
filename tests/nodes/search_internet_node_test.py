import unittest
from unittest.mock import MagicMock, patch
from langchain_community.chat_models import ChatOllama
from scrapegraphai.nodes import SearchInternetNode
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate

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

        # Mock the ChatOllama model
        self.mock_llm_model = MagicMock(spec=ChatOllama)
        self.mock_llm_model.format = "json"
        self.mock_llm_model.invoke.return_value = ["What is the capital of France"]

        # Mock CommaSeparatedListOutputParser
        self.mock_parser = MagicMock(spec=CommaSeparatedListOutputParser)
        self.mock_parser.invoke.return_value = ["What is the capital of France"]

        # Mock PromptTemplate
        self.mock_prompt = MagicMock(spec=PromptTemplate)

        # Initialize the SearchInternetNode with the mock model
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.mock_llm_model,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"]
            }
        )

    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node(self, mock_search_on_web, mock_prompt, mock_parser):
        """
        Test the execution of the SearchInternetNode with a sample query.
        This test checks if the node can process a query and return search results.
        """
        # Mock the search_on_web function to return some results
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

    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node_no_results(self, mock_search_on_web, mock_prompt, mock_parser):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
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
