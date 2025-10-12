import pandas as pd

from src.core.contracts.repository import DataFileRepositoryContract
from src.core.contracts.use_case import DataUseCase

# def first_non_null(s: pd.Series):
#     for v in s:
#         if pd.notna(v):
#             return v
#     return None

class AddPersonalIndicatorsUC(DataUseCase):
    def __init__(self, indicators_repo: DataFileRepositoryContract, merge_column: str = "person", anchor_column: str = "h1"):
        self.metadata = indicators_repo.read()
        self.merge_col = merge_column
        self.anchor_col = anchor_column

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        # self.metadata = self.prepare_metadata_for_merge()

        metadata_cols = set(self.metadata.columns) - {self.merge_col}
        overlap_cols = metadata_cols & set(data.columns)
        data = data.drop(columns=overlap_cols)

        merged = data.merge(self.metadata, on=self.merge_col, how="left")

        new_fields = [col for col in merged.columns if col not in data.columns]

        cols = list(merged.columns)
        anchor_candidates = [self.anchor_col]
        existing_anchors = [col for col in anchor_candidates if col in cols]

        if not existing_anchors:
            insert_idx = len(cols)
        else:
            insert_idx = min(merged.columns.get_loc(col) for col in existing_anchors)

        for field in new_fields:
            cols.remove(field)

        for field in reversed(new_fields):
            cols.insert(insert_idx, field)

        merged = merged[cols]

        return merged

    # def prepare_metadata_for_merge(self, key: str = "person") -> pd.DataFrame:
    #     m = self.metadata.copy()
    #
    #     m.drop(columns=["last_name", "first_name"], errors="ignore", inplace=True)
    #
    #     if key not in m.columns:
    #         if "full_name" in m.columns:
    #             m.rename(columns={"full_name": key}, inplace=True)
    #         else:
    #             raise KeyError(
    #                 f"Merge key {key!r} not found in metadata (and no 'full_name' to derive it)."
    #             )
    #
    #     non_key = [c for c in m.columns if c != key]
    #     coerced = m[non_key].apply(pd.to_numeric, errors="coerce")  # строковые числа → float/NaN
    #     num_cols = coerced.select_dtypes(include="number").columns
    #     if len(num_cols) > 0:
    #         m[num_cols] = coerced[num_cols]
    #
    #     other_cols = [c for c in non_key if c not in num_cols]
    #
    #     # агрегировать дубликаты по ключу:
    #     # числа → mean (NaN игнорируются), текст/прочее → первое ненулевое
    #     agg = {**{c: "mean" for c in num_cols}, **{c: first_non_null for c in other_cols}}
    #     m = m.groupby(key, as_index=False).agg(agg)
    #
    #     return m