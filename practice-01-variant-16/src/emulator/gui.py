"""Окно эмулятора на Tkinter."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .shell import ShellError


class Terminal:
    """Графический цикл ввода, исполнения и вывода команд."""

    def __init__(self, root, shell, vfs_name):
        self.root = root
        self.shell = shell
        root.title(f"Эмулятор оболочки — {vfs_name}")
        root.minsize(480, 280)
        self.output = ScrolledText(
            root, width=78, height=22, state="disabled",
            wrap="word", font="TkFixedFont", padx=8, pady=8,
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=(10, 6))
        row = ttk.Frame(root)
        row.pack(fill="x", padx=10, pady=(0, 10))
        self.prompt = ttk.Label(row, text="$ ", font="TkFixedFont")
        self.prompt.pack(side="left")
        self.entry = ttk.Entry(row, font="TkFixedFont")
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

    def write(self, text):
        """Добавить строку в область вывода и прокрутить к концу."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.see(tk.END)

    def submit(self, _event=None):
        """Принять строку из поля ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_line(line)

    def run_line(self, line):
        """Показать введённую строку и вывести ответ оболочки."""
        self.write(f"{self.prompt.cget('text')}{line}")
        try:
            response = self.shell.execute(line)
        except ShellError as error:
            self.write(f"Ошибка: {error}")
            return
        if response:
            self.write(response)
        if self.shell.closed:
            self.root.destroy()

    def run_startup(self, lines):
        """Выполнить команды по порядку, пока сеанс открыт."""
        for line in lines:
            self.run_line(line)
            if self.shell.closed:
                return
