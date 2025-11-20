# Advanced Claude Code Patterns: Production Infrastructure

## Overview

This repository demonstrates advanced patterns for using Claude Code on enterprise-scale projects. **Every pattern documented here is implemented in this codebase** - you can examine the working code in `actual-code/` and see it activated via symlinks in `.claude/`.

These patterns solve a critical challenge in AI-assisted development: **how to run multiple Claude Code agents in parallel without conflicts**. By combining git worktrees, custom agents, skills, and hooks, you can decompose large tasks into smaller, parallelizable units that maintain code quality while avoiding context bloat.

**Audience:** Senior developers and teams managing large codebases (100K+ lines) who need sophisticated Claude Code workflows beyond basic usage.

## Table of Contents

### Core Claude Code Patterns (Scenario C)

1. **[Custom Agents](#pattern-1-custom-agents)** - Autonomous task execution with structured workflows
   *Implemented:* `actual-code/agents/` → `.claude/agents/`

2. **[Custom Skills](#pattern-2-custom-skills)** - Reusable knowledge modules with bundled resources
   *Implemented:* `actual-code/skills/` → `.claude/skills/`

3. **[Claude Code Hooks](#pattern-3-claude-code-hooks)** - Event-driven automation and permissions
   *Implemented:* `actual-code/hooks-config/settings.local.json` → `.claude/settings.local.json`

### Infrastructure Patterns

4. **[Git Worktree Orchestration](#pattern-4-git-worktree-orchestration)** - Parallel agents without merge conflicts
   *Implemented:* Path-based detection, automated via `create_worktree.py`

5. **[Git Hooks for AI Safety](#pattern-5-git-hooks-for-ai-safety)** - Protect main branch from agentic workflows
   *Implemented:* `actual-code/hooks/` two-tier architecture (Git + Husky)

6. **[Symlink Discovery Pattern](#pattern-6-symlink-discovery-pattern)** - Separate documentation from runtime
   *Implemented:* `actual-code/` → `.claude/` symlink structure

7. **[CLAUDE.md Context Management](#pattern-7-claudemd-context-management)** - Stay under 40KB with external imports
   *Implemented:* `@docs/` import pattern

8. **[Direnv Tool Interception](#pattern-8-direnv-tool-interception)** - PATH manipulation for workflow enforcement
   *Implemented:* Python/pip interceptors with educational errors

### Placeholder Patterns (Future Work)

9. **Environment Automation Beyond Direnv** - Additional context-aware triggers
   *Status:* Documented in DocImp, not yet ported to this repo

10. **CI/CD Integration** - GitHub Actions for AI-assisted development
    *Status:* Planned for future implementation

---

## Why These Patterns Matter

**The Parallel Agent Problem:**
Smaller-scoped agents produce better code quality and manage context more effectively. However, running agents serially is slow. The solution: **parallelize agents across git worktrees**.

**The Tradeoff:**
This shifts burden from execution (fast parallel agents) to setup (worktree infrastructure) and planning (decomposing tasks properly). The payoff: multiple agents working simultaneously without merge hell.

**Prerequisites:**
Good task decomposition skills. If tasks have sequential dependencies, even worktrees won't help.

---

## Pattern 1: Custom Agents

Autonomous subprocesses that execute complex multi-step tasks with isolated context (fresh eyes, no conversation history).

### Why Agents Matter

When tasks require multiple steps, context analysis, and decision-making, agents provide structured autonomy. Unlike direct prompting, agents follow predefined workflows and can make decisions without human intervention at each step.

### Location and Structure

**Source**: `actual-code/agents/` → **Runtime**: `.claude/agents/` (symlinked)

### Agent Types

#### User Agents (`actual-code/agents/user/`)

Cross-project, language-specific agents you'd use across multiple repositories:

**python-313-conventions**:
- Python 3.13+ modernization reviewer
- 10 review dimensions: typing design, API contracts, async patterns, architectural cohesion
- Complements automation (Ruff/mypy handle syntax; this handles semantic design)
- Catches patterns automation cannot check (e.g., inconsistent error handling philosophy)

#### Project Agents (`actual-code/agents/project/`)

Repository-specific workflow agents:

**code-reviewer**:
- Autonomous 11-dimension code review
- Gathers context from PR description, `.planning/PLAN.md`, linked issues
- Checks previous review blockers (converts them to acceptance criteria)
- Classifies findings: Blocker, Important, Minor, Enhancement
- Saves detailed markdown review, posts summary comment to PR

### Invocation Patterns

Agents appear in Claude Code's agent menu and can be invoked via prompts referencing their name. Best practice: explicit invocation after completing a milestone.

**Example**: "Run the python-313-conventions agent to review my changes"

### Agent vs Skill vs Hook

| Feature | Agents | Skills | Hooks |
|---------|--------|--------|-------|
| **What** | Autonomous subprocess | Knowledge in context | Event-driven command |
| **When** | Complex multi-step tasks | Provide expertise | Respond to events |
| **Context** | Isolated (fresh eyes) | Shared with main session | Runs in shell |
| **Example** | Code reviewer | Git workflow standards | Inject git status |

See `actual-code/agents/*/README.md` for detailed agent documentation.

---

## Pattern 2: Custom Skills

Specialized knowledge and workflows loaded into Claude Code's context when needed. Skills provide domain expertise without requiring separate subprocess execution.

### Location and Structure

**Source**: `actual-code/skills/` → **Runtime**: `.claude/skills/` (symlinked)

Skills can bundle:
- `skill.md` - Core documentation and instructions
- `scripts/` - Supporting automation (e.g., `create_worktree.py`)
- `references/` - Additional context materials
- `assets/` - Configuration templates, examples

### Skill Categories

#### User Skills (`actual-code/skills/user/` - 6 skills)

Cross-project standards and practices:

- **development-standards**: No emoji in commits/code, use modern language features, comprehensive documentation (CRITICAL - enforced across all work)
- **exhaustive-testing**: Comprehensive test coverage philosophy (unit, integration, regression, e2e)
- **handle-deprecation-warnings**: Proactive dependency migration (notice warnings, update immediately)
- **dependency-management**: When to use libraries vs build custom (bias toward quality dependencies)
- **cli-ux-colorful**: Terminal output formatting (rich/chalk libraries, ANSI colors)
- **access-skill-resources**: How to navigate skill bundles and use bundled scripts

#### Official Skills (`actual-code/skills/official/`)

Meta-skills from Claude Code:

- **skill-creator**: Guide for creating effective new skills (structure, best practices, examples)

#### Project Skills (`actual-code/skills/project/`)

Repository-specific workflows:

- **git-workflow**: Worktree-based development, commit standards, branch management
  - **Bundles**: `scripts/create_worktree.py` (798 lines) - full worktree automation
  - Demonstrates skill script bundling pattern

### When to Use Skills vs Agents vs Hooks

- **Skill**: Provide domain knowledge (brand guidelines, API documentation, workflow procedures)
- **Agent**: Execute complex tasks requiring decisions (code review, comprehensive refactoring)
- **Hook**: Automate on events (inject context, run checks, enforce standards)

See `actual-code/skills/*/README.md` for skill-specific documentation.

---

## Pattern 3: Claude Code Hooks

Event-driven shell commands that execute during Claude Code sessions. **Critical distinction**: These are NOT Git hooks (which respond to Git operations like commit/push). Claude Code hooks respond to AI assistance events.

### Location and Structure

**Source**: `actual-code/hooks-config/settings.local.json` → **Runtime**: `.claude/settings.local.json` (gitignored, user-specific)

### Hook Types

**Available Events**:
- `user-prompt-submit`: Runs when user sends a message to Claude
- `tool-call`: Executes before Claude uses any tool
- `session-start`: Triggers when Claude Code session begins
- `session-end`: Runs when session terminates

### Example Use Cases

```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "git status --short",
      "_comment": "Inject git status so Claude knows about uncommitted changes"
    },
    "session-start": {
      "command": "uv pip list | grep -i outdated",
      "_comment": "Check for outdated dependencies on session start"
    },
    "tool-call": {
      "command": "echo '[TOOL] {{tool_name}}' >> .claude/tool-log.txt",
      "_comment": "Log every tool call for debugging"
    }
  }
}
```

### Permissions System

Fine-grained control over Claude's tool usage:

- `allow`: Tools Claude can use without asking (e.g., `["Read", "Glob", "Grep", "git status"]`)
- `deny`: Tools blocked completely (e.g., `["rm", "sudo"]`)
- `ask`: Tools requiring user approval each time (e.g., `["git commit", "git push", "npm install"]`)

**Example**:
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "git log", "pytest"],
    "deny": ["python -m pip", "sudo"],
    "ask": ["git commit", "git push", "gh pr create"]
  }
}
```

### Critical Distinction: Claude Code Hooks ≠ Git Hooks

Don't confuse these hook systems:

| | Claude Code Hooks | Git Hooks |
|---|---|---|
| **Trigger** | AI session events | Git operations |
| **Examples** | prompt-submit, tool-call | pre-commit, post-checkout |
| **Location** | `.claude/settings.local.json` | `.git/hooks/` or `.husky/` |
| **Purpose** | Inject context, control permissions | Enforce quality gates |

See `actual-code/hooks-config/README.md` for comprehensive documentation and advanced patterns.

---

## Integration Pattern: How Patterns Work Together

These patterns create a layered quality and automation framework:

```
1. User submits prompt
   ↓ (Claude Code Hook: user-prompt-submit)
2. Hook injects git status into context
   ↓ (Skill provides domain knowledge)
3. git-workflow skill provides commit standards
   ↓ (Agent executes complex task)
4. code-reviewer agent performs 11-dimension review
   ↓ (Git Hook provides final gate)
5. pre-commit hook blocks if tests fail or wrong branch
```

**Example workflow**:
1. `user-prompt-submit` hook injects uncommitted file list
2. `git-workflow` skill provides worktree guidance and commit message standards
3. `code-reviewer` agent autonomously reviews changes across 11 dimensions
4. Git `pre-commit` hook (Pattern 5) blocks commit if quality gates fail

**Result**: Robust quality framework where each layer reinforces the others.

---

## Pattern 4: Git Worktree Orchestration

Run multiple Claude Code agents in parallel without merge conflicts. This pattern provides the foundation for isolation, ensuring the main worktree remains stable while feature worktrees handle active development.

### Why Worktrees Solve the Parallel Agent Problem

**The Challenge:** Smaller-scoped agents produce better code quality and manage token budgets more effectively. But running agents serially is slow.

**The Solution:** Git worktrees enable parallel agent execution without merge conflicts. Each agent operates in its own isolated worktree, working on independent branches simultaneously.

**Real-World Impact:** This pattern has been tested with 7+ concurrent Claude Code instances running different tasks in parallel on the same codebase. The bottleneck shifts from execution time to task decomposition - can you break work into parallelizable chunks?

### Setup Approaches

#### Greenfield Projects (Recommended)

This repository demonstrates the clean approach - start with worktrees from day one:

```bash
# Repository structure
parent-dir/
├── .git/              # Shared git directory
├── main/              # Main worktree (reference only)
├── feature-1/         # Feature worktree
└── feature-2/         # Feature worktree
```

**Benefits:**
- Clean separation from the start
- Main worktree protected by default
- No migration complexity

#### Retrofitting Existing Repositories

If you have an existing repo, you can adopt worktrees incrementally:

1. Keep your current directory as the main worktree
2. Create feature worktrees alongside it
3. Configure git hooks to protect main (see Pattern 5)
4. Gradually shift development to feature worktrees

**Trade-off:** May need shared configuration patterns (e.g., `.shared/` directory) to avoid git tracking conflicts. See DocImp case study for retrofit implementation details.

### Automation: create_worktree.py

The `create_worktree.py` script (798 lines, available in `actual-code/skills/git-workflow/scripts/`) automates the entire workflow:

```bash
python3 create_worktree.py feature-name branch-name
```

**What it handles:**
- Validates source branch exists (local or remote)
- Detects main branch location automatically
- Creates isolated Python virtual environment per worktree
- Sets up symlinks for shared configuration (when needed)
- Coordinates git hooks across worktrees
- Prompts for uncommitted changes handling

**CLI Options:**
```bash
--source-branch BRANCH        # Branch from (default: main)
--include-changes none        # Don't bring uncommitted changes
--include-changes uncommitted # Bring uncommitted only
--include-changes unpushed    # Bring unpushed commits
--include-changes all         # Bring everything
```

### Common Gotchas and Workarounds

#### 1. Claude Ignores Worktree Automation

**Problem:** Claude Code's training data overwhelmingly uses `git checkout` instead of `git worktree`, so it often ignores the create_worktree.py script.

**Workarounds:**
- Add script to a `git-workflow` skill (forces Claude to see it in context)
- Bundle script in skill's `scripts/` subdirectory
- In prompts, explicitly say: "Use your `git-workflow` skill's `create_worktree.py` script"

#### 2. Claude Runs Script from Wrong Location

**Problem:** Claude may try to execute the script from the `scripts/` directory, causing path resolution failures.

**Workaround:**
- Script detects execution context and fails gracefully with clear error messages
- Advanced: Make script location-agnostic (auto-detect repo root)
- Simple: Just correct Claude when this happens

#### 3. Claude Invents CLI Flags

**Problem:** Claude sees a script and imagines what flags might exist, triggering interactive mode. Claude struggles with interactive prompts and may try to manually replicate the script's logic (token-inefficient and error-prone).

**Workarounds:**
- Interrupt Claude and tell it to use `--help`
- Create an `access-skill-resources` skill documenting how to use scripts with `--help`
- In interactive mode, display: "This is interactive mode. If you meant CLI, use `--help` for flag syntax"
- For simple setups: just go with interactive mode
- Run script yourself before starting Claude

#### 4. Claude Tries Checkout in Main Worktree

**Problem:** Training data inertia - Claude defaults to `git checkout` in current directory.

**Workaround:**
- Git hooks auto-block commits on main branch (see Pattern 5)
- Post-checkout hook auto-reverts branch changes in main worktree
- Claude learns from hook error messages to use worktrees instead

### Integration with Git Hooks

Worktrees work best with protective git hooks (Pattern 5: Git Hooks for AI Safety). See `actual-code/hooks/` for implementation details.

---

## Pattern 5: Git Hooks for AI Safety

Protect the main branch from accidental commits when using agentic AI workflows. Git hooks (not Claude Code hooks) provide the final safety net.

### Why This Matters for Agentic AI

Claude Code's training data overwhelmingly shows `git checkout` workflows, not worktrees. Even with prompts and skills, Claude may occasionally try to commit to main or checkout branches in the main worktree. Git hooks auto-block these operations.

### Two-Tier Hook Architecture

**Source**: `actual-code/hooks/` → **Installed**: `.git/hooks/` (or via Husky)

```
User Action (git commit/checkout)
    ↓
Layer 1: Git Hooks (.git/hooks/)
    ├─ pre-commit: Block commits on main in main worktree
    └─ post-checkout: Auto-revert branch changes in main worktree
    ↓
Layer 2: Husky Hooks (.husky/) [optional]
    ├─ Delegates to Git hooks
    └─ Adds lint-staged integration
```

### Path-Based Detection

**Core Insight**: Hooks identify worktree type via path pattern matching, not fragile git metadata.

```bash
# Check if we're in the main worktree
current_worktree=$(git rev-parse --show-toplevel)

if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # Path doesn't contain worktree pattern → this is main → block commit
    echo "✗ COMMIT BLOCKED: Cannot commit on main branch in main worktree"
    exit 1
fi
```

**Pattern**: `/.docimp-wt/` identifies feature worktrees. Adjust pattern for your naming convention.

### Hook Implementations

**pre-commit** (`actual-code/hooks/pre-commit`):
- Blocks commits to main branch when in main worktree
- Educational error messages guide users to create worktrees
- Allows `--no-verify` bypass for maintenance

**post-checkout** (`actual-code/hooks/post-checkout`):
- Auto-reverts if you check out non-main branch in main worktree
- Prevents accidental branch switching in reference worktree
- Silent operation (no blocking messages needed)

### Configuration

Hooks read from `actual-code/hooks/config/.worktree-config`:

```bash
WORKTREE_PATTERN="/.docimp-wt/"
CREATE_WORKTREE_SCRIPT="actual-code/create_worktree.py"
```

Adjust `WORKTREE_PATTERN` to match your directory naming (e.g., `/feature-/` or `/-wt/`).

### Installation

Git worktrees share the hooks directory, so install once:

```bash
# Copy hooks to shared git directory
cp actual-code/hooks/pre-commit .git/hooks/
cp actual-code/hooks/post-checkout .git/hooks/

# Make executable
chmod +x .git/hooks/*
```

All worktrees now protected automatically.

### Integration with Husky (Optional)

For npm projects, Husky provides additional tooling integration:

```bash
# .husky/pre-commit
#!/bin/bash
.git/hooks/pre-commit || exit 1  # Call Git hook first
npx lint-staged                  # Then run lint-staged
```

See `actual-code/hooks/README.md` for complete two-tier architecture details.

---

## Pattern 6: Symlink Discovery Pattern

Separate documentation (source of truth) from runtime discovery (what Claude Code sees). This enables version control flexibility and clear organization.

### The Pattern

**Source**: `actual-code/` contains all agents, skills, and configurations
**Runtime**: `.claude/` contains symlinks that Claude Code discovers

**Actual structure in this repo**:

```
.claude/
├── agents/
│   ├── code-reviewer.md -> ../../actual-code/agents/project/code-reviewer.md
│   └── python-313-conventions.md -> ../../actual-code/agents/user/python-313-conventions.md
├── skills/
│   ├── access-skill-resources -> ../../actual-code/skills/user/access-skill-resources/
│   ├── cli-ux-colorful -> ../../actual-code/skills/user/cli-ux-colorful/
│   ├── dependency-management -> ../../actual-code/skills/user/dependency-management/
│   ├── development-standards -> ../../actual-code/skills/user/development-standards/
│   ├── exhaustive-testing -> ../../actual-code/skills/user/exhaustive-testing/
│   ├── git-workflow -> ../../actual-code/skills/project/git-workflow/
│   ├── handle-deprecation-warnings -> ../../actual-code/skills/user/handle-deprecation-warnings/
│   └── skill-creator -> ../../actual-code/skills/official/skill-creator/
└── settings.local.json (not symlinked - user-specific, gitignored)
```

**Key insight**:
- **Agents**: Symlink individual `.md` files (agents are single files)
- **Skills**: Symlink individual skill directories (skills can bundle scripts, references, assets)

### Why This Works

**Benefits**:
1. **Single source of truth**: All content lives in `actual-code/`
2. **Clear documentation**: `actual-code/` is obviously the canonical location
3. **Fine-grained control**: Choose which agents/skills to activate per worktree
4. **Version control friendly**: Commit `actual-code/`, gitignore `.claude/`
5. **Easy discovery**: Claude Code automatically finds resources via `.claude/`

### Setup

```bash
# Create individual agent file symlinks
ln -s ../../actual-code/agents/project/code-reviewer.md .claude/agents/
ln -s ../../actual-code/agents/user/python-313-conventions.md .claude/agents/

# Create individual skill directory symlinks
ln -s ../../actual-code/skills/user/access-skill-resources .claude/skills/
ln -s ../../actual-code/skills/user/cli-ux-colorful .claude/skills/
ln -s ../../actual-code/skills/user/dependency-management .claude/skills/
ln -s ../../actual-code/skills/user/development-standards .claude/skills/
ln -s ../../actual-code/skills/user/exhaustive-testing .claude/skills/
ln -s ../../actual-code/skills/user/handle-deprecation-warnings .claude/skills/
ln -s ../../actual-code/skills/project/git-workflow .claude/skills/
ln -s ../../actual-code/skills/official/skill-creator .claude/skills/
```

### What to Version Control

**.gitignore**:
```
.claude/           # Don't commit symlinks (user-specific)
```

**Do commit**:
- `actual-code/agents/` - Agent definitions
- `actual-code/skills/` - Skill definitions
- `actual-code/hooks-config/` - Hook configuration templates

**User creates locally**:
- `.claude/agents/` symlinks - Individual agent files
- `.claude/skills/` symlinks - Individual skill directories
- `.claude/settings.local.json` - Copy and customize from template

---

## Pattern 7: CLAUDE.md Context Management

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

## Pattern 8: Direnv Tool Interception

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
