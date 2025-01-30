import unittest
from unittest.mock import patch, MagicMock
from scrapegraphai.nodes.search_internet_node import SearchInternetNode

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
        self.mock_llm_model = MagicMock()
        self.mock_llm_model.invoke.return_value = ["What is the capital of France?"]

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
    def test_execute_search_node(self, mock_parser, mock_search_on_web):
        """
        Test the execution of the SearchInternetNode with a sample query.
        This test checks if the node can process a query and return search results.
        """
        # Mock the parser to return a string
        mock_parser_instance = MagicMock()
        mock_parser_instance.invoke.return_value = ["What is the capital of France?"]
        mock_parser.return_value = mock_parser_instance

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

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    def test_execute_search_node_no_results(self, mock_parser, mock_search_on_web):
        """
        Test the SearchInternetNode when no search results are found.
        This should raise a ValueError.
        """
        # Mock the parser to return a string
        mock_parser_instance = MagicMock()
        mock_parser_instance.invoke.return_value = ["Non-existent topic"]
        mock_parser.return_value = mock_parser_instance

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
