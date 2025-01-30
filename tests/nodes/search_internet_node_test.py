import unittest
from unittest.mock import patch, MagicMock
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from scrapegraphai.nodes.search_internet_node import SearchInternetNode

class TestSearchInternetNode(unittest.TestCase):

    def setUp(self):
        # Mock ChatOllama
        self.mock_llm = MagicMock(spec=BaseChatModel)
        self.mock_llm.invoke.return_value = AIMessage(content="mocked search query")

        # Initialize the SearchInternetNode with the mock LLM
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.mock_llm,
                "search_engine": "google",
                "max_results": 3,
                "verbose": True
            }
        )

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    def test_execute_search_node(self, mock_search_on_web):
        """
        Test the execution of the SearchInternetNode with a sample query.
        This test checks if the node can process a query and return search results.
        """
        # Mock the search_on_web function
        mock_search_on_web.return_value = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/Île-de-France"
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
    def test_execute_search_node_no_results(self, mock_search_on_web):
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
