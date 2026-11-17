# Updating PaperSpine5

On Skill invocation, run `python scripts/paperspine_update.py --preflight --yes`.
It checks the current platform channel, skips an already-current installation,
and upgrades the suite and updater together. Explicit opt-out remains effective.

For an old install, rerun the latest platform installer or use the unchanged
protocol-v1 updater with `update-channel-<platform>.json`. The new installed
preflight completes old bootstrap refresh. V4 4.0.0 users receive compatibility
4.0.1 through their original component updater, then the invocation preflight
selects V5 0.4.0-alpha.4 for the current OS. An alpha.2 installation whose
Skill lacks `references/installed-suite.json` must run the alpha.3 platform
installer against the same profile; the old Skill-only preflight cannot prove
that installation's suite identity. These version sequences are separate.

Local task files and saved profiles are retained. Reload the host Skill and
restart an old Web process at a saved boundary, using the same profile. A Web
save does not wake an ended host conversation; use its continuation prompt.
