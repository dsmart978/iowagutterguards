#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from html import escape

ROOT = Path(".").resolve()
INDEX = ROOT / "index.html"

if not INDEX.exists():
    raise SystemExit("ERROR: index.html not found in repo root. Run this from the folder that contains index.html.")

base = INDEX.read_text(encoding="utf-8", errors="replace")

# ---- helpers ----
def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\\s-]", "", s)
    s = re.sub(r"\\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

def replace_title(html: str, new_title: str) -> str:
    if re.search(r"<title>.*?</title>", html, flags=re.I | re.S):
        return re.sub(r"<title>.*?</title>", f"<title>{escape(new_title)}</title>", html, flags=re.I | re.S, count=1)
    # If missing title (rare), inject it before </head>
    return re.sub(r"</head>", f"  <title>{escape(new_title)}</title>\\n</head>", html, flags=re.I, count=1)

def upsert_meta_description(html: str, desc: str) -> str:
    # handle: <meta name="description" content="...">
    if re.search(r'<meta\\s+name=["\\\']description["\\\']\\s+content=["\\\'][^"\\\']*["\\\']\\s*/?>', html, flags=re.I):
        return re.sub(
            r'<meta\\s+name=["\\\']description["\\\']\\s+content=["\\\'][^"\\\']*["\\\']\\s*/?>',
            f'<meta name="description" content="{escape(desc)}">',
            html,
            flags=re.I,
            count=1
        )
    # insert before </head>
    return re.sub(r"</head>", f'  <meta name="description" content="{escape(desc)}">\\n</head>', html, flags=re.I, count=1)

def upsert_canonical(html: str, canonical_url: str) -> str:
    if re.search(r'<link\\s+rel=["\\\']canonical["\\\']\\s+href=["\\\'][^"\\\']*["\\\']\\s*/?>', html, flags=re.I):
        return re.sub(
            r'<link\\s+rel=["\\\']canonical["\\\']\\s+href=["\\\'][^"\\\']*["\\\']\\s*/?>',
            f'<link rel="canonical" href="{escape(canonical_url)}">',
            html,
            flags=re.I,
            count=1
        )
    return re.sub(r"</head>", f'  <link rel="canonical" href="{escape(canonical_url)}">\\n</head>', html, flags=re.I, count=1)

def replace_first_h1(html: str, new_h1: str) -> str:
    # Replace only the first <h1>…</h1>
    if re.search(r"<h1\\b[^>]*>.*?</h1>", html, flags=re.I | re.S):
        return re.sub(r"<h1\\b([^>]*)>.*?</h1>", rf"<h1\1>{escape(new_h1)}</h1>", html, flags=re.I | re.S, count=1)
    return html

def insert_city_intro_after_hero(html: str, city: str, county_hint: str | None = None) -> str:
    intro = f'''
<section class="city-intro" style="max-width: 1100px; margin: 0 auto; padding: 18px 16px;">
  <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); border-radius: 14px; padding: 16px;">
    <p style="margin: 0; line-height: 1.6;">
      <strong>Iowa Gutter Guards serves {escape(city)}, Iowa</strong> with professionally installed, premium gutter guard systems designed to stop clogs, reduce overflow, and keep water moving where it belongs.
      Get a fast online quote, then we’ll confirm details and schedule your install.
    </p>
  </div>
</section>
'''.lstrip()

    # Try to insert after the first </section> inside <main> (typically the hero section).
    m_main = re.search(r"<main\\b[^>]*>", html, flags=re.I)
    if not m_main:
        return html + "\\n" + intro

    start = m_main.end()
    m_end_first_section = re.search(r"</section>", html[start:], flags=re.I)
    if not m_end_first_section:
        # Insert right after <main ...>
        return html[:start] + "\\n" + intro + html[start:]

    ins_at = start + m_end_first_section.end()
    return html[:ins_at] + "\\n" + intro + html[ins_at:]

def normalize_href_to_path(href: str) -> Path:
    href = href.strip()
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href or href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:") or href.startswith("tel:"):
        return None  # type: ignore

    if not href.startswith("/"):
        # relative: treat as root-relative-ish
        href = "/" + href

    rel = href.lstrip("/")
    if rel.endswith("/"):
        return ROOT / rel / "index.html"
    if rel.endswith(".html"):
        return ROOT / rel
    return ROOT / rel / "index.html"

# ---- find city/service-area links from homepage ----
anchors = re.findall(r'<a\\b[^>]*href=["\\\']([^"\\\']+)["\\\'][^>]*>([^<]+)</a>', base, flags=re.I)
candidates: list[tuple[str,str]] = []
for href, text in anchors:
    t = re.sub(r"\\s+", " ", text).strip()
    h = href.strip()
    # Heuristic: service area links usually contain 'service' and are internal.
    if ("service" in h.lower()) and not h.lower().startswith(("http://","https://","mailto:","tel:")):
        # Avoid generic links
        if t and len(t) <= 40:
            candidates.append((h, t))

# Deduplicate by href
seen = set()
cities: list[tuple[str,str]] = []
for href, t in candidates:
    key = href.split("#",1)[0].split("?",1)[0]
    if key in seen:
        continue
    seen.add(key)
    cities.append((href, t))

if not cities:
    raise SystemExit("ERROR: I couldn't find any internal links containing 'service' on index.html. If your city links don't include 'service' in the URL, tell me the URL pattern and I'll adjust the generator.")

domain = "https://iowagutterguards.online"

written = 0
for href, city_text in cities:
    out_path = normalize_href_to_path(href)
    if out_path is None:
        continue

    city = city_text
    # Build SEO fields
    new_title = f"Gutter Guards in {city}, IA | Iowa Gutter Guards"
    new_h1 = f"Gutter Guards in {city}, IA"
    new_desc = f"Professional gutter guard installation in {city}, Iowa. Stop clogs, reduce overflow, and protect your home. Get a fast online quote from Iowa Gutter Guards."
    canonical_url = f"{domain}{href.split('#',1)[0].split('?',1)[0]}"
    if not canonical_url.endswith("/") and out_path.name == "index.html":
        canonical_url += "/"

    html = base
    html = replace_title(html, new_title)
    html = upsert_meta_description(html, new_desc)
    html = upsert_canonical(html, canonical_url)
    html = replace_first_h1(html, new_h1)
    html = insert_city_intro_after_hero(html, city)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8", newline="\\n")
    written += 1

print(f"OK: regenerated {written} city/service-area pages as homepage-clones for layout consistency.")