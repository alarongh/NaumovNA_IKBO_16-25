"""Загрузка XML в независимое дерево каталогов и файлов."""

from base64 import b64decode
from dataclasses import dataclass, field
import re
from xml.etree import ElementTree


ACCOUNT_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*|[0-9]+")
OCTAL_MODE = re.compile(r"[0-7]{3,4}")
DIRECTORY_MODE = 0o755
FILE_MODE = 0o644


class VfsError(ValueError):
    """Ошибка структуры или доступа к виртуальной файловой системе."""


@dataclass(eq=False)
class Node:
    """Запись VFS. Для каталога data равно None, для файла это байты."""

    name: str
    mode: int
    owner: str
    group: str
    data: bytes | None = None
    parent: "Node | None" = None
    children: dict[str, "Node"] = field(default_factory=dict)

    @property
    def is_directory(self):
        """Определить тип записи по наличию содержимого файла."""
        return self.data is None

    @property
    def path(self):
        """Собрать абсолютный путь по цепочке родителей."""
        parts = []
        node = self
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))

    def walk(self):
        """Перечислить текущую запись и всё её поддерево."""
        yield self
        for child in self.children.values():
            yield from child.walk()


@dataclass
class Vfs:
    """Виртуальная файловая система, загруженная в память."""

    name: str
    root: Node

    @classmethod
    def load(cls, path):
        """Прочитать XML и собрать дерево без записи на диск."""
        try:
            element = ElementTree.parse(path).getroot()
        except (OSError, ElementTree.ParseError, LookupError) as error:
            raise VfsError(str(error)) from error
        name = element.get("name", "").strip()
        if element.tag != "vfs" or not name:
            raise VfsError("ожидается корневой элемент <vfs name=\"...\">")
        return cls(name, load_directory(element, "/", None))

    def resolve(self, path, cwd):
        """Найти узел, обрабатывая абсолютные пути, . и .."""
        node = self.root if path.startswith("/") else cwd
        for part in path.split("/"):
            if not node.is_directory:
                raise VfsError(f"{node.path}: не каталог")
            if part == "..":
                node = node.parent or self.root
            elif part not in {"", "."}:
                if part not in node.children:
                    raise VfsError(f"{path}: нет такого файла или каталога")
                node = node.children[part]
        return node

    def summary(self):
        """Сосчитать каталоги и файлы, включая корневой каталог."""
        nodes = list(self.root.walk())
        directories = sum(node.is_directory for node in nodes)
        files = len(nodes) - directories
        return f"VFS «{self.name}»: каталогов {directories}, файлов {files}"


def parse_octal_mode(value):
    """Преобразовать три или четыре восьмеричные цифры в числовой режим."""
    if not OCTAL_MODE.fullmatch(value):
        raise VfsError(f"недопустимый режим: {value}")
    return int(value, 8)


def load_node(element, name, parent, default_mode, data=None):
    """Создать узел и прочитать его атрибуты владельца и прав."""
    mode = parse_octal_mode(element.get("mode", f"{default_mode:o}"))
    owner = element.get("owner", "student")
    group = element.get("group", "students")
    if not (ACCOUNT_NAME.fullmatch(owner) and ACCOUNT_NAME.fullmatch(group)):
        raise VfsError(f"{name}: недопустимое имя владельца или группы")
    return Node(name, mode, owner, group, data, parent)


def load_directory(element, name, parent):
    """Рекурсивно заполнить каталог и проверить уникальность имён."""
    directory = load_node(element, name, parent, DIRECTORY_MODE)
    for child in element:
        if child.tag not in {"dir", "file"}:
            raise VfsError(f"неизвестный XML-элемент: {child.tag}")
        child_name = child.get("name", "")
        if not valid_name(child_name):
            raise VfsError(f"недопустимое имя записи: {child_name!r}")
        if child_name in directory.children:
            raise VfsError(f"{name}: повторяющееся имя {child_name}")
        if child.tag == "dir":
            node = load_directory(child, child_name, directory)
        else:
            node = load_node(
                child, child_name, directory, FILE_MODE, read_data(child),
            )
        directory.children[child_name] = node
    return directory


def valid_name(name):
    """Проверить имя записи с учётом простого пробельного парсера."""
    return (
        bool(name) and name.isprintable() and "/" not in name
        and name not in {".", ".."}
        and not any(character.isspace() for character in name)
    )


def read_data(element):
    """Прочитать текст или декодировать двоичные данные файла."""
    if len(element):
        raise VfsError("внутри <file> допускается только содержимое файла")
    data = element.text or ""
    encoding = element.get("encoding", "text")
    if encoding == "text":
        return data.encode("utf-8")
    if encoding == "base64":
        try:
            return b64decode("".join(data.split()), validate=True)
        except ValueError as error:
            raise VfsError("некорректные данные base64") from error
    raise VfsError(f"неизвестная кодировка: {encoding}")
