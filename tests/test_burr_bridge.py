import pytest

from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge, State, default, parse_boolean_expression
from unittest.mock import MagicMock, Mock, patch

class TestBurrBridge:
    def test_create_actions(self):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_node1 = Mock(node_name="node1")
        mock_node2 = Mock(node_name="node2")
        mock_base_graph.nodes = [mock_node1, mock_node2]

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_actions method
        actions = burr_bridge._create_actions()

        # Assert that the correct number of actions were created
        assert len(actions) == 2

        # Assert that the actions are instances of BurrNodeBridge
        assert isinstance(actions["node1"], BurrNodeBridge)
        assert isinstance(actions["node2"], BurrNodeBridge)

        # Assert that the actions have the correct nodes
        assert actions["node1"].node == mock_node1
        assert actions["node2"].node == mock_node2

    def test_create_transitions(self):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.edges = {
            "node1": "node2",
            "node2": "node3"
        }

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_transitions method
        transitions = burr_bridge._create_transitions()

        # Assert that the correct transitions were created
        expected_transitions = [
            ("node1", "node2", default),
            ("node2", "node3", default)
        ]
        assert transitions == expected_transitions

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.Application')
    def test_execute(self, mock_Application, mock_ApplicationBuilder):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="start_node"), Mock(node_name="end_node")]
        mock_base_graph.edges = {"start_node": "end_node"}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project", "inputs": {"input_key": "input_value"}}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock the ApplicationBuilder and its methods
        mock_builder = MagicMock()
        mock_ApplicationBuilder.return_value = mock_builder
        mock_builder.build.return_value = mock_Application

        # Mock the Application.run method
        mock_last_action = Mock()
        mock_result = Mock()
        mock_final_state = Mock()
        mock_final_state.__dict__ = {"output_key": "output_value"}
        mock_Application.run.return_value = (mock_last_action, mock_result, mock_final_state)

        # Execute the BurrBridge
        initial_state = {"initial_key": "initial_value"}
        result = burr_bridge.execute(initial_state)

        # Assert that the ApplicationBuilder was called with the correct arguments
        mock_ApplicationBuilder.assert_called_once()
        mock_builder.with_actions.assert_called_once()
        mock_builder.with_transitions.assert_called_once()
        mock_builder.with_entrypoint.assert_called_once_with("start_node")
        mock_builder.with_state.assert_called_once()
        mock_builder.with_identifiers.assert_called_once()
        mock_builder.with_hooks.assert_called_once()
        mock_builder.build.assert_called_once()

        # Assert that the Application.run method was called with the correct arguments
        mock_Application.run.assert_called_once_with(
            halt_after=["end_node"],
            inputs={"input_key": "input_value"}
        )

        # Assert that the result is correct
        assert result == {"output_key": "output_value"}

    def test_parse_boolean_expression(self):
        # Test simple expression
        assert parse_boolean_expression("a and b") == ["a", "b"]

        # Test complex expression
        assert set(parse_boolean_expression("(a or b) and (c or d)")) == set(["a", "b", "c", "d"])

        # Test expression with repeated keys
        assert parse_boolean_expression("a and b or a and c") == ["a", "b", "c"]

        # Test expression with numbers in variable names
        assert parse_boolean_expression("var1 and var2 or var3") == ["var1", "var2", "var3"]

        # Test empty expression
        assert parse_boolean_expression("") == []

    def test_burr_node_bridge_reads_property(self):
        # Create a mock node with a boolean expression as input
        mock_node = Mock()
        mock_node.input = "a and b or c"

        # Create a BurrNodeBridge instance
        burr_node_bridge = BurrNodeBridge(mock_node)

        # Test that the reads property correctly parses the input expression
        assert set(burr_node_bridge.reads) == set(["a", "b", "c"])

        # Test with a more complex expression
        mock_node.input = "(x or y) and (z or w)"
        assert set(burr_node_bridge.reads) == set(["x", "y", "z", "w"])

        # Test with an empty expression
        mock_node.input = ""
        assert burr_node_bridge.reads == []

    def test_burr_node_bridge_run(self):
        # Create a mock node
        mock_node = Mock()
        mock_node.input = "input1 and input2"
        mock_node.output = ["output1", "output2"]
        mock_node.execute.return_value = {"output1": "result1", "output2": "result2"}

        # Create a BurrNodeBridge instance
        burr_node_bridge = BurrNodeBridge(mock_node)

        # Create a mock state
        mock_state = State({"input1": "value1", "input2": "value2", "other": "value3"})

        # Run the BurrNodeBridge
        result = burr_node_bridge.run(mock_state)

        # Assert that the node's execute method was called with the correct inputs
        mock_node.execute.assert_called_once_with({"input1": "value1", "input2": "value2"})

        # Assert that the result is correct
        assert result == {"output1": "result1", "output2": "result2"}

        # Test the update method
        updated_state = burr_node_bridge.update(result, mock_state)

        # Assert that the state was correctly updated
        assert updated_state.output1 == "result1"
        assert updated_state.output2 == "result2"
        assert updated_state.other == "value3"  # Ensure other state values are preserved