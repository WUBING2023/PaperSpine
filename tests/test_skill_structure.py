from __future__ import annotations

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


class SkillStructureTests(unittest.TestCase):
    def test_required_project_files_exist(self) -> None:
        required = [
            "README.md",
            "README.zh-CN.md",
            "LICENSE",
            ".gitignore",
            "install.ps1",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "src/agents/openai.yaml",
            "src/references/task-genre-research.md",
            "src/references/version-requirements.md",
            "src/scripts/latex_guard.py",
            "src/scripts/revision_audit.py",
            "src/scripts/style_metrics.py",
            "src/scripts/intake_wizard.py",
            "src/scripts/material_inventory.py",
            "src/scripts/artifact_check.py",
            "src/scripts/reference_inventory.py",
            "src/scripts/citation_bank_check.py",
            "src/scripts/word_guard.py",
            "src/scripts/sync_local_installs.py",
            "src/scripts/paperspine_update.py",
            "src/scripts/_paper_spine_utils.py",
            "src/scripts/integrity_audit.py",
            "src/scripts/citation_quality_audit.py",
            "src/scripts/structured_review.py",
            "src/scripts/translate_guard.py",
            "src/scripts/humanize_check.py",
            "dist/paperspine_version.json",
            "src/references/local-reference-ingestion.md",
            "src/references/citation-support-bank.md",
            "src/references/orchestrator-branch-map.md",
            "dist/codex/paper-spine/SKILL.md",
            "dist/codex/skills/paper-spine/SKILL.md",
            "dist/openclaw/skills/paper-spine/SKILL.md",
            "dist/hermesagent/skills/academic-writing/paper-spine/SKILL.md",
            "dist/claude/commands/paperspine.md",
        ]
        missing = [path for path in required if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_root_skill_is_absent_to_avoid_duplicate_codex_discovery(self) -> None:
        self.assertFalse((ROOT / "SKILL.md").exists())

    def test_readme_language_switch_and_content_parity(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        for text in (english, chinese):
            self.assertIn("[English](README.md)", text)
            self.assertIn("[中文](README.zh-CN.md)", text)
            for fragment in [
                "dist/codex/paper-spine",
                "dist/codex/skills",
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
                "writing_rationale_matrix.md",
                "citation_support_bank.md",
                "reference_mode",
                "translation_package",
                "artifact_check.py",
                "reference_inventory.py",
                "citation_bank_check.py",
                "latex_guard.py",
                "word_guard.py",
            ]:
                self.assertIn(fragment, text)

        english_sections = [line for line in english.splitlines() if line.startswith("## ")]
        chinese_sections = [line for line in chinese.splitlines() if line.startswith("## ")]
        self.assertEqual(len(english_sections), len(chinese_sections))

    def test_suite_skills_exist(self) -> None:
        missing = [
            name
            for name in SUITE_SKILLS
            if not (ROOT / "dist" / "claude" / "skills" / name / "SKILL.md").exists()
        ]
        self.assertEqual(missing, [])
        for host in ("codex", "openclaw"):
            missing = [
                name
                for name in SUITE_SKILLS
                if not (ROOT / "dist" / host / "skills" / name / "SKILL.md").exists()
            ]
            self.assertEqual(missing, [])
        missing = [
            name
            for name in SUITE_SKILLS
            if not (ROOT / "dist" / "hermesagent" / "skills" / "academic-writing" / name / "SKILL.md").exists()
        ]
        self.assertEqual(missing, [])

    def test_suite_support_files_exist(self) -> None:
        required = [
            "dist/claude/skills/paper-spine-intake/scripts/intake_wizard.py",
            "dist/claude/skills/paper-spine-ui/scripts/intake_wizard.py",
            "dist/claude/skills/paper-spine-ui/scripts/launch_paperspine_ui.ps1",
            "dist/claude/skills/paper-spine/scripts/intake_wizard.py",
            "dist/claude/skills/paper-spine/scripts/material_inventory.py",
            "dist/claude/skills/paper-spine/scripts/artifact_check.py",
            "dist/claude/skills/paper-spine-build/scripts/material_inventory.py",
            "dist/claude/skills/paper-spine-research/scripts/reference_inventory.py",
            "dist/claude/skills/paper-spine-citation/scripts/citation_bank_check.py",
            "dist/claude/skills/paper-spine-audit/scripts/artifact_check.py",
            "dist/claude/skills/paper-spine-audit/scripts/citation_bank_check.py",
            "dist/claude/skills/paper-spine-latex/scripts/word_guard.py",
            "dist/claude/skills/paper-spine-audit/scripts/word_guard.py",
            "dist/claude/skills/paper-spine/references/orchestrator-branch-map.md",
            "dist/claude/skills/paper-spine-research/references/flash-pro-research.md",
            "dist/claude/skills/paper-spine-research/references/local-reference-ingestion.md",
            "dist/claude/skills/paper-spine-research/references/scenario-journal.md",
            "dist/claude/skills/paper-spine-research/references/scenario-conference.md",
            "dist/claude/skills/paper-spine-research/references/scenario-report-review.md",
            "dist/claude/skills/paper-spine-research/references/scenario-competition.md",
            "dist/claude/skills/paper-spine-citation/references/citation-support-bank.md",
            "dist/claude/skills/paper-spine-build/references/build-from-materials.md",
            "dist/claude/skills/paper-spine-intake/references/interactive-intake.md",
            "dist/claude/skills/paper-spine/references/writing-rationale-matrix.md",
            "dist/claude/skills/paper-spine-audit/references/translation-package.md",
            "dist/claude/skills/paper-spine-update/scripts/paperspine_update.py",
            "dist/claude/skills/paper-spine-update/paperspine_version.json",
            "dist/codex/skills/paper-spine-citation/scripts/citation_bank_check.py",
            "dist/codex/skills/paper-spine-update/scripts/paperspine_update.py",
            "dist/codex/skills/paper-spine-research/scripts/reference_inventory.py",
            "dist/openclaw/skills/paper-spine-citation/scripts/citation_bank_check.py",
            "dist/openclaw/skills/paper-spine-update/scripts/paperspine_update.py",
            "dist/openclaw/skills/paper-spine-research/scripts/reference_inventory.py",
        ]
        missing = [path for path in required if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_no_temporary_artifact_directories(self) -> None:
        tmp_dirs = [path.name for path in ROOT.glob("tmp_*_artifacts") if path.is_dir()]
        self.assertEqual(tmp_dirs, [])

    def test_no_obvious_local_private_paths_in_reusable_files(self) -> None:
        reusable_suffixes = {".md", ".py", ".yaml", ".yml", ".txt", ".json"}
        blocked_fragments = [
            "C:" + "\\Users\\",
            "/Users/",
            "file:" + "///",
            "Bio" + "informatics",
            "M:" + "\\" + "R" + "BP" + "\\",
            "paper" + "_v",
            "oup-" + "authoring",
        ]
        offenders: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in reusable_suffixes:
                continue
            if path.name == "test_skill_structure.py":
                continue
            if path.name in ("CLAUDE.md", "AGENTS.md"):
                continue
            if ".git" in path.parts:
                continue
            if "paper_rewriting_output" in path.parts:
                continue
            if "paper-spine-promo-video" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for fragment in blocked_fragments:
                if fragment in text:
                    offenders.append(str(path.relative_to(ROOT)))
                    break
        self.assertEqual(offenders, [])

    def test_skill_metadata_files_have_no_utf8_bom(self) -> None:
        files = [ROOT / "dist" / "codex" / "paper-spine" / "SKILL.md"]
        for host in ("claude", "codex", "openclaw"):
            files.extend(ROOT / "dist" / host / "skills" / name / "SKILL.md" for name in SUITE_SKILLS)
        files.extend(
            ROOT / "dist" / "hermesagent" / "skills" / "academic-writing" / name / "SKILL.md"
            for name in SUITE_SKILLS
        )
        offenders = []
        for path in files:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])
    def test_frontmatter_description_is_portable(self) -> None:
        skill_files = []
        for host in ("claude", "codex", "openclaw"):
            skill_files.extend(ROOT / "dist" / host / "skills" / name / "SKILL.md" for name in SUITE_SKILLS)
        skill_files.extend(
            ROOT / "dist" / "hermesagent" / "skills" / "academic-writing" / name / "SKILL.md"
            for name in SUITE_SKILLS
        )
        offenders: list[str] = []
        for path in skill_files:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            description = next(line for line in lines if line.startswith("description: "))
            value = description.removeprefix("description: ").strip()
            if len(value) > 200:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

