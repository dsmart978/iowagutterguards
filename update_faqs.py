#!/usr/bin/env python3
"""
Script to update Iowa Gutter Guards website:
1. Remove trust badges section from homepage
2. Add 10 unique FAQs to each city page (5 city-specific + 5 general)
"""

import os
import re
from pathlib import Path

# City data with unique characteristics for FAQ generation
CITY_DATA = {
    "des-moines-ia": {
        "name": "Des Moines",
        "population": "large",
        "description": "Iowa's capital and largest city",
        "home_age": "mix of historic and newer homes",
        "tree_types": ["mature oak", "maple", "walnut trees in established neighborhoods"],
        "unique_factor": "historic neighborhoods like Sherman Hill and Beaverdale",
        "distance": "local",
        "weather_concern": "downtown and urban heat island effects",
        "home_style": "Victorian homes, Craftsman bungalows, and modern developments"
    },
    "west-des-moines-ia": {
        "name": "West Des Moines",
        "population": "large",
        "description": "fast-growing suburb with Jordan Creek area",
        "home_age": "predominantly newer construction from 1990s-present",
        "tree_types": ["newly planted ornamental trees", "landscaping maples"],
        "unique_factor": "Valley Junction historic district and newer developments",
        "distance": "local",
        "weather_concern": "open terrain exposure in newer developments",
        "home_style": "two-story colonials, executive homes, and townhomes"
    },
    "ankeny-ia": {
        "name": "Ankeny",
        "population": "large",
        "description": "one of Iowa's fastest-growing cities",
        "home_age": "mostly newer construction, rapid development",
        "tree_types": ["young trees in new developments", "prairie restoration areas"],
        "unique_factor": "Prairie Trail development and DMACC campus area",
        "distance": "local",
        "weather_concern": "wind exposure in open prairie developments",
        "home_style": "modern subdivisions, split-levels, and new construction"
    },
    "ames-ia": {
        "name": "Ames",
        "population": "medium",
        "description": "home to Iowa State University",
        "home_age": "mix of student rentals and family homes",
        "tree_types": ["campus trees", "mature neighborhood shade trees"],
        "unique_factor": "university community with Campustown and research park",
        "distance": "30 miles north",
        "weather_concern": "Story County gets heavier snow accumulation",
        "home_style": "older homes near campus, newer family developments"
    },
    "urbandale-ia": {
        "name": "Urbandale",
        "population": "medium",
        "description": "established residential suburb",
        "home_age": "mature suburb with 1960s-1990s homes",
        "tree_types": ["large mature trees", "established landscaping"],
        "unique_factor": "Living History Farms area and corporate parks",
        "distance": "local",
        "weather_concern": "mature tree canopy creates heavy debris",
        "home_style": "ranch homes, split-levels, and bi-levels"
    },
    "waukee-ia": {
        "name": "Waukee",
        "population": "medium",
        "description": "explosive growth suburb",
        "home_age": "mostly built after 2000",
        "tree_types": ["young landscaping trees", "ornamental varieties"],
        "unique_factor": "one of America's fastest-growing small cities",
        "distance": "local",
        "weather_concern": "newer roof materials and construction standards",
        "home_style": "executive homes, two-story moderns, and new builds"
    },
    "clive-ia": {
        "name": "Clive",
        "population": "small",
        "description": "affluent inner-ring suburb",
        "home_age": "established 1970s-1990s neighborhoods",
        "tree_types": ["mature oaks", "large shade trees"],
        "unique_factor": "Greenbelt trails and Campbell Recreation Area",
        "distance": "local",
        "weather_concern": "dense tree coverage along greenbelt",
        "home_style": "well-maintained ranches and two-stories"
    },
    "johnston-ia": {
        "name": "Johnston",
        "population": "medium",
        "description": "family-oriented suburb north of Des Moines",
        "home_age": "mix of 1980s established and newer growth",
        "tree_types": ["mature and newly planted trees"],
        "unique_factor": "Camp Dodge military installation nearby",
        "distance": "local",
        "weather_concern": "Saylorville Lake area moisture patterns",
        "home_style": "family subdivisions, ranches, and newer developments"
    },
    "grimes-ia": {
        "name": "Grimes",
        "population": "small",
        "description": "rapidly expanding northern suburb",
        "home_age": "primarily new construction",
        "tree_types": ["young trees", "landscaping being established"],
        "unique_factor": "one of Dallas County's fastest-growing areas",
        "distance": "local",
        "weather_concern": "open farmland conversion means wind exposure",
        "home_style": "new single-family homes and townhomes"
    },
    "altoona-ia": {
        "name": "Altoona",
        "population": "medium",
        "description": "eastern suburb with Adventureland and casino",
        "home_age": "mix of established and newer construction",
        "tree_types": ["mature neighborhood trees", "newer development landscaping"],
        "unique_factor": "Outlets of Des Moines and entertainment district",
        "distance": "local",
        "weather_concern": "proximity to floodplain areas",
        "home_style": "working-class ranches and newer subdivisions"
    },
    "pleasant-hill-ia": {
        "name": "Pleasant Hill",
        "population": "small",
        "description": "quiet southeastern suburb",
        "home_age": "established 1970s-1990s homes",
        "tree_types": ["mature shade trees", "wooded lots"],
        "unique_factor": "close to Copper Creek Lake",
        "distance": "local",
        "weather_concern": "lake-area moisture and wooded debris",
        "home_style": "ranches and bi-levels on larger lots"
    },
    "norwalk-ia": {
        "name": "Norwalk",
        "population": "medium",
        "description": "southern suburb with small-town feel",
        "home_age": "rapid recent growth with older core",
        "tree_types": ["established trees in old Norwalk", "new landscaping"],
        "unique_factor": "small-town character despite metro proximity",
        "distance": "local",
        "weather_concern": "Warren County storm patterns",
        "home_style": "mix of historic homes and new developments"
    },
    "carlisle-ia": {
        "name": "Carlisle",
        "population": "small",
        "description": "small town east of Des Moines",
        "home_age": "older core with some newer development",
        "tree_types": ["mature trees", "rural wooded areas nearby"],
        "unique_factor": "maintains small-town Iowa atmosphere",
        "distance": "15 miles east",
        "weather_concern": "rural exposure to storms",
        "home_style": "older ranch homes and farmhouses"
    },
    "indianola-ia": {
        "name": "Indianola",
        "population": "medium",
        "description": "Warren County seat and Simpson College town",
        "home_age": "historic downtown with suburban growth",
        "tree_types": ["campus trees", "mature residential areas"],
        "unique_factor": "National Balloon Classic host city",
        "distance": "20 miles south",
        "weather_concern": "Warren County severe weather corridor",
        "home_style": "college town homes, historic districts, and newer suburbs"
    },
    "pella-ia": {
        "name": "Pella",
        "population": "medium",
        "description": "Dutch heritage community",
        "home_age": "well-maintained historic and modern homes",
        "tree_types": ["tulip trees", "mature shade trees"],
        "unique_factor": "Dutch architecture and Tulip Time festival",
        "distance": "45 miles southeast",
        "weather_concern": "Marion County gets significant rainfall",
        "home_style": "Dutch-inspired architecture and brick homes"
    },
    "newton-ia": {
        "name": "Newton",
        "population": "medium",
        "description": "Jasper County seat, former Maytag headquarters",
        "home_age": "older established neighborhoods",
        "tree_types": ["mature oaks and maples", "wooded residential areas"],
        "unique_factor": "industrial heritage and Iowa Speedway",
        "distance": "35 miles east",
        "weather_concern": "Jasper County tornado corridor",
        "home_style": "early 1900s homes and mid-century ranches"
    },
    "marshalltown-ia": {
        "name": "Marshalltown",
        "population": "medium",
        "description": "Marshall County seat with industrial base",
        "home_age": "older established community",
        "tree_types": ["large mature trees", "Iowa River bottomland trees"],
        "unique_factor": "recovering from 2018 tornado damage",
        "distance": "50 miles northeast",
        "weather_concern": "tornado rebuilding means newer roofs",
        "home_style": "older homes, many recently rebuilt or repaired"
    },
    "boone-ia": {
        "name": "Boone",
        "population": "medium",
        "description": "railroad heritage community",
        "home_age": "historic downtown with established neighborhoods",
        "tree_types": ["Des Moines River valley trees", "mature shade trees"],
        "unique_factor": "Ledges State Park and railroad tourism",
        "distance": "40 miles north",
        "weather_concern": "Boone County heavy snow accumulation",
        "home_style": "Victorian era homes and mid-century construction"
    },
    "oskaloosa-ia": {
        "name": "Oskaloosa",
        "population": "medium",
        "description": "Mahaska County seat with Penn Central heritage",
        "home_age": "historic downtown and established residential",
        "tree_types": ["mature shade trees", "campus landscaping"],
        "unique_factor": "William Penn University and Nelson Pioneer Farm",
        "distance": "60 miles southeast",
        "weather_concern": "Mahaska County severe weather patterns",
        "home_style": "historic brick homes and traditional ranches"
    },
    "knoxville-ia": {
        "name": "Knoxville",
        "population": "small",
        "description": "Marion County seat near Lake Red Rock",
        "home_age": "established older community",
        "tree_types": ["lake-area trees", "mature residential landscaping"],
        "unique_factor": "Knoxville Raceway sprint car capital",
        "distance": "40 miles southeast",
        "weather_concern": "Lake Red Rock moisture and storms",
        "home_style": "small-town homes and lakeside properties"
    },
    "grinnell-ia": {
        "name": "Grinnell",
        "population": "small",
        "description": "college town with Grinnell College",
        "home_age": "historic homes near campus, varied elsewhere",
        "tree_types": ["campus trees", "mature residential plantings"],
        "unique_factor": "prestigious liberal arts college community",
        "distance": "55 miles east",
        "weather_concern": "Poweshiek County wind and storm exposure",
        "home_style": "Victorian homes, professor housing, older ranches"
    },
    "perry-ia": {
        "name": "Perry",
        "population": "small",
        "description": "Dallas County community with railroad heritage",
        "home_age": "older established community",
        "tree_types": ["mature trees", "Raccoon River valley vegetation"],
        "unique_factor": "Hotel Pattee and meatpacking heritage",
        "distance": "30 miles northwest",
        "weather_concern": "Dallas County severe weather exposure",
        "home_style": "early 1900s worker housing and ranches"
    },
    "adel-ia": {
        "name": "Adel",
        "population": "small",
        "description": "Dallas County seat with historic courthouse",
        "home_age": "historic downtown, newer growth areas",
        "tree_types": ["established shade trees", "newer landscaping"],
        "unique_factor": "charming courthouse square and small-town feel",
        "distance": "25 miles west",
        "weather_concern": "Dallas County storm patterns",
        "home_style": "historic homes and newer subdivisions"
    },
    "winterset-ia": {
        "name": "Winterset",
        "population": "small",
        "description": "Madison County seat, John Wayne birthplace",
        "home_age": "historic downtown with charming older homes",
        "tree_types": ["covered bridge area trees", "mature shade trees"],
        "unique_factor": "Bridges of Madison County and apple orchards",
        "distance": "35 miles southwest",
        "weather_concern": "Madison County ridge exposure to winds",
        "home_style": "historic Victorian and craftsman homes"
    },
    "polk-city-ia": {
        "name": "Polk City",
        "population": "small",
        "description": "lakeside community on Saylorville",
        "home_age": "mix of established and newer lakeside homes",
        "tree_types": ["lake-area vegetation", "mature residential trees"],
        "unique_factor": "Big Creek State Park and Saylorville access",
        "distance": "local",
        "weather_concern": "lake effect moisture and humidity",
        "home_style": "lake homes, cabins, and newer subdivisions"
    },
    "bondurant-ia": {
        "name": "Bondurant",
        "population": "small",
        "description": "fast-growing eastern suburb",
        "home_age": "mostly new construction",
        "tree_types": ["young landscaping trees", "prairie areas"],
        "unique_factor": "one of Iowa's fastest-growing small towns",
        "distance": "local",
        "weather_concern": "open terrain wind exposure",
        "home_style": "new single-family construction"
    },
    "huxley-ia": {
        "name": "Huxley",
        "population": "small",
        "description": "Story County bedroom community",
        "home_age": "older core with newer residential growth",
        "tree_types": ["established trees", "farmstead trees"],
        "unique_factor": "small-town atmosphere near Ames",
        "distance": "25 miles north",
        "weather_concern": "Story County snow and wind",
        "home_style": "small-town homes and newer developments"
    },
    "slater-ia": {
        "name": "Slater",
        "population": "small",
        "description": "small Story County community",
        "home_age": "established older community",
        "tree_types": ["mature shade trees", "rural windbreaks nearby"],
        "unique_factor": "quiet small-town Iowa living",
        "distance": "20 miles north",
        "weather_concern": "rural exposure to prairie storms",
        "home_style": "older ranches and traditional homes"
    },
    "madrid-ia": {
        "name": "Madrid",
        "population": "small",
        "description": "Boone County community on High Trestle Trail",
        "home_age": "older established town",
        "tree_types": ["Des Moines River valley trees", "mature landscaping"],
        "unique_factor": "High Trestle Trail bridge access",
        "distance": "25 miles northwest",
        "weather_concern": "river valley fog and moisture",
        "home_style": "early 1900s homes and older ranches"
    },
    "story-city-ia": {
        "name": "Story City",
        "population": "small",
        "description": "Scandinavian heritage community",
        "home_age": "historic downtown with established residential",
        "tree_types": ["mature shade trees", "community park trees"],
        "unique_factor": "antique carousel and Nordic heritage",
        "distance": "35 miles north",
        "weather_concern": "Story County heavy winter weather",
        "home_style": "well-maintained older homes and ranches"
    },
    "nevada-ia": {
        "name": "Nevada",
        "population": "small",
        "description": "Story County seat",
        "home_age": "established county seat community",
        "tree_types": ["mature residential trees", "courthouse square landscaping"],
        "unique_factor": "historic Lincoln Highway community",
        "distance": "35 miles northeast",
        "weather_concern": "Story County storm corridor",
        "home_style": "older county seat homes and ranches"
    },
    "eldora-ia": {
        "name": "Eldora",
        "population": "small",
        "description": "Hardin County seat",
        "home_age": "older established community",
        "tree_types": ["Iowa River trees", "mature residential shade trees"],
        "unique_factor": "Pine Lake State Park nearby",
        "distance": "60 miles north",
        "weather_concern": "Hardin County severe weather exposure",
        "home_style": "older traditional Iowa homes"
    },
    "belle-plaine-ia": {
        "name": "Belle Plaine",
        "population": "small",
        "description": "Benton County community",
        "home_age": "older established railroad town",
        "tree_types": ["mature trees", "Iowa River valley vegetation"],
        "unique_factor": "historic railroad heritage",
        "distance": "50 miles east",
        "weather_concern": "Benton County tornado alley location",
        "home_style": "early 1900s homes and older ranches"
    },
    "colfax-ia": {
        "name": "Colfax",
        "population": "small",
        "description": "Jasper County community near Newton",
        "home_age": "established older community",
        "tree_types": ["mature shade trees", "rural windbreaks"],
        "unique_factor": "small-town community near Iowa Speedway",
        "distance": "30 miles east",
        "weather_concern": "Jasper County severe weather",
        "home_style": "older ranches and traditional homes"
    },
    "prairie-city-ia": {
        "name": "Prairie City",
        "population": "small",
        "description": "Jasper County community",
        "home_age": "older established small town",
        "tree_types": ["mature trees", "prairie restoration areas"],
        "unique_factor": "Neal Smith National Wildlife Refuge nearby",
        "distance": "25 miles east",
        "weather_concern": "prairie wind and storm exposure",
        "home_style": "small-town older homes"
    },
    "monroe-ia": {
        "name": "Monroe",
        "population": "small",
        "description": "Jasper County community",
        "home_age": "established older community",
        "tree_types": ["mature residential trees", "rural surroundings"],
        "unique_factor": "small-town rural Iowa character",
        "distance": "35 miles east",
        "weather_concern": "rural storm exposure",
        "home_style": "older traditional homes"
    },
    "sully-ia": {
        "name": "Sully",
        "population": "small",
        "description": "Jasper County Dutch community",
        "home_age": "established older community",
        "tree_types": ["mature shade trees", "well-maintained landscaping"],
        "unique_factor": "Dutch Reformed heritage",
        "distance": "40 miles southeast",
        "weather_concern": "rural agricultural exposure",
        "home_style": "well-maintained older homes"
    },
    "lynnville-ia": {
        "name": "Lynnville",
        "population": "small",
        "description": "tiny Jasper County community",
        "home_age": "older established small town",
        "tree_types": ["mature trees", "farmstead windbreaks"],
        "unique_factor": "peaceful rural Iowa setting",
        "distance": "40 miles east",
        "weather_concern": "rural storm and wind exposure",
        "home_style": "older farmhouses and small-town homes"
    },
    "melbourne-ia": {
        "name": "Melbourne",
        "population": "small",
        "description": "Marshall County small town",
        "home_age": "older established community",
        "tree_types": ["mature shade trees", "rural vegetation"],
        "unique_factor": "small-town Iowa character",
        "distance": "45 miles northeast",
        "weather_concern": "Marshall County severe weather",
        "home_style": "older traditional homes"
    },
    "baxter-ia": {
        "name": "Baxter",
        "population": "small",
        "description": "Jasper County community",
        "home_age": "older established small town",
        "tree_types": ["mature trees", "rural surroundings"],
        "unique_factor": "small-town rural community",
        "distance": "30 miles east",
        "weather_concern": "Jasper County storm patterns",
        "home_style": "older ranches and traditional homes"
    },
    "corydon-ia": {
        "name": "Corydon",
        "population": "small",
        "description": "Wayne County seat in southern Iowa",
        "home_age": "historic older community",
        "tree_types": ["mature trees", "southern Iowa hardwoods"],
        "unique_factor": "Mormon Trail historic site",
        "distance": "75 miles south",
        "weather_concern": "southern Iowa severe weather corridor",
        "home_style": "historic older homes"
    },
    "chariton-ia": {
        "name": "Chariton",
        "population": "small",
        "description": "Lucas County seat",
        "home_age": "established older county seat",
        "tree_types": ["mature shade trees", "Chariton River valley trees"],
        "unique_factor": "Red Haw State Park nearby",
        "distance": "55 miles south",
        "weather_concern": "Lucas County severe weather",
        "home_style": "older county seat homes"
    },
    "osceola-ia": {
        "name": "Osceola",
        "population": "small",
        "description": "Clarke County seat on I-35",
        "home_age": "established older community",
        "tree_types": ["mature trees", "southern Iowa vegetation"],
        "unique_factor": "I-35 corridor community",
        "distance": "50 miles south",
        "weather_concern": "southern Iowa severe weather",
        "home_style": "older traditional Iowa homes"
    },
    "greenfield-ia": {
        "name": "Greenfield",
        "population": "small",
        "description": "Adair County seat",
        "home_age": "historic older community",
        "tree_types": ["mature shade trees", "rural windbreaks"],
        "unique_factor": "small-town Iowa county seat",
        "distance": "50 miles southwest",
        "weather_concern": "Adair County wind exposure",
        "home_style": "older historic homes"
    },
    "stuart-ia": {
        "name": "Stuart",
        "population": "small",
        "description": "Guthrie County community on I-80",
        "home_age": "established older community",
        "tree_types": ["mature trees", "Middle River valley vegetation"],
        "unique_factor": "birthplace of John Wayne's parents",
        "distance": "40 miles west",
        "weather_concern": "I-80 corridor wind exposure",
        "home_style": "older small-town homes"
    },
    "earlham-ia": {
        "name": "Earlham",
        "population": "small",
        "description": "Madison County community",
        "home_age": "established older community",
        "tree_types": ["mature shade trees", "rural landscaping"],
        "unique_factor": "small-town near covered bridges",
        "distance": "30 miles southwest",
        "weather_concern": "Madison County storm patterns",
        "home_style": "older traditional homes"
    },
    "redfield-ia": {
        "name": "Redfield",
        "population": "small",
        "description": "Dallas County small town",
        "home_age": "older established community",
        "tree_types": ["mature trees", "Raccoon River valley vegetation"],
        "unique_factor": "quiet rural Dallas County setting",
        "distance": "30 miles west",
        "weather_concern": "Dallas County severe weather",
        "home_style": "older small-town homes"
    },
    "van-meter-ia": {
        "name": "Van Meter",
        "population": "small",
        "description": "Dallas County community, Bob Feller hometown",
        "home_age": "older core with newer growth",
        "tree_types": ["mature trees", "newer landscaping"],
        "unique_factor": "Bob Feller Museum and High Trestle Trail",
        "distance": "20 miles west",
        "weather_concern": "Raccoon River valley moisture",
        "home_style": "mix of historic and newer homes"
    },
    "dallas-center-ia": {
        "name": "Dallas Center",
        "population": "small",
        "description": "Dallas County community",
        "home_age": "established older community with growth",
        "tree_types": ["mature shade trees", "newer development landscaping"],
        "unique_factor": "growing Dallas County suburb",
        "distance": "20 miles west",
        "weather_concern": "Dallas County severe weather corridor",
        "home_style": "older homes and newer developments"
    },
    "jefferson-ia": {
        "name": "Jefferson",
        "population": "small",
        "description": "Greene County seat",
        "home_age": "historic county seat community",
        "tree_types": ["mature shade trees", "Raccoon River trees"],
        "unique_factor": "Mahanay Bell Tower and historic square",
        "distance": "55 miles northwest",
        "weather_concern": "Greene County severe weather",
        "home_style": "historic Victorian and older ranches"
    }
}

# 5 General FAQs (same for all cities)
GENERAL_FAQS = [
    {
        "question": "What type of gutter guards do you install?",
        "answer": "We install a professional-grade stainless steel micro-mesh gutter guard system with a rigid aluminum frame. This design filters out leaves, pine needles, maple helicopters, and roof grit while allowing water to flow freely. Unlike foam inserts or plastic snap-on guards, our micro-mesh system is built to handle Iowa's heavy rains and doesn't degrade in our harsh winters."
    },
    {
        "question": "How long do gutter guards last?",
        "answer": "Our stainless steel micro-mesh guards are designed to last 20+ years with minimal maintenance. The aluminum frame won't rust, and the surgical-grade stainless steel mesh resists corrosion and UV damage. We back our installation with a lifetime transferable warranty, so your investment is protected even if you sell your home."
    },
    {
        "question": "Will gutter guards work in heavy rain?",
        "answer": "Yes. Our micro-mesh system is specifically designed to handle heavy Iowa downpours. The fine mesh allows water to sheet through while debris slides off the angled surface. In extreme rainfall, some water may overshoot (as with any gutter system), but the guards prevent the clogs that cause real water damage problems."
    },
    {
        "question": "Do gutter guards cause ice dams in winter?",
        "answer": "Properly installed gutter guards don't cause ice dams. Ice dams form due to heat escaping from your attic, not from gutter guards. Our low-profile guards actually allow snow to slide off more easily than open gutters packed with frozen debris. We install with proper spacing to ensure winter performance."
    },
    {
        "question": "What's included in your warranty?",
        "answer": "Our lifetime transferable warranty covers both materials and workmanship. If the guards fail to perform as promised, we'll fix it at no charge. The warranty transfers to new homeowners if you sell, which adds value to your home. We provide warranty documentation with every installation."
    }
]

def generate_city_faqs(city_slug, city_info):
    """Generate 5 unique city-specific FAQs based on city characteristics."""
    city_name = city_info["name"]
    
    faqs = []
    
    # FAQ 1: Service area and travel question
    if city_info["distance"] == "local":
        faqs.append({
            "question": f"Do you provide gutter guard installation in {city_name}?",
            "answer": f"Yes, {city_name} is in our primary service area. As part of the Des Moines metro, we're able to provide quick scheduling and same-week consultations for {city_name} homeowners. We know the {city_info['unique_factor']} and understand the specific gutter challenges in your area."
        })
    else:
        faqs.append({
            "question": f"Do you travel to {city_name} for gutter guard installation?",
            "answer": f"Absolutely. {city_name}, located {city_info['distance']} of Des Moines, is well within our service area. We regularly work with homeowners throughout the region. Since {city_info['description']}, we understand the local home styles and gutter needs specific to your community."
        })
    
    # FAQ 2: Home style and age question
    if "historic" in city_info["home_age"] or "older" in city_info["home_age"]:
        faqs.append({
            "question": f"Can you install gutter guards on older homes in {city_name}?",
            "answer": f"Yes, we specialize in working with {city_info['home_age']}. Many {city_name} homes have {city_info['home_style']}, and our micro-mesh guards adapt to various gutter sizes and mounting configurations. We'll assess your existing gutters and recommend any repairs needed before installation."
        })
    elif "new" in city_info["home_age"]:
        faqs.append({
            "question": f"Do new homes in {city_name} need gutter guards?",
            "answer": f"Absolutely. {city_name} has {city_info['home_age']}, and even new gutters benefit from protection. Once landscaping matures, debris becomes a problem. Installing guards early prevents years of cleaning headaches and protects your investment in your new {city_info['home_style'].split(',')[0] if ',' in city_info['home_style'] else city_info['home_style']}."
        })
    else:
        faqs.append({
            "question": f"What types of homes do you service in {city_name}?",
            "answer": f"We work with all home types in {city_name}, including {city_info['home_style']}. Whether you have a {city_info['home_age']}, our micro-mesh guards can be installed on virtually any gutter system. We'll evaluate your specific setup during the free estimate."
        })
    
    # FAQ 3: Tree/debris specific question
    tree_list = ", ".join(city_info["tree_types"][:2])
    faqs.append({
        "question": f"What debris issues do {city_name} homeowners face?",
        "answer": f"In {city_name}, we commonly see gutters clogged with debris from {tree_list}. The {city_info['unique_factor']} means many properties have significant tree coverage. Our micro-mesh guards are specifically designed to handle maple helicopters, pine needles, and leaf accumulation that's common in your neighborhood."
    })
    
    # FAQ 4: Weather/climate specific question
    faqs.append({
        "question": f"How do your guards handle {city_name}'s weather conditions?",
        "answer": f"Our gutter guards are engineered for Iowa weather, including the conditions specific to {city_name}. We know that {city_info['weather_concern']}, so we ensure proper installation that handles heavy spring rains, summer storms, fall leaf drop, and winter snow and ice. The stainless steel construction won't crack or warp in temperature extremes."
    })
    
    # FAQ 5: Local/community specific question
    if city_info["population"] == "large":
        faqs.append({
            "question": f"Why do {city_name} homeowners choose Iowa Gutter Guards?",
            "answer": f"As {city_info['description']}, {city_name} homeowners want quality work from a company that stands behind their installation. We're not a big-box retailer subcontractor—we're a local Iowa company that focuses exclusively on gutter protection. Many of our customers in {city_name} found us through neighbor referrals."
        })
    elif city_info["population"] == "medium":
        faqs.append({
            "question": f"Are you familiar with homes in the {city_name} area?",
            "answer": f"Yes, we've installed gutter guards throughout {city_name} and know the {city_info['unique_factor']} well. As {city_info['description']}, your community has specific home styles we're experienced with. We provide the same quality service to {city_name} that we do for the Des Moines metro."
        })
    else:
        faqs.append({
            "question": f"Do you work in small towns like {city_name}?",
            "answer": f"Absolutely. We believe homeowners in {city_name} deserve the same professional gutter guard installation as those in larger cities. As {city_info['description']}, your homes face the same Iowa weather challenges. We travel to {city_name} regularly and include your area in our normal service routes."
        })
    
    return faqs

def create_faq_html(city_slug, city_info):
    """Create the complete FAQ HTML section with Schema.org markup."""
    city_name = city_info["name"]
    city_faqs = generate_city_faqs(city_slug, city_info)
    
    # Combine city-specific (first 5) + general (last 5)
    all_faqs = city_faqs + GENERAL_FAQS
    
    # Build FAQ items HTML
    faq_items_html = ""
    schema_items = []
    
    for i, faq in enumerate(all_faqs):
        faq_items_html += f'''          <details>
            <summary><strong>{faq["question"]}</strong></summary>
            <p style="margin-top:0.4rem; font-size:0.88rem; color:var(--muted);">
              {faq["answer"]}
            </p>
          </details>

'''
        # Add to schema
        schema_items.append({
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["answer"]
            }
        })
    
    # Build the complete FAQ section
    faq_section = f'''      <section class="section" id="faq">
        <h2>Frequently Asked Questions About Gutter Guards in {city_name}</h2>
        <p>
          These are the questions we hear most often from {city_name} homeowners. If you don't see your question here, call us at <a href="tel:+15153295128">(515) 329-5128</a> or include it in your estimate request.
        </p>
        <div style="display:grid; gap:0.75rem;">
{faq_items_html.rstrip()}
        </div>
      </section>'''
    
    return faq_section, schema_items

def update_city_page(city_slug):
    """Update a single city page with new FAQs."""
    city_info = CITY_DATA.get(city_slug)
    if not city_info:
        print(f"Warning: No data for {city_slug}")
        return False
    
    file_path = f"service-areas/{city_slug}/index.html"
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate new FAQ section
    new_faq_section, schema_items = create_faq_html(city_slug, city_info)
    
    # Replace existing FAQ section
    # Pattern to find the FAQ section
    faq_pattern = r'<section class="section" id="faq">.*?</section>'
    
    if re.search(faq_pattern, content, re.DOTALL):
        content = re.sub(faq_pattern, new_faq_section, content, flags=re.DOTALL)
    else:
        print(f"Warning: Could not find FAQ section in {file_path}")
        return False
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def remove_trust_badges_from_homepage():
    """Remove trust badges section from homepage."""
    file_path = "index.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the trust badges HTML section
    trust_badges_pattern = r'<!-- Trust Badges Section -->.*?</section>\s*'
    content = re.sub(trust_badges_pattern, '', content, flags=re.DOTALL)
    
    # Remove the trust badges CSS (keep it simple, just remove the HTML)
    # The CSS can stay as it won't affect anything
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Removed trust badges section from homepage")

def main():
    os.chdir("/home/ubuntu/iowa_gutter_guards_improved")
    
    # Step 1: Remove trust badges from homepage
    print("Removing trust badges from homepage...")
    remove_trust_badges_from_homepage()
    
    # Step 2: Update all city pages with new FAQs
    print("\nUpdating city pages with unique FAQs...")
    success_count = 0
    failed_cities = []
    
    for city_slug in CITY_DATA.keys():
        if update_city_page(city_slug):
            print(f"  ✓ Updated {city_slug}")
            success_count += 1
        else:
            failed_cities.append(city_slug)
            print(f"  ✗ Failed: {city_slug}")
    
    print(f"\nCompleted: {success_count}/{len(CITY_DATA)} cities updated")
    if failed_cities:
        print(f"Failed cities: {', '.join(failed_cities)}")

if __name__ == "__main__":
    main()
