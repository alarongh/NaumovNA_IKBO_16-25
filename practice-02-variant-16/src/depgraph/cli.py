"""Интерфейс командной строки."""

from .config import parse_args


def main(argv=None):
    """Вывести проверенные настройки в формате ключ=значение."""
    args = parse_args(argv)
    for name, value in vars(args).items():
        print(f"{name}={value}")
    return 0
