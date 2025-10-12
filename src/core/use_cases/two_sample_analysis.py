from dataclasses import asdict
from typing import Optional

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from src.core.contracts.filter import DataFrameFilterContract
from src.core.contracts.repository import ExperimentRepositoryContract
from src.core.contracts.stat_calculator import StatCalculatorContract
from src.core.contracts.use_case import DataUseCase
from src.infra.helpers.dot_dict import DotDict


class TwoSampleAnalysisUC(DataUseCase):
    def __init__(
            self,
            stat_calculator: StatCalculatorContract,
            df_filter: DataFrameFilterContract,
            repository: ExperimentRepositoryContract,
            hue_field: str,
            effect_field: str,
            stratify_fields: Optional[list[str]] = None,
            index_fields: Optional[list[str]] = None,
            experiment_config: Optional[dict] = None,
            test_method: str = "t"
    ):
        self.stat_calculator = stat_calculator
        self.df_filter = df_filter
        self.repository = repository
        self.hue_field = hue_field
        self.effect_field = effect_field
        self.stratify_fields = stratify_fields
        self.index_fields = index_fields
        self.cfg = DotDict(experiment_config if experiment_config else {})
        self.test_method = test_method

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        # print("run, type(data) = ", type(data))
        df = self.df_filter.filter(
            data.copy()
        )

        result_data = {}
        result_figs = {}

        stats, figs = self.run_aggregated(df)
        result_data.update(stats)
        result_figs.update(figs)

        if self.stratify_fields:
            for strat_field in self.stratify_fields:
                stats, figs = self.run_stratified(df, strat_field)
                result_data.update(stats)
                result_figs.update(figs)

        self.repository.save(result_data, result_figs)

        return data

    def run_aggregated(self, data: pd.DataFrame) -> tuple[dict, dict]:
        key = "aggregated"
        stats, figures = {}, {}
        config = self.cfg.aggregated

        g0 = self.prep_series(data, hue_value=0)
        g1 = self.prep_series(data, hue_value=1)

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

    def run_stratified(self, data: pd.DataFrame, strat_field: str) -> tuple[dict, dict]:
        stats, figures = {}, {}
        config = self.cfg.stratified[strat_field]

        # 1) Готовим данные для графика и сразу считаем статистику
        frames = []
        for val in data[strat_field].dropna().unique():
            subset = data[data[strat_field] == val]

            g0 = self.prep_series(subset, hue_value=0)
            g1 = self.prep_series(subset, hue_value=1)
            # if strat_field == "nsi_exceeded" and val == 0:
            #     print("g0 = ", g0)
            #     print("g1 = ", g1)
            # для статистики — используем ровно эти же серии
            stats[f"{strat_field}_{int(val)}"] = asdict(self.stat_calculator.calculate(
                g0, g1, method=self.test_method
            ))

            # для графика — собираем cleaned long-данные
            f0 = g0.to_frame(name=self.effect_field).assign(**{self.hue_field: 0, strat_field: val})
            f1 = g1.to_frame(name=self.effect_field).assign(**{self.hue_field: 1, strat_field: val})
            frames.extend([f0, f1])

        df_plot = pd.concat(frames, ignore_index=True)
        # на всякий случай убедимся в численном типе
        df_plot[self.effect_field] = pd.to_numeric(df_plot[self.effect_field], errors="coerce")

        # 2) Строим график по подготовленным данным
        fig = plt.figure(figsize=(6, 4))
        ax = sns.boxplot(
            data=df_plot,
            x=strat_field,
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
        legend = plt.legend()
        legend.get_texts()[0].set_text(config.labels.before)
        legend.get_texts()[1].set_text(config.labels.after)
        plt.tight_layout()
        figures[strat_field] = fig

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
