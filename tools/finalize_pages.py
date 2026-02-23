#!/usr/bin/env python3
"""
Finalize all HTML pages:
1. Add Bing Webmaster Tools verification meta tag
2. Comment out GA4 tracking code with clear instructions
"""

import os
import re
from pathlib import Path

# Configuration
BING_API_KEY = "de33b1b0324d427cbf3df33ce570686b"
PROJECT_ROOT = Path(__file__).parent.parent

def find_html_files():
    """Find all HTML files in the project."""
    html_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip tool directories and backups
        dirs[:] = [d for d in dirs if d not in ['tools', 'node_modules', '.git', 'backups']]
        for file in files:
            if file.endswith('.html') and 'template' not in file.lower():
                html_files.append(os.path.join(root, file))
    return html_files

def add_bing_verification(content):
    """Add Bing Webmaster Tools verification meta tag if not present."""
    bing_meta = f'<meta name="msvalidate.01" content="{BING_API_KEY}" />'
    
    # Check if already present
    if 'msvalidate.01' in content:
        return content
    
    # Insert after viewport meta tag
    viewport_pattern = r'(<meta name="viewport"[^>]*>)'
    match = re.search(viewport_pattern, content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + f'\n  {bing_meta}' + content[insert_pos:]
    
    return content

def comment_out_ga4(content):
    """Comment out GA4 tracking code with clear instructions."""
    
    # Pattern to find GA4 code block
    ga4_pattern = r'(  <!-- Google Analytics 4 -->\s*\n  <script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-XXXXXXXXXX"></script>\s*\n  <script>\s*\n    window\.dataLayer = window\.dataLayer \|\| \[\];\s*\n    function gtag\(\)\{dataLayer\.push\(arguments\);\}\s*\n    gtag\(\'js\', new Date\(\)\);\s*\n    gtag\(\'config\', \'G-XXXXXXXXXX\'\);\s*\n  </script>)'
    
    # Check if already commented out
    if '<!-- OPTIONAL: Google Analytics 4' in content:
        return content
    
    match = re.search(ga4_pattern, content)
    if match:
        ga4_code = match.group(1)
        replacement = """  <!-- =================================================================
       OPTIONAL: Google Analytics 4 (GA4) Tracking
       ==================================================================
       Uncomment the lines below if you want to track website traffic
       and phone clicks. NOTE: GA4 does NOT help SEO rankings.
       It only helps you see which marketing efforts generate calls.
       
       To enable:
       1. Go to analytics.google.com and create a GA4 property
       2. Replace G-XXXXXXXXXX with your actual GA4 Measurement ID
       3. Uncomment the script tags below
       ================================================================= -->
  <!--
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  </script>
  -->"""
        content = content.replace(ga4_code, replacement)
    
    return content

def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add Bing verification
        content = add_bing_verification(content)
        
        # Comment out GA4
        content = comment_out_ga4(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function to process all HTML files."""
    html_files = find_html_files()
    print(f"Found {len(html_files)} HTML files")
    
    modified = 0
    for filepath in html_files:
        if process_file(filepath):
            modified += 1
            print(f"✓ Modified: {os.path.relpath(filepath, PROJECT_ROOT)}")
        else:
            print(f"  Skipped: {os.path.relpath(filepath, PROJECT_ROOT)}")
    
    print(f"\n✅ Modified {modified} of {len(html_files)} files")
    print(f"   - Added Bing verification: msvalidate.01={BING_API_KEY}")
    print(f"   - Commented out GA4 tracking with enable instructions")

if __name__ == "__main__":
    main()
