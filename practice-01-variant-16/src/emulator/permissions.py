"""Разбор и применение виртуальных прав и владельцев."""

import re

from .vfs import ACCOUNT_NAME, VfsError, parse_octal_mode


SYMBOLIC_MODE = re.compile(r"([ugoa]*)([+=-])([rwx]*)")
CLASS_SHIFTS = {"u": 6, "g": 3, "o": 0}
PERMISSION_BITS = {"r": 4, "w": 2, "x": 1}
CLASS_MASK = 0o7
MODE_MASK = 0o7777


def mode_changes(value):
    """Разобрать числовой режим или список символьных правил."""
    if value.isdecimal():
        return [("=", MODE_MASK, parse_octal_mode(value))]
    return [symbolic_change(rule) for rule in value.split(",")]


def symbolic_change(rule):
    """Получить оператор, маску классов и биты прав для одного правила."""
    match = SYMBOLIC_MODE.fullmatch(rule)
    if not match:
        raise VfsError(f"недопустимый режим: {rule}")
    classes, operator, permissions = match.groups()
    if not permissions and operator != "=":
        raise VfsError(f"не указаны права: {rule}")
    if not classes or "a" in classes:
        classes = "ugo"
    bits = sum(PERMISSION_BITS[item] for item in set(permissions))
    shifts = [CLASS_SHIFTS[item] for item in set(classes)]
    mask = sum(CLASS_MASK << shift for shift in shifts)
    changed = sum(bits << shift for shift in shifts)
    return operator, mask, changed


def apply_mode(mode, changes):
    """Вычислить новые права после последовательного применения правил."""
    for operator, mask, bits in changes:
        if operator == "+":
            mode |= bits
        elif operator == "-":
            mode &= ~bits
        else:
            mode = (mode & ~mask) | bits
    return mode


def parse_owner(value):
    """Получить имя владельца и/или группы из аргумента chown."""
    owner, separator, group = value.partition(":")
    if not (owner or group) or (separator and not group):
        raise VfsError(f"недопустимый владелец или группа: {value}")
    for account in (owner, group):
        if account and not ACCOUNT_NAME.fullmatch(account):
            raise VfsError(f"недопустимое имя владельца или группы: {account}")
    return owner, group
