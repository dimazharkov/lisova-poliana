import pandas as pd

from src.infra.repositories.data_file_repository import DataFileRepository


class IndicatorsData(DataFileRepository):
    def read(self):
        if self.data is None:
            raise ValueError("Данные не загружены. Проверь source_path.")
        return self._prepare_data(self.data)

    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        drop_cols = ["last_name", "first_name"]
        metadata = data.drop(columns=drop_cols).copy()

        metadata = metadata.dropna(subset=["pcl_avg", "nsi_avg"], how="all")

        metadata["pcl_exceeded"] = (metadata["pcl_avg"] >= 36).astype("Int64")
        metadata["nsi_exceeded"] = (metadata["nsi_avg"] >= 25).astype("Int64")

        metadata = metadata.rename(columns={"full_name": "person"})

        return metadata


