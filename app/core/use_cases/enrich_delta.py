import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract


class EnrichDeltaUseCase(UseCaseContract):
    def __init__(self, metadata_repository: RepositoryContract):
        super().__init__()
        self.metadata = metadata_repository.all()

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        metadata = self._prep_metadata(self.metadata)

        merged = data.merge(metadata, left_on="person", right_on="full_name", how="left")
        merged = merged.drop(columns=["full_name"])

        new_fields = [col for col in merged.columns if col not in data.columns]

        cols = list(merged.columns)
        insert_idx = cols.index("date_after") + 1

        for field in new_fields:
            cols.remove(field)
        for field in reversed(new_fields):
            cols.insert(insert_idx, field)

        merged = merged[cols]

        norm_cols = [col for col in merged.columns if col.endswith('_norm')]
        merged["median_effect"] = merged[norm_cols].median(axis=1)

        return merged

    def _prep_metadata(self, metadata: pd.DataFrame) -> pd.DataFrame:
        drop_cols = ["last_name", "first_name", "gender", "year_of_birth", "age", "complains"]
        metadata = metadata.drop(columns=drop_cols)

        metadata["height"] = pd.to_numeric(metadata["height"], errors="coerce").astype("Int64")
        metadata["weight"] = pd.to_numeric(metadata["weight"], errors="coerce").astype("Int64")

        metadata["high_blood_pressure"] = (
            metadata[["systolic_before", "systolic_after"]].max(axis=1) > 140
        ) | (
            metadata[["diastolic_before", "diastolic_after"]].max(axis=1) > 90
        )

        metadata["high_blood_pressure"] = pd.to_numeric(metadata["high_blood_pressure"], errors="coerce").astype("Int64")

        return metadata