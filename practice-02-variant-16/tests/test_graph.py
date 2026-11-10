"""Рекурсивный обход, общие зависимости и циклы."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.depgraph.fixtures import FixtureRepository
from src.depgraph.graph import build_graph, describe_cycle
from src.depgraph.model import DependencyError, Package


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class GraphTests(unittest.TestCase):
    def test_diamond_keeps_both_edges_and_visits_shared_node_once(self):
        repository = FixtureRepository(EXAMPLES / "diamond.json")
        with patch.object(repository, "dependencies",
                          wraps=repository.dependencies) as dependencies:
            graph = build_graph(repository, "A")
        leaf = Package("D")
        self.assertEqual(graph.edges[Package("B")], (leaf,))
        self.assertEqual(graph.edges[Package("C")], (leaf,))
        self.assertEqual(graph.edges[leaf], ())
        self.assertEqual(dependencies.call_count, len(graph.edges))
        self.assertEqual(graph.cycles, [])

    def test_cycle_preserves_edges_and_explores_other_branch(self):
        graph = build_graph(FixtureRepository(EXAMPLES / "cycle.json"), "A")
        self.assertEqual([describe_cycle(c) for c in graph.cycles],
                         ["B -> C -> B"])
        self.assertIn(Package("B"), graph.edges[Package("C")])
        self.assertIn(Package("D"), graph.edges)

    def test_isolated_and_unknown_root(self):
        repository = FixtureRepository(EXAMPLES / "isolated.json")
        self.assertEqual(build_graph(repository, "X").edges, {Package("X"): ()})
        with self.assertRaisesRegex(DependencyError, "не найден"):
            build_graph(repository, "A")

    def test_invalid_fixtures_and_self_loop(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "repo.json"
            for text in ('{"A":["Z"]}', '{"a":[]}', '{"A":"B"}',
                         '{"A":[],"A":[]}', '{"A":[2]}'):
                with self.subTest(text=text):
                    source.write_text(text, encoding="utf-8")
                    with self.assertRaises(DependencyError):
                        FixtureRepository(source)
            source.write_text('{"A":["A","A"]}', encoding="utf-8")
            graph = build_graph(FixtureRepository(source), "A")
            self.assertEqual(len(graph.cycles), 1)
            self.assertEqual(graph.edges[graph.root], (graph.root,))
