from collections import defaultdict

from app.core.contracts.extract_use_case_contract import ExtractUseCaseContract


class ExtractParamDuplicatesUseCase(ExtractUseCaseContract):
    def run(self, json_data: dict) -> dict:
        reverse = defaultdict(list)
        for alias, param in json_data.items():
            reverse[param].append(alias)
        duplicates = {param: aliases for param, aliases in reverse.items() if len(aliases) > 1}
        return duplicates
