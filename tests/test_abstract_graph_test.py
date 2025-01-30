import pytest
from tests.graphs.abstract_graph_test import TestGraph


class TestAbstractGraph:
    def test_invalid_llm_provider(self):
        """
        Test that creating a concrete subclass of AbstractGraph with an invalid LLM provider raises a ValueError
        with the expected error message.
        """
        with pytest.raises(ValueError, match="Provider invalid_provider is not supported"):
            TestGraph("Test prompt", {"llm": {"model": "invalid_provider/model"}})
