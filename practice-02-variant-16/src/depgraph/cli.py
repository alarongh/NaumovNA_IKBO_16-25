"""Интерфейс командной строки."""

import sys

from .config import parse_args
from .fixtures import FixtureRepository
from .graph import build_graph, describe_cycle
from .model import DependencyError
from .nuget import NugetRepository


def print_graph(graph):
    """Показать связи и листья в текстовом виде."""
    print(f"Пакет: {graph.root}")
    for package in sorted(graph.edges):
        children = ", ".join(map(str, graph.edges[package])) or "—"
        print(f"{package} -> {children}")


def show_cycles(graph):
    """Вывести найденные циклы отдельно от графа."""
    for cycle in graph.cycles:
        print(f"Цикл: {describe_cycle(cycle)}", file=sys.stderr)


def print_order(graph):
    """Вывести порядок завершения DFS для ациклического графа."""
    if graph.cycles:
        cycle = describe_cycle(graph.cycles[0])
        raise DependencyError(f"порядок невозможен из-за цикла {cycle}")
    print(" -> ".join(map(str, graph.edges)))


def main(argv=None):
    """Построить граф зависимостей из NuGet V3 или JSON."""
    args = parse_args(argv)
    try:
        source = FixtureRepository if args.test else NugetRepository
        graph = build_graph(source(args.repository), args.package)
        if args.order:
            print_order(graph)
            return 0
    except DependencyError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except RecursionError:
        print("Ошибка: граф слишком глубокий для рекурсивного DFS",
              file=sys.stderr)
        return 1
    print_graph(graph)
    show_cycles(graph)
    return 0
