from dataclasses import asdict

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from app.core.contracts.experiment_use_case_contract import ExperimentUseCaseContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.experiment_result import ExperimentResultDTO


class BaselineControlExperimentUseCase(ExperimentUseCaseContract):
    def __init__(self, stat_evaluator: StatEvaluatorContract):
        self.stat_evaluator = stat_evaluator

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = data.copy()

        results = {}
        plots = {}
        plots_data = []

        for exp_id in [3, 5]:
            group = data[data["experiment"] == exp_id]
            g0 = group[group["treatment"] == 0]["median_effect"]
            g1 = group[group["treatment"] == 1]["median_effect"]

            stat_result = self.stat_evaluator.evaluate(g0, g1)
            results[f"baseline_experiment_{exp_id}"] = asdict(stat_result)

            plots_data.append(group)

        combined_plot_df = pd.concat(plots_data)

        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=combined_plot_df,
            x="experiment",
            y="median_effect",
            hue="treatment",
            palette="Set3",
            showfliers=False
        )
        plt.title("Порівняння початкових умов між групами за експериментами")
        plt.xlabel("Експеримент")
        plt.ylabel("Медіанний эфект")
        plt.legend(title="Експерименти")
        legend = plt.legend()
        legend.get_texts()[0].set_text("Контроль")
        legend.get_texts()[1].set_text("Дих")
        plt.tight_layout()

        plots["baseline_experiment"] = plt.gcf()

        return ExperimentResultDTO(
            data=results,
            figures=plots
        )
