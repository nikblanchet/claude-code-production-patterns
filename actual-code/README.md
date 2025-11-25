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

## When You Need More: Polyglot Projects

This script is Python-only for simplicity. If your project combines Python with JavaScript/TypeScript frontends or CLIs, you'll need additional setup steps.

### Common Polyglot Architectures

| Project Type | Backend | Frontend/CLI | Build Tools |
|--------------|---------|--------------|-------------|
| **Python + TypeScript CLI** | Python (uv) | TypeScript | npm, tsc |
| **Python + Svelte** | Python (uv) | Svelte + TypeScript | npm, vite |
| **Python + React/Vue** | Python (uv) | React/Vue + TypeScript | npm, vite/webpack |
| **Full-stack monorepo** | Python (uv) | Multiple frameworks | npm workspaces, turborepo |

### What Polyglot Projects Need

#### 1. JavaScript Dependency Management

**Package installation per worktree:**
```python
def install_npm_dependencies(worktree_path: Path) -> None:
    """Install npm dependencies in worktree."""
    package_json = worktree_path / "package.json"
    if not package_json.exists():
        return

    print("Installing npm dependencies...")
    # Timeout for large dependency trees
    subprocess.run(
        ["npm", "install"],
        cwd=worktree_path,
        timeout=300,  # 5 minutes
        check=True
    )
```

**Key considerations:**
- Per-worktree `node_modules/` for isolation
- Lock file handling (package-lock.json, pnpm-lock.yaml, yarn.lock)
- Workspace configuration for monorepos

#### 2. Frontend Build Process

**TypeScript compilation:**
```python
def build_typescript(worktree_path: Path) -> None:
    """Compile TypeScript code."""
    tsconfig = worktree_path / "tsconfig.json"
    if not tsconfig.exists():
        return

    print("Compiling TypeScript...")
    subprocess.run(
        ["npm", "run", "build"],
        cwd=worktree_path,
        timeout=120,  # 2 minutes
        check=True
    )
```

**Svelte compilation:**
```python
def build_svelte(worktree_path: Path) -> None:
    """Build Svelte application."""
    vite_config = worktree_path / "vite.config.js"
    if not vite_config.exists():
        return

    print("Building Svelte app with Vite...")
    subprocess.run(
        ["npm", "run", "build"],
        cwd=worktree_path,
        timeout=120,
        check=True
    )
```

#### 3. Node Version Management

**Reading version from .nvmrc or package.json:**
```python
def setup_node_version(worktree_path: Path) -> None:
    """Ensure correct Node.js version."""
    nvmrc = worktree_path / ".nvmrc"
    if nvmrc.exists():
        version = nvmrc.read_text().strip()
        print(f"Setting Node.js version: {version}")
        subprocess.run(["nvm", "install", version], check=True)
        subprocess.run(["nvm", "use", version], check=True)
```

**Alternatives to nvm:**
- volta (fast, cross-platform)
- asdf (multi-language version manager)
- package.json `engines` field with corepack

#### 4. Dependency Strategy

**Python-only (this script):**
```bash
uv sync --no-install-project --group dev
```

**Python + TypeScript:**
```bash
# Python backend
uv sync --group dev

# TypeScript CLI or frontend
npm install
npm run build
```

**Python + Svelte:**
```bash
# Python backend
uv sync --group dev

# Svelte frontend
cd frontend/
npm install
npm run build  # Uses Vite
```

### Comparison Table

| Aspect | Python-Only | Python + TypeScript | Python + Svelte |
|--------|-------------|---------------------|-----------------|
| **Script size** | 799 lines | ~900 lines | ~900 lines |
| **Dependencies** | uv | uv, npm, Node.js | uv, npm, Node.js |
| **Setup time** | 30-60s | 1-2 min | 1-2 min |
| **Build steps** | None (or Python build) | `npm install && npm run build` | `cd frontend/ && npm install && npm run build` |
| **Per-worktree isolation** | `.venv/` | `.venv/` + `node_modules/` | `.venv/` + `frontend/node_modules/` |
| **Version management** | `.python-version` | `.python-version` + `.nvmrc` | `.python-version` + `.nvmrc` |

### When to Extend This Script

**Keep it Python-only if:**
- Pure Python project (backend, CLI, libraries)
- No frontend compilation needed
- Team wants minimal setup complexity

**Add polyglot support if:**
- Full-stack application (Python backend + JS/TS frontend)
- TypeScript CLI alongside Python backend
- Multiple languages in same repository
- Team needs coordinated Python + Node toolchains

---

## Retrofit Patterns: A Case Study

**Context:** This section shows what happens when worktrees are added to an existing repository (retrofit) vs starting fresh (greenfield). The complexity differences are significant.

### Example: DocImp Retrofit

DocImp is a production codebase that retrofitted git worktrees onto an existing repository structure. This required additional complexity that greenfield projects don't need.

**Retrofit-specific features (NOT polyglot requirements):**

#### 1. Symlink Network for Shared Config

**Why needed in retrofit:**
- Existing `.claude/` was already in `.gitignore` (can't commit without disrupting team)
- Multiple worktrees need shared configuration
- Solution: Create `.docimp-shared/` directory with 7 symlinks

**Greenfield alternative:**
- Just commit `.claude/` to git
- Shared automatically across worktrees via git
- No symlink management needed

**Example symlinks:**
```
worktree/CLAUDE.md → ../. docimp-shared/CLAUDE.md
worktree/.claude/settings.local.json → ../.docimp-shared/.claude/settings.local.json
worktree/.planning/ → ../.docimp-shared/.planning/
worktree/.scratch/ → ../.docimp-shared/.scratch/
```

#### 2. Nested Worktree Structure

**Why used in retrofit:**
```
project/
├── docimp/         # Original repo location (can't move)
└── .docimp-wt/     # Worktrees isolated in subfolder
    ├── issue-221/
    └── issue-275/
```

**Greenfield alternative:**
```
project/
├── main/           # Clean naming
├── feature-x/      # Sibling directories
└── bugfix-y/       # Simple, flat structure
```

#### 3. Additional Setup Time

- Retrofit: 2-5 min (symlink creation, nested structure navigation)
- Greenfield: 30-60s (straightforward worktree creation)

### Key Insight

**Most retrofit complexity is NOT about polyglot requirements** - it's about working around constraints of existing repository structure.

If starting fresh, even polyglot projects should use the greenfield approach:
- Commit `.claude/` to git (shared via git, not symlinks)
- Use sibling directories (not nested structure)
- Simpler, faster, more maintainable

See [`GREENFIELD_NOTES.md`](../GREENFIELD_NOTES.md) for detailed comparison of greenfield vs retrofit patterns.

---

## Extending This Script

### Adding Polyglot Support

To support Python + JavaScript/TypeScript projects, add these functions:

#### 1. npm Dependency Installation
```python
def install_npm_dependencies(worktree_path: Path) -> None:
    """Install npm dependencies if package.json exists."""
    if (worktree_path / "package.json").exists():
        subprocess.run(["npm", "install"], cwd=worktree_path, check=True, timeout=300)
```

#### 2. Node Version Setup
```python
def setup_node_version(worktree_path: Path) -> None:
    """Configure Node.js version from .nvmrc."""
    if (worktree_path / ".nvmrc").exists():
        subprocess.run(["nvm", "install"], cwd=worktree_path, check=True)
```

#### 3. Build Step Execution
```python
def run_build_steps(worktree_path: Path, commands: list[str]) -> None:
    """Run configurable build commands."""
    for cmd in commands:
        subprocess.run(cmd.split(), cwd=worktree_path, check=True, timeout=120)
```

### Optional Enhancements

#### Hook Framework Integration

**Options:**
- Husky (JavaScript ecosystem standard)
- pre-commit (Python ecosystem standard)
- Direct git hooks (simplest, no framework)

**Trade-offs:**
- Husky: Great for npm projects, requires per-worktree config
- pre-commit: Excellent for Python projects, YAML configuration
- Git hooks: Universal, manual management

#### Environment Management

**Options:**
- direnv (automatic env loading when cd into directory)
- dotenv libraries (language-specific)
- Manual activation (scripts, aliases)

**Trade-offs:**
- direnv: Automatic but requires installation and setup
- dotenv: Language-native but manual activation
- Manual: Simple but easy to forget

### Configuration-Driven Approach

**Instead of hardcoding features, make script configurable:**

```python
# .worktree-setup.toml
[languages]
python = { manager = "uv", sync_cmd = "uv sync --group dev" }
node = { manager = "npm", install_cmd = "npm install", build_cmd = "npm run build" }

[versions]
python = ".python-version"
node = ".nvmrc"

[structure]
worktree_pattern = "../{name}/"  # Sibling dirs (greenfield)
# worktree_pattern = "../.project-wt/{name}/"  # Nested (retrofit)
```

This makes the script adaptable to different project needs without code changes.
