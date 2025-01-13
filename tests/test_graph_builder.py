import pytest

from scrapegraphai.builders.graph_builder import GraphBuilder
from unittest.mock import patch

class TestGraphBuilder:
    def test_create_llm_unsupported_model(self):
        # Arrange
        config = {
            "llm": {
                "api_key": "test_api_key",
                "model": "unsupported_model"
            }
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Model not supported"):
            GraphBuilder("test prompt", config)