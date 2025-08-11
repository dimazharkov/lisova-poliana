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
            effect_field: str = "median_effect"
    ):
        self.stat_evaluator = stat_evaluator
        self.experiment_config = experiment_config
        self.hue_field = hue_field
        self.grouping_fields = grouping_fields
        self.effect_field = effect_field

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:

        # print(f">> repeat={len(data[data["repeat"] == 0])}:{len(data[data['repeat'] == 1])}")
        #
        # print(data["age_over_40"].unique())
        # print(f"age_over_40={len(data[data["age_over_40"] == 0])}:{len(data[data['age_over_40'] == 1])}")
        #
        # print(data["overweight"].unique())
        # print(f"overweight={len(data[data["overweight"] == 0])}:{len(data[data['overweight'] == 1])}")
        #
        # print(data["high_blood_pressure"].unique())
        # print(f"high_blood_pressure={len(data[data["high_blood_pressure"] == 0])}:{len(data[data['high_blood_pressure'] == 1])}")
        #
        # print(data["pcl_exceeded"].unique())
        # print(f"pcl_exceeded={len(data[data["pcl_exceeded"] == 0])}:{len(data[data['pcl_exceeded'] == 1])}")
        #
        # print(data["nsi_exceeded"].unique())
        # print(f"nsi_exceeded={len(data[data["nsi_exceeded"] == 0])}:{len(data[data['nsi_exceeded'] == 1])}")
        result_data = {}
        result_figs = {}

        stats, figs = self.run_overall(data)
        result_data.update(stats)
        result_figs.update(figs)

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

        g0 = data[data[self.hue_field].astype(int) == 0][self.effect_field]
        g1 = data[data[self.hue_field].astype(int) == 1][self.effect_field]
        # print(data[self.effect_field].unique())
        # print("g0 count:", len(g0))
        # print("g1 count:", len(g1))

        stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

        fig = plt.figure(figsize=(6, 4))
        sns.boxplot(
            data=data,
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
            g0 = subset[subset[self.hue_field] == 0][self.effect_field]
            g1 = subset[subset[self.hue_field] == 1][self.effect_field]
            stats[f"{grouping_field}_{val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        return stats, figures

