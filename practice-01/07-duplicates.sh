#!/usr/bin/env bash
set -euo pipefail

root=${1:-.}
if [[ ! -d $root ]]; then
  printf 'Каталог не существует: %s\n' "$root" >&2
  exit 1
fi

declare -A buckets=()
declare -a representatives=() members=() counts=()

while IFS= read -r -d '' file; do
  digest=$(sha256sum -- "$file")
  digest=${digest:0:64}
  match=-1
  for index in ${buckets[$digest]-}; do
    if cmp -s -- "$file" "${representatives[index]}"; then
      match=$index
      break
    fi
  done

  printf -v quoted '%q' "$file"
  if (( match >= 0 )); then
    members[match]+=$'\n'"$quoted"
    ((counts[match] += 1))
  else
    index=${#representatives[@]}
    representatives+=("$file")
    members+=("$quoted")
    counts+=(1)
    buckets[$digest]="${buckets[$digest]-} $index"
  fi
done < <(find "$root" -type f -print0 | LC_ALL=C sort -z)

found=0
for ((index = 0; index < ${#representatives[@]}; index++)); do
  if (( counts[index] > 1 )); then
    ((found += 1))
    printf 'Группа %d (%d копии):\n%s\n' "$found" "${counts[index]}" "${members[index]}"
  fi
done
printf 'Групп дубликатов: %d\n' "$found"
