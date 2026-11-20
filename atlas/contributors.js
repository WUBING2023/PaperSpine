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

search.addEventListener("input", filterList);
function showContributors(data) {
  const fragment = document.createDocumentFragment();
  for (const entry of data.contributors) fragment.append(contributorCard(entry));
  list.replaceChildren(fragment);
  const stamp = document.querySelector("#data-date");
  const date = new Date(data.retrieved_at);
  stamp.dateTime = date.toISOString();
  stamp.textContent = date.toISOString().slice(0, 16).replace("T", " ") + " UTC";
  search.disabled = false;
  filterList();
}
PaperSpineLive.contributors(showContributors, () => { status.textContent = status.dataset.error; });
