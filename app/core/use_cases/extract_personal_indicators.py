import pandas as pd

from app.core.contracts.extract_use_case_contract import ExtractUseCaseContract


class ExtractPersonalIndicatorsUseCase(ExtractUseCaseContract):
    def run(self, json_data: dict) -> pd.DataFrame:
        person_data = json_data["виписки"][1:]
        selected_columns = ["col_4", "col_5", "col_12", "col_13", "col_14", "col_15"]

        column_rename_map = {
            "col_4": "last_name",
            "col_5": "first_name",
            "col_12": "pcl_in",
            "col_13": "pcl_out",
            "col_14": "nsi_in",
            "col_15": "nsi_out"
        }

        data = pd.DataFrame([{k: row.get(k) for k in selected_columns} for row in person_data])
        data = data.rename(columns=column_rename_map)

        data["full_name"] = data["last_name"].str.strip() + " " + data["first_name"].str.strip()

        numeric_cols = ["pcl_in", "pcl_out", "nsi_in", "nsi_out"]
        data[numeric_cols] = (
            data[numeric_cols]
            .replace(["-", ""], pd.NA)
            .astype("Float64")
        )

        data["pcl_avg"] = data[["pcl_in", "pcl_out"]].mean(axis=1)
        data["nsi_avg"] = data[["nsi_in", "nsi_out"]].mean(axis=1)

        data = data[data["full_name"].fillna("").str.strip() != ""]

        return data
