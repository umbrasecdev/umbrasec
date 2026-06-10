# UMBRASEC

**UMBRASEC is a new, independent research project focused on the defensive side of
security** — detection engineering, honest threat analysis, and open-source tooling
that helps defenders spot real techniques in their own logs.

Site: **[umbrasec.dev](https://umbrasec.dev)** · Contact: **0xdev1@umbrasec.com**

## Who's behind it

UMBRASEC is run by **0xdev1** — a single, independent researcher. It isn't a company,
a collective, or a consultancy, and it makes no claims of a track record it doesn't
have yet: it's new, and says so. The plan is the honest one — publish genuinely useful,
well-sourced work, let it be checked, and let any reputation grow from there.

Everything published is **defensive in scope**. The research explains how attacks work
*so defenders can detect and stop them* — no working exploits, malware, or offensive
tooling ships from here.

## Focus right now

- **Detection engineering** — writeups with rules you can actually run (Sigma, mapped to
  real event IDs and MITRE ATT&CK techniques), plus tuning and false-positive notes.
- **Honest threat analysis** — technical breakdowns of real techniques and CVEs, every
  claim tied to a primary source.
- **Open-source defensive tooling** — small, useful tools for defenders, built in the open.

## Roadmap (later)

Planned directions as the project grows — not live yet, listed honestly as intent:

- **Threat intelligence** — tracking and analysis of real-world campaigns and infrastructure.
- **LLM / AI security** — defensive coverage of prompt injection and the OWASP LLM Top 10
  as a class of risk.

## What's in this repo

The `umbrasec.dev` website and tooling. A static, multi-page site — plain HTML,
[Tailwind](https://tailwindcss.com) via CDN, one shared stylesheet and one shared
script. No build step, no framework, nothing to install.

```
index.html                              Landing page
about.html                              About the project
research/
  index.html                            Research index
  detecting-kerberoasting.html          Flagship: Kerberoasting (T1558.003) detection guide
assets/
  umbra.css                             Shared styles (Tokyo Night theme)
  umbra.js                              Shared interactivity (command palette, menu, etc.)
  favicon.svg                           "U" tab icon
tools/
  kev-watch/                            Defensive tool: CISA KEV monitor
```

### Interactivity (`assets/umbra.js`)

⌘K / Ctrl-K command palette, responsive mobile menu, scroll-reveal, scrollspy,
code-copy buttons, and back-to-top — all honouring `prefers-reduced-motion`. A page
opts in with `<body data-base="">` (`"../"` one level deep) and the script tag. When
adding pages, also add them to the `COMMANDS` list near the top of `umbra.js`.

### Tools

[`tools/kev-watch/`](tools/kev-watch/) — a zero-dependency Python monitor for the CISA
Known Exploited Vulnerabilities (KEV) catalog. Tracks newly added, actively exploited
CVEs and can filter to the vendors/products you run. Public data only; it does not scan
anything. See its [README](tools/kev-watch/README.md).

```bash
python3 tools/kev-watch/kev_watch.py --watch fortinet ivanti
```

## Run locally

No tooling required — open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000   # → http://localhost:8000
```

## Deploying

Static, so any host works. For **GitHub Pages** with the `umbrasec.dev` custom domain,
enable Pages on the `master` branch (root) and add a `CNAME` file containing
`umbrasec.dev` once DNS is set up.

## Corrections

Found a detection that misbehaves, a wrong citation, or an analysis that's off? That
feedback is welcome — [open an issue](https://github.com/atraxsrc/umbrasec/issues).
Corrections are credited.

## License

Code and tools: MIT. Written research/content: © UMBRASEC, free to read.
