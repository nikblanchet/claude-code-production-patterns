# Infrastructure Documentation: Performance Considerations

## Overview

DocImp's infrastructure balances thorough quality checks with developer velocity. This document details performance optimizations, benchmarks, bottleneck identification, and trade-offs across CI/CD, testing, linting, and analysis workflows.

Understanding these optimizations helps developers make informed decisions about when to prioritize speed versus thoroughness, identify performance regressions, and leverage caching strategies effectively.

## 1. CI/CD Performance

### Baseline Metrics

**Target**: Complete CI pipeline in < 6 minutes

**Current Performance** (as of 2025-11):
- **Total CI time**: 4-5 minutes (parallel execution)
- **Python Tests job**: 90-120 seconds
- **TypeScript Tests job**: 120-150 seconds
- **Integration Test job**: 60-90 seconds (depends on Python + TypeScript)
- **Module System Tests job**: 45-60 seconds
- **Workflow Validation job**: 30-45 seconds

**Breakdown**:
```
Start ──┬── Python Tests (120s) ─────────┐
        ├── TypeScript Tests (150s) ─────┤
        ├── Module System Tests (60s) ───┤
        │                                 ├── Integration Test (90s) ── End
        └── Workflow Validation (45s) ───┘

Total: max(150s) + 90s = 240s (4 minutes)
```

---

### Optimization: Parallel Job Execution

**Configuration**: `.github/workflows/ci.yml`

**Strategy**: Independent jobs run in parallel
```yaml
jobs:
  python-tests:
    runs-on: ubuntu-latest
    # Runs immediately

  typescript-tests:
    runs-on: ubuntu-latest
    # Runs in parallel with python-tests

  integration-test:
    runs-on: ubuntu-latest
    needs: [python-tests, typescript-tests]
    # Waits for both to complete
```

**Benefit**: Reduces total CI time from 7+ minutes (sequential) to 4-5 minutes (parallel)

**Cost**: Higher GitHub Actions minutes consumption (3-5 jobs × 4-5 minutes = 15-25 minutes per CI run)

---

### Optimization: Dependency Caching

#### npm Cache

**Configuration**:
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '24'
    cache: 'npm'  # Automatic npm cache
    cache-dependency-path: 'cli/package-lock.json'
```

**Impact**:
- **Without cache**: `npm ci` takes 45-60 seconds
- **With cache**: `npm ci` takes 10-15 seconds
- **Savings**: 30-45 seconds per job

**Cache Key**: Based on `package-lock.json` hash
- Cache hit: Lockfile unchanged since last run
- Cache miss: Lockfile updated, reinstall dependencies

---

#### uv Cache

**Configuration**:
```yaml
- name: Setup uv
  uses: astral-sh/setup-uv@v5
  with:
    version: "0.9.8"
    # Automatic caching enabled by default
```

**Impact**:
- **Without cache**: `uv pip sync` takes 30-45 seconds
- **With cache**: `uv pip sync` takes 5-10 seconds
- **Savings**: 20-35 seconds per job

**Cache Strategy**: uv caches packages in `~/.cache/uv/`

---

### Optimization: No Matrix Strategy

**Decision**: Run Python 3.13 only (not a matrix across 3.11, 3.12, 3.13)

**Rationale**:
- DocImp requires Python 3.13+ (see `pyproject.toml`)
- Testing older versions unnecessary (not supported)
- Matrix would 3× CI time (3 Python versions × 120s = 360s vs 120s)

**Trade-off**: No backward compatibility validation, but not needed for 3.13+ requirement

---

### Optimization: Minimal Test Duplication

**Strategy**: Avoid running same tests in multiple jobs

**Example**:
- **Python Tests job**: Runs `pytest` (Python tests only)
- **TypeScript Tests job**: Runs `jest` (TypeScript tests only)
- **Integration Test job**: Runs `docimp analyze` (end-to-end validation, minimal overlap)

**Anti-Pattern** (Avoided):
```yaml
# DON'T: Redundant full test runs
jobs:
  test-all:
    - run: pytest -v && npm test  # Full suite
  integration:
    - run: pytest -v && npm test  # Duplicate!
```

---

## 2. Test Execution Performance

### Baseline Metrics

**Python Tests**:
- **Total tests**: 187 tests
- **Execution time**: 4-6 seconds
- **Average**: 25-35 ms per test

**TypeScript Tests**:
- **Total tests**: 89 tests
- **Execution time**: 8-12 seconds
- **Average**: 90-135 ms per test

---

### Optimization: Sequential Jest Execution

**Configuration**: `cli/jest.config.js`

```javascript
export default {
  maxWorkers: 1,  // Sequential execution
  testEnvironment: 'node',
};
```

**Rationale**:
- Integration tests share `.docimp/state/` directory
- Parallel execution causes race conditions (git operations conflict)
- Sequential prevents: "fatal: Unable to create '/path/to/.docimp/state/.git/index.lock': File exists"

**Trade-off**:
- **Performance cost**: TypeScript tests take 8-12 seconds (sequential) vs 4-6 seconds (parallel, if isolated)
- **Stability gain**: Zero flaky tests due to state conflicts

**Future Optimization**: Isolate state per test (per-test `.docimp-test-<uuid>/` directories)

---

### Optimization: pytest Markers

**Configuration**: `analyzer/pytest.ini`

```ini
[pytest]
markers =
  unit: Unit tests (fast)
  integration: Integration tests (slower)
  slow: Long-running tests
```

**Usage**:
```bash
# Run only unit tests (fast feedback)
uv run pytest -m unit  # 2-3 seconds

# Run only integration tests
uv run pytest -m integration  # 1-2 seconds

# Run all tests
uv run pytest -v  # 4-6 seconds
```

**Developer Workflow**:
1. During development: `pytest -m unit` (fast iteration)
2. Before commit: `pytest -v` (full validation)
3. CI: `pytest -v --cov` (full suite + coverage)

---

### Optimization: Makefile Shortcuts

**File**: `Makefile`

```makefile
test:
	uv run pytest -v

test-cov:
	uv run pytest -v --cov=analyzer/src --cov-report=term

test-unit:
	uv run pytest -m unit -v

test-integration:
	uv run pytest -m integration -v

quality:
	uv run ruff check .
	uv run mypy analyzer/src --ignore-missing-imports
	uv run pytest -v
```

**Benefit**: Shorter commands for common tasks
```bash
# Instead of:
uv run pytest -v --cov=analyzer/src --cov-report=term-missing

# Just:
make test-cov
```

---

## 3. Linting & Formatting Performance

### Baseline Metrics

**Ruff** (Python):
- **Files**: ~60 Python files
- **Lint time**: 0.5-1.0 seconds (full repo)
- **Format time**: 0.3-0.5 seconds (full repo)

**ESLint** (TypeScript/JavaScript):
- **Files**: ~90 TypeScript/JavaScript files
- **Lint time**: 3-5 seconds (full repo)

**Prettier** (TypeScript/JavaScript):
- **Files**: ~90 files
- **Format time**: 1-2 seconds (full repo)

---

### Optimization: lint-staged (Pre-Commit)

**Configuration**: `cli/package.json`

```json
{
  "lint-staged": {
    "*.{ts,js,mjs,cjs}": ["prettier --write", "eslint --fix"],
    "*.py": ["ruff format", "ruff check --fix"]
  }
}
```

**Benefit**: Only lint/format staged files (not entire repo)

**Performance**:
- **Full repo linting**: 5-7 seconds (ESLint + Prettier + Ruff)
- **Staged files only** (typical commit, 2-3 files): 0.5-1.5 seconds
- **Savings**: 4-6 seconds per commit

**Trade-off**: Incremental checking (may miss issues in unchanged files)

---

### Optimization: Ruff (Replaces Multiple Tools)

**Before** (Hypothetical):
- black (formatting): 2-3 seconds
- flake8 (linting): 3-4 seconds
- isort (import sorting): 1-2 seconds
- **Total**: 6-9 seconds

**After** (Ruff):
- ruff format (formatting): 0.3-0.5 seconds
- ruff check (linting + import sorting): 0.5-1.0 seconds
- **Total**: 0.8-1.5 seconds

**Savings**: 5-7.5 seconds (5-10× faster)

**Rationale**: Ruff is Rust-based (vs Python tools), single tool vs coordination overhead

---

### Optimization: ESLint Selective Linting

**Command**:
```bash
# Lint only TypeScript files
npm run lint -- --ext .ts

# Lint specific directory
npm run lint -- src/commands/

# Lint single file
npm run lint -- src/commands/analyzeCommand.ts
```

**Use Case**: Debugging linting issues in specific file without full repo scan

**Performance**:
- **Full repo**: 3-5 seconds
- **Single file**: 0.2-0.5 seconds

---

## 4. Incremental Analysis Performance

### Baseline Metrics

**Full Analysis** (100 files):
- **Time**: 25-35 seconds
- **Per-file average**: 250-350 ms

**Incremental Analysis** (5 files changed):
- **Time**: 2-4 seconds
- **Savings**: 90-92%

---

### How Incremental Analysis Works

**Command**:
```bash
docimp analyze ./src --incremental
```

**Algorithm**:
1. Load `workflow-state.json` (previous file checksums)
2. Calculate checksums for all files in `./src`
3. Compare current checksums with stored checksums
4. Re-analyze only files with changed checksums
5. Reuse results from unchanged files
6. Update `workflow-state.json` with new checksums

**Checksum Calculation**:
```python
# analyzer/src/utils/state_manager.py
import hashlib

def calculate_checksum(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
```

**Performance**: SHA-256 hashing is fast (1-5 ms per file for typical source files)

---

### Performance Breakdown

**Scenario**: 100 files, 5 changed

**Full Analysis**:
```
File discovery:           500 ms
Parsing 100 files:     30,000 ms  (100 × 300 ms avg)
Impact scoring:           500 ms
JSON serialization:       200 ms
Total:                 31,200 ms  (31.2 seconds)
```

**Incremental Analysis**:
```
File discovery:           500 ms
Checksum calculation:     500 ms  (100 × 5 ms avg)
Comparison:               100 ms
Parsing 5 files:        1,500 ms  (5 × 300 ms avg)
Load cached results:      200 ms
Impact scoring:           100 ms
JSON serialization:       200 ms
Total:                  3,100 ms  (3.1 seconds)
```

**Speedup**: 10× faster (31.2s → 3.1s)

---

### When to Use Incremental

**Use Incremental** (`--incremental`):
- Large codebases (100+ files)
- Small changes (< 10% of files modified)
- Frequent re-analysis during development

**Use Full Analysis** (default):
- First analysis of new project
- After major refactoring (many files changed)
- When incremental results seem stale

**Dry-Run Preview**:
```bash
docimp analyze ./src --incremental --dry-run

# Output:
# Would re-analyze 5 file(s):
#   - src/analyzer.ts
#   - src/parser.py
# Would reuse results from 95 unchanged file(s)
# Estimated time savings: ~90%
```

---

## 5. Caching Strategies

### Plugin Validation Cache

**Location**: `plugins/validate-types.js`

**Pattern**: Module-level cache (performance optimization, documented exception to DI pattern)

**Implementation**:
```javascript
// plugins/validate-types.js
const compilerCache = new Map();

export function beforeAccept(docstring, item, config) {
  const filepath = item.filepath;

  // Cache TypeScript compiler program (expensive to create)
  if (compilerCache.has(filepath)) {
    return compilerCache.get(filepath);
  }

  const program = createTypeScriptProgram(filepath);
  compilerCache.set(filepath, program);

  return program;
}
```

**Performance**:
- **Without cache**: 100-500 ms per validation (TypeScript program creation)
- **With cache**: 5-10 ms per validation (program reuse)
- **Speedup**: 10-100× for repeated validations

**Cache Lifetime**: Session only (cleared when `docimp improve` exits)

**Hit Rate**: 80-90% in typical improve sessions (same files validated multiple times)

---

### Workflow State Cache

**File**: `.docimp/workflow-state.json`

**Purpose**: Persistent file checksums for incremental analysis

**Structure**:
```json
{
  "last_analyze": {
    "timestamp": "2025-11-12T14:30:00Z",
    "file_checksums": {
      "src/analyzer.py": "abc123...",
      "src/parser.py": "def456..."
    }
  }
}
```

**Cache Invalidation**: Automatic (file modification detected via checksum mismatch)

**Performance Benefit**: Incremental analysis (see Section 4)

---

## 6. Performance Benchmarks

### Benchmark Suite

**File**: `cli/src/__tests__/performance.bench.test.ts`

**Benchmarks**:
```typescript
describe('Performance Benchmarks', () => {
  it('workflow state update should complete in < 100ms', async () => {
    const start = Date.now();

    // Perform workflow state update
    await workflowStateManager.updateCommandState('analyze', {
      item_count: 100,
      file_checksums: generateChecksums(100),
    });

    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(100);  // 100ms target
  });

  it('file invalidation check should complete in < 500ms', async () => {
    // Benchmark checksum comparison for 100 files
    // ...
  });

  it('status command should complete in < 50ms', async () => {
    // Benchmark status command execution
    // ...
  });
});
```

**CI Integration**: Benchmarks run in TypeScript Tests job, fail if targets exceeded

**Target Performance**:
| Operation                  | Target Time | Current Avg |
|----------------------------|-------------|-------------|
| Workflow state update      | < 100ms     | 40-60ms     |
| File invalidation (100)    | < 500ms     | 200-300ms   |
| Status command             | < 50ms      | 15-25ms     |
| Incremental analysis (10%) | < 5s        | 2-4s        |

---

### Regression Detection

**Process**:
1. Benchmark tests run in CI (TypeScript Tests job)
2. If benchmark fails (exceeds target), CI fails
3. Developer investigates performance regression
4. Fix or update benchmark target (if intentional slowdown)

**Example CI Failure**:
```
Performance Benchmarks > workflow state update should complete in < 100ms

Expected: < 100ms
Received: 145ms

  ● Benchmark failure: Workflow state update took 145ms (target: 100ms)
```

---

## 7. Bottleneck Identification

### Python Performance Profiling

**Tool**: `cProfile`

**Usage**:
```bash
# Profile specific function
uv run python -m cProfile -s cumtime analyzer/src/main.py analyze ./src

# Output:
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#       100   20.123    0.201   25.456    0.255 parser.py:45(parse_file)
#        23    1.234    0.054    2.456    0.107 impact.py:12(calculate_score)
```

**Identify Bottlenecks**:
- High `cumtime`: Total time spent in function (including subcalls)
- High `tottime`: Time spent in function itself (excluding subcalls)

**Example Optimization**:
```python
# Before (slow):
def calculate_complexity(node):
    # Re-parses AST every call
    tree = ast.parse(node.source)
    return len(list(ast.walk(tree)))

# After (fast):
def calculate_complexity(node):
    # Use pre-parsed AST node
    return len(list(ast.walk(node)))
```

---

### TypeScript Performance Profiling

**Tool**: Node.js built-in profiler

**Usage**:
```bash
# Generate CPU profile
node --cpu-prof cli/dist/index.js analyze ./src

# Output: CPU.20250101.123456.12345.0.001.cpuprofile

# Analyze with Chrome DevTools:
# 1. Open Chrome → chrome://inspect
# 2. Click "Open dedicated DevTools for Node"
# 3. Profiler tab → Load profile
```

**Identify Bottlenecks**:
- Flame graph shows time spent per function
- Wide bars = slow functions
- Deep stacks = complex call chains

---

## 8. Trade-offs & Decisions

### Trade-off Matrix

| Optimization              | Speed Gain | Cost/Trade-off                       | Decision       |
|---------------------------|------------|--------------------------------------|----------------|
| Parallel CI jobs          | 3-4 min    | Higher GH Actions minutes            | ✓ Implement    |
| npm/uv caching            | 30-45 sec  | Cache invalidation complexity        | ✓ Implement    |
| Sequential Jest           | -4 sec     | Stability (no flaky tests)           | ✓ Worth it     |
| lint-staged               | 4-6 sec    | Incremental checking only            | ✓ Implement    |
| Ruff (vs black+flake8)    | 5-7 sec    | Single tool, less flexibility        | ✓ Implement    |
| Incremental analysis      | 90% time   | Complexity, stale result risk        | ✓ Implement    |
| Plugin validation cache   | 10-100×    | Session-scoped (no persistence)      | ✓ Implement    |
| Python 3.13 only (no matrix) | 240 sec | No backward compat testing           | ✓ Implement    |

---

### Decision Rationale: Sequential Jest

**Problem**: Integration tests conflict on `.docimp/state/.git/index.lock`

**Options**:
1. **Per-test state isolation**: Each test gets `.docimp-test-<uuid>/` directory
2. **Sequential execution**: `maxWorkers: 1`

**Analysis**:
- **Option 1**: Complex (setup/teardown), +15% test code overhead, +2-3 minutes development time
- **Option 2**: Simple (1 line config), -4 seconds test time, zero flaky tests

**Decision**: Option 2 (sequential execution)

**Rationale**: Developer time (avoiding flaky tests) > 4 seconds CI time

---

## Quick Reference

### Performance Commands

```bash
# Fast Development Iteration
uv run pytest -m unit                     # Unit tests only (2-3s)
npm run lint -- src/commands/*.ts         # Lint specific files
make test-unit                            # Python unit tests

# Incremental Analysis
docimp analyze ./src --incremental        # 90% faster for small changes
docimp analyze ./src --incremental --dry-run  # Preview changes

# Full Validation (Pre-Commit)
make quality                              # All checks (lint, type, test)
npm run test:all                          # All TypeScript tests

# Profiling
python -m cProfile -s cumtime script.py   # Python profiling
node --cpu-prof cli/dist/index.js         # TypeScript profiling

# Benchmarking
npm test -- performance.bench.test.ts     # Run performance benchmarks
```

---

### Performance Targets

| Workflow Stage         | Target Time | Current Avg | Status |
|------------------------|-------------|-------------|--------|
| Full CI pipeline       | < 6 min     | 4-5 min     | ✓      |
| Python tests           | < 10 sec    | 4-6 sec     | ✓      |
| TypeScript tests       | < 20 sec    | 8-12 sec    | ✓      |
| Ruff lint              | < 2 sec     | 0.5-1 sec   | ✓      |
| ESLint                 | < 10 sec    | 3-5 sec     | ✓      |
| Incremental analysis   | < 5 sec     | 2-4 sec     | ✓      |
| Workflow state update  | < 100 ms    | 40-60 ms    | ✓      |

---

## Troubleshooting

### Issue: CI takes > 10 minutes

**Symptom**: GitHub Actions workflow exceeds 10 minutes

**Diagnosis**:
```bash
# Check job durations in GitHub Actions UI
# Identify slowest job
```

**Common Causes**:
1. Dependency cache miss (reinstalling all packages)
2. Network issues (slow package downloads)
3. Test failures (retries, debugging output)

**Solution**:
```yaml
# Verify cache configuration
- uses: actions/setup-node@v4
  with:
    cache: 'npm'  # Ensure cache enabled
```

---

### Issue: Tests slower than benchmarks

**Symptom**: `pytest` taking 15+ seconds (target: < 10 seconds)

**Diagnosis**:
```bash
# Run with verbose timing
uv run pytest -v --durations=10

# Output:
# 10 slowest tests:
#   2.34s test_analyze_large_repo
#   1.89s test_git_integration
```

**Solution**: Optimize or mark slow tests
```python
@pytest.mark.slow
def test_analyze_large_repo():
    # Long-running test
    pass

# Run fast tests only by default
uv run pytest -m "not slow"
```

---

## Summary

DocImp's infrastructure is optimized for developer velocity while maintaining quality:

- **CI/CD**: 4-5 minutes (parallel jobs, dependency caching, no matrix)
- **Testing**: Sequential Jest (stability), pytest markers (fast iteration)
- **Linting**: lint-staged (incremental), Ruff (10× faster than black+flake8)
- **Analysis**: Incremental mode (90% savings for small changes)
- **Caching**: Plugin validation cache (10-100× speedup), workflow state persistence
- **Benchmarks**: Automated performance regression detection

**Next Steps**: See `INFRASTRUCTURE-DOCS_22-Future-Extension-Points.md` for guidance on where to add new infrastructure components without compromising performance.
