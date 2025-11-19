# Infrastructure Documentation: Critical Dependencies & Constraints

## Overview

DocImp's polyglot architecture requires careful coordination of Python, TypeScript, and JavaScript dependencies. This document catalogs all critical dependencies, version constraints, compatibility requirements, and upgrade procedures.

Understanding these constraints prevents compatibility issues, ensures CI/CD stability, and guides dependency update decisions. Version requirements reflect architectural decisions (e.g., ESM-only packages, modern Python features) and external constraints (e.g., API compatibility, tool support).

## 1. Python Dependencies

### Core Runtime Dependencies

#### anthropic (Claude API Client)

**Version Constraint**: `>=0.72.0, <1.0.0`

**Purpose**: Communication with Claude AI for docstring generation

**Critical Features**:
- Streaming responses
- Timeout configuration
- Error handling (rate limits, API errors)
- Message API (not legacy completions)

**Breaking Changes to Watch**:
- `0.72.0 → 0.85.0`: Renamed `timeout` parameter to `http_timeout`
- `1.0.0` (future): Major version may introduce breaking API changes

**Usage in Codebase**:
```python
# analyzer/src/claude.py
from anthropic import Anthropic

client = Anthropic(
    api_key=api_key,
    http_timeout=30  # Renamed in v0.85.0
)

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
```

**Upgrade Path**:
```bash
# Check current version
uv pip list | grep anthropic

# Update to specific version
uv add "anthropic>=0.85.0,<1.0.0"

# Regenerate lockfiles
uv pip compile pyproject.toml -o requirements.lock

# Test
uv run pytest analyzer/tests/test_claude.py -v
```

---

#### pydantic (Data Validation)

**Version Constraint**: `>=2.12.3, <3.0.0`

**Purpose**: Runtime data validation, JSON schema generation, type safety

**Critical Features**:
- `BaseModel` for structured data (CodeItem, AnalysisResult)
- JSON serialization/deserialization
- Field validation
- Type coercion

**Why Pydantic v2**:
- 5-50x performance improvement over v1
- Better TypeScript interop (JSON schema export)
- Core rewritten in Rust (pydantic-core)

**Breaking Changes (v1 → v2)**:
- `Config` class → `model_config` dict
- `.dict()` → `.model_dump()`
- `.json()` → `.model_dump_json()`

**Usage in Codebase**:
```python
# analyzer/src/models.py
from pydantic import BaseModel, Field

class CodeItem(BaseModel):
    """Structured representation of parsed code entity."""
    name: str
    type: str
    filepath: str
    line_number: int
    complexity: int = Field(ge=0)  # >= 0 validation

    model_config = {
        'frozen': False,  # Mutable
        'validate_assignment': True  # Validate on field update
    }

# Serialization (v2 API)
item = CodeItem(...)
json_str = item.model_dump_json()  # Not .json()
dict_repr = item.model_dump()      # Not .dict()
```

**Upgrade Path**:
```bash
# Update pydantic
uv add "pydantic>=2.15.0,<3.0.0"

# Find deprecated API usage
uv run ruff check . --select UP  # pyupgrade detects old patterns

# Manual migration
# Before (v1):
class Model(BaseModel):
    class Config:
        frozen = True

# After (v2):
class Model(BaseModel):
    model_config = {'frozen': True}
```

---

#### typing-extensions

**Version Constraint**: `>=4.9.0`

**Purpose**: Backport of typing features for older Python versions (used for forward compatibility)

**Critical Features**:
- `TypedDict` (structured dicts with type hints)
- `Literal` types
- `NotRequired` for TypedDict optional fields

**Usage**:
```python
from typing import Optional
from typing_extensions import TypedDict, NotRequired

class ConfigDict(TypedDict):
    timeout: int
    retry: NotRequired[bool]  # Optional field in TypedDict
```

**Note**: Python 3.13 includes most features, but `typing-extensions` provides forward compatibility for future additions.

---

### Development Dependencies

#### pytest (Testing Framework)

**Version Constraint**: `>=7.4.0`

**Purpose**: Unit and integration testing

**Critical Features**:
- Fixtures for test setup/teardown
- Parametrized tests
- Coverage integration (`pytest-cov`)
- Markers for test organization

**Configuration**:
```ini
# analyzer/pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --strict-markers --tb=short
markers =
  unit: Unit tests
  integration: Integration tests
  slow: Long-running tests
```

**Usage**:
```bash
uv run pytest -v                      # All tests
uv run pytest -m unit                 # Only unit tests
uv run pytest --cov=src --cov-report=term  # With coverage
```

---

#### ruff (Linting & Formatting)

**Version Constraint**: `>=0.1.0`

**Purpose**: Fast Python linter and formatter (replaces flake8, black, isort)

**Critical Features**:
- 8 rule groups enabled (E, F, DTZ, UP, PTH, I, SIM, PERF, YTT)
- Auto-fix capability
- Import sorting
- pyupgrade syntax modernization

**Rule Groups**:
```toml
# analyzer/pyproject.toml
[tool.ruff.lint]
select = [
  "E",      # pycodestyle errors (PEP 8)
  "F",      # pyflakes (undefined names, unused imports)
  "DTZ",    # flake8-datetimez (timezone-aware datetime)
  "UP",     # pyupgrade (Python 3.13 syntax)
  "PTH",    # flake8-use-pathlib (prefer pathlib over os.path)
  "I",      # isort (import ordering)
  "SIM",    # flake8-simplify (reduce complexity)
  "PERF",   # perflint (performance anti-patterns)
  "YTT"     # flake8-2020 (modern version checks)
]
```

**Usage**:
```bash
uv run ruff check .                   # Lint only
uv run ruff check . --fix             # Auto-fix
uv run ruff format .                  # Format code
uv run ruff format --check .          # Check formatting without changes
```

---

#### mypy (Type Checking)

**Version Constraint**: `>=1.7.0`

**Purpose**: Static type checking for Python

**Configuration**:
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true  # Allow imports without type stubs
```

**Usage**:
```bash
uv run mypy analyzer/src --ignore-missing-imports
```

**Common Warnings**:
- `Missing return type`: Add `-> ReturnType` to function signatures
- `Incompatible types`: Fix type mismatches
- `No module named 'X'`: Third-party library without type stubs (suppressed with `ignore_missing_imports`)

---

## 2. TypeScript/JavaScript Dependencies

### Core Runtime Dependencies

#### commander (CLI Framework)

**Version**: `^12.1.0`

**Purpose**: Command-line argument parsing

**Critical Features**:
- Command registration
- Argument/option parsing
- Auto-conversion: kebab-case flags → camelCase options
- Help text generation

**Usage**:
```typescript
// cli/src/index.ts
import { Command } from 'commander';

const program = new Command();

program
  .name('docimp')
  .description('Documentation improvement tool')
  .version('1.0.6-α');

program
  .command('analyze')
  .argument('<path>', 'Path to analyze')
  .option('--incremental', 'Incremental analysis')
  .action(async (path: string, options: { incremental?: boolean }) => {
    // options.incremental (auto-converted from --incremental)
  });

program.parse();
```

---

#### chalk (Terminal Colors)

**Version**: `^5.3.0`

**ESM-Only Constraint**: chalk v5+ is ESM-only (no CommonJS support)

**Purpose**: Colorized terminal output

**Critical Features**:
- ANSI color codes
- Template literals support
- Auto-detects color support

**Why ESM-Only Matters**:
```typescript
// ✓ CORRECT (ESM import)
import chalk from 'chalk';

// ✗ WRONG (CommonJS - does not work with chalk v5)
const chalk = require('chalk');  // ERROR: chalk v5 is ESM-only
```

**Usage**:
```typescript
import chalk from 'chalk';

console.log(chalk.green('✓ Success'));
console.log(chalk.red('✗ Error'));
console.log(chalk.yellow('⚠ Warning'));
console.log(chalk.blue.bold('INFO:'), 'Message');
```

**Downgrade Path (if ESM problematic)**:
```bash
# Downgrade to CommonJS-compatible version
npm install chalk@4.1.2
```

---

#### ora (Spinners)

**Version**: `^8.1.1`

**ESM-Only Constraint**: ora v6+ is ESM-only

**Purpose**: Terminal spinners for long-running operations

**Usage**:
```typescript
import ora from 'ora';

const spinner = ora('Analyzing codebase...').start();

// ... long operation ...

spinner.succeed('Analysis complete!');
// Or: spinner.fail('Analysis failed')
```

---

#### prompts (Interactive Prompts)

**Version**: `^2.4.2`

**Purpose**: Interactive CLI prompts for user input

**Critical Features**:
- Text input
- Select (single choice)
- Multi-select
- Confirm (yes/no)

**Usage**:
```typescript
import prompts from 'prompts';

const response = await prompts({
  type: 'select',
  name: 'action',
  message: 'What would you like to do?',
  choices: [
    { title: 'Accept', value: 'accept' },
    { title: 'Edit', value: 'edit' },
    { title: 'Skip', value: 'skip' },
  ],
});

console.log(response.action);  // 'accept', 'edit', or 'skip'
```

---

#### uuid (UUID Generation)

**Version**: `^11.0.5`

**Purpose**: Generate unique identifiers for sessions, transactions

**Usage**:
```typescript
import { v4 as uuidv4 } from 'uuid';

const sessionId = uuidv4();  // e.g., "550e8400-e29b-41d4-a716-446655440000"
```

---

#### zod (Runtime Validation)

**Version**: `^3.24.1`

**Purpose**: Runtime type validation for JSON responses from Python

**Critical Features**:
- Schema definition
- Validation with helpful error messages
- TypeScript type inference

**Usage**:
```typescript
import { z } from 'zod';

const CodeItemSchema = z.object({
  name: z.string(),
  type: z.string(),
  filepath: z.string(),
  line_number: z.number(),
  complexity: z.number().int().min(0),
  has_docs: z.boolean(),
});

// Parse and validate
const result = CodeItemSchema.safeParse(jsonData);

if (!result.success) {
  console.error('Validation failed:', result.error);
} else {
  const item = result.data;  // Type-safe
}
```

**Why Zod (not just TypeScript)**:
- TypeScript validates at compile-time only
- Zod validates runtime data from external sources (Python stdout)
- Prevents runtime errors from malformed JSON

---

### Development Dependencies

#### TypeScript

**Version**: `^5.7.2`

**Purpose**: Type-safe JavaScript compiler

**Configuration**:
```json
// cli/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "allowJs": true,
    "checkJs": true,  // CRITICAL: Enables real JSDoc validation
    "strict": true
  }
}
```

**Critical Setting**: `checkJs: true` enables **real JSDoc type-checking** (not cosmetic parsing)

---

#### jest + ts-jest (Testing)

**Versions**:
- jest: `^29.7.0`
- ts-jest: `^29.2.5`

**Purpose**: TypeScript testing framework

**Configuration**:
```javascript
// cli/jest.config.js
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  maxWorkers: 1,  // Sequential execution (shared .docimp/state)
};
```

**Why `maxWorkers: 1`**: Integration tests share `.docimp/state/` directory. Parallel execution causes race conditions.

---

#### ESLint (Linting)

**Version**: `^9.2.1`

**Flat Config Requirement**: ESLint v9+ uses new flat config format (`eslint.config.mjs`)

**Plugins**:
- `@typescript-eslint/eslint-plugin` - TypeScript-specific rules
- `eslint-plugin-jsdoc` - JSDoc validation
- `eslint-plugin-unicorn` - JavaScript best practices
- `eslint-plugin-n` - Node.js compatibility (targets v24+)
- `eslint-plugin-promise` - Promise best practices
- `eslint-plugin-import` - Import ordering

**Configuration**:
```javascript
// cli/eslint.config.mjs
import eslint from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import jsdoc from 'eslint-plugin-jsdoc';

export default [
  eslint.configs.recommended,
  {
    plugins: { '@typescript-eslint': tseslint, jsdoc },
    rules: {
      '@typescript-eslint/explicit-function-return-type': 'error',
      'jsdoc/require-jsdoc': 'warn',
    },
  },
];
```

**Upgrade from ESLint v8**:
```bash
# Old format (.eslintrc.json) - deprecated
{
  "extends": ["eslint:recommended"],
  "plugins": ["@typescript-eslint"]
}

# New format (eslint.config.mjs) - required in v9+
export default [
  eslint.configs.recommended,
  { plugins: { '@typescript-eslint': tseslint } }
];
```

---

#### prettier (Code Formatting)

**Version**: `^3.4.2`

**Purpose**: Opinionated code formatter

**Configuration**:
```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

**Integration with ESLint**:
```javascript
// cli/eslint.config.mjs
import prettier from 'eslint-config-prettier';

export default [
  // ... other configs ...
  prettier,  // Disables ESLint rules that conflict with Prettier
];
```

---

#### husky (Git Hooks)

**Version**: `^9.1.7`

**Purpose**: Git hooks management (pre-commit, post-checkout)

**Configuration**:
```bash
# .husky/pre-commit
npm test
npx lint-staged
```

**Version Requirement**: v9+ supports per-worktree configuration via `core.hooksPath`

---

## 3. Critical Version Constraints

### Node.js Version

**Requirement**: `>=24.0.0` (pinned to `24.11.0` in `.nvmrc`)

**Why Node 24+**:
- Native TypeScript support improvements
- Faster V8 engine
- Better ESM/CommonJS interop
- Long-term support (LTS until 2027)

**Pinning Rationale**:
- nvm installs globals per Node version
- Minor updates (24.11.0 → 24.11.1) create fresh global environments
- Pinning prevents loss of global packages (`@anthropic-ai/claude-code`)

**Upgrade Procedure**:
```bash
# Update .nvmrc
echo "24.12.0" > .nvmrc

# Install new version with global package migration
nvm install 24.12.0 --reinstall-packages-from=24.11.0

# Verify globals migrated
npm list -g --depth=0

# Commit
git add .nvmrc
git commit -m "Update Node to 24.12.0"
```

---

### Python Version

**Requirement**: `>=3.13` (not 3.12 or lower)

**Why Python 3.13**:
- Improved error messages
- Performance improvements (JIT compiler)
- `typing` enhancements
- `pathlib` improvements

**Enforcement**:
```toml
# pyproject.toml
[project]
requires-python = ">=3.13"
```

**.python-version File**:
```
3.13
```

**Installation** (via pyenv):
```bash
pyenv install 3.13.0
pyenv local 3.13.0
```

---

### uv (Python Package Manager)

**Requirement**: `>=0.9.8`

**Purpose**: Fast Rust-based Python package manager (replaces pip)

**Why uv**:
- 10-100x faster than pip
- Reproducible environments (lockfiles)
- Virtual environment management
- Works with pyenv

**Installation**:
```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify version
uv --version  # Should be >= 0.9.8
```

**CI Configuration**:
```yaml
# .github/workflows/ci.yml
- uses: astral-sh/setup-uv@v5
  with:
    version: "0.9.8"  # Pin for reproducibility
```

---

### Git Version

**Requirement**: `>=2.28` (for worktree support)

**Why Git 2.28+**:
- `git worktree` stability improvements
- `extensions.worktreeConfig` support (per-worktree git config)
- Better worktree cleanup

**Verification**:
```bash
git --version
# git version 2.45.0  ✓
```

**Worktree Features Required**:
- `git worktree add`
- `git worktree list`
- `git config --worktree` (sets config per worktree)

---

## 4. Compatibility Matrices

### Python Dependency Matrix

| Package         | Min Version | Max Version | Python 3.13 | Python 3.12 | Python 3.11 |
|-----------------|-------------|-------------|-------------|-------------|-------------|
| anthropic       | 0.72.0      | <1.0.0      | ✓           | ✓           | ✓           |
| pydantic        | 2.12.3      | <3.0.0      | ✓           | ✓           | ✓           |
| typing-ext      | 4.9.0       | -           | ✓           | ✓           | ✓           |
| pytest          | 7.4.0       | -           | ✓           | ✓           | ✓           |
| ruff            | 0.1.0       | -           | ✓           | ✓           | ✓           |
| mypy            | 1.7.0       | -           | ✓           | ✓           | ✓           |

**Note**: DocImp requires Python 3.13+, but dependencies support older versions.

---

### TypeScript Dependency Matrix

| Package         | Version  | Node 24 | Node 22 | Node 20 | ESM Support | CJS Support |
|-----------------|----------|---------|---------|---------|-------------|-------------|
| commander       | 12.1.0   | ✓       | ✓       | ✓       | ✓           | ✓           |
| chalk           | 5.3.0    | ✓       | ✓       | ✓       | ✓ (only)    | ✗           |
| ora             | 8.1.1    | ✓       | ✓       | ✓       | ✓ (only)    | ✗           |
| prompts         | 2.4.2    | ✓       | ✓       | ✓       | ✓           | ✓           |
| uuid            | 11.0.5   | ✓       | ✓       | ✓       | ✓           | ✓           |
| zod             | 3.24.1   | ✓       | ✓       | ✓       | ✓           | ✓           |
| typescript      | 5.7.2    | ✓       | ✓       | ✓       | ✓           | ✓           |
| jest            | 29.7.0   | ✓       | ✓       | ✓       | ✓           | ✓           |
| eslint          | 9.2.1    | ✓       | ✓       | ✓       | ✓           | ✓           |
| prettier        | 3.4.2    | ✓       | ✓       | ✓       | ✓           | ✓           |
| husky           | 9.1.7    | ✓       | ✓       | ✓       | ✓           | ✓           |

**ESM-Only Packages**: chalk, ora require ESM imports (no `require()`)

---

## 5. Breaking Change Scenarios

### Scenario 1: Major Version Update (anthropic 1.0.0)

**Impact**: API changes, deprecated methods removed

**Preparation**:
1. Read changelog: https://github.com/anthropics/anthropic-sdk-python/releases
2. Check migration guide
3. Test in isolated environment

**Migration Steps**:
```bash
# Create test branch
git checkout -b test-anthropic-v1

# Update dependency
uv add "anthropic>=1.0.0,<2.0.0"

# Run tests (expect failures)
uv run pytest -v

# Fix code based on error messages
# Example: client.completions → client.messages (hypothetical)

# Validate all tests pass
uv run pytest -v --cov

# Merge when stable
git checkout main
git merge test-anthropic-v1
```

---

### Scenario 2: ESLint v9 → v10 (Flat Config Changes)

**Impact**: Configuration format changes

**Preparation**:
1. Review ESLint migration guide
2. Check plugin compatibility

**Migration Steps**:
```bash
# Update ESLint
npm install eslint@10

# Check for deprecated config patterns
npx eslint --print-config eslint.config.mjs

# Update plugins (may require updates)
npm install @typescript-eslint/eslint-plugin@latest

# Test linting
npm run lint

# Fix any new violations
npm run lint -- --fix
```

---

### Scenario 3: TypeScript v6 (Breaking Type Changes)

**Impact**: Stricter type checking, new errors

**Preparation**:
1. Enable `skipLibCheck: false` to catch library type issues
2. Update `@types/*` packages

**Migration Steps**:
```bash
# Update TypeScript
npm install typescript@6

# Run type check (expect errors)
npx tsc --noEmit

# Fix type errors
# Common issues:
# - Stricter null checks
# - Changed library types
# - Deprecated features removed

# Validate build
npm run build

# Run tests
npm test
```

---

## 6. Dependency Audit Procedures

### Security Audits

**Python**:
```bash
# Audit dependencies for vulnerabilities
uv pip list --outdated

# Check for security advisories (manual)
# Visit: https://pypi.org/project/<package>/
```

**TypeScript**:
```bash
# Audit npm dependencies
npm audit

# Fix vulnerabilities (auto)
npm audit fix

# Fix breaking changes (manual)
npm audit fix --force  # Use with caution
```

---

### License Compliance

**Check Licenses**:
```bash
# Python
uv pip list --format=json | jq '.[] | {name: .name, license: .license}'

# TypeScript
npx license-checker --summary
```

**Acceptable Licenses** (DocImp policy):
- MIT, Apache-2.0, BSD-3-Clause: ✓ Permissive
- GPL-3.0: ✗ Copyleft (avoid for library code)
- Proprietary: ✗ Not allowed

---

## Quick Reference

### Version Requirements Summary

| Tool       | Minimum Version | Pinned Version | Rationale                     |
|------------|-----------------|----------------|-------------------------------|
| Node.js    | 24.0.0          | 24.11.0        | ESM support, LTS              |
| Python     | 3.13            | 3.13           | Modern syntax, performance    |
| uv         | 0.9.8           | 0.9.8 (CI)     | Lockfile compatibility        |
| Git        | 2.28            | -              | Worktree features             |
| Husky      | 9.1.7           | -              | Per-worktree config           |
| ESLint     | 9.0.0           | -              | Flat config format            |
| TypeScript | 5.7.0           | -              | checkJs support               |

---

### Critical Dependency Commands

```bash
# Python
uv pip list                           # List installed packages
uv pip list --outdated                # Check for updates
uv add "package>=1.0.0,<2.0.0"        # Add/update package
uv pip compile pyproject.toml -o requirements.lock  # Regenerate lockfile

# TypeScript
npm list                              # List dependencies
npm outdated                          # Check for updates
npm install package@latest            # Update package
npm audit                             # Security audit
npm audit fix                         # Auto-fix vulnerabilities

# Version Checks
node --version                        # Node.js version
python --version                      # Python version
uv --version                          # uv version
git --version                         # Git version
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'anthropic'`

**Cause**: Python environment not synchronized with lockfile

**Solution**:
```bash
uv pip sync requirements-dev.lock
uv run pytest -v
```

---

### Issue: `Error [ERR_REQUIRE_ESM]: require() of ES Module not supported`

**Cause**: Trying to `require()` an ESM-only package (chalk, ora)

**Solution**:
```typescript
// ✗ WRONG
const chalk = require('chalk');

// ✓ CORRECT
import chalk from 'chalk';
```

Or downgrade to CommonJS-compatible version:
```bash
npm install chalk@4.1.2
```

---

### Issue: `ESLint: Failed to load config` (v9+)

**Cause**: Using old `.eslintrc.json` format with ESLint v9+

**Solution**: Migrate to flat config (`eslint.config.mjs`)

```bash
# Use migration tool
npx @eslint/migrate-config .eslintrc.json

# Manually create eslint.config.mjs
# See INFRASTRUCTURE-DOCS_4-Quality-Checks.md for examples
```

---

### Issue: `CONFLICT (content): Merge conflict in uv.lock`

**Cause**: Parallel dependency updates in different branches

**Solution**:
```bash
# Regenerate lockfile from pyproject.toml
uv pip compile pyproject.toml -o requirements.lock
uv pip compile pyproject.toml --extra dev -o requirements-dev.lock

# Resolve conflicts
git add requirements.lock requirements-dev.lock uv.lock
git commit -m "Regenerate lockfiles after merge"
```

---

## Summary

DocImp's dependency stack balances modern tooling with stability:

- **Python**: anthropic (Claude API), pydantic (validation), pytest/ruff/mypy (quality)
- **TypeScript**: commander (CLI), chalk/ora (UI), zod (validation), jest/eslint (quality)
- **Critical Versions**: Node 24+, Python 3.13+, Git 2.28+, ESLint 9+, uv 0.9.8+
- **ESM Constraints**: chalk, ora require ESM imports (no CommonJS)
- **Lockfiles**: uv.lock (Python), package-lock.json (TypeScript) for reproducibility
- **Security**: Regular `npm audit` and `uv pip list --outdated` checks

**Next Steps**: See `INFRASTRUCTURE-DOCS_19-Maintenance-Procedures.md` for ongoing maintenance workflows (hook updates, Node version upgrades, CLAUDE.md management).
