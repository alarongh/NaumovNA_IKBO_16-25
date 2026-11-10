"""Чтение зависимостей из манифеста .nuspec."""

import re
from xml.etree import ElementTree

from .config import PACKAGE_ID
from .model import Dependency, DependencyError


TARGET = "net10.0"
MODERN = re.compile(r"net(\d+)\.(\d+)")
CORE = re.compile(r"\.?netcoreapp(\d+)\.(\d+)")
MIN_DOTNET = (5, 0)
MIN_CORE = (1, 0)
STANDARD = re.compile(r"\.?netstandard(\d+)\.(\d+)")
MAX_DOTNET = (10, 0)
MAX_STANDARD = (2, 1)


def framework_rank(value):
    """Оценить группу для обычного проекта net10.0 без RID."""
    name = value.strip().lower().replace(",version=v", "")
    if name in {"", "any"}:
        return 0, (0, 0)
    for pattern, minimum, limit, priority in (
        (MODERN, MIN_DOTNET, MAX_DOTNET, 2),
        (CORE, MIN_CORE, MAX_DOTNET, 2),
        (STANDARD, MIN_CORE, MAX_STANDARD, 1),
    ):
        match = pattern.fullmatch(name)
        if match:
            version = tuple(int(part) for part in match.groups())
            if minimum <= version <= limit:
                return priority, version
    return None


def select_group(dependencies):
    """Выбрать ближайшую совместимую группу, включая пустую."""
    groups = []
    for group in dependencies.findall("{*}group"):
        rank = framework_rank(group.get("targetFramework", ""))
        if rank is not None:
            groups.append((rank, group))
    if groups:
        return max(groups, key=lambda item: item[0])[1]
    if dependencies.findall("{*}group") and not dependencies.findall(
        "{*}dependency",
    ):
        raise DependencyError(f"нет группы зависимостей для {TARGET}")
    return dependencies


def read_dependencies(content):
    """Получить имена и ограничения из XML, независимо от namespace."""
    try:
        document = ElementTree.fromstring(content)
    except (ElementTree.ParseError, LookupError) as error:
        raise DependencyError(f"некорректный .nuspec: {error}") from error
    metadata = document.find("{*}metadata")
    if metadata is None:
        raise DependencyError("в .nuspec отсутствует элемент metadata")
    dependencies = metadata.find("{*}dependencies")
    if dependencies is None:
        return ()
    selected = select_group(dependencies)
    result = []
    for element in selected.findall("{*}dependency"):
        name = element.get("id", "")
        if not PACKAGE_ID.fullmatch(name):
            raise DependencyError(f"некорректный ID зависимости: {name!r}")
        result.append(Dependency(name.lower(), element.get("version", "")))
    return tuple(result)
