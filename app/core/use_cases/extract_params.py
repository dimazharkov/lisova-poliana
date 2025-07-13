from app.core.contracts.extract_use_case_contract import ExtractUseCaseContract


class ExtractParamsUseCase(ExtractUseCaseContract):
    def run(self, json_data: dict) -> dict:
        wsr_data = json_data["Дані ВСР"]
        parameters = [row["col_1"] for row in wsr_data[11:] if "col_1" in row and row["col_1"]]
        param_dict = {f"h{i + 1}": param for i, param in enumerate(parameters)}
        return param_dict
