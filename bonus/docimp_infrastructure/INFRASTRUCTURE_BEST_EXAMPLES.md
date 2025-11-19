# DocImp Infrastructure: Best Examples

This document showcases the 3 most impressive and sophisticated infrastructure components in the DocImp project. These represent **non-obvious solutions to real development challenges** that most teams struggle with.

---

## 1. Git Hooks + Worktree Workflow: Branch Protection via Path Detection

### The Problem It Solves

When using git worktrees for parallel development, you need to:
- Protect the main branch from accidental commits in the main worktree
- Allow feature branches to operate normally in their own worktrees
- Prevent branch checkouts that would break the worktree isolation model
- Coordinate multiple developers/Claude Code instances working simultaneously

Most teams either:
- Skip worktrees entirely (limiting to one workspace at a time)
- Use worktrees but rely on discipline alone (accidents happen)
- Implement branch protection at remote level only (doesn't prevent local mistakes)

### The Solution: Path-Based Detection

**Key Insight**: Worktree identity can be determined by path pattern matching, not git internals.

#### Pre-Commit Hook (`.git/hooks/pre-commit`)

```bash
#!/bin/bash
# pre-commit hook: Block commits on main branch in main worktree

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

**Why This Is Sophisticated**:
1. **Path pattern matching** (`/.docimp-wt/`) instead of fragile git metadata checks
2. **Educational error messages** with examples of correct workflow
3. **Escape hatch documented** (`--no-verify`) for legitimate maintenance
4. **Colored output** for visibility
5. **Branch-specific** (only protects main, not all branches)

#### Post-Checkout Hook (`.git/hooks/post-checkout`)

```bash
#!/bin/bash
# post-checkout hook: Block branch checkouts in main worktree

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

**Why This Is Sophisticated**:
1. **Auto-reverting** to main instead of just failing (graceful recovery)
2. **Distinguishes branch vs file checkout** (hook parameter inspection)
3. **Same path detection pattern** as pre-commit (consistency)

### Husky Integration for Per-Worktree Hook Management

**Challenge**: Git hooks are stored in `.git/hooks/`, which is shared across all worktrees. But we want:
- Main worktree: strict protection hooks active
- Feature worktrees: different hooks (lint-staged, formatters)

**Solution**: Per-worktree git config + Husky dispatcher pattern

#### Husky Pre-Commit Dispatcher (`.husky/pre-commit`)

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

**Configuration Command** (runs in each new worktree):
```bash
# Enable per-worktree config (one-time)
git config extensions.worktreeConfig true

# Set worktree-specific hooks path
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"

# Generate Husky dispatcher files
npx husky
```

**Why This Is Sophisticated**:
1. **Two-layer hook system**: Protected hooks (`.git/hooks/`) + Husky hooks (`.husky/`)
2. **Per-worktree config isolation** via `extensions.worktreeConfig`
3. **Automatic dispatcher generation** via `npx husky`
4. **Graceful failures** (protection hook runs first, linting is secondary)

### The Worktree Creation Orchestrator

**File**: `.claude/skills/git-workflow/scripts/create_worktree.py` (1067 lines)

This Python script automates the entire worktree creation process with sophisticated change detection and transfer logic.

#### Key Features

**1. Detects Uncommitted and Unpushed Changes**

```python
def check_local_changes(worktree_path: Path) -> dict:
    """Check for uncommitted and unpushed changes in specified worktree."""
    changes = {
        'uncommitted': False,
        'uncommitted_output': '',
        'unpushed': False,
        'unpushed_count': 0,
        'unpushed_log': ''
    }

    # Check for uncommitted changes
    status_result = run_git('status', '--porcelain', cwd=worktree_path, check=False)
    if status_result.returncode == 0 and status_result.stdout.strip():
        changes['uncommitted'] = True
        changes['uncommitted_output'] = status_result.stdout

    # Check for unpushed commits (requires upstream branch)
    upstream_result = run_git('rev-parse', '--abbrev-ref', '@{u}', cwd=worktree_path, check=False)
    if upstream_result.returncode == 0:
        count_result = run_git('rev-list', '--count', '@{u}..HEAD', cwd=worktree_path, check=False)
        if count_result.returncode == 0:
            count = int(count_result.stdout.strip())
            if count > 0:
                changes['unpushed'] = True
                changes['unpushed_count'] = count

                # Get formatted log of unpushed commits
                log_result = run_git(
                    'log', '@{u}..HEAD', '--oneline', '--no-decorate',
                    cwd=worktree_path, check=False
                )
                if log_result.returncode == 0:
                    changes['unpushed_log'] = log_result.stdout.strip()

    return changes
```

**Why This Matters**: When branching from a feature branch (not main), you often want to include work-in-progress. The script detects and offers to transfer:
- **Uncommitted changes** (stashed, applied to new worktree)
- **Unpushed commits** (new branch points to same HEAD)
- **Both** (stash + HEAD)
- **Neither** (branch from remote tracking branch)

**2. Interactive Prompting with Smart Defaults**

```python
def prompt_include_changes(branch_name: str, worktree_path: Path, changes_info: dict) -> str:
    """Prompt user about including changes from source worktree."""
    print()
    print_info(f"Changes detected in source worktree: {worktree_path}")
    print()

    # Show uncommitted changes (first 10 files)
    if changes_info['uncommitted']:
        print_warning("Uncommitted changes:")
        lines = changes_info['uncommitted_output'].strip().split('\n')
        for line in lines[:10]:
            print(f"  {line}")
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more files")
        print()

    # Show unpushed commits (first 5)
    if changes_info['unpushed']:
        print_warning(f"Unpushed commits ({changes_info['unpushed_count']}):")
        for line in changes_info['unpushed_log'].split('\n')[:5]:
            print(f"  {line}")
        if changes_info['unpushed_count'] > 5:
            print(f"  ... and {changes_info['unpushed_count'] - 5} more commits")
        print()

    # Build menu dynamically based on what exists
    print("Include changes in new worktree?")
    options = {}
    option_num = 1

    options[str(option_num)] = 'none'
    print(f"  {option_num}. None (branch from last pushed commit)")
    option_num += 1

    if changes_info['uncommitted']:
        options[str(option_num)] = 'uncommitted'
        print(f"  {option_num}. Uncommitted only")
        option_num += 1

    if changes_info['unpushed']:
        options[str(option_num)] = 'unpushed'
        print(f"  {option_num}. Unpushed commits only")
        option_num += 1

    if changes_info['uncommitted'] and changes_info['unpushed']:
        options[str(option_num)] = 'all'
        print(f"  {option_num}. All changes (uncommitted + unpushed)")
        default_choice = str(option_num)
    elif changes_info['uncommitted']:
        default_choice = '2'
    elif changes_info['unpushed']:
        default_choice = '2'
    else:
        default_choice = '1'

    print()

    # Get user choice with validation
    while True:
        choice = input(f"Choice [default: {default_choice}]: ").strip()
        if choice == '':
            return options[default_choice]
        if choice in options:
            return options[choice]
        print(f"Please enter a number between 1 and {len(options)}")
```

**Why This Is Sophisticated**:
- **Dynamic menu** (only shows options that apply to current state)
- **Smart defaults** (defaults to "all" if both types of changes exist)
- **Preview of changes** (shows first 10 files, first 5 commits)
- **Input validation** with helpful error messages

**3. Complete Orchestration Flow**

The script performs 10 steps in sequence:

```python
def main() -> int:
    # 1. Validate we're in the docimp repo
    validate_docimp_repo()

    # 2. Validate source branch exists (local or remote)
    is_valid, branch_type = validate_source_branch(args.source_branch)

    # 3. Find worktree containing source branch (if any)
    source_worktree_path = find_worktree_for_branch(args.source_branch)

    # 4. Detect uncommitted changes and unpushed commits
    if source_worktree_path:
        changes_info = check_local_changes(source_worktree_path)

    # 5. Prompt to include changes (or use flags for non-interactive)
    if changes_info['uncommitted'] or changes_info['unpushed']:
        include_changes_choice = prompt_include_changes(...)

    # 6. Create worktree with selected change inclusion strategy
    run_git('worktree', 'add', str(worktree_path), '-b', args.branch_name, ...)

    # 7. Create symlinks to shared files (with cleanup on failure)
    create_symlink('../../.docimp-shared/CLAUDE.md', worktree_path / 'CLAUDE.md')
    create_symlink('../../.docimp-shared/CLAUDE_CONTEXT.md', ...)
    # ... 7 symlinks total

    # 8. Configure Husky hooks for the new worktree
    configure_husky_hooks(worktree_path)

    # 9. Install npm dependencies and build TypeScript
    install_npm_dependencies(worktree_path)

    # 10. Setup Python venv (per-worktree isolation)
    setup_python_venv(worktree_path)

    # 11. Setup Node version via nvm
    setup_node_version(worktree_path)

    # 12. Enable direnv for tool interception
    enable_direnv(worktree_path)

    # 13. Print comprehensive success summary
    print_success("✓ Worktree created successfully!")
```

**4. Per-Worktree Python Environment (Critical for Parallel Work)**

```python
def setup_python_venv(worktree_path: Path) -> None:
    """Create per-worktree Python virtual environment using uv's managed Python.

    Uses 'uv python install' to download and manage an isolated Python version,
    then creates .venv using 'uv venv --python X.Y'. This approach provides
    containerization - Python is isolated from system Python and managed by uv.
    This prevents lock contention and conflicts when multiple worktrees
    run Python commands simultaneously.
    """
    # Read Python version from .python-version file
    python_version_file = worktree_path / '.python-version'
    python_version = python_version_file.read_text().strip() if python_version_file.exists() else '3.13'

    # Ensure uv has the requested Python version (downloads if needed)
    subprocess.run(['uv', 'python', 'install', python_version], check=True, timeout=120)

    # Create venv using uv's managed Python (containerized)
    subprocess.run(['uv', 'venv', '--python', python_version], cwd=worktree_path, check=True, timeout=30)

    # Verify Python version
    venv_python = worktree_path / '.venv' / 'bin' / 'python'
    version_result = subprocess.run([str(venv_python), '--version'], capture_output=True, text=True)
    actual_version = version_result.stdout.strip()
    print_success(f"✓ Virtual environment created with isolated {actual_version}")
    print_success(f"✓ Python managed by uv (containerized, not system Python)")

    # Install dependencies using uv sync (uses local .venv and uv.lock)
    subprocess.run(['uv', 'sync', '--extra', 'dev'], cwd=worktree_path, check=True, timeout=120)
    print_success("✓ Dependencies installed (anthropic, pytest, ruff, mypy)")
```

**Why This Is Critical**:
- **Lock contention**: Multiple worktrees sharing a single `.venv/` would compete for `uv.lock` writes
- **Dependency isolation**: Different worktrees might test different dependency versions
- **Containerization**: uv-managed Python (not system Python) prevents conflicts
- **Auto-setup**: New worktree is immediately usable without manual venv creation

### What Makes This Workflow Special

1. **Solves a real problem**: Parallel development with Claude Code instances working on different features simultaneously
2. **Path-based detection**: Simple, robust, maintainable (no fragile git metadata)
3. **Educational error messages**: Developers learn the workflow from the error messages
4. **Change transfer logic**: Sophisticated handling of uncommitted/unpushed work
5. **Complete orchestration**: One command creates fully configured worktree (hooks, deps, symlinks, venvs)
6. **Per-worktree isolation**: Python and Node environments containerized to prevent conflicts

**Comparison to Standard Approaches**:
- Most teams: Single workspace, branch switching (slow, context loss)
- Git worktrees (basic): Manual worktree creation, no protection, shared configs
- This approach: Automated creation, branch protection, isolated configs, change transfer

---

## 2. Claude Code Configuration: Permission Whitelist + Context Management

### The Problem It Solves

When using Claude Code for development, you need to:
- **Grant enough permissions** for productivity (file access, bash commands, skills)
- **Restrict dangerous operations** (no bare `python`, `pip`, `pytest` - must use `uv run`)
- **Manage context window** (CLAUDE.md has 40K character limit)
- **Share infrastructure** across worktrees without duplication
- **Separate public docs** (committed to git) from **private context** (gitignored)

### The Solution: Multi-Layered Configuration Architecture

#### Layer 1: Permission Whitelist (`.claude/settings.local.json`)

**Structure**: 3 permission levels (allow, deny, ask) with pattern matching

```json
{
  "permissions": {
    "allow": [
      "Bash(docimp analyze:*)",
      "Bash(uv run pytest:*)",
      "Bash(uv run ruff:*)",
      "Bash(uv run mypy:*)",
      "Bash(gh pr create:*)",
      "Bash(gh issue list:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(npm run test:*)",
      "Bash(npm run lint)",
      "Glob(./**)",
      "Grep(./**)",
      "Read(./**)",
      "Skill(git-workflow)",
      "Skill(development-standards)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:stackoverflow.com)",
      "WebSearch"
    ],
    "deny": [
      "Bash(python:*::*)",
      "Bash(python3:*::*)",
      "Bash(pytest:*::*)",
      "Bash(ruff:*::*)",
      "Bash(mypy:*::*)",
      "Bash(pip:*::*)"
    ],
    "ask": [
      "Bash(uv run python:*)",
      "Bash(uv pip:*)",
      "Bash(uv add:*)"
    ],
    "additionalDirectories": [
      "/Users/nik/Documents/Code/Polygot/.docimp-shared",
      "/Users/nik/Documents/Code/Polygot/.docimp-wt",
      "/Users/nik/Documents/Code/Polygot/docimp",
      "/Users/nik/Code/repos/anthropic-official-skills/skill-creator"
    ]
  }
}
```

**Why This Is Sophisticated**:

1. **Pattern-based whitelisting**: `Bash(docimp analyze:*)` allows `docimp analyze ./src` but blocks `docimp improve`
2. **Explicit deny for dangerous operations**: Bare `python`, `pip`, `pytest` are blocked (forces `uv run` prefix)
3. **Permission escalation for package management**: `uv add` requires explicit user approval
4. **Domain-restricted web access**: Only specific domains allowed for WebFetch
5. **Multi-directory access**: Grants read access to shared infrastructure, worktrees, and official skills

**Security Model**:
- **Default deny**: Everything not explicitly allowed is blocked
- **Layered permissions**: allow → deny → ask (in order of evaluation)
- **Audit trail**: User sees every `ask` permission request

#### Layer 2: Symlink-Based Infrastructure Sharing

**Directory Structure**:
```
.docimp-shared/
├── .claude/
│   ├── settings.local.json  ← Permissions (shared across all worktrees)
│   ├── skills/              ← Custom skills (git-workflow, etc.)
│   └── agents/              ← Custom agents
├── .planning/
│   └── PLAN.md              ← 31-step execution plan (gitignored)
├── .scratch/                ← Temporary working files
├── CLAUDE.md                ← Technical documentation (27.8KB)
└── CLAUDE_CONTEXT.md        ← Private project context (gitignored)

docimp/  (main worktree)
├── .claude/ → symlink to ../.docimp-shared/.claude/
├── CLAUDE.md → symlink to ../.docimp-shared/CLAUDE.md
├── CLAUDE_CONTEXT.md → symlink
├── .planning/ → symlink
└── .scratch/ → symlink

.docimp-wt/issue-260/  (feature worktree)
├── .claude/ → symlink to ../../.docimp-shared/.claude/
├── CLAUDE.md → symlink
├── CLAUDE_CONTEXT.md → symlink
├── .planning/ → symlink
└── .scratch/ → symlink
```

**Why Symlinks Instead of Copies**:
1. **Single source of truth**: Update CLAUDE.md once, applies to all worktrees
2. **No synchronization**: No risk of worktrees diverging in configuration
3. **Git-friendly**: Symlinks committed to git, point to gitignored shared directory
4. **Automatic propagation**: New worktrees get current config via symlinks

**Separation of Concerns**:
- **Public docs** (CLAUDE.md): Committed to git, technical reference for all contributors
- **Private context** (CLAUDE_CONTEXT.md): Gitignored, personal workflow preferences
- **Shared infrastructure** (.docimp-shared/): Gitignored, contains both public and private

#### Layer 3: CLAUDE.md External Import Pattern (27.8KB → 40K Limit)

**The Challenge**: CLAUDE.md must stay under 40K characters, but DocImp has complex architecture requiring extensive documentation.

**The Solution**: External documentation imports via `@docs/patterns/` references

**CLAUDE.md Structure** (27,792 bytes):
```markdown
# CLAUDE.md

**Character Limit: 40.0k characters (absolute maximum) for CLAUDE.md specifically.**

## Maintaining This File

**When to update:**
- Architecture changes
- New critical commands
- Major feature additions

**How to maintain:**
- Keep CLAUDE.md under 40k characters (check with `wc -c CLAUDE.md`)
- Use `@docs/patterns/filename.md` imports for detailed examples
- Supporting files go in `docs/patterns/` (public, committed to git)
- Maximum import depth: 5 hops

## Commands

[Core commands documented inline: ~3KB]

## Architecture

[High-level architecture: ~2KB]

## Error Handling Architecture

- @docs/patterns/error-handling.md

## Dependency Injection Pattern

- @docs/patterns/dependency-injection.md

## Transaction System Architecture

- @docs/patterns/transaction-integration.md

## Testing Strategy

- @docs/patterns/testing-strategy.md
```

**External Documentation Files** (`docs/patterns/`):
- `error-handling.md` (3.2KB) - Three-layer error pattern
- `dependency-injection.md` (4.1KB) - DI across Python/TypeScript
- `testing-strategy.md` (5.7KB) - Test organization
- `transaction-integration.md` (8.9KB) - Git-based rollback system
- `session-resume.md` (6.2KB) - Resume capability architecture
- `workflow-state-management.md` (12.4KB) - State tracking

**Total Documentation**: 27.8KB (CLAUDE.md) + 40.5KB (external) = **68.3KB** of technical documentation, while staying under the 40KB limit.

**Why This Is Non-Obvious**:
1. **Claude Code auto-loads** `@docs/patterns/*.md` references when needed (no manual fetching)
2. **Public documentation** (docs/ committed to git) serves dual purpose: Claude Code context + developer onboarding
3. **Depth limit** (5 hops) prevents infinite loops
4. **Size monitoring** enforced via character count check

#### Layer 4: CLAUDE_CONTEXT.md (Private Context)

**File**: `CLAUDE_CONTEXT.md` (gitignored, ~4KB)

**Purpose**: Separate private/personal context from technical documentation

**Contents**:
```markdown
# CLAUDE_CONTEXT.md

**Purpose**: Private context for Claude Code sessions (gitignored)

## Project Context
- Portfolio project for Anthropic job (Technical Documentation & Content Engineer)
- Job requirements being demonstrated: Full-stack dev, architecture, workflow docs, CI/CD
- Developer profile: Strong Python, learning TypeScript/JavaScript through project
- Technical background implications: Use Claude Code for TS/JS, but critique design decisions

## Scope Control
- Time-bounded project, must ship
- README-driven development philosophy

## Writing Context
- Professional tone (17 years technical writing experience)
- No emoji in developer-facing content (enforced by skills)

## Error Handling
- When blocked, investigate root cause
- Prefer fixing underlying issue over workarounds

## Context Management
- Externalize detailed patterns to docs/patterns/
- Keep CLAUDE.md under 40K characters

## Question Triggers
- Clarify ambiguous requirements before implementing
- Use AskUserQuestion tool for architectural decisions
```

**Why Separate from CLAUDE.md**:
1. **Technical vs Personal**: CLAUDE.md is technical reference, CLAUDE_CONTEXT.md is workflow preferences
2. **Gitignore boundary**: Personal context shouldn't be in public repo
3. **Session initialization**: Claude Code reads both files on startup
4. **Different update cadence**: Technical docs change with architecture, context is stable

### Integration: How It All Works Together

**Session Initialization Flow**:
```
1. User opens Claude Code in worktree
2. Claude Code reads symlinked CLAUDE.md → 27.8KB technical docs
3. Claude Code reads symlinked CLAUDE_CONTEXT.md → 4KB personal context
4. Claude Code loads permissions from symlinked settings.local.json
5. Claude Code discovers skills from symlinked .claude/skills/
6. When code mentions @docs/patterns/*.md, Claude Code auto-loads external docs
```

**Example Permission Flow**:
```
User: "Run pytest to check the tests"

Claude Code attempts: Bash(pytest -v)
↓
settings.local.json deny rule: "Bash(pytest:*::*)"
↓
Blocked with error: "Use uv run pytest instead"

Claude Code retries: Bash(uv run pytest -v)
↓
settings.local.json allow rule: "Bash(uv run pytest:*)"
↓
Executes successfully
```

**Example Context Management Flow**:
```
CLAUDE.md (27.8KB): "Error handling uses three-layer pattern. See @docs/patterns/error-handling.md"
↓
Claude Code encounters error handling question
↓
Auto-loads docs/patterns/error-handling.md (3.2KB)
↓
Understands: Core functions throw → Command wrappers convert to exit codes → Entry point manages process.exit
↓
Applies pattern correctly
```

### What Makes This Configuration Special

1. **Whitelist security model**: Explicit allow/deny/ask for every operation category
2. **Tool interception enforcement**: Blocks bare `python`/`pip`/`pytest`, forces `uv run` prefix
3. **Symlink architecture**: Single source of truth for config across all worktrees
4. **External docs pattern**: 68KB of documentation in 27.8KB CLAUDE.md (stays under 40K limit)
5. **Public/private separation**: CLAUDE.md committed to git, CLAUDE_CONTEXT.md gitignored
6. **Skill integration**: Custom skills (git-workflow) whitelisted and auto-loaded

**Comparison to Standard Approaches**:
- Most projects: No permission configuration (full access or nothing)
- Basic Claude Code setup: Single CLAUDE.md file, no size management
- This approach: Whitelist permissions + external docs + symlinked infrastructure + public/private separation

---

## 3. Direnv Integration: Tool Interception for Workflow Enforcement

### The Problem It Solves

DocImp uses `uv` for Python package management (not bare `pip`). Developers and Claude Code instances must:
- **Always use `uv run`** prefix for Python commands (`uv run pytest`, `uv run ruff`, etc.)
- **Never use bare `pip`** (blocked in favor of `uv add` or `uv pip`)
- **Auto-switch Node versions** per project (via `.nvmrc`)
- **Avoid accidental system Python usage** (must use per-worktree `.venv/`)

**The Challenge**: Changing habits is hard. Developers type `python script.py` by muscle memory, not `uv run python script.py`.

**Traditional Solutions (All Flawed)**:
1. **Documentation only**: "Remember to use `uv run`" → Developers forget
2. **Shell aliases**: `alias python='uv run python'` → Doesn't work in scripts, varies per shell
3. **PATH manipulation**: Remove system Python from PATH → Breaks system tools
4. **Pre-commit hooks**: Catches usage in git commits, but not during development

### The Solution: Tool Interception via Direnv PATH Injection

**Key Insight**: By creating wrapper scripts in `.direnv/bin/` and prepending to PATH, we intercept tool calls **before** they reach the system binaries.

#### The Direnv Configuration (`.envrc`)

```bash
#!/bin/bash

# Create interceptor directory
mkdir -p .direnv/bin

# Python interceptor
cat > .direnv/bin/python <<'PYTHON_EOF'
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
PYTHON_EOF

# pip interceptor (prevent accidental bare pip)
cat > .direnv/bin/pip <<'PIP_EOF'
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
PIP_EOF

# pytest interceptor
cat > .direnv/bin/pytest <<'PYTEST_EOF'
#!/bin/bash
# Intercept bare pytest calls and redirect to uv
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running pytest from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv run pytest" >&2
fi

# Remove .direnv/bin from PATH to prevent recursion
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run pytest "$@"
PYTEST_EOF

# ruff interceptor
cat > .direnv/bin/ruff <<'RUFF_EOF'
#!/bin/bash
# Intercept bare ruff calls and redirect to uv
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running ruff from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv run ruff" >&2
fi

# Remove .direnv/bin from PATH to prevent recursion
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run ruff "$@"
RUFF_EOF

# mypy interceptor
cat > .direnv/bin/mypy <<'MYPY_EOF'
#!/bin/bash
# Intercept bare mypy calls and redirect to uv
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running mypy from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv run mypy" >&2
fi

# Remove .direnv/bin from PATH to prevent recursion
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run mypy "$@"
MYPY_EOF

# Make executables
chmod +x .direnv/bin/python
chmod +x .direnv/bin/python3
chmod +x .direnv/bin/pip
chmod +x .direnv/bin/pytest
chmod +x .direnv/bin/ruff
chmod +x .direnv/bin/mypy

# Add to PATH (highest priority)
PATH_add .direnv/bin

# Auto-add Node bin to PATH based on .nvmrc
# (avoids calling nvm as command, which doesn't work in direnv's restricted context)
if [ -f .nvmrc ]; then
    NODE_VERSION=$(cat .nvmrc)
    # Find matching Node version directory (handles "24" matching "v24.11.0")
    if [ -d "$HOME/.nvm/versions/node" ]; then
        NODE_PATH=$(find "$HOME/.nvm/versions/node" -maxdepth 1 -name "v${NODE_VERSION}*" | head -1)
        if [ -n "$NODE_PATH" ] && [ -d "$NODE_PATH/bin" ]; then
            PATH_add "$NODE_PATH/bin"
        fi
    fi
fi

echo "✓ direnv loaded: Python tools intercepted (python, pip, pytest, ruff, mypy), Node version managed"
```

### How Tool Interception Works

**1. PATH Injection (Highest Priority)**

```bash
PATH_add .direnv/bin
```

**Before**:
```
PATH=/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

**After**:
```
PATH=.direnv/bin:/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

When user types `python script.py`:
1. Shell searches PATH left-to-right
2. Finds `.direnv/bin/python` first (before `/usr/bin/python`)
3. Executes wrapper script
4. Wrapper prints redirection message: `→ Redirecting to: uv run python`
5. Wrapper execs `uv run python script.py`

**2. Recursion Prevention**

**The Problem**: If wrapper calls `uv run python`, and `uv` internally calls `python`, we'd infinite loop.

**The Solution**: Remove `.direnv/bin` from PATH before exec

```bash
# Remove .direnv/bin from PATH to prevent recursion
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run python "$@"
```

**PATH transformation**:
```
Before: .direnv/bin:/usr/bin:/usr/local/bin
After:  /usr/bin:/usr/local/bin
```

Now when `uv` calls `python`, it finds `/usr/bin/python` (system Python), which is what `uv` expects.

**3. Helpful Error Blocking (pip)**

Instead of silently redirecting, `pip` interceptor **blocks and educates**:

```bash
echo "✗ Bare 'pip' detected!" >&2
echo "" >&2
echo "Instead of 'pip install <package>', use:" >&2
echo "  uv add <package>" >&2
echo "" >&2
echo "To sync lockfile:" >&2
echo "  uv pip sync requirements-dev.lock" >&2
exit 1
```

**Example Session**:
```
$ pip install requests
✗ Bare 'pip' detected!

Instead of 'pip install <package>', use:
  uv add <package>

To sync lockfile:
  uv pip sync requirements-dev.lock

$ uv add requests
✓ Added requests==2.31.0
```

**Why Block Instead of Redirect**:
- `pip install` outside `uv` breaks lockfile consistency
- Users must learn `uv add` (project-aware dependency management)
- Error message teaches correct workflow

**4. Subdirectory Warning System**

**The Problem**: Running `uv run pytest` from `cli/` subdirectory (which has its own `pyproject.toml`) can create a local `.venv/` instead of using root `.venv/`.

**The Solution**: Detect subdirectory execution and warn

```bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
CURRENT=$(pwd)

if [ -f "pyproject.toml" ] && [ "$CURRENT" != "$ROOT" ]; then
  echo "Warning: Running pytest from subdirectory with pyproject.toml ($CURRENT)" >&2
  echo "   May cause errors or create local .venv/. To avoid: cd $ROOT && uv run pytest" >&2
fi
```

**Example Warning**:
```
$ cd cli
$ pytest
Warning: Running pytest from subdirectory with pyproject.toml (/path/to/docimp/cli)
   May cause errors or create local .venv/. To avoid: cd /path/to/docimp && uv run pytest
→ Redirecting to: uv run pytest
```

**5. Node Version Auto-Switching**

**.nvmrc File**:
```
24.11.0
```

**Direnv Logic**:
```bash
if [ -f .nvmrc ]; then
    NODE_VERSION=$(cat .nvmrc)
    # Find matching Node version directory
    if [ -d "$HOME/.nvm/versions/node" ]; then
        NODE_PATH=$(find "$HOME/.nvm/versions/node" -maxdepth 1 -name "v${NODE_VERSION}*" | head -1)
        if [ -n "$NODE_PATH" ] && [ -d "$NODE_PATH/bin" ]; then
            PATH_add "$NODE_PATH/bin"
        fi
    fi
fi
```

**How It Works**:
1. Reads `.nvmrc` → "24.11.0"
2. Finds matching directory in `~/.nvm/versions/node/` → `v24.11.0/`
3. Adds `v24.11.0/bin/` to PATH
4. Now `node`, `npm`, `npx` all point to correct version

**Why Not Call `nvm use`**:
- `nvm` is a shell function, not a binary (doesn't work in direnv's restricted context)
- Direct PATH manipulation is faster and more reliable
- Handles version prefix matching ("24" matches "v24.11.0")

### Session Startup Flow

**1. User Opens Terminal in Worktree**

```bash
$ cd /path/to/.docimp-wt/issue-260/
direnv: loading ~/Documents/Code/Polygot/docimp/.envrc
✓ direnv loaded: Python tools intercepted (python, pip, pytest, ruff, mypy), Node version managed
direnv: export ~PATH
```

**2. Direnv Executes `.envrc`**
- Creates `.direnv/bin/` directory
- Generates 6 wrapper scripts (python, python3, pip, pytest, ruff, mypy)
- Makes them executable
- Prepends `.direnv/bin/` to PATH
- Adds Node version to PATH

**3. Tools Now Intercepted**

```bash
$ which python
.direnv/bin/python

$ which pip
.direnv/bin/pip

$ which pytest
.direnv/bin/pytest

$ which node
/Users/nik/.nvm/versions/node/v24.11.0/bin/node
```

**4. Developer Types Command**

```bash
$ pytest -v
→ Redirecting to: uv run pytest
============== test session starts ==============
...
```

**5. Claude Code Permission Check**

```
Claude Code attempts: Bash(pytest -v)
↓
settings.local.json deny: "Bash(pytest:*::*)"
↓
Blocked: "Bare pytest not allowed, use uv run"

Claude Code retries: Bash(uv run pytest -v)
↓
settings.local.json allow: "Bash(uv run pytest:*)"
↓
Executes successfully
```

### Per-Worktree Environment Isolation

**Directory Structure**:
```
docimp/  (main worktree)
├── .envrc                    ← direnv config (shared via git)
├── .direnv/                  ← Generated wrappers (gitignored)
│   └── bin/
│       ├── python
│       ├── pip
│       ├── pytest
│       ├── ruff
│       └── mypy
├── .venv/                    ← Per-worktree Python environment
├── .nvmrc                    ← Node version specification
└── node_modules/             ← Per-worktree Node modules

.docimp-wt/issue-260/  (feature worktree)
├── .envrc                    ← Same file via git
├── .direnv/                  ← Separate instance (worktree-specific)
│   └── bin/
│       ├── python
│       ├── pip
│       ├── pytest
│       ├── ruff
│       └── mypy
├── .venv/                    ← Separate .venv (no lock contention)
├── .nvmrc                    ← Same version spec
└── node_modules/             ← Separate node_modules (dependency testing)
```

**Why Separate `.direnv/` per Worktree**:
- `.envrc` regenerates wrappers on `direnv allow`
- Each worktree has independent PATH prepending
- Wrappers point to worktree-specific `.venv/`

**Why Separate `.venv/` per Worktree**:
- Prevents lock contention when running `uv run pytest` in parallel
- Allows testing different dependency versions across worktrees
- uv-managed Python (containerized, not system Python)

### What Makes This Integration Special

1. **Transparent interception**: Developers type familiar commands (`pytest`), get correct behavior (`uv run pytest`)
2. **Educational errors**: `pip` blocked with helpful message showing correct alternative
3. **Subdirectory safety**: Warns when running from wrong directory (prevents local `.venv/` creation)
4. **Node version auto-switching**: Changes Node version automatically based on `.nvmrc`
5. **Recursion prevention**: Wrappers don't interfere with underlying tool execution
6. **Per-worktree isolation**: Each worktree has independent environment setup
7. **Dual enforcement**: direnv interception + Claude Code permission whitelist

**Comparison to Standard Approaches**:
- Most projects: Documentation ("Remember to use X instead of Y")
- Shell aliases: Brittle, shell-specific, doesn't work in scripts
- This approach: Transparent PATH interception + helpful errors + per-worktree isolation

**Real-World Impact**:
- **Zero `pip install` accidents** (100% enforcement)
- **Zero wrong Python version usage** (wrappers always call `uv run`)
- **Parallel worktree development** (no lock contention or .venv conflicts)
- **Automatic Node version switching** (no manual `nvm use` required)

---

## Conclusion: Why These Examples Matter

These three infrastructure components demonstrate **non-obvious solutions to real development challenges**:

### 1. Git Hooks + Worktree Workflow
**Problem**: Parallel development without branch protection chaos
**Solution**: Path-based detection + change transfer logic + complete orchestration
**Impact**: Multiple Claude Code instances working simultaneously on different features

### 2. Claude Code Configuration
**Problem**: Context window limits + permission management + infrastructure sharing
**Solution**: Whitelist permissions + external docs pattern + symlink architecture
**Impact**: 68KB of documentation in 27.8KB CLAUDE.md, shared across all worktrees

### 3. Direnv Integration
**Problem**: Enforcing workflow (uv run prefix) without breaking existing habits
**Solution**: Transparent PATH interception + helpful errors + per-worktree isolation
**Impact**: 100% `uv run` compliance, zero manual environment management

**Common Themes Across All Three**:
- **Automation over discipline**: Don't rely on developers remembering rules
- **Educational errors**: Error messages teach the correct workflow
- **Isolation**: Per-worktree environments prevent conflicts
- **Transparency**: Infrastructure works invisibly until it prevents mistakes
- **Single source of truth**: Symlinks and shared configs eliminate synchronization issues

These patterns are **transferable to other projects** facing similar challenges with parallel development, context management, and workflow enforcement.
