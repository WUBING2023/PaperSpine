for (const example of document.querySelectorAll("[data-example-tabs]")) {
  const navigation = example.querySelector(".example-nav");
  const tabs = [...navigation.querySelectorAll("a")];
  const panels = tabs.map((tab) => example.querySelector(tab.hash));

  navigation.setAttribute("role", "tablist");
  tabs.forEach((tab, index) => {
    const panel = panels[index];
    tab.id = `tab-${panel.id}`;
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", panel.id);
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", tab.id);
    panel.tabIndex = 0;
  });

  function select(index, focus = false) {
    tabs.forEach((tab, position) => {
      const active = position === index;
      tab.tabIndex = active ? 0 : -1;
      tab.setAttribute("aria-selected", String(active));
      panels[position].hidden = !active;
    });
    if (focus) tabs[index].focus();
  }

  function selectFromHash() {
    const index = tabs.findIndex((tab) => tab.hash === window.location.hash);
    if (index >= 0) select(index);
  }

  select(0);
  selectFromHash();
  window.addEventListener("hashchange", selectFromHash);

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      select(index, true);
    });
    tab.addEventListener("keydown", (event) => {
      const targets = {
        ArrowLeft: (index + tabs.length - 1) % tabs.length,
        ArrowRight: (index + 1) % tabs.length,
        Home: 0,
        End: tabs.length - 1,
        " ": index,
      };
      if (!Object.hasOwn(targets, event.key)) return;
      event.preventDefault();
      select(targets[event.key], true);
    });
  });
}
