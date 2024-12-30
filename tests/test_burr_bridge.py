import inspect
import uuid

from burr import tracking
from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge, PrintLnHook, parse_boolean_expression
from unittest import TestCase
from unittest.mock import MagicMock, patch

try:
    from scrapegraphai.base import BaseGraph
except ImportError:
    BaseGraph = MagicMock()  # Mock BaseGraph if it doesn't exist

class TestBurrBridge(TestCase):
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.State')
    def test_execute_with_initial_state(self, mock_State, mock_ApplicationBuilder):
        # Create a mock BaseGraph
        mock_base_graph = MagicMock(spec=BaseGraph)
        mock_base_graph.nodes = [MagicMock(node_name='node1'), MagicMock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {"input1": "value1"}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock the Burr application
        mock_app = MagicMock()
        mock_ApplicationBuilder.return_value.build.return_value = mock_app

        # Mock the final state
        mock_final_state = MagicMock()
        mock_final_state.__dict__ = {'output1': 'result1', 'output2': 'result2'}
        mock_app.run.return_value = (None, None, mock_final_state)

        # Execute the BurrBridge with an initial state
        initial_state = {'initial_key': 'initial_value'}
        result = burr_bridge.execute(initial_state)

        # Assert that State was called with the initial state
        mock_State.assert_called_once_with(initial_state)

        # Assert that the application was run with the correct parameters
        mock_app.run.assert_called_once()
        call_args = mock_app.run.call_args[1]
        self.assertIn('halt_after', call_args)
        self.assertEqual(call_args['inputs'], {"input1": "value1"})

        # Assert that the result is correct
        expected_result = {'output1': 'result1', 'output2': 'result2'}
        self.assertEqual(result, expected_result)

    # ... existing tests ...

    def test_parse_boolean_expression(self):
        # Test a simple expression
        self.assertEqual(parse_boolean_expression("a AND b"), ["a", "b"])

        # Test an expression with duplicates
        self.assertEqual(parse_boolean_expression("a AND b OR a"), ["a", "b"])

        # Test a more complex expression
        self.assertEqual(set(parse_boolean_expression("(x AND y) OR (z AND w)")), set(["x", "y", "z", "w"]))

        # Test with different boolean operators
        self.assertEqual(set(parse_boolean_expression("a AND b OR c XOR d NOT e")), set(["a", "b", "c", "d", "e"]))

        # Test with an empty expression
        self.assertEqual(parse_boolean_expression(""), [])

    # ... existing tests ...

    @patch('inspect.getsource')
    def test_burr_node_bridge(self, mock_getsource):
        # Create a mock node
        mock_node = MagicMock()
        mock_node.input = "a AND b OR c"
        mock_node.output = ["result1", "result2"]
        mock_node.__class__ = MagicMock()

        # Set up the mock for inspect.getsource
        mock_source = "def mock_function():\n    pass"
        mock_getsource.return_value = mock_source

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Test the reads property
        self.assertEqual(set(bridge.reads), set(["a", "b", "c"]))

        # Test the writes property
        self.assertEqual(bridge.writes, ["result1", "result2"])

        # Test the get_source method
        self.assertEqual(bridge.get_source(), mock_source)

        # Verify that inspect.getsource was called with the correct argument
        mock_getsource.assert_called_once_with(mock_node.__class__)

    # ... existing tests ...

    @patch('scrapegraphai.integrations.burr_bridge.State')
    def test_burr_node_bridge_run_and_update(self, mock_State):
        # Create a mock node
        mock_node = MagicMock()
        mock_node.input = "a AND b"
        mock_node.output = ["result"]
        mock_node.execute.return_value = {"result": "test_result"}

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Create a mock State
        mock_state = MagicMock()
        mock_state.__getitem__.side_effect = lambda key: {"a": "value_a", "b": "value_b"}[key]

        # Test the run method
        result = bridge.run(mock_state)
        self.assertEqual(result, {"result": "test_result"})
        mock_node.execute.assert_called_once_with({"a": "value_a", "b": "value_b"})

        # Test the update method
        updated_state = bridge.update(result, mock_state)
        mock_state.update.assert_called_once_with(**{"result": "test_result"})
        self.assertEqual(updated_state, mock_state.update.return_value)

    # ... existing tests ...

    def test_create_actions_and_transitions(self):
        # Create mock nodes
        mock_node1 = MagicMock(node_name='node1')
        mock_node2 = MagicMock(node_name='node2')
        mock_node3 = MagicMock(node_name='node3')

        # Create a mock BaseGraph
        mock_base_graph = MagicMock(spec=BaseGraph)
        mock_base_graph.nodes = [mock_node1, mock_node2, mock_node3]
        mock_base_graph.edges = {'node1': 'node2', 'node2': 'node3'}

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Test _create_actions
        actions = burr_bridge._create_actions()
        self.assertEqual(len(actions), 3)
        self.assertIn('node1', actions)
        self.assertIn('node2', actions)
        self.assertIn('node3', actions)
        self.assertIsInstance(actions['node1'], BurrNodeBridge)
        self.assertIsInstance(actions['node2'], BurrNodeBridge)
        self.assertIsInstance(actions['node3'], BurrNodeBridge)

        # Test _create_transitions
        transitions = burr_bridge._create_transitions()
        self.assertEqual(len(transitions), 2)
        self.assertIn(('node1', 'node2', BurrBridge._create_transitions.__globals__['default']), transitions)
        self.assertIn(('node2', 'node3', BurrBridge._create_transitions.__globals__['default']), transitions)

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.State')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('uuid.uuid4')
    def test_initialize_burr_app(self, mock_uuid4, mock_ApplicationContext, mock_State, mock_ApplicationBuilder):
        # Mock UUID
        mock_uuid4.return_value = "mocked-uuid"

        # Create a mock BaseGraph
        mock_base_graph = MagicMock(spec=BaseGraph)
        mock_base_graph.nodes = [MagicMock(node_name='node1'), MagicMock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {"input1": "value1"}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Mock ApplicationContext
        mock_context = MagicMock()
        mock_context.tracker = MagicMock()
        mock_ApplicationContext.get.return_value = mock_context

        # Call _initialize_burr_app
        initial_state = {'initial_key': 'initial_value'}
        burr_bridge._initialize_burr_app(initial_state)

        # Assert ApplicationBuilder was called with correct parameters
        mock_ApplicationBuilder.return_value.with_actions.assert_called()
        mock_ApplicationBuilder.return_value.with_transitions.assert_called()
        mock_ApplicationBuilder.return_value.with_entrypoint.assert_called_with('node1')
        mock_State.assert_called_with(initial_state)
        mock_ApplicationBuilder.return_value.with_state.assert_called()
        mock_ApplicationBuilder.return_value.with_identifiers.assert_called_with(app_id="mocked-uuid")

        # Assert tracker is set correctly
        mock_ApplicationBuilder.return_value.with_tracker.assert_called_with(mock_context.tracker.copy.return_value)
        mock_ApplicationBuilder.return_value.with_spawning_parent.assert_called()

        # Assert build is called
        mock_ApplicationBuilder.return_value.build.assert_called()

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.State')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('uuid.uuid4')
    @patch('burr.tracking.LocalTrackingClient')
    def test_initialize_burr_app_with_no_context(self, mock_LocalTrackingClient, mock_uuid4, mock_ApplicationContext, mock_State, mock_ApplicationBuilder):
        # Mock UUID
        mock_uuid4.return_value = "mocked-uuid"

        # Mock ApplicationContext to return None
        mock_ApplicationContext.get.return_value = None

        # Create a mock BaseGraph
        mock_base_graph = MagicMock()
        mock_base_graph.nodes = [MagicMock(node_name='node1'), MagicMock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
            "inputs": {"input1": "value1"}
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call _initialize_burr_app
        initial_state = {'initial_key': 'initial_value'}
        burr_bridge._initialize_burr_app(initial_state)

        # Assert LocalTrackingClient was created with correct project name
        mock_LocalTrackingClient.assert_called_once_with(project="test_project")

        # Assert ApplicationBuilder was called with correct parameters
        mock_ApplicationBuilder.return_value.with_actions.assert_called()
        mock_ApplicationBuilder.return_value.with_transitions.assert_called()
        mock_ApplicationBuilder.return_value.with_entrypoint.assert_called_with('node1')
        mock_State.assert_called_with(initial_state)
        mock_ApplicationBuilder.return_value.with_state.assert_called()
        mock_ApplicationBuilder.return_value.with_identifiers.assert_called_with(app_id="mocked-uuid")

        # Assert tracker is set correctly
        mock_ApplicationBuilder.return_value.with_tracker.assert_called_with(mock_LocalTrackingClient.return_value)

        # Assert build is called
        mock_ApplicationBuilder.return_value.build.assert_called()

    # ... existing tests ...

    @patch('builtins.print')
    def test_print_ln_hook(self, mock_print):
        # Create a PrintLnHook instance
        hook = PrintLnHook()

        # Create mock State and Action objects
        mock_state = MagicMock()
        mock_action = MagicMock()
        mock_action.name = "TestAction"

        # Test pre_run_step
        hook.pre_run_step(state=mock_state, action=mock_action)
        mock_print.assert_called_with("Starting action: TestAction")

        # Reset mock_print
        mock_print.reset_mock()

        # Test post_run_step
        hook.post_run_step(state=mock_state, action=mock_action)
        mock_print.assert_called_with("Finishing action: TestAction")

    # ... existing tests ...

    def test_convert_state_from_burr(self):
        # Create a mock BaseGraph (not used in this test, but required for BurrBridge initialization)
        mock_base_graph = MagicMock()

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Create a mock Burr State object
        mock_burr_state = MagicMock()
        mock_burr_state.__dict__ = {
            'key1': 'value1',
            'key2': 42,
            'key3': ['item1', 'item2'],
        }

        # Call the _convert_state_from_burr method
        result = burr_bridge._convert_state_from_burr(mock_burr_state)

        # Verify that the resulting dictionary contains the expected key-value pairs
        expected_result = {
            'key1': 'value1',
            'key2': 42,
            'key3': ['item1', 'item2'],
        }
        self.assertEqual(result, expected_result)

    def test_burr_bridge_init_default_values(self):
        # Create a mock BaseGraph
        mock_base_graph = MagicMock()

        # Create a BurrBridge instance with minimal configuration
        minimal_config = {}
        burr_bridge = BurrBridge(mock_base_graph, minimal_config)

        # Assert that default values are set correctly
        self.assertEqual(burr_bridge.project_name, "scrapegraph_project")
        self.assertEqual(burr_bridge.app_instance_id, "default-instance")
        self.assertEqual(burr_bridge.burr_inputs, {})

        # Create another BurrBridge instance with partial configuration
        partial_config = {"project_name": "custom_project"}
        burr_bridge = BurrBridge(mock_base_graph, partial_config)

        # Assert that the custom value is set and other defaults are maintained
        self.assertEqual(burr_bridge.project_name, "custom_project")
        self.assertEqual(burr_bridge.app_instance_id, "default-instance")
        self.assertEqual(burr_bridge.burr_inputs, {})