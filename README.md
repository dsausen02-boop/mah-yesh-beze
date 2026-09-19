# מה יש בזה?

A Hebrew joke website. It pretends to be an online kosher-checking service run by
"HaRav Ezra שליט״א", a made-up rabbi who rules that everything is kosher. It is
aimed at Israelis travelling abroad. **It is for fun only** — every page says so.

The site is plain HTML files. There is no build step and nothing to install.
It runs on GitHub Pages and can be added to a phone's home screen like an app.

## The pages

| File | What it is |
|---|---|
| `index.html` | Kashrut check. Upload a food photo, get a (random) "kosher" ruling with reasons and sources. |
| `torah.html` | Joke sayings for travellers, with topic filters. |
| `chagim.html` | Joke rulings for 13 holidays — at home and while travelling. A toggle at the top picks הכל / 🏠 בבית / ✈ בדרך, and the holiday chips under it narrow it further. |
| `giyur.html` | "Can they convert?" Pick gender and country, upload a photo, get a percentage and a timeline. |
| `harav.html` | About the rabbi: dancing animation, life story, famous rulings, books. |

## How it is put together

- **Each page is self-contained.** Styles, scripts and pictures are all inside the
  HTML file. Pictures are stored as long text strings (`data:image/...`), which is
  why each page is 250–360 KB.
- **The bottom of every page is the same shared block** (about 650 lines). It
  holds the live counters, sound effects, the "ask the rabbi" chat, WhatsApp
  sharing and the certificate download. Pages use it through `window.MYB`.
- **The chat is simple keyword matching.** It checks the question against the
  `TOPICS` list and uses the first topic that matches. If nothing matches, it
  picks a random general answer from `GENERIC`.
- `sw.js` lets the site work offline. It always tries the internet first and only
  uses the saved copy when offline.

## When you change something

1. **Changing the shared block?** Make the exact same change in all five pages.
   They must stay identical.
2. **In the chat `TOPICS` list, put longer phrases before shorter ones.** For
   example, "בשר וחלב" must come before "בשר" and "חלב", or it will never be used.
3. **Bump the version in `sw.js`** (for example `v8` → `v9`) after any change, or
   people who installed the app may keep seeing the old version.
4. **New page?** Add it to the menu in every page, to `ASSETS` in `sw.js`, to
   `shortcuts` in `manifest.json`, and give it its own greeting and suggested
   questions in the chat (`PAGE`, `GREET`, `CHIPS`).

## Adding a card to the holidays page

Copy an existing `saying-card` block in `chagim.html` and put it in the right
holiday section, after the cards already there. The `data-topics` attribute
decides where it shows up:

- the holiday name, for example `pesach`, for the holiday chips;
- add `home` if it is about life at home — for example `data-topics="pesach home"`.
  A card without `home` counts as a travel card ("✈ בדרך").

All counts on the page are worked out when it loads, so you never edit numbers
by hand. A holiday heading hides itself when none of its cards are showing.

**New holiday?** Add a `section-divider` heading, its cards, and a
`filter-chip` button with the same name in `data-filter`.

**How the filters work:** the toggle (הכל / בבית / בדרך) and the holiday chip
are separate choices, and a card shows only if it matches both. Changing one
keeps the other — so "Pesach" stays picked when you switch from home to travel.

Tisha B'Av only has travel cards on purpose. It is a day of mourning, so it
was left out of the home-life jokes. Picking it with "בבית" shows a short
message explaining that.

## Line endings

The HTML pages use Windows line endings (CRLF). `sw.js` and `manifest.json` use
plain LF. Keep each file the way it is, so diffs only show real changes.
Careful: `sed -i` in Git Bash on Windows quietly turns CRLF into LF, so use a
proper editor or a script that keeps the endings.

## Running it on your computer

Service workers do not run from a double-clicked file, so use a small local server:

```bash
python -m http.server 8395
```

Then open http://localhost:8395.

## Change log

- **2026-09-20** — Holidays page filters rebuilt. The "🏠 בבית" chip looked broken:
  it did filter, but every holiday heading stayed on screen (even ones with no
  home cards), and picking a holiday switched it off. Now there is a toggle at
  the top (הכל / 🏠 בבית / ✈ בדרך) that works together with the holiday chips,
  empty headings hide, and every chip shows its count for the current choice.
  Added 33 more home cards: three more for each of the seven main holidays, two
  more each for Shavuot, Tu BiShvat and Lag BaOmer, and two new holidays with
  three cards each — Simchat Torah and Yom HaAtzmaut. 74 cards in total (53 at
  home, 21 travel). Also put back the page's CRLF line endings, which the
  previous change had switched to LF by accident. Service worker is now `v10`.

- **2026-09-19** — Holidays page is no longer only about travel. Added 14 home-life
  cards to the existing holidays (Yom Kippur, Pesach, Shabbat, Sukkot, Rosh
  Hashana, Chanuka, Purim) and three new holidays with two cards each: Shavuot,
  Tu BiShvat and Lag BaOmer. Added a "🏠 בבית" filter. The page title, the
  "about" box and the app shortcut now say "at home and on the road". The
  Shabbat section is now just "שבת". 41 cards in total. Service worker is now `v9`.

- **2026-09-19** — Fixed the chat so the "meat and milk" answer shows up (it was
  hidden behind the separate meat and milk answers). The chat now knows the rabbi
  page and has its own greeting and questions there. Sharing a holiday ruling now
  says "עוד פסקים לחגים בחו״ל" instead of the Torah page's text. The giyur timeline
  no longer shows "5–5 שנים", and its certificate now shows the same years as the
  page. Removed two empty country entries, the unused `harav-ezra.jpg`, and an
  accidentally uploaded project zip. Service worker is now `v8`.
