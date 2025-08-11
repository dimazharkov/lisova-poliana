from typing import Protocol, List


class ColumnListFilterContract(Protocol):
    def filter(self, columns: List[str]) -> List[str]: ...
