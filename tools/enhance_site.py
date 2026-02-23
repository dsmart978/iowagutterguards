#!/usr/bin/env python3
"""
Iowa Gutter Guards - Site Enhancement Script
This script updates all HTML files with:
- External CSS reference
- Favicon links
- GA4 tracking code
- Open Graph meta tags
- Twitter Card meta tags
- Canonical URLs
- Trust badges
- Sticky phone bar
- Why Choose Us section
- Enhanced reviews display
- Improved CTAs
"""

import os
import re
from pathlib import Path

BASE_URL = "https://www.iowagutterguards.com"
PHONE_NUMBER = "(515) 249-9929"
GA4_ID = "G-XXXXXXXXXX"  # Replace with actual GA4 ID

# Common head elements to inject
def get_head_inject(title, description, canonical_path, og_image="/assets/images/og-image.jpg"):
    """Generate the head elements to inject into each page."""
    return f'''
  <!-- Favicon -->
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="{BASE_URL}{canonical_path}">
  
  <!-- Open Graph Meta Tags -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{BASE_URL}{canonical_path}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{BASE_URL}{og_image}">
  <meta property="og:site_name" content="Iowa Gutter Guards">
  <meta property="og:locale" content="en_US">
  
  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{BASE_URL}{og_image}">
  
  <!-- External CSS -->
  <link rel="stylesheet" href="/assets/css/styles.css">
  
  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_ID}');
  </script>
'''

# Trust badges HTML
TRUST_BADGES_HTML = '''
  <!-- Trust Badges Section -->
  <section class="trust-badges">
    <div class="trust-badge">
      <div class="trust-badge-icon">🏆</div>
      <div class="trust-badge-number">10+</div>
      <div class="trust-badge-label">Years Experience</div>
    </div>
    <div class="trust-badge">
      <div class="trust-badge-icon">🏠</div>
      <div class="trust-badge-number">5,000+</div>
      <div class="trust-badge-label">Homes Protected</div>
    </div>
    <div class="trust-badge">
      <div class="trust-badge-icon">⭐</div>
      <div class="trust-badge-number">4.9</div>
      <div class="trust-badge-label">Average Rating</div>
    </div>
    <div class="trust-badge">
      <div class="trust-badge-icon">✓</div>
      <div class="trust-badge-number">25-Year</div>
      <div class="trust-badge-label">Warranty</div>
    </div>
  </section>
'''

# Why Choose Us HTML
WHY_CHOOSE_US_HTML = '''
  <!-- Why Choose Us Section -->
  <section class="section why-choose-us">
    <h2>Why Choose Iowa Gutter Guards?</h2>
    <p>We're Central Iowa's trusted gutter protection specialists with a commitment to quality and customer satisfaction.</p>
    <div class="why-grid">
      <div class="why-card">
        <div class="why-card-icon">🛡️</div>
        <h3>Premium Protection</h3>
        <p>Our micro-mesh guards block 100% of debris while allowing maximum water flow, protecting your home year-round.</p>
      </div>
      <div class="why-card">
        <div class="why-card-icon">👨‍🔧</div>
        <h3>Expert Installation</h3>
        <p>Factory-trained installers ensure your gutter guards are fitted perfectly for lasting performance.</p>
      </div>
      <div class="why-card">
        <div class="why-card-icon">📋</div>
        <h3>25-Year Warranty</h3>
        <p>Our comprehensive warranty covers materials and workmanship, giving you peace of mind for decades.</p>
      </div>
      <div class="why-card">
        <div class="why-card-icon">💰</div>
        <h3>Free Estimates</h3>
        <p>No-obligation quotes with transparent pricing. We'll never pressure you to buy.</p>
      </div>
    </div>
  </section>
'''

# Sticky phone bar HTML (goes before closing body tag)
STICKY_PHONE_HTML = f'''
  <!-- Sticky Mobile Phone Bar -->
  <div class="sticky-phone-bar">
    <div class="sticky-phone-content">
      <span class="sticky-phone-text">Call Now:</span>
      <a href="tel:+15152499929" class="track-phone-click">📞 {PHONE_NUMBER}</a>
    </div>
  </div>
'''

# Tracking script reference
TRACKING_SCRIPT = '''
  <!-- Event Tracking -->
  <script src="/assets/js/tracking.js" defer></script>
'''

# Exit intent popup placeholder
EXIT_POPUP_HTML = '''
  <!-- Exit Intent Popup Placeholder (disabled by default) -->
  <div class="exit-popup-overlay" id="exitPopup" style="display:none;">
    <div class="exit-popup">
      <button class="exit-popup-close" onclick="document.getElementById('exitPopup').style.display='none'">&times;</button>
      <h3>Wait! Get a Free Quote</h3>
      <p>Before you go, get your free, no-obligation estimate for gutter guard installation.</p>
      <a href="#quote-form" class="btn-primary" onclick="document.getElementById('exitPopup').style.display='none'">Get My Free Quote</a>
    </div>
  </div>
'''

def extract_title_and_description(html):
    """Extract title and meta description from HTML."""
    title_match = re.search(r'<title>([^<]+)</title>', html)
    title = title_match.group(1) if title_match else "Iowa Gutter Guards"
    
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    description = desc_match.group(1) if desc_match else "Professional gutter guard installation in Central Iowa."
    
    return title, description

def get_canonical_path(filepath):
    """Get canonical path from file path."""
    rel_path = filepath.replace('/home/ubuntu/iowa_gutter_guards_improved', '')
    
    if rel_path.endswith('/index.html'):
        return rel_path.replace('/index.html', '/')
    elif rel_path.endswith('.html'):
        return rel_path.replace('.html', '/')
    return rel_path

def remove_inline_styles(html):
    """Remove inline <style> block but keep any external CSS references."""
    # Match the style block
    pattern = r'<style>.*?</style>'
    return re.sub(pattern, '', html, flags=re.DOTALL)

def update_html_file(filepath):
    """Update a single HTML file with all enhancements."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract metadata
    title, description = extract_title_and_description(html)
    canonical_path = get_canonical_path(filepath)
    
    # Check if already processed (has our external CSS)
    if '/assets/css/styles.css' in html:
        print(f"  Skipping (already processed): {filepath}")
        return
    
    # Remove inline styles
    html = remove_inline_styles(html)
    
    # Generate head injection
    head_inject = get_head_inject(title, description, canonical_path)
    
    # Insert head elements after <meta name="description">
    if '<meta name="description"' in html:
        html = re.sub(
            r'(<meta name="description"[^>]+>)',
            r'\1' + head_inject,
            html
        )
    else:
        # Insert after viewport meta
        html = re.sub(
            r'(<meta name="viewport"[^>]+>)',
            r'\1' + head_inject,
            html
        )
    
    # Determine if this is the homepage
    is_homepage = filepath.endswith('/index.html') and '/service-areas/' not in filepath and filepath.count('/') <= 4
    is_city_page = '/service-areas/' in filepath
    
    # Add trust badges after hero section (only on homepage and city pages)
    if (is_homepage or is_city_page) and TRUST_BADGES_HTML.strip() not in html:
        # Try to insert after hero section
        if '</section>' in html:
            # Find first section closing tag after hero
            hero_end = html.find('</section>')
            if hero_end > 0:
                html = html[:hero_end + len('</section>')] + TRUST_BADGES_HTML + html[hero_end + len('</section>'):]
    
    # Add Why Choose Us section (only on homepage)
    if is_homepage and 'why-choose-us' not in html:
        # Insert before footer
        footer_pos = html.find('<footer')
        if footer_pos > 0:
            html = html[:footer_pos] + WHY_CHOOSE_US_HTML + '\n  ' + html[footer_pos:]
    
    # Add sticky phone bar and tracking script before </body>
    if '</body>' in html and 'sticky-phone-bar' not in html:
        html = html.replace('</body>', STICKY_PHONE_HTML + EXIT_POPUP_HTML + TRACKING_SCRIPT + '\n</body>')
    
    # Improve CTA button text
    html = html.replace('>Get Quote<', '>Get Your Free Quote<')
    html = html.replace('>Submit<', '>Get My Free Quote →<')
    html = html.replace('>Get Started<', '>Start Your Free Quote<')
    
    # Add lazy loading to images
    html = re.sub(r'<img ', '<img loading="lazy" ', html)
    # Fix double lazy loading
    html = html.replace('loading="lazy" loading="lazy"', 'loading="lazy"')
    
    # Add descriptive alt text to images without alt
    html = re.sub(r'<img([^>]*?)(?<!alt=")>', lambda m: f'<img{m.group(1)} alt="Iowa Gutter Guards installation">', html)
    
    # Write updated file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  Updated: {filepath}")

def process_all_files():
    """Process all HTML files in the project."""
    base_dir = '/home/ubuntu/iowa_gutter_guards_improved'
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'audit', 'tools', '.wrangler']]
        
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                # Skip template file
                if 'template' not in file.lower():
                    html_files.append(filepath)
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    for filepath in sorted(html_files):
        try:
            update_html_file(filepath)
        except Exception as e:
            print(f"  ERROR processing {filepath}: {e}")
    
    print(f"\nProcessed {len(html_files)} files")

if __name__ == '__main__':
    print("Iowa Gutter Guards - Site Enhancement Script")
    print("=" * 50)
    process_all_files()
    print("\nDone!")
