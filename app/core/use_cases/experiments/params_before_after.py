"""
Эксперимент по поиску самых отзывчивых параметров
внутри группы
before – after
"""
from dataclasses import asdict

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from app.core.contracts.config_provider_contract import ConfigProviderContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.experiment_result import ExperimentResultDTO


class ParamsBeforeAfterExperimentUseCase:
    def __init__(
            self,
            stat_evaluator: StatEvaluatorContract,
            experiment_config: ConfigProviderContract,
            experiment_hue: str
    ) -> None:
        self.stat_evaluator = stat_evaluator
        self.exp_conf = experiment_config
        self.exp_hue = experiment_hue

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:
        stats = {}
        figures = {}

        param_cols = [col for col in data.columns if col.startswith("h")]

        params_stat = {}
        for param in param_cols:
            g0 = data[data[self.exp_hue] == 0][param]
            g1 = data[data[self.exp_hue] == 1][param]
            params_stat[param] = asdict(self.stat_evaluator.evaluate(g0, g1))

        stats["params_stat"] = params_stat

        significant = {
            k: v for k, v in params_stat.items()
            if isinstance(v["p_value"], (float, int)) and v["p_value"] < 0.05
        }

        rows = []
        t_count = 0
        u_count = 0
        for key, v in significant.items():
            if v["method"] == "t" and isinstance(v["cohen_d"], (float, int)):
                rows.append({"value": abs(v["cohen_d"]), "test": "Cohen's d (t-test)"})
                t_count += 1
            elif v["method"] == "u" and isinstance(v["rank_biserial_r"], (float, int)):
                rows.append({"value": abs(v["rank_biserial_r"]), "test": "Rank biserial r (U-test)"})
                u_count += 1

        df_plot = pd.DataFrame(rows)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)

        # График для t-теста
        sns.boxplot(
            data=df_plot[df_plot["test"] == "Cohen's d (t-test)"],
            x="test", y="value", color="mediumseagreen", width=0.2, ax=axes[0], showfliers=False
        )
        axes[0].axhline(0.8, color='green', linestyle='--', label=self.exp_conf.plt.d_thresh_label)
        axes[0].set_ylabel(self.exp_conf.plt.y_lable)
        axes[0].set_xlabel(f"параметрів: {t_count}")

        # График для U-теста
        sns.boxplot(
            data=df_plot[df_plot["test"] == "Rank biserial r (U-test)"],
            x="test", y="value", color='orange', width=0.2, ax=axes[1], showfliers=False
        )
        axes[1].axhline(0.5, color='red', linestyle='--', label=self.exp_conf.plt.r_thresh_label)
        axes[1].set_ylabel("")  # убрать повтор подписи
        axes[1].set_xlabel(f"параметрів: {u_count}")

        fig.suptitle(self.exp_conf.plt.title)
        plt.tight_layout()

        figures["params_effect_power"] = fig

        return ExperimentResultDTO(data=stats, figures=figures)
