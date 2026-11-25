"""Чтение stdin, преобразование и запись TOML."""

import argparse
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from .evaluate import evaluate
from .toml_output import render_document


def save(path, data):
    """Заменить результат только после успешной записи временного файла."""
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        draft = Path(temporary.name)
        try:
            temporary.write(data)
            temporary.close()
            draft.replace(path)
        finally:
            draft.unlink(missing_ok=True)


def main(argv=None):
    """Принять вход из stdin и сохранить TOML по --output."""
    parser = argparse.ArgumentParser(description="Учебный язык в TOML")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.buffer.read().decode("utf-8-sig")
        result = render_document(evaluate(text))
        save(args.output, result.encode("utf-8"))
    except (OSError, ValueError, RecursionError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0
