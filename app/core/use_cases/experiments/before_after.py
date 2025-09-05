from dataclasses import asdict
from typing import Optional

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from app.core.contracts.config_provider_contract import ConfigProviderContract
from app.core.contracts.experiment_use_case_contract import ExperimentUseCaseContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.experiment_result import ExperimentResultDTO


class BeforeAfterExperimentUseCase(ExperimentUseCaseContract):
    def __init__(
            self,
            stat_evaluator: StatEvaluatorContract,
            experiment_config: ConfigProviderContract,
            hue_field: str,
            grouping_fields: Optional[list[str]] = None,
            effect_field: str = "median_effect",
            index_fields: Optional[list[str]] = None
    ):
        self.stat_evaluator = stat_evaluator
        self.experiment_config = experiment_config
        self.hue_field = hue_field
        self.grouping_fields = grouping_fields
        self.effect_field = effect_field
        self.index_fields = index_fields

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:
        result_data = {}
        result_figs = {}

        stats, figs = self.run_overall(data)
        result_data.update(stats)
        result_figs.update(figs)

        if self.grouping_fields:
            for grouping_field in self.grouping_fields:
                stats, figs = self.run_grouping(data, grouping_field)
                result_data.update(stats)
                result_figs.update(figs)

        return ExperimentResultDTO(
            data=result_data,
            figures=result_figs
        )

    def run_overall(self, data: pd.DataFrame) -> tuple[dict, dict]:
        key = "overall"
        stats, figures = {}, {}
        config = self.experiment_config.overall

        # g0 = data[data[self.hue_field].astype(int) == 0][self.effect_field]
        # g1 = data[data[self.hue_field].astype(int) == 1][self.effect_field]
        g0 = self.prep_series(data, hue_value=0)
        g1 = self.prep_series(data, hue_value=1)

        stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

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

    def run_grouping(self, data: pd.DataFrame, grouping_field: str) -> tuple[dict, dict]:
        stats, figures = {}, {}
        config = self.experiment_config.groupings[grouping_field]

        # 1) Готовим данные для графика и сразу считаем статистику
        frames = []
        for val in data[grouping_field].dropna().unique():
            subset = data[data[grouping_field] == val]

            g0 = self.prep_series(subset, hue_value=0)
            g1 = self.prep_series(subset, hue_value=1)

            # для статистики — используем ровно эти же серии
            stats[f"{grouping_field}_{val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

            # для графика — собираем cleaned long-данные
            f0 = g0.to_frame(name=self.effect_field).assign(**{self.hue_field: 0, grouping_field: val})
            f1 = g1.to_frame(name=self.effect_field).assign(**{self.hue_field: 1, grouping_field: val})
            frames.extend([f0, f1])

        df_plot = pd.concat(frames, ignore_index=True)
        # на всякий случай убедимся в численном типе
        df_plot[self.effect_field] = pd.to_numeric(df_plot[self.effect_field], errors="coerce")

        # 2) Строим график по подготовленным данным
        fig = plt.figure(figsize=(6, 4))
        ax = sns.boxplot(
            data=df_plot,
            x=grouping_field,
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
        figures[grouping_field] = fig
        # plt.title(f"{config.title}")
        # plt.xlabel("")
        # plt.ylabel(config.ylabel)
        #
        # # если нужен свой текст на осях:
        # # plt.xticks(range(len(config.xticks)), config.xticks)
        #
        # # аккуратно переименуем легенду
        # handles, labels = ax.get_legend_handles_labels()
        # if len(handles) >= 2:
        #     ax.legend(handles, [config.labels.before, config.labels.after], title=self.hue_field)
        # plt.tight_layout()
        # figures[grouping_field] = fig

        return stats, figures

    def run_grouping_bu(self, data: pd.DataFrame, grouping_field: str) -> tuple[dict, dict]:
        stats, figures = {}, {}
        config = self.experiment_config.groupings[grouping_field]

        fig = plt.figure(figsize=(6, 4))
        sns.boxplot(
            data=data,
            x=grouping_field,
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
        figures[grouping_field] = fig

        for val in data[grouping_field].dropna().unique():
            subset = data[data[grouping_field] == val]
            # g0 = subset[subset[self.hue_field] == 0][self.effect_field]
            # g1 = subset[subset[self.hue_field] == 1][self.effect_field]
            g0 = self.prep_series(subset, hue_value=0)
            g1 = self.prep_series(subset, hue_value=1)
            stats[f"{grouping_field}_{val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        return stats, figures

    def prep_series(self, data: pd.DataFrame, hue_value: int) -> pd.Series:
        """
        Возвращает Series значений effect_field,
        индексированных по index_fields (если заданы).
        """
        df = data[data[self.hue_field].astype(int) == hue_value].copy()
        df = df.dropna(subset=[self.effect_field])

        # print(f"df={df.describe()}")
        # print(f"hue_field={self.hue_field}, effect_field={self.effect_field}, index_fields={self.index_fields}")

        if not self.index_fields:
            # независимый сценарий — обычная серия без ключа
            return df[self.effect_field].astype(float)

        # парный сценарий — задаём индекс из index_fields
        s = df.set_index(self.index_fields)[self.effect_field].astype(float)

        return s
