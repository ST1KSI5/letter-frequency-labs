"""Частотний аналіз літер. Варіант 7. Python 3.10+."""

import unicodedata

def count_letters(text):
    counts = {}
    for char in unicodedata.normalize("NFC", text).lower():
        if char.isalpha():
            counts[char] = counts.get(char, 0) + 1
    return dict(sorted(counts.items()))

def main():
    text = input("Введіть текст: ")
    print(count_letters(text))

if __name__ == "__main__":
    main()
