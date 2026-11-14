const dialog = document.querySelector(".demo-dialog");
const preview = dialog.querySelector("img");
const close = dialog.querySelector("button");

if (typeof dialog.showModal === "function") {
  for (const link of document.querySelectorAll("[data-demo]")) {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
      event.preventDefault();
      preview.alt = link.getAttribute("aria-label");
      preview.src = link.href;
      dialog.showModal();
    });
  }
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => preview.removeAttribute("src"));
}

const copy = document.querySelector(".copy-press");
if (navigator.clipboard?.writeText) {
  copy.hidden = false;
  copy.addEventListener("click", async () => {
    const status = document.querySelector(".copy-status");
    const intro = document.querySelector("#press-intro");
    try {
      await navigator.clipboard.writeText(intro.textContent.trim());
      status.textContent = status.dataset.done;
    } catch {
      status.textContent = status.dataset.hint;
    }
  });
}

const archive = document.querySelector(".archive-disclosure");
if (archive) {
  function openArchiveTarget() {
    const target = document.getElementById(location.hash.slice(1));
    if (target && archive.contains(target)) {
      archive.open = true;
      target.scrollIntoView();
    }
  }
  addEventListener("hashchange", openArchiveTarget);
  openArchiveTarget();
}
