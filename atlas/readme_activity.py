"""Render the bilingual README ticker from the release and repository snapshots."""

from html import escape
import json
from pathlib import Path
import sys


def render(root):
    v6 = root / "v6"
    release = json.loads((v6 / "download-stats.json").read_text(encoding="utf-8"))
    repo_file = root / "api/v1/repository.json"
    repo = json.loads(repo_file.read_text(encoding="utf-8")) if repo_file.exists() else None
    downloads = sum(asset["download_count"] for asset in release["assets"])
    for zh in (False, True):
        name = "activity-zh" if zh else "activity"
        rows = [("当前版本" if zh else "RELEASE", release["tag"])]
        if repo:
            rows.append(("GitHub 星标" if zh else "GITHUB STARS", format(repo["stargazers_count"], ",")))
        rows.append(("三版累计下载" if zh else "RELEASE DOWNLOADS", format(downloads, ",")))
        description = " · ".join(f"{label} {value}" for label, value in rows)
        description += " · " + release["retrieved_at"][:10]
        lines = []
        for i, (label, value) in enumerate(rows):
            lines.append(f'<text x="560" y="64" text-anchor="middle" fill="#747680" opacity="{int(i == 0)}" class="r{i}">'
                         f'{escape(label)} [ <tspan fill="#df650d">{escape(value)}</tspan> ]</text>')
        total = len(rows)
        style = "".join(f".r{i}{{animation:show {total * 3}s steps(1,end) {-3 * ((total-i) % total)}s infinite}}"
                        for i in range(total))
        style += f"@keyframes show{{0%{{opacity:1}}{100/total:.3f}%,100%{{opacity:0}}}}"
        for still in (True, False):
            css = "" if still else f"<style>{style}</style>"
            body = lines[0] if still else "".join(lines)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 106" role="img">'
                   f'<title>{escape(description)}</title>{css}<rect width="1120" height="106" rx="20" fill="white"/>'
                   f'<g font-family="ui-monospace,monospace" font-size="38">{body}</g></svg>')
            (v6 / (name + ("-still" if still else "") + ".svg")).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    render(Path(sys.argv[1]))
