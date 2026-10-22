# Much Ado About Pizza: website redesign (demo)

A concept redesign for Much Ado About Pizza, Mission Plaza, Pleasanton CA. Built 2026-10-22 as a demo
for the owners. **Not published anywhere**: it carries the shop's real name, logo, photos and live
ordering links, so it goes online only with the owners' OK.

Open `index.html` in a browser to see it. `process.html` shows how it was built and which skills did what.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The built site. Don't edit by hand; it is rebuilt from the two files below. |
| `index.src.html` | The page: layout, styles, scripts. Placeholders like `{{PIES}}` are filled by `build.py`. |
| `build.py` | The menu (pizzas, breads, salads, dips, prices) and the build. Run `python3 build.py`. |
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

## Before launch

- Owners confirm prices and the photo-to-pie matches (Ham Let's photo was matched by toppings).
- Owners OK the use of their photos; low-res ones (Henry the 8, Viola's Veggie, Portia's) want replacing.
- 8 pies have no photo yet: Shake-ula, Frankenspeare, Alls Well In The End Zone, As You Like It,
  Capulet, Fowl-Staff, Montague, O'Thello's O'bsession.

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
