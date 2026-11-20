"""Assemble public Pages routes from the same sources for preview and deployment."""

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "atlas"
V6 = ROOT / "paperspine5/core/07_发布页/v6"


def run(script, *args):
    subprocess.run([sys.executable, "-B", str(script), *map(str, args)], check=True)


def assemble(output):
    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "zh.html", "atlas-view.css", "atlas.js", "language.js", "model.js",
                 "china-provinces.js", "worldgeo.js", "data.js", "community.css"):
        shutil.copy2(ATLAS / name, output / name)
    run(ATLAS / "public_feed.py", output / "api/v1/atlas.json")
    if (ATLAS / "repository.json").exists():
        shutil.copy2(ATLAS / "repository.json", output / "api/v1/repository.json")
    run(ATLAS / "static_preview.py", output)
    contributors = output / "contributors"
    contributors.mkdir(exist_ok=True)
    for source, target in (("contributors.html", "index.html"), ("contributors-zh.html", "zh.html"),
                           ("contributors.js", "contributors.js")):
        shutil.copy2(ATLAS / source, contributors / target)
    v5 = ROOT / "build/v5-site"
    shutil.copytree(v5, output / "v5", dirs_exist_ok=True,
                    ignore=lambda path, names: ["v6"] if Path(path) == v5 else [])
    metadata = ROOT / "website/v6/downloads"
    if (metadata / "channel.json").exists():
        run(V6 / "build_v6.py", "site", metadata, output / "v6")
        shutil.copy2(output / "v6/llms.txt", output / "llms.txt")
        sys.path.insert(0, str(V6))
        from localization import render_community, sync_readmes

        sync_readmes(ROOT, check=True)
        render_community(output, "https://wubing2023.github.io/PaperSpine/")


if __name__ == "__main__":
    assemble(Path(sys.argv[1]).resolve())
