from unittest import TestCase
from unittest.mock import Mock, patch
from typing import Any
from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge

from scrapegraphai.integrations.burr_bridge import BurrBridge

from burr.core import State

from unittest.mock import Mock

import unittest
from scrapegraphai.integrations.burr_bridge import parse_boolean_expression

from scrapegraphai.integrations.burr_bridge import BurrNodeBridge

from burr.core import ApplicationBuilder, State, ApplicationContext
from burr.tracking import LocalTrackingClient

from burr.core import ApplicationBuilder, State
from burr import tracking

from scrapegraphai.integrations.burr_bridge import PrintLnHook

class TestBurrBridge(TestCase):
    def test_create_actions(self):
        # Mock the base graph
        mock_base_graph = Mock()

        # Create mock nodes
        mock_node1 = Mock()
        mock_node1.node_name = "node1"
        mock_node2 = Mock()
        mock_node2.node_name = "node2"

        # Set up the mock base graph
        mock_base_graph.nodes = [mock_node1, mock_node2]

        # Create a BurrBridge instance with the mock base graph
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_actions method
        actions = burr_bridge._create_actions()

        # Assert that the correct number of actions were created
        self.assertEqual(len(actions), 2)

        # Assert that the actions are instances of BurrNodeBridge
        self.assertIsInstance(actions["node1"], BurrNodeBridge)
        self.assertIsInstance(actions["node2"], BurrNodeBridge)

        # Assert that the actions have the correct nodes
        self.assertEqual(actions["node1"].node, mock_node1)
        self.assertEqual(actions["node2"].node, mock_node2)

    def test_create_transitions(self):
        # Mock the base graph
        mock_base_graph = Mock()

        # Set up the mock edges
        mock_base_graph.edges = {
            "node1": "node2",
            "node2": "node3",
            "node3": "node4"
        }

        # Create a BurrBridge instance with the mock base graph
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_transitions method
        transitions = burr_bridge._create_transitions()

        # Assert that the correct number of transitions were created
        self.assertEqual(len(transitions), 3)

        # Assert that the transitions have the correct structure
        expected_transitions = [
            ("node1", "node2", burr_bridge._create_transitions.__globals__['default']),
            ("node2", "node3", burr_bridge._create_transitions.__globals__['default']),
            ("node3", "node4", burr_bridge._create_transitions.__globals__['default'])
        ]
        self.assertEqual(transitions, expected_transitions)

    @patch('scrapegraphai.integrations.burr_bridge.BurrBridge._initialize_burr_app')
    def test_execute(self, mock_initialize_burr_app):
        # Create a mock base graph
        mock_base_graph = Mock()

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Create a mock Burr application
        mock_app = Mock()
        mock_initialize_burr_app.return_value = mock_app

        # Create a mock final state
        mock_final_state = State({"result": "success"})

        # Set up the mock app's run method to return a tuple
        mock_app.run.return_value = (Mock(), Mock(), mock_final_state)

        # Set up the mock app's graph
        mock_app.graph.actions = [Mock(name="final_action")]

        # Execute the Burr application
        initial_state = {"input": "test"}
        result = burr_bridge.execute(initial_state)

        # Assert that _initialize_burr_app was called with the initial state
        mock_initialize_burr_app.assert_called_once_with(initial_state)

        # Assert that the app's run method was called with the correct arguments
        mock_app.run.assert_called_once_with(halt_after=["final_action"], inputs={})

        # Assert that the result is correct
        self.assertEqual(result, {"result": "success"})

    def test_convert_state_from_burr(self):
        # Create a mock base graph
        mock_base_graph = Mock()

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Create a mock Burr State
        test_state = State({"key1": "value1", "key2": 42})

        # Call the _convert_state_from_burr method
        result = burr_bridge._convert_state_from_burr(test_state)

        # Assert that the result is a dictionary
        self.assertIsInstance(result, dict)

        # Assert that the dictionary contains the correct key-value pairs
        self.assertEqual(result, {"key1": "value1", "key2": 42})

        # Test with an empty State
        empty_state = State()
        empty_result = burr_bridge._convert_state_from_burr(empty_state)
        self.assertEqual(empty_result, {})

class TestParseBooleanExpression(unittest.TestCase):
    def test_parse_boolean_expression(self):
        # Test with a simple expression
        self.assertEqual(parse_boolean_expression("a AND b"), ["a", "b"])

        # Test with a more complex expression
        self.assertEqual(set(parse_boolean_expression("(a OR b) AND (c OR d)")), {"a", "b", "c", "d"})

        # Test with repeated variables
        self.assertEqual(parse_boolean_expression("a AND a AND b"), ["a", "b"])

        # Test with non-alphabetic characters
        self.assertEqual(parse_boolean_expression("x1 AND y2 OR z3"), ["x1", "y2", "z3"])

        # Test with an empty string
        self.assertEqual(parse_boolean_expression(""), [])

        # Test with only boolean operators
        self.assertEqual(parse_boolean_expression("AND OR NOT"), [])

if __name__ == '__main__':
    unittest.main()

class TestBurrNodeBridge(unittest.TestCase):
    def test_run_method(self):
        # Create a mock node
        mock_node = Mock()
        mock_node.input = "a AND b"
        mock_node.execute.return_value = {"result": "success"}

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Create a mock State
        mock_state = State({"a": 1, "b": 2, "c": 3})

        # Run the method
        result = bridge.run(mock_state)

        # Assert that the node's execute method was called with the correct arguments
        mock_node.execute.assert_called_once_with({"a": 1, "b": 2})

        # Assert that the result is correct
        self.assertEqual(result, {"result": "success"})

if __name__ == '__main__':
    unittest.main()

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('scrapegraphai.integrations.burr_bridge.tracking.LocalTrackingClient')
    def test_initialize_burr_app(self, mock_local_tracking_client, mock_application_context, mock_application_builder):
        # Mock the base graph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="node1"), Mock(node_name="node2")]
        mock_base_graph.edges = {"node1": "node2"}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project", "app_instance_id": "test-instance"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock ApplicationContext
        mock_context = Mock()
        mock_context.tracker = None
        mock_context.app_id = "parent_app_id"
        mock_context.sequence_id = "parent_sequence_id"
        mock_context.partition_key = "parent_partition_key"
        mock_application_context.get.return_value = mock_context

        # Mock ApplicationBuilder
        mock_builder = Mock()
        mock_application_builder.return_value = mock_builder

        # Call the method
        initial_state = {"key": "value"}
        burr_bridge._initialize_burr_app(initial_state)

        # Assert that ApplicationBuilder was called and methods were chained correctly
        mock_application_builder.assert_called_once()
        mock_builder.with_actions.assert_called_once()
        mock_builder.with_transitions.assert_called_once()
        mock_builder.with_entrypoint.assert_called_once_with("start_node")
        mock_builder.with_state.assert_called_once()
        mock_builder.with_identifiers.assert_called_once()
        mock_builder.with_hooks.assert_called_once()
        mock_builder.with_tracker.assert_called_once()
        mock_builder.with_spawning_parent.assert_called_once_with("parent_app_id", "parent_sequence_id", "parent_partition_key")
        mock_builder.build.assert_called_once()

        # Assert that LocalTrackingClient was not called (because we have a parent context)
        mock_local_tracking_client.assert_not_called()

if __name__ == '__main__':
    unittest.main()

class TestBurrBridgeNoContext(unittest.TestCase):
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('scrapegraphai.integrations.burr_bridge.tracking.LocalTrackingClient')
    def test_initialize_burr_app_no_context(self, mock_local_tracking_client, mock_application_context, mock_application_builder):
        # Mock the base graph
        mock_base_graph = Mock()
        mock_base_graph.entry_point = "start_node"
        mock_base_graph.nodes = [Mock(node_name="node1"), Mock(node_name="node2")]
        mock_base_graph.edges = {"node1": "node2"}

        # Create a BurrBridge instance
        burr_config = {"project_name": "test_project", "app_instance_id": "test-instance"}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock ApplicationContext to return None
        mock_application_context.get.return_value = None

        # Mock ApplicationBuilder
        mock_builder = Mock()
        mock_application_builder.return_value = mock_builder

        # Call the method
        initial_state = {"key": "value"}
        burr_bridge._initialize_burr_app(initial_state)

        # Assert that ApplicationBuilder was called and methods were chained correctly
        mock_application_builder.assert_called_once()
        mock_builder.with_actions.assert_called_once()
        mock_builder.with_transitions.assert_called_once()
        mock_builder.with_entrypoint.assert_called_once_with("start_node")
        mock_builder.with_state.assert_called_once()
        mock_builder.with_identifiers.assert_called_once()
        mock_builder.with_hooks.assert_called_once()

        # Assert that LocalTrackingClient was called with the correct project name
        mock_local_tracking_client.assert_called_once_with(project="test_project")

        # Assert that with_tracker was called with the new LocalTrackingClient instance
        mock_builder.with_tracker.assert_called_once_with(mock_local_tracking_client.return_value)

        # Assert that with_spawning_parent was not called
        mock_builder.with_spawning_parent.assert_not_called()

        mock_builder.build.assert_called_once()

if __name__ == '__main__':
    unittest.main()

class TestPrintLnHook(unittest.TestCase):
    def setUp(self):
        self.hook = PrintLnHook()
        self.mock_state = Mock()
        self.mock_action = Mock()
        self.mock_action.name = "TestAction"

    @patch('builtins.print')
    def test_pre_run_step(self, mock_print):
        self.hook.pre_run_step(state=self.mock_state, action=self.mock_action)
        mock_print.assert_called_once_with("Starting action: TestAction")

    @patch('builtins.print')
    def test_post_run_step(self, mock_print):
        self.hook.post_run_step(state=self.mock_state, action=self.mock_action)
        mock_print.assert_called_once_with("Finishing action: TestAction")

if __name__ == '__main__':
    unittest.main()

    def test_reads_and_writes_properties(self):
        # Create a mock node with predefined input and output
        mock_node = Mock()
        mock_node.input = "a AND b OR c"
        mock_node.output = ["result1", "result2"]

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Test the reads property
        self.assertEqual(set(bridge.reads), {"a", "b", "c"})

        # Test the writes property
        self.assertEqual(bridge.writes, ["result1", "result2"])

if __name__ == '__main__':
    unittest.main()