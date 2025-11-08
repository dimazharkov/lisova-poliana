from dataclasses import asdict
from typing import Optional, Sequence

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from src.core.contracts.repository import ExperimentRepositoryContract
from src.core.contracts.stat_calculator import StatCalculatorContract
from src.core.contracts.use_case import DataUseCase
from src.infra.helpers.dot_dict import DotDict


class CheckControlGroupUC(DataUseCase):
    def __init__(
            self,
            stat_calculator: StatCalculatorContract,
            repository: ExperimentRepositoryContract,
            hue_field: str,
            effect_field: str,
            index_fields: Optional[list[str]] = None,
            experiment_config: Optional[dict] = None,
            test_method: str = "t"
    ):
        self.stat_calculator = stat_calculator
        self.repository = repository
        self.hue_field = hue_field
        self.effect_field = effect_field
        self.index_fields = index_fields
        self.cfg = DotDict(experiment_config if experiment_config else {})
        self.test_method = test_method

    def run(self, data: Sequence[pd.DataFrame]) -> Sequence[pd.DataFrame]:
        experiment_group = data[0].copy()
        control_group = data[1].copy()

        result_data = {}
        result_figs = {}

        stats, figs = self.run_aggregated(experiment_group, control_group)
        result_data.update(stats)
        result_figs.update(figs)

        self.repository.save(result_data, result_figs)

        return data

    def run_aggregated(self, experiment_data: pd.DataFrame, control_data: pd.DataFrame) -> tuple[dict, dict]:
        key = "aggregated"
        stats, figures = {}, {}
        config = self.cfg.aggregated

        g0 = self.prep_series(experiment_data, hue_value=0)
        g1 = self.prep_series(control_data, hue_value=0)

        stats[key] = asdict(self.stat_calculator.calculate(
            g0, g1, method=self.test_method
        ))

        df_plot = (
            pd.concat([
                g0.to_frame(name=self.effect_field).assign(**{self.hue_field: 0}),
                g1.to_frame(name=self.effect_field).assign(**{self.hue_field: 1})
            ])
        )

        fig = plt.figure(figsize=(6, 4))
        sns.boxplot(
            data=df_plot,
            x=self.hue_field,
            y=self.effect_field,
            hue=self.hue_field,
            palette="Set2",
            showfliers=False,
            width=0.2
        )
        plt.title(f"{config.title}")
        plt.xlabel("")
        plt.ylabel(config.ylabel)
        plt.xticks([0, 1], config.xticks)
        plt.tight_layout()
        figures[key] = fig
        return stats, figures

    def prep_series(self, data: pd.DataFrame, hue_value: int) -> pd.Series:
        """
        Возвращает Series значений effect_field,
        индексированных по index_fields (если заданы).
        """
        df = data[data[self.hue_field].astype(int) == hue_value].copy()
        df = df.dropna(subset=[self.effect_field])

        if not self.index_fields:
            # независимый сценарий — обычная серия без ключа
            return df[self.effect_field].astype(float)

        # парный сценарий — задаём индекс из index_fields
        s = df.set_index(self.index_fields)[self.effect_field].astype(float)

        return s
