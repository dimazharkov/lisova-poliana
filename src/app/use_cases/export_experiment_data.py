import csv
import json
import os

from src.config import config
from src.core.contracts.config_provider import ConfigProviderContract
from src.core.contracts.use_case import NoInputUseCase

csv_fieldnames = {
    "param": "Параметр",
    "method": "Метод",
    "x_len": "X",
    "y_len": "Y",
    "x_median": "Медіана X",
    "y_median": "Медіана Y",
    "effect_size": "Дельта медіан",
    "test_value": "Статистика",
    "p_value": "p-значення",
    "effect_value": "Hedges’ g (Cohen’s d)",
    "category": "Категорія",
    "label": "Інтерпретація"
}

class ExportExperimentDataUC(NoInputUseCase):
    def __init__(self, source_path: str, target_path: str, provider: ConfigProviderContract):
        self.source_path = source_path.strip("/")
        self.target_path = target_path.strip("/")
        self.provider = provider

    def run(self) -> None:
        export_file_name = self.source_path.replace("/", "-")
        full_path = config.static_path / self.source_path

        rows = []
        for filename in os.listdir(full_path):
            if filename.endswith(".json"):
                file_key = os.path.splitext(filename)[0]
                display_name = self.provider.get(file_key, file_key)
                filepath = os.path.join(full_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                conclusion = data.get("conclusion") or {}
                if not isinstance(conclusion, dict):
                    conclusion = {}

                raw_row = {
                    "param": display_name,
                    **{k: v for k, v in data.items() if k != "conclusion"},
                    **conclusion
                }

                # ключи строки — украинские заголовки
                row = {csv_fieldnames[k]: raw_row.get(k) for k in csv_fieldnames}
                rows.append(row)

        output_csv = config.static_path / self.target_path / f"{export_file_name}.csv"
        output_csv.parent.mkdir(parents=True, exist_ok=True)

        # fieldnames — список УКРАИНСКИХ заголовков в нужном порядке
        ukr_fieldnames = [csv_fieldnames[k] for k in csv_fieldnames]

        with open(output_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ukr_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

