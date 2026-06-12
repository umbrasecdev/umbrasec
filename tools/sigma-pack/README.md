# sigma-pack

[![Sigma validation](https://github.com/atraxsrc/umbrasec/actions/workflows/sigma-validate.yml/badge.svg)](https://github.com/atraxsrc/umbrasec/actions/workflows/sigma-validate.yml)

The detection rules and queries published in [UMBRASEC research writeups](https://umbrasec.dev/research/),
collected as runnable files. Honest status: **early** - this pack grows one writeup
at a time, and right now it contains exactly what the two published writeups cover.
Nothing here claims to be more finished than it is.

Every rule ships with the context that makes it usable: the writeup explains the
technique, the log artifacts, the tuning knobs, and the false-positive profile.
Read the writeup before deploying the rule. Every Sigma rule in `rules/` is
syntax-validated with [sigma-cli](https://github.com/SigmaHQ/sigma-cli) in CI on
every change - that's what the badge above checks.

## ATT&CK coverage

| Rule / query | Type | MITRE ATT&CK | Tactic | Status |
|---|---|---|---|---|
| [`kerberoasting-rc4-service-ticket.yml`](rules/windows/kerberoasting-rc4-service-ticket.yml) | Sigma | [T1558.003](https://attack.mitre.org/techniques/T1558/003/) Kerberoasting | Credential Access | experimental |
| [`kerberoasting-spn-fanout.yml`](rules/windows/kerberoasting-spn-fanout.yml) | Sigma (correlation) | [T1558.003](https://attack.mitre.org/techniques/T1558/003/) Kerberoasting | Credential Access | experimental |
| [`kerberoasting-honeypot-spn.yml`](rules/windows/kerberoasting-honeypot-spn.yml) | Sigma | [T1558.003](https://attack.mitre.org/techniques/T1558/003/) Kerberoasting | Credential Access | experimental |
| [`oauth-consent-sensitive-scopes.kql`](queries/kql/oauth-consent-sensitive-scopes.kql) | KQL | [T1528](https://attack.mitre.org/techniques/T1528/) Steal Application Access Token | Credential Access | query |
| [`oauth2-permission-grant-post.kql`](queries/kql/oauth2-permission-grant-post.kql) | KQL | [T1528](https://attack.mitre.org/techniques/T1528/) Steal Application Access Token | Credential Access | query |
| [`app-role-assignment.kql`](queries/kql/app-role-assignment.kql) | KQL | [T1528](https://attack.mitre.org/techniques/T1528/) Steal Application Access Token | Credential Access | query |
| [`litellm-proxy-spawns-shell.yml`](rules/linux/litellm-proxy-spawns-shell.yml) | Sigma | [T1190](https://attack.mitre.org/techniques/T1190/) Exploit Public-Facing App; [T1059](https://attack.mitre.org/techniques/T1059/) Command &amp; Scripting | Initial Access / Execution | experimental |
| [`litellm-mcp-test-endpoint.yml`](rules/web/litellm-mcp-test-endpoint.yml) | Sigma | [T1190](https://attack.mitre.org/techniques/T1190/) Exploit Public-Facing App | Initial Access | experimental |

`experimental` is the [Sigma status](https://sigmahq.io/docs/basics/rules.html) the
rules themselves declare - new rules, not yet battle-tested by many environments.
KQL queries are plain queries with no Sigma status; the CI validation covers the
Sigma rules only.

## Contents

### Kerberoasting (MITRE ATT&CK T1558.003) - Sigma, Windows Security Event 4769

Writeup: [Detecting Kerberoasting: A Practical Walkthrough with Sigma](https://umbrasec.dev/research/detecting-kerberoasting.html)

| File | What it catches | Level |
|---|---|---|
| [`rules/windows/kerberoasting-rc4-service-ticket.yml`](rules/windows/kerberoasting-rc4-service-ticket.yml) | RC4 (0x17) service-ticket request in an AES-capable domain - the deliberate downgrade signal | medium |
| [`rules/windows/kerberoasting-spn-fanout.yml`](rules/windows/kerberoasting-spn-fanout.yml) | One account requesting tickets for many distinct SPNs in a short window (Sigma correlation rule) | - |
| [`rules/windows/kerberoasting-honeypot-spn.yml`](rules/windows/kerberoasting-honeypot-spn.yml) | Any ticket request naming your decoy SPN account - edit the `ServiceName` to your decoy first | high |

Prerequisite: *Audit Kerberos Service Ticket Operations* (Success) enabled on all
domain controllers, Security log shipped from every DC.

### OAuth consent phishing (MITRE ATT&CK T1528) - KQL, Microsoft Sentinel / Log Analytics

Writeup: [Detecting OAuth Consent Phishing in Microsoft 365](https://umbrasec.dev/research/detecting-oauth-consent-phishing.html)

| File | What it catches |
|---|---|
| [`queries/kql/oauth-consent-sensitive-scopes.kql`](queries/kql/oauth-consent-sensitive-scopes.kql) | "Consent to application" audit events granting mail/files/directory scopes |
| [`queries/kql/oauth2-permission-grant-post.kql`](queries/kql/oauth2-permission-grant-post.kql) | The Graph API POST that creates a delegated permission grant (highest fidelity) |
| [`queries/kql/app-role-assignment.kql`](queries/kql/app-role-assignment.kql) | App-only (application permission) role assignments - standing access |

Prerequisite: Entra ID `AuditLogs` and `MicrosoftGraphActivityLogs` flowing into
your workspace. The shape of `modifiedProperties` shifts between schema versions -
validate field names against your own tenant before you alert on anything.

### LiteLLM command injection - CVE-2026-42271 (MITRE ATT&CK T1190 / T1059)

Writeup: [Detecting the LiteLLM Command Injection (CVE-2026-42271) in Your AI Gateway](https://umbrasec.dev/research/detecting-litellm-command-injection.html)

| File | What it catches | Level |
|---|---|---|
| [`rules/linux/litellm-proxy-spawns-shell.yml`](rules/linux/litellm-proxy-spawns-shell.yml) | The LiteLLM proxy process spawning a shell or recon/download utility - the command-injection landing (high fidelity) | high |
| [`rules/web/litellm-mcp-test-endpoint.yml`](rules/web/litellm-mcp-test-endpoint.yml) | POST requests to the vulnerable MCP preview endpoints (`/mcp-rest/test/connection`, `/mcp-rest/test/tools/list`) - the front-door signal | medium |

Prerequisite: for the host rule, Linux process-creation telemetry (Auditd execve,
Sysmon for Linux, or EDR) from the LiteLLM host/container; for the web rule, HTTP
access logs from the reverse proxy / ingress in front of LiteLLM. Scope the host
rule to your LiteLLM hosts to cut generic `python` parent noise. Patch status is
the real control - these cover the window before you've patched and the assets you
haven't found yet.

## How to use these

1. Read the writeup for the rule you're deploying.
2. Run the rule in **report-only mode** first and baseline your environment.
3. Tune per the notes in each file (thresholds, allowlists, the honeypot account name).
4. Only then page anyone with it.

Sigma rules convert to your SIEM's query language with
[sigma-cli / pySigma](https://github.com/SigmaHQ/sigma-cli).

## A rule misbehaved?

That's exactly the feedback this project wants -
[open an issue](https://github.com/atraxsrc/umbrasec/issues). Corrections are credited.

License: MIT, same as the rest of the repo's code.
