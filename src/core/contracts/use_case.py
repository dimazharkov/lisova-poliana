from abc import ABC, abstractmethod
from typing import Protocol, Optional, Any, runtime_checkable


# @runtime_checkable
class DataUseCase(ABC):
    @abstractmethod
    def run(self, data: Any) -> Optional[Any]:
        pass

# @runtime_checkable
class NoInputUseCase(ABC):
    @abstractmethod
    def run(self) -> Optional[Any]:
        pass