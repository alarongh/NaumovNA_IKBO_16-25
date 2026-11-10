# Практическое занятие №2. Вариант 16

Выполнил — Наумов Никита Александрович.

Группа — ИКБО-16-25.

Тема — граф зависимостей пакетов NuGet.

---

## Этап 1. Параметры командной строки

Команды выполняются из каталога этой практики. Нужен Python 3.10 или
новее. Прототип проверяет настройки и печатает их в формате
`ключ=значение`.

| Параметр | Значение |
| --- | --- |
| `--package ИМЯ` | Идентификатор пакета. В тестовом режиме — одна латинская буква от A до Z. |
| `--repository АДРЕС` | URL индекса NuGet V3 или путь к локальному файлу при `--test`. |
| `--test` | Использует локальный репозиторий. |
| `--output ФАЙЛ` | Имя файла SVG. По умолчанию `graph.svg`. |
| `--ascii` | Включает вывод дерева в терминал. |

```bat
run.bat --package A --repository examples\diamond.json --test --output graph.svg --ascii
python -B -m unittest discover -s tests -v
```

```text
package=A
repository=examples\diamond.json
test=True
output=graph.svg
ascii=True
```

Проверка ошибок для пяти параметров.

```bat
run.bat --package /bad
run.bat --package A --repository ftp://example.net/feed
run.bat --package A --test=maybe
run.bat --package A --output graph.png
run.bat --package A --ascii=maybe
```
