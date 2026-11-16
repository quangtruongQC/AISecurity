"""
ASVS 5.0.0 L1 requirement triage for WebGoat Run #9 (Section 3k).
Classifies all 345 L1 rows into TESTABLE-HTTP / N/A-TECHNOLOGY / N/A-METHOD / DEFERRED-TOOLING.
Rules are applied at (category, subcategory) granularity by default, with per-ID overrides
for subcategories that mix testable and non-testable rows. Every row gets an explicit reason.
"""
import json
import csv

RAW = r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\evidence\asvs-l1-raw-mcp-export.json"
OUT = r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\evidence\asvs-requirement-triage.csv"

TESTABLE = "TESTABLE-HTTP"
NA_TECH = "N/A-TECHNOLOGY"
NA_METHOD = "N/A-METHOD"
DEFERRED = "DEFERRED-TOOLING"

# Reusable reason strings
R_NOTLS = "Target serves plain HTTP only on 10.242.10.31:8007 with no TLS handshake possible (confirmed: every raw response captured this run, e.g. evidence/http/headers-01-get-login.txt, has no TLS; curl was used over http:// throughout) - requirement is TLS-specific and cannot apply to a non-TLS deployment."
R_NOOAUTH = "WebGoat login is a custom form (POST /WebGoat/login, confirmed in evidence/http/headers-02-post-login.txt) with no OAuth/OIDC/SAML flow; the 13 confirmed sidebar categories (Section 3c) include no OAuth/OIDC lesson or endpoint."
R_NOWEBRTC = "WebGoat is a web training app with no audio/video/P2P media feature; no WebRTC/DTLS-SRTP functionality exists in the lesson set (Section 3c)."
R_NOGRAPHQL = "No GraphQL endpoint exists - confirmed via authenticated direct probe: GET /WebGoat/graphql returned HTTP 404 (evidence/http/headers-03-graphql.txt)."
R_NOWEBSOCKET = "No WebSocket usage observed - the authenticated /WebGoat/login response body contains no 'WebSocket', 'ws://'/'wss://', or sockjs/stomp references (checked this run), and no WS lesson appears in the Section 3c sidebar."
R_NOMFA = "WebGoat's authentication is single-factor username/password only (confirmed via the login form and POST /WebGoat/login flow); no MFA/TOTP/OTP/push/biometric enrollment or verification exists anywhere in the app."
R_NOIDP = "WebGoat does not integrate with any external Identity Provider/SSO/SAML for the test account's login path; authentication is local to the app's own user store."
R_NODOC = "This is a documentation requirement (verifies that something is written down/defined in app or organizational documentation); no such documentation exists or is in scope for this self-owned lab engagement, and no HTTP request can confirm or refute a document's existence/content."
R_NOMETHOD_SRC = "Requires source code, build pipeline, or internal infrastructure/implementation access to verify (e.g., algorithm choice, library internals, key storage, service-to-service config); this Grey-box, no-source engagement (Section 3, Repo path: N/A) cannot observe this via HTTP."
R_NOMETHOD_LOGS = "Requires access to server-side log files/log pipeline to confirm what was logged, in what format, and for how long; this Grey-box engagement has no log access and WebGoat exposes no log-viewing feature to the test account."
R_NOMETHOD_GUARDRAIL_CONC = "Verifying this requires sending genuinely concurrent/parallel requests to win or lose a race condition; Section 6's guardrails explicitly restrict this engagement to sequential requests only ('no concurrency'), so the tooling/method needed is excluded by this engagement's own guardrails, not by effort."
R_NOMETHOD_RESETFORM = "Confirming this fully requires actually submitting/completing the password-reset flow; Section 6's guardrails explicitly prohibit this ('don't submit any contact/password-reset forms if present'), so this is blocked by the engagement's own declared scope limit, not by tester effort."
R_NOFEATURE_ACCOUNT = "WebGoat (a training app, not a real multi-tenant account system) has no general account-settings/profile page for the registered test account outside of lesson content; this specific account-management capability does not exist to test."
R_NOFEATURE_SESSIONSUI = "WebGoat provides no 'active sessions' management UI and no admin role (Section 3c confirms no admin/user visibility split), so there is nothing to click/call for this requirement."
R_NOFEATURE_BIZ = "WebGoat is a lesson/training app with no real booking/inventory/limited-resource or multi-party-approval business feature; this requirement targets functionality that does not exist in this application."
R_MEMSAFE = "WebGoat is written entirely in Java, a memory-managed language with automatic garbage collection; there is no unmanaged/manual memory allocation, pointer arithmetic, or manual buffer handling in the application for this requirement to apply to."
R_TESTABLE_INJECTION = "A hand-crafted HTTP request carrying the relevant injection/encoding payload into the matching WebGoat lesson's input field(s) (per Section 3b/3c active testing) can directly confirm or refute this."
R_TESTABLE_HEADERS = "Directly observable on every captured HTTP response this run (e.g. evidence/http/headers-*.txt) - header presence/absence is a single GET/POST away."
R_TESTABLE_COOKIE = "Directly observable in the Set-Cookie header of the authenticated login response (evidence/http/headers-02-post-login.txt already shows the JSESSIONID cookie's actual flags)."
R_TESTABLE_JWT = "WebGoat's (A7) JWT lesson sub-steps directly exercise this (alg confusion, signature stripping, exp/nbf, audience, trusted-key-source); testable via the lesson's own captured-and-modified request per Section 3f's capture-then-replay method."
R_TESTABLE_SESSION = "Testable by manipulating/reusing the real JSESSIONID captured this run (e.g., reuse after logout, inspect token format/entropy across repeated logins, test fixation) - all single, sequential HTTP requests."
R_TESTABLE_LESSONSTEP = "Testable by directly interacting with the relevant WebGoat lesson's own step flow/form fields per Section 3i/3g (submitting out-of-order steps, tampering hidden fields, bypassing client-side checks)."

rows_out = []

def classify(req):
    rid = req["id"]
    cat = req["category"]
    sub = req.get("subcategory", "")
    desc = req["description"]

    # ---------- Whole-category defaults ----------
    if cat == "OAuth and OIDC":
        return NA_TECH, R_NOOAUTH
    if cat == "WebRTC":
        return NA_TECH, R_NOWEBRTC
    if cat == "Secure Communication":
        return NA_TECH, R_NOTLS

    # ---------- API and Web Service ----------
    if cat == "API and Web Service":
        if sub == "GraphQL":
            return NA_TECH, R_NOGRAPHQL
        if sub == "WebSocket":
            return NA_TECH, R_NOWEBSOCKET
        if rid == "V4.1.2":
            return NA_TECH, "Requirement is about automatic HTTP->HTTPS redirect behavior; target serves plain HTTP only with no HTTPS listener at all (confirmed this run), so there is no HTTPS redirect to test for correctness. " + R_NOTLS
        if sub in ("Generic Web Service Security", "HTTP Message Structure Validation"):
            return TESTABLE, "Testable with a single hand-crafted HTTP request (Content-Type check, header-override attempt, HTTP method probe, or a deliberately malformed request/header to check smuggling-relevant framing) against the live target, consistent with Section 3e's method-tampering checks."
        return TESTABLE, R_TESTABLE_HEADERS

    # ---------- Authentication ----------
    if cat == "Authentication":
        if sub == "Authentication Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Authentication with an Identity Provider":
            return NA_TECH, R_NOIDP
        if sub == "Cryptographic authentication mechanism":
            return NA_TECH, "WebGoat has no certificate-based or hardware-token (e.g., FIDO) cryptographic authentication mechanism; login is username/password only."
        if sub == "General Multi-factor authentication requirements":
            return NA_TECH, R_NOMFA
        if sub == "Out-of-Band authentication mechanisms":
            return NA_TECH, R_NOMFA
        if sub == "Authentication Factor Lifecycle and Recovery":
            if rid == "V6.4.1":
                return NA_TECH, "WebGoat registration lets the user choose their own password directly; there is no system-generated initial password/activation-code flow to verify."
            if rid == "V6.4.2":
                return TESTABLE, "Testable by inspecting the WebGoat registration/account UI for the presence or absence of knowledge-based 'secret question' fields."
            if rid in ("V6.4.3", "V6.4.6"):
                return NA_METHOD, R_NOMETHOD_RESETFORM
            if rid == "V6.4.4":
                return NA_TECH, R_NOMFA
            if rid == "V6.4.5":
                return NA_TECH, "WebGoat's password does not expire/rotate on a schedule and there is no other authentication mechanism (certificate, hardware token) with a renewal/expiry feature to send reminders for."
        if sub == "General Authentication Security":
            if rid == "V6.3.6":
                return TESTABLE, "Testable by inspecting the login form's username field to confirm it is a username, not an email address."
            if rid == "V6.3.7":
                return NA_TECH, R_NOFEATURE_ACCOUNT
            return TESTABLE, "Testable via repeated login attempts, observing lockout/rate-limit behavior, default-account probing, and comparing error responses/timing for valid vs invalid usernames (Section 3b Authentication row)."
        if sub == "Password Security":
            return TESTABLE, "Testable via the registration form and/or the lesson-simulated password-change flow (length limits, character-set restrictions, masking, paste behavior, exact-match verification, breached/common-password checks) - all single HTTP submissions."
        return TESTABLE, "Directly testable via the login flow."

    # ---------- Authorization ----------
    if cat == "Authorization":
        if sub == "Authorization Documentation":
            return NA_METHOD, R_NODOC
        if sub == "General Authorization Design":
            return TESTABLE, "This is the core (A1) Broken Access Control / IDOR test target - modifying IDs/params and probing function-level, data-specific, and field-level access per Section 3b's Access Control row."
        if sub == "Operation Level Authorization":
            if rid == "V8.3.3":
                return NA_METHOD, "Verifying which identity a backend-to-backend call uses requires visibility into internal service-to-service calls, which this Grey-box, no-source engagement cannot observe from outside."
            return TESTABLE, "Testable by manipulating client-side-controlled values (JS-enforced checks, stale self-contained tokens) and replaying/reusing them server-side."
        if sub == "Other Authorization Considerations":
            if rid == "V8.4.1":
                return NA_TECH, "WebGoat is a single-tenant training app (the xtbuiquang test account is a standard user with no tenant/organization concept per Section 3c); there is no multi-tenant boundary to test."
            return NA_TECH, "WebGoat has no distinct administrative interface (Section 3c confirms no admin/user visibility split); there is nothing matching 'administrative interface' to test."

    # ---------- Configuration ----------
    if cat == "Configuration":
        if sub == "Configuration Documentation":
            return NA_METHOD, R_NODOC
        if sub in ("Backend Communication Configuration", "Secret Management"):
            return NA_METHOD, "Describes internal backend-to-backend authentication, least-privilege service accounts, or a secrets-vault implementation; none of this is observable via external HTTP requests without infrastructure/source access."
        if sub == "Unintended Information Leakage":
            return TESTABLE, "Directly the Section 3e advanced checks (.git/.svn exposure, debug mode, directory listing, HTTP TRACE, exposed docs/monitoring endpoints such as /actuator, version-string leakage, served file extensions) - each a single GET request."

    # ---------- Cryptography ----------
    if cat == "Cryptography":
        return NA_METHOD, "Verifies algorithm choice, key management, RNG implementation, or constant-time behavior inside the application's own code; a black-box HTTP client cannot observe which cipher mode, hash function, or RNG implementation the server uses internally. " + R_NOMETHOD_SRC

    # ---------- Data Protection ----------
    if cat == "Data Protection":
        if sub == "Data Protection Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Client-side Data Protection":
            return TESTABLE, "Testable via the browser's DevTools Application panel (localStorage/sessionStorage/cookie contents) and by inspecting Cache-Control/Clear-Site-Data response headers after logout."
        if sub == "General Data Protection":
            if rid in ("V14.2.4", "V14.2.7"):
                return NA_METHOD, "References controls defined by the application's own documented data-protection levels and retention schedule, neither of which exist/are accessible for this self-owned lab target."
            return TESTABLE, "Testable by inspecting URLs/query strings for sensitive data, checking Cache-Control on sensitive responses, checking for third-party tracker requests, probing cache-deception behavior (404 vs serving a cached file), checking response field minimization, and uploading a file with embedded metadata (EXIF) to see if it is stripped."

    # ---------- Encoding and Sanitization ----------
    if cat == "Encoding and Sanitization":
        if sub == "Memory, String, and Unmanaged Code":
            return NA_TECH, R_MEMSAFE
        if sub == "Safe Deserialization":
            if rid == "V1.5.3":
                return NA_METHOD, "Confirming 'different parsers used for the same data type parse consistently' requires knowing which parser implementations are used internally and comparing their source-level behavior; not conclusively black-box testable."
            return TESTABLE, R_TESTABLE_INJECTION + " (XXE via the XXE lesson; insecure-deserialization allowlist bypass via the (A8) Insecure Deserialization lesson's own baseline-request flow per Section 3f - full gadget-chain RCE construction beyond the lesson-provided object would separately require ysoserial-class tooling excluded by guardrails)."
        if sub == "Sanitization":
            if rid in ("V1.3.9", "V1.3.11"):
                return NA_TECH, "No memcache-backed or SMTP/IMAP mail-sending feature is exposed anywhere in the WebGoat lesson set (Section 3c) to direct this payload at."
            return TESTABLE, R_TESTABLE_INJECTION + " (SSRF, SSTI, JNDI, eval/SpEL, SVG, WYSIWYG/HTML, markdown/CSS/XSL, ReDoS, format-string payloads each map to a Section 3b/3e active test)."
        return TESTABLE, R_TESTABLE_INJECTION

    # ---------- File Handling ----------
    if cat == "File Handling":
        if sub == "File Handling Documentation":
            return NA_METHOD, R_NODOC
        return TESTABLE, "Testable via the File Upload/Path Traversal lessons: uploading oversized/zip-bomb/symlink-containing/mismatched-extension/EICAR files and crafted filenames/paths, observing server-side validation (Section 3b File Upload row)."

    # ---------- Secure Coding and Architecture ----------
    if cat == "Secure Coding and Architecture":
        if sub == "Secure Coding and Architecture Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Safe Concurrency":
            return DEFERRED, R_NOMETHOD_GUARDRAIL_CONC
        if sub == "Security Architecture and Dependencies":
            if rid == "V15.2.3":
                return TESTABLE, "Directly the Section 3e debug/test-endpoint checks (/swagger-ui, /v2/api-docs, /h2-console, /actuator) - a single GET per candidate path."
            return NA_METHOD, "References a documented remediation timeframe, a controlled dependency-source repository, or component isolation/sandboxing internals; none of this is observable via external HTTP requests without source/build-pipeline access."
        if sub == "Defensive Coding":
            return TESTABLE, "Testable via a single crafted request per check: requesting an API response and checking for field over-disclosure, submitting an unexpected extra field (mass assignment), sending duplicate parameters (HTTP parameter pollution), sending type-confused JSON values, or sending a proto-pollution payload to a JSON-accepting endpoint - all Section 3e/3g active checks."

    # ---------- Security Logging and Error Handling ----------
    if cat == "Security Logging and Error Handling":
        if sub == "Security Logging Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Error Handling":
            if rid == "V16.5.2":
                return NA_METHOD, "Verifying graceful degradation when an external dependency fails requires the ability to force that dependency to fail, which is not controllable from outside the application in this Grey-box engagement."
            return TESTABLE, "Testable by submitting malformed/invalid input and invalid IDs to trigger errors, then inspecting responses for stack traces/verbose errors vs generic messages, and checking whether the app keeps serving requests afterward (Section 3b Error Handling row)."
        return NA_METHOD, R_NOMETHOD_LOGS

    # ---------- Self-contained Tokens ----------
    if cat == "Self-contained Tokens":
        return TESTABLE, R_TESTABLE_JWT

    # ---------- Session Management ----------
    if cat == "Session Management":
        if sub == "Session Management Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Federated Re-authentication":
            return NA_TECH, R_NOIDP
        if sub == "Defenses Against Session Abuse":
            return NA_TECH, R_NOFEATURE_ACCOUNT + " / " + R_NOFEATURE_SESSIONSUI
        if sub == "Fundamental Session Management Security":
            return TESTABLE, R_TESTABLE_SESSION
        if sub == "Session Termination":
            if rid in ("V7.4.2", "V7.4.5"):
                return NA_TECH, "WebGoat has no account-disable/delete feature and no admin role (Section 3c), so there is no such action to trigger and observe."
            if rid == "V7.4.3":
                return TESTABLE, "Testable via the lesson-simulated password-change flow: change the (simulated) credential and check whether other active sessions are offered/forced to terminate."
            return TESTABLE, R_TESTABLE_SESSION + " (logout-then-reuse for V7.4.1; visible logout link check for V7.4.4)."
        if sub == "Session Timeout":
            return TESTABLE, "Testable by leaving an authenticated session idle past a plausible timeout window and re-checking access, and by holding a session open to probe for an absolute maximum lifetime; time-consuming but within guardrails (no concurrency/volume needed)."

    # ---------- Validation and Business Logic ----------
    if cat == "Validation and Business Logic":
        if sub == "Validation and Business Logic Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Anti-automation":
            return TESTABLE, "Testable by submitting a lesson/registration/login endpoint repeatedly in sequence and observing whether any rate-limit, CAPTCHA, or automation defense triggers (within the single-digit req/s guardrail itself acting as the probe rate)."
        if sub == "Business Logic Security":
            if rid == "V2.3.1":
                return TESTABLE, R_TESTABLE_LESSONSTEP + " (submit a later lesson step/assignment before completing an earlier required one)."
            if rid == "V2.3.2":
                return NA_METHOD, "References business-logic limits defined in the application's own documentation, which does not exist/is not accessible for this target."
            if rid == "V2.3.3":
                return NA_METHOD, "Confirming atomic rollback-on-failure for a business transaction requires reliably forcing a mid-transaction failure and inspecting resulting server-side state, which is not reliably achievable or observable from outside without source/DB access."
            if rid in ("V2.3.4", "V2.3.5"):
                return NA_TECH, R_NOFEATURE_BIZ
        if sub == "Input Validation":
            return TESTABLE, "Testable by sending values that violate the UI's own client-side validation directly to the backend endpoint, bypassing the browser entirely (Section 3g point 3)."

    # ---------- Web Frontend Security ----------
    if cat == "Web Frontend Security":
        if sub == "Web Frontend Security Documentation":
            return NA_METHOD, R_NODOC
        if sub == "Browser Origin Separation":
            return TESTABLE, "Directly the Section 3b CORS/CSRF active-testing row (varied Origin headers, preflight OPTIONS, credentialed cross-origin request, postMessage/JSONP/XSSI probes)."
        if sub == "Browser Security Mechanism Headers":
            if rid == "V3.4.1":
                return NA_TECH, "HSTS is a TLS-trust-pinning mechanism with no effect over plain HTTP; " + R_NOTLS
            return TESTABLE, R_TESTABLE_HEADERS + " (CSP, X-Content-Type-Options, Referrer-Policy, frame-ancestors/clickjacking PoC per Section 3e, CSP report-uri, Cross-Origin-Opener-Policy)."
        if sub == "Cookie Setup":
            return TESTABLE, R_TESTABLE_COOKIE
        if sub == "External Resource Integrity":
            return TESTABLE, "Testable by viewing page source for externally-hosted JS/CSS/font references and checking for a matching 'integrity' (SRI) attribute."
        if sub == "Other Browser Security Considerations":
            if rid == "V3.7.4":
                return NA_TECH, "HSTS preload is a TLS-only mechanism; " + R_NOTLS
            if rid == "V3.7.5":
                return NA_METHOD, "Requires comparing documented expected behavior against testing in a non-conforming browser lacking specific security features; no such documentation exists and this is not a practical single-request HTTP check."
            return TESTABLE, "Testable via view-source (deprecated plugin technology check) and a crafted open-redirect probe/parameter."
        if sub == "Unintended Content Interpretation":
            return TESTABLE, "Testable by requesting a user-uploaded/API resource directly out of context and inspecting Content-Disposition/CSP sandbox behavior, and by inspecting client-side JS source for unsafe HTML-rendering functions or DOM-clobbering-prone patterns."

    raise ValueError(f"Unclassified row: {rid} / {cat} / {sub}")


with open(RAW, encoding="utf-8") as f:
    data = json.load(f)

reqs = data["requirements"]
reqs.sort(key=lambda r: r["id"])

counts = {TESTABLE: 0, NA_TECH: 0, NA_METHOD: 0, DEFERRED: 0}
for r in reqs:
    tcat, reason = classify(r)
    counts[tcat] += 1
    rows_out.append({
        "id": r["id"],
        "category": r["category"],
        "subcategory": r.get("subcategory", ""),
        "description": r["description"],
        "triage_category": tcat,
        "reason": reason,
    })

assert len(rows_out) == 345, f"expected 345 rows, got {len(rows_out)}"

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "category", "subcategory", "description", "triage_category", "reason"])
    w.writeheader()
    for row in rows_out:
        w.writerow(row)

print("Total rows:", len(rows_out))
for k, v in counts.items():
    print(f"{k}: {v}")
print("Wrote:", OUT)
