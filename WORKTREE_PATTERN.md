# Git Worktree Orchestration for Parallel Claude Code Instances

## The Problem

Running multiple Claude Code instances on the same repository creates conflicts:
- Competing file modifications
- Inconsistent Claude Code configuration
- Manual coordination overhead
- Risk of corrupting main branch

**Real scenario:** Need 4 parallel instances working on different DocImp features simultaneously.

## The Solution: Retrofit Approach

This documents a **retrofit pattern** for existing repositories. For greenfield projects, see `GREENFIELD_NOTES.md` for a cleaner approach, but this shows how to adopt worktree orchestration incrementally on established projects.

### Architecture
```
[Paste your "Actual setup w/ worktree retrofit" diagram here]
```

**Key insight:** The `.shared/` directory with symlinks enables configuration consistency without git tracking conflicts.

## Implementation

### Step 1: Create Worktree Script

[Include create_worktree.py with inline comments explaining]:
- How it detects main branch location
- Why symlinks to `.shared/`
- How hooks are coordinated
```python
[Your actual code]
```

### Step 2: Git Hooks

[Include your actual hooks with explanations]:
```bash
# pre-commit hook (prevents direct commits to main)
[Actual code]
```

**Why this works:** Path-based branch detection - if the worktree path contains `/main/`, it's the main branch.

### Step 3: Setup Checklist
```bash
# 1. Copy create_worktree.py to project root
# 2. Create .shared/ directory
# 3. Move CLAUDE.md to .shared/
# 4. Run script for first worktree
python create_worktree.py issue-123
```

## What I Learned (Failure Modes)

### Problem: Symlink Confusion
**Symptom:** Claude Code can't find skills
**Cause:** Symlink path resolution in .claude/skills/
**Solution:** [Your solution]

### Problem: Hook Inconsistency  
**Symptom:** Some worktrees bypass hooks
**Cause:** [Your discovery]
**Solution:** [Your fix]

## When to Use This Pattern

✅ **Use when:**
- Multiple developers or Claude instances
- Repository > 10K lines
- Need branch protection
- Want configuration consistency

❌ **Don't use when:**
- Single developer projects
- Small codebases (< 5K lines)
- Simpler branch strategies work

## Retrofit vs. Greenfield

This pattern retrofits existing repos. For new projects, see `GREENFIELD_NOTES.md` for a cleaner initial structure that avoids the `.shared/` workaround.

**Why I'm showing the retrofit:** This is what I actually built and tested on 17K lines of production code. It works. The greenfield approach is theoretical optimization.

## Time Constraints

Given 3.5 hours for this take-home, I focused on:
- ✅ One pattern documented deeply with working code
- ✅ Real implementation from production use
- ✅ Honest about retrofit vs. optimal

**Would expand with more time:**
- Additional patterns (direnv, CLAUDE.md architecture)
- Video walkthrough
- Case study applying to different codebase
- Complete troubleshooting guide