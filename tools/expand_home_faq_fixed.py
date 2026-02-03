#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"

P_STYLE = 'style="margin-top:0.4rem; font-size:0.88rem; color:var(--muted);"'

# 8 new FAQs to ADD (not duplicates of your current 7)
NEW_FAQS = [
  (
    "Do gutter guards work in heavy rain?",
    "Yes, when they are installed correctly and the gutters underneath are draining properly. We make sure the gutter line is pitched correctly and downspouts are flowing so water can move through the system instead of backing up and spilling over."
  ),
  (
    "Will gutter guards cause water to overshoot the gutter?",
    "Overshoot is usually caused by poor alignment at the roof edge, incorrect slope, or existing drainage problems. We fit and fasten the guards so water follows the surface into the gutter, and we address obvious gutter issues before we cover anything up."
  ),
  (
    "Do gutter guards work with pine needles and small debris?",
    "They can, but the details matter. Iowa homes deal with pine needles, roof grit, and small debris, so the guard needs the right mesh and a solid frame, installed tight at seams and corners so debris cannot sneak into the trough."
  ),
  (
    "Will gutter guards cause ice dams in winter?",
    "No. Ice dams are caused by heat loss and refreezing at the roof edge, not by gutter guards. Guards can help keep the gutter channel clearer, but insulation and ventilation are what actually prevent ice dam formation."
  ),
  (
    "What if my gutters are sagging, leaking, or pulling away from the house?",
    "Guards do not fix structural gutter problems. If we find sagging runs, loose hangers, or leaking seams, we will recommend repairing those issues first so the guard system performs the way it should."
  ),
  (
    "How long does gutter guard installation usually take?",
    "Most installs are completed in a single visit. The time depends on the home size, roofline complexity, and whether any tuning or repairs are needed before we install the guards."
  ),
  (
    "Do I still need to maintain my gutters after guards are installed?",
    "Maintenance is dramatically reduced, but nothing is truly zero-maintenance. Most homeowners just do an occasional visual check after major storms and, if needed, rinse the top surface to keep water intake consistent."
  ),
  (
    "What happens after I request an estimate?",
    "We confirm your address and a few details, then provide a clear written estimate based on your roofline and gutter layout. If we need photos or one quick on-site check to verify tricky sections, we will tell you up front and keep it simple."
  ),
]

def strip_tags(s: str) -> str:
    return re.sub(r"<.*?>", "", s).strip()

def build_details_block(q: str, a: str) -> str:
    # Match the site's existing style: <summary><strong>Q</strong></summary> + <p style=...>A</p>
    return (
        "<details>\n"
        f"  <summary><strong>{q}</strong></summary>\n"
        f"  <p {P_STYLE}>\n"
        f"    {a}\n"
        "  </p>\n"
        "</details>"
    )

def replace_or_insert_schema_faq(html: str, faqs: list[tuple[str,str]]) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    script = f'<script id="schema-faq" type="application/ld+json">{schema_json}</script>\n'

    if re.search(r'<script[^>]+id="schema-faq"[^>]*>.*?</script>', html, flags=re.S):
        return re.sub(
            r'<script[^>]+id="schema-faq"[^>]*>.*?</script>\s*',
            script,
            html,
            flags=re.S,
        )

    # Insert before </head>
    if "</head>" not in html:
        raise SystemExit("Could not find </head> to insert FAQ schema.")
    return html.replace("</head>", script + "</head>", 1)

def main() -> None:
    html = HOME.read_text(encoding="utf-8", errors="replace")

    # Find the FAQ section
    m = re.search(r'(<section\b[^>]*\bid="faq"[^>]*>)(.*?)(</section>)', html, flags=re.S | re.I)
    if not m:
        raise SystemExit('Could not find <section id="faq"> on homepage.')

    sec_open, sec_body, sec_close = m.group(1), m.group(2), m.group(3)

    # Find the FAQ container div (the one holding the <details> blocks)
    dm = re.search(r'(<div\b[^>]*>\s*)(.*?<details>.*?</details>.*?)(\s*</div>)', sec_body, flags=re.S | re.I)
    if not dm:
        raise SystemExit("Could not find the FAQ <div> that contains <details> blocks inside the FAQ section.")

    div_open, div_inner, div_close = dm.group(1), dm.group(2), dm.group(3)

    # Extract existing FAQs (robust: any <details>...</details> inside that div)
    details_blocks = re.findall(r"<details>.*?</details>", div_inner, flags=re.S | re.I)
    if len(details_blocks) != 7:
        raise SystemExit(f"Expected 7 existing FAQ <details> blocks on homepage, found {len(details_blocks)}.")

    existing_qas: list[tuple[str,str]] = []
    for block in details_blocks:
        qm = re.search(r"<summary>.*?<strong>(.*?)</strong>.*?</summary>", block, flags=re.S | re.I)
        am = re.search(r"<p\b[^>]*>(.*?)</p>", block, flags=re.S | re.I)
        if not qm or not am:
            raise SystemExit("Could not parse an existing FAQ block. Homepage FAQ markup may have changed.")
        q = strip_tags(qm.group(1))
        a = strip_tags(am.group(1))
        existing_qas.append((q, a))

    # Build new 15 FAQ blocks: keep 7 existing + 8 new
    combined = existing_qas + NEW_FAQS
    if len(combined) != 15:
        raise SystemExit(f"FAQ combine error: expected 15 total, got {len(combined)}.")

    new_div_inner = "\n\n".join(build_details_block(q, a) for q, a in combined)

    # Replace just the details content inside the container div
    new_sec_body = sec_body[:dm.start(2)] + new_div_inner + sec_body[dm.end(2):]

    # Rebuild the full HTML
    new_html = html[:m.start(2)] + new_sec_body + html[m.end(2):]

    # Add/replace FAQPage schema that matches the 15 visible FAQs
    new_html = replace_or_insert_schema_faq(new_html, combined)

    HOME.write_text(new_html, encoding="utf-8")

if __name__ == "__main__":
    main()
