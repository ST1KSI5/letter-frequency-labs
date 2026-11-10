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
    lines = ["Літера | Діаграма | Кількість"]
    for letter, count in sorted(counts.items()):
        bar = "#" * min(count, 60)
        if count > 60:
            bar += "…"
        lines.append(f"{letter} {bar} {count}")
    lines.append(f"Усього літер: {sum(counts.values())}; різних: {len(counts)}")
    if max(counts.values()) > 60:
        lines.append("Діаграми довші за 60 символів скорочено; кількості точні.")
    return "\n".join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Підрахунок літер і символьна діаграма частот.")
    parser.add_argument("--file", type=Path, help="Шлях до текстового файлу UTF-8")
    args = parser.parse_args(argv)
    text = args.file.read_text(encoding="utf-8-sig") if args.file else input("Введіть текст: ")
    print(render_histogram(count_letters(text)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
