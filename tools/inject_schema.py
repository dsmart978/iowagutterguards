#!/usr/bin/env python3
from __future__ import annotations

import re, json
from pathlib import Path
from datetime import datetime
from html import unescape

ROOT = Path(".").resolve()
DOMAIN = "https://iowagutterguards.online"

ORG_NAME = "Iowa Gutter Guards"
ORG_URL  = DOMAIN + "/"
ORG_EMAIL = "info@iowagutterguards.online"
ORG_PHONE = "+1-515-329-5128"

# Pages to process: all index.html files + any root *.html
targets = []
targets += list(ROOT.glob("*.html"))
targets += list(ROOT.glob("**/index.html"))

# Skip folders we never want to touch
SKIP_PARTS = {".git", "node_modules", ".next", "dist", "build", ".cache"}

def is_skippable(p: Path) -> bool:
    parts = set(p.parts)
    return any(s in parts for s in SKIP_PARTS)

def strip_tags(html: str) -> str:
    html = re.sub(r"<script\\b[^>]*>.*?</script>", "", html, flags=re.I|re.S)
    html = re.sub(r"<style\\b[^>]*>.*?</style>", "", html, flags=re.I|re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\\s+", " ", text).strip()
    return unescape(text)

def page_url_from_path(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return DOMAIN + "/"
    if rel.endswith("/index.html"):
        return DOMAIN + "/" + rel[:-len("index.html")]
    return DOMAIN + "/" + rel

def detect_city_from_path(p: Path) -> str | None:
    # service-areas/des-moines-ia/index.html -> Des Moines
    parts = p.relative_to(ROOT).parts
    if len(parts) >= 3 and parts[0] == "service-areas" and parts[-1] == "index.html":
        slug = parts[1]
        slug = re.sub(r"-ia$", "", slug.lower())
        words = [w for w in slug.split("-") if w]
        return " ".join(w.capitalize() for w in words)
    return None

def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, flags=re.I|re.S)
    if m:
        t = strip_tags(m.group(1))
        if t:
            return t
    return ORG_NAME

def extract_meta_description(html: str) -> str | None:
    m = re.search(r'<meta\\s+name=["\\\']description["\\\']\\s+content=["\\\']([^"\\\']+)["\\\']', html, flags=re.I)
    if m:
        d = m.group(1).strip()
        return d if d else None
    return None

def extract_faq_from_details(html: str) -> list[dict]:
    # Looks for <details><summary>Question</summary> ... Answer ... </details>
    faqs = []
    for m in re.finditer(r"<details\\b[^>]*>\\s*<summary\\b[^>]*>(.*?)</summary>(.*?)</details>", html, flags=re.I|re.S):
        q_raw = m.group(1)
        a_raw = m.group(2)
        q = strip_tags(q_raw)
        a = strip_tags(a_raw)
        # sanity filters
        if not q or not a: 
            continue
        if len(q) < 6 or len(a) < 10:
            continue
        faqs.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })
    return faqs

def build_schema(html: str, path: Path) -> list[dict]:
    url = page_url_from_path(path)
    title = extract_title(html)
    desc = extract_meta_description(html)

    city = detect_city_from_path(path)

    # Base: Organization + WebSite + WebPage
    graph = []

    org = {
        "@type": "Organization",
        "@id": ORG_URL + "#org",
        "name": ORG_NAME,
        "url": ORG_URL,
        "email": ORG_EMAIL,
        "telephone": ORG_PHONE,
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": ORG_PHONE,
            "contactType": "sales",
            "areaServed": "US",
            "availableLanguage": ["en"]
        }]
    }
    graph.append(org)

    website = {
        "@type": "WebSite",
        "@id": ORG_URL + "#website",
        "url": ORG_URL,
        "name": ORG_NAME,
        "publisher": {"@id": ORG_URL + "#org"}
    }
    graph.append(website)

    webpage = {
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": title,
        "isPartOf": {"@id": ORG_URL + "#website"},
        "about": {"@id": ORG_URL + "#org"},
    }
    if desc:
        webpage["description"] = desc
    graph.append(webpage)

    # Service: present on all pages, but city pages get localized areaServed
    service = {
        "@type": "Service",
        "@id": ORG_URL + "#service-gutter-guards",
        "name": "Gutter Guard Installation",
        "serviceType": "Gutter guard installation",
        "provider": {"@id": ORG_URL + "#org"},
        "url": url,
    }
    if city:
        service["areaServed"] = {
            "@type": "City",
            "name": city,
            "address": {
                "@type": "PostalAddress",
                "addressRegion": "IA",
                "addressCountry": "US"
            }
        }
    else:
        service["areaServed"] = {
            "@type": "AdministrativeArea",
            "name": "Central Iowa",
            "address": {"@type": "PostalAddress", "addressRegion": "IA", "addressCountry": "US"}
        }
    graph.append(service)

    # FAQPage: only when we can extract visible FAQs
    faqs = extract_faq_from_details(html)
    if faqs:
        faqpage = {
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": faqs
        }
        graph.append(faqpage)

    return graph

def inject_jsonld(html: str, graph: list[dict]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@graph": graph
    }
    jsonld = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    block = f'<script id="schema-ld" type="application/ld+json">{jsonld}</script>'

    # Replace existing
    if re.search(r'<script\\s+id=["\\\']schema-ld["\\\']\\s+type=["\\\']application/ld\\+json["\\\']\\s*>.*?</script>', html, flags=re.I|re.S):
        return re.sub(
            r'<script\\s+id=["\\\']schema-ld["\\\']\\s+type=["\\\']application/ld\\+json["\\\']\\s*>.*?</script>',
            block,
            html,
            flags=re.I|re.S,
            count=1
        )

    # Insert before </head> if possible; else before </body>; else append
    if re.search(r"</head>", html, flags=re.I):
        return re.sub(r"</head>", block + "\\n</head>", html, flags=re.I, count=1)
    if re.search(r"</body>", html, flags=re.I):
        return re.sub(r"</body>", block + "\\n</body>", html, flags=re.I, count=1)
    return html + "\\n" + block + "\\n"

changed = 0
scanned = 0

for p in sorted(set(targets)):
    if is_skippable(p): 
        continue
    if not p.is_file():
        continue
    scanned += 1
    html = p.read_text(encoding="utf-8", errors="replace")
    graph = build_schema(html, p)
    new_html = inject_jsonld(html, graph)
    if new_html != html:
        p.write_text(new_html, encoding="utf-8", newline="\\n")
        changed += 1

print(f"OK: scanned {scanned} pages; updated {changed} pages with JSON-LD schema (Organization/WebSite/WebPage/Service + FAQPage when detected).")