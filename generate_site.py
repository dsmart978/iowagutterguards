import os

# -----------------------------
# SETTINGS
# -----------------------------

OUTPUT_DIR = "."

LEGAL_PAGES = {
    "privacy-policy": {
        "title": "Privacy Policy | Iowa Gutter Guards",
        "content": """
<h1>Privacy Policy</h1>
<p>Last updated: 2025</p>

<p>Iowa Gutter Guards (“we,” “us,” or “our”) respects your privacy. This privacy policy explains how we collect, use, and protect your information when you use our website or request an estimate.</p>

<h2>Information We Collect</h2>
<ul>
<li>Name, address, phone number, email address</li>
<li>Details about your home, gutters, roof, and debris type</li>
<li>Photos you text or email us</li>
</ul>

<h2>How We Use Your Information</h2>
<ul>
<li>To provide estimates and communicate about your project</li>
<li>To send SMS updates related to scheduling (with your consent)</li>
<li>To improve our services and customer experience</li>
<li>To share relevant information with our affiliated companies (Central Iowa Gutter, Smart Home Exteriors, Smart Home Services) when the services are directly related</li>
</ul>

<h2>Information Sharing</h2>
<p>We do not sell your information. We share your data only with affiliated companies when the services are related to your inquiry.</p>

<h2>Contact Us</h2>
<p>Email: info@iowagutterguards.online<br>
Phone: (515) 329-5128</p>
"""
    },

    "terms-of-service": {
        "title": "Terms of Service | Iowa Gutter Guards",
        "content": """
<h1>Terms of Service</h1>

<p>By using this website or submitting a request for an estimate, you agree to the terms below.</p>

<h2>Website Use</h2>
<p>Our website provides general information about gutter guard installation and related services. Final pricing and scope of work may change after evaluating your home.</p>

<h2>Texts & Communication</h2>
<p>By checking the SMS consent box on the estimate form, you authorize us to contact you via text for scheduling and project-related updates.</p>

<h2>Intellectual Property</h2>
<p>All content on this website is owned by Iowa Gutter Guards and may not be copied without permission.</p>

<h2>Contact</h2>
<p>Email: info@iowagutterguards.online</p>
"""
    },

    "warranty": {
        "title": "Workmanship Warranty | Iowa Gutter Guards",
        "content": """
<h1>2-Year Workmanship Warranty</h1>

<p>Your installation is backed by a 2-year workmanship warranty beginning on the date of final payment.</p>

<h2>What’s Covered</h2>
<ul>
<li>Improper fastening</li>
<li>Alignment or slope issues caused by our installation</li>
<li>Defects in installation technique</li>
</ul>

<h2>Not Covered</h2>
<ul>
<li>Storm damage or wind damage</li>
<li>Ice dams</li>
<li>Gutter or fascia rot</li>
<li>Clogs caused by excessive debris sitting on top of the guards</li>
</ul>

<h2>Warranty Claims</h2>
<p>Email: info@iowagutterguards.online<br>
Phone: (515) 329-5128</p>
"""
    },

    "customer-service": {
        "title": "Customer Service | Iowa Gutter Guards",
        "content": """
<h1>Customer Service</h1>

<p>If you need help with scheduling, project updates, or general questions, contact us:</p>

<p>Email: info@iowagutterguards.online<br>
Phone: (515) 329-5128</p>
"""
    }
}

# 50-city master list (same as installed pages)
CITY_LIST = [
    "des-moines-ia","west-des-moines-ia","ankeny-ia","altoona-ia","urbandale-ia","clive-ia","johnston-ia","waukee-ia","grimes-ia",
    "pleasant-hill-ia","norwalk-ia","indianola-ia","carlisle-ia","bondurant-ia","adel-ia","dallas-center-ia","van-meter-ia","winterset-ia",
    "perry-ia","boone-ia","ames-ia","nevada-ia","huxley-ia","story-city-ia","marshalltown-ia","newton-ia","colfax-ia","prairie-city-ia",
    "monroe-ia","pella-ia","oskaloosa-ia","grinnell-ia","knoxville-ia","chariton-ia","madrid-ia","polk-city-ia","slater-ia","melbourne-ia",
    "baxter-ia","sully-ia","lynnville-ia","earlham-ia","redfield-ia","stuart-ia","greenfield-ia"
]

# Template for all city pages
CITY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{city_title} | Gutter Guards</title>
<meta name="description" content="Professional gutter guard installation in {city_title}. Micro-mesh guards, gutter cleaning, tune-ups, and debris protection throughout Central Iowa." />
<link rel="stylesheet" href="/styles.css" />
</head>
<body>

<div class="page">
<header>
  <div class="logo">
    <div class="logo-mark">I G G</div>
    <div class="logo-text">
      <span class="logo-primary">Iowa</span>
      <span class="logo-primary">Gutter</span>
      <span class="logo-secondary">Guards</span>
    </div>
  </div>

  <nav class="main-nav">
    <a href="/">Home</a>
    <a href="/#guard-system">Our Guard System</a>
    <a href="/#process">Process</a>
    <a href="/#service-areas">Service Areas</a>
    <a href="/#reviews">Reviews</a>
    <a href="/#faq">FAQ</a>
    <a href="/#contact">Contact</a>
  </nav>
</header>

<section class="section">
<h1>Gutter Guards in {city_title}</h1>
<p>If you live in {city_title} or nearby communities, Iowa Gutter Guards provides professional gutter cleaning, gutter guard installation, and full gutter tune-ups designed for Iowa weather.</p>

<h2>Why homeowners in {city_title} choose us</h2>
<ul>
<li>Stainless steel micro-mesh guards</li>
<li>Full gutter cleaning included</li>
<li>Downspout flow testing</li>
<li>Low-profile installation</li>
<li>No high-pressure sales tactics</li>
</ul>

<h2>What nearby homeowners say</h2>
<p><strong>“The guards have worked perfectly and no more overflowing gutters.” — Homeowner near {city_title}</strong></p>

<p><a href="/#estimate-form" class="btn-primary">Request Your Estimate</a></p>
</section>

<footer>
<p><strong>Iowa Gutter Guards</strong> — Serving Central Iowa</p>
<p>
<a href="/privacy-policy/">Privacy Policy</a> &middot;
<a href="/terms-of-service/">Terms of Service</a> &middot;
<a href="/warranty/">Warranty</a> &middot;
<a href="/customer-service/">Customer Service</a>
</p>
</footer>

</div>
</body>
</html>
"""

# -----------------------------
# GENERATE LEGAL PAGES
# -----------------------------

def generate_legal_pages():
    for folder, data in LEGAL_PAGES.items():
        path = os.path.join(OUTPUT_DIR, folder)
        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, "index.html"), "w", encoding="utf8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{data['title']}</title>
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="page">
{data['content']}
<footer>
<p><a href="/privacy-policy/">Privacy Policy</a> &middot;
<a href="/terms-of-service/">Terms of Service</a> &middot;
<a href="/warranty/">Warranty</a> &middot;
<a href="/customer-service/">Customer Service</a></p>
</footer>
</div>
</body>
</html>
""")

    print("✔ Legal pages created.")


# -----------------------------
# GENERATE CITY PAGES
# -----------------------------

def generate_city_pages():
    base_path = os.path.join(OUTPUT_DIR, "service-areas")
    os.makedirs(base_path, exist_ok=True)

    for slug in CITY_LIST:
        city_title = slug.replace("-", " ").replace(" ia", ", IA").title()

        city_path = os.path.join(base_path, slug)
        os.makedirs(city_path, exist_ok=True)

        with open(os.path.join(city_path, "index.html"), "w", encoding="utf8") as f:
            f.write(CITY_TEMPLATE.format(city_title=city_title))

    print("✔ City pages created.")


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    generate_legal_pages()
    generate_city_pages()
    print("\n🎉 All pages have been generated uniformly.")
