const languageParam = new URLSearchParams(location.search).get("lang");
const siteMessages = JSON.parse(document.getElementById("site-messages")?.textContent ?? "{}");

function showLanguageInMenu(code) {
  for (const menu of document.querySelectorAll(".language-menu")) {
    const summary = menu.querySelector("summary");
    for (const link of menu.querySelectorAll("[hreflang]")) {
      if (link.hreflang === code) {
        const name = summary.querySelector("span");
        name.textContent = link.textContent;
        name.lang = code;
        summary.setAttribute("aria-label", link.dataset.languageLabel + " · " + link.textContent);
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    }
  }
}

for (const menu of document.querySelectorAll(".language-menu")) {
  menu.addEventListener("keydown", event => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary").focus();
      event.stopPropagation();
    }
  });
  document.addEventListener("pointerdown", event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  menu.addEventListener("focusout", event => {
    if (event.relatedTarget && !menu.contains(event.relatedTarget)) menu.open = false;
  });
  for (const link of menu.querySelectorAll("[hreflang]")) {
    link.addEventListener("click", () => {
      const destination = new URL(link.href);
      destination.hash = location.hash;
      link.href = destination;
    });
  }
}
