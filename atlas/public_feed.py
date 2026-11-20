"""Serve the newest usable aggregate and retain coverage while a cold cache fills."""

import json
from pathlib import Path
import sys
from urllib.request import urlopen

from validate_data import PREFIX, load_atlas, validate_atlas

HERE = Path(__file__).resolve().parent


def seed(path):
    """On a cold checkout recover the newer public aggregate from the deployed site."""
    current = load_atlas(path)
    try:
        with urlopen("https://wubing2023.github.io/PaperSpine/data.js", timeout=12) as response:
            source = response.read(4_000_001).decode("utf-8").strip()
        if len(source) > 4_000_000 or not source.startswith(PREFIX) or not source.endswith(";"):
            raise ValueError("Unexpected aggregate format")
        data = json.loads(source[len(PREFIX):-1])
        validate_atlas(data)
        if data["repo"] != current["repo"] or data["generated"] <= current["generated"]:
            return
        # Serialize parsed aggregate fields; never serve downloaded JavaScript verbatim.
        data = {key: data[key] for key in (current.keys() | {"retrieved_at"}) if key in data}
        path.write_text(PREFIX + json.dumps(data, ensure_ascii=False) + ";", encoding="utf-8")
    except (OSError, ValueError, KeyError) as error:
        print("Using bundled aggregate:", error)


def publish(output, source):
    aggregate = load_atlas(source)
    validate_atlas(aggregate)
    # Older bundled aggregates record the day, without a time of observation.
    aggregate.setdefault("retrieved_at", aggregate["generated"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(aggregate, ensure_ascii=False), encoding="utf-8")


def refresh():
    import process

    baseline = load_atlas(HERE / "data.js")
    coverage = json.loads((HERE / "coverage.json").read_text(encoding="utf-8"))
    if coverage["sampled"] < min(baseline["totalStars"], coverage["listed"]):
        print("Keeping dated aggregate while the profile cache fills", coverage)
        return
    process.main()


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed(Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "data.js")
    elif sys.argv[1:] == ["refresh"]:
        refresh()
    else:
        publish(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "data.js")
