import pandas as pd

from src.core.contracts.repository import DataFileRepositoryContract
from src.core.contracts.use_case import DataUseCase


class AddPersonalDataUC(DataUseCase):
    def __init__(self, personal_repo: DataFileRepositoryContract, merge_column: str = "person", anchor_column: str = "h1"):
        self.metadata = personal_repo.read()
        self.merge_col = merge_column
        self.anchor_col = anchor_column

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

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
