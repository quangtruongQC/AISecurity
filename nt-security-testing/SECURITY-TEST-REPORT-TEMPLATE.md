<!--
TEMPLATE USAGE NOTES (delete this block when generating an actual report)

This is the standard template for any security test report. When asked to
"write a security test report," start from this file, fill in every
{{PLACEHOLDER}}, and delete whichever evidence format (A or B) doesn't apply
to a given finding — most tests use one format throughout, but a hybrid
test (e.g. black-box testing plus a separate source-review pass) can mix them.

Testing methodologies supported:

  - BLACK-BOX / DAST: no source access, no internal docs, findings proven
    via raw HTTP request/response evidence. Use Evidence Format A.
    Section 5 (Restoration Notes) and the TLS/network-level PoCs only
    apply here — delete Section 5 for source-review-only tests with no
    live target.

  - GREY-BOX: partial internal knowledge (test credentials, API docs,
    architecture diagrams) but no source access — still proven via
    Evidence Format A (request/response), since there's no code to cite.
    The difference from black-box shows up in Methodology (state what
    was provided) and in wider requirement coverage, since knowing the
    intended design lets you target areas a blind black-box pass would
    miss (e.g. role-based authorization checks when you have multiple
    tiers of test credentials).

  - SOURCE REVIEW / SAST: has code access, findings proven via file:line
    citations and code snippets. Use Evidence Format B. Section 4
    (Dependency Security) and code-level test-result percentages
    (Section 6.2 style table) are most relevant here.

  - HYBRID: black-box or grey-box testing plus a separate source-review
    pass — mix Evidence Format A and B per finding as appropriate.

Reference examples:
  - Black-box style: dvwa-asvs-l1-blackbox-pentest-report.md (repo root)
  - Grey-box style: 192.168.232.128-42001-asvs-l1-greybox-report.md (repo root)
  - Source-review style: none included in this repo yet — cite file:line pairs
    directly in Evidence Format B if you produce one.

Keep whichever sections apply to the test at hand; delete the rest rather
than leaving "Not applicable" placeholders scattered throughout — a lean,
accurate report beats a complete-looking one padded with N/A.

OWASP Top 10:2025 categories (for the optional per-finding tag in Section 3 —
skip it unless a finding maps cleanly onto one of these):
  A01:2025 Broken Access Control · A02:2025 Security Misconfiguration ·
  A03:2025 Software Supply Chain Failures · A04:2025 Cryptographic Failures ·
  A05:2025 Injection · A06:2025 Insecure Design · A07:2025 Authentication
  Failures · A08:2025 Software or Data Integrity Failures · A09:2025 Security
  Logging and Alerting Failures · A10:2025 Mishandling of Exceptional Conditions
-->

# {{TEST_TYPE}} Security Test Report

## {{TARGET_NAME}} — OWASP ASVS {{ASVS_VERSION}} {{ASVS_LEVEL}} Security Test

| | |
|---|---|
| **Target** | {{target URL, repo path, or system name}} |
| **Testing method** | {{Black-box (no source access) \| Grey-box (partial knowledge, no source) \| Source review (code access) \| Hybrid}} — all findings derived from {{external HTTP interaction \| static code analysis \| both}} |
| **Provided for testing** *(grey-box only — delete row otherwise)* | {{e.g. "test credentials for 2 roles", "OpenAPI spec", "architecture doc"}} |
| **Standard applied** | OWASP ASVS {{ASVS_VERSION}}, {{ASVS_LEVEL}} |
| **Application/system state** | {{e.g. "Security level set to `low`" / "Version 0.5.0, commit {{hash}}"}} |
| **Authorization** | {{engagement reference, or "Owner-operated system, self-authorized"}} |
| **Tester** | {{name / "Security Tester"}} |
| **Test date** | {{YYYY-MM-DD}} |
| **Environment status** | {{"Restored to default (...)" — omit this row entirely for source-review-only tests}} |

---

## 1. Executive Summary

{{2-4 sentences: what was tested, against what standard, and the headline result. State the count of failing requirements and how many yield critical impact (RCE, full data compromise, auth bypass), if any.}}

**Severity breakdown:** {{N}} Critical, {{N}} High, {{N}} Medium, {{N}} Low.

### Test Case Summary (from the Test Results Matrix)

Count this directly from the Test Results Matrix rows below — don't estimate. Grep for `**FAIL**`/`**PASS**` occurrences in the matrix to cross-check the manual tally before publishing.

Of the {{N}} ASVS {{ASVS_VERSION}} {{ASVS_LEVEL}} requirement rows evaluated for this target's surface:

| Result | Count | % of evaluated |
|---|---|---|
| **PASS** | {{N}} | {{%}} |
| **FAIL** | {{N}} | {{%}} |
| **N/A** *(not applicable to this app, or not tested/testable — see below)* | {{N}} | {{%}} |

Among requirements actually **exercised** (PASS + FAIL, excluding N/A), the pass rate is **{{N}}/{{N}} = {{%}}**.

Split the N/A bucket into two sub-counts rather than leaving it flat — they imply different next steps: rows that are genuinely **not applicable** to this system's architecture (e.g. no WebSocket/OAuth/XML surface) versus rows that are **not tested/not testable** in this pass (e.g. would need volume testing, source access, or simply weren't exercised this round). The latter group is the natural scope for a follow-up test.

{{Optional, for re-tests/improvement tracking: state pass rate and delta from a prior test, e.g. "improved from 66% to 87% (+21%) following remediation of Phase 1-3 findings."}}

---

## 2. Methodology

{{Describe the workflow actually used. Adapt the numbered list below — delete steps that don't apply, add ones that do.}}

1. **Recon** — {{HTTP header inspection, TLS presence check, exposed-file probing, tech stack fingerprinting}} *(black-box/grey-box)* / **Code review** — {{static analysis of entry points, dependency manifest, configuration files}} *(source review)*
2. **Scoping** — {{how applicable ASVS requirements were determined for this target's surface — e.g. "no JWT/OAuth surface, so V9/V10 marked not applicable"}}. **Requirement data source:** {{Cheap — local `asvs-5.0.0-level{{N}}-requirements.md` reference file(s) | Heavier — `owasp-asvs` MCP server}}, per the intake's §4 setting.
3. **Per-requirement verification** — for each ASVS {{level}} item classified as testable, {{sent a request crafted to prove/disprove the control and captured evidence \| traced the code path implementing the control and captured the relevant lines}}, rather than relying on tool signatures alone.
4. **Evidence-only exploitation** *(black-box/grey-box only)* — where a vulnerability was confirmed, the proof-of-concept was the minimum needed to demonstrate impact — no destructive or lateral action was taken.
5. **Restoration** *(black-box/grey-box only, delete if not applicable)* — all state changes made during testing were reverted before reporting.

Requirements requiring information not available to this test type (e.g. internal documentation for a black-box test, or runtime behavior for a source-only review) are marked **Not Testable** rather than pass/fail.

---

## 3. Findings

> **Reproducing these findings:** {{for black-box/grey-box: note that session cookies/tokens are single-use and how to obtain fresh ones. For source review: note the commit/version the line citations refer to, since line numbers drift.}}

### F-01 — {{Finding Title}} ({{Severity: Critical/High/Medium/Low}})
**ASVS:** {{Shortcode}} — *{{short requirement description}}*
**CWE:** [CWE-{{ID}}](https://cwe.mitre.org/data/definitions/{{ID}}.html) — {{CWE title}} *(optional — include only when there's a clean mapping; skip rather than force a stretch fit)*
**OWASP Top 10 (2025):** {{A0X}}:2025 — {{category title, see list in the usage notes above}} *(optional, same rule as CWE)*

{{One or two sentences describing the root cause.}}

<!-- EVIDENCE FORMAT A — Black-box/grey-box / PoC. Use for DAST findings. -->
Request:
```http
{{METHOD}} {{path}} HTTP/1.1
Host: {{host}}
{{other relevant headers}}
Authorization: {{if applicable — redact to first/last 4 chars, e.g. "Bearer eyJh…3f9c", not the full token}}
Cookie: {{session cookie, if applicable — same redaction rule; full values are only OK when the report stays internal and the credential is already expired/single-use, per the reproducing-findings note above}}

{{request body, if POST/PUT — show the exact bytes sent, urlencoded/JSON/multipart as appropriate}}
```

Response ({{status code}}, relevant excerpt):
```http
HTTP/1.1 {{status}}
{{relevant response headers}}

{{response body excerpt proving the finding — the exact string/error/data that demonstrates impact, not a paraphrase}}
```

{{One sentence connecting the evidence to the claim — e.g. "The trailing X confirms arbitrary command execution."}}

<!-- EVIDENCE FORMAT B — Source review. Use for SAST/code-level findings. -->
**Location:** `{{file path}}:{{line numbers}}`
```{{language}}
{{the actual vulnerable code, verbatim from the file — not reconstructed from memory}}
```
{{One or two sentences explaining why this code fails the control.}}

- **Impact:** {{concrete consequence — what an attacker gains, not a generic severity label}}. {{Optional, for larger/regulated engagements: break out by Confidentiality/Integrity/Availability, plus a Compliance line (e.g. GDPR, PCI-DSS, SOC 2) if relevant — skip the breakdown when one sentence already covers it.}}
- **Remediation:** {{specific, actionable fix — name the technique/library/pattern, not just "sanitize input"}}

### F-02 — {{...}}
{{repeat the F-01 structure for each finding, numbered sequentially}}

---

## 4. Dependency Security *(source-review tests — delete this section for pure black-box/grey-box tests)*

### 4.1 Direct Dependencies

| Package | Version | Vulnerabilities | Status |
|---|---|---|---|
| {{package}} | {{version}} | {{None known / CVE-XXXX-XXXXX}} | {{PASS/FAIL}} |

### 4.2 Recommendations
{{Prioritized list — e.g. add `npm audit`/`pip-audit` to CI, automate dependency updates, pin versions.}}

---

## 5. Restoration Notes *(black-box/grey-box tests with live state changes — delete this section for source-review-only or fully read-only tests)*

All state modified during testing was reverted before this report was finalized:
- {{e.g. "Admin password reset to default via direct database update."}}
- {{e.g. "Uploaded proof-of-concept file removed."}}
- {{e.g. "Test data/entries deleted."}}

---

## 6. ASVS {{ASVS_VERSION}} {{ASVS_LEVEL}} Test Results Matrix

Only requirements applicable to this target's surface are listed; note the applicability methodology if any category is entirely excluded (e.g. "no web frontend, so all V3 items are not applicable").

| Shortcode | Requirement | Result |
|---|---|---|
| {{V_.X.X}} | {{short requirement text}} | **{{PASS/FAIL/Not applicable/Not tested}}** — {{finding ID if FAIL}} |

{{For larger code-based tests, optionally add a summary table by chapter: Requirements / Applicable / Passed / Failed / % Pass.}}

---

## 7. Priority Recommendations

Group by urgency, not by discovery order:

1. **Critical/High — fix immediately:** {{list, referencing finding IDs}}
2. **Medium — fix before next release:** {{list}}
3. **Low — track as backlog:** {{list}}

For each, state effort and impact if known (e.g. "Effort: 2h, Impact: closes F-05 CSRF exposure").

---

## 8. Conclusion

{{2-4 sentences: overall risk posture, whether the target is fit for its intended deployment context as-is, and what closing the top findings would change. Avoid restating every finding — this is the one paragraph a stakeholder reads if they read nothing else.}}

---

## 9. Revision History *(delete for a first-time/one-off test; keep for any test that will be re-run and compared over time)*

### Version {{X.X}} — {{YYYY-MM-DD}}
{{What changed since the prior version, and the pass-rate delta if re-measuring against a previous test of the same target.}}
