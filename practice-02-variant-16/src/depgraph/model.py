"""Узел и объявленная зависимость пакета."""

from dataclasses import dataclass


class DependencyError(ValueError):
    """Ошибка источника данных или графа."""


@dataclass(frozen=True, order=True)
class Package:
    """Пакет с конкретной версией, если она есть в источнике."""

    name: str
    version: str = ""

    def __str__(self):
        return f"{self.name} {self.version}" if self.version else self.name


@dataclass(frozen=True)
class Dependency:
    """Идентификатор пакета и ограничение из манифеста."""

    name: str
    requirement: str = ""
