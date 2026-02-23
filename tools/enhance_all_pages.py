#!/usr/bin/env python3
"""
Iowa Gutter Guards - Comprehensive Site Enhancement Script
This script updates all HTML files with:
- External CSS reference
- Favicon links
- Open Graph meta tags
- Twitter Card meta tags
- Canonical URLs
- GA4 tracking code
- Sticky phone bar (mobile)
- Trust badges
- Exit-intent popup placeholder
- Enhanced CTAs
- Social proof elements
- Lazy loading for images
"""

import os
import re
import glob
from pathlib import Path

# Configuration
BASE_URL = "https://www.iowagutterguards.com"
GA_MEASUREMENT_ID = "G-XXXXXXXXXX"  # Replace with actual GA4 ID
PHONE_NUMBER = "(515) 329-5128"
PHONE_LINK = "tel:+15153295128"

# Page metadata
PAGE_METADATA = {
    "/": {
        "title": "Iowa Gutter Guards | Gutter Guards in Central Iowa",
        "description": "Iowa Gutter Guards installs premium gutter protection on homes across Central Iowa. Stop clogs, protect your home, and never climb a ladder again.",
        "og_image": "/assets/images/og-home.jpg",
        "priority": "homepage"
    },
    "/warranty/": {
        "title": "Warranty | Iowa Gutter Guards",
        "description": "Learn about Iowa Gutter Guards' warranty coverage for gutter guard installation across Central Iowa.",
        "og_image": "/assets/images/og-warranty.jpg",
        "priority": "static"
    },
    "/privacy-policy/": {
        "title": "Privacy Policy | Iowa Gutter Guards",
        "description": "Privacy policy for Iowa Gutter Guards website visitors.",
        "og_image": "/assets/images/og-default.jpg",
        "priority": "static"
    },
    "/terms-of-service/": {
        "title": "Terms of Service | Iowa Gutter Guards",
        "description": "Terms of service for Iowa Gutter Guards.",
        "og_image": "/assets/images/og-default.jpg",
        "priority": "static"
    },
    "/customer-service/": {
        "title": "Customer Service | Iowa Gutter Guards",
        "description": "Contact Iowa Gutter Guards customer service for questions about your gutter guard installation.",
        "og_image": "/assets/images/og-default.jpg",
        "priority": "static"
    },
    "/thank-you/": {
        "title": "Thank You | Iowa Gutter Guards",
        "description": "Thank you for contacting Iowa Gutter Guards. We'll be in touch soon!",
        "og_image": "/assets/images/og-default.jpg",
        "priority": "utility"
    }
}

# Cities list for service area pages
CITIES = [
    "adel", "altoona", "ames", "ankeny", "baxter", "belle-plaine", "bondurant", "boone",
    "carlisle", "chariton", "clive", "colfax", "corydon", "dallas-center", "des-moines",
    "earlham", "eldora", "greenfield", "grimes", "grinnell", "huxley", "indianola",
    "jefferson", "johnston", "knoxville", "lynnville", "madrid", "marshalltown",
    "melbourne", "monroe", "nevada", "newton", "norwalk", "osceola", "oskaloosa",
    "pella", "perry", "pleasant-hill", "polk-city", "prairie-city", "redfield",
    "slater", "story-city", "stuart", "sully", "urbandale", "van-meter", "waukee",
    "west-des-moines", "winterset"
]

def get_city_name(slug):
    """Convert slug to proper city name."""
    return slug.replace("-", " ").title()

def get_page_path_from_file(filepath):
    """Get the URL path from a file path."""
    base_dir = Path("/home/ubuntu/iowa_gutter_guards_improved")
    rel_path = Path(filepath).relative_to(base_dir)
    
    if str(rel_path) == "index.html":
        return "/"
    
    # Remove index.html from path
    path_str = str(rel_path)
    if path_str.endswith("/index.html"):
        return "/" + path_str.replace("/index.html", "/")
    
    return "/" + path_str.replace(".html", "/")

def get_css_path(filepath):
    """Get the correct relative path to CSS based on file location."""
    base_dir = Path("/home/ubuntu/iowa_gutter_guards_improved")
    rel_path = Path(filepath).relative_to(base_dir)
    
    # Count directory depth
    depth = len(rel_path.parts) - 1  # -1 for the filename
    
    if depth == 0:
        return "assets/css/styles.min.css"
    else:
        return "../" * depth + "assets/css/styles.min.css"

def get_js_path(filepath):
    """Get the correct relative path to JS based on file location."""
    base_dir = Path("/home/ubuntu/iowa_gutter_guards_improved")
    rel_path = Path(filepath).relative_to(base_dir)
    
    depth = len(rel_path.parts) - 1
    
    if depth == 0:
        return "assets/js/tracking.js"
    else:
        return "../" * depth + "assets/js/tracking.js"

def get_favicon_path(filepath, filename):
    """Get the correct relative path to favicon based on file location."""
    base_dir = Path("/home/ubuntu/iowa_gutter_guards_improved")
    rel_path = Path(filepath).relative_to(base_dir)
    
    depth = len(rel_path.parts) - 1
    
    if depth == 0:
        return filename
    else:
        return "../" * depth + filename

def generate_favicon_links(filepath):
    """Generate favicon link tags."""
    return f'''
  <!-- Favicons -->
  <link rel="icon" href="{get_favicon_path(filepath, 'favicon.ico')}" sizes="any">
  <link rel="icon" href="{get_favicon_path(filepath, 'favicon.svg')}" type="image/svg+xml">
  <link rel="icon" type="image/png" sizes="16x16" href="{get_favicon_path(filepath, 'favicon-16x16.png')}">
  <link rel="icon" type="image/png" sizes="32x32" href="{get_favicon_path(filepath, 'favicon-32x32.png')}">
  <link rel="icon" type="image/png" sizes="48x48" href="{get_favicon_path(filepath, 'favicon-48x48.png')}">
  <link rel="icon" type="image/png" sizes="192x192" href="{get_favicon_path(filepath, 'favicon-192x192.png')}">
  <link rel="apple-touch-icon" sizes="180x180" href="{get_favicon_path(filepath, 'apple-touch-icon.png')}">'''

def generate_og_meta(filepath, title, description):
    """Generate Open Graph meta tags."""
    page_path = get_page_path_from_file(filepath)
    canonical_url = BASE_URL + page_path
    og_image = BASE_URL + "/assets/images/og-default.jpg"
    
    return f'''
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:site_name" content="Iowa Gutter Guards">
  <meta property="og:locale" content="en_US">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{canonical_url}">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{og_image}">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="{canonical_url}">'''

def generate_ga_tracking():
    """Generate Google Analytics 4 tracking code."""
    return f'''
  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>'''

def generate_sticky_phone_css():
    """Generate CSS for sticky phone bar."""
    return '''
  /* Sticky Phone Bar for Mobile */
  .sticky-phone {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    padding: 0.85rem 1rem;
    z-index: 9999;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
  }
  .sticky-phone a {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    color: white;
    font-weight: 700;
    font-size: 1.15rem;
    text-decoration: none;
  }
  .sticky-phone svg {
    width: 24px;
    height: 24px;
    animation: phone-ring 1.5s ease-in-out infinite;
  }
  @keyframes phone-ring {
    0%, 100% { transform: rotate(0); }
    10%, 30% { transform: rotate(-10deg); }
    20%, 40% { transform: rotate(10deg); }
    50% { transform: rotate(0); }
  }
  @media (max-width: 768px) {
    .sticky-phone { display: block; }
    body { padding-bottom: 60px; }
  }'''

def generate_sticky_phone_html():
    """Generate HTML for sticky phone bar."""
    return f'''
<!-- Sticky Phone Bar (Mobile) -->
<div class="sticky-phone" onclick="gtag('event', 'phone_click', {{'event_category': 'engagement', 'event_label': 'sticky_bar'}});">
  <a href="{PHONE_LINK}" data-track="phone-click">
    <svg xmlns="https://uxwing.com/wp-content/themes/uxwing/download/communication-chat-call/phone-outline-icon.svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
    </svg>
    <span>Call Now: {PHONE_NUMBER}</span>
  </a>
</div>'''

def generate_trust_badges_section():
    """Generate trust badges HTML section."""
    return '''
<!-- Trust Badges Section -->
<section class="trust-badges-section">
  <div class="trust-badges-grid">
    <div class="trust-badge-item">
      <div class="trust-badge-icon">🏆</div>
      <div class="trust-badge-text">
        <strong>10+ Years</strong>
        <span>Serving Iowa</span>
      </div>
    </div>
    <div class="trust-badge-item">
      <div class="trust-badge-icon">🏠</div>
      <div class="trust-badge-text">
        <strong>1,000+</strong>
        <span>Homes Protected</span>
      </div>
    </div>
    <div class="trust-badge-item">
      <div class="trust-badge-icon">⭐</div>
      <div class="trust-badge-text">
        <strong>4.9/5 Rating</strong>
        <span>Customer Reviews</span>
      </div>
    </div>
    <div class="trust-badge-item">
      <div class="trust-badge-icon">✅</div>
      <div class="trust-badge-text">
        <strong>Lifetime</strong>
        <span>Transferable Warranty</span>
      </div>
    </div>
  </div>
</section>'''

def generate_trust_badges_css():
    """Generate CSS for trust badges."""
    return '''
  /* Trust Badges Section */
  .trust-badges-section {
    padding: 1.5rem 0;
    margin: 1.5rem 0;
    border-top: 1px solid rgba(148, 163, 184, 0.3);
    border-bottom: 1px solid rgba(148, 163, 184, 0.3);
  }
  .trust-badges-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    text-align: center;
  }
  .trust-badge-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .trust-badge-icon {
    font-size: 2rem;
  }
  .trust-badge-text {
    display: flex;
    flex-direction: column;
    line-height: 1.3;
  }
  .trust-badge-text strong {
    font-size: 1.1rem;
    color: #4ade80;
  }
  .trust-badge-text span {
    font-size: 0.8rem;
    color: var(--muted);
  }
  @media (max-width: 768px) {
    .trust-badges-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
    }
  }'''

def generate_exit_intent_popup():
    """Generate exit-intent popup placeholder."""
    return '''
<!-- Exit Intent Popup (Placeholder - Enable via JS) -->
<div id="exit-popup" class="exit-popup hidden" style="display:none;">
  <div class="exit-popup-overlay"></div>
  <div class="exit-popup-content">
    <button class="exit-popup-close" aria-label="Close">&times;</button>
    <h3>Wait! Don't leave yet...</h3>
    <p>Get a free gutter inspection and estimate before you go!</p>
    <a href="#estimate-form" class="btn-primary" onclick="closeExitPopup()">Get Free Estimate</a>
  </div>
</div>'''

def generate_exit_popup_css():
    """Generate CSS for exit-intent popup."""
    return '''
  /* Exit Intent Popup */
  .exit-popup {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .exit-popup.hidden { display: none !important; }
  .exit-popup-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
  }
  .exit-popup-content {
    position: relative;
    background: #0f172a;
    padding: 2rem;
    border-radius: 12px;
    max-width: 400px;
    text-align: center;
    border: 1px solid rgba(148, 163, 184, 0.4);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  }
  .exit-popup-close {
    position: absolute;
    top: 10px;
    right: 15px;
    background: none;
    border: none;
    color: var(--muted);
    font-size: 1.5rem;
    cursor: pointer;
  }
  .exit-popup h3 {
    color: var(--accent);
    margin-bottom: 0.75rem;
  }
  .exit-popup p {
    color: var(--muted);
    margin-bottom: 1.25rem;
  }'''

def generate_why_choose_us_section():
    """Generate Why Choose Us section for homepage."""
    return '''
<!-- Why Choose Us Section -->
<section class="why-choose-section" id="why-choose-us">
  <h2>Why Choose Iowa Gutter Guards?</h2>
  <div class="why-choose-grid">
    <div class="why-choose-item">
      <div class="why-choose-icon">🔧</div>
      <h3>Expert Installation</h3>
      <p>Our trained professionals ensure precise installation that lasts, backed by years of Iowa-specific experience.</p>
    </div>
    <div class="why-choose-item">
      <div class="why-choose-icon">🌧️</div>
      <h3>Iowa Weather Ready</h3>
      <p>Our micro-mesh guards are designed to handle Iowa's heavy rains, snow, ice, and debris from maple helicopters.</p>
    </div>
    <div class="why-choose-item">
      <div class="why-choose-icon">💰</div>
      <h3>Transparent Pricing</h3>
      <p>No hidden fees or surprise charges. Get a clear, written estimate before any work begins.</p>
    </div>
    <div class="why-choose-item">
      <div class="why-choose-icon">🛡️</div>
      <h3>Lifetime Warranty</h3>
      <p>Our transferable lifetime warranty gives you peace of mind and adds value to your home.</p>
    </div>
  </div>
</section>'''

def generate_why_choose_css():
    """Generate CSS for Why Choose Us section."""
    return '''
  /* Why Choose Us Section */
  .why-choose-section {
    padding: 2.5rem 0;
    margin: 2rem 0;
  }
  .why-choose-section h2 {
    text-align: center;
    font-size: 1.8rem;
    margin-bottom: 2rem;
    color: var(--accent);
  }
  .why-choose-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
  }
  .why-choose-item {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .why-choose-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  }
  .why-choose-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }
  .why-choose-item h3 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    color: #4ade80;
  }
  .why-choose-item p {
    font-size: 0.9rem;
    color: var(--muted);
    line-height: 1.5;
  }
  @media (max-width: 900px) {
    .why-choose-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 600px) {
    .why-choose-grid { grid-template-columns: 1fr; }
  }'''

def generate_before_after_section():
    """Generate before/after image placeholders section."""
    return '''
<!-- Before/After Section -->
<section class="before-after-section">
  <h2>See the Difference</h2>
  <div class="before-after-grid">
    <div class="before-after-item">
      <div class="before-after-label">Before</div>
      <div class="before-after-placeholder" style="background: linear-gradient(45deg, #1e293b 25%, #334155 25%, #334155 50%, #1e293b 50%, #1e293b 75%, #334155 75%); background-size: 20px 20px; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: var(--radius);">
        <span style="color: var(--muted);">Clogged Gutters Image</span>
      </div>
    </div>
    <div class="before-after-item">
      <div class="before-after-label after">After</div>
      <div class="before-after-placeholder" style="background: linear-gradient(45deg, #1e293b 25%, #334155 25%, #334155 50%, #1e293b 50%, #1e293b 75%, #334155 75%); background-size: 20px 20px; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: var(--radius);">
        <span style="color: var(--muted);">Protected Gutters Image</span>
      </div>
    </div>
  </div>
</section>'''

def generate_before_after_css():
    """Generate CSS for before/after section."""
    return '''
  /* Before/After Section */
  .before-after-section {
    padding: 2rem 0;
    margin: 2rem 0;
  }
  .before-after-section h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: var(--accent);
  }
  .before-after-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  .before-after-item {
    position: relative;
  }
  .before-after-label {
    position: absolute;
    top: 10px;
    left: 10px;
    background: #dc2626;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    z-index: 1;
  }
  .before-after-label.after {
    background: #16a34a;
  }
  @media (max-width: 600px) {
    .before-after-grid { grid-template-columns: 1fr; }
  }'''

def extract_title_description(content):
    """Extract title and description from HTML content."""
    title_match = re.search(r'<title>([^<]+)</title>', content)
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    
    title = title_match.group(1) if title_match else "Iowa Gutter Guards"
    description = desc_match.group(1) if desc_match else "Professional gutter guard installation in Central Iowa."
    
    return title, description

def add_lazy_loading(content):
    """Add lazy loading to images."""
    # Add loading="lazy" to img tags that don't have it
    content = re.sub(
        r'<img(?![^>]*loading=)([^>]*?)(/?)>',
        r'<img\1 loading="lazy"\2>',
        content
    )
    return content

def enhance_cta_buttons(content):
    """Enhance CTA button text and add tracking."""
    # Make primary CTA more compelling
    content = re.sub(
        r'(class="btn-primary[^"]*"[^>]*>)([^<]*Get[^<]*estimate[^<]*)(</)',
        r'\1🎯 Get Your FREE Estimate Now\3',
        content,
        flags=re.IGNORECASE
    )
    return content

def add_tracking_attributes(content):
    """Add tracking attributes to clickable elements."""
    # Add tracking to phone links
    content = re.sub(
        r'(<a[^>]*href="tel:[^"]*"[^>]*)>',
        r'\1 data-track="phone-click" onclick="gtag(\'event\', \'phone_click\', {\'event_category\': \'engagement\'});">',
        content
    )
    return content

def process_html_file(filepath):
    """Process a single HTML file with all enhancements."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title, description = extract_title_description(content)
    
    # Remove existing inline CSS (between <style> and </style>)
    # Keep the content but replace with external CSS link
    style_pattern = r'<style>.*?</style>'
    inline_style_match = re.search(style_pattern, content, re.DOTALL)
    
    if inline_style_match:
        # Remove inline styles
        content = re.sub(style_pattern, '', content, flags=re.DOTALL)
    
    # Build the enhanced head section
    css_path = get_css_path(filepath)
    js_path = get_js_path(filepath)
    
    enhanced_head = f'''
  <!-- External Stylesheet -->
  <link rel="stylesheet" href="{css_path}">
{generate_favicon_links(filepath)}
{generate_og_meta(filepath, title, description)}
{generate_ga_tracking()}
  
  <!-- Event Tracking -->
  <script src="{js_path}" defer></script>'''
    
    # Add enhanced head content after viewport meta
    content = re.sub(
        r'(<meta name="viewport"[^>]*>)',
        r'\1' + enhanced_head,
        content,
        count=1
    )
    
    # Add additional CSS for enhanced features (inline for now, critical CSS)
    enhanced_css = f'''
  <style>
{generate_sticky_phone_css()}
{generate_trust_badges_css()}
{generate_exit_popup_css()}
{generate_why_choose_css()}
{generate_before_after_css()}
  </style>'''
    
    # Add before </head>
    content = content.replace('</head>', enhanced_css + '\n</head>')
    
    # Add sticky phone bar before </body>
    content = content.replace('</body>', generate_sticky_phone_html() + '\n</body>')
    
    # Add exit intent popup placeholder
    content = content.replace('</body>', generate_exit_intent_popup() + '\n</body>')
    
    # Add lazy loading to images
    content = add_lazy_loading(content)
    
    # Add tracking attributes
    content = add_tracking_attributes(content)
    
    # For homepage, add trust badges and why choose us sections
    page_path = get_page_path_from_file(filepath)
    if page_path == "/":
        # Add trust badges after hero section
        hero_end = content.find('</section>', content.find('class="hero"'))
        if hero_end > 0:
            content = content[:hero_end+10] + generate_trust_badges_section() + content[hero_end+10:]
        
        # Add Why Choose Us section (find a good spot)
        faq_section = content.find('id="faq"')
        if faq_section > 0:
            section_start = content.rfind('<section', 0, faq_section)
            if section_start > 0:
                content = content[:section_start] + generate_why_choose_us_section() + '\n' + content[section_start:]
    
    # Write the enhanced file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Enhanced: {filepath}")

def main():
    """Main function to process all HTML files."""
    base_dir = Path("/home/ubuntu/iowa_gutter_guards_improved")
    
    # Find all HTML files
    html_files = list(base_dir.glob("**/*.html"))
    
    # Exclude template and backup files
    html_files = [f for f in html_files if 
                  "city-template" not in str(f) and 
                  ".bak" not in str(f) and
                  "audit" not in str(f)]
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    for filepath in html_files:
        try:
            process_html_file(str(filepath))
        except Exception as e:
            print(f"  ✗ Error processing {filepath}: {e}")
    
    print(f"\n✓ Completed processing {len(html_files)} files")

if __name__ == "__main__":
    main()
