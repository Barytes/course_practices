#!/usr/bin/env python3
"""Pack the MiniMind HTML textbook into a phone-readable EPUB."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1] / "minimind-textbook"
OUT = ROOT / "minimind-3.epub"
BOOK_JS = ROOT / "assets" / "book.js"

CHAPTER_RE = re.compile(
    r'\{\s*file:\s*"([^"]+)"\s*,\s*title:\s*"([^"]+)"\s*,\s*short:\s*"([^"]+)"\s*,\s*part:\s*"([^"]+)"\s*\}'
)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
DROP_TAGS = {"script", "button"}
BOOL_ATTRS = {"hidden", "disabled", "checked", "selected", "open"}


def chapters() -> list[dict[str, str]]:
    text = BOOK_JS.read_text(encoding="utf-8")
    found = CHAPTER_RE.findall(text)
    if len(found) < 10:
        raise SystemExit(f"failed to parse chapter list from {BOOK_JS}")
    return [{"file": f, "title": t, "short": s, "part": p} for f, t, s, p in found]


def attr_value(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def serialize(node) -> str:
    if isinstance(node, NavigableString):
        if node.parent and node.parent.name == "script":
            return ""
        return escape(str(node))
    name = node.name
    if name is None:
        return "".join(serialize(child) for child in node.children)
    if name in DROP_TAGS:
        return ""
    classes = node.get("class") or []
    if "pager" in classes or "menu-btn" in classes:
        return ""
    attrs = []
    for key, value in node.attrs.items():
        if key.startswith("on"):
            continue
        if isinstance(value, list):
            value = " ".join(value)
        elif isinstance(value, bool) or key in BOOL_ATTRS:
            attrs.append(key)
            continue
        if value is None:
            continue
        attrs.append(f'{key}="{attr_value(str(value))}"')
    attr = (" " + " ".join(attrs)) if attrs else ""
    if name in VOID:
        return f"<{name}{attr}/>"
    inner = "".join(serialize(child) for child in node.children)
    return f"<{name}{attr}>{inner}</{name}>"


def extract_main(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    main = soup.select_one("main.paper")
    if main is None:
        raise ValueError("no main.paper content")
    for pager in main.select(".pager, [data-pager]"):
        pager.decompose()
    body = "".join(serialize(child) for child in main.children).strip()
    if not body:
        raise ValueError("empty chapter body")
    return body


EPUB_CSS = """
body {
  font-family: "Songti SC", "STSong", "Noto Serif SC", Georgia, serif;
  line-height: 1.7;
  color: #1b1610;
  font-size: 1em;
}
h1 { font-size: 1.6em; line-height: 1.25; }
h2 { font-size: 1.25em; margin-top: 1.4em; }
h3 { font-size: 1.08em; }
code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.86em; }
pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f3ead9;
  padding: 0.7em;
  border: 1px solid #cfc1a6;
}
table { border-collapse: collapse; width: 100%; font-size: 0.9em; }
th, td { border-bottom: 1px solid #d7cbb6; padding: 0.3em 0.35em; text-align: left; vertical-align: top; }
.callout, .plain-box, .where, .bridge, .say, .formula, .diagram, .card, .plain {
  margin: 0.9em 0;
  padding: 0.7em 0.8em;
  border: 1px solid #d7cbb6;
  background: #fbf6ea;
}
.plain-box { background: #1b1610; color: #f6f0e4; }
.label { font-size: 0.8em; font-weight: 700; letter-spacing: 0.06em; }
svg { max-width: 100%; height: auto; }
.toc-grid a { display: block; margin: 0.25em 0; }
"""


def xhtml(title: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-Hans" lang="zh-Hans">
<head>
  <meta charset="utf-8"/>
  <title>{escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="book.css"/>
</head>
<body>
{body}
</body>
</html>
"""


def nav_xhtml(items: list[dict[str, str]]) -> str:
    lis = "\n".join(
        f'<li><a href="{escape(it["href"])}">{escape(it["title"])}</a></li>' for it in items
    )
    return xhtml(
        "目录",
        "<h1>从零实现 MiniMind-3</h1>"
        f'<nav epub:type="toc"><ol>{lis}</ol></nav>',
    )


def content_opf(items: list[dict[str, str]]) -> str:
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="book.css" media-type="text/css"/>',
    ]
    spine = []
    for it in items:
        manifest.append(
            f'<item id="{it["id"]}" href="{it["href"]}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{it["id"]}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0" xml:lang="zh-Hans">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:6a1f2c4e-9b33-4b0a-9d2e-minimind3-textbook</dc:identifier>
    <dc:title>从零实现 MiniMind-3</dc:title>
    <dc:language>zh-Hans</dc:language>
    <dc:creator>course_practices MiniMind textbook</dc:creator>
    <meta property="dcterms:modified">2026-09-15T00:00:00Z</meta>
  </metadata>
  <manifest>
    {chr(10).join(manifest)}
  </manifest>
  <spine>
    {chr(10).join(spine)}
  </spine>
</package>
"""


def container_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def stem(filename: str) -> str:
    return Path(filename).stem.replace(".", "-")


def main() -> None:
    catalog = chapters()
    items = []
    files: dict[str, str] = {
        "OEBPS/book.css": EPUB_CSS,
        "META-INF/container.xml": container_xml(),
    }
    nav_items = []
    for ch in catalog:
        src = ROOT / ch["file"]
        body = extract_main(src.read_text(encoding="utf-8"))
        href = f"{stem(ch['file'])}.xhtml"
        ident = "ch-" + stem(ch["file"])
        files[f"OEBPS/{href}"] = xhtml(ch["title"], body)
        items.append({"id": ident, "href": href, "title": ch["title"]})
        nav_items.append({"href": href, "title": f'{ch["short"]} · {ch["title"]}'})
    files["OEBPS/nav.xhtml"] = nav_xhtml(nav_items)
    files["OEBPS/content.opf"] = content_opf(items)

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in files.items():
            zf.writestr(name, data.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(catalog)} chapters)")


if __name__ == "__main__":
    main()
