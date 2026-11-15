const viewer = document.querySelector("[data-research-viewer]");
const imageFiles = {
  paper: "first-page.webp",
  results: "results-page.webp",
  figure: "figure.webp",
  checks: "checks.webp",
};

async function initResearchPreview(panel) {
  const catalogUrl = new URL(panel.dataset.catalog, document.baseURI);
  const response = await fetch(catalogUrl);
  if (!response.ok) return;
  const catalog = await response.json();
  const chinese = document.documentElement.lang === "zh-CN";
  const language = chinese ? "zh" : "en";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const fields = Object.fromEntries(
    [...panel.querySelectorAll("[data-proof]")].map((node) => [node.dataset.proof, node]),
  );
  const groups = [...panel.querySelectorAll("[data-preview-group]")];
  const studyGroup = groups.find((group) => group.dataset.previewGroup === "study");
  const studies = [...studyGroup.querySelectorAll("button")].map((button) => button.value);
  let selection = Object.fromEntries(groups.map((group) => [
    group.dataset.previewGroup, group.querySelector('[aria-pressed="true"]').value,
  ]));
  let requested = selection;
  let generation = 0;
  let animation;

  function animateCard(studyChanged, direction) {
    animation?.cancel();
    if (reduceMotion.matches) return;
    const start = studyChanged
      ? `translate(${direction * 21}px, 15px) rotate(${direction * 1.5}deg) scale(.974)`
      : "translateY(7px) scale(.994)";
    animation = fields.stage.animate(
      [{ transform: start, opacity: .58 }, { transform: "none", opacity: 1 }],
      { duration: studyChanged ? 460 : 270, easing: "cubic-bezier(.2,.72,.25,1)" },
    );
  }

  async function show(study, mode, direction) {
    requested = { study, mode };
    const ticket = ++generation;
    fields.error.hidden = true;
    if (study === selection.study && mode === selection.mode) {
      fields.stage.removeAttribute("aria-busy");
      return;
    }

    const entry = catalog[study];
    const localized = entry[language];
    const output = localized[mode];
    const isPaper = mode === "paper" || mode === "results";
    const page = mode === "paper" ? 1 : entry.resultPage;
    const caseUrl = new URL(`${study}/`, catalogUrl);
    const sourceUrl = new URL(isPaper ? `paper.pdf#page=${page}` : `${mode}.svg`, caseUrl);
    const pictureUrl = new URL(imageFiles[mode], caseUrl);
    sourceUrl.search = catalogUrl.search;
    pictureUrl.search = catalogUrl.search;
    const picture = new Image();
    picture.alt = output.alt;
    picture.src = pictureUrl.href;
    fields.stage.setAttribute("aria-busy", "true");

    try {
      await picture.decode();
    } catch {
      if (ticket === generation) {
        requested = selection;
        fields.stage.removeAttribute("aria-busy");
        fields.error.hidden = false;
      }
      return;
    }
    if (ticket !== generation) return;

    const studyChanged = study !== selection.study;
    const movement = direction || Math.sign(studies.indexOf(study) - studies.indexOf(selection.study));
    selection = requested;
    panel.dataset.topic = study;
    fields.stage.dataset.kind = isPaper ? "paper" : "figure";
    fields.media.replaceChildren(picture);
    fields.title.textContent = output.title;
    fields.note.textContent = output.note;
    fields.metric.hidden = !output.value;
    fields.value.textContent = output.value || "";
    fields.unit.textContent = output.unit || "";
    fields.kind.textContent = isPaper
      ? (chinese ? `论文原页 · 第 ${page} 页 / 共 ${entry.pages} 页` : `Manuscript · page ${page} of ${entry.pages}`)
      : (mode === "checks"
        ? (chinese ? "稳健性图" : "Sensitivity figure")
        : (chinese ? "论文主图" : "Main figure"));
    fields.source.textContent = localized.source;
    fields.original.href = sourceUrl.href;
    fields.original.textContent = isPaper
      ? (chinese ? `打开 PDF · 第 ${page} 页 ↗` : `Open PDF · p. ${page} ↗`)
      : (chinese ? "查看 SVG 原图 ↗" : "Open vector SVG ↗");
    const label = [];
    for (const group of groups) {
      const key = group.dataset.previewGroup;
      for (const button of group.querySelectorAll("button")) {
        const active = button.value === selection[key];
        button.setAttribute("aria-pressed", String(active));
        if (active) label.push((button.querySelector(".viewer-study-name") || button).textContent.trim());
      }
    }
    fields.status.textContent = label.join(" · ");
    fields.stage.removeAttribute("aria-busy");
    animateCard(studyChanged, movement);
  }

  function stepStudy(direction) {
    const index = studies.indexOf(requested.study);
    const next = studies[(index + direction + studies.length) % studies.length];
    void show(next, requested.mode, direction);
  }

  function choose(key, value) {
    const next = { ...requested, [key]: value };
    void show(next.study, next.mode);
  }

  for (const group of groups) {
    const key = group.dataset.previewGroup;
    const buttons = [...group.querySelectorAll("button")];
    for (const [index, button] of buttons.entries()) {
      button.addEventListener("click", () => choose(key, button.value));
      button.addEventListener("keydown", (event) => {
        const destinations = {
          ArrowLeft: (index + buttons.length - 1) % buttons.length,
          ArrowRight: (index + 1) % buttons.length,
          Home: 0,
          End: buttons.length - 1,
        };
        const next = destinations[event.key];
        if (!Number.isInteger(next)) return;
        event.preventDefault();
        buttons[next].focus();
        buttons[next].click();
      });
    }
    group.hidden = false;
  }
  fields.previous.addEventListener("click", () => stepStudy(-1));
  fields.next.addEventListener("click", () => stepStudy(1));
  fields.picker.hidden = false;

  let swipe;
  studyGroup.addEventListener("touchstart", (event) => {
    swipe = event.touches.length === 1
      ? { point: event.touches[0], button: event.target.closest("button") }
      : null;
  }, { passive: true });
  studyGroup.addEventListener("touchcancel", () => { swipe = null; });
  studyGroup.addEventListener("touchend", (event) => {
    if (!swipe) return;
    const end = event.changedTouches[0];
    const x = end.clientX - swipe.point.clientX;
    const y = end.clientY - swipe.point.clientY;
    const button = swipe.button;
    swipe = null;
    if (Math.abs(x) >= 42 && Math.abs(x) > Math.abs(y)) {
      if (event.cancelable) event.preventDefault();
      stepStudy(x < 0 ? 1 : -1);
    } else if (Math.hypot(x, y) < 12 && button && event.cancelable) {
      event.preventDefault();
      choose("study", button.value);
    }
  }, { passive: false });
}

if (viewer) void initResearchPreview(viewer).catch(() => {});
