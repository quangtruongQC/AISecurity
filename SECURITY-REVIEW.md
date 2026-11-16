# WebGoat Run #5 Evidence Review

**Review date:** 2026-11-16
**Scope:** Review of Run #5 artifacts against the updated WebGoat intake and report template.
**Review method:** Read-only artifact review; no live requests were sent during this review.

## Summary

Run #5 is incomplete and does not substantiate its report of 21 confirmed findings. Its evidence directory contains 20 files, most of which record curl timeouts rather than HTTP responses. The saved output logs show that testing stopped during evidence creation with a Python `OSError`; another attempted PowerShell script failed to parse. The report's claim of completion and its finding count must not be relied on.

No new WebGoat vulnerability is confirmed by Run #5. Findings with valid evidence from earlier runs may be described only as historical observations, with their original run identifiers and evidence references; they were not reproduced by Run #5.

## Findings

| # | Severity | File | Issue | Confidence |
|---|---|---|---|---|
| 1 | High | `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/SECURITY-TEST-REPORT.md` | The report claims 21 confirmed findings and successful completion, but the run failed before completing the test set. | 10/10 |
| 2 | High | `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/evidence/http/` | Evidence does not support the finding claims: most captured files contain timeout/error text, and multiple filenames cited in the report are absent. | 10/10 |
| 3 | Medium | `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/evidence/http/03-sqli-3c.json` | The attempted SQL injection request contains a destructive `DROP TABLE` payload, prohibited by intake §3h. The timeout does not establish whether it reached the target or changed state. | 10/10 |
| 4 | Medium | `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/SECURITY-TEST-REPORT.md` | Finding ID F-14 is reused for unrelated claims, and the report lacks the template's reconciled ASVS results matrix and PASS/FAIL/N/A counts. | 10/10 |

## Evidence checked

- `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/evidence/http/`: 20 files. The login and most injection/access-control/error artifacts contain curl timeout messages; the brute-force file is a response-size summary, not paired raw request/response evidence; the header and cookie files list names, not response headers.
- `nt-security-testing/runs/run5-test-output.log`: ends with a Python `OSError` while creating an evidence filename.
- `nt-security-testing/runs/run5_output.log`: contains PowerShell parse errors.
- `nt-security-testing/runs/20261116-1430-webgoat-l1-greybox-run5/SECURITY-TEST-REPORT.md`: cites missing evidence such as `pt-11a.txt`, `ssrf-12a.json`, and `20-plain-http-test.txt`, and repeats F-14.
- `nt-security-testing/SECURITY-TEST-INTAKE-webgoat.md` §3h: requires raw execution logs, crash review, verified routes, reconciled evidence listings, unique finding IDs, and prohibits destructive payloads.
- `nt-security-testing/SECURITY-TEST-REPORT-TEMPLATE.md` §§1 and 6: requires an ASVS matrix and a summary reconciled directly from matrix results.

## Required disposition

1. Treat Run #5 as incomplete; do not count its findings as confirmed.
2. Preserve its logs and artifacts as evidence of the failed run; do not replay the destructive payload.
3. Keep any earlier supported findings explicitly labeled as historical, not reproduced.
4. For a new run, verify each endpoint from WebGoat navigation before testing, capture actual request/response pairs and the raw tool log, and reconcile every cited artifact against the evidence-directory listing.
5. Mark unexercised controls as not tested or not testable, not PASS. Complete the template's ASVS matrix and derive its counts from the matrix.

## Limitations

This review evaluates report and execution evidence only. It does not assert that the WebGoat target is secure or insecure, and it does not independently reproduce earlier findings.
