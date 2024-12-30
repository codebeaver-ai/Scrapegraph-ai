import pytest
from unittest.mock import Mock, patch
from scrapegraphai.integrations.burr_bridge import BurrBridge

from scrapegraphai.integrations.burr_bridge import parse_boolean_expression

from scrapegraphai.integrations.burr_bridge import BurrBridge, State

from unittest.mock import Mock
from burr.core import State

from burr.core import default

from scrapegraphai.integrations.burr_bridge import BurrNodeBridge, parse_boolean_expression

import uuid

from scrapegraphai.integrations.burr_bridge import BurrNodeBridge

# Mock the burr library
burr_mock = Mock()
burr_mock.tracking = Mock()
burr_mock.core = Mock()
burr_mock.lifecycle = Mock()

# Mock the BaseGraph class
class MockBaseGraph:
    def __init__(self):
        self.nodes = [
            Mock(node_name="node1"),
            Mock(node_name="node2"),
            Mock(node_name="node3")
        ]

# Apply the mock to the burr import
@pytest.fixture(autouse=True)
def mock_burr(monkeypatch):
    monkeypatch.setattr("scrapegraphai.integrations.burr_bridge.burr", burr_mock)

class TestBurrBridge:
    @patch('scrapegraphai.integrations.burr_bridge.BurrNodeBridge')
    def test_create_actions(self, mock_burr_node_bridge):
        # Arrange
        mock_graph = MockBaseGraph()
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {}
        }
        burr_bridge = BurrBridge(mock_graph, burr_config)

        # Act
        actions = burr_bridge._create_actions()

        # Assert
        assert len(actions) == 3
        assert "node1" in actions
        assert "node2" in actions
        assert "node3" in actions
        assert mock_burr_node_bridge.call_count == 3
        for node in mock_graph.nodes:
            mock_burr_node_bridge.assert_any_call(node)

class TestParseBoolean:
    def test_parse_boolean_expression(self):
        # Test case 1: Simple expression
        expression1 = "key1 AND key2"
        result1 = parse_boolean_expression(expression1)
        assert set(result1) == {"key1", "key2"}

        # Test case 2: Complex expression with multiple operators
        expression2 = "key1 AND (key2 OR key3) AND NOT key4"
        result2 = parse_boolean_expression(expression2)
        assert set(result2) == {"key1", "key2", "key3", "key4"}

        # Test case 3: Expression with repeated keys
        expression3 = "key1 AND key1 OR key2"
        result3 = parse_boolean_expression(expression3)
        assert set(result3) == {"key1", "key2"}

        # Test case 4: Empty expression
        expression4 = ""
        result4 = parse_boolean_expression(expression4)
        assert result4 == []

class TestBurrBridgeExecute:
    @patch('scrapegraphai.integrations.burr_bridge.BurrBridge._initialize_burr_app')
    def test_execute(self, mock_initialize_burr_app):
        # Arrange
        mock_base_graph = Mock()
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {"input1": "value1"}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        mock_app = Mock()
        mock_app.run.return_value = ("last_action", "result", State({"output1": "value1", "output2": "value2"}))
        mock_initialize_burr_app.return_value = mock_app

        initial_state = {"initial_key": "initial_value"}

        # Act
        result = burr_bridge.execute(initial_state)

        # Assert
        mock_initialize_burr_app.assert_called_once_with(initial_state)
        mock_app.run.assert_called_once_with(halt_after=['last_action'], inputs={"input1": "value1"})
        assert result == {"output1": "value1", "output2": "value2"}

    def test_convert_state_from_burr(self):
        # Arrange
        burr_bridge = BurrBridge(Mock(), {})
        mock_state = Mock(spec=State)
        mock_state.__dict__ = {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }

        # Act
        result = burr_bridge._convert_state_from_burr(mock_state)

        # Assert
        assert result == {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }
        assert len(result) == 3

class TestBurrBridgeTransitions:
    def test_create_transitions(self):
        # Arrange
        mock_base_graph = Mock()
        mock_base_graph.edges = {
            "node1": "node2",
            "node2": "node3",
            "node3": "node4"
        }
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Act
        transitions = burr_bridge._create_transitions()

        # Assert
        expected_transitions = [
            ("node1", "node2", default),
            ("node2", "node3", default),
            ("node3", "node4", default)
        ]
        assert transitions == expected_transitions
        assert len(transitions) == 3
        for transition in transitions:
            assert len(transition) == 3
            assert isinstance(transition[0], str)
            assert isinstance(transition[1], str)
            assert transition[2] == default

class TestBurrNodeBridge:
    def test_reads_property(self):
        # Arrange
        mock_node = Mock()
        mock_node.input = "key1 AND key2 OR key3"
        bridge = BurrNodeBridge(mock_node)

        # Act
        result = bridge.reads

        # Assert
        assert result == parse_boolean_expression(mock_node.input)
        assert set(result) == {"key1", "key2", "key3"}

class TestBurrBridgeInitializeApp:
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('scrapegraphai.integrations.burr_bridge.tracking')
    @patch('scrapegraphai.integrations.burr_bridge.uuid.uuid4')
    def test_initialize_burr_app(self, mock_uuid4, mock_tracking, mock_application_context, mock_application_builder):
        # Arrange
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        mock_builder = Mock()
        mock_application_builder.return_value = mock_builder
        mock_builder.with_actions.return_value = mock_builder
        mock_builder.with_transitions.return_value = mock_builder
        mock_builder.with_entrypoint.return_value = mock_builder
        mock_builder.with_state.return_value = mock_builder
        mock_builder.with_identifiers.return_value = mock_builder
        mock_builder.with_hooks.return_value = mock_builder
        mock_builder.with_tracker.return_value = mock_builder
        mock_builder.build.return_value = Mock()

        mock_application_context.get.return_value = None
        mock_uuid4.return_value = "mocked-uuid"

        # Act
        result = burr_bridge._initialize_burr_app({"initial_key": "initial_value"})

        # Assert
        mock_application_builder.assert_called_once()
        mock_builder.with_actions.assert_called_once()
        mock_builder.with_transitions.assert_called_once()
        mock_builder.with_entrypoint.assert_called_once_with("start_node")
        mock_builder.with_state.assert_called_once()
        mock_builder.with_identifiers.assert_called_once_with(app_id="mocked-uuid")
        mock_builder.with_hooks.assert_called_once()
        mock_builder.with_tracker.assert_called_once()
        mock_builder.build.assert_called_once()

        assert result == mock_builder.build.return_value

    def test_run(self):
        # Arrange
        mock_node = Mock()
        mock_node.execute.return_value = {"result_key": "result_value"}
        bridge = BurrNodeBridge(mock_node)

        mock_state = Mock(spec=State)
        mock_state.__getitem__.side_effect = lambda key: f"value_{key}"

        # Act
        result = bridge.run(mock_state, additional_kwarg="test")

        # Assert
        mock_node.execute.assert_called_once_with(
            {"key1": "value_key1", "key2": "value_key2", "key3": "value_key3"},
            additional_kwarg="test"
        )
        assert result == {"result_key": "result_value"}

    def test_update(self):
        # Arrange
        mock_node = Mock()
        bridge = BurrNodeBridge(mock_node)

        mock_state = Mock(spec=State)
        mock_state.update.return_value = State({"key1": "updated_value1", "key2": "value2"})

        result = {"key1": "updated_value1"}

        # Act
        updated_state = bridge.update(result, mock_state)

        # Assert
        mock_state.update.assert_called_once_with(**result)
        assert isinstance(updated_state, State)
        assert updated_state["key1"] == "updated_value1"
        assert updated_state["key2"] == "value2"

    def test_writes_property(self):
        # Arrange
        mock_node = Mock()
        mock_node.output = ["output1", "output2", "output3"]
        bridge = BurrNodeBridge(mock_node)

        # Act
        result = bridge.writes

        # Assert
        assert result == mock_node.output
        assert len(result) == 3
        assert "output1" in result
        assert "output2" in result
        assert "output3" in result