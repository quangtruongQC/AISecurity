# Chrome Evidence Index — Run 20261116-0823-webgoat-l1-greybox-evidence

| Filename | Description |
|---|---|
| 01-login-page.png | WebGoat login page before authentication (baseline, also the clickjacking PoC target). |
| 02-sidebar-full-lesson-access.png | Post-login sidebar for account `xtbuiquang`, confirming all 13 lesson categories listed in intake Section 3c are visible (full lesson access, no role restriction). |
| 03-idor-lesson-page.png | IDOR lesson landing page / lesson-internal login form ("tom"/"cat") prior to exploitation. |
| 04-idor-crossuser-profile-disclosed.png | IDOR lesson step 2 UI after GET /WebGoat/IDOR/profile/2342388 succeeded, confirming F-02 (cross-user profile disclosure) with the "Well done, you found someone else's profile" feedback visible. |
| 15-stored-xss-page-screenshot.png | CrossSiteScriptingStored lesson comment thread; the comment dated 2026-11-16 00:44:51 (containing the `<script>` payload) renders with no visible text, consistent with the script tag executing instead of being displayed/escaped — supports F-08. |
| 16-clickjacking-login-framed.png | Clickjacking PoC: WebGoat `/WebGoat/login` rendered inside an `<iframe>` on a simulated attacker page (same host, different path), fully interactive with no `X-Frame-Options`/CSP `frame-ancestors` blocking — strengthens F-10. |
| 20-about-webgoat-version.png | "About WebGoat" dialog confirming application Version 2026.4 — supports the (A6) Vulnerable & Outdated Components version-fingerprinting check (Section 3e). |
