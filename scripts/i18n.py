#!/usr/bin/env python3
"""Segment-based translation of rendered pages.

extract(html)  -> ordered list of translatable English segments (text blocks and attributes)
translate(html, mapping) -> html with every segment found in `mapping` replaced

A segment is the inner HTML of the smallest element that has its own text (whitespace collapsed,
inline <svg> replaced by {svgN}), or the value of alt / aria-label / data-caption / title /
meta content attributes. Translations live in scripts/i18n/<lang>.json as {english: translated}.
"""
import copy
import json
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, NavigableString

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

HERE = Path(__file__).resolve().parent
SKIP_TAGS = {"script", "style", "svg", "noscript", "head"}
ATTRS = ("alt", "aria-label", "data-caption", "title")
META = {"description", "og:title", "og:description"}
WORD = re.compile(r"[^\W\d_]{3,}", re.UNICODE)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def has_words(s):
    if s.strip().startswith("{{"):
        return False
    return bool(WORD.search(re.sub(r"<[^>]+>", " ", s)))


def holder(el):
    return any(type(c) is NavigableString and WORD.search(str(c)) for c in el.children)


def inner(el):
    """Inner HTML with svg elements replaced by placeholders; returns (string, [svg elements])."""
    clone = copy.copy(el)
    svgs = []
    for i, svg in enumerate(clone.find_all("svg")):
        svgs.append(svg)
        svg.replace_with(NavigableString("{svg%d}" % i))
    return norm(clone.decode_contents()), svgs


def walk(soup):
    """Yield ('text', element) and ('attr', element, name) in document order."""
    def visit(el):
        if el.get("translate") == "no":
            return
        for name in ATTRS:
            if el.has_attr(name):
                yield ("attr", el, name)
        if el.name == "meta" and (el.get("name") in META or el.get("property") in META) and el.has_attr("content"):
            yield ("attr", el, "content")
        if el.name == "title":
            yield ("text", el)
            return
        if el.name in SKIP_TAGS:
            return
        if holder(el):
            yield ("text", el)
            return
        for c in list(el.children):
            if hasattr(c, "children"):
                yield from visit(c)
    root = soup.find("html") or soup
    yield from visit(root)
    head = soup.find("head")
    if head:
        for el in head.find_all(["meta", "title"]):
            pass


def parse(html):
    return BeautifulSoup(html, "html.parser")


def collect(html):
    soup = parse(html)
    seen, out = set(), []
    head = soup.find("head")
    items = []
    if head:
        for el in head.find_all("title"):
            items.append(("text", el))
        for el in head.find_all("meta"):
            if (el.get("name") in META or el.get("property") in META) and el.has_attr("content"):
                items.append(("attr", el, "content"))
    body = soup.find("body")
    if body:
        items += list(walk(body))
    for it in items:
        if it[0] == "text":
            s, _ = inner(it[1])
        else:
            s = norm(it[1][it[2]])
        if s and has_words(s) and "@" not in re.sub(r"<[^>]+>", "", s) and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def translate(html, mapping, missing=None):
    soup = parse(html)
    head = soup.find("head")
    items = []
    if head:
        for el in head.find_all("title"):
            items.append(("text", el))
        for el in head.find_all("meta"):
            if (el.get("name") in META or el.get("property") in META) and el.has_attr("content"):
                items.append(("attr", el, "content"))
    body = soup.find("body")
    if body:
        items += list(walk(body))
    for it in items:
        if it[0] == "text":
            el = it[1]
            s, svgs = inner(el)
            if not (s and has_words(s)) or s not in mapping:
                if missing is not None and s and has_words(s) and "@" not in re.sub(r"<[^>]+>", "", s):
                    missing.add(s)
                continue
            frag = BeautifulSoup(mapping[s], "html.parser")
            el.clear()
            for c in list(frag.contents):
                el.append(c)
            for i, svg in enumerate(svgs):
                for node in list(el.find_all(string=re.compile(r"\{svg%d\}" % i))):
                    parts = re.split(r"(\{svg%d\})" % i, str(node))
                    new = []
                    for p in parts:
                        new.append(copy.copy(svg) if p == "{svg%d}" % i else NavigableString(p))
                    node.replace_with(*new)
        else:
            el, name = it[1], it[2]
            s = norm(el[name])
            if s in mapping:
                el[name] = mapping[s]
            elif missing is not None and s and has_words(s):
                missing.add(s)
    return str(soup)


def load(lang):
    p = HERE / "i18n" / f"{lang}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


if __name__ == "__main__":
    # usage: i18n.py dump <file.html>...   -> prints numbered untranslated segments for a language
    cmd, lang = sys.argv[1], sys.argv[2]
    mapping = load(lang)
    allseg = []
    for f in sys.argv[3:]:
        for s in collect(Path(f).read_text(encoding="utf-8")):
            if s not in allseg:
                allseg.append(s)
    todo = [s for s in allseg if s not in mapping]
    if cmd == "dump":
        for i, s in enumerate(todo):
            print(f"{i}\t{s}")
        print(f"# {len(todo)} untranslated of {len(allseg)}", file=sys.stderr)
