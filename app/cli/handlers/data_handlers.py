from app.infra.di import Container


def data_preparation(
        source_path: str,
        target_path: str,
        treatment: int
) -> None:
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.TREATMENT.from_value(treatment)

    preprocess_data_use_case = container.preprocess_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(preprocess_data_use_case)

def data_normalize(
        source_path: str,
        target_path: str,
        include_patterns: list[str],
        exclude_fields: list[str]
) -> None:
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    normalize_data_use_case = container.normalize_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(normalize_data_use_case)


def data_inspect(
        source_path: str,
        target_path: str,
        noizy_feature_path: str,
        include_patterns: list[str],
        exclude_fields: list[str]
) -> None:
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.NOIZY_FEATURE_PATH.from_value(noizy_feature_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    feature_inspect_use_case = container.feature_inspect_use_case()
    data_controller = container.data_controller()
    data_controller.run(feature_inspect_use_case)

def data_aggregate(
        source_path: str,
        target_path: str,
        include_patterns: list[str],
        exclude_fields: list[str]
) -> None:
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    aggregate_data_use_case = container.aggregate_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(aggregate_data_use_case)

def data_personalize(
        source_path: str,
        meta_path: str,
        target_path: str,
        merge_col: str,
        anchor_col: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.META_SOURCE_PATH.from_value(meta_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.MERGE_COL.from_value(merge_col)
    container.config.ANCHOR_COL.from_value(anchor_col)

    add_personal_data_use_case = container.add_personal_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(add_personal_data_use_case)

def data_add_indicators(
        source_path: str,
        meta_path: str,
        target_path: str,
        merge_col: str,
        anchor_col: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.META_SOURCE_PATH.from_value(meta_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.MERGE_COL.from_value(merge_col)
    container.config.ANCHOR_COL.from_value(anchor_col)

    add_personal_data_use_case = container.add_personal_indicators_use_case()
    data_controller = container.data_controller()
    data_controller.run(add_personal_data_use_case)
