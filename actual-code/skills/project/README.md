# Project Skills

Project skills are project-specific skills stored in `.claude/skills/` within the project repository. They capture project-specific workflows, standards, and domain knowledge.

## Skills in This Collection

### git-workflow
**Purpose**: Git worktree-based workflow for parallel development with shared context. Defines commit practices, branch management, and worktree orchestration.

**When to use**: When creating/managing worktrees, working on parallel features, committing code, creating branches, or handling branch cleanup.

**Key concepts**:

**Commit workflow**:
- Incremental commits after each logical unit of work
- Every commit must leave program in good state (tests pass, code runs)
- Push early, push often
- Squash and merge keeps main clean while preserving detailed feature branch history

**Worktree-based development**:
- Each feature/issue gets own worktree (separate working directory)
- Enables parallel development in multiple Claude Code instances
- Shared context files (code reviews, planning docs) accessible across worktrees
- No context switching, no stashing changes

**Branch naming**:
- Descriptive names with issue numbers
- Good: `issue-260-display-consistency`
- Bad: `feature-1`, `my-branch`

**Nested issue branches**:
- Create sub-issue worktrees from feature branch (not main)
- PR back to feature branch for independent review
- Maintains clear history and organization

**Protecting main**:
- Git hooks block commits/checkouts in main worktree
- Feature worktrees unrestricted
- Educational error messages guide to correct workflow

**Worktree creation**:
```bash
python3 .claude/skills/git-workflow/scripts/create_worktree.py <name> <branch>
```

The script automates:
- Creating worktree with new branch
- Setting up symlinks to shared context
- Installing hooks if needed
- Creating per-worktree Python venv
- Copying direnv configuration

**Per-worktree isolation**:
- Each worktree gets own `.venv/` (no lock contention)
- Independent dependencies managed with uv
- Direnv integration for automatic activation

---

## Project Skills vs User Skills

| Aspect | Project Skills | User Skills |
|--------|---------------|-------------|
| **Location** | `.claude/skills/` in project repo | `~/.claude/skills/` globally |
| **Scope** | Project-specific workflows | Cross-project standards |
| **Examples** | git-workflow, database-schema, deploy-runbook | development-standards, testing, dependency-management |
| **Versioned** | Yes (committed to git) | No (user's local machine) |
| **Shared** | All team members | Individual developer |

## Usage

Project skills are automatically available when working in the project directory. They often integrate with:

- **Git hooks** - Enforce workflow standards
- **Custom agents** - Automate project-specific tasks
- **Shared context** - Code reviews, planning docs
- **Tool wrappers** - Scripts for common operations

### Installation

Project skills are typically symlinked to a shared location:

```bash
cd project/.claude/skills/
ln -s /path/to/custom-claude-skills/project-scope/myproject/git-workflow
```

Or committed directly to the repository:

```bash
cp -r /path/to/skill project/.claude/skills/git-workflow
git add .claude/skills/git-workflow
git commit -m "Add git-workflow skill"
```

### Integration with Worktrees

The git-workflow skill is particularly powerful in worktree setups:

**Shared across all worktrees**:
```
project-main/
├── .claude/skills/git-workflow -> /shared/skills/git-workflow

.project-wt/
├── issue-260/
│   └── .claude/skills/ -> ../../project-main/.claude/skills/
└── issue-243/
    └── .claude/skills/ -> ../../project-main/.claude/skills/
```

All worktrees share the same skill, ensuring consistent workflow across parallel development.

## Creating Project Skills

Follow the skill-creator guidance (see `../official/skill-creator/`) and consider:

**Good project skill candidates**:
- Deployment procedures specific to your infrastructure
- Database schema and query patterns
- API design patterns and conventions
- Testing strategies and fixtures
- Build and release workflows
- Architecture decision records (ADRs)

**Bad project skill candidates**:
- Generic development practices (use user skills instead)
- Frequently changing information (use regular docs)
- One-time setup instructions (use README)

## Examples from Production Use

The git-workflow skill emerged from managing a 17,000+ line polyglot codebase with:
- 4 parallel Claude Code instances in different worktrees
- Shared code reviews and planning docs
- Consistent workflow enforcement via hooks
- Per-worktree Python environments to avoid lock contention

This real-world usage shaped the skill's features:
- Helper scripts for worktree creation
- Hook installation automation
- Symlink setup for shared context
- Per-worktree venv creation
- Direnv integration

## Summary

Project skills capture project-specific workflows and domain knowledge, making Claude an effective team member who understands your project's unique requirements, follows your conventions, and knows your systems.

They work best when combined with:
- User skills for cross-project standards
- Custom agents for complex multi-step tasks
- Claude Code hooks for workflow enforcement
- Git hooks for branch protection

Well-designed project skills reduce onboarding time, maintain consistency, and encode institutional knowledge that might otherwise live only in team members' heads.
