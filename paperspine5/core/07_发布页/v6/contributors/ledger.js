// =========================================================================
// 1. CATEGORY & METRIC DEFINITIONS (Strictly aligned with PRD Section 4.1, 4.3)
// =========================================================================
const CATEGORIES = [
  { id: 'Code', label: 'Code', zh: '代码开发', desc: '代码开发、Bug 修复、功能实现（PR / Commit）' },
  { id: 'Documentation', label: 'Documentation', zh: '文档完善', desc: 'README、教程、规范文档与多语言指南（PR）' },
  { id: 'Review', label: 'Review', zh: '代码审查', desc: '代码审查与技术反馈（GitHub Review）' },
  { id: 'Issue', label: 'Issue', zh: '问题分析', desc: 'Bug 报告、复现分析与需求讨论（Issue）' },
  { id: 'Design', label: 'Design', zh: '设计系统', desc: 'UI、UX、品牌视觉与交互设计（PR / 设计链接 / 审核记录）' },
  { id: 'Research', label: 'Research', zh: '技术调研', desc: '科研评测、基准实验与方法论验证（PR / 报告 / 审核记录）' },
  { id: 'Community', label: 'Community', zh: '社区协作', desc: '社区组织、活动维护与生态推广（可核实证据 + 人工审核）' }
];

const METRIC_DEFINITIONS = [
  { key: 'totalContributors', rule: ['按 GitHub 用户 ID 去重统计当前名录中的账户。', 'Counts distinct GitHub user IDs in the current directory.'] },
  { key: 'mergedPRs', rule: ['仅统计 source_type = pull_request 且 lifecycle status = merged 的记录；关联同一 PR 的 Commits 不重复累加。', 'Counts merged pull requests. Commits within the same PR are counted together.'] },
  { key: 'activeContributors', rule: ['按已收录的 PR 统计最近 30 天提交过 PR 的名录账户。', 'Counts listed accounts that opened a recorded pull request in the past 30 days.'] }
];

const LANGUAGE_KEY = 'paperspine-language';
let language = 'en';
const requestedLanguage = new URLSearchParams(location.search).get('lang');
if (requestedLanguage === 'en' || requestedLanguage === 'zh-CN') {
  language = requestedLanguage;
} else {
  try {
    if (localStorage.getItem(LANGUAGE_KEY) === 'zh-CN') language = 'zh-CN';
  } catch {
    // Storage can be disabled in a standalone preview.
  }
}

function t(zh, en) {
  return language === 'en' ? en : zh;
}

function categoryLabel(id) {
  const category = CATEGORIES.find(item => item.id === id);
  return category ? t(category.zh, category.label) : id;
}

function syncMessage(log) {
  return log.status === 'success'
    ? t(`已核对 ${log.fetched} 条 PR，新增或更新 ${log.upserted} 条记录。`, `Checked ${log.fetched} PRs. Records added or updated: ${log.upserted}.`)
    : t(`GitHub 拉取失败（${log.failureReason}），已保留当前账本。`, `GitHub refresh failed (${log.failureReason}). The current ledger was kept.`);
}

function renderLanguageLabels() {
  document.documentElement.lang = language;
  const target = t('en', 'zh-CN');
  const switchLabel = t('切换至英文', 'Switch to Chinese');
  const switchText = languageSwitch.firstElementChild;
  switchText.textContent = t('EN', '中文');
  switchText.lang = target;
  languageSwitch.title = switchLabel;
  languageSwitch.setAttribute('aria-label', switchLabel);
  const home = document.querySelector('.wordmark');
  home.setAttribute('aria-label', t('PaperSpine 首页', 'PaperSpine home'));
  if (home.hasAttribute('data-site-home')) {
    const homePath = location.protocol === 'file:' ? '../index.html' : '../';
    home.href = `${homePath}?lang=${language}`;
  }
  document.querySelector('.site-nav').setAttribute('aria-label', t('贡献页导航', 'Contribution navigation'));
  document.getElementById('drawerLabel').textContent = t('贡献记录与证据', 'Contribution record and evidence');
  document.getElementById('closeDrawer').setAttribute('aria-label', t('关闭详情', 'Close contribution details'));
}

const REPOSITORY = 'WUBING2023/PaperSpine';
const GITHUB_API = `https://api.github.com/repos/${REPOSITORY}`;

const ROSTER = [
  {
    github_user_id: '242776933',
    github_login: 'WUBING2023',
    owner: true,
    cardEffect: 'topography',
    role: ['发起者与主要贡献者', 'Creator and lead contributor'],
    bio: ['发起并维护 PaperSpine，主导核心 Skill、研究工作流与产品研发。', 'Created and maintains PaperSpine. Leads development of the core Skill, research workflows, and product.']
  },
  {
    github_user_id: '199017938',
    github_login: 'goya4140',
    role: ['VERA Table 插件贡献者', 'VERA Table contributor'],
    bio: ['贡献 VERA Table 制图插件，可从研究结果表生成可编辑统计图。', 'Contributed the VERA Table plugin for creating editable statistical figures from research result tables.'],
    acknowledgement: true
  },
  {
    github_user_id: '268598926',
    github_login: 'Lauyanng',
    role: ['前端贡献者', 'Frontend contributor'],
    bio: ['通过 PR #19 和 #20 改进 V6 官网、双语文档、社区星图和贡献者页。', 'Improved the V6 site, bilingual documentation, community atlas, and contributor directory in PRs #19 and #20.'],
    pullRequests: [19, 20]
  },
  {
    github_user_id: '16056485',
    github_login: 'yaxingwang',
    role: ['指导与经费支持', 'Guidance and funding support'],
    bio: ['为 PaperSpine 提供项目建议、科研指导与经费支持。', 'Provides advice, research guidance, and funding support for PaperSpine.'],
    acknowledgement: true
  }
].map(account => ({
  ...account,
  profile_url: `https://github.com/${account.github_login}`,
  avatar_url: `https://avatars.githubusercontent.com/u/${account.github_user_id}?v=4&s=128`,
  visibility: 'public'
}));

// Public PRs checked on GitHub. These records are available before a refresh.
const VERIFIED_PULLS = [
  {
    id: 5321497904,
    number: 18,
    user: { id: 242776933 },
    title: 'Resolve findings by review round and strengthen V6 research',
    created_at: '2026-11-15T09:45:42Z',
    merged_at: '2026-11-17T14:06:31Z',
    updated_at: '2026-11-17T14:06:32Z'
  },
  {
    id: 5412037992,
    number: 19,
    user: { id: 268598926 },
    title: 'Refresh the PaperSpine site, README, and community atlas',
    created_at: '2026-11-20T10:49:09Z',
    merged_at: '2026-11-20T13:06:51Z',
    updated_at: '2026-11-20T13:06:51Z'
  },
  {
    number: 20,
    user: { id: 268598926 },
    title: 'Add the organization globe and V6 contributor ledger',
    created_at: '2026-11-24T06:42:56Z',
    merged_at: '2026-11-24T07:39:00Z',
    updated_at: '2026-11-24T07:39:00Z'
  }
];

const PULL_DETAILS = {
  18: {
    categories: ['Code', 'Research'],
    description: ['按审阅轮次处理问题，并更新 V6 科研工作流。', 'Resolves findings by review round and updates the V6 research workflow.']
  },
  19: {
    categories: ['Design', 'Documentation', 'Community'],
    description: ['更新中英文官网和 README，并改进社区星图及嵌入视图。', 'Updates the bilingual site and README, and improves the community atlas and its embedded view.']
  },
  20: {
    categories: ['Design', 'Community', 'Code'],
    description: ['加入使用机构地球视图及双语贡献者名录、证据账本和同步日志。', 'Adds the organization globe and the bilingual contributor directory, evidence ledger, and sync log.']
  }
};

function mapPull(pull, recordedAt = null) {
  const details = PULL_DETAILS[pull.number];
  return {
    record_id: `rec_gh_pr_${pull.number}`,
    contributor_id: String(pull.user.id),
    repository: REPOSITORY,
    source_provider: 'github',
    source_type: 'pull_request',
    source_id: `PR#${pull.number}`,
    source_event_id: pull.id == null ? null : String(pull.id),
    idempotency_key: `github:${REPOSITORY}:pull_request:${pull.id ?? 'PR#' + pull.number}`,
    evidence_url: `https://github.com/${REPOSITORY}/pull/${pull.number}`,
    evidence_access: 'accessible',
    title: pull.title,
    description: details?.description || ['查看 GitHub 原始 PR 了解贡献内容。', 'See the original GitHub pull request for details.'],
    categories: details?.categories || [],
    status: pull.merged_at ? 'merged' : pull.state === 'closed' ? 'closed' : 'open',
    verification_status: 'github_verified',
    occurred_at: pull.created_at,
    completed_at: pull.merged_at || pull.closed_at || null,
    recorded_at: recordedAt,
    updated_at: pull.updated_at
  };
}

function withContributionDates(contributors, records) {
  return contributors.map(contributor => {
    const dates = records
      .filter(record => record.contributor_id === contributor.github_user_id)
      .map(record => record.occurred_at)
      .sort();
    return {
      ...contributor,
      first_contribution_at: dates[0],
      last_contribution_at: dates.at(-1)
    };
  });
}

const initialRecords = VERIFIED_PULLS.map(pull => mapPull(pull));

const state = {
  view: 'overview',          // 'overview' | 'profile' | 'ledger' | 'sync'
  selectedLogin: null,
  showDefinitions: false,
  fetching: false,

  // Profile timeline filters
  profileCategory: 'All',
  profileYear: 'All',
  profileRepo: 'All',
  profileSource: 'All',

  // Global ledger filters
  ledgerCategory: 'All',
  ledgerStatus: 'All',
  ledgerSearch: '',

  // Data
  contributors: withContributionDates(ROSTER, initialRecords),
  records: initialRecords,
  syncLogs: [],

  // Drawer
  activeRecordId: null
};

// =========================================================================
// 4. HELPERS & FORMATTERS
// =========================================================================
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return String(iso);
  return d.toISOString().slice(0, 10);
}

function formatDateTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return String(iso);
  return d.toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
}

function getInitials(login) {
  const src = (login || '?').trim();
  const parts = src.split(/[\s_-]+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return src.slice(0, 2).toUpperCase();
}

function renderAvatar(contributor, sizeClass = 'w-11 h-11 text-xs') {
  const initials = escapeHtml(getInitials(contributor.github_login));
  if (contributor.avatar_url) {
    return `
      <div class="${sizeClass} avatar rounded-full overflow-hidden border border-ink-200 bg-ink-100 shrink-0 flex items-center justify-center relative">
        <img src="${escapeHtml(contributor.avatar_url)}" alt="${escapeHtml(contributor.github_login)}"
        class="w-full h-full object-cover"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
        <span style="display:none" class="w-full h-full items-center justify-center font-mono font-semibold text-ink-950 bg-ink-100">${initials}</span>
      </div>
    `;
  }
  return `
    <div class="${sizeClass} avatar avatar-fallback rounded-full border border-ink-200 bg-ink-50 shrink-0 flex items-center justify-center font-mono font-semibold text-ink-950 tracking-tight">
      ${initials}
    </div>
  `;
}

function getContributorRecords(contributorId) {
  return state.records
    .filter(r => r.contributor_id === contributorId)
    .sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at));
}

function getContributorCategories(contributorId) {
  const set = new Set();
  getContributorRecords(contributorId).forEach(r => r.categories.forEach(c => set.add(c)));
  return Array.from(set);
}

function computeCommunityStats() {
  const visibleIds = new Set(state.contributors.filter(c => c.visibility === 'public').map(c => c.github_user_id));
  const visibleRecords = state.records.filter(r => visibleIds.has(r.contributor_id));

  const mergedPRs = visibleRecords.filter(r => r.source_type === 'pull_request' && r.status === 'merged').length;

  const refNow = Date.now();
  const thirtyDaysMs = 30 * 24 * 60 * 60 * 1000;
  const active30dIds = new Set(
    visibleRecords
      .filter(r => {
        const age = refNow - Date.parse(r.occurred_at);
        return age >= 0 && age <= thirtyDaysMs;
      })
      .map(r => r.contributor_id)
  );

  return {
    totalContributors: visibleIds.size,
    mergedPRs,
    activeContributors: active30dIds.size
  };
}

function buildContributorSummaryText(records) {
  const prs = records.filter(r => r.source_type === 'pull_request' && r.status === 'merged').length;
  const openPrs = records.filter(r => r.source_type === 'pull_request' && r.status === 'open').length;
  const reviews = records.filter(r => r.source_type === 'review').length;
  const issues = records.filter(r => r.source_type === 'issue').length;
  const manual = records.filter(r => r.source_provider === 'manual').length;
  const parts = [];
  if (prs) parts.push(t(`${prs} 条已合并 PR`, `${prs} merged PR${prs === 1 ? '' : 's'}`));
  if (openPrs) parts.push(t(`${openPrs} 条进行中 PR`, `${openPrs} open PR${openPrs === 1 ? '' : 's'}`));
  if (reviews) parts.push(t(`${reviews} 条审查`, `${reviews} review${reviews === 1 ? '' : 's'}`));
  if (issues) parts.push(t(`${issues} 个议题`, `${issues} issue${issues === 1 ? '' : 's'}`));
  if (manual) parts.push(t(`${manual} 条社区贡献`, `${manual} community contribution${manual === 1 ? '' : 's'}`));
  return parts.length ? parts.join(' · ') : t(`${records.length} 条已核实记录`, `${records.length} verified records`);
}

function statusLabel(status) {
  const labels = {
    merged: t('已合并', 'Merged'),
    open: t('进行中', 'Open'),
    closed: t('已关闭', 'Closed'),
    approved: t('已通过', 'Approved')
  };
  return labels[status] || status;
}

function renderStatusBadge(status) {
  const map = {
    merged: { dot: 'bg-ink-950', cls: 'border-ink-950 bg-ink-950 text-white' },
    open: { dot: 'border border-ink-500 bg-white', cls: 'border-ink-200 bg-white text-ink-950' },
    closed: { dot: 'bg-ink-500', cls: 'border-ink-200 bg-ink-100 text-ink-700' },
    approved: { dot: 'bg-ink-950', cls: 'border-ink-200 bg-white text-ink-950' }
  };
  const cfg = map[status] || { dot: 'bg-ink-400', cls: 'border-ink-200 bg-white text-ink-700' };
  return `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border font-mono text-[11px] ${cfg.cls}"><span class="w-1.5 h-1.5 rounded-full ${cfg.dot}"></span>${escapeHtml(statusLabel(status))}</span>`;
}

function renderVerificationBadge(vStatus) {
  const map = {
    github_verified: { text: t('GitHub 已核验', 'GitHub verified'), cls: 'text-ink-700 bg-ink-50 border-ink-200' },
    manual_verified: { text: t('人工已核验', 'Manually verified'), cls: 'text-ink-950 bg-white border-ink-950' },
    evidence_unavailable: { text: t('证据已归档', 'Evidence archived'), cls: 'text-ink-700 bg-white border-ink-400 border-dashed' }
  };
  const cfg = map[vStatus] || { text: vStatus, cls: 'text-ink-700 bg-ink-50 border-ink-200' };
  return `<span class="inline-flex items-center px-2 py-0.5 rounded border font-mono text-[11px] ${cfg.cls}">${escapeHtml(cfg.text)}</span>`;
}

function showToast(message, type = 'default') {
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  const bg = type === 'error' ? 'bg-white text-ink-950 border-ink-950' : 'bg-ink-950 text-white border-ink-700';
  el.className = `pointer-events-auto fade-in px-3.5 py-2.5 rounded-md border text-xs font-medium shadow-lg flex items-center gap-2 max-w-sm ${bg}`;
  el.innerHTML = `<span>${escapeHtml(message)}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity 180ms ease';
    setTimeout(() => el.remove(), 200);
  }, 3200);
}

function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => showToast(t('已复制档案链接到剪贴板', 'Profile link copied.'))).catch(() => fallbackCopy(text));
  } else {
    fallbackCopy(text);
  }
}

function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showToast(t('已复制档案路径到剪贴板', 'Profile link copied.'));
  } catch (e) {
    showToast(t('复制失败，请手动复制链接', 'Could not copy the link. Please copy it manually.'), 'error');
  }
  ta.remove();
}

// =========================================================================
// 5. VIEWS RENDERING
// =========================================================================
function renderOverview() {
  const stats = computeCommunityStats();
  const metricLabels = {
    totalContributors: t("贡献者", "Contributors"),
    mergedPRs: t("已合并 PR", "Merged PRs"),
    activeContributors: t("近 30 天活跃贡献者", "Active contributors in the last 30 days")
  };

  const contributors = state.contributors.filter(contributor => contributor.visibility === 'public');

  return `
    <div class="shell overview-body space-y-6">
      <section class="contribute-hero" aria-labelledby="contributeTitle">
        <h1 id="contributeTitle">PaperSpine <span>${t('贡献者', 'Contributors')}</span></h1>
        <p>${t('认识一起建设 PaperSpine 的人，查看他们的贡献记录与原始证据。', 'Meet the people building PaperSpine and explore the evidence behind their contributions.')}</p>
      </section>
      <section aria-labelledby="statsHeading" class="space-y-3">
        <div class="flex items-center justify-between gap-4">
          <h2 id="statsHeading" class="section-title">${t('贡献概览', 'Contribution overview')}</h2>
          <button id="toggleDefsBtn" type="button" aria-expanded="${state.showDefinitions}" class="metrics-link focus-ring text-xs font-medium">${t('统计口径', 'How we count')}</button>
        </div>
        <dl class="metrics">
          ${[
            [metricLabels.totalContributors, stats.totalContributors],
            [metricLabels.mergedPRs, stats.mergedPRs],
            [metricLabels.activeContributors, stats.activeContributors]
          ].map(([label, value]) => `<div class="metric"><dt>${label}</dt><dd>${value}</dd></div>`).join("")}
        </dl>
        ${state.showDefinitions ? `
          <div class="fade-in border border-ink-200 rounded-xl p-4 sm:p-5 bg-ink-50 space-y-2.5">
            <div class="font-mono text-[11px] uppercase tracking-wider text-ink-500">${t('各项指标的计算方式', 'How each metric is counted')}</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              ${METRIC_DEFINITIONS.map(d => `
                <div class="bg-white border border-ink-200 rounded-lg p-3">
                  <div class="font-semibold text-ink-950">${escapeHtml(metricLabels[d.key])}</div>
                  <p class="text-ink-500 mt-1 leading-relaxed">${escapeHtml(t(...d.rule))}</p>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </section>

      <section class="space-y-4" aria-labelledby="directoryHeading">
        <h2 id="directoryHeading" class="section-title">${t('贡献者名录', 'Contributor directory')}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          ${contributors.map(c => `
            <article class="contributor-card card-hover border border-ink-200 rounded-xl bg-white p-5 flex flex-col justify-between gap-4 cursor-pointer" data-open-profile="${escapeHtml(c.github_login)}" tabindex="0" role="button" aria-label="${escapeHtml(t(`查看 ${c.github_login} 的贡献档案`, `View ${c.github_login}’s profile`))}">
              <canvas class="card-effect" data-card-effect="${c.cardEffect || 'vortex'}" aria-hidden="true"></canvas>
              <div class="space-y-3.5">
                <div class="flex items-start justify-between gap-3">
                  <div class="flex items-center gap-3 min-w-0">
                    ${renderAvatar(c)}
                    <div class="min-w-0">
                      <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                        <h3 class="text-sm font-semibold text-ink-950 truncate">@${escapeHtml(c.github_login)}</h3>
                        ${c.role ? `<span class="${c.owner ? 'owner-tag' : 'card-tag'}">${escapeHtml(t(...c.role))}</span>` : ''}
                      </div>
                    </div>
                  </div>
                  <a href="${escapeHtml(c.profile_url)}" target="_blank" rel="noopener noreferrer" data-stop-prop="true"
                    class="focus-ring p-1.5 rounded-md text-ink-400 hover:text-ink-950 hover:bg-ink-100 shrink-0" title="GitHub Profile" aria-label="${t('访问 GitHub 主页', 'Open GitHub profile')}">
                    <svg class="icon w-4 h-4" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg>
                  </a>
                </div>

                <p class="card-bio text-ink-500 leading-relaxed">${escapeHtml(c.bio ? t(...c.bio) : t('PaperSpine 开源社区贡献者', 'PaperSpine open source contributor'))}</p>

                <div class="flex flex-wrap gap-1.5">
                  ${getContributorCategories(c.github_user_id).map(cat => `
                    <span class="card-tag">${escapeHtml(categoryLabel(cat))}</span>
                  `).join('')}
                </div>
              </div>

              <div class="pt-3.5 border-t border-ink-100 space-y-2">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <div class="text-xs font-medium text-ink-950 font-mono">${escapeHtml(c.acknowledgement ? t('项目致谢', 'Project acknowledgement') : buildContributorSummaryText(getContributorRecords(c.github_user_id)))}</div>
                  <span class="profile-prompt" aria-hidden="true">${t('查看档案 →', 'View profile →')}</span>
                </div>
                <div class="flex items-center justify-between text-[11px] font-mono text-ink-400">
                  <span>${t('首次', 'First')} ${formatDate(c.first_contribution_at)}</span>
                  <span>${t('最近', 'Latest')} ${formatDate(c.last_contribution_at)}</span>
                </div>
              </div>
            </article>
          `).join('')}
        </div>
      </section>
    </div>
  `;
}

function renderProfile() {
  const contributor = state.contributors.find(c => c.github_login.toLowerCase() === state.selectedLogin.toLowerCase());
  if (!contributor) {
    return `
      <div class="border border-ink-200 rounded-xl p-10 text-center max-w-lg mx-auto">
        <h2 class="text-base font-semibold text-ink-950">${t('未找到该贡献者档案', 'Contributor profile not found')}</h2>
        <p class="text-xs text-ink-500 mt-1">${t('请返回贡献者名录 总览页选择有效贡献者。', 'Return to the directory to select a contributor.')}</p>
        <button type="button" data-action="back-overview" class="mt-4 focus-ring px-3.5 py-1.5 text-xs bg-ink-950 text-white rounded-md">${t('返回贡献者名录', 'Back to the directory')}</button>
      </div>
    `;
  }

  const allRecs = getContributorRecords(contributor.github_user_id);
  const allCats = getContributorCategories(contributor.github_user_id);
  const years = Array.from(new Set(allRecs.map(r => formatDate(r.occurred_at).slice(0, 4)))).sort((a, b) => b.localeCompare(a));
  const repos = Array.from(new Set(allRecs.map(r => r.repository)));

  const filteredRecs = allRecs.filter(r => {
    if (state.profileCategory !== 'All' && !r.categories.includes(state.profileCategory)) return false;
    if (state.profileYear !== 'All' && formatDate(r.occurred_at).slice(0, 4) !== state.profileYear) return false;
    if (state.profileRepo !== 'All' && r.repository !== state.profileRepo) return false;
    if (state.profileSource !== 'All') {
      if (state.profileSource === 'github' && r.source_provider !== 'github') return false;
      if (state.profileSource === 'manual' && r.source_provider !== 'manual') return false;
    }
    return true;
  });

  const catBreakdown = CATEGORIES.map(cat => ({
    ...cat,
    count: allRecs.filter(r => r.categories.includes(cat.id)).length
  })).filter(x => x.count > 0);

  const githubCount = allRecs.filter(r => r.source_provider === 'github').length;
  const manualCount = allRecs.filter(r => r.source_provider === 'manual').length;

  return `
    <div class="space-y-8">
      <!-- Breadcrumb -->
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-2 text-xs font-mono text-ink-500">
          <button type="button" data-action="back-overview" class="focus-ring inline-flex items-center gap-1 text-ink-700 hover:text-ink-950">
            <svg class="icon w-3.5 h-3.5" aria-hidden="true"><use href="#icon-arrow-left"></use></svg>
            <span>${t('贡献者', 'Contributors')}</span>
          </button>
          <span>/</span>
          <span class="text-ink-950 font-medium">/contributors/${escapeHtml(contributor.github_login)}</span>
        </div>
        <button type="button" data-action="copy-profile-link" class="focus-ring inline-flex items-center gap-1.5 px-2.5 py-1 text-xs border border-ink-200 rounded-md hover:border-ink-950 text-ink-700">
          <svg class="icon w-3.5 h-3.5" aria-hidden="true"><use href="#icon-link"></use></svg>
          <span>${t('复制档案路径', 'Copy profile link')}</span>
        </button>
      </div>

      <!-- Profile Header Card -->
      <section class="border border-ink-200 rounded-xl p-6 sm:p-8 bg-white">
        <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-6">
          <div class="flex items-start gap-4 min-w-0">
            ${renderAvatar(contributor, 'w-16 h-16 text-base')}
            <div class="min-w-0 space-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h1 class="text-2xl font-semibold tracking-tight text-ink-950">@${escapeHtml(contributor.github_login)}</h1>
                ${contributor.role ? `<span class="${contributor.owner ? 'owner-tag' : 'card-tag'}">${escapeHtml(t(...contributor.role))}</span>` : ''}
                <span class="font-mono text-[11px] px-2 py-0.5 rounded bg-ink-100 text-ink-700">ID: ${escapeHtml(contributor.github_user_id)}</span>
              </div>
              <p class="text-sm text-ink-700 max-w-2xl leading-relaxed">${escapeHtml(contributor.bio ? t(...contributor.bio) : t('PaperSpine 开源社区贡献者', 'PaperSpine open source contributor'))}</p>
              ${(contributor.pullRequests || []).map(number => `
                <a class="focus-ring inline-flex px-2.5 py-1 text-xs border border-ink-200 rounded-md"
                  href="https://github.com/${REPOSITORY}/pull/${number}" target="_blank" rel="noopener noreferrer">PR #${number} ↗</a>
              `).join('')}
              <div class="flex flex-wrap items-center gap-2 pt-1">
                ${allCats.map(cat => `<span class="px-2.5 py-0.5 rounded-full border border-ink-200 bg-ink-50 font-mono text-[11px] text-ink-950">${escapeHtml(categoryLabel(cat))}</span>`).join('')}
              </div>
            </div>
          </div>

          <div class="flex sm:flex-col items-start sm:items-end gap-2 shrink-0">
            <a href="${escapeHtml(contributor.profile_url)}" target="_blank" rel="noopener noreferrer"
              class="focus-ring inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-medium bg-ink-950 text-white rounded-md hover:bg-ink-700">
              <svg class="icon w-3.5 h-3.5" aria-hidden="true"><use href="#icon-github"></use></svg>
              <span>${t('GitHub 主页 ↗', 'GitHub Profile ↗')}</span>
            </a>
            <div class="font-mono text-[11px] text-ink-500 sm:text-right">
              <div>${t("首次", "First")}: ${formatDate(contributor.first_contribution_at)}</div>
              <div>${t("最近", "Latest")}: ${formatDate(contributor.last_contribution_at)}</div>
            </div>
          </div>
        </div>

        <!-- Contribution Summary Breakdown -->
        <div class="mt-6 pt-6 border-t border-ink-200 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="border border-ink-200 rounded-lg p-3.5 bg-ink-50">
            <div class="text-[11px] font-mono text-ink-500">${t('已核实的贡献记录', 'TOTAL VERIFIED EVENTS')}</div>
            <div class="text-xl font-semibold font-mono text-ink-950 mt-1">${allRecs.length}</div>
            <div class="text-[11px] text-ink-500 mt-0.5">GitHub ${githubCount} · ${t("人工核验", "Manual")} ${manualCount}</div>
          </div>
          ${catBreakdown.slice(0, 3).map(cb => `
            <div class="border border-ink-200 rounded-lg p-3.5 bg-white">
              <div class="text-[11px] font-mono text-ink-500 uppercase">${escapeHtml(t(cb.zh, cb.label))}</div>
              <div class="text-xl font-semibold font-mono text-ink-950 mt-1">${cb.count}</div>
            </div>
          `).join('')}
        </div>
      </section>

      <!-- Contribution Timeline Section -->
      <section class="space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 class="text-base font-semibold text-ink-950">${t('贡献时间线', 'Contribution timeline')}</h2>
            <p class="text-xs text-ink-500 mt-0.5">${t('点击任意贡献条目查看来源、状态与时间。', 'Open any contribution to see its source, status, and dates.')}</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <select id="profileCatSelect" aria-label="${t('按贡献类型筛选', 'Filter by contribution type')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
              <option value="All">${t('类型：全部', 'All types')}</option>
              ${allCats.map(c => `<option value="${c}" ${state.profileCategory === c ? 'selected' : ''}>${escapeHtml(categoryLabel(c))}</option>`).join('')}
            </select>
            <select id="profileYearSelect" aria-label="${t('按年份筛选', 'Filter by year')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
              <option value="All">${t('年份：全部', 'All years')}</option>
              ${years.map(y => `<option value="${y}" ${state.profileYear === y ? 'selected' : ''}>${y}</option>`).join('')}
            </select>
            <select id="profileRepoSelect" aria-label="${t('按仓库筛选', 'Filter by repository')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
              <option value="All">${t('仓库：全部', 'All repositories')}</option>
              ${repos.map(rp => `<option value="${escapeHtml(rp)}" ${state.profileRepo === rp ? 'selected' : ''}>${escapeHtml(rp)}</option>`).join('')}
            </select>
            <select id="profileSourceSelect" aria-label="${t('按来源筛选', 'Filter by source')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
              <option value="All" ${state.profileSource === 'All' ? 'selected' : ''}>${t('来源：全部', 'All sources')}</option>
              <option value="github" ${state.profileSource === 'github' ? 'selected' : ''}>${t('GitHub 自动采集', 'GitHub import')}</option>
              <option value="manual" ${state.profileSource === 'manual' ? 'selected' : ''}>${t('人工审核记录', 'Manually verified records')}</option>
            </select>
          </div>
        </div>

        ${filteredRecs.length === 0 ? `
          <div class="border border-dashed border-ink-200 rounded-xl p-10 text-center">
            <p class="text-sm font-medium text-ink-950">${t('当前筛选条件下暂无时间轴记录', 'No contributions match these filters.')}</p>
            <button type="button" data-action="reset-profile-filters" class="mt-3 focus-ring px-3 py-1.5 text-xs border border-ink-200 rounded-md hover:border-ink-950">${t('清除时间轴筛选', 'Clear timeline filters')}</button>
          </div>
        ` : `
          <div class="relative pl-6 border-l border-ink-200 space-y-4 ml-2">
            ${filteredRecs.map(r => `
              <article class="relative card-hover border border-ink-200 rounded-xl bg-white p-4 sm:p-5 cursor-pointer" data-open-record="${escapeHtml(r.record_id)}" tabindex="0" role="button">
                <span class="w-2.5 h-2.5 rounded-full bg-white border-2 border-ink-950 absolute -left-[30px] top-6"></span>
                <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div class="space-y-1.5 min-w-0">
                    <div class="flex flex-wrap items-center gap-2 text-[11px] font-mono text-ink-500">
                      <span>${formatDate(r.occurred_at)}</span>
                      <span>·</span>
                      <span class="text-ink-950 font-medium">${escapeHtml(r.repository)}</span>
                      <span>·</span>
                      <span>${escapeHtml(r.source_id)}</span>
                    </div>
                    <h3 class="text-sm font-semibold text-ink-950 leading-snug">${escapeHtml(r.title)}</h3>
                    <p class="text-xs text-ink-500 line-clamp-2 leading-relaxed">${escapeHtml(t(...r.description))}</p>
                  </div>
                  <div class="flex sm:flex-col items-start sm:items-end gap-1.5 shrink-0">
                    ${renderStatusBadge(r.status)}
                    ${renderVerificationBadge(r.verification_status)}
                  </div>
                </div>
                <div class="mt-3.5 pt-3 border-t border-ink-100 flex flex-wrap items-center justify-between gap-2">
                  <div class="flex flex-wrap gap-1.5">
                    ${r.categories.map(cat => `<span class="px-2 py-0.5 rounded bg-ink-50 border border-ink-200 font-mono text-[10px] text-ink-700">${escapeHtml(categoryLabel(cat))}</span>`).join('')}
                  </div>
                  <div class="flex items-center gap-3 text-xs">
                    <span class="font-mono text-[11px] text-ink-500">${t('查看详情 →', 'View details →')}</span>
                    <a href="${escapeHtml(r.evidence_url)}" target="_blank" rel="noopener noreferrer" data-stop-prop="true"
                      class="focus-ring font-mono text-[11px] text-ink-950 underline underline-offset-4 hover:text-ink-700">
                      ${t("原始证据 ↗", "Original evidence ↗")}
                    </a>
                  </div>
                </div>
              </article>
            `).join('')}
          </div>
        `}
      </section>
    </div>
  `;
}

function renderLedgerView() {
  const q = state.ledgerSearch.trim().toLowerCase();
  const rows = state.records
    .filter(r => {
      if (state.ledgerCategory !== 'All' && !r.categories.includes(state.ledgerCategory)) return false;
      if (state.ledgerStatus !== 'All' && r.status !== state.ledgerStatus) return false;
      if (q) {
        const c = state.contributors.find(x => x.github_user_id === r.contributor_id);
        const hay = `${r.title} ${r.source_id} ${r.repository} ${c ? c.github_login : ''} ${r.idempotency_key}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    })
    .sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at));

  return `
    <div class="space-y-6">
      <div class="view-heading flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-ink-200 pb-5">
        <div>
          <h1>${t('贡献账本', 'Contribution ledger')}</h1>
          <p class="text-ink-500">${t('按时间查看贡献、核验状态和原始证据。', 'Browse contributions by date, with verification status and original evidence.')}</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
            <input id="ledgerSearchInput" type="text" inputmode="search" value="${escapeHtml(state.ledgerSearch)}" placeholder="${t('搜索标题、PR#、用户名', 'Search by title, PR number, or username')}" aria-label="${t('搜索贡献记录', 'Search contributions')}"
            class="focus-ring px-3 py-1.5 text-xs border border-ink-200 rounded-md bg-white w-48" />
          <select id="ledgerCatSelect" aria-label="${t('筛选类型', 'Filter by type')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
            <option value="All">${t('类型：全部', 'All types')}</option>
            ${CATEGORIES.map(c => `<option value="${c.id}" ${state.ledgerCategory === c.id ? 'selected' : ''}>${escapeHtml(categoryLabel(c.id))}</option>`).join('')}
          </select>
          <select id="ledgerStatusSelect" aria-label="${t('筛选状态', 'Filter by status')}" class="focus-ring px-2.5 py-1.5 text-xs border border-ink-200 rounded-md bg-white">
            <option value="All">${t('状态：全部', 'All statuses')}</option>
            <option value="merged" ${state.ledgerStatus === 'merged' ? 'selected' : ''}>${t('已合并', 'Merged')}</option>
            <option value="open" ${state.ledgerStatus === 'open' ? 'selected' : ''}>${t('进行中', 'Open')}</option>
            <option value="closed" ${state.ledgerStatus === 'closed' ? 'selected' : ''}>${t('已关闭', 'Closed')}</option>
            <option value="approved" ${state.ledgerStatus === 'approved' ? 'selected' : ''}>${t('已通过', 'Approved')}</option>
          </select>
        </div>
      </div>

      <div class="border border-ink-200 rounded-xl overflow-hidden bg-white">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-ink-200 bg-ink-50 font-mono text-[11px] text-ink-500">
                <th class="py-3 px-4 font-medium">${t('日期', 'Date')}</th>
                <th class="py-3 px-4 font-medium">${t('贡献者', 'Contributor')}</th>
                <th class="py-3 px-4 font-medium">${t('贡献 / 仓库', 'Contribution / repository')}</th>
                <th class="py-3 px-4 font-medium">${t('类型', 'Type')}</th>
                <th class="py-3 px-4 font-medium">${t('状态', 'Status')}</th>
                <th class="py-3 px-4 font-medium">${t('核验', 'Verification')}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-ink-100">
              ${rows.length === 0 ? `
                <tr><td colspan="6" class="py-10 text-center text-ink-500">${t('暂无匹配的账本记录', 'No matching contributions.')}</td></tr>
              ` : rows.map(r => {
                const c = state.contributors.find(x => x.github_user_id === r.contributor_id);
                return `
                  <tr class="hover:bg-ink-50 cursor-pointer transition-colors" data-open-record="${escapeHtml(r.record_id)}">
                    <td class="py-3.5 px-4 font-mono text-ink-500 whitespace-nowrap">${formatDate(r.occurred_at)}</td>
                    <td class="py-3.5 px-4 whitespace-nowrap">
                      <button type="button" data-open-profile="${escapeHtml(c ? c.github_login : '')}" data-stop-prop="true" class="font-mono text-ink-950 hover:underline">@${escapeHtml(c ? c.github_login : r.contributor_id)}</button>
                    </td>
                    <td class="py-3.5 px-4 max-w-md">
                      <button type="button" class="focus-ring block max-w-full truncate text-left font-medium text-ink-950 hover:underline">${escapeHtml(r.title)}</button>
                      <div class="font-mono text-[11px] text-ink-400 mt-0.5">${escapeHtml(r.repository)} · ${escapeHtml(r.source_id)}</div>
                    </td>
                    <td class="py-3.5 px-4 whitespace-nowrap">
                      <div class="flex flex-wrap gap-1">
                        ${r.categories.map(cat => `<span class="px-1.5 py-0.5 rounded border border-ink-200 bg-white font-mono text-[10px] text-ink-700">${escapeHtml(categoryLabel(cat))}</span>`).join('')}
                      </div>
                    </td>
                    <td class="py-3.5 px-4 whitespace-nowrap">${renderStatusBadge(r.status)}</td>
                    <td class="py-3.5 px-4 whitespace-nowrap">${renderVerificationBadge(r.verification_status)}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function renderSyncView() {
  const totalSuccess = state.syncLogs.filter(l => l.status === 'success').length;
  const totalFailed = state.syncLogs.filter(l => l.status === 'failed').length;
  const totalUpdates = state.syncLogs.reduce((sum, log) => sum + log.upserted, 0);

  return `
    <div class="space-y-8">
      <div class="view-heading flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-ink-200 pb-5">
        <div>
          <h1>${t('同步日志', 'Sync log')}</h1>
          <p class="text-ink-500">${t('查看当前页面手动拉取 GitHub 数据的结果。', 'See the results of GitHub refreshes run on this page.')}</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button type="button" data-action="live-github-fetch" ${state.fetching ? "disabled" : ""} class="focus-ring inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-ink-200 bg-white text-ink-950 rounded-md hover:border-ink-950">
            <svg class="icon w-3.5 h-3.5" aria-hidden="true"><use href="#icon-github"></use></svg>
            <span>${state.fetching ? t('拉取中…', 'Refreshing…') : t('拉取 GitHub 公开数据', 'Refresh from GitHub')}</span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="border border-ink-200 rounded-xl p-5 bg-white">
          <div class="text-xs text-ink-500">${t('同步次数（成功 / 失败）', 'Sync runs (successful / failed)')}</div>
          <div class="mt-2 text-2xl font-mono font-semibold text-ink-950">${totalSuccess} <span class="text-ink-400 text-base">/ ${totalFailed}</span></div>
        </div>
        <div class="border border-ink-200 rounded-xl p-5 bg-white">
          <div class="text-xs text-ink-500">${t('新增或更新的记录', 'Records added or updated')}</div>
          <div class="mt-2 text-2xl font-mono font-semibold text-ink-950">${totalUpdates}</div>
        </div>
      </div>

      <div class="border border-ink-200 rounded-xl overflow-hidden bg-white">
        <div class="px-5 py-3.5 border-b border-ink-200 bg-ink-50 flex items-center justify-between">
          <span class="font-mono text-xs font-medium text-ink-950">${t('本次打开期间的同步', 'Sync activity in this session')}</span>
          <span class="font-mono text-[11px] text-ink-500">${t('失败任务支持一键重试', 'You can retry failed runs')}</span>
        </div>
        <div class="divide-y divide-ink-100">
          ${state.syncLogs.length === 0 ? `<p class="p-5 text-sm text-ink-500">${t("还没有同步记录。拉取 GitHub 公开数据后，结果会显示在这里。", "No sync runs yet. Refresh from GitHub to see the result here.")}</p>` : state.syncLogs.map(log => `
            <div class="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div class="space-y-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2 font-mono text-xs">
                  <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] ${log.status === 'success' ? 'border-ink-200 bg-ink-50 text-ink-700' : 'border-ink-950 bg-white text-ink-950'}">
                    <span aria-hidden="true">${log.status === 'success' ? '✓' : '×'}</span>
                    ${log.status === 'success' ? t('成功', 'Succeeded') : t('失败', 'Failed')}
                  </span>
                  <span class="font-semibold text-ink-950">${escapeHtml(log.repository)}</span>
                  <span class="text-ink-400">·</span>
                  <span class="text-ink-400">${formatDateTime(log.timestamp)}</span>
                </div>
                <p class="text-xs text-ink-700">${escapeHtml(syncMessage(log))}</p>
                <div class="font-mono text-[11px] text-ink-400">
                  ${t(`耗时 ${log.duration_ms} ms`, `Duration: ${log.duration_ms} ms`)}
                </div>
              </div>
              ${log.status === 'failed' ? `
                <button type="button" data-action="live-github-fetch" ${state.fetching ? "disabled" : ""} class="focus-ring shrink-0 px-3 py-1.5 text-xs font-medium border border-ink-950 text-ink-950 rounded-md hover:bg-ink-950 hover:text-white transition-colors">
                  ${t("重试同步", "Retry sync")}
                </button>
              ` : ''}
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

// =========================================================================
// 6. CONTRIBUTION DETAIL & AUDIT DRAWER (PRD 4.2, 4.4, 4.5, 5.2, 5.3)
// =========================================================================
function renderDetailDrawer() {
  const backdrop = document.getElementById('detailModalBackdrop');
  const titleEl = document.getElementById('drawerTitle');
  const bodyEl = document.getElementById('drawerBody');

  if (!state.activeRecordId) {
    if (backdrop.open) backdrop.close();
    return;
  }
  const r = state.records.find(x => x.record_id === state.activeRecordId);
  if (!r) {
    if (backdrop.open) backdrop.close();
    return;
  }

  const contributor = state.contributors.find(c => c.github_user_id === r.contributor_id);
  titleEl.textContent = `${r.source_id} · ${r.repository}`;
  bodyEl.innerHTML = `
    <div class="space-y-3">
      <div class="flex flex-wrap items-center gap-2">
        ${renderStatusBadge(r.status)}
        ${renderVerificationBadge(r.verification_status)}
        ${r.categories.map(cat => `<span class="px-2 py-0.5 rounded bg-ink-50 border border-ink-200 font-mono text-[11px] text-ink-700">${escapeHtml(categoryLabel(cat))}</span>`).join('')}
      </div>
      <h3 class="text-lg font-semibold tracking-tight text-ink-950 leading-snug">${escapeHtml(r.title)}</h3>
      <p class="text-sm text-ink-700 leading-relaxed">${escapeHtml(t(...r.description))}</p>
    </div>

    <!-- Original Evidence Card -->
    <div class="border border-ink-200 rounded-xl p-4 bg-ink-50 space-y-3">
      <div class="flex items-center justify-between gap-2">
        <span class="font-mono text-[11px] uppercase tracking-wider text-ink-500">${t('可核验证据', 'Verifiable Evidence')}</span>
        <a href="${escapeHtml(r.evidence_url)}" target="_blank" rel="noopener noreferrer"
          class="focus-ring inline-flex items-center gap-1 font-mono text-xs font-medium text-ink-950 underline underline-offset-4">
          <span>${t('打开原始来源', 'Open original source')}</span>
          <svg class="icon w-3.5 h-3.5" aria-hidden="true"><use href="#icon-external-link"></use></svg>
        </a>
      </div>
      <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2.5 text-xs">
        <div>
          <dt class="font-mono text-[10px] text-ink-400 uppercase">${t('贡献者', 'Contributor')}</dt>
          <dd class="font-mono text-ink-950 mt-0.5">@${escapeHtml(contributor ? contributor.github_login : r.contributor_id)} (${escapeHtml(r.contributor_id)})</dd>
        </div>
        <div>
          <dt class="font-mono text-[10px] text-ink-400 uppercase">${t('来源 / 类型', 'Source Provider / Type')}</dt>
          <dd class="font-mono text-ink-950 mt-0.5">${escapeHtml(r.source_provider)} / ${escapeHtml(r.source_type)}</dd>
        </div>
        <div>
          <dt class="font-mono text-[10px] text-ink-400 uppercase">${t('来源 ID / 事件 ID', 'Source ID / Event ID')}</dt>
          <dd class="font-mono text-ink-950 mt-0.5 break-all">${escapeHtml(r.source_id)} · ${escapeHtml(r.source_event_id || '—')}</dd>
        </div>
        <div>
          <dt class="font-mono text-[10px] text-ink-400 uppercase">${t('证据可访问性', 'Evidence Access')}</dt>
          <dd class="font-mono text-ink-950 mt-0.5">${r.evidence_access === 'unavailable' ? t('不可访问（已归档）', 'Unavailable (archived)') : t('可访问（已核实）', 'Accessible (verified)')}</dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="font-mono text-[10px] text-ink-400 uppercase">${t('去重键', 'Idempotency Key')}</dt>
          <dd class="font-mono text-[11px] text-ink-700 mt-0.5 bg-white border border-ink-200 rounded px-2 py-1 break-all">${escapeHtml(r.idempotency_key)}</dd>
        </div>
      </dl>
    </div>

    <!-- Timestamps -->
    <div class="border border-ink-200 rounded-xl p-4 bg-white">
      <div class="font-mono text-[11px] uppercase tracking-wider text-ink-500 mb-3">${t('时间记录', 'Timestamps &amp; Lineage')}</div>
      <dl class="grid grid-cols-2 gap-3 text-xs font-mono">
        <div>
          <dt class="text-[10px] text-ink-400 uppercase">${t('提交时间', 'Occurred At')}</dt>
          <dd class="text-ink-950 mt-0.5">${formatDateTime(r.occurred_at)}</dd>
        </div>
        <div>
          <dt class="text-[10px] text-ink-400 uppercase">${t('完成或合并时间', 'Completed / Merged')}</dt>
          <dd class="text-ink-950 mt-0.5">${formatDateTime(r.completed_at)}</dd>
        </div>
        <div>
          <dt class="text-[10px] text-ink-400 uppercase">${t('收录时间', 'Recorded At')}</dt>
          <dd class="text-ink-950 mt-0.5">${formatDateTime(r.recorded_at)}</dd>
        </div>
        <div>
          <dt class="text-[10px] text-ink-400 uppercase">${t('更新时间', 'Updated At')}</dt>
          <dd class="text-ink-950 mt-0.5">${formatDateTime(r.updated_at)}</dd>
        </div>
      </dl>
      ${r.reviewer ? `
        <div class="mt-3 pt-3 border-t border-ink-100 text-xs font-mono text-ink-700">
          ${t("人工核验者", "Manual reviewer")}: <span class="text-ink-950 font-semibold">@${escapeHtml(r.reviewer)}</span> · ${formatDateTime(r.reviewed_at)}
        </div>
      ` : ''}
    </div>

  `;
  if (!backdrop.open) backdrop.showModal();
}

// Refresh public PRs for the accounts shown in the directory.
async function fetchLiveGitHubData() {
  if (state.fetching) return;
  state.fetching = true;
  render();
  const started = performance.now();
  let fetched = 0;
  let updated = 0;
  let failureReason;
  let status = 'success';

  try {
    const response = await fetch(`${GITHUB_API}/pulls?state=all&per_page=100&sort=updated&direction=desc`, {
      signal: AbortSignal.timeout(12000)
    });
    if (!response.ok) throw new Error(`GitHub API HTTP ${response.status}`);
    const pulls = await response.json();
    if (!Array.isArray(pulls)) throw new Error(t('GitHub 返回的数据格式有误', 'GitHub returned an unexpected response.'));

    const rosterIds = new Set(ROSTER.map(account => account.github_user_id));
    const records = new Map(state.records.map(record => [record.record_id, record]));
    const checkedAt = new Date().toISOString();
    for (const pull of pulls) {
      if (!rosterIds.has(String(pull.user?.id))) continue;
      fetched += 1;
      const incoming = mapPull(pull, checkedAt);
      const previous = records.get(incoming.record_id);
      if (previous && previous.updated_at >= incoming.updated_at) continue;
      incoming.recorded_at = previous?.recorded_at ?? incoming.recorded_at;
      records.set(incoming.record_id, incoming);
      updated += 1;
    }
    state.records = [...records.values()];
    state.contributors = withContributionDates(ROSTER, state.records);
  } catch (error) {
    status = 'failed';
    failureReason = error.message;
  } finally {
    const log = {
      repository: REPOSITORY,
      status,
      fetched,
      upserted: updated,
      duration_ms: Math.round(performance.now() - started),
      failureReason,
      timestamp: new Date().toISOString()
    };
    state.syncLogs.unshift(log);
    state.fetching = false;
    showToast(syncMessage(log), status === 'failed' ? 'error' : 'default');
    render();
  }
}

let unmountContributorCardEffects;

function render() {
  renderLanguageLabels();
  const navLabels = { overview: t('贡献者', 'Contributors'), ledger: t('贡献账本', 'Contribution ledger'), sync: t('同步日志', 'Sync log') };
  for (const link of document.querySelectorAll('[data-nav]')) {
    link.textContent = navLabels[link.dataset.nav];
    const current = link.dataset.nav === (state.view === 'profile' ? 'overview' : state.view);
    if (current) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }

  const main = document.getElementById('appMain');
  const currentView = { profile: renderProfile, ledger: renderLedgerView, sync: renderSyncView };
  const viewContent = currentView[state.view];
  unmountContributorCardEffects?.();
  main.innerHTML = viewContent
    ? `<div class="shell view-shell">${viewContent()}</div>`
    : renderOverview();
  unmountContributorCardEffects = viewContent ? undefined : window.mountContributorCardEffects?.(main);
  document.title = `${main.querySelector('h1, h2')?.textContent || t('贡献者', 'Contributors')} | PaperSpine.io`;
  renderDetailDrawer();
  bindDynamicListeners();
}
function bindDynamicListeners() {
  const toggleDefsBtn = document.getElementById('toggleDefsBtn');
  if (toggleDefsBtn) {
    toggleDefsBtn.addEventListener('click', () => {
      state.showDefinitions = !state.showDefinitions;
      render();
      document.getElementById('toggleDefsBtn')?.focus();
    });
  }

  // Open profile
  document.querySelectorAll('[data-open-profile]').forEach(el => {
    const openProfile = () => {
      const login = el.dataset.openProfile;
      if (!login) return;
      window.location.hash = `#/contributors/${encodeURIComponent(login)}`;
    };
    el.addEventListener('click', (e) => {
      if (e.target !== el && e.target.closest('[data-stop-prop="true"]')) return;
      openProfile();
    });
    el.addEventListener('keydown', (e) => {
      if (e.target === el && el.tagName !== 'BUTTON' && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        openProfile();
      }
    });
  });

  // Open record detail drawer
  document.querySelectorAll('[data-open-record]').forEach(el => {
    const openRec = () => {
      state.activeRecordId = el.dataset.openRecord;
      renderDetailDrawer();
    };
    el.addEventListener('click', (e) => {
      if (e.target.closest('[data-stop-prop="true"]')) return;
      openRec();
    });
    el.addEventListener('keydown', (e) => {
      if (e.target === el && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        openRec();
      }
    });
  });

  // Profile selects
  const pCat = document.getElementById('profileCatSelect');
  if (pCat) pCat.addEventListener('change', e => { state.profileCategory = e.target.value; render(); });
  const pYear = document.getElementById('profileYearSelect');
  if (pYear) pYear.addEventListener('change', e => { state.profileYear = e.target.value; render(); });
  const pRepo = document.getElementById('profileRepoSelect');
  if (pRepo) pRepo.addEventListener('change', e => { state.profileRepo = e.target.value; render(); });
  const pSrc = document.getElementById('profileSourceSelect');
  if (pSrc) pSrc.addEventListener('change', e => { state.profileSource = e.target.value; render(); });

  // Ledger filters
  const lSearch = document.getElementById('ledgerSearchInput');
  if (lSearch) {
    lSearch.addEventListener('input', e => {
      state.ledgerSearch = e.target.value;
      const pos = e.target.selectionStart;
      render();
      const next = document.getElementById('ledgerSearchInput');
      if (next) { next.focus(); next.setSelectionRange(pos, pos); }
    });
  }
  const lCat = document.getElementById('ledgerCatSelect');
  if (lCat) lCat.addEventListener('change', e => { state.ledgerCategory = e.target.value; render(); });
  const lStatus = document.getElementById('ledgerStatusSelect');
  if (lStatus) lStatus.addEventListener('change', e => { state.ledgerStatus = e.target.value; render(); });

  // Action buttons
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      if (action === 'back-overview') {
        window.location.hash = '#/contributors';
      } else if (action === 'copy-profile-link') {
        copyText(window.location.href);
      } else if (action === 'reset-profile-filters') {
        state.profileCategory = 'All';
        state.profileYear = 'All';
        state.profileRepo = 'All';
        state.profileSource = 'All';
        render();
      } else if (action === 'live-github-fetch') {
        fetchLiveGitHubData();
      }
    });
  });

}

function readRoute() {
  const [, page, login] = window.location.hash.split('/');
  let selectedLogin = null;
  if (page === 'contributors' && login) {
    try { selectedLogin = decodeURIComponent(login); } catch { /* Invalid profile link. */ }
  }
  if (selectedLogin !== state.selectedLogin) {
    state.profileCategory = 'All';
    state.profileYear = 'All';
    state.profileRepo = 'All';
    state.profileSource = 'All';
  }
  state.selectedLogin = selectedLogin;
  state.view = selectedLogin ? 'profile' : ['ledger', 'sync'].includes(page) ? page : 'overview';
  state.activeRecordId = null;
  render();
}

const languageSwitch = document.getElementById('languageSwitch');
languageSwitch.hidden = false;
languageSwitch.addEventListener('click', () => {
  language = t('en', 'zh-CN');
  try {
    localStorage.setItem(LANGUAGE_KEY, language);
  } catch {
    // The choice still applies to this visit.
  }
  const url = new URL(location.href);
  if (url.searchParams.has('lang')) {
    url.searchParams.set('lang', language);
    history.replaceState(history.state, '', url);
  }
  document.getElementById('toastContainer').replaceChildren();
  render();
});

const recordDialog = document.getElementById('detailModalBackdrop');
recordDialog.addEventListener('close', () => { state.activeRecordId = null; });
recordDialog.addEventListener('click', event => {
  if (event.target === recordDialog) recordDialog.close();
});
window.addEventListener('hashchange', () => {
  readRoute();
  window.scrollTo(0, 0);
});
readRoute();
