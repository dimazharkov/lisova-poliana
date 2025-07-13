import pandas as pd


class CombineDeltasUseCase:
    def run(self, data: list[pd.DataFrame]) -> pd.DataFrame:
        return pd.concat(data)