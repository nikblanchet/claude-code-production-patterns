# Infrastructure Documentation: Development Utilities

## Overview

DocImp provides **development automation** via Makefile targets that streamline common workflows. These utilities reduce cognitive load by providing:

- **Single-command operations** for complex multi-step tasks
- **Consistent interface** across development environments
- **Self-documenting targets** via `make help`
- **Idempotent operations** that are safe to run repeatedly

**Key Utilities:**
- `make setup` - One-command project initialization
- `make lint` - Run all linting checks
- `make format` - Auto-format all code
- `make test` - Run all tests
- `make quality` - Full quality gate (lint + typecheck + test)
- `make clean` - Remove build artifacts

---

## Makefile

**File: Makefile (Project Root)**

```makefile
# DocImp Development Makefile
#
# Provides convenient targets for common development tasks.
# All targets are idempotent and safe to run repeatedly.
#
# Usage:
#   make help      - Show this help message
#   make setup     - Initialize development environment
#   make lint      - Run linting (ruff check)
#   make format    - Format code (ruff format)
#   make test      - Run all tests (pytest)
#   make quality   - Run full quality gate (lint + typecheck + test)
#   make clean     - Remove build artifacts

.PHONY: help setup lint format test test-cov typecheck quality clean

# Default target: show help
help:
	@echo "DocImp Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make setup      - Initialize development environment (uv venv + deps)"
	@echo "  make lint       - Run ruff linting"
	@echo "  make format     - Format code with ruff"
	@echo "  make test       - Run pytest tests"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make quality    - Run full quality gate (lint + typecheck + test)"
	@echo "  make clean      - Remove build artifacts"
	@echo ""
	@echo "Python environment: $(shell which python3)"
	@echo "uv version: $(shell uv --version 2>/dev/null || echo 'not installed')"

# Setup development environment
setup:
	@echo "Setting up development environment..."
	@if ! command -v uv &> /dev/null; then \
		echo "Error: uv not found. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	@echo "Creating virtual environment..."
	cd analyzer && uv venv
	@echo "Installing dependencies..."
	cd analyzer && uv pip sync requirements-dev.lock
	@echo "Installing package in editable mode..."
	cd analyzer && uv pip install -e .
	@echo "Setup TypeScript CLI..."
	cd cli && npm install
	@echo "Build CLI..."
	cd cli && npm run build
	@echo ""
	@echo "✓ Setup complete!"
	@echo "  - Python env: analyzer/.venv/"
	@echo "  - Node modules: cli/node_modules/"
	@echo ""
	@echo "Next steps:"
	@echo "  make test       - Run tests"
	@echo "  make quality    - Run full quality gate"

# Linting
lint:
	@echo "Running ruff linting..."
	cd analyzer && uv run ruff check .
	@echo "✓ Linting passed"

# Formatting
format:
	@echo "Formatting Python code with ruff..."
	cd analyzer && uv run ruff format .
	@echo "Formatting TypeScript/JavaScript code with prettier..."
	cd cli && npm run format
	@echo "✓ Formatting complete"

# Testing
test:
	@echo "Running Python tests..."
	cd analyzer && uv run pytest -v
	@echo ""
	@echo "Running TypeScript tests..."
	cd cli && npm test
	@echo "✓ All tests passed"

# Testing with coverage
test-cov:
	@echo "Running Python tests with coverage..."
	cd analyzer && uv run pytest -v --cov=src --cov-report=term --cov-report=html
	@echo ""
	@echo "Coverage report: analyzer/htmlcov/index.html"

# Type checking
typecheck:
	@echo "Running mypy type checking..."
	cd analyzer && uv run mypy src --ignore-missing-imports
	@echo ""
	@echo "Running TypeScript type checking..."
	cd cli && npx tsc --noEmit
	@echo "✓ Type checking passed"

# Full quality gate
quality: lint typecheck test
	@echo ""
	@echo "╔════════════════════════════════════════╗"
	@echo "║  ✓ All quality checks passed!          ║"
	@echo "╔════════════════════════════════════════╗"
	@echo ""
	@echo "Summary:"
	@echo "  ✓ Linting (ruff)"
	@echo "  ✓ Type checking (mypy, tsc)"
	@echo "  ✓ Tests (pytest, jest)"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf analyzer/dist/ analyzer/build/ analyzer/*.egg-info
	rm -rf analyzer/.pytest_cache analyzer/.mypy_cache analyzer/.ruff_cache
	rm -rf analyzer/htmlcov analyzer/.coverage
	rm -rf cli/dist/ cli/coverage/ cli/*.tsbuildinfo
	rm -rf cli/node_modules/.cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"
```

### Target Breakdown

**1. help (default target)**

Shows available targets with descriptions.

```bash
make
# Or explicitly:
make help
```

**Output:**

```
DocImp Development Makefile

Available targets:
  make setup      - Initialize development environment (uv venv + deps)
  make lint       - Run ruff linting
  make format     - Format code with ruff
  make test       - Run pytest tests
  make test-cov   - Run tests with coverage report
  make typecheck  - Run mypy type checking
  make quality    - Run full quality gate (lint + typecheck + test)
  make clean      - Remove build artifacts

Python environment: /Users/user/.local/bin/python3
uv version: uv 0.9.8
```

**Implementation:**

```makefile
help:
	@echo "Available targets:"
	@echo "  make setup      - Initialize development environment"
	# ... more help text
```

**Design decisions:**
- `@` prefix suppresses command echo (only output shown)
- Includes system info (Python path, uv version)
- Default target (first in file) for convenience

**2. setup**

One-command initialization for new contributors.

```bash
make setup
```

**Steps performed:**

1. Check uv installation
2. Create virtual environment (`analyzer/.venv/`)
3. Install dependencies from `requirements-dev.lock`
4. Install package in editable mode (`pip install -e .`)
5. Install npm dependencies (`cli/node_modules/`)
6. Build TypeScript CLI (`cli/dist/`)

**Output:**

```
Setting up development environment...
Creating virtual environment...
Installing dependencies...
Installing package in editable mode...
Setup TypeScript CLI...
Build CLI...

✓ Setup complete!
  - Python env: analyzer/.venv/
  - Node modules: cli/node_modules/

Next steps:
  make test       - Run tests
  make quality    - Run full quality gate
```

**Error handling:**

```makefile
@if ! command -v uv &> /dev/null; then \
	echo "Error: uv not found. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	exit 1; \
fi
```

If uv not installed, clear error message with installation instructions.

**3. lint**

Run Python linting with ruff.

```bash
make lint
```

**Command:** `cd analyzer && uv run ruff check .`

**Output:**

```
Running ruff linting...
✓ Linting passed
```

**On failure:**

```
Running ruff linting...
analyzer/src/parsers/python_parser.py:45:5: F841 Local variable `unused` is assigned to but never used
analyzer/src/models/code_item.py:12:1: E501 Line too long (92 > 88 characters)
```

**4. format**

Auto-format all code (Python + TypeScript/JavaScript).

```bash
make format
```

**Commands:**
1. `cd analyzer && uv run ruff format .`
2. `cd cli && npm run format`

**Output:**

```
Formatting Python code with ruff...
2 files reformatted, 38 files left unchanged
Formatting TypeScript/JavaScript code with prettier...
cli/src/commands/analyze.ts 120ms
cli/src/display/TerminalDisplay.ts 85ms
✓ Formatting complete
```

**Idempotent:** Running twice produces no changes on second run.

**5. test**

Run all tests (Python + TypeScript).

```bash
make test
```

**Commands:**
1. `cd analyzer && uv run pytest -v`
2. `cd cli && npm test`

**Output:**

```
Running Python tests...
tests/test_parsers.py::test_parse_simple_function PASSED
tests/test_parsers.py::test_parse_class PASSED
... (476 tests)
======================== 476 passed in 12.34s =========================

Running TypeScript tests...
PASS src/__tests__/commands/status.test.ts
PASS src/__tests__/workflow-validator.test.ts
... (447 tests)
Test Suites: 50 passed, 50 total
Tests:       447 passed, 447 total
✓ All tests passed
```

**On failure:**

```
Running Python tests...
tests/test_parsers.py::test_parse_simple_function FAILED

FAILED tests/test_parsers.py::test_parse_simple_function - AssertionError: ...
======================== 1 failed, 475 passed in 12.34s ========================
make: *** [test] Error 1
```

Make exits with error code 1, stopping further targets.

**6. test-cov**

Run Python tests with coverage report.

```bash
make test-cov
```

**Command:** `cd analyzer && uv run pytest -v --cov=src --cov-report=term --cov-report=html`

**Output:**

```
Running Python tests with coverage...
tests/test_parsers.py::test_parse_simple_function PASSED
... (476 tests)

---------- coverage: platform linux, python 3.13.1-final-0 ----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
src/analysis/documentation_analyzer.py   145      3    98%
src/parsers/python_parser.py            234     12    95%
src/scoring/impact_scorer.py             87      0   100%
... (more files)
--------------------------------------------------------
TOTAL                                  3421     45    99%

Coverage HTML written to dir htmlcov

Coverage report: analyzer/htmlcov/index.html
```

**View coverage report:**

```bash
open analyzer/htmlcov/index.html
```

**7. typecheck**

Run type checking (mypy + TypeScript compiler).

```bash
make typecheck
```

**Commands:**
1. `cd analyzer && uv run mypy src --ignore-missing-imports`
2. `cd cli && npx tsc --noEmit`

**Output:**

```
Running mypy type checking...
Success: no issues found in 42 source files

Running TypeScript type checking...
✓ Type checking passed
```

**On failure (Python):**

```
Running mypy type checking...
src/parsers/python_parser.py:45: error: Incompatible types in assignment (expression has type "str", variable has type "int")
Found 1 error in 1 file (checked 42 source files)
make: *** [typecheck] Error 1
```

**On failure (TypeScript):**

```
Running TypeScript type checking...
src/commands/analyze.ts:45:10 - error TS2322: Type 'string' is not assignable to type 'number'.

45   const count: number = "not a number";
            ^^^^^

Found 1 error in 1 file.
make: *** [typecheck] Error 2
```

**8. quality**

Full quality gate (lint + typecheck + test).

```bash
make quality
```

**Dependencies:** Runs `lint`, `typecheck`, and `test` in sequence.

**Output:**

```
Running ruff linting...
✓ Linting passed

Running mypy type checking...
Success: no issues found in 42 source files

Running TypeScript type checking...
✓ Type checking passed

Running Python tests...
======================== 476 passed in 12.34s =========================

Running TypeScript tests...
Test Suites: 50 passed, 50 total
Tests:       447 passed, 447 total
✓ All tests passed

╔════════════════════════════════════════╗
║  ✓ All quality checks passed!          ║
╚════════════════════════════════════════╝

Summary:
  ✓ Linting (ruff)
  ✓ Type checking (mypy, tsc)
  ✓ Tests (pytest, jest)
```

**Fail-fast behavior:**

If any target fails, `make` stops immediately without running subsequent targets.

**Use case:** Run before creating PR to ensure all checks pass.

**9. clean**

Remove build artifacts and caches.

```bash
make clean
```

**Removes:**

- Python: `dist/`, `build/`, `*.egg-info`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `htmlcov`, `.coverage`, `__pycache__/`, `*.pyc`
- TypeScript: `dist/`, `coverage/`, `*.tsbuildinfo`, `node_modules/.cache`

**Output:**

```
Cleaning build artifacts...
✓ Clean complete
```

**Idempotent:** Safe to run multiple times (uses `-f` for `rm`).

**Use case:**
- Fresh build after major changes
- Resolve stale build issues
- Free disk space

---

## Make Best Practices

### 1. Use .PHONY for Non-File Targets

```makefile
.PHONY: help setup lint format test clean

# Without .PHONY:
# If file named "test" exists in directory, `make test` won't run

# With .PHONY:
# Always runs target regardless of file existence
```

**Why:**
- Prevents conflicts with files named same as targets
- Makes targets always execute

### 2. Fail Fast with set -e

```makefile
test:
	cd analyzer && uv run pytest -v  # If fails, stops here
	cd cli && npm test  # Only runs if pytest succeeds
```

Make's default behavior: stop on first error.

**Override (not recommended):**

```makefile
test:
	-cd analyzer && uv run pytest -v  # `-` prefix ignores errors
	cd cli && npm test  # Runs even if pytest fails
```

### 3. Use @ to Suppress Command Echo

```makefile
# Without @:
lint:
	echo "Running linting..."
	cd analyzer && uv run ruff check .

# Output:
# echo "Running linting..."
# Running linting...  ← Duplicate
# cd analyzer && uv run ruff check .
# ✓ Linting passed

# With @:
lint:
	@echo "Running linting..."
	@cd analyzer && uv run ruff check .

# Output:
# Running linting...  ← Clean
# ✓ Linting passed
```

### 4. Provide Helpful Error Messages

```makefile
setup:
	@if ! command -v uv &> /dev/null; then \
		echo "Error: uv not found."; \
		echo "Install via: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	# Continue setup...
```

**Benefits:**
- New contributors know exactly what to install
- No cryptic "command not found" errors

### 5. Use Multi-Line Commands with Continuation

```makefile
quality: lint typecheck test
	@echo ""
	@echo "╔════════════════════════════════════════╗"
	@echo "║  ✓ All quality checks passed!          ║"
	@echo "╚════════════════════════════════════════╝"
```

**Alternative (single line):**

```makefile
quality: lint typecheck test
	@echo "" && echo "All checks passed!"
```

### 6. Document Targets with Comments

```makefile
# Setup development environment
#
# Creates virtual environment, installs dependencies,
# and builds TypeScript CLI.
#
# Prerequisites:
#   - uv installed (https://github.com/astral-sh/uv)
#   - Node.js 24+ (for CLI build)
setup:
	# ... implementation
```

---

## Integration with npm Scripts

Makefile targets complement npm scripts in `cli/package.json`:

**npm Scripts (cli/package.json):**

```json
{
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src --ext .ts",
    "format": "prettier --write \"src/**/*.{ts,js,json,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,js,json,md}\""
  }
}
```

**Makefile delegates to npm:**

```makefile
format:
	@echo "Formatting TypeScript/JavaScript code..."
	cd cli && npm run format
```

**Why not use npm scripts for everything?**

1. **Multi-language projects**: Makefile coordinates Python + TypeScript
2. **System-level operations**: Makefile better for creating venvs, checking system deps
3. **Unified interface**: `make test` works regardless of language stack

---

## Common Workflows

### New Contributor Onboarding

```bash
# 1. Clone repository
git clone https://github.com/org/docimp.git
cd docimp

# 2. One-command setup
make setup

# 3. Verify setup
make test

# 4. Ready to develop!
```

**Total time: ~2 minutes**

**Alternative without Makefile:**

```bash
# Manual setup (error-prone)
cd analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
cd ../cli
npm install
npm run build
cd ..
pytest analyzer/tests/
cd cli && npm test
```

**Total time: ~10 minutes + debugging**

### Pre-Commit Workflow

```bash
# 1. Make changes
vim src/analyzer.py

# 2. Format code
make format

# 3. Run quality gate
make quality

# 4. If passes, commit
git add .
git commit -m "Add new feature"
```

**CI/CD will pass because local checks match CI checks.**

### Debugging Failed CI

```bash
# CI failed on "lint" check

# 1. Reproduce locally
make lint

# 2. Fix issues
vim src/parsers/python_parser.py

# 3. Verify fix
make lint

# 4. Run full quality gate
make quality

# 5. Push fix
git add .
git commit -m "Fix linting issues"
git push
```

---

## Advanced Makefile Patterns

### Conditional Execution

```makefile
setup:
	@if [ ! -d "analyzer/.venv" ]; then \
		echo "Creating virtual environment..."; \
		cd analyzer && uv venv; \
	else \
		echo "Virtual environment already exists"; \
	fi
```

### Parallel Execution

```makefile
# Run Python and TypeScript tests in parallel
test-parallel:
	@echo "Running tests in parallel..."
	(cd analyzer && uv run pytest -v) & \
	(cd cli && npm test) & \
	wait

# Note: Requires & background operator and wait
```

**Trade-offs:**
- Faster execution (parallelism)
- Harder to debug (interleaved output)

### Variables and Substitution

```makefile
PYTHON := $(shell which python3)
UV := $(shell which uv)
NODE := $(shell which node)

setup:
	@echo "Python: $(PYTHON)"
	@echo "uv: $(UV)"
	@echo "Node: $(NODE)"
	@if [ -z "$(UV)" ]; then \
		echo "Error: uv not found"; \
		exit 1; \
	fi
```

### Target Dependencies

```makefile
# quality depends on lint, typecheck, test
quality: lint typecheck test
	@echo "All checks passed!"

# Execution order:
# 1. make lint
# 2. make typecheck
# 3. make test
# 4. echo "All checks passed!"
```

---

## Troubleshooting

### Problem: make setup Fails with "uv: command not found"

**Solution:**

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env  # Add uv to PATH
make setup
```

### Problem: make test Passes Locally But Fails in CI

**Symptoms:**
- `make test` succeeds on development machine
- GitHub Actions CI shows test failures

**Solution:**

Check Python/Node versions match CI:

```bash
# Check local versions
python3 --version  # Should be 3.13.x
node --version     # Should be 24.x.x

# Install correct versions
pyenv install 3.13.1
nvm install 24.11.0

# Re-run tests
make test
```

Ensure clean environment:

```bash
make clean
make setup
make test
```

### Problem: make Targets Run Even When They Should Skip

**Symptoms:**
- `make test` runs tests even though code hasn't changed
- Slow iteration cycle

**Solution:**

This is expected behavior - Makefile targets are `.PHONY` (always run).

For watch mode during development:

```bash
# Python: pytest watch mode
cd analyzer && uv run pytest -v --watch

# TypeScript: jest watch mode
cd cli && npm test -- --watch
```

### Problem: Parallel make -j Causes Issues

**Symptoms:**
- `make -j4 quality` produces interleaved output
- Tests fail due to race conditions

**Solution:**

DocImp Makefile not designed for parallel execution. Run sequentially:

```bash
make quality  # Sequential execution (safe)
```

---

## Quick Reference

### All Makefile Targets

| Target | Description | Time |
|--------|-------------|------|
| `make help` | Show available targets | <1s |
| `make setup` | Initialize dev environment | ~60s |
| `make lint` | Run Python linting | ~5s |
| `make format` | Format all code | ~10s |
| `make test` | Run all tests | ~30s |
| `make test-cov` | Tests with coverage | ~40s |
| `make typecheck` | Type checking | ~15s |
| `make quality` | Full quality gate | ~50s |
| `make clean` | Remove build artifacts | ~2s |

### Common Command Patterns

```bash
# First time setup
make setup

# Before committing
make format && make quality

# After pulling changes
make setup && make test

# Debug CI failure
make quality

# Clean slate
make clean && make setup && make test
```

---

## Summary

DocImp's Makefile provides **one-command operations** for common development tasks:

- **make setup** - Initialize environment (uv venv + deps + build)
- **make quality** - Full quality gate (lint + typecheck + test)
- **make format** - Auto-format all code
- **make clean** - Remove build artifacts

**Key Benefits:**

- **Fast onboarding** - New contributors run `make setup` and start coding
- **Consistent interface** - Same commands work across environments
- **Fail-fast execution** - Stops on first error
- **Self-documenting** - `make help` shows all targets

**Integration:**

- Complements npm scripts for TypeScript/JavaScript
- Coordinates multi-language workflows
- Matches CI/CD checks exactly

**Next Steps**: See `INFRASTRUCTURE-DOCS_11-Planning-Documentation.md` for PLAN.md structure and development workflow tracking.
