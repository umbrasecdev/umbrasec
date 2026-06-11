# kev-watch

A small, **zero-dependency** Python monitor for the [CISA Known Exploited
Vulnerabilities (KEV) catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog).

It pulls CISA's public KEV feed, remembers what it has already seen, and reports
newly added, **actively-exploited** CVEs - optionally filtered to the vendors and
products you actually run. Useful as a daily cron job or a quick manual check.

> **Defensive, public-data-only.** kev-watch reads one public JSON feed. It does
> not scan, probe, or touch any target system. It's a watchlist, not a scanner.

## Requirements

- Python 3.9+
- Network access to `cisa.gov`
- No third-party packages

## Usage

```bash
# CVEs added to the KEV catalog since the last time you ran it
python3 kev_watch.py

# Only the vendors/products you care about
python3 kev_watch.py --watch fortinet ivanti citrix "microsoft windows"

# Everything added on or after a date (does not affect seen-state)
python3 kev_watch.py --since 2026-05-01

# KEV items whose CISA remediation deadline is within 14 days
python3 kev_watch.py --due-soon 14

# Machine-readable output for piping into other tooling
python3 kev_watch.py --json --watch fortinet
```

### How "new" works

On a normal run (no `--since` / `--due-soon`), kev-watch compares the current
catalog against a local state file (`.kev_state.json`) and prints only CVEs it
hasn't seen before, then records everything it saw. So the **first** run is quiet
by design (it's establishing a baseline); subsequent runs surface only what's
genuinely new. Use `--no-save` for a dry run that doesn't advance the baseline.

The `--since` and `--due-soon` modes are independent queries - they never advance
the seen-state, so they won't hide future "new" results.

### Output

Each reported CVE shows the vendor/product, the vulnerability name, the date CISA
added it, the federal remediation due date, the required action, and a link to the
NVD record. Entries flagged by CISA as used in ransomware campaigns are highlighted.

## As a cron job

```cron
# Weekday mornings, email me any new KEV entries touching my stack
0 8 * * 1-5  /usr/bin/python3 /opt/kev-watch/kev_watch.py --watch fortinet ivanti vmware | mail -s "New KEV entries" you@example.com
```

State is written next to the script by default; override with the
`KEV_WATCH_STATE` environment variable to keep it elsewhere.

## Why this exists

Part of [UMBRASEC](https://umbrasec.dev) - a defensive security research project.
The KEV catalog is the single best public signal for "patch this now": it only
lists vulnerabilities with confirmed in-the-wild exploitation. This tool just
makes it easy to watch the slice of it that's relevant to you.

## License

MIT
