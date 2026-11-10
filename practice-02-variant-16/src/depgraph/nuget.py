"""Доступ к индексам и манифестам NuGet V3 по HTTP."""

import json
from urllib.request import urlopen

from .config import repository_url
from .model import DependencyError, Package
from .nuspec import read_dependencies
from .versions import Requirement, version_key


TIMEOUT_SECONDS = 15
RESOURCE_TYPE = "PackageBaseAddress/3.0.0"


def read_url(url):
    """Загрузить данные и показать адрес при сетевой ошибке."""
    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except OSError as error:
        raise DependencyError(f"{url}: {error}") from error


def read_json(url):
    """Разобрать JSON-ответ сервера."""
    try:
        document = json.loads(read_url(url))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise DependencyError(f"{url}: некорректный JSON") from error
    if not isinstance(document, dict):
        raise DependencyError(f"{url}: ожидался объект JSON")
    return document


def find_base(index):
    """Найти адрес ресурса PackageBaseAddress в индексе."""
    resources = read_json(index).get("resources")
    if not isinstance(resources, list):
        raise DependencyError("в индексе NuGet нет списка resources")
    for item in resources:
        if not isinstance(item, dict) or item.get("@type") != RESOURCE_TYPE:
            continue
        address = item.get("@id")
        if isinstance(address, str):
            try:
                return repository_url(address).rstrip("/")
            except ValueError as error:
                raise DependencyError("ошибочный @id ресурса") from error
    raise DependencyError(f"в индексе NuGet нет ресурса {RESOURCE_TYPE}")


class NugetRepository:
    """Читать версии пакетов и их манифесты из одного репозитория."""

    def __init__(self, index):
        self.base = find_base(index)
        self.version_lists = {}

    def versions(self, name):
        """Получить версии в порядке от младшей к старшей."""
        if name not in self.version_lists:
            url = f"{self.base}/{name}/index.json"
            versions = read_json(url).get("versions")
            if not isinstance(versions, list) or not all(
                isinstance(item, str) for item in versions
            ):
                raise DependencyError(f"{url}: неверный список versions")
            self.version_lists[name] = tuple(sorted(versions, key=version_key))
        return self.version_lists[name]

    def root(self, name):
        """Выбрать новейшую стабильную версию корневого пакета."""
        name = name.lower()
        for version in reversed(self.versions(name)):
            if version_key(version)[1]:
                return Package(name, version)
        raise DependencyError(f"{name}: нет стабильной версии")

    def manifest(self, package):
        """Извлечь прямые зависимости из .nuspec нужной версии."""
        name = package.name
        address = f"{self.base}/{name}/{package.version.lower()}"
        try:
            return read_dependencies(read_url(f"{address}/{name}.nuspec"))
        except DependencyError as error:
            raise DependencyError(f"{package}: {error}") from error

    def resolve(self, dependency):
        """Выбрать минимальную версию, допустимую для данного ребра."""
        requirement = Requirement.parse(dependency.requirement)
        for version in self.versions(dependency.name):
            key = version_key(version)
            if not (key[1] or requirement.allows_prerelease):
                continue
            if requirement.accepts(key):
                return Package(dependency.name, version)
        detail = dependency.requirement or "(любая)"
        raise DependencyError(f"{dependency.name}: нет версии для {detail}")

    def dependencies(self, package):
        """Прочитать манифест и подобрать версию для каждой зависимости."""
        try:
            return tuple(self.resolve(item) for item in self.manifest(package))
        except DependencyError as error:
            raise DependencyError(f"зависимости {package}: {error}") from error
