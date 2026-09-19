# מה יש בזה?

A Hebrew joke website. It pretends to be an online kosher-checking service run by
"HaRav Ezra שליט״א", a made-up rabbi who rules that everything is kosher. It is
aimed at Israelis travelling abroad. **It is for fun only** — every page says so.

Live at **https://mahyeshbeze.com**

The site is plain HTML files. There is no build step and nothing to install.
It runs on GitHub Pages and can be added to a phone's home screen like an app.

## The domain

The domain was bought at Wix, and Wix still holds it. Only its DNS records point
elsewhere, so this is where to look if the site ever stops loading:

- **In Wix** (Domains → ⋯ → Manage DNS Records): four A records on the main
  domain pointing to `185.199.108.153`, `.109.153`, `.110.153` and `.111.153`,
  and a CNAME on `www` pointing to `dsausen02-boop.github.io`.
- **In this repo**: the `CNAME` file holds `mahyeshbeze.com`. Deleting it
  disconnects the domain, so leave it alone.
- HTTPS is enforced, and `www` forwards to the plain domain.

After a DNS change, expect up to an hour before it takes effect everywhere. A
Wix page showing up instead of the site usually means an old lookup is still
cached, on your computer or at your internet provider.

## The pages

| File | What it is |
|---|---|
| `index.html` | Kashrut check. Upload a food photo, get a (random) "kosher" ruling with reasons and sources. |
| `torah.html` | Joke sayings for travellers, with topic filters. |
| `chagim.html` | Joke rulings for 13 holidays — at home and while travelling. A toggle at the top picks הכל / 🏠 בבית / ✈ בדרך, and the holiday chips under it narrow it further. |
| `giyur.html` | "Can they convert?" Pick gender and country, upload a photo, get a percentage and a timeline. |
| `harav.html` | About the rabbi: dancing animation, life story, famous rulings, books. |
| `shavua.html` | This week's essay, plus the archive of past weeks. The text comes from `week.json`, rewritten whenever you ask Claude for a fresh one. |

## The weekly essay

`shavua.html` shows one essay a week, in Rav Ezra's voice.

**How it gets written today: by asking Claude Code.** Say "refresh the weekly
essay" in a session. Claude checks Hebcal for the week's holiday or parasha,
looks up what's going on in Israel, writes the essay into `week.json` and
`weeks/<date>.json`, adds a line to `weeks/index.json`, and pushes. No API key
and no scheduled job — it happens when you ask.

There is also a GitHub Action that can do the same thing every Sunday on its
own. **It is switched off** (Actions tab → Weekly essay → shows "disabled").
To turn it on you need an `ANTHROPIC_API_KEY` secret, as described below;
without one it just fails and emails you.

**The moving parts**

| File | What it does |
|---|---|
| `scripts/weekly_essay.py` | Asks Hebcal what this week holds, then asks Claude for the essay. Only used by the Action, or by hand with an API key. |
| `.github/workflows/weekly-essay.yml` | The switched-off Sunday job. Enabling it needs an API key. |
| `week.json` | This week's essay. The page reads this. |
| `weeks/<date>.json` | One copy per week, kept forever. |
| `weeks/index.json` | The archive list the page shows at the bottom. |

**What the essay is about:** a holiday that week if there is one, otherwise the
weekly Torah portion, always tied to what's actually going on in Israel that
week — the weather, the markets, the traffic before a holiday.

**How it reads:** a long weekly letter from the rabbi to his students, about
1000-1400 Hebrew words, not a short column. Each one has:

| Part | What it is |
|---|---|
| `greeting` | He opens by addressing them directly, from his desk in Jerusalem. |
| `paragraphs` | 8-12 paragraphs. Somewhere in the middle he drops the jokes for a moment and says something plainly kind, then picks the humour back up. |
| `letter` | A question from one of his students, with his answer. |
| `ruling` | The week's mock ruling, in invented halachic language. |
| `israel` | Two or three things happening in Israel this week. |
| `closing` + `blessing` | A short ending and a personal blessing, with an invitation to write to him. |

The generator refuses an essay that comes back short, or without the greeting,
the letter or the blessing — those are what make it feel like their rabbi wrote
it rather than a website.

**What it stays away from:** war, politics, disasters and real people, by
instruction in the prompt. Days of mourning — Tisha B'Av, Yom HaShoah, Yom
HaZikaron — are never the subject: those weeks fall back to the parasha, and
the prompt tells the model not to mention the day at all and to keep a gentler
tone throughout.

**If you ever want it automatic:** add an Anthropic API key under Settings →
Secrets and variables → Actions → New repository secret, named
`ANTHROPIC_API_KEY`, then re-enable the workflow in the Actions tab. Cost is
roughly 15–30 cents a week — one Claude Opus request plus a few web searches.

**Running the script yourself** (needs the key too):

```bash
pip install anthropic tzdata && ANTHROPIC_API_KEY=... python scripts/weekly_essay.py --dry-run
```

`--dry-run` prints the essay without writing any files.

**If a week is missed,** nothing breaks: the page keeps showing the last essay
in `week.json` until a new one replaces it.

**Editing an essay by hand** is fine — `week.json` is plain text. Keep the same
fields, and edit `weeks/<date>.json` too if you want the archive to match.

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

- **2026-09-20** — Weekly essays are now long letters to his students: an opening
  address, 8-12 paragraphs, a question from a student with his answer, and a
  closing blessing. The page renders the new parts, the generator asks for them
  and refuses anything shorter. This week's essay rewritten in that form.
  Service worker `v12`.

- **2026-09-20** — New weekly page (`shavua.html`): one essay a week on the
  holiday or the parasha, tied to what's going on in Israel, with an archive of
  past weeks (`weeks/`). Written by asking Claude Code — no API key. The Sunday
  GitHub Action was built too but is switched off; it needs a key. First essay
  written by hand. Nav link on every page, app shortcut, service worker `v11`.

- **2026-09-20** — Connected the domain `mahyeshbeze.com` (bought at Wix) to
  GitHub Pages, with HTTPS enforced. The old `dsausen02-boop.github.io/mah-yesh-beze/`
  address now forwards to it.

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
