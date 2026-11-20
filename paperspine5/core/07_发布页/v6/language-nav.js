const languageParam = new URLSearchParams(location.search).get("lang");

function showLanguageInMenu(code) {
  for (const menu of document.querySelectorAll(".language-menu")) {
    for (const link of menu.querySelectorAll("[hreflang]")) {
      if (link.hreflang === code) {
        menu.querySelector("summary span").textContent = link.textContent;
        menu.querySelector("summary").setAttribute("aria-label", link.dataset.languageLabel);
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    }
  }
}

for (const link of document.querySelectorAll(".language-menu a")) {
  link.addEventListener("click", () => {
    if (location.hash) {
      const destination = new URL(link.href);
      destination.hash = location.hash;
      link.href = destination;
    }
  });
}

const localizedProduct = document.querySelector("[data-localized-product]");
if (localizedProduct) {
  const code = document.documentElement.lang;
  initializeV6Content(localizedProduct, code);
  PaperSpineLive.repository(row => {
    localizedProduct.ownerDocument.querySelector("[data-localized-stars]").textContent =
      new Intl.NumberFormat(code, {notation: "compact"}).format(row.stargazers_count);
  });
}
