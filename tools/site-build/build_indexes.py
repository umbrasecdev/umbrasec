#!/usr/bin/env python3
"""
build_indexes.py - regenerate every derived list on the UMBRASEC site from the
single source of truth at research/articles.json.

What it owns (and nothing else):
  - index.html .............. the homepage "featured" trio (latest 3 articles)
  - research/index.html ..... the article card grid + the "N published so far" count
  - feed.xml ................ <lastBuildDate> + every <item>
  - sitemap.xml ............. the per-article research <url> entries
  - assets/umbra.js ......... the command-palette "Articles" entries
  - research/<slug>.html .... each article's prev/next footer nav

Everything else in those files - hand-written prose, article bodies, the channel
boilerplate, the guide/tooling sitemap entries - is left untouched. The generator
only rewrites the regions fenced by AUTO markers, plus the nav block in each
article (located structurally by its container class).

Usage:
  python3 tools/site-build/build_indexes.py          # write changes
  python3 tools/site-build/build_indexes.py --check   # CI guard: exit 1 if drift

The --check mode writes nothing; it just fails if the committed files don't match
what the manifest would produce. That's what the GitHub Action runs.
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research" / "articles.json"

# category key -> (uppercase eyebrow label, title-case feed/filter label, data-cat value)
CATEGORIES = {
    "threat":    ("THREAT ANALYSIS",      "Threat Analysis",      "threat"),
    "detection": ("DETECTION ENGINEERING", "Detection Engineering", "detection"),
    "ai":        ("AI & LLM SECURITY",    "AI & LLM Security",    "ai"),
    "tooling":   ("TOOLING",              "Tooling",              "tooling"),
}

# canonical display order for the research index filter chips
CATEGORY_ORDER = ["detection", "threat", "ai", "tooling"]

_ONES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
         "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]


def number_word(n: int) -> str:
    return _ONES[n] if 0 <= n < len(_ONES) else str(n)


def he(s: str) -> str:
    """HTML/XML-escape text content (ampersands and angle brackets; quotes stay literal, matching the existing markup)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def js(s: str) -> str:
    """Escape for a double-quoted JavaScript string literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def parse_date(d: str) -> dt.date:
    return dt.datetime.strptime(d, "%Y-%m-%d").date()


def rfc822(d: dt.date) -> str:
    # All articles publish at a normalized 12:00:00 UTC.
    return d.strftime("%a, %d %b %Y 12:00:00 +0000")


def load_articles():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    articles = data["articles"]
    for a in articles:
        if a["category"] not in CATEGORIES:
            sys.exit(f"error: article '{a['slug']}' has unknown category '{a['category']}'")
        a["_date"] = parse_date(a["date"])
    # newest first; stable sort keeps manifest order among equal dates
    articles.sort(key=lambda a: a["_date"], reverse=True)
    return articles


# ---- marker-region replacement -------------------------------------------------

def replace_region(text: str, name: str, new_inner: str, path: Path) -> str:
    """Replace content between <!-- AUTO:{name} START --> and END markers.
    Markers may be HTML (<!-- -->) or JS (/* */) comments."""
    patterns = [
        (f"<!-- AUTO:{name} START -->", f"<!-- AUTO:{name} END -->"),
        (f"/* AUTO:{name} START */", f"/* AUTO:{name} END */"),
    ]
    for start, end in patterns:
        i = text.find(start)
        if i == -1:
            continue
        j = text.find(end, i)
        if j == -1:
            sys.exit(f"error: found '{start}' but no matching END in {path}")
        return text[: i + len(start)] + new_inner + text[j:]
    sys.exit(f"error: AUTO:{name} markers not found in {path}")


# ---- block renderers -----------------------------------------------------------

def _wrap(items, sep: str, end_indent: int) -> str:
    """Join rendered items and frame them so the closing AUTO marker lands at end_indent."""
    return "\n" + sep.join(items) + "\n" + " " * end_indent


def render_home_rows(articles) -> str:
    rows = []
    for a in articles[:3]:
        label = he(CATEGORIES[a["category"]][0])
        mon_year = a["_date"].strftime("%b %Y")
        rows.append(
f'''                <a href="research/{a['slug']}.html" class="block">
                    <div class="research-row grid grid-cols-1 md:grid-cols-12 gap-x-8 py-8 group">
                        <div class="md:col-span-5">
                            <div class="font-mono text-xs text-[#9ece6a] mb-2">{label}</div>
                            <div class="font-semibold text-xl group-hover:text-[#7aa2f7] transition-colors">
                                {he(a['title'])}
                            </div>
                        </div>
                        <div class="md:col-span-7 text-[#a9b1d6] mt-2 md:mt-0">
                            {he(a['home_blurb'])}
                            <div class="mt-3 flex items-center gap-x-3 text-xs font-mono">
                                <span class="text-[#7aa2f7]">{mon_year}</span>
                                <span class="text-[#565f89]">·</span>
                                <span class="text-[#565f89]">~{a['read_min']} min read</span>
                                <span class="row-chev ml-auto">Read →</span>
                            </div>
                        </div>
                    </div>
                </a>''')
    return _wrap(rows, "\n\n", 16)


def render_hero(articles) -> str:
    a = articles[0]
    anchor = (
f'''                        <a href="research/{a['slug']}.html"
                           class="btn-primary inline-flex items-center px-8 py-3.5 rounded-2xl bg-white text-[#1a1b26] font-semibold hover:bg-[#e2e8f0] transition-all">
                            Read the latest research <span class="arrow ml-1.5">→</span>
                        </a>''')
    return _wrap([anchor], "\n", 24)


def render_cards(articles) -> str:
    cards = []
    for a in articles:
        label = he(CATEGORIES[a["category"]][0])
        cat = CATEGORIES[a["category"]][2]
        date_str = a["_date"].strftime("%b %d, %Y")
        cards.append(
f'''            <a href="{a['slug']}.html"
               class="research-card u-card block p-6 border border-[#2a2c38] rounded-3xl bg-[#16161e]" data-cat="{cat}">
                <div class="flex items-center justify-between mb-3">
                    <span class="font-mono text-xs text-[#9ece6a]">{label}</span>
                    <span class="font-mono text-[10px] text-[#565f89]">~{a['read_min']} min</span>
                </div>
                <div class="research-card-title font-semibold text-xl leading-tight mb-3">
                    {he(a['title'])}
                </div>
                <p class="text-sm text-[#a9b1d6] mb-5">
                    {he(a['card_blurb'])}
                </p>
                <div class="flex items-center text-xs font-mono text-[#7aa2f7]">
                    <span>{date_str}</span>
                    <span class="research-card-arrow ml-auto">Read →</span>
                </div>
            </a>''')
    return _wrap(cards, "\n\n", 12)


def render_count(articles) -> str:
    return f"{number_word(len(articles))} published so far"


def render_filters(articles) -> str:
    # "All" plus one chip per category that actually has at least one article
    present = [k for k in CATEGORY_ORDER if any(a["category"] == k for a in articles)]
    chips = ['            <button type="button" class="filter-chip active" data-filter="all">All</button>']
    for k in present:
        label = he(CATEGORIES[k][1])
        chips.append(f'            <button type="button" class="filter-chip" data-filter="{k}">{label}</button>')
    return _wrap(chips, "\n", 12)


def render_feed_items(articles) -> str:
    items = []
    for a in articles:
        feed_cat = he(CATEGORIES[a["category"]][1])
        url = f"https://umbrasec.dev/research/{a['slug']}.html"
        items.append(f"""    <item>
      <title>{he(a['title'])}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc822(a['_date'])}</pubDate>
      <category>{feed_cat}</category>
      <description>{he(a['feed_desc'])}</description>
    </item>""")
    return _wrap(items, "\n", 2)


def render_builddate(articles) -> str:
    return f"<lastBuildDate>{rfc822(articles[0]['_date'])}</lastBuildDate>"


def render_sitemap(articles) -> str:
    entries = []
    for a in articles:
        entries.append(f"""  <url>
    <loc>https://umbrasec.dev/research/{a['slug']}.html</loc>
    <lastmod>{a['date']}</lastmod>
    <priority>0.9</priority>
  </url>""")
    return _wrap(entries, "\n", 2)


def render_palette(articles) -> str:
    lines = []
    for a in articles:
        p = a["palette"]
        lines.append(
            f'    {{ group: "Articles", label: "{js(p["label"])}", '
            f'hint: "{js(p["hint"])}", icon: "{p["icon"]}", '
            f'href: "research/{a["slug"]}.html", keywords: "{js(p["keywords"])}" }},'
        )
    return _wrap(lines, "\n", 4)


# ---- per-article footer nav ----------------------------------------------------

NAV_RE = re.compile(
    r'(<div class="flex flex-wrap items-center justify-between gap-4">\s*)'
    r'<a\b[^>]*>.*?</a>'
    r'(\s*<div class="flex items-center gap-2">.*?</div>\s*)'
    r'<a\b[^>]*>.*?</a>'
    r'(\s*</div>)',
    re.DOTALL,
)

_A = '<a href="{href}" class="text-sm text-[#7aa2f7] hover:text-[#7dcfff]">{text}</a>'


def nav_prev(articles, i):
    if i + 1 < len(articles):  # an older article exists
        older = articles[i + 1]
        return _A.format(href=f"{older['slug']}.html", text=f"← {he(older['nav_title'])}")
    return _A.format(href="index.html", text="← All research")


def nav_next(articles, i):
    if i > 0:  # a newer article exists
        newer = articles[i - 1]
        return _A.format(href=f"{newer['slug']}.html", text=f"{he(newer['nav_title'])} →")
    return _A.format(href="index.html", text="All research →")


def rewrite_nav(text, prev_html, next_html, path):
    matches = NAV_RE.findall(text)
    if len(matches) != 1:
        sys.exit(f"error: expected exactly one footer nav block in {path}, found {len(matches)}")

    def repl(m):
        return m.group(1) + prev_html + m.group(2) + next_html + m.group(3)

    return NAV_RE.sub(repl, text, count=1)


# ---- driver --------------------------------------------------------------------

def build(check: bool) -> int:
    articles = load_articles()
    changes = []  # (path, new_text)

    def stage(rel, transform):
        path = ROOT / rel
        old = path.read_text(encoding="utf-8")
        new = transform(old)
        if new != old:
            changes.append((path, new))

    def index_home(t):
        t = replace_region(t, "hero", render_hero(articles), ROOT / "index.html")
        t = replace_region(t, "featured", render_home_rows(articles), ROOT / "index.html")
        return t
    stage("index.html", index_home)

    def research_index(t):
        t = replace_region(t, "filters", render_filters(articles), ROOT / "research/index.html")
        t = replace_region(t, "cards", render_cards(articles), ROOT / "research/index.html")
        t = replace_region(t, "count", render_count(articles), ROOT / "research/index.html")
        return t
    stage("research/index.html", research_index)

    def feed(t):
        t = replace_region(t, "builddate", render_builddate(articles), ROOT / "feed.xml")
        t = replace_region(t, "items", render_feed_items(articles), ROOT / "feed.xml")
        return t
    stage("feed.xml", feed)

    stage("sitemap.xml",
          lambda t: replace_region(t, "research", render_sitemap(articles), ROOT / "sitemap.xml"))

    stage("assets/umbra.js",
          lambda t: replace_region(t, "articles", render_palette(articles), ROOT / "assets/umbra.js"))

    for i, a in enumerate(articles):
        rel = f"research/{a['slug']}.html"
        path = ROOT / rel
        if not path.exists():
            sys.exit(f"error: manifest references {rel} but the file does not exist")
        stage(rel, lambda t, i=i: rewrite_nav(t, nav_prev(articles, i), nav_next(articles, i), ROOT / rel))

    if check:
        if changes:
            print("site-build: DRIFT - these files are out of sync with research/articles.json:")
            for path, _ in changes:
                print(f"  - {path.relative_to(ROOT)}")
            print("\nRun:  python3 tools/site-build/build_indexes.py   then commit the result.")
            return 1
        print(f"site-build: OK - {len(articles)} articles, all derived files in sync.")
        return 0

    for path, new in changes:
        path.write_text(new, encoding="utf-8")
        print(f"  updated {path.relative_to(ROOT)}")
    if not changes:
        print(f"site-build: nothing to do - {len(articles)} articles already in sync.")
    else:
        print(f"site-build: regenerated {len(changes)} file(s) from {len(articles)} articles.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Regenerate UMBRASEC derived lists from research/articles.json")
    ap.add_argument("--check", action="store_true", help="exit 1 if any file is out of sync (writes nothing)")
    args = ap.parse_args()
    sys.exit(build(args.check))


if __name__ == "__main__":
    main()
