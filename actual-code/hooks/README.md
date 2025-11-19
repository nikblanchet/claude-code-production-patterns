# Git Hooks: Worktree Protection Pattern

This directory contains the actual Git hook implementations from the docimp project, demonstrating a two-tier hook architecture for worktree-based development workflows.

## Architecture Overview

### Two-Tier Hook System

```
User Action (git commit/checkout)
         �
    Husky Hooks (.husky/)
         �
    Git Hooks (.git/hooks/)
         �
    Lint-staged (pre-commit only)
```

**Layer 1: Git Hooks** (in `.git/hooks/`)
- Core worktree protection logic
- Blocks commits/checkouts on main branch in main worktree
- Color-coded error messages with actionable guidance

**Layer 2: Husky Hooks** (in `.husky/`)
- Calls Git protection hooks
- Adds lint-staged integration (pre-commit)
- Manages hook installation via npm

## Hook Files

### Git Hooks

**`pre-commit`**
- Blocks commits on main branch when in main worktree
- Uses path pattern matching: `/.docimp-wt/` identifies feature worktrees
- Provides educational error message with worktree creation instructions
- Bypass: `git commit --no-verify`

**`post-checkout`**
- Blocks branch checkouts in main worktree (main branch only)
- Automatically reverts to main branch if checkout attempted
- Ensures main worktree stays clean and on main branch

### Husky Hooks

**`husky/pre-commit`**
- Delegates to Git pre-commit hook first
- Runs lint-staged for automatic formatting/linting
- Exits if protection hook fails

**`husky/post-checkout`**
- Delegates to Git post-checkout hook
- Passes through all arguments

### Configuration

**`config/lint-staged-config.json`**
- TypeScript/JavaScript: Prettier + ESLint
- Python: Ruff format + Ruff check

## Worktree Protection Pattern

### Problem
Developers accidentally commit to main branch or checkout feature branches in the main worktree, causing:
- Dirty main worktree state
- Confusion about which worktree is active
- Risk of pushing unintended changes

### Solution
Two-layer enforcement:

1. **Pre-commit hook**: Detects main worktree by path pattern, blocks commits to main
2. **Post-checkout hook**: Detects main worktree, blocks branch checkouts, auto-reverts to main

### Path Pattern Detection

```bash
current_worktree=$(git rev-parse --show-toplevel)

# Feature worktrees: /path/to/.docimp-wt/issue-260/
# Main worktree: /path/to/docimp/
if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # We're in main worktree - block the action
fi
```

### Error Message Design

```

 COMMIT BLOCKED


Cannot commit on main branch in the main worktree.

The main worktree is reserved for reference and worktree management.
All development work should be done in feature worktrees.

To create a new feature worktree:
  python3 actual-code/create_worktree.py <worktree-name> <branch-name>

Example:
  python3 actual-code/create_worktree.py issue-260 issue-260-fix-bug

If you need to bypass this check (for maintenance only):
  git commit --no-verify
```

## Installation

### Git Hooks (Manual)
```bash
# From the actual-code/hooks/ directory, copy to .git/hooks/
cp pre-commit .git/hooks/pre-commit
cp post-checkout .git/hooks/post-checkout

# Make executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-checkout
```

### Husky Hooks (npm)
```bash
# Copy to .husky/
cp husky/pre-commit .husky/pre-commit
cp husky/post-checkout .husky/post-checkout

# Install Husky
npm install --save-dev husky
npx husky install

# Make executable
chmod +x .husky/pre-commit
chmod +x .husky/post-checkout
```

### Lint-staged Configuration
Add to `package.json`:
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

## Benefits

1. **Enforced Workflow**: Impossible to accidentally commit to main in main worktree
2. **Educational Errors**: Clear guidance on correct workflow, not just blocking
3. **Automatic Formatting**: Pre-commit hook formats/lints staged files
4. **Clean Main Worktree**: Always stays on main branch, never dirty
5. **Parallel Development**: Feature worktrees unrestricted, can commit to any branch

## Technical Details

### Hook Execution Order

**Pre-commit**:
1. Husky hook runs (`npx husky install` sets this up)
2. Calls Git hook via `$GIT_COMMON_DIR/hooks/pre-commit`
3. Git hook checks worktree path pattern
4. If passed, runs `npx lint-staged`

**Post-checkout**:
1. Husky hook runs
2. Calls Git hook via `$GIT_COMMON_DIR/hooks/post-checkout`
3. Git hook checks worktree path + branch
4. If blocked, auto-reverts to main

### Color Codes

```bash
RED='\033[0;31m'      # Error messages
YELLOW='\033[1;33m'   # Warnings
NC='\033[0m'          # Reset
```

### Git Commands Used

```bash
git symbolic-ref --short HEAD          # Get current branch name
git rev-parse --show-toplevel          # Get worktree root path
git rev-parse --git-common-dir         # Get .git directory path (for Husky)
git checkout main                      # Auto-revert in post-checkout
```

## Related Patterns

- **Worktree Structure Pattern**: See `diagrams/worktree-structure.md`
- **Claude Config Pattern**: See `claude-config-pattern-section.md`
- **Direnv Pattern**: See `direnv-pattern-section.md`

## Notes

- **No pre-push hook**: The docimp project only uses pre-commit and post-checkout hooks
- **Bypass available**: `--no-verify` flag allows maintenance commits when needed
- **Worktree-aware**: Detection based on path pattern, works across all worktrees
- **Color support**: ANSI color codes work in most modern terminals
