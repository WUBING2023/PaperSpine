from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def frontmatter_field(text: str, field: str) -> str:
    match = re.search(rf"^{field}:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        raise AssertionError(f"Missing frontmatter field: {field}")
    return match.group(1).strip()


class SuiteHardeningTests(unittest.TestCase):
    def test_suite_skill_names_are_unique_and_match_directories(self) -> None:
        names: list[str] = []
        for skill in SUITE_SKILLS:
            text = read(f"dist/claude/skills/{skill}/SKILL.md")
            name = frontmatter_field(text, "name")
            self.assertEqual(name, skill)
            names.append(name)
        self.assertEqual(len(names), len(set(names)))

    def test_script_copies_match_root_versions(self) -> None:
        copies = {
            "src/scripts/intake_wizard.py": [
                "dist/claude/skills/paper-spine/scripts/intake_wizard.py",
                "dist/claude/skills/paper-spine-intake/scripts/intake_wizard.py",
                "dist/claude/skills/paper-spine-ui/scripts/intake_wizard.py",
                "dist/codex/paper-spine/scripts/intake_wizard.py",
                "dist/codex/skills/paper-spine/scripts/intake_wizard.py",
                "dist/codex/skills/paper-spine-intake/scripts/intake_wizard.py",
                "dist/codex/skills/paper-spine-ui/scripts/intake_wizard.py",
                "dist/openclaw/skills/paper-spine/scripts/intake_wizard.py",
                "dist/openclaw/skills/paper-spine-intake/scripts/intake_wizard.py",
                "dist/openclaw/skills/paper-spine-ui/scripts/intake_wizard.py",
            ],
            "src/scripts/launch_paperspine_ui.ps1": [
                "dist/claude/skills/paper-spine/scripts/launch_paperspine_ui.ps1",
                "dist/claude/skills/paper-spine-ui/scripts/launch_paperspine_ui.ps1",
                "dist/claude/skills/paper-spine-intake/scripts/launch_paperspine_ui.ps1",
                "dist/codex/paper-spine/scripts/launch_paperspine_ui.ps1",
                "dist/codex/skills/paper-spine/scripts/launch_paperspine_ui.ps1",
                "dist/codex/skills/paper-spine-ui/scripts/launch_paperspine_ui.ps1",
                "dist/codex/skills/paper-spine-intake/scripts/launch_paperspine_ui.ps1",
                "dist/openclaw/skills/paper-spine/scripts/launch_paperspine_ui.ps1",
                "dist/openclaw/skills/paper-spine-ui/scripts/launch_paperspine_ui.ps1",
                "dist/openclaw/skills/paper-spine-intake/scripts/launch_paperspine_ui.ps1",
            ],
            "src/scripts/launch_paperspine_ui.sh": [
                "dist/claude/skills/paper-spine/scripts/launch_paperspine_ui.sh",
                "dist/claude/skills/paper-spine-ui/scripts/launch_paperspine_ui.sh",
                "dist/claude/skills/paper-spine-intake/scripts/launch_paperspine_ui.sh",
                "dist/codex/paper-spine/scripts/launch_paperspine_ui.sh",
                "dist/codex/skills/paper-spine/scripts/launch_paperspine_ui.sh",
                "dist/codex/skills/paper-spine-ui/scripts/launch_paperspine_ui.sh",
                "dist/codex/skills/paper-spine-intake/scripts/launch_paperspine_ui.sh",
                "dist/openclaw/skills/paper-spine/scripts/launch_paperspine_ui.sh",
                "dist/openclaw/skills/paper-spine-ui/scripts/launch_paperspine_ui.sh",
                "dist/openclaw/skills/paper-spine-intake/scripts/launch_paperspine_ui.sh",
            ],
            "src/scripts/reference_inventory.py": [
                "dist/claude/skills/paper-spine-research/scripts/reference_inventory.py",
                "dist/codex/paper-spine/scripts/reference_inventory.py",
                "dist/codex/skills/paper-spine-research/scripts/reference_inventory.py",
                "dist/openclaw/skills/paper-spine-research/scripts/reference_inventory.py",
            ],
            "src/scripts/citation_bank_check.py": [
                "dist/claude/skills/paper-spine-citation/scripts/citation_bank_check.py",
                "dist/claude/skills/paper-spine-audit/scripts/citation_bank_check.py",
                "dist/codex/paper-spine/scripts/citation_bank_check.py",
                "dist/codex/skills/paper-spine-citation/scripts/citation_bank_check.py",
                "dist/codex/skills/paper-spine-audit/scripts/citation_bank_check.py",
                "dist/openclaw/skills/paper-spine-citation/scripts/citation_bank_check.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/citation_bank_check.py",
            ],
            "src/scripts/material_inventory.py": [
                "dist/claude/skills/paper-spine/scripts/material_inventory.py",
                "dist/claude/skills/paper-spine-build/scripts/material_inventory.py",
                "dist/codex/paper-spine/scripts/material_inventory.py",
                "dist/codex/skills/paper-spine/scripts/material_inventory.py",
                "dist/codex/skills/paper-spine-build/scripts/material_inventory.py",
                "dist/openclaw/skills/paper-spine/scripts/material_inventory.py",
                "dist/openclaw/skills/paper-spine-build/scripts/material_inventory.py",
            ],
            "src/scripts/artifact_check.py": [
                "dist/claude/skills/paper-spine/scripts/artifact_check.py",
                "dist/claude/skills/paper-spine-audit/scripts/artifact_check.py",
                "dist/codex/paper-spine/scripts/artifact_check.py",
                "dist/codex/skills/paper-spine/scripts/artifact_check.py",
                "dist/codex/skills/paper-spine-audit/scripts/artifact_check.py",
                "dist/openclaw/skills/paper-spine/scripts/artifact_check.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/artifact_check.py",
            ],
            "src/scripts/word_guard.py": [
                "dist/claude/skills/paper-spine-latex/scripts/word_guard.py",
                "dist/claude/skills/paper-spine-audit/scripts/word_guard.py",
                "dist/codex/paper-spine/scripts/word_guard.py",
                "dist/codex/skills/paper-spine-latex/scripts/word_guard.py",
                "dist/codex/skills/paper-spine-audit/scripts/word_guard.py",
                "dist/openclaw/skills/paper-spine-latex/scripts/word_guard.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/word_guard.py",
            ],
            "src/scripts/latex_guard.py": [
                "dist/claude/skills/paper-spine-latex/scripts/latex_guard.py",
                "dist/claude/skills/paper-spine-audit/scripts/latex_guard.py",
                "dist/codex/paper-spine/scripts/latex_guard.py",
                "dist/codex/skills/paper-spine-latex/scripts/latex_guard.py",
                "dist/codex/skills/paper-spine-audit/scripts/latex_guard.py",
                "dist/openclaw/skills/paper-spine-latex/scripts/latex_guard.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/latex_guard.py",
            ],
            "src/scripts/revision_audit.py": [
                "dist/claude/skills/paper-spine-audit/scripts/revision_audit.py",
                "dist/codex/paper-spine/scripts/revision_audit.py",
                "dist/codex/skills/paper-spine-audit/scripts/revision_audit.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/revision_audit.py",
            ],
            "src/scripts/paperspine_update.py": [
                "dist/claude/skills/paper-spine-update/scripts/paperspine_update.py",
                "dist/codex/paper-spine/scripts/paperspine_update.py",
                "dist/codex/skills/paper-spine-update/scripts/paperspine_update.py",
                "dist/openclaw/skills/paper-spine-update/scripts/paperspine_update.py",
            ],
            "src/scripts/_paper_spine_utils.py": [
                "dist/claude/skills/paper-spine/scripts/_paper_spine_utils.py",
                "dist/claude/skills/paper-spine-audit/scripts/_paper_spine_utils.py",
                "dist/claude/skills/paper-spine-citation/scripts/_paper_spine_utils.py",
                "dist/codex/paper-spine/scripts/_paper_spine_utils.py",
                "dist/codex/skills/paper-spine/scripts/_paper_spine_utils.py",
                "dist/codex/skills/paper-spine-audit/scripts/_paper_spine_utils.py",
                "dist/codex/skills/paper-spine-citation/scripts/_paper_spine_utils.py",
                "dist/openclaw/skills/paper-spine/scripts/_paper_spine_utils.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/_paper_spine_utils.py",
                "dist/openclaw/skills/paper-spine-citation/scripts/_paper_spine_utils.py",
            ],
            "src/scripts/integrity_audit.py": [
                "dist/claude/skills/paper-spine/scripts/integrity_audit.py",
                "dist/claude/skills/paper-spine-audit/scripts/integrity_audit.py",
                "dist/codex/paper-spine/scripts/integrity_audit.py",
                "dist/codex/skills/paper-spine/scripts/integrity_audit.py",
                "dist/codex/skills/paper-spine-audit/scripts/integrity_audit.py",
                "dist/openclaw/skills/paper-spine/scripts/integrity_audit.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/integrity_audit.py",
            ],
            "src/scripts/citation_quality_audit.py": [
                "dist/claude/skills/paper-spine-citation/scripts/citation_quality_audit.py",
                "dist/codex/paper-spine/scripts/citation_quality_audit.py",
                "dist/codex/skills/paper-spine-citation/scripts/citation_quality_audit.py",
                "dist/openclaw/skills/paper-spine-citation/scripts/citation_quality_audit.py",
            ],
            "src/scripts/structured_review.py": [
                "dist/claude/skills/paper-spine/scripts/structured_review.py",
                "dist/claude/skills/paper-spine-audit/scripts/structured_review.py",
                "dist/codex/paper-spine/scripts/structured_review.py",
                "dist/codex/skills/paper-spine/scripts/structured_review.py",
                "dist/codex/skills/paper-spine-audit/scripts/structured_review.py",
                "dist/openclaw/skills/paper-spine/scripts/structured_review.py",
                "dist/openclaw/skills/paper-spine-audit/scripts/structured_review.py",
            ],
            "src/scripts/humanize_check.py": [
                "dist/claude/skills/paper-spine-humanize/scripts/humanize_check.py",
                "dist/codex/paper-spine/scripts/humanize_check.py",
                "dist/codex/skills/paper-spine-humanize/scripts/humanize_check.py",
                "dist/openclaw/skills/paper-spine-humanize/scripts/humanize_check.py",
            ],
            "src/scripts/translate_guard.py": [
                "dist/claude/skills/paper-spine-translate/scripts/translate_guard.py",
                "dist/codex/paper-spine/scripts/translate_guard.py",
                "dist/codex/skills/paper-spine-translate/scripts/translate_guard.py",
                "dist/openclaw/skills/paper-spine-translate/scripts/translate_guard.py",
            ],
        }
        for source, targets in copies.items():
            source_text = read(source)
            for target in targets:
                self.assertEqual(read(target), source_text, target)

    def test_readme_documents_suite_modes_and_install_paths(self) -> None:
        text = read("README.md")
        required_fragments = [
            ".claude-plugin",
            "dist/codex/skills",
            "dist/codex/paper-spine",
            "dist/claude/skills",
            "dist/claude/commands",
            "dist/openclaw/skills",
            "dist/hermesagent/skills/academic-writing",
            "install.ps1",
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
            "flash",
            "pro",
            "journal",
            "conference",
            "report/review",
            "competition",
            "English",
            "Chinese",
            "Build From Materials",
            "word_guard.py",
            "translation_package",
            "citation_support_bank.md",
            "reference_mode",
            "main.tex",
            "Restart Codex",
            "OpenClaw",
            "HermesAgent",
            "/plugin marketplace add",
            "/plugin install paper-spine",
            "/paper-spine",
            "artifact_check.py paper_rewriting_output --markdown --write",
            "paperspine_update.py",
            "install_state.json",
            "dist/codex/paper-spine",
            "/paperspine",
        ]
        missing = [fragment for fragment in required_fragments if fragment not in text]
        self.assertEqual(missing, [])

    def test_paperspine_command_is_primary_auto_intake_entry(self) -> None:
        text = read("dist/claude/commands/paperspine.md")
        self.assertIn("description: Start PaperSpine", text)
        self.assertIn("launch the PaperSpine intake UI automatically", text)
        self.assertIn("paper_spine_config.json", text)
        self.assertIn("launch_paperspine_ui.ps1", text)
        self.assertIn("paper-spine` orchestrator", text)
        self.assertFalse((ROOT / "dist" / "claude" / "commands" / "paperspine-legacy.md").exists(),
                         "paperspine-legacy command should be removed")

    def test_claude_plugin_manifest_uses_flat_suite_skills(self) -> None:
        plugin = json.loads(read(".claude-plugin/plugin.json"))
        marketplace = json.loads(read(".claude-plugin/marketplace.json"))
        self.assertEqual(plugin["name"], "paper-spine")
        self.assertEqual(marketplace["plugins"][0]["name"], "paper-spine")
        skills = marketplace["plugins"][0]["skills"]
        expected = [f"./dist/claude/skills/{name}" for name in SUITE_SKILLS]
        self.assertEqual(skills, expected)
        self.assertTrue((ROOT / ".claude-plugin" / "plugin.json").exists())
        for skill_path in skills:
            self.assertTrue((ROOT / skill_path.removeprefix("./") / "SKILL.md").exists())

    def test_flat_suite_skill_files_match_across_hosts(self) -> None:
        for skill in SUITE_SKILLS:
            claude_dir = ROOT / "dist" / "claude" / "skills" / skill
            for host in ("codex", "openclaw"):
                host_dir = ROOT / "dist" / host / "skills" / skill
                self.assertEqual(
                    (host_dir / "SKILL.md").read_text(encoding="utf-8"),
                    (claude_dir / "SKILL.md").read_text(encoding="utf-8"),
                    f"{host}:{skill}:SKILL.md",
                )
                if skill != "paper-spine-citation":
                    self.assertTrue((host_dir / "agents" / "openai.yaml").exists(), f"{host}:{skill}:agents")
            hermes_dir = ROOT / "dist" / "hermesagent" / "skills" / "academic-writing" / skill
            self.assertEqual(
                (hermes_dir / "SKILL.md").read_text(encoding="utf-8"),
                (claude_dir / "SKILL.md").read_text(encoding="utf-8"),
                f"hermesagent:{skill}:SKILL.md",
            )
            if skill != "paper-spine-citation":
                self.assertTrue((hermes_dir / "agents" / "openai.yaml").exists(), f"hermesagent:{skill}:agents")

    def test_codex_release_layout_exposes_full_suite_and_legacy_bundle(self) -> None:
        for skill in SUITE_SKILLS:
            self.assertTrue((ROOT / "dist" / "codex" / "skills" / skill / "SKILL.md").exists(), skill)
        self.assertTrue((ROOT / "dist" / "codex" / "paper-spine" / "SKILL.md").exists())
        self.assertTrue((ROOT / "dist" / "codex" / "paper-spine" / "scripts" / "intake_wizard.py").exists())
        self.assertTrue((ROOT / "dist" / "codex" / "paper-spine" / "references" / "writing-rationale-matrix.md").exists())
        self.assertFalse((ROOT / "dist" / "codex" / "PaperSpine" / "SKILL.md").exists())
        self.assertFalse((ROOT / "dist" / "codex" / "SKILL.md").exists())

    def test_openclaw_release_layout_exposes_full_suite(self) -> None:
        for skill in SUITE_SKILLS:
            self.assertTrue((ROOT / "dist" / "openclaw" / "skills" / skill / "SKILL.md").exists(), skill)
        self.assertFalse((ROOT / "dist" / "openclaw" / "SKILL.md").exists())

    def test_hermesagent_release_layout_exposes_full_suite(self) -> None:
        for skill in SUITE_SKILLS:
            self.assertTrue(
                (ROOT / "dist" / "hermesagent" / "skills" / "academic-writing" / skill / "SKILL.md").exists(),
                skill,
            )
        self.assertFalse((ROOT / "dist" / "hermesagent" / "SKILL.md").exists())

    def test_sync_script_exports_expected_layouts_to_temp_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "desktop" / "PaperSpine" / "codex").mkdir(parents=True)
            (base / "desktop" / "PaperSpine" / "claude-code").mkdir(parents=True)
            (base / "codex" / "skills" / "PaperSpineV2").mkdir(parents=True)
            result = subprocess.run(
                [
                    sys.executable,
                    "src/scripts/sync_local_installs.py",
                    "--clean-legacy",
                    "--desktop-root",
                    str(base / "desktop" / "PaperSpine"),
                    "--codex-skills-dir",
                    str(base / "codex" / "skills"),
                    "--claude-skills-dir",
                    str(base / "claude" / "skills"),
                    "--claude-commands-dir",
                    str(base / "claude" / "commands"),
                    "--openclaw-skills-dir",
                    str(base / "openclaw" / "skills"),
                    "--hermesagent-skills-dir",
                    str(base / "hermesagent" / "skills" / "academic-writing"),
                    "--config-home",
                    str(base / "config"),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "codex" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "codex" / "skills" / "paper-spine-research" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / ".claude-plugin" / "plugin.json").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "claude" / "commands" / "paperspine.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "claude" / "commands" / "paperspine.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "claude" / "skills" / "paper-spine-ui" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "claude" / "skills" / "paper-spine-citation" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "openclaw" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "dist" / "hermesagent" / "skills" / "academic-writing" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "src" / "scripts" / "intake_wizard.py").exists())
            self.assertTrue((base / "desktop" / "PaperSpine" / "install.ps1").exists())
            self.assertFalse((base / "desktop" / "PaperSpine" / "SKILL.md").exists())
            self.assertFalse((base / "codex" / "skills" / "PaperSpine").exists())
            self.assertTrue((base / "codex" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "codex" / "skills" / "paper-spine-research" / "SKILL.md").exists())
            self.assertTrue((base / "codex" / "skills" / "paper-spine-citation" / "SKILL.md").exists())
            self.assertTrue((base / "claude" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "openclaw" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "openclaw" / "skills" / "paper-spine-audit" / "SKILL.md").exists())
            self.assertTrue((base / "openclaw" / "skills" / "paper-spine-update" / "SKILL.md").exists())
            self.assertTrue((base / "hermesagent" / "skills" / "academic-writing" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "hermesagent" / "skills" / "academic-writing" / "paper-spine-update" / "SKILL.md").exists())
            self.assertTrue((base / "claude" / "commands" / "paperspine.md").exists())
            self.assertFalse((base / "claude" / "commands" / "paperspine-legacy.md").exists())
            self.assertTrue((base / "config" / "install_state.json").exists())
            self.assertFalse((base / "desktop" / "PaperSpine" / "codex").exists())
            self.assertFalse((base / "desktop" / "PaperSpine" / "claude-code").exists())
            self.assertFalse((base / "codex" / "skills" / "PaperSpineV2").exists())
            self.assertFalse((base / "claude" / "skills" / "PaperSpineV2" / "skills" / "paper-spine" / "SKILL.md").exists())

    def test_sync_skill_overrides_cleans_stale_entries(self) -> None:
        import tempfile
        sys.path.insert(0, str(ROOT / "src" / "scripts"))
        from sync_local_installs import sync_skill_overrides, PAPERSPINE_INTERNAL_SKILLS
        with tempfile.TemporaryDirectory() as tmp:
            settings_dir = Path(tmp) / ".claude"
            settings_dir.mkdir(parents=True)
            stale = {"skillOverrides": {"paper-spine": "off", "paper-spine-research": "off"}, "model": "test"}
            (settings_dir / "settings.json").write_text(json.dumps(stale))
            sync_skill_overrides(settings_dir)
            updated = json.loads((settings_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertNotIn("skillOverrides", updated)  # all stale entries removed, key also removed
            self.assertEqual(updated["model"], "test")

    def test_sync_skill_overrides_noop_on_no_paperspine_overrides(self) -> None:
        import tempfile
        sys.path.insert(0, str(ROOT / "src" / "scripts"))
        from sync_local_installs import sync_skill_overrides
        with tempfile.TemporaryDirectory() as tmp:
            settings_dir = Path(tmp) / ".claude"
            settings_dir.mkdir(parents=True)
            existing = {"permissions": {"defaultMode": "acceptEdits"}, "model": "claude-sonnet-4-6"}
            (settings_dir / "settings.json").write_text(json.dumps(existing))
            sync_skill_overrides(settings_dir)
            updated = json.loads((settings_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(updated["permissions"]["defaultMode"], "acceptEdits")
            self.assertEqual(updated["model"], "claude-sonnet-4-6")

    def test_sync_script_does_not_delete_source_when_desktop_root_is_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "src/scripts/sync_local_installs.py",
                    "--desktop-root",
                    str(ROOT),
                    "--codex-skills-dir",
                    str(base / "codex" / "skills"),
                    "--claude-skills-dir",
                    str(base / "claude" / "skills"),
                    "--claude-commands-dir",
                    str(base / "claude" / "commands"),
                    "--openclaw-skills-dir",
                    str(base / "openclaw" / "skills"),
                    "--hermesagent-skills-dir",
                    str(base / "hermesagent" / "skills" / "academic-writing"),
                    "--config-home",
                    str(base / "config"),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((ROOT / "README.md").exists())
            self.assertTrue((base / "codex" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "codex" / "skills" / "paper-spine-research" / "SKILL.md").exists())
            self.assertTrue((base / "claude" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "openclaw" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "hermesagent" / "skills" / "academic-writing" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((base / "config" / "install_state.json").exists())

    def test_gitignore_blocks_user_and_generated_artifacts(self) -> None:
        text = read(".gitignore")
        required_fragments = [
            "paper_rewriting_output/",
            "tmp_*_artifacts/",
            "*.aux",
            "*.log",
            "*.docx",
            "*.pdf",
        ]
        missing = [fragment for fragment in required_fragments if fragment not in text]
        self.assertEqual(missing, [])

    def test_plugin_root_has_no_top_level_skill_to_avoid_duplicate_discovery(self) -> None:
        self.assertFalse((ROOT / "SKILL.md").exists())
        self.assertTrue((ROOT / ".claude-plugin" / "plugin.json").exists())
        self.assertTrue((ROOT / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md").exists())
        for legacy_root in ["codex", "skills", "commands", "scripts", "references"]:
            self.assertFalse((ROOT / legacy_root).exists(), legacy_root)

    def test_suite_install_layout_can_be_copied_to_temp_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            dest.mkdir()
            for skill in SUITE_SKILLS:
                shutil.copytree(ROOT / "dist" / "claude" / "skills" / skill, dest / skill)
            missing = [
                skill
                for skill in SUITE_SKILLS
                if not (dest / skill / "SKILL.md").exists()
            ]
            self.assertEqual(missing, [])
            self.assertTrue((dest / "paper-spine-intake" / "scripts" / "intake_wizard.py").exists())
            self.assertTrue((dest / "paper-spine-research" / "references" / "scenario-journal.md").exists())
            self.assertTrue((dest / "paper-spine-citation" / "scripts" / "citation_bank_check.py").exists())
            self.assertTrue((dest / "paper-spine-ui" / "scripts" / "launch_paperspine_ui.ps1").exists())
            self.assertTrue((dest / "paper-spine-update" / "scripts" / "paperspine_update.py").exists())

    def test_plugin_layout_can_be_copied_to_temp_project_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "paper-spine"
            dest.mkdir()
            for name in ["README.md", "README.zh-CN.md", "LICENSE", ".gitignore", "install.ps1"]:
                shutil.copy2(ROOT / name, dest / name)
            shutil.copytree(ROOT / ".claude-plugin", dest / ".claude-plugin")
            shutil.copytree(ROOT / "dist", dest / "dist")
            shutil.copytree(ROOT / "src", dest / "src")
            self.assertFalse((dest / "SKILL.md").exists())
            self.assertTrue((dest / ".claude-plugin" / "plugin.json").exists())
            self.assertTrue((dest / "src" / "references" / "task-genre-research.md").exists())
            self.assertTrue((dest / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md").exists())
            self.assertTrue((dest / "src" / "scripts" / "intake_wizard.py").exists())
            self.assertTrue((dest / "src" / "scripts" / "launch_paperspine_ui.ps1").exists())
            self.assertTrue((dest / "dist" / "codex" / "skills" / "paper-spine-citation" / "SKILL.md").exists())
            self.assertTrue((dest / "dist" / "openclaw" / "skills" / "paper-spine-citation" / "SKILL.md").exists())
            self.assertTrue((dest / "dist" / "hermesagent" / "skills" / "academic-writing" / "paper-spine-citation" / "SKILL.md").exists())
            self.assertTrue((dest / "dist" / "paperspine_version.json").exists())


if __name__ == "__main__":
    unittest.main()


