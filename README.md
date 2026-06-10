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

## Tools

[`tools/kev-watch/`](tools/kev-watch/) — a zero-dependency Python monitor for the CISA
Known Exploited Vulnerabilities (KEV) catalog. Tracks newly added, actively exploited
CVEs and can filter to the vendors/products you run. Public data only; it does not scan
anything. See its [README](tools/kev-watch/README.md).

```bash
python3 tools/kev-watch/kev_watch.py --watch fortinet ivanti
```

## Corrections

Found a detection that misbehaves, a wrong citation, or an analysis that's off? That
feedback is welcome — [open an issue](https://github.com/atraxsrc/umbrasec/issues).
Corrections are credited.

## License

Code and tools: MIT. Written research/content: © UMBRASEC, free to read.
