#!/usr/bin/env python3
"""Write this week's essay for מה יש בזה?

Run weekly by .github/workflows/weekly-essay.yml, or by hand:

    pip install anthropic
    ANTHROPIC_API_KEY=... python scripts/weekly_essay.py          # write the files
    ANTHROPIC_API_KEY=... python scripts/weekly_essay.py --dry-run  # print, write nothing

What it does:
  1. Asks Hebcal what this week holds: the Hebrew date, any holiday, the parasha.
  2. Asks Claude for an essay in HaRav Ezra's voice, with web search on so it can
     mention what is actually going on in Israel that week.
  3. Writes week.json (what the page shows), weeks/<date>.json (the archive copy)
     and weeks/index.json (the archive list).

The essay is satire, like the rest of the site. The prompt keeps it to everyday
life — food, weather, family, traffic — and away from war, politics and grief.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zoneinfo

import anthropic

MODEL = "claude-opus-5"
try:
    ISRAEL = zoneinfo.ZoneInfo("Asia/Jerusalem")
except zoneinfo.ZoneInfoNotFoundError:
    # Windows ships no time-zone database. `pip install tzdata` fixes it properly;
    # until then fall back to a fixed +3, which is right for picking today's date.
    ISRAEL = dt.timezone(dt.timedelta(hours=3), "Asia/Jerusalem (approx)")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEEKS_DIR = os.path.join(ROOT, "weeks")
HEBCAL = "https://www.hebcal.com"
SITE = "https://mahyeshbeze.com"

# Days the site does not joke about. A week holding one of these writes about the
# parasha instead, and the essay is asked for a gentler tone.
SOLEMN = ["תשעה באב", "יום הזיכרון", "יום הזכרון", "יום השואה", "יום הקדיש"]

# Hebcal marks Chanuka, Pesach and the like as "major", and the ordinary fasts as
# "fast" — both make good topics. "minor" and "modern" days mostly don't, so only
# these light ones are allowed through; the rest ride along as background.
LIGHT_MINOR = ["ל״ג בעומר", "ט״ו בשבט", "יום העצמאות", "ט״ו באב", "ראש חודש"]


# ─────────────────────────── the Hebrew calendar ───────────────────────────

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mah-yesh-beze/1.0 (+%s)" % SITE})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def week_of(today):
    """The Hebrew week runs Sunday to Saturday. Returns (sunday, saturday)."""
    sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
    return sunday, sunday + dt.timedelta(days=6)


def calendar_for(start, end):
    """Holidays and the parasha between two dates, in Hebrew, Israel schedule."""
    q = urllib.parse.urlencode({
        "v": 1, "cfg": "json", "maj": "on", "min": "on", "mod": "on", "ss": "on",
        "mf": "on", "s": "on", "i": "on", "lg": "h", "nx": "off",
        "start": start.isoformat(), "end": end.isoformat(),
    })
    return fetch_json(f"{HEBCAL}/hebcal?{q}").get("items", [])


def hebrew_date(day):
    q = urllib.parse.urlencode({"cfg": "json", "date": day.isoformat(), "g2h": 1, "strict": 1})
    d = fetch_json(f"{HEBCAL}/converter?{q}")
    return d.get("hebrew", ""), d.get("hy")


def is_solemn(name):
    return any(s in (name or "") for s in SOLEMN)


def pick_topic(items):
    """A holiday worth writing about wins; otherwise the parasha.

    'Erev' days are skipped when the holiday itself falls in the same week, so
    the essay is about Sukkot rather than the day before Sukkot.
    """
    holidays = [i for i in items if i.get("category") == "holiday"]
    names = [i.get("hebrew") or i.get("title") for i in holidays if i.get("hebrew") or i.get("title")]

    def usable(item):
        name = item.get("hebrew") or item.get("title") or ""
        if is_solemn(name):
            return False
        if item.get("subcat") in ("major", "fast"):
            return True
        return any(k in name for k in LIGHT_MINOR)

    candidates = [i.get("hebrew") or i.get("title") for i in holidays if usable(i)]
    main = next((n for n in candidates if not n.startswith("ערב ")), None) or \
        (candidates[0] if candidates else None)

    solemn_here = [n for n in names if is_solemn(n)]
    if main:
        return {"topic_type": "holiday", "topic_name": main,
                "all_holidays": names, "solemn": bool(solemn_here), "avoid": solemn_here}

    parasha = next((i for i in items if i.get("category") == "parashat"), None)
    name = (parasha.get("hebrew") if parasha else "") or "פרשת השבוע"
    return {"topic_type": "parasha", "topic_name": name, "all_holidays": names,
            "solemn": bool(solemn_here), "avoid": solemn_here}


# ─────────────────────────────── the essay ───────────────────────────────

SYSTEM = """\
אתה כותב עבור אתר הסאטירה העברי ״מה יש בזה?״ — בית הוראה מומצא בהנהגת ״הגאון הרב \
עזרא שליט״א״, פוסק בדיוני שתמיד מוצא היתר, אוהב אוכל, ומספר סיפורים על הרבנית, \
הנכדים והשכנה מהקומה השנייה.

הקול של הרב עזרא:
- גוף ראשון, חם, מתלוצץ על עצמו, לעולם לא מתנשא ולא לועג למאמינים.
- מביא ״מקורות״ מומצאים בשמות משעשעים (שו״ת ״קנה ותנסה״, ״לאכול ולחיות״).
- פסקיו תמיד לקולא, והנימוק תמיד נשמע הגיוני עד השורה האחרונה.
- מדבר עברית יומיומית וזורמת, לא מליצית.

כללים שאסור לעבור עליהם:
- זו סאטירה על פוסק מומצא, לא על ההלכה עצמה ולא על אנשים אמיתיים. אין להזכיר \
רבנים, פוליטיקאים או אישי ציבור אמיתיים בשמם.
- אין לכתוב על מלחמה, נפגעים, פיגועים, אסונות, פוליטיקה מפלגתית, או כל נושא \
שיש בו כאב אמיתי. אם השבוע בישראל עמוס באירועים כאלה — פשוט אל תיגע בהם, וכתוב \
על מזג האוויר, האוכל, העומס בכבישים, החגים, הספורט או החיים בבית.
- אין לתת פסק הלכה אמיתי. הכל בדיחה.
- אין להמציא ידיעות חדשותיות. כשאתה מזכיר משהו שקורה בישראל — הסתמך רק על מה \
שמצאת בחיפוש, וכתוב על זה בקלילות ובלי לצטט מספרים מדויקים.
"""

USER = """\
כתוב את ״מאמר השבוע״ של הרב עזרא לשבוע הקרוב.

נתוני השבוע:
- תאריך עברי בתחילת השבוע: {hebrew_date}
- תאריכים לועזיים: {start} עד {end}
- הנושא: {topic_kind} — {topic_name}
{holidays_line}

שלב א׳ — חיפוש: חפש באינטרנט 2–3 דברים קלילים שקורים בישראל בשבוע הזה (מזג אוויר \
ועונה, מחירים בשוק, עומסי תנועה לקראת החג, אירועי ספורט או תרבות, שעון קיץ/חורף, \
פתיחת שנת הלימודים וכדומה). התעלם מכל מה שנוגע למלחמה, פוליטיקה או אסון.

שלב ב׳ — כתוב מאמר של 500–700 מילים בעברית, בקול של הרב עזרא, שמחבר בין הנושא של \
השבוע לבין מה שמצאת. שלב את פרטי המציאות באופן טבעי — לא כרשימה.

החזר אך ורק JSON תקין (בלי טקסט לפני או אחרי, בלי גדרות קוד), במבנה הזה:

{{
  "title": "כותרת המאמר, עד 6 מילים",
  "dek": "משפט אחד שמסביר על מה המאמר",
  "paragraphs": ["פסקה", "פסקה", "..."],
  "ruling": {{"text": "פסק קצר בלשון הלכתית מומצאת עם ניקוד חלקי", "source": "שם מקור מומצא"}},
  "israel": ["מה שקורה בישראל השבוע, משפט לכל פריט", "..."],
  "closing": "משפט סיום אחד",
  "sources": ["כתובת אתר שהסתמכת עליה", "..."]
}}

הנחיות למבנה: 5–7 פסקאות. "israel" — 2 עד 3 פריטים קצרים. "sources" — הכתובות \
שמהן לקחת את מה שקורה בישראל.{tone_line}
"""


def build_prompt(info, hebdate, start, end):
    holidays = [h for h in info["all_holidays"] if h and h != info["topic_name"]]
    return USER.format(
        hebrew_date=hebdate,
        start=start.isoformat(),
        end=end.isoformat(),
        topic_kind="חג" if info["topic_type"] == "holiday" else "פרשת השבוע",
        topic_name=info["topic_name"],
        holidays_line=("- גם בשבוע הזה: " + ", ".join(holidays)) if holidays else "",
        tone_line=(
            "\n\nשים לב: בשבוע הזה חל " + ", ".join(info.get("avoid") or []) +
            ". אל תכתוב עליו, אל תתלוצץ עליו ואל תזכיר אותו כלל. שמור על טון "
            "עדין יותר לאורך כל המאמר, והתלוצץ רק על עצמך ועל הרגלי הבית."
            if info.get("solemn") else ""
        ),
    )


def extract_json(text):
    """The model is asked for bare JSON; be forgiving if it wraps it anyway."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in the reply")
    return json.loads(text[start:end + 1])


def ask_claude(client, prompt):
    """One request, with web search on. Falls back if the beta isn't available."""
    kwargs = dict(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[{
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": 6,
            "user_location": {
                "type": "approximate",
                "country": "IL",
                "city": "Jerusalem",
                "timezone": "Asia/Jerusalem",
            },
        }],
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        with client.beta.messages.stream(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        ) as stream:
            message = stream.get_final_message()
    except anthropic.BadRequestError:
        # The refusal-fallback beta isn't on for this account; run without it.
        with client.messages.stream(**kwargs) as stream:
            message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise RuntimeError("the model declined this prompt: %s" % message.stop_details)
    text = "".join(b.text for b in message.content if b.type == "text")
    if not text.strip():
        raise RuntimeError("empty reply (stop_reason=%s)" % message.stop_reason)
    return extract_json(text)


def validate(essay):
    for key in ("title", "dek", "paragraphs", "ruling", "closing"):
        if not essay.get(key):
            raise ValueError(f"the essay is missing '{key}'")
    if not isinstance(essay["paragraphs"], list) or len(essay["paragraphs"]) < 3:
        raise ValueError("expected at least 3 paragraphs")
    essay.setdefault("israel", [])
    essay.setdefault("sources", [])
    return essay


# ─────────────────────────────── writing out ───────────────────────────────

def write_files(essay, dry_run=False):
    if dry_run:
        print(json.dumps(essay, ensure_ascii=False, indent=2))
        return
    os.makedirs(WEEKS_DIR, exist_ok=True)
    blob = json.dumps(essay, ensure_ascii=False, indent=2) + "\n"
    # newline="\n" keeps the JSON files LF on every machine, like the rest of the repo
    with open(os.path.join(ROOT, "week.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(blob)
    with open(os.path.join(WEEKS_DIR, essay["week_start"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(blob)

    index_path = os.path.join(WEEKS_DIR, "index.json")
    index = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    index = [e for e in index if e.get("week_start") != essay["week_start"]]
    index.insert(0, {
        "week_start": essay["week_start"],
        "hebrew_date": essay.get("hebrew_date", ""),
        "topic_name": essay.get("topic_name", ""),
        "topic_type": essay.get("topic_type", ""),
        "title": essay["title"],
    })
    index.sort(key=lambda e: e["week_start"], reverse=True)
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote week.json and weeks/{essay['week_start']}.json ({len(index)} in the archive)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the essay, write nothing")
    ap.add_argument("--date", help="pretend today is this date (YYYY-MM-DD)")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(ISRAEL).date()
    start, end = week_of(today)
    items = calendar_for(start, end)
    info = pick_topic(items)
    hebdate, hyear = hebrew_date(start)
    print(f"week {start}..{end} | {hebdate} | {info['topic_type']}: {info['topic_name']}",
          file=sys.stderr)

    client = anthropic.Anthropic()
    essay = validate(ask_claude(client, build_prompt(info, hebdate, start, end)))
    essay.update({
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "generated_at": dt.datetime.now(ISRAEL).isoformat(timespec="seconds"),
        "hebrew_date": hebdate,
        "hebrew_year": hyear,
        "topic_type": info["topic_type"],
        "topic_name": info["topic_name"],
        "model": MODEL,
    })
    write_files(essay, args.dry_run)


if __name__ == "__main__":
    main()
