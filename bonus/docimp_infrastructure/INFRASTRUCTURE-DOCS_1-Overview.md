# Infrastructure Documentation: Overview

## Executive Summary

DocImp has a comprehensive, multi-layered development infrastructure spanning git hooks, Claude Code configuration, quality checks, CI/CD, development workflow automation, testing infrastructure, and documentation patterns. The infrastructure is designed to support **polyglot development** (Python, TypeScript, JavaScript) with clean separation of concerns, automated quality gates, and worktree-based parallel development.

## Infrastructure Philosophy

### Core Principles

1. **Automation Over Discipline**
   - Don't rely on developers remembering rules
   - Use tool interception, git hooks, and CI/CD to enforce correctness
   - Make the correct path the easy path

2. **Worktree-Based Parallel Development**
   - Main worktree protected (read-only reference state)
   - Feature worktrees for all development work
   - Per-worktree environment isolation (Python .venv, Node node_modules)
   - Multiple Claude Code instances working simultaneously

3. **Educational Infrastructure**
   - Error messages teach correct workflow
   - Helpful redirects instead of silent failures
   - Documentation generated from infrastructure code

4. **Single Source of Truth**
   - Symlinked configurations (no duplication)
   - Shared infrastructure directory (.docimp-shared/)
   - External documentation imports (@docs/patterns/)

5. **Polyglot Quality Standards**
   - Python: ruff (8 rule groups), mypy, pytest
   - TypeScript: ESLint (7 plugins), Prettier, Jest, strict tsconfig
   - JavaScript: Real JSDoc type-checking via TypeScript compiler

## Project Structure

```
docimp/  (main worktree - protected)
├── .git/hooks/              # Branch protection hooks
├── .husky/                  # Per-worktree hook coordination
├── .envrc                   # direnv tool interception
├── .claude/                 # Symlinks to shared infrastructure
│   ├── skills/              → .docimp-shared/.claude/skills/
│   └── settings.local.json  → .docimp-shared/.claude/settings.local.json
├── CLAUDE.md                → .docimp-shared/CLAUDE.md (27.8KB technical docs)
├── CLAUDE_CONTEXT.md        → .docimp-shared/CLAUDE_CONTEXT.md (private context)
├── .planning/               → .docimp-shared/.planning/
├── cli/                     # TypeScript CLI
│   ├── src/
│   ├── package.json
│   ├── tsconfig.json
│   ├── eslint.config.mjs
│   └── jest.config.js
├── analyzer/                # Python analysis engine
│   ├── src/
│   ├── tests/
│   ├── pyproject.toml
│   └── pytest.ini
├── plugins/                 # JavaScript validation plugins
├── docs/                    # Public documentation
│   ├── patterns/            # External docs for CLAUDE.md imports
│   ├── user-guide/
│   └── quality-control/
├── .github/workflows/       # CI/CD
│   └── ci.yml
└── test-samples/            # E2E test scripts

.docimp-shared/  (shared across all worktrees, gitignored)
├── .claude/
│   ├── settings.local.json  # Permission whitelist
│   ├── skills/              # Custom skills (git-workflow, etc.)
│   └── agents/              # Custom agents
├── .planning/
│   └── PLAN.md              # 31-step execution plan
├── .scratch/                # Temporary working files
├── CLAUDE.md                # Technical documentation (27.8KB)
└── CLAUDE_CONTEXT.md        # Private project context

.docimp-wt/  (feature worktrees)
├── issue-260/
│   ├── .claude/             → symlinks to .docimp-shared/
│   ├── .venv/               # Per-worktree Python environment
│   ├── cli/node_modules/    # Per-worktree Node modules
│   └── .direnv/             # Per-worktree tool interceptors
├── issue-275/
└── issue-293/
```

## Infrastructure Layers

### Layer 1: Git Workflow Protection

- **Pre-commit hook**: Blocks commits to main branch in main worktree
- **Post-checkout hook**: Prevents branch checkouts other than main in main worktree
- **Husky integration**: Per-worktree hooks (lint-staged, formatters)
- **Worktree creation script**: Automated setup with symlinks, hooks, deps

**Key Pattern**: Path-based detection (`/.docimp-wt/` in path) determines worktree identity

### Layer 2: Claude Code Configuration

- **Permission whitelist**: 256 allow rules, 6 deny rules, 3 ask rules
- **Symlinked infrastructure**: Single source of truth across all worktrees
- **External docs pattern**: 68KB total docs while staying under 40KB CLAUDE.md limit
- **Public/private separation**: CLAUDE.md (git) vs CLAUDE_CONTEXT.md (gitignored)

**Key Pattern**: `@docs/patterns/*.md` imports for detailed documentation

### Layer 3: Tool Interception (direnv)

- **Python tools**: Intercepts python, pip, pytest, ruff, mypy → redirects to `uv run`
- **Node version**: Auto-switches based on `.nvmrc` (no manual `nvm use`)
- **Helpful errors**: Blocks `pip` with educational message
- **Per-worktree isolation**: Each worktree has independent `.direnv/bin/`

**Key Pattern**: PATH injection with highest priority + recursion prevention

### Layer 4: Quality Enforcement

#### Python Quality
- **ruff**: 8 rule groups (E, F, DTZ, UP, PTH, I, SIM, PERF, YTT)
- **mypy**: Strict type checking (Python 3.13+)
- **pytest**: 46+ test files, markers (unit, integration, slow)

#### TypeScript/JavaScript Quality
- **ESLint**: 7 plugins (eslint, ts-eslint, jsdoc, unicorn, n, promise, import)
- **Prettier**: Consistent formatting (2-space, single quotes, LF)
- **Jest**: ESM preset, sequential execution (shared state)
- **TypeScript**: checkJs:true for real JSDoc validation

### Layer 5: CI/CD Pipeline

- **5 GitHub Actions jobs**: Python tests, TypeScript tests, Integration, Module Systems, Workflow Validation
- **Parallel execution**: Python + TypeScript jobs run simultaneously
- **Comprehensive coverage**: Lint, format check, type check, build, test, integration
- **Caching**: npm cache + uv cache for faster builds

### Layer 6: Development Workflow

- **create_worktree.py**: 1067-line orchestration script
  - Detects uncommitted and unpushed changes
  - Interactive prompts with smart defaults
  - Creates symlinks, installs hooks, sets up venvs
  - Per-worktree Python environment (uv-managed)
  - Per-worktree Node environment (nvm-managed)

## Key Metrics

| Metric | Value |
|--------|-------|
| CLAUDE.md size | 27,792 bytes (27.8 KB) |
| CLAUDE.md limit | 40,000 bytes (absolute max) |
| External doc files | 6 files in `docs/patterns/` |
| Total documentation | 68.3 KB (27.8KB + 40.5KB external) |
| Python test files | 46+ in `analyzer/tests/` |
| TypeScript test files | 27+ in `cli/src/__tests__/` |
| E2E test scripts | 5 shell scripts |
| GitHub Actions jobs | 5 (parallel: 3, sequential: 2) |
| ESLint plugins | 7 |
| Ruff rule groups | 8 |
| Node version | 24.11.0 (pinned exact) |
| Python version | 3.13 (minimum) |
| TypeScript target | ES2024 |
| Module system | NodeNext (deterministic ESM/CJS) |

## Infrastructure Benefits

### For Developers

1. **Parallel Development**
   - Work on multiple features simultaneously
   - No branch switching (maintains context)
   - Isolated environments (no dependency conflicts)

2. **Automatic Workflow Enforcement**
   - Can't commit to main by accident (git hook blocks)
   - Can't use wrong Python command (direnv redirects)
   - Can't skip linting (pre-commit hook runs)

3. **Educational Error Messages**
   - Git hook: "Cannot commit on main... use create_worktree.py"
   - direnv: "✗ Bare 'pip' detected! Use 'uv add <package>'"
   - Claude Code: Permission denied → shows correct alternative

4. **One-Command Setup**
   - `create_worktree.py issue-260 feature-branch`
   - Creates worktree + symlinks + hooks + venvs + deps

### For Claude Code Instances

1. **Permission Whitelist**
   - Explicit allow/deny for every operation
   - Prevents dangerous operations (bare pip, force push)
   - Requires approval for package management

2. **Context Management**
   - 27.8KB CLAUDE.md stays under 40KB limit
   - External docs loaded on-demand
   - Private context separated from public docs

3. **Worktree Isolation**
   - Multiple instances can run in parallel
   - No lock contention on shared files
   - Per-instance environment isolation

### For Project Quality

1. **Zero Manual Enforcement**
   - Git hooks + direnv + CI/CD handle enforcement
   - Quality checks run automatically
   - No reliance on developer discipline

2. **Comprehensive Testing**
   - 73+ test files (46 Python, 27 TypeScript)
   - Unit + integration + E2E coverage
   - CI validates every PR

3. **Consistent Code Style**
   - ruff + ESLint + Prettier enforce uniformly
   - Pre-commit hooks auto-fix violations
   - No bikeshedding in code reviews

## Unique Patterns

### 1. Path-Based Worktree Detection
```bash
if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # We're in main worktree - block operation
fi
```

**Why Unique**: Most teams use git metadata checks (fragile). Path matching is robust and obvious.

### 2. External Documentation Imports
```markdown
## Error Handling Architecture

- @docs/patterns/error-handling.md
```

**Why Unique**: Stays under CLAUDE.md 40KB limit while providing 68KB total docs. Claude Code auto-loads on reference.

### 3. Transparent Tool Interception
```bash
# Intercept python → redirect to uv run python
PATH_add .direnv/bin
```

**Why Unique**: Zero manual commands. Developers type `pytest`, get `uv run pytest` automatically. 100% enforcement.

### 4. Change Transfer Between Worktrees
```python
# Detect uncommitted and unpushed changes
# Offer interactive menu: none | uncommitted | unpushed | all
# Stash → create branch → apply stash
```

**Why Unique**: Most teams: create worktree from clean state only. This transfers WIP work intelligently.

### 5. Permission Whitelist with Pattern Matching
```json
"allow": ["Bash(uv run pytest:*)"],
"deny": ["Bash(pytest:*::*)"]
```

**Why Unique**: Explicit allow/deny for every tool, not broad categories. Forces correct workflow.

## Maintenance

### Updating CLAUDE.md (40K Character Limit)

**Check size**:
```bash
wc -c CLAUDE.md
# Output: 27792 CLAUDE.md
```

**If approaching 40K**:
1. Identify verbose sections
2. Move detailed content to `docs/patterns/new-file.md`
3. Add `@docs/patterns/new-file.md` reference in CLAUDE.md
4. Commit both files

**Example**:
```markdown
# Before (in CLAUDE.md, 5KB)
## Error Handling Pattern
[detailed 5KB explanation]

# After (in CLAUDE.md, 0.5KB)
## Error Handling Pattern
- @docs/patterns/error-handling.md

# docs/patterns/error-handling.md (5KB, public, committed to git)
[detailed explanation moved here]
```

### Adding New Worktree

```bash
# From main worktree
python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-300 feature-config

# Script automatically:
# 1. Validates source branch
# 2. Detects changes
# 3. Prompts for change inclusion
# 4. Creates worktree
# 5. Creates symlinks
# 6. Installs hooks
# 7. Installs npm deps
# 8. Creates Python venv
# 9. Sets up Node version
# 10. Enables direnv
```

### Updating Node Version

```bash
# 1. Update .nvmrc
echo "24.12.0" > .nvmrc

# 2. Install with package migration
nvm install 24.12.0 --reinstall-packages-from=24.11.0

# 3. Commit
git add .nvmrc
git commit -m "Update Node to 24.12.0"
```

### Adding New Quality Rule

**Python**:
```bash
# Edit ruff.toml
[tool.ruff.lint]
select = ["E", "F", "DTZ", "UP", "PTH", "I", "SIM", "PERF", "YTT", "NEW"]

# Apply to codebase
uv run ruff check . --fix
uv run ruff format .

# Commit
git add . && git commit -m "Add NEW ruff rule group"
```

**TypeScript**:
```javascript
// Edit cli/eslint.config.mjs
rules: {
  '@typescript-eslint/explicit-function-return-type': 'error'
}

// Apply to codebase
npm run lint -- --fix

// Commit
git add . && git commit -m "Enforce explicit return types"
```

## Next Steps

For detailed documentation on specific components:

- **Git Hooks**: See `INFRASTRUCTURE-DOCS_2-Git-Hooks.md`
- **Claude Code Config**: See `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md`
- **Quality Checks**: See `INFRASTRUCTURE-DOCS_4-Quality-Checks.md`
- **CI/CD**: See `INFRASTRUCTURE-DOCS_5-CI-CD.md`
- **Workflow Automation**: See `INFRASTRUCTURE-DOCS_6-Workflow-Automation.md`
- **Best Examples**: See `INFRASTRUCTURE_BEST_EXAMPLES.md` for the 3 most impressive components
