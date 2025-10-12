import pandas as pd
from sklearn.preprocessing import RobustScaler, MinMaxScaler, StandardScaler, MaxAbsScaler, QuantileTransformer

from src.core.contracts.filter import StringListFilterContract
from src.core.contracts.use_case import DataUseCase


class NormalizeDataUC(DataUseCase):
    def __init__(self, column_filter: StringListFilterContract, scallers: list[str] | None = None):
        self.column_filter = column_filter
        self.scallers: list[str] = scallers or ["robust", "minmax"]

    def _make_scaler(self, name: str):
        n = name.lower()
        if n == "robust":
            return RobustScaler()
        if n == "minmax":
            return MinMaxScaler()
        if n == "standard":
            return StandardScaler()
        if n == "maxabs":
            return MaxAbsScaler()
        if n == "quantile_normal":
            # преобразует ранги к нормальному распределению
            return QuantileTransformer(output_distribution="normal", copy=True)
        raise ValueError(f"Unknown scaler: {name!r}. Allowed: robust, minmax, standard, maxabs, quantile_normal")

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self.scallers:
            return data.copy()

        df = data.copy()

        # 1) колонки по фильтру; если фильтр пуст — все числовые
        target_columns = list(self.column_filter.filter(list(df.columns)))
        if not target_columns:
            target_columns = df.select_dtypes(include="number").columns.tolist()
        if not target_columns:
            return df  # нет числовых колонок — ничего не делаем

        # 2) исключаем из скейлинга те, где все значения NaN
        cols_all_nan = [c for c in target_columns if df[c].isna().all()]
        cols_to_scale = [c for c in target_columns if c not in cols_all_nan]
        if not cols_to_scale:
            return df

        # 3) приводим к числовому типу (object → float, где возможно)
        df[cols_to_scale] = (
            df[cols_to_scale]
            .apply(pd.to_numeric, errors="coerce")  # если вдруг object/строки
            .astype("float64")  # финальный dtype
        )

        # 4) последовательное применение скейлеров
        x = df[cols_to_scale].to_numpy(dtype=float, copy=False)
        for name in self.scallers:
            scaler = self._make_scaler(name)
            x = scaler.fit_transform(x)

        # 5) записываем назад через DataFrame
        df.loc[:, cols_to_scale] = pd.DataFrame(x, index=df.index, columns=cols_to_scale)

        # колонки, где все NaN, остаются без изменений
        return df

    # def run(self, data: pd.DataFrame) -> pd.DataFrame:
    #     if not self.scallers:
    #         return data.copy()
    #
    #     df = data.copy()
    #     target_columns = list(self.column_filter.filter(list(df.columns)))
    #     if not target_columns:
    #         target_columns = df.select_dtypes(include="number").columns.tolist()
    #         if not target_columns:
    #             return df  # нет числовых колонок — ничего не делаем
    #
    #     x = df[target_columns].to_numpy(dtype=float, copy=False)
    #     for name in self.scallers:
    #         scaler = self._make_scaler(name)
    #         x = scaler.fit_transform(x)
    #
    #     df.loc[:, target_columns] = x
    #     return df
