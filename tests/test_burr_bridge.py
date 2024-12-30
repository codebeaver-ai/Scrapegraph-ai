import pytest
from unittest.mock import Mock, patch
from scrapegraphai.integrations.burr_bridge import BurrBridge, State
from scrapegraphai.base_graph import BaseGraph

from scrapegraphai.integrations.burr_bridge import parse_boolean_expression

from unittest.mock import Mock
from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge

from scrapegraphai.integrations.burr_bridge import BurrBridge

from burr.core import default

from scrapegraphai.integrations.burr_bridge import BurrBridge, ApplicationBuilder, State, ApplicationContext

from scrapegraphai.integrations.burr_bridge import BurrNodeBridge
from unittest.mock import Mock, MagicMock
from typing import Any

from burr.core import State

from scrapegraphai.integrations.burr_bridge import BurrNodeBridge, parse_boolean_expression

import inspect

import uuid

from scrapegraphai.integrations.burr_bridge import BurrBridge, ApplicationBuilder, ApplicationContext, tracking

from burr.core import Application, State

@pytest.fixture
def mock_base_graph():
    graph = Mock(spec=BaseGraph)
    graph.nodes = [Mock(node_name="node1"), Mock(node_name="node2")]
    graph.edges = {"node1": "node2"}
    graph.entry_point = "node1"
    return graph

@patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
def test_burr_bridge_execute(mock_app_builder, mock_base_graph):
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {"input1": "value1"}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    mock_app = Mock()
    mock_app_builder.return_value.build.return_value = mock_app

    mock_final_state = State({"output1": "result1"})
    mock_app.run.return_value = (Mock(), Mock(), mock_final_state)

    # Act
    result = bridge.execute(initial_state={"initial": "state"})

    # Assert
    assert result == {"output1": "result1"}
    mock_app.run.assert_called_once_with(
        halt_after=["node2"],  # Assumes the last node is the final node
        inputs={"input1": "value1"}
    )

def test_parse_boolean_expression():
    # Test case 1: Simple expression
    expression1 = "a AND b OR c"
    result1 = parse_boolean_expression(expression1)
    assert set(result1) == {"a", "b", "c"}

    # Test case 2: Expression with repeated keys
    expression2 = "x AND y OR x AND z"
    result2 = parse_boolean_expression(expression2)
    assert set(result2) == {"x", "y", "z"}

    # Test case 3: Expression with numbers and underscores
    expression3 = "key1 AND key_2 OR key3"
    result3 = parse_boolean_expression(expression3)
    assert set(result3) == {"key1", "key_2", "key3"}

    # Test case 4: Empty expression
    expression4 = ""
    result4 = parse_boolean_expression(expression4)
    assert result4 == []

def test_burr_bridge_create_actions():
    # Create a mock BaseGraph with two nodes
    mock_graph = Mock(spec=BaseGraph)
    mock_node1 = Mock(node_name="node1")
    mock_node2 = Mock(node_name="node2")
    mock_graph.nodes = [mock_node1, mock_node2]

    # Create a BurrBridge instance
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_graph, burr_config)

    # Call the _create_actions method
    actions = bridge._create_actions()

    # Assert that the correct number of actions were created
    assert len(actions) == 2

    # Assert that the actions are instances of BurrNodeBridge
    assert isinstance(actions["node1"], BurrNodeBridge)
    assert isinstance(actions["node2"], BurrNodeBridge)

    # Assert that the actions have the correct nodes
    assert actions["node1"].node == mock_node1
    assert actions["node2"].node == mock_node2

def test_convert_state_from_burr():
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(Mock(), burr_config)  # Mock the base_graph

    # Create a mock State object
    mock_state = Mock()
    mock_state.__dict__ = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

    # Act
    result = bridge._convert_state_from_burr(mock_state)

    # Assert
    assert isinstance(result, dict)
    assert result == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

def test_burr_bridge_create_transitions():
    # Create a mock BaseGraph with some edges
    mock_graph = Mock(spec=BaseGraph)
    mock_graph.edges = {
        "node1": "node2",
        "node2": "node3",
        "node3": "node4"
    }

    # Create a BurrBridge instance
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_graph, burr_config)

    # Call the _create_transitions method
    transitions = bridge._create_transitions()

    # Assert that the correct number of transitions were created
    assert len(transitions) == 3

    # Assert that the transitions have the correct structure
    expected_transitions = [
        ("node1", "node2", default),
        ("node2", "node3", default),
        ("node3", "node4", default)
    ]
    assert transitions == expected_transitions

@pytest.fixture
def mock_base_graph():
    graph = Mock(spec=BaseGraph)
    graph.entry_point = "start_node"
    return graph

@patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
@patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
@patch('scrapegraphai.integrations.burr_bridge.tracking')
def test_initialize_burr_app(mock_tracking, mock_app_context, mock_app_builder, mock_base_graph):
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    mock_builder = Mock()
    mock_app_builder.return_value = mock_builder
    mock_builder.with_actions.return_value = mock_builder
    mock_builder.with_transitions.return_value = mock_builder
    mock_builder.with_entrypoint.return_value = mock_builder
    mock_builder.with_state.return_value = mock_builder
    mock_builder.with_identifiers.return_value = mock_builder
    mock_builder.with_hooks.return_value = mock_builder
    mock_builder.with_tracker.return_value = mock_builder
    mock_builder.build.return_value = Mock()

    mock_app_context.get.return_value = None
    mock_tracking.LocalTrackingClient.return_value = Mock()

    # Act
    result = bridge._initialize_burr_app({"initial": "state"})

    # Assert
    assert result is not None
    mock_app_builder.assert_called_once()
    mock_builder.with_actions.assert_called_once()
    mock_builder.with_transitions.assert_called_once()
    mock_builder.with_entrypoint.assert_called_once_with("start_node")
    mock_builder.with_state.assert_called_once()
    mock_builder.with_identifiers.assert_called_once()
    mock_builder.with_hooks.assert_called_once()
    mock_builder.with_tracker.assert_called_once()
    mock_builder.build.assert_called_once()
    mock_tracking.LocalTrackingClient.assert_called_once_with(project="test_project")

def test_convert_state_from_burr():
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(Mock(), burr_config)  # Mock the base_graph

    # Create a mock State object
    mock_state = Mock()
    mock_state.__dict__ = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

    # Act
    result = bridge._convert_state_from_burr(mock_state)

    # Assert
    assert isinstance(result, dict)
    assert result == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

def test_parse_boolean_expression_complex():
    # Test case with a more complex expression
    complex_expression = "key1 AND (key2 OR key3) AND NOT key4 OR (key5 AND key6)"
    result = parse_boolean_expression(complex_expression)

    # Assert that all keys are extracted correctly
    assert set(result) == {"key1", "key2", "key3", "key4", "key5", "key6"}

    # Assert that the order doesn't matter (since we're using a set)
    assert len(result) == 6

    # Test with an expression containing numbers and special characters
    special_expression = "key_1 AND key2 OR key3_special!"
    special_result = parse_boolean_expression(special_expression)
    assert set(special_result) == {"key_1", "key2", "key3_special"}

def test_burr_node_bridge_run():
    # Arrange
    mock_node = MagicMock()
    mock_node.input = "input1 AND input2"
    mock_node.execute.return_value = {"output": "result"}

    bridge = BurrNodeBridge(mock_node)

    mock_state = Mock()
    mock_state.__getitem__.side_effect = lambda key: {
        "input1": "value1",
        "input2": "value2"
    }.get(key)

    # Act
    result = bridge.run(mock_state)

    # Assert
    assert result == {"output": "result"}
    mock_node.execute.assert_called_once_with({"input1": "value1", "input2": "value2"})

def test_burr_node_bridge_run():
    # Arrange
    mock_node = MagicMock()
    mock_node.input = "input1 AND input2"
    mock_node.execute.return_value = {"output": "result"}

    bridge = BurrNodeBridge(mock_node)

    mock_state = Mock(spec=State)
    mock_state.__getitem__.side_effect = lambda key: {
        "input1": "value1",
        "input2": "value2"
    }.get(key)

    # Act
    result = bridge.run(mock_state)

    # Assert
    assert result == {"output": "result"}
    mock_node.execute.assert_called_once_with({"input1": "value1", "input2": "value2"})

def test_burr_node_bridge_update():
    # Arrange
    mock_node = Mock()
    bridge = BurrNodeBridge(mock_node)

    # Create a mock State object
    mock_state = Mock(spec=State)

    # Create a result dictionary
    result = {"key1": "value1", "key2": "value2"}

    # Act
    updated_state = bridge.update(result, mock_state)

    # Assert
    mock_state.update.assert_called_once_with(**result)
    assert updated_state == mock_state.update.return_value

def test_burr_node_bridge_reads_property():
    # Arrange
    mock_node = Mock()
    mock_node.input = "key1 AND key2 OR key3"
    bridge = BurrNodeBridge(mock_node)

    # Act
    result = bridge.reads

    # Assert
    assert isinstance(result, list)
    assert set(result) == {"key1", "key2", "key3"}

    # Verify that parse_boolean_expression was called with the correct argument
    parsed_result = parse_boolean_expression(mock_node.input)
    assert set(result) == set(parsed_result)

def test_burr_bridge_create_actions():
    # Arrange
    mock_base_graph = Mock()
    mock_node1 = Mock(node_name="node1")
    mock_node2 = Mock(node_name="node2")
    mock_base_graph.nodes = [mock_node1, mock_node2]

    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    # Act
    actions = bridge._create_actions()

    # Assert
    assert len(actions) == 2
    assert isinstance(actions["node1"], BurrNodeBridge)
    assert isinstance(actions["node2"], BurrNodeBridge)
    assert actions["node1"].node == mock_node1
    assert actions["node2"].node == mock_node2

def test_burr_node_bridge_get_source():
    # Define a simple class to use as our mock node
    class MockNode:
        def some_method(self):
            pass

    # Create a mock node instance
    mock_node = Mock(spec=MockNode)

    # Create a BurrNodeBridge instance with the mock node
    bridge = BurrNodeBridge(mock_node)

    # Get the source code using the get_source method
    source = bridge.get_source()

    # Get the expected source code using inspect
    expected_source = inspect.getsource(MockNode)

    # Assert that the returned source matches the expected source
    assert source == expected_source, "The returned source code does not match the expected source code"

def test_burr_bridge_create_transitions():
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
    bridge = BurrBridge(mock_base_graph, burr_config)

    # Act
    transitions = bridge._create_transitions()

    # Assert
    expected_transitions = [
        ("node1", "node2", default),
        ("node2", "node3", default),
        ("node3", "node4", default)
    ]
    assert transitions == expected_transitions

@pytest.fixture
def mock_base_graph():
    return Mock()

@patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
@patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
@patch('scrapegraphai.integrations.burr_bridge.tracking')
@patch('uuid.uuid4')
def test_initialize_burr_app_with_application_context(mock_uuid4, mock_tracking, mock_app_context, mock_app_builder, mock_base_graph):
    # Arrange
    mock_uuid4.return_value = "test-uuid"
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    mock_builder = Mock()
    mock_app_builder.return_value = mock_builder
    mock_builder.with_actions.return_value = mock_builder
    mock_builder.with_transitions.return_value = mock_builder
    mock_builder.with_entrypoint.return_value = mock_builder
    mock_builder.with_state.return_value = mock_builder
    mock_builder.with_identifiers.return_value = mock_builder
    mock_builder.with_hooks.return_value = mock_builder
    mock_builder.with_tracker.return_value = mock_builder
    mock_builder.with_spawning_parent.return_value = mock_builder
    mock_builder.build.return_value = Mock()

    mock_context = Mock()
    mock_context.tracker = Mock()
    mock_context.app_id = "parent-app-id"
    mock_context.sequence_id = "parent-sequence-id"
    mock_context.partition_key = "parent-partition-key"
    mock_app_context.get.return_value = mock_context

    # Act
    result = bridge._initialize_burr_app({"initial": "state"})

    # Assert
    assert result is not None
    mock_app_builder.assert_called_once()
    mock_builder.with_actions.assert_called_once()
    mock_builder.with_transitions.assert_called_once()
    mock_builder.with_entrypoint.assert_called_once()
    mock_builder.with_state.assert_called_once()
    mock_builder.with_identifiers.assert_called_once_with(app_id="test-uuid")
    mock_builder.with_hooks.assert_called_once()
    mock_builder.with_tracker.assert_called_once_with(mock_context.tracker.copy.return_value)
    mock_builder.with_spawning_parent.assert_called_once_with(
        "parent-app-id", "parent-sequence-id", "parent-partition-key"
    )
    mock_builder.build.assert_called_once()

def test_burr_node_bridge_writes_property():
    # Arrange
    mock_node = Mock()
    mock_node.output = ["output1", "output2"]
    bridge = BurrNodeBridge(mock_node)

    # Act
    result = bridge.writes

    # Assert
    assert result == ["output1", "output2"]
    assert isinstance(result, list)

@pytest.fixture
def mock_base_graph():
    return Mock()

@patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
@patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
@patch('scrapegraphai.integrations.burr_bridge.tracking')
@patch('uuid.uuid4')
def test_initialize_burr_app_with_application_context(mock_uuid4, mock_tracking, mock_app_context, mock_app_builder, mock_base_graph):
    # Arrange
    mock_uuid4.return_value = "test-uuid"
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    mock_builder = Mock()
    mock_app_builder.return_value = mock_builder
    mock_builder.with_actions.return_value = mock_builder
    mock_builder.with_transitions.return_value = mock_builder
    mock_builder.with_entrypoint.return_value = mock_builder
    mock_builder.with_state.return_value = mock_builder
    mock_builder.with_identifiers.return_value = mock_builder
    mock_builder.with_hooks.return_value = mock_builder
    mock_builder.with_tracker.return_value = mock_builder
    mock_builder.with_spawning_parent.return_value = mock_builder
    mock_builder.build.return_value = Mock()

    mock_context = Mock()
    mock_context.tracker = Mock()
    mock_context.app_id = "parent-app-id"
    mock_context.sequence_id = "parent-sequence-id"
    mock_context.partition_key = "parent-partition-key"
    mock_app_context.get.return_value = mock_context

    # Act
    result = bridge._initialize_burr_app({"initial": "state"})

    # Assert
    assert result is not None
    mock_app_builder.assert_called_once()
    mock_builder.with_actions.assert_called_once()
    mock_builder.with_transitions.assert_called_once()
    mock_builder.with_entrypoint.assert_called_once()
    mock_builder.with_state.assert_called_once()
    mock_builder.with_identifiers.assert_called_once_with(app_id="test-uuid")
    mock_builder.with_hooks.assert_called_once()
    mock_builder.with_tracker.assert_called_once_with(mock_context.tracker.copy.return_value)
    mock_builder.with_spawning_parent.assert_called_once_with(
        "parent-app-id", "parent-sequence-id", "parent-partition-key"
    )
    mock_builder.build.assert_called_once()

def test_convert_state_from_burr():
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {}
    }
    bridge = BurrBridge(Mock(), burr_config)  # Mock the base_graph

    # Create a mock State object
    mock_state = Mock(spec=State)
    mock_state.__dict__ = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

    # Act
    result = bridge._convert_state_from_burr(mock_state)

    # Assert
    assert isinstance(result, dict)
    assert result == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

@pytest.fixture
def mock_base_graph():
    graph = Mock(spec=BaseGraph)
    graph.entry_point = "start_node"
    return graph

@patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
def test_burr_bridge_execute(mock_app_builder, mock_base_graph):
    # Arrange
    burr_config = {
        "project_name": "test_project",
        "app_instance_id": "test_instance",
        "inputs": {"input1": "value1"}
    }
    bridge = BurrBridge(mock_base_graph, burr_config)

    mock_app = Mock(spec=Application)
    mock_app_builder.return_value.build.return_value = mock_app

    mock_final_state = State({"output1": "result1"})
    mock_app.run.return_value = (Mock(), Mock(), mock_final_state)

    # Act
    result = bridge.execute(initial_state={"initial": "state"})

    # Assert
    assert result == {"output1": "result1"}
    mock_app.run.assert_called_once_with(
        halt_after=[mock_app.graph.actions[-1].name],
        inputs={"input1": "value1"}
    )
    mock_app_builder.assert_called_once()