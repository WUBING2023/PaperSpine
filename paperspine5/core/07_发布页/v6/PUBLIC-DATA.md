# Website and community data

The V6 site serves the same research files and verified edition manifest in nine languages. The four interactive studies link to the original manuscripts, analysis and figures. Every language has the full installation guide and contributor history. Contributor design credit links to [Lauyanng’s PR #19](https://github.com/WUBING2023/PaperSpine/pull/19). The public site reads public repository data. Manuscripts and annotations from a user’s workbench stay local.

Paths below are relative to the Pages project root, including its `/PaperSpine/` prefix.

| Surface | Upstream or public JSON | Update behavior |
| --- | --- | --- |
| GitHub stars | GitHub REST `GET /repos/WUBING2023/PaperSpine`, field `stargazers_count` | The visible page checks once an hour. `api/v1/repository.json` supplies a dated fallback. |
| Downloads | GitHub REST `GET /repos/WUBING2023/PaperSpine/releases/tags/{tag}` | The install cards match asset filenames against the three links built from `v6/channel.json`. `v6/download-stats.json` supplies the last saved counts for that tag. A genuine zero is displayed. |
| Contributors | GitHub REST `GET /repos/WUBING2023/PaperSpine/contributors?anon=false&per_page=100&page={page}` | A complete paginated roster replaces the previous result and preserves the visitor’s search. The dated fallback is `contributors/contributors-data.json`. GitHub determines attributed commits and may cache its response. The editorial credits link to the actual PRs or commits. |
| Cities and universities | `api/v1/atlas.json` | GitHub Actions is scheduled at minute 17 of every hour (UTC). The map checks hourly for a newly published aggregate. `totalStars` in this historical schema counts **profiles sampled**, `located` counts matched profiles, and `generated` gives the observation date. Repository stars have a separate source. |

Each feed loads when first opened and refreshes hourly while the page is visible. Returning to the page or reconnecting checks for an overdue refresh. The browser retains the last successful result in memory and respects GitHub rate limits. Snapshots retain their original observation dates. Only aggregate map data and public contributor credit are served. The profile collector budgets up to 400 profile reads per run and rotates older cached entries. During a cold start the site retains the preceding dated map until coverage catches up.

The GitHub READMEs use SVG version and activity indicators regenerated during the hourly Pages build and on release deployments. Their download total covers the three assets of the displayed release. GitHub may cache these images.

China’s province geometry uses Natural Earth 1:50m Admin 1 v5.1.1. The map places university markers at identified cities. To regenerate province shapes, run `node atlas/build-provinces.cjs path/to/ne_50m_admin_1_states_provinces.geojson` in the public checkout. [Dataset](https://github.com/nvkelso/natural-earth-vector/blob/v5.1.1/geojson/ne_50m_admin_1_states_provinces.geojson) · [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/)

## Local preview

From the public checkout, run the commands below. The Pages workflow uses the same assembly function. A fresh output directory keeps previously generated files out of the published routes.

```sh
python -B paperspine5/release_tools/build_site.py
python -B paperspine5/release_tools/assemble_pages.py build/preview
python -B "paperspine5/core/07_发布页/v6/build_v6.py" download-stats website/v6/downloads build/preview/v6/download-stats.json
python -B atlas/community_snapshot.py build/preview/contributors/contributors-data.json
python -m http.server 8000 --bind 127.0.0.1 --directory build/preview
```

Open `/v6/` for the product, `/?lang=en` for the standalone atlas, or `/contributors/` for credits. The GitHub Actions job also publishes the repository fallback when it fetches repository metadata.

## Keep language editions synchronized

The Pages build renders the complete home, installation guide and contributor layouts for every language. Update the matching entries in [locales.json](locales.json) when changing public prose or the four study captions. From the public checkout, regenerate the localized GitHub READMEs with `python -B "paperspine5/core/07_发布页/v6/localization.py" .`. The Pages build checks that the generated READMEs match their source and translation catalog.
