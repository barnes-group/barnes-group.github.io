# Barnes Group product pages

Static product website served by GitHub Pages at `https://barnes-group.github.io/`.

| Path | Content |
| --- | --- |
| `/` | Product hub (`index.html`) |
| `/g25/` | G25 hot runner temperature controller |

More product sections can be added as further top-level folders (for example `/g26/`) and linked from the hub.

## Structure

- `assets/` shared across products: fonts, brand logos, base styles (`css/site.css`)
- `g25/assets/` G25 styles, script and images. `img/screens/` holds genuine G25 application screenshots as WebP (full size and `-sm` for small screens).
- `scripts/templates/g25.html` source of `g25/index.html`. Do not edit the generated file by hand.
- `scripts/build_pages.py` renders templates. `{{dev <screen>|<panel|tablet|browser>|<alt>|<caption>|<slot>|<url>}}` inserts a screenshot inside a device frame, and a caption makes it enlargeable.
- Screenshots are exported by `doc/website/prepare_screenshots.py` in the (private) G25 repository, which also replaces customer names in the sample data and fails if one is still readable.
- `scripts/detect_crops.py` writes `scripts/crops.json`, which crops tall screens to the relevant area. Edit `OVERRIDES` in the script for dialogs and short screens.

## Update the G25 page

```sh
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt   # tesseract is also required
# in the G25 repository, only when screenshots changed:
#   python3 doc/website/prepare_screenshots.py ../barnes-group.github.io
.venv/bin/python scripts/detect_crops.py
.venv/bin/python scripts/build_pages.py
python3 -m http.server 8000                                  # preview at http://localhost:8000/g25/
```

Content must stay limited to features of the latest released G25 software. Screenshots come from the release screenshot pipeline of the G25 repository, so rerun it for a new release.

## Publishing

GitHub Pages serves the `main` branch from the repository root. Pushing to `main` publishes.
