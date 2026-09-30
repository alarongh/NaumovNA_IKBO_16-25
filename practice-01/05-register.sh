#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
  printf 'Использование: %s ПРОГРАММА [КАТАЛОГ_НАЗНАЧЕНИЯ]\n' "$0" >&2
  exit 2
fi

source_file=$1
destination=${2:-/usr/local/bin}
if [[ ! -f $source_file || ! -r $source_file ]]; then
  printf 'Не удаётся прочитать программу: %s\n' "$source_file" >&2
  exit 1
fi
if [[ ! -d $destination ]]; then
  printf 'Каталог назначения не существует: %s\n' "$destination" >&2
  exit 1
fi

install -m 0755 -- "$source_file" "$destination/$(basename -- "$source_file")"
printf 'Установлено: %s/%s\n' "$destination" "$(basename -- "$source_file")"
