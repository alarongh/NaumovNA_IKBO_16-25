"""Интерфейс командной строки."""

import sys

from .config import parse_args
from .model import DependencyError
from .nuget import NugetRepository


def main(argv=None):
    """Вывести прямые зависимости из манифеста корневого пакета."""
    args = parse_args(argv)
    try:
        if args.test:
            raise DependencyError("режим JSON появится на этапе 3")
        repository = NugetRepository(args.repository)
        package = repository.root(args.package)
        dependencies = repository.manifest(package)
    except DependencyError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print(package)
    for dependency in dependencies:
        print(f"- {dependency.name} {dependency.requirement or '(любая)'}")
    if not dependencies:
        print("Прямых зависимостей нет.")
    return 0
