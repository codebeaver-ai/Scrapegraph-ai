import unittest
from unittest.mock import Mock, patch
from scrapegraphai.nodes.search_internet_node import SearchInternetNode, PromptTemplate, CommaSeparatedListOutputParser

class TestSearchInternetNode(unittest.TestCase):
    """Test cases for the SearchInternetNode class."""

    def setUp(self):
        """Set up the test environment."""
        # Configuration for the graph
        self.graph_config = {
            "llm": {
                "model": "llama3",
                "temperature": 0,
                "streaming": True
            },
            "search_engine": "google",
            "max_results": 3,
            "verbose": True
        }

        # Mock ChatOllama
        self.mock_chat_ollama = Mock()
        
        # Initialize the SearchInternetNode
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.mock_chat_ollama,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"]
            }
        )

    @patch('scrapegraphai.nodes.search_internet_node.search_on_web')
    @patch('scrapegraphai.nodes.search_internet_node.PromptTemplate')
    @patch('scrapegraphai.nodes.search_internet_node.CommaSeparatedListOutputParser')
    def test_execute_search_node(self, mock_output_parser, mock_prompt_template, mock_search_on_web):
        """
        Test the execution of the SearchInternetNode.
        
        This test verifies that the SearchInternetNode correctly processes user input,
        generates a search query, performs a web search, and returns the expected results.
        """
        # Mock the search_on_web function
        mock_search_on_web.return_value = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
        ]

        # Mock the LLM chain response
        mock_chain = Mock()
        mock_chain.invoke.return_value = ["What is the capital of France"]
        mock_prompt_template.return_value.__or__.return_value.__or__.return_value = mock_chain

        # Initial state
        state = {
            "user_input": "What is the capital of France?"
        }

        # Expected output
        expected_output = {
            "user_input": "What is the capital of France?",
            "search_results": [
                "https://en.wikipedia.org/wiki/Paris",
                "https://en.wikipedia.org/wiki/France",
                "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
            ]
        }

        # Execute the node
        result = self.search_node.execute(state)

        # Assert the results
        self.assertEqual(result, expected_output)
        mock_search_on_web.assert_called_once()
        mock_chain.invoke.assert_called_once()
        mock_prompt_template.assert_called_once()
        mock_output_parser.assert_called_once()

if __name__ == "__main__":
    unittest.main()
