"""Запись результата с проверкой исходного пути."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def write_result(source, target, data):
    """Проверить пути и атомарно заменить выходной файл."""
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError("входной и выходной пути совпадают")
    if target.exists() and os.path.samefile(source, target):
        raise ValueError("выходной файл ссылается на входной")
    with NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
        draft = Path(temporary.name)
        try:
            temporary.write(data)
            temporary.close()
            draft.replace(target)
        finally:
            draft.unlink(missing_ok=True)
