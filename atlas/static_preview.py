"""Draw a compact vector map from the same aggregates as the interactive atlas."""

from html import escape
import json
from math import sqrt
from pathlib import Path
import sys

from validate_data import load_atlas, validate_atlas

ROOT = Path(__file__).resolve().parent


def point(lon, lat):
    return 38 + (lon + 30) * 2.35, 288 - lat * 2.31


def path_data(geometry):
    polygons = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        polygons = [polygons]
    return " ".join(
        "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in (point(*coordinate[:2]) for coordinate in ring)) + "Z"
        for polygon in polygons for ring in polygon
    )


def preview(data, features, zh):
    title = "PaperSpine 社区星图" if zh else "PaperSpine stargazer atlas"
    stats = (
        ("已采集星标" if zh else "Stargazers sampled", data["totalStars"]),
        ("地区可识别" if zh else "Located profiles", data["located"]),
        ("国家与地区" if zh else "Countries / regions", data["countryCount"]),
    )
    regions = "\n  ".join(
        f'<path d="{path_data(item["geometry"])}"/>'
        for item in features
        if item.get("geometry", {}).get("type") in {"Polygon", "MultiPolygon"}
        and item["properties"].get("name") != "Antarctica"
    )
    vertical = [point(lon, 0)[0] for lon in range(0, 330, 30)]
    horizontal = [point(0, lat)[1] for lat in range(-60, 90, 30)]
    grid = " ".join(f"M{x:g},88V433" for x in vertical)
    grid += " " + " ".join(f"M38,{y:g}H886" for y in horizontal)
    dots = []
    for city in sorted(data["cities"], key=lambda item: item["count"]):
        if city["name"].endswith("(city unspecified)"):
            continue
        x, y = point(city["lng"], city["lat"])
        size = min(14, 2.1 + 1.12 * sqrt(city["count"]))
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}"/>')
    captions = []
    for i, (name, number) in enumerate(stats):
        y = 155 + i * 100
        captions.append(f'<text x="930" y="{y}" fill="#bad0ca" font-size="20">{name}</text>'
                        f'<text x="930" y="{y+47}" fill="#ffe5a9" font-family="Georgia,serif" font-size="42">{number:,}</text>')
    foot = ("公开 GitHub 资料 · 按城市聚合" if zh else "Public GitHub profiles · aggregated by city")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1230" height="475" viewBox="0 0 1230 475" role="img">
<title>{title}</title>
<desc>{foot}</desc>
<rect width="1230" height="475" fill="#0b1d27"/>
<g font-family="Segoe UI, Noto Sans CJK SC, Microsoft YaHei, sans-serif">
  <text x="38" y="57" fill="#faf5e5" font-size="30" font-weight="650">{title}</text>
  <path d="M38 79H1190 M905 111V414 M38 431H1190" stroke="#405e63" stroke-width="1"/>
  <text x="38" y="457" fill="#b4cfc7" font-size="17">{foot}</text>
  <text x="1190" y="457" text-anchor="end" fill="#b4cfc7" font-size="17">{escape(data["generated"])}</text>
  {" ".join(captions)}
</g>
<path d="{grid}" fill="none" stroke="#28444d" stroke-width="1"/>
<g fill="#193d47" stroke="#46636a" stroke-width=".7" fill-rule="evenodd">
  {regions}
</g>
<g fill="#ffda84" fill-opacity=".78" stroke="#ffe6ab" stroke-width=".45">
  {" ".join(dots)}
</g>
</svg>
'''


def main(output):
    data = load_atlas(ROOT / "data.js")
    validate_atlas(data)
    features = json.loads((ROOT / "world.geo.json").read_text(encoding="utf-8"))["features"]
    for zh, name in ((False, "atlas-preview.svg"), (True, "atlas-preview-zh.svg")):
        (output / name).write_text(preview(data, features, zh), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
