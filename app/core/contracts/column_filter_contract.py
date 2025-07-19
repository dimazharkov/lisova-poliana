from typing import Protocol, List


class ColumnFilterContract(Protocol):
    def filter(self, columns: List[str]) -> List[str]: ...
