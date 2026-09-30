#!/usr/bin/env bash
set -euo pipefail

scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -r -- "$tmp"' EXIT
passed=0

assert_equal() {
  local expected=$1 actual=$2 label=$3
  if [[ $expected != "$actual" ]]; then
    printf 'FAIL: %s\nОжидалось: <%s>\nПолучено:  <%s>\n' "$label" "$expected" "$actual" >&2
    exit 1
  fi
  ((passed += 1))
}

printf 'bob:x:2:2::/home/bob:/bin/bash\nalice:x:1:1::/home/alice:/bin/bash\n' > "$tmp/passwd"
actual=$(bash "$scripts/01-users.sh" "$tmp/passwd")
assert_equal $'alice\nbob' "$actual" '1: сортировка пользователей'

printf 'ip 0 IP\ntcp 6 TCP\nfoo 150 FOO\nbar 140 BAR\nbaz 139 BAZ\nqux 138 QUX\nend 137 END\n' > "$tmp/protocols"
actual=$(bash "$scripts/02-protocols.sh" "$tmp/protocols")
assert_equal $'150 foo\n140 bar\n139 baz\n138 qux\n137 end' "$actual" '2: пять наибольших номеров'

actual=$(bash "$scripts/03-banner.sh" 'Hello from RTU MIREA!')
assert_equal $'+-----------------------+\n| Hello from RTU MIREA! |\n+-----------------------+' "$actual" '3: баннер'

printf '#include <stdio.h>\nint main(void) { printf("world"); return 0; }\n' > "$tmp/hello.c"
actual=$(bash "$scripts/04-identifiers.sh" "$tmp/hello.c")
assert_equal 'h include int main printf return stdio void world' "$actual" '4: идентификаторы из образца'

mkdir "$tmp/bin"
bash "$scripts/05-register.sh" "$scripts/03-banner.sh" "$tmp/bin" > /dev/null
[[ -x "$tmp/bin/03-banner.sh" ]] || { printf 'FAIL: 5: исполняемый файл не установлен\n' >&2; exit 1; }
actual=$("$tmp/bin/03-banner.sh" OK)
assert_equal $'+----+\n| OK |\n+----+' "$actual" '5: регистрация с правами 755'

mkdir "$tmp/comments"
printf '# comment\nprint(1)\n' > "$tmp/comments/good.py"
printf '// comment\nconst x = 1;\n' > "$tmp/comments/good.js"
printf '/* comment */\nint x;\n' > "$tmp/comments/good.c"
actual=$(bash "$scripts/06-check-comments.sh" "$tmp/comments")
assert_equal 'Проверено: 3; без комментария: 0' "$actual" '6: комментарии найдены'
printf 'print(2)\n' > "$tmp/comments/bad.py"
if bash "$scripts/06-check-comments.sh" "$tmp/comments" > "$tmp/check-output"; then
  printf 'FAIL: 6: отсутствие комментария не обнаружено\n' >&2
  exit 1
fi
grep -q 'bad.py' "$tmp/check-output"
((passed += 1))

mkdir -p "$tmp/dupes/nested"
printf 'same\n' > "$tmp/dupes/a.txt"
printf 'same\n' > "$tmp/dupes/nested/b.txt"
printf 'other\n' > "$tmp/dupes/c.txt"
actual=$(bash "$scripts/07-duplicates.sh" "$tmp/dupes")
[[ $actual == *'a.txt'* && $actual == *'b.txt'* && $actual != *'c.txt'* ]] || {
  printf 'FAIL: 7: неправильная группа дубликатов\n' >&2
  exit 1
}
((passed += 1))

mkdir "$tmp/archive"
printf 'A' > "$tmp/archive/a.txt"
printf 'B' > "$tmp/archive/b.txt"
printf 'C' > "$tmp/archive/c.md"
(cd "$tmp/archive" && bash "$scripts/08-archive-by-extension.sh" txt texts.tar > /dev/null)
actual=$(tar -tf "$tmp/archive/texts.tar" | LC_ALL=C sort)
assert_equal $'./a.txt\n./b.txt' "$actual" '8: архив файлов расширения txt'

printf 'a    b        c\n' > "$tmp/spaces.txt"
bash "$scripts/09-spaces-to-tabs.sh" "$tmp/spaces.txt" "$tmp/tabs.txt"
actual=$(< "$tmp/tabs.txt")
assert_equal $'a\tb\t\tc' "$actual" '9: замена четвёрок пробелов'

mkdir "$tmp/empty"
: > "$tmp/empty/one.txt"
: > "$tmp/empty/two.md"
: > "$tmp/empty/three.bin"
printf 'content' > "$tmp/empty/four.txt"
actual=$(bash "$scripts/10-empty-text-files.sh" "$tmp/empty")
assert_equal "$tmp/empty/one.txt"$'\n'"$tmp/empty/two.md" "$actual" '10: пустые текстовые файлы'

printf 'Успешно: %d проверок\n' "$passed"
