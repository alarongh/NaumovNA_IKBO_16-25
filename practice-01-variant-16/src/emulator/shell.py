"""Разбор строк и исполнение команд оболочки."""


class ShellError(ValueError):
    """Ошибка, которую нужно вывести в терминале."""


def parse_command(line):
    """Разделить строку по пробельным символам."""
    words = line.split()
    return (words[0], words[1:]) if words else ("", [])


class Shell:
    """Сеанс эмулятора."""

    def __init__(self):
        self.closed = False
        self.commands = {"ls": self.ls, "cd": self.cd, "exit": self.exit}

    def execute(self, line):
        """Выполнить команду и вернуть текст её ответа."""
        command, arguments = parse_command(line)
        if not command:
            return ""
        if command not in self.commands:
            raise ShellError(f"{command}: команда не найдена")
        return self.commands[command](arguments)

    def ls(self, arguments):
        """Показать аргументы команды ls."""
        return f"ls: {arguments}"

    def cd(self, arguments):
        """Показать аргументы команды cd."""
        return f"cd: {arguments}"

    def exit(self, arguments):
        """Завершить сеанс."""
        if arguments:
            raise ShellError("exit: команда не принимает аргументы")
        self.closed = True
        return ""
