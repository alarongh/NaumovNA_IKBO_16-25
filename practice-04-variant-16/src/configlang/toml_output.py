"""Сериализация поддерживаемых значений в TOML 1.0."""


MIN_INTEGER = -(1 << 63)
MAX_INTEGER = (1 << 63) - 1


def render_value(value):
    """Вывести число, массив или inline-словарь, включая вложенные."""
    if type(value) is int:
        if not MIN_INTEGER <= value <= MAX_INTEGER:
            raise ValueError("число выходит за диапазон TOML int64")
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(map(render_value, value)) + "]"
    if isinstance(value, dict):
        fields = [f"{key} = {render_value(item)}"
                  for key, item in value.items()]
        return "{ " + ", ".join(fields) + " }"
    raise ValueError("неподдерживаемый тип значения")


def render_document(value):
    """Вывести корневые поля либо обернуть значение ключом value."""
    fields = value if isinstance(value, dict) else {"value": value}
    lines = [f"{key} = {render_value(item)}"
             for key, item in fields.items()]
    return "\n".join(lines) + "\n"
