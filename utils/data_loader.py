import json


def load_json(file_path: str) -> dict | list:
    with open(file_path) as f:
        return json.load(f)