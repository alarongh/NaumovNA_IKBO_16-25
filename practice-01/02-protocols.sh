#!/usr/bin/env bash
set -euo pipefail

protocols_file=${1:-/etc/protocols}
if [[ ! -f $protocols_file || ! -r $protocols_file ]]; then
  printf 'Не удаётся прочитать файл: %s\n' "$protocols_file" >&2
  exit 1
fi

# В /etc/protocols второе поле - номер протокола, а не сетевой порт.
awk '
  /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
  $2 ~ /^[0-9]+$/ { print $2, $1 }
' "$protocols_file" | LC_ALL=C sort -k1,1nr -k2,2 | awk 'NR <= 5'
