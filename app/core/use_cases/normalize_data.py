from sklearn.preprocessing import RobustScaler, MinMaxScaler
import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract


class NormalizeDataUseCase(UseCaseContract):
    def run(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        param_cols = [col for col in data.columns if col.startswith("h")]

        robust_scaler = RobustScaler()
        robust_scaled = robust_scaler.fit_transform(data[param_cols])

        minmax_scaler = MinMaxScaler()
        final_scaled = minmax_scaler.fit_transform(robust_scaled)

        for i, col in enumerate(param_cols):
            data[f"{col}_norm"] = final_scaled[:, i]

        norm_cols = [f"{col}_norm" for col in param_cols]
        data["median_effect"] = data[norm_cols].median(axis=1)

        return data
