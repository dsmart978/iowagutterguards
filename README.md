# Iowa Gutter Guards - Enhanced Website

A static website for Iowa Gutter Guards, built for Cloudflare Pages hosting with comprehensive SEO, analytics, and conversion optimization enhancements.

## 📁 Project Structure

```
iowa_gutter_guards_improved/
├── index.html                    # Homepage
├── assets/
│   ├── css/
│   │   ├── styles.css           # Main stylesheet (source)
│   │   └── styles.min.css       # Minified CSS (production)
│   ├── js/
│   │   └── tracking.js          # GA4 event tracking
│   └── images/                   # Image assets
├── service-areas/                # 50 city-specific landing pages
│   ├── des-moines-ia/
│   ├── ankeny-ia/
│   ├── west-des-moines-ia/
│   └── ... (47 more cities)
├── functions/
│   └── api/
│       └── lead.js              # Cloudflare Functions form handler
├── customer-service/             # Customer service page
├── warranty/                     # Warranty information
├── privacy-policy/               # Privacy policy
├── terms-of-service/             # Terms of service
├── thank-you/                    # Form submission thank you page
├── favicon.ico                   # Favicon (ICO format)
├── favicon.svg                   # SVG favicon
├── favicon-*.png                 # Various PNG favicon sizes
├── apple-touch-icon.png          # Apple touch icon
├── sitemap.xml                   # XML sitemap (58 pages)
├── robots.txt                    # Robots.txt with crawl rules
├── tools/                        # Build and enhancement scripts
│   └── enhance_all_pages.py     # Main enhancement script
├── generate_city_pages.py        # City page generator
├── city-template.html            # Template for city pages
└── generate_site.py              # Site generator
```

## 🚀 Deployment

### Cloudflare Pages Deployment

1. **Connect Repository**
   - Go to Cloudflare Dashboard → Pages
   - Connect your GitHub repository

2. **Build Settings**
   - Build command: (leave empty - static site)
   - Build output directory: `/`
   - Root directory: `/`

3. **Environment Variables**
   Set these in Cloudflare Pages → Settings → Environment Variables:
   ```
   RESEND_API_KEY=your_resend_api_key
   LEAD_TO=your_email@example.com
   LEAD_FROM=noreply@yourdomain.com
   ```

4. **Deploy**
   - Push to main branch to trigger deployment
   - Or use Cloudflare Wrangler CLI:
   ```bash
   npx wrangler pages deploy . --project-name=iowa-gutter-guards
   ```

### Google Analytics 4 (Optional)

**NOTE:** Google Analytics does NOT help SEO rankings. It's a tracking tool to see which marketing generates calls.

The GA4 code is **commented out by default**. To enable:

1. Go to [analytics.google.com](https://analytics.google.com) and create a GA4 property
2. Get your Measurement ID (looks like `G-XXXXXXXXXX`)
3. Find and replace in all files:
   ```bash
   # Uncomment GA4 code and replace placeholder ID
   find . -name "*.html" -exec sed -i 's/<!--\s*<script async src.*gtag/js/g' {} +
   find . -name "*.html" -exec sed -i 's/G-XXXXXXXXXX/G-YOUR-ID/g' {} +
   ```

**See [ANALYTICS_GUIDE.md](ANALYTICS_GUIDE.md) for detailed guidance on whether you need analytics.**

### Bing Webmaster Tools Setup

Bing verification is already added to all pages. To complete setup:

1. **Sign in to Bing Webmaster Tools**
   - Go to [bing.com/webmasters](https://www.bing.com/webmasters)
   - Sign in with Microsoft account

2. **Add Your Site**
   - Click "Add Site"
   - Enter `https://www.iowagutterguards.com`

3. **Verify Ownership**
   - The meta tag is already in all pages: `<meta name="msvalidate.01" content="de33b1b0324d427cbf3df33ce570686b" />`
   - Click "Verify" - it should work immediately after deployment

4. **Submit Sitemap**
   - Go to Sitemaps section
   - Submit: `https://www.iowagutterguards.com/sitemap.xml`

**Why Bing matters:** Bing powers ~30% of US searches (including Yahoo and DuckDuckGo). It's free SEO exposure.

### Call Tracking (If You Want to Track Which Marketing Generates Calls)

**The Real Question:** "Which ads/marketing efforts make my phone ring?"

Google Analytics can tell you website behavior but not which actual phone calls came from where. For that, you need call tracking:

#### Option 1: Free (Basic)
- Google Analytics tracks phone *clicks* on your website
- You'll know someone clicked to call, but not if they actually called or booked

#### Option 2: CallRail (~$45/month)
- Gives you different phone numbers for different traffic sources
- Tracks actual calls, not just clicks
- Records calls (for training)
- Shows which ads/pages generate actual calls
- [callrail.com](https://www.callrail.com)

#### Option 3: WhatConverts (~$30/month)
- Similar to CallRail
- Good for tracking form submissions + calls together
- [whatconverts.com](https://www.whatconverts.com)

**Recommendation:** If you're spending money on ads (Google Ads, Facebook, etc.), call tracking is worth it. If you're just doing SEO and word-of-mouth, phone clicks from GA4 might be enough.

## ✅ Improvements Made

### Critical Fixes
- [x] **Form Redirect**: Fixed form handler to redirect to `/thank-you/` instead of `/thanks/`
- [x] **Sitemap**: Generated comprehensive `sitemap.xml` for all 58 pages
- [x] **Robots.txt**: Created with proper crawl rules and sitemap reference
- [x] **Favicon**: Created favicons in multiple sizes (16x16, 32x32, 48x48, 64x64, 128x128, 180x180, 192x192, 512x512)

### Analytics & Tracking
- [x] **GA4 Tracking**: Added Google Analytics 4 tracking code
- [x] **Event Tracking** for:
  - Form submissions (with lead value tracking)
  - Phone click tracking
  - CTA button click tracking
  - Scroll depth tracking (25%, 50%, 75%, 90%, 100%)
  - Time on page tracking (30s, 60s, 120s, 300s)
  - External link tracking
  - Form field interaction tracking

### Code Quality & Performance
- [x] **External CSS**: Extracted all duplicated CSS into `assets/css/styles.css`
- [x] **Minified CSS**: Created `assets/css/styles.min.css` for production
- [x] **All HTML Updated**: All 58 pages reference the external stylesheet
- [x] **Image Lazy Loading**: Added `loading="lazy"` attribute to images
- [x] **Correct Path References**: Fixed CSS/JS paths for all subdirectory pages

### SEO Enhancements
- [x] **Open Graph Tags**: Added to all pages (og:title, og:description, og:image, og:url, og:type)
- [x] **Twitter Cards**: Added Twitter Card meta tags
- [x] **Canonical URLs**: Added to all pages
- [x] **Descriptive Alt Text**: Ensured all images have alt text

### Conversion Optimization
- [x] **Sticky Phone Bar**: Mobile-only sticky call button at bottom of screen
- [x] **Enhanced CTA Buttons**: Larger, more prominent with better copy
- [x] **Trust Badges Section**: Years in business, homes served, rating, warranty highlight
- [x] **Social Proof**: Rating display and review count
- [x] **Exit-Intent Popup**: Placeholder ready to be enabled via JS
- [x] **Improved Mobile Forms**: Better spacing and larger touch targets

### Content Enhancements
- [x] **Why Choose Us Section**: Key differentiators on homepage
- [x] **Before/After Placeholders**: Ready for real images
- [x] **Prominent Warranty Info**: Highlighted throughout site
- [x] **Social Proof Elements**: Review count and rating display

## 📝 Python Build Scripts

### Generate City Pages
```bash
python generate_city_pages.py
```
Generates 50 city-specific landing pages from `city-template.html`.

### Enhance All Pages
```bash
python tools/enhance_all_pages.py
```
Applies all enhancements to existing HTML files (CSS extraction, OG tags, tracking, etc.).

## 🔧 Configuration

### Update GA4 Measurement ID
Replace `G-XXXXXXXXXX` in:
1. All HTML files
2. `assets/js/tracking.js`

### Update Phone Number
Current: `(515) 329-5128` / `tel:+15153295128`

To change, update in:
- All HTML files
- `tracking.js`
- `city-template.html`

### Update Base URL
Current: `https://www.iowagutterguards.com`

To change, update in:
- `sitemap.xml`
- `robots.txt`
- All HTML files (canonical URLs, OG tags)

## 📊 Tracking Events Reference

| Event Name | Category | When Fired |
|------------|----------|------------|
| `phone_click` | contact | Phone link clicked |
| `cta_click` | engagement | CTA button clicked |
| `form_submit` | conversion | Form submitted |
| `generate_lead` | conversion | Form submitted (conversion value) |
| `scroll_depth` | engagement | Scroll threshold reached |
| `time_on_page` | engagement | Time threshold reached |
| `outbound_link` | engagement | External link clicked |
| `form_start` | engagement | Form field first focused |

## 🎨 Design System

### Colors
```css
--primary: #0f766e;      /* Teal */
--primary-dark: #115e59; /* Dark Teal */
--accent: #eab308;       /* Yellow/Gold */
--cta: #f97316;          /* Orange */
--cta-dark: #ea580c;     /* Dark Orange */
--bg: #0b1120;           /* Dark Blue */
--light: #f9fafb;        /* Off White */
--muted: #6b7280;        /* Gray */
```

### Fonts
- System fonts: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

## 🔒 Security Features

- Honeypot field in forms (prevents spam)
- Form validation (requires name + email or phone)
- No sensitive data exposure in tracking

## 📱 Mobile Optimization

- Responsive design (breakpoints at 900px, 768px, 600px)
- Sticky phone bar on mobile devices
- Touch-friendly form inputs
- Optimized tap targets

## 🧪 Testing Checklist

Before deployment:
- [ ] Verify all 58 pages load correctly
- [ ] Test form submission and redirect
- [ ] Verify GA4 tracking fires correctly
- [ ] Test phone links on mobile
- [ ] Check all favicon sizes display
- [ ] Validate sitemap.xml
- [ ] Test robots.txt with Google Search Console
- [ ] Mobile responsiveness on various devices
- [ ] Check all internal links

## 📄 License

All rights reserved © 2025 Iowa Gutter Guards

## 📞 Support

For technical questions about this website, contact the development team.

---

*Last updated: February 2026*
