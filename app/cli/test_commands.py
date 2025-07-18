import json

import pandas as pd
import typer

from app.core.use_cases.experiments.baseline_control_experiment import BaselineControlExperimentUseCase
from app.infra.evaluators.stat_evaluator import StatEvaluator
from app.utils.os_utils import load_df_from_disc

app = typer.Typer()

@app.command()
def baseline():
    evaluator = StatEvaluator()
    use_case = BaselineControlExperimentUseCase(evaluator)

    control_df = load_df_from_disc("control_data.json")
    treatment_df = load_df_from_disc("treatment_data.json")
    combined = pd.concat([control_df, treatment_df], ignore_index=True)
    combined = combined[combined["repeat"] == 0]

    dto = use_case.run(combined)
    print(json.dumps(dto.data, indent=4, ensure_ascii=False))
