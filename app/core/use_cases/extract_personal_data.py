import pandas as pd

from app.core.contracts.extract_use_case_contract import ExtractUseCaseContract


class ExtractPersonalDataUseCase(ExtractUseCaseContract):
    def run(self, json_data: dict) -> pd.DataFrame:
        person_data = json_data["Військові"]
        selected_columns = ["col_5", "col_6", "col_9", "col_10", "col_11", "col_12", "col_13", "col_14",
                            "col_20", "col_29", "col_30", "col_33", "col_34", "col_35", "col_36",
                            "col_37", "col_38", "col_39"]

        column_rename_map = {
            "col_5": "last_name",
            "col_6": "first_name",
            "col_9": "gender",
            "col_10": "year_of_birth",
            "col_11": "age",
            "col_12": "height",
            "col_13": "weight",
            "col_14": "blood_pressure",
            "col_20": "complains",
            "col_29": "l5_sdnn_si",
            "col_30": "s3_sdnn_si",
            "col_33": "dass21",
            "col_34": "d",
            "col_35": "a",
            "col_36": "c",
            "col_37": "vein",
            "col_38": "ptsr",
            "col_39": "sleep"
        }

        data = pd.DataFrame([{k: row.get(k) for k in selected_columns} for row in person_data])
        data = data.rename(columns=column_rename_map)

        data["full_name"] = data["last_name"].str.strip() + " " + data["first_name"].str.strip()

        bp_split = data["blood_pressure"].str.extract(r"(?P<systolic>\d{2,3})\s*/\s*(?P<diastolic>\d{2,3})")
        data["systolic"] = pd.to_numeric(bp_split["systolic"], errors="coerce")
        data["diastolic"] = pd.to_numeric(bp_split["diastolic"], errors="coerce")

        sdnn_5l_split = data["l5_sdnn_si"].str.extract(r"(?P<l5_sdnn>\d{2,4})\s*/\s*(?P<l5_si>\d{2,4})")
        data["5l_sdnn"] = pd.to_numeric(sdnn_5l_split["l5_sdnn"], errors="coerce")
        data["5l_si"] = pd.to_numeric(sdnn_5l_split["l5_si"], errors="coerce")

        sdnn_s3_split = data["s3_sdnn_si"].str.extract(r"(?P<s3_sdnn>\d{2,4})\s*/\s*(?P<s3_si>\d{2,4})")
        data["s3_sdnn"] = pd.to_numeric(sdnn_s3_split["s3_sdnn"], errors="coerce")
        data["s3_si"] = pd.to_numeric(sdnn_s3_split["s3_si"], errors="coerce")

        number_cols = ["systolic", "diastolic", "5l_sdnn", "5l_si", "s3_sdnn", "s3_si", "dass21", "d", "a", "c",
                       "vein", "ptsr", "sleep"]

        def extract_before_after(group):
            result = {}

            # Поля с единичным значением (паспортные данные)
            single_value_fields = ["last_name", "first_name", "gender", "year_of_birth", "age", "height", "weight"]
            for col in single_value_fields:
                result[col] = group[col].dropna().iloc[0] if not group[col].dropna().empty else None

            # Конкатенация жалоб
            result["complains"] = ', '.join(group["complains"].dropna().unique())

            # Before/after поля

            for col in number_cols:
                before = pd.to_numeric(group[col].iloc[0], errors="coerce") if len(group) > 0 else None
                after = pd.to_numeric(group[col].iloc[-1], errors="coerce") if len(group) > 1 else None
                result[f"{col}_before"] = before
                result[f"{col}_after"] = after

            return pd.Series(result)

        data = data.groupby("full_name").apply(extract_before_after).reset_index()

        for col in number_cols:
            data[f"{col}_mean"] = data[[f"{col}_before", f"{col}_after"]].mean(axis=1)

        data = data[data["full_name"].fillna("").str.strip() != ""]

        return data
