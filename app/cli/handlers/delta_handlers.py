from app.infra.di import Container


def delta_build(
        source_path: str,
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    build_delta_use_case = container.build_delta_use_case()
    data_controller = container.data_controller()
    data_controller.run(build_delta_use_case)

def delta_combine(
        source_path: list[str],
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    combine_deltas_use_case = container.combine_deltas_use_case()
    multi_data_controller = container.multi_data_controller()
    multi_data_controller.run(combine_deltas_use_case)
