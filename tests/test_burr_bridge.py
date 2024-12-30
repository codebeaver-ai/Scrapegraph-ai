from burr.core import State
from burr.core import State, Action
from burr.core import default

from scrapegraphai.integrations.burr_bridge import BurrBridge
from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge
from scrapegraphai.integrations.burr_bridge import BurrNodeBridge
from scrapegraphai.integrations.burr_bridge import BurrNodeBridge, parse_boolean_expression
from scrapegraphai.integrations.burr_bridge import PrintLnHook
from scrapegraphai.integrations.burr_bridge import parse_boolean_expression

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from unittest.mock import patch
from unittest.mock import patch, MagicMock

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
        # Test with a simple expression
        simple_expr = "a AND b"
        self.assertEqual(parse_boolean_expression(simple_expr), ['a', 'b'])

        # Test with a complex expression
        complex_expr = "a AND (b OR c) AND d"
        self.assertEqual(set(parse_boolean_expression(complex_expr)), set(['a', 'b', 'c', 'd']))

        # Test with an empty expression
        empty_expr = ""
        self.assertEqual(parse_boolean_expression(empty_expr), [])

        # Test with repeated keys
        repeated_expr = "a AND a AND b OR b"
        self.assertEqual(set(parse_boolean_expression(repeated_expr)), set(['a', 'b']))

    @patch('scrapegraphai.integrations.burr_bridge.BaseGraph')
    def test_create_actions(self, mock_BaseGraph):
        # Create mock nodes
        mock_node1 = MagicMock(node_name='node1')
        mock_node2 = MagicMock(node_name='node2')
        mock_node3 = MagicMock(node_name='node3')

        # Set up the mock base graph
        mock_graph = mock_BaseGraph.return_value
        mock_graph.nodes = [mock_node1, mock_node2, mock_node3]

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
        }
        burr_bridge = BurrBridge(mock_graph, burr_config)

        # Call the _create_actions method
        actions = burr_bridge._create_actions()

        # Verify the results
        self.assertEqual(len(actions), 3)
        self.assertIsInstance(actions['node1'], BurrNodeBridge)
        self.assertIsInstance(actions['node2'], BurrNodeBridge)
        self.assertIsInstance(actions['node3'], BurrNodeBridge)
        self.assertEqual(set(actions.keys()), {'node1', 'node2', 'node3'})

        # Verify that each BurrNodeBridge was created with the correct node
        self.assertEqual(actions['node1'].node, mock_node1)
        self.assertEqual(actions['node2'].node, mock_node2)
        self.assertEqual(actions['node3'].node, mock_node3)

    @patch('scrapegraphai.integrations.burr_bridge.BaseGraph')
    def test_create_transitions(self, mock_BaseGraph):
        # Set up the mock base graph
        mock_graph = mock_BaseGraph.return_value
        mock_graph.edges = {
            'node1': 'node2',
            'node2': 'node3',
            'node3': 'node4'
        }

        # Create a BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
        }
        burr_bridge = BurrBridge(mock_graph, burr_config)

        # Call the _create_transitions method
        transitions = burr_bridge._create_transitions()

        # Verify the results
        expected_transitions = [
            ('node1', 'node2', default),
            ('node2', 'node3', default),
            ('node3', 'node4', default)
        ]
        self.assertEqual(len(transitions), 3)
        self.assertEqual(set(transitions), set(expected_transitions))

        # Verify that each transition is a tuple with the correct structure
        for transition in transitions:
            self.assertIsInstance(transition, tuple)
            self.assertEqual(len(transition), 3)
            self.assertIsInstance(transition[0], str)
            self.assertIsInstance(transition[1], str)
            self.assertEqual(transition[2], default)

    # ... existing tests ...

    def test_burr_node_bridge_reads(self):
        # Create a mock node with a complex input expression
        mock_node = MagicMock()
        mock_node.input = "a AND (b OR c) AND d"

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Test the reads property
        expected_reads = ['a', 'b', 'c', 'd']
        self.assertEqual(set(bridge.reads), set(expected_reads))

        # Verify that parse_boolean_expression is called with the correct argument
        self.assertEqual(bridge.reads, parse_boolean_expression(mock_node.input))

        # Test with a different input expression
        mock_node.input = "x OR y AND z"
        expected_reads = ['x', 'y', 'z']
        self.assertEqual(set(bridge.reads), set(expected_reads))

class TestBurrNodeBridge(TestCase):
    def test_burr_node_bridge_run(self):
        # Create a mock node with a mock execute method
        mock_node = MagicMock()
        mock_node.execute.return_value = {'output': 'result'}

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Mock the reads property
        with patch.object(BurrNodeBridge, 'reads', new_callable=MagicMock(return_value=['input1', 'input2'])):
            # Create a mock State
            mock_state = MagicMock(spec=State)
            mock_state.__getitem__.side_effect = lambda key: f'value_{key}'

            # Call the run method
            result = bridge.run(mock_state, extra_kwarg='extra')

            # Assert that the node's execute method was called with the correct arguments
            mock_node.execute.assert_called_once_with(
                {'input1': 'value_input1', 'input2': 'value_input2'},
                extra_kwarg='extra'
            )

            # Assert that the result is correct
            self.assertEqual(result, {'output': 'result'})

    def test_burr_node_bridge_update(self):
        # Create a mock node with mock output
        mock_node = MagicMock()
        mock_node.output = ['output1', 'output2']

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Create a mock State
        mock_state = MagicMock(spec=State)
        mock_state.update.return_value = mock_state  # State.update should return the updated state

        # Create a mock result
        mock_result = {'output1': 'value1', 'output2': 'value2'}

        # Call the update method
        updated_state = bridge.update(mock_result, mock_state)

        # Assert that the state's update method was called with the correct arguments
        mock_state.update.assert_called_once_with(**mock_result)

        # Assert that the method returns the updated state
        self.assertEqual(updated_state, mock_state)

    # ... existing tests ...

    @patch('inspect.getsource')
    def test_burr_node_bridge_get_source(self, mock_getsource):
        # Create a mock node
        class MockNode:
            def execute(self):
                pass

        mock_node = MockNode()

        # Set up the mock for inspect.getsource
        expected_source = "class MockNode:\n    def execute(self):\n        pass\n"
        mock_getsource.return_value = expected_source

        # Create a BurrNodeBridge instance
        bridge = BurrNodeBridge(mock_node)

        # Call the get_source method
        result = bridge.get_source()

        # Assert that inspect.getsource was called with the correct argument
        mock_getsource.assert_called_once_with(MockNode)

        # Assert that the result is correct
        self.assertEqual(result, expected_source)

    @patch('scrapegraphai.integrations.burr_bridge.ApplicationBuilder')
    @patch('scrapegraphai.integrations.burr_bridge.State')
    @patch('scrapegraphai.integrations.burr_bridge.ApplicationContext')
    @patch('scrapegraphai.integrations.burr_bridge.tracking.LocalTrackingClient')
    def test_initialize_burr_app_no_context(self, mock_LocalTrackingClient, mock_ApplicationContext, mock_State, mock_ApplicationBuilder):
        # Set up mocks
        mock_base_graph = MagicMock()
        mock_base_graph.nodes = [MagicMock(node_name='node1'), MagicMock(node_name='node2')]
        mock_base_graph.edges = {'node1': 'node2'}
        mock_base_graph.entry_point = 'node1'

        mock_ApplicationContext.get.return_value = None  # Simulate no existing context

        # Create BurrBridge instance
        burr_config = {
            "project_name": "test_project",
            "app_instance_id": "test_instance",
        }
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call _initialize_burr_app
        initial_state = {'initial_key': 'initial_value'}
        burr_app = burr_bridge._initialize_burr_app(initial_state)

        # Assertions
        mock_State.assert_called_once_with(initial_state)
        mock_ApplicationBuilder.return_value.with_actions.assert_called_once()
        mock_ApplicationBuilder.return_value.with_transitions.assert_called_once()
        mock_ApplicationBuilder.return_value.with_entrypoint.assert_called_once_with('node1')
        mock_ApplicationBuilder.return_value.with_state.assert_called_once()
        mock_ApplicationBuilder.return_value.with_identifiers.assert_called_once()
        mock_ApplicationBuilder.return_value.with_hooks.assert_called_once()
        mock_ApplicationBuilder.return_value.with_tracker.assert_called_once()
        mock_LocalTrackingClient.assert_called_once_with(project='test_project')

        # Assert that the method returns the built application
        self.assertEqual(burr_app, mock_ApplicationBuilder.return_value.build.return_value)

    # ... existing tests ...

    @patch('builtins.print')
    def test_print_ln_hook(self, mock_print):
        # Create mock State and Action objects
        mock_state = State()
        mock_action = Action()
        mock_action.name = "TestAction"

        # Create an instance of PrintLnHook
        hook = PrintLnHook()

        # Test pre_run_step
        hook.pre_run_step(state=mock_state, action=mock_action)
        mock_print.assert_called_with("Starting action: TestAction")

        # Reset mock_print
        mock_print.reset_mock()

        # Test post_run_step
        hook.post_run_step(state=mock_state, action=mock_action)
        mock_print.assert_called_with("Finishing action: TestAction")