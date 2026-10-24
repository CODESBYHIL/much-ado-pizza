# Much Ado About Pizza: website redesign (demo)

A concept redesign for Much Ado About Pizza, Mission Plaza, Pleasanton CA. Built 2026-10-22 as a demo
for the owners, who OK'd sharing it on 2026-10-23. Live preview: https://codesbyhil.github.io/much-ado-pizza/
(GitHub Pages runs only the static page, so ordering there is always the demo; a bar at the top says so,
and search engines are asked not to list it).

Open `index.html` in a browser to see it. `process.html` shows how it was built and which skills did what.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The built site. Don't edit by hand; it is rebuilt from the two files below. |
| `index.src.html` | The page: layout, styles, scripts. Placeholders like `{{PIES}}` are filled by `build.py`. |
| `build.py` | The menu (pizzas, breads, salads, dips, prices) and the build. Run `python3 build.py`. |
| `server.mjs` | Serves the site and takes payment with Stripe inside the page. `node server.mjs`, then open http://localhost:4242. No packages. |
| `menu.json` | Written by `build.py`. The price list the server charges from (it never trusts prices from the browser). |
| `ring.py` | The hero's pizza wheel: which pies, their order, placement. Run `python3 ring.py`, then `build.py`. |
| `process.html` | Build notes: the dealt design direction, every inspector round, the Vercel audit, checklists. |
| `web/` | Web-sized photos (`name.jpg` large, `name-s.jpg` small). `img/` holds the originals from the shop's site. |
| `share/` | Walkthrough video (mp4 + gif) and a phone screenshot, for showing the site without a link. |
| `.taste-skill/` | Design direction sheet and inspector screenshots from each round. |
| `.audit/` | The Vercel Web Interface Guidelines audit findings. |

## Common changes

- **A price or pie changed:** edit `PIES` / `SIDES` in `build.py`, run `python3 build.py`. The "19 pies"
  headline counts itself.
- **Seasonal spotlight pies swapped:** they are the first rows of `PIES`.
- **A pie got a photo:** put it in `web/` as `name.jpg` and `name-s.jpg`, set the last field of its row in
  `build.py`, and add it to `ITEMS` + `TARGET` in `ring.py` if it should be on the wheel.
- **Check the design after a change:**
  `node ~/.claude/skills/design-taste-frontend/scripts/inspect.mjs index.html` (aim for 0 FAIL).

Menu copied from the live HungerRush ordering page on 2026-10-22. HungerRush has no link to a single
item (items open in a popup), so each menu row opens its HungerRush section (#pizzas, #appetizers,
#salads, #epicdips).

## Ordering on the page

Nobody leaves the site to order. Tapping a pie (in the menu or the wheel) opens a sheet with its photo,
style (Original round or Marlowe rectangle), any choices (sauce and up to 5 toppings for As You Like It,
the included dip for Bard Bread), a kitchen note and how many. "Your order" (bottom right; on a phone, the
red bar button) opens the bag: order → pickup (name, phone, a 15-minute slot on the next open days) → pay
→ done. The bag is remembered in the visitor's browser.

- **Demo mode** (opened as a file, or the server running without keys): the pay step says nothing is
  charged and places a pretend order. Nothing reaches the shop.
- **Real payments:** `STRIPE_SECRET_KEY=sk_test_... STRIPE_PUBLISHABLE_KEY=pk_test_... node server.mjs`.
  Stripe's own card form (cards, Apple Pay, Google Pay) loads inside the bag. Paid orders print in the
  terminal and append to `orders.jsonl`. Test card: 4242 4242 4242 4242, any future date, any CVC.

## Menu photos

Every pie and bread in the menu uses the shop's own item photo from its HungerRush ordering page
(originals in `img/hungerrush/`). `python3 photos.py` turns them into `web/hr/name.jpg` (3:2, for the
preview and the order sheet) and `name-s.jpg` (square thumbnail). They are only 600×300, so ask the
owners for the full-size files before launch. The hero wheel still uses the larger photos from their site.

## Bringing people back

- **Email and text signup** ("First to the next pie") and two opt-in boxes at checkout. With `server.mjs`
  running they are saved to `signups.jsonl` with the exact text-message consent wording; on GitHub Pages the
  form says it's a demo. Before launch: pick an email tool (Mailchimp, Klaviyo) and a texting tool (Klaviyo,
  Postscript, Twilio), register the texting number (US 10DLC), and add a privacy policy page.
- **Order again:** the last order is remembered in the visitor's browser and offered on the menu and in the bag.
- **Gift cards** ($25 / $50 / $100) go through the bag like food. Before launch the owners need a way to
  issue and redeem them (HungerRush or their POS gift cards).
- **Popular on Yelp** tags come from Yelp's Popular Dishes list (Montague, Taming of the Chew, Capulet,
  Bard Bread), and the 4.7 / 290 reviews line from their Yelp page, both read 2026-10-23. Update them now and then.
- Not done, needs the owners: photos or a short clip of the shop, the oven and the dough.

## Before launch

- **The kitchen must get the orders.** Today they come through HungerRush, which feeds the shop's POS.
  Paying on this site skips that, so before going live pick one: a Stripe webhook that prints/texts/emails
  each order to the shop, or keep HungerRush for the kitchen side. Decide this with the owners first.
- Sales tax: turn on Stripe Tax (or add a tax rate in `server.mjs`); the bag says tax is added at payment.
- Prices to confirm: extra dips ($1–$3, so they're paid at pickup for now), topping prices on As You Like It
  (charged at the $22 base for now), and whether the Marlowe rectangle costs the same as the round.
- To host it, the server needs a Node host (or the two `/api` routes moved to Vercel functions).

- Owners confirm prices and the photo-to-pie matches (Ham Let's photo was matched by toppings).
- Owners OK the use of their photos; low-res ones (Henry the 8, Viola's Veggie, Portia's) want replacing.

## How the website works (plain version)

The site is built so you can find anything and order in one or two taps.

1. **The top (the pizza wheel).** A ring of 11 real pizzas surrounds the shop's name. Point at one to
   see its name and price; click it to jump to that pie on the menu. A red Order for Pickup button sits
   in the middle, and a live line says whether they're open right now and how long is left to order
   before the 4pm dinner rush.
2. **The menu.** All 19 pizzas, all on sourdough, with real names, toppings and prices. A big photo stays
   put as you scroll and switches to whichever pie you point at. Tap a pie to order. Breads, salads and
   dips follow.
3. **The awards.** A moving band: Yelp Top 100 two years running, SF Gate Best of the Bay, and more.
4. **Catering.** Type how many guests; the site works out pizzas, breads and salads, and one tap opens a
   pre-written email to the shop.
5. **The family.** Kira and Mark, their kids, and their magazine cover.
6. **Visit.** Address, hours and phone in big type; tap for directions or to call; DoorDash and Uber Eats.

On a phone, a bar at the bottom always has Order Pickup, Call and Directions; it hides while you scroll
down and returns when you scroll up.

## How the pizza wheel works

The ring of 11 pizzas around the name shows only real pies from the menu, each in the shop's own photo
of that pie. Point at one and the others dim while its name and price appear. Click one and the page
scrolls to that exact pie on the menu, highlights it, and switches the big menu photo to it. Click the
pie's row to open the shop's ordering page. The ring scales as one piece so it never covers the text,
on any screen; on a phone the pizzas sit in two arcs above and below the name.
