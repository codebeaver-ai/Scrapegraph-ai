import unittest

from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge, parse_boolean_expression
from unittest.mock import Mock, patch

class TestBurrBridge(unittest.TestCase):
    @patch('scrapegraphai.integrations.burr_bridge.burr')
    @patch('scrapegraphai.integrations.burr_bridge.tracking')
    def test_execute_with_empty_initial_state(self, mock_tracking, mock_burr):
        # Mock the BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.nodes = [Mock(node_name='node1'), Mock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        # Mock the Burr Application
        mock_app = Mock()
        mock_app.run.return_value = (Mock(), Mock(), Mock())
        mock_burr.ApplicationBuilder.return_value.build.return_value = mock_app

        # Create BurrBridge instance
        burr_config = {'project_name': 'test_project', 'app_instance_id': 'test_instance'}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Execute with empty initial state
        result = burr_bridge.execute()

        # Assertions
        self.assertIsInstance(result, dict)
        mock_app.run.assert_called_once()
        mock_tracking.LocalTrackingClient.assert_called_once_with(project='test_project')

        # Check if the application was initialized with the correct parameters
        mock_burr.ApplicationBuilder.assert_called_once()
        builder = mock_burr.ApplicationBuilder.return_value
        builder.with_actions.assert_called_once()
        builder.with_transitions.assert_called_once()
        builder.with_entrypoint.assert_called_once_with('node1')
        builder.with_state.assert_called_once()
        builder.with_identifiers.assert_called_once()
        builder.with_hooks.assert_called_once()
        builder.with_tracker.assert_called_once()

    @patch('scrapegraphai.integrations.burr_bridge.burr')
    @patch('scrapegraphai.integrations.burr_bridge.tracking')
    def test_execute_with_non_empty_initial_state(self, mock_tracking, mock_burr):
        # Mock the BaseGraph
        mock_base_graph = Mock()
        mock_base_graph.nodes = [Mock(node_name='node1'), Mock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        # Mock the Burr Application
        mock_app = Mock()
        mock_final_state = Mock()
        mock_final_state.__dict__ = {'key1': 'value1', 'key2': 'value2'}
        mock_app.run.return_value = (Mock(), Mock(), mock_final_state)
        mock_burr.ApplicationBuilder.return_value.build.return_value = mock_app

        # Create BurrBridge instance
        burr_config = {'project_name': 'test_project', 'app_instance_id': 'test_instance'}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Execute with non-empty initial state
        initial_state = {'input_key': 'input_value'}
        result = burr_bridge.execute(initial_state)

        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2'})
        mock_app.run.assert_called_once()
        mock_tracking.LocalTrackingClient.assert_called_once_with(project='test_project')

        # Check if the application was initialized with the correct parameters
        mock_burr.ApplicationBuilder.assert_called_once()
        builder = mock_burr.ApplicationBuilder.return_value
        builder.with_actions.assert_called_once()
        builder.with_transitions.assert_called_once()
        builder.with_entrypoint.assert_called_once_with('node1')
        builder.with_state.assert_called_once()
        builder.with_identifiers.assert_called_once()
        builder.with_hooks.assert_called_once()
        builder.with_tracker.assert_called_once()

        # Check if the initial state was passed correctly
        _, kwargs = builder.with_state.call_args
        self.assertEqual(kwargs, initial_state)

    def test_parse_boolean_expression(self):
        # Test simple expression
        self.assertEqual(parse_boolean_expression("a AND b"), ["a", "b"])

        # Test complex expression
        self.assertEqual(set(parse_boolean_expression("(a AND b) OR (c AND d)")), {"a", "b", "c", "d"})

        # Test expression with repeated keys
        self.assertEqual(set(parse_boolean_expression("a AND b AND a")), {"a", "b"})

        # Test expression with non-alphabetic characters
        self.assertEqual(parse_boolean_expression("key1 AND key_2 AND key-3"), ["key1", "key_2", "key", "3"])

        # Test empty expression
        self.assertEqual(parse_boolean_expression(""), [])

        # Test expression with only operators
        self.assertEqual(parse_boolean_expression("AND OR NOT"), [])

    @patch('scrapegraphai.integrations.burr_bridge.burr')
    def test_create_actions(self, mock_burr):
        # Mock the BaseGraph
        mock_base_graph = Mock()
        mock_node1 = Mock(node_name='node1')
        mock_node2 = Mock(node_name='node2')
        mock_base_graph.nodes = [mock_node1, mock_node2]

        # Create BurrBridge instance
        burr_config = {'project_name': 'test_project', 'app_instance_id': 'test_instance'}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call _create_actions
        actions = burr_bridge._create_actions()

        # Assertions
        self.assertEqual(len(actions), 2)
        self.assertIn('node1', actions)
        self.assertIn('node2', actions)
        self.assertIsInstance(actions['node1'], BurrNodeBridge)
        self.assertIsInstance(actions['node2'], BurrNodeBridge)
        self.assertEqual(actions['node1'].node, mock_node1)
        self.assertEqual(actions['node2'].node, mock_node2)
