// Preserve explicit V5 support and historical page links.
const legacyQuery = new URLSearchParams(window.location.search);
if (!legacyQuery.has("legacy") && !legacyQuery.has("support") && !window.location.hash) {
  const target = document.currentScript.dataset.upgradeHref;
  window.location.replace(new URL(target, window.location.href));
}
