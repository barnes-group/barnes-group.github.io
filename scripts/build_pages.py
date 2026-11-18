#!/usr/bin/env python3
"""Render scripts/templates/<page>.html into <page>/index.html.

Template macro:  {{dev <screen>|<panel|tablet|browser>|<alt text>|<caption>|<slot>|<url>}}
  screen   file name (without extension) in g25/assets/img/screens
  caption  optional; screens with a caption can be enlarged in the lightbox
  slot     optional data-slot used by the scenario switcher
  url      address shown in the browser frame
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCREENS = ROOT / "g25/assets/img/screens"
CROPS = json.loads((ROOT / "scripts/crops.json").read_text())

SIZES = {
    "panel": "(max-width: 700px) 46vw, 300px",
    "tablet": "(max-width: 700px) 40vw, 240px",
    "browser": "(max-width: 700px) 90vw, 420px",
}


def device(match):
    parts = [p.strip() for p in match.group(1).split("|")]
    parts += [""] * (6 - len(parts))
    name, variant, alt, caption, slot, url = parts[:6]
    if not (SCREENS / f"{name}.webp").exists():
        raise SystemExit(f"missing screenshot: {name}")
    img = f"assets/img/screens/{name}"
    attrs = [
        f'src="{img}-sm.webp"',
        f'srcset="{img}-sm.webp 540w, {img}.webp 1080w"',
        f'sizes="{SIZES[variant]}"',
        'width="1080" height="1920"',
        f'alt="{html.escape(alt, quote=True)}"',
        'loading="lazy" decoding="async"',
    ]
    if caption:
        attrs += [
            'class="zoomable" tabindex="0" role="button"',
            f'data-full="{img}.webp"',
            f'data-caption="{html.escape(caption, quote=True)}"',
        ]
    if slot:
        attrs.append(f'data-slot="{slot}"')
    screen_style, img_style, crop_cls = "", "", ""
    top, bottom = CROPS.get(name, (0, 1))
    if variant == "panel" and not slot and (top, bottom) != (0, 1):
        span = bottom - top
        screen_style = f' style="aspect-ratio: 1080 / {round(1920 * span)}"'
        img_style = f' style="height: {100 / span:.3f}%; top: {-100 * top / span:.3f}%"'
        crop_cls = " device--crop" if top == 0 else " device--crop-mid"
    bar = ""
    if variant == "browser":
        bar = f'<div class="device__bar"><i></i><i></i><i></i><span>{html.escape(url)}</span></div>'
    cap = f"<figcaption>{html.escape(caption)}</figcaption>" if caption else ""
    return (
        f'<figure class="device device--{variant}{crop_cls}"><div class="device__shell">{bar}'
        f'<div class="device__screen"{screen_style}><img {" ".join(attrs)}{img_style}></div></div>{cap}</figure>'
    )


BASE = "https://barnes-group.github.io"
PAGES = {
    # template -> (output folder relative to ROOT, public path)
    "hub": ("", "/"),
    "g25": ("g25", "/g25/"),
}
LANGS = ["de"]
EN_MAILTO = "mailto:info@gammaflux.com?subject=G25%20demo%20request&body=Hello%2C%0A%0AI%20would%20like%20to%20book%20a%20demo%20of%20the%20G25.%0A%0AName%3A%0ACompany%3A%0APhone%3A%0APreferred%20date%3A%0A"
DE_MAILTO = "mailto:info@gammaflux.de?subject=G25%20Demo-Anfrage&body=Guten%20Tag%2C%0A%0Aich%20m%C3%B6chte%20gerne%20eine%20Demo%20des%20G25%20buchen.%0A%0AName%3A%0AFirma%3A%0ATelefon%3A%0AWunschtermin%3A%0A"
# German pages link to German versions of the other pages
DE_LINKS = {"hub": [('href="../g25/"', 'href="../g25/de/"')],
            "g25": [('href="../../"', 'href="../../de/"')]}


def asset_hash(page_dir, url):
    f = (page_dir / url).resolve()
    return hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.exists() else None


def stamp_assets(text, page_dir):
    def sub(m):
        h = asset_hash(page_dir, m.group(2))
        return f'{m.group(1)}="{m.group(2)}?v={h}"' if h else m.group(0)
    return re.sub(r'(src|href)="([^"?#:]+\.(?:css|js))(?:\?v=\w+)?"', sub, text)


def prefix_urls(text, prefix="../"):
    def fix(u):
        u = u.strip()
        if not u or u.startswith(("http", "mailto:", "#", "data:", "/", "./", "{{")) or u == ".":
            return u
        return prefix + u

    def attr(m):
        name, val = m.group(1), m.group(2)
        if name == "srcset":
            val = ", ".join(" ".join([fix(p.split()[0])] + p.split()[1:]) for p in val.split(","))
        else:
            val = fix(val)
        return f'{name}="{val}"'
    return re.sub(r'\b(src|href|srcset|data-full)="([^"]*)"', attr, text)


def finalize(text, tpl, lang, folder, path):
    en_url, de_url = BASE + path, BASE + path + "de/"
    alt = (f'<link rel="canonical" href="{en_url if lang == "en" else de_url}">'
           f'<link rel="alternate" hreflang="en" href="{en_url}">'
           f'<link rel="alternate" hreflang="de" href="{de_url}">'
           f'<link rel="alternate" hreflang="x-default" href="{en_url}">')
    redirect = ("<script>try{if(!localStorage.getItem('lang')&&/^de\\b/i.test(navigator.language||''))"
                "location.replace('de/'+location.hash)}catch(e){}</script>") if lang == "en" else ""
    text = text.replace("<!--LANG_HEAD-->", redirect + alt)
    hrefs = {"en": ("./", "de/"), "de": ("../", "./")}[lang]
    text = text.replace("{{lang_en}}", hrefs[0] if lang == "en" else "../").replace("{{lang_de}}", hrefs[1])
    text = text.replace(f'data-lang="{lang}"', f'data-lang="{lang}" aria-current="true"')
    return text


def main():
    for name, (folder, path) in PAGES.items():
        tpl = ROOT / "scripts/templates" / f"{name}.html"
        raw = re.sub(r"\{\{dev ([^}]+)\}\}", device, tpl.read_text(encoding="utf-8"))
        page_dir = ROOT / folder if folder else ROOT
        raw = stamp_assets(raw, page_dir)
        out = page_dir / "index.html"
        out.write_text(finalize(raw, name, "en", folder, path), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
        for lang in LANGS:
            mapping = i18n.load(lang)
            missing = set()
            text = i18n.translate(raw.replace(EN_MAILTO, DE_MAILTO), mapping, missing)
            if missing:
                print(f"  {lang}: {len(missing)} untranslated segments in {name}")
            text = text.replace('<html lang="en"', f'<html lang="{lang}" data-root="../"', 1)
            text = text.replace('data-dec="2">0.05<', 'data-dec="2">0,05<').replace('>0.1 °C (0.2 °F)<', '>0,1 °C (0,2 °F)<')
            text = prefix_urls(text)
            for a, b in DE_LINKS.get(name, []):
                text = text.replace(a, b)
            text = finalize(text, name, lang, folder, path)
            lout = page_dir / lang / "index.html"
            lout.parent.mkdir(parents=True, exist_ok=True)
            lout.write_text(text, encoding="utf-8")
            print("wrote", lout.relative_to(ROOT))


if __name__ == "__main__":
    main()
