# Version Requirement Carry-Forward

Use this when creating numbered manuscript versions such as V8, V9, or V10.

## Rule

Each version must have `paper_rewriting_output/special_requirements.md`. The next version must read the previous version's file before rewriting. Active requirements are inherited unless the user explicitly modifies, retires, or overrides them.

If the previous version has no file, infer the first one from:

1. the user's explicit requests in the conversation,
2. the previous version's `research_report.md`,
3. the previous version's `logic_transfer_audit.md`,
4. visible manuscript decisions.

Do not treat these requirements as style preferences. They are project memory.

## Template

```markdown
# Special Requirements

## Version

- Current version:
- Previous version read:
- Last updated:

## Active Requirements To Carry Forward

| ID | Requirement | Source | Scope | Rationale | Status |
|---|---|---|---|---|---|
| SR-001 | | user / inherited / audit | manuscript / section / figure / wording | | active |

## New Requirements Added In This Version

| ID | Requirement | Source | Scope | Rationale | Status |
|---|---|---|---|---|---|

## Retired Or Overridden Requirements

| ID | Requirement | Reason | Replacement |
|---|---|---|---|

## Before Next Version

The next version must read this file first and either carry forward, edit, or explicitly retire each active requirement.
```

## Common Requirement Types

- Do not include a weak analysis in the main text; move it to Supplementary material.
- Do not over-explain a dataset-processing detail; use the approved concise wording.
- Do not claim data, code, or models are public until stable URLs/DOIs are supplied.
- Keep a specific motivation as the paper spine.
- Preserve a specific figure order, section order, or title direction.
- Avoid a claim-strength pattern such as causal language, universal superiority, or exact deltas not supported by evidence.
