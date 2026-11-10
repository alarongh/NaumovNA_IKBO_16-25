"""Построение графа рекурсивным обходом в глубину."""

from dataclasses import dataclass

from .model import Package


@dataclass
class Graph:
    """Рёбра ориентированы от пакета к его зависимостям."""

    root: Package
    edges: dict[Package, tuple[Package, ...]]
    cycles: list[tuple[Package, ...]]


def build_graph(repository, name):
    """Обойти каждый узел один раз и записать обратные рёбра DFS."""
    graph = Graph(repository.root(name), {}, [])
    stack = []
    active = set()

    def visit(package):
        """Завершить обработку пакета после обхода его зависимостей."""
        if package in active:
            start = stack.index(package)
            graph.cycles.append((*stack[start:], package))
            return
        if package in graph.edges:
            return
        active.add(package)
        stack.append(package)
        children = tuple(dict.fromkeys(repository.dependencies(package)))
        for dependency in children:
            visit(dependency)
        stack.pop()
        active.remove(package)
        graph.edges[package] = children

    visit(graph.root)
    return graph


def describe_cycle(cycle):
    """Показать цепочку, которая возвращается к исходному узлу."""
    return " -> ".join(map(str, cycle))
