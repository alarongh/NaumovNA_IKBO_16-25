#!/usr/bin/env bash
set -euo pipefail

root=${1:-.}
if [[ ! -d $root ]]; then
  printf 'Каталог не существует: %s\n' "$root" >&2
  exit 1
fi

# Содержимое нулевой длины нельзя распознать как текст или бинарные данные.
# Поэтому текстовыми считаются файлы с перечисленными текстовыми расширениями.
find "$root" -maxdepth 1 -type f -empty \( \
  -iname '*.txt' -o -iname '*.md' -o -iname '*.csv' -o \
  -iname '*.json' -o -iname '*.xml' -o -iname '*.yaml' -o \
  -iname '*.yml' -o -iname '*.ini' -o -iname '*.log' -o \
  -iname '*.py' -o -iname '*.js' -o -iname '*.c' -o \
  -iname '*.h' -o -iname '*.sh' \
\) -print | LC_ALL=C sort
