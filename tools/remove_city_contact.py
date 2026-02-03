#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]

def remove_section_by_id(html_text: str, section_id: str) -> tuple[str, bool]:
    # Removes <section ... id="section_id"> ... </section> including nested sections.
    pattern = re.compile(rf'(<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>)', re.I)
    m = pattern.search(html_text)
    if not m:
        return html_text, False

    start = m.start(1)
    i = start
    depth = 0
    while i < len(html_text):
        if html_text.startswith("<section", i):
            depth += 1
        elif html_text.startswith("</section>", i):
            depth -= 1
            if depth == 0:
                end = i + len("</section>")
                return html_text[:start] + html_text[end:], True
        i += 1

    return html_text, False

def main() -> None:
    sa_dir = SITE_ROOT / "service-areas"
    if not sa_dir.exists():
        raise SystemExit("Missing service-areas directory.")

    pages = sorted(sa_dir.glob("*-ia/index.html"))
    changed = 0

    for page in pages:
        txt = page.read_text(encoding="utf-8", errors="replace")
        txt2, did = remove_section_by_id(txt, "contact")
        if did:
            page.write_text(txt2, encoding="utf-8")
            changed += 1

    # Zero output on success unless something is wrong.
    # If you want proof later, use: git diff --name-only

if __name__ == "__main__":
    main()
