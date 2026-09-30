#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
  printf 'Использование: %s РАСШИРЕНИЕ [АРХИВ.tar]\n' "$0" >&2
  exit 2
fi

extension=${1#.}
if [[ ! $extension =~ ^[[:alnum:]_+-]+$ ]]; then
  printf 'Некорректное расширение: %s\n' "$1" >&2
  exit 2
fi
archive=${2:-"files-${extension}.tar"}

files=()
while IFS= read -r -d '' file; do
  if [[ -e $archive && $file -ef $archive ]]; then
    continue
  fi
  files+=("$file")
done < <(find . -maxdepth 1 -type f -name "*.${extension}" -print0 | LC_ALL=C sort -z)

if (( ${#files[@]} == 0 )); then
  printf 'В текущем каталоге нет файлов .%s\n' "$extension" >&2
  exit 1
fi

tar -cf "$archive" -- "${files[@]}"
printf 'Архив %s: %d файлов\n' "$archive" "${#files[@]}"
