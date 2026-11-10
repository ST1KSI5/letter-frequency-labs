"""Частотний аналіз літер. Варіант 7. Python 3.10+."""

import unicodedata
import argparse
import sys
from pathlib import Path

def count_letters(text):
    counts = {}
    for char in unicodedata.normalize("NFC", text).lower():
        if char.isalpha():
            counts[char] = counts.get(char, 0) + 1
    return dict(sorted(counts.items()))

def render_histogram(counts):
    if not counts:
        return "Літер не знайдено."
    max_count = max(counts.values())
    lines = ["Літера | Діаграма (максимум 50 символів) | Кількість"]
    for letter, count in sorted(counts.items()):
        width = max(1, (count * 50 + max_count // 2) // max_count)
        lines.append(f"{letter} {'#' * width} {count}")
    lines.append(f"Усього літер: {sum(counts.values())}; різних: {len(counts)}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Підрахунок літер і символьна діаграма частот.")
    parser.add_argument("--file", type=Path, help="Шлях до текстового файлу UTF-8")
    args = parser.parse_args(argv)
    try:
        text = args.file.read_text(encoding="utf-8-sig") if args.file else input("Введіть текст: ")
    except UnicodeError:
        print("Помилка: файл має бути збережений у UTF-8.", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Помилка читання файлу: {error.strerror or error}.", file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("Помилка: ввід перервано або текст не надано.", file=sys.stderr)
        return 2
    if not text.strip():
        print("Помилка: введіть непорожній текст із літерами.", file=sys.stderr)
        return 2
    counts = count_letters(text)
    if not counts:
        print("Помилка: текст не містить літер; цифри й розділові знаки не враховуються.", file=sys.stderr)
        return 2
    print(render_histogram(counts))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
