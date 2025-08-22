from app.cli.handlers.data_handlers import data_preparation, data_normalize, data_aggregate, data_personalize, \
    data_add_indicators, data_inspect
from app.cli.handlers.delta_handlers import delta_build, delta_combine
from app.cli.handlers.experiment_handlers import experiment_before_after
from app.cli.handlers.extract_handlers import extract_data
from app.cli.handlers.util_handlers import util_export_experiment_data


def pipeline_overall():
    folder = "overall"
    column_names=[]
    column_indexes=[]
    pipeline_run(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes
    )
    print("Pipeline completed")

def pipeline_first():
    folder = "pipeline_first"
    column_names=["h155"]
    column_indexes=[(0,9)]
    pipeline_run(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col="h155"
    )
    print("Pipeline completed")

def pipeline_second():
    folder = "pipeline_second"
    column_names=["h2", "h3", "h4", "h5", "h11"]
    column_indexes=[(0,9)]
    pipeline_run(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col="h2"
    )
    print("Pipeline completed")

def pipeline_third():
    folder = "pipeline_third"
    column_names=[("h2", "h26")]
    column_indexes=[(0,9)]
    pipeline_run(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col="h2"
    )
    print("Pipeline completed")

def pipeline_fourth():
    folder = "pipeline_fourth"
    column_names=[("h29", "h149")]
    column_indexes=[(0,9)]
    pipeline_run(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col="h29"
    )
    print("Pipeline completed")


def pipeline_run(folder: str, column_names: list, column_indexes: list, anchor_col: str = "h1"):
    process_control_data(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col=anchor_col
    )

    process_treatment_data(
        folder=folder,
        column_names=column_names,
        column_indexes=column_indexes,
        anchor_col=anchor_col
    )

    prepare_deltas(
        folder=folder,
        anchor_col=anchor_col
    )


def process_control_data(folder: str, column_names: list, column_indexes: list, anchor_col: str):
    data_raw_path = f"{folder}/control_data_raw.json"
    data_path = f"{folder}/control_data.json"
    noizy_feature_path = f"{folder}/control_noizy_features.json"

    extract_data(
        source_path="source/raw_data.json",
        target_path=data_raw_path,
        params_path="source/params.json",
        data_key="контроль"
    )
    print(".")

    data_preparation(
        source_path=data_raw_path,
        target_path=data_raw_path,
        treatment=0,
        column_names=column_names,
        column_indexes=column_indexes,
        keep_columns=True
    )
    print(".")

    data_normalize_aggregate_personalize(
        source_path=data_raw_path,
        target_path=data_path,
        noizy_feature_path=noizy_feature_path,
        anchor_col=anchor_col
    )
    print(".")

    hue_field = "repeat"
    effect_field = "median_effect"
    grouping_fields = ["age_over_40", "overweight", "high_blood_pressure", "pcl_exceeded", "nsi_exceeded"]

    experiment_before_after(
        source_path=[data_path],
        target_folder=f"{folder}/control-ba-3",
        experiment="3",
        config_path="experiments/control-ba-3.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields,
        test_type="paired"
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/control-ba-3",
        config_path="utils/experiment-files.json",
    )
    print(".")

    experiment_before_after(
        source_path=[data_path],
        target_folder=f"{folder}/control-ba-5",
        experiment="5",
        config_path="experiments/control-ba-5.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields,
        test_type="paired"
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/control-ba-5",
        config_path="utils/experiment-files.json",
    )
    print(".")


def process_treatment_data(folder: str, column_names: list, column_indexes: list, anchor_col: str):
    data_raw_path = f"{folder}/treatment_data_raw.json"
    data_path = f"{folder}/treatment_data.json"
    noizy_feature_path = f"{folder}/treatment_noizy_features.json"

    extract_data(
        source_path="source/raw_data.json",
        target_path=data_raw_path,
        params_path="source/params.json",
        data_key="Дих"
    )
    print(".")

    data_preparation(
        source_path=data_raw_path,
        target_path=data_raw_path,
        treatment=1,
        column_names=column_names,
        column_indexes=column_indexes,
        keep_columns=True
    )
    print(".")

    data_normalize_aggregate_personalize(
        source_path=data_raw_path,
        target_path=data_path,
        noizy_feature_path=noizy_feature_path,
        anchor_col=anchor_col
    )
    print(".")

    hue_field = "repeat"
    effect_field = "median_effect"
    grouping_fields = ["age_over_40", "overweight", "high_blood_pressure", "pcl_exceeded", "nsi_exceeded"]

    experiment_before_after(
        source_path=[data_path],
        target_folder=f"{folder}/treatment-ba-3",
        experiment="3",
        config_path="experiments/treatment-ba-3.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields,
        test_type="paired"
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/treatment-ba-3",
        config_path="utils/experiment-files.json",
    )
    print(".")

    experiment_before_after(
        source_path=[data_path],
        target_folder=f"{folder}/treatment-ba-5",
        experiment="5",
        config_path="experiments/treatment-ba-5.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields,
        test_type="paired"
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/treatment-ba-5",
        config_path="utils/experiment-files.json",
    )
    print(".")


def prepare_deltas(folder: str, anchor_col: str):
    control_delta_path = f"{folder}/control_delta.json"
    treatment_delta_path = f"{folder}/treatment_delta.json"
    delta_path = f"{folder}/delta.json"
    noizy_feature_path = f"{folder}/delta_noizy_features.json"

    delta_build(
        source_path=f"{folder}/control_data_raw.json",
        target_path=control_delta_path
    )
    print(".")

    delta_build(
        source_path=f"{folder}/treatment_data_raw.json",
        target_path=treatment_delta_path
    )
    print(".")

    delta_combine(
        source_path=[control_delta_path, treatment_delta_path],
        target_path=delta_path
    )
    print(".")

    data_normalize_aggregate_personalize(
        source_path=delta_path,
        target_path=delta_path,
        noizy_feature_path=noizy_feature_path,
        anchor_col=anchor_col
    )
    print(".")

    hue_field = "treatment"
    effect_field = "median_effect"
    grouping_fields = ["age_over_40", "overweight", "high_blood_pressure", "pcl_exceeded", "nsi_exceeded"]

    experiment_before_after(
        source_path=[delta_path],
        target_folder=f"{folder}/delta-ba-3",
        experiment="3",
        config_path="experiments/delta-ba-3.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/delta-ba-3",
        config_path="utils/experiment-files.json",
    )
    print(".")

    experiment_before_after(
        source_path=[delta_path],
        target_folder=f"{folder}/delta-ba-5",
        experiment="5",
        config_path="experiments/delta-ba-5.json",
        hue_field=hue_field,
        effect_field=effect_field,
        grouping_fields=grouping_fields
    )
    print(".")

    util_export_experiment_data(
        source_path=f"{folder}/delta-ba-5",
        config_path="utils/experiment-files.json",
    )
    print(".")

def data_normalize_aggregate_personalize(
        source_path: str,
        target_path: str,
        noizy_feature_path: str,
        anchor_col: str = "h1"
):
    # пока не используем
    # data_inspect(
    #     source_path=source_path,
    #     target_path=target_path,
    #     noizy_feature_path=noizy_feature_path,
    #     include_patterns=[r"h\d+"],
    #     exclude_fields=[]
    # )
    # source_path = target_path


    data_normalize(
        source_path=source_path,
        target_path=target_path,
        include_patterns=[r"h\d+"],
        exclude_fields=[]
    )
    print(".")

    source_path = target_path

    data_aggregate(
        source_path=source_path,
        target_path=target_path,
        include_patterns=[r"h\d+"],
        exclude_fields=[]
    )
    print(".")

    data_personalize(
        source_path=source_path,
        target_path=target_path,
        meta_path="source/personal_data.json",
        merge_col="person",
        anchor_col=anchor_col
    )
    print(".")

    data_add_indicators(
        source_path=source_path,
        target_path=target_path,
        meta_path="source/personal_indicators_data.json",
        merge_col="person",
        anchor_col=anchor_col
    )
    print(".")
