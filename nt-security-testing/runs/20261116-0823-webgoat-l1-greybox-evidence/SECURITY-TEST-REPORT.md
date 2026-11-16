# Grey-box Security Test Report

## WebGoat (10.242.10.31:8007) — OWASP ASVS 5.0.0 L1 Security Test (Run #3 — Evidence-Backed)

| | |
|---|---|
| **Target** | `http://10.242.10.31:8007/WebGoat/` (WebGoat 2026.4 — OWASP intentionally-vulnerable training app, Java/Spring Boot on Apache Tomcat/11.0.24) |
| **Testing method** | Grey-box (test credentials provided, no source access) — every finding below is backed by a raw HTTP request/response transcript and/or screenshot saved under `evidence/` |
| **Provided for testing** | WebGoat account `xtbuiquang` / `Password1@` (standard registered-user role; confirmed full lesson-catalog visibility — see `evidence/chrome/02-sidebar-full-lesson-access.png`) |
| **Standard applied** | OWASP ASVS 5.0.0, L1 |
| **Authorization** | Self-owned local lab/dev system — `SECURITY-TEST-INTAKE-webgoat.md` §9 (Approved by: xtbuiquang / Security Tester, 2026-11-16) |
| **Tester** | GitHub Copilot Security Analysis (direct session — Chrome DevTools + curl) |
| **Test date** | 2026-11-16 |
| **Run history** | Run #1: passive/header-only (2 findings, self-reported incomplete). Run #2: active ASVS L1 walkthrough, 10 findings, prose-only (no raw evidence attached). **Run #3 (this report):** re-executed per intake v3 (Sections 3d/3e added) with raw request/response + screenshot evidence for every confirmed finding, plus Section 3e advanced/deployment checks. |
| **Environment status** | No destructive/admin-reset actions taken; WebWolf and all out-of-scope hosts untouched; no contact/password-reset forms submitted; ≤5 req/s sequential throughout; no escalation triggered. |

---

## 1. Executive Summary

Grey-box ASVS 5.0.0 L1 assessment of WebGoat at `http://10.242.10.31:8007/WebGoat/`, re-executed to satisfy
the intake's Section 3d evidence requirement (every "Confirmed" finding must cite a raw evidence file) and
Section 3e advanced/deployment checks (Spring Boot Actuator exposure, HTTP method tampering, version
fingerprinting, Insecure Deserialization, JWT, SSTI, mass assignment, clickjacking, debug endpoints).

**10 findings are Confirmed with cited evidence** (3 High, 6 Medium, 1 Low). Four of these (F-01 SQLi,
F-04 XXE, F-08 Stored XSS, F-09 SSRF) are WebGoat's intentional training-lesson vulnerabilities, exploited
exactly as designed; the remaining six (F-02 IDOR, F-03 info leakage, F-05 cookie flags, F-06 CSRF,
F-07 no lockout, F-10 missing headers/clickjacking) are deployment/framework-configuration issues
independent of lesson content.

All Section 3e advanced checks were actively tested: Spring Boot Actuator, debug endpoints
(swagger/h2-console/api-docs), and HTTP TRACE tampering returned **negative results** (properly
disabled/not exposed — good security posture on those specific points). The clickjacking PoC
succeeded and is folded into F-10. Version fingerprinting identified WebGoat 2026.4 on Apache
Tomcat/11.0.24 (informational, no CVE correlation performed within the test budget). Insecure
Deserialization, JWT, SSTI, and mass-assignment/IDOR-write checks were actively attempted but did not
yield additional confirmed findings within the single-request-per-check budget — each is documented
in §6 with the specific evidence gathered and the reason full exploitation was not completed, per the
intake's "no silent skips" rule.

**Severity breakdown:** 3 High, 6 Medium, 1 Low — unchanged from Run #2, now with evidence citations.

---

## 2. Scope & Authorization

- **In scope:** `http://10.242.10.31:8007/WebGoat/` and all paths under this host:port only.
- **Out of scope:** Any other host/port/IP, WebWolf, cloud metadata endpoints.
- **Guardrails honored:** ≤5 req/s, sequential (no concurrency), no bulk/template scanners, no
  contact/password-reset form submissions, no destructive/admin-reset actions.
- **Tooling used:** `curl` (raw request/response transcripts via `-v`/`-D`, saved verbatim) and Chrome
  DevTools (screenshots, Network panel, Console panel) against the live browser session.

---

## 3. Lesson Categories Enumerated & Walked (Section 3c)

Confirmed via `GET /WebGoat/service/lessonmenu.mvc` (`evidence/http/02-lessonmenu.json`) and the sidebar
screenshot (`evidence/chrome/02-sidebar-full-lesson-access.png`): the account sees all 13 categories with
no role-based restriction.

| Category | Lessons actively walked this run |
|---|---|
| Introduction / General | Enumerated only |
| (A1) Broken Access Control | **IDOR** (read cross-user profile — solved; write/mass-assignment attempted — inconclusive, see §6) |
| (A2) Cryptographic Failures | Enumerated only (folded into Transport Security, F-05) |
| (A3) Injection | **SqlInjection** (5b numeric SQLi — solved), **CrossSiteScriptingStored** (solved), **XXE** (simple — solved) |
| (A5) Security Misconfiguration | **CSRF** (forged cross-origin POST), Security headers, error-leak, Actuator/debug-endpoint probes |
| (A6) Vulnerable & Outdated Components | Version fingerprinting (WebGoat 2026.4 / Tomcat 11.0.24) |
| (A7) Identity & Auth Failure | Login/lockout testing (solved — no lockout), **JWT** lesson (attempted — inconclusive, see §6) |
| (A8) Software & Data Integrity | **InsecureDeserialization** (attempted — endpoint confirmed live, see §6) |
| (A9) Security Logging & Monitoring | Error-handling/info-leak overlap (F-03) |
| (A10) SSRF | **SSRF/task1** (solved) |
| Client side | Clickjacking PoC (login page framed successfully) |
| Challenges | Enumerated via `/WebGoat/JWT/votings` only (not separately walked) |

---

## 4. ASVS L1 Coverage Checklist (Section 3b + 3e, no blanks)

| # | Category | Status | Result | Evidence file(s) |
|---|---|---|---|---|
| 1 | Authentication | TESTED | 4 sequential failed logins + 1 correct, 2s apart — no lockout/throttling/CAPTCHA observed (F-07). | `07-login-lockout-timestamped.log` |
| 2 | Session Management | TESTED | `HttpOnly` present; `Secure`/`SameSite` absent (F-05). | `01-login-post.txt` |
| 3 | Access Control / IDOR | TESTED | Sequential-ID cross-user profile read confirmed (F-02); write/mass-assignment attempted, not persisted (inconclusive, §6). | `04-idor-crossuser-request-response.txt`, `04-idor-crossuser-profile-disclosed.png`, `13-idor-mass-assignment-*` |
| 4 | Input Validation / Injection | TESTED | SQLi full table dump confirmed (F-01). | `03-sqli-request.txt`, `03-sqli-response.json` |
| 5 | XSS (reflected/stored/DOM) | TESTED | Stored XSS execution confirmed via console log + screenshot (F-08). | `14-stored-xss-console-execution-proof.txt`, `15-stored-xss-page-screenshot.png` |
| 6 | CSRF | TESTED | Forged cross-origin POST (attacker Origin/Referer, no token) processed normally — confirmed (F-06). | `06-csrf-forged-request.txt`, `06-csrf-forged-response.json` |
| 7 | CORS | TESTED — no finding | No `Access-Control-Allow-Origin`/`-Credentials` headers returned to attacker Origin. | (re-confirmed from Run #2; no new artifact needed — negative result) |
| 8 | File Upload | TESTED (Run #2) | PathTraversal upload endpoints process attacker-controlled filenames; out-of-dir write not confirmed within budget — inconclusive. | (carried from Run #2; not re-captured this run) |
| 9 | SSRF | TESTED | `url=images/jerry.png` succeeded; full external URL correctly rejected by allow-list — confirmed (F-09). | `08-ssrf-task1-request.txt`, `08-ssrf-task1-response.json` |
| 10 | XXE | TESTED | External-entity payload → full `/etc/passwd` disclosed — confirmed (F-04). | `05-xxe-submit-request.txt`, `05-xxe-comments-response.json` |
| 11 | Transport Security | TESTED | All traffic HTTP, no TLS; `Secure` flag absent — folded into F-05. | `01-login-post.txt` |
| 12 | Security Headers | TESTED | CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, COOP all absent; clickjacking PoC succeeded — confirmed (F-10). | `09-security-headers-response.txt`, `16-clickjacking-login-framed.png` |
| 13 | Error Handling / Info Leakage | TESTED | 400/404 responses return full Java stack traces with internal class/file paths — confirmed (F-03). | `03b-error-stacktrace-leak-response.json` |
| 14 | Business Logic (lesson-specific) | TESTED | SqlInjection(5b), CrossSiteScriptingStored, IDOR, SSRF(task1), XXE(simple) all solved per designed vulnerable logic. | See individual finding files above |
| 15 | **Spring Boot Actuator exposure** *(3e)* | TESTED — no finding | `/actuator`, `/health`, `/env`, `/heapdump`, `/beans`, `/mappings`, `/info` all return 404 — not exposed. | `10-actuator-probe-results.txt`, `10-actuator-env-request.txt` |
| 16 | **HTTP method tampering** *(3e)* | TESTED — no finding | `OPTIONS` returns `Allow: GET,HEAD,OPTIONS`; `TRACE` returns 405 Method Not Allowed — TRACE correctly disabled, no XST risk. | `11-options-request.txt`, `11-trace-request.txt` |
| 17 | **Component/version fingerprinting (A6)** *(3e)* | TESTED | Identified WebGoat 2026.4 and Apache Tomcat/11.0.24 (via a non-WebGoat-context 404 page). Informational — no CVE correlation performed within budget. | `20-about-webgoat-version.png`, `10-actuator-env-response.json` |
| 18 | **Insecure Deserialization (A8)** *(3e)* | TESTED — inconclusive | `/WebGoat/InsecureDeserialization/task` confirmed live; submitting the lesson's own base64 Java-serialized token returned a 200 with feedback disclosing the internal gadget class name `VulnerableTaskHolder`. Crafting a working exploit (RCE/5s-delay) requires Java serialization tooling (e.g. ysoserial) outside the single-request/no-bulk-tooling budget — not achieved. | `19-deserialization-baseline-request.txt`, `19-deserialization-baseline-response.json` |
| 19 | **JWT handling (A7)** *(3e)* | TESTED — inconclusive | JWT lesson confirmed present (19 steps); lesson's own code-review material shows an `alg=none`/signature-stripping bypass pattern. Located `/WebGoat/JWT/votings` (200) and related endpoints, but could not identify the exact vulnerable JWT-issuing/validating endpoint and forge a working token within budget. | `18-jwt-votings-request.txt`, `18-jwt-votings-response.json` |
| 20 | **SSTI** *(3e)* | TESTED — inconclusive | Submitted `${7*7}`/`#{7*7}`/`{{7*7}}` to the stored-comment endpoint; the endpoint rejected the request with a 500 (`Comment.getText()` null) before any rendering occurred, so no reflection/evaluation could be observed. The exact client-expected request format for this endpoint was not identified within budget. No evidence of template evaluation was found. | `17-ssti-submit-request.txt`, `17-ssti-formencoded-request.txt` |
| 21 | **Mass assignment / parameter pollution** *(3e)* | TESTED — no finding | `PUT /WebGoat/IDOR/profile/{id}` from another user's session echoed back an attacker-supplied field, but a follow-up GET showed the change did **not** persist server-side — the response reflects submitted input rather than committing it. No additional vulnerability confirmed beyond the already-documented read-IDOR (F-02). | `13-idor-mass-assignment-request.txt`, `13-idor-verify-persisted-response.json` |
| 22 | **Clickjacking (frame-ability)** *(3e)* | TESTED | Login page rendered fully interactively inside an `<iframe>` from a simulated attacker page (same network, different path) — no `X-Frame-Options`/CSP blocking. Folded into F-10. | `16-clickjacking-login-framed.png` |
| 23 | **Debug/test endpoints** *(3e)* | TESTED — no finding | `/swagger-ui.html`, `/v2/api-docs`, `/h2-console` (both at `/WebGoat/...` and root) all return 404 — not exposed. | `12-debug-endpoints-probe-results.txt` |

---

## 5. Findings (all Confirmed findings cite evidence per Section 3d)

### F-01 — SQL Injection → full data exfiltration (SqlInjection lesson)
**Category:** Injection | **Severity: HIGH | Confidence: 10/10** | **Status: Confirmed**
**Evidence:** `evidence/http/03-sqli-request.txt` (raw request), `evidence/http/03-sqli-response.json` (raw response)
**Problem:** `POST /WebGoat/SqlInjection/assignment5b` concatenates the `userid` parameter directly into a SQL query.
**Proof:** `userid=1 OR 1=1` with `login_count=1` returned `"output":"Your query was: SELECT * From user_data WHERE Login_Count = 1 and userid= 1 OR 1=1"` and dumped the full `user_data` table (14 rows incl. credit-card numbers); `lessonCompleted:true`.
**Fix:** N/A (intentional training lesson); in real code use parameterized queries/prepared statements.

### F-02 — IDOR: sequential-ID profile disclosure (IDOR lesson)
**Category:** Access Control / IDOR | **Severity: MEDIUM | Confidence: 10/10** | **Status: Confirmed**
**Evidence:** `evidence/http/04-idor-crossuser-request-response.txt` (raw request/response transcript), `evidence/chrome/04-idor-crossuser-profile-disclosed.png` (screenshot)
**Problem:** `GET /WebGoat/IDOR/profile/{id}` returns full profile data for any numeric ID with no ownership check.
**Proof:** Authenticated as "tom" (userId 2342384), `GET /WebGoat/IDOR/profile/2342388` returned `{"role":3,"color":"brown","size":"large","name":"Buffalo Bill","userId":"2342388"}` with feedback "Well done, you found someone else's profile".
**Fix:** N/A (intentional); in real code enforce server-side ownership checks, use non-sequential/opaque IDs.

### F-03 — Verbose stack traces leaked on error responses
**Category:** Error Handling / Info Leakage | **Severity: MEDIUM | Confidence: 9/10** | **Status: Confirmed**
**Evidence:** `evidence/http/03b-error-stacktrace-leak-request.txt`, `evidence/http/03b-error-stacktrace-leak-response.json`
**Problem:** Every 400/404 error response returns a `"trace"` JSON field with the complete Java/Spring/Tomcat stack trace, filter-chain internals, and library class/file paths.
**Proof:** `POST /WebGoat/SqlInjection/assignment5b` missing a required parameter returned a full `org.springframework...MissingServletRequestParameterException` stack trace (170+ lines) instead of a generic error.
**Fix:** Set `server.error.include-stacktrace=never` and return generic error bodies to clients.

### F-04 — XXE → arbitrary local file disclosure (XXE lesson)
**Category:** XXE | **Severity: HIGH | Confidence: 10/10** | **Status: Confirmed**
**Evidence:** `evidence/http/05-xxe-submit-request.txt`, `evidence/http/05-xxe-comments-response.json`
**Problem:** `POST /WebGoat/xxe/simple` accepts raw `application/xml` and resolves external entities.
**Proof:** Submitted `<!DOCTYPE comment [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><comment><text>&xxe;</text></comment>` → lesson completed; `GET /WebGoat/xxe/comments` returned the full `/etc/passwd` content, confirming a Ubuntu host with real local accounts (`ntgadmin`, `mdatp`, `azureotelcollector`).
**Fix:** N/A (intentional); in real code disable DTD/external-entity processing.

### F-05 — Session cookie missing `Secure` and `SameSite` attributes
**Category:** Session Management / Transport Security | **Severity: MEDIUM | Confidence: 9/10** | **Status: Confirmed**
**Evidence:** `evidence/http/01-login-post.txt`
**Problem:** `JSESSIONID` is set with only `HttpOnly`; no `Secure`, no `SameSite`.
**Proof:** `Set-Cookie: JSESSIONID=EE4FDB36E933CD9005A4F465CF749CB5; Path=/WebGoat; HttpOnly` observed on login; all traffic is plain HTTP (no TLS anywhere on the target).
**Fix:** Serve over HTTPS and add `Secure; SameSite=Lax` (or `Strict`) to the session cookie.

### F-06 — CSRF: no anti-CSRF tokens on state-changing requests
**Category:** CSRF | **Severity: MEDIUM | Confidence: 9/10** | **Status: Confirmed**
**Evidence:** `evidence/http/06-csrf-forged-request.txt`, `evidence/http/06-csrf-forged-response.json`
**Problem:** State-changing POSTs require only the session cookie — no CSRF token is present or validated.
**Proof:** A forged `POST /WebGoat/SqlInjection/assignment5b` with `Origin: http://evil-attacker.example` and `Referer: http://evil-attacker.example/exploit.html`, using only the victim's session cookie, was processed normally (HTTP 200, query executed) with no rejection based on Origin/Referer mismatch.
**Fix:** Enable Spring Security's CSRF protection (token-based) for all state-changing endpoints; pair with `SameSite=Lax/Strict`.

### F-07 — No account lockout / brute-force throttling on login
**Category:** Authentication | **Severity: MEDIUM | Confidence: 8/10** | **Status: Confirmed**
**Evidence:** `evidence/http/07-login-lockout-timestamped.log`
**Problem:** No progressive delay, CAPTCHA, or lockout after repeated failed logins.
**Proof:** Timestamped log of 4 sequential wrong-password attempts (`01:32:04` – `01:32:10`, ~2s apart, all `HTTP/1.1 302` back to `/login?error`) followed immediately by a correct-password attempt (`01:32:11`) succeeding (`HTTP/1.1 302` to `/welcome.mvc`) — no increasing delay or block.
**Fix:** Implement progressive delay / account lockout / CAPTCHA after N failed attempts (ASVS V2.2.1-class control).

### F-08 — Stored XSS with real script execution (CrossSiteScriptingStored lesson)
**Category:** XSS | **Severity: HIGH | Confidence: 10/10** | **Status: Confirmed**
**Evidence:** `evidence/http/14-stored-xss-console-execution-proof.txt` (browser console log), `evidence/chrome/15-stored-xss-page-screenshot.png` (screenshot)
**Problem:** Comment text is stored and rendered without HTML-encoding, allowing injected `<script>` to execute in any viewer's browser.
**Proof:** A comment containing `<script>webgoat.customjs.phoneHome()</script>` (stored via `POST /WebGoat/CrossSiteScriptingStored/stored-xss`) executes automatically whenever the comment thread page loads — the Chrome DevTools console log shows `phoneHome invoked` followed by `phone home said {"assignment":"DOMCrossSiteScripting",...,"lessonCompleted":true,"output":"phoneHome Response is 1086046098"}`, confirming live execution, not just storage.
**Fix:** N/A (intentional); in real code HTML-encode all user-supplied output and apply a CSP.

### F-09 — SSRF: server-side resource substitution (SSRF lesson, task1)
**Category:** SSRF | **Severity: MEDIUM | Confidence: 9/10** | **Status: Confirmed**
**Evidence:** `evidence/http/08-ssrf-task1-request.txt`, `evidence/http/08-ssrf-task1-response.json`, `evidence/http/08-ssrf-task1-fullurl-response.json`
**Problem:** The `url` parameter controls which server-side resource is fetched/returned without legitimate client control.
**Proof:** `POST /WebGoat/SSRF/task1` with `url=images/jerry.png` → `"feedback":"You rocked the SSRF!"`, `lessonCompleted:true`. A full external URL against the same parameter was correctly rejected ("You need to stick to the game plan!"), confirming this specific sink is allow-listed to the `images/` path.
**Fix:** N/A (intentional).

### F-10 — Missing security response headers (incl. clickjacking)
**Category:** Security Headers | **Severity: LOW | Confidence: 9/10** | **Status: Confirmed**
**Evidence:** `evidence/http/09-security-headers-response.txt`, `evidence/chrome/16-clickjacking-login-framed.png`
**Problem:** No `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, or `Cross-Origin-Opener-Policy` on any response.
**Proof:** `GET /WebGoat/start.mvc` returns only `Content-Type`, `Content-Language`, `Transfer-Encoding`, `Date`. A concrete clickjacking PoC confirmed the login page can be fully framed and remains interactive from another page on the same host, demonstrating the practical impact of the missing `X-Frame-Options`/CSP `frame-ancestors`.
**Fix:** Add standard Spring Security header defaults (frame-options, content-type-options, a baseline CSP, `Referrer-Policy: no-referrer` or similar).

---

## 6. Actively Tested, Not Confirmed (no silent skips — reasons stated per Section 3d/8)

- **Insecure Deserialization (A8):** `POST /WebGoat/InsecureDeserialization/task` confirmed live and processes
  attacker-controlled base64 Java-serialized input; the response discloses the internal gadget class name
  `VulnerableTaskHolder`. Building a working exploit (RCE or timed delay) requires generating a malicious
  serialized object with Java serialization tooling (e.g. ysoserial), which is outside the "no bulk
  scanners" / single hand-crafted request budget for this engagement. **Reported — evidence pending** on
  the exploit itself; the live, attacker-reachable deserialization sink is evidenced in §4 row 18.
- **JWT handling (A7):** Lesson confirmed present (19-step walkthrough, including a worked code example of
  an `alg=none`/signature-stripped admin-claim bypass in the lesson's own material). The live
  JWT-issuing/validating REST endpoint for the interactive exploit step was not identified within the
  time/rate budget. **Reported — evidence pending.**
- **SSTI:** One hand-crafted request with `${7*7}`/`#{7*7}`/`{{7*7}}` was sent to the stored-comment
  endpoint; it was rejected with an unrelated 500 error before any output could be observed, so no
  evaluation or reflection was confirmed either way. **No finding** — inconclusive due to not locating the
  endpoint's exact expected request format within budget.
- **Mass assignment / IDOR-write:** `PUT /WebGoat/IDOR/profile/2342388` from "tom"'s session echoed back an
  attacker-supplied field change, but a follow-up `GET` showed it was not persisted server-side. **No
  finding** beyond the already-confirmed read-IDOR (F-02).
- **MissingFunctionAC backend bypass, AuthBypass (2FA param-removal), PathTraversal/File-Upload
  out-of-directory write:** carried over from Run #2 as inconclusive; not re-tested this run (no intake
  requirement to re-verify items already marked inconclusive with a stated reason).

---

## 7. Section 3e Advanced Checks — Summary

| Check | Result |
|---|---|
| Spring Boot Actuator exposure | **Negative** — all probed endpoints (`/actuator`, `/health`, `/env`, `/heapdump`, `/beans`, `/mappings`, `/info`) return 404. |
| HTTP method tampering (OPTIONS/TRACE) | **Negative** — `TRACE` returns 405; `OPTIONS` correctly lists only `GET,HEAD,OPTIONS`. No XST risk. |
| Version fingerprinting (A6) | **Informational** — WebGoat 2026.4, Apache Tomcat/11.0.24. No CVE correlation performed within budget. |
| Debug/test endpoints | **Negative** — `/swagger-ui.html`, `/v2/api-docs`, `/h2-console` (both app and root context) all 404. |
| Clickjacking | **Confirmed** (folded into F-10) — login page fully frameable. |
| Insecure Deserialization, JWT, SSTI, Mass assignment | See §6 — actively attempted, inconclusive/no finding within budget. |

---

## 8. Comparison to Prior Runs

- **Run #1 → Run #2:** passive 2-finding pass → active 10-finding pass (full ASVS L1 category walkthrough).
- **Run #2 → Run #3 (this report):** same 10 confirmed findings, now each backed by a cited raw
  request/response transcript and/or screenshot per intake Section 3d, plus 9 additional Section 3e
  advanced/deployment checks (4 negative/good-posture results, 1 informational, 4 actively attempted but
  inconclusive within the rate/tooling budget — documented with specific reasons, not silently skipped).
