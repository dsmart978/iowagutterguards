#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".cache"}

def skippable(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)

def normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")

def write_utf8_lf(path: Path, text: str) -> None:
    path.write_bytes(normalize_newlines(text).encode("utf-8"))

FORM_OPEN_RE = re.compile(r"<form\b[^>]*>", re.I)
ON_SUBMIT_RE = re.compile(r'\s+onsubmit\s*=\s*(["\']).*?\1', re.I | re.S)
ENCTYPE_RE = re.compile(r'\s+enctype\s*=\s*(["\']).*?\1', re.I | re.S)
ACTION_RE  = re.compile(r'\s+action\s*=\s*(["\']).*?\1', re.I | re.S)
METHOD_RE  = re.compile(r'\s+method\s*=\s*(["\']).*?\1', re.I | re.S)
ACCEPT_RE  = re.compile(r'\s+accept-charset\s*=\s*(["\']).*?\1', re.I | re.S)

HONEYPOT_HTML = """
  <div style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden" aria-hidden="true">
    <label>Leave this field empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label>
  </div>
""".rstrip("\n")

def patch_form_open_tag(open_tag: str) -> str:
    # Remove inline handlers and mailto junk
    t = open_tag
    t = ON_SUBMIT_RE.sub("", t)
    t = ENCTYPE_RE.sub("", t)

    # Ensure method/action/charset are set to what we want
    if METHOD_RE.search(t):
        t = METHOD_RE.sub(' method="POST"', t, count=1)
    else:
        t = t[:-1] + ' method="POST">'

    if ACTION_RE.search(t):
        t = ACTION_RE.sub(' action="/api/lead"', t, count=1)
    else:
        t = t[:-1] + ' action="/api/lead">'

    if ACCEPT_RE.search(t):
        t = ACCEPT_RE.sub(' accept-charset="UTF-8"', t, count=1)
    else:
        t = t[:-1] + ' accept-charset="UTF-8">'

    # Clean double spaces that can happen after removals
    t = re.sub(r"\s{2,}", " ", t)
    t = t.replace(" >", ">")
    return t

def ensure_honeypot_after_open(html: str, open_tag: str) -> str:
    # If honeypot already exists, do nothing
    if re.search(r'name\s*=\s*(["\'])website\1', html, flags=re.I):
        return html
    return html.replace(open_tag, open_tag + "\n" + HONEYPOT_HTML + "\n", 1)

def looks_like_our_lead_form(open_tag: str, html: str) -> bool:
    # Primary match: the exact mailto/onsubmit style you currently have
    if "mailto:" in open_tag.lower():
        return True
    if "handlesubmit" in open_tag.lower():
        return True

    # Fallback: if the form contains a submit button "Send my info", treat it as the lead form
    # (Your scan shows that button everywhere.)
    return bool(re.search(r'<button[^>]+type\s*=\s*(["\'])submit\1[^>]*>\s*Send my info\s*</button>', html, flags=re.I))

def main() -> None:
    pages = []
    pages += list(ROOT.glob("*.html"))
    pages += list(ROOT.glob("**/index.html"))

    scanned = 0
    updated = 0
    forms_seen = 0

    for p in sorted(set(pages)):
        if not p.is_file() or skippable(p):
            continue

        scanned += 1
        html = p.read_text(encoding="utf-8", errors="replace")
        html = normalize_newlines(html)

        m = FORM_OPEN_RE.search(html)
        if not m:
            continue

        open_tag = m.group(0)
        forms_seen += 1

        # Only patch pages where the first form looks like the lead form
        # (On your site, it does.)
        if not looks_like_our_lead_form(open_tag, html):
            # Try to find ANY form tag that matches mailto/handleSubmit
            found = None
            for fm in FORM_OPEN_RE.finditer(html):
                tag = fm.group(0)
                if looks_like_our_lead_form(tag, html):
                    found = tag
                    break
            if not found:
                continue
            open_tag = found

        new_open = patch_form_open_tag(open_tag)
        if new_open != open_tag:
            html = html.replace(open_tag, new_open, 1)
            html = ensure_honeypot_after_open(html, new_open)
            write_utf8_lf(p, html)
            updated += 1
        else:
            # Even if tag already matches, still ensure honeypot exists
            html2 = ensure_honeypot_after_open(html, open_tag)
            if html2 != html:
                write_utf8_lf(p, html2)
                updated += 1

    print(f"OK: scanned {scanned} pages; updated {updated} pages. (Forms examined: {forms_seen})")
    print("Expected result: every lead form now POSTs to /api/lead (no mailto, no onsubmit handler).")

if __name__ == "__main__":
    main()