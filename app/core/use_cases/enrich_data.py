import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract


class EnrichDataUseCase(UseCaseContract):
    def __init__(self, metadata_repository: RepositoryContract, treatment: int = 0):
        super().__init__()
        self.metadata = metadata_repository.all()
        self.treatment = treatment

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["experiment_date"] = pd.to_datetime(data["experiment_date"], dayfirst=True, errors="coerce")

        group_fields = ["person", "sex", "dob", "age", "category", "experiment"]

        data.insert(
            loc=data.columns.get_loc("experiment") + 1,
            column="repeat",
            value=(
                data.sort_values("experiment_date")
                .groupby(group_fields)
                .cumcount()
            )
        )

        data.insert(
            data.columns.get_loc("repeat") + 1, "treatment", self.treatment
        )
        data = data[data["repeat"] <= 1]

        metadata = self._prep_metadata(self.metadata)
        merged = data.merge(metadata, left_on="person", right_on="full_name", how="left")
        merged = merged.drop(columns=["full_name"])

        new_fields = [col for col in merged.columns if col not in data.columns]

        cols = list(merged.columns)
        insert_idx = cols.index("experiment_date") + 1

        for field in new_fields:
            cols.remove(field)
        for field in reversed(new_fields):
            cols.insert(insert_idx, field)

        merged = merged[cols]

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