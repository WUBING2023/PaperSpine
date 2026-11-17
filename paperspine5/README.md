# PaperSpine5 release source

This directory contains the public product core and release tools for
`0.4.0-alpha.4`. The canonical Skill instructions, scripts and host projections
are in the repository's `src/` and `dist/` directories.

The [release manifest](../website/downloads/manifest.json) identifies the current
Windows x64, Linux glibc x86_64, macOS arm64 and macOS x86_64 suites by build ID,
byte count and SHA-256. Installable ZIPs are hosted on
[GitHub Releases](https://github.com/WUBING2023/PaperSpine/releases/tag/v0.4.0-alpha.4).
Use the matching full platform suite for installation or repair. This release
does not offer a Skill-only ZIP; historical copies lack the runtime and Web core.
The older compatibility bridge is for V4 migration, not a current V5 download.

The original update entry remains available. Component version `4.0.1` bridges
old V4 installations to the V5 suite; it is separate from product version
`0.4.0-alpha.4`. Each Skill invocation checks the official platform channel and
updates the suite and updater when needed, respecting an explicit opt-out.
Updates retain task data and profile identity. See [UPDATE.md](../UPDATE.md).

The host Agent creates or resumes the public paper task and performs research,
writing, figures and review. Web saves configuration, choices and feedback and
displays actual results. Historical Runner job files are not startup prerequisites.
The release never authorizes external manuscript submission.

## Review rounds and V6 research methods

Use `payload.review_id` with `finding_id` to close a finding in a specific round
through MCP or the existing HTTP resolution endpoint. A request with only
`finding_id` can close a single matching open finding. Ambiguous requests return
the candidate review IDs. Older resolution events without `review_id` rebuild in
first-open order, matching the local hotfix described in [Issue #17](https://github.com/WUBING2023/PaperSpine/issues/17).

The V6 stage methods and [reproducible research intake pilot](core/01_PaperSpine4/qa/research-intake-20261115/README.md)
are part of the product source. The pilot records five reference Skills, the
data provenance, the time split and a check for target leakage.
