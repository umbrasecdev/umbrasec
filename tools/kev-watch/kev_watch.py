#!/usr/bin/env python3
"""
kev-watch — monitor the CISA Known Exploited Vulnerabilities (KEV) catalog.

A small, zero-dependency defensive tool. It pulls CISA's public KEV feed,
remembers what it has seen before, and reports newly added, actively-exploited
CVEs — optionally filtered to the vendors/products you actually run.

Public data only. Nothing here touches a target system or performs any scanning.

Source feed:
    https://www.cisa.gov/known-exploited-vulnerabilities-catalog
    https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json

Usage:
    python3 kev_watch.py                      # show CVEs added since last run
    python3 kev_watch.py --watch fortinet ivanti "microsoft windows"
    python3 kev_watch.py --since 2026-05-01   # everything added on/after a date
    python3 kev_watch.py --due-soon 14        # KEV items with a remediation date within N days
    python3 kev_watch.py --json               # machine-readable output

License: MIT
Project: https://github.com/atraxsrc/umbrasec
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)
STATE_PATH = os.environ.get(
    "KEV_WATCH_STATE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".kev_state.json"),
)
USER_AGENT = "kev-watch/1.0 (+https://github.com/atraxsrc/umbrasec)"


# ── ANSI helpers (auto-disabled when not a TTY) ──────────────────────────────
def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


class C:
    if _supports_color():
        RESET = "\033[0m"
        DIM = "\033[2m"
        BOLD = "\033[1m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        CYAN = "\033[36m"
    else:
        RESET = DIM = BOLD = RED = GREEN = YELLOW = BLUE = CYAN = ""


def fetch_kev(timeout: int = 30) -> dict:
    """Download and parse the CISA KEV catalog."""
    req = urllib.request.Request(KEV_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:  # network / TLS / DNS
        sys.exit(f"error: could not reach CISA KEV feed: {exc}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: KEV feed was not valid JSON: {exc}")


def load_state() -> set[str]:
    if not os.path.exists(STATE_PATH):
        return set()
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            return set(json.load(fh).get("seen", []))
    except (OSError, json.JSONDecodeError):
        return set()


def save_state(seen: set[str]) -> None:
    tmp = STATE_PATH + ".tmp"
    payload = {"seen": sorted(seen), "updated": dt.date.today().isoformat()}
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, tmp[: -len(".tmp")])


def matches_watch(vuln: dict, watch_terms: list[str]) -> bool:
    if not watch_terms:
        return True
    haystack = " ".join(
        str(vuln.get(k, "")) for k in ("vendorProject", "product", "vulnerabilityName")
    ).lower()
    return any(term.lower() in haystack for term in watch_terms)


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        sys.exit(f"error: '{value}' is not a valid YYYY-MM-DD date")


def select(
    catalog: dict,
    seen: set[str],
    args: argparse.Namespace,
) -> list[dict]:
    """Pick the vulnerabilities to report based on the chosen mode."""
    vulns = catalog.get("vulnerabilities", [])
    today = dt.date.today()
    out = []

    for v in vulns:
        if not matches_watch(v, args.watch):
            continue

        if args.since:
            added = v.get("dateAdded", "")
            if not added or parse_date(added) < args.since:
                continue
        elif args.due_soon is not None:
            due = v.get("dueDate", "")
            if not due:
                continue
            delta = (parse_date(due) - today).days
            if delta < 0 or delta > args.due_soon:
                continue
        else:
            # default mode: only CVEs we haven't seen on a prior run
            if v.get("cveID") in seen:
                continue

        out.append(v)

    # newest first by dateAdded
    out.sort(key=lambda v: v.get("dateAdded", ""), reverse=True)
    return out


def render_human(rows: list[dict], catalog: dict, mode: str) -> None:
    version = catalog.get("catalogVersion", "?")
    total = catalog.get("count", len(catalog.get("vulnerabilities", [])))
    print(
        f"{C.DIM}CISA KEV catalog {version} · {total} total entries · "
        f"mode: {mode}{C.RESET}\n"
    )
    if not rows:
        print(f"{C.GREEN}Nothing to report.{C.RESET}")
        return

    for v in rows:
        cve = v.get("cveID", "CVE-?")
        ran = v.get("knownRansomwareCampaignUse", "Unknown")
        ran_flag = (
            f"  {C.RED}{C.BOLD}[ransomware]{C.RESET}"
            if ran.strip().lower() == "known"
            else ""
        )
        print(f"{C.BOLD}{C.CYAN}{cve}{C.RESET}{ran_flag}")
        print(f"  {C.BOLD}{v.get('vendorProject','?')} {v.get('product','?')}{C.RESET}"
              f" — {v.get('vulnerabilityName','')}")
        print(f"  {C.DIM}added{C.RESET} {v.get('dateAdded','?')}   "
              f"{C.DIM}remediate by{C.RESET} {C.YELLOW}{v.get('dueDate','?')}{C.RESET}")
        action = (v.get("requiredAction") or "").strip()
        if action:
            print(f"  {C.DIM}action:{C.RESET} {action}")
        print(f"  {C.BLUE}https://nvd.nist.gov/vuln/detail/{cve}{C.RESET}")
        print()

    print(f"{C.DIM}{len(rows)} item(s) reported.{C.RESET}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Monitor the CISA Known Exploited Vulnerabilities (KEV) catalog.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--watch",
        nargs="*",
        default=[],
        metavar="TERM",
        help="only report entries matching these vendor/product terms",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--since",
        type=parse_date,
        metavar="YYYY-MM-DD",
        help="report everything added on or after this date (ignores seen-state)",
    )
    mode.add_argument(
        "--due-soon",
        type=int,
        metavar="DAYS",
        help="report KEV items whose remediation due date is within DAYS",
    )
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument(
        "--no-save",
        action="store_true",
        help="do not update the seen-state file (dry run)",
    )
    args = p.parse_args(argv)

    catalog = fetch_kev()
    seen = load_state()
    rows = select(catalog, seen, args)

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        mode_name = (
            "since" if args.since else "due-soon" if args.due_soon is not None else "new"
        )
        render_human(rows, catalog, mode_name)

    # Only the default ("new since last run") mode advances the seen-state,
    # so --since / --due-soon queries never hide future "new" results.
    if not args.no_save and not args.since and args.due_soon is None:
        all_ids = {v.get("cveID") for v in catalog.get("vulnerabilities", []) if v.get("cveID")}
        save_state(seen | all_ids)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
