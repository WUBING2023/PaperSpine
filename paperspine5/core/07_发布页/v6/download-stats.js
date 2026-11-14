const downloads = [...document.querySelectorAll("[data-release-download]")];

async function showDownloadCounts() {
  const source = document.querySelector("[data-release-stats-source]");
  if (!source || !downloads.length) return;

  const format = new Intl.NumberFormat(document.documentElement.lang);
  const timeFormat = new Intl.DateTimeFormat(document.documentElement.lang, {
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
      label.textContent = label.dataset.downloadCount.replace("{count}", format.format(count));
      label.hidden = false;
    }
    const stamp = document.querySelector("[data-download-stamp]");
    const date = new Date(timestamp);
    if (stamp && !Number.isNaN(date.valueOf())) {
      const time = stamp.querySelector("time");
      time.dateTime = date.toISOString();
      time.textContent = timeFormat.format(date);
      stamp.hidden = false;
    }
  }

  try {
    const response = await fetch(source.getAttribute("data-release-stats-source"));
    if (!response.ok) throw new Error(response.status);
    const snapshot = await response.json();
    display(snapshot.assets, snapshot.retrieved_at);
  } catch {
    try {
      const response = await fetch(source.href, { signal: AbortSignal.timeout(5000) });
      if (!response.ok) return;
      const release = await response.json();
      display(release.assets, new Date().toISOString());
    } catch {
      // Download links remain usable if both count sources are unavailable.
    }
  }
}

showDownloadCounts();
