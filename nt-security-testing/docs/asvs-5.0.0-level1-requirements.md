# OWASP ASVS 5.0.0 — Level 1 Requirements (Reference)

All 70 requirements marked **L1** in ASVS 5.0.0 — the baseline every application should meet, fully testable via black-box DAST without source access. Pulled from `nt-security-testing/data/asvs-5.0.0.json`.

Two chapters (V16 GenAI, and one other) have zero L1-rated items — everything in them starts at L2, so they don't appear below.

## Encoding and Sanitization
- **V1.2.1** — Output encoding for HTTP/HTML/XML responses matches context (HTML elements, attributes, CSS, headers)
- **V1.2.2** — Untrusted data in dynamically built URLs is encoded per context; only safe URL protocols allowed
- **V1.2.3** — Output encoding/escaping used when dynamically building JS/JSON content
- **V1.2.4** — DB queries use parameterized queries/ORMs, protected from SQL/NoSQL injection
- **V1.2.5** — OS command injection prevented via parameterized calls or output encoding
- **V1.3.1** — Untrusted HTML from WYSIWYG editors sanitized via a known secure library
- **V1.3.2** — `eval()`/dynamic code execution avoided; sanitize input if unavoidable
- **V1.5.1** — XML parsers configured restrictively; external entity resolution disabled (XXE)

## Validation and Business Logic
- **V2.1.1** — Documentation defines input validation rules against expected structure
- **V2.2.1** — Input validated against allow-lists/expected structure for business/security decisions
- **V2.2.2** — Input validation enforced at a trusted service layer, not just client-side
- **V2.3.1** — Business logic flows processed only in expected sequential order

## Web Frontend Security
- **V3.2.1** — Controls prevent browsers rendering responses in the wrong context (API/upload responses)
- **V3.2.2** — Text-only content rendered via safe functions (`textContent`, not `innerHTML`)
- **V3.3.1** — Cookies have `Secure` attribute + `__Host-`/`__Secure-` prefix
- **V3.4.1** — `Strict-Transport-Security` header on all responses, max-age ≥ 1 year
- **V3.4.2** — CORS `Access-Control-Allow-Origin` is fixed or allowlist-validated
- **V3.5.1** — Non-preflight-reliant sensitive requests validated as same-origin (CSRF defense)
- **V3.5.2** — Preflight-reliant sensitive requests can't be triggered without a preflight
- **V3.5.3** — Sensitive functionality uses non-"safe" HTTP methods (POST/PUT/PATCH/DELETE)

## API and Web Service
- **V4.1.1** — Every response with a body has a correct `Content-Type` + charset
- **V4.4.1** — WebSocket connections use WSS (TLS)

## File Handling
- **V5.2.1** — File size limits enforced to prevent performance/DoS impact
- **V5.2.2** — File extension + content (magic bytes) validated against expected type
- **V5.3.1** — Uploaded/generated files in public folders aren't executed as server code
- **V5.3.2** — File paths use trusted/internal data, not raw user input (path traversal/SSRF)

## Authentication
- **V6.1.1** — Documentation defines rate-limiting/anti-automation controls
- **V6.2.1** — Passwords ≥ 8 chars (15+ recommended)
- **V6.2.2** — Users can change their password
- **V6.2.3** — Password change requires current + new password
- **V6.2.4** — New/changed passwords checked against top-3000 breached password list
- **V6.2.5** — No composition rules restricting character types
- **V6.2.6** — Password fields use `type=password` (with optional reveal)
- **V6.2.7** — Paste, browser/password-manager autofill permitted
- **V6.2.8** — Password verified exactly as received, no truncation/case changes
- **V6.3.1** — Credential-stuffing/brute-force controls implemented per documentation
- **V6.3.2** — Default accounts (root/admin/sa) absent or disabled
- **V6.4.1** — System-generated initial passwords are random, expire quickly, can't become permanent
- **V6.4.2** — No password hints or knowledge-based "secret questions"

## Session Management
- **V7.2.1** — Session token verification done via trusted backend service
- **V7.2.2** — Dynamically generated tokens used, not static API secrets
- **V7.2.3** — Reference tokens are CSPRNG-generated with ≥128 bits entropy
- **V7.2.4** — New session token issued on authentication/re-authentication
- **V7.4.1** — Terminated sessions can't be reused (logout/expiry invalidation)
- **V7.4.2** — All active sessions terminated when an account is disabled/deleted

## Authorization
- **V8.1.1** — Documentation defines function-level and data-specific access rules
- **V8.2.1** — Function-level access restricted to explicit permissions
- **V8.2.2** — Data-specific access restricted (mitigates IDOR/BOLA)
- **V8.3.1** — Authorization enforced at a trusted service layer, not client-side

## Self-contained Tokens
- **V9.1.1** — Tokens validated via signature/MAC before trusting contents
- **V9.1.2** — Only allowlisted algorithms used; `none` algorithm disallowed
- **V9.1.3** — Validation key material from trusted pre-configured sources (`jku`/`x5u`/`jwk` allowlisted)
- **V9.2.1** — Token validity time span (`nbf`/`exp`) enforced

## OAuth and OIDC
- **V10.4.1** — Redirect URIs validated against exact-match client allowlist
- **V10.4.2** — Authorization codes are single-use; reuse revokes issued tokens
- **V10.4.3** — Authorization codes are short-lived (≤10 min at L1/L2)
- **V10.4.4** — Clients restricted to grants they need; `token`/`password` grants banned
- **V10.4.5** — Refresh token replay mitigated (rotation or sender-constrained tokens)

## Cryptography
- **V11.3.1** — No insecure block modes (ECB) or weak padding (PKCS#1 v1.5)
- **V11.3.2** — Only approved ciphers/modes (e.g., AES-GCM)
- **V11.4.1** — Only approved hash functions; MD5 banned for crypto use

## Secure Communication
- **V12.1.1** — Only TLS 1.2/1.3 enabled, latest preferred
- **V12.2.1** — TLS enforced for all client↔external-service connections, no fallback
- **V12.2.2** — Publicly trusted TLS certificates used

## Configuration
- **V13.4.1** — Source control metadata (`.git`/`.svn`) not deployed or inaccessible

## Data Protection
- **V14.2.1** — Sensitive data never sent via URL/query string
- **V14.3.1** — Authenticated data cleared from client storage on session termination

## Secure Coding and Architecture
- **V15.1.1** — Documentation defines remediation timeframes for vulnerable components
- **V15.2.1** — No components breach documented remediation timeframes
- **V15.3.1** — API responses return only required fields, not entire objects
