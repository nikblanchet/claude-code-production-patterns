# Infrastructure Documentation: Git Hooks

## Overview

DocImp uses a **two-layer git hook system** to protect the main branch while enabling flexible development in feature worktrees:

1. **Protected hooks** (`.git/hooks/`) - Main worktree branch protection
2. **Husky hooks** (`.husky/`) - Code quality enforcement (all worktrees)

**Key Innovation**: Hooks determine worktree identity via path pattern matching (`/.docimp-wt/`), not fragile git metadata.

## Architecture

### Worktree Model

```
docimp/  (main worktree)
├── .git/
│   └── hooks/
│       ├── pre-commit      # Blocks main commits
│       └── post-checkout   # Blocks branch checkouts
└── .husky/
    ├── pre-commit          # Dispatcher (calls protected hook + lint-staged)
    ├── post-checkout       # Dispatcher (calls protected hook)
    └── _/                  # Per-worktree generated files (gitignored)

.docimp-wt/issue-260/  (feature worktree)
├── .git/                   # Worktree metadata (points to main .git/)
└── .husky/
    └── _/                  # Separate dispatcher instance
```

**Hooks Path Configuration**:
- Main worktree: Uses `.git/hooks/` (protected hooks)
- Feature worktrees: Uses `.husky/_` (Husky dispatchers, per-worktree config)

---

## Protected Hooks (Main Worktree Only)

### Pre-Commit Hook

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash
# pre-commit hook: Block commits on main branch in main worktree
#
# This hook prevents accidental commits to the main branch when working
# in the main repository worktree. Feature worktrees are unaffected.
#
# To bypass this check temporarily (for maintenance):
#   git commit --no-verify

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current branch
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)

# Only check if we're on main branch
if [ "$current_branch" != "main" ]; then
    exit 0
fi

# Get the absolute path of the current worktree
current_worktree=$(git rev-parse --show-toplevel)

# Get list of all worktrees and check if current is the main worktree
# The main worktree is the one that doesn't have "/.docimp-wt/" in its path
if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # We're in the main worktree - block the commit
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ COMMIT BLOCKED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Cannot commit on main branch in the main worktree.${NC}"
    echo ""
    echo "The main worktree is reserved for reference and worktree management."
    echo "All development work should be done in feature worktrees."
    echo ""
    echo "To create a new feature worktree:"
    echo "  python3 .claude/skills/git-workflow/scripts/create_worktree.py <worktree-name> <branch-name>"
    echo ""
    echo "Example:"
    echo "  python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-260 issue-260-fix-bug"
    echo ""
    echo "If you need to bypass this check (for maintenance only):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

# We're in a feature worktree - allow the commit
exit 0
```

**What It Does**:
1. Gets current branch name
2. If not on main, exits immediately (allows commit)
3. Gets worktree absolute path
4. Checks if path contains `/.docimp-wt/`
   - **No match** → Main worktree → Block commit with educational error
   - **Match** → Feature worktree → Allow commit
5. Provides escape hatch (`--no-verify`) for maintenance

**Key Decisions**:
- **Path-based detection**: Robust, maintainable, obvious
- **Educational error message**: Teaches correct workflow
- **Colored output**: High visibility in terminal
- **Branch-specific**: Only protects main, not all branches
- **Documented bypass**: Escape hatch for legitimate maintenance

**Example Output**:
```
$ git commit -m "Update README"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ COMMIT BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cannot commit on main branch in the main worktree.

The main worktree is reserved for reference and worktree management.
All development work should be done in feature worktrees.

To create a new feature worktree:
  python3 .claude/skills/git-workflow/scripts/create_worktree.py <worktree-name> <branch-name>

Example:
  python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-260 issue-260-fix-bug

If you need to bypass this check (for maintenance only):
  git commit --no-verify
```

### Post-Checkout Hook

**File**: `.git/hooks/post-checkout`

```bash
#!/bin/bash
# post-checkout hook: Block branch checkouts in main worktree
#
# This hook prevents checking out branches other than main when working
# in the main repository worktree. Feature worktrees are unaffected.
#
# The hook automatically reverts the checkout and switches back to main.

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hook parameters
prev_head=$1
new_head=$2
is_branch_checkout=$3

# Only act on branch checkouts (not file checkouts)
if [ "$is_branch_checkout" != "1" ]; then
    exit 0
fi

# Get the current branch after checkout
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)

# If we're on main, allow it
if [ "$current_branch" = "main" ]; then
    exit 0
fi

# Get the absolute path of the current worktree
current_worktree=$(git rev-parse --show-toplevel)

# Check if we're in the main worktree (not a feature worktree)
if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # We're in the main worktree and not on main branch - block this!
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ CHECKOUT BLOCKED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Cannot check out branch '$current_branch' in the main worktree.${NC}"
    echo ""
    echo "The main worktree should always remain on the main branch."
    echo "All development work should be done in feature worktrees."
    echo ""
    echo "To work on a feature branch, create a new worktree:"
    echo "  python3 .claude/skills/git-workflow/scripts/create_worktree.py <worktree-name> <branch-name>"
    echo ""
    echo "Example:"
    echo "  python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-260 issue-260-fix-bug"
    echo ""
    echo -e "${YELLOW}Automatically reverting to main branch...${NC}"
    echo ""

    # Revert back to main branch
    git checkout main

    exit 1
fi

# We're in a feature worktree - allow the checkout
exit 0
```

**What It Does**:
1. Gets hook parameters (prev_head, new_head, is_branch_checkout)
2. If not a branch checkout (e.g., file checkout), exits immediately
3. Gets current branch name after checkout
4. If on main, exits (allows checkout)
5. Gets worktree absolute path
6. Checks if path contains `/.docimp-wt/`
   - **No match** → Main worktree → Block checkout, auto-revert to main
   - **Match** → Feature worktree → Allow checkout

**Key Decisions**:
- **Auto-reverting**: Graceful recovery instead of just failing
- **Distinguishes branch vs file checkout**: Uses hook parameter `$3`
- **Same path detection pattern**: Consistency with pre-commit hook
- **Automatic remediation**: No user action needed (auto-switches back)

**Example Output**:
```
$ git checkout feature-xyz
Switched to branch 'feature-xyz'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ CHECKOUT BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cannot check out branch 'feature-xyz' in the main worktree.

The main worktree should always remain on the main branch.
All development work should be done in feature worktrees.

To work on a feature branch, create a new worktree:
  python3 .claude/skills/git-workflow/scripts/create_worktree.py <worktree-name> <branch-name>

Example:
  python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-260 issue-260-fix-bug

Automatically reverting to main branch...

Previous HEAD position was abc1234... Some commit
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
```

---

## Husky Integration (All Worktrees)

### Directory Structure

```
.husky/
├── pre-commit           # Dispatcher script
├── post-checkout        # Dispatcher script
├── _/                   # Generated per-worktree (gitignored)
│   ├── husky.sh         # Husky helper script
│   ├── pre-commit       # Generated dispatcher
│   └── post-checkout    # Generated dispatcher
└── README.md            # Setup instructions
```

### Pre-Commit Dispatcher

**File**: `.husky/pre-commit`

```bash
#!/usr/bin/env bash
. "$(dirname "$0")/_/husky.sh"

# Call protected hook first (main worktree protection)
HOOK_DIR="$(git rev-parse --show-toplevel)/.git/hooks"
if [ -f "$HOOK_DIR/pre-commit" ]; then
  "$HOOK_DIR/pre-commit" || exit 1
fi

# Run lint-staged for code quality (all worktrees)
npx lint-staged
```

**What It Does**:
1. Sources Husky helper script (sets up environment)
2. Calls protected hook (`.git/hooks/pre-commit`) **first**
   - If protected hook fails (main worktree on main branch), exits immediately
   - If protected hook succeeds (feature worktree), continues
3. Runs `lint-staged` for code quality checks

**Execution Flow**:

**Main Worktree (on main branch)**:
```
Attempt commit
↓
Husky pre-commit dispatcher
↓
Calls .git/hooks/pre-commit
↓
Protected hook blocks (exit 1)
↓
Dispatcher exits (lint-staged never runs)
```

**Feature Worktree**:
```
Attempt commit
↓
Husky pre-commit dispatcher
↓
Calls .git/hooks/pre-commit
↓
Protected hook allows (exit 0)
↓
Dispatcher continues to lint-staged
↓
lint-staged runs ruff + eslint on staged files
↓
If lint passes, commit succeeds
```

### Post-Checkout Dispatcher

**File**: `.husky/post-checkout`

```bash
#!/usr/bin/env bash
. "$(dirname "$0")/_/husky.sh"

# Call protected hook (main worktree protection)
HOOK_DIR="$(git rev-parse --show-toplevel)/.git/hooks"
if [ -f "$HOOK_DIR/post-checkout" ]; then
  "$HOOK_DIR/post-checkout" "$@"
fi
```

**What It Does**:
1. Sources Husky helper script
2. Calls protected hook (`.git/hooks/post-checkout`)
3. Passes all hook parameters (`$@` = prev_head, new_head, is_branch_checkout)

### Lint-Staged Configuration

**File**: `cli/package.json`

```json
{
  "lint-staged": {
    "*.{ts,js,mjs,cjs}": [
      "prettier --write",
      "eslint --fix"
    ],
    "*.py": [
      "ruff format",
      "ruff check --fix"
    ]
  }
}
```

**What It Does**:
- Runs Prettier → ESLint on staged TypeScript/JavaScript files
- Runs ruff format → ruff check on staged Python files
- Auto-fixes violations where possible
- Only processes **staged files** (not entire codebase)

**Example Execution**:
```
$ git add src/analyzer.py cli/src/commands.ts
$ git commit -m "Add new command"

✔ Preparing lint-staged...
✔ Running tasks for staged files...
  ✔ cli/src/commands.ts
    ✔ prettier --write
    ✔ eslint --fix
  ✔ src/analyzer.py
    ✔ ruff format
    ✔ ruff check --fix
✔ Applying modifications from tasks...
✔ Cleaning up temporary files...
[feature-branch abc1234] Add new command
 2 files changed, 45 insertions(+)
```

---

## Per-Worktree Hook Configuration

### Why Per-Worktree Config Is Needed

**Problem**: Git hooks are stored in `.git/hooks/`, which is **shared** across all worktrees. But we want:
- Main worktree: Protected hooks (block main commits)
- Feature worktrees: Quality hooks (lint-staged)

**Solution**: Use `git config --worktree` to set different `core.hooksPath` per worktree.

### Setup Process (Automated in create_worktree.py)

**Step 1: Enable Per-Worktree Config**
```bash
git config extensions.worktreeConfig true
```

This creates `.git/config.worktree` in each worktree (separate from `.git/config`).

**Step 2: Set Worktree-Specific Hooks Path**
```bash
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
```

This tells git to use `.husky/_/` instead of `.git/hooks/` for this worktree.

**Step 3: Generate Husky Dispatcher Files**
```bash
npx husky
```

This creates `.husky/_/husky.sh` and generates dispatcher wrappers.

### Configuration Files

**Main Worktree** (`.git/config`):
```ini
[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true
[extensions]
    worktreeConfig = true
```

**Feature Worktree** (`.git/config.worktree`):
```ini
[core]
    hooksPath = /path/to/.docimp-wt/issue-260/.husky/_
```

**Result**: Each worktree uses its own `.husky/_/` directory, with independent dispatcher instances.

---

## Hook Installation

### Automatic Installation (Recommended)

**Via create_worktree.py**:
```bash
python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-260 feature-branch
```

The script automatically:
1. Creates worktree
2. Configures per-worktree config
3. Sets hooks path to `.husky/_`
4. Runs `npx husky` to generate dispatchers

### Manual Installation

**If hooks are missing in main worktree**:
```bash
# Copy from repository to .git/hooks/
cp .claude/skills/git-workflow/scripts/hooks/pre-commit .git/hooks/
cp .claude/skills/git-workflow/scripts/hooks/post-checkout .git/hooks/
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-checkout
```

**If Husky not configured in feature worktree**:
```bash
cd /path/to/.docimp-wt/issue-260

# Enable per-worktree config
git config extensions.worktreeConfig true

# Set hooks path
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"

# Generate dispatchers
npx husky
```

---

## Testing Hooks

### Test Main Worktree Protection

**Test 1: Block commit on main**:
```bash
cd /path/to/docimp  # Main worktree
git checkout main
echo "test" >> README.md
git add README.md
git commit -m "Test commit"

# Expected: Commit blocked with error message
```

**Test 2: Block branch checkout**:
```bash
cd /path/to/docimp  # Main worktree
git checkout feature-xyz

# Expected: Checkout blocked, auto-reverted to main
```

**Test 3: Bypass protection (maintenance)**:
```bash
cd /path/to/docimp  # Main worktree
git checkout main
echo "maintenance" >> .gitignore
git add .gitignore
git commit --no-verify -m "Update gitignore"

# Expected: Commit succeeds (bypassed protection)
```

### Test Feature Worktree Hooks

**Test 4: Commit allowed in feature worktree**:
```bash
cd /path/to/.docimp-wt/issue-260
git checkout feature-branch
echo "test" >> README.md
git add README.md
git commit -m "Test commit"

# Expected: Commit succeeds (protected hook allows, lint-staged runs)
```

**Test 5: Branch checkout allowed**:
```bash
cd /path/to/.docimp-wt/issue-260
git checkout another-branch

# Expected: Checkout succeeds (protected hook allows)
```

**Test 6: Lint-staged auto-fixes**:
```bash
cd /path/to/.docimp-wt/issue-260

# Create file with formatting issues
cat > src/test.py <<EOF
def foo(  ):
    x=1
    return   x
EOF

git add src/test.py
git commit -m "Add test"

# Expected: ruff format auto-fixes, commit includes formatted version
```

---

## Troubleshooting

### Problem: Hooks not running

**Symptom**: Able to commit on main in main worktree

**Diagnosis**:
```bash
# Check if hooks exist
ls -la .git/hooks/

# Check if hooks are executable
ls -l .git/hooks/pre-commit
```

**Fix**:
```bash
# Reinstall hooks
cp .claude/skills/git-workflow/scripts/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Problem: Husky not running in feature worktree

**Symptom**: Lint-staged not running on commit

**Diagnosis**:
```bash
# Check hooks path config
git config --worktree --get core.hooksPath

# Expected: /path/to/.docimp-wt/issue-260/.husky/_
```

**Fix**:
```bash
# Configure per-worktree hooks
git config extensions.worktreeConfig true
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
npx husky
```

### Problem: lint-staged fails with "command not found"

**Symptom**: `npx lint-staged` fails in Husky hook

**Diagnosis**:
```bash
# Check if npm dependencies installed
ls cli/node_modules/

# Check if lint-staged exists
npx lint-staged --version
```

**Fix**:
```bash
# Install npm dependencies
cd cli
npm install
```

### Problem: Hooks run but don't block (always succeed)

**Symptom**: Protected hooks run but don't prevent commits

**Diagnosis**:
```bash
# Test hook directly
bash -x .git/hooks/pre-commit

# Check for bash errors
```

**Common Causes**:
- Incorrect path regex (should be `/.docimp-wt/`)
- Missing branch check (`git symbolic-ref --short HEAD`)
- Hook exits with 0 instead of 1

---

## Hook Bypass Scenarios

### When to Use --no-verify

1. **Maintenance commits in main worktree**:
   - Updating `.gitignore`
   - Fixing broken CI config
   - Emergency hotfixes

2. **Temporary hook issues**:
   - Hook script has bug
   - Lint-staged fails due to tooling issue

**Example**:
```bash
git commit --no-verify -m "Emergency fix: update CI config"
```

**Warning**: Use sparingly. Most commits should go through feature worktrees.

### When NOT to Use --no-verify

1. **Regular development work**: Use feature worktrees instead
2. **Code changes**: All code should be linted and tested
3. **Bypassing quality checks**: Fix the quality issues instead

---

## Summary

**Git Hook Architecture**:
- **Two layers**: Protected hooks (main worktree) + Husky hooks (all worktrees)
- **Path-based detection**: Robust, simple, maintainable
- **Per-worktree config**: Independent hook configuration per worktree
- **Educational errors**: Teach correct workflow through error messages

**Key Files**:
- `.git/hooks/pre-commit` - Blocks main commits in main worktree
- `.git/hooks/post-checkout` - Blocks branch checkouts in main worktree
- `.husky/pre-commit` - Dispatcher (calls protected hook + lint-staged)
- `.husky/post-checkout` - Dispatcher (calls protected hook)
- `cli/package.json` (lint-staged config) - Auto-formats/lints staged files

**Workflow Protection**:
- ✓ Main branch protected in main worktree (can't commit or checkout)
- ✓ Feature branches unrestricted in feature worktrees
- ✓ Lint-staged auto-fixes quality issues before commit
- ✓ Educational error messages guide developers
- ✓ Escape hatch available for legitimate maintenance

**Next Steps**: See `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md` for Claude Code permission configuration.
