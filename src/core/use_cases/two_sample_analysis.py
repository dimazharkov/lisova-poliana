from dataclasses import asdict
from typing import Optional, overload, Sequence, Union

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from src.core.contracts.filter import DataFrameFilterContract
from src.core.contracts.repository import ExperimentRepositoryContract
from src.core.contracts.stat_calculator import StatCalculatorContract
from src.core.contracts.use_case import DataUseCase
from src.infra.helpers.dot_dict import DotDict

DataLike = Union[pd.DataFrame, Sequence[pd.DataFrame]]

class TwoSampleAnalysisUC(DataUseCase):
    def __init__(
            self,
            stat_calculator: StatCalculatorContract,
            df_filter: DataFrameFilterContract,
            repository: ExperimentRepositoryContract,
            effect_field: str,
            hue_field: Optional[str] = None,
            hue_values: Optional[Sequence[Union[int, str]]] = (0, 1),
            stratify_fields: Optional[list[str]] = None,
            index_fields: Optional[list[str]] = None,
            experiment_config: Optional[dict] = None,
            test_method: str = "t"
    ):
        self.stat_calculator = stat_calculator
        self.df_filter = df_filter
        self.repository = repository
        self.hue_field = hue_field
        self.hue_values = list(hue_values) if hue_values is not None else None
        self.effect_field = effect_field
        self.stratify_fields = stratify_fields
        self.index_fields = index_fields
        self.cfg = DotDict(experiment_config if experiment_config else {})
        self.test_method = test_method

    @overload
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        ...

    @overload
    def run(self, data: Sequence[pd.DataFrame]) -> Sequence[pd.DataFrame]:
        ...

    def run(self, data: DataLike) -> DataLike:
        if isinstance(data, pd.DataFrame):
            if not self.hue_field:
                raise ValueError("For a single DataFrame, hue_field must be specified.")
            if not self.hue_values or len(self.hue_values) != 2:
                raise ValueError("For a single DataFrame, hue_values must contain exactly two values.")
            hue_value0, hue_value1 = self.hue_values
            df = self.df_filter.filter(data.copy())
            df0 = df[df[self.hue_field] == hue_value0].copy()
            df1 = df[df[self.hue_field] == hue_value1].copy()
        elif (
                isinstance(data, list)
                and len(data) == 2
                and all(isinstance(x, pd.DataFrame) for x in data)
        ):
            df0 = self.df_filter.filter(data[0].copy())
            df1 = self.df_filter.filter(data[1].copy())
        else:
            raise ValueError("Data must be a pd.DataFrame or a tuple of two pd.DataFrame.")

        result_data = {}
        result_figs = {}

        stats, figs = self.run_aggregated(df0, df1)
        result_data.update(stats)
        result_figs.update(figs)

        if self.stratify_fields:
            for strat_field in self.stratify_fields:
                stats, figs = self.run_stratified(df0, df1, strat_field)
                result_data.update(stats)
                result_figs.update(figs)

        self.repository.save(result_data, result_figs)

        return data

    def run_aggregated(self, df0: pd.DataFrame, df1: pd.DataFrame) -> tuple[dict, dict]:
        key = "aggregated"
        stats, figures = {}, {}
        config = self.cfg.aggregated

        g0 = self.prep_series(df0)
        g1 = self.prep_series(df1)

        stats[key] = asdict(self.stat_calculator.calculate(
            g0, g1, method=self.test_method
        ))

        hue_field = "__hue"

        df_plot = (
            pd.concat([
                g0.to_frame(name=self.effect_field).assign(**{hue_field: 0}),
                g1.to_frame(name=self.effect_field).assign(**{hue_field: 1})
            ])
        )

        fig = plt.figure(figsize=(6, 4))
        sns.boxplot(
            data=df_plot,
            x=hue_field,
            y=self.effect_field,
            hue=hue_field,
            palette="Set2",
            showfliers=False,
            width=0.2
        )
        plt.title(f"{config.title}")
        plt.xlabel("")
        plt.ylabel(config.ylabel)
        plt.xticks([0, 1], config.xticks)
        if "labels" in config:
            legend = plt.legend()
            legend.get_texts()[0].set_text(config.labels.before)
            legend.get_texts()[1].set_text(config.labels.after)
        else:
            plt.legend().set_visible(False)
        plt.tight_layout()
        figures[key] = fig
        return stats, figures

    def run_stratified(self, df0: pd.DataFrame, df1: pd.DataFrame, strat_field: str) -> tuple[dict, dict]:
        stats, figures = {}, {}
        config = self.cfg.stratified[strat_field]

        strat_field_values = df0[strat_field].dropna().unique()

        # 1) Готовим данные для графика и сразу считаем статистику
        frames = []
        for val in strat_field_values:
            sub0 = df0[df0[strat_field] == val].copy()
            g0 = self.prep_series(sub0)

            sub1 = df1[df1[strat_field] == val].copy()
            g1 = self.prep_series(sub1)

            # для статистики — используем ровно эти же серии
            stats[f"{strat_field}_{int(val)}"] = asdict(self.stat_calculator.calculate(
                g0, g1, method=self.test_method
            ))

            hue_field = "__hue"

            # для графика — собираем cleaned long-данные
            f0 = g0.to_frame(name=self.effect_field).assign(**{hue_field: 0, strat_field: val})
            f1 = g1.to_frame(name=self.effect_field).assign(**{hue_field: 1, strat_field: val})
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
            hue=hue_field,
            palette="Set2",
            showfliers=False,
            width=0.2
        )
        plt.title(f"{config.title}")
        plt.xlabel("")
        plt.ylabel(config.ylabel)
        plt.xticks([0, 1], config.xticks)
        if "labels" in config:
            legend = plt.legend()
            legend.get_texts()[0].set_text(config.labels.before)
            legend.get_texts()[1].set_text(config.labels.after)
        else:
            plt.legend().set_visible(False)
        # legend = plt.legend()
        # legend.get_texts()[0].set_text(config.labels.before)
        # legend.get_texts()[1].set_text(config.labels.after)
        plt.tight_layout()
        figures[strat_field] = fig

        return stats, figures

    def prep_series(self, data: pd.DataFrame) -> pd.Series:
        """
        Возвращает Series значений effect_field,
        индексированных по index_fields (если заданы).
        """
        df = data.copy()
        df = df.dropna(subset=[self.effect_field])

        if not self.index_fields:
            # независимый сценарий — обычная серия без ключа
            return df[self.effect_field].astype(float)

        # парный сценарий — задаём индекс из index_fields
        s = df.set_index(self.index_fields)[self.effect_field].astype(float)

        return s
