const releaseUrl = document.querySelector('link[rel="canonical"]').href;
let language = "en";

new ResizeObserver(([entry]) => {
  document.documentElement.style.setProperty("--site-header-height", `${entry.contentRect.height}px`);
}).observe(document.querySelector(".site-header"));

const copyButton = document.querySelector("#copy-install");
const copyStatus = document.querySelector("#copy-status");
const installPrompt = [
  "Install PaperSpine for this host. Read the official guide first.",
  releaseUrl + "llms.txt",
  "",
  "Choose the edition that fits my task and environment.",
  "Verify the ZIP with SHA-256. After installing, confirm the version and tell me how to invoke the Skill.",
].join("\n");
const chineseInstallPrompt = [
  "请为当前环境安装 PaperSpine。先阅读官方指南。",
  releaseUrl + "llms.txt",
  "",
  "选择适合我的任务和环境的版本。用 SHA-256 校验 ZIP。安装后，请确认版本并告诉我如何调用该 Skill。",
].join("\n");
let resetCopyLabel;

function renderCopyFeedback() {
  const labels = language === "zh-CN"
    ? { idle: "复制安装提示", copied: "已复制安装提示", failed: "无法访问剪贴板，请打开安装指南。" }
    : { idle: "Copy install prompt", copied: "Installation prompt copied.", failed: "Clipboard unavailable. Open the installation guide." };
  const result = copyButton.dataset.result;
  copyButton.setAttribute("aria-label", labels.idle);
  copyButton.title = labels[result ?? "idle"];
  copyStatus.textContent = result ? labels[result] : "";
}

copyButton.addEventListener("click", async () => {
  clearTimeout(resetCopyLabel);
  try {
    await navigator.clipboard.writeText(language === "zh-CN" ? chineseInstallPrompt : installPrompt);
    copyButton.dataset.result = "copied";
  } catch {
    copyButton.dataset.result = "failed";
  }
  renderCopyFeedback();
  resetCopyLabel = setTimeout(() => {
    delete copyButton.dataset.result;
    renderCopyFeedback();
  }, 2000);
});

const agentBand = document.querySelector(".host-band");
const agentTrack = agentBand.querySelector(".agent-track");
const agentWindow = agentBand.querySelector(".agent-window");
const repeatedAgents = agentTrack.firstElementChild.cloneNode(true);
repeatedAgents.setAttribute("aria-hidden", "true");
agentTrack.append(repeatedAgents);
agentBand.setAttribute("data-marquee", "");

function updateAgentSpeed() {
  const animation = agentTrack.getAnimations().find(item => item.animationName === "agents-left");
  animation?.updatePlaybackRate(agentWindow.matches(":hover, :focus") ? 0.35 : 1);
}
for (const event of ["pointerenter", "pointerleave", "focus", "blur"]) {
  agentWindow.addEventListener(event, updateAgentSpeed);
}
agentTrack.addEventListener("animationstart", updateAgentSpeed);

const updateResearchLanguage = initializeResearchDemo(document.querySelector("#research-preview"));

const starCount = document.querySelector("#github-stars");
const githubLink = starCount.closest("a");
const compactCount = new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 });
const fullCount = new Intl.NumberFormat("en");
let repoStars;

function renderGitHubStars() {
  const label = language === "zh-CN" ? "在 GitHub 查看 PaperSpine" : "PaperSpine on GitHub";
  const count = repoStars === undefined ? "" : ` · ${fullCount.format(repoStars)} stars`;
  githubLink.setAttribute("aria-label", label + count);
  githubLink.title = label + count;
  starCount.textContent = repoStars === undefined ? "GitHub" : compactCount.format(repoStars);
}

async function refreshGitHubStars() {
  try {
    const response = await fetch("https://api.github.com/repos/WUBING2023/PaperSpine");
    if (!response.ok) return;

    const { stargazers_count: count } = await response.json();
    if (!Number.isSafeInteger(count) || count < 0) return;

    repoStars = count;
    renderGitHubStars();
  } catch {
    // The repository link still works when the counter is unavailable.
  }
}

const languageSwitch = document.querySelector(".language-switch");
const contentSlot = document.querySelector("#v6-content");
contentSlot.addEventListener("pointerover", event => {
  if (event.pointerType === "touch") return;
  const card = event.target.closest(".edition");
  if (!card || card.contains(event.relatedTarget)) return;
  const bounds = card.getBoundingClientRect();
  card.style.setProperty("--ripple-x", `${Math.max(0, Math.min(bounds.width, event.clientX - bounds.left))}px`);
  card.style.setProperty("--ripple-y", `${Math.max(0, Math.min(bounds.height, event.clientY - bounds.top))}px`);
});
const footerSlot = document.querySelector("#v6-footer");
const chineseContent = document.querySelector("#v6-chinese").content;
const lowerPage = {
  en: { content: [...contentSlot.childNodes], footer: footerSlot.firstElementChild },
  "zh-CN": { content: [...chineseContent.querySelector(".v6-content").childNodes], footer: chineseContent.querySelector("footer") },
};
let visibleLowerPage = "en";

function showLowerPage(locale) {
  const page = lowerPage[locale];
  if (visibleLowerPage !== locale) {
    contentSlot.replaceChildren(...page.content);
    footerSlot.replaceChildren(page.footer);
    visibleLowerPage = locale;
  }
  if (!page.initialized) {
    initializeV6Content(contentSlot, locale);
    page.initialized = true;
  }
  const target = document.getElementById(location.hash.slice(1));
  const archive = target?.closest(".archive-disclosure");
  if (archive) archive.open = true;
}
const translatedText = [...document.querySelectorAll("[data-zh]")].map(element => [element, element.textContent]);
const translatedAttributes = [
  ["data-zh-label", "aria-label"],
  ["data-zh-alt", "alt"],
].flatMap(([dataAttribute, target]) =>
  [...document.querySelectorAll(`[${dataAttribute}]`)].map(element => [element, dataAttribute, target, element.getAttribute(target)])
);

function setLanguage(nextLanguage) {
  language = nextLanguage;
  document.documentElement.lang = nextLanguage;
  const chinese = nextLanguage === "zh-CN";
  for (const [element, english] of translatedText) {
    element.textContent = chinese ? element.dataset.zh : english;
  }
  for (const [element, dataAttribute, target, english] of translatedAttributes) {
    element.setAttribute(target, chinese ? element.getAttribute(dataAttribute) : english);
  }
  languageSwitch.textContent = chinese ? "中" : "EN";
  languageSwitch.title = chinese ? "切换至英文" : "Switch to Chinese";
  languageSwitch.setAttribute("aria-label", languageSwitch.title);
  renderCopyFeedback();
  renderGitHubStars();
  updateResearchLanguage();
  showLowerPage(nextLanguage);
}

const requestedLanguage = new URLSearchParams(location.search).get("lang");
let savedLanguage;
try { savedLanguage = localStorage.getItem("paperspine-language"); } catch {}
if ((requestedLanguage ?? savedLanguage) === "zh-CN") setLanguage("zh-CN");

languageSwitch.addEventListener("click", () => {
  setLanguage(language === "en" ? "zh-CN" : "en");
  try {
    localStorage.setItem("paperspine-language", language);
    const url = new URL(location.href);
    url.searchParams.set("lang", language);
    history.replaceState(null, "", url);
  } catch {
    // The selected language remains active for this visit.
  }
});
languageSwitch.hidden = false;
showLowerPage(language);

refreshGitHubStars();
setInterval(() => {
  if (!document.hidden) refreshGitHubStars();
}, 5 * 60 * 1000);
