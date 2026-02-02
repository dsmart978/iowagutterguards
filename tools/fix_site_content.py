#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import html as htmlmod

SITE_ROOT = Path(__file__).resolve().parents[1]

# Exact marker sentence you said you want removed (it lives inside a section on each city page).
REPETITIVE_CITY_MARKER = (
    "premium gutter guard systems designed to stop clogs, reduce overflow, and keep water moving where it belongs"
)

# Hard requirement: one unique paragraph per city page folder in this repo.
# NOTE: Keys MUST match folder names under /service-areas/*-ia
CITY_PARAGRAPHS: dict[str, str] = {
    "adel-ia": "Adel homes deal with heavy spring rain, falling leaves, and long winters that make gutters clog at the worst time. We start by clearing the system and confirming the gutters are pitched correctly so water actually moves to the downspouts. Then we install guards with tight edge alignment to keep leaves and roof grit from packing into the trough. Corners and outlets are secured carefully because that is where backups usually start. The goal is simple: fewer cleanouts and less overflow along fascia and landscaping.",
    "altoona-ia": "In Altoona, gutter issues tend to show up fast during big storms and the freeze-thaw stretch when small clogs turn into ice problems. We clean the gutters, verify downspouts are flowing, and correct any loose hangers before installing guards. The guards are fitted to match the roof edge so water enters while debris is directed away. We pay extra attention to high-flow spots like valleys and inside corners. You end up with a system that stays calmer through leaf season and heavy rain.",
    "ames-ia": "Ames has a lot of mature trees and plenty of seasonal weather swings, which is a perfect recipe for clogged gutters. We prep the job by removing debris and confirming the gutter line drains the way it should. Then we install guards that sit tight along the roofline so leaves do not wedge under the edge. Transitions, seams, and corners are fastened consistently so the system does not lift over time. The result is less overflow and less time thinking about gutters at all.",
    "ankeny-ia": "Ankeny homes see rapid growth, new landscaping, and the same old Midwest storms that expose weak gutter flow. We start with a full clean-out and a quick inspection to catch sagging, leaky seams, or clogged outlets that would undermine any guard. Then we install gutter guards with secure attachment across long runs so they stay put in wind and heavy water flow. Problem areas like corners and downspout openings are reinforced to prevent backups. You get a cleaner look and a more dependable drainage path off the roof.",
    "baxter-ia": "Baxter properties often get a mix of open wind exposure and debris that collects where rooflines meet valleys. We clear the gutters and confirm the downspouts are not restricted so water has a real exit. Then we install guards with consistent overlap and fastening, especially at seams and corners. We also check for small issues like loose spikes or hangers that can cause overflow even with guards. The end result is better flow and less maintenance through storm season.",
    "belle-plaine-ia": "Belle Plaine’s weather can be hard on gutters, especially when wind-driven debris and sudden downpours hit together. We clean the gutter runs, verify slope, and make sure outlets are clear before installing guards. The guards are fitted to the roof edge so they do not leave easy gaps for leaves or shingle grit. Inside corners and transitions are secured carefully because that is where clogs typically begin. You get a gutter system that sheds water more reliably and stays cleaner longer.",
    "bondurant-ia": "Bondurant has plenty of new builds and older homes, and both can suffer from the same problem: water overflow caused by clogged or poorly draining gutters. We remove debris, confirm the gutter line is pitched correctly, and check downspout flow first. Then we install guards that sit tight along the roof edge and are fastened evenly so they do not lift. Corners, valleys, and outlet points are handled with extra care because that is where backups start. The goal is a system that keeps water moving without constant cleanouts.",
    "boone-ia": "Boone homeowners know that one bad clog can send water straight over the edge and into fascia, siding, or landscaping. We start by cleaning the gutter system and verifying the downspouts are actually carrying water away. Then we install gutter guards with secure attachment that resists shifting in wind and heavy rain. Seams and corners get a careful fit so debris does not sneak in where the flow is strongest. The result is less overflow risk and fewer seasonal surprises.",
    "carlisle-ia": "Carlisle roofs and gutter lines take a beating through storms, leaf season, and winter buildup. We prep by clearing debris and checking for sagging or loose hangers that can create standing water. Then we install gutter guards that align closely with the roof edge so water enters cleanly while debris is blocked. We reinforce corners and outlets because that is where clogs become overflow. You get a more dependable drainage system with far less maintenance.",
    "chariton-ia": "Chariton properties often face heavy rain and seasonal debris that can pack into gutters and choke downspouts. We clean the gutter runs, verify proper pitch, and make sure outlet openings are not restricted. Then we install guards that are secured across seams and transitions so they stay flush and consistent. Valleys and corners are addressed carefully because that is where high-volume runoff concentrates. The goal is fewer cleanouts and a cleaner path for water off the roof.",
    "clive-ia": "Clive homes deal with debris from mature trees and the kind of storms that punish clogged gutters immediately. We start by clearing the system and confirming water flows to the downspouts without pooling. Then we install guards fitted to the roof edge and gutter profile so leaves and shingle grit do not accumulate in the trough. Fastening is done consistently across long runs and corners to prevent lifting. You get less overflow, less mess, and fewer ladder trips.",
    "colfax-ia": "Colfax weather and debris can turn gutters into a collection tray that overflows right where you do not want it. We clean the gutters, confirm downspouts are moving water, and fix obvious weak points like loose hangers or leaky seams. Then we install guards with tight alignment so debris is shed while water enters. Corners and outlet areas are secured carefully to prevent backups. The end result is a system that drains more reliably through storms and leaf season.",
    "corydon-ia": "Corydon homes can see clogs build up slowly, then fail all at once during a heavy rain or thaw. We start with a clean-out and verify the gutters are pitched correctly toward the downspouts. Then we install guards that sit flush along the roof edge to keep leaves and grit out of the trough. We pay close attention to seams and corners because small gaps cause big problems over time. You get steadier flow and less risk of overflow staining or rot.",
    "dallas-center-ia": "Dallas Center properties often face wind-driven debris and fast weather changes that make gutter maintenance a constant chore. We clean the system, check gutter alignment, and confirm downspouts are clear before installing guards. Then we install guards that lock down consistently across long runs so they do not lift in wind. Corners and outlets are handled carefully to prevent the most common backup points. The goal is simpler maintenance and fewer overflow events around the home.",
    "des-moines-ia": "Des Moines homes see everything: heavy rain, tree debris, roof grit, and winter ice that can turn clogged gutters into real damage. We start by clearing the gutters and verifying downspouts are flowing correctly, because guards do not fix bad drainage. Then we install gutter guards with a tight roofline fit so water enters while debris is kept out. High-flow areas like valleys and inside corners are reinforced so runoff does not overwhelm the system. You get a cleaner setup and better protection against overflow and water intrusion.",
    "earlham-ia": "Earlham homes often deal with debris that accumulates quickly and creates slow drains that are easy to miss until water spills over. We clean the gutters, confirm pitch, and check that downspout outlets are not restricted. Then we install guards with secure fastening and consistent overlaps to prevent gaps that collect debris. Corners and transitions are treated as priority points because that is where clogs begin. The end result is more predictable drainage and less seasonal maintenance.",
    "eldora-ia": "Eldora weather swings can turn a small clog into a big overflow problem, especially when thaw hits after snow and ice. We prep the system by clearing debris and checking for sagging sections that cause standing water. Then we install guards that are fitted to the roof edge so leaves and grit do not wedge into the gutter. Seams, corners, and outlet areas are secured to keep flow open where it matters most. You get better performance through storms and fewer gutter cleanouts.",
    "greenfield-ia": "Greenfield homes can see debris collect in gutters quietly, then fail during the first major downpour of the season. We start by cleaning the system and verifying the downspouts are not blocked or undersized for the runoff they handle. Then we install gutter guards that sit tight and remain stable across long runs. Corners and valleys get extra attention to keep water moving when volume is high. The outcome is less overflow and fewer maintenance headaches through the year.",
    "grimes-ia": "Grimes has plenty of fast-growing neighborhoods and the same Midwest storms that punish clogged gutters. We clean the gutters, confirm the downspouts drain properly, and address any loose hangers before installing guards. Then we fit guards to the roof edge so debris is deflected and water can enter consistently. Inside corners and outlet points are secured and checked for proper flow. You get a cleaner-looking gutter line that stays functional through leaf season and heavy rain.",
    "grinnell-ia": "Grinnell homes often deal with mature trees, seasonal debris, and strong rain events that quickly expose weak gutter flow. We begin with a full clean-out and verify the system is pitched correctly toward the downspouts. Then we install guards with consistent fastening so they stay flush and resist lifting. Corners and seam transitions are fitted carefully to reduce the most common clog points. The goal is fewer overflows and less time spent maintaining gutters.",
    "huxley-ia": "Huxley properties can see gutters clog from wind-driven debris and roof grit that accumulates at seams and corners. We clean the system, confirm slope, and make sure downspout outlets are clear before installing guards. Then we install guards that sit tight along the roof edge and remain stable across long runs. We focus on corners and outlets because that is where backups start and overflow becomes visible. You get a system that drains more consistently and needs far less attention.",
    "indianola-ia": "Indianola weather and tree debris can fill gutters quickly, especially around valleys and inside corners. We start by clearing debris, verifying downspout flow, and checking for sagging or leaky sections that would cause overflow even with guards installed. Then we fit gutter guards tightly to the roof edge so water can enter while debris is kept out. Transitions, seams, and corners are secured with care to prevent gaps. The result is better flow and less routine maintenance through the seasons.",
    "jefferson-ia": "Jefferson homes can see clogs form from leaves, small branches, and roof grit that settles in the gutter trough. We clean the system and confirm that downspouts are moving water away from the foundation. Then we install guards that keep debris out while maintaining water intake during heavy rain. We secure seams and corners to prevent the common failure point where debris sneaks in at transitions. You get fewer backups and a gutter system that behaves more predictably.",
    "johnston-ia": "Johnston properties often have mature trees and high-volume runoff during storms, which makes clogged gutters a fast problem. We begin by cleaning the gutters and verifying slope and downspout flow so water has a real exit. Then we install gutter guards with tight alignment and consistent fastening along the roof edge. Corners, seams, and outlet areas are handled carefully to avoid gaps that collect debris. You get reduced clogs, less overflow, and a cleaner gutter line.",
    "knoxville-ia": "Knoxville homes can see gutters clog from seasonal debris that piles up and blocks outlets right when storms hit. We start with a clean-out and confirm the system drains correctly to the downspouts. Then we install guards that fit the roof edge and are secured evenly across seams and corners. High-flow spots are reinforced so runoff does not overwhelm the gutter line. The end result is less overflow risk and less time spent cleaning gutters.",
    "lynnville-ia": "Lynnville properties often deal with wind, debris, and sudden storms that make clogged gutters show up at the worst moment. We clean the gutters and verify that downspouts are clear and draining away properly. Then we install gutter guards that sit flush to the roof edge and remain stable across long runs. We treat corners and seam transitions as priority points to prevent gaps from forming. You get steadier flow and fewer seasonal cleanouts.",
    "madrid-ia": "Madrid homes can see debris collect in gutters gradually, then overflow during a heavy rain when the system cannot drain fast enough. We start by clearing the gutter trough and confirming the downspouts are flowing. Then we install guards that align tightly with the roof edge so leaves and grit are shed instead of captured. Seams and corners get careful fastening to prevent small openings that become clog points. The result is a cleaner gutter system that drains more reliably.",
    "marshalltown-ia": "Marshalltown weather can be harsh on gutter systems, especially when debris and ice buildup combine to restrict flow. We clean the gutters, confirm pitch, and check outlets and downspouts for restrictions before installation. Then we install guards with secure fastening that keeps the surface stable through storms and seasonal shifts. Valleys, corners, and transitions are fitted carefully so high-volume runoff does not force debris underneath. You get better drainage performance and less maintenance over time.",
    "melbourne-ia": "Melbourne homes can see clogs form from leaves and roof grit that settle around seams and corners. We begin by cleaning the gutters and verifying water flow to the downspouts. Then we install guards that sit flush to the roof edge and remain secure across long runs. We focus on corners and outlet openings to prevent the most common backup points. The end result is fewer cleanouts and less overflow staining or rot risk.",
    "monroe-ia": "Monroe properties often face debris buildup that blocks gutters slowly, then causes overflow when storms arrive. We start by clearing the system, checking gutter pitch, and confirming downspouts are open. Then we install guards that fit tightly and are fastened consistently so they do not lift or shift. Corners and transitions are addressed carefully because those are the typical failure points. You get a gutter line that drains more predictably and stays cleaner longer.",
    "nevada-ia": "Nevada homes see the same Midwest pattern: debris in fall, heavy rain in spring, and ice risk in winter. We clean the gutters, verify proper slope, and confirm downspouts are draining correctly before installing guards. Then we fit guards to the roof edge so leaves and grit are blocked without starving water intake. Seams and corners are secured to reduce gaps that become clog points. The result is fewer backups and less maintenance through the year.",
    "newton-ia": "Newton properties can develop gutter problems when debris packs into the trough and blocks outlets, leading to overflow and staining. We start with a thorough clean-out and a quick inspection for sagging runs or leaky seams. Then we install gutter guards with consistent fastening and tight roofline alignment. High-flow areas like valleys and corners are handled carefully to keep water moving during storms. You get a system that stays functional with far less routine cleaning.",
    "norwalk-ia": "Norwalk homes often deal with fast storm runoff and debris that collects at corners and downspout outlets. We clean the system, verify pitch and drainage, and address loose hangers before installing any guard. Then we install guards that sit tight along the roof edge and remain stable across long runs. Corners and outlets are reinforced so backups do not start where flow is strongest. The goal is predictable drainage and fewer gutter cleanouts.",
    "osceola-ia": "Osceola weather can turn a clogged gutter into a water damage problem quickly, especially during heavy rain and thaw cycles. We clear the gutters and confirm the downspouts are open and carrying water away. Then we install guards that keep debris out while maintaining water intake across the full run. We secure seams and corners carefully to prevent gaps where debris can slip under. You get fewer overflows and less seasonal maintenance.",
    "oskaloosa-ia": "Oskaloosa homes can see gutter clogs form from leaves, grit, and small debris that collect around transitions and corners. We start by cleaning the gutter system and verifying drainage through the downspouts. Then we install gutter guards with tight alignment to the roof edge so debris is shed instead of captured. Corners and outlet areas get extra care because that is where backups are most common. The result is better flow and fewer cleanouts during the year.",
    "pella-ia": "Pella properties often have landscaping and rooflines where overflow can do real damage if gutters clog. We begin by clearing debris, confirming gutter pitch, and making sure downspouts are flowing correctly. Then we install guards that sit flush along the roof edge to block debris while allowing water to enter. Seams, corners, and outlet points are fitted carefully to keep the system consistent. You get a cleaner gutter line and better protection during storms.",
    "perry-ia": "Perry homes can see debris build up quietly until the first heavy rain forces water over the gutter edge. We clean the gutters, verify slope, and confirm the downspouts drain freely before installing guards. Then we install guards with secure fastening across seams and corners so they do not lift or separate. We pay attention to outlet areas because that is where clogs become overflow. The end result is more reliable drainage and less maintenance.",
    "pleasant-hill-ia": "Pleasant Hill has plenty of runoff events where a clogged gutter can overflow and soak fascia or spill near the foundation. We start by cleaning the system and checking for sagging sections that create standing water. Then we install gutter guards fitted to the roof edge to keep leaves and roof grit out of the trough. Corners and transitions are secured carefully to prevent gaps that collect debris. You get fewer backups and a gutter system that drains more consistently.",
    "polk-city-ia": "Polk City homes can get hit with wind-driven debris that piles into gutters and blocks outlets quickly. We begin with a clean-out and verify the gutter line is pitched correctly toward the downspouts. Then we install guards that stay tight along the roof edge and are fastened consistently across long runs. We reinforce corners and outlet points because those are the most common failure areas. The result is reduced clogs and less overflow during storms.",
    "prairie-city-ia": "Prairie City properties often deal with debris that collects in gutters and turns into overflow once storms arrive. We clean the system and confirm downspouts are clear and draining the way they should. Then we install gutter guards with tight alignment to the roof edge so leaves and grit are blocked without restricting water intake. Seams and corners are fitted carefully to keep debris from slipping under. You get steadier flow and far fewer cleanouts.",
    "redfield-ia": "Redfield homes can see gutters clog from seasonal debris and roof grit that settles at seams and corners. We start by clearing the gutters and confirming water moves to the downspouts without pooling. Then we install guards that sit flush and remain secure through wind and heavy rain. Corners and outlet areas are treated as priority points because that is where backups start. The end result is less overflow and less routine maintenance.",
    "slater-ia": "Slater weather and debris can fill gutters quickly, especially when wind pushes leaves into corners and valleys. We clean the system, check the pitch, and verify downspouts are flowing before installing guards. Then we install guards with consistent fastening so they do not lift or separate at seams. We focus on corners and outlets to prevent the common clog points that trigger overflow. You get a gutter line that drains more predictably through storm season.",
    "story-city-ia": "Story City homes often deal with debris buildup that restricts gutters and causes overflow when rain volume spikes. We start by clearing debris and confirming the downspouts are open and carrying water away properly. Then we install gutter guards that fit tight along the roof edge and remain stable across long runs. Corners and transition points are fitted carefully to prevent gaps that collect debris. The result is fewer clogs and less time spent maintaining gutters.",
    "stuart-ia": "Stuart properties can see gutter issues when debris packs into the trough and blocks the downspout outlets. We clean the gutters, confirm pitch, and check outlets for restrictions before installing guards. Then we install guards with tight alignment and secure fastening across seams and corners. Valleys and inside corners are handled carefully because that is where runoff concentrates. You get better drainage performance and fewer maintenance cycles.",
    "sully-ia": "Sully homes can have clogs form from leaves and grit that collect at seams and corners, then overflow when storms hit. We start by cleaning the gutter system and verifying downspout flow. Then we install gutter guards with consistent overlap and fastening so the surface stays flush. Corners and outlet areas get extra attention to prevent backups from starting in high-flow spots. The goal is fewer cleanouts and less overflow along the roofline.",
    "urbandale-ia": "Urbandale homes often have tree cover and storm runoff that expose gutter clogs fast. We begin with a clean-out and confirm the gutters are pitched correctly so water moves to the downspouts. Then we install guards that fit tightly to the roof edge and are fastened evenly across runs, seams, and corners. We reinforce outlets and inside corners because that is where clogs become overflow. You get a cleaner-looking gutter line that stays functional longer.",
    "van-meter-ia": "Van Meter properties can see debris collect in gutters and restrict flow until the first major storm forces water over the edge. We clean the system, verify downspouts are clear, and address loose hangers before installing guards. Then we install guards with tight roofline alignment and consistent fastening across seams. Corners and transition points are fitted carefully to keep debris from slipping underneath. The result is steadier drainage and less maintenance over time.",
    "waukee-ia": "Waukee homes see fast storm runoff and the kind of seasonal debris that clogs gutters right when water volume is highest. We start by clearing the gutters and confirming downspouts drain properly. Then we install guards that fit the roof edge closely and are fastened consistently so they stay put. Inside corners, valleys, and outlet points are handled carefully to keep flow open under heavy load. You get fewer clogs and less overflow around fascia and landscaping.",
    "west-des-moines-ia": "West Des Moines homes often deal with mature trees, heavy storms, and winter conditions that make clogged gutters a repeated problem. We clean the system, verify pitch, and make sure downspouts are moving water away from the home. Then we install gutter guards with tight alignment and secure fastening across long runs and seams. We treat corners and outlet areas as priority points to prevent backups. The goal is dependable drainage and fewer ladder trips through the seasons.",
    "winterset-ia": "Winterset homes can see gutters clog from leaves and debris, then freeze into bigger issues when temperatures swing. We start by cleaning the gutters and checking for sagging runs that hold water. Then we install guards that sit flush to the roof edge to block debris while keeping water intake consistent. Corners and transitions are secured carefully so runoff does not push debris under the guard. You get a system that drains more reliably and needs far less routine cleaning.",
    "belle-plaine-ia": "Belle Plaine’s weather can be hard on gutters, especially when wind-driven debris and sudden downpours hit together. We clean the gutter runs, verify slope, and make sure outlets are clear before installing guards. The guards are fitted to the roof edge so they do not leave easy gaps for leaves or shingle grit. Inside corners and transitions are secured carefully because that is where clogs typically begin. You get a gutter system that sheds water more reliably and stays cleaner longer.",
    "dallas-center-ia": "Dallas Center properties often face wind-driven debris and fast weather changes that make gutter maintenance a constant chore. We clean the system, check gutter alignment, and confirm downspouts are clear before installing guards. Then we install guards that lock down consistently across long runs so they do not lift in wind. Corners and outlets are handled carefully to prevent the most common backup points. The goal is simpler maintenance and fewer overflow events around the home.",
    "pleasant-hill-ia": "Pleasant Hill has plenty of runoff events where a clogged gutter can overflow and soak fascia or spill near the foundation. We start by cleaning the system and checking for sagging sections that create standing water. Then we install gutter guards fitted to the roof edge to keep leaves and roof grit out of the trough. Corners and transitions are secured carefully to prevent gaps that collect debris. You get fewer backups and a gutter system that drains more consistently.",
    "polk-city-ia": "Polk City homes can get hit with wind-driven debris that piles into gutters and blocks outlets quickly. We begin with a clean-out and verify the gutter line is pitched correctly toward the downspouts. Then we install guards that stay tight along the roof edge and are fastened consistently across long runs. We reinforce corners and outlet points because those are the most common failure areas. The result is reduced clogs and less overflow during storms.",
}

def get_meta_description(html_text: str) -> str:
    m = re.search(r'<meta name="description" content="([^"]+)"\s*/?>', html_text)
    return m.group(1) if m else ""

def get_title(html_text: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html_text, re.S)
    return htmlmod.unescape(m.group(1).strip()) if m else ""

def replace_schema(html_text: str, schema_obj: dict) -> str:
    schema_json = json.dumps(schema_obj, separators=(",", ":"), ensure_ascii=False)
    if re.search(r'<script id="schema-ld" type="application/ld\+json">.*?</script>', html_text, flags=re.S):
        return re.sub(
            r'<script id="schema-ld" type="application/ld\+json">.*?</script>',
            f'<script id="schema-ld" type="application/ld+json">{schema_json}</script>',
            html_text,
            flags=re.S,
        )
    inject = f'<script id="schema-ld" type="application/ld+json">{schema_json}</script>\n'
    if "</head>" in html_text:
        return html_text.replace("</head>", inject + "</head>", 1)
    return inject + html_text

def city_from_slug(slug: str) -> str:
    parts = slug.split("-")
    if parts and parts[-1].lower() == "ia":
        parts = parts[:-1]
    return " ".join(w.capitalize() for w in parts)

def build_city_schema(slug: str, city: str, desc: str) -> dict:
    url = f"https://iowagutterguards.online/service-areas/{slug}/"

    business = {
        "@type": "LocalBusiness",
        "@id": "https://iowagutterguards.online/#business",
        "name": "Iowa Gutter Guards",
        "url": "https://iowagutterguards.online/",
        "email": "info@iowagutterguards.online",
        "telephone": "+1-515-329-5128",
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": "+1-515-329-5128",
                "contactType": "sales",
                "areaServed": "US",
                "availableLanguage": ["en"],
            }
        ],
    }

    website = {
        "@type": "WebSite",
        "@id": "https://iowagutterguards.online/#website",
        "url": "https://iowagutterguards.online/",
        "name": "Iowa Gutter Guards",
        "publisher": {"@id": "https://iowagutterguards.online/#business"},
    }

    webpage = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": f"Gutter Guards in {city}, IA | Iowa Gutter Guards",
        "description": desc,
        "about": {"@id": "https://iowagutterguards.online/#business"},
        "isPartOf": {"@id": "https://iowagutterguards.online/#website"},
    }

    service = {
        "@type": "Service",
        "@id": f"{url}#service-gutter-guards",
        "name": f"Gutter Guard Installation in {city}, IA",
        "serviceType": "Gutter guard installation",
        "provider": {"@id": "https://iowagutterguards.online/#business"},
        "url": url,
        "areaServed": {
            "@type": "City",
            "name": city,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressRegion": "IA",
                "addressCountry": "US",
            },
        },
    }

    breadcrumb = {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumbs",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://iowagutterguards.online/"},
            {"@type": "ListItem", "position": 2, "name": "Service Areas", "item": "https://iowagutterguards.online/#service-areas"},
            {"@type": "ListItem", "position": 3, "name": f"{city}, IA", "item": url},
        ],
    }

    return {"@context": "https://schema.org", "@graph": [business, website, webpage, service, breadcrumb]}

def build_simple_schema(url: str, title: str, desc: str) -> dict:
    business = {
        "@type": "LocalBusiness",
        "@id": "https://iowagutterguards.online/#business",
        "name": "Iowa Gutter Guards",
        "url": "https://iowagutterguards.online/",
        "email": "info@iowagutterguards.online",
        "telephone": "+1-515-329-5128",
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": "+1-515-329-5128",
                "contactType": "sales",
                "areaServed": "US",
                "availableLanguage": ["en"],
            }
        ],
    }

    website = {
        "@type": "WebSite",
        "@id": "https://iowagutterguards.online/#website",
        "url": "https://iowagutterguards.online/",
        "name": "Iowa Gutter Guards",
        "publisher": {"@id": "https://iowagutterguards.online/#business"},
    }

    webpage = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": title or url,
        "description": desc,
        "about": {"@id": "https://iowagutterguards.online/#business"},
        "isPartOf": {"@id": "https://iowagutterguards.online/#website"},
    }

    return {"@context": "https://schema.org", "@graph": [business, website, webpage]}

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

def remove_repetitive_city_block(html_text: str) -> tuple[str, bool]:
    if REPETITIVE_CITY_MARKER not in html_text:
        return html_text, False

    idx = html_text.find(REPETITIVE_CITY_MARKER)
    start = html_text.rfind("<section", 0, idx)
    if start == -1:
        return html_text, False

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

def replace_hero_lede(html_text: str, new_paragraph: str) -> tuple[str, bool]:
    m = re.search(r'<p class="hero-lede">\s*(.*?)\s*</p>', html_text, flags=re.S)
    if not m:
        return html_text, False
    replacement = f'<p class="hero-lede">\n            {new_paragraph}\n          </p>'
    return html_text[: m.start()] + replacement + html_text[m.end() :], True

def main() -> None:
    updated = []

    # Homepage: remove the whole "Text us about your gutters" block.
    # Current site uses section id="contact" for that block.
    home = SITE_ROOT / "index.html"
    if home.exists():
        html_text = home.read_text(encoding="utf-8")
        html_text2, did = remove_section_by_id(html_text, "contact")
        if did:
            home.write_text(html_text2, encoding="utf-8")
            updated.append(str(home))

    # City pages
    sa_dir = SITE_ROOT / "service-areas"
    if not sa_dir.exists():
        raise SystemExit("Missing /service-areas directory.")

    city_pages = sorted(sa_dir.glob("*-ia/index.html"))
    slugs = [p.parent.name for p in city_pages]

    missing = [s for s in slugs if s not in CITY_PARAGRAPHS]
    extra = [s for s in CITY_PARAGRAPHS.keys() if s not in slugs]

    if missing:
        raise SystemExit(f"Missing unique paragraph entries for: {missing}")
    if extra:
        # Not fatal, but indicates mapping drift.
        print(f"Warning: CITY_PARAGRAPHS includes entries not present in repo: {extra}")

    for page in city_pages:
        slug = page.parent.name
        city = city_from_slug(slug)

        html_text = page.read_text(encoding="utf-8")

        # Remove the repetitive boilerplate block.
        html_text, _ = remove_repetitive_city_block(html_text)

        # Install the unique paragraph.
        paragraph = CITY_PARAGRAPHS[slug]
        html_text, did = replace_hero_lede(html_text, paragraph)
        if not did:
            # If hero-lede class changes later, fail loudly instead of silently doing nothing.
            raise SystemExit(f"Could not find <p class='hero-lede'> on {page}")

        # Replace page schema with city-appropriate schema.
        desc = get_meta_description(html_text)
        schema = build_city_schema(slug, city, desc)
        html_text = replace_schema(html_text, schema)

        page.write_text(html_text, encoding="utf-8")
        updated.append(str(page))

    # Legal/support pages: schema should match the page, not the whole site.
    for d in ["privacy-policy", "terms-of-service", "warranty", "customer-service", "thanks", "thank-you"]:
        page = SITE_ROOT / d / "index.html"
        if not page.exists():
            continue
        html_text = page.read_text(encoding="utf-8")
        title = get_title(html_text)
        desc = get_meta_description(html_text)
        url = f"https://iowagutterguards.online/{d}/"
        schema = build_simple_schema(url, title, desc)
        html_text = replace_schema(html_text, schema)
        page.write_text(html_text, encoding="utf-8")
        updated.append(str(page))

    print("Updated files:")
    for p in updated:
        print(" -", p)
    print(f"\nDone. Total updated: {len(updated)}")

if __name__ == "__main__":
    main()
