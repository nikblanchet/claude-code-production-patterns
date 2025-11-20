# Quick Start: See These Patterns in Action

This guide demonstrates all patterns in 15-20 minutes total.

## Prerequisites

- Claude Code installed
- This repository cloned
- Git worktrees supported (Git 2.5+)

## 1. Verify Installation (2 minutes)

### Check What's Already Configured

**Git Hooks:**
```bash
# Check if hooks exist in this repo
ls -la .git/hooks/
# You should see: pre-commit, post-checkout, etc.
```

**Claude Code Hooks:**
```bash
# View configured hooks
cat .claude/settings.local.json
# Look for: "hooks" section with SessionStart, etc.
```

**Skills and Agents:**
```bash
# Check what's available
ls actual-code/skills/user/
ls actual-code/agents/
```

**Success:** You can see the infrastructure exists and is configured.

---

## 2. Test Git Hooks (3 minutes)

**Demonstrates:** Pre-commit hook protecting main worktree.

### Try to Commit on Main (Should Block)

```bash
# In the main worktree on main branch
echo "test" >> README.md
git add README.md
git commit -m "test"
```

**Expected Result:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ COMMIT BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cannot commit on main branch in the main worktree.

The main worktree is reserved for reference and worktree management.
All development work should be done in feature worktrees.
```

**Clean up:**
```bash
git reset HEAD README.md
git checkout README.md
```

**Success:** Hook blocked the commit with clear message.

---

## 3. Create a Worktree (5 minutes)

**Demonstrates:** create_worktree.py script creating isolated development environment.

### Run the Script

```bash
# Create a test feature worktree
python3 actual-code/create_worktree.py test-demo test-branch
```

**What Happens:**
1. Script checks for uncommitted changes
2. Creates new git worktree
3. Sets up symlinks for shared config
4. Installs dependencies (if needed)
5. Prints success message with path

**Expected Output:**
```
Creating worktree 'test-demo' with branch 'test-branch'...
✓ Worktree created at: /path/to/project-wt-test-demo/
✓ Dependencies installed
✓ Configuration symlinked

To switch to this worktree:
  cd /path/to/project-wt-test-demo/
```

### Verify It Works

```bash
# List all worktrees
git worktree list

# You should see:
# /path/to/main/worktree        abcd123 [main]
# /path/to/project-wt-test-demo efgh456 [test-branch]

# Try committing in the feature worktree
cd ../project-wt-test-demo/  # Adjust path as shown in output
echo "test" >> README.md
git add README.md
git commit -m "test commit in feature worktree"
# This should SUCCEED (not blocked)
```

### Clean Up

```bash
cd /path/to/main/worktree
git worktree remove ../project-wt-test-demo
git branch -D test-branch
```

**Success:** Worktree created, commits allowed there but not in main, cleaned up successfully.

---

## 4. Verify Skills Installation (3 minutes)

**Demonstrates:** Skills are available and properly structured.

### Check Skill Files

```bash
# View available skills
ls -la actual-code/skills/user/

# Should show:
# cli-ux-colorful/
# dependency-management/
# development-standards/
# exhaustive-testing/
# handle-deprecation-warnings/
```

### Read a Skill

```bash
# View the development-standards skill
cat actual-code/skills/user/development-standards/skill.md | head -50
```

**Expected:** You see a comprehensive skill definition with clear "when to use" guidance.

### Install Skills (if not already)

```bash
# Copy skills to Claude Code user directory
mkdir -p ~/.claude/skills/user/
cp -r actual-code/skills/user/* ~/.claude/skills/user/
```

**Success:** Skills are properly formatted and ready to use.

---

## 5. Verify Agents (3 minutes)

**Demonstrates:** Agents are defined with clear prompts and tools.

### Check Agent Definitions

```bash
# View available agents
ls -la actual-code/agents/project/
ls -la actual-code/agents/user/

# Should show:
# project/code-reviewer.md
# user/python-313-conventions.md
```

### Read an Agent

```bash
# View the code-reviewer agent
cat actual-code/agents/project/code-reviewer.md | head -100
```

**Expected:** You see:
- Agent description
- When to use it
- Tools it has access to
- Clear task definition

### Install Agents (if not already)

```bash
# Copy agents to Claude Code user directory
mkdir -p ~/.claude/agents/user/
mkdir -p ~/.claude/agents/project/
cp actual-code/agents/user/*.md ~/.claude/agents/user/
cp actual-code/agents/project/*.md ~/.claude/agents/project/
```

**Success:** Agents are properly defined and installable.

---

## 6. Check Claude Code Hooks (2 minutes)

**Demonstrates:** Session start hooks and permission approvals configured.

### View Hook Configuration

```bash
cat .claude/settings.local.json
```

**Look for:**

1. **SessionStart hook** (lines ~10-20):
   ```json
   "SessionStart": [
     {
       "hooks": [
         {
           "type": "command",
           "command": "uv run python .claude/hooks/on_session_start.py",
           ...
         }
       ]
     }
   ]
   ```

2. **Permissions** (lines ~30+):
   ```json
   "permissions": {
     "allow": [
       "Bash(test:*)",
       "Bash(uv run pytest:*)",
       ...
     ]
   }
   ```

**Success:** Hooks and permissions are configured for this project.

---

## Summary: What You've Verified

After completing this guide, you've seen:

- Git hooks - Protect main worktree (tested live)
- Worktree script - Create isolated environments (ran successfully)
- Skills - Properly defined and installable (examined structure)
- Agents - Ready to use (examined definitions)
- Claude hooks - Configured for workflow automation (verified config)

## Total Time: ~15-20 minutes

All patterns are functional and ready to use. This repository contains working, production-tested infrastructure extracted from a large-scale project.

## Next Steps

To adopt these patterns in your own project:
1. Read [ADVANCED_PATTERNS.md](../ADVANCED_PATTERNS.md) for detailed implementation guidance
2. Follow [actual-code/hooks/CONFIGURATION.md](../actual-code/hooks/CONFIGURATION.md) to customize for your project
3. Review [docs/PERFORMANCE.md](../docs/PERFORMANCE.md) for optimization strategies
