#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP = {".git", "node_modules", ".next", "dist", "build", ".cache", "functions"}

def skippable(p: Path) -> bool:
    return any(part in SKIP for part in p.parts)

def find_lead_form(html: str):
    # Find all <form ...>...</form> blocks
    forms = list(re.finditer(r"<form\\b[^>]*>.*?</form>", html, flags=re.I|re.S))
    if not forms:
        return None

    # Choose the first one that looks like a lead form (has name/email/phone inputs)
    for m in forms:
        block = m.group(0)
        if re.search(r'name=["\\\']?(name|fullname|full_name|email|phone|tel|telephone)["\\\']?', block, flags=re.I):
            return m
    # Fallback: first form
    return forms[0]

def patch_form_open_tag(form_block: str) -> str:
    # Update only the opening <form ...> tag
    m = re.search(r"<form\\b[^>]*>", form_block, flags=re.I)
    if not m:
        return form_block
    open_tag = m.group(0)

    def set_attr(tag: str, attr: str, value: str) -> str:
        if re.search(rf"\\b{attr}\\s*=", tag, flags=re.I):
            tag = re.sub(rf"\\b{attr}\\s*=\\s*([\"\\\']).*?\\1", rf'{attr}="{value}"', tag, flags=re.I)
        else:
            tag = tag[:-1] + f' {attr}="{value}">'
        return tag

    open_tag2 = open_tag
    open_tag2 = set_attr(open_tag2, "method", "POST")
    open_tag2 = set_attr(open_tag2, "action", "/api/lead")
    open_tag2 = set_attr(open_tag2, "accept-charset", "UTF-8")

    return form_block.replace(open_tag, open_tag2, 1)

def ensure_honeypot(form_block: str) -> str:
    # Add a hidden honeypot input if not present
    if re.search(r'name=["\\\']website["\\\']', form_block, flags=re.I):
        return form_block
    insert = '\\n  <div style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden" aria-hidden="true">\\n' \
             '    <label>Leave this field empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label>\\n' \
             '  </div>\\n'
    # Put it right after opening tag
    form_block = re.sub(r"(<form\\b[^>]*>)", r"\\1" + insert, form_block, flags=re.I, count=1)
    return form_block

def write_lf(path: Path, text: str):
    text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    path.write_bytes(text.encode("utf-8"))

def main():
    pages = []
    pages += list(ROOT.glob("*.html"))
    pages += list(ROOT.glob("**/index.html"))

    changed = 0
    scanned = 0

    for p in sorted(set(pages)):
        if not p.is_file() or skippable(p):
            continue
        scanned += 1
        html = p.read_text(encoding="utf-8", errors="replace")

        fm = find_lead_form(html)
        if not fm:
            continue

        old_block = fm.group(0)
        new_block = patch_form_open_tag(old_block)
        new_block = ensure_honeypot(new_block)

        if new_block != old_block:
            html2 = html.replace(old_block, new_block, 1)
            write_lf(p, html2)
            changed += 1

    print(f"OK: scanned {scanned} pages; updated lead form on {changed} pages to POST /api/lead")

if __name__ == "__main__":
    main()