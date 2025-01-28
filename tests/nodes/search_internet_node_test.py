from unittest.mock import MagicMock, patch
from scrapegraphai.nodes.search_internet_node import SearchInternetNode
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
import unittest

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

        # Mock the LLM model
        self.mock_llm_model = MagicMock()
        self.mock_llm_model.invoke.return_value = ["mock search query"]

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

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    def test_execute_search_node(self, mock_prompt_template, mock_output_parser, mock_search_on_web):
        """
        Test the SearchInternetNode when search results are found.
        This should update the state with search results.
        """
        # Mock the output parser
        mock_parser = MagicMock()
        mock_parser.invoke.return_value = ["mock search query"]
        mock_output_parser.return_value = mock_parser

        # Mock the prompt template
        mock_prompt = MagicMock()
        mock_prompt.__or__.return_value = mock_prompt
        mock_prompt_template.return_value = mock_prompt

        # Mock search results
        mock_search_results = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
        ]
        mock_search_on_web.return_value = mock_search_results

        # Initial state
        state = {
            "user_input": "What is the capital of France?"
        }

        # Expected output
        expected_output = {
            "user_input": "What is the capital of France?",
            "search_results": mock_search_results
        }

        # Execute the node
        result = self.search_node.execute(state)

        # Assert the results
        self.assertEqual(result, expected_output)
        mock_search_on_web.assert_called_once()

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    def test_execute_search_node_no_results(self, mock_prompt_template, mock_output_parser, mock_search_on_web):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
        # Mock the output parser
        mock_parser = MagicMock()
        mock_parser.invoke.return_value = ["mock search query"]
        mock_output_parser.return_value = mock_parser

        # Mock the prompt template
        mock_prompt = MagicMock()
        mock_prompt.__or__.return_value = mock_prompt
        mock_prompt_template.return_value = mock_prompt

        # Configure the mock to return an empty list
        mock_search_on_web.return_value = []

        # Initial state
        state = {
            "user_input": "Non-existent topic that yields no search results"
        }

        # Execute the node and expect a ValueError
        with self.assertRaises(ValueError) as context:
            self.search_node.execute(state)

        self.assertEqual(str(context.exception), "Zero results found for the search query.")

        # Assert that search_on_web was called
        mock_search_on_web.assert_called_once()

if __name__ == "__main__":
    unittest.main()
