import unittest
import networkx as nx
from shortest_path_project import run_dijkstra


def build_sample_graph() -> nx.MultiDiGraph:
    """
    Create a small directed MultiDiGraph for deterministic Dijkstra testing:
      1 --(length=10, travel_time=5)--> 2 --(length=15, travel_time=20)--> 4
      1 --(length=5,  travel_time=30)--> 3 --(length=10, travel_time=5)-->  4
      Node 5 is disconnected (no path from 1..4).
    """
    G = nx.MultiDiGraph()
    G.add_nodes_from([1, 2, 3, 4, 5])

    G.add_edge(1, 2, key=0, length=10.0, travel_time=5.0)
    G.add_edge(2, 4, key=0, length=15.0, travel_time=20.0)
    G.add_edge(1, 3, key=0, length=5.0, travel_time=30.0)
    G.add_edge(3, 4, key=0, length=10.0, travel_time=5.0)

    # Parallel edge between 1 and 2: one shorter, one longer
    G.add_edge(1, 2, key=1, length=50.0, travel_time=2.0)

    return G


class TestRunDijkstra(unittest.TestCase):
    def setUp(self):
        self.G = build_sample_graph()

    def test_shortest_path_by_length(self):
        # 1 -> 3 -> 4 has length 5 + 10 = 15 (vs 1 -> 2 -> 4 = 25)
        res = run_dijkstra(self.G, source=1, target=4, weight_attr="length")
        self.assertTrue(res["reachable"])
        self.assertEqual(res["path"], [1, 3, 4])
        self.assertAlmostEqual(res["total_cost"], 15.0)
        self.assertGreaterEqual(res["visited_nodes"], 3)
        self.assertGreaterEqual(res["elapsed_ms"], 0.0)

    def test_shortest_path_by_travel_time_and_parallel_edges(self):
        # Parallel edge (1, 2, key=1) has travel_time=2.0; 1 -> 2 -> 4 costs 2 + 20 = 22
        # whereas 1 -> 3 -> 4 costs 30 + 5 = 35
        res = run_dijkstra(self.G, source=1, target=4, weight_attr="travel_time")
        self.assertTrue(res["reachable"])
        self.assertEqual(res["path"], [1, 2, 4])
        self.assertAlmostEqual(res["total_cost"], 22.0)

    def test_source_equals_target(self):
        res = run_dijkstra(self.G, source=2, target=2, weight_attr="length")
        self.assertTrue(res["reachable"])
        self.assertEqual(res["path"], [2])
        self.assertAlmostEqual(res["total_cost"], 0.0)
        self.assertEqual(res["visited_nodes"], 1)

    def test_unreachable_target(self):
        res = run_dijkstra(self.G, source=1, target=5, weight_attr="length")
        self.assertFalse(res["reachable"])
        self.assertEqual(res["path"], [])
        self.assertEqual(res["total_cost"], float("inf"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
