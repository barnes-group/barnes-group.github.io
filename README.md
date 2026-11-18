# Barnes Group product pages

Static product website served by GitHub Pages at `https://barnes-group.github.io/`.

| Path | Content |
| --- | --- |
| `/`, `/de/` | Landing page in the SPECTRIX look (EN, DE) |
| `/g25/`, `/g25/de/` | G25 hot runner temperature controller in the Gammaflux blue look (EN, DE) |

Add further products as top-level folders (for example `/g26/`) and link them from the landing page.

## Structure

- `scripts/templates/*.html` are the English sources of every page. Do not edit generated `index.html` files.
- `scripts/build_pages.py` renders templates to `index.html` and the translated `de/index.html`, adds cache-busting hashes to CSS/JS, and writes canonical and hreflang tags. `{{dev <screen>|<panel|tablet|browser>|<alt>|<caption>|<slot>|<url>}}` inserts a screenshot in a device frame; a caption makes it enlargeable.
- `scripts/i18n.py` and `scripts/i18n/de.json` translate by exact English segment (`{english: german}`). Run `python3 scripts/i18n.py dump de index.html g25/index.html` after changing copy to list segments without a translation; the build also reports counts. Product names (Mold Wizard, Mold Doctor, Even Heat, Tool Graph, ...) stay in English.
- `assets/css/site.css` shared base and G25 look, `assets/css/hub.css` landing page (SPECTRIX look), `g25/assets/` G25 styles, script and images.
- `scripts/detect_crops.py` writes `scripts/crops.json` (crop of tall screenshots).
- Screenshots are exported from the private G25 repository by `doc/website/prepare_screenshots.py`, which also replaces customer names in sample data.

## Language

The language dropdown (flag + code) lists every entry of `LANG_META` in `scripts/build_pages.py`. To add a language: add it to `LANG_META` and `LANG_LABEL`, add its flag to `FLAGS`, and create `scripts/i18n/<code>.json` (start from `python3 scripts/i18n.py dump <code> index.html g25/index.html`). The build then creates `/<code>/` pages and links them everywhere.

Pages exist in English (default) and German. The EN/DE switch is in the header. First-time visitors whose browser language is German are redirected to `/de/`; an explicit choice is remembered in `localStorage` and wins.

## Update

```sh
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt   # tesseract is also required for the screenshot export
.venv/bin/python scripts/detect_crops.py
.venv/bin/python scripts/build_pages.py
python3 -m http.server 8000      # preview at http://localhost:8000/
```

Content stays limited to features of the latest released G25 software.

## Publishing

GitHub Pages serves `main` from the repository root. Pushing to `main` publishes.
