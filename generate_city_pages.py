import os

TEMPLATE_FILE = "city-template.html"
OUTPUT_ROOT = "service-areas"

cities = [
    {"slug": "des-moines-ia", "name": "Des Moines", "nearby": "West Des Moines and Altoona"},
    {"slug": "west-des-moines-ia", "name": "West Des Moines", "nearby": "Clive and Waukee"},
    {"slug": "ankeny-ia", "name": "Ankeny", "nearby": "Alleman and Polk City"},
    {"slug": "altoona-ia", "name": "Altoona", "nearby": "Bondurant and Pleasant Hill"},
    {"slug": "urbandale-ia", "name": "Urbandale", "nearby": "Clive and Johnston"},
    {"slug": "clive-ia", "name": "Clive", "nearby": "Urbandale and West Des Moines"},
    {"slug": "johnston-ia", "name": "Johnston", "nearby": "Grimes and Urbandale"},
    {"slug": "waukee-ia", "name": "Waukee", "nearby": "Clive and Adel"},
    {"slug": "grimes-ia", "name": "Grimes", "nearby": "Johnston and Dallas Center"},
    {"slug": "pleasant-hill-ia", "name": "Pleasant Hill", "nearby": "Altoona and Des Moines"},
    {"slug": "norwalk-ia", "name": "Norwalk", "nearby": "West Des Moines and Cumming"},
    {"slug": "indianola-ia", "name": "Indianola", "nearby": "Carlisle and Norwalk"},
    {"slug": "carlisle-ia", "name": "Carlisle", "nearby": "Pleasant Hill and Indianola"},
    {"slug": "bondurant-ia", "name": "Bondurant", "nearby": "Altoona and Elkhart"},
    {"slug": "adel-ia", "name": "Adel", "nearby": "Dallas Center and Van Meter"},
    {"slug": "dallas-center-ia", "name": "Dallas Center", "nearby": "Grimes and Adel"},
    {"slug": "van-meter-ia", "name": "Van Meter", "nearby": "Waukee and Adel"},
    {"slug": "winterset-ia", "name": "Winterset", "nearby": "Earlham and Patterson"},
    {"slug": "perry-ia", "name": "Perry", "nearby": "Dallas Center and Minburn"},
    {"slug": "boone-ia", "name": "Boone", "nearby": "Ames and Ogden"},
    {"slug": "ames-ia", "name": "Ames", "nearby": "Gilbert and Nevada"},
    {"slug": "nevada-ia", "name": "Nevada", "nearby": "Ames and Maxwell"},
    {"slug": "huxley-ia", "name": "Huxley", "nearby": "Slater and Cambridge"},
    {"slug": "story-city-ia", "name": "Story City", "nearby": "Roland and Ames"},
    {"slug": "marshalltown-ia", "name": "Marshalltown", "nearby": "State Center and Melbourne"},
    {"slug": "newton-ia", "name": "Newton", "nearby": "Colfax and Baxter"},
    {"slug": "colfax-ia", "name": "Colfax", "nearby": "Prairie City and Mitchellville"},
    {"slug": "prairie-city-ia", "name": "Prairie City", "nearby": "Monroe and Colfax"},
    {"slug": "monroe-ia", "name": "Monroe", "nearby": "Prairie City and Reasnor"},
    {"slug": "pella-ia", "name": "Pella", "nearby": "Otley and New Sharon"},
    {"slug": "oskaloosa-ia", "name": "Oskaloosa", "nearby": "University Park and New Sharon"},
    {"slug": "grinnell-ia", "name": "Grinnell", "nearby": "Brooklyn and Newton"},
    {"slug": "knoxville-ia", "name": "Knoxville", "nearby": "Pella and Melcher-Dallas"},
    {"slug": "chariton-ia", "name": "Chariton", "nearby": "Corydon and Lucas"},
    {"slug": "madrid-ia", "name": "Madrid", "nearby": "Slater and Perry"},
    {"slug": "polk-city-ia", "name": "Polk City", "nearby": "Alleman and Ankeny"},
    {"slug": "slater-ia", "name": "Slater", "nearby": "Huxley and Madrid"},
    {"slug": "melbourne-ia", "name": "Melbourne", "nearby": "Marshalltown and Baxter"},
    {"slug": "baxter-ia", "name": "Baxter", "nearby": "Newton and Collins"},
    {"slug": "sully-ia", "name": "Sully", "nearby": "Lynnville and Grinnell"},
    {"slug": "lynnville-ia", "name": "Lynnville", "nearby": "Sully and Grinnell"},
    {"slug": "earlham-ia", "name": "Earlham", "nearby": "Stuart and Dexter"},
    {"slug": "redfield-ia", "name": "Redfield", "nearby": "Earlham and Dexter"},
    {"slug": "stuart-ia", "name": "Stuart", "nearby": "Redfield and Menlo"},
    {"slug": "greenfield-ia", "name": "Greenfield", "nearby": "Stuart and Fontanelle"},
    {"slug": "osceola-ia", "name": "Osceola", "nearby": "Murray and Saint Charles"},
    {"slug": "jefferson-ia", "name": "Jefferson", "nearby": "Grand Junction and Scranton"},
    {"slug": "eldora-ia", "name": "Eldora", "nearby": "Union and Iowa Falls"},
    {"slug": "belle-plaine-ia", "name": "Belle Plaine", "nearby": "Marengo and Tama"},
    {"slug": "corydon-ia", "name": "Corydon", "nearby": "Chariton and Allerton"},
]

def main():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    for city in cities:
        slug = city["slug"]
        name = city["name"]
        nearby = city["nearby"]

        html = (
            template
            .replace("{{CITY_NAME}}", name)
            .replace("{{CITY_SLUG}}", slug)
            .replace("{{NEARBY_TOWNS}}", nearby)
        )

        out_dir = os.path.join(OUTPUT_ROOT, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
