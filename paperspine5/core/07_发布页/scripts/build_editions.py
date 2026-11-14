#!/usr/bin/env python3
"""Build the three PaperSpine distributions and a local download index."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "06_插件化/release"
SOURCE = ROOT / "01_PaperSpine4/src"
sys.path.insert(0, str(RELEASE))

from edition_manager import ENTRY, FORMAT, MARKETPLACE, MODES, STAGES, WEB_ENTRY, digest, names
from suite_release import FIXED_ZIP_TIME, build_bundle

METHOD_LINK = re.compile(r"\]\(([^() ]+\.md)(?=#[^ )]+|\))")
TOOLS = (
    "_paper_spine_utils.py", "artifact_check.py", "author_voice_check.py",
    "citation_bank_check.py", "citation_quality_audit.py", "citation_verification_en.py",
    "evidence_grounded_review.py", "figure_comparison.py", "figure_layout_probe.py",
    "figure_reference_check.py", "figure_story_check.py", "latex_guard.py",
    "manuscript_export.py", "material_inventory.py", "pdf_reserved_band_probe.py",
    "preserve_figure_revision.py", "publication_surface_check.py", "results_validation_check.py",
    "visual_readiness_check.py", "word_guard.py",
)
DOWNLOADS = {
    "skill": ("全流程 Skill", "一次调用，从题目、结果或稿件做到可编辑论文。"),
    "skills-pack": ("Skills 包", "同一全流程入口。研究、Followwriting、制图、审阅和交付都可单独调用。"),
    "web-plugin": ("Web 插件包", "包含 Skills 包和 Windows x64 Codex 插件，在本地比较图件、预览论文和保存反馈。"),
}


def json_bytes(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def shared_methods(stages: dict[str, str]) -> dict[str, bytes]:
    refs = SOURCE / "skill/references"
    pending = [match.split("/")[-1] for text in stages.values()
               for match in METHOD_LINK.findall(text) if match.startswith("../../skill/references/")]
    methods = {}
    while pending:
        name = pending.pop()
        if name in methods:
            continue
        text = read_md(refs / name)
        methods[name] = text.encode()
        pending.extend(link for link in METHOD_LINK.findall(text)
                       if not re.match(r"[a-z]+:", link) and (refs / link).is_file())
        pending.extend(re.findall(r"`references/([\w./-]+\.md)`", text))
    for text in list(methods.values()):
        for name in re.findall(r"`references/(contracts/[\w./-]+\.json)`", text.decode()):
            methods[name] = (refs / name).read_bytes()
    return methods


def skill_payload(mode: str) -> dict[str, bytes]:
    source = SOURCE / "skill-editions"
    primary = f"skills/{ENTRY}"
    stages = {name: read_md(source / name / "SKILL.md") for name in STAGES}
    files = {f"{primary}/references/{name}": content for name, content in shared_methods(stages).items()}
    files[f"{primary}/SKILL.md"] = read_md(source / ENTRY / "SKILL.md").replace(
        "../EDITION-MANAGEMENT.md", "references/installation.md").encode()
    files[f"{primary}/references/installation.md"] = read_md(source / "EDITION-MANAGEMENT.md").encode()
    for tool in TOOLS:
        files[f"{primary}/scripts/{tool}"] = (SOURCE / "scripts" / tool).read_bytes()
    for name, content in stages.items():
        if mode == "skill":
            path = f"{primary}/references/stages/{name}.md"
            content = content.replace("../../skill/references/", "../")
            content = content.replace("../EDITION-MANAGEMENT.md", "../installation.md")
        else:
            path = f"skills/{name}/SKILL.md"
            content = content.replace("../../skill/references/", f"../{ENTRY}/references/")
            content = content.replace("../EDITION-MANAGEMENT.md", f"../{ENTRY}/references/installation.md")
        files[path] = content.encode()
    return files


def web_payload(zip_path: Path, version: str, sequence: int) -> tuple[dict[str, bytes], str]:
    build_bundle(ROOT, zip_path)
    adapter_version = f"{version}+{sequence}"
    with zipfile.ZipFile(zip_path) as suite:
        files = {f"runtime/{name}": suite.read(name) for name in suite.namelist()}
    plugin = f"marketplace/plugins/{WEB_ENTRY}"
    plugin_manifest = json.loads(files["runtime/.codex-plugin/plugin.json"])
    plugin_manifest.pop("mcpServers", None)
    plugin_manifest.update(
        name=WEB_ENTRY, version=adapter_version, skills="./skills/",
        description="Optional local PaperSpine workbench for the installed Skills Pack.",
    )
    plugin_manifest["interface"].update(
        displayName="PaperSpine Web",
        shortDescription="Local paper and figure workbench.",
        longDescription="Open the local workbench and use the installed PaperSpine Skills Pack.",
        capabilities=["Interactive", "Local files"],
        defaultPrompt=["Use $paper-spine-web:paper-spine-web to open my PaperSpine task."],
    )
    files[f"{plugin}/.codex-plugin/plugin.json"] = json_bytes(plugin_manifest)
    for key in ("composerIcon", "logo", "logoDark"):
        icon = plugin_manifest["interface"][key].removeprefix("./")
        files[f"{plugin}/{icon}"] = files[f"runtime/{icon}"]
    files[f"{plugin}/skills/{WEB_ENTRY}/SKILL.md"] = read_md(RELEASE / WEB_ENTRY / "SKILL.md").replace(
        "../../../01_PaperSpine4/src/skill/references/", "references/"
    ).encode()
    files[f"{plugin}/skills/{WEB_ENTRY}/agents/openai.yaml"] = b"policy:\n  allow_implicit_invocation: false\n"
    files[f"{plugin}/skills/{WEB_ENTRY}/references/product-v1-workflow.md"] = (
        files[f"runtime/standalone/{ENTRY}/references/product-v1-workflow.md"]
    )
    files["marketplace/.agents/plugins/marketplace.json"] = json_bytes({
        "name": MARKETPLACE, "interface": {"displayName": "PaperSpine editions"},
        "plugins": [{
            "name": WEB_ENTRY, "source": {"source": "local", "path": f"./plugins/{WEB_ENTRY}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity", "version": adapter_version,
        }],
    })
    return files, adapter_version


def write_archive(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)


def download_page(entries: dict) -> str:
    cards = []
    for kind, (label, description) in DOWNLOADS.items():
        item = entries[kind]
        cards.append(f"""<article><h2>{label}</h2><p>{description}</p>
<a href="{html.escape(item['file'])}" download>下载 ZIP · {item['bytes'] / (1024 * 1024):.2f} MiB</a></article>""")
    return """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>下载 PaperSpine</title>
<style>
:root{color-scheme:light;font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;color:#203431;background:#f4f6f0}
main{max-width:64rem;margin:8vh auto;padding:1.5rem}h1{font-size:clamp(2rem,5vw,4rem);margin-bottom:0}
section{display:grid;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));gap:1rem;margin:2rem 0}
article{background:white;border:1px solid #c4d0c4;border-radius:.6rem;padding:1.25rem;display:flex;flex-direction:column}
article p{line-height:1.55;flex:1}a{color:#1e5449}article a{font-weight:700}
</style>
<main><h1>下载 PaperSpine</h1><p>选一种安装方式。三种版本都使用同一套科研、写作和制图方法。</p>
<section aria-label="安装方式">""" + "\n".join(cards) + """</section>
<p><a href="INSTALL.md">安装、更新和卸载</a> · <a href="channel.json" download>更新频道</a> · <a href="checksums.sha256" download>SHA-256</a></p>
</main></html>
"""


def build(output: Path, version: str, sequence: int, base_url: str | None = None,
          channel_url: str | None = None) -> dict:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.]+)?", version) or sequence < 1:
        raise ValueError("Provide a release version and positive increasing sequence")
    if base_url and not base_url.startswith("https://"):
        raise ValueError("A public download base must use HTTPS")
    if channel_url and not channel_url.startswith("https://"):
        raise ValueError("A public update channel must use HTTPS")
    output.mkdir(parents=True, exist_ok=True)
    entries = {}
    guide = (ROOT / "07_发布页/EDITIONS.md").read_bytes()
    common = {
        "README.md": guide,
        "edition_manager.py": (RELEASE / "edition_manager.py").read_bytes(),
        "stable_updater.py": (RELEASE / "stable_updater.py").read_bytes(),
        "LICENSE": (ROOT / "01_PaperSpine4/LICENSE").read_bytes(),
    }
    with tempfile.TemporaryDirectory(prefix=".paperspine-build-", dir=output) as stage:
        for kind in MODES:
            files = {**common, **skill_payload(kind)}
            metadata = {"format": FORMAT, "edition": kind, "version": version,
                        "sequence": sequence, "skills": list(names(kind))}
            if channel_url:
                metadata["channel_url"] = channel_url
            if kind == "web-plugin":
                web, adapter = web_payload(Path(stage) / "suite.zip", version, sequence)
                files.update(web)
                metadata["plugin_version"] = adapter
            metadata["files"] = {key: hashlib.sha256(data).hexdigest() for key, data in sorted(files.items())}
            files["edition.json"] = json_bytes(metadata)
            suffix = "-windows-x64" if kind == "web-plugin" else ""
            filename = f"paperspine-{kind}-{version}{suffix}.zip"
            target = output / filename
            prepared = Path(stage) / filename
            write_archive(prepared, files)
            prepared.replace(target)
            entries[kind] = {"edition": kind, "sequence": sequence, "version": version,
                             "file": f"{base_url.rstrip('/')}/{filename}" if base_url else filename,
                             "asset": filename, "bytes": target.stat().st_size, "sha256": digest(target)}
    index = {"format": FORMAT, "editions": entries}
    (output / "channel.json").write_bytes(json_bytes(index))
    (output / "checksums.sha256").write_text(
        "".join(f"{item['sha256']}  {item['asset']}\n" for item in entries.values()), encoding="utf-8"
    )
    (output / "INSTALL.md").write_bytes(guide)
    (output / "index.html").write_text(download_page(entries), encoding="utf-8")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--sequence", type=int, required=True)
    parser.add_argument("--base-url", help="HTTPS directory hosting the published ZIPs")
    parser.add_argument("--channel-url", help="Stable HTTPS update channel offered by these archives")
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.version, args.sequence, args.base_url, args.channel_url),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
