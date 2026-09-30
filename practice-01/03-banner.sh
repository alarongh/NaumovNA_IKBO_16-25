#!/usr/bin/env bash
set -euo pipefail

if (( $# != 1 )); then
  printf 'Использование: %s ТЕКСТ\n' "$0" >&2
  exit 2
fi

text=$1
# Ширина измеряется в символах; для кириллицы нужна UTF-8 локаль.
width=${#text}
printf -v border '%*s' "$((width + 2))" ''
border=${border// /-}
printf '+%s+\n| %s |\n+%s+\n' "$border" "$text" "$border"
