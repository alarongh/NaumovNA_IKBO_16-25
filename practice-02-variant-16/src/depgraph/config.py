"""Параметры командной строки и проверка путей."""

import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit


NUGET_INDEX = "https://api.nuget.org/v3/index.json"
PACKAGE_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,99}")
TEST_ID = re.compile(r"[A-Z]")


def parser():
    """Описать параметры запуска."""
    result = argparse.ArgumentParser(description="Граф зависимостей NuGet")
    result.add_argument("--package", required=True, help="имя пакета")
    result.add_argument("--repository", help="URL NuGet V3 или путь к JSON")
    result.add_argument("--test", action="store_true", help="режим JSON")
    result.add_argument(
        "--output", type=Path, default=Path("graph.svg"),
        help="имя SVG-файла, по умолчанию graph.svg",
    )
    result.add_argument(
        "--ascii", action="store_true", help="вывести ASCII-дерево",
    )
    result.add_argument(
        "--order", action="store_true", help="вывести порядок зависимостей",
    )
    return result


def repository_url(value):
    """Проверить URL сервисного индекса NuGet."""
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("нужен URL с http:// или https://")
    if parts.username or parts.password or parts.fragment:
        raise ValueError("URL с учётными данными или фрагментом недопустим")
    if any(character.isspace() for character in value):
        raise ValueError("пробельные символы в URL недопустимы")
    if parts.port == 0:
        raise ValueError("порт должен быть положительным")
    return value


def check_repository(value, test):
    """Проверить источник согласно выбранному режиму."""
    if not test:
        return repository_url(value if value is not None else NUGET_INDEX)
    if not value or not Path(value).is_file():
        raise ValueError("для --test нужен существующий файл репозитория")
    return value


def check_output(path, source=None):
    """Проверить имя SVG и расположение обоих выходных файлов."""
    if path.suffix.lower() != ".svg":
        raise ValueError("имя файла должно оканчиваться на .svg")
    if not path.parent.is_dir():
        raise ValueError("каталог для результата должен существовать")
    for target in (path, path.with_suffix(".dot")):
        if target.is_dir():
            raise ValueError(f"{target} — каталог")
        if source is not None and target.resolve() == Path(source).resolve():
            raise ValueError("имя результата совпадает с файлом репозитория")


def parse_args(argv):
    """Проверить значения и вернуть настройки запуска."""
    cli = parser()
    args = cli.parse_args(argv)
    pattern = TEST_ID if args.test else PACKAGE_ID
    if not pattern.fullmatch(args.package):
        cli.error("--package: недопустимое имя пакета")
    try:
        args.repository = check_repository(args.repository, args.test)
    except (ValueError, OSError) as error:
        cli.error(f"--repository: {error}")
    try:
        check_output(args.output, args.repository if args.test else None)
    except (ValueError, OSError, RuntimeError) as error:
        cli.error(f"--output: {error}")
    return args
