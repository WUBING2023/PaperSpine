#!/usr/bin/env python3
"""Build PaperSpine V6 assets or render the Pages site from the release index."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import html
import json
import os
import re
import shutil
import sys
import tempfile
from urllib.request import Request, urlopen
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(__file__).resolve().parent
CONTRACT = json.loads((SITE / "product-release.json").read_text(encoding="utf-8"))
VERSION = CONTRACT["product"]["version"]
TAG = CONTRACT["release"]["tagTemplate"].format(version=VERSION)
REPO = f"{CONTRACT['github']['owner']}/{CONTRACT['github']['repository']}"
RELEASE = f"https://github.com/{REPO}/releases/download/{TAG}"
CHANNEL = CONTRACT["website"]["productionUrl"] + "channel.json"
SEED = CONTRACT["compatibility"]["runtimeSeed"]
EDITION_KEYS = {"skill": "SKILL", "skills-pack": "PACK", "web-plugin": "WEB"}


def checked_index(directory: Path) -> dict:
    index = json.loads((directory / "channel.json").read_text(encoding="utf-8"))
    editions = index.get("editions", {})
    if index.get("format") != "paperspine-editions/1" or set(editions) != set(EDITION_KEYS):
        raise ValueError("Expected the three V6 distribution editions")
    expected = []
    for mode in EDITION_KEYS:
        item = editions[mode]
        suffix = "-windows-x64" if mode == "web-plugin" else ""
        asset = f"paperspine-{mode}-{VERSION}{suffix}.zip"
        if (
            item["edition"] != mode or item["version"] != VERSION
            or item["sequence"] != CONTRACT["release"]["sequence"]
            or item["asset"] != asset or item["file"] != f"{RELEASE}/{asset}"
            or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) or item["bytes"] < 1
        ):
            raise ValueError(f"Invalid release channel entry for {mode}")
        expected.append(f"{item['sha256']}  {asset}")
    if (directory / "checksums.sha256").read_text(encoding="ascii").splitlines() != expected:
        raise ValueError("Release index and published checksums disagree")
    return editions


def runtime_from_seed(seed: Path) -> None:
    """Reuse the exact published Windows runtime for a clean source checkout."""
    sys.path.insert(0, str(ROOT / "06_插件化/release"))
    from edition_manager import digest, extract

    if digest(seed) != SEED["sha256"]:
        raise ValueError("Runtime seed SHA-256 differs from the V6 release contract")
    parent = ROOT / "06_插件化/runtime_vendor"
    runtime = parent / "windows-py312"
    path_config = runtime / "python312._pth"
    if runtime.is_dir() and set(runtime.iterdir()) != {path_config}:
        raise ValueError("Runtime seed extraction expects a clean checkout")
    with tempfile.TemporaryDirectory(prefix=".seed-", dir=parent) as temporary:
        stage = Path(temporary)
        with zipfile.ZipFile(seed) as old, zipfile.ZipFile(stage / "vendor.zip", "w") as vendor:
            old_lock = json.loads(old.read("runtime_vendor/requirements.lock.json"))
            source_lock = json.loads((parent / "requirements.lock.json").read_bytes())
            if old_lock != source_lock:
                raise ValueError("Windows runtime lock differs from verified release")
            for entry in old.infolist():
                if entry.filename.startswith("runtime_vendor/windows-py312/"):
                    vendor.writestr(entry, old.read(entry))
        extract(stage / "vendor.zip", stage)
        prepared = stage / "runtime_vendor/windows-py312"
        if not (prepared / "python.exe").is_file():
            raise ValueError("The pinned runtime has no Windows Python")
        if path_config.is_file():
            if path_config.read_bytes() != (prepared / path_config.name).read_bytes():
                raise ValueError("The tracked Python path config differs from the pinned runtime")
            for entry in prepared.iterdir():
                if entry.name != path_config.name:
                    entry.rename(runtime / entry.name)
        else:
            prepared.rename(runtime)


def build(output: Path, seed: Path | None) -> None:
    sys.path.insert(0, str(ROOT / "07_发布页/scripts"))
    from build_editions import build as build_editions

    if seed is not None:
        runtime_from_seed(seed)
    build_editions(output, VERSION, CONTRACT["release"]["sequence"], RELEASE, CHANNEL)
    checked_index(output)


def render(metadata: Path, output: Path) -> None:
    editions = checked_index(metadata)
    replacements = {"VERSION": VERSION, "TAG": TAG}
    for mode, key in EDITION_KEYS.items():
        item = editions[mode]
        replacements[f"{key}_URL"] = html.escape(item["file"], quote=True)
        replacements[f"{key}_SIZE"] = (
            f"{item['bytes'] / 1024:.0f} KiB" if item["bytes"] < 1024**2 else f"{item['bytes'] / 1024**2:.2f} MiB"
        )
    output.mkdir(parents=True, exist_ok=True)
    for document in ("index.html", "zh/index.html", "en/index.html"):
        text = (SITE / document).read_text(encoding="utf-8")
        text = re.sub(r"@([A-Z_]+)@", lambda match: replacements[match[1]], text)
        target = output / document
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for file in ("v6.css", "science.js", "locale.js", "study-deck.js", "download-stats.js"):
        shutil.copyfile(SITE / file, output / file)
    for directory in ("fonts", "science"):
        shutil.copytree(SITE / directory, output / directory, dirs_exist_ok=True)
    for file in ("channel.json", "checksums.sha256"):
        shutil.copyfile(metadata / file, output / file)


def download_stats(metadata: Path, output: Path) -> None:
    modes = {edition["asset"]: mode for mode, edition in checked_index(metadata).items()}
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "PaperSpine-Pages",
    }
    token = os.environ.get("PAPERSPINE_RELEASE_READ_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    endpoint = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    with urlopen(Request(endpoint, headers=headers), timeout=12) as response:
        release = json.load(response)
    assets = sorted(
        ({"name": entry["name"], "download_count": entry["download_count"]}
         for entry in release["assets"] if entry["name"] in modes),
        key=lambda entry: entry["name"],
    )
    if release["tag_name"] != TAG or len(assets) != len(modes) or {entry["name"] for entry in assets} != set(modes):
        raise ValueError("Release download statistics do not match the three V6 packages")
    if any(type(entry["download_count"]) is not int or entry["download_count"] < 0 for entry in assets):
        raise ValueError("GitHub returned an invalid asset download count")
    snapshot = {"tag": TAG, "retrieved_at": datetime.now(UTC).isoformat(), "assets": assets}
    output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8", newline="\n")
    for asset in assets:
        count = f"{asset['download_count']:,}"
        badge = f'''<svg xmlns="http://www.w3.org/2000/svg" width="134" height="23" viewBox="0 0 134 23" role="img">
  <title>{count} GitHub Release downloads</title>
  <rect width="134" height="23" rx="3" fill="#e7ede6"/>
  <text x="10" y="15.5" font-family="Verdana,sans-serif" font-size="11" fill="#314640">Downloads</text>
  <text x="124" y="15.5" text-anchor="end" font-family="Verdana,sans-serif" font-size="11" font-weight="700" fill="#135e52">{count}</text>
</svg>
'''
        output.with_name(f"downloads-{modes[asset['name']]}.svg").write_text(badge, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    assets = commands.add_parser("assets")
    assets.add_argument("output", type=Path)
    assets.add_argument("--runtime-seed", type=Path)
    site = commands.add_parser("site")
    site.add_argument("metadata", type=Path)
    site.add_argument("output", type=Path)
    stats = commands.add_parser("download-stats")
    stats.add_argument("metadata", type=Path)
    stats.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "assets":
        build(args.output, args.runtime_seed)
    elif args.command == "site":
        render(args.metadata, args.output)
    else:
        download_stats(args.metadata, args.output)


if __name__ == "__main__":
    main()
