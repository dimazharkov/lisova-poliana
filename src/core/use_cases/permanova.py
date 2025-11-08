import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import permanova, DistanceMatrix

# Загружаем данные
df = pd.read_csv("medical_data.csv")

# Пример: фильтрация подгруппы
# (контроль, до 40 лет)
subset = df.query("group == 'control' and stratum == 'under40'")

# Только признаки (100 показателей)
features = [c for c in subset.columns if c.startswith("f")]
X = subset[features].values

# Матрица расстояний (евклидовая или косинусная)
dist_matrix = squareform(pdist(X, metric="euclidean"))
dm = DistanceMatrix(dist_matrix, ids=subset.index.astype(str))

# PERMANOVA по фактору period ("before"/"after")
res = permanova(dm, subset["period"], permutations=999)
print(res)


from skbio.stats.ordination import pcoa
import matplotlib.pyplot as plt

ordination = pcoa(dm)
coords = ordination.samples

plt.scatter(
    coords["PC1"], coords["PC2"],
    c=subset["period"].map({"before": "blue", "after": "red"}),
    label=subset["period"]
)
plt.xlabel("PCoA1"); plt.ylabel("PCoA2")
plt.title("PERMANOVA: Control / Under 40")
plt.legend(["before", "after"])
plt.show()

# ----
groups = df["group"].unique()
strata = df["stratum"].unique()

results = []

for g in groups:
    for s in strata:
        subset = df.query("group == @g and stratum == @s")
        if subset["period"].nunique() < 2:
            continue
        X = subset[features].values
        dm = DistanceMatrix(squareform(pdist(X)), ids=subset.index.astype(str))
        res = permanova(dm, subset["period"], permutations=999)
        results.append({
            "group": g,
            "stratum": s,
            "F": res["test statistic"],
            "p": res["p-value"]
        })

results_df = pd.DataFrame(results)
print(results_df)

# R² ≈ 0.05–0.10 — слабый эффект, 0.10–0.20 — средний, 0.20+ — сильный (условно).

# Demo: PERMANOVA-style visualizations (PCoA scatter, distance boxplots, ellipse overlays)
# This notebook builds three plots for one example stratum/group, using synthetic data.
# You can replace the synthetic dataframe `df` with your real data (same schema).

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2

# --- 0) Synthetic demo dataset (replace with your real df) ---
# Schema required:
# columns = ["id", "group", "stratum", "period", f1..fN]
rng = np.random.default_rng(42)
n_people = 60
n_features = 8

ids = np.arange(1, n_people + 1)
groups = np.where(rng.random(n_people) < 0.5, "therapy", "control")
# three strata for demo
strata_labels = np.array(["under40", "obese", "hypertension"])
strata = strata_labels[rng.integers(0, 3, size=n_people)]

# build before/after profiles; add a small shift for therapy in 'under40' to simulate effect
def make_profile(base_shift):
    base = rng.normal(0, 1, size=(n_people, n_features))
    before = base + base_shift
    after = base + base_shift + rng.normal(0, 0.2, size=(n_people, n_features))
    return before, after

before, after = make_profile(0.0)

# inject a meaningful effect for therapy/under40 after
mask_effect = (groups == "therapy") & (strata == "under40")
after[mask_effect] += np.array([0.6, 0.5, 0.7, 0.0, 0.0, 0.2, 0.0, 0.3])

def build_long_df(before, after):
    rows = []
    for i in range(n_people):
        bi = before[i]
        ai = after[i]
        row_before = {
            "id": ids[i],
            "group": groups[i],
            "stratum": strata[i],
            "period": "before",
        }
        row_after = {
            "id": ids[i],
            "group": groups[i],
            "stratum": strata[i],
            "period": "after",
        }
        for j in range(n_features):
            row_before[f"f{j+1}"] = bi[j]
            row_after[f"f{j+1}"] = ai[j]
        rows.append(row_before)
        rows.append(row_after)
    return pd.DataFrame(rows)

df = build_long_df(before, after)

# --- 1) Helper: simple PCoA via classical MDS on a distance matrix ---
def pcoa_from_distance_matrix(D, n_components=2):
    """
    Classical (metric) MDS = PCoA on a distance matrix.
    D: (n x n) pairwise distance matrix (Euclidean or any metric)
    Returns: coordinates (n x n_components), explained_variance_ratio (n_components,)
    """
    # Double-centering
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J  # inner-product (Gram) matrix

    # Eigen-decomposition
    vals, vecs = np.linalg.eigh(B)
    # sort descending
    idx = np.argsort(vals)[::-1]
    vals = vals[idx]
    vecs = vecs[:, idx]

    # keep positive eigenvalues only
    positive = vals > 1e-12
    vals_pos = vals[positive][:n_components]
    vecs_pos = vecs[:, positive][:, :n_components]

    coords = vecs_pos * np.sqrt(vals_pos)
    explained = vals_pos / np.sum(vals[vals > 0]) if np.any(vals > 0) else np.zeros_like(vals_pos)
    return coords, explained

# --- 2) Helper: covariance ellipse (95% by default) ---
def add_cov_ellipse(ax, points, conf=0.95, **kwargs):
    """
    Add a confidence ellipse based on the 2D covariance of 'points' (n x 2).
    """
    from matplotlib.patches import Ellipse

    mean = points.mean(axis=0)
    cov = np.cov(points, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    # sort eigenvalues ascending -> largest is vals[1]
    order = np.argsort(vals)
    vals = vals[order]
    vecs = vecs[:, order]
    angle = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
    # scaling by chi-square quantile
    k = np.sqrt(chi2.ppf(conf, df=2))
    width, height = 2 * k * np.sqrt(vals[1]), 2 * k * np.sqrt(vals[0])
    ell = Ellipse(xy=mean, width=width, height=height, angle=angle, fill=False, **kwargs)
    ax.add_patch(ell)
    return ell

# --- 3) Choose one subgroup and build visualizations ---
chosen_group = "control"
chosen_stratum = "under40"

subset = df[(df["group"] == chosen_group) & (df["stratum"] == chosen_stratum)].copy()
feature_cols = [c for c in df.columns if c.startswith("f")]

# Pairwise distances on features
X = subset[feature_cols].to_numpy()
D = squareform(pdist(X, metric="euclidean"))

# 3a) PCoA scatter with period overlay
coords, explained = pcoa_from_distance_matrix(D, n_components=2)
subset = subset.assign(PC1=coords[:, 0], PC2=coords[:, 1])

fig1 = plt.figure()
for p in ["before", "after"]:
    pts = subset[subset["period"] == p][["PC1", "PC2"]].to_numpy()
    plt.scatter(pts[:, 0], pts[:, 1], label=p)
    # ellipse overlay (95%)
    ax = plt.gca()
    if len(pts) >= 3:
        add_cov_ellipse(ax, pts, conf=0.95, lw=2)
plt.xlabel(f"PCoA1 ({explained[0]*100:.1f}% var)")
plt.ylabel(f"PCoA2 ({explained[1]*100:.1f}% var)")
plt.title(f"PCoA — {chosen_group} / {chosen_stratum}")
plt.legend()
plt.show()

# 3b) Boxplots of distances: within-before, within-after, between
# Build masks for within/between by period
period = subset["period"].to_numpy()
n = len(period)

# collect distances (upper triangle only to avoid duplication and zeros)
within_before = []
within_after = []
between = []

for i in range(n):
    for j in range(i+1, n):
        if period[i] == "before" and period[j] == "before":
            within_before.append(D[i, j])
        elif period[i] == "after" and period[j] == "after":
            within_after.append(D[i, j])
        elif period[i] != period[j]:
            between.append(D[i, j])

fig2 = plt.figure()
plt.boxplot([within_before, within_after, between], labels=["within_before", "within_after", "between"])
plt.ylabel("Pairwise distance")
plt.title(f"Distances — {chosen_group} / {chosen_stratum}")
plt.show()

# 3c) Ellipse overlay already included in (3a).
# If you want a separate plot that shows only ellipses and centroids:
fig3 = plt.figure()
ax = plt.gca()
for p in ["before", "after"]:
    pts = subset[subset["period"] == p][["PC1", "PC2"]].to_numpy()
    plt.scatter(pts[:, 0], pts[:, 1], label=p)
    if len(pts) >= 3:
        add_cov_ellipse(ax, pts, conf=0.95, lw=2)
    # centroid
    c = pts.mean(axis=0)
    plt.plot(c[0], c[1], marker="x")
plt.xlabel(f"PCoA1 ({explained[0]*100:.1f}% var)")
plt.ylabel(f"PCoA2 ({explained[1]*100:.1f}% var)")
plt.title(f"Ellipses & Centroids — {chosen_group} / {chosen_stratum}")
plt.legend()
plt.show()

# --- 4) Helper utilities for your real data ---

def pcoa_plot_for_subset(df_long, group, stratum, feature_cols, metric="euclidean", conf=0.95):
    """
    Builds a PCoA scatter with 95% covariance ellipses and returns (coords_df, explained_variance_ratio).
    df_long: DataFrame with columns ["group", "stratum", "period"] + features
    """
    sub = df_long[(df_long["group"] == group) & (df_long["stratum"] == stratum)].copy()
    X = sub[feature_cols].to_numpy()
    D = squareform(pdist(X, metric=metric))
    coords, explained = pcoa_from_distance_matrix(D, n_components=2)
    sub = sub.assign(PC1=coords[:, 0], PC2=coords[:, 1])

    fig = plt.figure()
    ax = plt.gca()
    for p in sorted(sub["period"].unique()):
        pts = sub[sub["period"] == p][["PC1", "PC2"]].to_numpy()
        plt.scatter(pts[:, 0], pts[:, 1], label=p)
        if len(pts) >= 3:
            add_cov_ellipse(ax, pts, conf=conf, lw=2)
    plt.xlabel(f"PCoA1 ({explained[0]*100:.1f}% var)")
    plt.ylabel(f"PCoA2 ({explained[1]*100:.1f}% var)")
    plt.title(f"PCoA — {group} / {stratum}")
    plt.legend()
    plt.show()

    return sub[["id", "group", "stratum", "period", "PC1", "PC2"]], explained

def distance_boxplots_for_subset(df_long, group, stratum, feature_cols, metric="euclidean"):
    """
    Builds boxplots for within-before, within-after, and between-period distances.
    """
    sub = df_long[(df_long["group"] == group) & (df_long["stratum"] == stratum)].copy()
    X = sub[feature_cols].to_numpy()
    D = squareform(pdist(X, metric=metric))
    period = sub["period"].to_numpy()
    n = len(period)

    within_before, within_after, between = [], [], []
    for i in range(n):
        for j in range(i+1, n):
            if period[i] == "before" and period[j] == "before":
                within_before.append(D[i, j])
            elif period[i] == "after" and period[j] == "after":
                within_after.append(D[i, j])
            elif period[i] != period[j]:
                between.append(D[i, j])

    fig = plt.figure()
    plt.boxplot([within_before, within_after, between], labels=["within_before", "within_after", "between"])
    plt.ylabel("Pairwise distance")
    plt.title(f"Distances — {group} / {stratum}")
    plt.show()

# Example usage with the synthetic df:
_ = pcoa_plot_for_subset(df, chosen_group, chosen_stratum, feature_cols)
distance_boxplots_for_subset(df, chosen_group, chosen_stratum, feature_cols)

# PERMDISP (Permutational Analysis of Multivariate Dispersions) тестирует:
# “Одинаков ли разброс наблюдений внутри каждой группы?”

from skbio.stats.distance import permanova, permdisp, DistanceMatrix
from scipy.spatial.distance import pdist, squareform

# Матрица расстояний
D = squareform(pdist(X_scaled, metric="correlation"))
dm = DistanceMatrix(D, ids=subset.index.astype(str))

# PERMANOVA (до/после)
permanova_res = permanova(dm, subset["period"], permutations=999)
print(permanova_res)

# PERMDISP (гомогенность дисперсий)
permdisp_res = permdisp(dm, subset["period"], permutations=999)
print(permdisp_res)
