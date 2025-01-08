import unittest

from scrapegraphai.integrations.burr_bridge import BurrBridge
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