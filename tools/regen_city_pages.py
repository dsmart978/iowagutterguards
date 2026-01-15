#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from html import escape

ROOT = Path(".").resolve()
INDEX = ROOT / "index.html"
SERVICE_AREAS = ROOT / "service-areas"

if not INDEX.exists():
    raise SystemExit("ERROR: index.html not found in repo root.")
if not SERVICE_AREAS.exists():
    raise SystemExit("ERROR: service-areas/ folder not found. Your repo tree shows it exists, so run this from the repo root.")

base = INDEX.read_text(encoding="utf-8", errors="replace")

DOMAIN = "https://iowagutterguards.online"

def replace_title(html: str, new_title: str) -> str:
    if re.search(r"<title>.*?</title>", html, flags=re.I | re.S):
        return re.sub(r"<title>.*?</title>", f"<title>{escape(new_title)}</title>", html, flags=re.I | re.S, count=1)
    return re.sub(r"</head>", f"  <title>{escape(new_title)}</title>\n</head>", html, flags=re.I, count=1)

def upsert_meta_description(html: str, desc: str) -> str:
    pat = r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>'
    if re.search(pat, html, flags=re.I):
        return re.sub(pat, f'<meta name="description" content="{escape(desc)}">', html, flags=re.I, count=1)
    return re.sub(r"</head>", f'  <meta name="description" content="{escape(desc)}">\n</head>', html, flags=re.I, count=1)

def upsert_canonical(html: str, canonical_url: str) -> str:
    pat = r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>'
    if re.search(pat, html, flags=re.I):
        return re.sub(pat, f'<link rel="canonical" href="{escape(canonical_url)}">', html, flags=re.I, count=1)
    return re.sub(r"</head>", f'  <link rel="canonical" href="{escape(canonical_url)}">\n</head>', html, flags=re.I, count=1)

def replace_first_h1(html: str, new_h1: str) -> str:
    pat = r"<h1\b([^>]*)>.*?</h1>"
    if re.search(pat, html, flags=re.I | re.S):
        return re.sub(pat, rf"<h1\1>{escape(new_h1)}</h1>", html, flags=re.I | re.S, count=1)
    return html

def insert_city_intro_after_first_section(html: str, city: str) -> str:
    intro = f"""
<section class="city-intro" style="max-width: 1100px; margin: 0 auto; padding: 18px 16px;">
  <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); border-radius: 14px; padding: 16px;">
    <p style="margin: 0; line-height: 1.6;">
      <strong>Iowa Gutter Guards serves {escape(city)}, Iowa</strong> with professionally installed, premium gutter guard systems designed to stop clogs, reduce overflow, and keep water moving where it belongs.
      Get a fast online quote, then we’ll confirm details and schedule your install.
    </p>
  </div>
</section>
""".lstrip()

    # Insert after the first </section> that appears after <main ...>
    m_main = re.search(r"<main\b[^>]*>", html, flags=re.I)
    if not m_main:
        return html + "\n" + intro

    start = m_main.end()
    m_end_first_section = re.search(r"</section>", html[start:], flags=re.I)
    if not m_end_first_section:
        return html[:start] + "\n" + intro + html[start:]

    ins_at = start + m_end_first_section.end()
    return html[:ins_at] + "\n" + intro + html[ins_at:]

def titlecase_from_slug(slug: str) -> str:
    # slug like "west-des-moines-ia" -> "West Des Moines"
    s = slug.strip().lower()
    s = re.sub(r"-ia$", "", s)
    words = [w for w in s.split("-") if w]
    return " ".join(w.capitalize() for w in words)

def extract_city_from_existing(existing_html: str, slug: str) -> str:
    # Prefer existing H1 text if present
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", existing_html, flags=re.I | re.S)
    if m:
        h1 = re.sub(r"<[^>]+>", "", m.group(1))
        h1 = re.sub(r"\s+", " ", h1).strip()
        # Try patterns like "Gutter Guards in Des Moines, IA"
        m2 = re.search(r"in\s+(.+?),\s*IA\b", h1, flags=re.I)
        if m2:
            return m2.group(1).strip()
        # Or just use the whole h1 if it contains city-like words
        if len(h1) <= 80 and any(ch.isalpha() for ch in h1):
            # Strip leading service phrase if present
            h1 = re.sub(r"^(gutter guards?\s+(installation\s+)?)in\s+", "", h1, flags=re.I).strip()
            h1 = re.sub(r",\s*IA\b.*$", "", h1, flags=re.I).strip()
            if h1:
                return h1

    return titlecase_from_slug(slug)

def build_city_page(home_html: str, city: str, slug: str) -> str:
    title = f"Gutter Guards in {city}, IA | Iowa Gutter Guards"
    h1 = f"Gutter Guards in {city}, IA"
    desc = f"Professional gutter guard installation in {city}, Iowa. Stop clogs, reduce overflow, and protect your home. Get a fast online quote from Iowa Gutter Guards."
    canonical = f"{DOMAIN}/service-areas/{slug}/"

    html = home_html
    html = replace_title(html, title)
    html = upsert_meta_description(html, desc)
    html = upsert_canonical(html, canonical)
    html = replace_first_h1(html, h1)
    html = insert_city_intro_after_first_section(html, city)
    return html

# Iterate every service area folder
targets = []
for d in sorted(SERVICE_AREAS.iterdir()):
    if not d.is_dir():
        continue
    slug = d.name
    out = d / "index.html"
    if out.exists():
        targets.append((slug, out))

if not targets:
    raise SystemExit("ERROR: No service-areas/*/index.html pages found to regenerate.")

written = 0
for slug, out_path in targets:
    existing_html = out_path.read_text(encoding="utf-8", errors="replace")
    city = extract_city_from_existing(existing_html, slug)
    new_html = build_city_page(base, city, slug)
    out_path.write_text(new_html, encoding="utf-8", newline="\n")
    written += 1

print(f"OK: regenerated {written} service-area pages as homepage clones (consistent layout).")