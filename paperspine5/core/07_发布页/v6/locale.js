const homepage = new URL("../", window.location.href);
homepage.search = window.location.search;
homepage.searchParams.set("lang", document.documentElement.lang);
homepage.hash = window.location.hash;
window.location.replace(homepage);
