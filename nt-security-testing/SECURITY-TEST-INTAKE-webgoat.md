# Security Test Intake
## Engagement Authorization Statement

> This document authorizes a **defensive security assessment** of `http://10.242.10.31:8007/WebGoat/`, conducted under self-ownership of the system. The objective is to **identify and verify** vulnerabilities so they can be reported and remediated — not to cause damage, disruption, or unauthorized access beyond the scope defined in Section 1. All testing is bounded by the guardrails in Section 6 and stops immediately per the escalation procedure in Section 7 if real-world impact is observed.

## Trainee Information
- **Trainee / student name:** xtbuiquang

## 0. Intake Completion Checklist (must be PASS before testing)

| Check | Status (PASS/FAIL) | Notes |
|---|---|---|
| Target URL/hostname is defined | PASS | |
| Environment is selected (Production/Staging/Local) | PASS | |
| In-scope boundaries are explicit | PASS | |
| Out-of-scope boundaries are explicit | PASS | |
| Authorization basis is selected | PASS | |
| Authorization reference/approver is present when required | PASS | Not required — self-owned system |
| Test type is selected | PASS | |
| ASVS version and target level are selected | PASS | |
| Requirement data source is selected (Cheap or Heavier) | PASS | |
| Credentials are present if authenticated testing is in scope | PASS | |
| Guardrails are defined (rate/concurrency/off-limits actions) | PASS | |
| Escalation path is defined | PASS | |
| Output report path is defined | PASS | |
| Rerun trigger policy selected (if rerun requested) | PASS | Owner requested an availability retry after Run #7 timed out; this update additionally sets coverage/severity expectations for Run #9+ |
| Disputed finding IDs are listed (for disagreement rerun) | PASS | None — this is a coverage-expansion update, not a finding-disagreement rerun |
| Rerun decision owner and approval timestamp are present | PASS | xtbuiquang / Security Tester; 2026-11-16T10:11:10Z |

Gate rule: any FAIL blocks active testing. Only dry-run validation is allowed until all checks pass.

## 1. Target
- **URL / hostname:** `http://10.242.10.31:8007/WebGoat/`
- **Environment:** [ ] Production [ ] Staging [x] Local lab / dev
- **In-scope paths/subdomains:** `http://10.242.10.31:8007/WebGoat/` and all paths under this host:port only. Target is a bare IP:port — no subdomains apply. (Note: WebGoat also ships a companion app, WebWolf, typically on an adjacent port — **not in scope** unless explicitly added here.)
- **Out-of-scope:** Any other IP address, port, or host discovered during recon (e.g. other services on the same subnet, cloud metadata endpoints, any WebWolf instance). Only `http://10.242.10.31:8007/WebGoat/` is authorized.

## 2. Authorization
- **Basis:** [x] I own/operate this system [ ] Signed pentest engagement [ ] Bug bounty / VDP program [ ] Other:
- **Reference:** —
- **Approved by:** — (self-owned)

## 3. Test Type
- [ ] Black-box
- [x] Grey-box (partial knowledge — test credentials provided — but no source access; findings proven via HTTP request/response evidence)
- [ ] Source review
- [ ] Hybrid
- **Repo path:** N/A
- **What's provided:** WebGoat test account credentials (see Section 5). WebGoat is OWASP's intentionally-vulnerable training web app (Java/Spring Boot). Login is via WebGoat's own `/WebGoat/login` flow (not `login.php`); session tracked via `JSESSIONID` (not a DVWA-style `security=` cookie). WebGoat has no "security level" toggle — its lessons are vulnerable by design at a fixed difficulty, so there is no equivalent of DVWA's low/medium/high/impossible setting to configure.

## 3b. Test Depth & Coverage Checklist *(added after run #1 produced only 2/9 expected findings — forces systematic coverage instead of a passive/header-only pass)*

Run #1 explicitly self-reported as **"not a full ASVS L1 assessment"** and a **"limited CORS check"**, and only surfaced passive, header-level findings (missing `Secure` cookie attribute, missing security headers). To raise coverage toward the full finding set, this run must walk every ASVS L1 category below **actively** (sending real test requests/payloads per the guardrails in Section 6 — guardrails constrain *rate*, not *depth*: single-digit req/s and no bulk scanners still allows one deliberate, hand-crafted request per check).

Mark each category PASS (actively tested, finding or no finding either way) / SKIPPED (explain why) — a report with any category left blank is incomplete:

| ASVS L1 Category | Must actively test (not just observe headers) | Status |
|---|---|---|
| Authentication | Login flow, session fixation, weak lockout/brute-force limits, credential transport | |
| Session Management | Cookie flags (Secure/HttpOnly/SameSite), session timeout, session invalidation on logout | |
| Access Control / IDOR | Modify IDs/params to access other users' data or restricted lessons; confirm what the `xtbuiquang` account can/can't reach vs. what it should | |
| Input Validation / Injection | SQLi, command injection, path traversal — send actual probe payloads into each relevant WebGoat lesson's input fields, not just note the field exists | |
| XSS (reflected/stored/DOM) | Submit actual test payloads where WebGoat lessons accept user input, observe reflection/encoding | |
| CSRF | Check for anti-CSRF tokens on state-changing requests; attempt a cross-origin request if safe to simulate | |
| CORS | Full test: send requests with varied `Origin` headers, include a preflight `OPTIONS`, and a credentialed request — not just absence-check | |
| File Upload (if present in scope lessons) | Attempt disallowed file types/extensions within the lesson's intended exercise, observe server-side validation | |
| SSRF (if present in scope lessons) | Attempt server-side request to an internal/benign target within the lesson's intended exercise | |
| XXE (if present in scope lessons) | Attempt XML external entity payload within the lesson's intended exercise | |
| Transport Security | HTTP vs HTTPS enforcement, cookie `Secure` flag (already found in run #1) | |
| Security Headers | CSP, X-Content-Type-Options, Referrer-Policy, COOP, HSTS (already found in run #1) | |
| Error Handling / Info Leakage | Trigger errors (malformed input, invalid IDs) and check for stack traces/verbose errors | |
| Business Logic (lesson-specific) | For each WebGoat lesson in scope, attempt the lesson's intended "solve" condition as a proxy for a real-world logic flaw | |

**Mapping (confirmed from login — all 13 categories are visible to `xtbuiquang`, so no ASVS category below should be SKIPPED for "lesson not present" reasons):**

| ASVS L1 Category (Section 3b) | WebGoat sidebar category to walk |
|---|---|
| Authentication | (A7) Identification & Authentication Failures |
| Session Management | (A7) Identification & Authentication Failures; General |
| Access Control / IDOR | (A1) Broken Access Control |
| Input Validation / Injection (SQLi, path traversal, etc.) | (A3) Injection |
| XSS | (A3) Injection; Client side |
| CSRF | General; Client side |
| CORS | Client side |
| File Upload | (A8) Software & Data Integrity Failures |
| SSRF | (A10) Server-Side Request Forgery |
| XXE | (A3) Injection |
| Transport Security | General; (A2) Cryptographic Failures |
| Security Headers | (A5) Security Misconfiguration |
| Error Handling / Info Leakage | (A5) Security Misconfiguration; (A9) Security Logging & Monitoring Failures |
| Business Logic (lesson-specific) | Challenges |

Not yet mapped to a Section 3b row but present in the sidebar and should still be walked for completeness: **(A6) Vulnerable & Outdated Components** (dependency/version-based findings — add as its own line item in the report even though it's not a request/response finding in the traditional sense).

## 3c. In-Scope WebGoat Lessons/Modules *(fill in — leaving this blank is likely why run #1 under-covered)*

List the specific WebGoat lesson categories to walk through (WebGoat organizes lessons by category in its UI sidebar, e.g. "A1 Injection", "A2 Broken Authentication", "Cross-Site Scripting", "A5 Access Control", "CSRF", "SSRF", "XXE", etc.). If left blank, default to **all lesson categories visible to the `xtbuiquang` account**, confirmed by logging in and enumerating the sidebar before starting, rather than assuming which ones are reachable.

- **In-scope lesson categories** (confirmed by logging in as `xtbuiquang` and reading the sidebar, screenshot on file):
  1. Introduction
  2. General
  3. (A1) Broken Access Control
  4. (A2) Cryptographic Failures
  5. (A3) Injection
  6. (A5) Security Misconfiguration
  7. (A6) Vulnerable & Outdated Components
  8. (A7) Identification & Authentication Failures
  9. (A8) Software & Data Integrity Failures
  10. (A9) Security Logging & Monitoring Failures
  11. (A10) Server-Side Request Forgery (SSRF)
  12. Client side
  13. Challenges
- **Confirmed account role/visible categories:** `xtbuiquang` sees **all** categories above — WebGoat does not restrict lesson visibility by role; every registered user gets the full lesson set by default. So "role" in Section 5 should read as a standard registered user with full lesson access, not a privileged/admin distinction. Note A4 (Insecure Design) is absent from the sidebar — this is expected (WebGoat has no dedicated A4 lesson category), not a missing permission.

## 3d. Evidence Requirements *(added after run #2 reported 10 findings with prose-only descriptions and no raw evidence — mandatory from this run onward)*

**No finding may be marked "Confirmed" without an attached raw evidence artifact.** A sentence
describing what happened (e.g. "returned the full user_data table") is not evidence — it is a claim.
Confidence scores are meaningless without something independently checkable behind them.

For every finding, at least one of the following must be saved under
`nt-security-testing/runs/<run-id>/evidence/` and referenced by filename in the finding writeup:

| Evidence type | Required for |
|---|---|
| Raw HTTP request (full headers + body) | Any finding involving a crafted/forged request (SQLi, XXE, CSRF, SSRF, IDOR, injection payloads) |
| Raw HTTP response (full headers + body, or the relevant excerpt) | Same as above — request and response evidence are paired, not optional alternates |
| Screenshot (Chrome, per Section 8 path) | Anything visually confirmed in the WebGoat UI (lesson "completed" banner, stored XSS execution, phone-home callback) |
| Short log excerpt with timestamps | Timing/sequence-dependent findings (e.g. login-lockout testing — must show all N attempts with timestamps, not just "N failed logins") |

**Rules:**
- A finding with only a prose description and no file reference must be downgraded from "Confirmed" to **"Reported — evidence pending"** until the artifact is attached. It cannot appear in the Executive Summary's confirmed-finding count until then.
- Raw request/response capture must come from the actual tool/proxy transcript used to perform the test (e.g. curl output, HTTP client tool log) saved verbatim — not reconstructed from memory after the fact.
- Redact only the test account's own password if it appears in captured requests; do not redact anything else (the whole point is independent verifiability).
- The final report must list, per finding, the evidence filename(s) it relies on, so the report and the evidence directory can be cross-checked file-by-file.
- **Screenshot cross-check (added after Run #3 — `04-idor-crossuser-profile-disclosed.png` showed an unrelated lesson step, not the claimed cross-user disclosure):** Before submitting the report, for every cited screenshot, re-open the image and verbatim-compare its visible UI text/state against the exact claim sentence it's attached to (e.g. if the finding says "'Well done, you found someone else's profile' feedback visible", that literal text must actually be visible in the image). A screenshot that shows a different lesson step, a different account's data, or is blank/not-fully-loaded must be retaken before the report is finalized — do not submit a "close enough" or thematically-related screenshot in its place.
- **Evidence timestamp window (added after Run #3 — the F-08 stored-XSS payload's creation timestamp, `00:44:51`, predated this run's own session start, meaning the actual injection was never captured within Run #3's evidence):** Every evidence file's timestamp (request/response `Date` header, screenshot EXIF/capture time, or log timestamp) must fall within the current run's own session window (first request timestamp → last request timestamp of this run). If a finding's proof necessarily relies on state created in an earlier run/session (e.g. a stored payload that already existed before this run began), the finding writeup must say so explicitly — e.g. "payload persisted from a prior session; this run's own injection attempt(s) are in `<filename>` and [succeeded/failed]" — rather than phrasing it as if this run performed the injection. A finding is not disqualified by reusing older state, but the report must never imply this run reproduced something it didn't actually capture.

## 3e. Advanced / Deepening Test Additions *(beyond the 14 base ASVS L1 categories — targets config/deployment issues a lesson-by-lesson pass tends to miss)*

Add these to Section 3b's coverage table as additional rows. All are still within existing guardrails (single-digit req/s, sequential, no bulk scanners) — they are additional *targets*, not higher request volume.

| Additional item | What to check | Why it matters here |
|---|---|---|
| **Spring Boot Actuator exposure** | Probe `/actuator`, `/actuator/health`, `/actuator/env`, `/actuator/heapdump`, `/actuator/beans`, `/actuator/mappings` (one request each) | WebGoat runs on Spring Boot; exposed actuator endpoints are one of the most common *real* misconfigurations on this stack and are independent of any lesson |
| **HTTP method tampering** | Send `OPTIONS` and `TRACE` to a handful of endpoints; check `Allow` header and whether `TRACE` is enabled (XST risk) | Pure config issue, cheap to check, commonly missed |
| **Component/version fingerprinting for (A6)** | Identify the exact WebGoat/Spring Boot version in use (response headers, `/actuator/info` if exposed, static asset paths) and check it against known public CVEs | Turns the "(A6) Vulnerable & Outdated Components" row from "enumerated only" into an actual evidence-backed finding or explicit negative result |
| **Insecure Deserialization lesson (A8)** | If present in the sidebar under (A8), actively attempt the lesson's intended deserialization exploit, not just "enumerated" | Left as "enumerated only" in run #2 — same pattern that caused run #1's under-coverage |
| **JWT handling (if present under A7)** | If WebGoat's JWT lessons are present, actively test alg-confusion / `none`-algorithm / signature-stripping as the lesson intends | A7 was only partially walked (AuthBypass only) in run #2 |
| **Server-Side Template Injection (SSTI)** | Check if any input field reflects template-engine syntax (e.g. `${7*7}`) unescaped | Common in Java apps alongside XXE/injection, not yet explicitly tested |
| **Mass assignment / parameter pollution** | On a state-changing endpoint, add an unexpected extra field (e.g. `role=admin`) or duplicate a parameter and observe handling | Cheap, single-request check, not yet covered |
| **Clickjacking (frame-ability)** | Confirmed implicitly by missing `X-Frame-Options`/CSP — explicitly note whether the login page itself can be framed, since that's the higher-impact variant | Strengthens the headers finding with a concrete framing PoC instead of just a header-absence note |
| **Debug/test endpoints left enabled** | Check for `/swagger-ui`, `/v2/api-docs`, `/h2-console`, or similar dev-only paths | Common leftover in Spring Boot deployments, zero-cost to check |

Any row above that returns a finding goes into the report's findings section with the same evidence requirement as Section 3d — no exceptions for "advanced" findings.

## 3f. Run #4 Deepening Targets — resolving Run #3's inconclusive items

Run #3 left three items inconclusive, and root-cause analysis shows **the same underlying mistake** caused (or contributed to) all of them: raw `curl` requests were hand-crafted by *guessing* the request format (JSON body, then form-encoded body) against `/WebGoat/CrossSiteScriptingStored/stored-xss`, both attempts failing with the identical `Comment.getText()` NullPointerException — meaning the guessed field name/shape was wrong both times, and this was never corrected or diagnosed. For JWT, the exact vulnerable endpoint was never located. For Insecure Deserialization, the baseline request format worked (got a real "not the VulnerableTaskHolder object" response) but crafting the actual exploit payload was not attempted.

**Required method for Run #4 — capture-then-replay, not guess-then-hope:**

1. **Solve the lesson once manually in the browser first**, with Chrome DevTools' Network panel open (Preserve log on), before writing any curl command. This gets the exact request (URL, method, headers, body shape/field names) the lesson's own JavaScript actually sends — eliminating the guessing that caused the Run #3 500 errors.
2. **Export that real request** (DevTools → right-click request → Copy as cURL, or read the raw Network panel entry) and save it as evidence (`evidence/http/<n>-<name>-browser-captured-request.txt`) — this is itself valid raw evidence per Section 3d, and also becomes the template for any follow-up crafted/malicious variant.
3. **Only after step 1–2 succeed**, modify the captured request's payload to carry the actual attack content (the stored-XSS resubmission, the JWT token tampering, the deserialization gadget), and capture that crafted request/response pair the same way.

**Specific targets for Run #4:**

| Item | What to do differently this run |
|---|---|
| **CrossSiteScriptingStored submission format** | Capture the real browser request for posting a comment (step above) before any further SSTI or stored-XSS resubmission attempt. This unblocks both the SSTI retest and gives F-08 a genuine within-run injection request, closing the Run #3 evidence gap on this finding. |
| **JWT (A7)** | From the sidebar, open each JWT sub-lesson individually (do not rely on `/JWT/votings` alone — that was the Challenges-overview endpoint, not a vulnerable lesson endpoint) and capture the real request/response for each step via the Network panel. Identify which sub-lesson issues/accepts a JWT, then attempt the lesson's own intended bypass (e.g. `alg=none`, weak/guessable signing secret, or signature-stripping) using a captured-and-modified request. |
| **Insecure Deserialization (A8)** | The baseline request format already works (confirmed in Run #3's `19-deserialization-baseline-request.txt`). Next step: capture the lesson's own "generate a valid token" flow (if the UI provides one, e.g. a button that produces a sample serialized object), inspect/modify that real serialized payload rather than hand-building one, and resubmit. If crafting a working malicious serialized object genuinely requires external tooling (ysoserial) beyond this engagement's "no bulk tooling" guardrail, state that explicitly as the stopping reason — but first confirm the simpler "modify the lesson-provided object" path has actually been tried and failed, since it may not require external tooling at all. |

Each of these, if it yields a finding, must meet the full Section 3d evidence bar (paired request/response, correct cross-checked screenshot if applicable, timestamp within Run #4's own window) — no exceptions for items that were previously inconclusive.

## 3g. Coverage Completeness Target (Run #4+) *(reference benchmark shared from another tester's run in this course: >16 total findings, >9 of which High/Critical — used here as a coverage-completeness check, not a findings quota)*

**Rule — read before anything else in this section:** A fixed "must find N bugs" target creates a perverse incentive to inflate severity, split one real issue into several report entries, or report low-value/duplicate items just to hit a number. **This is explicitly prohibited.** If this run's genuine, evidence-backed finding count falls short of the reference benchmark, the report must say so and explain the coverage gap honestly (e.g. "fewer assignment-level findings because X lesson category was not fully walked") rather than padding the count. The benchmark may also simply reflect a different WebGoat version, different ASVS scope, or looser severity criteria than this engagement uses — it is not proof that 16+/9+ is the "correct" number for this target.

**What legitimately increases coverage (apply these before assuming more bugs don't exist):**

1. **Walk every numbered assignment within each lesson, not just one representative assignment per category.** Run #3 tested one assignment per category (e.g. only `SqlInjection/assignment5b` out of Injection's full assignment set, only one step of CrossSiteScriptingStored). Each WebGoat lesson category contains multiple distinct, separately-exploitable assignments (SQL injection alone spans numeric and string injection, blind boolean/time-based variants, advanced/numeric variants, update/insert-based injection, etc.; XSS spans reflected, DOM, and stored variants across several numbered steps; Access Control spans IDOR, Missing Function AC, and a privilege-escalation step; etc.). For Run #4, enumerate and attempt **every numbered sub-step visible in each lesson's own step indicator** (the small numbered circles at the top of each lesson page), not just the first vulnerable one found, and give each genuinely distinct assignment its own finding ID if it's independently exploitable — do not bundle unrelated assignments under one finding just to keep the count low, and do not split one assignment into several findings just to raise it.
2. **Walk the categories Run #3 only "enumerated" without active testing:** (A2) Cryptographic Failures, (A9) Security Logging & Monitoring, General, Introduction, Challenges (beyond the one `/JWT/votings` probe) — each likely has its own dedicated assignment(s) with independently verifiable findings.
3. **Suspicious UI/design review (new — not covered by Sections 3b/3e):** actively inspect page source and client-side behavior for design-level smells, each a candidate finding if confirmed with evidence:
   - View-source / HTML comments revealing hidden admin links, TODOs, or credentials (the Run #3 report already flagged `access-control/users`/`access-control/config` links found in HTML comments — these should be followed up and either confirmed/denied as reachable, not left permanently inconclusive)
   - Hidden form fields (`type="hidden"`) carrying security-relevant values (price, role, user ID) that the server trusts without re-validation
   - Client-side-only validation (JS `required`/pattern checks) that the server does not re-enforce — test by sending the "invalid" value directly to the endpoint, bypassing the UI
   - Inconsistent error styling/behavior between lessons that may indicate a shared, unpatched component
   - Any exposed version/build/debug marker in HTML comments or JS console output beyond what Section 3e's Actuator/debug-endpoint checks already cover
4. **Do not re-litigate Section 3b/3e items already marked PASS/negative with a clean evidence trail** (e.g. Actuator, TRACE, debug endpoints from Run #3) — focus new effort on genuinely unwalked surface per points 1–3 above.

Every finding produced this way still requires full Section 3d evidence (paired raw request/response, cross-checked screenshot, in-run timestamp) — the coverage expansion changes *where* Claude looks, not the evidence bar for what gets reported.

## 3h. Execution Integrity & Anti-Fabrication Controls *(added after Run #5 — both execution scripts crashed/failed to parse, yet the report claimed "21 findings confirmed, ✓ COMPLETE"; endpoints used did not match previously-verified real paths)*

**Root problem Run #5 exposed:** a findings-count target (Section 3g) combined with no hard check against actual tool execution allowed a report to be submitted that was internally disconnected from reality — the Python script crashed partway (traceback, `OSError`) and the PowerShell script never parsed at all, yet 21 "confirmed" findings were reported anyway, using endpoint paths that don't match any path verified in Runs #1–#4. The controls below exist to make that outcome structurally impossible, not just discouraged.

**Mandatory controls — a report missing any of these must be rejected outright, not just downgraded:**

1. **Raw execution log is itself a required evidence artifact.** The full, unedited stdout/stderr of whatever tool/script ran the tests (not a cleaned-up excerpt, not the AI's paraphrase of it) must be saved under `evidence/` and referenced in the report. A report with no raw execution log attached must not be accepted.
2. **Crash/exception cross-check is mandatory before writing any findings.** Before drafting the report, scan the raw execution log for tracebacks, parser errors, unhandled exceptions, or a non-zero/abnormal exit. If found, identify the exact point of failure and **exclude every finding whose evidence would have been generated at or after that point** — do not report a finding whose generating test never actually ran to completion. The report must state the crash point explicitly if one occurred, even if it means the finding count drops sharply.
3. **"Complete" must come from the tool, not from the AI's own summary.** A report may only claim a test/run "completed successfully" if the raw log's own last lines show the tool's own completion signal (e.g. exit code 0, an explicit success line the *script itself* printed after finishing all intended steps). The AI restating "✓ COMPLETE" in a report or README is not evidence of completion — it must be traceable to something the tool printed.
4. **No invented/guessed endpoint paths.** Any endpoint used in a crafted test request must be either (a) a path already confirmed real in a prior run's evidence (Section 3d), or (b) freshly confirmed via the application's own navigation/enumeration (e.g. `/WebGoat/service/lessonmenu.mvc`, sidebar links, in-lesson links) **with its own "existence check" evidence** (a simple request showing a real, non-404/non-generic response) captured *before* it's used in an attack payload. A path that merely "sounds plausible" for a generic web app (e.g. `/access-control/users?id=`, `/deserialize`, `/ssrf/submit` — none of which match WebGoat's actual verified routes from Runs #1–#4) must never appear in a finding without this existence-check evidence.
5. **Evidence directory listing is required and must reconcile with the report.** Attach a plain directory listing (`dir`/`ls -la` output, saved as its own evidence file) of the run's evidence folder. Every evidence filename cited anywhere in the report must appear in that listing with a non-trivial size (not 0 bytes, not a stub) and a modification time inside this run's own session window (Section 3d's timestamp rule). Any cited file missing from the listing invalidates the finding that cites it.
6. **Destructive payloads are not "tested," they are prohibited outright — no exceptions, not even to "confirm" a finding.** Payloads containing `DROP`, `DELETE`, `TRUNCATE`, destructive `UPDATE`/`INSERT`, or any other state-destroying operation must never be sent, per Section 6's guardrails. Read-only proof techniques only (boolean-based, UNION SELECT for read access, time-based blind, etc.). A raw request evidence file containing a destructive payload is itself a guardrail violation to flag, not a valid finding to report.
7. **Finding IDs must be unique and sequential — check before submission.** A report where one ID (e.g. "F-14") is reused for two unrelated findings must be corrected before submission; this kind of collision is itself a signal the report wasn't assembled from real per-finding evidence capture.
8. **Spot-check reproducibility.** For at least 2 findings per run, selected by the reviewer (not the tester) after the report is submitted, the tester must be able to re-issue the exact same request live and reproduce the same result on request. Inability to reproduce a cited finding on demand invalidates it retroactively.

These controls apply on top of, not instead of, Sections 3d–3g — evidence that passes 3h's checks still needs the screenshot cross-check, timestamp window, and non-inflated severity/count rules already in place.

## 3i. Full-Surface Coverage Mandate (Run #9+) *(requested after Run #8 — goal is to exercise every reachable page, sub-page, and element, not just a representative sample)*

**Objective:** maximize genuine finding count by maximizing genuine coverage of the attack surface — not by relaxing the evidence or severity rules in Sections 3d–3h, which remain in full force.

1. **Build a page/element inventory before testing, and check it off as you go.** Starting from the authenticated `GET /WebGoat/service/lessonmenu.mvc` response (already confirmed working in Run #8), enumerate every lesson under every one of the 13 categories in Section 3c — not just one representative lesson per category. For each lesson, enumerate every numbered sub-step shown in that lesson's own step indicator (per Section 3g point 1). Save this inventory as its own evidence file (`evidence/page-inventory.csv` or similar) with columns: category, lesson, sub-step, URL/route, status (tested / not tested / not applicable), finding ID if any.
2. **Within each page, check every element that accepts input or triggers a request** — every form field (including hidden fields per Section 3g point 3), every button, every link, and every API call the page's own JavaScript makes (visible via the Network panel per Section 3f's capture-then-replay method). A lesson page with three form fields and a hidden field is four things to check, not one.
3. **Treat every sub-step as independently reportable** per Section 3g point 1 — a lesson with 8 numbered sub-steps can legitimately yield up to 8 distinct findings if each is a separately exploitable issue, which is why full sub-step coverage (not representative sampling) is the main lever for increasing genuine finding count.
4. **"Not tested" must be a tracked, explained status, not a silent gap.** Any inventory row left untested by the end of the run must say why (e.g. "requires external tooling outside guardrails," "rate budget exhausted," "not reachable by this account") rather than simply being absent from the report.
5. **This mandate does not create any exception to Sections 3d/3h.** Every page/element/sub-step that yields a finding still needs paired raw request/response evidence, a cross-checked screenshot where applicable, an in-run timestamp, and a real, existence-checked endpoint. Breadth of coverage is the goal; it is not a reason to loosen how any individual finding is proven.

## 3j. Objective Severity Classification — decided before counting, not after *(added because this update's request to "approach 9 High + 9 Critical" is a severity-count target, which carries the same inflation risk Section 3g already flagged for total count — this section exists so severity assignment cannot be adjusted toward that number)*

**Rule — read before classifying any finding:** 9 High + 9 Critical is **not a target to hit**. It is not confirmed to be achievable, correct, or even desirable for this specific WebGoat version and scope — it is, at most, another secondhand reference number, with the same caveats Section 3g already states about the >16/9 benchmark (different version, different scope, possibly looser criteria). Severity must be assigned using the fixed rubric below, decided **before** tallying how many of each severity level have accumulated so far in the run. If applying the rubric honestly yields fewer than 9 High or fewer than 9 Critical, the report must say so plainly and must not relabel findings upward to close the gap.

**Fixed severity rubric (apply the same way regardless of running tally):**

| Severity | Objective criteria (must meet at least one, with evidence) |
|---|---|
| **Critical** | Remote code execution; full, unauthenticated compromise of the application or host; or a single request achieving both full sensitive-data exfiltration *and* a path to further compromise (e.g. working deserialization RCE, not just a live-but-unexploited sink) |
| **High** | Full sensitive-data exfiltration *without* RCE (e.g. full-table SQLi dump); full authentication/authorization bypass; arbitrary local file read (XXE/path traversal) confirmed with real file content; stored XSS with confirmed execution impacting other users |
| **Medium** | Partial data exposure; a real but limited-impact bypass (e.g. CSRF on a single endpoint, session-fixation); missing defense-in-depth controls with a demonstrated (not just theoretical) exploit path (e.g. clickjacking PoC, not just a missing header) |
| **Low** | Missing defense-in-depth / hardening controls with no demonstrated exploit path beyond the header/config absence itself (e.g. missing CSP with no framing PoC attempted) |

**Procedure to prevent target-chasing:**
1. For each finding, write down which rubric row applies and why, **using only the finding's own evidence** — before looking at how many findings of each severity exist so far this run.
2. Do not revisit an already-classified finding's severity later in the same run "to balance the totals." If new evidence genuinely changes the picture (e.g. a previously-Medium finding turns out to chain into RCE), document the new evidence that caused the change, not the running count.
3. The report's Executive Summary must state the rubric row used for every High/Critical finding in one clause (e.g. "F-01 — Critical: RCE via deserialization gadget, confirmed in `evidence/...`"), so a reviewer can check the classification against the rubric without re-deriving it.
4. If the honest result is, say, 5 High and 2 Critical, the report must present that as the result — not as a shortfall to apologize for or re-engineer around. Section 3g's anti-padding rule and this section's anti-inflation rule are the same principle applied to count and to severity respectively.

## 3k. ASVS Requirement Triage & Forced-Execution Protocol *(added after Run #8 left 337/345 L1 requirements as "Not tested" — most of that gap is not a testing failure, it is rows that are structurally untestable by this engagement's method, and treating them the same as genuinely-skipped testable rows hides the real coverage gap)*

**Diagnosis:** The 345-row ASVS L1 matrix mixes several different kinds of requirement. Many rows (documentation requirements like V6.1.1/V13.1.x, source-level crypto implementation requirements like most of V11, requirements for technologies this application doesn't implement like V4.3 GraphQL/V4.4 WebSocket/V9-V10 OAuth-OIDC/V17 WebRTC, and TLS-configuration rows like V12.x when the target runs plain HTTP with no TLS at all) **cannot be resolved by any HTTP request, no matter how many are sent** — they require source code, internal documentation, or a technology that simply isn't present. Labeling all of these "Not tested" alongside rows that genuinely could have been exercised but weren't hides which gap is real.

**Mandatory one-time triage pass (do this before Run #9's active testing, and before building the Section 3i page/element inventory):** Go through all 345 rows exactly once and assign each to one of these categories — this triage table is itself a required evidence artifact (`evidence/asvs-requirement-triage.csv`), reusable in later runs unless the application's technology stack changes:

| Category | Definition | What happens to it |
|---|---|---|
| **TESTABLE-HTTP** | A grey-box HTTP request/response (or a browser-driven lesson interaction) can directly confirm or refute this requirement for this application | **Must be actively tested this run or a later run — "Not tested" is not an acceptable final status for any row in this category.** Feeds directly into Section 3i's page/element inventory. |
| **N/A-TECHNOLOGY** | The requirement only applies to a technology this application does not implement (GraphQL, WebSocket, OAuth/OIDC/SAML, WebRTC, TLS/HTTPS, MFA, biometric auth, etc.) | Marked N/A with a one-line verification (e.g. "no `/graphql` endpoint exists — confirmed via lesson-menu enumeration and a direct probe returning 404" or "target serves plain HTTP only, no TLS handshake possible — confirmed in every captured response"). A bare assumption is not enough; the absence itself needs one small piece of evidence where that's cheap to get (as several already are, e.g. no TLS is already evidenced by every raw HTTP trace so far). |
| **N/A-METHOD** | The requirement needs source code, internal security documentation, organizational policy, or infrastructure/server config access that this Grey-box, no-source engagement (Section 3, Repo path: N/A) does not have | Marked N/A with the reason being the engagement's own declared method/scope limit, not the tester's effort. This is not a finding and not a gap to close within this engagement. |
| **DEFERRED-TOOLING** | Technically testable via HTTP in principle, but only with tooling this engagement's guardrails exclude (bulk scanners, external exploit frameworks like ysoserial) per Section 6/3h | Marked deferred with the specific guardrail that blocks it, consistent with how Section 3f already handles the Insecure Deserialization exploit-crafting step |

**Force-execution rule:** Once triage is complete, the Section 3b/3i coverage tables and the ASVS matrix must show **zero rows left as a bare "Not tested"** — every row is either actively tested (PASS/FAIL with evidence), or carries one of the three N/A/deferred labels above with its one-line reason. A row sitting at plain "Not tested" with no reason given is treated the same as an unexplained gap under Section 3i point 4 — it must be chased down (tested, or correctly classified) before the report is finalized.

**Expected effect, stated honestly in advance:** This will not make all 345 rows "tested" — a large fraction will legitimately land in N/A-METHOD (no source) and N/A-TECHNOLOGY (features not present). What it does is shrink the dishonest-looking "97.7% not tested" down to the much smaller, real number of TESTABLE-HTTP rows that are genuinely still outstanding — which is the number that actually matters and the number Run #9 onward should be judged against, not the raw 345.

## 4. ASVS Standard
- **Version:** 5.0.0
- **Target Level:** [x] L1 [ ] L2 [ ] L3
- **Requirement data source:** [ ] Cheap — local reference files, no MCP [x] Heavier — query the `owasp-asvs` MCP server

## 5. Test Credentials
*(only needed if authenticated testing is in scope)*

| Username | Password | Role | Notes |
|---|---|---|---|
| xtbuiquang | Password1@ | user (full lesson access) | Confirmed via login screenshot: account sees all 13 sidebar categories (Introduction, General, A1, A2, A3, A5–A10, Client side, Challenges). WebGoat has no admin/user visibility split — this is the standard access level for any registered account. |

## 6. Constraints & Guardrails
- **Max request rate / concurrency:** Single-digit req/s (≤5 req/s), sequential (no concurrency), no bulk template scanners (nuclei/dirsearch-style sweeps).
- **Known WAF/rate-limiting in front of target:** None observed — direct responses with no WAF/CDN signature noted so far; confirm actual server header fingerprint for WebGoat (not nginx — WebGoat is typically served directly by its embedded Spring Boot/Tomcat server) before testing.
- **Actions explicitly off-limits:** No bulk template scanners; no destructive admin actions (data/DB resets); don't submit any contact/password-reset forms if present; do not interact with WebWolf or any other service on the same host/subnet.
- **Maintenance window / blackout dates:** None specified.
- **Anything that broke during a prior test of this target:** None broke, but run #1 under-covered: it self-reported as a limited/passive pass (not full ASVS L1, "limited CORS check") and returned only 2 of an expected ~9 findings. Root cause was scope depth, not a guardrail violation — see Section 3b/3c added after run #1. Rate/concurrency guardrails below are unchanged; only testing depth is increased. (Prior notes referencing DVWA security-level changes and an unrelated WordPress/Azure Front Door incident do not apply here and have been removed as stale/mismatched content.)
- **DVWA security level for this assessment:** N/A — target is WebGoat, which has no security-level setting. *(This field is kept only to explicitly mark it as not applicable, since the original intake incorrectly carried DVWA-specific content for this target.)*

## 7. Escalation
- **If something appears to break:** Stop and report directly in this conversation — no other contact.

## 8. Output
- **Report file name/location:** `nt-security-testing/runs/<run-id>/SECURITY-TEST-REPORT.md`
- **Chrome evidence:** `nt-security-testing/runs/<run-id>/evidence/chrome/<filename>` — one-line description per screenshot
- **Anything else the report should include/exclude:** Report must include the completed Section 3b coverage table (no blank rows, including the Section 3e advanced rows), the Section 3c lesson list actually walked, and the Section 3i page/element inventory. For any category or inventory row marked not tested/SKIPPED, state the concrete reason rather than omitting it silently. **Per Section 3d, every "Confirmed" finding must cite the evidence filename(s) backing it**, and per Section 3j must cite the rubric row justifying its severity — a finding without a cited evidence file must be relabeled "Reported — evidence pending" and excluded from the confirmed-finding count in the Executive Summary.

## 9. Pre-Scan Validation Gate

- **Validation mode:** [ ] Dry-run only [x] Active testing approved
- **Overall intake status:** [x] PASS [ ] FAIL
- **If FAIL, blocking reasons:** N/A
- **If PASS, approved scope summary:** Active testing approved for `http://10.242.10.31:8007/WebGoat/` only (all paths under this host:port, no subdomains), Grey-box, ASVS 5.0.0 L1, single-digit req/s sequential requests, no bulk template scanners, per Sections 1 and 6 above.
- **Approved by (name/role):** xtbuiquang / Security Tester
- **Approval timestamp (UTC):** 2026-11-16

## 10. Rerun Request and Delta Control

- **Is this a rerun?** [x] No [ ] Yes
- **Rerun trigger:** N/A for this update — this is a coverage/severity-methodology update (Sections 3i/3j) applying to Run #9 onward, not a rerun of a specific prior run.
- **Rerun type / delta:** N/A — see Sections 3i and 3j for what changes going forward.
- **Disputed finding IDs:** None.
- **Rerun decision owner:** xtbuiquang / Security Tester.
- **Approval timestamp (UTC):** 2026-11-16 (this update).

---

**Last updated:** 2026-11-16
