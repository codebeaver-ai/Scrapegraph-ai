from unittest.mock import Mock, MagicMock
import pytest
from scrapegraphai.integrations.burr_bridge import BurrBridge
from burr.core import Action

from scrapegraphai.integrations.burr_bridge import parse_boolean_expression

from unittest.mock import Mock
from burr.core import State

def test_create_actions():
    # Mock BaseGraph
    mock_base_graph = Mock()

    # Create mock nodes
    mock_node1 = Mock()
    mock_node1.node_name = "node1"
    mock_node2 = Mock()
    mock_node2.node_name = "node2"

    # Set up the mock base graph
    mock_base_graph.nodes = [mock_node1, mock_node2]

    # Create BurrBridge instance
    burr_bridge = BurrBridge(mock_base_graph, {})

    # Call _create_actions
    actions = burr_bridge._create_actions()

    # Assert that the correct number of actions were created
    assert len(actions) == 2

    # Assert that the action names match the node names
    assert "node1" in actions
    assert "node2" in actions

    # Assert that the created actions are instances of BurrNodeBridge (which is a subclass of Action)
    assert isinstance(actions["node1"], Action)
    assert isinstance(actions["node2"], Action)

    # Assert that the BurrNodeBridge instances have the correct nodes
    assert actions["node1"].node == mock_node1
    assert actions["node2"].node == mock_node2

def test_parse_boolean_expression():
    # Test with a simple expression
    assert parse_boolean_expression("a AND b") == ["a", "b"]

    # Test with a more complex expression
    assert set(parse_boolean_expression("(x OR y) AND (z OR w)")) == set(["x", "y", "z", "w"])

    # Test with repeated keys
    assert parse_boolean_expression("a AND a AND b") == ["a", "b"]

    # Test with non-alphabetic characters
    assert parse_boolean_expression("key1 OR key2 AND key3") == ["key1", "key2", "key3"]

    # Test with an empty string
    assert parse_boolean_expression("") == []

def test_convert_state_from_burr():
    # Create a mock BurrBridge instance
    burr_bridge = BurrBridge(Mock(), {})

    # Create a mock Burr State object
    mock_state = Mock(spec=State)

    # Set up the mock state with some attributes
    mock_state.__dict__ = {
        'attr1': 'value1',
        'attr2': 42,
        'attr3': [1, 2, 3]
    }

    # Call the _convert_state_from_burr method
    result = burr_bridge._convert_state_from_burr(mock_state)

    # Assert that the result is a dictionary
    assert isinstance(result, dict)

    # Assert that all attributes from the mock state are in the result dictionary
    assert result == {
        'attr1': 'value1',
        'attr2': 42,
        'attr3': [1, 2, 3]
    }

    # Assert that getattr was called for each attribute
    for attr in mock_state.__dict__.keys():
        getattr(mock_state, attr)

    # Assert that getattr was called the correct number of times
    assert mock_state.__getattribute__.call_count == len(mock_state.__dict__)