import csv
import json
import os

from app.config import config
from app.core.contracts.config_provider_contract import ConfigProviderContract


class UtilController:
    def experiment_map_file(self, source_path: str, config_provider: ConfigProviderContract):
        mapping = {}
        full_path = config.static_path / source_path.strip("/")
        for filename in os.listdir(full_path):
            if filename.endswith(".json"):
                key = os.path.splitext(filename)[0]  # без .json
                mapping[key] = ""
        config_provider.save(mapping)

        print("done!")

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
                    row = {
                        "filter": display_name,
                        "method": data.get("method"),
                        "x_len": data.get("x_len"),
                        "y_len": data.get("y_len"),
                        "x_median": data.get("x_median"),
                        "y_median": data.get("y_median"),
                        "test_value": data.get("test_value"),
                        "p_value": data.get("p_value"),
                        "cohen_d": data.get("cohen_d"),
                        "rank_biserial_r": data.get("rank_biserial_r"),
                        "effect_size": data.get("effect_size"),
                        "relative_difference": data.get("relative_difference"),
                        "score": data.get("conclusion", {}).get("score"),
                        "meaning": data.get("conclusion", {}).get("meaning"),
                    }
                    if row["meaning"] != "not enough data":
                        rows.append(row)

        fieldnames = [
            "filter",
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
            "meaning"
        ]

        output_csv = config.static_path / "export" / f"{export_file_name}.csv"
        output_csv.parent.mkdir(parents=True, exist_ok=True)

        with open(output_csv, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print("done!")
