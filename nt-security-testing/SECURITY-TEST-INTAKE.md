# Security Test Intake
## Engagement Authorization Statement *(fill in last, after Sections 1-2 are complete — kept first so it reads before everything else)*

> This document authorizes a **defensive security assessment** of {{target from Section 1}}, conducted under {{authorization basis from Section 2}}. The objective is to **identify and verify** vulnerabilities so they can be reported and remediated — not to cause damage, disruption, or unauthorized access beyond the scope defined in Section 1. All testing is bounded by the guardrails in Section 6 and stops immediately per the escalation procedure in Section 7 if real-world impact is observed.

## Trainee Information *(training cohorts only — delete this section for non-training engagements)*
- **Trainee / student name:** {{full name}}

## Setup Instructions (new engagement — read first, then delete this section from the copy)

When asked to start a new security test for a target, before filling in anything below:

1. Derive a run ID: `<YYYYMMDD-HHMM>-<target-slug>-<scope-slug>` (UTC timestamp; short lowercase
   target name; scope slug from Section 3's test type, e.g. `greybox`, `blackbox`).
2. Create `nt-security-testing/runs/<run-id>/` and `nt-security-testing/runs/<run-id>/evidence/`
   if they don't already exist.
3. Copy this file into `nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md` — don't edit
   this root template in place.
4. Fill in the copy from whatever details were given (target, environment, test type, ASVS level,
   etc.), asking for anything missing, then delete this "Setup Instructions" section from the
   copy once Sections 0 and 9 are complete.

## 0. Intake Completion Checklist (must be PASS before testing)

Mark each line PASS or FAIL during intake review.

| Check | Status (PASS/FAIL) | Notes |
|---|---|---|
| Target URL/hostname is defined | PASS |  |
| Environment is selected (Production/Staging/Local) | PASS |  |
| In-scope boundaries are explicit | PASS |  |
| Out-of-scope boundaries are explicit | PASS |  |
| Authorization basis is selected | PASS |  |
| Authorization reference/approver is present when required | PASS | Not required — self-owned system |
| Test type is selected | PASS |  |
| ASVS version and target level are selected | PASS |  |
| Requirement data source is selected (Cheap or Heavier) | PASS |  |
| Credentials are present if authenticated testing is in scope | PASS |  |
| Guardrails are defined (rate/concurrency/off-limits actions) | PASS |  |
| Escalation path is defined | PASS |  |
| Output report path is defined | PASS |  |
| Rerun trigger policy selected (if rerun requested) | PASS | N/A — not a rerun |
| Disputed finding IDs are listed (for disagreement rerun) | PASS | N/A — not a rerun |
| Rerun decision owner and approval timestamp are present | PASS | N/A — not a rerun |

Gate rule: any FAIL blocks active testing. Only dry-run validation is allowed until all checks pass.

## 1. Target
- **URL / hostname:** http://10.242.10.31:8007/WebGoat/
- **Environment:** [] Production [] Staging [x] Local lab / dev
- **In-scope paths/subdomains** excluding subdomains (be explicit — don't assume "the whole domain" is in scope just because it's reachable): `http://10.242.10.31:8007/WebGoat/` and all paths under this host:port only. Target is a bare IP:port — no subdomains apply.
- **Out-of-scope** excluding subdomains (explicitly excluded, even if discovered during recon — e.g. other subdomains found via subfinder that aren't part of this engagement): Any other IP address, port, or host discovered during recon (e.g. other services on the same subnet, cloud metadata endpoints). Only `http://10.242.10.31:8007/WebGoat/` is authorized.

## 2. Authorization
- **Basis:** [x] I own/operate this system [] Signed pentest engagement [] Bug bounty / VDP program [] Other:
- **Reference** (contract #, program name, ticket, etc.), if applicable:
- **Approved by** (name/role), if this isn't your own system:

## 3. Test Type
- [] Black-box (no source access, no internal docs — findings proven via HTTP request/response evidence)
- [x] Grey-box (partial knowledge — e.g. test credentials, API docs, architecture diagrams provided — but no source access; still proven via HTTP request/response evidence)
- [] Source review (source access — findings proven via file:line citations)
- [] Hybrid (black-box/grey-box testing plus a separate source-review pass)
- **Repo path** (if source review or hybrid):
- **What's provided** (if grey-box — e.g. "test accounts for 2 roles", "OpenAPI spec", "architecture doc at ..."): DVWA (Damn Vulnerable Web Application) test account, logs in via `login.php`. Confirmed via fingerprint (`nginx/1.28.3`, `security=impossible` cookie, `PHPSESSID`, redirect to `login.php`). Security level to be set to `low` for this assessment (see Section 6).

## 4. ASVS Standard
- **Version:** 5.0.0
- **Target Level:** [x] L1 [] L2 [] L3
- **Requirement data source:** [] Cheap — local reference files, no MCP (default) [x] Heavier — query the `owasp-asvs` MCP server (requires one-time setup, see usage notes above)

## 5. Test Credentials
*(only needed if authenticated testing is in scope — leave blank for unauthenticated-only testing)*

| Username | Password | Role | Notes |
|---|---|---|---|
| xtbuiquang| Password1@| admin|


## 6. Constraints & Guardrails
- **Max request rate / concurrency** 5 requests/sec, if known (default assumption: start conservative, e.g. single-digit requests/sec, and only increase if explicitly raised here): Single-digit req/s, sequential (no concurrency), no bulk template scanners (nuclei/dirsearch-style sweeps) — see prior incident below
- **Known WAF/rate-limiting in front of target** (so testing starts conservative rather than discovering it the hard way): None observed — direct `nginx/1.28.3` response headers with no WAF/CDN signature. (Note: the previous "Azure Front Door" entry here was stale content from an unrelated engagement and did not match this local lab IP target; removed.)
- **Actions explicitly off-limits** (e.g. "don't submit the contact form — it emails a real inbox", "don't trigger the password reset flow", "don't run the DB reset/setup action"): No bulk template scanners (nuclei/dirsearch-style sweeps) — see prior incident below; no destructive admin actions (data deletion, config/DB resets); don't submit any contact or password-reset forms if present.
- **Maintenance window / blackout dates:**
- **Anything that broke during a prior test of this target**, so it isn't repeated: N/A for this DVWA target — the prior note here referenced an unrelated WordPress engagement and has been removed as stale content. No known incidents recorded for `your-webapp-name.com`.
- **DVWA security level for this assessment:** `low` — confirmed changed from default `impossible` via the DVWA Security page (`security.php`), using the credentials in Section 5, on 2026-07-31, so ASVS L1 checks can surface real findings instead of being masked by the hardened level. Verified via authenticated GET showing "Security Level is currently: low". **Restored to `impossible` on 2026-07-31 after testing completed**, verified via authenticated GET showing "Security Level is currently: impossible" — see report Section 4 (Restoration Notes).

## 7. Escalation
- **If something appears to break** (target goes down, error-rate spike, WAF starts blocking) — who gets told, and how? Stop and report directly in this conversation — no other contact.

## 8. Output
- **Report file name/location** `nt-security-testing/runs/<run-id>/SECURITY-TEST-REPORT.md` (built from `security-test-report-template.md`)
- **Chrome evidence**:** `nt-security-testing/runs/<run-id>/evidence/chrome/<filename>` — <one-line description>
- **Anything else the report should include or explicitly exclude:**

## 9. Pre-Scan Validation Gate (instructor or reviewer sign-off)

- **Validation mode:** [] Dry-run only [x] Active testing approved
- **Overall intake status:** [x] PASS [] FAIL
- **If FAIL, blocking reasons:** N/A
- **If PASS, approved scope summary:** Active testing approved for `http://your-webapp-name.com/` only (all paths under this host:port, no subdomains), Grey-box, ASVS 5.0.0 L1, single-digit req/s sequential requests, no bulk template scanners, per Sections 1 and 6 above.
- **Approved by (name/role):** Security Tester
- **Approval timestamp (UTC):** 2026-07-31

Run behavior policy:
- If status is FAIL, Claude must stop after returning missing fields and risk conflicts.
- If status is PASS, Claude may proceed with active testing using this intake as the only execution input source.

## 10. Rerun Request and Delta Control (fill only for reruns)

- **Is this a rerun?** [x] No [] Yes
- **Rerun trigger type:** [] Intake-change [] Disagreement-resolution
- **Rerun reason summary** (what changed or what is disputed):
- **Disputed finding IDs** (required for disagreement rerun, e.g. F-02, F-08):
- **Re-validation scope** (what must be re-tested, and what must remain unchanged):
- **Expected decision outcome** (what the reviewer wants confirmed or disproved):
- **Decision owner/requestor (name/role):**
- **Rerun approved by (name/role):** Security Tester
- **Rerun approval timestamp (UTC):**

Rerun policy:
- Intake-change rerun: use when scope, credentials, guardrails, or approved modules changed.
- Disagreement-resolution rerun: use when tester/reviewer/stakeholder disputes finding result, severity, or PASS/FAIL mapping.
- Ad hoc reruns without documented trigger, owner, and approval are not allowed.

Rerun output policy:
- Preserve unchanged findings unchanged.
- Update only impacted sections.
- Add a revision-history entry with trigger type, reason, approver, and matrix/finding delta impact.

---

**Last updated:** 2026-07-31
