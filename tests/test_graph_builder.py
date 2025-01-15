import unittest

from scrapegraphai.builders.graph_builder import GraphBuilder
from unittest.mock import patch

class TestGraphBuilder(unittest.TestCase):
    def test_unsupported_model_raises_value_error(self):
        # Arrange
        prompt = "Test prompt"
        config = {
            "llm": {
                "api_key": "test_api_key",
                "model": "unsupported_model"
            }
        }

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            GraphBuilder(prompt, config)

        self.assertEqual(str(context.exception), "Model not supported")