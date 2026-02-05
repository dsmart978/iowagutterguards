#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def get_meta_description(html: str) -> str:
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"\s*/?>', html, flags=re.I)
    return m.group(1).strip() if m else ""

def get_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, flags=re.I|re.S)
    return re.sub(r"\s+", " ", (m.group(1).strip() if m else "Iowa Gutter Guards"))

def replace_schema_block(html: str, schema_obj: dict) -> str:
    schema_json = json.dumps(schema_obj, ensure_ascii=False, separators=(",", ":"))
    block = f'<script id="schema-ld" type="application/ld+json">{schema_json}</script>'

    # Replace existing schema-ld block if present
    if re.search(r'<script\s+id="schema-ld"\s+type="application/ld\+json">.*?</script>', html, flags=re.I|re.S):
        return re.sub(
            r'<script\s+id="schema-ld"\s+type="application/ld\+json">.*?</script>',
            block,
            html,
            flags=re.I|re.S
        )

    # Otherwise insert before </head>
    if "</head>" in html.lower():
        return re.sub(r"</head>", block + "\n</head>", html, flags=re.I, count=1)

    return block + "\n" + html

def main() -> None:
    html = read_text(HOME)

    base = "https://iowagutterguards.online"
    desc = get_meta_description(html)
    title = get_title(html)

    # Clean, valid JSON-LD for the homepage.
    # Keep it focused: Business + Website + WebPage + primary Service.
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "LocalBusiness",
                "@id": f"{base}/#business",
                "name": "Iowa Gutter Guards",
                "url": f"{base}/",
                "telephone": "+1-515-329-5128",
                "email": "info@iowagutterguards.online",
                "priceRange": "$$",
                "image": f"{base}/assets/gutter-guard-features-1.jpg",
                "address": {
                    "@type": "PostalAddress",
                    "addressRegion": "IA",
                    "addressCountry": "US"
                },
                "openingHoursSpecification": [
                    {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
                        "opens": "08:00",
                        "closes": "18:00"
                    }
                ],
                "areaServed": {
                    "@type": "GeoCircle",
                    "geoMidpoint": {
                        "@type": "GeoCoordinates",
                        "latitude": 41.5868,
                        "longitude": -93.625
                    },
                    "geoRadius": 120000
                }
            },
            {
                "@type": "WebSite",
                "@id": f"{base}/#website",
                "url": f"{base}/",
                "name": "Iowa Gutter Guards",
                "publisher": {"@id": f"{base}/#business"}
            },
            {
                "@type": "WebPage",
                "@id": f"{base}/#webpage",
                "url": f"{base}/",
                "name": title,
                "description": desc if desc else "Professional gutter guard installation across Central Iowa to prevent clogs and reduce overflow.",
                "isPartOf": {"@id": f"{base}/#website"},
                "about": {"@id": f"{base}/#business"}
            },
            {
                "@type": "Service",
                "@id": f"{base}/#service-gutter-guards",
                "name": "Gutter Guard Installation",
                "serviceType": "Gutter guard installation",
                "provider": {"@id": f"{base}/#business"},
                "url": f"{base}/",
                "areaServed": {
                    "@type": "AdministrativeArea",
                    "name": "Central Iowa",
                    "address": {
                        "@type": "PostalAddress",
                        "addressRegion": "IA",
                        "addressCountry": "US"
                    }
                }
            }
        ]
    }

    out = replace_schema_block(html, schema)
    write_text(HOME, out)
    print("Updated: index.html (homepage schema replaced with valid JSON-LD)")

if __name__ == "__main__":
    main()
