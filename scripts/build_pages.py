#!/usr/bin/env python3
"""Render scripts/templates/<page>.html into <page>/index.html.

Template macro:  {{dev <screen>|<panel|tablet|browser>|<alt text>|<caption>|<slot>|<url>}}
  screen   file name (without extension) in g25/assets/img/screens
  caption  optional; screens with a caption can be enlarged in the lightbox
  slot     optional data-slot used by the scenario switcher
  url      address shown in the browser frame
"""
import html
import json
import re
from pathlib import Path

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


def main():
    for tpl in (ROOT / "scripts/templates").glob("*.html"):
        out = ROOT / tpl.stem / "index.html"
        text = re.sub(r"\{\{dev ([^}]+)\}\}", device, tpl.read_text(encoding="utf-8"))
        out.write_text(text, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
