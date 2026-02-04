#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime, timezone

SITE_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BASE_URL = "https://iowagutterguards.online"

EXCLUDE_DIRS = {
    ".git", ".github", "assets", "audit", "data", "tools", "node_modules", ".wrangler"
}

def detect_base_url() -> str:
    home = SITE_ROOT / "index.html"
    if home.exists():
        txt = home.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', txt, flags=re.I)
        if m:
            # canonical might be https://domain/ or https://domain
            url = m.group(1).strip()
            url = re.sub(r"/+$", "", url)
            return url
    return DEFAULT_BASE_URL.rstrip("/")

def find_index_pages() -> list[Path]:
    pages: list[Path] = []
    for p in SITE_ROOT.rglob("index.html"):
        rel_parts = p.relative_to(SITE_ROOT).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        pages.append(p)
    return sorted(pages)

def path_to_url(base: str, index_path: Path) -> str:
    rel = index_path.relative_to(SITE_ROOT).as_posix()  # e.g. service-areas/ankeny-ia/index.html
    if rel == "index.html":
        return base + "/"
    # directory URL form with trailing slash
    dir_url = rel[:-len("index.html")]
    if not dir_url.endswith("/"):
        dir_url += "/"
    return base + "/" + dir_url

def file_lastmod(p: Path) -> str:
    ts = p.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    # date-only is acceptable and keeps things simple
    return dt.strftime("%Y-%m-%d")

def escape_xml(s: str) -> str:
    return (s.replace("&","&amp;")
              .replace("<","&lt;")
              .replace(">","&gt;")
              .replace('"',"&quot;")
              .replace("'","&apos;"))

def build_sitemap(base: str, pages: list[Path]) -> str:
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        url = path_to_url(base, p)
        lastmod = file_lastmod(p)
        lines.append("  <url>")
        lines.append(f"    <loc>{escape_xml(url)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

def build_robots(base: str) -> str:
    # Keep it permissive. If you need to block admin/drafts later, we can.
    return (
        "User-agent: *\n"
        "Disallow:\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )

def maybe_write_indexnow_key() -> str | None:
    key = (os.environ.get("INDEXNOW_KEY") or "").strip()
    if not key:
        return None

    # Bing/IndexNow keys are often hex-ish. We'll allow a safe filename charset.
    if not re.fullmatch(r"[A-Za-z0-9]{8,128}", key):
        raise SystemExit("INDEXNOW_KEY contains invalid characters. Use only letters/numbers (8-128 chars).")

    key_file = SITE_ROOT / f"{key}.txt"
    key_file.write_text(key + "\n", encoding="utf-8")
    return key_file.name

def main() -> None:
    base = detect_base_url()
    pages = find_index_pages()

    sitemap = build_sitemap(base, pages)
    (SITE_ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = build_robots(base)
    (SITE_ROOT / "robots.txt").write_text(robots, encoding="utf-8")

    key_filename = maybe_write_indexnow_key()

    print(f"Base URL: {base}")
    print(f"Pages in sitemap: {len(pages)}")
    print("Wrote: sitemap.xml")
    print("Wrote: robots.txt")
    if key_filename:
        print(f"Wrote IndexNow key file: {key_filename}")
    else:
        print("IndexNow key file: not created (set $env:INDEXNOW_KEY to create it)")

if __name__ == "__main__":
    main()
