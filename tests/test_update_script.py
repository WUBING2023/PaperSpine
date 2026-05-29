from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "scripts" / "paperspine_update.py"
SUITE_SKILLS = [
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
]


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_repo(root: Path, version: str, *, broken: bool = False) -> Path:
    manifest = {
        "version": version,
        "channel": "main",
        "repository": "https://github.com/WUBING2023/PaperSpine",
        "manifest_url": "https://raw.githubusercontent.com/WUBING2023/PaperSpine/main/dist/paperspine_version.json",
        "archive_url": "https://github.com/WUBING2023/PaperSpine/archive/refs/heads/main.zip",
    }
    write_json(root / "dist" / "paperspine_version.json", manifest)
    write_json(root / ".claude-plugin" / "plugin.json", {"name": "paper-spine", "version": version})
    write_json(root / ".claude-plugin" / "marketplace.json", {"plugins": [{"name": "paper-spine"}]})
    (root / "install.ps1").write_text("# installer\n", encoding="utf-8")
    (root / "install.sh").write_text("#!/bin/bash\n# installer\n", encoding="utf-8")
    (root / "README.md").write_text("# PaperSpine\n", encoding="utf-8")
    (root / "README.zh-CN.md").write_text("# PaperSpine\n", encoding="utf-8")
    (root / "dist" / "claude" / "commands").mkdir(parents=True)
    for cmd_name in ("paperspine.md", "paper-spine.md", "paperspine-legacy.md"):
        (root / "dist" / "claude" / "commands" / cmd_name).write_text(
            f"---\ndescription: {cmd_name}\n---\n", encoding="utf-8")
    (root / "dist" / "codex" / "paper-spine").mkdir(parents=True)
    (root / "dist" / "codex" / "paper-spine" / "SKILL.md").write_text(
        "---\nname: paper-spine\ndescription: legacy\n---\n",
        encoding="utf-8",
    )
    skills = SUITE_SKILLS[:-1] if broken else SUITE_SKILLS
    for host in ("claude", "codex", "openclaw"):
        for skill in skills:
            skill_dir = root / "dist" / host / "skills" / skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: {skill}\n---\n",
                encoding="utf-8",
            )
    for skill in skills:
        skill_dir = root / "dist" / "hermesagent" / "skills" / "academic-writing" / skill
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: {skill}\n---\n",
            encoding="utf-8",
        )
    return root


def zip_repo(repo_root: Path, archive_path: Path) -> Path:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in repo_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(repo_root.parent))
    return archive_path


class PaperSpineUpdateScriptTests(unittest.TestCase):
    def run_updater(self, base: Path, archive: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "PAPERSPINE_CODEX_SKILLS_DIR": str(base / "codex" / "skills"),
                "PAPERSPINE_CLAUDE_SKILLS_DIR": str(base / "claude" / "skills"),
                "PAPERSPINE_CLAUDE_COMMANDS_DIR": str(base / "claude" / "commands"),
                "PAPERSPINE_OPENCLAW_SKILLS_DIR": str(base / "openclaw" / "skills"),
                "PAPERSPINE_HERMESAGENT_SKILLS_DIR": str(base / "hermesagent" / "skills" / "academic-writing"),
            }
        )
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo-archive",
                str(archive),
                "--config-home",
                str(base / "config"),
                *extra,
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_already_latest_check_only_does_not_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = create_repo(base / "PaperSpine-main", "2.0.0-rc.3")
            archive = zip_repo(repo, base / "paperspine.zip")
            write_json(base / "config" / "install_state.json", {"installed_version": "2.0.0-rc.3"})
            result = self.run_updater(base, archive, "--check-only")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("already latest", result.stdout)
            self.assertFalse((base / "codex" / "skills" / "paper-spine" / "SKILL.md").exists())

    def test_updates_from_local_archive_and_preserves_global_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = create_repo(base / "PaperSpine-main", "2.0.0-rc.3")
            archive = zip_repo(repo, base / "paperspine.zip")
            write_json(base / "config" / "install_state.json", {"installed_version": "2.0.0-rc.2"})
            config = {"ui_language": "zh"}
            write_json(base / "config" / "config.json", config)
            result = self.run_updater(base, archive, "--yes")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((base / "codex" / "skills" / "paper-spine-update" / "SKILL.md").exists())
            self.assertTrue((base / "claude" / "skills" / "paper-spine-update" / "SKILL.md").exists())
            self.assertTrue((base / "claude" / "commands" / "paperspine.md").exists())
            self.assertTrue((base / "openclaw" / "skills" / "paper-spine-update" / "SKILL.md").exists())
            self.assertTrue((base / "hermesagent" / "skills" / "academic-writing" / "paper-spine-update" / "SKILL.md").exists())
            self.assertEqual(json.loads((base / "config" / "config.json").read_text(encoding="utf-8")), config)
            state = json.loads((base / "config" / "install_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["installed_version"], "2.0.0-rc.3")
            self.assertEqual(state["targets"], ["codex", "claude", "openclaw", "hermesagent"])

    def test_broken_archive_fails_without_overwriting_existing_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = create_repo(base / "PaperSpine-main", "2.0.0-rc.3", broken=True)
            archive = zip_repo(repo, base / "paperspine.zip")
            write_json(base / "config" / "install_state.json", {"installed_version": "2.0.0-rc.2"})
            existing = base / "codex" / "skills" / "paper-spine" / "SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("old install\n", encoding="utf-8")
            result = self.run_updater(base, archive, "--yes")
            self.assertEqual(result.returncode, 1)
            self.assertIn("incomplete", result.stderr)
            self.assertEqual(existing.read_text(encoding="utf-8"), "old install\n")

    def test_check_only_with_update_available_returns_two_and_does_not_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = create_repo(base / "PaperSpine-main", "2.0.0")
            archive = zip_repo(repo, base / "paperspine.zip")
            write_json(base / "config" / "install_state.json", {"installed_version": "2.0.0-rc.2"})
            result = self.run_updater(base, archive, "--check-only")
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertIn("update available", result.stdout)
            self.assertFalse((base / "codex" / "skills" / "paper-spine" / "SKILL.md").exists())

    def test_final_version_compares_higher_than_rc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = create_repo(base / "PaperSpine-main", "2.0.0")
            archive = zip_repo(repo, base / "paperspine.zip")
            write_json(base / "config" / "install_state.json", {"installed_version": "2.0.0-rc.9"})
            result = self.run_updater(base, archive, "--yes")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            state = json.loads((base / "config" / "install_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["installed_version"], "2.0.0")


if __name__ == "__main__":
    unittest.main()
