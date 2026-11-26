"use strict";

// The public task projection and user decisions drive this view. The host owns
// scholarly work; there are no Runner mutations or client-side stage transitions.
const PHASES = [
  ["intake", "配置与材料", "Setup"], ["research", "研究", "Research"], ["contribution", "动机与贡献", "Motivation"],
  ["evidence", "证据", "Evidence"], ["draft", "主稿", "Draft"], ["figure", "图件", "Figures"],
  ["review", "审阅", "Review"], ["delivery", "交付", "Delivery"],
];
const UI_LANG_KEY = "paperspine5.ui-lang.v1";
let uiLang = (() => {
  try { return globalThis.localStorage?.getItem(UI_LANG_KEY) === "en" ? "en" : "zh"; } catch (_) { return "zh"; }
})();
const UI_EN = {
  "收起任务栏": "Hide tasks",
  "展开任务栏": "Show tasks",
  "审阅与返修记录": "Review and revisions",
  "当前稿件与核查材料": "Current manuscript and review materials",
  "历史稿件与核查材料": "Earlier manuscripts and review materials",
  "正式审阅结论尚未登记": "No formal review verdict recorded",
  "已保存的返修意见": "Saved revision requests",
  "正在加载 Markdown…": "Loading Markdown…",
  "Markdown 无法读取，可打开原文件。": "Could not read Markdown. Open the original file to view it.",
  "全屏阅读": "Expand reader",
  "正在加载 Word…": "Loading Word document…",
  "Word 预览无法加载，请下载原文件。": "Could not load the Word preview. Download the original file.",
  "适合窗口 · 滚动翻页": "Fit page · scroll to turn pages",
  "此文件可打开原 PDF 阅读。": "Open the original PDF to read this file.",
  "使用文档": "Docs",
  "正在连接": "Connecting",
  "正在读取本机服务…": "Checking local server…",
  "本机服务已连接 · AI 状态未确认": "Local connected · AI idle",
  "配置与文件保存在本机": "Saved locally",
  "连接未完成": "Disconnected",
  "论文流程": "Workflow",
  "收起": "Hide",
  "展开": "Show",
  "收起 Spine": "Hide Spine",
  "展开 Spine": "Show Spine",
  "等待任务": "Waiting for task",
  "当前论文": "Current paper",
  "当前任务": "Active task",
  "论文任务名称": "Task title",
  "材料文件夹路径": "Material roots",
  "论文任务": "Tasks",
  "继续你的论文工作": "Resume your research paper",
  "回到最近保存的阶段，或从 Codex 开始一篇论文。": "Pick up from your last saved stage, or launch a new paper from Codex.",
  "最近任务": "Recent task",
  "打开最近任务": "Open recent task",
  "打开已保存的工作区后，可查看继续指令。": "Open a saved workspace to view host continuation prompts.",
  "从 Codex 开始": "Start from Codex",
  "在 Codex 运行 PaperSpine Web 技能，再打开它给出的任务链接。": "Run the PaperSpine Web skill in Codex, then open the task URL it provides.",
  "查看启动命令": "Show launch command",
  "当前论文任务": "Active task",
  "识别码与本机版本绑定": "Task ID & local version binding",
  "返回当前工作": "Return to active stage",
  "当前工作": "Focus",
  "配置与材料": "Setup & Materials",
  "设置保存为本地文件，宿主读取后继续。研究步骤由宿主根据材料判断。": "Settings save locally for the host agent to read. Research steps are determined from your materials.",
  "论文设置": "Paper configuration",
  "本次工作": "Workflow type",
  "由材料形成论文": "Build from materials",
  "改写已有稿件": "Rewrite manuscript",
  "核查已有论文": "Audit paper",
  "独立审阅": "Independent review",
  "按意见返修": "Revise by feedback",
  "适配其他目标": "Adapt target venue",
  "使用场景": "Venue type",
  "期刊": "Journal",
  "会议": "Conference",
  "研究报告": "Report",
  "综述": "Review",
  "竞赛": "Competition",
  "其他": "Other",
  "输出语言": "Output language",
  "英文": "English",
  "中文": "Chinese",
  "中英": "Bilingual",
  "填写输出语言，例如：日文、法文": "Specify output language (e.g. Japanese, French)",
  "其他输出语言": "Custom output language",
  "目标名称（选填）": "Target venue (optional)",
  "暂未确定": "Unspecified",
  "已指定目标": "Target set",
  "填写目标期刊、会议或其他发表去向；留空则按暂未确定处理": "Enter journal/conference name, or leave blank if undecided",
  "研究分析": "Analysis mode",
  "由宿主判断": "Host decides",
  "需要新增分析": "New analysis",
  "仅用已有材料": "Materials only",
  "交付内容": "Deliverables",
  "论文稿件": "Manuscript",
  "完整本地稿包": "Full local bundle",
  "投稿材料包": "Submission package",
  "保留作者表达": "Author voice",
  "不特别要求": "Standard",
  "适度保留": "Moderate",
  "严格保留": "Strict",
  "期刊与文献学习": "Literature & venue study",
  "学习篇数": "Reference count",
  "3 + 3 篇（默认）": "3 + 3 papers (Default)",
  "6 + 6 篇（深入）": "6 + 6 papers (Deep)",
  "自定义篇数": "Custom count",
  "同方向论文篇数": "Same-field papers",
  "目标期刊论文篇数": "Target-venue papers",
  "参考文献目标": "Citation target",
  "高于样本平均（默认）": "Above sample avg (Default)",
  "自定数量": "Custom count",
  "自定参考文献数量": "Custom citation count",
  "请输入篇数": "Enter count",
  "机制 / 架构图": "Mechanism / architecture figure",
  "优先考虑（默认）": "Prefer if warranted (Default)",
  "不采用": "Omit",
  "宿主学习相关研究及目标期刊同类型论文（记录实际样本与限制），用于正文、图件和期刊格式。": "The host studies related work and target-venue style for writing, figures, and formatting.",
  "交付格式": "Output formats",
  "LaTeX 源文件": "LaTeX source",
  "仅使用已有材料与结果时，不新增分析、实验或模型运行；仍可学习公开文献、核对引用和读取参考图。私有材料保留在本地，明确的离线要求仍有效。": "When using existing materials only, no new experiments or model runs are added; public literature and reference checks still apply.",
  "恢复已保存配置": "Reset to saved",
  "保存设置": "Save configuration",
  "宿主提供的材料": "Host materials",
  "材料": "File",
  "大小": "Size",
  "上一页": "Previous",
  "下一页": "Next",
  "研究进展": "Research progress",
  "宿主依据材料和设置开展必要研究；已有研究结果可直接使用。": "Host carries out needed analysis per materials & setup.",
  "动机与贡献": "Motivation & contributions",
  "请核对宿主提供的候选并保存你的选择与意见。": "Review host candidates and save your selection.",
  "论证与证据": "Evidence & claims",
  "宿主保存的证据和论证记录，仅供查看。": "Saved evidence and claim links (read-only).",
  "论文主稿": "Manuscript",
  "查看已登记的论文正文、PDF、Word或TeX源文件。": "View registered manuscript PDF, Word, or LaTeX sources.",
  "图件工作台": "Figures workbench",
  "左列是我们的图，右列是对应参考图；按图号和子图逐行排列。参考旁可查看原文，保留／修改意见仍分别保存。": "Compare manuscript figures against paired references, inspect originals, and save per-figure choices.",
  "浏览全部目录文件（含历史文件和可编辑源）": "Browse all directory files (history & sources)",
  "审阅记录": "Review records",
  "显示宿主提供的真实审阅记录。": "Displays host-recorded peer/audit reviews.",
  "完成稿与论文包": "Deliverables & packages",
  "意见与返修": "Feedback & revisions",
  "提交跨阶段或整稿修改意见，保留当前版本后继续返修。": "Submit cross-stage or manuscript-wide revision notes while preserving saved versions.",
  "本次意见": "Current note",
  "意见范围": "Scope",
  "稿件": "Manuscript",
  "整项工作": "Whole task",
  "图件": "Figures",
  "意见": "Comment",
  "描述希望调整的内容。": "Describe requested changes.",
  "保存意见": "Save feedback",
  "交给当前 AI 接手": "Hand off to host AI",
  "复制接手指令": "Copy handoff prompt",
  "本地目录与历史": "Local folder & history",
  "打开任务目录": "Open folder",
  "交接文件": "Handoff files",
  "归属未明的文件": "Unassigned files",
  "任务历史（只读）": "Task history (read-only)",
  "查看接手指令": "View handoff prompt",
  "复制继续指令": "Copy prompt",
  "知道了，关闭": "Close",
  "支持 PaperSpine": "Support PaperSpine",
  "等待你的选择": "Awaiting selection",
  "请核对宿主提供的候选": "Please review host candidates",
  "选择与意见会保存为本地交接文件，等待中的宿主读取后继续。": "Selections save locally for the host agent to resume.",
  "等待配置": "Awaiting setup",
  "请保存本次论文配置": "Please save paper configuration",
  "配置保存后，宿主可读取实际设置。": "Once saved, the host agent reads your configuration.",
  "进度已保存": "Saved",
  "进度已保存；宿主运行状态未确认。": "Progress saved; host runtime status unconfirmed.",
  "已交付": "Delivered",
  "查看完成稿与论文包": "View deliverables & packages",
  "你可以查看已有文件或提出返修意见。": "Inspect generated files or submit revision feedback.",
  "已保存；宿主读取相同配置。": "Saved; synced with host configuration.",
  "宿主预填的草案，尚待你确认并保存。": "Host draft awaiting your confirmation.",
  "请核对本次论文的设置和材料后保存。": "Review configuration & materials before saving.",
  "宿主尚未提供可读取的材料清单。": "No readable material inventory from host yet.",
  "材料由宿主提供。": "Materials provided by host.",
  "我们的图": "Our figure",
  "对应参考图": "Reference figure",
  "尚未关联对应参考图；不会自动拿其他图来凑对。": "No paired reference yet; unrelated figures are never auto-matched.",
  "放大查看": "Zoom",
  "缩小": "Zoom out",
  "放大": "Zoom in",
  "复位": "Reset",
  "滚轮放大 · 拖拽平移 · 双击切换": "Wheel to zoom · Drag to pan · Double-click",
  "打开原文件 ↗": "Open file ↗",
  "关闭放大预览": "Close zoom",
  "图像缩放": "Zoom",
  "适合窗口": "Fit window",
  "100%（窗口内）": "100% (Fit)",
  "150% 放大": "150%",
  "200% 放大": "200%",
  "对此图提意见": "Comment on figure",
  "对此文件提意见": "Comment on file",
  "此文件的修改意见": "Revision note for this file",
  "保存此图意见": "Save note",
  "查看完整问题与方案说明": "View full prompt & option details",
  "已有整页对照文件": "Comparison sheets",
  "预览此文件": "Preview file",
  "查看历史版本": "Version history",
  "请选择一个方案": "Select an option",
  "选择理由或修改意见（选填）": "Reason or revision note (optional)",
  "可选：填写选择理由、局部修改建议或细节要求…": "Optional: reason, local edits, or style notes…",
  "保存我的选择": "Save selection",
  "待选择 · 尚未保存本图意见": "Pending · Not saved yet",
  "宿主尚未提供交接文件。": "No handoff files provided by host yet.",
  "目录由宿主建立后可打开。": "Folder can be opened once created by host.",
  "尚无可读取的审阅记录。": "No review records available yet.",
  "尚无可读取的研究记录。": "No research records available yet.",
  "尚无可读取的证据记录。": "No evidence records available yet.",
  "刷新任务列表": "Refresh tasks",
  "宿主打开任务后会出现在这里。": "Tasks opened by the host appear here.",
  "当前为只读回看。可回到当前阶段保存意见，或直接与宿主 Agent 对话，并附上此文件路径。": "Read-only historical view. Return to the active stage to submit feedback.",
};
function tr(text) {
  if (uiLang !== "en" || typeof text !== "string" || !text) return text;
  if (Object.hasOwn(UI_EN, text)) return UI_EN[text];
  const mId = text.match(/^识别码：(.+)$/);
  if (mId) return `ID: ${mId[1]}`;
  const mTaskId = text.match(/^任务识别码：(.+)$/);
  if (mTaskId) return `Task ID: ${mTaskId[1]}`;
  const mUnsaved = text.match(/^未保存：(.+)$/);
  if (mUnsaved) return `Unsaved: ${mUnsaved[1]}`;
  const mChosen = text.match(/^已选择：(.+)$/);
  if (mChosen) return `Selected: ${mChosen[1]}`;
  const mRecent = text.match(/^最近记录：(.+)$/);
  if (mRecent) return `Latest: ${mRecent[1]}`;
  const mLit = text.match(/^同方向 (\d+) \+ 目标期刊 (\d+) 篇$/);
  if (mLit) return `${mLit[1]} same-field + ${mLit[2]} venue papers`;
  const mDir = text.match(/^(.+) · (\d+) 个文件$/);
  if (mDir) return `${mDir[1]} · ${mDir[2]} file(s)`;
  const mDisc = text.match(/^自动发现 (\d+) 个实际文件。/);
  if (mDisc) return `Discovered ${mDisc[1]} files. Click to expand previews.`;
  const mRefNote = text.match(/^参考说明：(.+)$/);
  if (mRefNote) return `Reference note: ${mRefNote[1]}`;
  const mRange = text.match(/^选择范围：(.+)$/);
  if (mRange) return `Scope: ${mRange[1]}`;
  return text;
}
const phaseLabel = (phase) => {
  const entry = PHASES.find(([id]) => id === phase);
  if (!entry) return uiLang === "en" ? "Unrecorded stage" : "尚未记录阶段";
  return uiLang === "en" ? entry[2] : entry[1];
};
const taskPath = (id) => `/api/v1/tasks/${encodeURIComponent(id)}`;
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const decisionsOf = (task) => task?.domain_decisions ?? task?.decisions ?? [];
const SUPPORT_PAGE_URL = "https://wubing2023.github.io/PaperSpine/v5/?support=1";
const SUPPORT_USAGE_KEY = "paperspine5.support-usage.v1";
function supportMilestone(count) { return count === 3 || (count >= 10 && count % 10 === 0); }
function recordPackageUse(artifact, taskContext) {
  if (!artifact || !taskContext?.taskId) return null;
  const type = String(artifact.artifact_type || "").toLowerCase();
  const name = String(artifact.filename || artifact.file_name || "").toLowerCase();
  if (!type.includes("package") && !name.endsWith(".zip")) return null;
  try {
    const storage = globalThis.localStorage;
    if (!storage) return null;
    const data = JSON.parse(storage.getItem(SUPPORT_USAGE_KEY) || '{"count":0,"seen":[]}');
    const key = `${taskContext.taskId}:${taskContext.task?.task_version ?? taskContext.task?.version ?? "current"}:${artifact.artifact_id || name}`;
    if (!Array.isArray(data.seen)) data.seen = [];
    if (data.seen.includes(key)) return null;
    data.seen.push(key); data.seen = data.seen.slice(-200); data.count = Math.max(0, Number(data.count) || 0) + 1;
    storage.setItem(SUPPORT_USAGE_KEY, JSON.stringify(data));
    return supportMilestone(data.count) ? data.count : null;
  } catch (_) { return null; }
}
function showSupportMilestone(count) {
  const panel = document.querySelector("#support-milestone");
  if (!panel || !count) return;
  const countNode = document.querySelector("#support-milestone-count");
  if (countNode) countNode.textContent = String(count);
  panel.hidden = false;
}
function decisionPhase(decision) {
  const kind = String(decision.decision_type || "").toLowerCase();
  if (["figure", "visual", "plot", "chart"].some((s) => kind.includes(s))) return "figure";
  if (["motivation", "contribution", "hypothesis", "research_question"].some((s) => kind.includes(s))) return "contribution";
  return null;
}
function configurationStatus(task) {
  const readiness = task?.configuration_readiness;
  if (readiness?.ready === true && readiness.user_confirmed === true
      && readiness.source === "web_user" && !task.configuration_stale) return "confirmed";
  if (task?.configuration_source === "agent_proposal") return "proposal";
  if (task?.configuration_stale) return "stale";
  return task?.configuration && Object.keys(task.configuration).length ? "unverified" : "missing";
}
function currentPhase(task) {
  const pending = decisionsOf(task).find((d) => d.status === "pending" && !d.stale && decisionPhase(d));
  return pending ? decisionPhase(pending) : task?.stage || "intake";
}
function optionDetails(decision) {
  return decision.allowed_decision_details || (decision.allowed_decisions || []).map((id) => ({option_id: id, label: id}));
}
function preferredFigureFile(decision, isAvailable) {
  const excluded = new Set([...(decision.figure?.reference_files || []), ...(decision.figure?.comparison_files || [])]);
  const usable = path => !excluded.has(path) && isAvailable(path);
  const options = optionDetails(decision);
  const saved = decision.status === "resolved" ? options.find(option => option.option_id === decision.option_id) : null;
  // A preview is not a choice: pending radios remain unset until the user acts.
  return saved?.files?.find(usable)
    || options.filter(option => option.action === "adopt").flatMap(option => option.files || []).find(usable)
    || (decision.figure?.current_files || []).find(usable);
}
function decisionBinding(decision) {
  return {prompt: decision.prompt, type: decision.decision_type, scope_refs: decision.scope_refs,
    requested_by_command_id: decision.requested_by_command_id, figure: decision.figure, options: optionDetails(decision)};
}
function canRebase(entry, task) {
  if (task.task_id !== entry.taskId) return false;
  if (entry.kind === "decision") {
    const decision = decisionsOf(task).find((d) => d.decision_id === entry.body.payload.decision_id);
    return Boolean(decision && decision.status === "pending" && !decision.stale
      && same(decisionBinding(decision), entry.base)
      && optionDetails(decision).some((o) => o.option_id === entry.body.payload.option_id));
  }
  if (entry.kind === "configuration") return Object.keys(entry.body.payload).every((key) =>
    same(task.configuration?.[key], entry.base?.[key]));
  return entry.kind === "feedback";
}
class PublicError extends Error {
  constructor(message, code, status = 0) { super(message); this.code = code; this.status = status; }
}
async function performMutation(entry, send, read, persist = () => {}) {
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try { return await send(entry.route, entry.body); }
    catch (error) {
      if (error.code !== "version_conflict" || attempt !== 0) throw error;
      const fresh = await read(entry.taskId);
      if (!canRebase(entry, fresh)) throw new PublicError("任务或候选内容已变化，请核对后重新确认。", "choice_changed");
      // Only a definite version rejection allows rebasing. Unknown outcomes
      // retain the exact command_id, version, payload and confirmation time.
      entry.body.expected_version = fresh.task_version;
      persist(entry);
    }
  }
}
function allowedTaskUrl(value, taskId, origin) {
  if (typeof value !== "string" || !value) return null;
  try {
    const url = new URL(value, origin);
    if (url.origin !== origin || url.username || url.password || !url.pathname.startsWith(taskPath(taskId) + "/")) return null;
    return url.href;
  } catch (_) { return null; }
}
function optionFiles(option, files, taskId, origin) {
  const allowed = new Map(files.map((file) => [file.relative_path, file]));
  return (option.files || []).map((path) => {
    const file = allowed.get(path);
    return file && allowedTaskUrl(file.content_url, taskId, origin) ? file : null;
  }).filter(Boolean);
}

function figureUnits(decisions) {
  const groups = new Map();
  const figures = decisions.filter(d => decisionPhase(d) === "figure");
  const replaced = new Set(figures.map(d => d.figure?.replaces_decision_id).filter(Boolean));
  for (const d of figures) {
    const key = d.figure ? JSON.stringify([d.figure.figure_id, d.figure.panel_id || ""]) : d.decision_id;
    if (!groups.has(key)) groups.set(key, {key, records: []});
    groups.get(key).records.push(d);
  }
  return [...groups.values()].map(group => {
    const live = group.records.filter(d => !d.stale && !replaced.has(d.decision_id));
    const current = live.at(-1) || group.records.at(-1);
    return {...group, current, historical: !live.length, label: current.figure
      ? [current.figure.label, current.figure.panel_label || current.figure.panel_id].filter(Boolean).join(" · ")
      : current.prompt || current.decision_id};
  });
}
function artifactGroup(a) {
  if (a.stale || a.historical || a.freshness === "stale") return "history";
  const type = String(a.artifact_type || "").toLowerCase();
  const name = String(a.filename || a.file_name || "").toLowerCase();
  if (type === "delivery_package") {
    if (a.package_scope === "local_workspace") return "workspace";
    if (a.package_scope === "shareable") return "package";
    // Legacy packages have no declared scope. Keep them downloadable without
    // inferring permission to share from a suggestive filename.
    return "unspecified_package";
  }
  if (/workspace|private|full.local|complete.local/.test(type)) return "workspace";
  if (/package|submission|shareable/.test(type)) return "package";
  if (type === "pdf") return "pdf";
  if (type === "docx") return "word";
  if ((/manuscript|paper|reading/.test(type)) && /\.pdf$/.test(name)) return "pdf";
  if (/\.docx?$/.test(name) && /manuscript|paper|docx/.test(type)) return "word";
  if (/figure|graphical|mechanism/.test(type)) return "figures";
  return "sources";
}

function literatureValues(value = {}) {
  return {same_field_papers: 3, target_venue_papers: 3, reference_count_mode: "venue_average",
    reference_count: null, mechanism_figure: "prefer", ...value};
}
function literaturePreset(value) {
  for (const count of [3, 6]) if (Number(value.same_field_papers) === count && Number(value.target_venue_papers) === count) return String(count);
  return "custom";
}
function validatedLiterature(raw) {
  const value = literatureValues(raw);
  function positiveInteger(raw, label) {
    const number = Number(raw);
    if (raw == null || String(raw).trim() === "" || !Number.isSafeInteger(number) || number < 1)
      throw new PublicError(`${label}须为正整数。`, "validation_failed");
    return number;
  }
  value.same_field_papers = positiveInteger(value.same_field_papers, "同方向论文篇数");
  value.target_venue_papers = positiveInteger(value.target_venue_papers, "目标期刊论文篇数");
  if (!["venue_average", "custom"].includes(value.reference_count_mode) || !["prefer", "auto", "omit"].includes(value.mechanism_figure))
    throw new PublicError("请选择有效的参考文献目标和图件偏好。", "validation_failed");
  value.reference_count = value.reference_count == null || value.reference_count === "" ? null
    : positiveInteger(value.reference_count, "参考文献数量");
  if (value.reference_count_mode === "custom") value.reference_count = positiveInteger(value.reference_count, "参考文献数量");
  return value;
}

// A saved task can be handed to another host; this text neither wakes an AI nor carries credentials.
function hostHandoffText(task, handoff, origin) {
  if (!task?.task_id || handoff?.task_id !== task.task_id || !handoff.instruction) return "";
  if (handoff.task_version != null && handoff.task_version !== task.task_version) return "";
  const address = new URL("/?task_id=" + encodeURIComponent(task.task_id), origin);
  const binding = handoff.host_binding || {};
  return [handoff.instruction, `同一任务：${task.task_id}`,
    `工作台：${address.href}`,
    `指令生成时任务版本：${task.task_version}；接手时重新读取最新状态。`,
    handoff.workflow_directory ? `工作流目录：${handoff.workflow_directory}` : "",
    handoff.workspace_root ? `任务目录：${handoff.workspace_root}` : "",
    ...[["user_data_root", "用户数据根（--user-data-root）"], ["core_root", "已有任务内核根（--core-root）"],
      ["domain_database", "事件数据库（--domain-database）"]].map(([key, label]) => binding[key] ? `${label}：${JSON.stringify(binding[key])}` : ""),
    "使用这些明确路径或经核对等价的 profile 读取同一任务，不默认沿用另一个宿主记住的 profile。不要直接改数据库或工作流状态 JSON。",
    "读取实际稿件/图源和相关笔记，确认下一动作；未落盘的历史不可假称记得。若原宿主仍在写入，先协调为单一写入者。",
    "本指令须由用户发给选定宿主；复制没有启动 AI。"
  ].filter(Boolean).join("\n");
}
// A milestone records host work; files or unrelated version changes do not finish a phase.
function continuationProgress(task, previous) {
  const latest = (task?.milestones || []).at(-1);
  const snapshot = {taskId: task?.task_id, phase: task?.stage || "intake", milestone: latest?.milestone_id || null};
  const pending = decisionsOf(task).some(d => d.status === "pending" && !d.stale);
  const changed = previous?.taskId === snapshot.taskId && previous.phase !== snapshot.phase
    && snapshot.milestone && previous.milestone !== snapshot.milestone && latest.stage === snapshot.phase;
  const notice = changed && !pending && !task.configuration_stale
    && !["intake", "delivery"].includes(snapshot.phase) && task.status !== "completed"
    ? {title: "阶段记录已更新", description: `工作台已记录「${phaseLabel(snapshot.phase)}」阶段。请回到宿主 Agent 对话确认进展并继续下一步。`}
    : null;
  return {snapshot, notice};
}
function configurationDraftMessage(task, draft) {
  if (!draft) return "";
  const changed = Object.keys(draft.values || {}).some(key => !same(draft.base?.[key], task.configuration?.[key]));
  return changed ? `已保存配置已更新至版本 ${task.task_version}；本页未保存修改仍保留。请核对差异，或重新载入已保存配置。`
    : "有尚未保存的设置，仅保留在本页；其他页面只同步已保存数据。";
}

const figureStem = path => String(path || "").replace(/\.(pdf|png|jpe?g|svg|webp|gif)$/i, "");
function uniqueFigureFormats(paths) {
  const groups = new Map(), priority = {png:0,svg:1,webp:2,jpg:3,jpeg:3,pdf:4,gif:5};
  for (const path of paths) {
    const key = figureStem(path), old = groups.get(key);
    const rank = value => priority[value.split(".").at(-1).toLowerCase()] ?? 9;
    if (!old || rank(path) < rank(old)) groups.set(key,path);
  }
  return [...groups.values()];
}
function pairedFigureRows(decision, metadata = []) {
  const figure = decision.figure || {}, options = optionDetails(decision);
  const comparison = new Set(figure.comparison_files || []);
  const refs = [...new Set(figure.reference_files || [])];
  // Legacy files have no explicit roles; recognizable reference filenames are
  // display hints only. Never pair list positions or invent panel identities.
  const linked = options.flatMap(option=>option.files || []);
  if (!decision.figure) for (const path of linked) if (/参考|(?:^|[\/_-])ref(?:erence)?(?:[\/_-]|\.)/i.test(path)) refs.push(path);
  const referenceSet = new Set([...refs,...comparison]);
  // Keep A/B/C candidates visible together even after a user chooses one.
  // The saved choice is labelled, never used as a preview filter or implicit adoption.
  let current = [...(figure.current_files || []),...linked];
  current = uniqueFigureFormats([...new Set(current.filter(path=>!referenceSet.has(path)))]);
  current.sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
  const namedKey = path => figureStem(path).split("/").at(-1).replace(/(?:[_ -]?(?:参考图?|reference|ref))$/i, "");
  return current.map(file => {
    const pairs = metadata.filter(pair=>figureStem(pair.figure_file)===figureStem(file));
    if (pairs.length) return {file, references:uniqueFigureFormats(pairs.map(pair=>pair.reference_file)), explicit:true, shared:false};
    const matching = uniqueFigureFormats(refs.filter(ref=>namedKey(ref)===namedKey(file)));
    if (matching.length) return {file,references:matching,explicit:false,shared:false};
    const references = uniqueFigureFormats([...new Set(refs)]);
    return {file,references,explicit:false,shared:references.length>1 || current.length>1 && references.length>0};
  });
}
function safeOriginalPaperUrl(value, taskId, origin) {
  if (typeof value!=="string" || !value.trim()) return null;
  try {
    const url=new URL(value);
    if (!["https:","http:"].includes(url.protocol) || url.username || url.password) return null;
    if (url.origin===origin) return allowedTaskUrl(url.href,taskId,origin);
    return url.href;
  } catch (_) {return null;}
}
function referenceOriginalLinks(file, metadata, documents, taskId, origin) {
  const links=[],entries=metadata.filter(pair=>figureStem(pair.reference_file)===figureStem(file.relative_path));
  for (const item of entries) {
    const doc=documents.find(doc=>doc.relative_path===item.source_pdf);
    const local=doc && allowedTaskUrl(doc.content_url,taskId,origin);
    if (local) { const url=new URL(local);url.searchParams.set("preview","1");if(item.page)url.hash=`pdf-page-${item.page}`;
      links.push({url:url.href,label:"查看本地原文",note:item.figure_label || doc.filename,inferred:false}); }
    const online=safeOriginalPaperUrl(item.source_url,taskId,origin);
    if (online) links.push({url:online,label:"在线原文 ↗",note:item.figure_label || "已登记在线来源",inferred:false});
  }
  if (!links.length) {
    // Explicit page-bearing basename only: tang2025_page6_roc ->
    // target_tang2025_GNRI.pdf. Multiple matches are not guessed.
    const name=file.filename || String(file.relative_path).split("/").at(-1);
    const match=name.match(/^(.+?)[_-](?:page|p)(\d+)(?:[_.-]|$)/i);
    if (match) {
      const key=match[1].replace(/^(?:reference|ref|source|target)[_-]/i,"").toLowerCase();
      const hits=documents.filter(doc=>{const stem=figureStem(doc.filename || "").replace(/^(?:target|source|reference|ref)[_-]/i,"").toLowerCase();return stem===key || stem.startsWith(key+"_") || stem.startsWith(key+"-");});
      if (hits.length===1) {
        const local=allowedTaskUrl(hits[0].content_url,taskId,origin);
        if(local){const url=new URL(local);url.searchParams.set("preview","1");url.hash=`pdf-page-${Number(match[2])}`;
          links.push({url:url.href,label:"查看本地原文",note:"按文件名与页码定位，请核对原文",inferred:true});}
      }
    }
  }
  return links.filter((item,index)=>links.findIndex(other=>other.url===item.url)===index);
}
function orderedFigureUnits(decisions) {
  return figureUnits(decisions).sort((a,b)=>{
    const x=a.current.figure, y=b.current.figure;
    const group=(x?.figure_id || a.current.decision_id).localeCompare(y?.figure_id || b.current.decision_id,undefined,{numeric:true});
    return group || (x?.panel_id || "").localeCompare(y?.panel_id || "",undefined,{numeric:true});
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {pairedFigureRows, referenceOriginalLinks, safeOriginalPaperUrl, orderedFigureUnits, hostHandoffText, continuationProgress, configurationDraftMessage, preferredFigureFile, configurationStatus, PHASES, decisionsOf, decisionPhase, currentPhase, optionDetails, decisionBinding,
    canRebase, performMutation, PublicError, allowedTaskUrl, optionFiles,
    literatureValues, literaturePreset, validatedLiterature, figureUnits, artifactGroup};
}

if (typeof document !== "undefined") {
  const $ = (selector) => document.querySelector(selector);
  const state = {task: null, taskId: null, tasks: [], files: [], referenceDocuments: [], referencePairs: [], referenceWarnings: [], events: [], handoff: null, view: null,
    loadSequence: 0, refreshRequest: null, session: "", csrf: "", decisionDrafts: new Map(), configDrafts: new Map(),
    feedbackDrafts: new Map(), feedbackReceipts: new Map(), figureViews: new Map(), discoveredFigureViews: new Map(), figureCatalogViews: new Map(), pending: new Map(), inFlight: new Set(), renderingChoices: "", activeFigure: null};
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = tr(text);
    if (className) node.className = className;
    return node;
  }
  let continuationFocus = null;
  const continuationSnapshots = new Map();
  function restoreContinuationFocus() {
    if (!continuationFocus) return;
    const target = continuationFocus.isConnected && !continuationFocus.disabled ? continuationFocus : $("#refresh");
    continuationFocus = null;
    target.focus({preventScroll: true});
  }
  function hideSaveToast() {
    const dialog = $("#save-toast");
    if (dialog.open) dialog.close();
    dialog.hidden = true;
    restoreContinuationFocus();
  }
  function syncContinuationHandoff() {
    const dialog = $("#save-toast");
    if (dialog.hidden || dialog.dataset.taskId !== state.taskId) return;
    const instruction = hostHandoffText(state.task, state.handoff, location.origin);
    if ($("#save-toast-handoff").value !== instruction) $("#save-toast-handoff").value = instruction;
    $("#copy-save-handoff").disabled = !instruction;
    setText("#save-toast-binding", instruction ? `当前论文 · 已保存版本 ${state.task.task_version}`
      : "正在读取同一任务的接手指令；暂未就绪时可先回到原宿主对话。");
  }
  function showSaveToast(taskId, content = {}, returnFocus = document.activeElement) {
    if (state.taskId !== taskId) return;
    const dialog = $("#save-toast");
    dialog.dataset.taskId = taskId;
    setText("#save-toast-title", content.title || "已保存，请回到宿主对话");
    const pending = decisionsOf(state.task).some(d => d.status === "pending" && !d.stale);
    setText("#save-toast-description", content.description || (pending
      ? "本次选择或意见已保存。还有待确认的选择，可先完成这些选择，再回到宿主 Agent 对话继续。"
      : "请回到宿主 Agent 对话，告诉它继续下一步。"));
    setText("#save-toast-copy-status", "");
    dialog.hidden = false;
    syncContinuationHandoff();
    if (!dialog.open) {
      continuationFocus = returnFocus;
      dialog.showModal();
      $("#save-toast-title").focus();
    }
  }
  function observeContinuation(task) {
    const key = `paperspine.public.continuation:${task.task_id}`;
    let previous = continuationSnapshots.get(task.task_id);
    if (!previous) {
      try { previous = JSON.parse(sessionStorage.getItem(key) || "null"); } catch (_) { /* In-memory dedupe still works. */ }
    }
    const result = continuationProgress(task, previous);
    continuationSnapshots.set(task.task_id, result.snapshot);
    try { sessionStorage.setItem(key, JSON.stringify(result.snapshot)); } catch (_) { /* Keep memory fallback. */ }
    return result.notice;
  }
  $("#dismiss-save-toast").addEventListener("click", hideSaveToast);
  $("#save-toast").addEventListener("cancel", event => { event.preventDefault(); hideSaveToast(); });
  $("#save-toast").addEventListener("close", () => {
    $("#save-toast").hidden = true;
    restoreContinuationFocus();
  });
  $("#copy-save-handoff").addEventListener("click", async () => {
    const instruction = hostHandoffText(state.task, state.handoff, location.origin);
    if (!instruction || $("#save-toast").dataset.taskId !== state.taskId) { syncContinuationHandoff(); return; }
    try {
      await navigator.clipboard.writeText(instruction);
      setText("#save-toast-copy-status", "已复制，请粘贴到宿主 Agent 对话并发送。");
    } catch (_) {
      $("#save-toast-instruction-details").open = true;
      $("#save-toast-handoff").focus(); $("#save-toast-handoff").select();
      setText("#save-toast-copy-status", "自动复制不可用，已选中指令，请手动复制后发给宿主。");
    }
  });
  $("#support-milestone-dismiss")?.addEventListener("click", () => { $("#support-milestone").hidden = true; });
  let notice = null, noticeTimer = null;
  function message(text, error = false) {
    if (error) hideSaveToast();
    clearTimeout(noticeTimer); noticeTimer = null;
    const node = $("#security-error"); node.textContent = text; node.classList.toggle("hidden", !text);
    node.classList.toggle("success", Boolean(text) && !error);
    node.setAttribute("role", error ? "alert" : "status");
    notice = text ? {taskId: state.taskId, phase: currentPhase(state.task), error} : null;
    if (text && !error) noticeTimer = setTimeout(() => message(""), 6000);
  }
  function setText(selector, text) { $(selector).textContent = tr(text); }
  function size(bytes) { return Number.isFinite(bytes) ? (bytes < 1024 ? bytes + " B" : bytes < 1048576 ? (bytes / 1024).toFixed(1) + " KB" : (bytes / 1048576).toFixed(1) + " MB") : ""; }
  async function request(route, body) {
    const headers = {"X-PaperSpine5-Session": state.session};
    if (body !== undefined) Object.assign(headers, {"Content-Type": "application/json", "X-PaperSpine5-CSRF": state.csrf});
    const response = await fetch(route, {method: body === undefined ? "GET" : "POST", headers,
      cache: "no-store", signal: AbortSignal.timeout(15000), ...(body === undefined ? {} : {body: JSON.stringify(body)})});
    let value;
    try { value = await response.json(); }
    catch (_) { throw new PublicError("响应未能确认，请刷新核对后重试原提交。", "unknown_outcome", response.status); }
    if (!response.ok || value.error) {
      const detail = typeof value.error === "object" ? value.error : {};
      throw new PublicError(detail.message || value.error || `请求失败 (${response.status})`, detail.code || value.error_code || "http_error", response.status);
    }
    return value;
  }
  async function readTask(id) {
    const value = await request(taskPath(id));
    if (value.task_id !== id || !Number.isInteger(value.task_version)) throw new PublicError("任务投影不完整，请由宿主核对。", "projection_invalid");
    return value;
  }
  function storageKey(id) { return `paperspine.public.pending:${id}`; }
  function persistPending(id) {
    try { sessionStorage.setItem(storageKey(id), JSON.stringify([...state.pending].filter(([, entry]) => entry.taskId === id))); }
    catch (_) { /* Memory still preserves retries for this open page. */ }
  }
  function restorePending(id) {
    try {
      for (const [key, entry] of JSON.parse(sessionStorage.getItem(storageKey(id)) || "[]")) {
        if (entry.taskId === id && entry.route.startsWith(taskPath(id) + "/")) state.pending.set(key, entry);
      }
    } catch (_) { /* Invalid local draft is never submitted. */ }
  }
  function keyFor(kind, detail = "") { return `${state.taskId}:${kind}:${detail}`; }
  function readLocalDraft(key) {
    try { return JSON.parse(sessionStorage.getItem(`paperspine.public.draft:${key}`) || "null"); }
    catch (_) { return null; }
  }
  function writeLocalDraft(key, value) {
    try {
      if (value == null) sessionStorage.removeItem(`paperspine.public.draft:${key}`);
      else sessionStorage.setItem(`paperspine.public.draft:${key}`, JSON.stringify(value));
    } catch (_) { /* In-memory drafts still survive polling. */ }
  }
  function editable(phase) {
    return state.task && (state.view == null || state.view === currentPhase(state.task)) && phase === currentPhase(state.task);
  }
  async function mutate(key, makeEntry) {
    if (state.inFlight.has(key)) return;
    const taskId = state.taskId, returnFocus = document.activeElement;
    state.inFlight.add(key); renderEditability();
    let entry = state.pending.get(key);
    try {
      if (!entry) {
        const fresh = await readTask(taskId);
        if (state.taskId !== taskId) return;
        entry = makeEntry(fresh);
        state.pending.set(key, entry); persistPending(taskId);
      }
      const result = await performMutation(entry, request, readTask, () => persistPending(taskId));
      state.pending.delete(key); persistPending(taskId);
      if (entry.kind === "configuration") state.configDrafts.delete(taskId);
      if (entry.kind === "decision") {
        state.decisionDrafts.delete(`${taskId}:${entry.body.payload.decision_id}`);
        writeLocalDraft(`${taskId}:decision:${entry.body.payload.decision_id}`, null);
      }
      if (entry.kind === "feedback" && !entry.figurePath) state.feedbackDrafts.delete(taskId);
      if (entry.figurePath) { state.feedbackDrafts.delete(key); writeLocalDraft(key, null); state.feedbackReceipts.set(taskId + ":" + entry.figurePath, entry.figureText); }
      if (state.taskId === taskId) {
        // The accepted save is already authoritative. A slower GET must not
        // restore an older version after its local draft has been cleared.
        const saved = result.projection;
        if (saved?.task_id === taskId && Number.isInteger(saved.task_version)
            && saved.task_version >= (state.task?.task_version ?? 0)) state.task = {...state.task, ...saved};
        if (entry.kind === "feedback" && !entry.figurePath) { $("#feedback-form").reset(); requestAnimationFrame(syncConfigVisuals); setText("#feedback-status", result.feedback_file ? `意见已保存：${result.feedback_file}` : "意见已保存到同一任务，宿主 Agent 可读取后继续。"); }
        message("");
        showSaveToast(taskId, {}, returnFocus);
        await refreshTask({force: true});
      }
      return result;
    } catch (error) {
      // Definite validation/choice failures can be corrected; connectivity and
      // server failures keep the original request for an explicit retry.
      const definite = ["validation_failed", "choice_changed", "decision_already_resolved", "forbidden", "not_found"].includes(error.code);
      if (definite) { state.pending.delete(key); persistPending(taskId); }
      // A concurrent save must not erase this page's unsaved draft. Reload is an explicit user action.
      if (state.taskId === taskId) {
        message(definite ? error.message : `${error.message || "连接中断"} 未确认结果，请用“重试原提交”核对，保留原请求。`, true);
        if (error.code === "choice_changed" || error.code === "decision_already_resolved") await refreshTask({force: true});
      }
    } finally {
      state.inFlight.delete(key); if (state.taskId === taskId) { state.renderingChoices = ""; render(); }
    }
  }
  function entryFor(kind, fresh, route, payload, base) {
    const body = {schema_version: "1.1", command_id: `web-${kind}-${crypto.randomUUID()}`, expected_version: fresh.task_version, payload};
    return {kind, taskId: fresh.task_id, route, body, base};
  }
  function saveDrafts() {
    if (!state.taskId) return;
    state.feedbackDrafts.set(state.taskId, {text: $("#feedback-text").value, scope: $("#feedback-scope").value});
  }
  async function loadTask(id) {
    hideSaveToast();
    document.querySelector(".figure-zoom-dialog")?.close();
    message("");
    saveDrafts(); state.taskId = id; state.task = null; state.view = null; state.files = []; state.referenceDocuments = []; state.referencePairs = []; state.referenceWarnings = []; state.events = []; state.handoff = null;
    state.renderingChoices = ""; state.activeFigure = null; materialPage = 0; renderedMaterials = ""; restorePending(id);
    document.title = "正在打开论文 · PaperSpine";
    setText("#sidebar-active-title", "正在打开论文…");
    setText("#sidebar-active-description", "");
    setText("#sidebar-active-id", `识别码：${id}`);
    document.body.classList.add("task-open");
    $("#workspace-empty").classList.add("hidden");
    $("#task-load-state").classList.remove("hidden");
    setText("#task-load-message", "正在打开这篇论文…");
    $("#retry-task-load").hidden = true;
    $("#task-workspace").classList.add("hidden");
    $("#global-stage-strip").classList.add("hidden");
    const url = new URL(location.href); url.searchParams.set("task_id", id); url.hash = ""; history.replaceState(null, "", url);
    const draft = state.feedbackDrafts.get(id);
    $("#feedback-form").reset();
    if (draft) { $("#feedback-text").value = draft.text; $("#feedback-scope").value = draft.scope; }
    const pendingFeedback = state.pending.get(keyFor("feedback"));
    if (pendingFeedback) { $("#feedback-text").value = pendingFeedback.body.feedback; $("#feedback-scope").value = pendingFeedback.body.scope; }
    setText("#feedback-status", "");
    requestAnimationFrame(syncConfigVisuals);
    await refreshTask({force: true});
  }
  function refreshTask({force = false} = {}) {
    if (!state.taskId) return Promise.resolve();
    // Polls/manual refreshes share this navigation's pending read. Incrementing
    // the sequence on every poll would starve any task slower than the timer.
    if (!force && state.refreshRequest?.id === state.taskId) return state.refreshRequest.promise;
    const id = state.taskId, sequence = ++state.loadSequence;
    const refresh = {id, promise: null};
    state.refreshRequest = refresh;
    refresh.promise = (async () => {
      // Show configuration independently of slow figure/history reads.
      const ancillary = Promise.allSettled([
        request(taskPath(id) + "/figure-files"), request(taskPath(id) + "/events"),
        request(taskPath(id) + "/host-handoff"),
      ]);
      let task;
      try { task = await readTask(id); }
      catch (error) {
        if (sequence === state.loadSequence && id === state.taskId) {
          setText("#task-load-message", error.message || "暂时无法打开，请重试。");
          $("#retry-task-load").hidden = false; message(error.message, true);
        }
        return;
      }
      if (sequence !== state.loadSequence || id !== state.taskId) return;
      if (state.task && task.task_version < state.task.task_version) return;
      state.task = task;
      const continuation = observeContinuation(task);
      $("#task-load-state").classList.add("hidden");
      render();
      const [files, events, handoff] = await ancillary;
      if (sequence !== state.loadSequence || id !== state.taskId) return;
      if (files.status === "fulfilled" && files.value.task_id === id) {
        state.files = files.value.files || [];
        state.referenceDocuments = files.value.reference_documents || [];
        state.referencePairs = files.value.reference_pairs || [];
        state.referenceWarnings = files.value.reference_warnings || [];
        // Only an accepted file list can invalidate a task's browsing choice.
        if (!state.files.some(file => file.relative_path === state.discoveredFigureViews.get(id) && isPreviewableFigureFile(file)))
          state.discoveredFigureViews.delete(id);
        const catalog = state.figureCatalogViews.get(id);
        if (catalog) {
          const directories = new Set(state.files.map(file => file.relative_path.slice(0, file.relative_path.lastIndexOf("/"))));
          const previews = new Set(state.files.filter(isPreviewableFigureFile).map(file => file.relative_path));
          for (const path of catalog.directories) if (!directories.has(path)) catalog.directories.delete(path);
          for (const path of catalog.previews) if (!previews.has(path)) catalog.previews.delete(path);
        }
      }
      if (events.status === "fulfilled") state.events = events.value.events || [];
      if (handoff.status === "fulfilled" && handoff.value.handoff?.task_id === id) state.handoff = handoff.value.handoff;
      state.filesError = files.status === "rejected";
      render();
      if (continuation && !state.inFlight.size && !document.querySelector("dialog[open]")) showSaveToast(id, continuation);
    })().finally(() => {
      if (state.refreshRequest === refresh) state.refreshRequest = null;
    });
    return refresh.promise;
  }
  function renderHomeRecent(unavailable = false) {
    const recent = state.tasks[0];
    setText("#home-recent-title", recent ? recent.title || "未命名论文"
      : unavailable ? "暂时无法读取论文任务" : "还没有已保存的论文任务");
    setText("#home-recent-stage", recent ? phaseLabel(recent.stage) : "");
    $("#home-recent-stage").hidden = !recent;
    $("#home-open-recent").hidden = !recent;
  }

  function renderTaskList() {
    renderHomeRecent();
    const list = $("#task-list"); list.replaceChildren();
    for (const task of state.tasks) {
      const button = el("button", null, "task-card"); button.type = "button";
      const meta = el("div", null, "task-card-meta");
      meta.append(el("span", phaseLabel(task.stage), "task-stage-badge"), el("small", task.task_id || "", "task-identity"));
      button.append(el("strong", task.title || (uiLang === "en" ? "Untitled paper" : "未命名论文")),
        el("span", task.description || (uiLang === "en" ? "Description unavailable" : "任务简介暂不可用"), "task-description"),
        meta);
      button.dataset.taskId = task.task_id;
      button.setAttribute("aria-current", task.task_id === state.taskId ? "true" : "false");
      button.title = `${task.title || "论文任务"}\n${task.description || ""}\n${task.task_id}`;
      button.addEventListener("click", () => loadTask(task.task_id).catch((error) => message(error.message, true)));
      list.append(button);
    }
    if (!state.tasks.length) list.append(el("p", "宿主打开任务后会出现在这里。", "muted"));
  }
  async function refreshTasks() {
    let result;
    try { result = await request("/api/v1/tasks"); }
    catch (error) { renderHomeRecent(true); throw error; }
    state.tasks = result.tasks || [];
    renderTaskList();
  }
  function buildNavigation() {
    $("#home-workflow").replaceChildren(...PHASES.map(([phase]) => el("li", phaseLabel(phase))));
    for (const nav of document.querySelectorAll(".workflow-progress")) {
      nav.replaceChildren();
      PHASES.forEach(([phase], index) => {
        const item = el("li"); item.dataset.phase = phase;
        const button = el("button"); button.type = "button";
        button.append(el("b", index + 1), el("span", phaseLabel(phase)));
        button.addEventListener("click", () => { state.view = phase === currentPhase(state.task) ? null : phase; render(); });
        item.append(button); nav.append(item);
      });
    }
  }
  function renderNavigation() {
    const current = currentPhase(state.task), currentIndex = PHASES.findIndex(([id]) => id === current);
    const selected = state.view || current;
    const earlyFigures = PHASES.findIndex(([id]) => id === "figure") > currentIndex && state.files.length > 0;
    const figureAccess = state.files.some(isPreviewableFigureFile) ? "已有预览，只读" : "已有文件，只读";
    // Registered files can be read before delivery is ready; this only opens the view.
    const readableArtifacts = (state.task.domain_artifacts ?? state.task.artifacts ?? [])
      .some(a => allowedTaskUrl(a.content_url, state.taskId, location.origin) || allowedTaskUrl(a.download_url, state.taskId, location.origin));
    const earlyDelivery = PHASES.findIndex(([id]) => id === "delivery") > currentIndex && readableArtifacts;
    for (const item of document.querySelectorAll(".workflow-progress li")) {
      const phase = item.dataset.phase, index = PHASES.findIndex(([id]) => id === phase);
      item.classList.toggle("active", phase === current);
      item.classList.toggle("viewing", phase === selected);
      const available = index <= currentIndex || (phase === "figure" && state.files.length > 0)
        || (phase === "delivery" && (Boolean(state.task.delivery) || readableArtifacts));
      const button = item.querySelector("button"); button.disabled = !available;
      if (phase === selected) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
      button.setAttribute("aria-label", `${phaseLabel(phase)}${phase === current ? "（当前）" : phase === "figure" && earlyFigures ? `（${figureAccess}）` : phase === "delivery" && earlyDelivery ? "（已有文件，只读）" : available ? "（只读回看）" : "（尚无可读记录）"}`);
    }
    for (const panel of document.querySelectorAll("[data-phase-panel]")) {
      const visible = panel.dataset.phasePanel === selected;
      panel.hidden = !visible; panel.classList.toggle("stage-current", visible);
    }
    const historical = state.view != null && state.view !== current;
    $("#stage-view-banner").classList.toggle("hidden", !historical);
    setText("#stage-view-title", `${phaseLabel(selected)} · ${selected === "figure" && earlyFigures ? figureAccess : selected === "delivery" && earlyDelivery ? "已有文件，只读" : "只读回看"}`);
    setText("#stage-view-copy", `最近记录阶段：${phaseLabel(current)}。回看不会推进或回退科研工作。`);
    setText("#global-stage-number", currentIndex < 0 ? "" : String(currentIndex + 1));
    setText("#global-stage-label", phaseLabel(current));
    $("#feedback-panel").hidden = historical;
    $("#host-handoff-panel").hidden = historical;
    requestAnimationFrame(syncStageSlider);
  }
  function syncStageSlider() {
    const nav = $("#global-workflow-progress"), thumb = $("#stage-slider-thumb"), shell = $("#global-workflow-shell");
    if (!nav || !thumb || !shell || $("#global-stage-strip")?.classList.contains("hidden") || $("#global-stage-strip")?.classList.contains("is-collapsed")) return;
    const target = nav.querySelector("li.viewing") || nav.querySelector("li.active");
    const rect = target?.getBoundingClientRect(), shellRect = shell.getBoundingClientRect();
    if (!target || !rect?.width) { thumb.style.opacity = "0"; return; }
    thumb.style.opacity = "1";
    thumb.style.width = `${rect.width}px`;
    thumb.style.transform = `translate3d(${rect.left - shellRect.left}px, 0, 0)`;
  }
  function render() {
    if (!state.task) return;
    const task = state.task;
    if (notice && !notice.error && (notice.taskId !== task.task_id || notice.phase !== currentPhase(task))) message("");
    $("#task-workspace").classList.remove("hidden"); $("#workspace-empty").classList.add("hidden");
    $("#global-stage-strip").classList.remove("hidden"); $("#active-context-card").classList.remove("hidden");
    document.body.dataset.taskId = task.task_id; document.body.classList.add("task-open");
    document.title = `${task.title || "论文任务"} · ${task.task_id} · PaperSpine`;
    for (const card of document.querySelectorAll(".task-card[data-task-id]"))
      card.setAttribute("aria-current", card.dataset.taskId === task.task_id ? "true" : "false");
    const description = task.description || `围绕“${task.title || "论文任务"}”的 PaperSpine 论文任务`;
    setText("#active-task-title", task.title || "论文任务"); setText("#sidebar-active-title", task.title || "论文任务");
    setText("#sidebar-active-description", description);
    setText("#active-task-id", `任务识别码：${task.task_id}`);
    setText("#workspace-binding", `服务：${location.origin} · 已保存版本：${task.task_version}。仅相同服务与任务同步已保存数据，未保存草稿留在各自页面。`);
    setText("#sidebar-active-id", `识别码：${task.task_id}`);
    setText("#sidebar-task-name", task.title || "论文任务");
    setText("#sidebar-active-status", phaseLabel(currentPhase(task)));
    setText("#active-task-subtitle", description);
    renderFocus();
    renderNavigation(); renderConfiguration(); renderMaterials(); renderDecisions(); renderFigures(); renderArtifacts(); renderRecords(); renderBridge(); renderPendingSubmissions(); renderEditability();
    const handoff = hostHandoffText(task, state.handoff, location.origin);
    setText("#host-handoff-text", handoff || "暂未读取到与当前任务版本一致的接手指令，请刷新重试。配置、选择和成果保持不变。");
    $("#copy-handoff").disabled = !handoff;
    syncContinuationHandoff();
  }
  function renderFocus() {
    const task = state.task, phase = currentPhase(task);
    const pending = decisionsOf(task).some((d) => d.status === "pending" && !d.stale);
    const key = keyFor("configuration"), submission = state.pending.has(key), draft = state.configDrafts.has(state.taskId);
    const delivered = task.delivery_manifest?.ready && !task.delivery?.stale;
    let summary;
    if (pending) summary = ["等待你的选择", "请核对宿主提供的候选", "选择与意见会保存为本地交接文件，等待中的宿主读取后继续。"];
    else if (phase === "intake") {
      // Configuration and local edits describe the UI, never the host's activity.
      if (submission) summary = state.inFlight.has(key)
        ? ["正在保存配置", "正在确认配置提交", "本次提交结果尚未确认。"]
        : ["配置提交待确认", "请重试原配置提交", "本次提交结果尚未确认；请重试原提交，核对保存结果。"];
      else if (draft) summary = ["配置有未保存修改", "请保存修改后的配置", "本页修改尚未保存；宿主只能读取已保存的配置。"];
      else if (configurationStatus(task) === "confirmed") summary = ["配置已保存", "本次论文配置已保存", "配置已保存，宿主可读取；宿主运行状态未确认。你仍可修改并保存设置。"];
      else if (configurationStatus(task) === "proposal") summary = ["配置草案待确认", "请核对并保存本次设置", "宿主已预填部分设置。请核对配置和材料后保存，宿主才能继续。"];
      else if (["stale", "unverified"].includes(configurationStatus(task))) summary = ["配置待重新确认", "请核对并重新保存设置", "当前设置尚未得到有效确认。请核对配置和材料后保存。"];
      else summary = ["等待配置", "请保存本次论文配置", "配置保存后，宿主可读取实际设置。"];
    } else if (delivered) summary = ["已交付", "查看完成稿与论文包", "你可以查看已有文件或提出返修意见。"];
    else summary = ["进度已保存", `最近记录：${phaseLabel(phase)}`, "进度已保存；宿主运行状态未确认。"];
    setText("#active-task-state", summary[0]); setText("#focus-title", summary[1]); setText("#focus-copy", summary[2]);
    $(".focus-card").classList.toggle("progress-summary", !pending && !delivered
      && !(phase === "intake" && (configurationStatus(task) !== "confirmed" || draft || submission)));
  }
  function customLangStorageKey(id = state.taskId) {
    return id ? `paperspine5.custom-lang.v1:${location.origin}:${id}` : "";
  }
  function readSavedCustomLanguage(id = state.taskId) {
    const key = customLangStorageKey(id);
    if (!key) return "";
    try { return globalThis.localStorage?.getItem(key) || ""; } catch (_) { return ""; }
  }
  function writeSavedCustomLanguage(val, id = state.taskId) {
    const key = customLangStorageKey(id);
    if (!key) return;
    try {
      const cleaned = String(val || "").trim();
      if (cleaned) globalThis.localStorage?.setItem(key, cleaned);
      else globalThis.localStorage?.removeItem(key);
    } catch (_) {}
  }
  function configValues() {
    const formats = [...document.querySelectorAll('[name="formats"]:checked')].map((input) => input.value);
    const targetName = $("#target-name").value.trim();
    return {workflow: $("#workflow").value, scene: $("#scene").value,
      target: targetName ? {status: "known", name: targetName} : {status: "unknown", name: null},
      output_language: $("#output-language").value, formats, research_mode: $("#research-mode").value,
      literature: {same_field_papers: $("#same-field-papers").value, target_venue_papers: $("#target-venue-papers").value,
        reference_count_mode: $("#reference-count-mode").value, reference_count: $("#reference-count").value || null,
        mechanism_figure: $("#mechanism-figure").value},
      requested_scope: $("#requested-scope").value, author_voice_restoration: $("#author-voice-restoration").value,
      network_policy: {allow_network: true, allow_external_upload: false}};
  }
  function syncTargetPill() {
    const known = Boolean($("#target-name")?.value.trim());
    const pill = $("#target-status-pill");
    if (!pill) return;
    pill.textContent = tr(known ? "已指定目标" : "暂未确定");
    pill.dataset.known = String(known);
  }
  function syncConfigLabels() {
    for (const group of document.querySelectorAll("#configuration-form .ui-choice-group, #feedback-form .ui-choice-group")) {
      const select = group.previousElementSibling;
      if (!select || select.tagName !== "SELECT") continue;
      for (const btn of group.querySelectorAll("button[data-value]")) {
        const opt = [...select.options].find((o) => o.value === btn.dataset.value);
        const span = btn.querySelector("span");
        if (opt && span) span.textContent = tr(opt.dataset.zh || opt.textContent);
      }
    }
  }
  function syncConfigVisuals() {
    for (const group of document.querySelectorAll("#configuration-form .ui-choice-group, #feedback-form .ui-choice-group")) {
      const select = group.previousElementSibling;
      if (!select || select.tagName !== "SELECT") continue;
      const val = select.value;
      const buttons = [...group.querySelectorAll("button[data-value]")];
      let activeBtn = null;
      for (const btn of buttons) {
        const active = btn.dataset.value === val;
        btn.setAttribute("aria-checked", String(active));
        btn.classList.toggle("is-active", active);
        if (active) activeBtn = btn;
      }
      const thumb = group.querySelector(".seg-thumb");
      if (thumb) {
        if (activeBtn && activeBtn.offsetWidth) {
          thumb.style.opacity = "1";
          thumb.style.width = `${activeBtn.offsetWidth}px`;
          thumb.style.transform = `translate3d(${activeBtn.offsetLeft - 3}px, 0, 0)`;
        } else {
          thumb.style.opacity = "0";
        }
      }
    }
    syncTargetPill();
    const litSummary = $("#literature-summary-chip");
    if (litSummary) litSummary.textContent = tr(`同方向 ${$("#same-field-papers").value || 3} + 目标期刊 ${$("#target-venue-papers").value || 3} 篇`);
  }
  function enhanceConfigControls() {
    for (const select of document.querySelectorAll("#configuration-form select[data-ui], #feedback-form select[data-ui]")) {
      if (select.dataset.enhanced === "true") continue;
      select.dataset.enhanced = "true";
      const mode = select.dataset.ui;
      select.classList.add("sr-only");
      select.tabIndex = -1;
      select.setAttribute("aria-hidden", "true");
      const group = el("div", null, mode === "segmented" ? "ui-choice-group segmented-control" : "ui-choice-group chip-selector");
      group.setAttribute("role", "radiogroup");
      if (mode === "segmented") group.append(el("span", null, "seg-thumb"));
      for (const option of select.options) {
        if (!option.value) continue;
        const btn = el("button", null, mode === "segmented" ? "seg-option" : "choice-chip");
        btn.type = "button";
        btn.setAttribute("role", "radio");
        btn.dataset.value = option.value;
        btn.append(el("span", option.textContent));
        btn.addEventListener("click", () => {
          if (select.disabled || select.closest("fieldset")?.disabled) return;
          select.value = option.value;
          select.dispatchEvent(new Event("input", {bubbles: true}));
          select.dispatchEvent(new Event("change", {bubbles: true}));
          syncConfigVisuals();
          if (select.id === "output-language" && option.value === "other") {
            requestAnimationFrame(() => {
              const input = $("#output-language-custom");
              if (input && !input.disabled) input.focus({preventScroll: true});
            });
          }
        });
        group.append(btn);
      }
      select.after(group);
    }
    for (const wrap of document.querySelectorAll("#configuration-form .stepper-input")) {
      if (wrap.dataset.enhanced === "true") continue;
      wrap.dataset.enhanced = "true";
      const input = wrap.querySelector("input[type='number']");
      if (!input) continue;
      const minus = el("button", "−", "stepper-btn"), plus = el("button", "+", "stepper-btn");
      minus.type = "button"; plus.type = "button";
      minus.setAttribute("aria-label", "减少"); plus.setAttribute("aria-label", "增加");
      const stepBy = (delta) => {
        if (input.disabled || input.readOnly || $("#configuration-fields").disabled) return;
        const current = Number(input.value || input.min || 1) || 1;
        const next = Math.max(Number(input.min || 1), current + delta);
        input.value = String(next);
        input.dispatchEvent(new Event("input", {bubbles: true}));
      };
      minus.addEventListener("click", () => stepBy(-1));
      plus.addEventListener("click", () => stepBy(1));
      wrap.prepend(minus);
      wrap.append(plus);
    }
  }
  function renderConfiguration() {
    const saved = state.task.configuration || {}, draft = state.configDrafts.get(state.taskId);
    const values = {...saved, ...(draft?.values || {}), ...(state.pending.get(keyFor("configuration"))?.body.payload || {})};
    values.scene ??= "journal";
    values.research_mode ??= "agent_decide";
    const fields = {workflow: "workflow", scene: "scene", research_mode: "research-mode", requested_scope: "requested-scope", author_voice_restoration: "author-voice-restoration"};
    for (const [key, id] of Object.entries(fields)) $("#" + id).value = values[key] ?? "";
    const presetLangs = new Set(["", "en", "zh", "multilingual", "other"]);
    const rawLang = values.output_language ?? "";
    const savedCustom = readSavedCustomLanguage();
    $("#output-language").value = presetLangs.has(rawLang) ? rawLang : "other";
    if ($("#output-language-custom")) {
      $("#output-language-custom").value = presetLangs.has(rawLang)
        ? (draft?.customLanguage ?? (rawLang === "other" ? savedCustom : ""))
        : rawLang;
    }
    renderLanguageEditability();
    $("#target-name").value = values.target?.name || "";
    $("#target-name").disabled = false;
    $("#target-name").required = false;
    const literature = literatureValues(values.literature);
    $("#literature-preset").value = draft?.literaturePreset || literaturePreset(literature);
    $("#same-field-papers").value = literature.same_field_papers;
    $("#target-venue-papers").value = literature.target_venue_papers;
    $("#reference-count-mode").value = literature.reference_count_mode;
    $("#reference-count").value = literature.reference_count ?? "";
    $("#mechanism-figure").value = literature.mechanism_figure;
    renderLiteratureEditability();
    $("#reload-saved-configuration").hidden = !draft;
    for (const input of document.querySelectorAll('[name="formats"]')) input.checked = (values.formats || []).includes(input.value);
    setText("#configuration-status", state.pending.has(keyFor("configuration")) ? "本次提交结果尚待确认，请重试原提交。" : draft ? configurationDraftMessage(state.task, draft) : configurationStatus(state.task) === "confirmed" ? "已保存；宿主读取相同配置。" : configurationStatus(state.task) === "proposal" ? "宿主预填的草案，尚待你确认并保存。" : "请核对本次论文的设置和材料后保存。");
    requestAnimationFrame(syncConfigVisuals);
  }
  function renderLanguageEditability() {
    const isOther = $("#output-language")?.value === "other";
    const customInput = $("#output-language-custom");
    const drawer = $("#custom-language-drawer");
    if (customInput) customInput.disabled = !isOther;
    if (drawer) drawer.dataset.open = String(Boolean(isOther));
  }
  function renderLiteratureEditability() {
    const custom = $("#literature-preset").value === "custom";
    const refCustom = $("#reference-count-mode").value === "custom";
    $("#same-field-papers").readOnly = !custom;
    $("#target-venue-papers").readOnly = !custom;
    $("#reference-count").disabled = !refCustom;
    $("#reference-count").required = refCustom;
    const litDrawer = $("#custom-literature-drawer"), refDrawer = $("#custom-reference-drawer");
    if (litDrawer) litDrawer.dataset.open = String(custom);
    if (refDrawer) refDrawer.dataset.open = String(refCustom);
  }
  const MATERIAL_PAGE_SIZE = 50;
  let materialPage = 0, renderedMaterials = "";
  function renderMaterials() {
    const roots = (state.task.material_grants || []).map((grant) => grant.root || grant.uri).filter(Boolean);
    const entries = state.task.material_inventory?.entries || [];
    const issues = state.task.material_inventory?.scan_issues || [];
    const pages = Math.max(1, Math.ceil(entries.length / MATERIAL_PAGE_SIZE));
    materialPage = Math.min(materialPage, pages - 1);
    const start = materialPage * MATERIAL_PAGE_SIZE;
    const visible = entries.slice(start, start + MATERIAL_PAGE_SIZE);
    // Polls render twice. Compare only displayed data, so unchanged polls retain
    // the rows, focus and scroll position without rebuilding thousands of nodes.
    const key = JSON.stringify([state.taskId, roots, entries.length, materialPage, issues,
      visible.map(file => [file.relative_path || file.source_id, file.size_bytes])]);
    if (key === renderedMaterials) return;
    for (const selector of ["#sidebar-material-roots", "#task-material-roots"]) {
      const list = $(selector); list.replaceChildren(); for (const root of roots) list.append(el("p", root, "material-root"));
      if (!roots.length) list.append(el("p", "材料由宿主提供。", "muted"));
    }
    const body = $("#task-material-table tbody");
    const rows = visible.map(file => {
      const row = el("tr"); row.append(el("td", file.relative_path || file.source_id), el("td", size(file.size_bytes)));
      return row;
    });
    body.replaceChildren(...rows);
    const summary = entries.length
      ? `${entries.length} 个材料文件；显示 ${start + 1}–${start + visible.length}；每页 ${MATERIAL_PAGE_SIZE} 个，仅供查看。`
      : "宿主尚未提供可读取的材料清单。";
    setText("#task-materials-summary", summary + (issues.length ? (entries.length
      ? " 部分文件未读取，宿主可继续处理已读取材料。"
      : " 请宿主核对下方路径，继续不依赖这些材料的工作。") : ""));
    const issueList = $("#task-material-issues");
    issueList.replaceChildren(...issues.map(issue => el("li", [issue.code, issue.details].filter(Boolean).join("："))));
    issueList.hidden = !issues.length;
    const select = $("#material-page");
    if (select.options.length !== pages) {
      select.replaceChildren(...Array.from({length: pages}, (_, index) => {
        const option = el("option", `第 ${index + 1} / ${pages} 页`); option.value = String(index); return option;
      }));
    }
    select.value = String(materialPage);
    $("#material-pagination").hidden = entries.length <= MATERIAL_PAGE_SIZE;
    $("#material-previous").disabled = materialPage === 0;
    $("#material-next").disabled = materialPage === pages - 1;
    renderedMaterials = key;
  }
  function changeMaterialPage(page) {
    materialPage = page;
    renderMaterials();
    $("#task-material-table").parentElement.scrollTop = 0;
  }
  $("#material-previous").addEventListener("click", () => changeMaterialPage(materialPage - 1));
  $("#material-next").addEventListener("click", () => changeMaterialPage(materialPage + 1));
  $("#material-page").addEventListener("change", (event) => changeMaterialPage(Number(event.target.value)));
  function versionedFigureFile(file) {
    const allowed = allowedTaskUrl(file.content_url, state.taskId, location.origin); if (!allowed) return file;
    const url = new URL(allowed), version = file.sha256 || file.size_bytes;
    if (version != null) url.searchParams.set("file_version", String(version));
    return {...file, content_url: url.href};
  }
  function attachPanZoom(stage, image, {modal = false} = {}) {
    let scale = 1, tx = 0, ty = 0, dragging = false, startX = 0, startY = 0, baseTx = 0, baseTy = 0;
    const minScale = 1, maxScale = modal ? 8 : 6;
    image.draggable = false;

    const hud = el("div", null, "figure-zoom-hud");
    hud.title = tr("滚轮放大 · 拖拽平移 · 双击切换");
    const zoomOut = el("button", "−", "zoom-hud-btn"); zoomOut.type = "button"; zoomOut.setAttribute("aria-label", tr("缩小"));
    const readout = el("button", "100%", "zoom-hud-readout"); readout.type = "button"; readout.title = tr("复位");
    const zoomIn = el("button", "+", "zoom-hud-btn"); zoomIn.type = "button"; zoomIn.setAttribute("aria-label", tr("放大"));
    hud.append(zoomOut, readout, zoomIn);
    stage.append(hud);

    const clampPan = (nextScale, nextTx, nextTy) => {
      if (nextScale <= 1.001) return [0, 0];
      const rect = stage.getBoundingClientRect();
      const maxTx = Math.max(0, (rect.width * (nextScale - 1)) / 2 + 48);
      const maxTy = Math.max(0, (rect.height * (nextScale - 1)) / 2 + 48);
      return [Math.max(-maxTx, Math.min(maxTx, nextTx)), Math.max(-maxTy, Math.min(maxTy, nextTy))];
    };
    const apply = (animate = false) => {
      stage.classList.toggle("is-zoomed", scale > 1.001);
      stage.classList.toggle("is-animating", animate && !dragging);
      image.style.transform = `translate3d(${tx.toFixed(1)}px, ${ty.toFixed(1)}px, 0) scale(${scale.toFixed(4)})`;
      const pct = `${Math.round(scale * 100)}%`;
      readout.textContent = pct;
      zoomOut.disabled = scale <= minScale + 0.001;
      zoomIn.disabled = scale >= maxScale - 0.001;
      stage.dataset.zoomScale = scale.toFixed(2);
    };
    const zoomAt = (nextScale, clientX, clientY, animate = false) => {
      const clamped = Math.max(minScale, Math.min(maxScale, nextScale));
      const cleanScale = clamped <= 1.02 ? 1 : clamped;
      if (cleanScale === 1) {
        scale = 1; tx = 0; ty = 0; apply(animate); return;
      }
      const rect = stage.getBoundingClientRect();
      const px = (clientX ?? rect.left + rect.width / 2) - (rect.left + rect.width / 2);
      const py = (clientY ?? rect.top + rect.height / 2) - (rect.top + rect.height / 2);
      const ix = (px - tx) / scale, iy = (py - ty) / scale;
      [tx, ty] = clampPan(cleanScale, px - ix * cleanScale, py - iy * cleanScale);
      scale = cleanScale;
      apply(animate);
    };

    stage.addEventListener("wheel", (event) => {
      if (hud.contains(event.target)) return;
      const zoomingIn = event.deltaY < 0;
      if (!modal && scale <= 1.001 && !zoomingIn) return;
      event.preventDefault();
      const factor = Math.exp(-event.deltaY * 0.0016);
      zoomAt(scale * factor, event.clientX, event.clientY, false);
    }, {passive: false});

    stage.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || hud.contains(event.target) || scale <= 1.001) return;
      event.preventDefault();
      dragging = true; startX = event.clientX; startY = event.clientY; baseTx = tx; baseTy = ty;
      stage.classList.add("is-dragging");
      stage.setPointerCapture?.(event.pointerId);
    });
    stage.addEventListener("pointermove", (event) => {
      if (!dragging) return;
      [tx, ty] = clampPan(scale, baseTx + (event.clientX - startX), baseTy + (event.clientY - startY));
      apply(false);
    });
    const endDrag = (event) => {
      if (!dragging) return;
      dragging = false;
      stage.classList.remove("is-dragging");
      if (event?.pointerId != null && stage.hasPointerCapture?.(event.pointerId)) stage.releasePointerCapture(event.pointerId);
    };
    stage.addEventListener("pointerup", endDrag);
    stage.addEventListener("pointercancel", endDrag);
    stage.addEventListener("dblclick", (event) => {
      if (hud.contains(event.target)) return;
      if (scale > 1.05) zoomAt(1, event.clientX, event.clientY, true);
      else zoomAt(2.2, event.clientX, event.clientY, true);
    });

    zoomOut.addEventListener("click", (e) => { e.stopPropagation(); zoomAt(scale / 1.35, null, null, true); });
    zoomIn.addEventListener("click", (e) => { e.stopPropagation(); zoomAt(scale * 1.35, null, null, true); });
    readout.addEventListener("click", (e) => { e.stopPropagation(); zoomAt(1, null, null, true); });
    apply(false);
    return { setScale: (next) => zoomAt(next, null, null, true), reset: () => zoomAt(1, null, null, true) };
  }
  const isMarkdownFile = file => /\.md(?:own)?$/i.test(file.filename || file.file_name || file.relative_path || "")
    || /^text\/markdown(?:;|$)/i.test(file.media_type || "");

  function markdownPreview(source, reader) {
    const cells = line => line.trim().replace(/^\||\|$/g, "").split("|").map(value => value.trim());
    const markedText = (tag, value) => {
      const node = el(tag);
      for (const [index, part] of value.split(/(`[^`\r\n]+`|\*\*[^*\r\n]+\*\*)/g).entries()) {
        if (index % 2) {
          const code = part.startsWith("`");
          const span = el(code ? "code" : "strong");
          span.textContent = part.slice(code ? 1 : 2, code ? -1 : -2);
          node.append(span);
        } else {
          node.append(part);
        }
      }
      return node;
    };
    for (const block of source.trim().split(/\r?\n\s*\r?\n/)) {
      const heading = /^(#{1,6})\s+([^\r\n]+)$/.exec(block);
      if (heading) {
        reader.append(markedText("h" + Math.min(heading[1].length + 1, 6), heading[2]));
        continue;
      }
      const lines = block.split(/\r?\n/);
      if (lines.length > 2 && /^\|?[\s:|-]+$/.test(lines[1]) && lines[1].includes("---")) {
        const table = el("table"), head = table.createTHead().insertRow();
        cells(lines[0]).forEach(value => head.append(markedText("th", value)));
        const body = table.createTBody();
        for (const line of lines.slice(2)) {
          const row = body.insertRow();
          cells(line).forEach(value => row.append(markedText("td", value)));
        }
        reader.append(table);
      } else if (lines.every(line => /^[-*+]\s+/.test(line))) {
        const list = el("ul");
        lines.forEach(line => list.append(markedText("li", line.slice(2))));
        reader.append(list);
      } else {
        reader.append(markedText("p", block));
      }
    }
  }

  async function loadMarkdownPreview(url, reader) {
    reader.textContent = tr("正在加载 Markdown…");
    try {
      const response = await fetch(url, {headers: {"X-PaperSpine5-Session": state.session},
                                        redirect: "error", signal: AbortSignal.timeout(15000)});
      if (!response.ok || !/^text\/(plain|markdown)(;|$)/i.test(response.headers.get("Content-Type") || ""))
        throw new Error("Unexpected Markdown response");
      const source = await response.text();
      if (source.length > 1000000) throw new Error("Markdown is too large for the embedded reader");
      reader.replaceChildren();
      markdownPreview(source, reader);
    } catch (_) {
      reader.textContent = tr("Markdown 无法读取，可打开原文件。");
    }
  }

  const isWordFile = file => /\.docx$/i.test(file.filename || file.file_name || file.relative_path || "")
    || file.media_type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
  const supportsReader = file => isMarkdownFile(file) || isWordFile(file) || isPreviewableFigureFile(file);
  const readerUrl = file => allowedTaskUrl(file.content_url, state.taskId, location.origin)
    || (isWordFile(file) ? allowedTaskUrl(file.download_url, state.taskId, location.origin) : null);

  async function readLimited(stream, limit) {
    const reader = stream.getReader(), chunks = [];
    let size = 0;
    try {
      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        size += value.length;
        if (size > limit) {
          await reader.cancel();
          throw new Error("Word preview size limit exceeded");
        }
        chunks.push(value);
      }
    } finally {
      reader.releaseLock();
    }
    return new Blob(chunks);
  }

  // Read only the OOXML entries the preview needs. Never extract files to disk.
  function wordArchive(buffer) {
    const data = new DataView(buffer), bytes = new Uint8Array(buffer), names = new Map();
    const decode = new TextDecoder();
    const short = offset => data.getUint16(offset, true);
    const long = offset => data.getUint32(offset, true);
    let end = data.byteLength - 22;
    for (; end >= Math.max(0, data.byteLength - 65557); end--) {
      if (long(end) === 0x06054b50 && end + 22 + short(end + 20) === data.byteLength) break;
    }
    if (end < 0 || end < data.byteLength - 65557 || short(end + 4) || short(end + 6))
      throw new Error("Unsupported Word archive");
    const count = short(end + 10), start = long(end + 16);
    if (count > 4096 || start + long(end + 12) > end) throw new Error("Invalid Word directory");
    let offset = start;
    for (let i = 0; i < count; i++) {
      if (offset + 46 > end || long(offset) !== 0x02014b50) throw new Error("Invalid Word entry");
      const length = short(offset + 28);
      const name = decode.decode(bytes.subarray(offset + 46, offset + 46 + length));
      names.set(name, {method: short(offset + 10), compressed: long(offset + 20),
                       size: long(offset + 24), offset: long(offset + 42)});
      offset += 46 + length + short(offset + 30) + short(offset + 32);
    }
    return async name => {
      const entry = names.get(name);
      if (!entry) return null;
      const {offset, size, compressed, method} = entry;
      if (size > 16 * 1024 * 1024 || offset + 30 > start || long(offset) !== 0x04034b50)
        throw new Error("Invalid Word entry bounds");
      const body = offset + 30 + short(offset + 26) + short(offset + 28);
      if (body + compressed > start || ![0, 8].includes(method)) throw new Error("Unsupported Word entry");
      const blob = new Blob([bytes.subarray(body, body + compressed)]);
      const unpacked = method === 0 ? blob : await readLimited(blob.stream().pipeThrough(new DecompressionStream("deflate-raw")), size);
      if (unpacked.size !== size) throw new Error("Invalid Word entry size");
      return unpacked;
    };
  }

  const wordElements = (node, name) => [...node.getElementsByTagNameNS("*", name)];
  const wordAttribute = (node, name) => node && [...node.attributes].find(attr => attr.localName === name)?.value;

  async function loadWordPreview(url, reader) {
    reader.textContent = tr("正在加载 Word…");
    try {
      const response = await fetch(url, {headers: {"X-PaperSpine5-Session": state.session},
                                        redirect: "error", signal: AbortSignal.timeout(30000)});
      if (!response.ok || !response.body) throw new Error("Word download failed");
      const file = await readLimited(response.body, 32 * 1024 * 1024);
      const entry = wordArchive(await file.arrayBuffer());
      const parse = async name => {
        const xml = await entry(name);
        if (!xml) return null;
        const doc = new DOMParser().parseFromString(await xml.text(), "application/xml");
        if (doc.doctype || doc.querySelector("parsererror")) throw new Error("Invalid Word XML");
        return doc;
      };
      const doc = await parse("word/document.xml"), body = doc && wordElements(doc, "body")[0];
      if (!body) throw new Error("No Word document body");
      const rels = await parse("word/_rels/document.xml.rels");
      const media = new Map((rels ? wordElements(rels, "Relationship") : [])
        .filter(rel => rel.getAttribute("TargetMode") !== "External" && rel.getAttribute("Type")?.endsWith("/image"))
        .map(rel => [rel.getAttribute("Id"), rel.getAttribute("Target")]));
      const fragment = document.createDocumentFragment();
      let imageCount = 0, imageBytes = 0;
      for (const block of body.children) {
        if (block.localName === "p") {
          const style = wordAttribute(wordElements(block, "pStyle")[0], "val") || "";
          const level = /^Heading([1-5])$/i.exec(style);
          const node = el(level ? "h" + (Number(level[1]) + 1) : style === "Title" ? "h2" : "p");
          node.textContent = wordElements(block, "t").map(run => run.textContent).join("");
          if (node.textContent) fragment.append(node);
          for (const image of wordElements(block, "blip")) {
            const target = media.get(wordAttribute(image, "embed"));
            if (imageCount >= 32 || imageBytes >= 32 * 1024 * 1024
              || !target || !/^(?:\/word\/)?media\/[a-z0-9_.-]+\.(?:png|jpe?g|gif|webp)$/i.test(target)) continue;
            const blob = await entry(target.startsWith("/") ? target.slice(1) : "word/" + target);
            if (!blob || imageBytes + blob.size > 32 * 1024 * 1024) continue;
            imageCount++;
            imageBytes += blob.size;
            const picture = el("img");
            picture.alt = wordAttribute(wordElements(block, "docPr")[0], "descr") || "";
            const objectUrl = URL.createObjectURL(blob);
            picture.addEventListener("load", () => URL.revokeObjectURL(objectUrl), {once: true});
            picture.addEventListener("error", () => URL.revokeObjectURL(objectUrl), {once: true});
            picture.src = objectUrl;
            node.append(picture);
            if (!node.parentNode) fragment.append(node);
          }
        } else if (block.localName === "tbl") {
          const table = el("table"), rows = table.createTBody();
          for (const tr of [...block.children].filter(child => child.localName === "tr")) {
            const row = rows.insertRow();
            for (const tc of [...tr.children].filter(child => child.localName === "tc")) {
              const cell = row.insertCell();
              cell.textContent = wordElements(tc, "p").map(p => wordElements(p, "t").map(t => t.textContent).join("")).join("\n");
            }
          }
          fragment.append(table);
        }
      }
      reader.replaceChildren(fragment);
    } catch (_) {
      reader.textContent = tr("Word 预览无法加载，请下载原文件。");
    }
  }

  function filePreview(file, container, {enlarge = true, modal = false} = {}) {
    let url = readerUrl(file);
    if (!url) { container.append(el("p", "文件尚未出现在本任务允许的预览列表中。", "muted")); return; }
    const title = file.filename || file.relative_path || "图件", media = file.media_type || "";
    if (isMarkdownFile(file) || isWordFile(file)) {
      const reader = el("article", null, "markdown-reader");
      reader.tabIndex = 0;
      reader.setAttribute("aria-label", title);
      container.append(reader);
      if (isWordFile(file)) loadWordPreview(url, reader);
      else loadMarkdownPreview(url, reader);
    } else if (media === "application/pdf") {
      const preview = new URL(url, location.origin); preview.searchParams.set("preview", "1"); url = preview.pathname + preview.search;
      const frame = el("iframe"); frame.loading = "lazy"; frame.src = url; frame.title = `${title} PDF 预览`; frame.className = "public-file-preview";
      frame.addEventListener("load", () => fitFigurePdf(frame)); container.append(frame);
    } else if (["image/png", "image/jpeg", "image/svg+xml", "image/webp", "image/gif"].includes(media)) {
      const stage = el("div", null, modal ? "figure-panzoom-stage is-modal" : "figure-panzoom-stage");
      const image = el("img"); image.loading = "lazy"; image.src = url; image.alt = title; image.className = "public-file-preview";
      stage.append(image);
      const panzoom = attachPanZoom(stage, image, {modal});
      image._panzoom = panzoom;
      image.addEventListener("error", () => { stage.replaceWith(el("p", "预览未能加载，请刷新同一任务核对文件。", "muted")); });
      container.append(stage);
    }
    const actions = el("div", null, "figure-action-bar");
    if (enlarge && supportsReader(file)) {
      const button = el("button", file.artifact_id || isMarkdownFile(file) ? "全屏阅读" : "放大查看", "button figure-enlarge"); button.type = "button";
      button.addEventListener("click", () => openFileZoom(file, button)); actions.append(button);
    }
    const link = el("a", isWordFile(file) ? "下载" : "打开原文件 ↗", "file-link"); link.href = url;
    if (isWordFile(file)) link.download = title;
    else { link.target = "_blank"; link.rel = "noopener"; }
    actions.append(link);
    container.append(actions);
  }
  function fitFigurePdf(frame, {allDocuments = false} = {}) {
    let doc, pages;
    try {
      doc = frame.contentDocument;
      const url = doc && allowedTaskUrl(doc.URL, state.taskId, location.origin);
      // Fit manuscript pages in the expanded reader only; inline previews keep their normal layout.
      if (!url || (!allDocuments && !new URL(url).pathname.startsWith(taskPath(state.taskId) + "/figure-files/"))) return false;
      pages = [...doc.querySelectorAll("figure > .pdf-page")].filter(page => page.querySelector(":scope > img"));
    } catch (_) { return false; }
    if (!pages.length) return false;
    const header = doc.querySelector("body > header"); if (header) header.hidden = true;
    for (const page of pages) {
      const figure = page.parentElement, caption = figure.querySelector("figcaption"), img = page.querySelector(":scope > img");
      if (caption) Object.assign(caption.style, {font: "12px/16px system-ui", padding: "4px 8px"});
      const [width, height] = page.style.aspectRatio.split("/").map(Number);
      const ratio = width / height || img.naturalWidth / img.naturalHeight;
      const fit = Number.isFinite(ratio) && ratio > 0;
      // Size the wrapper, preserving the original percentage link/target layers.
      // Viewport units keep cards fitted on resize without per-card observers.
      Object.assign(figure.style, {maxWidth: "none", margin: "8px auto",
        width: fit ? `max(1px, min(calc(100vw - 32px), calc((100vh - 48px) * ${ratio})))` : "calc(100vw - 32px)"});
    }
    return true;
  }
  function openFileZoom(file, trigger) {
    if (!supportsReader(file)) return;
    const dialog = el("dialog", null, "figure-zoom-dialog"), heading = el("div", null, "figure-zoom-heading");
    if (isMarkdownFile(file) || isWordFile(file) || file.artifact_id) dialog.classList.add("document-reader-dialog");
    const title = el("h3", file.filename || file.relative_path || "文件预览"); title.id = "figure-zoom-title";
    dialog.setAttribute("aria-labelledby", title.id);
    const close = el("button", "关闭放大预览", "button"); close.type = "button"; close.autofocus = true;
    close.addEventListener("click", () => dialog.close()); heading.append(title, close);
    const body = el("div", null, "figure-zoom-body"); filePreview(file, body, {enlarge: false, modal: true});
    const image = body.querySelector("img");
    if (image) {
      const label = el("div", null, "figure-zoom-presets");
      for (const [value, text] of [[1, "适合窗口"], [1.5, "150% 放大"], [2, "200% 放大"]]) {
        const btn = el("button", text, "button"); btn.type = "button";
        btn.addEventListener("click", () => image._panzoom?.setScale(value));
        label.append(btn);
      }
      heading.append(label);
    }
    const frame = body.querySelector("iframe");
    if (frame && file.media_type === "application/pdf") {
      const status = el("p", "正在加载 PDF 页面预览。", "figure-pdf-zoom-status muted"); status.setAttribute("role", "status");
      const original = el("a", "打开原 PDF", "file-link");
      original.href = allowedTaskUrl(file.content_url, state.taskId, location.origin);
      original.target = "_blank"; original.rel = "noopener";
      const escape = event => { if (event.key === "Escape") { event.preventDefault(); dialog.close(); } };
      let previewDocument = null;
      function applyPdfFit() {
        let doc;
        try {
          doc = frame.contentDocument;
        } catch (_) { /* An unavailable or different-origin viewer keeps its original link. */ }
        if (!doc || !fitFigurePdf(frame, {allDocuments: true})) {
          status.textContent = tr("此文件可打开原 PDF 阅读。");
          return;
        }
        if (previewDocument !== doc) {
          previewDocument?.removeEventListener("keydown", escape);
          previewDocument = doc; doc.addEventListener("keydown", escape);
        }
        status.textContent = tr("适合窗口 · 滚动翻页");
      }
      heading.append(original, status);
      frame.addEventListener("load", applyPdfFit);
      const resize = new ResizeObserver(applyPdfFit); resize.observe(frame);
      dialog.addEventListener("close", () => {
        resize.disconnect(); frame.removeEventListener("load", applyPdfFit);
        previewDocument?.removeEventListener("keydown", escape);
      });
    }
    dialog.append(heading, body);
    dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => { dialog.remove(); if (trigger.isConnected) trigger.focus({preventScroll: true}); });
    document.body.append(dialog); dialog.showModal();
  }
  const shortFigureText = (value, limit = 42) => {
    const chars = Array.from(String(value || "").replace(/\s+/g, " ").trim());
    return chars.length > limit ? chars.slice(0, limit).join("") + "…" : chars.join("");
  };
  function figureTitle(decision, index) {
    const named = decision.figure && [decision.figure.label, decision.figure.panel_label || decision.figure.panel_id].filter(Boolean).join(" · ");
    return named ? shortFigureText(named) : Array.from(decision.prompt || "").length <= 42
      ? decision.prompt || `图件 ${index + 1}` : `图件 ${index + 1}`;
  }
  function figureChoiceText(decision, draft, pending = false) {
    const optionId = decision.status === "resolved" ? decision.option_id : draft?.option_id;
    const option = optionDetails(decision).find(o => o.option_id === optionId);
    const label = shortFigureText(option?.label || optionId);
    if (decision.stale) return "历史方案／需宿主更新";
    if (pending) return `提交结果待确认：${label || "当前意见"}`;
    const saved = {keep: "保留意见", adopt: "采用意见", revise: "修改意见", reject: "不采用意见"}[option?.action] || "方案";
    if (decision.status === "resolved") return `已选择：${label} · 已保存${saved}${decision.reason && decision.reason.trim() !== "无" ? "／附有意见，见详情。" : "。"}`;
    if (decision.status !== "pending") return "宿主记录，仅供查看";
    return optionId ? `未保存：${label}` : "待选择 · 尚未保存本图意见";
  }
  function syncFigureChoiceStatus(node, decision, draft, pending = false) {
    node.textContent = figureChoiceText(decision, draft, pending);
    node.dataset.state = decision.stale ? "stale" : decision.status === "resolved" ? "resolved" : pending || draft?.option_id ? "selected" : "pending";
  }
  function figureHeading(decision, card, index) {
    const header = el("div", null, "figure-card-header");
    header.append(el("h4", figureTitle(decision, index)));
    const status = el("p", "", "figure-choice-status"); status.setAttribute("role", "status");
    syncFigureChoiceStatus(status, decision);
    header.append(status);
    card.append(header);
    if (decision.prompt) card.append(el("p", shortFigureText(decision.prompt, 120), "figure-prompt-lead"));
    const details = el("details", null, "figure-instructions"); details.append(el("summary", "查看完整问题与方案说明"));
    if (decision.figure) details.append(el("p", [decision.figure.label, decision.figure.panel_label || decision.figure.panel_id].filter(Boolean).join(" · ")));
    if (decision.figure?.reference_note) details.append(el("p", "参考说明：" + decision.figure.reference_note));
    if (Array.isArray(decision.figure?.panel_ids)) details.append(el("p", decision.figure.panel_ids.length
      ? "独立面板选择范围：" + decision.figure.panel_ids.join("、") : "选择范围：整图"));
    details.append(el("p", decision.prompt || "请核对并选择", "figure-original-prompt"));
    for (const option of optionDetails(decision)) {
      const section = el("div"); section.append(el("strong", option.label || option.option_id));
      if (option.description) section.append(el("p", option.description));
      if (option.risk) section.append(el("p", "注意：" + option.risk));
      details.append(section);
    }
    if (decision.reason) details.append(el("p", "已保存的完整意见：" + decision.reason));
    card.append(details); return status;
  }
  function collapseFigurePreviews(container) {
    for (const preview of container.querySelectorAll(".figure-preview[open]")) preview.open = false;
  }
  function figureFile(file, container, catalogView = null) {
    const row = el("article", null, "public-figure-card"); row.dataset.figurePath = file.relative_path;
    const savedFeedback = state.feedbackReceipts.get(state.taskId + ":" + file.relative_path);
    if (savedFeedback) row.append(el("p", "此图意见已保存：" + savedFeedback, "figure-feedback-status"));
    row.append(el("strong", file.filename || file.relative_path), el("small", file.relative_path, "figure-path"));
    const preview = el("details", null, "figure-preview");
    const body = el("div"); preview.append(el("summary", "预览此文件"), body);
    const showPreview = () => {
      if (catalogView && !preview.isConnected) return;
      if (catalogView) {
        if (preview.open) catalogView.previews.add(file.relative_path);
        else catalogView.previews.delete(file.relative_path);
      }
      // A collapsed historical record must not create even a lazy iframe.
      if (preview.open && !body.children.length) filePreview(catalogView ? versionedFigureFile(file) : file, body);
      if (!preview.open) body.replaceChildren();
    };
    preview.addEventListener("toggle", showPreview);
    row.append(preview);
    const feedback = el("details", null, "figure-file-feedback");
    feedback.append(el("summary", "对此文件提意见"));
    feedback.addEventListener("toggle", () => {
      if (feedback.open && feedback.children.length === 1) renderFigureFeedback(file, feedback);
    });
    row.append(feedback); container.append(row);
    if (catalogView?.previews.has(file.relative_path) && isPreviewableFigureFile(file)) { preview.open = true; showPreview(); }
  }
  function renderFigureFeedback(file, container) {
    if (state.view && state.view !== currentPhase(state.task)) {
      container.append(el("p", "当前为只读回看。可回到当前阶段保存意见，或直接与宿主 Agent 对话，并附上此文件路径。", "muted"));
      return;
    }
    const key = keyFor("figure-feedback", file.relative_path), pending = state.pending.get(key);
    let draft = state.feedbackDrafts.get(key) || readLocalDraft(key) || {text: ""};
    state.feedbackDrafts.set(key, draft);
    const fields = el("fieldset"), label = el("label", "此文件的修改意见"), input = el("textarea");
    input.rows = 3; input.value = pending?.figureText ?? draft.text;
    input.addEventListener("input", () => { draft.text = input.value; writeLocalDraft(key, draft); });
    label.append(input); fields.append(label);
    const button = el("button", pending ? "重试原提交" : "保存此图意见", "button"), status = el("p", "", "muted");
    button.type = "button"; status.setAttribute("role", "status");
    fields.disabled = Boolean(pending) || state.inFlight.has(key); button.disabled = state.inFlight.has(key);
    button.addEventListener("click", async () => {
      if (state.view && state.view !== currentPhase(state.task)) return;
      const text = input.value.trim();
      const feedback = `图件文件（精确相对路径）：${JSON.stringify(file.relative_path)}\n\n${text}`;
      if (!state.pending.has(key) && (!text || [...feedback].length > 32000)) { status.textContent = "请填写意见；含文件路径的总长度不能超过 32,000 字符。"; return; }
      fields.disabled = true; button.disabled = true;
      const result = await mutate(key, (fresh) => {
        const entry = entryFor("feedback", fresh, `${taskPath(fresh.task_id)}/feedback`, {}, null);
        const {schema_version, payload, ...body} = entry.body;
        return {...entry, figurePath: file.relative_path, figureText: text,
          body: {...body, scope: "figures", feedback}};
      });
      if (result) { input.value = ""; draft = {text: ""}; status.textContent = "此图意见已保存到同一任务，可直接与宿主 Agent 对话继续修改。"; }
      fields.disabled = state.pending.has(key); button.disabled = false;
      button.textContent = state.pending.has(key) ? "重试原提交" : "保存此图意见";
    });
    container.append(fields, button, status);
  }
  function pairedFileCell(path, reference = false) {
    const cell = el("section", null, reference ? "paired-reference-cell" : "paired-study-cell");
    const file = optionFiles({files:[path]}, state.files, state.taskId, location.origin)[0];
    cell.dataset.figurePath = path;
    const headerRow = el("div", null, "paired-cell-header");
    headerRow.append(el("span", reference ? "对应参考图" : "我们的图", "paired-role-badge"), el("p", path.split("/").at(-1), "paired-file-name"));
    cell.append(headerRow);
    if (file) filePreview(versionedFigureFile(file),cell);
    else cell.append(el("p", "文件暂不可预览，请宿主核对该确切路径。", "muted"));
    if (!reference && file) {
      const savedFeedback=state.feedbackReceipts.get(state.taskId + ":" + file.relative_path);
      if(savedFeedback)cell.append(el("p","此图意见已保存："+savedFeedback,"figure-feedback-status"));
      const feedback=el("details",null,"figure-file-feedback");feedback.append(el("summary","对此图提意见"));
      feedback.addEventListener("toggle",()=>{if(feedback.open && feedback.children.length===1)renderFigureFeedback(file,feedback);});cell.append(feedback);
    }
    if (reference && file) {
      const sources = el("div",null,"reference-original-links");
      const links=referenceOriginalLinks(file,state.referencePairs,state.referenceDocuments,state.taskId,location.origin);
      for (const item of links) {
        const link=el("a",item.label,"file-link reference-original-link");link.href=item.url;
        link.target="_blank";link.rel="noopener noreferrer";link.title=item.note;
        const localDocument=state.referenceDocuments.find(doc=>{
          const url=allowedTaskUrl(doc.content_url,state.taskId,location.origin);
          return url && new URL(url).pathname===new URL(item.url).pathname && new URL(item.url).origin===location.origin;
        });
        if(localDocument)link.addEventListener("click",event=>{
          if(event.button!==0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)return;
          event.preventDefault();openFileZoom({...localDocument,filename:"原文 · "+localDocument.filename,content_url:item.url},link);
        });
        sources.append(link);
      }
      if(!links.length) sources.append(el("span","原文尚未关联，请宿主补充来源。","muted"));
      cell.append(sources);
    }
    return cell;
  }
  function decisionFiles(decision, container) {
    const rows=pairedFigureRows(decision,state.referencePairs);
    if(!rows.length){container.append(el("p","尚未登记可与参考图配对的当前图件。","muted"));return;}
    const hasReferences = rows.some(row => row.references.length > 0);
    const table=el("div",null, hasReferences ? "figure-paired-table" : "figure-paired-table is-unpaired-only");
    if (hasReferences) {
      const head=el("div",null,"figure-paired-columns");head.append(el("strong","我们的图"),el("strong","对应参考图"));table.append(head);
    }
    for (const row of rows) {
      const pair=el("div",null, row.references.length ? "figure-paired-row" : "figure-paired-row is-unpaired");
      pair.dataset.studyFile=row.file;
      const study=pairedFileCell(row.file);
      const options=optionDetails(decision).filter(option=>(option.files||[]).some(path=>figureStem(path)===figureStem(row.file)));
      if(options.length){
        const chosen=decision.status==="resolved" && options.find(option=>option.option_id===decision.option_id);
        study.prepend(el("p",chosen ? `已保存选择：${chosen.label || chosen.option_id}` : options.map(option=>option.label || option.option_id).join(" / "),"paired-candidate-label"));
      }
      pair.append(study);
      const reference=el("div",null, row.references.length ? "figure-paired-reference-list" : "figure-paired-reference-list is-empty");
      if(row.shared) reference.append(el("p","本图共用参考（尚未登记逐子图配对，不按列表顺序猜配）","muted"));
      if(!row.references.length) {
        const note = el("div", null, "figure-unpaired-note");
        note.append(el("strong", "对应参考图"), el("p", decision.figure?.reference_note || "尚未关联对应参考图；不会自动拿其他图来凑对。", "muted"));
        reference.append(note);
      }
      for(const ref of row.references) reference.append(pairedFileCell(ref,true));
      pair.append(reference);table.append(pair);
    }
    container.append(table);
    // Prebuilt comparison sheets are supporting files, never the reference column.
    const comparisons=decision.figure?.comparison_files || [];
    if(comparisons.length){const details=el("details",null,"paired-extra-comparisons");details.append(el("summary","已有整页对照文件"));
      details.addEventListener("toggle",()=>{if(details.open && details.children.length===1)for(const path of comparisons){const f=optionFiles({files:[path]},state.files,state.taskId,location.origin)[0];if(f)figureFile(f,details);}});container.append(details);}
  }
  function isPreviewableFigureFile(file) {
    return ["application/pdf", "image/png", "image/jpeg", "image/svg+xml", "image/webp", "image/gif"].includes(file.media_type)
      && Boolean(allowedTaskUrl(file.content_url, state.taskId, location.origin));
  }
  function renderDiscoveredFigures(container) {
    const files=state.files.filter(isPreviewableFigureFile);
    const mapped=new Set(state.referencePairs.map(pair=>pair.figure_file));
    const references=new Set(state.referencePairs.map(pair=>pair.reference_file));
    const current=uniqueFigureFormats(files.filter(file=>mapped.has(file.relative_path) ||
      /^(?:paper\/figures\/|paper\/figure-candidates\/)/.test(file.relative_path)
      && !/\/(?:history[^/]*|archive[^/]*|references?|sources?)\//i.test(file.relative_path)
      && !/参考|reference|comparison|对照/i.test(file.filename)).map(file=>file.relative_path));
    const card=el("div",null,"figure-discovery");card.append(el("h4","已有图件与参考"),el("p","此处仅展示文件；没有登记选择方案，不代表已采用或已审阅。","muted"));
    if(current.length){
      current.sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
      for(const path of current) decisionFiles({figure:{current_files:[path],reference_files:files.filter(file=>references.has(file.relative_path) || /参考|reference/i.test(file.filename)).map(file=>file.relative_path),comparison_files:[]},allowed_decision_details:[]},card);
    }else card.append(el("p","尚无明确的当前图件。宿主保存图件和对应参考后会逐行显示；其他文件仍可在下方目录查看。","muted"));
    for(const warning of state.referenceWarnings)card.append(el("p",warning,"muted"));
    container.append(card);
  }
  function renderUnregisteredCurrentFigures(container, units) {
    const represented = new Set(units.flatMap(unit=>pairedFigureRows(unit.current,state.referencePairs).map(row=>figureStem(row.file))));
    const files=uniqueFigureFormats(state.files.filter(file=>/^paper\/figures\/[^/]+$/.test(file.relative_path)
      && isPreviewableFigureFile(file) && !/参考|reference|comparison|对照/i.test(file.filename)
      && !represented.has(figureStem(file.relative_path))).map(file=>file.relative_path));
    if(!files.length)return;
    const section=el("section",null,"figure-unregistered-current");section.append(el("h4","当前图件目录"),el("p","以下是宿主保存的当前图件；未登记单独选择的文件只供对照查看，不表示新增采用记录。","muted"));
    const base=path=>figureStem(path).split("/").at(-1);
    files.sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
    for(const file of files){
      const refs=state.files.filter(item=>base(item.relative_path).replace(/(?:[_ -]?(?:参考图?|reference|ref))$/i,"")===base(file) && figureStem(item.relative_path)!==figureStem(file)).map(item=>item.relative_path);
      decisionFiles({figure:{current_files:[file],reference_files:refs,comparison_files:[]},allowed_decision_details:[]},section);
    }
    container.append(section);
  }
  function renderDecisions() {
    const signature = JSON.stringify([state.taskId, decisionsOf(state.task), state.task.historical_decisions,
      currentPhase(state.task), state.files, state.referencePairs, state.referenceDocuments, state.view, state.activeFigure, [...state.pending.keys()], [...state.inFlight]]);
    if (signature === state.renderingChoices) return; state.renderingChoices = signature;
    for (const selector of ["#motivation-decisions", "#figure-decisions", "#other-decisions"]) $(selector).replaceChildren();
    let ordered = [...decisionsOf(state.task)].sort((a, b) => {
      const pending = (d) => d.status === "pending" && !d.stale;
      return Number(pending(b)) - Number(pending(a))
        || (Date.parse(b.confirmed_at) || 0) - (Date.parse(a.confirmed_at) || 0);
    });
    const units = orderedFigureUnits(decisionsOf(state.task));
    const visibleUnits = units.filter(unit => !unit.historical);
    const position = new Map(visibleUnits.map((unit,index)=>[unit.current.decision_id,index]));
    ordered = ordered.filter(d=>decisionPhase(d)!=="figure").concat(
      ordered.filter(d=>decisionPhase(d)==="figure").sort((a,b)=>(position.get(a.decision_id)??9999)-(position.get(b.decision_id)??9999)));
    if (!visibleUnits.some(unit => unit.key === state.activeFigure))
      state.activeFigure = (visibleUnits.find(unit => unit.current.status === "pending") || visibleUnits[0])?.key || null;
    const navigation = el("nav", null, "figure-stepper"); navigation.setAttribute("aria-label", "图件与子图");
    navigation.hidden = visibleUnits.length <= 1;
    const workspace = el("div", null, "figure-focus figure-paired-list");
    const history = el("details", null, "figure-versions"); history.append(el("summary", "查看历史版本"));
    const currentIds = new Set(visibleUnits.map(unit => unit.current.decision_id));
    for (const [index, unit] of visibleUnits.entries()) {
      const button = el("button", null, "figure-step"); button.type = "button";
      button.dataset.figureKey = unit.key; button.setAttribute("aria-current", String(unit.key === state.activeFigure));
      button.append(el("span", String(index + 1), "figure-step-number"), el("strong", figureTitle(unit.current, index)),
        el("small", unit.current.status === "pending" ? "待选择" : "已保存意见"));
      button.addEventListener("click", () => {
        const row = [...workspace.querySelectorAll("form[data-decision-id]")].find(form=>form.dataset.decisionId===unit.current.decision_id);
        row?.scrollIntoView({behavior:"auto",block:"start"});
      }); navigation.append(button);
    }
    if (visibleUnits.length) { $("#figure-decisions").append(navigation); renderUnregisteredCurrentFigures(workspace,visibleUnits); }
    else renderDiscoveredFigures(workspace);
    $("#figure-decisions").append(workspace, history);
    for (const decision of ordered) {
      if (decision.stale && decisionPhase(decision) !== "figure") continue;
      const decisionStage = decisionPhase(decision), phase = decisionStage || currentPhase(state.task);
      const unit = units.find(unit => unit.records.includes(decision));
      const isCurrentFigure = decisionStage === "figure" && currentIds.has(decision.decision_id);
      // Every current figure/panel remains visible; navigation only scrolls to it.
      const container = decisionStage === "figure" ? (isCurrentFigure ? workspace : history)
        : $(decisionStage === "contribution" ? "#motivation-decisions" : "#other-decisions");
      const card = el("form", null, "public-decision"); card.dataset.decisionId = decision.decision_id;
      const choiceStatus = decisionStage === "figure" ? figureHeading(decision, card, Math.max(0, visibleUnits.indexOf(unit))) : null;
      if (!choiceStatus) card.append(el("h4", decision.prompt || "请核对并选择"));
      if (decision.status !== "pending" || decision.stale) {
        if (!choiceStatus) card.append(el("p", decision.stale ? "候选需要宿主更新，暂不提交。" : decision.status === "resolved" ? `已选择：${optionDetails(decision).find((o) => o.option_id === decision.option_id)?.label || decision.option_id}` : "宿主记录，仅供查看。"));
        if (decision.reason) card.append(el("p", choiceStatus ? shortFigureText(decision.reason, 100) : decision.reason, "figure-saved-reason"));
        const selected = optionDetails(decision).find((o) => o.option_id === decision.option_id);
        if (selected?.description && !choiceStatus) card.append(el("p", selected.description));
        if (decisionStage === "figure") {
          const record = el("details", null, "figure-decision-history");
          record.dataset.decisionId = decision.decision_id;
          record.open = isCurrentFigure;
          record.append(el("summary", isCurrentFigure ? "当前保存的用户意见" : "历史版本：" + figureTitle(decision, 0)), card);
          // Build comparison controls only when this record is actually opened.
          let built = false;
          const show = () => {
            if (record.open && !built) { built = true; decisionFiles(decision, card); }
            if (!record.open) collapseFigurePreviews(record);
          };
          record.addEventListener("toggle", show); show(); container.append(record);
        } else {
          if (selected) for (const file of optionFiles(selected, state.files, state.taskId, location.origin)) filePreview(file, card);
          container.append(card);
        }
        continue;
      }
      const draftKey = `${state.taskId}:${decision.decision_id}`;
      const localKey = keyFor("decision", decision.decision_id);
      let draft = state.decisionDrafts.get(draftKey) || readLocalDraft(localKey);
      if (!draft || !same(draft.binding, decisionBinding(decision))) {
        draft = {option_id: "", reason: "", binding: decisionBinding(decision)};
        state.decisionDrafts.set(draftKey, draft);
      }
      const saveDraft = () => { state.decisionDrafts.set(draftKey, draft); writeLocalDraft(localKey, draft); };
      if (decisionStage === "figure") decisionFiles(decision, card);
      const key = keyFor("decision", decision.decision_id), pending = state.pending.get(key);
      if (pending) { draft.option_id = pending.body.payload.option_id; draft.reason = pending.body.payload.reason; }
      if (choiceStatus) syncFigureChoiceStatus(choiceStatus, decision, draft, Boolean(pending));
      const fields = el("fieldset"); fields.disabled = !editable(phase) || Boolean(pending) || state.inFlight.has(key);
      fields.append(el("legend", "请选择一个方案"));
      for (const option of optionDetails(decision)) {
        const label = el("label", null, "public-option"), radio = el("input"); radio.type = "radio"; radio.name = decision.decision_id;
        radio.value = option.option_id; radio.checked = draft.option_id === option.option_id; radio.required = true;
        radio.addEventListener("change", () => { draft.option_id = option.option_id; saveDraft();
          if (choiceStatus) syncFigureChoiceStatus(choiceStatus, decision, draft); });
        label.append(radio, el("strong", choiceStatus ? shortFigureText(option.label || option.option_id, 70) : option.label || option.option_id));
        if (option.description && !choiceStatus) label.append(el("p", option.description));
        if (option.risk && !choiceStatus) label.append(el("p", `注意：${option.risk}`, "muted"));
        fields.append(label);
        if (decisionStage !== "figure") {
          const matches = optionFiles(option, state.files, state.taskId, location.origin);
          for (const file of matches) { const preview = el("div", null, "public-option-file"); preview.append(el("small", file.filename || file.relative_path)); filePreview(file, preview); fields.append(preview); }
          if ((option.files || []).length > matches.length) fields.append(el("p", "部分候选文件尚不可预览，请联系宿主核对。", "muted"));
        }
      }
      const reasonLabel = el("label", "选择理由或修改意见（选填）"), reason = el("textarea", null, "choice-reason"); reason.rows = 2; reason.placeholder = tr("可选：填写选择理由、局部修改建议或细节要求…"); reason.value = pending && draft.reason === "无" ? "" : draft.reason;
      reason.addEventListener("input", () => { draft.reason = reason.value; saveDraft(); }); reasonLabel.append(reason); fields.append(reasonLabel);
      const submitBar = el("div", null, "figure-submit-bar");
      const button = el("button", pending ? "重试原提交" : "保存我的选择", "button strong"); button.type = "submit";
      button.disabled = !editable(phase) || state.inFlight.has(key);
      submitBar.append(button);
      card.append(fields, submitBar);
      card.addEventListener("submit", async (event) => {
        event.preventDefault(); if (!editable(phase)) return;
        if (!pending && !draft.option_id) return;
        const original = decisionBinding(decision);
        await mutate(key, (fresh) => {
          const current = decisionsOf(fresh).find((d) => d.decision_id === decision.decision_id);
          if (!current || current.status !== "pending" || current.stale || !same(original, decisionBinding(current))) throw new PublicError("候选已变化，请重新核对。", "choice_changed");
          return entryFor("decision", fresh, `${taskPath(fresh.task_id)}/decisions/${encodeURIComponent(current.decision_id)}/resolution`,
            {decision_id: current.decision_id, option_id: draft.option_id, reason: draft.reason.trim() || "无", confirmed_at: new Date().toISOString()}, original);
        });
      });
      container.append(card);
    }
    if (history.children.length === 1) history.hidden = true;
    for (const record of state.task.historical_decisions || []) {
      const phase = decisionPhase(record) || (String(record.decision_id || "").includes("figure") ? "figure" : "contribution");
      const container = $(phase === "figure" ? "#figure-decisions" : "#motivation-decisions");
      const card = el("article", null, "public-decision");
      card.append(el("h4", "此前保存的选择（只读）"));
      for (const choice of record.decisions || []) {
        const candidate = (record.candidates || []).find((item) => item.candidate_id === choice.candidate_id);
        const label = choice.choice === "accept" ? "已保留" : choice.choice === "reject" ? "未采用" : "已记录";
        card.append(el("p", `${label}：${candidate?.statement || choice.label || "此前方案"}`));
        if (choice.reason) card.append(el("p", choice.reason, "muted"));
      }
      const history = el("details", null, "figure-decision-history");
      history.append(el("summary", "此前保存的选择（只读）"), card); container.append(history);
    }
    for (const selector of ["#motivation-decisions", "#figure-decisions"]) if (!$(selector).children.length) $(selector).append(el("p", "宿主尚未提供需要确认的候选。", "muted"));
  }
  function renderFigures() {
    const list = $("#task-figure-records"), signature = JSON.stringify([state.taskId, state.files, state.view, currentPhase(state.task)]);
    const view = state.figureCatalogViews.get(state.taskId) || {directories: new Set(), previews: new Set()};
    state.figureCatalogViews.set(state.taskId, view);
    if (list.dataset.contentKey !== signature) {
      list.dataset.contentKey = signature; list.replaceChildren();
      const directories = new Map();
      for (const file of state.files) {
        const directory = file.relative_path.slice(0, file.relative_path.lastIndexOf("/"));
        if (!directories.has(directory)) directories.set(directory, []);
        directories.get(directory).push(file);
      }
      for (const [directory, files] of directories) {
        const group = el("details", null, "figure-directory");
        group.append(el("summary", `${directory} · ${files.length} 个文件`));
        const showDirectory = () => {
          if (!group.isConnected) return;
          if (group.open) view.directories.add(directory);
          else {
            view.directories.delete(directory);
            for (const file of files) view.previews.delete(file.relative_path);
          }
          if (group.open && group.children.length === 1) {
            const grid = el("div", null, "figure-comparison-grid");
            group.append(grid);
            for (const file of files) figureFile(file, grid, view);
          }
          if (!group.open) collapseFigurePreviews(group);
        };
        group.addEventListener("toggle", showDirectory);
        group.open = view.directories.has(directory); list.append(group); showDirectory();
      }
    }
    setText("#task-figures-summary", state.filesError ? "图件目录暂时无法读取，请刷新重试。" : state.files.length ? `自动发现 ${state.files.length} 个实际文件。按目录折叠，点击才加载预览；文件名与格式不代表采用状态。` : "宿主将图件保存到约定目录后，这里自动显示。");
  }
  function appendArtifact(container, artifact) {
    const row = el("div", null, "task-file-row");
    row.append(el("strong", artifact.filename || artifact.file_name || artifact.artifact_type || "论文文件"));
    if (artifact.stale || artifact.historical || artifact.freshness === "stale") row.append(el("small", "历史版本／需重新核对", "muted"));
    for (const [key, title] of [["content_url", "预览"], ["download_url", "下载"]]) {
      const url = key === "content_url" ? readerUrl(artifact) : allowedTaskUrl(artifact[key], state.taskId, location.origin);
      if (url && key === "content_url") {
        const preview = el("details", null, "artifact-preview"), summary = el("summary", "预览");
        preview.append(summary);
        preview.addEventListener("toggle", () => {
          if (preview.open && !preview.querySelector(".artifact-preview-content")) {
            const body = el("div", null, "artifact-preview-content");
            preview.append(body);
            filePreview(artifact, body, {enlarge: false});
          }
        });
        row.append(preview);
        if (supportsReader(artifact)) {
          const open = el("button", "全屏阅读", "button artifact-reader-button"); open.type = "button";
          open.addEventListener("click", () => openFileZoom(artifact, open));
          row.append(open);
        }
      } else if (url) {
        const link = el("a", title, "file-link"); link.href = url;
        link.download = artifact.filename || artifact.file_name || "";
        const status = el("span", "", "download-status"); status.setAttribute("role", "status");
        link.addEventListener("click", async event => {
          event.preventDefault(); if (link.dataset.busy) return;
          link.dataset.busy = "true"; status.textContent = "正在准备下载…";
          try {
            const response = await fetch(url, {headers: {"X-PaperSpine5-Session": state.session}, cache: "no-store", signal: AbortSignal.timeout(60000)});
            if (!response.ok) throw new Error("下载失败，请重试（" + response.status + "）");
            const blob = await response.blob();
            if (!blob.size) throw new Error("文件为空，请重新生成。");
            const objectUrl = URL.createObjectURL(blob), save = el("a");
            const encoded = response.headers.get("content-disposition")?.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
            save.href = objectUrl; save.download = encoded ? decodeURIComponent(encoded) : link.download || "论文文件";
            document.body.append(save); save.click(); save.remove();
            setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
            status.textContent = "已交给浏览器保存，请在下载列表查看。";
            showSupportMilestone(recordPackageUse(artifact, state));
          } catch (error) { status.textContent = error.message || "下载未完成，请重试。"; }
          finally { delete link.dataset.busy; }
        });
        row.append(link, status);
      }
    }
    row.append(el("small", [size(artifact.size_bytes), artifact.created_at ? new Date(artifact.created_at).toLocaleString() : ""].filter(Boolean).join(" · "), "muted"));
    container.append(row);
  }
  function isManuscriptArtifact(artifact) {
    // Public manuscript roles, including the legacy Runner's mapped outputs.
    // A note rendered as PDF is still a note; never promote it by filename.
    return ["manuscript_source", "pdf", "docx", "tex"].includes(artifact.artifact_type);
  }
  function artifactTypePhase(artifact) {
    if (isManuscriptArtifact(artifact)) return "draft";
    switch (artifact.artifact_type) {
      case "figure": return "figure";
      case "evidence_graph": return "evidence";
      case "review_packet": return "review";
      default: return null; // Notes and bibliography can belong to several stages.
    }
  }
  function renderArtifacts() {
    const list = $("#task-artifact-list"), delivery = $("#delivery-files");
    const artifacts = state.task.domain_artifacts ?? state.task.artifacts ?? [];
    const signature = JSON.stringify([state.taskId, artifacts]);
    if (list.dataset.contentKey !== signature) {
      list.dataset.contentKey = signature; list.replaceChildren(); delivery.replaceChildren();
      const primary = el("div", null, "delivery-primary"); delivery.append(primary);
      for (const [group, label] of [["pdf","论文 PDF"],["package","分享包"],["workspace","完整本地包"],["word","可编辑稿"],["unspecified_package","其他文件包（内容范围未标注）"],["figures","图件"],["sources","源文件与研究记录"],["history","历史版本"]]) {
        const matches = artifacts.filter(a => artifactGroup(a) === group); if (!matches.length) continue;
        const important = ["pdf","word","package","workspace"].includes(group);
        const section = el(important ? "section" : "details", null, important ? "delivery-card" : "delivery-secondary");
        section.dataset.downloadGroup = group;
        section.append(el(important ? "h4" : "summary", label));
        if (group === "unspecified_package") section.append(el("p", "旧版本未标注是否含原始材料，分享前请核对包内内容。", "muted"));
        if (group === "package") section.append(el("p", "宿主标注为可分享的论文包。", "muted"));
        if (group === "workspace") section.append(el("p", "完整本地工作区，仅供本地保存。", "muted"));
        for (const artifact of matches) appendArtifact(section, artifact);
        (important ? primary : delivery).append(section);
      }
      const manuscripts = artifacts.filter(isManuscriptArtifact);
      const historical = a => a.stale || a.historical || ["stale", "historical"].includes(a.freshness);
      const current = manuscripts.filter(a => !historical(a));
      for (const artifact of current) appendArtifact(list, artifact);
      if (!current.length) list.append(el("p", "尚未登记当前可识别的论文稿件。阶段可回看不表示主稿已生成。研究笔记、证据和图件请到相关阶段查看；归属未明的文件保留在“本地目录与历史”。", "muted"));
      const older = manuscripts.filter(historical);
      if (older.length) {
        const history = el("details", null, "manuscript-history"); history.append(el("summary", "历史稿件（需重新核对）"));
        for (const artifact of older) appendArtifact(history, artifact);
        list.append(history);
      }
    }
    const manifest = state.task.delivery_manifest;
    setText("#task-delivery-summary", manifest?.ready && !state.task.delivery?.stale ? "本地论文包可下载，投稿条件以实际审阅为准。" : "当前完整交付包尚未就绪；已有文件仍可查看。");
    const issues = $("#task-delivery-blockers"); issues.replaceChildren();
    for (const item of manifest?.blockers || []) issues.append(el("li", typeof item === "string" ? item : item.message || item.code));
  }
  function renderRecords() {
    const groups = Object.fromEntries(["intake", "research", "contribution", "evidence", "draft", "figure", "review"]
      .map(phase => [phase, $("#" + phase + "-records")]));
    const artifacts = state.task.domain_artifacts ?? state.task.artifacts ?? [];
    const milestones = state.task.milestones || [];
    const byId = new Map(artifacts.map(a => [a.artifact_id, a]));
    const phaseOf = m => m.stage || m.phase;
    const knownPhase = phase => PHASES.some(([id]) => id === phase);
    const linked = new Set(milestones.filter(m => knownPhase(phaseOf(m))).flatMap(m => m.artifact_ids || []));
    const unassigned = artifacts.filter(a => !knownPhase(a.stage) && !linked.has(a.artifact_id) && !artifactTypePhase(a));
    const unassignedNotes = unassigned.filter(a => a.artifact_type === "research_note");
    const reviews = state.task.reviews || [];
    const revisions = state.task.revision_requests || (state.task.revision_request ? [state.task.revision_request] : []);
    const reviewEvents = state.events.filter(event => event.task_id === state.taskId && event.event_type === "review.submitted");
    // A task-version-only poll must not close a note the reader has opened.
    const signature = JSON.stringify([state.taskId, milestones, artifacts, state.task.evidence_links, state.task.findings, reviews, reviewEvents, revisions]);
    if (groups.research.dataset.contentKey !== signature) {
      Object.values(groups).forEach(node => { node.replaceChildren(); node.dataset.contentKey = signature; });
      for (const [phase, container] of Object.entries(groups)) {
        const relevant = milestones.filter(m => phaseOf(m) === phase);
        if (phase === "review") {
          renderReviewMaterials(container, artifacts, relevant, revisions);
          continue;
        }
        for (const milestone of relevant) {
          const row = el("div", null, "task-file-row milestone-record");
          row.append(el("small", "历史里程碑 · 登记记录，非当前运行状态", "milestone-record-label"));
          row.append(el("strong", milestone.title || phaseLabel(phase)), el("p", milestone.summary || milestone.description || "宿主已保存此项工作记录。"));
          container.append(row);
        }
        // These are related files, not inferred ownership: a milestone can cite
        // an earlier stage's artifact. Never classify by filename or current phase.
        const ids = new Set(relevant.flatMap(m => m.artifact_ids || []));
        const files = artifacts.filter(a => (a.stage === phase || artifactTypePhase(a) === phase || ids.has(a.artifact_id))
          && (phase !== "draft" || !isManuscriptArtifact(a)));
        if (files.length) {
          const list = el("div", null, "stage-artifact-list");
          list.append(el("h4", phase === "draft" ? "主稿阶段相关文件（非主稿）" : "相关文件"));
          for (const artifact of files) appendArtifact(list, artifact);
          container.append(list);
        }
        if (["research", "evidence"].includes(phase) && unassignedNotes.length) {
          const shared = el("details", null, "unassigned-research-notes");
          shared.append(el("summary", `其他研究笔记（阶段未标注或未识别） · ${unassignedNotes.length}`));
          for (const artifact of unassignedNotes) appendArtifact(shared, artifact);
          container.append(shared);
        }
      }
      for (const link of state.task.evidence_links || []) groups.evidence.append(el("p", `${link.claim_id}：${link.relation} → ${link.evidence_id}`));
      renderReviewRecords(groups.review, reviews, artifacts, reviewEvents);
      for (const [phase, node] of Object.entries(groups)) if (!node.children.length && ["research", "evidence", "review"].includes(phase)) node.append(el("p", `尚无可读取的${phaseLabel(phase)}记录。`, "muted"));
      const unknown = $("#unassigned-artifact-records"); unknown.replaceChildren(); unknown.hidden = !unassigned.length;
      unknown.append(el("summary", `归属未明的文件 · ${unassigned.length}`));
      if (unassigned.length) {
        unknown.append(el("p", "现有记录无法可靠确定所属阶段，保留文件入口；不据文件名认定为论文稿件。", "muted"));
        for (const artifact of unassigned) appendArtifact(unknown, artifact);
      }
    }
    const events = $("#task-history-records");
    const staleDecisions = decisionsOf(state.task).filter(item => item.stale);
    const historyKey = JSON.stringify([state.taskId, state.events, artifacts, staleDecisions]);
    if (events.dataset.contentKey !== historyKey) {
      events.dataset.contentKey = historyKey; events.replaceChildren();
      for (const decision of staleDecisions) {
        const record = el("details"), summary = el("summary", "已失效的历史候选");
        record.append(summary, el("p", decision.prompt || "历史候选"));
        if (decision.reason) record.append(el("p", decision.reason));
        events.append(record);
      }
      for (const event of state.events.slice(-30).reverse()) {
        const row = el("div", null, "task-history-entry");
        row.append(el("p", `${event.occurred_at || event.created_at || ""} ${event.event_type || event.type || ""}`));
        const artifact = byId.get(event.payload?.artifact_id);
        if ((event.event_type || event.type) === "artifact.published" && artifact
            && (!event.payload.sha256 || event.payload.sha256 === artifact.sha256)) appendArtifact(row, artifact);
        events.append(row);
      }
    }
    const feedback = $("#feedback-history");
    const feedbackKey = JSON.stringify([state.taskId, revisions]);
    // Keep the reader's disclosure and scroll position through ordinary polls.
    if (feedback.dataset.contentKey !== feedbackKey) {
      feedback.dataset.contentKey = feedbackKey; feedback.replaceChildren();
      for (const item of revisions) {
        const text = item.feedback || item.text || "已保存意见", characters = [...text];
        const long = characters.length > 180 || text.split("\n").length > 4;
        const row = el("div", null, "feedback-record");
        const excerpt = [...text.replace(/\s+/gu, " ").trim()];
        row.append(el("p", long ? excerpt.slice(0, 180).join("") + (excerpt.length > 180 ? "…" : "") : text, "feedback-excerpt"));
        if (long) {
          const details = el("details", null, "feedback-full");
          const summary = el("summary", `展开全文（${characters.length} 字符）`);
          const full = el("div", text, "feedback-full-text");
          full.tabIndex = 0; full.setAttribute("role", "region"); full.setAttribute("aria-label", "已保存意见全文");
          details.addEventListener("toggle", () => { summary.textContent = `${details.open ? "收起" : "展开"}全文（${characters.length} 字符）`; });
          details.append(summary, full); row.append(details);
        }
        feedback.append(row);
      }
    }
  }
  function renderReviewMaterials(container, artifacts, milestones, revisions) {
    const related = new Set(milestones.flatMap(milestone => milestone.artifact_ids || []));
    const files = artifacts.filter(artifact => artifact.stage === "review" || related.has(artifact.artifact_id)
      || (artifact.stage === "draft" && isManuscriptArtifact(artifact)));
    const current = files.filter(artifact => !artifact.stale && !artifact.historical && !["stale", "historical"].includes(artifact.freshness));
    const history = files.filter(artifact => !current.includes(artifact));
    const latest = milestones.at(-1);
    if (latest) container.append(el("p", latest.summary || latest.description, "review-latest-summary"));
    if (current.length) {
      const section = el("section", null, "review-materials");
      section.append(el("h4", "当前稿件与核查材料"));
      current.forEach(file => appendArtifact(section, file));
      container.append(section);
    }
    if (revisions.length) {
      const list = el("section", null, "review-revisions");
      list.append(el("h4", "已保存的返修意见"));
      [...revisions].reverse().forEach(item => {
        const row = el("details", null, "review-revision-entry");
        const label = Number.isInteger(item.requested_revision) ? (uiLang === "en" ? "Revision " : "返修版本 ") + item.requested_revision : "已保存的返修意见";
        row.append(el("summary", label), el("p", item.feedback || item.text || "已保存意见"));
        list.append(row);
      });
      container.append(list);
    }
    if (history.length || milestones.length > 1) {
      const older = el("details", null, "review-material-history");
      older.append(el("summary", "历史稿件与核查材料"));
      for (const milestone of milestones.slice(0, -1).reverse()) {
        const summary = milestone.summary || milestone.description;
        if (summary) older.append(el("p", summary, "muted"));
      }
      history.forEach(file => appendArtifact(older, file));
      container.append(older);
    }
  }
  function renderReviewRecords(container, reviews, artifacts, reviewEvents) {
    const list = el("div", null, "review-records"), byId = new Map(artifacts.map(a => [a.artifact_id, a]));
    const allFindings = state.task.findings || [], displayedFindings = new Set();
    const historical = artifact => artifact.stale || artifact.historical || ["stale", "historical"].includes(artifact.freshness);
    const appendFinding = (parent, finding) => {
      const status = finding.status === "resolved" ? "已处理" : finding.status === "open" ? "待处理" : "状态未记录";
      const severity = {blocking: "阻断", major: "主要", minor: "次要"}[finding.severity];
      parent.append(el("p", `${status}${severity ? ` · ${severity}` : ""}：${finding.message || finding.description || finding.finding_id}`));
    };
    for (const review of [...reviews].reverse()) {
      const findings = allFindings.filter(f => f.review_id ? f.review_id === review.review_id : (review.finding_ids || []).includes(f.finding_id));
      const unresolved = findings.filter(f => f.status === "open" && ["major", "blocking"].includes(f.severity));
      const conflict = review.decision === "pass" && unresolved.length > 0;
      const staleIds = new Set(review.stale_artifact_ids || []);
      const scope = (review.reviewed_artifact_ids || []).map(id => {
        const artifact = byId.get(id), hash = review.reviewed_hashes?.[id];
        const changed = review.stale || staleIds.has(id) || (artifact && (historical(artifact)
          || (hash && artifact.sha256 && hash !== artifact.sha256)));
        return {id, artifact, hash, status: changed ? "changed" : !artifact || !hash || !artifact.sha256 ? "unknown" : "current"};
      });
      const changed = scope.filter(item => item.status === "changed").length;
      const freshness = review.stale ? "stale" : changed ? changed === scope.length ? "stale" : "partial"
        : !scope.length || scope.some(item => item.status === "unknown") ? "unknown" : "current";
      const card = el("article", null, "review-record"); card.dataset.reviewId = review.review_id; card.dataset.freshness = freshness;
      const heading = el("div", null, "review-record-heading"), result = el("h4", null, "review-result");
      const conclusion = {pass: "通过（PASS）", block: "未通过（BLOCK）"}[review.decision];
      result.textContent = conclusion ? `${freshness === "current" ? "审阅结论" : "当时结论"}：${conclusion}` : "审阅已登记 · 未记录结论";
      if (conflict) { result.textContent = "已记录 PASS · 仍有待处理问题"; result.classList.add("review-result-warning"); }
      else if (review.decision === "pass" && freshness === "current") result.classList.add("review-result-pass");
      heading.append(result, el("span", {current: "范围内文件与审阅版本一致", partial: "部分范围已更新", stale: "历史审阅 · 范围已更新", unknown: "适用版本未确认"}[freshness], "review-freshness"));
      card.append(heading);
      if (conflict) card.append(el("p", `审阅结论与问题状态不一致：${unresolved.length} 项主要或阻断问题仍待处理。`, "review-conflict"));
      const metadata = el("div", null, "review-metadata");
      metadata.append(el("p", `审阅者：${review.reviewer_id || "未记录"}`));
      const event = reviewEvents.find(event => event.payload?.review_id === review.review_id);
      const submittedAt = review.submitted_at || event?.occurred_at;
      if (Number.isInteger(review.reviewed_task_version)) metadata.append(el("p", `被审任务版本：${review.reviewed_task_version}`));
      else if (Number.isInteger(event?.task_version)) metadata.append(el("p", `审阅登记版本：${event.task_version}`));
      if (submittedAt) metadata.append(el("p", `登记时间：${Number.isFinite(Date.parse(submittedAt)) ? new Date(submittedAt).toLocaleString() : submittedAt}`));
      card.append(metadata, el("p", conclusion ? "结论仅适用于本次记录的审阅范围与文件版本。" : "现有记录未包含明确结论；问题数量不能代替通过结论。", "muted"));
      const reportArea = el("div", null, "review-report"), report = byId.get(review.report_artifact_id);
      if (!review.report_artifact_id) reportArea.append(el("p", "未关联审阅报告。", "muted"));
      else if (!report || historical(report) || (review.report_sha256 && review.report_sha256 !== report.sha256))
        reportArea.append(el("p", "关联报告已更新或暂不可用；请由宿主核对原审阅报告。", "muted"));
      else {
        const content = allowedTaskUrl(report.content_url, state.taskId, location.origin);
        const download = allowedTaskUrl(report.download_url, state.taskId, location.origin);
        if (content) {
          const link = el("a", "打开审阅报告", "file-link"); link.href = content; link.target = "_blank"; link.rel = "noopener";
          reportArea.append(link);
        }
        if (download) {
          appendArtifact(reportArea, {...report, content_url: null});
          if (!content) {
            const link = reportArea.querySelector("a[download]");
            link.textContent = "下载审阅报告"; link.classList.add("review-report-download");
          }
        }
        if (!content && !download) reportArea.append(el("p", "关联报告暂不可打开或下载。", "muted"));
      }
      card.append(reportArea);
      const details = el("details", null, "review-scope");
      details.append(el("summary", `审阅范围与版本 · ${scope.length} 个文件`), el("p", `审阅记录：${review.review_id}`, "muted"));
      if (!scope.length) details.append(el("p", "未记录被审文件范围。", "muted"));
      for (const item of scope) {
        const row = el("div", null, "review-scope-file");
        row.append(el("strong", item.artifact?.filename || item.id), el("span", {changed: "已更新，原结论不覆盖当前版本", unknown: "当前版本无法核对", current: "版本一致"}[item.status]));
        row.append(el("small", `文件标识：${item.id}`), el("small", item.hash ? `被审文件 SHA-256：${item.hash}` : "被审文件版本未记录"));
        details.append(row);
      }
      card.append(details);
      const ids = new Set([...(review.finding_ids || []), ...findings.map(f => f.finding_id)]);
      card.append(el("p", Array.isArray(review.finding_ids) || findings.length ? `本次登记问题：${ids.size}` : "本次问题数未记录", "review-finding-count"));
      for (const finding of findings) { appendFinding(card, finding); displayedFindings.add(finding); }
      if (ids.size > findings.length) card.append(el("p", `${ids.size - findings.length} 项问题的详情暂不可读取。`, "muted"));
      list.append(card);
    }
    if (reviews.length) container.prepend(list);
    else container.prepend(el("p", "正式审阅结论尚未登记", "review-verdict-note muted"));
    const unassigned = allFindings.filter(finding => !displayedFindings.has(finding));
    if (unassigned.length) {
      const remaining = el("section", null, "review-unassigned-findings"); remaining.append(el("h4", "其他问题记录"));
      for (const finding of unassigned) appendFinding(remaining, finding);
      container.append(remaining);
    }
  }
  function renderBridge() {
    const bridge = state.task.skill_bridge || {}, list = $("#task-skill-bridge-files"); list.replaceChildren();
    for (const file of bridge.files || []) {
      const link = el("a", file.name, "file-link"); link.href = `${taskPath(state.taskId)}/skill-files/${encodeURIComponent(file.name)}`; link.target = "_blank"; link.rel = "noopener"; list.append(link);
    }
    setText("#task-skill-bridge-summary", bridge.files?.length ? "配置、选择与意见保存在同一任务的交接文件中，供宿主读取。" : "宿主尚未提供交接文件。");
    setText("#package-directory", bridge.package_directory || "目录由宿主建立后可打开。");
  }
  function renderPendingSubmissions() {
    const list = $("#pending-submissions"); list.replaceChildren();
    list.hidden = Boolean(state.view && state.view !== currentPhase(state.task));
    if (list.hidden) return;
    for (const [key, entry] of state.pending) {
      if (entry.taskId !== state.taskId) continue;
      const label = {configuration: "配置", decision: "选择", feedback: "意见"}[entry.kind] || "提交";
      const button = el("button", `核对原${label}提交`, "button"); button.type = "button";
      button.disabled = state.inFlight.has(key);
      button.addEventListener("click", () => mutate(key, () => entry));
      list.append(el("p", `${label}结果尚待确认。核对会使用原请求，不会另造一次提交。`, "muted"), button);
    }
  }
  function renderEditability() {
    if (!state.task) return;
    const key = keyFor("configuration"), saved = state.pending.has(key);
    $("#configuration-fields").disabled = !editable("intake") || saved || state.inFlight.has(key);
    $("#configuration-submit").disabled = !editable("intake") || state.inFlight.has(key);
    setText("#configuration-submit", saved ? "重试原提交" : "保存设置");
    const feedbackKey = keyFor("feedback");
    $("#feedback-fields").disabled = state.pending.has(feedbackKey) || state.inFlight.has(feedbackKey);
    $("#feedback-submit").disabled = state.inFlight.has(feedbackKey);
    setText("#feedback-submit", state.pending.has(feedbackKey) ? "重试原提交" : "保存意见");
  }
  $("#configuration-form").addEventListener("input", (event) => {
    if (!state.task) return;
    const field = event.target.dataset.field; if (!field) return;
    const draft = state.configDrafts.get(state.taskId) || {values: {}, base: structuredClone(state.task.configuration || {})};
    if (field === "output_language") {
      if (event.target.id === "output-language-custom") draft.customLanguage = $("#output-language-custom").value;
      renderLanguageEditability();
    }
    if (field === "literature") {
      if (event.target.id === "literature-preset") {
        if (draft.literaturePreset === "custom" || (!draft.literaturePreset && literaturePreset(literatureValues(state.task.configuration?.literature)) === "custom"))
          draft.customPaperCounts = [$("#same-field-papers").value, $("#target-venue-papers").value];
        const preset = $("#literature-preset").value;
        const counts = preset === "custom" ? draft.customPaperCounts : [preset, preset];
        if (counts) { $("#same-field-papers").value = counts[0]; $("#target-venue-papers").value = counts[1]; }
      }
      draft.literaturePreset = $("#literature-preset").value;
      renderLiteratureEditability();
    }
    const value = configValues()[field]; draft.values[field] = value; state.configDrafts.set(state.taskId, draft);
    syncConfigVisuals();
    setText("#configuration-status", configurationDraftMessage(state.task, draft));
    $("#reload-saved-configuration").hidden = false;
    renderFocus();
  });
  $("#reload-saved-configuration").addEventListener("click", async () => {
    const id = state.taskId;
    if (!id || state.inFlight.size || state.pending.has(keyFor("configuration"))) return;
    try {
      const fresh = await readTask(id);
      if (id !== state.taskId || fresh.task_version < state.task.task_version) return;
      state.configDrafts.delete(id); state.task = fresh; render();
    } catch (error) { message(error.message, true); }
  });
  $("#configuration-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (!editable("intake")) return;
    const key = keyFor("configuration"), values = configValues(), draft = state.configDrafts.get(state.taskId);
    if (!state.pending.has(key) && (!values.formats.length || !values.research_mode)) { message("请选择交付格式和是否需要研究分析。", true); return; }
    await mutate(key, (fresh) => {
      // A reopened configuration node also permits confirming unchanged values.
      // Keep only fields already displayed and saved; do not add blank defaults
      // or transport metadata from historical configuration projections.
      const payload = fresh.configuration
        ? Object.keys(draft?.values || {}).length ? {...draft.values}
          : Object.fromEntries(Object.keys(values).filter((key) => Object.hasOwn(state.task.configuration || {}, key))
              .map((key) => [key, state.task.configuration[key]]))
        : values;
      // Displayed additive defaults are saved on explicit confirmation even for
      // an older configuration; unrelated fields remain patches, not resets.
      if (!Object.hasOwn(fresh.configuration || {}, "scene")) payload.scene ??= values.scene;
      if (!Object.hasOwn(fresh.configuration || {}, "literature")) payload.literature ??= values.literature;
      if (payload.literature) payload.literature = validatedLiterature(payload.literature);
      if (payload.target?.status === "known" && !payload.target.name?.trim())
        throw new PublicError("请填写已确定的目标期刊或会议名称。", "validation_failed");
      // Public literature retrieval is a standard Skill capability, not a user
      // permission checkbox. Preserve private-data boundaries when saving.
      payload.network_policy = {...(fresh.configuration?.network_policy || {}),
        allow_network: true, allow_external_upload: false};
      if (!Object.keys(payload).length) throw new PublicError("设置没有变化。", "validation_failed");
      const base = draft?.base || state.task.configuration || {};
      if (Object.keys(payload).some((field) => !same(fresh.configuration?.[field], base[field]))) throw new PublicError("宿主已更新这些设置，请重新核对后保存。", "choice_changed");
      writeSavedCustomLanguage(payload.output_language === "other" ? ($("#output-language-custom")?.value || "") : "");
      return entryFor("configuration", fresh, `${taskPath(fresh.task_id)}/configuration`, payload, base);
    });
  });
  $("#feedback-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (!state.task || (state.view && state.view !== currentPhase(state.task))) return;
    const key = keyFor("feedback"), id = state.taskId, scope = $("#feedback-scope").value;
    const text = $("#feedback-text").value.trim();
    if (!state.pending.has(key)) {
      if (state.taskId !== id) return;
      if (!text || [...text].length > 32000) { message("意见不能为空且不能超过 32,000 字符。", true); return; }
    }
    await mutate(key, (fresh) => {
      const entry = entryFor("feedback", fresh, `${taskPath(fresh.task_id)}/feedback`, {}, null);
      const {schema_version, payload, ...body} = entry.body;
      entry.body = {...body, feedback: text, scope};
      return entry;
    });
  });
  const workflowToggle = $("#global-stage-toggle");
  workflowToggle.addEventListener("click", () => {
    const expanded = workflowToggle.getAttribute("aria-expanded") !== "true";
    workflowToggle.setAttribute("aria-expanded", String(expanded));
    workflowToggle.setAttribute("aria-label", tr(expanded ? "收起 Spine" : "展开 Spine"));
    setText("#global-stage-toggle-verb", expanded ? "收起" : "展开");
    $("#global-stage-strip").classList.toggle("is-collapsed", !expanded);
    const shell = $("#global-workflow-shell");
    if (shell) shell.inert = !expanded;
    if (expanded) requestAnimationFrame(syncStageSlider);
  });
  $("#global-workflow-shell")?.addEventListener("scroll", syncStageSlider, {passive: true});
  window.addEventListener("resize", () => { syncStageSlider(); syncConfigVisuals(); }, {passive: true});
  const workbenchHeader = $(".workbench-header");
  new ResizeObserver(() => {
    workbenchHeader.parentElement.style.setProperty("--workbench-header-height", `${workbenchHeader.offsetHeight}px`);
  }).observe(workbenchHeader);
  $("#stage-return-current").addEventListener("click", () => { state.view = null; render(); });
  $("#copy-handoff").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("#host-handoff-text").textContent); setText("#handoff-status", "已复制，请发给当前选定的宿主（原对话或新对话）；复制没有启动 AI。"); }
    catch (_) { setText("#handoff-status", "请手动复制上方指令，发给有权访问任务文件的宿主。"); }
  });
  $("#open-package").addEventListener("click", async () => {
    const id = state.taskId; if (!id) return;
    try { const result = await request(`${taskPath(id)}/open-package`, {}); if (id === state.taskId) setText("#package-directory", result.opened ? "已打开当前任务目录。" : result.package_directory || "目录暂不可用。"); }
    catch (error) { message(error.message, true); }
  });
  const refreshButton = $("#refresh");
  refreshButton.addEventListener("click", async () => {
    if (refreshButton.dataset.spinning === "true") return;
    refreshButton.dataset.spinning = "true";
    refreshButton.classList.remove("is-spinning");
    void refreshButton.offsetWidth;
    refreshButton.classList.add("is-spinning");
    refreshButton.setAttribute("aria-busy", "true");
    const minSpin = new Promise((resolve) => setTimeout(resolve, 620));
    try {
      await Promise.all([refreshTasks(), refreshTask(), minSpin]);
    } catch (error) {
      await minSpin;
      message(error.message, true);
    } finally {
      delete refreshButton.dataset.spinning;
      refreshButton.classList.remove("is-spinning");
      refreshButton.removeAttribute("aria-busy");
    }
  });
  $("#home-open-recent").addEventListener("click", () => {
    const recent = state.tasks[0];
    if (recent) loadTask(recent.task_id).catch((error) => message(error.message, true));
  });
  $(".figure-file-catalog").addEventListener("toggle", (event) => {
    if (!event.currentTarget.open) {
      state.figureCatalogViews.get(state.taskId)?.previews.clear();
      collapseFigurePreviews(event.currentTarget);
    }
  });
  $("#retry-task-load").addEventListener("click", () => loadTask(state.taskId));
  const staticTextOriginals = new WeakMap();
  const staticAttrOriginals = new WeakMap();
  function translateStaticDom() {
    const roots = [".topbar-links", ".health", "#global-stage-summary", ".sidebar", "#workspace-empty", "#task-workspace", "#save-toast", "#support-milestone"];
    for (const sel of roots) {
      const root = $(sel);
      if (!root) continue;
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (node.parentElement?.closest("#lang-toggle")) continue;
        const trimmed = node.textContent.trim();
        if (!trimmed) continue;
        if (!staticTextOriginals.has(node)) {
          const lead = node.textContent.match(/^\s*/)[0];
          const trail = node.textContent.match(/\s*$/)[0];
          staticTextOriginals.set(node, {lead, text: trimmed, trail});
        }
        const orig = staticTextOriginals.get(node);
        const mapped = tr(orig.text);
        if (mapped !== orig.text || uiLang === "zh") node.textContent = orig.lead + mapped + orig.trail;
      }
      for (const nodeEl of [root, ...root.querySelectorAll("[placeholder],[aria-label],[title]")]) {
        if (nodeEl.closest("#lang-toggle")) continue;
        let saved = staticAttrOriginals.get(nodeEl);
        if (!saved) {
          saved = {};
          for (const attr of ["placeholder", "aria-label", "title"]) {
            const v = nodeEl.getAttribute(attr);
            if (v) saved[attr] = v;
          }
          staticAttrOriginals.set(nodeEl, saved);
        }
        for (const [attr, zhVal] of Object.entries(saved)) {
          nodeEl.setAttribute(attr, tr(zhVal));
        }
      }
    }
    for (const opt of document.querySelectorAll("#configuration-form select option, #feedback-form select option")) {
      if (!opt.dataset.zh) opt.dataset.zh = opt.textContent.trim();
      opt.textContent = tr(opt.dataset.zh);
    }
  }
  function syncLangThumb() {
    const toggle = $("#lang-toggle"), thumb = toggle?.querySelector(".lang-thumb");
    const active = toggle?.querySelector(`.lang-btn[data-lang="${uiLang}"]`);
    if (!toggle || !thumb || !active) return;
    const tr = toggle.getBoundingClientRect(), br = active.getBoundingClientRect();
    if (!br.width) return;
    thumb.style.width = `${br.width}px`;
    thumb.style.transform = `translate3d(${br.left - tr.left - 2}px, 0, 0)`;
  }
  function applyUiLanguage(lang) {
    uiLang = lang === "en" ? "en" : "zh";
    try { globalThis.localStorage?.setItem(UI_LANG_KEY, uiLang); } catch (_) {}
    document.documentElement.lang = uiLang === "en" ? "en" : "zh-CN";
    const toggle = $("#lang-toggle");
    if (toggle) {
      toggle.dataset.lang = uiLang;
      for (const btn of toggle.querySelectorAll(".lang-btn")) {
        const active = btn.dataset.lang === uiLang;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", String(active));
      }
    }
    translateStaticDom();
    buildNavigation();
    syncConfigLabels();
    if (state.tasks.length) renderTaskList();
    state.renderingChoices = "";
    renderedMaterials = "";
    for (const node of document.querySelectorAll("[data-content-key]")) delete node.dataset.contentKey;
    if (state.task) render();
    const expanded = $("#global-stage-toggle")?.getAttribute("aria-expanded") !== "false";
    $("#global-stage-toggle")?.setAttribute("aria-label", tr(expanded ? "收起 Spine" : "展开 Spine"));
    setText("#global-stage-toggle-verb", expanded ? "收起" : "展开");
    if ($("#health-dot")?.classList.contains("ok")) setText("#health-label", "本机服务已连接 · AI 状态未确认");
    setText("#build-label", "配置与文件保存在本机");
    syncLangThumb();
    syncStageSlider();
    syncConfigVisuals();
    requestAnimationFrame(() => { syncLangThumb(); syncStageSlider(); syncConfigVisuals(); });
    setTimeout(syncStageSlider, 260);
  }
  if ($("#global-workflow-progress")) new ResizeObserver(syncStageSlider).observe($("#global-workflow-progress"));
  for (const btn of document.querySelectorAll("#lang-toggle .lang-btn")) {
    btn.addEventListener("click", () => applyUiLanguage(btn.dataset.lang));
  }
  const sidebar = $("#task-sidebar"), sidebarToggle = $("#task-sidebar-toggle");
  const sidebarKey = "paperspine5.sidebar-collapsed.v1";
  function setSidebarCollapsed(collapsed) {
    sidebar.hidden = collapsed;
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    sidebarToggle.setAttribute("aria-expanded", String(!collapsed));
    sidebarToggle.textContent = tr(collapsed ? "展开任务栏" : "收起任务栏");
  }
  let initialSidebarCollapsed = matchMedia("(max-width: 620px)").matches;
  try {
    const saved = localStorage.getItem(sidebarKey);
    if (saved !== null) initialSidebarCollapsed = saved === "true";
  } catch (_) { /* Storage is optional. */ }
  setSidebarCollapsed(initialSidebarCollapsed);
  sidebarToggle.addEventListener("click", () => {
    const collapsed = !sidebar.hidden;
    setSidebarCollapsed(collapsed);
    try { localStorage.setItem(sidebarKey, String(collapsed)); } catch (_) { /* Keep the in-page choice. */ }
  });

  async function start() {
    buildNavigation();
    enhanceConfigControls();
    applyUiLanguage(uiLang);
    try {
      const session = await request("/api/v1/session");
      state.session = session.session_token || session.session || ""; state.csrf = session.csrf_token || "";
      setText("#health-label", "本机服务已连接 · AI 状态未确认"); setText("#build-label", "配置与文件保存在本机");
      $("#health-dot").classList.add("ok");
      const id = new URL(location.href).searchParams.get("task_id");
      await Promise.allSettled([refreshTasks(), id ? loadTask(id) : Promise.resolve()]);
      document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshTask(); });
      window.addEventListener("focus", () => refreshTask());
      setInterval(() => { if (!document.hidden && state.taskId && !state.inFlight.size) refreshTask().catch((error) => message(error.message, true)); }, 5000);
    } catch (error) { setText("#health-label", "连接未完成"); renderHomeRecent(true); message(error.message, true); }
  }
  start();
}
