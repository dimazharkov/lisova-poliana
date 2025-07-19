import pandas as pd

from app.repositories.data_repository import DataRepository


class PersonRepository(DataRepository):
    def all(self):
        if self.data is None:
            raise ValueError("Данные не загружены. Проверь source_path.")
        return self._prepare_data(self.data)

    def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        drop_cols = ["last_name", "first_name", "gender", "year_of_birth", "age", "complains"]
        metadata = data.drop(columns=drop_cols).copy()

        metadata["height"] = pd.to_numeric(metadata["height"], errors="coerce")
        metadata["weight"] = pd.to_numeric(metadata["weight"], errors="coerce")

        # BMI и overweight (если height и weight заданы)
        height_m = metadata["height"] / 100
        bmi = metadata["weight"] / (height_m ** 2)
        metadata["bmi"] = bmi

        metadata["overweight"] = pd.NA
        valid_bmi = bmi.notna()
        metadata.loc[valid_bmi, "overweight"] = (bmi[valid_bmi] >= 25).astype("Int64")

        # high_blood_pressure (если давление задано)
        systolic = metadata[["systolic_before", "systolic_after"]].copy()
        diastolic = metadata[["diastolic_before", "diastolic_after"]].copy()

        systolic_max = systolic.max(axis=1, skipna=True)
        diastolic_max = diastolic.max(axis=1, skipna=True)

        metadata["high_blood_pressure"] = pd.NA
        valid_bp = systolic_max.notna() & diastolic_max.notna()
        metadata.loc[valid_bp, "high_blood_pressure"] = (
            ((systolic_max > 140) | (diastolic_max > 90))[valid_bp]
        ).astype("Int64")

        # Приведение к Int64 (безопасное)
        metadata["height"] = metadata["height"].astype("Int64")
        metadata["weight"] = metadata["weight"].astype("Int64")

        # Переименование имени
        metadata = metadata.rename(columns={"full_name": "person"})

        return metadata
