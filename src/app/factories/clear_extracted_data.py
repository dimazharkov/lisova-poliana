from dependency_injector import containers

from src.app.use_cases.clear_extracted_data import ClearExtractedDataUC


class ClearExtractedDataFactory:
    Schema = None

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: None = None) -> ClearExtractedDataUC:
        return container.clear_extracted_data_uc()