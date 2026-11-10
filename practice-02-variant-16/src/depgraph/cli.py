"""Интерфейс командной строки."""

import sys

from .config import parse_args
from .fixtures import FixtureRepository
from .graph import build_graph, describe_cycle
from .model import DependencyError
from .nuget import NugetRepository
from .visualize import ascii_tree, save_visualization


def main(argv=None):
    """Собрать зависимости, сохранить DOT и SVG, вывести дерево по флагу."""
    args = parse_args(argv)
    try:
        source = FixtureRepository if args.test else NugetRepository
        graph = build_graph(source(args.repository), args.package)
        tree = ascii_tree(graph) if args.ascii else None
        save_visualization(graph, args.output)
    except DependencyError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except RecursionError:
        print("Ошибка: граф слишком глубокий для рекурсивного DFS",
              file=sys.stderr)
        return 1
    if tree is not None:
        print(tree)
    for cycle in graph.cycles:
        print(f"Цикл: {describe_cycle(cycle)}", file=sys.stderr)
    print(f"DOT: {args.output.with_suffix('.dot')}")
    print(f"SVG: {args.output}")
    return 0
