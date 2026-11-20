// Interactions adapted from the V6 release page and scoped to each language.
function initializeV6Content(root, locale) {
  const atlas = root.querySelector(".community-preview");
  let atlasResize;
  function sizeAtlas() {
    atlasResize?.disconnect();
    const atlasPage = atlas.contentDocument;
    const atlasMain = atlasPage?.querySelector("html[data-embed] main");
    if (!atlasMain) return;
    const syncHeight = () => {
      atlas.style.height = Math.ceil(atlasMain.getBoundingClientRect().height) + "px";
    };
    syncHeight();
    atlasResize = new ResizeObserver(syncHeight);
    atlasResize.observe(atlasMain);
  }
  atlas.addEventListener("load", sizeAtlas);
  sizeAtlas();

  const dialog = root.querySelector(".demo-dialog");
  const preview = dialog?.querySelector("img");
  const close = dialog?.querySelector("button");

  if (typeof dialog?.showModal === "function") {
    for (const link of root.querySelectorAll("[data-demo]")) {
      link.addEventListener("click", (event) => {
        if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
        event.preventDefault();
        preview.alt = link.getAttribute("aria-label");
        preview.src = link.href;
        dialog.showModal();
      });
    }
    close?.addEventListener("click", () => dialog.close());
    dialog?.addEventListener("close", () => preview.removeAttribute("src"));
  }

  for (const download of root.querySelectorAll("[data-release-download]")) {
    const terminal = download.parentElement.querySelector(".edition-cli");
    const command = terminal.querySelector("code");
    command.textContent = `npx --yes download-cli@1.1.1 --out . "${download.href}"`;
    command.title = command.textContent;
    terminal.hidden = false;
  }

  if (navigator.clipboard?.writeText) {
    for (const button of root.querySelectorAll("[data-copy-source]")) {
      const source = root.querySelector("#" + button.dataset.copySource);
      const status = root.querySelector("#" + button.dataset.copyFeedback);
      button.hidden = false;
      button.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(source.textContent.trim());
          status.textContent = status.dataset.done;
        } catch {
          status.textContent = status.dataset.hint;
        }
      });
    }
  }

  const archive = root.querySelector(".archive-disclosure");
  if (archive) {
    function openArchiveTarget() {
      const target = document.getElementById(location.hash.slice(1));
      if (!archive.isConnected) return;
      if (target && archive.contains(target)) {
        archive.open = true;
        target.scrollIntoView();
      }
    }
    addEventListener("hashchange", openArchiveTarget);
    openArchiveTarget();
  }

  const downloads = [...root.querySelectorAll("[data-release-download]")];

  function showDownloadCounts() {
    const source = root.querySelector("[data-release-stats-source]");
    const stamp = root.querySelector("[data-download-stamp]");
    if (!source || !downloads.length) return;

    const format = new Intl.NumberFormat(locale);
    const timeFormat = new Intl.DateTimeFormat(locale, {
      dateStyle: "medium", timeStyle: "short", timeZone: "UTC",
    });

    function display(assets, timestamp) {
      const counts = new Map(assets.map(asset => [asset.name, asset.download_count]));
      for (const el of downloads) {
        const url = new URL(el.getAttribute("href"));
        const count = counts.get(url.pathname.split("/").at(-1));
        if (!Number.isSafeInteger(count) || count < 0) continue;
        const label = el.closest(".edition-download")?.querySelector("[data-download-count]");
        if (!label) continue;
        label.textContent = count === 1 && locale === "en" ? "1 download"
          : label.dataset.downloadCount.replace("{count}", format.format(count));
        label.hidden = false;
      }
      const date = new Date(timestamp);
      if (stamp && !Number.isNaN(date.valueOf())) {
        const time = stamp.querySelector("time");
        time.dateTime = date.toISOString();
        time.textContent = timeFormat.format(date);
        stamp.hidden = false;
      }
    }

    const tag = new URL(source.href).pathname.split("/").pop();
    const expected = downloads.map(link => new URL(link.href).pathname.split("/").pop());
    PaperSpineLive.downloads(tag, expected, row => display(row.assets, row.retrieved_at));
  }
  showDownloadCounts();
}
