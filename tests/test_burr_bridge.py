from unittest import TestCase
from unittest.mock import Mock, patch
from scrapegraphai.integrations.burr_bridge import BurrBridge

from scrapegraphai.integrations.burr_bridge import BurrBridge, BurrNodeBridge

# Mock classes for testing
class MockNode:
    def __init__(self, node_name):
        self.node_name = node_name

class MockBaseGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

class TestBurrBridge(TestCase):
    def test_create_transitions(self):
        # Mock the BaseGraph
        mock_base_graph = Mock()

        # Set up the edges in the mock base graph
        mock_base_graph.edges = {
            'node1': 'node2',
            'node2': 'node3',
            'node3': 'node4'
        }

        # Create a BurrBridge instance with the mock base graph
        burr_config = {'project_name': 'test_project'}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_transitions method
        transitions = burr_bridge._create_transitions()

        # Assert that the transitions list has the correct length
        self.assertEqual(len(transitions), 3)

        # Assert that each transition is a tuple with the correct structure
        for transition in transitions:
            self.assertIsInstance(transition, tuple)
            self.assertEqual(len(transition), 3)
            self.assertIn(transition[0], mock_base_graph.edges)
            self.assertEqual(transition[1], mock_base_graph.edges[transition[0]])
            self.assertEqual(transition[2].__name__, 'default')

        # Assert that the transitions match the edges in the base graph
        expected_transitions = [
            ('node1', 'node2', burr_bridge._create_transitions()[0][2]),
            ('node2', 'node3', burr_bridge._create_transitions()[1][2]),
            ('node3', 'node4', burr_bridge._create_transitions()[2][2])
        ]
        self.assertEqual(transitions, expected_transitions)

    def test_create_actions(self):
        # Create a mock base graph with some nodes
        mock_base_graph = MockBaseGraph()
        mock_base_graph.add_node(MockNode("node1"))
        mock_base_graph.add_node(MockNode("node2"))
        mock_base_graph.add_node(MockNode("node3"))

        # Create a BurrBridge instance with the mock base graph
        burr_config = {'project_name': 'test_project'}
        burr_bridge = BurrBridge(mock_base_graph, burr_config)

        # Call the _create_actions method
        actions = burr_bridge._create_actions()

        # Assert that the actions dictionary has the correct length
        self.assertEqual(len(actions), 3)

        # Assert that each action is a BurrNodeBridge instance with the correct node name
        for node_name, action in actions.items():
            self.assertIsInstance(action, BurrNodeBridge)
            self.assertEqual(action.node.node_name, node_name)

        # Assert that all node names are present in the actions dictionary
        self.assertSetEqual(set(actions.keys()), {"node1", "node2", "node3"})