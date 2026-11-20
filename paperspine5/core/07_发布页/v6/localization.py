"""Render language editions from the complete V6 website and its shared sources."""

import argparse
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SOURCE = Path(__file__).parent
LANGUAGES = {"en": "English", "zh-CN": "简体中文", "ja": "日本語", "ko": "한국어",
             "es": "Español", "fr": "Français", "de": "Deutsch", "pt": "Português", "ru": "Русский"}
LOCALIZED = tuple(code for code in LANGUAGES if code not in {"en", "zh-CN"})
LABELS = {"en": "Language", "zh-CN": "语言", "ja": "言語", "ko": "언어", "es": "Idioma",
          "fr": "Langue", "de": "Sprache", "pt": "Idioma", "ru": "Язык"}
MENU = "<!-- language-menu -->"
ALTERNATES = "<!-- language-alternates -->"
TEXT_ATTRIBUTES = {
    "alt", "aria-label", "title", "placeholder", "data-done", "data-hint",
    "data-download-count", "data-visible", "data-empty", "data-error", "data-commits",
}
VERBATIM = {"script", "style", "svg", "code", "pre"}
SHARED = {
    "PaperSpine", ".io", "GitHub", "One", "Spine", "AI for Science", "Followwriting", "GitHub ↗",
    "OpenAI Codex", "Claude Code", "OpenClaw", "Hermes CLI", "Cursor", "OpenCode", "Gemini CLI",
    "GitHub Copilot", "LIGO / GWOSC", "Windows x64 · Codex", "PaperSpine V6 · MIT", "UTC",
    "PR #19", "@Lauyanng", "@WUBING2023", "@Wubin2023",
    "v6.0.0-beta.2", "v6.0.0-beta.1", "PaperSpine · AI for Science", "NOAA NHC · Atlantic HURDAT2",
    "EPA AirData", "USGS ComCat · Shelly 2020", "USGS ComCat / Shelly", "USGS ComCat · Shelly",
    "V6", "MIT", "Instrument Serif", "Noto Serif SC", "Codex", "Claude", "writing_rationale_matrix",
    "citation_support_bank", "translation_package", "artifact_check.py", "reference_inventory.py",
    "citation_bank_check.py", "latex_guard.py", "word_guard.py", "install.ps1", "install.sh",
}
ATTR = re.compile(r'''(\s)([\w:-]+)=(["'])(.*?)\3''', re.S)
RELEASE_FIELDS = re.compile(r"@([A-Z_]+)@")
MARKDOWN_INLINE = re.compile(r'(!?)\[([^\]]+)\]\(([^\s)]+)\)|`[^`]+`|<a id="[^"]+"></a>')
SITE_ROOT = "https://wubing2023.github.io/PaperSpine/"
DEMO_MESSAGES = {
    "copied": "Installation prompt copied.",
    "clipboardUnavailable": "Clipboard unavailable. Open the installation guide.",
    "starCount": "{count} stars",
    "pause": "Pause",
    "resume": "Resume",
    "openPdf": "Open PDF · p. {page}",
    "openSvg": "Open SVG",
    "pageOf": "Manuscript · page {page} of {pages}",
}
DEMO_PROMPTS = {
    "atlantic-ri": "Use NOAA HURDAT2 to compare rapid intensification of Atlantic cyclones across two 21-season periods. Match comparable starting conditions, check sensitivity to the wind-speed threshold, and produce a figure and an editable paper.",
    "ridgecrest": "Compare early aftershock decay after the 2019 Ridgecrest earthquake in USGS ComCat and Shelly’s relocated catalog. Fit both catalogs over the same time window, test different magnitude cutoffs, and report the results in a figure and an editable paper.",
    "smoke": "Use EPA AirData to compare two June 2023 wildfire-smoke episodes across the Atlantic and Great Lakes corridors. Estimate PM₂.₅ departures from each monitor’s local reference, check sensitivity to monitor selection, and produce a figure and an editable paper.",
}


def routes(surface):
    if surface == "home":
        return {code: "" if code == "en" else "zh/" if code == "zh-CN" else code + "/" for code in LANGUAGES}
    if surface == "contributors":
        return {code: "" if code == "en" else "zh.html" if code == "zh-CN" else code + ".html" for code in LANGUAGES}
    if surface == "guide":
        return {code: "install-guide.html" if code == "en" else "install-guide.html?lang=zh-CN"
                if code == "zh-CN" else code + "/install.html" for code in LANGUAGES}
    return {code: "" if code == "en" else "zh.html" if code == "zh-CN" else "?lang=" + code for code in LANGUAGES}


def menu(surface, code, prefix="./"):
    links = []
    for lang, route in routes(surface).items():
        current = ' aria-current="page"' if lang == code else ""
        links.append(f'<a href="{escape(prefix + route)}" lang="{lang}" hreflang="{lang}" '
                     f'data-language-label="{LABELS[lang]}"{current}>{LANGUAGES[lang]}</a>')
    name = LANGUAGES[code]
    return (f'<details class="language-menu"><summary aria-label="{LABELS[code]} · {name}">'
            f'<span lang="{code}">{name}</span></summary><div class="language-options">{"".join(links)}</div></details>')


def alternates(surface, base, code):
    options = routes(surface)
    return "\n  ".join([
        f'<link rel="canonical" href="{base + options[code]}">',
        f'<link rel="alternate" hreflang="x-default" href="{base + options["en"]}">',
        *(f'<link rel="alternate" hreflang="{lang}" href="{base + route}">' for lang, route in options.items()),
    ])


def write(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8", newline="\n")


def inject(html, surface, base, code, prefix="./"):
    return (html.replace(MENU, menu(surface, code, prefix))
            .replace(ALTERNATES, alternates(surface, base, code)))


def requires_translation(text):
    return (text not in SHARED and text not in LANGUAGES.values()
            and bool(re.search("[A-Za-z]", text)) and not RELEASE_FIELDS.fullmatch(text))


def translations():
    return json.loads((SOURCE / "locales.json").read_text(encoding="utf-8"))


def translate(text, catalog, code):
    if not requires_translation(text):
        return text
    try:
        return catalog[text][code]
    except KeyError as exc:
        raise ValueError(f"Missing {code} translation for {text!r}") from exc


def localized_url(value, surface, code):
    if surface == "readme":
        if value == "INSTALL-V6.en.md":
            return f"{SITE_ROOT}v6/{code}/install.html"
        parts = urlsplit(value)
        base = urlsplit(SITE_ROOT)
        if (parts.scheme, parts.netloc) != (base.scheme, base.netloc):
            return value
        if parts.path == base.path + "v6/":
            return urlunsplit(parts._replace(path=parts.path + code + "/"))
        if parts.path == base.path + "contributors/":
            return urlunsplit(parts._replace(path=parts.path + code + ".html"))
        if parts.path == base.path:
            return urlunsplit(parts._replace(query="lang=" + code))
        return value
    if surface == "contributors":
        return {"../v6/": f"../v6/{code}/", ".././": f"../?lang={code}",
                "../contributors/": f"./{code}.html"}.get(value, value)
    if value == "install-guide.html":
        return "install.html"
    if value in {"./", "./#download"} or value.startswith(("#", "@")):
        return value
    parts = urlsplit(value)
    if parts.scheme or parts.netloc or not parts.path:
        return value
    if parts.path == "../" and "lang=" in parts.query:
        query = urlencode([(key, code if key == "lang" else item) for key, item in parse_qsl(parts.query)])
        parts = parts._replace(query=query)
    return urlunsplit(parts._replace(path="../" + parts.path))


class LocalizedHTML(HTMLParser):
    """Replace prose and route-relative URLs while retaining the source markup."""

    def __init__(self, catalog, code, surface):
        super().__init__(convert_charrefs=False)
        self.catalog = catalog
        self.code = code
        self.surface = surface
        self.fragments = []
        self.text = []
        self.verbatim = None

    def flush_text(self):
        raw = "".join(self.text)
        self.text.clear()
        text = unescape(raw).strip()
        if self.verbatim or not requires_translation(text):
            self.fragments.append(raw)
            return
        before = raw[:len(raw) - len(raw.lstrip())]
        after = raw[len(raw.rstrip()):]
        self.fragments.append(before + escape(translate(text, self.catalog, self.code)) + after)

    def handle_starttag(self, tag, attrs):
        self.flush_text()
        raw = self.get_starttag_text()
        if self.verbatim:
            self.fragments.append(raw)
            return
        attributes = dict(attrs)

        def replace(match):
            space, name, quote, raw_value = match.groups()
            value = unescape(raw_value)
            if tag in {"html", "article"} and name == "lang":
                value = self.code
            elif name in {"href", "src", "data-release-stats-source"}:
                value = localized_url(value, self.surface, self.code)
            elif name in TEXT_ATTRIBUTES or (name == "content" and tag == "meta" and (
                    attributes.get("name") == "description" or attributes.get("property") in {"og:title", "og:description"})):
                value = translate(value, self.catalog, self.code)
            else:
                return match.group()
            return f"{space}{name}={quote}{escape(value, quote=True)}{quote}"

        self.fragments.append(ATTR.sub(replace, raw))
        if tag in VERBATIM or attributes.get("translate") == "no":
            self.verbatim = tag

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        self.flush_text()
        if tag == self.verbatim:
            self.verbatim = None
        self.fragments.append(f"</{tag}>")

    def handle_decl(self, decl):
        self.flush_text()
        self.fragments.append(f"<!{decl}>")

    def handle_comment(self, comment):
        self.flush_text()
        self.fragments.append(f"<!--{comment}-->")

    def handle_data(self, data):
        self.text.append(data)

    def handle_entityref(self, name):
        self.text.append(f"&{name};")

    def handle_charref(self, name):
        self.text.append(f"&#{name};")


def localized_html(text, catalog, code, surface):
    parser = LocalizedHTML(catalog, code, surface)
    parser.feed(text)
    parser.close()
    parser.flush_text()
    return "".join(parser.fragments)


def english_page(surface):
    if surface == "home":
        source = (SOURCE / "index.html").read_text(encoding="utf-8")
        return source[:source.index('  <template id="v6-chinese"')] + "</body>\n</html>\n"
    source = (SOURCE / "install-guide.html").read_text(encoding="utf-8")
    return source[:source.index('    <article lang="zh-CN"')] + "  </main>\n</body>\n</html>\n"


def site_messages(catalog, code):
    messages = {key: translate(value, catalog, code) for key, value in DEMO_MESSAGES.items()}
    messages["prompts"] = {key: "$paper-spine " + translate(value, catalog, code)
                           for key, value in DEMO_PROMPTS.items()}
    return '<script type="application/json" id="site-messages">' + json.dumps(
        messages, ensure_ascii=False).replace("<", "\\u003c") + '</script>'


def render_research_catalog(output, catalog):
    path = output / "science/research/showcase.json"
    studies = json.loads(path.read_text(encoding="utf-8"))
    for study in studies.values():
        for code in LOCALIZED:
            study[code] = {
                key: ({field: translate(text, catalog, code) for field, text in value.items()}
                      if isinstance(value, dict) else translate(value, catalog, code))
                for key, value in study["en"].items()
            }
    write(path, json.dumps(studies, ensure_ascii=False, indent=2) + "\n")


def render_v6(output, release):
    catalog = translations()
    base = release["SITE"]
    for surface, source_name, filename in (("home", "index.html", "index.html"),
                                          ("guide", "install-guide.html", "install.html")):
        path = output / source_name
        write(path, inject(path.read_text(encoding="utf-8"), surface, base, "en"))
        source = english_page(surface)
        for code in LOCALIZED:
            text = localized_html(source, catalog, code, surface)
            if surface == "home":
                text = text.replace("<!-- locale-messages -->", site_messages(catalog, code))
            text = RELEASE_FIELDS.sub(lambda match: release[match[1]], text)
            write(output / code / filename, inject(text, surface, base, code, "../"))
    render_research_catalog(output, catalog)


def render_community(output, base):
    catalog = translations()
    contributors = output / "contributors"
    source = (contributors / "index.html").read_text(encoding="utf-8")
    for code, name in (("en", "index.html"), ("zh-CN", "zh.html")):
        for surface, path in (("atlas", output / name), ("contributors", contributors / name)):
            url = base + "contributors/" if surface == "contributors" else base
            write(path, inject(path.read_text(encoding="utf-8"), surface, url, code))
    for code in LOCALIZED:
        text = localized_html(source, catalog, code, "contributors")
        write(contributors / (code + ".html"), inject(text, "contributors", base + "contributors/", code))


def markdown_prose(text, catalog, code):
    """Keep links and code intact while giving translated prose control of word order."""
    slots = []

    def reserve(match):
        image, label, url = match.groups()
        if label:
            plain = label.strip("*")
            name = label.replace(plain, translate(plain, catalog, code))
            item = f"{image}[{name}]({localized_url(url, 'readme', code)})"
        else:
            item = match.group()
        slots.append(item)
        return "{" + str(len(slots)) + "}"

    result = translate(MARKDOWN_INLINE.sub(reserve, text), catalog, code)
    for number, item in enumerate(slots, 1):
        token = "{" + str(number) + "}"
        if result.count(token) != 1:
            raise ValueError(f"Invalid placeholder {token} in {code} translation of {text!r}")
        result = result.replace(token, item)
    return result


def readme_language(source, catalog, code):
    rows = []
    in_code = False
    for line in source.splitlines():
        source_text = line.strip()
        if source_text.startswith("```"):
            in_code = not in_code
        elif not in_code and source_text:
            if source_text.startswith("<"):
                line = localized_html(line, catalog, code, "readme")
            elif source_text.startswith("|") and not re.fullmatch(r"[\s|:-]+", line):
                cells = [markdown_prose(cell.strip(), catalog, code) for cell in line.strip("|").split("|")]
                line = "| " + " | ".join(cells) + " |"
            else:
                prefix = re.match(r"^(?:#{1,6} |- )?", line).group()
                line = prefix + markdown_prose(line[len(prefix):], catalog, code)
        rows.append(line)
    text = "\n".join(rows) + "\n"
    prompt = next(key for key in catalog if key.startswith("Install PaperSpine for this host."))
    return text.replace(prompt.replace("@SITE@", SITE_ROOT + "v6/"),
                        translate(prompt, catalog, code).replace("@SITE@", SITE_ROOT + "v6/"))


def sync_readmes(root, check):
    """Keep the complete localized GitHub READMEs aligned with the English source."""
    catalog = translations()
    source = (root / "README.md").read_text(encoding="utf-8")
    for code in LOCALIZED:
        path = root / f"README.{code}.md"
        expected = readme_language(source, catalog, code)
        if check:
            if path.read_text(encoding="utf-8") != expected:
                raise ValueError(f"Regenerate {path.name} with localization.py")
        else:
            write(path, expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=sync_readmes.__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    sync_readmes(options.root, options.check)
