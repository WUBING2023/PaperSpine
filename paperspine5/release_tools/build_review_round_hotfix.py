"""Build the V5 review-round patch from the verified alpha.3 platform suites."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

REPO = Path(__file__).resolve().parents[2]
CORE = REPO / "paperspine5/core"
sys.path.insert(0, str(CORE / "06_插件化/release"))
import suite_release as suite  # noqa: E402

V5_BASE = "0.4.0-alpha.3"
PATCH_FILES = {
    f"03_联合开发/{name}": f"03_联合开发/{name}"
    for name in (
        "contracts/paperspine-domain-commands.schema.json",
        "contracts/paperspine-domain-commands.v1.1.schema.json",
        "contracts/paperspine-domain-events.schema.json",
        "contracts/paperspine-domain-events.v1.1.schema.json",
        "src/paperspine_figure_integration/delivery_manifest.py",
        "src/paperspine_figure_integration/p1_application.py",
        "ui/product-v1.js",
    )
}
RUNTIME = "06_插件化/runtime/paperspine5_runtime.py"
PATCH_FILES.update({
    RUNTIME: RUNTIME,
    "release/suite_release.py": "06_插件化/release/suite_release.py",
})


def build_suite(archive: Path, output: Path, spec: dict) -> dict:
    prior = suite.verify_bundle(archive)
    if (prior["archive_sha256"] != spec["sha256"] or prior["platform"] != spec["platform"]
            or prior["build_id"] != spec["build_id"]):
        raise ValueError(f"Unexpected base archive: {archive.name}")
    files, _ = suite._read_bundle(archive)
    old_manifest = json.loads(files.pop("suite-manifest.json"))
    for member, source in PATCH_FILES.items():
        if member not in files:
            raise ValueError(f"Missing patch target in {archive.name}: {member}")
        files[member] = (CORE / source).read_bytes()

    files["RELEASE-CANDIDATE.md"] = (
        "# PaperSpine5 review-round maintenance\n\n"
        "The public resolution command can target a finding within a review round. "
        "Event replay preserves resolutions written by the alpha.3 hotfix. "
        "This package is derived from the verified alpha.3 platform suite.\n"
    ).encode()
    digest = suite._tree_digest(files)
    build_id = f"review-{spec['platform']}-{digest[:16]}"
    files[".codex-plugin/plugin.json"] = suite._rewrite_plugin_manifest(
        files[".codex-plugin/plugin.json"], build_id=build_id)
    files[RUNTIME] = suite._rewrite_runtime(files[RUNTIME], build_id=build_id)
    manifest = suite.build_manifest(files, source_digest=digest, build_id=build_id)
    manifest["runtime"] = old_manifest["runtime"]
    manifest["suite"]["platform"] = spec["platform"]
    files["suite-manifest.json"] = suite.canonical_json_bytes(manifest)
    temporary = output.with_suffix(".tmp")
    with zipfile.ZipFile(archive) as original, zipfile.ZipFile(temporary, "w") as updated:
        for item in original.infolist():
            updated.writestr(item, files.pop(item.filename), zipfile.ZIP_DEFLATED, compresslevel=9)
    if files:
        raise ValueError(f"Unexpected new archive members: {sorted(files)}")
    verified = suite.verify_bundle(temporary)
    if verified["product_version"] != suite.PRODUCT_VERSION:
        raise ValueError("Version verification failed")
    temporary.replace(output)
    return {"file": output.name, "platform": verified["platform"], "bytes": output.stat().st_size,
            "sha256": verified["archive_sha256"], "build_id": verified["build_id"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bases", type=Path, help="Directory with the original platform suites")
    parser.add_argument("output", type=Path)
    parser.add_argument("--platform", choices=("windows-amd64", "linux-x86_64", "macos-arm64", "macos-x86_64"))
    args = parser.parse_args()
    old = json.loads((REPO / f"release/v{V5_BASE}/manifest.json").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for spec in old["artifacts"]:
        if args.platform and spec["platform"] != args.platform:
            continue
        filename = spec["file"].replace(V5_BASE, suite.PRODUCT_VERSION)
        result = build_suite(args.bases / spec["file"], args.output / filename, spec)
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
