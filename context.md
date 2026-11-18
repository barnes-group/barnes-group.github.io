# Context: G25 product website (barnes-group.github.io)

Hand-over notes for continuing work in a new chat, for example to add another language. Languages so far: English, German, Italian. Ticket: G6P-3087 (customer-facing G25 product website).

## Live site

- https://barnes-group.github.io/, /de/ and /it/ : landing page in the SPECTRIX look (purple, Roboto Condensed). The G25 tile stays Gammaflux blue.
- https://barnes-group.github.io/g25/, /g25/de/ and /g25/it/ : G25 product page in the Gammaflux blue/dark look (Open Sans).
- Repo: `barnes-group/barnes-group.github.io` (public), local clone `~/Documents/GitHub/barnes-group.github.io`. GitHub Pages serves `main` from the root. Pushing to `main` publishes within about 1 to 2 minutes.
- The private G25 repo (`barnes-group/g6p`, local `~/Documents/GitHub/g6p`, branch `g6p-3087`) is the source of the screenshots, the operator manual and the release facts. Nothing for this ticket is committed there yet (see "Open items").

## How the site is built

Plain static HTML/CSS/JS, no framework. Generated pages are committed; never edit `index.html` files by hand.

- `scripts/templates/hub.html` and `scripts/templates/g25.html`: English sources.
- `scripts/build_pages.py`: renders templates to `index.html`, then creates `<lang>/index.html` for every language in `LANGS`. Also adds cache-busting hashes to CSS/JS, canonical and hreflang tags, a browser-language redirect on the English page, and the language dropdown. Run: `python3 scripts/build_pages.py` (needs `beautifulsoup4`; a venv with it exists at `/tmp/venv` only in the old session, so create a new one: `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt`).
- `{{dev <screen>|<panel|tablet|browser>|<alt>|<caption>|<slot>|<url>}}` inserts a screenshot in a device frame. A caption makes it enlargeable. `scripts/crops.json` (from `scripts/detect_crops.py`) crops tall screens.
- `scripts/i18n.py` and `scripts/i18n/<lang>.json`: translation by exact English segment (`{"english text": "translation"}`). The segment is the inner HTML of the smallest element with its own text, with inline `<svg>` replaced by `{svg0}`, plus `alt`, `aria-label`, `data-caption`, `title` and meta description/OG attributes. Elements with `translate="no"` are skipped.
- `assets/css/site.css` (shared base and G25 look), `assets/css/hub.css` (landing page), `g25/assets/css/g25.css`, `g25/assets/js/g25.js`, `assets/js/lang.js` (language dropdown behaviour).
- Screenshots live in `g25/assets/img/screens/*.webp` (full size and `-sm`), exported from the G25 repo (see below).
- Manual: `g25/downloads/G25-Operator-Manual-EN-Rev02.pdf` (English only, published as is, 24 MB). Its screenshots still show the customer sample name "Toyota Air Filter"; this was accepted by the user.

## How to add a language (for example French)

1. In `scripts/build_pages.py` add the language to `LANG_META` (code: (native name, flag key)), add its accessible label to `LANG_LABEL`, and add an SVG flag to `FLAGS`. Also add a localised demo mailto next to `DE_MAILTO`/`IT_MAILTO` and register it in the `MAILTO` dict. Update the language-specific CSS in `assets/css/site.css` (`html:is([lang="de"], [lang="it"])` rules: hides the header crumb below 1900 px and collapses the menu below 1300 px) for the new language if its labels are long.
2. Generate the list of untranslated segments: `python3 scripts/i18n.py dump <code> index.html g25/index.html` (423 segments, ~25k characters). Translate them into `scripts/i18n/<code>.json` as `{english: translation}`. Use `scripts/i18n/de.json` as the reference for tone and for which terms stay English.
3. `g25/assets/js/g25.js` has the scenario texts and image alt texts in code (`pick({ de: ..., it: ... }, english)`); add the new language there. The count-up decimal separator is set there too (`COMMA`). `build_pages.py` replaces `0.05` and `0.1 °C (0.2 °F)` with comma decimals for `de` and `it`; extend that tuple for other comma languages. `main()` sets `lang` and `data-root` on the `<html>` tag of translated pages.
4. Run the build, check that it reports no untranslated segments, check both pages at about 1440 px and at a narrow width, then commit and push.
5. The dropdown, hreflang links, language redirect (browser language) and links between pages inside one language are generated automatically.

## Translation rules the user gave

- Keep proper names and feature names in English: Mold Wizard, Mold Doctor®, Even Heat, Even Cool, Tool Graph, Quick Mold, Fault Analysis, Wiring Analysis, Thermodynamic Analysis, Tuning Wizard, Find Zones, One Motion Controller, G25, Gammaflux, SPECTRIX, OPC UA, EUROMAP 82.2.
- Customer-facing, plain language, little jargon. Technical detail only where a section is about that detail.
- Only features of the latest released G25 software (1.5.934). The "News" box announces an upcoming version (custom user roles, USB-stick login, Wi-Fi setup, cycle count per mold). Do not claim anything else from it.

## Design decisions

- G25 page: dark Gammaflux blue by default, light theme available (toggle, `?theme=light|dark` for testing). Device frames use a concentric radius (screen radius = bezel radius minus bezel padding, set via `--ro` and `--bz` in `g25.css`).
- Sections on the G25 page: News banner, Overview and specs, architecture diagram, "Outstanding features" (7 tabs: Even Heat/Cool, sequences, OPC UA, touch UI, remote screens, motion control, materials), "Explore more features" (8 tabs), manual download, contact. Tabs wrap onto a new line. `#<feature-id>` deep links open a tab (for example `#opcua`, `#omc`).
- The landing page has no "Book a demo" button; it lives only on the G25 page.
- Book a demo = mailto link to `info@gammaflux.com` (the German page uses `info@gammaflux.de`, the Italian page `info@gammaflux.com` with Italian text). No separate support address was found online; gammaflux.com redirects to the SPECTRIX contact form.
- Landing page footer links to spectrix.com. The Gammaflux by SPECTRIX logo is on the G25 tile and the G25 page.
- Simulation mode was removed from the features on purpose. The motion controller (OMC) has no screenshot on purpose (the available one still says "eControl"); it uses the servo-drive icon from the G25 UI (`ui/app/src/components/IconSVG.svelte`).
- Language dropdown uses inline SVG flags (no emoji, they do not render on Windows).

## Screenshots and customer names

The screenshots come from `g6p/doc/manual/screenshots/en/en_<name>.png` (1080x1920). The sample data contains the customer name "Toyota" in the footer and on two pages. The export script replaces it with "Air Filter" and fails if OCR still finds it. The script was meant to live at `g6p/doc/website/prepare_screenshots.py` (with `screens.txt`), but that folder does not exist right now (see below). The version that worked is in the git history of this repo only as output; recreate it if screenshots must be re-exported: crop footer text cells and repaint them with Open Sans using the cell background colour, then check with `tesseract`.

## Preview and checks

- `python3 -m http.server 8912 --bind 127.0.0.1` in the repo root, then open `http://127.0.0.1:8912/g25/` (port 8765 is used by another app on the user's machine).
- Headless screenshots: Google Chrome with `--headless=new --window-size=W,H --screenshot=out.png URL`. The `--window-size` minimum is about 500 px wide; the in-IDE browser tool ignores custom viewport sizes. Lazy images need a copy of the page without `loading="lazy"` to appear in full-page shots.
- After a deploy: `gh api repos/barnes-group/barnes-group.github.io/pages --jq .status` should say `built`. Users may need a hard refresh (assets carry a content hash, so this is normally not needed).

## Open items

- `g6p` branch `g6p-3087` has no commits. Untracked there: `context.md` (not part of this work; it contains unrelated FillControl notes, leave it alone). The folder `doc/website/` with `prepare_screenshots.py` and `screens.txt` was lost or never created in the last step; recreate it if wanted.
- The pull request for G6P-3087 (with the link https://barnes-group.github.io/g25/) is not created. The repo's PR skill requires: base `develop`, title starting with the ticket id, short body in the fixed format (Description / Major / Minor/Notes), no AI attribution, and the branch must be pushed first. The user decides when to commit and push.
- German and Italian text were written without a native review; edits go in `scripts/i18n/de.json` and `scripts/i18n/it.json`.
- The manual is English only.
- Content wording on the landing page ("Six strong brands") paraphrases spectrix.com and should be confirmed.
- All imagery and copy still need approval for external use (acceptance criterion of the ticket).
