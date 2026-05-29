#!/usr/bin/env python3
"""Index local PaperSpine reference materials into source_index.md."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


REFERENCE_EXTENSIONS = {
    ".pdf": "paper_pdf",
    ".caj": "paper_caj",
    ".kdh": "paper_kdh",
    ".nh": "paper_nh",
    ".bib": "bibliography",
    ".ris": "bibliography",
    ".enw": "bibliography",
    ".txt": "note",
    ".md": "note",
    ".doc": "document",
    ".docx": "document",
    ".tex": "template_or_latex",
    ".cls": "template_or_latex",
    ".bst": "template_or_latex",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
}


@dataclass
class ReferenceItem:
    source_id: str
    kind: str
    title: str
    origin: str
    why_included: str
    local_file: str
    used_for: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index local reference materials for PaperSpine.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Local reference folders/files. Defaults to the current project folder.",
    )
    parser.add_argument("--output-dir", default="paper_rewriting_output")
    parser.add_argument("--mode", choices=("local_first", "specified_paths", "web"), default="local_first")
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_files(paths: list[Path], max_files: int) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for root in paths:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else root.rglob("*")
        for path in candidates:
            if len(found) >= max_files:
                return found
            if not path.is_file():
                continue
            if path.suffix.lower() not in REFERENCE_EXTENSIONS:
                continue
            if "paper_rewriting_output" in path.parts or ".git" in path.parts:
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            found.append(path)
    return found


def classify(path: Path) -> str:
    return REFERENCE_EXTENSIONS.get(path.suffix.lower(), "other")


def make_items(paths: list[Path], mode: str, max_files: int) -> list[ReferenceItem]:
    files = iter_files(paths, max_files)
    items: list[ReferenceItem] = []
    for index, path in enumerate(files, start=1):
        kind = classify(path)
        source_id = f"REF{index:03d}"
        title = path.stem.replace("_", " ").replace("-", " ")
        origin = str(path)
        if mode == "web":
            why = "User-provided local seed for web-supported reference research."
        elif mode == "specified_paths":
            why = "User-specified local reference material."
        else:
            why = "Local/current-folder reference material collected before web supplementation."
        used_for = "reference reading, source indexing, citation support, or target-scene learning"
        items.append(ReferenceItem(source_id, kind, title, origin, why, str(path), used_for))
    return items


def to_markdown(items: list[ReferenceItem], mode: str) -> str:
    lines = [
        "# Source Index",
        "",
        f"- Reference mode: `{mode}`",
        f"- Indexed items: {len(items)}",
        "",
        "| Source ID | Type | Title/Name | Origin/URL/Path | Why Included | Local File/Note | Used For |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item.source_id} | {item.kind} | {item.title} | {item.origin} | "
            f"{item.why_included} | {item.local_file} | {item.used_for} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir) / "reference_materials"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [Path(value) for value in args.paths] or [Path(".")]
    items = make_items(paths, args.mode, args.max_files)
    index_path = output_dir / "source_index.md"
    index_path.write_text(to_markdown(items, args.mode), encoding="utf-8")
    if args.json:
        print(json.dumps([item.__dict__ for item in items], ensure_ascii=False, indent=2))
    else:
        print(f"Wrote {index_path} with {len(items)} indexed reference items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
