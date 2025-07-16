import re
from typing import Optional


def clear_person_text(value: str) -> Optional[str]:
    if not isinstance(value, str):
        return None

    parts = value.strip().split()

    cleaned = []
    for part in parts:
        # Удаляем мусор вроде "001", "001-", "-001", "001-Остап"
        core = re.sub(r"^[\d\-_]+|[\d\-_]+$", "", part)
        # Пропускаем слишком короткие или пустые слова после очистки
        if len(core) > 1 and not re.fullmatch(r"\d+", core):
            cleaned.append(core)

    if len(cleaned) >= 2:
        return " ".join(cleaned[:2])
    return None
