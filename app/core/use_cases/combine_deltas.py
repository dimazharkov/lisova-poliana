from functools import reduce

import pandas as pd


class CombineDeltasUseCase:
    def run(self, data: list[pd.DataFrame]) -> pd.DataFrame:
        # общее множество колонок во всех фреймах
        common_cols_set = reduce(lambda x, y: x & y, (set(df.columns) for df in data))

        # Возьмём порядок колонок из первого датафрейма
        first_df_cols = [col for col in data[0].columns if col in common_cols_set]

        # ggреобразуем все фреймы к этим колонкам и объединяем
        combined_df = pd.concat([df[first_df_cols] for df in data], ignore_index=True)

        return combined_df
