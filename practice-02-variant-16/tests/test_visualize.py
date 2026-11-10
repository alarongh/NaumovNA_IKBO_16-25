"""Проверки DOT, ASCII и сохранения результата."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.depgraph.fixtures import FixtureRepository
from src.depgraph.graph import build_graph
from src.depgraph.model import DependencyError
from src.depgraph.visualize import ascii_tree, render_dot, save_visualization


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def graph_from(filename, root="A"):
    """Построить граф по одному из примеров."""
    return build_graph(FixtureRepository(EXAMPLES / filename), root)


class VisualizationTests(unittest.TestCase):
    def test_diamond_preserves_both_paths(self):
        graph = graph_from("diamond.json")
        dot = render_dot(graph)
        self.assertIn('"B" -> "D";', dot)
        self.assertIn('"C" -> "D";', dot)
        expected = (
            "A\n|-- B\n|   \\-- D\n\\-- C\n    \\-- D [shared]"
        )
        self.assertEqual(ascii_tree(graph), expected)
        self.assertTrue(ascii_tree(graph).isascii())

    def test_cycle_and_isolated(self):
        cycle = graph_from("cycle.json")
        self.assertIn('"C" -> "B" [color=', render_dot(cycle))
        self.assertIn("B [cycle]", ascii_tree(cycle))
        isolated = graph_from("isolated.json", "X")
        self.assertIn('"X"', render_dot(isolated))
        self.assertEqual(ascii_tree(isolated), "X")

    def test_saves_both_formats(self):
        graph = graph_from("diamond.json")
        with TemporaryDirectory() as directory:
            output = Path(directory) / "result.svg"
            renderer = "src.depgraph.visualize.render_svg"
            with patch(renderer, return_value=b"<svg/>"):
                save_visualization(graph, output)
            self.assertEqual(output.read_bytes(), b"<svg/>")
            self.assertEqual(
                output.with_suffix(".dot").read_text(encoding="utf-8"),
                render_dot(graph),
            )

    def test_renderer_error_keeps_existing_files(self):
        graph = graph_from("diamond.json")
        with TemporaryDirectory() as directory:
            output = Path(directory) / "result.svg"
            dot = output.with_suffix(".dot")
            output.write_bytes(b"old svg")
            dot.write_bytes(b"old dot")
            error = DependencyError("dot failed")
            with patch("src.depgraph.visualize.render_svg", side_effect=error):
                with self.assertRaises(DependencyError):
                    save_visualization(graph, output)
            self.assertEqual(output.read_bytes(), b"old svg")
            self.assertEqual(dot.read_bytes(), b"old dot")

    def test_svg_write_failure_rolls_back_dot(self):
        graph = graph_from("diamond.json")
        replace = Path.replace
        renderer = "src.depgraph.visualize.render_svg"
        for had_dot in (False, True):
            with self.subTest(had_dot=had_dot), TemporaryDirectory() as folder:
                output = Path(folder) / "result.svg"
                dot = output.with_suffix(".dot")
                output.write_bytes(b"old svg")
                if had_dot:
                    dot.write_bytes(b"old dot")

                def fail_on_svg(path, target):
                    if target == output:
                        raise PermissionError("SVG is read-only")
                    return replace(path, target)

                with patch(renderer, return_value=b"<svg/>"), patch.object(
                    Path, "replace", autospec=True, side_effect=fail_on_svg,
                ):
                    with self.assertRaises(DependencyError):
                        save_visualization(graph, output)
                self.assertEqual(output.read_bytes(), b"old svg")
                self.assertEqual(dot.exists(), had_dot)
                if had_dot:
                    self.assertEqual(dot.read_bytes(), b"old dot")
