from tests.graphs.abstract_graph_test import TestGraph
import pytest
import re


class TestAbstractGraph:
    def test_invalid_llm_provider(self):
        """
        Test that creating a TestGraph (which inherits from AbstractGraph) with an invalid LLM provider
        raises a ValueError with the correct error message.
        """
        expected_error_message = (
            "Provider invalid_provider is not supported.\n"
            "                             If possible, try to use a model instance instead."
        )
        with pytest.raises(ValueError, match=re.escape(expected_error_message)):
            TestGraph("Test prompt", {"llm": {"model": "invalid_provider/model"}})
