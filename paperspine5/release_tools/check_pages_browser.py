"""Exercise a built Pages site with Playwright, including polling and offline fallback."""

import argparse
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import expect, sync_playwright


def check_hero(page):
    expect(page.locator(".hero-brand h1")).to_have_text("One Spine,")
    expect(page.locator(".hero-brand h2")).to_have_text("From Evidence to Paper.")
    expect(page.locator(".hero-brand em")).to_have_text(["Spine", "Paper"])


def check_locales(page, base):
    codes = ("ja", "ko", "es", "fr", "de", "pt", "ru")
    page.goto(base + "v6/", wait_until="domcontentloaded")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    check_hero(page)
    expect(page.locator(".language-menu a")).to_have_count(9)
    filenames = page.locator("[data-release-download]").evaluate_all("(links) => links.map(link => link.href)")
    case_files = (
        "gravitational-waves", "atlantic-ri", "ridgecrest", "smoke",
    )
    section_ids = page.locator("main section[id]").evaluate_all("(sections) => sections.map(section => section.id)")
    study_labels = page.locator("[data-study]").all_inner_texts()
    page.goto(base + "contributors/", wait_until="domcontentloaded")
    credits = page.locator(".credit-row").count()
    for code in codes:
        page.goto(base + "v6/" + code + "/", wait_until="domcontentloaded")
        expect(page.locator("html")).to_have_attribute("lang", code)
        check_hero(page)
        expect(page.locator("[data-download-count]").first).to_be_visible()
        assert page.locator("[data-release-download]").evaluate_all("(links) => links.map(link => link.href)") == filenames
        assert page.locator("main section[id]").evaluate_all("(sections) => sections.map(section => section.id)") == section_ids
        assert page.locator("[data-study]").all_inner_texts() != study_labels
        for width in (320, 390, 820, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (code, width)
        for slug in case_files:
            page.locator(f"[data-study={slug}]").click()
            prompt = page.locator("#research-task")
            assert prompt.input_value().startswith("$paper-spine ")
            for step in range(4):
                page.locator(f"[data-case-step='{step}']").click()
                expect(page.locator(".case-note")).to_be_visible()
                assert f"/science/research/{slug}/" in page.locator(".case-original").get_attribute("href")
            page.locator(".case-original").click()
            expect(page.locator(".case-file-dialog")).to_be_visible()
            page.keyboard.press("Escape")
            expect(page.locator(".case-file-dialog")).to_be_hidden()
        for clip in page.locator("[data-demo]").all():
            clip.click()
            expect(page.locator(".demo-dialog")).to_be_visible()
            page.locator(".demo-dialog button").click()
        page.locator(".archive-disclosure summary").click()
        expect(page.locator("#dry-bean")).to_be_visible()
        expect(page.locator("#feature-aggregation")).to_be_visible()
        page.goto(f"{base}v6/{code}/install.html", wait_until="domcontentloaded")
        expect(page.locator("html")).to_have_attribute("lang", code)
        expect(page.locator("main")).to_contain_text("edition_manager.py")
        expect(page.locator(".guide-editions > div")).to_have_count(3)
        expect(page.locator("#guide-back")).to_have_attribute("href", "./#download")
        page.goto(base + "?lang=" + code, wait_until="domcontentloaded")
        expect(page.locator("html")).to_have_attribute("lang", code)
        expect(page.locator("#sample")).not_to_have_text("—")
        expect(page.locator('a[data-en-href="v6/"]')).to_have_attribute("href", f"v6/{code}/")
        page.locator("[data-mode='schools']").click()
        expect(page.locator("#directory-title")).to_be_visible()
        page.goto(f"{base}contributors/{code}.html", wait_until="domcontentloaded")
        expect(page.locator("html")).to_have_attribute("lang", code)
        expect(page.locator(".credit-row")).to_have_count(credits)
        expect(page.locator(".roster")).to_contain_text("@sample-user")
    page.goto(base + "v6/fr/#research", wait_until="domcontentloaded")
    page.set_viewport_size({"width": 390, "height": 844})
    menu = page.locator(".language-menu")
    trigger = menu.locator("summary")
    assert "🌐" not in trigger.inner_text()
    trigger.focus()
    trigger.press("Enter")
    expect(menu.locator('[aria-current="page"]')).to_have_text("Français")
    box = menu.locator(".language-options").bounding_box()
    assert box["x"] >= 0 and box["x"] + box["width"] <= 390
    trigger.press("Escape")
    expect(trigger).to_be_focused()
    expect(menu.locator(".language-options")).to_be_hidden()
    trigger.click()
    page.locator('.language-menu [hreflang="en"]').click()
    expect(page).to_have_url(base + "v6/#research")
    expect(page.locator("html")).to_have_attribute("lang", "en")


def check(browser, base):
    ctx = browser.new_context(reduced_motion="reduce")
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    samples = {}
    for key, path in (("repo", "api/v1/repository.json"), ("geo", "api/v1/atlas.json"),
                      ("release", "v6/download-stats.json"), ("people", "contributors/contributors-data.json")):
        response = ctx.request.get(base + path)
        assert response.ok, (path, response.status)
        samples[key] = response.json()
    names = [a["name"] for a in samples["release"]["assets"]]
    version = {"n": 0, "offline": False}

    def github(route):
        if version["offline"]:
            return route.fulfill(status=429, json={"message": "rate limited"}, headers={"Retry-After": "300"})
        path = urlsplit(route.request.url).path
        n = version["n"]
        if "/releases/tags/" in path:
            value = {"tag_name": samples["release"]["tag"], "assets": [
                {"name": name, "download_count": 100 * i + n} for i, name in enumerate(names)]}
        elif path.endswith("/contributors"):
            value = [{"id": 1, "login": "sample-user", "contributions": 18 + n}]
        else:
            value = {"stargazers_count": 7300 + n}
        route.fulfill(json=value)

    ctx.route("https://api.github.com/**", github)
    page.clock.install(time=datetime.now(timezone.utc))
    page.goto(base + "v6/", wait_until="domcontentloaded")
    labels = page.locator("[data-download-count]")
    expect(labels.nth(0)).to_have_text("0 downloads")
    expect(page.locator(".github")).to_have_attribute("title", "PaperSpine on GitHub · 7,300 stars")
    for choice in page.locator("[data-study]").all():
        choice.click()
        for step in page.locator("[data-case-step]").all():
            step.click()
            href = page.locator(".case-original").get_attribute("href")
            assert href and ctx.request.get(urljoin(page.url, href)).ok, href
    version["n"] = 1
    page.clock.fast_forward(59 * 60_000)
    page.evaluate("window.dispatchEvent(new Event('online'))")
    expect(labels.nth(0)).to_have_text("0 downloads")
    expect(page.locator(".github")).to_have_attribute("title", "PaperSpine on GitHub · 7,300 stars")
    page.clock.fast_forward(61_000)
    expect(labels.nth(0)).to_have_text("1 download")
    expect(page.locator(".github")).to_have_attribute("title", "PaperSpine on GitHub · 7,301 stars")
    page.locator(".language-menu summary").click()
    page.locator('.language-menu [hreflang="zh-CN"]').click()
    expect(labels.nth(0)).to_have_text("下载 1 次")
    check_hero(page)
    assert page.locator(".community-preview").get_attribute("src").startswith("../?lang=zh-CN")
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.goto(base + "?lang=en", wait_until="domcontentloaded")
    expect(page.locator("#sample")).to_have_text(f"{samples['geo']['totalStars']:,}")
    expect(page.locator("#total")).to_have_text("7,301")
    page.locator("[data-mode=schools]").click()
    page.locator("#country").select_option("China")
    page.locator("#province").select_option("北京市")
    page.locator("#query").fill("Tsinghua")
    expect(page.locator("#list")).to_contain_text("Tsinghua")
    next_geo = dict(samples["geo"], totalStars=samples["geo"]["totalStars"] + 2,
                    retrieved_at=page.evaluate("new Date(Date.now() + 1000).toISOString()"))
    page.route("**/api/v1/atlas.json", lambda route: route.fulfill(json=next_geo))
    page.clock.fast_forward(59 * 60_000)
    expect(page.locator("#sample")).to_have_text(f"{samples['geo']['totalStars']:,}")
    page.clock.fast_forward(61_000)
    expect(page.locator("#sample")).to_have_text(f"{next_geo['totalStars']:,}")
    expect(page.locator("#query")).to_have_value("Tsinghua")
    page.goto(base + "contributors/", wait_until="domcontentloaded")
    page.locator("#contributor-search").fill("sample")
    expect(page.locator(".roster")).to_contain_text("19")
    version["n"] = 2
    page.clock.fast_forward(59 * 60_000)
    expect(page.locator(".roster")).to_contain_text("19")
    page.clock.fast_forward(61_000)
    expect(page.locator(".roster")).to_contain_text("20")
    expect(page.locator("#contributor-search")).to_have_value("sample")
    assert page.locator('a[href$="/pull/19"]').count()
    version["offline"] = True
    page.goto(base + "v6/?lang=en", wait_until="domcontentloaded")
    expect(labels.nth(0)).to_have_text(f"{samples['release']['assets'][0]['download_count']:,} downloads")
    for link in page.locator("[data-release-download]").all():
        assert link.get_attribute("href").startswith("https://github.com/WUBING2023/PaperSpine/releases/download/")
    version["offline"] = False
    check_locales(page, base)
    assert not errors, errors
    print("PASS: nine languages with full research, installation and contribution pages; "
          "responsive layout, keyboard navigation, hourly polling, fallback and downloads.")
    ctx.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--browser")
    args = parser.parse_args()
    with sync_playwright() as pw:
        engine = pw.chromium.launch(executable_path=args.browser)
        check(engine, args.url.rstrip("/") + "/")
        engine.close()
