# Grey-box Security Test Report

## WebGoat (10.242.10.31:8007) — OWASP ASVS 5.0.0 L1 Security Test

| | |
|---|---|
| **Target** | `http://10.242.10.31:8007/WebGoat/` (WebGoat — OWASP intentionally-vulnerable training app, Java/Spring Boot) |
| **Testing method** | Grey-box (test credentials provided, no source access) — all findings derived from external HTTP interaction |
| **Provided for testing** | WebGoat account `xtbuiquang` / `Password1@` (role: user; confirmed full lesson-catalog visibility, no hidden/admin-restricted categories) |
| **Standard applied** | OWASP ASVS 5.0.0, L1 |
| **Authorization** | Self-owned local lab/dev system — sign-off recorded in `SECURITY-TEST-INTAKE-webgoat.md` §9 (Approved by: xtbuiquang / Security Tester, 2026-11-16) |
| **Tester** | GitHub Copilot Security Analysis |
| **Test date** | 2026-11-16 |
| **Runs** | Run #1 (passive, header/cookie-only) and Run #2 (active, full ASVS L1 coverage per intake §3b/§3c) |
| **Environment status** | No destructive/admin-reset actions taken; WebWolf and all out-of-scope hosts untouched; no contact/password-reset forms submitted; no escalation triggered |

---

## 1. Executive Summary

Grey-box ASVS 5.0.0 L1 assessment of WebGoat at `http://10.242.10.31:8007/WebGoat/`. Run #1 was a
passive, header/cookie-level pass and self-reported as incomplete. Run #2 actively exercised all 14
ASVS L1 categories required by intake §3b, confirming **10 findings** (3 High, 6 Medium, 1 Low) with
concrete HTTP request/response evidence. The most severe confirmed issues are **SQL injection**
(F-01, full `user_data` table dump including credit-card numbers), **XXE** (F-04, arbitrary local file
disclosure — read `/etc/passwd`), and **stored XSS** (F-08, unsanitized script execution). Four
findings (F-01, F-04, F-08, F-09) are WebGoat's intentional training-lesson vulnerabilities, confirmed
exploitable exactly as designed — not defects in WebGoat itself. The remaining six (F-02, F-03, F-05,
F-06, F-07, F-10) are application/framework-configuration issues independent of lesson content and are
the items an operator should remediate if this configuration pattern were reused in a production
service.

**Severity breakdown:** 3 High, 6 Medium, 1 Low.

### Test Case Summary (Section 3b coverage — all 14 categories actively tested, no blanks)

| Result | Count |
|---|---|
| **Confirmed finding** | 10 |
| **Tested — no finding (CORS)** | 1 |
| **Tested — inconclusive** (MissingFunctionAC backend bypass, AuthBypass param-removal, PathTraversal/File-Upload out-of-dir write) | 3 sub-items (stated explicitly, not silently skipped) |

---

## 2. Scope & Authorization

- **In scope:** `http://10.242.10.31:8007/WebGoat/` and all paths under this host:port only.
- **Out of scope:** Any other host/port/IP, WebWolf, cloud metadata endpoints.
- **Guardrails honored:** ≤5 req/s, sequential (no concurrency), no bulk/template scanners, no
  contact/password-reset form submissions, no destructive/admin-reset actions.
- **Basis:** Self-owned system (intake §2).

---

## 3. Lesson Categories Enumerated & Walked (Section 3c)

Logged in as `xtbuiquang` and enumerated `/WebGoat/service/lessonmenu.mvc`. The account can see every
lesson category — a standard WebGoat `user` account has full lesson-catalog visibility by design.

| Category | Lessons walked this run |
|---|---|
| Introduction | (enumerated only) |
| General | (enumerated only) |
| (A1) Broken Access Control | **IDOR** (solved), **MissingFunctionAC** (partially) |
| (A2) Cryptographic Failures | (enumerated only) |
| (A3) Injection | **SqlInjection** (solved — 5b numeric SQLi), **CrossSiteScripting** (DOM route), **CrossSiteScriptingStored** (solved), **PathTraversal** (attempted) |
| (A5) Security Misconfiguration | **CSRF** (tested via forged request), **XXE** (solved) |
| (A6) Vuln & Outdated Components | (enumerated only) |
| (A7) Identity & Auth Failure | **AuthBypass** (attempted, inconclusive) |
| (A8)/(A9) | (enumerated only) |
| (A10) SSRF | **SSRF** (solved — task1) |
| Client side / Challenges | (enumerated only) |

---

## 4. ASVS L1 Coverage Checklist (Section 3b — no blanks)

| # | Category | Status | Result |
|---|---|---|---|
| 1 | Authentication | TESTED | 4 sequential failed logins followed by correct password succeeded immediately — no lockout/throttling/CAPTCHA observed (F-07). Login form has no anti-CSRF token. AuthBypass (2FA param-removal) attempted — inconclusive within rate budget. |
| 2 | Session Management | TESTED | `HttpOnly` present; `Secure`/`SameSite` absent (F-05). Session-fixation: pre-set attacker JSESSIONID rejected, fresh ID issued on login — PASS. Logout: old session rejected after logout — invalidation works correctly, PASS. |
| 3 | Access Control / IDOR | TESTED | IDOR lesson: sequential ID enumeration disclosed another "user's" full profile — confirmed (F-02). MissingFunctionAC: hidden admin menu found in HTML comments; direct access returned 500/404 — inconclusive on server-side bypass within budget. |
| 4 | Input Validation / Injection | TESTED | SQLi: numeric injection in SqlInjectionLesson5b → full `user_data` table dump incl. credit-card numbers — confirmed (F-01). Path Traversal: crafted traversal filenames triggered disclosed stack trace (reinforces F-03); out-of-directory write not conclusively confirmed within budget — inconclusive. |
| 5 | XSS (reflected/stored/DOM) | TESTED | Stored XSS payload stored unsanitized and executed, confirmed via phone-home callback — confirmed (F-08). |
| 6 | CSRF | TESTED | Forged cross-origin POST (attacker `Origin`/`Referer`, no CSRF token) to a state-changing endpoint succeeded — confirmed (F-06). |
| 7 | CORS | TESTED — no finding | Preflight `OPTIONS` + credentialed GET with attacker `Origin` sent; no `Access-Control-Allow-Origin`/`-Credentials` headers returned. No CORS misconfiguration found. |
| 8 | File Upload | TESTED | PathTraversal profile-photo multipart endpoints accept attacker-controlled filename metadata; traversal-crafted filenames processed but confirmed out-of-directory write not achieved within budget — inconclusive, overlaps F-03. |
| 9 | SSRF | TESTED | `SSRF/task1`: `url=images/jerry.png` returned unintended server-side resource content — confirmed, lesson-scoped (F-09). Full external-URL SSRF rejected by this task's allow-list. |
| 10 | XXE | TESTED | `xxe/simple`: external-entity payload → full `/etc/passwd` disclosed — confirmed (F-04). |
| 11 | Transport Security | TESTED | All traffic plain HTTP, no TLS; `Secure` cookie flag absent — folded into F-05. |
| 12 | Security Headers | TESTED | CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, COOP all absent — confirmed (F-10). |
| 13 | Error Handling / Info Leakage | TESTED | Every 404/400 response includes a full Java stack trace revealing internal class names, Spring/Tomcat internals, filesystem paths — confirmed (F-03). |
| 14 | Business Logic (lesson-specific) | TESTED | Successfully completed the intended "solve" for SqlInjection(5b), CrossSiteScriptingStored, IDOR, SSRF(task1), XXE(simple) — all behaved per designed vulnerable business logic. |

---

## 5. Findings

### F-01 — SQL Injection → full data exfiltration (SqlInjection lesson)
**Category:** Injection | **Severity: HIGH | Confidence: 10/10**
**Evidence:** `POST /WebGoat/SqlInjection/assignment5b` with `userid=1+OR+1%3D1` returned the full
`user_data` table (14 rows incl. credit-card numbers); `lessonCompleted:true`.
**Fix:** N/A (intentional training lesson); in real code use parameterized queries/prepared statements.

### F-02 — IDOR: sequential-ID profile disclosure (IDOR lesson)
**Category:** Access Control / IDOR | **Severity: MEDIUM | Confidence: 10/10**
**Evidence:** `GET /WebGoat/IDOR/profile/{id}` returns full profile data for any numeric ID with no
ownership check (e.g. ID `2342388` → "Buffalo Bill"'s profile from the `xtbuiquang` session).
**Fix:** N/A (intentional); in real code enforce server-side ownership checks, use non-sequential/opaque IDs.

### F-03 — Verbose stack traces leaked on error responses
**Category:** Error Handling / Info Leakage | **Severity: MEDIUM | Confidence: 9/10**
**Evidence:** Every 404/400 error returns a `"trace"` JSON field with the complete Java/Spring/Tomcat
stack trace, filter-chain internals, and library class names/paths (reproduced on multiple endpoints).
**Fix:** Set `server.error.include-stacktrace=never` and return generic error bodies to clients.

### F-04 — XXE → arbitrary local file disclosure (XXE lesson)
**Category:** XXE | **Severity: HIGH | Confidence: 10/10**
**Evidence:** `POST /WebGoat/xxe/simple` with an external-entity DOCTYPE referencing `file:///etc/passwd`
→ lesson completed; subsequent `GET /WebGoat/xxe/comments` disclosed the full file content.
**Fix:** N/A (intentional); in real code disable DTD/external-entity processing.

### F-05 — Session cookie missing `Secure` and `SameSite` attributes
**Category:** Session Management / Transport Security | **Severity: MEDIUM | Confidence: 9/10**
**Evidence:** `Set-Cookie: JSESSIONID=...; Path=/WebGoat; HttpOnly` observed on every login/logout — no
`Secure`, no `SameSite`.
**Fix:** Serve over HTTPS and add `Secure; SameSite=Lax` (or `Strict`) to the session cookie.

### F-06 — CSRF: no anti-CSRF tokens on state-changing requests
**Category:** CSRF | **Severity: MEDIUM | Confidence: 9/10**
**Evidence:** A forged POST to `/WebGoat/SqlInjection/assignment5b` with attacker `Origin`/`Referer` and
no CSRF token, using only the victim's session cookie, was processed normally (HTTP 200). The `/login`
form itself also lacks a CSRF token.
**Fix:** Enable Spring Security's CSRF protection (token-based) for all state-changing endpoints; pair
with `SameSite=Lax/Strict`.

### F-07 — No account lockout / brute-force throttling on login
**Category:** Authentication | **Severity: MEDIUM | Confidence: 8/10**
**Evidence:** 4 sequential failed logins produced no increasing delay, CAPTCHA, or lockout; the 5th
attempt with the correct password succeeded immediately.
**Fix:** Implement progressive delay / account lockout / CAPTCHA after N failed attempts (ASVS
V2.2.1-class control).

### F-08 — Stored XSS with real script execution (CrossSiteScriptingStored lesson)
**Category:** XSS | **Severity: HIGH | Confidence: 10/10**
**Evidence:** `POST /WebGoat/CrossSiteScriptingStored/stored-xss` with `<script>webgoat.customjs.phoneHome()</script>`
was stored verbatim/unescaped and executed, confirmed by the resulting phone-home callback.
**Fix:** N/A (intentional); in real code HTML-encode all user-supplied output and apply a CSP.

### F-09 — SSRF: server-side resource substitution (SSRF lesson, task1)
**Category:** SSRF | **Severity: MEDIUM | Confidence: 9/10**
**Evidence:** `POST /WebGoat/SSRF/task1` with `url=images/jerry.png` → "You rocked the SSRF!",
lessonCompleted:true. A full external URL against the same param was correctly rejected by the task's
allow-list (no full network SSRF via this endpoint).
**Fix:** N/A (intentional).

### F-10 — Missing security response headers
**Category:** Security Headers | **Severity: LOW | Confidence: 9/10**
**Evidence:** No `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, or `Cross-Origin-Opener-Policy` on any response observed.
**Fix:** Add standard Spring Security header defaults (frame-options, content-type-options, a baseline
CSP, `Referrer-Policy: no-referrer` or similar).

---

## 6. Inconclusive Items (actively probed, not silently skipped)

- **MissingFunctionAC backend bypass:** hidden admin menu links found in HTML comments
  (`access-control/users`, `access-control/config`); direct access attempts returned 500/404 — not
  conclusively confirmed as a server-side bypass within the rate/time budget.
- **AuthBypass (2FA parameter-removal) lesson:** attempted but not achieved within budget.
- **PathTraversal / File-Upload out-of-directory write:** traversal-crafted filenames were processed
  (not rejected outright) by `profile-upload`/`zip-slip` endpoints, but a confirmed out-of-directory
  write was not achieved within budget.

## 7. Comparison to Run #1

Run #1 reported 2 passive header/cookie findings and explicitly flagged itself as incomplete. Run #2
actively probed and obtained concrete request/response evidence for all 14 Section 3b categories,
surfacing 8 additional confirmed issues (F-01–F-04, F-06–F-09) while re-confirming the original 2
(F-05, F-10).
