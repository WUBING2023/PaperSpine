from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# V4: a single 'paper-spine' skill replaces B's 12-skill flat suite.
# These are the four host copies of the one skill's SKILL.md.
SKILL_COPIES = [
    ROOT / "src" / "skill" / "SKILL.md",
    ROOT / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md",
    ROOT / "dist" / "codex" / "skills" / "paper-spine" / "SKILL.md",
    ROOT / "dist" / "openclaw" / "skills" / "paper-spine" / "SKILL.md",
    ROOT / "dist" / "hermes" / "skills" / "academic-writing" / "paper-spine" / "SKILL.md",
]


class SkillStructureTests(unittest.TestCase):
    def test_required_project_files_exist(self) -> None:
        required = [
            "README.md",
            "README.en.md",
            "LICENSE",
            ".gitignore",
            "install.ps1",
            "install.sh",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            # Single-skill source layout.
            "src/skill/SKILL.md",
            "src/skill/agents/openai.yaml",
            "src/skill/references/task-genre-research.md",
            "src/skill/references/version-requirements.md",
            "src/skill/references/orchestrator-branch-map.md",
            "src/skill/references/product-runner-host-route.md",
            "src/skill/references/semantic-confirmation.md",
            "src/skill/references/local-reference-ingestion.md",
            "src/skill/references/citation-support-bank.md",
            "src/skill/references/writing-rationale-matrix.md",
            "src/skill/references/scientific-evidence-ledger.md",
            "src/skill/references/visual-readiness-gate.md",
            "src/skill/references/figure-story.md",
            "src/skill/references/submission-metadata.md",
            "src/skill/references/usage-telemetry.md",
            "src/skill/references/phase-contracts.md",
            "src/skill/references/execution-efficiency.md",
            "src/skill/references/publication-surface.md",
            "src/skill/references/publication-cycle.md",
            "src/skill/references/publication-cycle-interface.md",
            "src/skill/references/open-release.md",
            "src/skill/references/open-release-interface.md",
            "src/skill/references/open-release-platforms.json",
            "src/skill/references/contracts/publication-cycle-invocation.schema.json",
            "src/skill/references/contracts/publication-cycle-result.schema.json",
            "src/skill/references/contracts/open-release-invocation.schema.json",
            "src/skill/references/contracts/open-release-plan.schema.json",
            "src/skill/references/contracts/open-release-manifest.schema.json",
            "src/skill/references/contracts/open-release-confirmation.schema.json",
            "src/skill/references/contracts/open-release-agent-ticket.schema.json",
            "src/skill/references/contracts/open-release-platform-receipts.schema.json",
            "src/skill/references/contracts/open-release-result.schema.json",
            "src/skill/references/contracts/author-voice-profile.schema.json",
            "src/skill/references/contracts/author-voice-restoration.schema.json",
            "src/skill/references/contracts/author-voice-receipt.schema.json",
            "src/skill/references/contracts/skill-discovery-migration.schema.json",
            "src/skill/references/publication-target-profile.md",
            "src/skill/references/publication-cycle-contracts.md",
            "src/skill/references/asset-selection.md",
            "src/skill/references/contracts/asset-selection-request.schema.json",
            "src/skill/references/adaptive-shadow.md",
            "src/skill/references/contracts/adaptive-shadow-request.schema.json",
            "src/skill/references/contracts/adaptive-shadow-result.schema.json",
            "src/skill/references/contracts/publication-target-profile.schema.json",
            "src/skill/references/contracts/submission-package-plan.schema.json",
            "src/skill/references/contracts/supplement-evidence-index.schema.json",
            "src/skill/references/supplement-evidence-index.md",
            "src/skill/references/journal-transfer.md",
            "src/skill/references/submission.md",
            "src/skill/references/respond.md",
            "src/skill/references/review-policy.md",
            "src/skill/references/assertive-scientific-writing.md",
            # Single-source scripts (B carry-overs).
            "src/scripts/latex_guard.py",
            "src/scripts/revision_audit.py",
            "src/scripts/style_metrics.py",
            "src/scripts/intake_wizard.py",
            "src/scripts/material_inventory.py",
            "src/scripts/asset_selection.py",
            "src/scripts/adaptive_shadow.py",
            "src/scripts/artifact_check.py",
            "src/scripts/reference_inventory.py",
            "src/scripts/citation_bank_check.py",
            "src/scripts/word_guard.py",
            "src/scripts/sync_local_installs.py",
            "src/scripts/skill_discovery_migration.py",
            "src/scripts/paperspine5_web.py",
            "src/scripts/paperspine_update.py",
            "src/scripts/_paper_spine_utils.py",
            "src/scripts/integrity_audit.py",
            "src/scripts/citation_quality_audit.py",
            "src/scripts/structured_review.py",
            "src/scripts/translate_guard.py",
            "src/scripts/humanize_check.py",
            "src/scripts/author_voice_check.py",
            # New V4 stage scripts.
            "src/scripts/progress_check.py",
            "src/scripts/submission_check.py",
            "src/scripts/respond_check.py",
            "src/scripts/citation_verification_en.py",
            "src/scripts/contribution_check.py",
            "src/scripts/results_validation_check.py",
            "src/scripts/reviewer_audit_check.py",
            "src/scripts/scientific_evidence_check.py",
            "src/scripts/visual_readiness_check.py",
            "src/scripts/figure_story_check.py",
            "src/scripts/metadata_readiness_check.py",
            "src/scripts/publication_surface_check.py",
            "src/scripts/usage_ledger.py",
            "src/scripts/execution_receipt.py",
            "src/scripts/publication_cycle.py",
            "src/scripts/supplement_evidence_index.py",
            "src/scripts/open_release.py",
            # Versioned distribution metadata + the four host copies.
            "dist/paperspine_version.json",
            "dist/claude/skills/paper-spine/SKILL.md",
            "dist/codex/skills/paper-spine/SKILL.md",
            "dist/codex/prompts/paperspine.md",
            "dist/openclaw/skills/paper-spine/SKILL.md",
            "dist/hermes/skills/academic-writing/paper-spine/SKILL.md",
            "dist/claude/commands/paperspine.md",
        ]
        missing = [path for path in required if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_references_directory_has_enough_playbooks(self) -> None:
        refs = list((ROOT / "src" / "skill" / "references").glob("*.md"))
        self.assertGreater(len(refs), 30)

    def test_author_voice_contract_schemas_parse(self) -> None:
        import json

        contracts = ROOT / "src" / "skill" / "references" / "contracts"
        expected_titles = {
            "author-voice-profile.schema.json": "PaperSpine authorized author-voice profile",
            "author-voice-restoration.schema.json": "PaperSpine authorial-voice restoration revision contract",
            "author-voice-receipt.schema.json": "PaperSpine authorial-voice restoration validation receipt",
        }
        for name, title in expected_titles.items():
            payload = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(payload["title"], title)

    def test_skill_discovery_migration_contract_schema_parses(self) -> None:
        import json

        path = (
            ROOT
            / "src"
            / "skill"
            / "references"
            / "contracts"
            / "skill-discovery-migration.schema.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(payload["properties"]["canonical_skill"]["const"], "paper-spine")
        self.assertEqual(payload["properties"]["external_action_authorized"]["const"], False)

    def test_distribution_and_plugin_match_canonical_version(self) -> None:
        import json

        canonical = json.loads((ROOT / "src" / "paperspine_version.json").read_text(encoding="utf-8"))
        self.assertRegex(canonical["version"], r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
        data = json.loads((ROOT / "dist" / "paperspine_version.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], canonical["version"])

        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], canonical["version"])

    def test_root_skill_is_absent_to_avoid_duplicate_codex_discovery(self) -> None:
        self.assertFalse((ROOT / "SKILL.md").exists())

    def test_single_skill_distribution_layout(self) -> None:
        # All host copies present; no legacy worker dirs remain anywhere.
        for path in SKILL_COPIES:
            self.assertTrue(path.exists(), f"missing skill copy: {path}")

        legacy_workers = [
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
        offenders: list[str] = []
        for skills_root in ROOT.glob("dist/*/skills"):
            for worker in legacy_workers:
                if (skills_root / worker).exists():
                    offenders.append(str((skills_root / worker).relative_to(ROOT)))
        # Hermes nests under an extra category directory.
        for worker in legacy_workers:
            nested = ROOT / "dist" / "hermes" / "skills" / "academic-writing" / worker
            if nested.exists():
                offenders.append(str(nested.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_readme_language_switch_and_content_parity(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        former_english_entry = (ROOT / "README.en.md").read_text(encoding="utf-8")

        self.assertIn("[中文](README.zh-CN.md)", english)
        self.assertIn("[English](README.md)", chinese)
        self.assertIn("[English](README.md)", former_english_entry)
        for text in (english, chinese):
            for fragment in [
                "dist/codex/skills",
                "dist/claude/skills",
                "dist/claude/commands",
                "dist/openclaw/skills",
                "install.ps1",
                "install.sh",
                "paper-spine",
                "writing_rationale_matrix",
                "citation_support_bank",
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
        english_downloads = set(re.findall(r"https://[^\s)]+/releases/download/[^\s)]+\.zip", english))
        chinese_downloads = set(re.findall(r"https://[^\s)]+/releases/download/[^\s)]+\.zip", chinese))
        self.assertEqual(len(english_downloads), 3)
        self.assertEqual(english_downloads, chinese_downloads)

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
        ]
        # Match the private directory, not the public OUP document-class name.
        private_directory = re.compile(r"[/\\]oup-authoring[/\\]", re.IGNORECASE)
        offenders: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in reusable_suffixes:
                continue
            if path.name == "test_skill_structure.py":
                continue
            if path.name in ("CLAUDE.md", "AGENTS.md"):
                continue
            if path.name.endswith("_ATLAS_HANDOFF.md"):
                # Repository-local governance evidence is intentionally allowed
                # to name the concrete project; it is not shipped as reusable
                # skill content.
                continue
            if path.parent == ROOT and path.name.startswith("ATLAS-HANDOFF-") and path.suffix == ".md":
                # Root component handoffs are local evidence, not shipped Skill
                # content. Keep the private-path scan active throughout src/dist.
                continue
            if ".git" in path.parts:
                continue
            if "paper_rewriting_output" in path.parts:
                continue
            if "paper-spine-promo-video" in path.parts:
                continue
            if "runtime_vendor" in path.parts:
                # The bundled interpreter is executable product payload, not
                # reusable Skill text; its dependency sources may contain
                # platform-specific paths.
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if private_directory.search(text):
                offenders.append(str(path.relative_to(ROOT)))
                continue
            for fragment in blocked_fragments:
                if fragment in text:
                    offenders.append(str(path.relative_to(ROOT)))
                    break
        self.assertEqual(offenders, [])

    def test_no_control_char_corruption_in_text_files(self) -> None:
        # Guards against escaping bugs that mangle backslash content while
        # authoring SKILL.md/references (e.g. "\r"->CR, "\a"->BEL), which silently
        # corrupts LaTeX command guidance like \ref/\autoref. Scans src/ + dist/.
        text_suffixes = {".md", ".py", ".sh", ".ps1", ".json", ".yaml", ".yml", ".toml"}
        control_chars = ("\a", "\b", "\f", "\v")
        offenders: list[str] = []
        for base in ("src", "dist"):
            for path in (ROOT / base).rglob("*"):
                if not path.is_file() or path.suffix.lower() not in text_suffixes:
                    continue
                if "__pycache__" in path.parts:
                    continue
                if ".git" in path.parts or "paper_rewriting_output" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(ch in text for ch in control_chars):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_skill_metadata_files_have_no_utf8_bom(self) -> None:
        offenders = []
        for path in SKILL_COPIES:
            data = path.read_bytes()
            if data.startswith(b"\xef\xbb\xbf"):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_frontmatter_description_is_portable(self) -> None:
        # The single paper-spine SKILL.md (claude copy and its siblings) must keep
        # a portable description <= 200 chars.
        offenders: list[str] = []
        for path in SKILL_COPIES:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            description = next(line for line in lines if line.startswith("description: "))
            value = description.removeprefix("description: ").strip()
            if len(value) > 200:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_entrypoint_playbooks_are_packaged_for_each_host(self) -> None:
        text = (ROOT / "src" / "skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 320)
        # Invocation updates, stage read-back and partial material failures add
        # explicit host obligations; retain the 320-line and bounded byte budget.
        self.assertLessEqual(len(text.encode("utf-8")), 24_000)
        self.assertNotIn("python scripts/artifact_check.py", text)
        self.assertNotIn("python scripts/word_guard.py", text)
        reference_links = set(re.findall(r"\]\((references/[^)#]+)(?:#[^)]+)?\)", text))
        self.assertTrue(reference_links)
        for copy in SKILL_COPIES:
            for link in reference_links:
                with self.subTest(host=str(copy.parent), reference=link):
                    source = ROOT / "src" / "skill" / link
                    packaged = copy.parent / link
                    self.assertTrue(packaged.is_file(), str(packaged))
                    self.assertEqual(packaged.read_bytes(), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
