# OWASP ASVS MCP Server

[![Security Status](https://img.shields.io/badge/ASVS%20L1%20Compliance-87%25-brightgreen)](SECURITY.md)
[![Production Ready](https://img.shields.io/badge/Production-Ready-success)](SECURITY.md)
[![OWASP ASVS](https://img.shields.io/badge/OWASP%20ASVS-5.0.0-blue)](https://owasp.org/www-project-application-security-verification-standard/)

A **production-ready** Model Context Protocol (MCP) server that provides AI assistants with access to the OWASP Application Security Verification Standard (ASVS), enabling intelligent security recommendations and requirement lookups.

## **Git Repository**: https://github.com/NashTech-Global/nt-security-testing
# temporary replacement for training
**Git Repository**: https://github.com/hientrinhgpt/nt-security-testing

**Security:** This server implements production-grade security controls including structured logging, TLS 1.2+, data integrity verification, rate limiting, and configurable security tiers. See [SECURITY.md](SECURITY.md) for detailed documentation.

> **Quick setup:** see **[Configuration → For GitHub Copilot (VS Code)](#for-github-copilot-vs-code)**
> below, or go straight to **[SETUP_INSTRUCTION.md](SETUP_INSTRUCTION.md)** for the full guide
> covering VS Code's `mcp.json` schema plus verification/troubleshooting. For running an actual
> security test end-to-end (not just querying ASVS data), see
> **[SECURITY-TEST-INTAKE.md](SECURITY-TEST-INTAKE.md)**,
> **[SECURITY-TEST-REPORT-TEMPLATE.md](SECURITY-TEST-REPORT-TEMPLATE.md)**, and
> **[.github/copilot-instructions.md](.github/copilot-instructions.md)**.

## Features

### Core Capabilities
- **Query by Level**: Get all requirements for ASVS verification levels L1, L2, or L3
- **Query by Category**: Filter requirements by security categories (Authentication, Access Control, etc.)
- **Detailed Requirements**: Look up specific requirements by ID
- **Smart Recommendations**: Get prioritized control recommendations based on your application context
- **Search**: Find requirements by keyword or vulnerability type
- **Category Overview**: See summaries of all ASVS categories
- **Compliance Mapping**: Map ASVS requirements to compliance frameworks with validated HIPAA mappings
- **Gap Analysis**: Identify missing controls needed for compliance frameworks
- **Compliance Impact**: Understand which regulations a security control helps satisfy
- **HIPAA Integration**: 76 validated HIPAA Security Rule mappings to ASVS 5.0.0 requirements

### Production-Grade Security ✅
- **Structured Logging**: Winston-based JSON logging with rotation (10MB max, 5 files)
- **Data Integrity**: SHA-256 hash verification for remote data fetching
- **TLS 1.2+**: Explicit TLS configuration with certificate validation
- **Rate Limiting**: Sliding window algorithm (configurable: 100 req/min default)
- **Memory Safety**: Cache size limits and input validation
- **Request Tracking**: UUID-based request IDs for log correlation
- **Configurable Security**: Three tiers (CONSERVATIVE/BALANCED/GENEROUS)
- **Environment Variables**: Full configuration via env vars (see [SETUP_INSTRUCTION.md](SETUP_INSTRUCTION.md))

## Installation

### From Git Repository (Recommended)

```bash
# Clone the repository
# git clone https://github.com/NashTech-Global/nt-security-testing.git
# temporary replacement for training
git clone https://<KEY>@github.com/hientrinhgpt/nt-security-testing.git
cd nt-security-testing

# Install dependencies
npm install

# Build the TypeScript code
npm run build
```

### Manual Installation

```bash
# Create the project directory
mkdir nt-security-testing
cd nt-security-testing

# Initialize and install dependencies
npm install

# Build the TypeScript code
npm run build
```

## Project Structure

```
nt-security-testing/
├── src/
│   ├── index.ts                          # Main server code
│   └── opencre-client.ts                 # OpenCRE API client
├── data/
│   ├── asvs-5.0.0.json                   # ASVS 5.0.0 requirements (345 reqs)
│   ├── asvs-4.0.3.json                   # ASVS 4.0.3 requirements (legacy)
│   ├── asvs-5.0.0-hipaa-mapping.json     # Validated HIPAA mappings ✅
│   ├── asvs-4.0.3-hipaa-mapping.json     # Legacy HIPAA mappings (ASVS 4.0.3)
│   ├── asvs-cwe-mapping.json             # Official CWE mappings from OWASP
│   ├── asvs-nist-mapping.json            # Official NIST 800-63B mappings
│   ├── asvs-nist-mapping.md              # Source NIST markdown mapping
│   ├── opencre-iso27001-mappings.json    # OpenCRE ISO 27001 mappings
│   └── drafts/                           # Work-in-progress/candidate mapping files
├── scripts/
│   ├── update-asvs-data.js               # Update ASVS from OWASP GitHub
│   ├── parse-nist-mapping.cjs            # Parse NIST markdown to JSON
│   ├── benchmark-loading.js              # Performance benchmarking
│   ├── validate-asvs5-hipaa-mappings.js  # Validate HIPAA mappings
│   ├── validate-hipaa-mappings.js        # Validate legacy HIPAA mappings
│   ├── validate-corrected.js             # Validate corrected mapping data
│   ├── test-hipaa-integration.js         # Test HIPAA integration
│   ├── analyze-asvs-5.js                 # Analyze ASVS 5.0.0 requirement data
│   ├── apply-asvs5-mappings.js           # Apply mappings onto ASVS 5.0.0
│   ├── asvs4-to-5-mapping.json           # ASVS 4.0.3 -> 5.0.0 crosswalk data
│   ├── check-v1-14.js                    # Requirement-range spot-check script
│   ├── compare-asvs-versions.js          # Diff ASVS 4.0.3 vs 5.0.0
│   ├── convert-hipaa-to-asvs5.js         # Convert HIPAA mappings to ASVS 5.0.0
│   └── fetch-opencre-iso27001.js         # Fetch OpenCRE ISO 27001 mappings
├── docs/
│   ├── asvs-5.0.0-level1-requirements.md # ASVS L1 requirements reference
│   ├── asvs-5.0.0-level2-requirements.md # ASVS L2 requirements reference
│   └── asvs-5.0.0-level3-requirements.md # ASVS L3 requirements reference
├── runs/                                  # Security test run artifacts
│   └── <timestamp>-<target>-<scope>/     # Per-run folder (evidence/, scripts/, report)
├── dist/                                  # Compiled JavaScript (generated, git-ignored)
├── .github/
│   └── copilot-instructions.md           # GitHub Copilot instructions (this repo's workflow contract)
├── .mcp.json / .mcp.json.example         # MCP server configuration (legacy, unused by VS Code)
├── package.json
├── tsconfig.json
├── README.md
├── SETUP_INSTRUCTION.md                   # GitHub Copilot / VS Code setup guide
├── SECURITY-TEST-INTAKE.md                # Security-test intake template
├── SECURITY-TEST-REPORT-TEMPLATE.md       # Security-test report template
├── SECURITY.md                            # Security controls & posture documentation
├── ENVIRONMENT_VARIABLES.md               # Full environment variable reference
├── HIPAA_INTEGRATION.md                   # HIPAA integration docs
├── COMPLIANCE_MAPPING_AUDIT.md            # Compliance mapping audit notes
├── MAPPING_INTEGRATION_PROPOSAL.md        # Mapping integration proposal
├── PHASE1_IMPLEMENTATION.md / PHASE2_IMPLEMENTATION.md / PHASE3_IMPLEMENTATION.md  # Phased implementation notes
├── test-phase1.js / test-phase2.js / test-phase3.js  # Phase verification scripts
└── *-report.md      # Sample security test reports
```

## Data Sources

This MCP server uses **official OWASP ASVS data and mappings**:

### ASVS Requirements
- **Source**: [OWASP ASVS 5.0.0](https://github.com/OWASP/ASVS)
- **File**: `data/asvs-5.0.0.json`
- **Contains**: All security verification requirements with levels (L1, L2, L3)

### CWE Mappings ✅ Official
- **Source**: [OWASP ASVS 5.0 CWE Mapping](https://github.com/OWASP/ASVS/blob/master/5.0/mappings/v5.0.be_cwe_mapping.json)
- **File**: `data/asvs-cwe-mapping.json`
- **Contains**: 214 mappings from ASVS requirements to Common Weakness Enumeration (CWE) IDs
- **Status**: Official OWASP mapping

### NIST Mappings ✅ Official
- **Source**: [OWASP ASVS 5.0 NIST Mapping](https://github.com/OWASP/ASVS/blob/master/5.0/mappings/nist.md)
- **File**: `data/asvs-nist-mapping.json`
- **Contains**: 52 mappings from ASVS requirements to NIST 800-63B authentication guidelines
- **Status**: Official OWASP mapping

### HIPAA Mappings ✅ Validated
- **Source**: Validated HIPAA Security Rule mappings (45 CFR Parts 164.308, 164.312, etc.)
- **File**: `data/asvs-5.0.0-hipaa-mapping.json`
- **Contains**: 76 HIPAA requirements mapped to 48 ASVS 5.0.0 requirements (102 total mappings)
- **Coverage**: 94.7% full coverage, 1.3% partial, 3.9% no coverage (physical security only)
- **Status**: Validated - All mappings verified against ASVS 5.0.0 and HIPAA Security Rule
- **Date**: Created 2025-10-22
- **See**: `HIPAA_INTEGRATION.md` for detailed documentation

### Other Compliance Framework Mappings ⚠️ Illustrative Only
- **Frameworks**: PCI DSS, GDPR, SOX, ISO 27001
- **Status**: **Not official** - Illustrative examples for demonstration purposes only
- **Important**: These mappings are conceptually reasonable but have NOT been validated by compliance auditors
- **Recommendation**: For production compliance work, use [OpenCRE](https://www.opencre.org) or consult qualified compliance professionals. HIPAA mappings (above) are an exception - they have been validated.

### Updating Data

```bash
# Update ASVS requirements data
npm run update-asvs

# Update CWE and NIST mappings (manual)
curl -o data/asvs-cwe-mapping.json https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/mappings/v5.0.be_cwe_mapping.json
curl -o data/asvs-nist-mapping.md https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/mappings/nist.md
node scripts/parse-nist-mapping.cjs
```

## Configuration

The server supports comprehensive configuration via environment variables. See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for the complete variable reference.

### Quick Start Configuration

Add the server to your MCP client configuration:

### For GitHub Copilot (VS Code)

> Full walkthrough (workspace vs. user config, Command Palette method, troubleshooting): **[SETUP_INSTRUCTION.md](SETUP_INSTRUCTION.md)**.

1. **Build the server**:
   ```powershell
   cd nt-security-testing
   npm install
   npm run build
   ```

2. **Add a server entry** to `.vscode/mcp.json` (workspace-level, recommended) or your user `mcp.json`
   (open via Command Palette → `MCP: Open User Configuration`). VS Code's MCP config uses a
   top-level **`servers`** key and an explicit **`type`** field:

   ```jsonc
   {
     "servers": {
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

3. **Trust the server** when VS Code prompts (local MCP servers run arbitrary code) — review and confirm.

4. **Verify it's working**: open the Chat view (`Ctrl+Alt+I`), select **Configure Tools**, and confirm
   `owasp-asvs` is listed and enabled. Then test with a prompt such as:
   ```
   Show me all ASVS Level 1 authentication requirements
   ```

### Environment Variables

The server supports comprehensive configuration. See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for complete reference.

**Key Variables:**
- `ASVS_SECURITY_TIER`: CONSERVATIVE | BALANCED | GENEROUS (default: BALANCED)
- `ASVS_RATE_LIMIT`: Enable rate limiting (default: true)
- `ASVS_RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `LOG_LEVEL`: error | warn | info | debug (default: info)
- `LOG_FILE`: Path to log file (default: ./asvs-server.log)
- `ASVS_DATA_HASH`: SHA-256 hash for data integrity verification (optional)

## Sample Prompts — Security Tester Reference

These prompts follow one pattern: **`SECURITY-TEST-INTAKE.md` is the single source of truth**.
None of the prompts below hardcode target URLs, scope, rate limits, or ASVS level — they all
tell Copilot to read those from the intake file instead. That means changing an engagement's
parameters (new target, different guardrails, rerun) only requires editing the intake copy, not
rewriting any prompt.

See `.github/copilot-instructions.md` for the rules Copilot follows behind these prompts.

### 1. Prerequisite: create the intake (one-time per engagement)

`SECURITY-TEST-INTAKE.md` now has a "Setup Instructions" section at the top that tells Copilot
to derive the run ID, create `nt-security-testing/runs/<run-id>/`, and copy itself there — so the
prompt only needs the engagement details, not the folder path:

- "Start a new security test intake for target [URL], environment [Production/Staging/Local], test
type [black-box/grey-box/source review], ASVS target level [L1/L2/L3]. Follow the Setup
Instructions at the top of SECURITY-TEST-INTAKE.md to create the run folder and copy. Ask me for
anything else you need before marking Section 0/9."


### 2. Get all requirements for a specific verification level.

**Example Use:**
- "Show me all Level 1 ASVS requirements"
- "What are the L2 security requirements?"
- "Get the first 50 Level 1 requirements"

### 3. Get requirements filtered by security category.

**Example Use:**
- "What are the authentication requirements in ASVS?"
- "Show me Level 2 session management requirements"
- "Get the first 25 access control requirements"

### 4. Get detailed information about a specific requirement.

**Parameters:**
- `requirement_id` (string): ASVS ID (e.g., "2.1.1")

**Example Use:**
- "Tell me about ASVS requirement 2.1.1"
- "What does requirement 3.2.1 say?"

### 5. Get prioritized security recommendations based on context.

**Example Use:**
- "We're a fintech app at L1, recommend priority controls to reach L2"
- "What authentication controls should we implement first for a healthcare application?"

### 6. Search requirements by keyword

**Example Use:**
- "Find requirements related to SQL injection"
- "Search for password requirements"

### 7. Get an overview of all ASVS categories.

**Example Use:**
- "Give me a summary of all ASVS categories"
- "How many requirements are in each category?"

### 8. Get ASVS requirements mapped to specific compliance frameworks.

**Example Use:**
- "Show me all ASVS requirements that map to PCI DSS"
- "What ASVS L2 requirements help with HIPAA compliance?"
- "Which controls satisfy GDPR Article 32?"

### 9. Analyze compliance gaps and identify missing controls.

**Parameters:**
- `frameworks` (array): List of frameworks to analyze
- `target_level` (number): Target ASVS level
- `implemented_requirements` (array, optional): List of already-implemented requirement IDs

**Example Use:**
- "We need PCI DSS and SOX compliance at L2. What are we missing?"
- "Gap analysis for HIPAA compliance, we've implemented requirements 2.1.1, 3.2.1, and 4.1.1"
- "Show compliance coverage for GDPR and ISO 27001"

### 9. Show which compliance frameworks a specific requirement satisfies.

**Parameters:**
- `requirement_id` (string): ASVS requirement ID

**Example Use:**
- "Which compliance frameworks does requirement 2.1.1 help with?"
- "What's the regulatory impact of implementing ASVS 8.3.4?"
- "Show me the compliance mapping for requirement 9.1.1"

## Usage Examples

Once configured in VS Code, you can ask Copilot Chat questions like:

**Security Requirements:**
- "What are the top priority security controls for a new web application?"
- "Show me all ASVS Level 1 authentication requirements"
- "Our application currently meets L1. What are the most critical requirements to reach L2?"
- "Find ASVS requirements related to cross-site scripting (XSS)"
- "What does ASVS say about password policies?"
- "Recommend security controls for a financial services API"

**Compliance Questions:**
- "We're building a payment processing app. Which ASVS requirements help us meet PCI DSS?"
- "Show me all HIPAA-related security controls in ASVS Level 1" (uses validated HIPAA mappings ✅)
- "What HIPAA Security Rule sections does ASVS V6.2.1 satisfy?" (validated mappings ✅)
- "Our company needs SOX and ISO 27001 compliance. What's the gap between L1 and L2?"
- "If I implement ASVS requirement 9.1.1, which compliance frameworks does it satisfy?"
- "We've implemented basic auth controls. Run a gap analysis for GDPR compliance at L2"
- "What percentage of HIPAA requirements do we currently meet?" (uses validated mappings ✅)

**Real-World Scenarios:**

- "Conduct security test using SECURITY-TEST-INTAKE.md"

- "Using nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md, pull the ASVS requirement checklist for Section 4's level/categories only. Don't start active testing yet."

- "Using nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md, test requirement [ID] only, within Section 6's guardrails. Show the raw request/response as evidence and a PASS/FAIL verdict."

- "Using nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md, generate/update the report at the Section 8 path from evidence already collected in runs/<run-id>/evidence/ — don't run any new tests."

- "Something looks wrong — [describe: 500 errors spiking / unexpected lockout]. Stop testing and follow Section 7 (Escalation) in nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md before continuing."

- "We need to dispute finding [F-0X]. Update Section 10 of nt-security-testing/runs/<run-id>/SECURITY-TEST-INTAKE.md as a disagreement-resolution rerun
(reason, disputed finding IDs, re-validation scope), then run the canonical prompt again — it will follow the rerun policy automatically.

- "We're a healthcare startup. Map our path from no security controls to HIPAA compliance"
- "Generate a compliance roadmap for a fintech app targeting PCI DSS Level 1"
- "We have L1 covered. Prioritize L2 requirements by compliance impact for PCI and SOX"
- "Which ASVS controls give us the most compliance coverage across multiple frameworks?"
- "Show me the 48 ASVS requirements that satisfy HIPAA Security Rule"

## Data Source

The server uses a cascading data source strategy for optimal performance:

1. **Local File (Primary)**: Loads from `data/asvs-5.0.0.json` - **54x faster** than remote fetch (2ms vs 110ms)
2. **Remote Fetch (Fallback)**: Downloads from official OWASP ASVS GitHub repository (ASVS 5.0.0) if local file unavailable
3. **Mock Data (Last Resort)**: Uses built-in representative requirements if both sources fail

To update the local ASVS data file:
```bash
npm run update-asvs
```

The data source used is indicated in the `_meta.data_source` field of all responses (`local`, `remote`, or `mock`).

### Security & Performance

The server implements **configurable security tiers** to match your deployment environment:

#### Security Constraint Tiers

Configure via `ASVS_SECURITY_TIER` environment variable:

| Constraint | CONSERVATIVE | BALANCED ⭐ | GENEROUS |
|------------|--------------|-------------|----------|
| File Size | 10 MB | **25 MB** | 50 MB |
| Query Length | 1000 chars | **2000 chars** | 5000 chars |
| Max Category Name | 200 chars | **500 chars** | 1000 chars |
| Max ID Length | 50 chars | **100 chars** | 200 chars |
| Search Results | 100 | **250** | 500 |
| Cache Entries | 5,000 | **10,000** | 20,000 |
| **Security Level** | Excellent | **Excellent** | Good |
| **Best For** | Public APIs | **Production** | Development |

**Default**: BALANCED tier (recommended for production)

**Additional Security Features:**
- ✅ **Rate Limiting**: Sliding window algorithm (100 requests/minute default)
- ✅ **TLS 1.2+**: Explicit TLS configuration with certificate validation
- ✅ **Data Integrity**: SHA-256 hash verification for remote data
- ✅ **Request Tracking**: UUID-based request IDs for log correlation
- ✅ **Structured Logging**: Winston with JSON format and rotation
- ✅ **Memory Safety**: Cache size limits and input validation

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

## Development

```bash
# Watch mode for development
npm run watch

# Build for production
npm run build

# Test the server
npm run dev

# Update ASVS data from OWASP repository
npm run update-asvs

# Run security tests
npm run test:phase1   # Logging and data integrity tests
npm run test:phase2   # Configuration and TLS tests
npm run test:phase3   # Rate limiting and request ID tests
npm run test:all      # Run all test suites
```

## Compliance Frameworks Supported

The server maps ASVS requirements to the following compliance frameworks:

### PCI DSS (Payment Card Industry Data Security Standard)
- Requirement sections: 3.x (Data Protection), 4.x (Encryption), 6.x (Secure Development), 8.x (Access Control), 10.x (Logging)
- Use case: Payment processing, e-commerce, financial services

### HIPAA (Health Insurance Portability and Accountability Act) ✅ Validated
- **Security Rule sections**: 164.308 (Administrative), 164.312 (Technical), 164.316 (Policies), 164.502/514 (Use & Disclosure)
- **Mappings**: 76 HIPAA requirements → 48 ASVS 5.0.0 controls (102 total mappings)
- **Coverage**: 94.7% of HIPAA requirements have full ASVS coverage
- **Use case**: Healthcare applications, medical records, patient data, PHI (Protected Health Information)
- **Validation**: All mappings verified against HIPAA Security Rule (45 CFR)
- **Documentation**: See `HIPAA_INTEGRATION.md` for complete details

### GDPR (General Data Protection Regulation)
- Articles: Article 32 (Security of Processing), Article 25 (Privacy by Design)
- Use case: EU data processing, personal data protection, privacy compliance

### SOX (Sarbanes-Oxley Act)
- IT General Controls (ITGC)
- Use case: Financial reporting, publicly traded companies, audit controls

### ISO 27001 (Information Security Management)
- Annex A controls across all domains
- Use case: Information security management systems, global security standards

## Compliance Mapping Features

**Bidirectional Mapping:**
- From ASVS → Compliance: "Which frameworks does this control satisfy?"
- From Compliance → ASVS: "Which ASVS controls help meet PCI DSS 8.2.3?"

**Gap Analysis:**
- Identify missing requirements for compliance
- Calculate coverage percentage per framework
- Prioritize gaps by criticality and compliance impact

**Multi-Framework Analysis:**
- Compare requirements across multiple frameworks simultaneously
- Find controls that satisfy multiple regulations
- Optimize compliance efforts by implementing high-impact controls

- **Level 1**: Applications where information disclosure or modification would not cause material harm
- **Level 2**: Applications that contain sensitive data requiring protection (most applications)
- **Level 3**: Critical applications performing high-value transactions or containing sensitive medical data

## Key Categories

- **V1**: Architecture, Design and Threat Modeling
- **V2**: Authentication
- **V3**: Session Management
- **V4**: Access Control
- **V5**: Validation, Sanitization and Encoding
- **V6**: Stored Cryptography
- **V7**: Error Handling and Logging
- **V8**: Data Protection
- **V9**: Communication
- **V10**: Malicious Code
- **V11**: Business Logic
- **V12**: Files and Resources
- **V13**: API and Web Service
- **V14**: Configuration

### Recent Enhancements

**Version 0.5.0 (2025-10-23) - Production Security Release:**
- ✅ **87% ASVS Level 1 Compliance** achieved (up from 66%)
- ✅ **Winston Structured Logging** with JSON format and rotation
- ✅ **Rate Limiting** with sliding window algorithm
- ✅ **TLS 1.2+** explicit configuration with certificate validation
- ✅ **Data Integrity** SHA-256 hash verification
- ✅ **Configurable Security Tiers** via environment variables
- ✅ **Request ID Tracking** with UUID for log correlation
- ✅ **Comprehensive Documentation**: SECURITY.md, SETUP_GUIDE.md, ENVIRONMENT_VARIABLES.md
- ✅ **Automated Test Suites** for all security features
- ✅ **Production Ready** status confirmed by security audit

**Version 0.4.0 (2025-10-22):**
- ✅ ASVS 5.0.0 integration (345 requirements, 17 chapters)
- ✅ Validated HIPAA Security Rule mappings (76 requirements, 102 mappings)
- ✅ Bidirectional HIPAA ↔ ASVS indexing for O(1) lookups
- ✅ Official CWE mappings (214 mappings)
- ✅ Official NIST 800-63B mappings (52 mappings)
- ✅ Comprehensive validation scripts for data integrity

## License

MIT

## Documentation

- **[README.md](README.md)** - This file - Quick start and overview
- **[SETUP_INSTRUCTION.md](SETUP_INSTRUCTION.md)** - GitHub Copilot / VS Code setup guide (`.vscode/mcp.json`, troubleshooting)
- **[SECURITY-TEST-INTAKE.md](SECURITY-TEST-INTAKE.md)** - Intake template to fill in before running a security test
- **[SECURITY-TEST-REPORT-TEMPLATE.md](SECURITY-TEST-REPORT-TEMPLATE.md)** - Report template for test output
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - How Copilot should run a test using the files above
- **[SECURITY.md](SECURITY.md)** - Comprehensive security documentation (13.5 KB)
- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Complete configuration reference
- **[HIPAA_INTEGRATION.md](HIPAA_INTEGRATION.md)** - Validated HIPAA mapping documentation
- **[PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md)** - Logging and data integrity implementation
- **[PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)** - Configuration and TLS implementation
- **[PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md)** - Rate limiting and request ID implementation

## Resources

- [OWASP ASVS Official Site](https://owasp.org/www-project-application-security-verification-standard/)
- [ASVS GitHub Repository](https://github.com/OWASP/ASVS) - Source for official mappings
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html) - Official HHS documentation
- [OpenCRE](https://www.opencre.org) - Additional compliance mappings and cross-references
