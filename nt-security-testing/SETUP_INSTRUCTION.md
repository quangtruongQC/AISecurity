# OWASP ASVS MCP Server — Setup Guide for GitHub Copilot (VS Code)

This is the GitHub Copilot 

---

## Quick Start

### 1. Build the Server

```powershell
cd nt-security-testing
npm install
npm run build
```

This produces `dist/index.js` (the stdio MCP server entry point).

### 2. Choose Your Setup Method

- **Method A**: Workspace-level `.vscode/mcp.json` (recommended — shareable via source control, scoped to this repo/workspace)
- **Method B**: User profile `mcp.json` (available in every VS Code workspace)
- **Method C**: Guided setup via the Command Palette (`MCP: Add Server`)
- **Method D**: `.env` file for local/manual `node dist/index.js` runs (same as Claude Code setup — unchanged)

---

## Method A: Workspace-Level `.vscode/mcp.json` (Recommended)

**Best for:** project-specific configuration, version-controlled with the repo.

### Step 1: Create the file

Create `.vscode/mcp.json` at the root of the workspace that contains this repo (e.g.
 `nt-security-testing/.vscode/mcp.json` if you open this
folder directly as its own workspace).

### Step 2: Add the server entry

VS Code's MCP config uses a top-level **`servers`** key and an explicit **`type`** field. 
Add `chrome-devtools` alongside `owasp-asvs` — it needs no `env` block,
just `npx` to fetch and run the published package on demand:

```jsonc
{
  "servers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "owasp-asvs": {
      "type": "stdio",
      "command": "node",
      "args": ["${workspaceFolder}/nt-security-testing/dist/index.js"],
      "env": {
        "ASVS_SECURITY_TIER": "BALANCED",
        "ASVS_RATE_LIMIT": "true",
        "ASVS_RATE_LIMIT_REQUESTS": "100",
        "ASVS_RATE_LIMIT_WINDOW_MS": "60000",
        "LOG_LEVEL": "warn",
        "LOG_FILE": "${workspaceFolder}/nt-security-testing/asvs-server.log"
      }
    }
  }
}
```

> If you open `nt-security-testing` itself as the workspace root, drop the extra path segment:
> `"args": ["${workspaceFolder}/dist/index.js"]` for `owasp-asvs` (`chrome-devtools`'s args are
> unaffected, since it doesn't reference `${workspaceFolder}`).
>
> Optional `chrome-devtools` flags (add to `args` if needed): `--proxyServer=http://host:port` to
> route traffic through an intercepting proxy, `--acceptInsecureCerts=true` for self-signed/test
> certs, and `--userDataDir=<path>` to isolate its browser profile from your regular Chrome
> profile.

### Step 3: Trust and start the servers

The first time VS Code starts each of these servers it shows a **trust prompt** (local MCP
servers run arbitrary code on your machine) — review the config and confirm for both. VS Code
then discovers `owasp-asvs`'s 9 tools and `chrome-devtools`'s browser-automation tools
automatically. `chrome-devtools` also launches a real Chrome instance on first use — allow it
through any local firewall prompt if one appears.

### Step 4: Commit (optional)

`.vscode/mcp.json` can be committed to share the config with your team. Avoid putting secrets in
it directly — use `${input:...}` variables for anything sensitive (this server has no required
secrets, so plain `env` values are fine here).

### Step 5: Verify

Open the Chat view (`Ctrl+Alt+I`), select **Configure Tools** in the chat input, and confirm both
`owasp-asvs` and `chrome-devtools` tools are listed and enabled. Test `owasp-asvs` with:

```
Show me all ASVS Level 1 authentication requirements
```

And test `chrome-devtools` with:

```
Open a new browser page and navigate to https://example.com, then take a snapshot of the page
```

---

## Method B: User Profile `mcp.json` (Global, all workspaces)

**Best for:** using this server across every project, not just this repo.

### Step 1: Open the user config

Run **`MCP: Open User Configuration`** from the Command Palette (`Ctrl+Shift+P`). This opens the
`mcp.json` file in your VS Code user profile folder.

### Step 2: Add the same server entry

Same schema as Method A, but use an **absolute path** for `owasp-asvs` (no `${workspaceFolder}`,
since this file isn't tied to one workspace). `chrome-devtools` is unaffected since it uses `npx`
rather than a workspace-relative path:

```json
{
  "servers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "owasp-asvs": {
      "type": "stdio",
      "command": "node",
      "args": ["C:/absolute/path/to/nt-security-testing/dist/index.js"],
      "env": {
        "ASVS_SECURITY_TIER": "BALANCED",
        "ASVS_RATE_LIMIT": "true",
        "ASVS_RATE_LIMIT_REQUESTS": "100",
        "ASVS_RATE_LIMIT_WINDOW_MS": "60000",
        "LOG_LEVEL": "warn",
        "LOG_FILE": "C:/absolute/path/to/nt-security-testing/asvs-server.log"
      }
    }
  }
}
```

### Step 3: Save and trust

VS Code prompts for trust on first start of each server, same as Method A.

---

## Method C: Guided Setup (Command Palette)

**Best for:** first-time setup without hand-editing JSON.

1. Open the Command Palette (`Ctrl+Shift+P`) and run **`MCP: Add Server`**.
2. Choose **Command (stdio)** as the server type.
3. Command: `node`; Args: the absolute or `${workspaceFolder}`-relative path to `dist/index.js`. (e.g, `node ${workspaceFolder} dist/index.js`)
4. Name the server `owasp-asvs`.
5. Choose **Workspace** (writes to `.vscode/mcp.json`) or **Global** (writes to the user profile).
6. Repeat for `chrome-devtools`: Command **`npx`**; Args: `-y chrome-devtools-mcp@latest`; no
   `env` block needed. Name it `chrome-devtools`. (e.g, `npx -y chrome-devtools-mcp@latest`)

---

## Method D: `.env` File for Manual/CLI Runs

**Best for:** local development, testing the server outside of VS Code's MCP client.

Unchanged from the Claude Code setup — this is just running the Node process directly, so the
client (Copilot vs. Claude) doesn't matter here.

```powershell
cd nt-security-testing
Copy-Item .env.example .env
# edit .env, then:
npm install --save-dev dotenv-cli
npx dotenv -e .env -- node dist/index.js
```

See `ENVIRONMENT_VARIABLES.md` for the full variable reference (identical for both clients).

---

## Environment Variables Reference

Same variables as `SETUP_GUIDE.md` / `ENVIRONMENT_VARIABLES.md` — the server doesn't know or care
which MCP client launched it.

```bash
ASVS_SECURITY_TIER=BALANCED             # CONSERVATIVE | BALANCED | GENEROUS
ASVS_RATE_LIMIT=true
ASVS_RATE_LIMIT_REQUESTS=100
ASVS_RATE_LIMIT_WINDOW_MS=60000
LOG_LEVEL=warn                          # error | warn | info | debug
LOG_FILE=./asvs-server.log
ASVS_DATA_HASH=""                       # optional SHA-256 of data/asvs-5.0.0.json
ASVS_USE_OPENCRE=false
```

**Windows PowerShell SHA-256 for `ASVS_DATA_HASH`:**
```powershell
Get-FileHash data\asvs-5.0.0.json -Algorithm SHA256
```

---

## Verification (VS Code / Copilot specific)

### Confirm tools are loaded
- Extensions view (`Ctrl+Shift+X`) → **MCP SERVERS - INSTALLED** section should list both
  `owasp-asvs` and `chrome-devtools`.
- Or Command Palette → **`MCP: List Servers`** → select either name to see status/actions.
- Or in the Chat view, select **Configure Tools** to see the individual `owasp-asvs` tools and the
  `chrome-devtools` browser-automation tools, and toggle them on/off.

### Confirm it actually answers
In Chat, ask:
```
Search ASVS requirements for "SQL injection"
```
and confirm you get structured JSON-backed results (not a generic LLM answer).

### Check logs
Same `asvs-server.log` file as the Claude setup (Winston JSON logs). In VS Code, you can also use
**`MCP: List Servers`** → select `owasp-asvs` → **Show Output** to see the MCP protocol-level log
(stdio traffic, startup errors) directly in VS Code's Output panel — this is the fastest way to
debug a server that fails to start, and doesn't require opening the log file manually.

---

## Troubleshooting

### Server not starting / not listed
1. Confirm `dist/index.js` exists: `Test-Path nt-security-testing/dist/index.js` (run `npm run build` if missing).
2. Confirm `node` is on PATH: `node --version` (for `owasp-asvs`) and `npx --version` (for `chrome-devtools`).
3. Run `MCP: List Servers` → select `owasp-asvs` or `chrome-devtools` → **Show Output** for the exact startup error.
4. Confirm you accepted the trust prompt — a declined/reset trust silently disables the server (`MCP: Reset Trust` to re-prompt).
5. **`chrome-devtools`-specific:** the first run downloads the `chrome-devtools-mcp` package via
   `npx` and launches a real Chrome instance — expect a longer first start, and confirm Chrome/
   Chromium is installed and not blocked by a corporate policy or firewall.

### Config changes not taking effect
- VS Code needs to restart the server after editing `mcp.json`. Either use `MCP: List Servers` →
  restart the server, or enable the experimental `chat.mcp.autostart` setting to auto-restart on
  config changes.
- Double-check you used `servers` (VS Code) and not `mcpServers` (Claude) examples into `.vscode/mcp.json` is the most
  common mistake, since the two schemas differ only in that one key name plus the extra `type` field.

### Server enabled but tools missing from a specific chat request
Open **Configure Tools** in the chat input and confirm the `owasp-asvs` tools aren't individually
toggled off — VS Code lets you disable specific tools per server without disabling the whole
server.

---

Everything else — the 9 tools, ASVS/CWE/NIST/HIPAA data, security tiers, rate limiting — is
identical regardless of which client you use, since it all lives in the server process itself.
