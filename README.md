# Breathing Intervention Statistical Analysis

This project implements a complete pipeline for processing and analyzing experimental data collected from participants who completed tasks under different conditions: with and without a breathing-based intervention. Two experiment durations were used: **3 minutes** and **5 minutes**.

## Overview of Comparisons

The analysis includes the following comparisons:

1. **Initial group comparison**  
   Comparison of baseline measurements between control and intervention groups, separately for 3-minute and 5-minute experiments.

2. **Within-group before/after comparison**  
   For each group (control and breathing), changes between the first and repeated sessions are analyzed for both experiment durations.

3. **Delta comparison between groups**  
   Log-transformed relative changes ("deltas") are computed for each participant and compared between control and breathing groups.

## Stratification

All comparisons are performed not only for the entire dataset but also within specific strata:

- **Blood pressure**: normal / elevated  
- **Weight status**: normal / overweight  
- **Age**: under 40 / 40 and older  
- **All combinations** of the above factors  
- **Overall (pooled)** population without stratification

## Data Processing Pipeline

The project follows a structured multi-stage pipeline:

### 1. Data Preparation  
- Removal of invalid or incomplete rows  
- Filtering for only first and repeated attempts (`repeat` in {0, 1})  
- Insertion of group labels (`treatment`) and participant metadata

### 2. Feature Engineering  
- Removal of low-quality features based on statistical criteria  
- Storage of excluded features and reasons for exclusion  
- Selection of valid numerical features for analysis

### 3. Normalization  
- Robust scaling followed by Min-Max scaling of selected features  
- Brings all features to a common scale [0, 1]

### 4. Median Effect Calculation  
- For each experiment, a `median_effect` is computed  
- This value aggregates all normalized numerical features to a single value, used to reduce dimensionality and simplify group comparison

### 5. Integration of Personal Data  
- Computation of BMI and classification into overweight/normal  
- Detection of high blood pressure based on systolic/diastolic readings  
- Conversion of personal fields to numerical formats

### 6. Delta Computation  
- For participants with two valid sessions, relative changes are computed  
- Deltas are calculated as log-transformed absolute changes:  
  `log1p(abs((after - before) / before))`  
- This ensures scale invariance and robustness to noise

- The delta data then undergoes the same processing:  
  feature cleaning, normalization, and median effect computation

### 7. Statistical Testing  
- Depending on distribution, either **Welch’s t-test** or **Mann–Whitney U test** is used  
- Effect size is reported via **Cohen’s d** (t-test) or **rank biserial correlation** (U test)  
- Absolute and relative differences are also reported  
- An interpretation of effect strength is generated based on statistical and practical significance

## Output

Each analysis produces a structured statistical report including:
- Median values per group  
- p-value and test statistics  
- Effect size and direction  
- Scaled score and qualitative interpretation (e.g., "strong effect")

## Usage

Below is a full sequence of commands to run the complete analysis pipeline:

```bash
# 1. Source Preparation
python main.py extract params --source-path=source/raw_data.json --target-path=source/params.json
# Edit params.json manually to assign group names (e.g. "Амплітуда P (мкВ)" → "Амплітуда P (мкВ) — відведення I")
python main.py extract param-duplicates --source-path=source/params.json --target-path=source/param_duplicates.json
python main.py extract personal-data --source-path=source/raw_data.json --target-path=source/personal_data.json
python main.py extract personal-indicators --source-path=source/raw_data.json --target-path=source/personal_indicators_data.json

# 2. Control Data Preparation
python main.py extract data --source-path=source/raw_data.json --target-path=control_data.json --data-key=контроль
python main.py data prep --source-path=control_data.json --target-path=control_data.json --treatment=0
python main.py data inspect --source-path=control_data.json --target-path=control_data.json --noizy-feature-path=control_noizy.json
python main.py data normalize --source-path=control_data.json --target-path=control_norm.json
python main.py data aggregate --source-path=control_norm.json --target-path=control_norm.json
python main.py data personalize --source-path=control_norm.json --target-path=control_norm.json --meta-path=source/personal_data.json
python main.py data add-indicators --source-path=control_norm.json --target-path=control_norm.json --meta-path=source/personal_indicators_data.json

# 3. Treatment Data Preparation
python main.py extract data --source-path=source/raw_data.json --target-path=treatment_data.json --data-key=Дих
python main.py data prep --source-path=treatment_data.json --target-path=treatment_data.json --treatment=1
python main.py data inspect --source-path=treatment_data.json --target-path=treatment_data.json --noizy-feature-path=treatment_noizy.json
python main.py data normalize --source-path=treatment_data.json --target-path=treatment_norm.json
python main.py data aggregate --source-path=treatment_norm.json --target-path=treatment_norm.json
python main.py data personalize --source-path=treatment_norm.json --target-path=treatment_norm.json --meta-path=source/personal_data.json
python main.py data add-indicators --source-path=treatment_norm.json --target-path=treatment_norm.json --meta-path=source/personal_indicators_data.json

# 4. Delta Preparation
python main.py delta build --source-path=control_data.json --target-path=control_delta.json
python main.py delta build --source-path=treatment_data.json --target-path=treatment_delta.json
python main.py delta combine --source-path=control_delta.json --source-path=treatment_delta.json --target-path=delta.json
python main.py data inspect --source-path=delta.json --target-path=delta.json --noizy-feature-path=delta_noizy.json
python main.py data normalize --source-path=delta.json --target-path=delta_norm.json
python main.py data aggregate --source-path=delta_norm.json --target-path=delta_norm.json
python main.py data personalize --source-path=delta_norm.json --target-path=delta_norm.json --meta-path=source/personal_data.json
python main.py data add-indicators --source-path=delta_norm.json --target-path=delta_norm.json --meta-path=source/personal_indicators_data.json

# 5. Run Experiments
python main.py experiment baseline --source-path control_norm.json --source-path treatment_norm.json --target-folder=baseline
python main.py experiment before-after --source-path control_norm.json --target-folder=before-after/control-3 --experiment=3 --config-path=experiments/before-after-control-3.json
python main.py experiment before-after --source-path control_norm.json --target-folder=before-after/control-5 --experiment=5 --config-path=experiments/before-after-control-5.json
python main.py experiment before-after --source-path treatment_norm.json --target-folder=before-after/treatment-3 --experiment=3 --config-path=experiments/before-after-treatment-3.json
python main.py experiment before-after --source-path treatment_norm.json --target-folder=before-after/treatment-5 --experiment=5 --config-path=experiments/before-after-treatment-5.json
python main.py experiment control-treatment --source-path delta_norm.json --target-folder=control-treatment/treatment-3 --experiment=3 --config-path=experiments/control-treatment-treatment-3.json
python main.py experiment control-treatment --source-path=delta_norm.json --target-folder=control-treatment/treatment-5 --experiment=5 --config-path=experiments/control-treatment-treatment-5.json

python main.py experiment params-before-after --source-path overall/control_data.json --target-folder=params-before-after/control-3 --experiment=3 --config-path=experiments/params-before-after-control-3.json --test-type=paired
python main.py experiment params-before-after --source-path overall/control_data.json --target-folder=params-before-after/control-5 --experiment=5 --config-path=experiments/params-before-after-control-5.json --test-type=paired

python main.py experiment params-before-after --source-path overall/treatment_data.json --target-folder=params-before-after/treatment-3 --experiment=3 --config-path=experiments/params-before-after-treatment-3.json --test-type=paired
python main.py experiment params-before-after --source-path overall/treatment_data.json --target-folder=params-before-after/treatment-5 --experiment=5 --config-path=experiments/params-before-after-treatment-5.json --test-type=paired

python main.py experiment params-delta-before-after --source-path overall/delta.json --target-folder=params-before-after/delta-3 --experiment=3 --config-path=experiments/params-before-after-delta-3.json
python main.py experiment params-delta-before-after --source-path overall/delta.json --target-folder=params-before-after/delta-5 --experiment=5 --config-path=experiments/params-before-after-delta-5.json

# 6. Utilities
python main.py utils experiment-map-file --source-path=control-treatment/treatment-5 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=control-treatment/treatment-5 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=control-treatment/treatment-3 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=before-after/control-3 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=before-after/control-5 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=before-after/treatment-3 --config-path=utils/experiment-map-file.json
python main.py utils export-experiment-data --source-path=before-after/treatment-5 --config-path=utils/experiment-map-file.json
python main.py utils export-params-experiment-data --source-path=params-before-after --config-path=utils/params.json
```

## Design Notes

The `repeat` and `treatment` fields (or other splitting parameters) are assumed to be **binary encoded**:
  - `repeat` ∈ {0, 1} — first and repeated attempts only
  - `treatment` ∈ {0, 1} — control and intervention groups

## Requirements

- Python 3.12+  
- pandas, numpy, scipy, scikit-learn

## License

MIT License
