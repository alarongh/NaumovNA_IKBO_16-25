#!/usr/bin/env bash
set -euo pipefail

if (( $# != 1 )) || [[ ! -f $1 || ! -r $1 ]]; then
  printf 'Использование: %s ИСХОДНЫЙ_ФАЙЛ\n' "$0" >&2
  exit 2
fi

# По образцу задания ищем слова во всём тексте, включая комментарии и строки.
if ! grep -Eq '[[:alpha:]_][[:alnum:]_]*' -- "$1"; then
  printf '\n'
  exit 0
fi
grep -Eo '[[:alpha:]_][[:alnum:]_]*' -- "$1" | LC_ALL=C sort -u | paste -sd ' ' -
