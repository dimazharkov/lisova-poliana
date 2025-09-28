from typing import Protocol, List


class ColumnListFilter(Protocol):
    def filter(self, columns: List[str]) -> List[str]: ...