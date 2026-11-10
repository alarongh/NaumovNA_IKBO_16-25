"""Чтение тестового репозитория из JSON."""

import json
from pathlib import Path

from .config import TEST_ID
from .model import DependencyError, Package


def unique_members(pairs):
    """Отклонить повторное объявление ключа в JSON."""
    result = {}
    for name, value in pairs:
        if name in result:
            raise DependencyError(f"пакет {name} описан повторно")
        result[name] = value
    return result


def read_fixture(path):
    """Прочитать JSON и проверить, что все ссылки ведут к пакетам."""
    try:
        graph = json.loads(Path(path).read_text(encoding="utf-8-sig"),
                           object_pairs_hook=unique_members)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DependencyError(f"{path}: {error}") from error
    if not isinstance(graph, dict):
        raise DependencyError("ожидался объект JSON с пакетами")
    for name, children in graph.items():
        if not TEST_ID.fullmatch(name):
            raise DependencyError(f"{name!r}: нужна буква от A до Z")
        if not isinstance(children, list):
            raise DependencyError(f"{name}: ожидался список зависимостей")
        for child in children:
            if not isinstance(child, str) or child not in graph:
                raise DependencyError(f"{name}: пакет {child!r} не описан")
    return graph


class FixtureRepository:
    """Предоставить тестовые пакеты и их зависимости из файла."""

    def __init__(self, path):
        self.graph = read_fixture(path)

    def root(self, name):
        """Найти начальный пакет по имени."""
        if name not in self.graph:
            raise DependencyError(f"{name}: пакет не найден")
        return Package(name)

    def dependencies(self, package):
        """Вернуть пакеты, на которые ссылается узел."""
        return tuple(Package(name) for name in self.graph[package.name])
