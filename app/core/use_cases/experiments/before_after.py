from dataclasses import asdict

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from app.core.contracts.experiment_design_contract import ExperimentDesignContract
from app.core.contracts.experiment_use_case_contract import ExperimentUseCaseContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.experiment_result import ExperimentResultDTO


class BeforeAfterExperimentUseCase(ExperimentUseCaseContract):
    def __init__(self, stat_evaluator: StatEvaluatorContract, experiment_config: ExperimentDesignContract):
        self.stat_evaluator = stat_evaluator
        self.exp_conf = experiment_config

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = self._preprocess(data)

        stats = {}
        figures = {}

        stats1, figs1 = self._plot_overall(data)
        stats.update(stats1)
        figures.update(figs1)

        stats2, figs2 = self._plot_single_groupings(data)
        stats.update(stats2)
        figures.update(figs2)

        stats3, figs3 = self._plot_facet_pairs(data)
        stats.update(stats3)
        figures.update(figs3)

        stats4, figs4 = self._plot_fixed_facets(data)
        stats.update(stats4)
        figures.update(figs4)

        return ExperimentResultDTO(data=stats, figures=figures)

    def _preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        self.LABEL_MAP = {
            "lt40": self.exp_conf.labels.lt40,
            "gt40": self.exp_conf.labels.gt40,
            "nw": self.exp_conf.labels.nw,
            "ow": self.exp_conf.labels.ow,
            "np": self.exp_conf.labels.np,
            "op": self.exp_conf.labels.op
        }
        data["age_group"] = data["age"].apply(lambda x: "lt40" if x <= 40 else "gt40").map(self.LABEL_MAP)
        data["weight_status"] = data["overweight"].apply(lambda x: "nw" if x == 0 else "ow").map(self.LABEL_MAP)
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "np" if x == 0 else "op").map(self.LABEL_MAP)
        return data

    def _plot_overall(self, data):
        stats = {}
        figures = {}
        g0 = data[data["repeat"] == 0]["median_effect"]
        g1 = data[data["repeat"] == 1]["median_effect"]
        stats["all"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        fig = plt.figure(figsize=(5, 4))
        sns.boxplot(data=data, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
        plt.title(f"{self.exp_conf.plt_title_prefix}")
        plt.xlabel("")
        plt.ylabel(self.exp_conf.plt_ylabel)
        plt.xticks([0, 1], self.exp_conf.plt_xticks)
        plt.tight_layout()
        figures["all"] = fig
        return stats, figures

    def _plot_single_groupings(self, data):
        stats = {}
        figures = {}
        for col, title in [
            ("age_group", self.exp_conf.labels.by_age),
            ("weight_status", self.exp_conf.labels.by_weight),
            ("bp_status", self.exp_conf.labels.by_bp)
        ]:
            fig = plt.figure(figsize=(6, 4))
            sns.boxplot(data=data, x=col, y="median_effect", hue="repeat", palette="Set2", showfliers=False, width=0.4)
            plt.title(f"{self.exp_conf.plt_title_prefix}, {title}")
            plt.xlabel("")
            plt.ylabel(self.exp_conf.plt_ylabel)
            legend = plt.legend()
            legend.get_texts()[0].set_text(self.exp_conf.labels.before)
            legend.get_texts()[1].set_text(self.exp_conf.labels.after)
            plt.tight_layout()
            figures[col] = fig

            for val in data[col].dropna().unique():
                subset = data[data[col] == val]
                g0 = subset[subset["repeat"] == 0]["median_effect"]
                g1 = subset[subset["repeat"] == 1]["median_effect"]
                stats[f"{col}_{val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))
        return stats, figures

    def _plot_facet_pairs(self, data):
        stats = {}
        figures = {}
        pairs = [
            ("age_group", "weight_status", "facet_age_weight", self.exp_conf.labels.age_weight),
            ("age_group", "bp_status", "facet_age_bp", self.exp_conf.labels.age_bp),
            ("weight_status", "bp_status", "facet_weight_bp", self.exp_conf.labels.weight_bp),
        ]
        for row, col, key, title in pairs:
            g = sns.FacetGrid(data, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("", self.exp_conf.plt_ylabel)
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            for ax in g.axes.flatten():
                ax.set_xticks([0, 1])
                ax.set_xticklabels(self.exp_conf.plt_xticks)
            for ax in g.axes[:, 1]:
                ax.set_ylabel("")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{self.exp_conf.plt_title_prefix}, {title}")
            figures[key] = g.fig

            for rv in data[row].unique():
                for cv in data[col].unique():
                    subset = data[(data[row] == rv) & (data[col] == cv)]
                    if subset.empty:
                        continue
                    g0 = subset[subset["repeat"] == 0]["median_effect"]
                    g1 = subset[subset["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{rv}+{cv}"] = asdict(self.stat_evaluator.evaluate(g0, g1))
        return stats, figures

    def _plot_fixed_facets(self, data):
        print(f"shape={data.shape}")
        stats = {}
        figures = {}
        fixed_triplets = [
            ("bp_status", self.exp_conf.labels.np, "age_group", "weight_status", "facet_bp_norm"),
            ("bp_status", self.exp_conf.labels.op, "age_group", "weight_status", "facet_bp_high"),
            ("weight_status", self.exp_conf.labels.nw, "age_group", "bp_status", "facet_weight_norm"),
            ("weight_status", self.exp_conf.labels.ow, "age_group", "bp_status", "facet_weight_high"),
            ("age_group", self.exp_conf.labels.lt40, "weight_status", "bp_status", "facet_age_le40"),
            ("age_group", self.exp_conf.labels.gt40, "weight_status", "bp_status", "facet_age_gt40"),
        ]
        for fixed, val, row, col, key in fixed_triplets:
            subset = data[data[fixed] == val].copy()
            if subset.empty or subset[row].nunique() != 2 or subset[col].nunique() != 2:
                continue

            g = sns.FacetGrid(subset, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("", self.exp_conf.plt_ylabel)
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            for ax in g.axes.flatten():
                ax.set_xticks([0, 1])
                ax.set_xticklabels(self.exp_conf.plt_xticks)
            for ax in g.axes[:, 1]:
                ax.set_ylabel("")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{self.exp_conf.plt_title_prefix}, {val.lower()}")
            figures[key] = g.fig

            for rv in subset[row].unique():
                for cv in subset[col].unique():
                    part = subset[(subset[row] == rv) & (subset[col] == cv)]
                    if part.empty:
                        continue
                    g0 = part[part["repeat"] == 0]["median_effect"]
                    g1 = part[part["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{rv}+{cv}"] = asdict(self.stat_evaluator.evaluate(g0, g1))
        return stats, figures

