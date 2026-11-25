"""Синтаксический разбор Lark по отдельной грамматике."""

from pathlib import Path

from lark import Lark, UnexpectedInput


GRAMMAR = Path(__file__).with_name("grammar.lark")
PARSER = Lark(GRAMMAR.read_text(encoding="utf-8"), parser="lalr",
              propagate_positions=True, maybe_placeholders=False)


def parse(text):
    """Построить дерево или сообщить строку и столбец ошибки."""
    try:
        return PARSER.parse(text)
    except UnexpectedInput as error:
        message = (
            f"строка {error.line}, столбец {error.column}: "
            "синтаксическая ошибка"
        )
        raise ValueError(message) from error
