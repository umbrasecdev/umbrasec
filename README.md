<p align="center">
  <a href="https://umbrasec.dev"><img src="assets/umbra-avatar.png" alt="UMBRASEC logo" width="96" height="96"></a>
</p>

# UMBRASEC

**Defensive security tooling and detection research** - runnable Sigma rules and KQL
queries, a zero-dependency CISA KEV monitor, a daily-synced KEV feed, and a single-page
blue-team reference. Defensive in scope, every claim tied to a primary source.

[![KEV sync](https://github.com/atraxsrc/umbrasec/actions/workflows/kev-sync.yml/badge.svg)](https://github.com/atraxsrc/umbrasec/actions/workflows/kev-sync.yml)
[![Sigma validation](https://github.com/atraxsrc/umbrasec/actions/workflows/sigma-validate.yml/badge.svg)](https://github.com/atraxsrc/umbrasec/actions/workflows/sigma-validate.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-umbrasec.dev-8a2be2)](https://umbrasec.dev)

## Try it in 10 seconds

`kev-watch` needs Python 3.9+ and nothing else - no packages, no install step:

```bash
git clone https://github.com/atraxsrc/umbrasec
python3 umbrasec/tools/kev-watch/kev_watch.py --watch fortinet ivanti citrix
```

That prints newly-added, **actively exploited** CVEs from CISA's Known Exploited
Vulnerabilities catalog, filtered to the vendors you actually run:

```text
CISA KEV catalog 2026.06.11 · 1618 total entries · mode: since

CVE-2026-10520
  Ivanti Sentry - Ivanti Sentry OS Command Injection Vulnerability
  added 2026-06-11   remediate by 2026-06-14
  action: Apply mitigations in accordance with vendor instructions ...
  https://nvd.nist.gov/vuln/detail/CVE-2026-10520

1 item(s) reported.
```

Public data only; it reads one JSON feed and never touches a target system.

## What's inside

| | What it is |
|---|---|
| [`tools/kev-watch/`](tools/kev-watch/) | Zero-dependency Python monitor for the CISA KEV catalog. Tracks newly added, actively exploited CVEs, filters to your stack, flags ransomware-linked entries, warns on remediation deadlines. |
| [`tools/sigma-pack/`](tools/sigma-pack/) | The detection rules from the research writeups as runnable files: three Kerberoasting Sigma rules (T1558.003) and three OAuth consent-phishing KQL queries (T1528) so far, each with tuning and false-positive notes. Sigma rules are syntax-validated with sigma-cli in CI, and a per-rule [ATT&CK coverage table](tools/sigma-pack/#attck-coverage) maps every artifact to its technique. |
| [`tools/blue-team-mapper/`](tools/blue-team-mapper/) | A single-page defender reference covering the defensive lifecycle: SIEM/log-source priority, detection engineering, IR flow chains, threat hunting, identity and cloud hardening, SOAR playbooks - ATT&CK-aligned. [Use it live](https://umbrasec.dev/tools/blue-team-mapper/). |
| [`research/`](https://umbrasec.dev/research/) | Detection writeups: [Kerberoasting](https://umbrasec.dev/research/detecting-kerberoasting.html), [OAuth consent phishing in M365](https://umbrasec.dev/research/detecting-oauth-consent-phishing.html), [OWASP LLM Top 10 for defenders](https://umbrasec.dev/research/owasp-llm-top-10-for-defenders.html). Every rule in `sigma-pack` comes from one of these. |
| [`guide/`](https://umbrasec.dev/guide/) | A free, staged security guide for small and mid-sized businesses - from zero to a defensible baseline, with every recommendation mapped to the ASD Essential Eight, ISO 27001:2022, and NIST CSF 2.0, and each step explained as what it is, why it matters, and what it costs. |

## The KEV feed, as a feed

A GitHub Action [syncs the CISA KEV catalog daily](.github/workflows/kev-sync.yml) into
a small JSON file holding the **10 most recently added** actively-exploited CVEs,
newest first - handy for dashboards, tickers, and "what just got exploited" checks
without CORS issues or hitting cisa.gov yourself:

```
https://umbrasec.dev/assets/kev-latest.json
```

```bash
# the five most recently added actively-exploited CVEs
curl -s https://umbrasec.dev/assets/kev-latest.json |
  jq -r '.vulnerabilities[:5][] | "\(.dateAdded)  \(.cveID)  \(.vendorProject) \(.product)"'
```

Fields per entry: `cveID`, `vendorProject`, `product`, `vulnerabilityName`,
`dateAdded`, `knownRansomwareCampaignUse`. Top level carries `catalogVersion`,
`synced`, and `count` (the full catalog's entry count, not this file's). It is
deliberately a recent-entries feed, not a mirror - for the full catalog, go to
[CISA](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) or run
`kev-watch`, which queries CISA's feed directly. Updates daily at 06:17 UTC.

## Focus right now

- **Detection engineering** - writeups with rules you can actually run (Sigma, mapped to
  real event IDs and MITRE ATT&CK techniques), plus tuning and false-positive notes.
- **Honest threat analysis** - technical breakdowns of real techniques and CVEs, every
  claim tied to a primary source.
- **Open-source defensive tooling** - small, useful tools for defenders, built in the open.
- **LLM / AI security** - defensive coverage of prompt injection and the OWASP LLM Top 10
  as a class of risk (first writeup live).
- **SMB security guidance** - a free, framework-grounded [guide](https://umbrasec.dev/guide/)
  taking a small business from zero to a defensible baseline, one stage at a time.

## Who's behind it

UMBRASEC is run by **0xdev1** - a single, independent practitioner. The research and
tools here are free and open; there is also a one-person
[vCISO advisory service](https://umbrasec.dev/services) for small and mid-sized
businesses, honestly labelled as exactly that. It makes no claims of a track record it
doesn't have yet: it's new, and says so. The plan is the honest one - publish genuinely
useful, well-sourced work, let it be checked, and let any reputation grow from there.

Everything published is **defensive in scope**. The research explains how attacks work
*so defenders can detect and stop them* - no working exploits, malware, or offensive
tooling ships from here.

Site: **[umbrasec.dev](https://umbrasec.dev)** · Contact: **0xdev1@umbrasec.dev**

## Roadmap (later)

Planned directions as the project grows - not live yet, listed honestly as intent:

- **Threat intelligence** - tracking and analysis of real-world campaigns and infrastructure.

## Forking the site

This repo is also the source of [umbrasec.dev](https://umbrasec.dev). If you fork it
for your own project, swap these for your own details:

- **Scheduling link** - `services.html` has a `Book a scoping call` button pointing at
  `https://cal.com/0xdev1`. To change it, edit that one URL (marked with a
  `<!-- SCHEDULING: ... -->` comment).
- **Contact email** - `0xdev1@umbrasec.dev`, used in `index.html`, `services.html`,
  `about.html`, and the palette in `assets/umbra.js`.
- **GitHub** - `github.com/atraxsrc/umbrasec` throughout.
- **Crypto tip addresses** - the BTC/XMR addresses and QR SVGs live in `assets/umbra.js`
  (`COINS`) and `assets/btc-qr.svg` / `assets/xmr-qr.svg`.

## Corrections

Found a detection that misbehaves, a wrong citation, or an analysis that's off? That
feedback is welcome - [open an issue](https://github.com/atraxsrc/umbrasec/issues).
Corrections are credited.

## License

Code and tools: MIT. Written research/content: © UMBRASEC, free to read.
