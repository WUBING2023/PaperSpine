const list = document.querySelector(".roster");
const search = document.querySelector("#contributor-search");
const status = document.querySelector("#contributor-status");
const format = new Intl.NumberFormat(document.documentElement.lang);

function contributorCard(entry) {
  const row = document.createElement("li");
  row.dataset.login = entry.login.toLowerCase();
  const anchor = document.createElement("a");
  anchor.className = "contributor";
  anchor.href = `https://github.com/${encodeURIComponent(entry.login)}`;
  const picture = document.createElement("img");
  picture.loading = "lazy";
  picture.src = `https://avatars.githubusercontent.com/u/${entry.id}?s=98&v=4`;
  picture.alt = "";
  const text = document.createElement("span");
  const name = document.createElement("strong");
  name.textContent = `@${entry.login}`;
  const count = document.createElement("small");
  count.textContent = list.dataset.commits.replace("{count}", format.format(entry.contributions));
  text.append(name, count);
  anchor.append(picture, text);
  row.append(anchor);
  return row;
}

function filterList() {
  const term = search.value.replace(/^@/, "").trim().toLowerCase();
  let visible = 0;
  for (const row of list.children) {
    const show = row.dataset.login.includes(term);
    row.hidden = !show;
    if (show) visible += 1;
  }
  status.textContent = visible
    ? status.dataset.visible.replace("{count}", format.format(visible))
    : status.dataset.empty;
}

async function initContributors() {
  try {
    const response = await fetch("contributors-data.json");
    if (!response.ok) throw new Error(response.status);
    const data = await response.json();
    if (!Array.isArray(data.contributors)) throw new Error("Invalid contributor manifest");
    for (const entry of data.contributors) {
      if (/^[a-z0-9-]{1,39}(?:\[bot\])?$/i.test(entry.login) && Number.isSafeInteger(entry.id)
          && Number.isSafeInteger(entry.contributions) && entry.contributions >= 0) {
        list.append(contributorCard(entry));
      }
    }
    const stamp = document.querySelector("#data-date");
    const date = new Date(data.retrieved_at);
    if (!Number.isNaN(date.valueOf())) {
      stamp.dateTime = date.toISOString();
      stamp.textContent = date.toISOString().slice(0, 10);
    }
    search.disabled = false;
    search.addEventListener("input", filterList);
    filterList();
  } catch {
    status.textContent = status.dataset.error;
  }
}

initContributors();
