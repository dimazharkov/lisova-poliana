from typing import TypeVar, runtime_checkable, Protocol

FileRepositoryDataType = TypeVar("FileRepositoryDataType")

@runtime_checkable
class FileRepository(Protocol[FileRepositoryDataType]):
    def read(self) -> FileRepositoryDataType: ...
    def write(self, data: FileRepositoryDataType) -> None: ...