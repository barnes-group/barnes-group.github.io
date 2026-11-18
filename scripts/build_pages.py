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
    "moldmind": ("moldmind", "/moldmind/"),
    "intelligate-p": ("intelligate-p", "/intelligate-p/"),
}
# Add a language: append it here, add its flag below and create scripts/i18n/<code>.json
LANG_META = {"en": ("English", "GB"), "de": ("Deutsch", "DE"), "it": ("Italiano", "IT")}
LANGS = [c for c in LANG_META if c != "en"]
# Pages that exist only in some languages
PAGE_LANGS = {"intelligate-p": ["en", "de"]}
LANG_LABEL = {"en": "Language", "de": "Sprache", "it": "Lingua"}  # accessible name of the dropdown
FLAGS = {
    "GB": '<svg viewBox="0 0 60 40" aria-hidden="true"><clipPath id="gb"><rect width="60" height="40" rx="4"/></clipPath><g clip-path="url(#gb)"><rect width="60" height="40" fill="#012169"/><path d="M0 0l60 40M60 0L0 40" stroke="#fff" stroke-width="8"/><path d="M0 0l60 40M60 0L0 40" stroke="#C8102E" stroke-width="3"/><path d="M30 0v40M0 20h60" stroke="#fff" stroke-width="13"/><path d="M30 0v40M0 20h60" stroke="#C8102E" stroke-width="7"/></g></svg>',
    "DE": '<svg viewBox="0 0 60 40" aria-hidden="true"><clipPath id="de"><rect width="60" height="40" rx="4"/></clipPath><g clip-path="url(#de)"><rect width="60" height="14" fill="#000"/><rect y="13" width="60" height="14" fill="#DD0000"/><rect y="26" width="60" height="14" fill="#FFCE00"/></g></svg>',
    "IT": '<svg viewBox="0 0 60 40" aria-hidden="true"><clipPath id="it"><rect width="60" height="40" rx="4"/></clipPath><g clip-path="url(#it)"><rect width="20" height="40" fill="#009246"/><rect x="20" width="20" height="40" fill="#fff"/><rect x="40" width="20" height="40" fill="#CE2B37"/></g></svg>',
}
EN_MAILTO = "mailto:info@gammaflux.com?subject=G25%20demo%20request&body=Hello%2C%0A%0AI%20would%20like%20to%20book%20a%20demo%20of%20the%20G25.%0A%0AName%3A%0ACompany%3A%0APhone%3A%0APreferred%20date%3A%0A"
DE_MAILTO = "mailto:info@gammaflux.de?subject=G25%20Demo-Anfrage&body=Guten%20Tag%2C%0A%0Aich%20m%C3%B6chte%20gerne%20eine%20Demo%20des%20G25%20buchen.%0A%0AName%3A%0AFirma%3A%0ATelefon%3A%0AWunschtermin%3A%0A"
IT_MAILTO = "mailto:info@gammaflux.com?subject=Richiesta%20demo%20G25&body=Buongiorno%2C%0A%0Avorrei%20prenotare%20una%20demo%20del%20G25.%0A%0ANome%3A%0AAzienda%3A%0ATelefono%3A%0AData%20preferita%3A%0A"
MAILTO = {"de": DE_MAILTO, "it": IT_MAILTO}
# German pages link to German versions of the other pages
def lang_links(name, lang):
    """Links between pages must stay inside the chosen language."""
    return {"hub": [('href="../g25/"', f'href="../g25/{lang}/"'), ('href="../moldmind/"', f'href="../moldmind/{lang}/"'), ] + ([('href="../intelligate-p/"', f'href="../intelligate-p/{lang}/"')] if lang in PAGE_LANGS["intelligate-p"] else []),
            "g25": [('href="../../"', f'href="../../{lang}/"')],
            "moldmind": [('href="../../"', f'href="../../{lang}/"')],
            "intelligate-p": [('href="../../"', f'href="../../{lang}/"')]}.get(name, [])


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
    avail = {c: m for c, m in LANG_META.items() if c in PAGE_LANGS.get(tpl, LANG_META)}
    langs = [c for c in avail if c != "en"]
    url = lambda c: BASE + path + ("" if c == "en" else c + "/")
    alt = f'<link rel="canonical" href="{url(lang)}">'
    alt += "".join(f'<link rel="alternate" hreflang="{c}" href="{url(c)}">' for c in avail)
    alt += f'<link rel="alternate" hreflang="x-default" href="{url("en")}">'
    codes = json.dumps(langs)
    redirect = ("<script>try{if(!localStorage.getItem('lang')){var l=(navigator.language||'').slice(0,2).toLowerCase();"
                f"if({codes}.indexOf(l)>-1)location.replace(l+'/'+location.hash)}}}}catch(e){{}}</script>") if lang == "en" else ""
    text = text.replace("<!--LANG_HEAD-->", redirect + alt)
    items = []
    for code, (label, flag) in avail.items():
        if code == lang:
            href = "./"
        elif lang == "en":
            href = f"{code}/"
        else:
            href = "../" if code == "en" else f"../{code}/"
        cur = ' aria-current="true"' if code == lang else ""
        items.append(f'<li><a href="{href}" hreflang="{code}" lang="{code}" data-lang="{code}" translate="no"{cur}>'
                     f'<span class="flag">{FLAGS[flag]}</span>{label}</a></li>')
    cur_flag = FLAGS[LANG_META[lang][1]]
    chev = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
    switch = (f'<details class="lang-switch"><summary aria-label="{LANG_LABEL[lang]}"><span class="flag">{cur_flag}</span>'
              f'<span class="code" translate="no">{lang.upper()}</span>{chev}</summary><ul>{"".join(items)}</ul></details>')
    text = text.replace("<!--LANG_SWITCH-->", switch)
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
        for lang in [l for l in LANGS if l in PAGE_LANGS.get(name, LANGS)]:
            mapping = i18n.load(lang)
            missing = set()
            text = i18n.translate(raw.replace(EN_MAILTO, MAILTO[lang]), mapping, missing)
            if missing:
                print(f"  {lang}: {len(missing)} untranslated segments in {name}")
            text = re.sub(r'<html\b[^>]*>', lambda m: m.group(0).replace('lang="en"', f'lang="{lang}" data-root="../"', 1), text, count=1)
            if lang in ("de", "it"):
                text = text.replace('data-dec="2">0.05<', 'data-dec="2">0,05<').replace('>0.1 °C (0.2 °F)<', '>0,1 °C (0,2 °F)<')
            text = prefix_urls(text)
            for a, b in lang_links(name, lang):
                text = text.replace(a, b)
            text = finalize(text, name, lang, folder, path)
            lout = page_dir / lang / "index.html"
            lout.parent.mkdir(parents=True, exist_ok=True)
            lout.write_text(text, encoding="utf-8")
            print("wrote", lout.relative_to(ROOT))


if __name__ == "__main__":
    main()
