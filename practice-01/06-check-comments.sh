#!/usr/bin/env bash
set -euo pipefail

root=${1:-.}
if [[ ! -d $root ]]; then
  printf 'Каталог не существует: %s\n' "$root" >&2
  exit 1
fi

failed=0
checked=0
while IFS= read -r -d '' file; do
  ((checked += 1))
  first_line=''
  IFS= read -r first_line < "$file" || true
  first_line=${first_line#$'\xef\xbb\xbf'}
  case $file in
    *.py) pattern='^[[:space:]]*#' ;;
    *.c|*.js) pattern='^[[:space:]]*(//|/\*)' ;;
  esac
  if [[ ! $first_line =~ $pattern ]]; then
    printf 'Нет комментария в первой строке: %s\n' "$file"
    ((failed += 1))
  fi
done < <(find "$root" -type f \( -name '*.c' -o -name '*.js' -o -name '*.py' \) -print0)

printf 'Проверено: %d; без комментария: %d\n' "$checked" "$failed"
(( failed == 0 ))
