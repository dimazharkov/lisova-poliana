import re
from typing import List, Optional

from app.infra.filters.column_list_filter import ColumnListFilter as ColumnListFilterContract


class ColumnListFilter(ColumnListFilterContract):
    r"""
    Filters a list of column names using regex-based includes and explicit excludes.

    include_patterns: List of regex patterns used to select columns.
                             Example: [r"h\d+", r"bp_.*"].
                             Patterns use Python's `re` syntax and are case-sensitive
                             by default.
    exclude_fields:   List of exact column names to drop after inclusion.
                             Example: ["h13", "bp_debug"].
    """
    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ):
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
