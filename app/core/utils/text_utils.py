import re
from typing import Optional


def clear_person_text(self, value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None
    # trim
    parts = value.strip().split()

    # очистить каждый элемент от цифр, "-", "_" в начале и в конце
    cleaned = [
        re.sub(r"^[\d\-_]+|[\d\-_]+$", "", part)
        for part in parts
    ]

    # оставить только слова длиной > 1 после очистки
    cleaned = [part for part in cleaned if len(part) > 1]

    if len(cleaned) >= 2:
        return " ".join(cleaned[:2])  # имя и фамилия
    return None
