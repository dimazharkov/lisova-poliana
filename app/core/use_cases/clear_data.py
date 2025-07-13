from datetime import datetime

import numpy as np
import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract
from app.core.utils.text_utils import clear_person_text


class ClearDataUseCase(UseCaseContract):
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        h151_map = {
            "Відсутні": 0,
            "Незначні": 1,
            "Помірні": 2,
            "Значні": 3
        }

        data["h151"] = data["h151"].map(h151_map)

        experiment_map = {
            '3 хв сидячи': 3,
            '5 хв лежачи': 5,
            '5л п': 5,
            '3с п': 3,
            '5лп': 5,
            '3сп': 3
        }
        data["experiment"] = data["experiment"].map(experiment_map)

        sex_map = {
            'Чоловіча': 'm',
            'Жіноча': 'f'
        }
        data["sex"] = data["sex"].map(sex_map)

        data["person"] = data["person"].apply(clear_person_text)

        # 2. Оставить только дату (без времени) в 'experiment_date'
        data["experiment_date"] = data["experiment_date"].astype(str).str.strip().str.split().str[0]

        current_year = datetime.now().year

        data.insert(
            data.columns.get_loc("dob") + 1, "age",
            (current_year - pd.to_datetime(data["dob"], errors="coerce", dayfirst=True).dt.year)
        )

        # 3. Найти колонки, где хранятся параметры (все кроме служебных)
        meta_cols = ["person", "sex", "dob", "category", "experiment", "experiment_date"]
        param_cols = [col for col in data.columns if col not in meta_cols]

        # 4. Очистка значений параметров
        for col in param_cols:
            data[col] = pd.to_numeric(
                data[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace(r"[^\d\.\-]", "", regex=True)
                .replace(["", "-", "nan"], np.nan),
                errors="coerce"
            )

        return data
