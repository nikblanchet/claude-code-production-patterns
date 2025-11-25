# Git Hooks: Path-Based Worktree Detection

## Core Insight

Git hooks determine worktree identity via **path pattern matching** (e.g., `/{worktree-dir}/`), not fragile git metadata. This approach is robust, maintainable, and obvious: if the worktree path doesn't match the configured pattern, it's the main worktree. This simple check enables branch protection without relying on git configuration that can become inconsistent across worktrees.

## Implementation

### Pre-Commit Hook (Simplified)

```bash
#!/bin/bash
# Block commits on main branch in main worktree

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get current branch
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)

# Only check if we're on main branch
if [ "$current_branch" != "main" ]; then
    exit 0
fi

# Get the absolute path of the current worktree
current_worktree=$(git rev-parse --show-toplevel)

# Check if we're in the main worktree (not a feature worktree)
# Replace WORKTREE_PATTERN with your pattern (e.g., /.myproject-wt/)
if [[ ! "$current_worktree" =~ $WORKTREE_PATTERN ]]; then
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
    echo "If you need to bypass this check (for maintenance only):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

# We're in a feature worktree - allow the commit
exit 0
```

## Example Output

```
$ git commit -m "Update README"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ COMMIT BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cannot commit on main branch in the main worktree.

The main worktree is reserved for reference and worktree management.
All development work should be done in feature worktrees.

If you need to bypass this check (for maintenance only):
  git commit --no-verify
```

## When to Use

**✅ Use this pattern when:**
- You have a multi-worktree setup with a consistent path naming convention
- You need to protect the main branch in a specific worktree (typically the main one)
- You want educational error messages that guide developers to the correct workflow

**❌ Don't use this pattern when:**
- You have a single worktree workflow (standard git workflow)
- Your worktree paths don't follow a predictable naming pattern
- You need hooks that run identically across all worktrees
