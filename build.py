# Builds index.html from index.src.html: fills the ring, the menu rows and the proof band.
# Menu copied from the shop's live HungerRush menu on 2026-10-22. HungerRush has no link to a single item
# (items open in a popup), so each row links to the HungerRush section it lives in.
import html, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
ORDER = "https://muchadoaboutpizza.hungerrush.com/Order/Menu/1"

PIES = [  # sauce, name, toppings, price, photo (only where the shop's own photo is named after the pie)
    ("White garlic", "Shake-ula", "Spotlight, vegetarian. Italian cheese blend under splatters of the award-winning red sauce", "$22", None),
    ("Pesto", "Frankenspeare", "Spotlight. Italian sausage, red onion, mushrooms", "$28", None),
    ("White garlic", "Alls Well In The End Zone", "Spotlight, limited time. Goat cheese, bacon, red onion, jalapeños", "$30", None),
    ("Red", "Much Ado Original Cheese", "House tomato sauce, Italian cheese blend, fresh basil", "$22", "orig"),
    ("Your pick", "As You Like It", "Build your own: one of 3 sauces, the 5-cheese blend, up to 5 toppings. No half and half", "from $22", None),
    ("Pesto", "Groundling", "Vegetarian. Italian cheese blend, fresh cherry tomatoes", "$24", "groundling"),
    ("Red", "Taming of the Chew", "An epic amount of pepperoni. Ask for the “Kiss Me Kate” to add jalapeños", "$25", "taming"),
    ("Red", "Capulet", "Vegetarian margherita. Goat cheese, mozzarella, cherry tomatoes, fresh basil", "$25", None),
    ("Red", "Tempest", "Vegetarian. Goat cheese, pineapple, black olives", "$28", "tempest"),
    ("Red", "Quatrain", "Vegetarian. Black olives, baby bella mushrooms, green peppers, red onion", "$28", "quatrain"),
    ("White garlic", "Fowl-Staff", "Truffle cheese, roasted chicken, mushrooms, red onion", "$29", None),
    ("Red", "Montague", "Truffle cheese, pepperoni, Italian sausage, mushroom", "$30", None),
    ("White garlic", "Viola’s Veggie", "Award-winning, vegetarian. Spinach, basil, truffle cheese, seasonal squash, red onion", "$30", "viola"),
    ("Red", "Ham Let", "Prosciutto, ham, pineapple, green peppers, finished with arugula and baby bell peppers", "$32", "polish2022"),
    ("Pesto", "O’Thello’s O’bsession", "Vegetarian. Spinach, seasonal squash, red onion, broccoli, arugula, baby bell peppers", "$32", None),
    ("Pesto", "Portia’s Pesto Pizza", "Roasted chicken, bacon, spinach, red onion, cherry tomatoes", "$32", "portia"),
    ("Red and garlic", "Titania’s Bounty", "Vegetarian, two sauces. Squash, olives, onion, peppers, broccoli, fresh greens and tomatoes", "$32", "titania"),
    ("Red", "Act Five", "The combo. Pepperoni, Italian sausage, mushrooms, green peppers, red onion", "$33", "act5"),
    ("Red", "Henry the 8", "Cup-and-char pepperoni, Italian sausage, mushrooms, black olives, red onion, green peppers", "$35", "henry8"),
]
SIDES = [  # kind, name, what, price, photo, HungerRush section
    ("Bread", "Cheesy “Bard” Bread", "Garlic EVOO, Italian herbs and cheese, with one epic dip", "$8", "p20221126", "appetizers"),
    ("Bread", "Stuffed Cheesy Bread", "The Bard, stuffed with mozzarella and Provo-nello", "$12", "p20231017", "appetizers"),
    ("Bread", "Stuffed Jalapeño, Bacon", "Stuffed with cheese, bacon and pickled jalapeños", "$14", None, "appetizers"),
    ("Bread", "Stuffed Spinach, Goat", "Stuffed with cheese, goat cheese and spinach", "$14", None, "appetizers"),
    ("Green room", "Individual Salad", "Seasonal greens, green onion, cherry tomatoes, 1 dressing. Feeds 1–2", "$6", "salad", "salads"),
    ("Green room", "Family Salad", "The same, to share. Feeds 3–4", "$10", "salad", "salads"),
    ("Dips", "Epic Dips", "Much Ado red, Benedick white garlic, Beatrice pesto, hot honey, salsa Parmesan, Don Rancho garlic ranch, jalapeño ranch, ranch", "$1–$3", "p20230429", "epicdips"),
]
NAMES = ["Yelp Top 100, 2024", "Yelp Top 100, 2025", "SF Gate Best of the Bay", "U.S. Pizza Team",
         "International Pizza Challenge", "California Pizza Challenge", "PMQ cover story"]


def slug(name):
    return 'pie-' + re.sub(r'[^a-z0-9]+', '-', name.lower().replace('’', '').replace('“', '').replace('”', '')).strip('-')


def row(kind, name, what, price, img, section):
    e = html.escape
    pic = f' data-img="web/{img}.jpg" data-cap="{e(name)}, {e(price)}"' if img else ''
    return (f'<li id="{slug(name)}"><a href="{ORDER}#{section}"{pic}><span class="kind">{e(kind)}</span><span><span class="name" translate="no">{e(name)}</span>'
            f'<span class="what">{e(what)}</span></span><span class="price num">{e(price)}<span class="arr" aria-hidden="true">→</span></span></a></li>')


src = open(os.path.join(ROOT, "index.src.html"), encoding="utf-8").read()
ring = open(os.path.join(ROOT, "ring.html"), encoding="utf-8").read().strip()
out = (src.replace("{{RING}}", ring)
          .replace("{{PIES}}", "\n          ".join(row(*p, "pizzas") for p in PIES))
          .replace("{{SIDES}}", "\n          ".join(row(*s) for s in SIDES))
          .replace("{{COUNT}}", str(len(PIES)))
          .replace("{{NAMES}}", "".join(f"<span>{html.escape(n)}</span>" for n in NAMES))
          .replace("{{ORDER}}", ORDER))
assert "{{" not in out
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
print("built index.html", len(out), "bytes,", len(PIES), "pies")
