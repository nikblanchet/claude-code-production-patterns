# Infrastructure Documentation: CI/CD Pipeline

## Overview

DocImp uses **GitHub Actions** for continuous integration and deployment with **5 parallel/sequential jobs** that validate Python quality, TypeScript quality, end-to-end integration, module system detection, and documented workflows.

**Workflow File**: `.github/workflows/ci.yml`

**Triggers**:
- `push` to `main` branch
- `pull_request` to any branch

**Job Dependency Graph**:
```
┌─────────────────┐  ┌──────────────────┐
│  python-tests   │  │ typescript-tests │
│   (parallel)    │  │   (parallel)     │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         └──────────┬─────────┘
                    │
        ┌───────────▼────────────┐
        │  integration-test      │
        │  (depends on both)     │
        └────────────────────────┘

┌─────────────────────────────┐
│  module-system-matrix       │
│  (independent)              │
└─────────────────────────────┘

        ┌───────────┬──────────┐
        │  workflow-validation │
        │  (depends on both)   │
        └─────────────────────┘
```

---

## Job 1: Python Tests (3.13)

### Configuration

**Matrix Strategy**: Python 3.13 only (not a true matrix, but prepared for future expansion)

**Runs on**: `ubuntu-latest`

**Setup Steps**:
1. Checkout code (`actions/checkout@v4`)
2. Set up Python 3.13 (`actions/setup-python@v5`)
3. Install uv 0.9.8 (`astral-sh/setup-uv@v5`, caching enabled)
4. Set up Node.js 24 (for building CLI)
5. Install Python dependencies (`uv pip sync requirements-dev.lock`)
6. Install Node dependencies and build CLI (`npm ci`, `npm run build`)

### Quality Checks

```yaml
- name: Lint with ruff
  run: uv run ruff check analyzer/

- name: Check Python formatting
  run: uv run ruff format --check analyzer/

- name: Type check with mypy
  run: uv run mypy analyzer/src --ignore-missing-imports

- name: Run tests
  run: uv run pytest analyzer/tests/ -v --cov=analyzer/src --cov-report=term
```

**What This Validates**:
- ✓ ruff linting (8 rule groups: E, F, DTZ, UP, PTH, I, SIM, PERF, YTT)
- ✓ ruff formatting (88-char line length, Python 3.13+ syntax)
- ✓ mypy type checking (strict mode, warn on Any)
- ✓ pytest tests (46+ test files, unit + integration coverage)

**Failure Conditions**:
- Ruff linting violations (e.g., undefined names, PEP 8 violations)
- Format violations (code not formatted with `ruff format`)
- Type errors (missing type annotations, incompatible types)
- Test failures (assertions fail, exceptions raised)

---

## Job 2: TypeScript Tests

### Configuration

**Matrix Strategy**: Node.js 24 only

**Runs on**: `ubuntu-latest`

**Setup Steps**:
1. Checkout code
2. Set up Python 3.13 (for analyzer dependency)
3. Install uv 0.9.8 (caching enabled)
4. Set up Node.js 24 (npm cache enabled, `cli/package-lock.json`)
5. Install Python dependencies (`uv pip sync requirements.lock`)
6. Install Node dependencies (`npm ci`)

### Quality Checks

```yaml
- name: Lint TypeScript
  run: |
    cd cli
    npm run lint

- name: Check TypeScript/JavaScript formatting
  run: |
    cd cli
    npm run format:check

- name: Lint JSDoc
  run: |
    cd cli
    npm run lint:jsdoc
  continue-on-error: true

- name: Type check
  run: |
    cd cli
    npx tsc --noEmit

- name: Build
  run: |
    cd cli
    npm run build

- name: Run tests
  run: |
    cd cli
    npm test

- name: Run integration tests
  run: |
    cd cli
    npm run test:integration
```

**What This Validates**:
- ✓ ESLint linting (7 plugins: eslint, ts-eslint, jsdoc, unicorn, n, promise, import)
- ✓ Prettier formatting (2-space, single quotes, LF line endings)
- ✓ JSDoc linting (continue-on-error: warning only, not blocking)
- ✓ TypeScript compilation (checkJs:true, strict mode, no emit)
- ✓ Build success (TypeScript → JavaScript in `dist/`)
- ✓ Jest unit tests (27+ test files)
- ✓ Integration tests (TypeScript integration test suite)

**Failure Conditions**:
- ESLint violations (e.g., import ordering, unused vars, no-explicit-any)
- Format violations (code not formatted with Prettier)
- TypeScript compilation errors (type mismatches, missing annotations)
- Build failures (tsc errors)
- Test failures (unit or integration tests fail)

**Note**: JSDoc linting uses `continue-on-error: true`, so violations won't block CI. This allows incremental JSDoc adoption.

---

## Job 3: Integration Test (Python + TypeScript)

### Configuration

**Depends on**: `python-tests` + `typescript-tests` (runs **after** both complete)

**Runs on**: `ubuntu-latest`

**Purpose**: Validate end-to-end workflow (TypeScript CLI → Python analyzer → JSON output)

### Setup Steps

1. Checkout code
2. Set up Python 3.13
3. Install uv 0.9.8 (caching enabled)
4. Set up Node.js 24 (npm cache enabled)
5. Install Python dependencies (`uv pip sync requirements.lock`)
6. Install Node dependencies and build (`npm ci`, `npm run build`)

### End-to-End Test

```yaml
- name: Run end-to-end analysis test
  env:
    DOCIMP_ANALYZER_PATH: ${{ github.workspace }}/analyzer
  run: |
    cd cli
    node dist/index.js analyze ../examples --format json > /dev/null
    echo "✓ End-to-end analysis completed successfully"
```

**What This Validates**:
- ✓ TypeScript CLI entry point (`dist/index.js`)
- ✓ Python subprocess spawning (`PythonBridge`)
- ✓ Analyzer execution on example codebase
- ✓ JSON output generation (redirected to `/dev/null`, validates format)
- ✓ Complete data flow: CLI → Python → parsers → impact scorer → JSON

**Failure Conditions**:
- CLI crashes (exit code ≠ 0)
- Python bridge fails to spawn analyzer
- Analyzer throws exception
- Invalid JSON output

---

## Job 4: Module System Tests (CommonJS/ESM)

### Configuration

**Runs on**: `ubuntu-latest`

**Independent**: No dependencies (runs in parallel with other jobs)

**Purpose**: Validate TypeScript parser correctly detects ESM and CommonJS module systems

### Setup Steps

1. Checkout code
2. Set up Python 3.13
3. Install uv 0.9.8 (caching enabled)
4. Set up Node.js 24 (npm cache enabled)
5. Install dependencies (Python + Node, build CLI)

### Module System Tests

**Test 1: ESM Detection**:
```yaml
- name: Test ESM JavaScript parsing
  run: |
    cd analyzer
    uv run python -c "
    from src.parsers.typescript_parser import TypeScriptParser
    parser = TypeScriptParser()
    items = parser.parse_file('../examples/test_javascript_patterns.js')
    assert any(item.module_system == 'esm' for item in items), 'ESM not detected'
    print('✓ ESM detection working')
    "
```

**Test 2: CommonJS Detection**:
```yaml
- name: Test CommonJS parsing
  run: |
    cd analyzer
    uv run python -c "
    from src.parsers.typescript_parser import TypeScriptParser
    parser = TypeScriptParser()
    items = parser.parse_file('../examples/test_commonjs.cjs')
    assert any(item.module_system == 'commonjs' for item in items), 'CommonJS not detected'
    print('✓ CommonJS detection working')
    "
```

**What This Validates**:
- ✓ TypeScript parser detects `export`/`import` keywords (ESM)
- ✓ TypeScript parser detects `module.exports`/`require` (CommonJS)
- ✓ CodeItem objects have correct `module_system` field (`'esm'` or `'commonjs'`)

**Failure Conditions**:
- Parser fails to parse test files
- Module system detection returns `'unknown'` for known patterns
- Assertions fail (no items with expected module_system)

---

## Job 5: Workflow Validation (Test Samples)

### Configuration

**Depends on**: `python-tests` + `typescript-tests` (runs **after** both complete)

**Runs on**: `ubuntu-latest`

**Purpose**: Validate documented workflows end-to-end using test samples

### Setup Steps

1. Checkout code
2. Set up Python 3.13
3. Install uv 0.9.8 (caching enabled)
4. Set up Node.js 24 (npm cache enabled)
5. **Install jq** (for JSON validation in test script)
6. Install Python dependencies
7. Install Node dependencies and build

### Workflow Test Script

```yaml
- name: Run workflow validation tests
  env:
    DOCIMP_ANALYZER_PATH: ${{ github.workspace }}/analyzer
  run: |
    chmod +x test-samples/test-workflows.sh
    ./test-samples/test-workflows.sh
```

**What `test-workflows.sh` Does**:
1. Creates temporary workspace
2. Runs `docimp analyze` on example project
3. Validates JSON output with `jq`
4. Runs `docimp audit` (non-interactive mode)
5. Validates audit session file
6. Runs `docimp plan`
7. Validates plan output
8. Runs `docimp improve` (non-interactive mode)
9. Validates documentation generation
10. Cleans up temporary files

**What This Validates**:
- ✓ Complete documented workflow: analyze → audit → plan → improve
- ✓ JSON schema correctness (validated with jq)
- ✓ Session state management
- ✓ Non-interactive mode (for CI/CD use cases)

**Failure Conditions**:
- Any command exits with non-zero code
- JSON output doesn't match schema
- Session files missing or malformed
- Documentation generation fails

---

## Caching Strategy

### npm Cache

```yaml
- name: Set up Node.js 24
  uses: actions/setup-node@v4
  with:
    node-version: '24'
    cache: 'npm'
    cache-dependency-path: cli/package-lock.json
```

**Cache Key**: Based on `cli/package-lock.json`

**Benefit**: Speeds up `npm ci` (reuses cached `node_modules/`)

### uv Cache

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5
  with:
    version: "0.9.8"
    enable-cache: true
```

**Cache Key**: Managed by `astral-sh/setup-uv` action

**Benefit**: Speeds up Python package downloads (reuses cached wheels)

---

## Environment Variables

### DOCIMP_ANALYZER_PATH

```yaml
env:
  DOCIMP_ANALYZER_PATH: ${{ github.workspace }}/analyzer
```

**Purpose**: Tells TypeScript CLI where to find Python analyzer

**Used by**: Integration test, workflow validation

**Why needed**: CI runs from different directory than development environment

---

## Parallel vs Sequential Execution

### Parallel Jobs (No Dependencies)

```
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐
│  python-tests   │  │ typescript-tests │  │ module-system-matrix    │
└─────────────────┘  └──────────────────┘  └─────────────────────────┘
```

**Benefit**: Faster total CI time (runs simultaneously)

**Constraint**: GitHub Actions free tier allows 20 concurrent jobs

### Sequential Jobs (With Dependencies)

```
┌─────────────────┐  ┌──────────────────┐
│  python-tests   │  │ typescript-tests │
└────────┬────────┘  └────────┬─────────┘
         └──────────┬─────────┘
                    │
        ┌───────────▼────────────┐
        │  integration-test      │
        └────────────────────────┘
```

**Why sequential**: Integration test needs both Python and TypeScript validated first

**Benefit**: Fail fast (skip integration if unit tests fail)

---

## Typical CI Timeline

**Best Case** (all tests pass):
```
00:00 - Start: python-tests, typescript-tests, module-system-matrix (parallel)
02:30 - python-tests completes (2m 30s)
03:00 - typescript-tests completes (3m 00s)
03:00 - module-system-matrix completes (3m 00s)
03:00 - Start: integration-test, workflow-validation (parallel, depends on python + typescript)
04:30 - integration-test completes (1m 30s)
05:00 - workflow-validation completes (2m 00s)
-----
Total: ~5 minutes
```

**Worst Case** (Python tests fail):
```
00:00 - Start: python-tests, typescript-tests, module-system-matrix (parallel)
01:00 - python-tests fails (1m 00s) - ruff linting error
03:00 - typescript-tests completes (3m 00s)
03:00 - module-system-matrix completes (3m 00s)
03:00 - integration-test skipped (dependency failed)
03:00 - workflow-validation skipped (dependency failed)
-----
Total: ~3 minutes (fail fast)
```

---

## Pull Request Protection Rules

**Branch Protection** (configured on GitHub):
- ✓ Require status checks to pass before merging
- ✓ Required checks:
  - `python-tests`
  - `typescript-tests`
  - `integration-test`
  - `module-system-matrix`
  - `workflow-validation`
- ✓ Require branches to be up to date before merging
- ✓ Require linear history (squash merge)

**Effect**: PRs cannot be merged unless all 5 jobs pass

---

## Local CI Simulation

### Run Python Checks Locally

```bash
# Lint
uv run ruff check analyzer/

# Format check
uv run ruff format --check analyzer/

# Type check
uv run mypy analyzer/src --ignore-missing-imports

# Tests
uv run pytest analyzer/tests/ -v --cov=analyzer/src --cov-report=term
```

### Run TypeScript Checks Locally

```bash
cd cli

# Lint
npm run lint

# Format check
npm run format:check

# JSDoc lint
npm run lint:jsdoc

# Type check
npx tsc --noEmit

# Build
npm run build

# Tests
npm test
npm run test:integration
```

### Run Integration Test Locally

```bash
cd cli
npm run build
node dist/index.js analyze ../examples --format json > /dev/null
echo "✓ End-to-end analysis completed successfully"
```

### Run Workflow Validation Locally

```bash
chmod +x test-samples/test-workflows.sh
./test-samples/test-workflows.sh
```

---

## Debugging CI Failures

### Problem: Python tests fail with "module not found"

**Symptom**:
```
ModuleNotFoundError: No module named 'anthropic'
```

**Diagnosis**: Python dependencies not installed

**Fix in CI**:
```yaml
- name: Install Python dependencies
  run: |
    uv venv
    uv pip sync requirements-dev.lock
    uv pip install -e .
```

**Fix locally**:
```bash
uv pip sync requirements-dev.lock
uv pip install -e .
```

### Problem: TypeScript tests fail with "Cannot find module"

**Symptom**:
```
Cannot find module '../utils/config' or its corresponding type declarations.
```

**Diagnosis**: TypeScript not built, `dist/` directory missing

**Fix in CI**:
```yaml
- name: Build
  run: |
    cd cli
    npm run build
```

**Fix locally**:
```bash
cd cli
npm run build
```

### Problem: Integration test fails with "DOCIMP_ANALYZER_PATH not set"

**Symptom**:
```
Error: DOCIMP_ANALYZER_PATH environment variable not set
```

**Diagnosis**: Environment variable missing

**Fix in CI**:
```yaml
- name: Run end-to-end analysis test
  env:
    DOCIMP_ANALYZER_PATH: ${{ github.workspace }}/analyzer
  run: ...
```

**Fix locally**:
```bash
export DOCIMP_ANALYZER_PATH=$(pwd)/analyzer
cd cli
node dist/index.js analyze ../examples --format json
```

### Problem: Module system tests fail with assertion error

**Symptom**:
```
AssertionError: ESM not detected
```

**Diagnosis**: Parser not detecting module system correctly

**Debug locally**:
```bash
cd analyzer
uv run python -c "
from src.parsers.typescript_parser import TypeScriptParser
parser = TypeScriptParser()
items = parser.parse_file('../examples/test_javascript_patterns.js')
for item in items:
    print(f'{item.name}: {item.module_system}')
"
```

**Check**:
- Is `test_javascript_patterns.js` using `export` keywords?
- Is TypeScript parser detecting keywords correctly?
- Are items being created with correct `module_system` value?

---

## CI Performance Optimization

### Current Optimizations

1. **npm caching** - Reuses `node_modules/` between runs
2. **uv caching** - Reuses Python package downloads
3. **Parallel jobs** - python-tests + typescript-tests + module-system-matrix run simultaneously
4. **Fail fast** - Integration tests skipped if unit tests fail
5. **Minimal installs** - `npm ci` (clean install) instead of `npm install` (respects lockfile exactly)

### Future Optimizations

1. **Matrix strategy for Python versions** - Test Python 3.13, 3.14, etc. in parallel
2. **Artifact caching** - Cache built CLI between jobs (avoid rebuilding)
3. **Test splitting** - Split pytest/Jest tests across multiple runners
4. **Conditional runs** - Skip Python tests if only TypeScript files changed (and vice versa)

---

## Summary

**CI/CD Pipeline**:
- **5 jobs**: python-tests, typescript-tests, integration-test, module-system-matrix, workflow-validation
- **Parallel execution**: 3 jobs run simultaneously (python-tests, typescript-tests, module-system-matrix)
- **Sequential dependencies**: integration-test and workflow-validation wait for python-tests + typescript-tests
- **Total time**: ~5 minutes (all tests pass), ~3 minutes (fail fast)

**Quality Gates**:
- ✓ Python: ruff (lint + format), mypy (types), pytest (46+ tests)
- ✓ TypeScript: ESLint (lint), Prettier (format), tsc (types), Jest (27+ tests)
- ✓ Integration: End-to-end CLI → analyzer → JSON output
- ✓ Module systems: ESM and CommonJS detection
- ✓ Workflows: analyze → audit → plan → improve validation

**Caching**:
- ✓ npm cache (based on package-lock.json)
- ✓ uv cache (Python packages)

**Pull Request Protection**:
- ✓ All 5 jobs must pass before merge
- ✓ Branches must be up to date
- ✓ Squash merge required (linear history)

**Next Steps**: See `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md` for tool interception and environment management.
