const english = new URL("../", window.location.href);
english.search = window.location.search;
english.hash = window.location.hash;
window.location.replace(english);
