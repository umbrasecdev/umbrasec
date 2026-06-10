# UMBRASEC

Source for **[umbrasec.dev](https://umbrasec.dev)** — a new, independent, one-person
defensive security research project. Detection engineering, honest threat analysis,
and small open-source defensive tools, published openly.

> **Scope:** defensive only. The research explains how attacks work *so defenders can
> detect and stop them* — no working exploits, malware, or offensive tooling. The site
> makes no claims of a track record it doesn't have; it's new, and says so.

## What's here

A static, multi-page site — plain HTML, [Tailwind](https://tailwindcss.com) via CDN,
one shared stylesheet and one shared script. No build step, no framework, nothing to
install. Deploys as-is to any static host (GitHub Pages, Netlify, Cloudflare Pages…).

```
index.html                              Landing page
about.html                              About the project
research/
  index.html                            Research index
  detecting-kerberoasting.html          Flagship: Kerberoasting (T1558.003) detection guide
assets/
  umbra.css                             Shared styles (Tokyo Night theme)
  umbra.js                              Shared interactivity (see below)
tools/
  kev-watch/                            Working defensive tool: CISA KEV monitor
```

## Interactivity

`assets/umbra.js` is shared across every page and provides:

- **⌘K command palette** — `⌘K` / `Ctrl+K` (or `/`) to search and jump anywhere
- **Mobile menu** — responsive hamburger nav, built from the desktop links
- **Scroll-reveal** + **scrollspy** active-section highlighting
- **Copy buttons** on code/rule blocks
- **Back-to-top** button

All of it honours `prefers-reduced-motion`. A page opts in with two lines:

```html
<body data-base="">             <!-- "" at the repo root, "../" one level deep -->
<script src="assets/umbra.js" defer></script>
```

When adding pages, also add them to the `COMMANDS` list near the top of `umbra.js`
so they appear in the command palette.

## Tools

[`tools/kev-watch/`](tools/kev-watch/) — a zero-dependency Python monitor for the
CISA Known Exploited Vulnerabilities (KEV) catalog. Tracks newly added, actively
exploited CVEs and can filter to the vendors/products you run. Public data only; it
does not scan anything. See its [README](tools/kev-watch/README.md).

```bash
python3 tools/kev-watch/kev_watch.py --watch fortinet ivanti
```

## Develop locally

No tooling required — open `index.html` directly, or serve the folder:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Deploying

The site is static, so any host works. For **GitHub Pages** with the `umbrasec.dev`
custom domain, enable Pages on the `master` branch (root) and add a `CNAME` file
containing `umbrasec.dev` (not committed yet — add it once Pages/DNS are set up).

## Contributing / corrections

Found a detection that misbehaves, a wrong citation, or an analysis that's off?
That feedback is welcome — open an issue. Corrections are credited.

## License

Code and tools: MIT. Written research/content: © UMBRASEC, free to read.
