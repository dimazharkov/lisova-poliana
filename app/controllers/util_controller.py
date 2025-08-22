import csv
import json
import os

from app.config import config
from app.core.contracts.config_provider_contract import ConfigProviderContract

csv_fieldnames = [
    "param",
    "method",
    "x_len",
    "y_len",
    "x_median",
    "y_median",
    "test_value",
    "p_value",
    "cohen_d",
    "rank_biserial_r",
    "effect_size",
    "relative_difference",
    "score",
    "interpretation"
]

score_threshold = 0.4

class UtilController:
    def experiment_map_file(self, source_path: str, config_provider: ConfigProviderContract):
        mapping = {}
        full_path = config.static_path / source_path.strip("/")
        for filename in os.listdir(full_path):
            if filename.endswith(".json"):
                key = os.path.splitext(filename)[0]  # без .json
                mapping[key] = ""
        config_provider.save(mapping)

        # print("done!")

    def export_params_experiment_data(self, source_path: str, config_provider: ConfigProviderContract):
        base_path = config.static_path / source_path.strip("/")

        for subdir in base_path.iterdir():
            if subdir.is_dir():
                json_file = subdir / "params_stat.json"
                if json_file.exists():
                    with open(json_file, "r") as f:
                        data = json.load(f)
                    rows = []

                    for param, stat in data.items():
                        raw_row = {
                            "param": config_provider.get(param, param),
                            **{k: v for k, v in stat.items() if k != "conclusion"},
                            **stat.get("conclusion", {})
                        }
                        row = {k: raw_row.get(k, None) for k in csv_fieldnames}

                        try:
                            if float(row.get("score", 0)) >= score_threshold:
                                rows.append(row)
                        except (TypeError, ValueError):
                            continue

                    output_csv = config.static_path / "export" / f"params-stat-{subdir.name}.csv"
                    output_csv.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_csv, "w", newline="") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)

        # print("done!")

    def export_experiment_data(self, source_path: str, config_provider: ConfigProviderContract):
        export_file_name = source_path.strip("/").replace("/", "-")
        full_path = config.static_path / source_path.strip("/")

        rows = []

        for filename in os.listdir(full_path):
            if filename.endswith(".json"):
                file_key = os.path.splitext(filename)[0]
                display_name = config_provider.get(file_key, file_key)
                filepath = os.path.join(full_path, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)

                    conclusion = data.get("conclusion")
                    if not isinstance(conclusion, dict):
                        conclusion = {}

                    raw_row = {
                        "param": display_name,
                        **{k: v for k, v in data.items() if k != "conclusion"},
                        **conclusion
                    }
                    row = {k: raw_row.get(k, None) for k in csv_fieldnames}
                    rows.append(row)
                    # try:
                    #     if float(row.get("score", 0)) >= score_threshold:
                    #         rows.append(row)
                    # except (TypeError, ValueError):
                    #     continue

        output_csv = config.static_path / "export" / f"{export_file_name}.csv"
        output_csv.parent.mkdir(parents=True, exist_ok=True)

        with open(output_csv, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # print("done!")
