# Git Hooks Configuration Guide

## Overview

The git hooks in this directory (`pre-commit` and `post-checkout`) are designed to enforce worktree workflow patterns. They need to be configured for your specific project to work correctly.

## Configuration File

The hooks read configuration from `.worktree-config` in your project root.

### Setup Steps

1. **Copy the template:**
   ```bash
   cp .worktree-config.template .worktree-config
   ```

2. **Edit `.worktree-config` for your project:**
   ```bash
   # Example configuration
   WORKTREE_PATTERN="/.myproject-wt/"
   CREATE_WORKTREE_SCRIPT="scripts/create_worktree.py"
   ```

3. **Verify `.worktree-config` is in `.gitignore`:**
   The configuration file is project-specific and should not be committed to version control.

## Configuration Variables

### `WORKTREE_PATTERN` (Required)

The path pattern that identifies feature worktrees vs. the main worktree.

**How it works:**
- Feature worktrees MUST contain this pattern in their absolute path
- The main worktree must NOT contain this pattern
- The hooks use this to determine where commits/checkouts are allowed

**Examples:**

```bash
# Pattern: /.myproject-wt/
# Main worktree:    /Users/you/projects/myproject/
# Feature worktree: /Users/you/projects/myproject-wt-feature-123/
WORKTREE_PATTERN="/.myproject-wt/"

# Pattern: -wt-
# Main worktree:    /home/user/code/app/
# Feature worktree: /home/user/code/app-wt-bugfix/
WORKTREE_PATTERN="-wt-"

# Pattern: /worktrees/
# Main worktree:    /opt/project/
# Feature worktree: /opt/project/worktrees/feature-x/
WORKTREE_PATTERN="/worktrees/"
```

**Choosing a pattern:**
- Use a pattern that will ONLY match feature worktrees, never the main worktree
- Common patterns: `/<project>-wt/`, `-wt-`, `/wt/`
- Test it: Does your main worktree path contain this pattern? If yes, choose a different pattern.

### `CREATE_WORKTREE_SCRIPT` (Optional)

Path to the worktree creation script, shown in error messages.

```bash
# Relative to project root
CREATE_WORKTREE_SCRIPT="scripts/create_worktree.py"

# Or absolute path
CREATE_WORKTREE_SCRIPT="/usr/local/bin/create_worktree.py"
```

## Auto-Detection Fallback

If `.worktree-config` doesn't exist, the hooks try to auto-detect:

1. If the current worktree path contains `-wt-`, use that as the pattern
2. Otherwise, use `/.docimp-wt/` (default for this example project)

**Best practice:** Always create `.worktree-config` explicitly rather than relying on auto-detection.

## Testing Your Configuration

After setting up `.worktree-config`:

1. **In your main worktree:**
   ```bash
   # This should be blocked by pre-commit hook
   echo "test" >> README.md
   git add README.md
   git commit -m "test"
   # Expected: Commit is blocked
   ```

2. **In a feature worktree:**
   ```bash
   # Create a test feature worktree
   python3 actual-code/create_worktree.py test-config test-branch

   # This should be allowed
   cd ../<your-project>-wt-test-config/
   echo "test" >> README.md
   git add README.md
   git commit -m "test"
   # Expected: Commit succeeds
   ```

3. **Verify the pattern matches:**
   ```bash
   # Check main worktree path
   cd /path/to/main/worktree
   git rev-parse --show-toplevel
   # Should NOT contain WORKTREE_PATTERN

   # Check feature worktree path
   cd /path/to/feature/worktree
   git rev-parse --show-toplevel
   # Should contain WORKTREE_PATTERN
   ```

## Adapting Documentation References

Many files in this repository reference:
- `.docimp-wt` - The pattern used in the original DocImp project
- `DocImp` - The production project these patterns were extracted from

When adapting for your project:

1. **Replace in code/scripts:** Update actual references to use your `WORKTREE_PATTERN`
2. **In documentation:** Understand these are examples from the source project
3. **In diagrams:** Substitute your project name and pattern mentally

Example: If documentation shows `/Users/example/docimp-wt-feature/`,
for your project it would be `/Users/you/yourproject-wt-feature/` (if using `-wt-` pattern).

## Troubleshooting

### Hooks don't execute

```bash
# Check hooks are installed
ls -la .git/hooks/pre-commit .git/hooks/post-checkout

# Verify they're executable
chmod +x .git/hooks/pre-commit .git/hooks/post-checkout
```

### Hooks block everything / block nothing

```bash
# Check your configuration
cat .worktree-config

# Verify the pattern
current_worktree=$(git rev-parse --show-toplevel)
echo "Current worktree: $current_worktree"
echo "Contains pattern? (should be empty for main, non-empty for feature)"
echo "$current_worktree" | grep -o "<your-pattern>"
```

### Can't determine main vs feature worktree

```bash
# Manually test the pattern matching logic
current_worktree=$(git rev-parse --show-toplevel)
WORKTREE_PATTERN="/.myproject-wt/"  # Your pattern

if [[ ! "$current_worktree" =~ $WORKTREE_PATTERN ]]; then
    echo "This is the MAIN worktree (pattern not found)"
else
    echo "This is a FEATURE worktree (pattern found)"
fi
```

## Advanced Configuration

### Multiple Projects

If you work on multiple projects, each needs its own `.worktree-config`:

```
~/projects/project-a/.worktree-config   # WORKTREE_PATTERN="/.project-a-wt/"
~/projects/project-b/.worktree-config   # WORKTREE_PATTERN="/.project-b-wt/"
```

### Team Usage

For teams, consider:
- Documenting your team's `WORKTREE_PATTERN` in project README
- Providing a setup script that creates `.worktree-config`
- Including example `.worktree-config` in onboarding docs (but NOT in git)

### Customizing Hook Behavior

The hooks are bash scripts you can modify:
- `pre-commit`: Edit to change commit blocking logic
- `post-checkout`: Edit to change checkout blocking logic
- Both: Customize error messages, add logging, etc.

See the inline comments in each hook file for customization points.
