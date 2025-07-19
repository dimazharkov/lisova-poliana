import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract


class AddPersonalDataUseCase(UseCaseContract):
    def __init__(self, repository: RepositoryContract, anchor_col: str = "h1"):
        self.metadata = repository.all()
        self.anchor_col = anchor_col

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        merged = data.merge(self.metadata, left_on="person", right_on="person", how="left")

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
