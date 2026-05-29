#!/usr/bin/env python3
"""Check and update local PaperSpine installs.

The updater is deliberately self-contained and standard-library only so it can
run from Codex, Claude Code, OpenClaw, HermesAgent, or a plain terminal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/WUBING2023/PaperSpine/main/dist/paperspine_version.json"
)
DEFAULT_ARCHIVE_URL = "https://github.com/WUBING2023/PaperSpine/archive/refs/heads/main.zip"
CONFIG_HOME_ENV = "PAPERSPINE_CONFIG_HOME"
VERSION_FILE = "paperspine_version.json"
INSTALL_STATE_FILE = "install_state.json"

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


class UpdateError(RuntimeError):
    """Raised for expected updater failures."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check and update local PaperSpine installs.")
    parser.add_argument("--check-only", action="store_true", help="Only check whether an update is available.")
    parser.add_argument(
        "--target",
        choices=("all", "codex", "claude", "openclaw", "hermesagent"),
        default="all",
        help="Install target to update. Default: all.",
    )
    parser.add_argument(
        "--config-home",
        type=Path,
        default=None,
        help="Override the PaperSpine global config directory. Default: ~/.paperspine.",
    )
    parser.add_argument(
        "--repo-archive",
        default=None,
        help="Optional repo zip, repo directory, or URL. Tests can pass a local zip.",
    )
    parser.add_argument("--yes", action="store_true", help="Update without interactive confirmation.")
    return parser.parse_args()


def config_home(args: argparse.Namespace) -> Path:
    if args.config_home is not None:
        return args.config_home
    env_value = os.environ.get(CONFIG_HOME_ENV)
    if env_value:
        return Path(env_value)
    return Path.home() / ".paperspine"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise UpdateError(f"JSON root must be an object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def version_key(version: str) -> tuple[int, int, int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+))?", version.strip())
    if not match:
        raise UpdateError(f"Unsupported PaperSpine version: {version}")
    major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    rc = match.group(4)
    if rc is None:
        return (major, minor, patch, 1, 0)
    return (major, minor, patch, 0, int(rc))


def compare_versions(left: str, right: str) -> int:
    left_key = version_key(left)
    right_key = version_key(right)
    if left_key == right_key:
        return 0
    return -1 if left_key < right_key else 1


def find_local_version_file() -> Path | None:
    script_path = Path(__file__).resolve()
    candidates: list[Path] = []
    for parent in script_path.parents:
        candidates.append(parent / VERSION_FILE)
        candidates.append(parent / "dist" / VERSION_FILE)
    for path in candidates:
        if path.exists():
            return path
    return None


def local_version(config_dir: Path) -> str:
    state_path = config_dir / INSTALL_STATE_FILE
    if state_path.exists():
        state = read_json(state_path)
        version = state.get("installed_version")
        if isinstance(version, str) and version:
            return version
    version_path = find_local_version_file()
    if version_path is not None:
        data = read_json(version_path)
        version = data.get("version")
        if isinstance(version, str) and version:
            return version
    return "0.0.0"


def load_manifest_from_url(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise UpdateError(f"Unable to fetch PaperSpine manifest: {url} ({exc})") from exc
    data = json.loads(body)
    if not isinstance(data, dict):
        raise UpdateError("Remote manifest JSON root must be an object.")
    return data


def extract_zip(zip_path: Path, temp_dir: Path) -> Path:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temp_dir)
    except zipfile.BadZipFile as exc:
        raise UpdateError(f"Invalid PaperSpine archive: {zip_path}") from exc
    return find_repo_root(temp_dir)


def download_archive(url: str, temp_dir: Path) -> Path:
    archive_path = temp_dir / "paperspine-update.zip"
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            archive_path.write_bytes(response.read())
    except (urllib.error.URLError, TimeoutError) as exc:
        raise UpdateError(f"Unable to download PaperSpine archive: {url} ({exc})") from exc
    return extract_zip(archive_path, temp_dir / "extracted")


def find_repo_root(base: Path) -> Path:
    candidates = [base]
    candidates.extend(path for path in base.iterdir() if path.is_dir())
    for candidate in candidates:
        if (candidate / "dist" / VERSION_FILE).exists() and (candidate / "install.ps1").exists():
            return candidate
    raise UpdateError(f"Unable to locate PaperSpine repository root in: {base}")


def repo_root_from_archive(repo_archive: str | None, manifest: dict[str, Any], temp_dir: Path) -> Path:
    archive_value = repo_archive or str(manifest.get("archive_url") or DEFAULT_ARCHIVE_URL)
    archive_path = Path(archive_value)
    if archive_path.exists():
        if archive_path.is_dir():
            return archive_path
        return extract_zip(archive_path, temp_dir / "extracted")
    if archive_value.startswith("file://"):
        file_path = Path(urllib.request.url2pathname(archive_value.removeprefix("file://")))
        if file_path.is_dir():
            return file_path
        return extract_zip(file_path, temp_dir / "extracted")
    return download_archive(archive_value, temp_dir)


def manifest_from_archive(repo_archive: str) -> dict[str, Any]:
    archive_path = Path(repo_archive)
    with tempfile.TemporaryDirectory(prefix="paperspine-manifest-") as tmp:
        temp_dir = Path(tmp)
        if archive_path.exists() and archive_path.is_dir():
            root = archive_path
        elif archive_path.exists():
            root = extract_zip(archive_path, temp_dir / "extracted")
        elif repo_archive.startswith("file://"):
            file_path = Path(urllib.request.url2pathname(repo_archive.removeprefix("file://")))
            root = file_path if file_path.is_dir() else extract_zip(file_path, temp_dir / "extracted")
        else:
            raise UpdateError("--repo-archive must be a local path when used for manifest discovery.")
        return read_json(root / "dist" / VERSION_FILE)


def latest_manifest(args: argparse.Namespace) -> dict[str, Any]:
    if args.repo_archive:
        return manifest_from_archive(args.repo_archive)
    return load_manifest_from_url(DEFAULT_MANIFEST_URL)


def validate_repo(root: Path) -> dict[str, Any]:
    root_files = [
        "install.ps1", "install.sh", "README.md", "README.zh-CN.md",
    ]
    plugin_files = [
        ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    ]
    dist_files = [
        "dist/paperspine_version.json",
    ]
    # Dynamically discover suite skills from dist/claude/skills/
    claude_skills_dir = root / "dist" / "claude" / "skills"
    discovered_skills: list[str] = []
    if claude_skills_dir.is_dir():
        discovered_skills = [d.name for d in claude_skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

    missing: list[str] = []
    for rel in root_files + plugin_files + dist_files:
        if not (root / rel).exists():
            missing.append(rel)
    if not discovered_skills:
        missing.append("dist/claude/skills/*/SKILL.md — no skills discovered")
    if set(discovered_skills) != set(SUITE_SKILLS):
        extra = set(discovered_skills) - set(SUITE_SKILLS)
        lacking = set(SUITE_SKILLS) - set(discovered_skills)
        if extra:
            missing.append(f"Unexpected skills in dist: {', '.join(sorted(extra))}")
        if lacking:
            missing.append(f"Missing skills from dist: {', '.join(sorted(lacking))}")
    for skill in discovered_skills:
        for host in ("claude", "codex", "openclaw"):
            path = root / "dist" / host / "skills" / skill / "SKILL.md"
            if not path.exists():
                missing.append(str(path.relative_to(root)))
        hermes_path = root / "dist" / "hermesagent" / "skills" / "academic-writing" / skill / "SKILL.md"
        if not hermes_path.exists():
            missing.append(str(hermes_path.relative_to(root)))
    for cmd_name in ("paperspine.md", "paper-spine.md", "paperspine-legacy.md"):
        cmd_path = root / "dist" / "claude" / "commands" / cmd_name
        if not cmd_path.exists():
            missing.append(str(cmd_path.relative_to(root)))
    if not (root / "dist" / "codex" / "paper-spine" / "SKILL.md").exists():
        missing.append("dist/codex/paper-spine/SKILL.md")

    if missing:
        raise UpdateError("Downloaded PaperSpine package is incomplete:\n" + "\n".join(missing[:20]))
    return read_json(root / "dist" / VERSION_FILE)


def replace_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / f".{dest.name}.paperspine-update-tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def target_paths(target: str) -> dict[str, Path]:
    home = Path.home()
    paths = {
        "codex": Path(os.environ.get("PAPERSPINE_CODEX_SKILLS_DIR", home / ".codex" / "skills")),
        "claude_skills": Path(os.environ.get("PAPERSPINE_CLAUDE_SKILLS_DIR", home / ".claude" / "skills")),
        "claude_commands": Path(os.environ.get("PAPERSPINE_CLAUDE_COMMANDS_DIR", home / ".claude" / "commands")),
        "openclaw": Path(os.environ.get("PAPERSPINE_OPENCLAW_SKILLS_DIR", home / ".openclaw" / "skills")),
        "hermesagent": Path(
            os.environ.get("PAPERSPINE_HERMESAGENT_SKILLS_DIR", home / ".hermes" / "skills" / "academic-writing")
        ),
    }
    if target == "codex":
        return {"codex": paths["codex"]}
    if target == "claude":
        return {"claude_skills": paths["claude_skills"], "claude_commands": paths["claude_commands"]}
    if target == "openclaw":
        return {"openclaw": paths["openclaw"]}
    if target == "hermesagent":
        return {"hermesagent": paths["hermesagent"]}
    return paths


def target_names(target: str) -> list[str]:
    if target == "all":
        return ["codex", "claude", "openclaw", "hermesagent"]
    return [target]


def install_target(root: Path, target: str) -> list[str]:
    paths = target_paths(target)
    current_skills = {d.name for d in (root / "dist" / "claude" / "skills").iterdir() if d.is_dir()}
    current_commands = {f.name for f in (root / "dist" / "claude" / "commands").glob("*.md")}
    installed: list[str] = []

    if "codex" in paths:
        source = root / "dist" / "codex" / "skills"
        for skill_dir in source.iterdir():
            if skill_dir.is_dir():
                replace_tree(skill_dir, paths["codex"] / skill_dir.name)
        # Clean up skills no longer in dist
        if paths["codex"].exists():
            for existing in paths["codex"].iterdir():
                if existing.is_dir() and existing.name.startswith("paper-spine") and existing.name not in current_skills:
                    shutil.rmtree(existing)
        installed.append("codex")
    if "claude_skills" in paths:
        source = root / "dist" / "claude" / "skills"
        for skill_dir in source.iterdir():
            if skill_dir.is_dir():
                replace_tree(skill_dir, paths["claude_skills"] / skill_dir.name)
        # Clean up stale skills
        if paths["claude_skills"].exists():
            for existing in paths["claude_skills"].iterdir():
                if existing.is_dir() and existing.name.startswith("paper-spine") and existing.name not in current_skills:
                    shutil.rmtree(existing)
        # Install commands
        commands_source = root / "dist" / "claude" / "commands"
        paths["claude_commands"].mkdir(parents=True, exist_ok=True)
        for command_file in commands_source.glob("*.md"):
            copy_file(command_file, paths["claude_commands"] / command_file.name)
        # Clean up stale commands
        for existing in paths["claude_commands"].glob("*.md"):
            if existing.name.startswith("paperspine") and existing.name not in current_commands:
                existing.unlink()
        installed.append("claude")
    if "openclaw" in paths:
        source = root / "dist" / "openclaw" / "skills"
        for skill_dir in source.iterdir():
            if skill_dir.is_dir():
                replace_tree(skill_dir, paths["openclaw"] / skill_dir.name)
        if paths["openclaw"].exists():
            for existing in paths["openclaw"].iterdir():
                if existing.is_dir() and existing.name.startswith("paper-spine") and existing.name not in current_skills:
                    shutil.rmtree(existing)
        installed.append("openclaw")
    if "hermesagent" in paths:
        source = root / "dist" / "hermesagent" / "skills" / "academic-writing"
        for skill_dir in source.iterdir():
            if skill_dir.is_dir():
                replace_tree(skill_dir, paths["hermesagent"] / skill_dir.name)
        if paths["hermesagent"].exists():
            for existing in paths["hermesagent"].iterdir():
                if existing.is_dir() and existing.name.startswith("paper-spine") and existing.name not in current_skills:
                    shutil.rmtree(existing)
        installed.append("hermesagent")
    return installed


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


def write_install_state(config_dir: Path, manifest: dict[str, Any], targets: list[str]) -> None:
    state = {
        "installed_version": manifest["version"],
        "installed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "repository": manifest.get("repository"),
            "channel": manifest.get("channel"),
            "manifest_url": manifest.get("manifest_url", DEFAULT_MANIFEST_URL),
            "archive_url": manifest.get("archive_url", DEFAULT_ARCHIVE_URL),
        },
        "targets": targets,
        "preserved_config_path": str(config_dir / "config.json"),
    }
    write_json(config_dir / INSTALL_STATE_FILE, state)


def confirm_update(current: str, latest: str, args: argparse.Namespace) -> bool:
    if args.yes:
        return True
    if not sys.stdin.isatty():
        raise UpdateError("Update available but --yes was not provided in a non-interactive session.")
    answer = input(f"Update PaperSpine from {current} to {latest}? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def run(args: argparse.Namespace) -> int:
    config_dir = config_home(args)
    current = local_version(config_dir)
    manifest = latest_manifest(args)
    latest = str(manifest.get("version") or "")
    if not latest:
        raise UpdateError("Latest manifest does not contain a version.")

    comparison = compare_versions(current, latest)
    if comparison >= 0:
        print(f"PaperSpine is already latest: {current}")
        if comparison == 0 and not args.check_only:
            write_install_state(config_dir, manifest, target_names(args.target))
            sync_skill_overrides(Path.home() / ".claude")
        return 0

    print(f"PaperSpine update available: {current} -> {latest}")
    if args.check_only:
        return 2
    if not confirm_update(current, latest, args):
        print("PaperSpine update cancelled.")
        return 0

    with tempfile.TemporaryDirectory(prefix="paperspine-update-") as tmp:
        root = repo_root_from_archive(args.repo_archive, manifest, Path(tmp))
        package_manifest = validate_repo(root)
        package_version = str(package_manifest.get("version") or "")
        if compare_versions(package_version, latest) != 0:
            raise UpdateError(f"Archive version {package_version} does not match manifest version {latest}.")
        installed = install_target(root, args.target)
        if "claude" in installed:
            sync_skill_overrides(Path.home() / ".claude")
        write_install_state(config_dir, package_manifest, installed)
    print(f"PaperSpine updated to {latest}: {', '.join(installed)}")
    print(f"Global config preserved: {config_dir / 'config.json'}")
    return 0


def main() -> int:
    args = parse_args()
    try:
        return run(args)
    except UpdateError as exc:
        print(f"PaperSpine update failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
