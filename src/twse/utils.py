import json
from pathlib import Path


def save_json(obj: dict | list, f: str | Path) -> None:
    path = Path(f)
    if path.suffix != ".json":
        raise ValueError(f"File name must end with .json, got {path.suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as fp:
        json.dump(obj, fp, indent=2, ensure_ascii=False)
