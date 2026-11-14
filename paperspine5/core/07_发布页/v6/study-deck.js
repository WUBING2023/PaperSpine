const deck = document.querySelector(".study-deck");
if (deck) {
  const cards = [...deck.querySelectorAll(".study-card")];
  const controls = deck.querySelector(".deck-controls");
  const targets = [...deck.querySelectorAll("[data-deck-target]")];
  const next = deck.querySelector("[data-deck-next]");
  const toggle = deck.querySelector("[data-deck-toggle]");
  const status = deck.querySelector(".deck-status");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  let front = 0;
  let timer;
  let playing = !reduce.matches;

  function schedule() {
    clearTimeout(timer);
    if (playing && !document.hidden && !deck.matches(":hover, :focus-within")) {
      timer = setTimeout(() => select((front + 1) % cards.length), 9000);
    }
  }

  function select(index, announce = false) {
    if (index !== front) {
      cards[index].classList.remove("deal");
      cards[index].getBoundingClientRect();
      if (!reduce.matches) cards[index].classList.add("deal");
    }
    front = index;
    cards.forEach((card, i) => {
      const delta = (i - index + cards.length) % cards.length;
      card.dataset.depth = delta === 0 ? "0" : String(cards.length - delta);
      card.inert = delta !== 0;
      card.setAttribute("aria-hidden", String(delta !== 0));
    });
    targets.forEach((button, i) => {
      if (i === index) button.setAttribute("aria-current", "true");
      else button.removeAttribute("aria-current");
    });
    if (announce) status.textContent = cards[index].querySelector("h2").textContent.trim();
    schedule();
  }

  function setPlaying(value) {
    playing = value;
    toggle.textContent = value ? toggle.dataset.pause : toggle.dataset.play;
    schedule();
  }

  if (cards.length > 1) {
    deck.classList.add("deck-ready");
    controls.hidden = false;
    select(0);
    setPlaying(playing);
    next.addEventListener("click", () => select((front + 1) % cards.length, true));
    targets.forEach((button, i) => button.addEventListener("click", () => select(i, true)));
    toggle.addEventListener("click", () => setPlaying(!playing));
    deck.addEventListener("mouseenter", schedule);
    deck.addEventListener("mouseleave", schedule);
    deck.addEventListener("focusin", schedule);
    deck.addEventListener("focusout", () => requestAnimationFrame(schedule));
    document.addEventListener("visibilitychange", schedule);
    reduce.addEventListener("change", (event) => {
      if (event.matches) setPlaying(false);
    });
  }
}
