#!/usr/bin/env python3
"""Sync PaperSpine dist layouts into local Codex, Claude Code, OpenClaw, and HermesAgent installs."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIST_CODEX_SKILL = ROOT / "dist" / "codex" / "paper-spine"
DIST_CODEX_SKILLS = ROOT / "dist" / "codex" / "skills"
DIST_CLAUDE_SKILLS = ROOT / "dist" / "claude" / "skills"
DIST_CLAUDE_COMMANDS = ROOT / "dist" / "claude" / "commands"
DIST_OPENCLAW_SKILLS = ROOT / "dist" / "openclaw" / "skills"
DIST_HERMESAGENT_SKILLS = ROOT / "dist" / "hermesagent" / "skills" / "academic-writing"
DIST_VERSION_MANIFEST = ROOT / "dist" / "paperspine_version.json"

SUITE_SKILLS = (
    "paper-spine",
    "paper-spine-ui",
    "paper-spine-intake",
    "paper-spine-research",
    "paper-spine-citation",
    "paper-spine-rewrite",
    "paper-spine-build",
    "paper-spine-latex",
    "paper-spine-audit",
    "paper-spine-translate",
    "paper-spine-humanize",
    "paper-spine-update",
)


def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser(description="Sync PaperSpine dist layouts into local installs.")
    parser.add_argument(
        "--desktop-root",
        type=Path,
        default=home / "Desktop" / "PaperSpine",
        help="Optional desktop export root. Receives dist/ only; skipped when equal to this repository.",
    )
    parser.add_argument(
        "--codex-skills-dir",
        type=Path,
        default=home / ".codex" / "skills",
        help="Codex skills directory. Receives dist/codex/skills/*.",
    )
    parser.add_argument(
        "--claude-skills-dir",
        type=Path,
        default=home / ".claude" / "skills",
        help="Claude Code flat skills directory. Receives dist/claude/skills/*.",
    )
    parser.add_argument(
        "--claude-commands-dir",
        type=Path,
        default=home / ".claude" / "commands",
        help="Claude Code commands directory. Receives dist/claude/commands/*.md.",
    )
    parser.add_argument(
        "--openclaw-skills-dir",
        type=Path,
        default=home / ".openclaw" / "skills",
        help="OpenClaw skills directory. Receives dist/openclaw/skills/*.",
    )
    parser.add_argument(
        "--hermesagent-skills-dir",
        type=Path,
        default=home / ".hermes" / "skills" / "academic-writing",
        help="HermesAgent academic-writing skills directory. Receives dist/hermesagent/skills/academic-writing/*.",
    )
    parser.add_argument("--clean-legacy", action="store_true")
    parser.add_argument("--clean-legacy-claude-nested", action="store_true", help="Deprecated alias for --clean-legacy.")
    parser.add_argument(
        "--config-home",
        type=Path,
        default=home / ".paperspine",
        help="PaperSpine global config directory. Receives install_state.json.",
    )
    parser.add_argument(
        "--dist-only",
        action="store_true",
        help="Only sync src/ scripts and references into dist/ copies within the repository. Skips install targets and desktop export.",
    )
    return parser.parse_args()


def copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))


def same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left.absolute() == right.absolute()


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except PermissionError as exc:
        print(f"Warning: skipped locked legacy path: {path} ({exc})", file=sys.stderr)


def clean_legacy(args: argparse.Namespace) -> None:
    paths = [
        args.desktop_root / "codex",
        args.desktop_root / "claude",
        args.desktop_root / "claude-code",
        args.codex_skills_dir / "PaperSpine",
        args.codex_skills_dir / "PaperSpineV2",
        args.codex_skills_dir / "paper-spine",
        args.openclaw_skills_dir / "PaperSpine",
        args.openclaw_skills_dir / "PaperSpineV2",
        args.hermesagent_skills_dir / "PaperSpine",
        args.hermesagent_skills_dir / "PaperSpineV2",
        args.claude_skills_dir / "PaperSpine",
        args.claude_skills_dir / "PaperSpineV2",
        args.claude_skills_dir / "paper-writing-assistant",
        args.claude_commands_dir / "paperspine.md",
        args.claude_commands_dir / "paperspine-ui.md",
        args.claude_commands_dir / "paperspine-legacy.md",
    ]
    paths.extend(args.codex_skills_dir / skill for skill in SUITE_SKILLS)
    paths.extend(args.claude_skills_dir / skill for skill in SUITE_SKILLS)
    paths.extend(args.openclaw_skills_dir / skill for skill in SUITE_SKILLS)
    paths.extend(args.hermesagent_skills_dir / skill for skill in SUITE_SKILLS)
    for path in paths:
        remove_path(path)


def sync_desktop_export(desktop_root: Path) -> None:
    if same_path(desktop_root, ROOT):
        print(f"Skipping desktop export because target is repository root: {desktop_root}")
        return
    desktop_root.mkdir(parents=True, exist_ok=True)
    copy_tree(ROOT / "dist", desktop_root / "dist")
    copy_tree(ROOT / "src", desktop_root / "src")
    copy_tree(ROOT / ".claude-plugin", desktop_root / ".claude-plugin")
    shutil.copy2(ROOT / "README.md", desktop_root / "README.md")
    shutil.copy2(ROOT / "README.zh-CN.md", desktop_root / "README.zh-CN.md")
    shutil.copy2(ROOT / "LICENSE", desktop_root / "LICENSE")
    shutil.copy2(ROOT / "install.ps1", desktop_root / "install.ps1")


def sync_local_installs(args: argparse.Namespace) -> None:
    args.codex_skills_dir.mkdir(parents=True, exist_ok=True)
    args.claude_skills_dir.mkdir(parents=True, exist_ok=True)
    args.claude_commands_dir.mkdir(parents=True, exist_ok=True)
    args.openclaw_skills_dir.mkdir(parents=True, exist_ok=True)
    args.hermesagent_skills_dir.mkdir(parents=True, exist_ok=True)

    codex_source = DIST_CODEX_SKILLS if DIST_CODEX_SKILLS.exists() else None
    if codex_source:
        for skill_dir in codex_source.iterdir():
            if skill_dir.is_dir():
                copy_tree(skill_dir, args.codex_skills_dir / skill_dir.name)
    else:
        copy_tree(DIST_CODEX_SKILL, args.codex_skills_dir / "paper-spine")
    for skill_dir in DIST_CLAUDE_SKILLS.iterdir():
        if skill_dir.is_dir():
            copy_tree(skill_dir, args.claude_skills_dir / skill_dir.name)
    for command_file in DIST_CLAUDE_COMMANDS.glob("*.md"):
        shutil.copy2(command_file, args.claude_commands_dir / command_file.name)
    for skill_dir in DIST_OPENCLAW_SKILLS.iterdir():
        if skill_dir.is_dir():
            copy_tree(skill_dir, args.openclaw_skills_dir / skill_dir.name)
    for skill_dir in DIST_HERMESAGENT_SKILLS.iterdir():
        if skill_dir.is_dir():
            copy_tree(skill_dir, args.hermesagent_skills_dir / skill_dir.name)


def sync_dist_only() -> None:
    """Copy src/scripts/*.py and src/references/*.md into all dist/ copies."""
    src_scripts = ROOT / "src" / "scripts"
    src_references = ROOT / "src" / "references"
    dist_root = ROOT / "dist"

    synced = 0
    for src_file in list(src_scripts.glob("*.py")) + list(src_scripts.glob("*.sh")) + list(src_references.glob("*.md")):
        for dist_copy in dist_root.rglob(src_file.name):
            if dist_copy.is_file():
                shutil.copy2(src_file, dist_copy)
                synced += 1

    print(f"Dist-only sync complete: {synced} files updated")
    print(f"Source scripts: {src_scripts}")
    print(f"Source references: {src_references}")
    print(f"Dist root: {dist_root}")


PAPERSPINE_INTERNAL_SKILLS: set[str] = set()


def sync_skill_overrides(claude_settings_dir: Path) -> None:
    """Remove stale PaperSpine skillOverrides. All skills are now visible."""
    settings_path = claude_settings_dir / "settings.json"
    if not settings_path.exists():
        return
    try:
        existing = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    overrides = existing.get("skillOverrides", {})
    if isinstance(overrides, list):
        return

    stale = [k for k in overrides if k.startswith("paper-spine")]
    if not stale:
        return

    for skill in stale:
        del overrides[skill]
    if not overrides:
        existing.pop("skillOverrides", None)
    else:
        existing["skillOverrides"] = overrides

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Cleaned {len(stale)} stale PaperSpine skillOverrides")


def write_install_state(args: argparse.Namespace) -> None:
    manifest = json.loads(DIST_VERSION_MANIFEST.read_text(encoding="utf-8"))
    args.config_home.mkdir(parents=True, exist_ok=True)
    state = {
        "installed_version": manifest["version"],
        "installed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "repository": manifest.get("repository"),
            "channel": manifest.get("channel"),
            "manifest_url": manifest.get("manifest_url"),
            "archive_url": manifest.get("archive_url"),
        },
        "targets": ["codex", "claude", "openclaw", "hermesagent"],
        "preserved_config_path": str(args.config_home / "config.json"),
    }
    (args.config_home / "install_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sync_version_from_canonical() -> None:
    """Update plugin.json and marketplace.json version fields from the canonical version file."""
    canonical = json.loads(DIST_VERSION_MANIFEST.read_text(encoding="utf-8"))
    version = canonical["version"]

    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"

    updated = []
    for path in (plugin_path, marketplace_path):
        data = json.loads(path.read_text(encoding="utf-8"))
        if path == marketplace_path:
            for plugin in data.get("plugins", []):
                if plugin.get("version") != version:
                    plugin["version"] = version
                    updated.append(str(path.relative_to(ROOT)))
        else:
            if data.get("version") != version:
                data["version"] = version
                updated.append(str(path.relative_to(ROOT)))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if updated:
        print(f"Version synced to {version}: {', '.join(updated)}")


def main() -> int:
    args = parse_args()

    if args.dist_only:
        sync_dist_only()
        sync_version_from_canonical()
        sync_skill_overrides(Path.home() / ".claude")
        return 0

    for required in (
        DIST_CODEX_SKILL,
        DIST_CLAUDE_SKILLS,
        DIST_CLAUDE_COMMANDS,
        DIST_OPENCLAW_SKILLS,
        DIST_HERMESAGENT_SKILLS,
        DIST_VERSION_MANIFEST,
    ):
        if not required.exists():
            raise FileNotFoundError(required)

    if args.clean_legacy or args.clean_legacy_claude_nested:
        clean_legacy(args)
    sync_version_from_canonical()
    sync_desktop_export(args.desktop_root)
    sync_local_installs(args)
    sync_skill_overrides(args.claude_skills_dir.parent)
    write_install_state(args)

    print("PaperSpine local sync complete")
    print(f"Desktop dist export: {args.desktop_root / 'dist'}")
    print(f"Codex skills install: {args.codex_skills_dir}")
    print(f"Claude skills install: {args.claude_skills_dir}")
    print(f"Claude commands install: {args.claude_commands_dir}")
    print(f"OpenClaw skills install: {args.openclaw_skills_dir}")
    print(f"HermesAgent skills install: {args.hermesagent_skills_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
