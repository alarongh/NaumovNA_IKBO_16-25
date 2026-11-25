"""Вычисление констант и построение значений конфигурации."""

from copy import deepcopy

from .parser import parse


class Evaluator:
    """Обходить дерево с отдельной областью констант для словаря."""

    def __init__(self):
        self.scopes = [{}]

    def evaluate(self, tree):
        """Вычислить узел и добавить место семантической ошибки."""
        try:
            return getattr(self, str(tree.data))(tree.children)
        except ValueError as error:
            raise ValueError(
                f"строка {tree.meta.line}, столбец {tree.meta.column}: {error}"
            ) from error

    def start(self, nodes):
        """Обработать объявления перед корневым значением."""
        for node in nodes[:-1]:
            self.evaluate(node)
        return self.evaluate(nodes[-1])

    def number(self, nodes):
        """Преобразовать положительную десятичную запись в целое."""
        return int(nodes[0])

    def declaration(self, nodes):
        """Объявить константу после вычисления её значения."""
        name, value = nodes
        name = str(name)
        if name in self.scopes[-1]:
            raise ValueError(f"повторное объявление константы {name}")
        self.scopes[-1][name] = self.evaluate(value)

    def reference(self, nodes):
        """Найти ближайшую уже объявленную константу."""
        name = str(nodes[0])
        for scope in reversed(self.scopes):
            if name in scope:
                return deepcopy(scope[name])
        raise ValueError(f"константа {name} не определена")

    def array(self, nodes):
        """Вычислить элементы массива слева направо."""
        return [self.evaluate(node) for node in nodes]

    def dictionary(self, nodes):
        """Собрать поля словаря и ограничить область констант."""
        result = {}
        self.scopes.append({})
        try:
            for node in nodes:
                if node.data == "declaration":
                    self.evaluate(node)
                else:
                    name, value = node.children
                    if str(name) in result:
                        raise ValueError(f"повторное поле {name}")
                    result[str(name)] = self.evaluate(value)
        finally:
            self.scopes.pop()
        return result

    def integers(self, nodes):
        """Получить два числовых операнда."""
        left, right = (self.evaluate(node) for node in nodes)
        if type(left) is not int or type(right) is not int:
            raise ValueError("операции + и - требуют числа")
        return left, right

    def add(self, nodes):
        """Сложить два числа."""
        left, right = self.integers(nodes)
        return left + right

    def subtract(self, nodes):
        """Вычесть правое число из левого."""
        left, right = self.integers(nodes)
        return left - right

    def concat(self, nodes):
        """Соединить два массива в новый массив."""
        left, right = (self.evaluate(node) for node in nodes)
        if not isinstance(left, list) or not isinstance(right, list):
            raise ValueError("concat требует два массива")
        return left + right

    def length(self, nodes):
        """Получить число элементов массива или полей словаря."""
        value = self.evaluate(nodes[0])
        if not isinstance(value, (list, dict)):
            raise ValueError("len требует массив или словарь")
        return len(value)


def evaluate(text):
    """Вычислить независимый документ с новым окружением."""
    return Evaluator().evaluate(parse(text))
