import pytest
import uuid

from burr.core import State
from scrapegraphai.integrations.burr_bridge import ApplicationContext, BurrBridge, BurrNodeBridge, State, default, parse_boolean_expression, tracking
from unittest.mock import Mock, patch

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

    # ... existing tests ...

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
    @patch('scrapegraphai.integrations.burr_bridge.State')
    def test_execute(self, mock_State, mock_Application, mock_ApplicationBuilder):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="start_node"), Mock(node_name="end_node")]
        mock_base_graph.edges = {"start_node": "end_node"}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project", "inputs": {"input_key": "input_value"}}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock the ApplicationBuilder and Application
        mock_builder = Mock()
        mock_ApplicationBuilder.return_value = mock_builder
        mock_app = Mock()
        mock_builder.build.return_value = mock_app

        # Mock the State
        mock_final_state = Mock()
        mock_final_state.__dict__ = {"result_key": "result_value"}
        mock_app.run.return_value = (Mock(), Mock(), mock_final_state)

        # Execute the Burr application
        initial_state = {"initial_key": "initial_value"}
        result = burr_bridge.execute(initial_state)

        # Assert that the application was built and run correctly
        mock_ApplicationBuilder.assert_called_once()
        mock_app.run.assert_called_once()

        # Assert that the result is correct
        assert result == {"result_key": "result_value"}

        # Assert that the initial state was used
        mock_State.assert_called_once_with(initial_state)

    # ... existing tests ...

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('uuid.uuid4')
    def test_initialize_burr_app_with_context(self, mock_uuid4, mock_ApplicationContext, mock_ApplicationBuilder):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="start_node")]
        mock_base_graph.edges = {}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock ApplicationContext
        mock_context = Mock()
        mock_tracker = Mock(spec=tracking.LocalTrackingClient)
        mock_context.tracker = mock_tracker
        mock_context.app_id = "parent_app_id"
        mock_context.sequence_id = "parent_sequence_id"
        mock_context.partition_key = "parent_partition_key"
        mock_ApplicationContext.get.return_value = mock_context

        # Mock uuid4
        mock_uuid4.return_value = "mocked-uuid"

        # Mock the ApplicationBuilder
        mock_builder = Mock()
        mock_ApplicationBuilder.return_value = mock_builder

        # Initialize the Burr app
        burr_bridge._initialize_burr_app()

        # Assert that ApplicationBuilder was called with the correct parameters
        mock_ApplicationBuilder.assert_called_once()
        mock_builder.with_tracker.assert_called_once_with(mock_tracker.copy())
        mock_builder.with_spawning_parent.assert_called_once_with(
            "parent_app_id",
            "parent_sequence_id",
            "parent_partition_key"
        )
        mock_builder.with_identifiers.assert_called_once_with(app_id="mocked-uuid")

        # Assert that the application was built
        mock_builder.build.assert_called_once()

    # ... existing tests ...

    def test_parse_boolean_expression(self):
        # Test simple expression
        assert parse_boolean_expression("a AND b") == ["a", "b"]

        # Test expression with parentheses
        assert set(parse_boolean_expression("(a OR b) AND c")) == set(["a", "b", "c"])

        # Test expression with duplicates
        assert set(parse_boolean_expression("a AND b OR a")) == set(["a", "b"])

        # Test complex expression
        complex_expr = "((x AND y) OR (z AND w)) AND (v OR u)"
        assert set(parse_boolean_expression(complex_expr)) == set(["x", "y", "z", "w", "v", "u"])

        # Test expression with numbers
        assert set(parse_boolean_expression("field1 AND field2 OR field3")) == set(["field1", "field2", "field3"])

        # Test empty expression
        assert parse_boolean_expression("") == []

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('uuid.uuid4')
    def test_initialize_burr_app_without_context(self, mock_uuid4, mock_ApplicationContext, mock_ApplicationBuilder):
        # Create a mock BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="start_node")]
        mock_base_graph.edges = {}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock ApplicationContext to return None
        mock_ApplicationContext.get.return_value = None

        # Mock uuid4
        mock_uuid4.return_value = "mocked-uuid"

        # Mock the ApplicationBuilder
        mock_builder = Mock()
        mock_ApplicationBuilder.return_value = mock_builder

        # Mock LocalTrackingClient
        mock_tracking_client = Mock(spec=tracking.LocalTrackingClient)
        with patch('scrapegraphai.integrations.burr_bridge.tracking.LocalTrackingClient', return_value=mock_tracking_client):
            # Initialize the Burr app
            burr_bridge._initialize_burr_app()

        # Assert that ApplicationBuilder was called with the correct parameters
        mock_ApplicationBuilder.assert_called_once()
        mock_builder.with_tracker.assert_called_once_with(mock_tracking_client)
        mock_builder.with_identifiers.assert_called_once_with(app_id="mocked-uuid")

        # Assert that with_spawning_parent was not called
        mock_builder.with_spawning_parent.assert_not_called()

        # Assert that the application was built
        mock_builder.build.assert_called_once()

class TestBurrNodeBridge:
    def test_burr_node_bridge_run(self):
        # Create a mock node
        mock_node = Mock()
        mock_node.input = "input1 AND input2"
        mock_node.execute = Mock(return_value={"output": "result"})

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Create a State object
        state = State({"input1": "value1", "input2": "value2", "input3": "value3"})

        # Run the bridge
        result = bridge.run(state)

        # Assert that the node's execute method was called with the correct inputs
        mock_node.execute.assert_called_once_with({"input1": "value1", "input2": "value2"})

        # Assert that the result is correct
        assert result == {"output": "result"}

    # ... existing tests ...

    def test_convert_state_from_burr(self):
        # Create a mock BaseGraph and config
        mock_base_graph = Mock()
        burr_config = {"project_name": "test_project"}

        # Create a BurrBridge instance
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Create a mock Burr State object
        mock_state = Mock(spec=State)
        mock_state.__dict__ = {
            "attr1": "value1",
            "attr2": 42,
            "attr3": ["list", "of", "values"]
        }

        # Call the _convert_state_from_burr method
        result = burr_bridge._convert_state_from_burr(mock_state)

        # Assert that the result is a dictionary with all the State attributes
        assert isinstance(result, dict)
        assert result == {
            "attr1": "value1",
            "attr2": 42,
            "attr3": ["list", "of", "values"]
        }

    def test_burr_node_bridge_reads_and_writes(self):
        # Create a mock node
        mock_node = Mock()
        mock_node.input = "input1 AND (input2 OR input3)"
        mock_node.output = ["output1", "output2"]

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Test the reads property
        assert set(bridge.reads) == set(["input1", "input2", "input3"])

        # Test the writes property
        assert bridge.writes == ["output1", "output2"]