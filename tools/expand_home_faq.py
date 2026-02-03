#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"

NEW_FAQS = [
  ("Do gutter guards work in heavy rain?",
   "Yes, when they are installed correctly. Proper gutter pitch, clean downspouts, and tight alignment along the roof edge allow water to enter the gutter while debris is kept out. Most overflow problems come from poor installation or underlying drainage issues, not the guards themselves."),

  ("Will gutter guards cause water to overshoot the gutter?",
   "Overshoot usually happens when guards are installed incorrectly or when gutters are already sagging or clogged. We check slope, attachment, and roof edge alignment so water flows into the gutter instead of skipping past it."),

  ("Do gutter guards work with pine needles and small debris?",
   "They do, as long as the guard style and installation match the debris conditions. Fine debris like pine needles and shingle grit are common in Iowa, which is why proper fit and consistent fastening matter more than brand names."),

  ("Will gutter guards cause ice dams in winter?",
   "No. Ice dams are caused by heat loss and refreezing at the roof edge, not by gutter guards. Guards can still allow snowmelt to drain when conditions permit, but insulation and ventilation are what actually prevent ice dams."),

  ("Can gutter guards be installed on existing gutters?",
   "In most cases, yes. We inspect the existing gutters first to make sure they are pitched correctly and draining properly. If repairs or adjustments are needed, we address those before installing guards."),

  ("What if my gutters are sagging or leaking?",
   "Gutter guards will not fix structural problems. If we find sagging sections, loose hangers, or leaking seams, we recommend repairing those issues first so the guards can actually perform as intended."),

  ("How long does gutter guard installation take?",
   "Most installations are completed in a single visit. The exact time depends on the size of the home, roof complexity, and whether any repairs are needed beforehand."),

  ("Do gutter guards eliminate all maintenance?",
   "They greatly reduce maintenance, but nothing is completely maintenance-free. Occasional checks are still recommended, especially after major storms, to make sure water is flowing freely through the system.")
]

def extract_existing_faq(html: str) -> list[tuple[str,str]]:
    items = []
    for m in re.finditer(r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", html, re.S):
        q = re.sub(r"<.*?>", "", m.group(1)).strip()
        a = re.sub(r"<.*?>", "", m.group(2)).strip()
        items.append((q, a))
    return items

def build_faq_schema(faqs: list[tuple[str,str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a
                }
            } for q, a in faqs
        ]
    }

html = HOME.read_text(encoding="utf-8")

existing = extract_existing_faq(html)
if len(existing) < 7:
    raise SystemExit("Expected at least 7 existing FAQs on homepage.")

combined = existing + NEW_FAQS
combined = combined[:15]

# Rebuild FAQ HTML
faq_html = "\n".join(
    f"<details>\n  <summary>{q}</summary>\n  <p>{a}</p>\n</details>"
    for q, a in combined
)

# Replace FAQ block
html = re.sub(
    r"(<section[^>]+id=\"faq\"[^>]*>).*?(</section>)",
    r"\1\n" + faq_html + r"\n\2",
    html,
    flags=re.S
)

# Replace or insert FAQ schema
schema = build_faq_schema(combined)
schema_json = json.dumps(schema, ensure_ascii=False)

if re.search(r'"@type"\s*:\s*"FAQPage"', html):
    html = re.sub(
        r"<script[^>]*application/ld\+json[^>]*>.*?FAQPage.*?</script>",
        f'<script type="application/ld+json">{schema_json}</script>',
        html,
        flags=re.S
    )
else:
    html = html.replace("</head>", f'<script type="application/ld+json">{schema_json}</script>\n</head>')

HOME.write_text(html, encoding="utf-8")
