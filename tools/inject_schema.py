#!/usr/bin/env python3
from __future__ import annotations

import re, json
from pathlib import Path
from html import unescape

ROOT = Path(".").resolve()
DOMAIN = "https://iowagutterguards.online"

# Brand/entity (no address because you don't want GBP yet and we won't invent one)
BUSINESS_NAME = "Iowa Gutter Guards"
BUSINESS_URL  = DOMAIN + "/"
BUSINESS_EMAIL = "info@iowagutterguards.online"
BUSINESS_PHONE = "+1-515-329-5128"

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".cache"}

def is_skippable(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)

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
        slug = parts[1].lower()
        slug = re.sub(r"-ia$", "", slug)
        words = [w for w in slug.split("-") if w]
        return " ".join(w.capitalize() for w in words)
    return None

def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, flags=re.I|re.S)
    if m:
        t = strip_tags(m.group(1))
        if t:
            return t
    return BUSINESS_NAME

def extract_meta_description(html: str) -> str | None:
    m = re.search(r'<meta\\s+name=["\\\']description["\\\']\\s+content=["\\\']([^"\\\']+)["\\\']', html, flags=re.I)
    if m:
        d = m.group(1).strip()
        return d if d else None
    return None

def extract_faq_from_details(html: str) -> list[dict]:
    """
    Extract visible FAQs from <details><summary>Question</summary>Answer...</details>
    This keeps us compliant: schema only for content users can see.
    """
    faqs = []
    for m in re.finditer(
        r"<details\\b[^>]*>\\s*<summary\\b[^>]*>(.*?)</summary>(.*?)</details>",
        html,
        flags=re.I|re.S
    ):
        q = strip_tags(m.group(1))
        a = strip_tags(m.group(2))
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

def build_graph(html: str, path: Path) -> list[dict]:
    url = page_url_from_path(path)
    title = extract_title(html)
    desc = extract_meta_description(html)
    city = detect_city_from_path(path)

    org_id = BUSINESS_URL + "#business"
    site_id = BUSINESS_URL + "#website"
    page_id = url + "#webpage"
    service_id = BUSINESS_URL + "#service-gutter-guards"

    graph: list[dict] = []

    # Use LocalBusiness as primary entity (better fit than generic Organization)
    business = {
        "@type": "LocalBusiness",
        "@id": org_id,
        "name": BUSINESS_NAME,
        "url": BUSINESS_URL,
        "email": BUSINESS_EMAIL,
        "telephone": BUSINESS_PHONE,
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": BUSINESS_PHONE,
            "contactType": "sales",
            "areaServed": "US",
            "availableLanguage": ["en"]
        }]
    }
    graph.append(business)

    website = {
        "@type": "WebSite",
        "@id": site_id,
        "url": BUSINESS_URL,
        "name": BUSINESS_NAME,
        "publisher": {"@id": org_id}
    }
    graph.append(website)

    webpage = {
        "@type": "WebPage",
        "@id": page_id,
        "url": url,
        "name": title,
        "isPartOf": {"@id": site_id},
        "about": {"@id": org_id}
    }
    if desc:
        webpage["description"] = desc
    graph.append(webpage)

    service = {
        "@type": "Service",
        "@id": service_id,
        "name": "Gutter Guard Installation",
        "serviceType": "Gutter guard installation",
        "provider": {"@id": org_id},
        "url": url
    }

    # City pages get explicit areaServed
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
            "address": {
                "@type": "PostalAddress",
                "addressRegion": "IA",
                "addressCountry": "US"
            }
        }

    graph.append(service)

    # FAQ schema only if we can detect visible FAQs
    faqs = extract_faq_from_details(html)
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": faqs
        })

    return graph

def inject_schema(html: str, graph: list[dict]) -> str:
    payload = {"@context": "https://schema.org", "@graph": graph}
    jsonld = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    block = f'<script id="schema-ld" type="application/ld+json">{jsonld}</script>'

    # Replace existing schema block if present
    pat = r'<script\\s+id=["\\\']schema-ld["\\\']\\s+type=["\\\']application/ld\\+json["\\\']\\s*>.*?</script>'
    if re.search(pat, html, flags=re.I|re.S):
        return re.sub(pat, block, html, flags=re.I|re.S, count=1)

    # Otherwise insert before </head>
    if re.search(r"</head>", html, flags=re.I):
        return re.sub(r"</head>", block + "\\n</head>", html, flags=re.I, count=1)

    # Fallback insert
    if re.search(r"</body>", html, flags=re.I):
        return re.sub(r"</body>", block + "\\n</body>", html, flags=re.I, count=1)

    return html + "\\n" + block + "\\n"

# Collect pages: root *.html + all */index.html
targets = []
targets += list(ROOT.glob("*.html"))
targets += list(ROOT.glob("**/index.html"))

scanned = 0
updated = 0

for p in sorted(set(targets)):
    if not p.is_file():
        continue
    if is_skippable(p):
        continue

    scanned += 1
    html = p.read_text(encoding="utf-8", errors="replace")
    graph = build_graph(html, p)
    new_html = inject_schema(html, graph)

    if new_html != html:
        p.write_text(new_html, encoding="utf-8", newline="\\n")
        updated += 1

print(f"OK: scanned {scanned} pages; updated {updated} pages with JSON-LD (LocalBusiness/WebSite/WebPage/Service + FAQPage when visible).")