const researchBase = new URL("science/research/", document.currentScript.src);

function initializeResearchDemo(section) {
  const pauseButton = section.querySelector("#pause-case-demo");
  const prompt = section.querySelector("#research-task");
  const picker = section.querySelector(".study-picker");
  const choices = [...picker.querySelectorAll("[data-study]")];
  const dataSource = section.querySelector("#case-data-source");
  const panel = section.querySelector(".case-playback");
  const footer = panel.querySelector(".case-footer");
  const source = footer.querySelector(".case-source");
  const original = footer.querySelector(".case-original");
  const wave = panel.querySelector(".case-wave");
  const canvas = wave.querySelector("canvas");
  const context = canvas.getContext("2d");
  const result = panel.querySelector(".case-result");
  const imageLink = result.querySelector(".case-image-link");
  const image = result.querySelector("img");
  const kind = result.querySelector(".case-kind");
  const title = result.querySelector(".case-title");
  const note = result.querySelector(".case-note");
  const metric = result.querySelector(".case-metric");
  const metricValue = metric.querySelector("strong");
  const metricUnit = metric.querySelector("span");
  const fileDialog = section.querySelector(".case-file-dialog");
  const fileTitle = fileDialog.querySelector("h3");
  const direct = fileDialog.querySelector(".case-file-direct");
  const pdf = fileDialog.querySelector("iframe");
  const svg = fileDialog.querySelector("img");
  const steps = [...panel.querySelectorAll("[data-case-step]")];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)");
  const assets = researchBase.href;
  const frames = [
    { key: "paper", image: "first-page.webp" },
    { key: "results", image: "results-page.webp" },
    { key: "figure", image: "figure.webp", original: "figure.svg" },
    { key: "checks", image: "checks.webp", original: "checks.svg" },
  ];
  const tasks = {
    "gravitational-waves": {
      source: "LIGO / GWOSC",
      resultPage: 3,
      en: prompt.defaultValue,
      zh: "$paper-spine 比较两次 LIGO 黑洞并合中信号到达两个探测器的时差，检验九种预处理方案下结果是否一致，并输出主图和可编辑论文。",
    },
    "atlantic-ri": {
      source: "NOAA NHC / HURDAT2",
      resultPage: 2,
      en: "$paper-spine Use NOAA HURDAT2 to compare rapid intensification of Atlantic cyclones across two 21-season periods. Match comparable starting conditions, check sensitivity to the wind-speed threshold, and produce a figure and an editable paper.",
      zh: "$paper-spine 用 NOAA HURDAT2 对照两个各含 21 个气旋季的时期，比较起始条件相近的大西洋气旋快速增强情况。检验结果对风速阈值的敏感性，并输出图表和可编辑论文。",
    },
    ridgecrest: {
      source: "USGS ComCat / Shelly",
      resultPage: 4,
      en: "$paper-spine Compare early aftershock decay after the 2019 Ridgecrest earthquake in USGS ComCat and Shelly’s relocated catalog. Fit both catalogs over the same time window, test different magnitude cutoffs, and report the results in a figure and an editable paper.",
      zh: "$paper-spine 用 USGS ComCat 和 Shelly 重定位目录比较 2019 年里奇克雷斯特地震后的早期余震衰减。在相同时间范围内拟合两套目录，检验不同震级下限，并输出图表和可编辑论文。",
    },
    smoke: {
      source: "EPA AirData",
      resultPage: 4,
      en: "$paper-spine Use EPA AirData to compare two June 2023 wildfire-smoke episodes across the Atlantic and Great Lakes corridors. Estimate PM₂.₅ departures from each monitor’s local reference, check sensitivity to monitor selection, and produce a figure and an editable paper.",
      zh: "$paper-spine 用 EPA AirData 对比 2023 年 6 月两次野火烟霾在大西洋沿岸和五大湖地区的影响。估计各监测站 PM₂.₅ 相对本地基准的偏离，检验站点选择的影响，并输出图表和可编辑论文。",
    },
  };
  const drafts = new Map();
  let currentChoice = choices[0];
  const lastStep = frames.length - 1;
  let position = -1;
  let playing = false;
  let inView = false;
  let frameRequest;
  let frameTime;
  let elapsed = 0;
  let lastWave = -Infinity;
  let pointerFrame;
  let catalog = {};

  function assetPath(file) {
    return assets + currentChoice.dataset.study + "/" + file;
  }

  function renderPrompt() {
    const study = currentChoice.dataset.study;
    const task = tasks[study];
    const chinese = document.documentElement.lang === "zh-CN";
    prompt.value = drafts.get(study) ?? siteMessages.prompts?.[study] ?? (chinese ? task.zh : task.en);
    dataSource.textContent = task.source;
    for (const choice of choices) {
      choice.setAttribute("aria-pressed", String(choice === currentChoice));
    }
  }

  function render() {
    const chinese = document.documentElement.lang === "zh-CN";
    const loading = position === -1;
    pauseButton.hidden = position === lastStep || reduced.matches;
    pauseButton.textContent = playing
      ? (chinese ? "暂停" : siteMessages.pause ?? "Pause")
      : (chinese ? "继续" : siteMessages.resume ?? "Resume");
    wave.hidden = !loading;
    result.hidden = loading;
    footer.hidden = loading;
    panel.dataset.phase = loading ? "loading" : "result";
    for (const button of steps) {
      button.setAttribute("aria-pressed", String(Number(button.dataset.caseStep) === position));
    }
    if (loading) return;
    const frame = frames[position];
    const study = currentChoice.dataset.study;
    const entry = catalog[study];
    const localized = entry?.[chinese ? "zh" : document.documentElement.lang];
    const details = localized?.[frame.key];
    const paper = !frame.original;
    const page = frame.key === "results" ? entry?.resultPage ?? tasks[study].resultPage : 1;
    const originalFile = frame.original ?? `paper.pdf#page=${page}`;
    const label = steps[position].textContent;
    result.dataset.kind = paper ? "paper" : "figure";
    imageLink.href = original.href = assetPath(originalFile);
    original.textContent = paper
      ? (chinese ? `打开 PDF · 第 ${page} 页` : (siteMessages.openPdf ?? "Open PDF · p. {page}").replace("{page}", page))
      : (chinese ? "打开 SVG 原图" : siteMessages.openSvg ?? "Open SVG");
    imageLink.setAttribute("aria-label", original.textContent);
    kind.textContent = paper && entry?.pages
      ? (chinese ? `论文原页 · 第 ${page} 页 / 共 ${entry.pages} 页`
        : (siteMessages.pageOf ?? "Manuscript · page {page} of {pages}").replace("{page}", page).replace("{pages}", entry.pages))
      : label;
    title.textContent = details?.title || currentChoice.textContent;
    note.textContent = details?.note || "";
    note.hidden = !details?.note;
    metricValue.textContent = details?.value || "";
    metricUnit.textContent = details?.unit || "";
    metric.hidden = !details?.value;
    source.textContent = localized?.source || tasks[study].source;
    const next = assetPath(frame.image);
    if (image.getAttribute("src") !== next) {
      image.src = next;
      if (!reduced.matches) {
        image.getAnimations().forEach(animation => animation.cancel());
        image.animate([{ opacity: 0.25, transform: "translateY(4px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 240, easing: "ease-out" });
      }
    }
    image.alt = details?.alt || currentChoice.textContent + " · " + label;
  }

  function drawWave(time) {
    if (!context || time - lastWave < 80) return;
    lastWave = time;
    const ratio = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!width || !height) return;
    const pixelWidth = Math.round(width * ratio);
    const pixelHeight = Math.round(height * ratio);
    if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
      canvas.width = pixelWidth;
      canvas.height = pixelHeight;
    }
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    context.font = "13px monospace";
    context.textBaseline = "middle";
    const chars = ".:+*#";
    for (let x = 12; x < width - 8; x += 9) {
      const distance = (x / width - 0.56) * 6;
      const amplitude = 0.34 * height * Math.exp(-distance * distance);
      const offset = Math.sin(26 * x / width + x * x / (width * width) * 38 - time / 115) * amplitude;
      context.fillStyle = "#c9b7aa";
      context.fillText("·", x, height / 2);
      context.fillStyle = "#bf4217";
      context.fillText(chars[Math.round(Math.abs(offset) / (0.34 * height) * 4)], x, height / 2 + offset);
    }
  }

  function tick(time) {
    frameRequest = undefined;
    if (frameTime !== undefined) elapsed += time - frameTime;
    frameTime = time;
    if (position === -1) drawWave(time);
    if (elapsed >= (position === -1 ? 1350 : 2450)) {
      elapsed = 0;
      position++;
      if (position === lastStep) playing = false;
      render();
    }
    syncPlayback();
  }

  function syncPlayback() {
    const active = playing && inView && !document.hidden && !reduced.matches;
    panel.toggleAttribute("data-playing", active);
    if (active) {
      frameRequest ??= requestAnimationFrame(tick);
      return;
    }
    cancelAnimationFrame(frameRequest);
    frameRequest = undefined;
    frameTime = undefined;
  }

  function start() {
    position = reduced.matches ? 0 : -1;
    elapsed = 0;
    frameTime = undefined;
    playing = !reduced.matches;
    for (const frame of frames) new Image().src = assetPath(frame.image);
  }

  picker.hidden = false;
  panel.hidden = false;
  start();
  render();
  fetch(assets + "showcase.json")
    .then(response => response.ok ? response.json() : {})
    .then(data => { catalog = data; render(); })
    .catch(() => {/* The preview still works with its local files and labels. */});
  prompt.addEventListener("input", () => drafts.set(currentChoice.dataset.study, prompt.value));
  for (const choice of choices) {
    choice.addEventListener("click", () => {
      if (choice === currentChoice) return;
      currentChoice = choice;
      renderPrompt();
      start();
      render();
      syncPlayback();
    });
  }
  for (const link of [imageLink, original]) {
    link.addEventListener("click", event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      playing = false;
      syncPlayback();
      render();
      const paper = result.dataset.kind === "paper";
      fileTitle.textContent = title.textContent;
      direct.href = link.href;
      pdf.hidden = !paper;
      svg.hidden = paper;
      if (paper) pdf.src = link.href;
      else {
        svg.src = link.href;
        svg.alt = image.alt;
      }
      fileDialog.showModal();
    });
  }
  fileDialog.addEventListener("close", () => {
    pdf.removeAttribute("src");
    svg.removeAttribute("src");
  });
  pauseButton.addEventListener("click", () => {
    playing = !playing;
    render();
    syncPlayback();
  });
  for (const button of steps) {
    button.addEventListener("click", () => {
      position = Number(button.dataset.caseStep);
      elapsed = 0;
      playing = false;
      render();
      syncPlayback();
    });
  }

  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    syncPlayback();
  }).observe(panel);
  document.addEventListener("visibilitychange", syncPlayback);
  reduced.addEventListener("change", () => {
    if (reduced.matches) {
      playing = false;
      position = Math.max(0, position);
      render();
    }
    syncPlayback();
  });

  wave.addEventListener("pointermove", event => {
    if (reduced.matches || !finePointer.matches) return;
    const bounds = wave.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    cancelAnimationFrame(pointerFrame);
    pointerFrame = requestAnimationFrame(() => {
      wave.style.setProperty("--wave-x", `${x * 16}px`);
      wave.style.setProperty("--wave-y", `${y * 12}px`);
    });
  });
  wave.addEventListener("pointerleave", () => {
    cancelAnimationFrame(pointerFrame);
    wave.style.removeProperty("--wave-x");
    wave.style.removeProperty("--wave-y");
  });
  return () => {
    renderPrompt();
    render();
  };
}
