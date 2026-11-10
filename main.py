"""Частотний аналіз літер. Варіант 7. Python 3.10+."""

import unicodedata

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

def main():
    text = input("Введіть текст: ")
    print(render_histogram(count_letters(text)))

if __name__ == "__main__":
    main()
