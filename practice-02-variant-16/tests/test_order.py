"""Проверка порядка завершения DFS, использованного на этапе 4."""

from pathlib import Path
import unittest

from src.depgraph.fixtures import FixtureRepository
from src.depgraph.graph import build_graph


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class OrderTests(unittest.TestCase):
    def test_dependencies_finish_before_their_parent(self):
        repository = FixtureRepository(EXAMPLES / "diamond.json")
        graph = build_graph(repository, "A")
        self.assertEqual(list(map(str, graph.edges)), ["D", "B", "C", "A"])
