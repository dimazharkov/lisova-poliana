import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract


class SetupRepeatAndTreatmentUseCase(UseCaseContract):
    def __init__(self, treatment: int = 0):
        super().__init__()
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

        data = data[data["repeat"] <= 1]

        # удаляем строки, где все h*-колонки пустые
        h_cols = data.filter(regex=r"^h\d+$").columns
        data = data.dropna(subset=h_cols, how="all")

        # оставляем только если есть точно две строки repeat=0 и repeat=1
        data = data.groupby(group_fields, as_index=False).filter(
            lambda g: len(g) == 2 and set(g["repeat"]) == {0, 1}
        ).reset_index(drop=True)

        data.insert(
            data.columns.get_loc("repeat") + 1,
            "treatment",
            self.treatment
        )

        # print("add_treatment_data")
        # print(data["h155"].unique())

        return data
