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
| `chagim.html` | Joke rulings for holidays and fasts while travelling, with holiday filters. |
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

## Running it on your computer

Service workers do not run from a double-clicked file, so use a small local server:

```bash
python -m http.server 8395
```

Then open http://localhost:8395.

## Change log

- **2026-09-19** — Fixed the chat so the "meat and milk" answer shows up (it was
  hidden behind the separate meat and milk answers). The chat now knows the rabbi
  page and has its own greeting and questions there. Sharing a holiday ruling now
  says "עוד פסקים לחגים בחו״ל" instead of the Torah page's text. The giyur timeline
  no longer shows "5–5 שנים", and its certificate now shows the same years as the
  page. Removed two empty country entries, the unused `harav-ezra.jpg`, and an
  accidentally uploaded project zip. Service worker is now `v8`.
