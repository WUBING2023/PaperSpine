"""Generate locale routes and navigation from the V6 translations and release index."""

from html import escape
import json
from pathlib import Path
from string import Template

SOURCE = Path(__file__).parent
TRANSLATIONS = json.loads((SOURCE / "locales.json").read_text(encoding="utf-8"))
LANGUAGES = {"en": "English", "zh-CN": "简体中文",
             **{code: strings["name"] for code, strings in TRANSLATIONS.items()}}
LABELS = {"en": "Language", "zh-CN": "语言", "ja": "言語", "ko": "언어", "es": "Idioma",
          "fr": "Langue", "de": "Sprache", "pt": "Idioma", "ru": "Язык"}
MENU = "<!-- language-menu -->"
ALTERNATES = "<!-- language-alternates -->"


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
    return (f'<details class="language-menu"><summary aria-label="{LABELS[code]}">🌐 '
            f'<span>{LANGUAGES[code]}</span></summary><div>{"".join(links)}</div></details>')


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


def inject(html, surface, base, code):
    return (html.replace(MENU, menu(surface, code))
            .replace(ALTERNATES, alternates(surface, base, code)))


def template(name, values):
    return Template((SOURCE / name).read_text(encoding="utf-8")).substitute(values)


def edition_cards(d, release):
    cards = []
    for key, placeholder, command in (("skill", "SKILL", "$paper-spine"),
                                       ("pack", "PACK", "$paper-spine-followwriting"),
                                       ("web", "WEB", "$paper-spine-web:paper-spine-web")):
        cards.append(f'''<article class="localized-card" id="edition-{key}">
          <h3>{d[key]}</h3><p>{d[key + "_desc"]}</p><code>{command}</code>
          <div class="edition-download">
            <a class="button" data-release-download href="{release[placeholder + "_URL"]}">{d["zip"]}</a>
            <div class="edition-cli" hidden><code></code></div>
            <span>{release[placeholder + "_SIZE"]}</span> <span data-download-count="{d["downloads"]}" hidden></span>
          </div>
        </article>''')
    return "\n".join(cards)


def studies(d):
    cards = []
    for key, directory in (("atlantic", "atlantic-ri"), ("ligo", "gravitational-waves"),
                           ("ridgecrest", "ridgecrest"), ("smoke", "smoke")):
        path = "../science/research/" + directory
        cards.append(f'''<article class="localized-card" id="{directory}">
          <a href="{path}/figure.svg"><img src="{path}/figure.webp" alt="{d[key]} · {d["svg"]}" loading="lazy"></a>
          <h3>{d[key]}</h3><p>{d[key + "_desc"]}</p>
          <div class="links"><a href="{path}/paper.pdf">{d["paper"]}</a>
          <a href="{path}/figure.svg">SVG</a><a href="{path}/source.zip">{d["source"]}</a></div>
        </article>''')
    return "\n".join(cards)


def render_v6(output, release):
    base = release["SITE"]
    for name, surface in (("index.html", "home"), ("install-guide.html", "guide")):
        path = output / name
        write(path, inject(path.read_text(encoding="utf-8"), surface, base, "en"))
    for code, strings in TRANSLATIONS.items():
        d = {key: escape(value) for key, value in strings.items()}
        d.update(release, lang=code, cards=edition_cards(d, release), cases=studies(d))
        for surface, filename, layout in (
                ("home", "index.html", "localized-home.html"), ("guide", "install.html", "localized-guide.html")):
            write(output / code / filename, template(layout, d | {
                "menu": menu(surface, code, "../"), "alternates": alternates(surface, base, code),
            }))


def render_community(output, base):
    for code, name in (("en", "index.html"), ("zh-CN", "zh.html")):
        for surface, path in (("atlas", output / name), ("contributors", output / "contributors" / name)):
            url = base + "contributors/" if surface == "contributors" else base
            write(path, inject(path.read_text(encoding="utf-8"), surface, url, code))
    for code, strings in TRANSLATIONS.items():
        d = {key: escape(value) for key, value in strings.items()}
        write(output / "contributors" / (code + ".html"), template("localized-contributors.html", d | {
            "lang": code, "menu": menu("contributors", code),
            "alternates": alternates("contributors", base + "contributors/", code),
        }))
