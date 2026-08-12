# N-able N-central Article Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish research article #8 (`n-able-ncentral-msp-supply-chain`) covering the August 2026 N-able N-central compromise from the angle of an SMB that does not run N-central but is managed through it, and ship the two supporting Sigma rules.

**Architecture:** Hand-written static HTML following the existing article scaffold, plus two Sigma rules in `tools/sigma-pack/rules/windows/`. All index/listing/feed/palette/prev-next content is generated - never hand-edited - by `tools/site-build/build_indexes.py` from the `research/articles.json` manifest.

**Tech Stack:** Static HTML + Tailwind CDN, shared `assets/umbra.css` / `assets/umbra.js`, Python 3 build script, Sigma YAML validated by `sigma check` in CI.

**Spec:** `docs/superpowers/specs/2026-08-12-n-able-ncentral-article-design.md` - read it before starting. Every fact in the article must come from the "Verified facts" section of that spec.

## Global Constraints

- **No em-dashes or en-dashes anywhere.** Plain hyphen `-` only. Applies to HTML, YAML, commit messages.
- **No `Co-Authored-By` trailer** on any commit.
- **Do not run `git push`.** Commit to `master` only; the user pushes.
- **Never hand-edit** `research/index.html`, `research/articles.json` derived output, `sitemap.xml`, `feed.xml`, or the `AUTO:` regions of `index.html` / `assets/umbra.js`. Run the build script.
- **No IOC IP list in the article.** Approved decision - sources disagree on at least one address and VPN exit nodes rot. Link the vendor advisory as the live IOC source.
- **Do not reconstruct an exploit path.** The code-level root cause is not public. See spec honesty constraint #1 for exactly what is and isn't in scope.
- **Contact email is `0xdev1@umbrasec.dev`** (`.dev`, not `.com`).
- **Word count target 1,900-2,400.**
- Article date: **2026-08-12**. Sigma rule date field format: **`2026/08/12`**.

**Environment notes (apply to every git command in this plan):**

- The sandbox blocks `~/.gitconfig`, so plain `git` fails with
  `fatal: unknown error occurred while reading the configuration files`.
  Before any git command, run:
  `export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`
- With global config bypassed there is no committer identity, so commit as:
  `git -c user.name=atraxsrc -c user.email=0xdev1@umbrasec.dev commit -m "..."`
- **The pre-commit hook is active** (`core.hooksPath=.githooks`). It runs
  `build_indexes.py --check`, regenerates and stages derived files on drift,
  and **aborts the commit if a `research/*.html` page exists with no matching
  entry in `research/articles.json`** (an "orphan"). This is why Task 2's
  commit uses `--no-verify` and Task 3's does not - see those steps.

---

### Task 1: Two Sigma rules + sigma-pack documentation

**Files:**
- Create: `tools/sigma-pack/rules/windows/masquerading-svchost-outside-system32.yml`
- Create: `tools/sigma-pack/rules/windows/cloudflared-tunnel-service-install.yml`
- Modify: `tools/sigma-pack/README.md` (ATT&CK coverage table + Contents section)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: two rule filenames that Task 2's article References and Detection sections link to, and that Task 3's blurb count (7 rules) depends on. Rule titles as written below are quoted in the article.

- [ ] **Step 1: Create the svchost masquerading rule**

Create `tools/sigma-pack/rules/windows/masquerading-svchost-outside-system32.yml`:

```yaml
title: Masquerading svchost.exe Outside System32
id: 1991446b-a433-4c51-97c8-ab493c79afcd
status: experimental
description: >
    A process named svchost.exe executed from a path outside System32,
    SysWOW64 or WinSxS. Genuine Windows service hosting only ever runs from
    those directories, so a match is a strong masquerading signal rather than
    a behavioural guess. Observed in the August 2026 N-able N-central
    intrusions, where operators placed svchost.exe in a user's Documents
    directory on managed endpoints.
references:
    - https://attack.mitre.org/techniques/T1036/005/
    - https://www.n-able.com/blog/n-central-security-update-august-6-2026
    - https://umbrasec.dev/research/n-able-ncentral-msp-supply-chain.html
author: UMBRASEC
date: 2026/08/12
tags:
    - attack.defense_evasion
    - attack.t1036.005
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\svchost.exe'
    filter_windows_paths:
        Image|startswith:
            - 'C:\Windows\System32\'
            - 'C:\Windows\SysWOW64\'
            - 'C:\Windows\WinSxS\'
    condition: selection and not 1 of filter_*
falsepositives:
    - Installers or update packages that stage a temporary copy of svchost.exe
    - Windows installed to a drive or directory other than C:\Windows - adjust
      the filter paths to match your build before deploying
    - Software test harnesses and imaging tools that copy system binaries
level: high
```

- [ ] **Step 2: Create the Cloudflare Tunnel service rule**

Create `tools/sigma-pack/rules/windows/cloudflared-tunnel-service-install.yml`:

```yaml
title: Cloudflare Tunnel Service Installed
id: bf3f2f8a-f904-4978-9ff1-6dc3c79a2afb
status: experimental
description: >
    A Windows service was created for cloudflared, the Cloudflare Tunnel
    client. A tunnel client gives an operator inbound reach to a host without
    any inbound firewall rule, and it keeps working after whatever access
    established it has been revoked. Observed in the August 2026 N-able
    N-central intrusions, where a service named Cloudflared was registered on
    managed endpoints specifically to hold access after N-central credentials
    were revoked.
references:
    - https://attack.mitre.org/techniques/T1543/003/
    - https://attack.mitre.org/techniques/T1572/
    - https://www.n-able.com/blog/n-central-security-update-august-6-2026
    - https://umbrasec.dev/research/n-able-ncentral-msp-supply-chain.html
author: UMBRASEC
date: 2026/08/12
tags:
    - attack.persistence
    - attack.t1543.003
    - attack.command_and_control
    - attack.t1572
logsource:
    product: windows
    service: system
detection:
    selection_name:
        EventID: 7045
        ServiceName|contains: 'cloudflared'
    selection_image:
        EventID: 7045
        ImagePath|contains: 'cloudflared'
    condition: 1 of selection_*
falsepositives:
    - Cloudflare Tunnel is legitimate dual-use software. If your organisation
      deploys it deliberately, allowlist the known install path and service
      account and alert only on installs outside it
    - A sanctioned vendor or MSP deploying Cloudflare Tunnel for remote support
level: medium
```

- [ ] **Step 3: Validate both rules parse and carry the required fields**

`sigma-cli` is not installed locally and the sandbox blocks PyPI, so validate structurally with pyyaml first. CI runs the full `sigma check` on push.

Run:

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 - <<'PY'
import yaml, glob, sys
REQUIRED = {"title","id","status","description","references","author","date",
            "tags","logsource","detection","falsepositives","level"}
ok = True
seen_ids = {}
for f in sorted(glob.glob("tools/sigma-pack/rules/**/*.yml", recursive=True)):
    d = yaml.safe_load(open(f))
    missing = REQUIRED - set(d)
    if missing:
        print(f"  FAIL {f}: missing {sorted(missing)}"); ok = False
    if "condition" not in d.get("detection", {}):
        print(f"  FAIL {f}: detection has no condition"); ok = False
    if d["id"] in seen_ids:
        print(f"  FAIL {f}: duplicate id, also in {seen_ids[d['id']]}"); ok = False
    seen_ids[d["id"]] = f
    print(f"  ok   {f}  ({d['level']})")
sys.exit(0 if ok else 1)
PY
```

Expected: 7 rules listed, all `ok`, exit 0.

- [ ] **Step 4: Add both rules to the sigma-pack README ATT&CK coverage table**

In `tools/sigma-pack/README.md`, append these two rows to the existing ATT&CK coverage table (the one starting `| Rule / query | Type | MITRE ATT&CK | Tactic | Status |`), after the existing `litellm-mcp-test-endpoint.yml` row:

```markdown
| [`masquerading-svchost-outside-system32.yml`](rules/windows/masquerading-svchost-outside-system32.yml) | Sigma | [T1036.005](https://attack.mitre.org/techniques/T1036/005/) Match Legitimate Name or Location | Defense Evasion | experimental |
| [`cloudflared-tunnel-service-install.yml`](rules/windows/cloudflared-tunnel-service-install.yml) | Sigma | [T1543.003](https://attack.mitre.org/techniques/T1543/003/) Windows Service; [T1572](https://attack.mitre.org/techniques/T1572/) Protocol Tunneling | Persistence / Command &amp; Control | experimental |
```

- [ ] **Step 5: Add a Contents section for the new rules**

In `tools/sigma-pack/README.md`, after the existing LiteLLM Contents subsection, add:

```markdown
### N-able N-central intrusion artifacts - CVE-2026-18556 / CVE-2026-18577 (T1036.005, T1543.003, T1572)

These two rules do not detect the N-central authentication bypass itself - that
happens on the MSP's server, not on your endpoints. They detect what the
operators did *after* it, on the managed machines, which is the part a managed
client can actually see.

| Rule | What it catches | Level |
|---|---|---|
| [`rules/windows/masquerading-svchost-outside-system32.yml`](rules/windows/masquerading-svchost-outside-system32.yml) | A binary named `svchost.exe` running from anywhere other than System32/SysWOW64/WinSxS - the Documents-folder drop reported by N-able is one instance | high |
| [`rules/windows/cloudflared-tunnel-service-install.yml`](rules/windows/cloudflared-tunnel-service-install.yml) | Registration of a `Cloudflared` service, used here to hold access after N-central credentials were revoked | medium |

Prerequisite: Windows process-creation telemetry (Sysmon Event 1 or Security
4688 with command line auditing) for the first rule, and the Windows System log
(Event 7045) for the second.

Read the [writeup](https://umbrasec.dev/research/n-able-ncentral-msp-supply-chain.html)
before deploying - the Cloudflare Tunnel rule in particular is a tuning
exercise, not a drop-in alert.
```

- [ ] **Step 6: Re-run the structural validation**

Run the same command as Step 3. Expected: still 7 rules, all `ok`, exit 0.

- [ ] **Step 7: Commit**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
git add tools/sigma-pack/rules/windows/masquerading-svchost-outside-system32.yml \
        tools/sigma-pack/rules/windows/cloudflared-tunnel-service-install.yml \
        tools/sigma-pack/README.md
git -c user.name=atraxsrc -c user.email=0xdev1@umbrasec.dev commit -m "sigma-pack: add N-central post-exploitation rules

Two rules for what the August 2026 N-able N-central operators did on managed
endpoints after bypassing authentication on the MSP's server:

- masquerading svchost.exe outside System32 (T1036.005)
- Cloudflare Tunnel service installation (T1543.003, T1572)

Neither detects the auth bypass itself, which happens on infrastructure a
managed client does not own. Both detect the part that lands on their hardware.

The cloudflared rule ships at medium with an explicit allowlist note - Cloudflare
Tunnel is legitimate dual-use software and this is a rule you tune, not deploy
blind."
```

---

### Task 2: The article HTML

**Files:**
- Create: `research/n-able-ncentral-msp-supply-chain.html`
- Reference (copy scaffold from): `research/safepay-australian-smb.html`

**Interfaces:**
- Consumes: the two rule filenames and titles from Task 1.
- Produces: an article file whose `<footer>` appears exactly once and whose end-of-article nav div matches `NAV_RE` in `tools/site-build/build_indexes.py:301` - Task 3's build step rewrites both and **hard-fails** if either is missing or duplicated.

- [ ] **Step 1: Copy the scaffold**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
cp research/safepay-australian-smb.html research/n-able-ncentral-msp-supply-chain.html
```

Then replace, throughout the new file: the `<title>`, meta description, canonical, all `og:`/`twitter:` values, the JSON-LD block, the breadcrumb slug span, the header category/date/read-time line, the `<h1>`, the standfirst `<p>`, and the entire `article-body` inner content. Keep the nav, footer, `data-base="../"`, `data-reading`, and `<script src="../assets/umbra.js" defer>` exactly as they are.

- [ ] **Step 2: Set the head block values**

- `<title>`: `Your MSP's RMM Is Your Attack Surface - UMBRASEC`
- `<meta name="description">`: `The August 2026 N-able N-central compromise (CVE-2026-18556, CVE-2026-18577) from the position most SMBs are actually in - you don't run the vulnerable server, your MSP does. What you can still detect on your own endpoints, and what to ask your provider.`
- `<link rel="canonical">`: `https://umbrasec.dev/research/n-able-ncentral-msp-supply-chain.html`
- `og:url` / `mainEntityOfPage`: same URL
- `og:title` / `twitter:title`: `Your MSP's RMM Is Your Attack Surface - UMBRASEC`
- JSON-LD `headline`: `Your MSP's RMM Is Your Attack Surface - What the N-central Compromise Means for SMBs`
- JSON-LD `datePublished`: `2026-08-12`
- JSON-LD `about`: `N-able N-central authentication bypass, MSP/RMM supply-chain risk for SMBs, and endpoint-side detection`
- JSON-LD `keywords`: `N-able, N-central, CVE-2026-18556, CVE-2026-18577, RMM, MSP, supply chain, CISA KEV, Cloudflare Tunnel, cloudflared, Take Control, Essential Eight, third-party risk, Australian SMB`

- [ ] **Step 3: Set the header block**

Category chip text `THREAT ANALYSIS` (keep the `text-[#9ece6a]` class), date `Aug 12, 2026`, read time `~11 min`.

`<h1>`: `Your MSP's RMM Is Your Attack Surface - What the N-central Compromise Means for SMBs`

Standfirst paragraph must establish: N-central is an RMM platform MSPs use to manage client fleets; two authentication bypasses were exploited in the wild in early August 2026; the vulnerable server sits in the MSP's rack so the client has no patch to apply; but every artifact the operators left - remote-control sessions, a masqueraded binary, a persistence service - landed on client endpoints. That inversion is the piece.

- [ ] **Step 4: Write the article body**

Replace everything inside `<div class="prose mx-auto mt-10 article-body">`, keeping the `<aside class="toc-rail" data-toc aria-label="On this page"></aside>` as the first child.

Open with a `<div class="callout">` TL;DR covering: what happened, that the client cannot patch it, the three endpoint artifacts to hunt for right now (`svchost.exe` outside System32, a `Cloudflared` service, Take Control sessions in `C:\ProgramData\GetSupportService_N-Central\Logs\`), and the single most useful action (ask the MSP for their patch date and treat late patching as suspected compromise, per N-able's own guidance).

Then these `<h2>` sections, in order. Content requirements per the spec's "Verified facts" - do not state anything not on that list:

1. **`Your MSP's RMM is your attack surface`** - the inversion. An RMM agent is, by design, a remote code execution channel into every managed endpoint, running as SYSTEM, trusted by the client. That is what makes it worth attacking. Name the trust relationship as the actual attack surface.

2. **`What actually happened`** - the timeline as an HTML table: 31 Jul (N-able's own Adlumin MDR detects an actor exploiting a then-unknown flaw in a customer environment), 1 Aug (initial guidance, active exploitation confirmed), 2 Aug (Hotfix 1, build 2026.3.1.7; both CVEs registered), 3 Aug (CISA adds CVE-2026-18577 to KEV), 4 Aug (CISA adds CVE-2026-18556), 6 Aug (further attack path found, Hotfix 2, build 2026.3.1.10), 10 Aug (consolidated vendor update). Note the reported three-day FCEB remediation deadline and attribute it to the reporting, not to CISA directly.

3. **`What the advisories actually tell you`** - the mechanism section. Say once, plainly, that the code-level cause has not been disclosed: no source names the endpoint, the alternate channel, the parameter, or what the first patch changed. Then work from what is published:
   - the weakness class from CISA's catalog title, Authentication Bypass Using an Alternate Path or Channel (CWE-288), explained as a *category* - a second route to a resource that does not enforce the checks the primary route does - explicitly flagged as describing the class, not this instance
   - both CVSS vectors printed in a `<pre>` block so readers can check the reading:
     - `CVE-2026-18556  CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N   (7.4)`
     - `CVE-2026-18556  CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N   (8.2)`
     - `CVE-2026-18577  CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H   (8.1)`
     - `CVE-2026-18577  CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:L   (8.2)`
   - one sentence clearing up that 8.1 vs 8.2 in circulating coverage is v3.1 vs v4.0, not a disagreement
   - the `AC:H` observation: high attack complexity, exploited as a zero-day anyway. Attack complexity is not a deprioritisation signal and a KEV listing overrides complexity-based triage
   - the v4.0 delta: `SC:N/SI:N/SA:N` on 18556 becomes `SC:L/SI:L/SA:L` on 18577. Subsequent-system impact went from none to low - the scoring itself records that the second flaw reaches past the N-central server into downstream managed systems

4. **`Why there are two CVEs`** - 18577 exists because the 18556 fix was incomplete; affected ranges differ accordingly (18556 through 2026.1; 18577 through 2026.3.1). Hotfix 1 was superseded by Hotfix 2 four days later. The generalisable lesson: "we patched it" and "we are not exploitable" are different claims. N-able's own guidance to treat late-patching environments as potentially compromised is the vendor conceding exactly that.

5. **`You don't run N-central. So what can you do?`** - the pivot. Enumerate what the operators did that touched client hardware: Take Control sessions into servers and workstations including domain controllers; pushing scripts and jobs to managed endpoints; running discovery utilities and enumerating process lists; dropping `svchost.exe` into a user's Documents directory; registering a `Cloudflared` service that survived revocation of their N-central access. Every one of those is visible from the endpoint.

6. **`What to log on your endpoints`** - process creation (Sysmon Event 1, or Security 4688 with command-line auditing enabled - note that command line logging is off by default), service installation (System log Event 7045), and the Take Control log directory `C:\ProgramData\GetSupportService_N-Central\Logs\` with files matching `BASupSrvc_*.log.gz`. Be honest that Sysmon is free but is a deployment project, and that 4688 plus command-line auditing is the cheaper starting point.

7. **`Detection`** - three `<h3>` subsections:
   - `1. A binary named svchost.exe outside System32 (high fidelity)` - include the full YAML of `masquerading-svchost-outside-system32.yml` in a `<pre><code>` block, plus tuning notes on non-C: Windows installs and installer temp paths
   - `2. A Cloudflare Tunnel service appears (tune before you trust)` - include the full YAML of `cloudflared-tunnel-service-install.yml`, and be explicit that this is dual-use software: if the org deploys cloudflared deliberately, invert the rule to alert on installs outside the known path
   - `3. Take Control session review (a hunt, not a rule)` - explain *why* this is a hunt and not a Sigma rule: the artifacts are specific and real, but the event channel and provider cannot be pinned from secondary reporting, and a guessed `logsource:` block ships a rule that silently matches nothing. Give the file path, the `BASupSrvc_*.log.gz` pattern, the reported Event IDs 4102/8192/8193 (labelled as reported), and the default `mspsupport@n-able.com` support account. Say what to correlate: session timestamps against the client's own change/ticket records.

8. **`Questions to put to your MSP this week`** - five or six questions, each with a short "what a good answer sounds like". Cover: which N-central build are you on and when did you apply Hotfix 2 (2026.3.1.10); were you on Hotfix 1 only, between 2 and 6 August; is MFA enforced on all N-central accounts; are in-product support accounts disabled; have you reviewed for unfamiliar accounts and unexpected password resets; and can you give us the Take Control session log for our endpoints over 31 July to 10 August. Note that a provider unable to answer the build-and-date question is itself the finding.

9. **`Where the Essential Eight actually helps`** - be honest that this incident stresses the model. Patch applications is the control that mattered and the client cannot apply it, so it becomes a supplier-assurance obligation rather than a technical one. MFA is directly recommended by N-able and is partly within the client's ask. Restrict administrative privileges limits what a Take Control session reaches. Application control would have stopped the masqueraded `svchost.exe`. Frame the E8 here as a checklist for interrogating the provider, not just for configuring your own estate.

10. **`Honest limitations`** - the code-level root cause is undisclosed so this is not a mechanism writeup; we have not reproduced any of it; the Event IDs are from secondary reporting; no IOC list is published here because sources disagree on at least one address and exit nodes rot, so the vendor advisory is the live source; the rules are `experimental` and untested at scale; attribution is not addressed because no source names an actor.

11. **`References`** - `<ul>` of `<li><a target="_blank" rel="noopener">` entries: NVD/Tenable for both CVEs, CISA KEV catalog, N-able's 10 August security update (labelled as the live IOC source), Rapid7, Huntress, Horizon3, MITRE ATT&CK T1036.005 / T1543.003 / T1572, MITRE CWE-288, FIRST CVSS v3.1 and v4.0 specifications, ASD Essential Eight.

Close with the standard `<div class="callout mt-10">` scope note, adapted: built entirely from public reporting and vendor advisories, names no victim, contains no exploit code, and publishes defense not offense.

- [ ] **Step 5: Update the end-of-article nav block**

Leave the structure exactly as copied but point the share links at the new slug and set the prev link to the current newest article. The build script rewrites the two `<a>` elements in Task 3, but the block must already match `NAV_RE` or the build **exits with an error**.

Set the share URLs to:
- X: `https://twitter.com/intent/tweet?text=Your%20MSP%27s%20RMM%20Is%20Your%20Attack%20Surface%20-%20What%20the%20N-central%20Compromise%20Means%20for%20SMBs&url=https%3A%2F%2Fumbrasec.dev%2Fresearch%2Fn-able-ncentral-msp-supply-chain.html`
- LinkedIn: `https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fumbrasec.dev%2Fresearch%2Fn-able-ncentral-msp-supply-chain.html`

- [ ] **Step 6: Verify the file is well-formed and correctly shaped**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 - <<'PY'
import re
p = "research/n-able-ncentral-msp-supply-chain.html"
h = open(p, encoding="utf-8").read()

NAV_RE = re.compile(
    r'(<div class="flex flex-wrap items-center justify-between gap-4">\s*)'
    r'<a\b[^>]*>.*?</a>'
    r'(\s*<div class="flex items-center gap-2">.*?</div>\s*)'
    r'<a\b[^>]*>.*?</a>'
    r'(\s*</div>)', re.DOTALL)

print("  footer count      :", len(re.findall(r'<footer\b.*?</footer>', h, re.S)), "(must be 1)")
print("  nav block matches :", len(NAV_RE.findall(h)), "(must be 1)")
print("  h1 count          :", len(re.findall(r'<h1', h)), "(must be 1)")
print("  toc-rail present  :", 'data-toc' in h)
print("  data-reading      :", 'data-reading' in h)
print("  data-base=\"../\"   :", 'data-base="../"' in h)
print("  em/en dashes      :", len(re.findall(r'[\u2013\u2014]', h)), "(must be 0)")
print("  .com email typo   :", h.count("0xdev1@umbrasec.com"), "(must be 0)")

body = re.search(r'<article.*?</article>', h, re.S).group(0)
words = len(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style).*?</\1>', '', body, flags=re.S)).split())
print(f"  word count        : {words} (target 1900-2400)")
PY
```

Expected: footer 1, nav 1, h1 1, toc-rail True, data-reading True, data-base True, dashes 0, email typo 0, word count in range.

- [ ] **Step 7: Commit**

`--no-verify` is **required** here and is not a shortcut. Until Task 3 adds the
manifest entry, this article is an orphan by the pre-commit hook's definition,
and the hook aborts the commit. The hook's own documentation names
`--no-verify` as the bypass. Task 3's commit runs the hook normally and is the
gate that proves the orphan is resolved.

```bash
cd /home/atrax/Documents/projects/github/umbrasec
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
git add research/n-able-ncentral-msp-supply-chain.html
git -c user.name=atraxsrc -c user.email=0xdev1@umbrasec.dev commit --no-verify -m "research: add N-central MSP supply-chain writeup

Covers CVE-2026-18556 and CVE-2026-18577 from the position most SMBs are
actually in: the vulnerable server is in the MSP's rack, so there is no patch
for the client to apply - but every artifact the operators left landed on
client endpoints.

The mechanism section is built from the weakness class, the published CVSS
vectors and the confirmed outcome. The code-level root cause has not been
disclosed by any source and is not reconstructed here. No IOC IP list; the
vendor advisory is cited as the live source instead."
```

---

### Task 3: Manifest entry, derived-file regeneration, and site-wide verification

**Files:**
- Modify: `research/articles.json` (new entry, first in the `articles` array)
- Modify: `index.html` and `tools/index.html` (sigma-pack blurb count only)
- Regenerated by script: `research/index.html`, `sitemap.xml`, `feed.xml`, `assets/umbra.js` (AUTO:articles), `index.html` (AUTO:hero, AUTO:featured), every article's prev/next nav

**Interfaces:**
- Consumes: the article file from Task 2 and the rule filenames from Task 1.
- Produces: the finished, verified site state.

- [ ] **Step 1: Add the manifest entry**

In `research/articles.json`, insert as the **first** element of the `articles` array (newest first). Use literal `&` and `"` - the generator escapes per output format.

```json
{
  "slug": "n-able-ncentral-msp-supply-chain",
  "title": "Your MSP's RMM Is Your Attack Surface - What the N-central Compromise Means for SMBs",
  "nav_title": "Your MSP's RMM Is Your Attack Surface",
  "category": "threat",
  "date": "2026-08-12",
  "read_min": 11,
  "home_blurb": "Two authentication bypasses in N-able N-central were exploited in the wild in early August 2026. If your IT is outsourced, the vulnerable server sits in your provider's rack and you have no patch to apply - but the remote-control sessions, the masqueraded binary and the tunnel service all landed on your endpoints. What you can still detect, and what to ask your MSP.",
  "card_blurb": "N-central is the RMM platform your MSP uses to manage your fleet, and in early August 2026 two authentication bypasses in it were exploited in the wild. You cannot patch someone else's server - but every artifact the operators left behind ran on your machines. The timeline, what the advisories actually tell you, endpoint-side detections, and the questions to put to your provider this week.",
  "feed_desc": "CVE-2026-18556 and CVE-2026-18577 are authentication bypasses in N-able N-central, an RMM platform used by MSPs to manage client fleets. Both were added to CISA KEV in early August 2026 after in-the-wild exploitation, and the second exists because the fix for the first was incomplete. For an SMB with outsourced IT the vulnerable server is not theirs to patch - but the Take Control sessions, the svchost.exe dropped into a user's Documents folder, and the Cloudflared persistence service all executed on their endpoints. The timeline, what the published CVSS vectors tell a defender, two Sigma rules, a hunt procedure, and the supplier questions that follow.",
  "palette": {
    "label": "Your MSP's RMM Is Your Attack Surface",
    "hint": "N-central + third-party risk",
    "icon": "fa-network-wired",
    "keywords": "n-able n-central rmm msp managed service provider supply chain third party risk cve-2026-18556 cve-2026-18577 authentication bypass cwe-288 cisa kev take control cloudflared cloudflare tunnel svchost masquerading persistence essential eight patch applications mfa supplier assurance australian smb sigma t1036.005 t1543.003 t1572"
  }
}
```

- [ ] **Step 2: Regenerate every derived file**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 tools/site-build/build_indexes.py
```

Expected: reports 8 articles and rewrites the derived files. If it errors with `expected exactly one footer nav block`, Task 2 Step 5 was not completed correctly - fix the article, do not edit the script.

- [ ] **Step 3: Update the sigma-pack blurb count on both pages**

The pack now holds 7 Sigma rules, not 5. In **both** `index.html` and `tools/index.html`, replace:

`five Sigma rules (Kerberoasting, LiteLLM command injection)`

with:

`seven Sigma rules (Kerberoasting, LiteLLM command injection, N-central post-exploitation)`

- [ ] **Step 4: Confirm the build is idempotent and in sync**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 tools/site-build/build_indexes.py --check
```

Expected: `site-build: OK - 8 articles, all derived files in sync.`

- [ ] **Step 5: Run the full link, anchor and well-formedness check**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 - <<'PY'
import re, os, glob
from urllib.parse import unquote
from html.parser import HTMLParser

pages = sorted(glob.glob("**/*.html", recursive=True))
ids = {p: set(re.findall(r'id="([^"]+)"', open(p, encoding="utf-8").read())) for p in pages}
broken, anch = [], []
for p in pages:
    html = open(p, encoding="utf-8").read(); base = os.path.dirname(p)
    for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
        h = m.group(1)
        if h.startswith(("http://","https://","mailto:","data:","javascript:","tel:")): continue
        if h.startswith("#"):
            f = unquote(h[1:])
            if f and f not in ids[p]: anch.append((p,h))
            continue
        path,_,frag = h.partition("#")
        t = os.path.normpath(os.path.join(base, path)) if path else p
        if not os.path.exists(t): broken.append((p,h))
        elif frag and t.endswith(".html") and frag not in ids.get(t,set()): anch.append((p,h))
print("  broken links:", broken or "none")
print("  bad anchors :", anch or "none")

VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.stack=[]; s.err=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.stack.append(t)
    def handle_endtag(s,t):
        if t in VOID: return
        if not s.stack: s.err.append(f"stray </{t}>"); return
        if s.stack[-1]==t: s.stack.pop()
        elif t in s.stack:
            while s.stack and s.stack[-1]!=t: s.err.append(f"unclosed <{s.stack.pop()}>")
            if s.stack: s.stack.pop()
        else: s.err.append(f"stray </{t}>")
bad = 0
for f in pages:
    p = P(); p.feed(open(f, encoding="utf-8").read())
    left = [x for x in p.stack if x not in ("html","body")]
    if p.err or left:
        bad += 1; print(f"  {f}: {(p.err + ['unclosed <'+x+'>' for x in left])[:4]}")
print("  all pages well-formed" if not bad else f"  {bad} page(s) with issues")
PY
```

Expected: broken `none`, anchors `none`, all pages well-formed.

- [ ] **Step 6: Confirm the article is wired into every derived surface**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
S=n-able-ncentral-msp-supply-chain
echo "homepage hero      : $(grep -c "AUTO:hero" -A3 index.html >/dev/null; grep -c "$S" index.html)"
echo "research index card: $(grep -c "$S" research/index.html)"
echo "command palette    : $(grep -c "$S" assets/umbra.js)"
echo "sitemap            : $(grep -c "$S" sitemap.xml)"
echo "feed               : $(grep -c "$S" feed.xml)"
echo "prev link on safepay: $(grep -c "$S" research/safepay-australian-smb.html)"
echo "article count shown : $(grep -o 'AUTO:count START-->[^<]*' research/index.html || grep -A1 'AUTO:count START' research/index.html | tail -1)"
echo "sigma rule count    : $(find tools/sigma-pack/rules -name '*.yml' | wc -l)"
grep -c 'seven Sigma rules' index.html tools/index.html
```

Expected: non-zero on every surface, safepay's forward link points at the new slug, 7 Sigma rules, and both pages say "seven Sigma rules".

- [ ] **Step 7: Serve locally and confirm the new page returns 200**

```bash
cd /home/atrax/Documents/projects/github/umbrasec
python3 -m http.server 8765 >/dev/null 2>&1 &
sleep 1.5
for u in "" "research/" "research/n-able-ncentral-msp-supply-chain.html" "feed.xml" "sitemap.xml"; do
  code=$(python3 -c "
import urllib.request
try:
    print(urllib.request.urlopen('http://127.0.0.1:8765/$u', timeout=5).status)
except Exception as e:
    print('ERR', e)
")
  echo "  $code  /$u"
done
kill %1 2>/dev/null
```

Expected: 200 on all five.

- [ ] **Step 8: Commit**

The pre-commit hook runs normally here and is the gate proving the orphan from
Task 2 is resolved. If it aborts, the manifest entry is wrong - fix the entry,
do not use `--no-verify`.

```bash
cd /home/atrax/Documents/projects/github/umbrasec
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
git add research/articles.json research/index.html sitemap.xml feed.xml \
        assets/umbra.js index.html tools/index.html research/safepay-australian-smb.html
git -c user.name=atraxsrc -c user.email=0xdev1@umbrasec.dev commit -m "site-build: publish the N-central writeup and refresh derived files

Adds the article to the manifest and regenerates the homepage hero and featured
trio, the research index and count, the category filters, the command palette,
sitemap, feed, and the prev/next nav on the adjacent article.

Also bumps the sigma-pack blurb from five rules to seven on the homepage and
the tools index, following the two rules added for this writeup."
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| Identity (slug/title/category/date/read_min/icon) | Task 3 Step 1 |
| Verified facts - CVEs, CVSS, KEV dates | Task 2 Step 4 §3 |
| Vector reading section | Task 2 Step 4 §3 |
| Timeline | Task 2 Step 4 §2 |
| Post-exploitation detail | Task 2 Step 4 §5 |
| N-able hardening guidance | Task 2 Step 4 §4, §8 |
| Honesty constraint 1 (no exploit path) | Task 2 Step 4 §3, §10; Global Constraints |
| Honesty constraint 2 (no IOC list) | Task 2 Step 4 §10; Global Constraints |
| Honesty constraint 3 (no exploit detail) | Global Constraints |
| Honesty constraint 4 (event IDs reported) | Task 2 Step 4 §7.3, §10 |
| Honesty constraint 5 (no attribution) | Task 2 Step 4 §10 |
| Structure sections 1-11 | Task 2 Step 4 |
| Sigma rule 1 | Task 1 Step 1 |
| Sigma rule 2 | Task 1 Step 2 |
| Take Control as hunt not rule | Task 1 Step 5; Task 2 Step 4 §7.3 |
| References list | Task 2 Step 4 §11 |
| Build steps 1-7 | Tasks 2 and 3 |
| Success criteria - word count | Task 2 Step 6 |
| Success criteria - vectors printed | Task 2 Step 4 §3 |
| Success criteria - CI validation | Task 1 Steps 3, 6 |

No gaps.

**Placeholder scan:** No TBD/TODO. Both Sigma rules are given in full. All verification commands are complete and runnable. Section content is specified by required claims rather than finished prose, which is the deliverable of execution - every claim is enumerated and traceable to the spec.

**Type consistency:** Rule filenames are identical across Task 1 (creation), Task 1 Steps 4-5 (README), Task 2 Step 4 §7 (article), and Task 3 Step 6 (verification). Slug `n-able-ncentral-msp-supply-chain` is identical across Tasks 2 and 3. `NAV_RE` in Task 2 Step 6 is copied verbatim from `build_indexes.py:301`. The rule count 7 is consistent between Task 1 Step 3, Task 3 Step 3 and Task 3 Step 6.
