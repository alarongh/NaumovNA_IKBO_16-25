#!/usr/bin/env bash
set -euo pipefail

passwd_file=${1:-/etc/passwd}
if [[ ! -f $passwd_file || ! -r $passwd_file ]]; then
  printf 'Не удаётся прочитать файл: %s\n' "$passwd_file" >&2
  exit 1
fi

cut -d: -f1 -- "$passwd_file" | LC_ALL=C sort
