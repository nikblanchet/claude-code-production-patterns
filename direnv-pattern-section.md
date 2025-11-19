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
