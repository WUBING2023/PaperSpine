const originalLanguage = document.documentElement.lang;
let language = originalLanguage;

new ResizeObserver(([entry]) => {
  document.documentElement.style.setProperty("--site-header-height", `${entry.contentRect.height}px`);
}).observe(document.querySelector(".site-header"));

const copyButton = document.querySelector("#copy-install");
const copyStatus = document.querySelector("#copy-status");
const copyLabel = copyButton.getAttribute("aria-label");
let resetCopyLabel;

function renderCopyFeedback() {
  const labels = language === "zh-CN"
    ? { idle: "复制安装提示", copied: "已复制安装提示", failed: "无法访问剪贴板，请打开安装指南。" }
    : { idle: copyLabel, copied: siteMessages.copied ?? "Installation prompt copied.",
        failed: siteMessages.clipboardUnavailable ?? "Clipboard unavailable. Open the installation guide." };
  const result = copyButton.dataset.result;
  copyButton.setAttribute("aria-label", labels.idle);
  copyButton.title = labels[result ?? "idle"];
  copyStatus.textContent = result ? labels[result] : "";
}

copyButton.addEventListener("click", async () => {
  clearTimeout(resetCopyLabel);
  try {
    await navigator.clipboard.writeText(document.getElementById("agent-install-prompt").textContent.trim());
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
const githubLabel = githubLink.getAttribute("aria-label");
let repoStars;

function renderGitHubStars() {
  const label = language === "zh-CN" ? "在 GitHub 查看 PaperSpine" : githubLabel;
  const pattern = language === "zh-CN" ? "{count} 个星标" : siteMessages.starCount ?? "{count} stars";
  const fullCount = new Intl.NumberFormat(language);
  const compactCount = new Intl.NumberFormat(language, { notation: "compact", maximumFractionDigits: 1 });
  const count = repoStars === undefined ? "" : " · " + pattern.replace("{count}", fullCount.format(repoStars));
  githubLink.setAttribute("aria-label", label + count);
  githubLink.title = label + count;
  starCount.textContent = repoStars === undefined ? "GitHub" : compactCount.format(repoStars);
}

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
const chineseContent = document.querySelector("#v6-chinese")?.content;
const lowerPage = {
  [originalLanguage]: { content: [...contentSlot.childNodes], footer: footerSlot.firstElementChild },
};
if (chineseContent) {
  lowerPage["zh-CN"] = {
    content: [...chineseContent.querySelector(".v6-content").childNodes],
    footer: chineseContent.querySelector("footer"),
  };
}
let visibleLowerPage = originalLanguage;

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
  showLanguageInMenu(nextLanguage);
  document.querySelector("#site-guide").href = chinese ? "install-guide.html?lang=zh-CN" : "install-guide.html";
  renderCopyFeedback();
  renderGitHubStars();
  updateResearchLanguage();
  showLowerPage(nextLanguage);
}

if (originalLanguage === "en" && (languageParam === "zh-CN" || languageParam === "zh")) setLanguage("zh-CN");
else if (languageParam && languageParam !== originalLanguage) {
  const alternate = [...document.querySelectorAll(".language-menu [hreflang]")]
    .find(link => link.hreflang === languageParam);
  if (alternate) {
    const destination = new URL(alternate.href);
    destination.hash = location.hash;
    location.replace(destination);
  }
}
showLowerPage(language);

PaperSpineLive.repository(row => {
  repoStars = row.stargazers_count;
  renderGitHubStars();
  starCount.dataset.asOf = row.retrieved_at;
});
