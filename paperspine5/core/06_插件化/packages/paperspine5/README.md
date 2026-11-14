# PaperSpine 本地产品

普通用户从随安装 ZIP 提供的 **USER_GUIDE.md** 开始。唯一入口是 **paper-spine Skill**：将需求和材料交给宿主 Agent，由宿主创建或恢复同一任务、读取授权材料并实际研究写作；Web 保存配置、动机和图件选择及反馈，展示进度、预览和下载。包内 Windows 运行环境无需系统 Python。网页右上角“使用帮助”随本地服务提供；API_REFERENCE.md 面向集成者。原创练习材料在 examples/local-demo。

外部材料文件夹由宿主按实际需要取得本地读取授权；宿主在任务目录内生成的科研成果通过任务相对路径发布，无须再次授权自己的输出目录。论文经实际独立审阅后交付，用户意见在同一任务续作。以下内部插件和 Runner 说明仅保留用于兼容性排查，不是当前科研执行流程；教学示例不代表完整论文自动生成或投稿就绪。

## 历史内部 Codex plugin 参考（兼容性排查）

The source plugin interface uses the approved PaperSpine `Ridge Seal` identity:
deep-pine `brandColor`, a 64 px composer icon, 512 px light/dark logos, and the
canonical SVG under `assets/`. The deterministic suite builder allowlists these
files and verifies every manifest binding. This source statement does not claim
that the current installed plugin or the current exact candidate has already
been rebuilt or activated with the new icon.

This package is the internal MCP dispatch backend behind the one canonical
`paper-spine` user Skill; it does not advertise or ship a second plugin Skill.
Its local stdio server's 31 tools use Product Kernel create/list/get, a runtime-owned
writer, the registered ProductRunner 0.2 J1–J11 facade, and the secure
Web-first workspace. Academic gates use a dedicated issue/revision/stage-bound
JSON answer tool; `payload.input_artifacts` contains actual evidence payloads,
not a caller-supplied trusted map. Generic `runner.*` submissions and
client-selected writers are rejected; explicitly supplied legacy jobs can be
imported read-only. The package does not bundle a second paper engine or fixed
domain/venue/track rules.

The public Runner MCP schemas are sufficient for black-box J1–J3 use. `actor`
is optional at the tool boundary and, when supplied, exposes its required
members and complete surface enum. Every `configuration.required` issue
persists the same complete J3 `answer_schema` and valid guided example that
`paperspine5_runner_answer_issue` exposes in `tools/list`; Product Web displays
and fail-closed checks that contract before submission. External upload remains
locked at `network_policy.allow_external_upload=false`.

All later `academic.input.required` issues now carry the dedicated tool,
task/issue/revision/stage-specialized answer schema, a schema-valid shape
example and the false external-action lock. The generic academic MCP schema is
loaded from the same contract file, and Product Web refuses stale or missing
issue contracts before a write. J4 explicitly describes and tests the
`sources[].content_sha256` binding to actual canonical JSON at
`payload.input_artifacts["source:<source_id>"]`; directory/source-code searching
is not part of the public workflow.

For a broad or mixed materials root, the entry Skill now routes through a
bounded, read-only and non-authoritative Paper Map before task creation. The
map records scan limits/issues, role/version candidates and precise recommended
grants without copying the parent tree. It is navigation only: after selection,
ProductRunner's `paperspine5.material-source-ledger` remains the sole authority
for complete hashes, immutable snapshots, freshness and invalidation. No new
Paper Map MCP/API or readiness state is claimed by this Skill-level route.

Novelty-, priority-, and differentiation-bearing claims now route through a
provider-neutral Evidence-Backed Prior-Art Reviewer as a shadow protocol: J6
decomposes and challenges each claim against locator-bound nearest evidence,
and J9 repeats the review independently against the exact frozen revision and
input hashes. No-hit remains insufficient coverage, not novelty proof;
first/new/novel wording is blocked or narrowed under unknown coverage, and
overlap is resolved claim-locally rather than rejecting a whole manuscript by
default. This route does not add a WisPaper dependency or a typed prior-art
receipt/tool/schema/API/readiness authority.

Direction and target preferences are learned by runtime research Agents. The
adapter only carries orchestration, permissions, state, evidence, review, and
fail-closed contracts. A local `target_package_ready` task still has
`external_action_authorized=false`; W8 maturity and P0 remain blocked.

Use `python scripts/paperspine5_mcp.py health` for a no-network self-check. A
deterministic suite candidate embeds its exact 01/02/03/06 source. Only the thin
development package locates this workspace through `config/local-project.json`.
The canonical MCP registration and Product Web shell launchers invoke Python
with `-B`. The MCP adapter, Product Web launcher, runtime, legacy recovery
adapter, and compatibility bridge also set
`sys.dont_write_bytecode` plus inherited `PYTHONDONTWRITEBYTECODE=1` before any
product-core import. Because the adapters execute the shared runtime with
`runpy`, they explicitly retain the embedded runtime directory on `sys.path` for
the process lifetime; this gives lazy sibling adapters such as
`web_agent_runtime.py` the same import semantics as direct script execution.
Product Web and Agent subprocesses receive the same environment explicitly.
Normal MCP/Web/resume/Agent use therefore must preserve every path and byte of
the immutable installed suite and must not add `__pycache__`, `.pyc`, or `.pyo`
residue.

The retained source-only route document under `skills/paperspine5/` is development
evidence and is deliberately excluded from release candidates; the plugin manifest
does not advertise a `skills` root. The canonical standalone Skill exposes the
hash-bound suite update route. Plugin
check, upgrade, state, receipt, backup, activation, and rollback are separate from
the standalone Skill equivalents; no command can update or roll back both surfaces.
An update check is read-only, and an upgrade requires explicit confirmation plus
full bundle verification before the plugin source is replaced. Placement or plugin
activation failure restores the prior plugin bytes. Successful plugin activation
requires a new Codex task. This mechanism does not change maturity, readiness, or
external-action authority.

Update preflight distinguishes a strict cache, hash-bound runtime `.pyc` residue,
and unsafe drift. Only bytecode that deterministically binds to an indexed Python
source may be transactionally copied into the update control root and isolated;
the archive remains auditable and is restored on failure or explicit rollback.
Missing/changed indexed bytes, orphan or forged bytecode, any non-bytecode extra,
and link/reparse/path-escape evidence block before plugin deactivation. The updater
never treats those unknown bytes as cleanup candidates.
