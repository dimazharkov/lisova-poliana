from dataclasses import asdict

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from app.core.contracts.experiment_use_case_contract import ExperimentUseCaseContract
from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.experiment_result import ExperimentResultDTO


class BeforeAfterExperimentUseCase(ExperimentUseCaseContract):
    def __init__(self, stat_evaluator: StatEvaluatorContract):
        self.stat_evaluator = stat_evaluator

    def run(self, data: pd.DataFrame) -> ExperimentResultDTO:

        LABEL_MAP = {
            "≤40": "До 40",
            ">40": "Після 40",
            "норм. вага": "Нормальна вага",
            "зайва вага": "Зайва вага",
            "норм. тиск": "Нормальний тиск",
            "вис. тиск": "Високий тиск"
        }

        data = data.copy()
        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40").map(LABEL_MAP)
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага").map(
            LABEL_MAP)
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск").map(
            LABEL_MAP)

        figures = {}
        stats = {}

        def apply_custom_legend():
            handles, labels = plt.gca().get_legend_handles_labels()
            plt.legend(handles, ["До", "Після"], title="Заміри")

        def apply_custom_facet_legend(g):
            g.add_legend(title="Заміри")
            for text, new_label in zip(g._legend.texts, ["До", "Після"]):
                text.set_text(new_label)
            g._legend.set_bbox_to_anchor((1, 1))

        def eval_and_plot_global(label: str, df: pd.DataFrame, title: str):
            if df.empty:
                return
            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[label] = asdict(self.stat_evaluator.evaluate(g0, g1))

            fig = plt.figure(figsize=(5, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            plt.title(title)
            plt.xlabel("Заміри")
            plt.ylabel("Медіанний ефект")
            apply_custom_legend()
            plt.xticks([0, 1], ["До", "Після"])
            plt.tight_layout()
            figures[label] = fig

        eval_and_plot_global("all", data, "Усі дані")

        def eval_and_plot_grouped(label: str, group_col: str, title: str):
            fig = plt.figure(figsize=(6, 4))
            sns.boxplot(data=data, x=group_col, y="median_effect", hue="repeat", palette="Set2", showfliers=False,
                        width=0.4)
            plt.title(title)
            plt.xlabel(group_col)
            plt.ylabel("Медіанний ефект")
            apply_custom_legend()
            plt.tight_layout()
            figures[label] = fig

            for val in data[group_col].unique():
                subset = data[data[group_col] == val]
                g0 = subset[subset["repeat"] == 0]["median_effect"]
                g1 = subset[subset["repeat"] == 1]["median_effect"]
                key = f"{label}_{val}"
                stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

        eval_and_plot_grouped("by_age", "age_group", "За віком")
        eval_and_plot_grouped("by_weight", "weight_status", "За вагою")
        eval_and_plot_grouped("by_bp", "bp_status", "За тиском")

        def plot_facet_2x2_and_stats(df, row, col, key, title):
            if df[row].nunique() != 2 or df[col].nunique() != 2:
                return

            g = sns.FacetGrid(df, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("", "Медіанний ефект")
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            apply_custom_facet_legend(g)
            for ax in g.axes.flatten():
                ax.set_xticks([0, 1])
                ax.set_xticklabels(["До", "Після"])
            for ax in g.axes[:, 1]:
                ax.set_ylabel("")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            figures[key] = g.fig

            for row_val in df[row].unique():
                for col_val in df[col].unique():
                    subset = df[(df[row] == row_val) & (df[col] == col_val)]
                    if subset.empty:
                        continue
                    g0 = subset[subset["repeat"] == 0]["median_effect"]
                    g1 = subset[subset["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{row_val}+{col_val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        facet_pairs = [
            ("bp_status", "weight_status", "facet_bp_weight", "Тиск × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
        ]
        for row, col, key, title in facet_pairs:
            plot_facet_2x2_and_stats(data, row, col, key, title)

        def plot_facet_fixed_and_stats(fixed_col, fixed_val, row, col, key, title_prefix):
            subset = data[data[fixed_col] == fixed_val].copy()
            if subset.empty or subset[row].nunique() != 2 or subset[col].nunique() != 2:
                return

            g = sns.FacetGrid(subset, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("", "Медіанний ефект")
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            apply_custom_facet_legend(g)
            for ax in g.axes.flatten():
                ax.set_xticks([0, 1])
                ax.set_xticklabels(["До", "Після"])
            for ax in g.axes[:, 1]:
                ax.set_ylabel("")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{title_prefix}: {fixed_val}")
            figures[key] = g.fig

            for rv in subset[row].unique():
                for cv in subset[col].unique():
                    part = subset[(subset[row] == rv) & (subset[col] == cv)]
                    if part.empty:
                        continue
                    g0 = part[part["repeat"] == 0]["median_effect"]
                    g1 = part[part["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{rv}+{cv}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        fixed_triplets = [
            ("bp_status", "Нормальний тиск", "age_group", "weight_status", "facet_bp_norm", "Тиск"),
            ("bp_status", "Високий тиск", "age_group", "weight_status", "facet_bp_high", "Тиск"),
            ("weight_status", "Нормальна вага", "age_group", "bp_status", "facet_weight_norm", "Вага"),
            ("weight_status", "Зайва вага", "age_group", "bp_status", "facet_weight_high", "Вага"),
            ("age_group", "До 40", "weight_status", "bp_status", "facet_age_le40", "Вік"),
            ("age_group", "Після 40", "weight_status", "bp_status", "facet_age_gt40", "Вік"),
        ]
        for fixed, val, row, col, key, prefix in fixed_triplets:
            plot_facet_fixed_and_stats(fixed, val, row, col, key, prefix)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )

    def run5(self, data: pd.DataFrame) -> ExperimentResultDTO:
        LABEL_MAP = {
            "≤40": "До 40",
            ">40": "Після 40",
            "норм. вага": "Нормальна вага",
            "зайва вага": "Зайва вага",
            "норм. тиск": "Нормальний тиск",
            "вис. тиск": "Високий тиск"
        }

        data = data.copy()

        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40")
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага")
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск")

        # Применим читаемые метки
        data["age_group"] = data["age_group"].map(LABEL_MAP)
        data["weight_status"] = data["weight_status"].map(LABEL_MAP)
        data["bp_status"] = data["bp_status"].map(LABEL_MAP)

        figures = {}
        stats = {}

        def apply_custom_legend():
            handles, labels = plt.gca().get_legend_handles_labels()
            plt.legend(handles, ["До", "Після"], title="Заміри")

        def apply_custom_facet_legend(g):
            g.add_legend(title="Заміри")
            for text, new_label in zip(g._legend.texts, ["До", "Після"]):
                text.set_text(new_label)

        # === all ===
        def eval_and_plot_global(label: str, df: pd.DataFrame, title: str):
            if df.empty:
                return
            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[label] = asdict(self.stat_evaluator.evaluate(g0, g1))

            fig = plt.figure(figsize=(5, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            plt.title(title)
            plt.xlabel("Заміри")
            plt.ylabel("Медіанний ефект")
            apply_custom_legend()
            plt.tight_layout()
            figures[label] = fig

        eval_and_plot_global("all", data, "Усі дані")

        # === сгруппированные графики по age, weight, bp ===
        def eval_and_plot_grouped(label: str, group_col: str, title: str):
            fig = plt.figure(figsize=(6, 4))
            sns.boxplot(data=data, x=group_col, y="median_effect", hue="repeat", palette="Set2", showfliers=False, width=0.4)
            plt.title(title)
            plt.xlabel(group_col)
            plt.ylabel("Медіанний ефект")
            apply_custom_legend()
            plt.tight_layout()
            figures[label] = fig

            for val in data[group_col].unique():
                subset = data[data[group_col] == val]
                g0 = subset[subset["repeat"] == 0]["median_effect"]
                g1 = subset[subset["repeat"] == 1]["median_effect"]
                key = f"{label}_{val}"
                stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

        eval_and_plot_grouped("by_age", "age_group", "За віком")
        eval_and_plot_grouped("by_weight", "weight_status", "За вагою")
        eval_and_plot_grouped("by_bp", "bp_status", "За тиском")

        # === фасеты 2×2 ===
        def plot_facet_2x2_and_stats(df, row, col, key, title):
            if df[row].nunique() != 2 or df[col].nunique() != 2:
                return

            g = sns.FacetGrid(df, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("Заміри", "Медіанний ефект")
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            apply_custom_facet_legend(g)
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)

            # Заменить 0/1 на До/Після
            for ax in g.axes.flatten():
                ax.set_xticks([0, 1])
                ax.set_xticklabels(["До", "Після"])

            # Убрать дублирующиеся подписи справа
            for ax in g.axes[:, 1]:
                ax.set_ylabel("")

            figures[key] = g.fig

            for row_val in df[row].unique():
                for col_val in df[col].unique():
                    subset = df[(df[row] == row_val) & (df[col] == col_val)]
                    if subset.empty:
                        continue
                    g0 = subset[subset["repeat"] == 0]["median_effect"]
                    g1 = subset[subset["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{row_val}+{col_val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        facet_pairs = [
            ("bp_status", "weight_status", "facet_bp_weight", "Тиск × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
        ]
        for row, col, key, title in facet_pairs:
            plot_facet_2x2_and_stats(data, row, col, key, title)

        # === фасеты 2×2 с фиксированным 3 признаком ===
        def plot_facet_fixed_and_stats(fixed_col, fixed_val, row, col, key, title_prefix):
            subset = data[data[fixed_col] == fixed_val].copy()
            if subset.empty or subset[row].nunique() != 2 or subset[col].nunique() != 2:
                return

            g = sns.FacetGrid(subset, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(sns.boxplot, x="repeat", y="median_effect", palette="Set2", showfliers=False, width=0.4)
            g.set_axis_labels("Заміри", "Медіанний ефект")
            g.set_titles(row_template="{row_name}", col_template="{col_name}")
            apply_custom_facet_legend(g)
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{title_prefix}: {fixed_val}")
            figures[key] = g.fig

            for rv in subset[row].unique():
                for cv in subset[col].unique():
                    part = subset[(subset[row] == rv) & (subset[col] == cv)]
                    if part.empty:
                        continue
                    g0 = part[part["repeat"] == 0]["median_effect"]
                    g1 = part[part["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{rv}+{cv}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        fixed_triplets = [
            ("bp_status", "Нормальний тиск", "age_group", "weight_status", "facet_bp_norm", "Тиск"),
            ("bp_status", "Високий тиск", "age_group", "weight_status", "facet_bp_high", "Тиск"),
            ("weight_status", "Нормальна вага", "age_group", "bp_status", "facet_weight_norm", "Вага"),
            ("weight_status", "Зайва вага", "age_group", "bp_status", "facet_weight_high", "Вага"),
            ("age_group", "До 40", "weight_status", "bp_status", "facet_age_le40", "Вік"),
            ("age_group", "Після 40", "weight_status", "bp_status", "facet_age_gt40", "Вік"),
        ]
        for fixed, val, row, col, key, prefix in fixed_triplets:
            plot_facet_fixed_and_stats(fixed, val, row, col, key, prefix)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )



    def run4(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = data.copy()

        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40")
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага")
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск")

        figures = {}
        stats = {}

        # === График all ===
        def eval_and_plot_global(label: str, df: pd.DataFrame, title: str):
            if df.empty:
                return
            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[label] = asdict(self.stat_evaluator.evaluate(g0, g1))

            fig = plt.figure(figsize=(5, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False)
            plt.title(title)
            plt.xlabel("Заміри")
            plt.ylabel("Медіанний ефект")
            plt.tight_layout()
            figures[label] = fig

        eval_and_plot_global("all", data, "Усі дані")

        # === Объединённые графики по возрасту, весу и давлению ===
        def eval_and_plot_grouped(label: str, group_col: str, title: str):
            fig = plt.figure(figsize=(6, 4))
            sns.boxplot(data=data, x=group_col, y="median_effect", hue="repeat", palette="Set2", showfliers=False)
            plt.title(title)
            plt.xlabel(group_col)
            plt.ylabel("Медіанний ефект")
            plt.tight_layout()
            figures[label] = fig

            for val in data[group_col].unique():
                subset = data[data[group_col] == val]
                g0 = subset[subset["repeat"] == 0]["median_effect"]
                g1 = subset[subset["repeat"] == 1]["median_effect"]
                key = f"{label}_{val}"
                stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

        eval_and_plot_grouped("by_age", "age_group", "За віком")
        eval_and_plot_grouped("by_weight", "weight_status", "За вагою")
        eval_and_plot_grouped("by_bp", "bp_status", "За тиском")

        # === Фасеты 2×2 ===
        def plot_facet_2x2_and_stats(df, row, col, key, title):
            if df[row].nunique() != 2 or df[col].nunique() != 2:
                print(f"Пропуск {key}: недостаточно уникальных значений")
                return

            g = sns.FacetGrid(df, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(
                sns.boxplot,
                x="repeat",
                y="median_effect",
                palette="Set2",
                showfliers=False
            )
            g.set_axis_labels("Заміри", "Медіанний ефект")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            figures[key] = g.fig

            # Статистика по каждой подгруппе
            for row_val in df[row].unique():
                for col_val in df[col].unique():
                    subset = df[(df[row] == row_val) & (df[col] == col_val)]
                    if subset.empty:
                        continue
                    g0 = subset[subset["repeat"] == 0]["median_effect"]
                    g1 = subset[subset["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{row_val}+{col_val}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        facet_pairs = [
            ("bp_status", "weight_status", "facet_bp_weight", "Тиск × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
        ]
        for row, col, key, title in facet_pairs:
            plot_facet_2x2_and_stats(data, row, col, key, title)

        # === Фасеты с фиксированным третьим фактором ===
        def plot_facet_fixed_and_stats(fixed_col, fixed_val, row, col, key, title_prefix):
            subset = data[data[fixed_col] == fixed_val].copy()
            if subset.empty or subset[row].nunique() != 2 or subset[col].nunique() != 2:
                return

            g = sns.FacetGrid(subset, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(
                sns.boxplot,
                x="repeat",
                y="median_effect",
                palette="Set2",
                showfliers=False
            )
            g.set_axis_labels("Заміри", "Медіанний ефект")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{title_prefix}: {fixed_val}")
            figures[key] = g.fig

            # Статистика по 4 подгруппам
            for rv in subset[row].unique():
                for cv in subset[col].unique():
                    part = subset[(subset[row] == rv) & (subset[col] == cv)]
                    if part.empty:
                        continue
                    g0 = part[part["repeat"] == 0]["median_effect"]
                    g1 = part[part["repeat"] == 1]["median_effect"]
                    stats[f"{key}:{rv}+{cv}"] = asdict(self.stat_evaluator.evaluate(g0, g1))

        fixed_triplets = [
            ("bp_status", "норм. тиск", "age_group", "weight_status", "facet_bp_norm", "Тиск"),
            ("bp_status", "вис. тиск", "age_group", "weight_status", "facet_bp_high", "Тиск"),
            ("weight_status", "норм. вага", "age_group", "bp_status", "facet_weight_norm", "Вага"),
            ("weight_status", "зайва вага", "age_group", "bp_status", "facet_weight_high", "Вага"),
            ("age_group", "≤40", "weight_status", "bp_status", "facet_age_le40", "Вік"),
            ("age_group", ">40", "weight_status", "bp_status", "facet_age_gt40", "Вік"),
        ]
        for fixed, val, row, col, key, prefix in fixed_triplets:
            plot_facet_fixed_and_stats(fixed, val, row, col, key, prefix)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )

    def run3(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = data.copy()

        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40")
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага")
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск")

        figures = {}
        stats = {}

        # ===== Одиночные боксплоты =====
        def eval_and_plot_single(label: str, df: pd.DataFrame, title: str):
            if df.empty:
                return
            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[label] = asdict(self.stat_evaluator.evaluate(g0, g1))

            fig = plt.figure(figsize=(5, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False)
            plt.title(title)
            plt.xlabel("Repeat")
            plt.ylabel("Медіанний ефект")
            plt.tight_layout()
            figures[label] = fig

        eval_and_plot_single("all", data, "Усі дані")

        for col, label_prefix in [("bp_status", "bp"), ("weight_status", "weight"), ("age_group", "age")]:
            for val in data[col].unique():
                subset = data[data[col] == val]
                eval_and_plot_single(f"{label_prefix}_{val}", subset, f"{label_prefix}: {val}")

        # ===== Фасетные графики 2×2 (две переменные) =====
        def plot_facet_2x2_grid(df, var1, var2, key, title):
            if df[var1].nunique() != 2 or df[var2].nunique() != 2:
                print(f"Пропуск {key}: недостаточно уникальных значений в {var1} или {var2}")
                return

            g = sns.FacetGrid(df, row=var1, col=var2, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(
                sns.boxplot,
                x="repeat",
                y="median_effect",
                palette="Set2",
                showfliers=False
            )
            g.set_axis_labels("Repeat", "Медіанний ефект")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            figures[key] = g.fig

        facet_pairs = [
            ("bp_status", "weight_status", "facet_bp_weight", "Тиск × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
        ]
        for var1, var2, key, title in facet_pairs:
            plot_facet_2x2_grid(data, var1, var2, key, title)

        # ===== Фасет 2×2 при фиксированном третьем факторе =====
        def plot_facet_3way_fixed(fixed_col, fixed_val, row, col, key, title_prefix):
            subset = data[data[fixed_col] == fixed_val].copy()
            if subset.empty:
                return
            if subset[row].nunique() != 2 or subset[col].nunique() != 2:
                print(f"Пропущено {key}: не 2×2 после фильтра {fixed_col}={fixed_val}")
                return

            g = sns.FacetGrid(subset, row=row, col=col, margin_titles=True, height=4, aspect=1)
            g.map_dataframe(
                sns.boxplot,
                x="repeat",
                y="median_effect",
                palette="Set2",
                showfliers=False
            )
            g.set_axis_labels("Repeat", "Медіанний ефект")
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{title_prefix}: {fixed_val}")
            figures[key] = g.fig

        fixed_triplets = [
            ("bp_status", "норм. тиск", "age_group", "weight_status", "facet_bp_norm", "Тиск"),
            ("bp_status", "вис. тиск", "age_group", "weight_status", "facet_bp_high", "Тиск"),
            ("weight_status", "норм. вага", "age_group", "bp_status", "facet_weight_norm", "Вага"),
            ("weight_status", "зайва вага", "age_group", "bp_status", "facet_weight_high", "Вага"),
            ("age_group", "≤40", "weight_status", "bp_status", "facet_age_le40", "Вік"),
            ("age_group", ">40", "weight_status", "bp_status", "facet_age_gt40", "Вік"),
        ]
        for fixed, val, row, col, key, prefix in fixed_triplets:
            plot_facet_3way_fixed(fixed, val, row, col, key, prefix)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )

    def run2(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = data.copy()

        # Группировки
        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40")
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага")
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск")

        figures = {}
        stats = {}

        def eval_and_plot_single(label: str, df: pd.DataFrame, title: str):
            if df.empty:
                return
            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[label] = asdict(self.stat_evaluator.evaluate(g0, g1))

            fig = plt.figure(figsize=(5, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False)
            plt.title(title)
            plt.xlabel("Repeat")
            plt.ylabel("Медіанний ефект")
            plt.tight_layout()
            figures[label] = fig

        # === Одиночные боксплоты ===
        eval_and_plot_single("all", data, "Усі дані")
        for col, label_prefix in [("bp_status", "bp"), ("weight_status", "weight"), ("age_group", "age")]:
            for val in data[col].unique():
                subset = data[data[col] == val]
                eval_and_plot_single(f"{label_prefix}_{val}", subset, f"{label_prefix}: {val}")

        # === Фасетные графики 2×2 для пар признаков ===
        def plot_facet_2x2(var1, var2, key, title):
            df = data.copy()
            df["group_code"] = df[var1] + " + " + df[var2]
            if df["group_code"].nunique() < 4:
                return
            g = sns.catplot(
                data=df,
                kind="box",
                x="repeat",
                y="median_effect",
                col="group_code",
                palette="Set2",
                showfliers=False,
                height=4,
                aspect=0.9
            )
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            g.add_legend(title="Repeat")
            figures[key] = g.fig

        facet_pairs = [
            ("bp_status", "weight_status", "facet_bp_weight", "Тиск × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
        ]
        for var1, var2, key, title in facet_pairs:
            plot_facet_2x2(var1, var2, key, title)

        # === Фасетные графики 2×2 с фиксированным третьим признаком ===
        def plot_facet_3way_fixed(fixed_col, fixed_val, var1, var2, key, title_prefix):
            subset = data[data[fixed_col] == fixed_val].copy()
            if subset.empty:
                return
            subset["group_code"] = subset[var1] + " + " + subset[var2]
            if subset["group_code"].nunique() < 4:
                return
            g = sns.catplot(
                data=subset,
                kind="box",
                x="repeat",
                y="median_effect",
                col="group_code",
                palette="Set2",
                showfliers=False,
                height=4,
                aspect=0.9
            )
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(f"{title_prefix}: {fixed_val}")
            g.add_legend(title="Repeat")
            figures[key] = g.fig

        fixed_triplets = [
            ("bp_status", "норм. тиск", "age_group", "weight_status", "facet_bp_norm", "Тиск"),
            ("bp_status", "вис. тиск", "age_group", "weight_status", "facet_bp_high", "Тиск"),
            ("weight_status", "норм. вага", "age_group", "bp_status", "facet_weight_norm", "Вага"),
            ("weight_status", "зайва вага", "age_group", "bp_status", "facet_weight_high", "Вага"),
            ("age_group", "≤40", "weight_status", "bp_status", "facet_age_le40", "Вік"),
            ("age_group", ">40", "weight_status", "bp_status", "facet_age_gt40", "Вік"),
        ]
        for fixed, fixed_val, var1, var2, key, prefix in fixed_triplets:
            plot_facet_3way_fixed(fixed, fixed_val, var1, var2, key, prefix)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )

    def run1(self, data: pd.DataFrame) -> ExperimentResultDTO:
        data = data.copy()

        # Группировка: для боксплотов и фасетных графиков
        data["age_group"] = data["age"].apply(lambda x: "≤40" if x <= 40 else ">40")
        data["weight_status"] = data["overweight"].apply(lambda x: "норм. вага" if x == 0 else "зайва вага")
        data["bp_status"] = data["high_blood_pressure"].apply(lambda x: "норм. тиск" if x == 0 else "вис. тиск")

        figures = {}
        stats = {}

        # ==== 1. Обычные боксплоты ====

        def plot_basic(title, df, key):
            fig = plt.figure(figsize=(6, 4))
            sns.boxplot(data=df, x="repeat", y="median_effect", palette="Set2", showfliers=False)
            plt.title(title)
            plt.xlabel("Repeat")
            plt.ylabel("Медіанний ефект")
            plt.tight_layout()
            figures[key] = fig

            g0 = df[df["repeat"] == 0]["median_effect"]
            g1 = df[df["repeat"] == 1]["median_effect"]
            stats[key] = asdict(self.stat_evaluator.evaluate(g0, g1))

        # Все данные
        plot_basic("Усі дані", data, "all")

        # По каждому признаку
        for col, values, name in [
            ("bp_status", ["норм. тиск", "вис. тиск"], "bp"),
            ("weight_status", ["норм. вага", "зайва вага"], "weight"),
            ("age_group", ["≤40", ">40"], "age")
        ]:
            for val in values:
                subset = data[data[col] == val]
                plot_basic(f"{name}: {val}", subset, f"{name}_{val}")

        # ==== 2. Пары признаков — фасетные графики ====

        def plot_facet(df, row, col, key, title):
            g = sns.catplot(
                data=df,
                kind="box",
                x=row,
                y="median_effect",
                hue="repeat",
                col=col,
                palette="Set2",
                showfliers=False,
                height=4,
                aspect=1
            )
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            g.add_legend(title="Repeat")
            figures[key] = g.fig

        facet_pairs = [
            ("age_group", "weight_status", "facet_age_weight", "Вік × Вага"),
            ("age_group", "bp_status", "facet_age_bp", "Вік × Тиск"),
            ("weight_status", "bp_status", "facet_weight_bp", "Вага × Тиск")
        ]

        for row, col, key, title in facet_pairs:
            plot_facet(data, row, col, key, title)

        # ==== 3. Зафиксированные признаки: отдельный график ====

        fixed_conditions = [
            ("bp_status", "норм. тиск", "facet_fixed_bp_norm", "Нормальний тиск"),
            ("bp_status", "вис. тиск", "facet_fixed_bp_high", "Підвищений тиск"),
            ("weight_status", "норм. вага", "facet_fixed_weight_norm", "Нормальна вага"),
            ("weight_status", "зайва вага", "facet_fixed_weight_high", "Зайва вага"),
            ("age_group", "≤40", "facet_fixed_age_le40", "Вік ≤ 40"),
            ("age_group", ">40", "facet_fixed_age_gt40", "Вік > 40"),
        ]

        def plot_facet_fixed(df, fix_col, fix_val, row, col, key, title):
            subset = df[df[fix_col] == fix_val]
            if subset.empty:
                return
            g = sns.catplot(
                data=subset,
                kind="box",
                x=row,
                y="median_effect",
                hue="repeat",
                col=col,
                palette="Set2",
                showfliers=False,
                height=4,
                aspect=1
            )
            g.fig.subplots_adjust(top=0.85)
            g.fig.suptitle(title)
            g.add_legend(title="Repeat")
            figures[key] = g.fig

        for fix_col, fix_val, key, title in fixed_conditions:
            other = ["age_group", "weight_status", "bp_status"]
            other.remove(fix_col)
            plot_facet_fixed(data, fix_col, fix_val, other[0], other[1], key, title)

        return ExperimentResultDTO(
            data=stats,
            figures=figures
        )

