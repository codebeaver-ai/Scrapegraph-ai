import pytest

from scrapegraphai.graphs import AbstractGraph, BaseGraph
from tests.graphs.abstract_graph_test import TestGraph

class TestAbstractGraph:
    class ConcreteGraph(AbstractGraph):
        def _create_graph(self) -> BaseGraph:
            return BaseGraph(nodes=[], edges=[], entry_point=None, graph_name="TestGraph")

        def run(self) -> str:
            return "Test run"

    def test_invalid_llm_provider(self):
        """
        Test that creating a concrete implementation of AbstractGraph with an invalid LLM provider raises a ValueError.
        The error message should contain information about the unsupported provider.
        """
        with pytest.raises(ValueError, match="Provider invalid_provider is not supported"):
            self.ConcreteGraph("Test prompt", {"llm": {"model": "invalid_provider/model"}})

    def test_invalid_llm_provider(self):
        """
        Test that creating a TestGraph with an invalid LLM provider raises a ValueError.
        The error message should contain information about the unsupported provider.
        """
        with pytest.raises(ValueError, match="Provider invalid_provider is not supported"):
            TestGraph("Test prompt", {"llm": {"model": "invalid_provider/model"}})