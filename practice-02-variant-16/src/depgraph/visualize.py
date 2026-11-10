"""Представление графа в DOT, SVG и ASCII."""

import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from .model import DependencyError


RENDER_TIMEOUT = 45


def render_dot(graph):
    """Описать узлы, рёбра и обратные рёбра DFS на языке DOT."""
    lines = [
        "digraph dependencies {",
        "  rankdir=LR;",
        '  node [shape=box, style=filled, fillcolor="#f1f5f9"];',
    ]
    backwards = {(cycle[-2], cycle[-1]) for cycle in graph.cycles}
    for package in sorted(graph.edges):
        name = json.dumps(str(package))
        style = ' [fillcolor="#dbeafe"]' if package == graph.root else ""
        lines.append(f"  {name}{style};")
        for dependency in graph.edges[package]:
            target = json.dumps(str(dependency))
            mark = ' [color="#b91c1c", style=dashed]' if (
                package, dependency
            ) in backwards else ""
            lines.append(f"  {name} -> {target}{mark};")
    return "\n".join([*lines, "}", ""])


def ascii_tree(graph):
    """Вывести ветви, помечая повторные узлы и возврат в стек."""
    lines = [str(graph.root)]
    visited = {graph.root}
    active = {graph.root}

    def visit(package, prefix):
        """Добавить дочерние строки и развернуть новые узлы."""
        children = graph.edges[package]
        for index, dependency in enumerate(children, start=1):
            last = index == len(children)
            connector = "\\-- " if last else "|-- "
            line = f"{prefix}{connector}{dependency}"
            if dependency in active:
                lines.append(line + " [cycle]")
            elif dependency in visited:
                lines.append(line + " [shared]")
            else:
                lines.append(line)
                visited.add(dependency)
                active.add(dependency)
                visit(dependency, prefix + ("    " if last else "|   "))
                active.remove(dependency)

    visit(graph.root, "")
    return "\n".join(lines)


def dot_command():
    """Найти Graphviz в PATH или в стандартной среде WSL."""
    native = shutil.which("dot")
    if native:
        return [native, "-Tsvg"]
    if os.name == "nt" and shutil.which("wsl.exe"):
        return ["wsl.exe", "--exec", "dot", "-Tsvg"]
    raise DependencyError("не найдена команда dot из Graphviz")


def render_svg(dot):
    """Передать описание в Graphviz через stdin и получить байты SVG."""
    try:
        process = subprocess.run(
            dot_command(), input=dot.encode("utf-8"), capture_output=True,
            timeout=RENDER_TIMEOUT, check=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", errors="replace").strip()
        if "\x00" in detail:
            detail = error.stderr.decode("utf-16-le", errors="replace").strip()
        raise DependencyError(f"Graphviz не создал SVG: {detail}") from error
    except (OSError, subprocess.TimeoutExpired) as error:
        message = f"не удалось запустить Graphviz: {error}"
        raise DependencyError(message) from error
    return process.stdout


def save_visualization(graph, output):
    """Отрисовать SVG, затем заменить выходные файлы."""
    dot = render_dot(graph)
    svg = render_svg(dot)
    try:
        with TemporaryDirectory(dir=output.parent) as directory:
            draft_dot = Path(directory) / "graph.dot"
            draft_svg = Path(directory) / "graph.svg"
            draft_dot.write_bytes(dot.encode("utf-8"))
            draft_svg.write_bytes(svg)
            draft_dot.replace(output.with_suffix(".dot"))
            draft_svg.replace(output)
    except OSError as error:
        message = f"не удалось сохранить результат: {error}"
        raise DependencyError(message) from error
