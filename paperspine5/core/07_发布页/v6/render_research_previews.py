"""Render the featured manuscript pages and the study sensitivity figures."""

from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PIL import Image
import pymupdf


RESEARCH = Path(__file__).resolve().parent / "science" / "research"
ARCHIVED_PLOTS = {"gravitational-waves": "lag-sensitivity", "ridgecrest": "fig2_counts"}


def save_page(page, output, scale, quality=88):
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    image.save(output, "WEBP", quality=quality, method=6)


def save_plot(pdf, output, width=2160, quality=88):
    with pymupdf.open(stream=pdf, filetype="pdf") as plot:
        save_page(plot[0], output, width / plot[0].rect.width, quality)


def regenerate_smoke_checks(results, directory):
    sensitivity = results["sensitivity"]
    checks = [
        ("Primary estimate", results["primary"]),
        ("Alternate reference days", sensitivity["alternate_reference"]),
        ("Hourly-derived daily values", sensitivity["hourly_derived"]),
    ]
    series = [
        (label, [(window["Atlantic_minus_Lake"],) for window in values["windows"]])
        for label, values in checks
    ]
    for label, key in (("Omit one monitor", "leave_site_out"), ("Omit one county group", "leave_group_out")):
        values = list(sensitivity[key].values())
        series.append((f"{label} ({len(values)} runs)", list(zip(*values, strict=True))))

    colors = ("#ac4826", "#176584")
    background = "#f9f7f1"
    ink = "#182e36"
    with matplotlib.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "path", "svg.hashsalt": "smoke-checks"}):
        figure = Figure(figsize=(10.2, 5.85), facecolor=background)
        FigureCanvasAgg(figure)
        axis = figure.add_axes((.315, .235, .633, .535), facecolor=background)
        axis.axvspan(-110, 0, color="#e9f1f1", zorder=0)
        axis.axvspan(0, 110, color="#f7ede3", zorder=0)
        axis.axvline(0, color="#718688", lw=1.1)
        for y in (.5, 1.5, 2.5, 3.5):
            axis.axhline(y, color="#ced4cd", lw=.65)
        for row, (_, episodes) in enumerate(series):
            for color, values in zip(colors, episodes, strict=True):
                data = sorted(values)
                if len(data) > 1:
                    axis.hlines(row, data[0], data[-1], color=color, alpha=.7, lw=1.4)
                    offsets = [(index % 5 - 2) * .065 for index in range(len(data))]
                    axis.scatter(data, [row + offset for offset in offsets], s=22, color=color,
                                 edgecolors=background, linewidths=.45, alpha=.88, zorder=4)
                else:
                    axis.scatter(data, [row], marker="D" if row == 0 else "o",
                                 s=47 if row == 0 else 29, color=color, zorder=4)

        axis.set(xlim=(-110, 110), ylim=(4.55, -.55), xticks=range(-100, 101, 25))
        axis.set_yticks(range(len(series)), [label for label, _ in series], fontsize=10, color=ink)
        axis.tick_params(axis="y", length=0, pad=10)
        axis.tick_params(axis="x", colors="#43565d", labelsize=10, length=3.5)
        for edge in ("top", "left", "right"):
            axis.spines[edge].set_visible(False)
        axis.spines["bottom"].set_color("#a8b6b2")
        axis.set_xlabel("Atlantic minus Great Lakes PM₂.₅ departure (µg/m³)", labelpad=10, fontsize=11, color=ink)
        axis.text(-55, 1.035, "Great Lakes higher", ha="center", transform=axis.get_xaxis_transform(),
                  color=colors[1], fontsize=9)
        axis.text(55, 1.035, "Atlantic higher", ha="center", transform=axis.get_xaxis_transform(),
                  color=colors[0], fontsize=9)
        figure.text(.052, .914, "The smoke contrast reverses under each check", color=ink,
                    fontfamily="DejaVu Serif", fontweight="bold", fontsize=23)
        figure.text(.052, .857, "June 2023 · 27 fixed EPA monitors in eight county groups",
                    color="#4d6067", fontsize=11.5)
        markers = [Line2D([0], [0], marker="o", color=color, linestyle="", markersize=6)
                   for color in colors]
        figure.legend(markers, ("June 6–8", "June 27–29"), ncol=2, loc="upper right",
                      bbox_to_anchor=(.956, .882), frameon=False, fontsize=10, labelcolor=ink)
        figure.text(.052, .092, "Each omission dot is a rerun. Lines span the reruns for that check.",
                    color="#46595d", fontsize=9.5)
        figure.text(.052, .050, "Source: EPA AirData AQS 88101 · Archived results from the PaperSpine smoke study.",
                    color="#46595d", fontsize=9)
        figure.savefig(directory / "checks.svg", format="svg", metadata={
            "Date": None,
            "Description": "Atlantic minus Great Lakes departures under the primary, alternate reference, "
                           "hourly-derived, leave-one-site-out, and leave-one-group-out settings. Values "
                           "come from results.json in the smoke study source bundle. Ranges are over reruns.",
        })
        buffer = BytesIO()
        figure.savefig(buffer, format="pdf")
        save_plot(buffer.getvalue(), directory / "checks.webp")


def main():
    catalog = json.loads((RESEARCH / "showcase.json").read_bytes())
    for study, meta in catalog.items():
        directory = RESEARCH / study
        with pymupdf.open(directory / "paper.pdf") as paper:
            save_page(paper[0], directory / "first-page.webp", 1.35)
            save_page(paper[meta["resultPage"] - 1], directory / "results-page.webp", 1.6)
        with ZipFile(directory / "source.zip") as source:
            if study == "atlantic-ri":
                for name in ("figure", "checks"):
                    (directory / f"{name}.svg").write_bytes(source.read(f"out/{name}.svg"))
                    save_plot(source.read(f"out/{name}.pdf"), directory / f"{name}.webp", width=2400, quality=91)
            elif study in ARCHIVED_PLOTS:
                name = ARCHIVED_PLOTS[study]
                (directory / "checks.svg").write_bytes(source.read(f"{name}.svg"))
                save_plot(source.read(f"{name}.pdf"), directory / "checks.webp")
            else:
                regenerate_smoke_checks(json.loads(source.read("results.json")), directory)


if __name__ == "__main__":
    main()
