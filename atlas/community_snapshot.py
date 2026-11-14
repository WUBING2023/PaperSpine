"""Write a public, paginated GitHub contributor snapshot for Pages."""

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

REPO = "WUBING2023/PaperSpine"


def contributors():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "PaperSpine-Pages"}
    token = os.getenv("ATLAS_GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    rows = {}
    for page in range(1, 22):
        url = f"https://api.github.com/repos/{REPO}/contributors?anon=false&per_page=100&page={page}"
        with urlopen(Request(url, headers=headers), timeout=18) as response:
            batch = [] if response.status == 204 else json.load(response)
        if not isinstance(batch, list):
            raise ValueError("GitHub returned an invalid contributors list")
        for person in batch:
            login, id_, count = person.get("login"), person.get("id"), person.get("contributions")
            if (
                isinstance(login, str) and re.fullmatch(r"[a-z0-9-]{1,39}(?:\[bot\])?", login, re.I)
                and type(id_) is int and id_ >= 0 and type(count) is int and count >= 0
            ):
                rows[id_] = {"id": id_, "login": login, "contributions": count}
        if len(batch) < 100:
            return sorted(rows.values(), key=lambda item: (-item["contributions"], item["login"].lower(), item["id"]))
    raise ValueError("Contributor catalog exceeded the expected page volume")


def main():
    output = Path(sys.argv[1])
    rows = contributors()
    if not rows:
        raise ValueError("No attributed contributors returned")
    data = {"repo": REPO, "retrieved_at": datetime.now(UTC).isoformat(), "contributors": rows}
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"GitHub attributed contributor accounts: {len(rows)}")


if __name__ == "__main__":
    main()
