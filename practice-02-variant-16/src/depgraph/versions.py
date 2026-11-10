"""Сравнение версий и разбор диапазонов NuGet."""

from dataclasses import dataclass
import re

from .model import DependencyError


VERSION = re.compile(
    r"(\d+(?:\.\d+){0,3})(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?",
    re.ASCII,
)
COMPONENTS = 4


def version_key(value):
    """Получить ключ NuGet-версии, включая prerelease."""
    match = VERSION.fullmatch(value)
    if not match:
        raise DependencyError(f"некорректная версия NuGet: {value!r}")
    numbers, suffix = match.groups()
    digits = [int(part) for part in numbers.split(".")]
    digits.extend([0] * (COMPONENTS - len(digits)))
    labels = () if suffix is None else tuple(map(label_key, suffix.split(".")))
    return tuple(digits), suffix is None, labels


def label_key(label):
    """Поставить числовой идентификатор перед текстовым."""
    return (0, int(label)) if label.isdigit() else (1, label.casefold())


@dataclass(frozen=True)
class Requirement:
    """Нижняя и верхняя границы с признаками включения."""

    lower: tuple | None = None
    upper: tuple | None = None
    include_lower: bool = False
    include_upper: bool = False

    @classmethod
    def parse(cls, value):
        """Разобрать интервал, точную версию или нижнюю границу."""
        value = value.strip()
        if not value:
            return cls()
        if value[0] not in "[(":
            return cls(lower=version_key(value), include_lower=True)
        if value[-1] not in ")]":
            raise DependencyError(f"некорректный диапазон NuGet: {value!r}")
        lower, comma, upper = value[1:-1].partition(",")
        low = version_key(lower.strip()) if lower.strip() else None
        high = version_key(upper.strip()) if upper.strip() else None
        if not comma:
            if value[0] == "[" and value[-1] == "]" and low is not None:
                return cls(low, low, True, True)
            raise DependencyError(f"некорректный диапазон NuGet: {value!r}")
        return cls(low, high, value[0] == "[", value[-1] == "]")

    def accepts(self, version):
        """Проверить, удовлетворяет ли версия границам."""
        if self.lower is not None:
            if version < self.lower or (version == self.lower
                                        and not self.include_lower):
                return False
        if self.upper is not None:
            if version > self.upper or (version == self.upper
                                        and not self.include_upper):
                return False
        return True

    @property
    def allows_prerelease(self):
        """Разрешить prerelease, когда он явно указан в границе."""
        return any(bound is not None and not bound[1]
                   for bound in (self.lower, self.upper))
