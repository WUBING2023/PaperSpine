import { connectAtlanticExplorer } from "./atlantic-explorer.js?v=interactive-atlantic";

const viewer = document.querySelector("[data-research-viewer]");

function initPreviewReader(fields) {
  if (typeof fields.reader.showModal !== "function") return;
  const setZoom = (zoom) => {
    fields.readerZoom.setAttribute("aria-pressed", String(zoom));
    fields.readerCanvas.dataset.zoom = String(zoom);
    if (!zoom) fields.readerCanvas.scrollTo(0, 0);
  };
  const openReader = () => {
    const preview = fields.media.querySelector("img");
    const enlarged = new Image();
    enlarged.alt = preview.alt;
    enlarged.src = fields.stage.dataset.kind === "figure" ? fields.original.href : preview.currentSrc;
    fields.readerTitle.textContent = fields.title.textContent;
    fields.readerKind.textContent = fields.kind.textContent;
    fields.readerCanvas.replaceChildren(enlarged);
    fields.readerOriginal.href = fields.original.href;
    fields.readerOriginal.textContent = fields.original.textContent;
    fields.readerCanvas.dataset.kind = fields.stage.dataset.kind;
    setZoom(false);
    fields.reader.showModal();
  };
  fields.media.addEventListener("click", (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    openReader();
  });
  fields.print.addEventListener("click", openReader);
  fields.readerClose.addEventListener("click", () => fields.reader.close());
  fields.readerZoom.addEventListener("click", () => {
    setZoom(fields.readerZoom.getAttribute("aria-pressed") !== "true");
  });
  fields.reader.addEventListener("close", () => fields.readerCanvas.replaceChildren());
  fields.magnify.hidden = false;
}

async function initResearchPreview(panel) {
  const catalogUrl = new URL(panel.dataset.catalog, document.baseURI);
  const response = await fetch(catalogUrl);
  if (!response.ok) return;
  const catalog = await response.json();
  const chinese = document.documentElement.lang === "zh-CN";
  const language = chinese ? "zh" : "en";
  const imageFiles = {
    paper: "first-page.webp",
    results: "results-page.webp",
    figure: "figure.webp",
    checks: "checks.webp",
  };
  const fields = Object.fromEntries(
    [...panel.querySelectorAll("[data-proof]")].map((node) => [node.dataset.proof, node]),
  );
  const groups = [...panel.querySelectorAll("[data-preview-group]")];
  let selection = Object.fromEntries(groups.map((group) => [
    group.dataset.previewGroup, group.querySelector('[aria-pressed="true"]').value,
  ]));
  let requested = selection;
  let generation = 0;
  const atlasUrl = new URL("atlantic-ri/explorer.json", catalogUrl);
  atlasUrl.search = catalogUrl.search;
  const atlas = panel.querySelector("[data-atlantic-explorer]");
  const showExplorer = connectAtlanticExplorer(atlas, atlasUrl, chinese, (visible) => {
    atlas.hidden = !visible;
    if (visible) fields.stage.dataset.explorer = "active";
    else delete fields.stage.dataset.explorer;
    fields.print.hidden = !visible || typeof fields.reader.showModal !== "function";
  });
  const figureButton = panel.querySelector('.viewer-mode [value="figure"]');
  const syncExplorer = () => {
    const atlantic = selection.study === "atlantic-ri";
    figureButton.textContent = atlantic
      ? (chinese ? "交互主图" : "Explore data")
      : (chinese ? "主图" : "Main figure");
    void showExplorer(atlantic && selection.mode === "figure");
  };

  async function show(study, mode) {
    requested = { study, mode };
    const ticket = ++generation;
    fields.error.hidden = true;
    if (study === selection.study && mode === selection.mode) {
      fields.stage.removeAttribute("aria-busy");
      syncExplorer();
      return;
    }

    const entry = catalog[study];
    const localized = entry[language];
    const output = localized[mode];
    const isPaper = mode === "paper" || mode === "results";
    const page = mode === "paper" ? 1 : entry.resultPage;
    const pages = entry.pages;
    const caseUrl = new URL(`${study}/`, catalogUrl);
    const sourceUrl = new URL(
      isPaper ? `paper.pdf#page=${page}` : `${mode}.svg`,
      caseUrl,
    );
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

    selection = requested;
    panel.dataset.topic = study;
    fields.stage.dataset.kind = isPaper ? "paper" : "figure";
    fields.media.href = sourceUrl.href;
    fields.media.querySelector("img").replaceWith(picture);
    fields.title.textContent = output.title;
    fields.note.textContent = output.note;
    fields.metric.hidden = !output.value;
    fields.value.textContent = output.value || "";
    fields.unit.textContent = output.unit || "";
    fields.kind.textContent = isPaper
      ? (chinese ? `论文原页 · 第 ${page} 页 / 共 ${pages} 页` : `Manuscript · page ${page} of ${pages}`)
      : (mode === "checks"
        ? (chinese ? "分析图件 · 稳健性检验" : "Analysis figure · sensitivity")
        : (chinese ? "论文图件 · 主图" : "Manuscript figure · main plate"));
    fields.source.textContent = localized.source;
    fields.original.href = sourceUrl.href;
    fields.original.textContent = isPaper
      ? (chinese ? `打开 PDF · 第 ${page} 页 ↗` : `Open PDF · p. ${page} ↗`)
      : (chinese ? "打开 SVG 原图 ↗" : "Open vector SVG ↗");
    syncExplorer();
    const label = [];
    for (const group of groups) {
      const key = group.dataset.previewGroup;
      for (const button of group.querySelectorAll("button")) {
        const active = button.value === selection[key];
        button.setAttribute("aria-pressed", String(active));
        if (active) label.push(button.textContent.trim());
      }
    }
    fields.status.textContent = label.join(" · ");
    fields.stage.removeAttribute("aria-busy");
  }

  for (const group of groups) {
    const key = group.dataset.previewGroup;
    const buttons = [...group.querySelectorAll("button")];
    for (const [index, button] of buttons.entries()) {
      const choose = () => {
        const next = { ...requested, [key]: button.value };
        void show(next.study, next.mode);
      };
      button.addEventListener("click", choose);
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
  initPreviewReader(fields);
  syncExplorer();
}

if (viewer) {
  // The initial preview and its source link also work without the catalog.
  void initResearchPreview(viewer).catch(() => {});
}
