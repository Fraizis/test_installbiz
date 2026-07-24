"""Подсчёт цифр в тексте файла."""

from pathlib import Path


def count_digits(text: str) -> dict[str, int]:
    """Подсчитать цифры в тексте."""
    counts = {str(d): 0 for d in range(10)}
    for ch in text:
        if ch in counts:
            counts[ch] += 1
    return counts


def count_digits_in_file(path: Path) -> dict[str, int]:
    """Прочитать файл как UTF-8 и вернуть счётчики цифр."""
    content = path.read_text(encoding="utf-8")
    return count_digits(content)


def merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    """Сложить два словаря цифр."""
    for digit, value in source.items():
        target[digit] = target.get(digit, 0) + value



