#!/usr/bin/env bash
set -euo pipefail

if (( $# != 2 )); then
  printf 'Использование: %s ВХОДНОЙ_ФАЙЛ ВЫХОДНОЙ_ФАЙЛ\n' "$0" >&2
  exit 2
fi
if [[ ! -f $1 || ! -r $1 ]]; then
  printf 'Не удаётся прочитать файл: %s\n' "$1" >&2
  exit 1
fi
if [[ $1 == "$2" || ( -e $2 && $1 -ef $2 ) ]]; then
  printf 'Входной и выходной файлы должны различаться\n' >&2
  exit 2
fi

sed $'s/    /\t/g' -- "$1" > "$2"
