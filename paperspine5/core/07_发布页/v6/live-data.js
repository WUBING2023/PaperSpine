// Shared by the release page, its embedded atlas, and the contributor directory.
(() => {
  const site = new URL("../", document.currentScript.src);
  const api = "https://api.github.com/repos/WUBING2023/PaperSpine";
  const interval = 60 * 60 * 1000;
  const feeds = new Map();
  const integer = value => Number.isSafeInteger(value) && value >= 0;
  let apiRetryAfter = 0;

  async function json(url) {
    const github = String(url).startsWith(api);
    if (github && Date.now() < apiRetryAfter) throw Error("GitHub rate limit");
    const response = await fetch(url, { cache: "no-cache", credentials: "omit", signal: AbortSignal.timeout(10000) });
    if (!response.ok) {
      if (github && [403, 429].includes(response.status)) {
        const retry = response.headers.get("retry-after");
        const retryTime = Number.isFinite(Number(retry))
          ? Date.now() + Number(retry) * 1000 : Date.parse(retry);
        apiRetryAfter = Math.max(Date.now() + interval, retryTime || 0,
          (Number(response.headers.get("x-ratelimit-reset")) || 0) * 1000);
      }
      throw Error("HTTP " + response.status);
    }
    return response.status === 204 ? [] : response.json();
  }

  const timestamp = () => new Date().toISOString();
  function watch(key, source, backup, accept, listener) {
    let feed = feeds.get(key);
    if (!feed) {
      feed = { listeners: new Set(), due: 0 };
      function deliver(value) {
        if (!accept(value)) throw Error("Unexpected public data");
        if (feed.value && Date.parse(value.retrieved_at) < Date.parse(feed.value.retrieved_at)) return;
        feed.value = value;
        for (const fn of feed.listeners) fn(value);
      }
      feed.refresh = async () => {
        if (document.hidden || feed.busy || Date.now() < feed.due) return;
        feed.busy = true;
        feed.due = Date.now() + interval;
        clearTimeout(feed.timer);
        feed.timer = setTimeout(feed.refresh, interval);
        try {
          const fallback = () => json(new URL(backup, site)).then(deliver);
          const known = Boolean(feed.value);
          const calls = [source().then(deliver).catch(() => {
            if (known && backup) return fallback();
          })];
          if (backup && !known) calls.push(fallback());
          await Promise.allSettled(calls);
        } finally { feed.busy = false; }
      };
      feeds.set(key, feed);
    }
    feed.listeners.add(listener);
    if (feed.value) listener(feed.value);
    feed.refresh();
  }
  function refresh() { for (const feed of feeds.values()) feed.refresh(); }
  document.addEventListener("visibilitychange", refresh);
  addEventListener("online", refresh);
  const dated = value => value && Number.isFinite(Date.parse(value.retrieved_at));
  window.PaperSpineLive = {
    repository(listener) {
      watch("repo", async () => {
        const row = await json(api);
        return { stargazers_count: row.stargazers_count, retrieved_at: timestamp() };
      }, "api/v1/repository.json", row => dated(row) && integer(row.stargazers_count), listener);
    },
    downloads(tag, expected, listener) {
      watch("downloads:" + tag, async () => {
        const release = await json(api + "/releases/tags/" + encodeURIComponent(tag));
        return { tag: release.tag_name, assets: release.assets, retrieved_at: timestamp() };
      }, "v6/download-stats.json", row => dated(row) && row.tag === tag && Array.isArray(row.assets) &&
        expected.every(name => row.assets.some(a => a.name === name && integer(a.download_count))), listener);
    },
    contributors(listener, unavailable) {
      async function read() {
        const people = new Map();
        for (let page = 1; page <= 21; page++) {
          const batch = await json(api + "/contributors?anon=false&per_page=100&page=" + page);
          if (!Array.isArray(batch)) throw Error("Invalid contributors");
          for (const { login, id, contributions } of batch) people.set(id, { login, id, contributions });
          if (batch.length < 100) return { contributors: [...people.values()], retrieved_at: timestamp() };
        }
        throw Error("Incomplete contributors");
      }
      watch("contributors", read, "contributors/contributors-data.json", row => dated(row) &&
        Array.isArray(row.contributors) && row.contributors.every(p => integer(p.id) && integer(p.contributions)
          && /^[a-z0-9-]{1,39}(?:\[bot\])?$/i.test(p.login)), listener);
      if (unavailable) setTimeout(() => { if (!feeds.get("contributors").value) unavailable(); }, 12000);
    },
    atlas(listener) {
      watch("atlas", () => json(new URL("api/v1/atlas.json", site)), null,
        row => dated(row) && row.repo === "WUBING2023/PaperSpine" && Array.isArray(row.schools)
          && Array.isArray(row.cities) && row.countries && integer(row.totalStars), listener);
    },
  };
})();
