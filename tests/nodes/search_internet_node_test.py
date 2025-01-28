import unittest
from unittest.mock import patch, MagicMock
from scrapegraphai.nodes.search_internet_node import SearchInternetNode
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate


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

        # Mock the ChatOllama client
        self.mock_ollama = MagicMock()
        self.mock_ollama.invoke.return_value = ["What is the capital of France"]

        # Mock the PromptTemplate
        self.mock_prompt = MagicMock(spec=PromptTemplate)
        self.mock_prompt.format_prompt.return_value.to_string.return_value = "Mocked prompt"

        # Mock the CommaSeparatedListOutputParser
        self.mock_parser = MagicMock(spec=CommaSeparatedListOutputParser)
        self.mock_parser.parse.return_value = ["What is the capital of France"]

        # Initialize the SearchInternetNode with the mocked components
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
        self.search_node.llm_model = self.mock_ollama

    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node(self, mock_search_on_web, mock_parser, mock_prompt):
        """
        Test the SearchInternetNode when search results are found.
        This should update the state with search results.
        """
        # Mock search results
        mock_search_results = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
        ]
        mock_search_on_web.return_value = mock_search_results

        # Mock the parser to return a valid search query
        mock_parser.return_value.parse.return_value = ["What is the capital of France"]

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

    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser', return_value=MagicMock())
    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node_no_results(self, mock_search_on_web, mock_parser, mock_prompt):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
        # Configure the mock to return an empty list
        mock_search_on_web.return_value = []

        # Mock the parser to return a valid search query
        mock_parser.return_value.parse.return_value = ["Non-existent topic"]

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
