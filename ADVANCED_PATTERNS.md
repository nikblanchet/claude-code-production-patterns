# Advanced Claude Code Patterns: Production Infrastructure

## Overview

DocImp (17,000+ lines across Python, TypeScript, and JavaScript) required sophisticated infrastructure to coordinate 4 parallel Claude Code instances working simultaneously on different features. Managing multiple worktrees, keeping context synchronized, and ensuring workflow consistency posed unique challenges at scale.

This document presents battle-tested patterns that emerged from real production use, organized into two categories:

**Core Claude Code Features** (Scenario C Focus):
1. **Claude Code Hooks** - Event-driven workflow automation and permissions (`actual-code/hooks-config/`)
2. **Custom Agents** - Autonomous multi-step task execution (`actual-code/agents/`)
3. **Custom Skills** - Specialized knowledge and workflows (`actual-code/skills/`)

**Supporting Git Patterns**:
4. **Git Worktree Orchestration** - Path-based detection and automated hooks for branch protection
5. **CLAUDE.md Context Management** - External imports to overcome the 40KB character limit
6. **Direnv Tool Interception** - PATH manipulation for workflow enforcement with helpful errors

These patterns are designed for senior developers managing large codebases (100K+ lines) who need to coordinate multiple concurrent development workflows while maintaining strict quality gates. Each pattern includes working code, implementation guidance, and honest assessment of when to use (or avoid) the approach.

---

## Pattern 0: Claude Code Hooks, Agents, and Skills

Before diving into Git integration patterns, it's critical to understand Claude Code's native features for workflow automation. These are the foundation of Scenario C.

### Claude Code Hooks

**Location**: `actual-code/hooks-config/`

Event-driven shell commands that execute during Claude Code sessions. Unlike Git hooks (which respond to Git operations), Claude Code hooks respond to AI assistance events.

**Key hook types**:
- `user-prompt-submit`: Runs when user submits a prompt
- `tool-call`: Intercepts tool execution
- `session-start` / `session-end`: Lifecycle management

**Example use cases**:
```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "git status --short",
      "_comment": "Inject git status so Claude knows about uncommitted changes"
    }
  }
}
```

**Permissions system**:
- `allow`: Tools Claude can use freely
- `deny`: Tools blocked completely
- `ask`: Tools requiring user approval

**Critical distinction**: Claude Code hooks ≠ Git hooks
- Claude Code hooks: During AI sessions (prompt submit, tool calls)
- Git hooks: During Git operations (commit, push, checkout)

See [`actual-code/hooks-config/README.md`](actual-code/hooks-config/README.md) for comprehensive documentation.

---

### Custom Agents

**Location**: `actual-code/agents/`

Autonomous subprocesses that execute complex multi-step tasks with fresh eyes (no inherited conversation context).

**User Agents** (`actual-code/agents/user/`):
- **python-313-conventions**: Python 3.13+ modernization reviewer
  - 10 review dimensions: typing design, API contracts, async patterns, etc.
  - Complements automation (Ruff/mypy) with semantic review
  - Catches design patterns automation cannot check

**Project Agents** (`actual-code/agents/project/`):
- **code-reviewer**: Autonomous 11-dimension code review
  - Gathers requirements from PR, .planning/PLAN.md, linked issues
  - Checks previous review blockers (now acceptance criteria)
  - Classifies: Blocker, Important, Minor, Enhancement
  - Saves detailed review, posts summary to PR

**Agent vs Skill vs Hook**:
| Feature | Agents | Skills | Hooks |
|---------|--------|--------|-------|
| **What** | Autonomous subprocess | Knowledge in context | Event-driven command |
| **When** | Complex multi-step tasks | Provide expertise | Respond to events |
| **Context** | Isolated (fresh eyes) | Shared | Runs in shell |
| **Example** | Code reviewer | Git workflow standards | Inject git status |

See agent READMEs for invocation patterns and examples.

---

### Custom Skills

**Location**: `actual-code/skills/`

Specialized knowledge and workflows loaded into context when relevant.

**User Skills** (`actual-code/skills/user/` - 6 skills):
- **development-standards**: No emoji, modern features, thorough docs (CRITICAL)
- **exhaustive-testing**: Comprehensive test coverage
- **handle-deprecation-warnings**: Proactive API migration
- **dependency-management**: Library usage philosophy
- **cli-ux-colorful**: Terminal formatting
- **access-skill-resources**: Navigate skill bundles

**Official Skills** (`actual-code/skills/official/`):
- **skill-creator**: Guide for creating effective skills

**Project Skills** (`actual-code/skills/project/`):
- **git-workflow**: Git worktree-based workflow, commit standards, branch management

**When to use**:
- **Skill**: Provide domain knowledge (brand guidelines, API docs, workflows)
- **Agent**: Execute complex tasks (code review, test generation)
- **Hook**: Automate on events (inject context, enforce standards)

See skill READMEs for detailed instructions.

---

## Integration Pattern: Hooks + Skills + Agents

These features work together powerfully:

```
1. Hook triggers on event
   ↓
2. Skill provides domain knowledge
   ↓
3. Agent executes complex task
   ↓
4. Git hooks enforce quality gates
```

**Example workflow**:
1. User submits prompt → `user-prompt-submit` hook injects git status
2. `git-workflow` skill provides commit standards and worktree guidance
3. `code-reviewer` agent autonomously reviews changes across 11 dimensions
4. Git `pre-commit` hook blocks commit if tests fail or on wrong branch

This creates a robust quality framework where:
- Hooks ensure Claude has necessary context
- Skills provide consistent guidance
- Agents handle complex multi-step tasks
- Git hooks provide final safety net

---

## Pattern 1: Git Worktree Orchestration

This pattern provides the foundation for isolation, ensuring the main worktree remains stable while feature worktrees handle active development.

# Git Hooks: Path-Based Worktree Detection

## Core Insight

Git hooks determine worktree identity via **path pattern matching** (`/.docimp-wt/`), not fragile git metadata. This approach is robust, maintainable, and obvious: if the worktree path doesn't contain `/.docimp-wt/`, it's the main worktree. This simple check enables branch protection without relying on git configuration that can become inconsistent across worktrees.

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

**Use this pattern when:**
- You have a multi-worktree setup with a consistent path naming convention
- You need to protect the main branch in a specific worktree (typically the main one)
- You want educational error messages that guide developers to the correct workflow

**Don't use this pattern when:**
- You have a single worktree workflow (standard git workflow)
- Your worktree paths don't follow a predictable naming pattern
- You need hooks that run identically across all worktrees

### Implementation

See `actual-code/create_worktree.py` (1066 lines) for complete automation.
See `actual-code/hooks/` for hook implementations.

---

## Pattern 2: CLAUDE.md Context Management

Once worktrees are isolated, managing context becomes critical. Claude Code's 40KB limit on CLAUDE.md requires careful architecture to provide comprehensive documentation without hitting the ceiling.

# Claude Code Config Pattern: External Documentation Imports

## The 40KB Character Limit Challenge

**Constraint**: CLAUDE.md must stay under 40,000 characters

**Current size**: 27,792 bytes (27.8 KB) - 69.5% of limit used

**Check size**:
```bash
wc -c CLAUDE.md
# Output: 27792 CLAUDE.md
```

## The External Import Pattern

**Problem**: DocImp has complex architecture requiring extensive documentation. Inline documentation would exceed 40KB.

**Solution**: Use `@docs/patterns/*.md` imports for detailed explanations.

## CLAUDE.md Structure with Imports

```markdown
# CLAUDE.md

**Character Limit: 40.0k characters (absolute maximum) for CLAUDE.md specifically.**

## Commands

[Core commands documented inline: ~3KB]
docimp analyze ./src
docimp audit ./src
docimp plan ./src
docimp improve ./src

## Error Handling Architecture

**Three-layer pattern**: Core functions (throw) → Command wrappers (exit codes) → Entry point (process.exit)

- @docs/patterns/error-handling.md

## Dependency Injection Pattern

**Core Principle**: All dependencies passed as required parameters

- @docs/patterns/dependency-injection.md

## Transaction System Architecture

**Side-car Git repository** in `.docimp/state/.git` for rollback capability

- @docs/patterns/transaction-integration.md
```

## External Documentation Files

| File | Size | Purpose |
|------|------|---------|
| `error-handling.md` | 3.2 KB | Three-layer error pattern |
| `dependency-injection.md` | 4.1 KB | DI across Python/TypeScript |
| `testing-strategy.md` | 5.7 KB | Test organization |
| `transaction-integration.md` | 8.9 KB | Git-based rollback system |
| `session-resume.md` | 6.2 KB | Resume capability architecture |
| `workflow-state-management.md` | 12.4 KB | State tracking, schema versioning |
| **Total external** | **40.5 KB** | |

**Total Documentation**: 27.8KB (CLAUDE.md) + 40.5KB (external) = **68.3KB**

## How Auto-Loading Works

1. Claude Code reads CLAUDE.md on session start (27.8KB loaded)
2. When code mentions `@docs/patterns/error-handling.md`, Claude Code auto-loads it
3. Loaded content added to context window on-demand
4. Maximum import depth: 5 hops (prevents infinite loops)

### Example Structure

See `claude-config/` directory for working examples.

---

## Pattern 3: Direnv Tool Interception

The final piece ensures workflow consistency across all worktrees by intercepting tool calls and enforcing project standards through PATH manipulation and educational error messages.

# Direnv Pattern: Tool Interception with Helpful Errors

## What Direnv Tool Interception Does

When you `cd` into a worktree, direnv automatically:

1. **Intercepts Python tools** (`python`, `pip`, `pytest`, `ruff`, `mypy`) → redirects to `uv run`
2. **Blocks dangerous operations** (`pip` with helpful error message)
3. **Injects PATH** with highest priority wrapper scripts

## PATH Injection Mechanism

**Before direnv**:
```
PATH=/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

**After direnv executes `.envrc`**:
```
PATH=.direnv/bin:/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

Shell searches PATH left-to-right, finds `.direnv/bin/python` first (wrapper script).

## Actual .envrc Code: Python Interceptor

```bash
#!/bin/bash
# Intercept bare python calls and redirect to uv
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running python from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv run python" >&2
fi

echo "→ Redirecting to: uv run python" >&2
# Remove .direnv/bin from PATH to prevent recursion
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run python "$@"
```

## Actual .envrc Code: pip Interceptor (Blocks with Error)

```bash
#!/bin/bash
# Block bare pip, show helpful error
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running pip from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv pip ..." >&2
  echo "" >&2
fi

echo "✗ Bare 'pip' detected!" >&2
echo "" >&2
echo "Instead of 'pip install <package>', use:" >&2
echo "  uv add <package>" >&2
echo "" >&2
echo "To sync lockfile:" >&2
echo "  uv pip sync requirements-dev.lock" >&2
exit 1
```

## Helpful Errors vs Blocking

**Why pip blocks instead of redirecting**:
- `pip install` outside `uv` breaks lockfile consistency
- Users must learn `uv add` (project-aware dependency management)
- Educational error message teaches correct workflow

**Example Session**:
```bash
$ pip install requests
✗ Bare 'pip' detected!

Instead of 'pip install <package>', use:
  uv add <package>

To sync lockfile:
  uv pip sync requirements-dev.lock

$ uv add requests
✓ Added requests==2.31.0
```

## Recursion Prevention

```bash
# Remove .direnv/bin from PATH before exec
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run python "$@"
```

**PATH transformation**:
```
Before: .direnv/bin:/usr/bin:/usr/local/bin
After:  /usr/bin:/usr/local/bin
```

Now when `uv` calls `python`, PATH finds `/usr/bin/python` (system Python), preventing infinite loop.

### Example Configuration

See `direnv/.envrc` for working example.

---

## Visual Architecture

# Repository Worktree and Symlink Structure

**What it Represents**:
The physical file system layout of the DocImp repository, showing how worktrees, symlinks, and shared configuration enable multi-branch development with consistent Claude Code settings.

**Diagram**:

```
/Users/nik/Documents/Code/Polygot/
│
├── docimp/                                    # Main worktree
│   ├── .git/                                  # Git repository
│   │
│   ├── analyzer/                              # Python analysis engine
│   │   ├── src/
│   │   │   ├── parsers/                       # AST parsers
│   │   │   ├── utils/                         # State managers
│   │   │   └── main.py                        # CLI entry point
│   │   └── tests/
│   │
│   ├── cli/                                   # TypeScript CLI
│   │   ├── src/
│   │   │   ├── commands/                      # Command implementations
│   │   │   ├── utils/                         # StateManager, PythonBridge
│   │   │   └── index.ts                       # Entry point
│   │   └── __tests__/
│   │
│   ├── plugins/                               # JavaScript validation plugins
│   │   ├── validate-types.js                  # JSDoc type checking
│   │   └── jsdoc-style.js                     # Style enforcement
│   │
│   ├── docs/                                  # Committed documentation
│   │   └── patterns/                          # Architecture docs
│   │
│   ├── .docimp/                               # State directory (gitignored)
│   │   ├── session-reports/                   # Session JSON files
│   │   ├── workflow-state.json                # Command execution tracking
│   │   ├── history/                           # Workflow state snapshots
│   │   └── state/.git/                        # Side-car Git for transactions
│   │
│   ├── CLAUDE.md ─────────────────┐           # Symlinks to shared config
│   ├── CLAUDE_CONTEXT.md ─────────┤
│   ├── WARP.md ───────────────────┤
│   ├── .planning ─────────────────┤
│   ├── .scratch ──────────────────┤
│   │                              │
│   └── .claude/                   │
│       ├── settings.local.json ───┤
│       ├── skills ────────────────┤
│       └── agents ────────────────┤
│                                  │
├── .docimp-shared/                │           # Shared config (gitignored)
│   │                              │
│   ├── CLAUDE.md ←────────────────┘           # Technical docs for Claude Code
│   ├── CLAUDE_CONTEXT.md                      # User workflow preferences
│   │
│   ├── .planning/                             # Development plans
│   │   ├── PLAN.md                            # 31-step execution plan
│   │   ├── workflow-state-master-plan.md      # Phase tracking
│   │   ├── development-workflow.md            # Claude Code workflow
│   │   └── ARCHITECTURE_DIAGRAMS.md           # This file
│   │
│   ├── .scratch/                              # Temporary work files
│   │   ├── pr-391-summary.md
│   │   └── code-review-*.md
│   │
│   └── .claude/
│       ├── settings.local.json                # Claude Code settings
│       ├── skills/
│       │   └── git-workflow ──────────────┐   # Symlink to external skill
│       └── agents/                        │
│                                          │
├── .docimp-wt/                              │   # Additional worktrees
│   ├── issue-293/                           │   # Feature branch worktrees
│   ├── issue-300/                           │
│   └── ...                                  │
│                                            │
└── /Users/nik/Code/Polygot/docimp           │   # Alternate worktree path
                                             │
                                             │
/Users/nik/Code/repos/custom-claude-skills/  │   # External skills repository
└── project-scope/docimp/                    │
    └── git-workflow/ ───────────────────────┘   # Source of git-workflow skill
```

**Key Concepts**:

**Worktree Structure**:
- **Main worktree**: `/Users/nik/Documents/Code/Polygot/docimp/` - primary development location
- **Additional worktrees**: `.docimp-wt/issue-*/` - parallel development on different branches
- **Alternate path**: `/Users/nik/Code/Polygot/docimp` - same repo, different filesystem location

**Symlink Patterns**:
- **CLAUDE.md**: Technical documentation for Claude Code (40k char limit) - symlinked to shared location
- **WARP.md**: Alias to CLAUDE.md for Warp terminal integration
- **CLAUDE_CONTEXT.md**: User workflow preferences (gitignored) - shared across worktrees
- **.planning/**: Development plans and progress tracking - shared to maintain consistency
- **.scratch/**: Temporary work files, code reviews - shared for cross-worktree access
- **.claude/skills**: Custom Claude Code skills - pulled from external repository
- **.claude/settings.local.json**: User-specific Claude Code settings - shared for consistent behavior

**State Directory (.docimp/)**:
- **session-reports/**: JSON files for audit/improve sessions
- **workflow-state.json**: Command execution tracking (timestamps, checksums)
- **history/**: Timestamped snapshots for debugging and recovery
- **state/.git/**: Side-car Git repository for transaction tracking (never touches main `.git/`)

**External Integrations**:
- **git-workflow skill**: Symlinked from `/Users/nik/Code/repos/custom-claude-skills/project-scope/docimp/git-workflow`
- Provides standardized Git commands for worktree management, branch operations, PR creation

**Benefits**:
1. **Consistent Configuration**: Same CLAUDE.md, skills, and settings across all worktrees
2. **Parallel Development**: Work on multiple branches simultaneously with shared context
3. **Settings Isolation**: User preferences (gitignored) separate from project code
4. **Reusable Skills**: Custom Claude Code skills shared across projects
5. **Centralized Planning**: Single source of truth for development plans and progress

**File Sharing Strategy**:
- **Committed files** (docs/, README.md): In main repo, shared via Git
- **Gitignored config** (CLAUDE.md, .planning/): In `.docimp-shared/`, shared via symlinks
- **User preferences** (settings.local.json): Absolute path symlinks for cross-worktree consistency
- **External skills**: Relative symlinks to custom skills repository

---

## When to Use These Patterns

**Use when:**
- Multiple Claude Code instances needed for parallel development
- Codebase exceeds 10,000 lines with complex architecture
- Team needs coordination between concurrent workflows and quality enforcement
- Context window management becomes critical (approaching 40KB CLAUDE.md limit)

**Don't use when:**
- Single developer working on small projects (under 5,000 lines)
- Simple workflows are sufficient for your team's needs
- Team doesn't use or understand git worktrees
- Project doesn't require strict workflow enforcement

---

## Implementation Roadmap

**Quick Win (30 minutes):**
1. Install git hooks from `actual-code/hooks/`
2. Test protection in main worktree
3. Verify educational error messages guide developers correctly

**Full Setup (2 hours):**
1. Run `create_worktree.py` to create first feature worktree
2. Configure CLAUDE.md with external imports (move detailed docs to `@docs/patterns/`)
3. Set up direnv tool interception with wrapper scripts
4. Test full workflow across multiple worktrees

**Advanced:**
- Customize patterns for your specific tech stack and tooling
- Add additional quality gates (linting, type checking, security scanning)
- Extend worktree automation with issue tracking integration
- Build dashboards for cross-worktree status monitoring

---

## Limitations & Future Work

**Time Constraints:**
This take-home was completed in 3.5 hours, focusing on one working pattern (worktree orchestration) with supporting patterns documented.

**Would Expand:**
- Additional case studies with different codebases (monorepos, microservices, mobile apps)
- Video walkthroughs of each pattern showing real-world usage
- Comprehensive troubleshooting guides for common issues
- Performance metrics and optimization strategies for large teams

**Known Issues:**
- Patterns tested on macOS/Linux only (Windows compatibility untested)
- Assumes familiarity with git worktrees (learning curve for new users)
- Direnv requires installation and shell integration
- Path-based detection assumes consistent naming conventions

---

## Links

- **Source Code**: DocImp at [github.com/nikblanchet/docimp](https://www.github.com/nikblanchet/docimp)
- **Working Implementation**: See `actual-code/` directory in this repository
- **Planning Strategy**: See `PLANNING.md` for development approach
- **Worktree Creation Script**: `actual-code/create_worktree.py` (1066 lines, production-ready)
