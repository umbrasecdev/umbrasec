# site-build

One generator, one source of truth. Adding a research article used to mean
hand-editing seven places (the article, the research index card + count, the
homepage featured rows, `feed.xml`, `sitemap.xml`, the command palette, and the
prev/next nav on two articles). Every one of those was a chance to desync. This
removes that whole class of mistake.

## How publishing works now

1. Write the article HTML in `research/<slug>.html` (copy an existing one; keep
   the standard footer nav block so the generator can find it).
2. Add one entry to `research/articles.json`, at the **top** of the `articles`
   array (newest first).
3. Run the generator:

   ```sh
   python3 tools/site-build/build_indexes.py
   ```

4. Commit. CI (`.github/workflows/site-build.yml`) re-runs it in `--check` mode
   and fails the build if anything is out of sync, so a forgotten step can't ship.

## What the generator owns

It rewrites only the regions fenced by `AUTO:*` markers, plus each article's
footer nav (located by its container class). Everything else - article bodies,
hand-written prose, channel boilerplate, the guide and tooling sitemap entries -
is never touched.

| File | Region | Marker |
| --- | --- | --- |
| `index.html` | hero "Read the latest research" button (latest 1) | `<!-- AUTO:hero ... -->` |
| `index.html` | homepage featured trio (latest 3) | `<!-- AUTO:featured ... -->` |
| `research/index.html` | category filter chips (only categories with articles) | `<!-- AUTO:filters ... -->` |
| `research/index.html` | article card grid | `<!-- AUTO:cards ... -->` |
| `research/index.html` | "N published so far" count | `<!-- AUTO:count ... -->` |
| `feed.xml` | `<lastBuildDate>` + every `<item>` | `<!-- AUTO:builddate ... -->`, `<!-- AUTO:items ... -->` |
| `sitemap.xml` | per-article research `<url>` entries | `<!-- AUTO:research ... -->` |
| `assets/umbra.js` | command-palette "Articles" entries | `/* AUTO:articles ... */` |
| `research/<slug>.html` | prev/next footer nav | located structurally (no marker) |
| every site page | shared site footer (depth-aware links) | the whole `<footer>` element is replaced (no marker) |

The count is computed, so "Three/Six published so far" can never go stale again.
Articles are sorted by date (newest first); equal dates keep manifest order.

The shared footer is defined once in `render_footer()` and written into every
standard site page (root pages plus `guide/*.html`, `research/*.html`, and
`tools/index.html`), with relative links adjusted for page depth. New pages just
need any `<footer>...</footer>` placeholder - the generator replaces it wholesale -
which you get for free by copying an existing page.

## Manifest fields (`research/articles.json`)

Per article: `slug`, `title`, `nav_title` (short label for prev/next), `category`
(`threat` | `detection` | `ai` | `tooling`), `date` (`YYYY-MM-DD`), `read_min`,
`home_blurb` (homepage row), `card_blurb` (research index card), `feed_desc` (RSS),
and a `palette` object (`label`, `hint`, `icon`, `keywords`).

Use **raw** text: literal `&` and `"`. The generator escapes per output format
(HTML/XML entity-escaping for the pages and feed, JS-string escaping for the
palette). Do not pre-escape.

## Commands

```sh
python3 tools/site-build/build_indexes.py          # regenerate (writes changes)
python3 tools/site-build/build_indexes.py --check   # CI guard: exit 1 on drift, writes nothing
```
