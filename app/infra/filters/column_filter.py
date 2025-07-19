import re
from typing import List, Optional

from app.core.contracts.column_filter_contract import ColumnFilterContract


class ColumnFilter(ColumnFilterContract):
    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,  # теперь это regex-паттерны
        exclude_fields: Optional[List[str]] = None,
    ):
        r"""
        :param include_patterns: список regex-паттернов, по которым выбирать колонки
                                 Пример: [r"h\d+", r"bp_.*"]
        :param exclude_fields: список точных имён колонок, которые нужно исключить
        """
        self.include_patterns = include_patterns
        self.exclude_fields = exclude_fields

    def filter(self, columns: List[str]) -> List[str]:
        if not self.include_patterns:
            matched = set(columns)
        else:
            matched = set()
            for pattern in self.include_patterns:
                regex = re.compile(pattern)
                matched.update(col for col in columns if regex.fullmatch(col))

        if self.exclude_fields:
            matched = [col for col in matched if col not in self.exclude_fields]
        else:
            matched = list(matched)

        return matched
