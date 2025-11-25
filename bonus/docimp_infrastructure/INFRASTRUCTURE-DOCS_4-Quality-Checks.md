# Infrastructure Documentation: Quality Checks

## Overview

DocImp enforces **polyglot quality standards** across Python, TypeScript, and JavaScript with automated linting, formatting, type checking, and testing:

**Python Stack**:
- **ruff**: Linting + formatting (8 rule groups, Python 3.13+)
- **mypy**: Static type checking
- **pytest**: Testing framework (46+ test files)

**TypeScript/JavaScript Stack**:
- **ESLint**: Linting (7 plugins, flat config)
- **Prettier**: Code formatting
- **Jest**: Testing framework (27+ test files, ESM preset)
- **TypeScript Compiler**: Type checking + JSDoc validation

**Enforcement Layers**:
1. **Pre-commit hooks** (lint-staged) - Auto-fix on commit
2. **CI/CD** (GitHub Actions) - Block PRs with violations
3. **direnv interception** - Force `uv run` prefix for Python tools
4. **Claude Code permissions** - Block bare python/pip/pytest

---

## Python Quality: ruff

### Configuration Files

**Root-level**: `/Users/nik/Documents/Code/Polyglot/docimp/ruff.toml`
```toml
exclude = [
  "test-samples/malformed",
  "test-samples/mixed-valid-invalid",
  ".venv", "venv", "__pycache__", ".pytest_cache",
  "node_modules"
]
```

**Analyzer-level**: `/Users/nik/Documents/Code/Polyglot/docimp/analyzer/pyproject.toml`
```toml
[tool.ruff]
target-version = "py313"
line-length = 88
exclude = [".venv", "venv", "__pycache__", ".pytest_cache"]

[tool.ruff.lint]
select = [
  "E",     # pycodestyle errors (PEP 8 violations)
  "F",     # pyflakes (undefined names, unused imports)
  "DTZ",   # flake8-datetimez (timezone-aware datetime)
  "UP",    # pyupgrade (modernize syntax for Python 3.13+)
  "PTH",   # flake8-use-pathlib (prefer pathlib.Path)
  "I",     # isort (import sorting)
  "SIM",   # flake8-simplify (reduce complexity)
  "PERF",  # perflint (performance anti-patterns)
  "YTT",   # flake8-2020 (modern version checks)
]
ignore = []  # Strict enforcement - no ignored rules
```

### Rule Groups Explained

| Group | Name | Purpose | Examples |
|-------|------|---------|----------|
| **E** | pycodestyle | PEP 8 compliance | Line length, indentation, whitespace |
| **F** | pyflakes | Logic errors | Undefined names, unused imports, duplicate keys |
| **DTZ** | flake8-datetimez | Timezone safety | Naive datetime usage detection |
| **UP** | pyupgrade | Modern syntax | `dict[str, int]` vs `Dict[str, int]`, `\| ` vs `Union` |
| **PTH** | flake8-use-pathlib | Path handling | `Path()` vs `os.path.join()` |
| **I** | isort | Import organization | Grouped/sorted imports (builtin → external → internal) |
| **SIM** | flake8-simplify | Code simplification | Remove unnecessary `if`/`else`, `return` statements |
| **PERF** | perflint | Performance | List comprehension vs generator, dict lookups |
| **YTT** | flake8-2020 | Version checks | `sys.version_info >= (3, 13)` vs string comparison |

### Example Violations and Fixes

**DTZ (Timezone-aware datetime)**:
```python
# ✗ Violation (DTZ005: datetime.now() with no tz argument)
from datetime import datetime
now = datetime.now()

# ✓ Fixed
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```

**UP (Modern Python 3.13 syntax)**:
```python
# ✗ Violation (UP006: Use dict instead of Dict)
from typing import Dict
data: Dict[str, int] = {}

# ✓ Fixed
data: dict[str, int] = {}  # PEP 585 built-in generics
```

**PTH (Use pathlib)**:
```python
# ✗ Violation (PTH118: os.path.join should be replaced with Path)
import os
path = os.path.join('/tmp', 'file.txt')

# ✓ Fixed
from pathlib import Path
path = Path('/tmp') / 'file.txt'
```

**SIM (Simplify code)**:
```python
# ✗ Violation (SIM108: Use ternary operator instead of if/else)
if condition:
    value = 'yes'
else:
    value = 'no'

# ✓ Fixed
value = 'yes' if condition else 'no'
```

### Running ruff

**Lint (check only)**:
```bash
uv run ruff check .
# Or via interceptor:
ruff check .  # direnv redirects to: uv run ruff check .
```

**Lint with auto-fix**:
```bash
uv run ruff check . --fix
```

**Format (auto-fix all formatting)**:
```bash
uv run ruff format .
```

**Combined (lint + format)**:
```bash
uv run ruff check . --fix && uv run ruff format .
```

**Check specific file**:
```bash
uv run ruff check analyzer/src/parsers/python_parser.py
```

---

## Python Quality: mypy

### Configuration

**File**: `analyzer/pyproject.toml`
```toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true        # Warn if function returns Any
warn_unused_configs = true    # Warn about unused mypy config options
ignore_missing_imports = true # Don't error on missing type stubs for 3rd party
```

### Strict Rules

| Rule | Purpose | Example |
|------|---------|---------|
| `warn_return_any` | Catch overly generic return types | `def foo() -> Any` triggers warning |
| `warn_unused_configs` | Catch typos in mypy config | `warn_retrun_any` (typo) triggers warning |
| `ignore_missing_imports` | Allow 3rd party libs without stubs | `anthropic` has no type stubs → ignore instead of error |

### Running mypy

**Check all source**:
```bash
uv run mypy analyzer/src --ignore-missing-imports
```

**Check specific file**:
```bash
uv run mypy analyzer/src/parsers/python_parser.py
```

**Example Output**:
```
analyzer/src/commands/analyze.py:45: error: Function is missing a return type annotation  [no-untyped-def]
analyzer/src/commands/analyze.py:67: error: Argument 1 to "create_analyzer" has incompatible type "str"; expected "Path"  [arg-type]
Found 2 errors in 1 file (checked 23 source files)
```

---

## Python Quality: pytest

### Configuration

**File**: `analyzer/pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
markers =
  unit: Unit tests
  integration: Integration tests
  slow: Tests that take a long time to run
```

### Test Organization

```
analyzer/tests/
├── test_analyzer.py           # Core analyzer functionality
├── test_analyze_*.py          # Analyze command variants (incremental, auto-clean)
├── test_audit_*.py            # Audit command and session state
├── test_cli.py                # CLI entry point
├── test_cmd_*.py              # Individual commands (status, etc.)
├── test_conflict_resolution.py # Git merge conflict handling
├── test_coverage.py           # Coverage calculations
├── test_di_compliance.py      # Dependency injection validation
├── test_git_integration.py    # Git operations
├── test_parser_*.py           # Parser-specific tests
└── [30+ more test files]
```

**Total**: 46+ test files

### Test Markers

**Define markers** in `pytest.ini`:
```ini
markers =
  unit: Unit tests
  integration: Integration tests
  slow: Tests that take a long time to run
```

**Use markers** in tests:
```python
import pytest

@pytest.mark.unit
def test_parse_function():
    """Unit test for parsing function."""
    assert parse("def foo(): pass") == expected_item

@pytest.mark.integration
def test_analyze_workflow():
    """Integration test for complete analyze workflow."""
    result = run_analyze("./test-samples/example-project")
    assert result.total_items > 0

@pytest.mark.slow
def test_large_codebase_analysis():
    """Slow test analyzing large codebase."""
    result = run_analyze("./large-codebase")
    assert result.coverage_percent > 70
```

**Run specific markers**:
```bash
# Run only unit tests
uv run pytest -m unit

# Run integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"
```

### Running pytest

**Run all tests**:
```bash
uv run pytest -v
```

**Run with coverage**:
```bash
uv run pytest -v --cov=analyzer/src --cov-report=term
```

**Run specific test file**:
```bash
uv run pytest analyzer/tests/test_analyzer.py -v
```

**Run specific test function**:
```bash
uv run pytest analyzer/tests/test_analyzer.py::test_analyze_python_file -v
```

**Example Output**:
```
============== test session starts ==============
collected 127 items

analyzer/tests/test_analyzer.py::test_analyze_python_file PASSED
analyzer/tests/test_analyzer.py::test_analyze_typescript_file PASSED
analyzer/tests/test_parser_python.py::test_parse_function PASSED
...

============== 127 passed in 3.45s ==============
```

---

## TypeScript/JavaScript Quality: ESLint

### Configuration

**File**: `cli/eslint.config.mjs` (Flat config format, ESLint v9+)

**Plugin Stack** (7 plugins):
```javascript
import eslint from '@eslint/js';                      // Base recommended rules
import tseslint from '@typescript-eslint/eslint-plugin'; // TypeScript-specific
import jsdoc from 'eslint-plugin-jsdoc';              // JSDoc validation
import unicorn from 'eslint-plugin-unicorn';          // Modern JS best practices
import n from 'eslint-plugin-n';                      // Node.js compatibility
import promise from 'eslint-plugin-promise';          // Promise best practices
import importPlugin from 'eslint-plugin-import';      // Import ordering
```

### Base Configuration

```javascript
export default [
  eslint.configs.recommended,
  unicorn.configs['flat/recommended'],
  n.configs['flat/recommended-module'],
  promise.configs['flat/recommended'],
  importPlugin.flatConfigs.recommended,
  importPlugin.flatConfigs.typescript,

  // Customizations
  {
    rules: {
      // Unicorn: Downgrade aggressive rules
      'unicorn/no-array-reduce': 'warn',       // Reduce is sometimes clearest
      'unicorn/prefer-top-level-await': 'warn', // Not always possible
      'unicorn/no-null': 'off',                // External APIs use null
      'unicorn/prevent-abbreviations': [
        'error',
        {
          replacements: { i: false }  // "i" in i-config.ts = "interface"
        }
      ],

      // Node: Target Node 24+
      'n/no-unsupported-features/node-builtins': [
        'error',
        { version: '>=24.0.0' }
      ],

      // Import: Consistent ordering
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          'newlines-between': 'never',
          alphabetize: { order: 'asc', caseInsensitive: true }
        }
      ]
    }
  }
]
```

### TypeScript-Specific Configuration

```javascript
{
  files: ['**/*.ts'],
  languageOptions: {
    parser: tsparser,
    parserOptions: {
      ecmaVersion: 2022,
      sourceType: 'module'
    }
  },
  plugins: { '@typescript-eslint': tseslint },
  rules: {
    ...tseslint.configs.recommended.rules,
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'off', // Let inference work
    '@typescript-eslint/no-explicit-any': 'warn'  // Warn but don't error
  }
}
```

### JavaScript JSDoc Configuration

**Stricter rules for JavaScript** (no TypeScript type system):
```javascript
{
  files: ['**/*.js', '**/*.mjs', '**/*.cjs'],
  plugins: { jsdoc },
  rules: {
    'jsdoc/require-jsdoc': [
      'error',
      {
        require: {
          FunctionDeclaration: true,
          MethodDefinition: true,
          ClassDeclaration: true,
          ArrowFunctionExpression: false  // Optional for arrow functions
        }
      }
    ],
    'jsdoc/require-param': 'error',
    'jsdoc/require-param-type': 'error',
    'jsdoc/require-returns': 'error',
    'jsdoc/require-returns-type': 'error',
    'jsdoc/check-types': 'error'  // TypeScript compiler validates types
  }
}
```

### Example Violations and Fixes

**Unicorn: Array reduce warning**:
```javascript
// ⚠️  Warning (unicorn/no-array-reduce)
const sum = numbers.reduce((acc, n) => acc + n, 0);

// Alternative (but reduce is sometimes clearer)
let sum = 0;
for (const n of numbers) sum += n;
```

**Import ordering**:
```javascript
// ✗ Violation (import/order)
import { foo } from './utils';
import * as fs from 'node:fs';
import chalk from 'chalk';

// ✓ Fixed (builtin → external → internal)
import * as fs from 'node:fs';
import chalk from 'chalk';
import { foo } from './utils';
```

**TypeScript unused vars**:
```javascript
// ✗ Violation (@typescript-eslint/no-unused-vars)
function processData(input: string, _format: string): void {
  return input.trim();  // _format unused but not ignored
}

// ✓ Fixed
function processData(input: string, _format: string): void {
  return input.trim();  // Leading _ = intentionally unused
}
```

### Running ESLint

**Lint all TypeScript/JavaScript**:
```bash
cd cli
npm run lint
# Or: npx eslint src --ext .ts,.js,.mjs,.cjs
```

**Lint with auto-fix**:
```bash
npm run lint -- --fix
```

**Lint JSDoc specifically**:
```bash
npm run lint:jsdoc
```

**Example Output**:
```
/path/to/cli/src/commands/analyze.ts
  45:7   error    Function 'runAnalyze' is missing return type  @typescript-eslint/explicit-function-return-type
  67:15  warning  Unexpected any. Specify a different type      @typescript-eslint/no-explicit-any

/path/to/cli/src/utils/config.js
  12:1   error    Missing JSDoc comment                         jsdoc/require-jsdoc
  23:10  error    Missing JSDoc @returns tag                    jsdoc/require-returns

✖ 4 problems (3 errors, 1 warning)
```

---

## TypeScript/JavaScript Quality: Prettier

### Configuration

**File**: `.prettierrc`
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf",
  "overrides": [
    {
      "files": "*.json",
      "options": { "printWidth": 100 }
    },
    {
      "files": "*.md",
      "options": { "printWidth": 88, "proseWrap": "always" }
    }
  ]
}
```

### Format Rules

| Option | Value | Purpose |
|--------|-------|---------|
| `semi` | `true` | Always add semicolons |
| `singleQuote` | `true` | Use `'` instead of `"` |
| `printWidth` | `80` | Max line length (standard) |
| `tabWidth` | `2` | 2-space indentation |
| `trailingComma` | `es5` | Add trailing commas where valid in ES5 |
| `arrowParens` | `always` | Always parenthesize arrow function params |
| `endOfLine` | `lf` | Unix-style line endings |

**Overrides**:
- JSON files: 100 character width (allow longer lines)
- Markdown files: 88 character width, wrap prose

### Running Prettier

**Check formatting**:
```bash
cd cli
npm run format:check
```

**Auto-format all files**:
```bash
npm run format
```

**Format specific file**:
```bash
npx prettier --write src/commands/analyze.ts
```

**Example Output** (check):
```
Checking formatting...
src/commands/analyze.ts
src/utils/config.js
Code style issues found in the above file(s). Forgot to run Prettier?
```

---

## TypeScript/JavaScript Quality: TypeScript Compiler

### Configuration

**File**: `cli/tsconfig.json`

**Critical Settings**:
```json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "allowJs": true,           // Parse JavaScript files
    "checkJs": true,           // Type-check JSDoc in .js files (CRITICAL)
    "outDir": "./dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "exclude": [
    "node_modules", "dist", "**/*.test.ts",
    "**/__tests__/fixtures/**"
  ]
}
```

### Key Features

**checkJs: true** - **CRITICAL for DocImp**:
- Enables **real JSDoc type-checking** via TypeScript compiler
- Not cosmetic parsing - actual type validation
- Validates parameter names, types, return types
- Used by `validate-types.js` plugin to catch JSDoc errors

**strict: true** - Comprehensive type safety:
- `noImplicitAny`: All types must be explicit
- `strictNullChecks`: `null` and `undefined` must be handled
- `strictFunctionTypes`: Function parameter contravariance
- `strictPropertyInitialization`: Class properties must be initialized

**NodeNext module resolution**:
- Deterministic ESM/CJS interop
- Respects `package.json` `"type": "module"`
- Handles `.mjs` and `.cjs` extensions correctly

### Running TypeScript Compiler

**Type check (no emit)**:
```bash
cd cli
npx tsc --noEmit
```

**Build (compile to dist/)**:
```bash
npm run build
```

**Build with watch mode**:
```bash
npm run build:watch
```

**Example Output**:
```
src/commands/analyze.ts:45:7 - error TS7006: Parameter 'config' implicitly has an 'any' type.

45 function runAnalyze(config) {
         ~~~~~~

src/utils/state.ts:67:3 - error TS2322: Type 'string | undefined' is not assignable to type 'string'.

67   filepath: data.filepath,
     ~~~~~~~~

Found 2 errors in 2 files.
```

---

## TypeScript/JavaScript Quality: Jest

### Configuration

**File**: `cli/jest.config.js`

```javascript
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],
  maxWorkers: 1,  // Sequential execution (shared .docimp/state)

  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',  // ESM .js extensions
    '^@/(.*)$': '<rootDir>/src/$1' // @ alias
  },

  transform: {
    '^.+\\.ts$': [
      'ts-jest',
      {
        useESM: true,
        isolatedModules: true
      }
    ]
  },

  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html']
};
```

### Key Settings

**maxWorkers: 1** - Sequential execution:
- Prevents race conditions on shared `.docimp/state/` files
- Integration tests write to same state directory
- Parallel execution would cause test flakiness

**ESM Support**:
- `preset: 'ts-jest/presets/default-esm'`
- `extensionsToTreatAsEsm: ['.ts']`
- `useESM: true` in transform

**Module Name Mapper**:
- `^(\\.{1,2}/.*)\\.js$': '$1'` - Handles TypeScript-generated `.js` imports
- `^@/(.*)$': '<rootDir>/src/$1'` - `@/` alias for clean imports

### Test Organization

```
cli/src/__tests__/
├── commands/            # Command-specific tests
│   ├── analyze-command.test.ts
│   ├── audit-command.test.ts
│   └── plan-command.test.ts
├── config/              # Configuration tests
│   └── config-loader.test.ts
├── display/             # Display/output tests
│   └── display.test.ts
├── fixtures/            # Test fixtures and mock data
├── integration/         # End-to-end integration tests
│   └── workflow.test.ts
├── parsers/             # Parser tests
├── plugins/             # Plugin system tests
├── python-bridge/       # Python subprocess communication
├── session/             # Session management tests
└── setup.ts             # Global Jest setup
```

**Total**: 27+ test files

### Running Jest

**Run all tests**:
```bash
cd cli
npm test
```

**Run with coverage**:
```bash
npm test -- --coverage
```

**Run specific test file**:
```bash
npm test -- src/__tests__/commands/analyze-command.test.ts
```

**Run in watch mode**:
```bash
npm test -- --watch
```

**Example Output**:
```
PASS  src/__tests__/commands/analyze-command.test.ts
  AnalyzeCommand
    ✓ should execute analyze successfully (45 ms)
    ✓ should handle Python bridge errors (23 ms)
    ✓ should validate incremental flag (12 ms)

Test Suites: 27 passed, 27 total
Tests:       127 passed, 127 total
Snapshots:   0 total
Time:        8.456 s
```

---

## Pre-Commit Integration (lint-staged)

### Configuration

**File**: `cli/package.json`

```json
{
  "lint-staged": {
    "*.{ts,js,mjs,cjs}": [
      "prettier --write",
      "eslint --fix"
    ],
    "*.py": [
      "ruff format",
      "ruff check --fix"
    ]
  }
}
```

### Workflow

**On git commit**:
1. Husky pre-commit hook triggers
2. Calls `npx lint-staged`
3. lint-staged identifies staged files
4. Runs appropriate tools on each file type:
   - **TypeScript/JavaScript**: Prettier → ESLint
   - **Python**: ruff format → ruff check
5. Auto-fixes applied to staged files
6. If fixes made, adds them to commit
7. If violations can't be auto-fixed, commit fails

**Example Execution**:
```bash
$ git add src/analyzer.py cli/src/commands.ts
$ git commit -m "Add new command"

✔ Preparing lint-staged...
✔ Running tasks for staged files...
  ✔ cli/src/commands.ts
    ✔ prettier --write
    ✔ eslint --fix
  ✔ src/analyzer.py
    ✔ ruff format
    ✔ ruff check --fix
✔ Applying modifications from tasks...
✔ Cleaning up temporary files...
[feature-branch abc1234] Add new command
 2 files changed, 45 insertions(+)
```

---

## CI/CD Integration

### GitHub Actions Workflow

**File**: `.github/workflows/ci.yml`

**Python Quality Checks** (Job 1):
```yaml
- name: Lint with ruff
  run: uv run ruff check analyzer/

- name: Format check with ruff
  run: uv run ruff format --check analyzer/

- name: Type check with mypy
  run: uv run mypy analyzer/src --ignore-missing-imports

- name: Test with pytest
  run: uv run pytest analyzer/tests/ -v --cov=analyzer/src --cov-report=term
```

**TypeScript Quality Checks** (Job 2):
```yaml
- name: Lint with ESLint
  run: npm run lint

- name: Format check with Prettier
  run: npm run format:check

- name: JSDoc lint
  run: npm run lint:jsdoc
  continue-on-error: true

- name: Type check with TypeScript
  run: npx tsc --noEmit

- name: Build TypeScript
  run: npm run build

- name: Test with Jest
  run: npm test
```

**See `INFRASTRUCTURE-DOCS_5-CI-CD.md` for complete CI/CD documentation.**

---

## Summary

**Quality Infrastructure**:
- **8 tools**: ruff, mypy, pytest, ESLint, Prettier, TypeScript, Jest, lint-staged
- **3 enforcement layers**: Pre-commit hooks, direnv interception, CI/CD
- **Polyglot standards**: Python 3.13+, TypeScript ES2024, Node 24+

**Python Quality**:
- ruff: 8 rule groups, 88-char line length, Python 3.13+ target
- mypy: Strict type checking, warn on Any returns
- pytest: 46+ test files, markers (unit/integration/slow)

**TypeScript/JavaScript Quality**:
- ESLint: 7 plugins, flat config, Node 24+ target
- Prettier: 2-space indentation, single quotes, LF line endings
- TypeScript: checkJs:true for JSDoc validation, strict mode
- Jest: 27+ test files, ESM preset, sequential execution

**Auto-Enforcement**:
- ✓ Pre-commit hooks auto-fix violations before commit
- ✓ CI/CD blocks PRs with quality issues
- ✓ direnv forces `uv run` prefix (no bare python/pip/pytest)
- ✓ Claude Code permissions block dangerous operations

**Next Steps**: See `INFRASTRUCTURE-DOCS_5-CI-CD.md` for GitHub Actions CI/CD configuration.
