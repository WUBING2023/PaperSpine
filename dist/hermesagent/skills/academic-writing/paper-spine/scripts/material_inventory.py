#!/usr/bin/env python3
"""Inventory a PaperSpine materials folder without parsing document content."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".tif", ".tiff"}
PDF_EXTS = {".pdf"}
WORD_TEXT_EXTS = {".docx", ".doc", ".txt", ".md", ".rtf"}
LATEX_EXTS = {".tex", ".bib", ".bst", ".cls", ".sty"}
DATA_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".yaml", ".yml"}
CODE_EXTS = {".py", ".r", ".m", ".ipynb", ".sh", ".ps1"}


@dataclass
class InventoryItem:
    path: str
    extension: str
    file_type: str
    role_hint: str
    size_bytes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory a materials folder.")
    parser.add_argument("materials_dir", help="Folder containing user materials.")
    parser.add_argument(
        "--output-dir",
        default="paper_rewriting_output",
        help="Directory for source_inventory.md and .json",
    )
    parser.add_argument("--markdown", action="store_true", help="Print markdown to stdout.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    return parser.parse_args()


def classify_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTS:
        return "image"
    if suffix in PDF_EXTS:
        return "pdf"
    if suffix in WORD_TEXT_EXTS:
        return "word_text"
    if suffix in LATEX_EXTS:
        return "latex"
    if suffix in DATA_EXTS:
        return "data"
    if suffix in CODE_EXTS:
        return "code"
    return "other"


def infer_role(path: Path) -> str:
    name = path.name.lower()
    checks = [
        ("draft", ("draft", "manuscript", "paper", "initial")),
        ("result", ("result", "figure", "table", "experiment", "metric", "plot")),
        ("research", ("survey", "literature", "reference", "review", "background")),
        ("method", ("method", "protocol", "setting", "setup", "pipeline", "workflow")),
        ("requirement", ("rubric", "guideline", "requirement", "rules", "template")),
    ]
    for role, tokens in checks:
        if any(token in name for token in tokens):
            return role
    return "material"


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def inventory(root: Path) -> list[InventoryItem]:
    items: list[InventoryItem] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        items.append(
            InventoryItem(
                path=rel,
                extension=path.suffix.lower(),
                file_type=classify_type(path),
                role_hint=infer_role(path),
                size_bytes=path.stat().st_size,
            )
        )
    return items


def to_markdown(items: list[InventoryItem], root: Path) -> str:
    lines = [
        "# Source Inventory",
        "",
        f"- Materials directory: `{root}`",
        f"- Files found: {len(items)}",
        "",
        "| Path | Type | Role Hint | Size Bytes |",
        "|---|---|---|---:|",
    ]
    for item in items:
        lines.append(
            f"| `{item.path}` | {item.file_type} | {item.role_hint} | {item.size_bytes} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.materials_dir)
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Materials directory not found: {root}")

    items = inventory(root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [asdict(item) for item in items]
    md = to_markdown(items, root)

    (output_dir / "source_inventory.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "source_inventory.md").write_text(md, encoding="utf-8")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
