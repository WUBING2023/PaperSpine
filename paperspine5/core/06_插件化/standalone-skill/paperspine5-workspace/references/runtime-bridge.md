# Runtime bridge

The Skill launcher resolves `PAPERSPINE5_PROJECT_ROOT`, an updater-written
`installed-suite.json`, or the development-only `local-project.json`, in that
order. It then delegates to `06_插件化/runtime/paperspine5_runtime.py` or, for
an explicitly supplied legacy job in a development checkout,
`03_联合开发/scripts/paperspine_figure.py`.

For a moved repository, either update `local-project.json` or set `PAPERSPINE5_PROJECT_ROOT`. The target
must contain `03_联合开发/src/paperspine_figure_integration/coordinator.py`.

Current HostBridge requests use protocol `paperspine5.host`, version `0.4.0`.
Product actions are `create_task`, `import_legacy_task`, `list_tasks`,
`get_task`, `command`, `open_product_workspace`, `workspace_status`, and
`stop_workspace`. Version 0.2.0 and the following actions remain legacy-only:
`snapshot`, `save_configuration`, `advance`, `record_decision`, `record_signal`, `publication_cycle`,
`manuscript_status`, `save_manuscript_revision`, `restore_manuscript_revision`,
`confirm_manuscript_revision`, `answer_user_input`, `open_workspace`.
MCP is required for the Web-first product workspace because the host process
owns reuse/status/stop and closes the Product Kernel repository handle.

The self-contained candidate includes the runtime and this standalone Skill
projection but intentionally omits the developer `local-project.json`. The
Skill updater writes `references/installed-suite.json` only in the installed
Skill projection and binds it to the verified suite build/content index. Use
`release/release_cli.py skill-update-check|skill-upgrade|skill-upgrade-rollback`.
The Skill updater never calls plugin commands or shares rollback state with the
plugin updater. Do not rewrite the pointer or marketplace metadata manually.

The managed suite root is immutable after verification. Canonical Web/MCP
launchers use Python `-B`; Python adapters also set `sys.dont_write_bytecode`
and inherited `PYTHONDONTWRITEBYTECODE=1` before any product-core import.
Adapters that delegate with `runpy` retain the resolved
`06_插件化/runtime/` directory on `sys.path` for the process lifetime, so lazy
sibling imports have the same behavior in source, candidate, and installed
suite shapes.
Background Web, legacy recovery, and Agent children retain
that environment. Runtime state belongs only under the selected user-data or
task workspace root: a normal launch, resume, or Agent run must leave the suite
path set and file hashes unchanged and create no `__pycache__`, `.pyc`, or
`.pyo` files there.
