# Infrastructure Documentation: Direnv Integration

## Overview

DocImp uses **direnv** for transparent tool interception and environment management. When you `cd` into a worktree, direnv automatically:

1. **Intercepts Python tools** (`python`, `pip`, `pytest`, `ruff`, `mypy`) → redirects to `uv run`
2. **Blocks dangerous operations** (`pip` with helpful error message)
3. **Auto-switches Node version** based on `.nvmrc`
4. **Warns on subdirectory execution** (prevents local `.venv/` creation)

**Key Innovation**: PATH injection with **highest priority** + **recursion prevention**

---

## Configuration File

**File**: `.envrc` (checked into git, present in all worktrees)

**Size**: 141 lines

**Purpose**: Generate tool interceptors and manage environment

---

## Tool Interception Architecture

### How PATH Injection Works

**Before direnv**:
```
PATH=/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

When user types `python script.py`:
- Shell searches PATH left-to-right
- Finds `/usr/bin/python` first
- Executes system Python

**After direnv** (executes `.envrc`):
```
PATH=.direnv/bin:/usr/bin:/usr/local/bin:/opt/homebrew/bin
```

When user types `python script.py`:
- Shell searches PATH left-to-right
- Finds `.direnv/bin/python` **first** (wrapper script)
- Wrapper executes: `uv run python script.py`

### .envrc Execution Flow

```bash
# 1. Create interceptor directory
mkdir -p .direnv/bin

# 2. Generate wrapper scripts
#    (python, python3, pip, pytest, ruff, mypy)
cat > .direnv/bin/python <<'PYTHON_EOF'
[wrapper script]
PYTHON_EOF

# 3. Make executables
chmod +x .direnv/bin/python
chmod +x .direnv/bin/python3
chmod +x .direnv/bin/pip
chmod +x .direnv/bin/pytest
chmod +x .direnv/bin/ruff
chmod +x .direnv/bin/mypy

# 4. Prepend to PATH (highest priority)
PATH_add .direnv/bin

# 5. Auto-add Node version from .nvmrc
[Node version detection and PATH injection]

# 6. Success message
echo "✓ direnv loaded: Python tools intercepted (...), Node version managed"
```

---

## Python Tool Interceptors

### python / python3 Interceptor

**Files**: `.direnv/bin/python`, `.direnv/bin/python3` (identical)

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

**What It Does**:
1. Gets repository root via `git rev-parse --show-toplevel`
2. Gets current directory
3. If `pyproject.toml` exists in subdirectory (not root), warns about potential `.venv/` creation
4. Prints redirect message to stderr
5. Removes `.direnv/bin` from PATH (prevents infinite recursion)
6. Execs `uv run python` with all original arguments

**Example Session**:
```bash
$ python script.py arg1 arg2
→ Redirecting to: uv run python
[script executes via uv-managed Python]
```

**Subdirectory Warning**:
```bash
$ cd cli  # subdirectory with pyproject.toml
$ python -c "print('hello')"
Warning: Running python from subdirectory with pyproject.toml (/path/to/docimp/cli)
   May cause errors or create local .venv/. To avoid: cd /path/to/docimp && uv run python
→ Redirecting to: uv run python
hello
```

### pip Interceptor (Blocks with Error)

**File**: `.direnv/bin/pip`

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

**What It Does**:
1. Checks subdirectory execution (same as python interceptor)
2. **Blocks execution** with `exit 1`
3. Prints educational error message to stderr
4. Suggests correct alternatives (`uv add`, `uv pip sync`)

**Why Block Instead of Redirect**:
- `pip install` outside `uv` breaks lockfile consistency
- Users must learn `uv add` (project-aware dependency management)
- Forces correct workflow, no silent bypasses

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

### pytest Interceptor

**File**: `.direnv/bin/pytest`

```bash
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
```

**What It Does**: Same as python interceptor (redirect to `uv run pytest`)

**Example Session**:
```bash
$ pytest -v analyzer/tests/test_analyzer.py
→ Redirecting to: uv run pytest
============== test session starts ==============
...
```

### ruff Interceptor

**File**: `.direnv/bin/ruff`

```bash
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
```

**What It Does**: Same as python interceptor (redirect to `uv run ruff`)

**Example Session**:
```bash
$ ruff check .
→ Redirecting to: uv run ruff
All checks passed!
```

### mypy Interceptor

**File**: `.direnv/bin/mypy`

```bash
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
```

**What It Does**: Same as python interceptor (redirect to `uv run mypy`)

**Example Session**:
```bash
$ mypy analyzer/src
→ Redirecting to: uv run mypy
Success: no issues found in 23 source files
```

---

## Recursion Prevention

### The Problem

**Naive Implementation** (infinite loop):
```bash
#!/bin/bash
# BAD: Causes infinite recursion
exec uv run python "$@"
```

**What happens**:
1. User types: `python script.py`
2. Wrapper executes: `uv run python script.py`
3. `uv` internally calls `python` (to find executable)
4. PATH search finds `.direnv/bin/python` again
5. Wrapper executes: `uv run python` (again)
6. **Infinite loop** ♾️

### The Solution: PATH Scrubbing

```bash
# Remove .direnv/bin from PATH before exec
PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '.direnv/bin' | tr '\n' ':' | sed 's/:$//')
exec uv run python "$@"
```

**How it works**:
1. Split PATH on `:` into separate lines
2. Filter out lines containing `.direnv/bin`
3. Join back into `:` separated string
4. Remove trailing `:` (sed)
5. Execute `uv run python` with modified PATH

**PATH transformation**:
```
Before: .direnv/bin:/usr/bin:/usr/local/bin:/opt/homebrew/bin
After:  /usr/bin:/usr/local/bin:/opt/homebrew/bin
```

Now when `uv` calls `python`:
- PATH search finds `/usr/bin/python` (system Python)
- No wrapper involved (recursion prevented)

---

## Node Version Auto-Switching

### .nvmrc File

**File**: `.nvmrc`

**Content**: `24.11.0` (exact version, not `24`)

**Purpose**: Pin project to specific Node.js version

### direnv Node Version Detection

```bash
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
```

**How It Works**:
1. Reads `.nvmrc` file
2. Searches `~/.nvm/versions/node/` for matching version
   - Pattern: `v${NODE_VERSION}*`
   - Example: `v24.11.0*` matches `v24.11.0/`
3. If found, prepends `v24.11.0/bin/` to PATH
4. Now `node`, `npm`, `npx` all use version 24.11.0

**Why Not Call `nvm use`**:
- `nvm` is a shell function, not a binary
- Doesn't work in direnv's restricted execution context
- Direct PATH manipulation is faster and more reliable

**Example**:
```bash
$ cd /path/to/docimp
direnv: loading .envrc
✓ direnv loaded: Python tools intercepted (python, pip, pytest, ruff, mypy), Node version managed

$ which node
/Users/nik/.nvm/versions/node/v24.11.0/bin/node

$ node --version
v24.11.0
```

---

## Per-Worktree Environment Isolation

### Directory Structure

```
docimp/  (main worktree)
├── .envrc                    # direnv config (shared via git)
├── .direnv/                  # Generated wrappers (gitignored)
│   └── bin/
│       ├── python
│       ├── pip
│       ├── pytest
│       ├── ruff
│       └── mypy
├── .venv/                    # Per-worktree Python environment
├── .nvmrc                    # Node version specification
└── cli/node_modules/         # Per-worktree Node modules

.docimp-wt/issue-260/  (feature worktree)
├── .envrc                    # Same file via git
├── .direnv/                  # Separate instance (worktree-specific)
│   └── bin/
│       ├── python
│       ├── pip
│       ├── pytest
│       ├── ruff
│       └── mypy
├── .venv/                    # Separate .venv (no lock contention)
├── .nvmrc                    # Same version spec
└── cli/node_modules/         # Separate node_modules (dependency testing)
```

**Why Separate `.direnv/` per Worktree**:
- `.envrc` regenerates wrappers on `direnv allow`
- Each worktree has independent PATH prepending
- Wrappers point to worktree-specific `.venv/`

**Why Separate `.venv/` per Worktree**:
- Prevents lock contention when running `uv run pytest` in parallel
- Allows testing different dependency versions across worktrees
- uv-managed Python (containerized, not system Python)

**Why Separate `node_modules/` per Worktree**:
- npm installs to `cli/node_modules/` per worktree
- Allows testing different npm package versions
- Prevents conflicts between worktrees

---

## Session Startup

### What Happens on `cd` Into Worktree

**Step 1: direnv Detection**
```bash
$ cd /path/to/.docimp-wt/issue-260/
```

**Step 2: direnv Loads `.envrc`**
```bash
direnv: loading ~/Documents/Code/Polygot/docimp/.envrc
```

**Step 3: .envrc Executes**
- Creates `.direnv/bin/` directory
- Generates 6 wrapper scripts (python, python3, pip, pytest, ruff, mypy)
- Makes them executable
- Prepends `.direnv/bin/` to PATH
- Adds Node version to PATH

**Step 4: Success Message**
```bash
✓ direnv loaded: Python tools intercepted (python, pip, pytest, ruff, mypy), Node version managed
```

**Step 5: direnv Exports Modified PATH**
```bash
direnv: export ~PATH
```

**Result**: Environment ready, all tools intercepted

### Verification

**Check interceptors**:
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

**Test interception**:
```bash
$ python --version
→ Redirecting to: uv run python
Python 3.13.0
```

---

## Dual Enforcement with Claude Code

### Layer 1: direnv Interception (Local Development)

**Triggers**: Developer types bare command in terminal

**Action**: Redirect to `uv run` prefix

**Example**:
```bash
$ pytest -v
→ Redirecting to: uv run pytest
[tests run via uv-managed Python]
```

### Layer 2: Claude Code Permissions (AI Development)

**Triggers**: Claude Code attempts bare command

**Action**: Permission denied, suggests correct alternative

**Example**:
```
Claude Code attempts: Bash(pytest -v)
↓
settings.local.json: "Bash(pytest:*::*)" in deny list
↓
Permission denied: "Command blocked. Try: uv run pytest -v"
↓
Claude Code retries: Bash(uv run pytest -v)
↓
Executes successfully
```

### Combined Effect

**Developer workflow**:
- Types `pytest` → direnv redirects to `uv run pytest` (transparent)
- Muscle memory unchanged, correct behavior enforced

**Claude Code workflow**:
- Attempts `pytest` → permission denied (explicit)
- Learns correct command, retries with `uv run pytest`
- No silent bypasses, educational feedback

**Result**: 100% `uv run` compliance across human and AI developers

---

## Benefits of direnv Integration

### 1. Transparent Workflow Enforcement

**Problem**: Developers forget to use `uv run` prefix

**Solution**: direnv automatically redirects

**Impact**: Zero manual compliance needed

### 2. Educational Errors

**Problem**: Silent failures hard to debug

**Solution**: `pip` blocked with helpful message

**Impact**: Developers learn correct workflow

### 3. Per-Worktree Isolation

**Problem**: Shared `.venv/` causes lock contention

**Solution**: Each worktree has independent `.venv/`

**Impact**: Parallel development enabled

### 4. Automatic Node Version Management

**Problem**: Developers manually run `nvm use`

**Solution**: direnv auto-switches based on `.nvmrc`

**Impact**: Always correct Node version

### 5. Subdirectory Safety

**Problem**: Running `uv run pytest` from `cli/` creates local `.venv/`

**Solution**: Warns when executing from subdirectory

**Impact**: Prevents accidental environment duplication

---

## Troubleshooting

### Problem: direnv not loading

**Symptom**: No interception, tools use system binaries

**Diagnosis**:
```bash
$ which python
/usr/bin/python  # Should be .direnv/bin/python
```

**Fix**:
```bash
# Install direnv
brew install direnv

# Add to shell config (~/.bashrc, ~/.zshrc)
eval "$(direnv hook bash)"  # or hook zsh

# Reload shell
source ~/.bashrc

# Allow .envrc
cd /path/to/docimp
direnv allow
```

### Problem: Interception not working after .envrc update

**Symptom**: Changes to `.envrc` not applied

**Diagnosis**:
```bash
$ cat .direnv/bin/python
# Shows old wrapper code
```

**Fix**:
```bash
# Force reload
direnv allow
```

### Problem: "direnv: error .envrc is blocked"

**Symptom**:
```bash
direnv: error .envrc is blocked. Run `direnv allow` to approve its content.
```

**Fix**:
```bash
direnv allow
```

**Why**: direnv requires explicit approval for security (prevents untrusted `.envrc` execution)

### Problem: Node version not switching

**Symptom**:
```bash
$ node --version
v20.10.0  # Wrong version, should be v24.11.0
```

**Diagnosis**:
```bash
# Check if .nvmrc exists
cat .nvmrc
# Output: 24.11.0

# Check if nvm has version installed
nvm list
# Should show v24.11.0

# Check if direnv loaded
echo $PATH | tr ':' '\n' | grep nvm
# Should show /Users/nik/.nvm/versions/node/v24.11.0/bin
```

**Fix**:
```bash
# Install missing Node version
nvm install 24.11.0

# Reload direnv
direnv allow
```

### Problem: Interceptor shows "command not found: uv"

**Symptom**:
```bash
$ python script.py
→ Redirecting to: uv run python
bash: uv: command not found
```

**Diagnosis**: uv not installed

**Fix**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.bashrc
```

---

## Summary

**direnv Integration**:
- **6 tool interceptors**: python, python3, pip, pytest, ruff, mypy
- **PATH injection**: Highest priority, prevents system binaries
- **Recursion prevention**: PATH scrubbing before exec
- **Node auto-switching**: Based on `.nvmrc` (no manual `nvm use`)
- **Subdirectory warnings**: Prevents accidental `.venv/` creation

**Enforcement**:
- ✅ 100% `uv run` compliance (transparent redirection)
- ✅ `pip` blocked with educational error
- ✅ Per-worktree isolation (separate `.direnv/` and `.venv/`)
- ✅ Dual enforcement: direnv (local) + Claude Code permissions (AI)

**Benefits**:
- ✅ Zero manual workflow compliance
- ✅ Parallel development (no lock contention)
- ✅ Automatic environment management
- ✅ Educational error messages

**Next Steps**: See `../INFRASTRUCTURE_BEST_EXAMPLES.md` for in-depth exploration of the 3 most impressive infrastructure components (Git Hooks, Claude Code Config, direnv).
