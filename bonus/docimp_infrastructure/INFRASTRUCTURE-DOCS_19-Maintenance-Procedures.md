# Infrastructure Documentation: Maintenance Procedures

## Overview

This document provides step-by-step procedures for maintaining DocImp's development infrastructure. Regular maintenance ensures infrastructure stays current, secure, and functional as the project evolves.

Procedures cover git hooks, Node version upgrades, CLAUDE.md content management, worktree onboarding, dependency updates, and CI/CD configuration. Each procedure includes triggers (when to perform), steps, verification, and rollback instructions.

## 1. Adding a New Git Hook

### When to Add

**Triggers**:
- New quality check needs automated enforcement (e.g., commit message validation)
- Workflow protection required (e.g., prevent accidental main branch operations)
- Team requests standardized pre-commit/post-checkout behavior

**Examples**:
- `commit-msg`: Validate commit message format
- `pre-push`: Run full test suite before pushing
- `post-merge`: Auto-install dependencies after pulling changes

---

### Procedure

#### Step 1: Create Protected Hook

**File**: `.git/hooks/<hook-name>`

**Example** (commit-msg hook):
```bash
#!/bin/bash
# .git/hooks/commit-msg

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check commit message format (Conventional Commits)
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"; then
  echo -e "${RED}ERROR: Invalid commit message format${NC}"
  echo -e "${YELLOW}Expected format: <type>[optional scope]: <description>${NC}"
  echo -e "Examples:"
  echo -e "  feat(parser): add async function support"
  echo -e "  fix: resolve race condition in state manager"
  echo -e "  docs: update README with installation steps"
  exit 1
fi

echo "✓ Commit message format valid"
exit 0
```

**Make Executable**:
```bash
chmod +x .git/hooks/commit-msg
```

---

#### Step 2: Create Husky Dispatcher

**File**: `.husky/commit-msg`

```bash
#!/bin/bash
# .husky/commit-msg

# Call protected hook (only in main worktree)
if [ -f .git/hooks/commit-msg ]; then
  .git/hooks/commit-msg "$1"
fi

# Additional Husky-managed tasks (if needed)
# Example: npx commitlint --edit "$1"
```

**Make Executable**:
```bash
chmod +x .husky/commit-msg
```

---

#### Step 3: Test in Feature Worktree

```bash
# Create test worktree
python3 create_worktree.py test-commit-msg feature/test-commit-msg

cd ../.docimp-wt/test-commit-msg

# Configure Husky
git config extensions.worktreeConfig true
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
npx husky

# Test invalid commit message
git commit --allow-empty -m "invalid message"
# Expected: ERROR: Invalid commit message format

# Test valid commit message
git commit --allow-empty -m "test: validate commit-msg hook"
# Expected: ✓ Commit message format valid

# Clean up
cd ../../docimp
git worktree remove ../.docimp-wt/test-commit-msg
git branch -d feature/test-commit-msg
```

---

#### Step 4: Document in Husky README

**File**: `.husky/README.md`

```markdown
# Git Hooks Configuration

## Available Hooks

### pre-commit
- **Purpose**: Format and lint staged files
- **Tools**: lint-staged (Prettier + ESLint + Ruff)
- **Protected Hook**: `.git/hooks/pre-commit` (blocks main commits)

### post-checkout
- **Purpose**: Prevent branch checkouts in main worktree
- **Protected Hook**: `.git/hooks/post-checkout`

### commit-msg (NEW)
- **Purpose**: Validate commit message format (Conventional Commits)
- **Format**: `<type>[optional scope]: <description>`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Examples**:
  - `feat(parser): add async function support`
  - `fix: resolve race condition in state manager`
```

---

#### Step 5: Commit Changes

```bash
git add .git/hooks/commit-msg .husky/commit-msg .husky/README.md

git commit -m "feat(hooks): add commit-msg hook for Conventional Commits validation

Implements automatic commit message format validation:
- Enforces Conventional Commits format
- Validates type (feat, fix, docs, etc.)
- Provides helpful error messages with examples

Integration:
- Protected hook: .git/hooks/commit-msg
- Husky dispatcher: .husky/commit-msg
- Tested in feature worktree (test-commit-msg)

Documentation updated in .husky/README.md
"
```

---

### Verification

**Checklist**:
- [ ] Hook executes in main worktree
- [ ] Hook executes in feature worktrees
- [ ] Invalid input rejected with helpful error
- [ ] Valid input passes without issues
- [ ] Hook documented in `.husky/README.md`
- [ ] Changes committed to repository

---

### Rollback

**Remove Hook**:
```bash
# Remove files
rm .git/hooks/commit-msg
rm .husky/commit-msg

# Update README
# (Remove commit-msg section from .husky/README.md)

# Commit
git add .git/hooks/ .husky/
git commit -m "revert: remove commit-msg hook"
```

---

## 2. Updating Node Version

### When to Update

**Triggers**:
- Security vulnerabilities in current Node version
- New LTS release available (e.g., Node 26 LTS)
- Feature required from newer Node version
- Current version approaching end-of-life

**Check for Updates**:
```bash
# List available Node versions
nvm list-remote | grep "Latest LTS"

# Output:
v24.11.0   (Latest LTS: Iron)
v26.0.0    (Latest LTS: <codename>)
```

---

### Procedure

#### Step 1: Update .nvmrc

**File**: `.nvmrc`

```bash
# Before:
24.11.0

# After:
24.12.0  # Or new LTS version
```

**Commit Change**:
```bash
git add .nvmrc
git commit -m "chore: update Node to 24.12.0"
```

---

#### Step 2: Install New Node Version

**With Global Package Migration**:
```bash
# Install new version and migrate global packages
nvm install 24.12.0 --reinstall-packages-from=24.11.0

# Output:
Downloading and installing node v24.12.0...
...
Reinstalling global packages from v24.11.0...
...
@anthropic-ai/claude-code@1.2.3
typescript@5.7.2
npm@10.5.0
```

**Verify Globals Migrated**:
```bash
nvm use 24.12.0
npm list -g --depth=0

# Expected output includes:
# @anthropic-ai/claude-code@1.2.3
# typescript@5.7.2
```

---

#### Step 3: Reinstall Missing Globals (if any)

```bash
# If globals not migrated automatically
npm install -g @anthropic-ai/claude-code
npm install -g typescript

# Verify
npm list -g --depth=0
```

---

#### Step 4: Test Project Build

```bash
# Verify Node version
node --version  # Should output: v24.12.0

# Reinstall project dependencies
cd cli
npm ci  # Clean install from lockfile

# Build
npm run build

# Test
npm test

# Lint
npm run lint
```

---

#### Step 5: Update CI Configuration (if needed)

**File**: `.github/workflows/ci.yml`

```yaml
# .github/workflows/ci.yml
jobs:
  typescript-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: '24'  # Major version (auto-uses latest 24.x)
```

**Note**: Using major version (`'24'`) in CI auto-upgrades to latest 24.x patch. No change needed unless upgrading to Node 26.

---

### Verification

**Checklist**:
- [ ] `.nvmrc` updated and committed
- [ ] New Node version installed locally
- [ ] Global packages migrated (`npm list -g`)
- [ ] Project builds successfully (`npm run build`)
- [ ] Tests pass (`npm test`)
- [ ] CI uses correct Node version (check CI logs)

---

### Rollback

**Revert to Previous Version**:
```bash
# Restore old .nvmrc
git revert <commit-hash>  # Revert the "update Node" commit

# Switch Node version
nvm use 24.11.0

# Reinstall dependencies
cd cli
npm ci
npm run build
```

---

## 3. Updating CLAUDE.md

### When to Update

**Triggers**:
- New architectural patterns added (e.g., caching strategy)
- Major feature addition (e.g., workflow state tracking)
- Breaking changes to existing patterns
- Quarterly review (every 3 months)

**Size Check**:
```bash
wc -c CLAUDE.md
# 28456 CLAUDE.md  (28.5K / 40K = 71%)
```

**Warning Threshold**: 35K characters (87.5% of limit)

---

### Procedure

#### Step 1: Assess Content Addition

**Scenario A: Adding Small Section (< 2K chars)**

Add directly to CLAUDE.md:
```markdown
## New Feature

Brief description (1-2 paragraphs)

**Key Points**:
- Point 1
- Point 2

For details, see @docs/patterns/new-feature.md
```

**Scenario B: Adding Large Section (> 2K chars)**

Create external documentation file.

---

#### Step 2: Create External Documentation (if needed)

**File**: `docs/patterns/new-feature.md`

```markdown
# New Feature Pattern

## Overview

Detailed explanation...

## Implementation

\`\`\`typescript
// Code examples
\`\`\`

## Troubleshooting

Common issues...

## Summary

Key takeaways...
```

---

#### Step 3: Reference in CLAUDE.md

**Add Import Reference**:
```markdown
## New Feature

Brief high-level overview (2-3 paragraphs).

- @docs/patterns/new-feature.md
```

**Import Pattern**:
- `@docs/patterns/filename.md` - Relative to project root
- Maximum import depth: 5 hops
- Supporting files in `docs/patterns/` (public, committed to git)

---

#### Step 4: Check Size After Update

```bash
wc -c CLAUDE.md
# 29234 CLAUDE.md  (29.2K / 40K = 73%)
```

**If Exceeds 35K** (Warning Threshold):

1. Identify large sections (> 3K chars)
2. Move to `docs/patterns/`
3. Replace with brief summary + import reference
4. Verify size reduced below 35K

---

#### Step 5: Commit Changes

```bash
git add CLAUDE.md docs/patterns/new-feature.md

git commit -m "docs: add new feature pattern to CLAUDE.md

Adds documentation for new feature pattern:
- Brief overview in CLAUDE.md (500 chars)
- Detailed guide in docs/patterns/new-feature.md (4.2K)

CLAUDE.md size: 29.2K / 40K (73%)
"
```

---

### Maintenance Schedule

**Quarterly Review** (Every 3 Months):

1. Check CLAUDE.md size: `wc -c CLAUDE.md`
2. Review accuracy of existing content
3. Remove outdated information
4. Consolidate redundant sections
5. Move verbose sections to `docs/patterns/`
6. Verify import references still valid

**Target Size**: Keep below 35K (87.5%) for safety margin

---

### Verification

**Checklist**:
- [ ] CLAUDE.md size < 40K characters (strict limit)
- [ ] All `@docs/patterns/` references valid (files exist)
- [ ] No more than 5 levels of import depth
- [ ] External docs in `docs/patterns/` (committed to git)
- [ ] CLAUDE_CONTEXT.md NOT committed (gitignored)
- [ ] Changes committed with size noted in commit message

---

### Rollback

**Revert Changes**:
```bash
# Revert commit
git revert <commit-hash>

# Or restore from previous version
git checkout HEAD~1 -- CLAUDE.md docs/patterns/new-feature.md
```

---

## 4. Onboarding New Worktree

### When to Create

**Triggers**:
- Starting work on new feature (issue-based worktree)
- Parallel development of multiple features
- Testing breaking changes in isolation

**Worktree Naming Convention**: `issue-<number>` or `<feature-name>`

---

### Procedure

#### Step 1: Run create_worktree.py

**From Project Root**:
```bash
# Syntax: create_worktree.py <worktree-name> <branch-name>
python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-221 feature/issue-221-async-support

# Or with options:
python3 create_worktree.py issue-221 feature/issue-221-async-support \
  --source-branch main \
  --include-changes uncommitted
```

**Script Output**:
```
Creating worktree 'issue-221' with branch 'feature/issue-221-async-support'...

✓ Worktree created: ../.docimp-wt/issue-221
✓ Branch created: feature/issue-221-async-support
✓ Symlinks created (.claude, .docimp-shared, etc.)
✓ Husky configured
✓ npm dependencies installed
✓ Python virtual environment created (.venv/)

Next steps:
  cd ../.docimp-wt/issue-221
  git config extensions.worktreeConfig true
  git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
  npx husky
```

---

#### Step 2: Navigate to Worktree

```bash
cd ../.docimp-wt/issue-221
```

---

#### Step 3: Configure Git for Worktree

**Enable Per-Worktree Config**:
```bash
git config extensions.worktreeConfig true
```

**Set Husky Hooks Path**:
```bash
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
```

**Verify Config**:
```bash
git config --worktree --list
# Should include:
# core.hookspath=/Users/nik/Documents/Code/Polygot/.docimp-wt/issue-221/.husky/_
```

---

#### Step 4: Initialize Husky

**Generate Dispatcher Files**:
```bash
npx husky
```

**Verify Hooks**:
```bash
ls -la .husky/_/
# Should include:
# .husky/_/husky.sh
# .husky/_/h
```

---

#### Step 5: Allow direnv (if using)

**Load Environment**:
```bash
direnv allow
```

**Verify Interception**:
```bash
which python
# Should output: /path/to/.docimp-wt/issue-221/.direnv/bin/python

which pytest
# Should output: /path/to/.docimp-wt/issue-221/.direnv/bin/pytest
```

---

#### Step 6: Verify Setup

**Run Tests**:
```bash
# Python tests
uv run pytest -v

# TypeScript tests
cd cli
npm test
```

**Verify Git Hooks**:
```bash
# Test pre-commit hook
git commit --allow-empty -m "test: verify hooks"
# Should run lint-staged
```

---

### Verification

**Checklist**:
- [ ] Worktree created in `../.docimp-wt/<name>/`
- [ ] Branch created and checked out
- [ ] Symlinks present (`.claude/`, `.docimp-shared/`)
- [ ] Git config: `extensions.worktreeConfig = true`
- [ ] Git config: `core.hooksPath` points to `.husky/_`
- [ ] Husky initialized (`npx husky` succeeded)
- [ ] direnv allowed (if using direnv)
- [ ] Python tests pass (`uv run pytest -v`)
- [ ] TypeScript tests pass (`npm test`)
- [ ] Git hooks active (test with dummy commit)

---

### Cleanup (Removing Worktree)

**When Work Complete**:
```bash
# From main worktree
cd /path/to/main/docimp

# Remove worktree
git worktree remove ../.docimp-wt/issue-221

# Delete branch (if merged)
git branch -d feature/issue-221-async-support

# Or force delete (if not merged)
git branch -D feature/issue-221-async-support
```

---

## 5. Dependency Update Schedule

### Frequency Guidelines

| Dependency Type     | Check Frequency | Update Trigger                     |
|---------------------|-----------------|-------------------------------------|
| Security patches    | Weekly          | `npm audit` or CVE notification     |
| Patch versions      | Monthly         | Bug fixes, performance improvements |
| Minor versions      | Quarterly       | New features, non-breaking changes  |
| Major versions      | As needed       | Breaking changes, manual review     |

---

### Weekly: Security Audits

**Python**:
```bash
# Check for vulnerabilities (manual check)
uv pip list --outdated
# Review https://pypi.org/project/<package>/ for security advisories
```

**TypeScript**:
```bash
cd cli
npm audit

# Output:
# found 2 vulnerabilities (1 moderate, 1 high)
# run `npm audit fix` to fix them

# Auto-fix (non-breaking)
npm audit fix

# Manual fix (breaking changes)
npm audit fix --force  # Review changes before committing
```

---

### Monthly: Patch Updates

**Python**:
```bash
# Check outdated packages
uv pip list --outdated

# Update to latest patch version
uv add "anthropic>=0.85.1,<1.0.0"  # 0.85.0 → 0.85.1

# Regenerate lockfiles
uv pip compile pyproject.toml -o requirements.lock
uv pip compile pyproject.toml --extra dev -o requirements-dev.lock

# Test
uv run pytest -v

# Commit
git add pyproject.toml requirements.lock requirements-dev.lock uv.lock
git commit -m "chore(deps): update anthropic to 0.85.1 (patch)"
```

**TypeScript**:
```bash
cd cli
npm outdated

# Update patches (respects semver in package.json)
npm update

# Or update specific package
npm install typescript@latest

# Test
npm run build
npm test

# Commit
git add package.json package-lock.json
git commit -m "chore(deps): update TypeScript dependencies (patches)"
```

---

### Quarterly: Minor Updates

**Review Changes**:
1. Check changelogs for breaking changes
2. Test in isolated branch
3. Update code if necessary
4. Merge when stable

**Example**:
```bash
# Create test branch
git checkout -b deps-quarterly-update

# Update minor versions
cd cli
npm install eslint@latest  # 9.2.1 → 9.5.0

# Test
npm run lint
npm test

# If stable, merge
git checkout main
git merge deps-quarterly-update
```

---

### As Needed: Major Updates

**Process**:
1. Review migration guide
2. Create dedicated branch
3. Update dependencies incrementally (one at a time)
4. Fix breaking changes
5. Full test suite validation
6. Merge when all tests pass

**See**: INFRASTRUCTURE-DOCS_18-Critical-Dependencies-Constraints.md Section 5 (Breaking Change Scenarios)

---

## 6. CI/CD Maintenance

### When to Update Workflow

**Triggers**:
- New job required (e.g., security scanning)
- Workflow optimization (reduce CI time)
- Action version updates (security patches)
- New quality check (e.g., license compliance)

---

### Procedure: Adding New CI Job

**Example**: Add security scanning job

#### Step 1: Define New Job

**File**: `.github/workflows/ci.yml`

```yaml
# .github/workflows/ci.yml
jobs:
  # ... existing jobs ...

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

#### Step 2: Test Locally (if possible)

```bash
# Install Trivy
brew install aquasecurity/trivy/trivy

# Run scan locally
trivy fs .

# Expected output: List of vulnerabilities (if any)
```

---

#### Step 3: Commit and Push

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add Trivy security scanning job

Adds automated security vulnerability scanning:
- Scans file system for known vulnerabilities
- Uploads results to GitHub Security tab
- Runs on every push and PR

Trivy version: latest
"

git push
```

---

#### Step 4: Verify CI Execution

**Check GitHub Actions**:
1. Navigate to repository → Actions tab
2. Find latest workflow run
3. Verify new `security-scan` job appears
4. Check job logs for errors

---

### Updating GitHub Actions

**Monthly Review**:
```bash
# Check for action updates in workflow file
# Look for version tags: uses: actions/setup-node@v4
#                              (Check for v5 availability)

# Update action versions
# Before:
- uses: actions/checkout@v3

# After:
- uses: actions/checkout@v4
```

**Verify Compatibility**:
1. Review action changelog
2. Test in PR
3. Merge if stable

---

## Quick Reference

### Maintenance Checklist

#### Weekly
- [ ] Run `npm audit` (TypeScript security)
- [ ] Check `uv pip list --outdated` (Python security)
- [ ] Review CI failures (if any)

#### Monthly
- [ ] Update patch versions (Python + TypeScript)
- [ ] Review GitHub Actions for updates
- [ ] Check for new Ruff/ESLint rules

#### Quarterly
- [ ] Review CLAUDE.md size (`wc -c CLAUDE.md`)
- [ ] Update minor versions (dependencies)
- [ ] Review git hooks (add/remove as needed)
- [ ] Audit worktree health (`git worktree list`)

#### As Needed
- [ ] Node version updates (.nvmrc)
- [ ] Major dependency updates (breaking changes)
- [ ] New git hooks (workflow changes)
- [ ] CI/CD job additions (new quality checks)

---

### Common Commands

```bash
# Git Hooks
chmod +x .git/hooks/<hook-name>            # Make hook executable
npx husky                                   # Regenerate Husky dispatchers

# Node Version
nvm install <version> --reinstall-packages-from=<old-version>
node --version                              # Verify active version

# CLAUDE.md
wc -c CLAUDE.md                             # Check size (< 40K)

# Worktree
python3 create_worktree.py <name> <branch>  # Create worktree
git worktree list                           # List worktrees
git worktree remove <path>                  # Remove worktree

# Dependencies
uv pip list --outdated                      # Python outdated packages
npm outdated                                # TypeScript outdated packages
npm audit                                   # Security vulnerabilities

# CI/CD
# (Edit .github/workflows/ci.yml, commit, push)
```

---

## Troubleshooting

### Issue: Hook Not Executing in Worktree

**Symptom**: Git hook doesn't run in feature worktree

**Cause**: `core.hooksPath` not configured per-worktree

**Solution**:
```bash
cd /path/to/worktree

# Enable per-worktree config
git config extensions.worktreeConfig true

# Set hooks path
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"

# Regenerate Husky
npx husky

# Test
git commit --allow-empty -m "test: verify hooks"
```

---

### Issue: Node Version Not Updating

**Symptom**: `node --version` shows old version after `.nvmrc` update

**Cause**: Shell not reloading nvm

**Solution**:
```bash
# Manually load new version
nvm use

# Or specify version
nvm use 24.12.0

# Verify
node --version  # Should show 24.12.0

# Make default (optional)
nvm alias default 24.12.0
```

---

### Issue: CLAUDE.md Exceeds 40K

**Symptom**: `wc -c CLAUDE.md` shows > 40,000 characters

**Cause**: Too much detailed content in main file

**Solution**:
```bash
# Identify large sections (manual review)
# Example: "Testing Strategy" section is 5K chars

# Move to external file
# Create docs/patterns/testing-strategy.md with detailed content

# Update CLAUDE.md
# Replace 5K detailed section with:
# "Brief overview (500 chars)
#  - @docs/patterns/testing-strategy.md"

# Verify size
wc -c CLAUDE.md  # Should be < 40K now
```

---

## Summary

Regular maintenance ensures DocImp's infrastructure stays healthy:

- **Git Hooks**: Add when workflow protection needed, test in feature worktree
- **Node Updates**: Update .nvmrc, migrate global packages, test build/tests
- **CLAUDE.md**: Keep under 40K chars, move detailed content to `docs/patterns/`
- **Worktrees**: Use `create_worktree.py`, configure git, initialize Husky
- **Dependencies**: Weekly security, monthly patches, quarterly minors, cautious majors
- **CI/CD**: Add jobs as needed, update actions monthly, verify execution

**Next Steps**: See `INFRASTRUCTURE-DOCS_20-Security-Isolation.md` for security practices and environment isolation strategies.
