"""Exercise a built Pages site with Playwright, including polling and offline fallback."""

import argparse
from datetime import datetime, timezone
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


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
            assert href and ctx.request.get(base + "v6/" + href).ok, href
    version["n"] = 1
    page.clock.fast_forward(301_000)
    expect(labels.nth(0)).to_have_text("1 download")
    expect(page.locator(".github")).to_have_attribute("title", "PaperSpine on GitHub · 7,301 stars")
    page.locator(".language-switch").click()
    expect(labels.nth(0)).to_have_text("下载 1 次")
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
    page.clock.fast_forward(316_000)
    expect(page.locator("#sample")).to_have_text(f"{next_geo['totalStars']:,}")
    expect(page.locator("#query")).to_have_value("Tsinghua")
    page.goto(base + "contributors/", wait_until="domcontentloaded")
    page.locator("#contributor-search").fill("sample")
    expect(page.locator(".roster")).to_contain_text("19")
    version["n"] = 2
    page.clock.fast_forward(301_000)
    expect(page.locator(".roster")).to_contain_text("20")
    expect(page.locator("#contributor-search")).to_have_value("sample")
    assert page.locator('a[href$="/pull/19"]').count()
    version["offline"] = True
    page.goto(base + "v6/?lang=en", wait_until="domcontentloaded")
    expect(labels.nth(0)).to_have_text(f"{samples['release']['assets'][0]['download_count']:,} downloads")
    for link in page.locator("[data-release-download]").all():
        assert link.get_attribute("href").startswith("https://github.com/WUBING2023/PaperSpine/releases/download/")
    assert not errors, errors
    print("PASS: 4 studies × 4 outputs, EN/ZH, mobile width, two successive live responses, "
          "genuine zero, contributor search, university filter, rate-limit fallback and download URLs.")
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
