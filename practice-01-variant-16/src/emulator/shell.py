"""Разбор строк и исполнение команд оболочки."""

from stat import S_IFDIR, S_IFREG, filemode

from .permissions import apply_mode, mode_changes, parse_owner
from .vfs import VfsError


class ShellError(ValueError):
    """Ошибка, которую нужно вывести в терминале."""


def parse_command(line):
    """Разделить строку по пробельным символам."""
    words = line.split()
    return (words[0], words[1:]) if words else ("", [])


def parse_options(arguments, supported):
    """Разобрать короткие флаги и позиционные параметры."""
    options, operands = set(), []
    read_options = True
    for argument in arguments:
        if read_options and argument == "--":
            read_options = False
        elif read_options and argument.startswith("-") and argument != "-":
            for option in argument[1:]:
                if option not in supported:
                    raise VfsError(f"неизвестный флаг -{option}")
                options.add(option)
        else:
            operands.append(argument)
    return options, operands


def one_path(arguments, default):
    """Вернуть единственный путь или значение по умолчанию."""
    if not arguments:
        return default
    path, *extra = arguments
    if extra:
        raise VfsError("ожидается один путь")
    return path


def long_entry(name, node):
    """Вывести права, владельца, группу, размер файла и имя."""
    kind = S_IFDIR if node.is_directory else S_IFREG
    size = len(node.data or b"")
    mode = filemode(kind | node.mode)
    return f"{mode} {node.owner} {node.group} {size} {name}"


def directory_entries(node, show_hidden):
    """Сформировать отсортированный список записей для ls."""
    entries = []
    if show_hidden:
        entries.extend(((".", node), ("..", node.parent or node)))
    for name in sorted(node.children):
        if show_hidden or not name.startswith("."):
            entries.append((name, node.children[name]))
    return entries


def disk_usage(node, rows):
    """Подсчитать байты и собрать строки для вложенных каталогов."""
    if not node.is_directory:
        return len(node.data)
    size = 0
    for name in sorted(node.children):
        size += disk_usage(node.children[name], rows)
    rows.append(f"{size}\t{node.path}")
    return size


class Shell:
    """Сеанс эмулятора с собственным текущим каталогом."""

    def __init__(self, vfs):
        self.vfs = vfs
        self.cwd = vfs.root
        self.closed = False
        self.commands = {
            "ls": self.ls,
            "cd": self.cd,
            "pwd": self.pwd,
            "uname": self.uname,
            "du": self.du,
            "chmod": self.chmod,
            "chown": self.chown,
            "exit": self.exit,
        }

    @property
    def prompt(self):
        """Показать текущий виртуальный путь в приглашении."""
        return f"{self.cwd.path} $ "

    def execute(self, line):
        """Выполнить команду и вернуть текст её ответа."""
        command, arguments = parse_command(line)
        if not command:
            return ""
        if command not in self.commands:
            raise ShellError(f"{command}: команда не найдена")
        try:
            return self.commands[command](arguments)
        except VfsError as error:
            raise ShellError(f"{command}: {error}") from error

    def ls(self, arguments):
        """Показать файл или содержимое каталога."""
        options, operands = parse_options(arguments, "al")
        node = self.vfs.resolve(one_path(operands, "."), self.cwd)
        if node.is_directory:
            entries = directory_entries(node, "a" in options)
        else:
            entries = [(node.name, node)]
        if "l" in options:
            return "\n".join(long_entry(name, item) for name, item in entries)
        return "\n".join(name for name, _ in entries)

    def cd(self, arguments):
        """Сменить текущий каталог внутри VFS."""
        path = one_path(arguments, "/")
        target = self.vfs.resolve(path, self.cwd)
        if not target.is_directory:
            raise VfsError(f"{path}: не каталог")
        self.cwd = target
        return ""

    def pwd(self, arguments):
        """Вернуть абсолютный путь текущего каталога."""
        if arguments:
            raise VfsError("команда не принимает аргументы")
        return self.cwd.path

    def uname(self, arguments):
        """Показать условное имя системы эмулятора."""
        if not arguments:
            return "Linux"
        if arguments == ["-a"]:
            return "Linux vfs 1.0 emulator"
        raise VfsError("использование: uname [-a]")

    def du(self, arguments):
        """Показать размер файла или дерева каталогов в байтах."""
        options, operands = parse_options(arguments, "s")
        node = self.vfs.resolve(one_path(operands, "."), self.cwd)
        rows = []
        size = disk_usage(node, rows)
        if "s" in options or not node.is_directory:
            return f"{size}\t{node.path}"
        return "\n".join(rows)

    def change_targets(self, arguments, usage):
        """Проверить наличие параметров и найти все цели до изменения."""
        if not arguments:
            raise VfsError(f"использование: {usage}")
        value, *paths = arguments
        if not paths:
            raise VfsError(f"использование: {usage}")
        targets = [self.vfs.resolve(path, self.cwd) for path in paths]
        return value, targets

    def chmod(self, arguments):
        """Изменить права файлов и каталогов в памяти."""
        value, targets = self.change_targets(arguments, "chmod РЕЖИМ ПУТЬ ...")
        changes = mode_changes(value)
        for node in targets:
            node.mode = apply_mode(node.mode, changes)
        return ""

    def chown(self, arguments):
        """Изменить владельца и/или группу в памяти."""
        value, targets = self.change_targets(
            arguments, "chown ВЛАДЕЛЕЦ[:ГРУППА] ПУТЬ ...",
        )
        owner, group = parse_owner(value)
        for node in targets:
            node.owner = owner or node.owner
            node.group = group or node.group
        return ""

    def exit(self, arguments):
        """Завершить сеанс."""
        if arguments:
            raise VfsError("команда не принимает аргументы")
        self.closed = True
        return ""
