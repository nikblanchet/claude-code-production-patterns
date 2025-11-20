# Infrastructure Documentation: Claude Code Configuration

## Overview

DocImp's Claude Code configuration uses a **multi-layered architecture** to manage permissions, share infrastructure across worktrees, and keep documentation under the 40K character limit:

1. **Permission Whitelist** - Explicit allow/deny/ask for every operation
2. **Symlink Infrastructure** - Single source of truth across all worktrees
3. **External Documentation Pattern** - 68KB total docs in 27.8KB CLAUDE.md
4. **Public/Private Separation** - Technical docs (committed) vs context (gitignored)

---

## Layer 1: Permission Whitelist

### File Location

**File**: `/Users/nik/Code/Polygot/.docimp-shared/.claude/settings.local.json`

**Shared via symlinks**:
```
docimp/.claude/settings.local.json               → .docimp-shared/.claude/settings.local.json
.docimp-wt/issue-260/.claude/settings.local.json → .docimp-shared/.claude/settings.local.json
```

**Why symlinked**: Single source of truth. Update permissions once, applies to all worktrees instantly.

### Permission Structure

```json
{
  "permissions": {
    "allow": [...],    // Auto-approved operations
    "deny": [...],     // Explicitly blocked operations
    "ask": [...],      // Requires user confirmation
    "additionalDirectories": [...]  // Extended file access
  }
}
```

### Permission Categories

#### Bash Commands (Allow)

**Core Development Tools**:
```json
"Bash(uv run pytest:*)",
"Bash(uv run ruff:*)",
"Bash(uv run mypy:*)",
"Bash(npm run test:*)",
"Bash(npm run lint)",
"Bash(npm run build)"
```

**Pattern Matching**:
- `:*` suffix = allow any arguments
- `::*` suffix = deny pattern (see below)

**Example**:
- `Bash(uv run pytest:*)` allows: `uv run pytest -v`, `uv run pytest analyzer/tests/`
- `Bash(pytest:*::*)` denies: Bare `pytest` without `uv run` prefix

**Git Operations**:
```json
"Bash(git add:*)",
"Bash(git commit:*)",
"Bash(git push:*)",
"Bash(git checkout:*)",
"Bash(git fetch:*)",
"Bash(git log:*)",
"Bash(git worktree:*)",
"Bash(git diff:*)"
```

**GitHub CLI**:
```json
"Bash(gh pr create:*)",
"Bash(gh pr view:*)",
"Bash(gh pr list:*)",
"Bash(gh issue create:*)",
"Bash(gh issue list:*)",
"Bash(gh issue view:*)",
"Bash(gh run list:*)",
"Bash(gh run view:*)"
```

**DocImp Commands**:
```json
"Bash(docimp analyze:*)",
"Bash(docimp audit:*)",
"Bash(docimp plan:*)",
"Bash(docimp improve:*)",
"Bash(docimp status:*)"
```

#### Bash Commands (Deny)

**Blocked: Bare Python Tools** (forces `uv run` prefix):
```json
"Bash(python:*::*)",
"Bash(python3:*::*)",
"Bash(pytest:*::*)",
"Bash(ruff:*::*)",
"Bash(mypy:*::*)",
"Bash(pip:*::*)"
```

**Why deny with `::*` pattern**:
- Prevents Claude Code from running bare `python`, `pip`, `pytest`
- Forces use of `uv run` prefix (project environment isolation)
- Coordinated with direnv interception (double enforcement)

**Example Blocked Commands**:
- ✗ `python script.py` → Blocked, suggests `uv run python script.py`
- ✗ `pip install requests` → Blocked, suggests `uv add requests`
- ✗ `pytest -v` → Blocked, suggests `uv run pytest -v`

#### Bash Commands (Ask)

**Requires user approval** (package management):
```json
"Bash(uv run python:*)",
"Bash(uv pip:*)",
"Bash(uv add:*)"
```

**Why ask instead of allow**:
- Package management changes lockfiles (requires awareness)
- Running arbitrary Python code (`uv run python -c "..."`) needs review
- User must explicitly approve dependency additions

#### File Operations (Allow)

**Full project access**:
```json
"Glob(./**)",
"Grep(./**)",
"LS(./**)",
"Read(./**)"
```

**Extended directories**:
```json
"Read(//Users/nik/Documents/Code/Polygot/.docimp-shared/**)",
"Read(//Users/nik/Documents/Code/Polygot/.docimp-wt/**)",
"Read(//Users/nik/Code/repos/custom-claude-skills/**)",
"Read(//private/tmp/**)"
```

**Why extended access**:
- `.docimp-shared/`: Read CLAUDE.md, skills, planning docs
- `.docimp-wt/**`: Access all feature worktrees
- `custom-claude-skills/`: Read official and custom skill sources
- `/private/tmp/**`: Temporary files (e.g., test fixtures)

#### Skills (Allow)

```json
"Skill(git-workflow)",
"Skill(development-standards)",
"Skill(exhaustive-testing)",
"Skill(handle-deprecation-warnings)",
"Skill(dependency-management)",
"Skill(cli-ux-colorful)",
"Skill(skill-creator)",
"Skill(access-skill-resources)"
```

**Skill Descriptions**:
- `git-workflow`: Worktree creation, branch management
- `development-standards`: No emoji, modern Python features
- `exhaustive-testing`: Comprehensive test coverage
- `handle-deprecation-warnings`: Address immediately, never suppress
- `dependency-management`: Use quality dependencies freely (conda → pip)
- `cli-ux-colorful`: Terminal colors, syntax highlighting
- `skill-creator`: Guide for creating effective skills

#### Web Access (Allow)

**Domain-restricted**:
```json
"WebFetch(domain:github.com)",
"WebFetch(domain:raw.githubusercontent.com)",
"WebFetch(domain:stackoverflow.com)",
"WebFetch(domain:docs.astral.sh)",
"WebFetch(domain:pypi.org)",
"WebFetch(domain:claude.com)",
"WebSearch"
```

**Why domain restrictions**:
- Limit exposure to trusted documentation sources
- Prevent arbitrary URL fetching
- WebSearch allowed for general queries

### Example Permission Flow

**Scenario 1: Claude Code attempts bare pytest**
```
User: "Run the tests"

Claude Code attempts: Bash(pytest -v)
↓
settings.local.json: "Bash(pytest:*::*)" in deny list
↓
Permission denied: "Command blocked by permissions. Try: uv run pytest -v"
↓
Claude Code retries: Bash(uv run pytest -v)
↓
settings.local.json: "Bash(uv run pytest:*)" in allow list
↓
Executes successfully
```

**Scenario 2: Claude Code attempts package installation**
```
User: "Install the requests library"

Claude Code attempts: Bash(uv add requests)
↓
settings.local.json: "Bash(uv add:*)" in ask list
↓
User prompt: "Allow: uv add requests? [Y/n]"
↓
User approves: Y
↓
Executes: uv add requests
```

**Scenario 3: Claude Code reads external skill**
```
Claude Code needs: Read git-workflow skill source

Attempts: Read(//Users/nik/Code/repos/custom-claude-skills/project-scope/docimp/git-workflow/SKILL.md)
↓
settings.local.json: "Read(//Users/nik/Code/repos/custom-claude-skills/**)" in allow list
↓
Executes successfully (no prompt)
```

---

## Layer 2: Symlink Infrastructure

### Directory Structure

```
.docimp-shared/  (gitignored, shared across all worktrees)
├── .claude/
│   ├── settings.local.json  ← Permission whitelist
│   ├── skills/              ← Custom skills
│   │   └── git-workflow/    → external symlink to custom-claude-skills repo
│   └── agents/              ← Custom agents
├── .planning/
│   ├── PLAN.md              ← 31-step execution plan (gitignored)
│   └── development-workflow.md
├── .scratch/                ← Temporary working files
├── CLAUDE.md                ← Technical documentation (27.8KB, committed to git)
└── CLAUDE_CONTEXT.md        ← Private project context (gitignored)

docimp/  (main worktree)
├── .claude/                 → symlink to ../.docimp-shared/.claude/
├── CLAUDE.md                → symlink to ../.docimp-shared/CLAUDE.md
├── WARP.md                  → symlink to ../.docimp-shared/CLAUDE.md (alias)
├── CLAUDE_CONTEXT.md        → symlink to ../.docimp-shared/CLAUDE_CONTEXT.md
├── .planning/               → symlink to ../.docimp-shared/.planning/
└── .scratch/                → symlink to ../.docimp-shared/.scratch/

.docimp-wt/issue-260/  (feature worktree)
├── .claude/                 → symlink to ../../.docimp-shared/.claude/
├── CLAUDE.md                → symlink to ../../.docimp-shared/CLAUDE.md
├── WARP.MD                  → symlink to ../../.docimp-shared/CLAUDE.md
├── CLAUDE_CONTEXT.md        → symlink to ../../.docimp-shared/CLAUDE_CONTEXT.md
├── .planning/               → symlink to ../../.docimp-shared/.planning/
└── .scratch/                → symlink to ../../.docimp-shared/.scratch/
```

### Symlink Creation (Automated)

**In create_worktree.py**:
```python
def create_symlink(target: str, link_name: Path) -> None:
    """Create a symlink and print success message."""
    # Check if link already exists
    if link_name.exists() or link_name.is_symlink():
        if link_name.is_symlink() and link_name.readlink() == Path(target):
            print_info(f"  Symlink already exists: {link_name.name}")
            return
        exit_with_error(f"File already exists at {link_name}, refusing to overwrite")

    # Create the symlink
    try:
        link_name.symlink_to(target)
        print_success(f"✓ Created symlink: {link_name.name}")
    except OSError as e:
        exit_with_error(f"Failed to create symlink {link_name.name}: {e}")

# Root-level symlinks
create_symlink('../../.docimp-shared/CLAUDE.md', worktree_path / 'CLAUDE.md')
create_symlink('../../.docimp-shared/CLAUDE.md', worktree_path / 'WARP.md')
create_symlink('../../.docimp-shared/CLAUDE_CONTEXT.md', worktree_path / 'CLAUDE_CONTEXT.md')
create_symlink('../../.docimp-shared/.planning', worktree_path / '.planning')
create_symlink('../../.docimp-shared/.scratch', worktree_path / '.scratch')

# .claude directory symlinks
claude_dir = worktree_path / '.claude'
claude_dir.mkdir(exist_ok=True)
create_symlink('../../../.docimp-shared/.claude/skills', claude_dir / 'skills')
create_symlink('../../../.docimp-shared/.claude/settings.local.json', claude_dir / 'settings.local.json')
```

**Symlink Validation**:
- Checks if symlink already exists and points to correct target (idempotent)
- Refuses to overwrite existing files
- Creates parent directories as needed
- Reports success/failure clearly

### Why Symlinks Instead of Copies

**Problem with copies**:
1. **Synchronization**: Changes to CLAUDE.md in one worktree don't propagate
2. **Drift**: Worktrees diverge over time (different configs, outdated docs)
3. **Maintenance**: Update permissions → must copy to all worktrees manually

**Benefits of symlinks**:
1. **Single source of truth**: Update CLAUDE.md once → applies everywhere instantly
2. **No synchronization**: No risk of worktrees diverging
3. **Git-friendly**: Symlinks committed to git, point to gitignored shared directory
4. **Automatic propagation**: New worktrees get current config via symlinks

**Example**:
```bash
# Update CLAUDE.md in .docimp-shared/
cd /Users/nik/Code/Polygot/.docimp-shared
vim CLAUDE.md  # Add new command documentation

# Automatically visible in all worktrees
cd /Users/nik/Code/Polygot/docimp
cat CLAUDE.md  # Shows updated content (via symlink)

cd /Users/nik/Documents/Code/Polygot/.docimp-wt/issue-260
cat CLAUDE.md  # Shows updated content (via symlink)
```

---

## Layer 3: CLAUDE.md External Documentation Pattern

### The 40K Character Limit Challenge

**Constraint**: CLAUDE.md must stay under 40,000 characters

**Current size**: 27,792 bytes (27.8 KB) - **69.5% of limit used**

**Check size**:
```bash
wc -c CLAUDE.md
# Output: 27792 CLAUDE.md
```

### The External Import Pattern

**Problem**: DocImp has complex architecture requiring extensive documentation. Inline documentation would exceed 40KB.

**Solution**: Use `@docs/patterns/*.md` imports for detailed explanations.

**CLAUDE.md Structure**:
```markdown
# CLAUDE.md

**Character Limit: 40.0k characters (absolute maximum) for CLAUDE.md specifically.**

## Commands

[Core commands documented inline: ~3KB]
docimp analyze ./src
docimp audit ./src
docimp plan ./src
docimp improve ./src
docimp status

## Architecture

[High-level architecture: ~2KB]
TypeScript CLI ↔ Python Engine ↔ JavaScript Plugins

## Error Handling Architecture

**Three-layer pattern**: Core functions (throw) → Command wrappers (exit codes) → Entry point (process.exit)

- @docs/patterns/error-handling.md

## Dependency Injection Pattern

**Core Principle**: All dependencies passed as required parameters

- @docs/patterns/dependency-injection.md

## Transaction System Architecture

**Side-car Git repository** in `.docimp/state/.git` for rollback capability

- @docs/patterns/transaction-integration.md

## Testing Strategy

**Complete testing guide** with running tests, writing tests, performance benchmarks

- @docs/patterns/testing-strategy.md
```

**External Documentation Files**:

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

### How Auto-Loading Works

**Claude Code behavior**:
1. Reads CLAUDE.md on session start (27.8KB loaded into context)
2. When code mentions `@docs/patterns/error-handling.md`, Claude Code auto-loads it
3. Loaded content added to context window on-demand
4. Maximum import depth: 5 hops (prevents infinite loops)

**Example Session**:
```
User: "How should I handle errors in the new command?"

Claude Code thinks:
- CLAUDE.md mentions @docs/patterns/error-handling.md
- Auto-load external doc
- Read: "Core functions throw → Command wrappers convert to exit codes → Entry point manages process.exit"
- Apply pattern to new command

Claude Code responds: "Use the three-layer error pattern:
1. Core function throws descriptive error
2. Command wrapper catches, converts to exit code
3. Entry point (index.ts) handles process.exit"
```

### Maintenance: Adding New External Docs

**When CLAUDE.md approaches 35-38KB**:
```bash
# Check current size
wc -c CLAUDE.md
# Output: 37500 CLAUDE.md  ← Approaching limit

# Identify verbose sections
# Example: "Plugin System" section is 4KB

# Create external doc
cd docs/patterns
vim plugin-system.md

# Move content from CLAUDE.md to plugin-system.md
# [4KB of plugin documentation moved]

# Update CLAUDE.md with import
vim ../../CLAUDE.md
# Replace 4KB section with:
## Plugin System
- @docs/patterns/plugin-system.md

# Commit both files
git add CLAUDE.md docs/patterns/plugin-system.md
git commit -m "Externalize plugin system documentation to stay under 40K limit"

# Verify size
wc -c CLAUDE.md
# Output: 33792 CLAUDE.md  ← Back under limit
```

---

## Layer 4: CLAUDE_CONTEXT.md (Private Context)

### File Location

**File**: `/Users/nik/Code/Polygot/.docimp-shared/CLAUDE_CONTEXT.md`

**Status**: **Gitignored** (not committed to public repository)

**Shared via symlinks**: Same pattern as CLAUDE.md

### Purpose: Public vs Private Separation

**CLAUDE.md** (public, committed to git):
- Technical documentation
- Architecture details
- Commands, patterns, workflows
- Shared with all contributors

**CLAUDE_CONTEXT.md** (private, gitignored):
- Personal workflow preferences
- Project context (job application, portfolio piece)
- Developer background
- Writing style preferences
- Error handling philosophy

### Contents Structure

```markdown
# CLAUDE_CONTEXT.md

**Purpose**: Private context for Claude Code sessions (gitignored)

## Project Context
- Portfolio project for Anthropic job (Technical Documentation & Content Engineer)
- Job requirements being demonstrated:
  - Full-stack development (Python + TypeScript/JavaScript)
  - Architecture design and documentation
  - Workflow documentation and automation
  - CI/CD pipeline setup
  - Open-source project management
- Developer profile:
  - Strong Python background (17 years)
  - Learning TypeScript/JavaScript through this project
  - 17 years technical writing experience

## Development Philosophy
- **README-driven development**: Document before implementing
- **Test-first validation**: Write tests, then implementation
- **Scope control**: Time-bounded project, must ship

## Writing Context
- **Professional tone**: No marketing hype, no over-selling
- **No emoji in developer content**: Enforced by development-standards skill
- **Precision**: Specific over vague (e.g., "Use 2-space indentation" not "consistent formatting")

## Error Handling
- When blocked, investigate root cause
- Prefer fixing underlying issue over workarounds
- Use AskUserQuestion tool for ambiguous requirements

## Context Management
- Externalize detailed patterns to docs/patterns/
- Keep CLAUDE.md under 40K characters
- Use `@` imports for detailed documentation
```

### Why Separate Files

**CLAUDE.md** (public):
- **Audience**: All contributors, users, interviewers
- **Content**: Technical facts, architecture, commands
- **Lifecycle**: Changes with architecture updates
- **Version control**: Committed to git

**CLAUDE_CONTEXT.md** (private):
- **Audience**: Claude Code only (private context)
- **Content**: Personal preferences, project goals, workflow style
- **Lifecycle**: Stable (rarely changes)
- **Version control**: Gitignored (personal, not public)

**Example Distinction**:

| Topic | CLAUDE.md | CLAUDE_CONTEXT.md |
|-------|-----------|-------------------|
| How to run tests | `uv run pytest -v` | "Test-first validation: write tests before implementation" |
| Error handling pattern | Three-layer (throw → exit code → process.exit) | "Investigate root cause, prefer fixing over workarounds" |
| Code style | ruff (8 rule groups), ESLint (7 plugins) | "No emoji in developer content (enforced by skill)" |
| Project architecture | Three-layer polyglot (Python ↔ TypeScript ↔ JavaScript) | "Portfolio piece demonstrating full-stack + CI/CD for Anthropic job" |

---

## Session Initialization Flow

### What Happens When Claude Code Starts

**Step 1: Load symlinked CLAUDE.md**
```
Claude Code opens worktree
↓
Reads CLAUDE.md (via symlink)
↓
Loads 27.8KB technical documentation into context
```

**Step 2: Load symlinked CLAUDE_CONTEXT.md**
```
Reads CLAUDE_CONTEXT.md (via symlink)
↓
Loads 4KB private context into context
↓
Understands project goals, developer preferences
```

**Step 3: Load permissions**
```
Reads .claude/settings.local.json (via symlink)
↓
Loads 256 allow rules, 6 deny rules, 3 ask rules
↓
Permission whitelist active
```

**Step 4: Discover skills**
```
Reads .claude/skills/ (via symlink)
↓
Discovers git-workflow, development-standards, etc.
↓
Skills available for invocation
```

**Step 5: On-demand external doc loading**
```
User asks question about error handling
↓
CLAUDE.md mentions @docs/patterns/error-handling.md
↓
Claude Code auto-loads error-handling.md (3.2KB)
↓
Applies three-layer error pattern to answer
```

---

## Configuration Updates

### Updating Permissions

**File**: `.docimp-shared/.claude/settings.local.json`

**Add new allowed command**:
```json
{
  "permissions": {
    "allow": [
      "Bash(docimp analyze:*)",
      "Bash(docimp new-command:*)"  // ← Add new command
    ]
  }
}
```

**Propagates immediately** to all worktrees (symlinked).

### Updating CLAUDE.md

**File**: `.docimp-shared/CLAUDE.md`

**Add new section**:
```markdown
## New Feature Documentation

[Inline documentation: ~2KB]

For detailed implementation, see:
- @docs/patterns/new-feature.md
```

**Create external doc**:
```bash
vim docs/patterns/new-feature.md
# [Write detailed documentation]

git add CLAUDE.md docs/patterns/new-feature.md
git commit -m "Document new feature (externalized to stay under 40K)"
```

**Visible immediately** in all worktrees (symlinked).

### Updating CLAUDE_CONTEXT.md

**File**: `.docimp-shared/CLAUDE_CONTEXT.md`

**Update private context**:
```markdown
## Project Context
- Portfolio project for Anthropic job ← updated
- Demonstrates: Full-stack dev, CI/CD, documentation, open-source management
```

**Not committed to git** (gitignored). Changes visible immediately in all worktrees.

---

## Troubleshooting

### Problem: Symlink broken (points to non-existent file)

**Symptom**: Claude Code can't find CLAUDE.md

**Diagnosis**:
```bash
ls -la CLAUDE.md
# Output: CLAUDE.md -> ../.docimp-shared/CLAUDE.md (broken)

# Check if target exists
ls ../.docimp-shared/CLAUDE.md
# Output: No such file or directory
```

**Fix**:
```bash
# Remove broken symlink
rm CLAUDE.md

# Recreate symlink to correct location
ln -s ../.docimp-shared/CLAUDE.md CLAUDE.md
```

### Problem: Permission denied for allowed command

**Symptom**: Claude Code blocked when running `uv run pytest`

**Diagnosis**:
```bash
# Check settings.local.json
cat .claude/settings.local.json | jq '.permissions.allow' | grep pytest

# Expected: "Bash(uv run pytest:*)"
```

**Fix**:
```bash
# Edit settings.local.json
vim .claude/settings.local.json

# Add to allow list
"Bash(uv run pytest:*)"
```

### Problem: CLAUDE.md changes not visible

**Symptom**: Updated CLAUDE.md in `.docimp-shared/`, but worktree shows old content

**Diagnosis**:
```bash
cd /path/to/worktree
ls -la CLAUDE.md

# Check if it's a symlink
# Expected: CLAUDE.md -> ../../.docimp-shared/CLAUDE.md

# If it's a regular file (not symlink), that's the problem
```

**Fix**:
```bash
# Remove regular file
rm CLAUDE.md

# Create symlink
ln -s ../../.docimp-shared/CLAUDE.md CLAUDE.md
```

---

## Summary

**Claude Code Configuration Architecture**:
- **4 layers**: Permission whitelist + Symlink infrastructure + External docs + Public/private separation
- **Single source of truth**: Symlinks ensure consistency across all worktrees
- **Context window management**: 68KB total docs while staying under 40KB CLAUDE.md limit
- **Security model**: Explicit allow/deny for every operation category

**Key Files**:
- `.docimp-shared/.claude/settings.local.json` - Permission whitelist (256 allow, 6 deny, 3 ask)
- `.docimp-shared/CLAUDE.md` - Technical documentation (27.8KB, committed to git)
- `.docimp-shared/CLAUDE_CONTEXT.md` - Private context (4KB, gitignored)
- `docs/patterns/*.md` - External documentation (40.5KB, committed to git)

**Key Patterns**:
- **Symlinks**: Single source of truth, no synchronization issues
- **External imports**: `@docs/patterns/*.md` auto-loaded on-demand
- **Public/private separation**: Technical facts (git) vs personal preferences (gitignored)
- **Permission whitelist**: Explicit allow/deny/ask for maximum control

**Workflow**:
- ✓ Update CLAUDE.md once → visible in all worktrees instantly
- ✓ Add permission → applies to all Claude Code instances immediately
- ✓ External docs loaded on-demand (keeps CLAUDE.md under 40KB)
- ✓ Private context separated from public technical docs

**Next Steps**: See `INFRASTRUCTURE-DOCS_4-Quality-Checks.md` for quality enforcement configuration (ruff, ESLint, Prettier, pytest, Jest).
