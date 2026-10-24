# Builds index.html from index.src.html: fills the ring, the menu rows and the proof band, and writes
# menu.json, the price list the checkout server trusts (it never takes prices from the browser).
# Menu copied from the shop's live HungerRush menu on 2026-10-22. HungerRush has no link to a single item
# (items open in a popup), so each row links to the HungerRush section it lives in.
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
ORDER = "https://muchadoaboutpizza.hungerrush.com/Order/Menu/1"

PIES = [  # sauce, name, toppings, price, photo (the shop's own item photo from HungerRush, see photos.py)
    ("White garlic", "Shake-ula", "Spotlight, vegetarian. Italian cheese blend under splatters of the award-winning red sauce", "$22", "hr/shakeula"),
    ("Pesto", "Frankenspeare", "Spotlight. Italian sausage, red onion, mushrooms", "$28", "hr/frankenspeare"),
    ("White garlic", "Alls Well In The End Zone", "Spotlight, limited time. Goat cheese, bacon, red onion, jalapeños", "$30", "hr/allswellintheendzone"),
    ("Red", "Much Ado Original Cheese", "House tomato sauce, Italian cheese blend, fresh basil", "$22", "hr/theoriginalpizza"),
    ("Your pick", "As You Like It", "Build your own: one of 3 sauces, the 5-cheese blend, up to 5 toppings. No half and half", "from $22", "hr/asyoulikeitpizza"),
    ("Pesto", "Groundling", "Vegetarian. Italian cheese blend, fresh cherry tomatoes", "$24", "hr/thegroundlingpizza"),
    ("Red", "Taming of the Chew", "An epic amount of pepperoni. Ask for the “Kiss Me Kate” to add jalapeños", "$25", "hr/tamingofthechewpizza"),
    ("Red", "Capulet", "Vegetarian margherita. Goat cheese, mozzarella, cherry tomatoes, fresh basil", "$25", "hr/capuletpizza"),
    ("Red", "Tempest", "Vegetarian. Goat cheese, pineapple, black olives", "$28", "hr/tempestpizza"),
    ("Red", "Quatrain", "Vegetarian. Black olives, baby bella mushrooms, green peppers, red onion", "$28", "hr/thequatrainpizza"),
    ("White garlic", "Fowl-Staff", "Truffle cheese, roasted chicken, mushrooms, red onion", "$29", "hr/fowlstaffpizza"),
    ("Red", "Montague", "Truffle cheese, pepperoni, Italian sausage, mushroom", "$30", "hr/montaguepizza"),
    ("White garlic", "Viola’s Veggie", "Award-winning, vegetarian. Spinach, basil, truffle cheese, seasonal squash, red onion", "$30", "hr/violasvegpizza"),
    ("Red", "Ham Let", "Prosciutto, ham, pineapple, green peppers, finished with arugula and baby bell peppers", "$32", "hr/hamletpizza"),
    ("Pesto", "O’Thello’s O’bsession", "Vegetarian. Spinach, seasonal squash, red onion, broccoli, arugula, baby bell peppers", "$32", "hr/othellospizza"),
    ("Pesto", "Portia’s Pesto Pizza", "Roasted chicken, bacon, spinach, red onion, cherry tomatoes", "$32", "hr/portiaspestopizza"),
    ("Red and garlic", "Titania’s Bounty", "Vegetarian, two sauces. Squash, olives, onion, peppers, broccoli, fresh greens and tomatoes", "$32", "hr/titaniasbountypizza"),
    ("Red", "Act Five", "The combo. Pepperoni, Italian sausage, mushrooms, green peppers, red onion", "$33", "hr/actfivepizza"),
    ("Red", "Henry the 8", "Cup-and-char pepperoni, Italian sausage, mushrooms, black olives, red onion, green peppers", "$35", "hr/henrythe8pizza"),
]
SIDES = [  # kind, name, what, price, photo, HungerRush section
    ("Bread", "Cheesy “Bard” Bread", "Garlic EVOO, Italian herbs and cheese, with one epic dip", "$8", "hr/garlicbread", "appetizers"),
    ("Bread", "Stuffed Cheesy Bread", "The Bard, stuffed with mozzarella and Provo-nello", "$12", "hr/stuffedcheezybread", "appetizers"),
    ("Bread", "Stuffed Jalapeño, Bacon", "Stuffed with cheese, bacon and pickled jalapeños", "$14", "hr/stuffedjalapenobread", "appetizers"),
    ("Bread", "Stuffed Spinach, Goat", "Stuffed with cheese, goat cheese and spinach", "$14", "hr/stuffedspinachbread", "appetizers"),
    ("Green room", "Individual Salad", "Seasonal greens, green onion, cherry tomatoes, 1 dressing. Feeds 1–2", "$6", "salad", "salads"),
    ("Green room", "Family Salad", "The same, to share. Feeds 3–4", "$10", "salad", "salads"),
    ("Dips", "Epic Dips", "Much Ado red, Benedick white garlic, Beatrice pesto, hot honey, salsa Parmesan, Don Rancho garlic ranch, jalapeño ranch, ranch", "$1–$3", "p20230429", "epicdips"),
]
SAUCES = ["Red", "White garlic", "Pesto"]
TOPPINGS = ["Pepperoni", "Italian sausage", "Bacon", "Ham", "Prosciutto", "Roasted chicken", "Mushrooms",
            "Red onion", "Green peppers", "Black olives", "Pineapple", "Jalapeños", "Spinach", "Broccoli",
            "Cherry tomatoes", "Seasonal squash", "Goat cheese", "Truffle cheese", "Arugula", "Fresh basil"]
DIPS = ["Much Ado red", "Benedick white garlic", "Beatrice pesto", "Hot honey", "Salsa Parmesan",
        "Don Rancho garlic ranch", "Jalapeño ranch", "Ranch"]
STYLES = ["Original, 14-inch round", "Marlowe, 13×9 rectangle"]
NAMES = ["Yelp Top 100, 2024", "Yelp Top 100, 2025", "SF Gate Best of the Bay", "U.S. Pizza Team",
         "International Pizza Challenge", "California Pizza Challenge", "PMQ cover story"]


def slug(name):
    return 'pie-' + re.sub(r'[^a-z0-9]+', '-', name.lower().replace('’', '').replace('“', '').replace('”', '')).strip('-')


def cents(price):
    """'$22' and 'from $22' -> 2200; a range like '$1–$3' has no single price, so it can't go in the cart."""
    m = re.fullmatch(r'(?:from )?\$(\d+)', price)
    return int(m.group(1)) * 100 if m else None


def item(kind, name, what, price, img, section):
    it = {"id": slug(name), "kind": kind, "name": name, "what": what, "price": price, "cents": cents(price),
          "img": img, "section": section, "opts": {}}
    if section == "pizzas":
        it["opts"]["style"] = STYLES
    if name == "As You Like It":
        it["opts"].update(sauce=SAUCES, toppings=TOPPINGS)
    if "Bard" in name:
        it["opts"]["dip"] = DIPS
    return it


def row(it):
    e = html.escape
    pic = f' data-img="web/{it["img"]}.jpg"' if it["img"] else ''
    thumb = (f'<img src="web/{it["img"]}-s.jpg" alt="" width="64" height="64" loading="lazy">' if it["img"]
             else '')
    return (f'<li id="{it["id"]}"><a href="{ORDER}#{it["section"]}" data-item="{it["id"]}"{pic} data-cap="{e(it["name"])}, {e(it["price"])}">'
            f'<span class="thumb" aria-hidden="true">{thumb}</span><span class="kind">{e(it["kind"])}</span><span><span class="name" translate="no">{e(it["name"])}</span>'
            f'<span class="what">{e(it["what"])}</span></span><span class="price num">{e(it["price"])}<span class="arr" aria-hidden="true">→</span></span></a></li>')


pies = [item(*p, "pizzas") for p in PIES]
sides = [item(*x) for x in SIDES]
menu = {it["id"]: it for it in pies + sides}
open(os.path.join(ROOT, "menu.json"), "w", encoding="utf-8").write(json.dumps(menu, ensure_ascii=False, indent=1))

# the menu preview: one stacked layer per photo, so pointing at a row only switches which layer shows
shots = list(dict.fromkeys(it["img"] for it in pies + sides if it["img"]))
preview = "".join(f'<img data-for="{s}" src="web/{s}.jpg" alt="" width="900" height="600" loading="lazy" decoding="async"{" class=on" if s == "hr/hamletpizza" else ""}>' for s in shots)

src = open(os.path.join(ROOT, "index.src.html"), encoding="utf-8").read()
ring = open(os.path.join(ROOT, "ring.html"), encoding="utf-8").read().strip()
out = (src.replace("{{RING}}", ring)
          .replace("{{PIES}}", "\n          ".join(row(it) for it in pies))
          .replace("{{SIDES}}", "\n          ".join(row(it) for it in sides))
          .replace("{{MENU}}", json.dumps(menu, ensure_ascii=False).replace("</", "<\\/"))
          .replace("{{COUNT}}", str(len(PIES)))
          .replace("{{PREVIEW}}", preview)
          .replace("{{NAMES}}", "".join(f"<span>{html.escape(n)}</span>" for n in NAMES))
          .replace("{{ORDER}}", ORDER))
assert "{{" not in out
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
print("built index.html", len(out), "bytes,", len(PIES), "pies")
