# Infrastructure Documentation: Security & Isolation

## Overview

DocImp's security model balances developer productivity with protection against accidental damage, dependency vulnerabilities, and state corruption. This document details security boundaries, isolation strategies, threat models, and incident response procedures.

Security is implemented through multiple layers: git hooks (workflow protection), environment isolation (per-worktree independence), dependency management (lockfiles, whitelisting), and careful credential handling. Understanding these mechanisms helps developers work safely while maintaining flexibility.

## 1. Main Worktree Protection

### Threat Model

**Threats**:
- Accidental commits to `main` branch in production worktree
- Branch checkouts disrupting stable development environment
- Lost work due to unexpected git operations
- Confusion between feature worktrees and main worktree

**Consequences**:
- Broken CI/CD (direct commits bypass review)
- Corrupted main branch history
- Lost uncommitted work
- Difficult rollback scenarios

---

### Protection Mechanisms

#### Pre-Commit Hook (Main Worktree Only)

**File**: `.git/hooks/pre-commit`

**Purpose**: Block commits to `main` branch when in main worktree

**Implementation**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect worktree location
WORKTREE_PATH=$(git rev-parse --show-toplevel)

# Check if in main worktree (not in /.docimp-wt/ path)
if [[ ! "$WORKTREE_PATH" =~ /.docimp-wt/ ]]; then
  # Main worktree detected
  BRANCH=$(git rev-parse --abbrev-ref HEAD)

  if [ "$BRANCH" = "main" ]; then
    echo -e "${RED}ERROR: Direct commits to 'main' branch are blocked in the main worktree${NC}"
    echo -e "${YELLOW}Use a feature worktree for development:${NC}"
    echo -e "  python3 create_worktree.py <name> <branch>"
    echo ""
    echo -e "${YELLOW}To bypass (maintenance only):${NC}"
    echo -e "  git commit --no-verify"
    exit 1
  fi
fi

# Feature worktree: allow all operations
exit 0
```

**Bypass** (Maintenance Only):
```bash
# Emergency commits (use sparingly)
git commit --no-verify -m "hotfix: critical bug"

# Document why bypass was necessary
```

---

#### Post-Checkout Hook (Main Worktree Only)

**File**: `.git/hooks/post-checkout`

**Purpose**: Prevent branch checkouts (other than `main`) in main worktree

**Implementation**:
```bash
#!/bin/bash
# .git/hooks/post-checkout

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

WORKTREE_PATH=$(git rev-parse --show-toplevel)

# Only enforce in main worktree
if [[ ! "$WORKTREE_PATH" =~ /.docimp-wt/ ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)

  # Allow only 'main' branch
  if [ "$BRANCH" != "main" ]; then
    echo -e "${RED}ERROR: Branch checkouts are blocked in main worktree${NC}"
    echo -e "${YELLOW}Reverting to 'main' branch...${NC}"
    git checkout main
    exit 1
  fi
fi

exit 0
```

**Behavior**:
```bash
# In main worktree:
git checkout feature-branch
# Output: ERROR: Branch checkouts are blocked in main worktree
#         Reverting to 'main' branch...

# In feature worktree:
git checkout feature-branch
# ✓ Allowed
```

---

### Worktree Detection Logic

**Pattern Matching**:
```bash
WORKTREE_PATH=$(git rev-parse --show-toplevel)

if [[ "$WORKTREE_PATH" =~ /.docimp-wt/ ]]; then
  echo "Feature worktree detected"
else
  echo "Main worktree detected"
fi
```

**Path Examples**:
- Main worktree: `/Users/nik/Documents/Code/Polygot/docimp`
- Feature worktree: `/Users/nik/Documents/Code/Polygot/.docimp-wt/issue-221`

**Robust Detection**: Pattern `/.docimp-wt/` is unlikely to appear in main worktree path

---

### Documented Bypass Cases

**Legitimate Bypass Scenarios**:
1. **Hotfixes**: Critical bug requiring immediate commit to `main`
2. **Infrastructure updates**: Updating `.git/hooks/` or `.husky/`
3. **Lockfile regeneration**: Resolving merge conflicts in `uv.lock`
4. **CI configuration**: Emergency `.github/workflows/` fixes

**Process**:
```bash
# 1. Use --no-verify flag
git commit --no-verify -m "hotfix: description"

# 2. Document in commit message WHY bypass was necessary
git commit --no-verify -m "hotfix: resolve critical security vulnerability in anthropic

BYPASS REASON: Immediate deployment required, CVE-2024-XXXXX affects
production. Feature worktree unavailable due to network partition.

Tested locally with uv run pytest -v (all pass).
"

# 3. Create follow-up issue for proper review
# (If bypass was emergency measure)
```

---

## 2. Environment Isolation

### Threat Model

**Threats**:
- Dependency conflicts between worktrees
- Version mismatches (Python, Node)
- Global package pollution
- Shared state corruption

**Consequences**:
- Test failures due to wrong dependency versions
- Subtle bugs in one worktree affecting others
- Difficult debugging (non-reproducible environments)

---

### Per-Worktree Python Environment

#### Isolated .venv Directories

**Structure**:
```
docimp/                      # Main worktree
  .venv/                     # Python 3.13 environment

.docimp-wt/issue-221/        # Feature worktree
  .venv/                     # Independent Python 3.13 environment

.docimp-wt/issue-300/        # Another feature worktree
  .venv/                     # Separate Python 3.13 environment
```

**Creation** (Automatic via `create_worktree.py`):
```bash
# create_worktree.py automatically runs:
uv venv .venv
uv pip sync requirements-dev.lock
```

**Benefits**:
- No lock contention between worktrees
- Different dependency versions testable in parallel
- Clean environment per feature

---

#### direnv Scope Isolation

**File**: `.envrc` (per worktree)

**Scope**: Environment variables and PATH modifications apply only to current directory tree

**Example**:
```bash
# Terminal 1: Main worktree
cd /path/to/docimp
which python
# Output: /path/to/docimp/.direnv/bin/python

# Terminal 2: Feature worktree (simultaneously)
cd /path/to/.docimp-wt/issue-221
which python
# Output: /path/to/.docimp-wt/issue-221/.direnv/bin/python

# Different environments, no interference
```

**Verification**:
```bash
# Check Python environment isolation
cd /path/to/docimp
python -c "import sys; print(sys.executable)"
# /path/to/docimp/.venv/bin/python

cd /path/to/.docimp-wt/issue-221
python -c "import sys; print(sys.executable)"
# /path/to/.docimp-wt/issue-221/.venv/bin/python
```

---

### Per-Node-Version Global Packages

**Isolation Mechanism**: nvm installs global packages per Node version

**Structure**:
```
~/.nvm/versions/node/
  v24.11.0/
    bin/
      node
      npm
    lib/
      node_modules/
        @anthropic-ai/claude-code/  # Globals for Node 24.11.0

  v24.12.0/
    bin/
      node
      npm
    lib/
      node_modules/
        # Empty (fresh install, no globals yet)
```

**Implication**: Upgrading Node version (24.11.0 → 24.12.0) loses globals

**Solution**: Use `--reinstall-packages-from` flag
```bash
nvm install 24.12.0 --reinstall-packages-from=24.11.0
```

**Project Dependencies Unaffected**: `package.json` dependencies are per-project (not global)

---

### State Isolation (.docimp/state/)

#### Side-Car Git Repository

**Location**: `.docimp/state/.git`

**Purpose**: Transaction tracking for `docimp improve` session rollback

**Isolation**:
- **Separate from user's `.git/`**: Uses `--git-dir` and `--work-tree` flags
- **No interference**: Never touches user's main repository
- **Independent history**: Transaction commits separate from code commits

**Usage**:
```bash
# DocImp internal (user never runs directly)
git --git-dir=.docimp/state/.git --work-tree=. commit -m "Transaction: document add()"
```

**Security Benefit**: Rollback operations can't accidentally corrupt user's git history

---

## 3. Dependency Management Security

### Threat Model

**Threats**:
- Malicious packages in dependency tree
- Dependency confusion attacks
- Typosquatting (similar package names)
- Compromised package maintainer accounts
- Unlocked dependencies (version drift)

**Consequences**:
- Code execution by malicious packages
- Data exfiltration (API keys, source code)
- Supply chain compromise

---

### Lockfile Strategy

#### Python: uv.lock + requirements.lock

**Files**:
- `uv.lock`: uv's lockfile (full dependency graph with hashes)
- `requirements.lock`: Runtime dependencies (pip-compatible)
- `requirements-dev.lock`: Development dependencies

**Security Properties**:
- **Exact versions**: `anthropic==0.85.0` (not `>=0.85.0`)
- **Content hashes**: SHA-256 checksums verify package integrity
- **Reproducible**: Same lockfile → same packages across environments

**Verification**:
```bash
# Sync from lockfile (no network, local cache only)
uv pip sync requirements-dev.lock

# If package hash mismatch:
# ERROR: Hash mismatch for package 'anthropic'
#   Expected: abc123...
#   Got: def456...
# (Indicates package corruption or tampering)
```

---

#### TypeScript: package-lock.json

**Security Properties**:
- Exact versions: `"chalk": "5.3.0"` (not `"^5.3.0"`)
- Integrity hashes: `"integrity": "sha512-abc123..."`
- Locked dependency tree: Transitive dependencies fixed

**CI Enforcement**:
```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: npm ci  # Enforces lockfile (not `npm install`)
```

**`npm ci` vs `npm install`**:
- `npm ci`: Clean install from lockfile (deletes `node_modules/`, strict)
- `npm install`: Updates lockfile if `package.json` changed (looser)

**Use in CI**: Always `npm ci` for reproducibility

---

### Dependency Whitelisting (Claude Code)

**File**: `.docimp-shared/.claude/settings.local.json`

**Purpose**: Restrict Claude Code tool access to whitelisted commands

**Example**:
```json
{
  "allowedCommands": [
    "Bash(uv run pytest:*)",
    "Bash(uv run ruff:*)",
    "Bash(npm test:*)",
    "Bash(git status:*)",
    "Bash(git log:*)"
  ]
}
```

**Protection**:
- Claude Code cannot run arbitrary commands
- Only whitelisted patterns allowed
- Prevents accidental `rm -rf` or destructive operations

**Maintenance**: Add new commands as needed, but review for security implications

---

### No Bare pip (Enforced via direnv)

**File**: `.envrc`

**Implementation**:
```bash
# Block bare pip with helpful error
cat > .direnv/bin/pip <<'EOF'
#!/bin/bash
echo "ERROR: Use 'uv add <package>' or 'uv pip <command>' instead of bare 'pip'"
exit 1
EOF
chmod +x .direnv/bin/pip
```

**Rationale**:
- `pip` doesn't update lockfiles automatically
- `uv add` ensures `uv.lock` stays synchronized
- Prevents version drift from undocumented `pip install` commands

**Allowed**:
```bash
uv add "anthropic>=0.85.0,<1.0.0"  # ✓ Updates lockfile
uv pip sync requirements-dev.lock  # ✓ Syncs from lockfile
```

**Blocked**:
```bash
pip install anthropic  # ✗ ERROR: Use 'uv add' instead
```

---

### Regular Audits

**Python** (Manual):
```bash
# Check for outdated packages with known vulnerabilities
uv pip list --outdated

# Research each package:
# - Visit https://pypi.org/project/<package>/
# - Check for security advisories
# - Review changelog for vulnerability fixes
```

**TypeScript** (Automated):
```bash
cd cli
npm audit

# Output:
# found 0 vulnerabilities

# Or:
# found 2 vulnerabilities (1 moderate, 1 high)
#   Run `npm audit fix` to fix them
```

**Schedule**: Weekly security audits (see INFRASTRUCTURE-DOCS_19-Maintenance-Procedures.md)

---

## 4. Plugin System Security

### Threat Model

**Threats**:
- Malicious plugin code execution
- File system access abuse
- Network requests to exfiltrate data
- Path traversal attacks

**Consequences**:
- Source code theft
- Credential exfiltration
- System compromise

---

### NO Sandboxing (Intentional Design)

**Decision**: DocImp plugins run with **full Node.js access** (no sandboxing)

**Rationale**:
1. Sandboxing is complex (VM, worker threads, separate processes)
2. Sandboxes can be bypassed (security theater)
3. Plugins need real file system access (validate docstrings against source)
4. Trust boundary: Plugins are **user-controlled code**

**User Responsibility**: Only install trusted plugins

---

### Whitelist Approach

**Allowed Directories**:
- `./plugins/` (project plugins)
- `node_modules/` (npm-installed plugins)

**File Extensions**:
- `.js`, `.mjs`, `.cjs` only

**Enforcement**:
```typescript
// cli/src/plugins/PluginManager.ts
function validatePluginPath(pluginPath: string): boolean {
  const resolved = path.resolve(pluginPath);

  // Whitelist check
  const allowedDirs = [
    path.resolve('./plugins'),
    path.resolve('./node_modules'),
  ];

  const isInAllowedDir = allowedDirs.some((dir) =>
    resolved.startsWith(dir)
  );

  if (!isInAllowedDir) {
    throw new Error(`Plugin path not in whitelist: ${resolved}`);
  }

  // Extension check
  const ext = path.extname(resolved);
  if (!['.js', '.mjs', '.cjs'].includes(ext)) {
    throw new Error(`Invalid plugin extension: ${ext}`);
  }

  return true;
}
```

**Protection**:
- Path traversal blocked: `../../etc/passwd` rejected
- Arbitrary file execution blocked: `/tmp/malicious.js` rejected
- Only JavaScript allowed: `plugin.sh` rejected

---

### Symlink Resolution

**Attack**: Symlink in `plugins/` pointing to malicious file outside whitelist

**Defense**: Resolve symlinks before whitelist check
```typescript
import { realpathSync } from 'fs';

function validatePluginPath(pluginPath: string): boolean {
  const resolved = realpathSync(pluginPath);  // Resolves symlinks

  // Continue with whitelist check...
}
```

**Example**:
```bash
# Attempted attack:
ln -s /tmp/malicious.js plugins/evil.js

# Detection:
# realpathSync('plugins/evil.js') → '/tmp/malicious.js'
# Whitelist check fails: /tmp not in allowed directories
# Throws error: Plugin path not in whitelist
```

---

### Plugin Code Review

**Before Installing Third-Party Plugin**:

1. **Review source code**: Check `beforeAccept` and `afterWrite` hooks
2. **Check network requests**: Look for `fetch()`, `http.request()`, `axios` calls
3. **Inspect file operations**: `fs.readFile()`, `fs.writeFile()` outside expected paths
4. **Verify publisher**: npm package maintainer reputation

**Red Flags**:
- Obfuscated code
- Network requests to unknown domains
- File writes to `~/.ssh/`, `~/.aws/`, etc.
- `eval()` or `Function()` with external input

**Example Review**:
```javascript
// Plugin: validate-length.js
export function beforeAccept(docstring, item, config) {
  // ✓ No network requests
  // ✓ No file system operations
  // ✓ Only string manipulation
  // ✓ Returns PluginResult object

  const length = docstring.trim().length;
  return { accept: length >= 20 && length <= 500 };
}

// VERDICT: Safe to use
```

---

## 5. Credential Handling

### Threat Model

**Threats**:
- API keys committed to git
- Credentials in plain text config files
- Secrets exposed in CI logs
- Environment variables leaked in error messages

**Consequences**:
- Unauthorized API usage (cost, rate limits)
- Data breaches
- Account compromise

---

### .gitignore Strategy

**File**: `.gitignore`

**Philosophy**: **Do NOT gitignore credential patterns** (e.g., `*.key`, `*.pem`)

**Rationale**:
```gitignore
# NOTE on credential patterns (*.key, *.pem, credentials.json, etc.):
# We intentionally do NOT include these patterns. Adding them to .gitignore
# creates false security - they don't prevent "git add -f" and give developers
# a false sense of protection. Real credential protection comes from:
# - GitHub's secret scanning (enabled by default on public repos)
# - Pre-commit hooks (e.g., detect-secrets, gitleaks)
# - Developer security training
```

**Real Protection**:
1. **GitHub Secret Scanning**: Automatically detects committed secrets
2. **Pre-commit hooks** (optional): Use `detect-secrets` or `gitleaks`
3. **Education**: Train developers to never commit credentials

---

### Environment Variables

**Storage**: `.env` file (gitignored)

**`.gitignore` Entry**:
```gitignore
.env
.env.local
.env.*.local
```

**Usage**:
```bash
# .env (never commit)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Loading** (Python):
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env into os.environ

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError('ANTHROPIC_API_KEY not set')
```

**Loading** (TypeScript):
```typescript
import dotenv from 'dotenv';

dotenv.config();  // Loads .env into process.env

const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  throw new Error('ANTHROPIC_API_KEY not set');
}
```

---

### CI/CD Secrets

**GitHub Actions**: Use repository secrets (not environment variables in workflow files)

**Configuration**:
```yaml
# .github/workflows/ci.yml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - name: Run integration test
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          uv run pytest tests/integration/test_claude.py
```

**Setting Secrets**:
1. GitHub repo → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `ANTHROPIC_API_KEY`
4. Value: `sk-ant-xxxxxxxxxxxxx`

**Security**: Secrets masked in logs automatically by GitHub Actions

---

## 6. Access Controls

### Claude Code Permissions

**File**: `.docimp-shared/.claude/settings.local.json`

**Permission Categories**:

1. **Bash Commands**: Whitelist specific commands and patterns
2. **File Operations**: Glob, Grep, Read, Write paths
3. **Skills**: Allowed skill invocations
4. **Web Access**: WebFetch/WebSearch domains

**Example**:
```json
{
  "allowedCommands": {
    "Bash": [
      "uv run pytest:*",
      "git status:*",
      "npm test:*"
    ],
    "Read": [
      "./**",  // Project files
      "//Users/nik/Code/Polygot/.docimp-shared/**"  // Shared infrastructure
    ],
    "Write": [
      "./**"  // Project files only
    ],
    "WebFetch": [
      "domain:github.com",
      "domain:pypi.org"
    ]
  }
}
```

**Principle of Least Privilege**: Only grant permissions actually needed

---

### File System Boundaries

**Allowed Write Paths**:
- Project directory: `/Users/nik/Documents/Code/Polygot/docimp/`
- Shared infrastructure: `/Users/nik/Documents/Code/Polygot/.docimp-shared/`

**Prohibited Write Paths**:
- Home directory: `/Users/nik/` (too broad)
- System directories: `/usr/`, `/etc/`, `/var/`
- Sensitive paths: `~/.ssh/`, `~/.aws/`

**Enforcement**: Claude Code respects permission boundaries

---

## Quick Reference

### Security Checklist

#### Git Hooks
- [ ] Pre-commit hook blocks `main` commits in main worktree
- [ ] Post-checkout hook prevents branch changes in main worktree
- [ ] Hooks tested in both main and feature worktrees
- [ ] Bypass procedure documented (`git commit --no-verify`)

#### Environment Isolation
- [ ] Each worktree has separate `.venv/`
- [ ] direnv scope limited to worktree directory
- [ ] Node globals isolated per version
- [ ] `.docimp/state/.git` separate from user's `.git/`

#### Dependency Management
- [ ] Lockfiles committed (`uv.lock`, `package-lock.json`)
- [ ] CI uses `npm ci` (not `npm install`)
- [ ] Weekly security audits (`npm audit`, `uv pip list --outdated`)
- [ ] Bare `pip` blocked via `.envrc`

#### Plugin System
- [ ] Only install plugins from trusted sources
- [ ] Review plugin code before use
- [ ] Whitelist enforcement (`.plugins/`, `node_modules/`)
- [ ] Symlink resolution prevents path traversal

#### Credentials
- [ ] API keys in `.env` (gitignored)
- [ ] CI secrets in GitHub repository settings
- [ ] No credential patterns in `.gitignore` (false security)
- [ ] GitHub secret scanning enabled

#### Access Controls
- [ ] Claude Code permissions whitelisted
- [ ] File operations scoped to project directory
- [ ] Bash commands limited to safe operations

---

### Incident Response

#### Scenario: Credential Committed to Git

**Immediate Actions**:
1. Revoke credential (Claude API key, npm token, etc.)
2. Generate new credential
3. Update `.env` with new credential
4. Notify team (if public repository)

**Remove from Git History** (CAUTION):
```bash
# Use git-filter-repo (safer than filter-branch)
pip install git-filter-repo

# Remove file from entire history
git filter-repo --path .env --invert-paths

# Force push (DESTRUCTIVE)
git push --force
```

**Better**: Accept that credential is compromised, revoke it, move on. Git history rewriting is dangerous.

---

#### Scenario: Malicious Plugin Detected

**Immediate Actions**:
1. Remove plugin from `docimp.config.js`
2. Delete plugin file (`rm plugins/malicious.js`)
3. Review git history for commits by plugin (check `afterWrite` hook)
4. Scan system for indicators of compromise (IOCs)

**IOC Check**:
```bash
# Check for unexpected network connections
lsof -i -P | grep node

# Check for unexpected file modifications
find . -type f -mtime -1  # Files modified in last 24 hours

# Review git commits
git log --all --since="1 day ago" --oneline
```

---

## Troubleshooting

### Issue: Pre-commit hook not blocking commits

**Symptom**: Can commit to `main` branch in main worktree

**Cause**: Hook not executable

**Solution**:
```bash
chmod +x .git/hooks/pre-commit
git commit -m "test"  # Should now block
```

---

### Issue: direnv not isolating environments

**Symptom**: `which python` shows same path in different worktrees

**Cause**: direnv not loaded

**Solution**:
```bash
direnv allow  # In each worktree
```

---

### Issue: npm audit shows vulnerabilities

**Symptom**: `npm audit` reports vulnerabilities

**Solution**:
```bash
# Review vulnerabilities
npm audit

# Auto-fix (non-breaking)
npm audit fix

# Manual fix (breaking changes, use with caution)
npm audit fix --force

# Commit lockfile changes
git add package-lock.json
git commit -m "fix: resolve npm security vulnerabilities"
```

---

## Summary

DocImp's security model protects through multiple layers:

- **Workflow Protection**: Git hooks block accidental `main` commits/checkouts
- **Environment Isolation**: Per-worktree `.venv/`, direnv scope, Node version separation
- **Dependency Security**: Lockfiles, npm audit, uv pip list --outdated, no bare pip
- **Plugin System**: Whitelist approach, no sandboxing (user-controlled code), symlink resolution
- **Credentials**: `.env` files (gitignored), CI secrets, no credential patterns in `.gitignore`
- **Access Controls**: Claude Code permissions, file system boundaries

**Next Steps**: See `INFRASTRUCTURE-DOCS_21-Performance-Considerations.md` for optimization strategies and performance benchmarks.
