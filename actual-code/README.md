# create_worktree.py

Automated git worktree creation with isolated Python environments.

## Overview

This script creates git worktrees with per-worktree Python virtual environments, enabling parallel development without environment conflicts or lock contention.

**Specs:**
- **799 lines** - Python-only implementation
- **Dependencies:** uv only
- **Setup time:** ~30-60 seconds
- **Target:** This project (documentation/patterns repository)

## Usage

```bash
# Basic usage
./actual-code/create_worktree.py <worktree-name> <branch-name>

# Examples
./actual-code/create_worktree.py feature-x feature-x-implementation
./actual-code/create_worktree.py fix-docs fix-typos --source-branch main
./actual-code/create_worktree.py hotfix critical-fix --exclude-changes
```

**Prerequisites:**
- uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Why This Version

This version is **tailored specifically for this project**:

1. **Python-only** - No npm/TypeScript complexity
2. **Documentation project** - Uses `--no-install-project` (no package to install)
3. **Simple structure** - Sibling directories, no symlinks
4. **Fast setup** - Single dependency (uv), quick installation
5. **Educational** - Clear example of worktree + uv integration

## Comparison with DocImp Version

The DocImp project uses a more comprehensive version designed for polyglot codebases:

**Reference:** https://github.com/nikblanchet/claude-skills/tree/main/project-scope/docimp/git-workflow/scripts

| Aspect | This Version | DocImp Version |
|--------|--------------|----------------|
| **Size** | 799 lines | 1,067 lines (+268) |
| **Languages** | Python only | Python + TypeScript/JavaScript |
| **Dependencies** | uv | uv, npm, nvm, direnv, npx |
| **Setup time** | ~30-60s | ~2-5 min |
| **Worktree location** | `../feature-x/` (siblings) | `../.docimp-wt/issue-221/` |
| **Shared files** | None | 7 symlinks |
| **npm handling** | ❌ | ✅ install + build |
| **Husky hooks** | ❌ | ✅ configured |
| **direnv** | ❌ | ✅ enabled |
| **nvm/Node** | ❌ | ✅ version managed |
| **Git hooks install** | ❌ | ✅ automated |

## DocImp Additional Features

The DocImp version adds:

1. **npm/TypeScript Integration**
   - Runs `npm install` in cli/ directory (5-min timeout)
   - Compiles TypeScript with `npm run build` (2-min timeout)
   - Per-worktree node_modules/

2. **Husky Hook Configuration**
   - Enables per-worktree git config
   - Sets `core.hooksPath` to `.husky/_`
   - Generates hook dispatcher files

3. **direnv Setup**
   - Runs `direnv allow` to authorize .envrc
   - Enables automatic environment loading

4. **nvm Node Version Management**
   - Reads .nvmrc file
   - Installs specified Node version
   - Containerized Node environment

5. **Symlink Creation**
   - CLAUDE.md → shared documentation
   - .claude/settings.local.json → shared config
   - .planning/ → shared planning directory
   - .scratch/ → shared workspace
   - (7 symlinks total to `.docimp-shared/`)

6. **Git Hooks Installation**
   - Checks if hooks installed
   - Calls install_hooks.py
   - Interactive or automated (`--install-hooks-if-missing`)

## Architectural Differences

### Worktree Structure

**This version (sibling directories):**
```
project/
├── main/           # Main worktree
├── feature-x/      # Feature worktree
└── hotfix/         # Hotfix worktree
```

**DocImp version (nested):**
```
project/
├── docimp/         # Main worktree (protected)
└── .docimp-wt/     # All feature worktrees
    ├── issue-221/
    └── issue-275/
```

### Dependency Strategy

**This version:**
```bash
uv sync --no-install-project --group dev
```
- Doesn't install project as package (doc-only repo)
- Only dev tools (ruff, mypy, pytest)

**DocImp version:**
```bash
uv sync --extra dev
npm install && npm run build
```
- Installs Python analyzer package
- Installs npm dependencies
- Compiles TypeScript CLI

## When to Use Which

### Use This Version

- ✅ Pure Python projects with pyproject.toml
- ✅ Teaching/learning worktree workflows
- ✅ Minimal infrastructure desired
- ✅ No shared configuration needed
- ✅ Fast setup required

### Use DocImp Version

- ✅ Polyglot codebases (Python + TypeScript/JavaScript)
- ✅ Multiple developers/AI agents need shared config
- ✅ Tool enforcement (direnv, hooks) required
- ✅ Protected main branch workflow
- ✅ Production infrastructure patterns needed

## Migration Path

**To add DocImp features to this version:**

1. Add `configure_husky_hooks()` function
2. Add `install_npm_dependencies()` function
3. Add `setup_node_version()` function
4. Add `enable_direnv()` function
5. Add symlink creation logic
6. Change worktree location to `.docimp-wt/`
7. Update dependency command to `--extra dev`

See the DocImp version for complete implementations.
