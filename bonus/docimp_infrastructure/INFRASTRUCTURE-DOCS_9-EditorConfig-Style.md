# Infrastructure Documentation: EditorConfig & Style Enforcement

## Overview

DocImp uses a **three-layer style enforcement** strategy to ensure consistency across all files:

1. **EditorConfig** (.editorconfig) - Editor-agnostic basic formatting
2. **Language-Specific Formatters** (Prettier, ruff format) - Automated style fixes
3. **Linters** (ESLint, ruff check) - Style rule enforcement with auto-fix

This layered approach provides:
- **Consistent formatting** regardless of editor or IDE
- **Automatic fixes** via pre-commit hooks
- **Zero configuration** for new contributors

---

## 1. EditorConfig

### Purpose

**EditorConfig** defines basic formatting rules that work across **all editors and IDEs**:
- VS Code, Sublime Text, Atom, Vim, Emacs, IntelliJ IDEA, etc.

Editors automatically read `.editorconfig` and apply settings without requiring plugins or configuration.

### Configuration File

**File: .editorconfig**

```ini
# EditorConfig: https://EditorConfig.org

# Top-most EditorConfig file
root = true

# Global settings for all files
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# Python files
[*.py]
indent_style = space
indent_size = 4
max_line_length = 88  # Black/ruff default

# TypeScript/JavaScript files
[*.{ts,tsx,js,jsx,mjs,cjs}]
indent_style = space
indent_size = 2
max_line_length = 80  # Prettier default

# JSON files
[*.json]
indent_style = space
indent_size = 2

# YAML files (GitHub Actions, etc.)
[*.{yml,yaml}]
indent_style = space
indent_size = 2

# Markdown files
[*.md]
indent_style = space
max_line_length = 88  # Match Python for consistency
trim_trailing_whitespace = false  # Preserve trailing spaces (Markdown line breaks)

# Shell scripts
[*.sh]
indent_style = space
indent_size = 2

# Makefile (MUST use tabs)
[Makefile]
indent_style = tab

# Package manager lock files (generated, don't enforce style)
[{package-lock.json,npm-shrinkwrap.json,yarn.lock,pnpm-lock.yaml}]
indent_style = unset
indent_size = unset

# Generated/vendor files
[{dist/**,node_modules/**,.pytest_cache/**}]
charset = unset
end_of_line = unset
insert_final_newline = unset
trim_trailing_whitespace = unset
```

### Per-Language Settings

| Language | Indent | Size | Max Line | Notes |
|----------|--------|------|----------|-------|
| Python | space | 4 | 88 | PEP 8 with Black default |
| TypeScript | space | 2 | 80 | Standard TypeScript style |
| JavaScript | space | 2 | 80 | Standard JavaScript style |
| JSON | space | 2 | - | Readable formatting |
| YAML | space | 2 | - | GitHub Actions, CI/CD |
| Markdown | space | - | 88 | No trailing space trim |
| Shell | space | 2 | - | Bash scripts |
| Makefile | tab | - | - | REQUIRED for make |

### Key Design Decisions

**1. LF Line Endings Everywhere**

```ini
end_of_line = lf
```

**Rationale:**
- Git repositories use LF on all platforms
- CI/CD runs on Linux (LF)
- Cross-platform consistency

**Trade-offs:**
- Windows users need `core.autocrlf=true` in git config
- Prevents line ending conflicts in PRs

**2. UTF-8 Encoding**

```ini
charset = utf-8
```

**Rationale:**
- Universal character support
- No encoding detection issues
- Required for emoji in comments (if used)

**3. Final Newline Required**

```ini
insert_final_newline = true
```

**Rationale:**
- POSIX standard: text files should end with newline
- Prevents git diff noise
- Required for shell scripts to execute correctly

**4. Trim Trailing Whitespace**

```ini
trim_trailing_whitespace = true
```

**Exception: Markdown files**

```ini
[*.md]
trim_trailing_whitespace = false
```

**Rationale:**
- Markdown uses two trailing spaces for line breaks
- Trimming breaks intentional formatting
- Separate rule for Markdown preserves this

**5. Makefile Tabs (Non-Negotiable)**

```ini
[Makefile]
indent_style = tab
```

**Rationale:**
- `make` requires tabs for recipe indentation
- Spaces cause "missing separator" errors
- Cannot be changed without breaking make

**6. Unset Rules for Generated Files**

```ini
[{dist/**,node_modules/**}]
charset = unset
end_of_line = unset
```

**Rationale:**
- Generated files shouldn't be formatted
- Prevents EditorConfig from modifying build output
- Reduces editor performance overhead

### Editor Support

**Editors with Native Support** (no plugin needed):
- IntelliJ IDEA
- WebStorm
- PyCharm
- Rider
- Visual Studio

**Editors Requiring Plugin:**
- VS Code: [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
- Sublime Text: [EditorConfig](https://packagecontrol.io/packages/EditorConfig)
- Vim: [editorconfig-vim](https://github.com/editorconfig/editorconfig-vim)
- Emacs: [editorconfig-emacs](https://github.com/editorconfig/editorconfig-emacs)

### Verification

**Check EditorConfig Compliance:**

```bash
# Install editorconfig-checker
npm install -g editorconfig-checker

# Run checker
editorconfig-checker

# Check specific files
editorconfig-checker src/**/*.ts
```

**Manual Verification:**

```bash
# Check line endings
file -b src/analyzer.py
# Expected: "Python script, UTF-8 Unicode text"

# Check for CRLF (should be empty)
grep -r $'\r' src/

# Check final newline
tail -c 1 src/analyzer.py | od -An -ta
# Expected: \n
```

---

## 2. Prettier (TypeScript/JavaScript)

### Purpose

**Prettier** is an opinionated code formatter that enforces consistent style across TypeScript, JavaScript, JSON, YAML, and Markdown files.

**Key Benefit**: Zero style debates - Prettier's decisions are final.

### Configuration

**File: .prettierrc**

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
      "options": {
        "printWidth": 100
      }
    },
    {
      "files": "*.md",
      "options": {
        "printWidth": 88,
        "proseWrap": "always"
      }
    }
  ]
}
```

### Configuration Explained

**General Settings:**

```json
{
  "semi": true,              // Always use semicolons (TypeScript default)
  "trailingComma": "es5",    // Trailing commas where valid in ES5 (objects, arrays)
  "singleQuote": true,       // Use single quotes for strings
  "printWidth": 80,          // Line length limit (80 chars)
  "tabWidth": 2,             // 2 spaces per indentation level
  "useTabs": false,          // Use spaces, not tabs
  "bracketSpacing": true,    // Spaces inside object literals: { foo: bar }
  "arrowParens": "always",   // Always parentheses around arrow function params: (x) => x
  "endOfLine": "lf"          // LF line endings (matches EditorConfig)
}
```

**File-Specific Overrides:**

```json
{
  "overrides": [
    {
      "files": "*.json",
      "options": {
        "printWidth": 100  // JSON files: allow longer lines (less wrapping)
      }
    },
    {
      "files": "*.md",
      "options": {
        "printWidth": 88,       // Match Python line length
        "proseWrap": "always"   // Wrap prose at printWidth
      }
    }
  ]
}
```

### Prettier Ignore

**File: .prettierignore**

```
# Dependencies
node_modules/

# Build output
dist/
build/
*.tsbuildinfo

# Coverage
coverage/

# Cache
.cache/
.eslintcache

# Test fixtures with intentional formatting issues
test-samples/malformed/
test-samples/mixed-valid-invalid/

# Git metadata
.git/

# GitHub workflows (preserve exact YAML formatting)
.github/workflows/

# Config files that need specific formatting
tsconfig*.json
```

### Running Prettier

**Commands:**

```bash
# Format all files
cd cli && npm run format

# Check formatting without modifying files
cd cli && npm run format:check

# Format specific files
npx prettier --write src/commands/**/*.ts

# Format only staged files (pre-commit hook)
npx lint-staged
```

**npm Scripts (cli/package.json):**

```json
{
  "scripts": {
    "format": "prettier --write \"src/**/*.{ts,js,json,md}\" \"**/*.{json,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,js,json,md}\" \"**/*.{json,md}\""
  }
}
```

### Prettier Integration

**Pre-commit Hook (Husky + lint-staged):**

```json
// cli/package.json
{
  "lint-staged": {
    "*.{ts,js,mjs,cjs}": [
      "prettier --write",
      "eslint --fix"
    ]
  }
}
```

**Execution Flow:**
1. User runs `git commit`
2. Husky triggers pre-commit hook
3. lint-staged runs Prettier on staged `.ts` and `.js` files
4. Prettier auto-formats files
5. ESLint runs with `--fix` for additional corrections
6. Commit proceeds with formatted files

**CI/CD Check:**

```yaml
# .github/workflows/ci.yml
- name: Format check with Prettier
  run: cd cli && npm run format:check
```

If formatting issues detected, CI fails with detailed diff.

---

## 3. Ruff (Python Formatting)

### Purpose

**Ruff** is a fast Python linter and formatter that replaces Black, isort, and Flake8 with a single tool.

**Key Benefits:**
- 10-100x faster than Black
- Integrated linting and formatting
- Modern Python 3.13+ syntax support

### Configuration

**File: analyzer/pyproject.toml**

```toml
[tool.ruff]
exclude = [".venv", "venv", "__pycache__", ".pytest_cache"]
target-version = "py313"
line-length = 88  # Black default

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors (PEP 8 violations)
    "F",     # pyflakes (undefined names, unused imports)
    "DTZ",   # flake8-datetimez (timezone-aware datetime)
    "UP",    # pyupgrade (modernize syntax for Python 3.13)
    "PTH",   # flake8-use-pathlib (prefer pathlib over os.path)
    "I",     # isort (import sorting)
    "SIM",   # flake8-simplify (reduce complexity)
    "PERF",  # perflint (performance anti-patterns)
    "YTT",   # flake8-2020 (modern version checks)
]
ignore = []  # No exceptions - strict enforcement
```

**Root Configuration (ruff.toml):**

```toml
exclude = [
    "test-samples/malformed",
    "test-samples/mixed-valid-invalid",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules"
]
```

### Ruff Rule Groups Explained

| Rule Group | Purpose | Example Violations |
|------------|---------|-------------------|
| E (pycodestyle) | PEP 8 errors | Line too long, missing whitespace |
| F (pyflakes) | Code errors | Undefined variable, unused import |
| DTZ (datetimez) | Timezone safety | `datetime.now()` without tz |
| UP (pyupgrade) | Modern syntax | `typing.List` → `list`, `typing.Dict` → `dict` |
| PTH (pathlib) | Path handling | `os.path.join()` → `Path()` |
| I (isort) | Import sorting | Unsorted imports, missing groups |
| SIM (simplify) | Code simplification | `if x: return True else: return False` → `return x` |
| PERF (perflint) | Performance | `+= str` in loop (use list + join) |
| YTT (flake8-2020) | Version checks | Old `sys.version_info` checks |

### Running Ruff

**Commands:**

```bash
# Format Python files
cd analyzer && uv run ruff format .

# Check formatting without modifying
cd analyzer && uv run ruff format --check .

# Run linting with auto-fix
cd analyzer && uv run ruff check . --fix

# Run linting without fixes
cd analyzer && uv run ruff check .

# Check specific file
uv run ruff check src/parsers/python_parser.py
```

**Pre-commit Hook:**

```json
// cli/package.json
{
  "lint-staged": {
    "*.py": [
      "ruff format",
      "ruff check --fix"
    ]
  }
}
```

**CI/CD Check:**

```yaml
# .github/workflows/ci.yml
- name: Lint with ruff
  run: cd analyzer && uv run ruff check .
- name: Format check with ruff
  run: cd analyzer && uv run ruff format --check .
```

### Ruff vs Black Comparison

| Feature | Ruff | Black |
|---------|------|-------|
| Speed | 10-100x faster | Baseline |
| Linting | ✓ Integrated | ✗ Requires Flake8 |
| Import sorting | ✓ Integrated | ✗ Requires isort |
| Python 3.13 | ✓ Full support | ✓ Full support |
| Configuration | pyproject.toml | pyproject.toml |
| Auto-fix | ✓ Many rules | N/A |

**Migration from Black to Ruff:**

```bash
# Before (multiple tools)
black .
isort .
flake8 .

# After (single tool)
ruff format .
ruff check . --fix
```

---

## 4. Style Enforcement Workflow

### Development Workflow

**Step 1: Developer Edits File**

Editor automatically applies EditorConfig rules:
- Indentation (spaces/tabs)
- Line endings (LF)
- Final newline
- Trailing whitespace trimming

**Step 2: Save File**

Editor plugins (optional) auto-format on save:
- VS Code: Prettier extension + Format On Save
- IntelliJ: Reformat Code on Save

**Step 3: Commit File**

Pre-commit hook runs:

```bash
# Husky triggers lint-staged
npx lint-staged

# For TypeScript/JavaScript:
prettier --write staged-files
eslint --fix staged-files

# For Python:
ruff format staged-files
ruff check --fix staged-files
```

**Step 4: Push to Remote**

GitHub Actions CI checks:

```yaml
# Format verification
- npm run format:check  # Prettier
- uv run ruff format --check .  # Ruff

# Linting
- npm run lint  # ESLint
- uv run ruff check .  # Ruff
```

If checks fail, CI blocks merge until formatting fixed.

### CI/CD Integration

**Full CI Pipeline (.github/workflows/ci.yml):**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  python-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Format check
        run: cd analyzer && uv run ruff format --check .
      - name: Lint
        run: cd analyzer && uv run ruff check .
      - name: Type check
        run: cd analyzer && uv run mypy src --ignore-missing-imports

  typescript-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
      - name: Install deps
        run: cd cli && npm ci
      - name: Format check
        run: cd cli && npm run format:check
      - name: Lint
        run: cd cli && npm run lint
      - name: Type check
        run: cd cli && npx tsc --noEmit
```

### Fixing Style Violations

**Scenario 1: Failed Prettier Check**

```bash
# CI error: "Code style issues found"

# Fix locally
cd cli && npm run format

# Verify
npm run format:check

# Commit fix
git add .
git commit -m "Fix code formatting"
git push
```

**Scenario 2: Failed Ruff Check**

```bash
# CI error: "Ruff found linting errors"

# Auto-fix
cd analyzer && uv run ruff check . --fix

# Manual fixes for unfixable issues
# (e.g., unused variables, missing docstrings)

# Verify
uv run ruff check .

# Commit fix
git add .
git commit -m "Fix Python linting issues"
git push
```

**Scenario 3: Line Too Long**

```python
# Before (92 characters - exceeds 88 limit)
def calculate_impact_score(complexity, audit_rating, weights={'complexity': 0.6, 'quality': 0.4}):
    pass

# After (manual reformat to fit 88 chars)
def calculate_impact_score(
    complexity,
    audit_rating,
    weights={'complexity': 0.6, 'quality': 0.4}
):
    pass
```

Ruff and Prettier will automatically format this on save.

---

## 5. Bypassing Style Checks

### When to Bypass (Rare Cases Only)

**Valid Reasons:**
- Emergency hotfix (skip pre-commit hook)
- Intentionally malformed test samples
- Generated code that shouldn't be formatted

**Invalid Reasons:**
- "I prefer different style"
- "Too lazy to fix formatting"
- "It's just a quick change"

### How to Bypass

**Pre-commit Hook:**

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "Emergency hotfix"

# Use sparingly - CI will still catch issues
```

**Prettier Ignore Specific Files:**

```javascript
// Add to .prettierignore
src/generated/schema.ts
test-samples/malformed/*.js
```

**Ruff Ignore Specific Rules:**

```python
# Ignore specific rule for one line
def foo():
    x = 1  # noqa: F841  (unused variable)

# Ignore all rules for one line
bad_code()  # noqa

# Ignore specific rule for entire file
# ruff: noqa: E501  (line too long)
```

**ESLint Disable:**

```typescript
/* eslint-disable-next-line @typescript-eslint/no-explicit-any */
const data: any = fetchData();

// Disable for entire file (rarely needed)
/* eslint-disable @typescript-eslint/no-explicit-any */
```

### Overriding EditorConfig

**Per-File Override:**

Create `.editorconfig` in subdirectory:

```ini
# test-samples/.editorconfig
root = true

[*]
# Allow any formatting in test samples
indent_style = unset
```

**Editor-Specific Override:**

Most editors allow workspace-specific settings that override EditorConfig.

---

## Quick Reference

### Style Tools by Language

| Language | EditorConfig | Formatter | Linter | Config File |
|----------|--------------|-----------|--------|-------------|
| Python | ✓ | ruff format | ruff check | pyproject.toml |
| TypeScript | ✓ | prettier | eslint | .prettierrc, eslint.config.mjs |
| JavaScript | ✓ | prettier | eslint | .prettierrc, eslint.config.mjs |
| JSON | ✓ | prettier | - | .prettierrc |
| YAML | ✓ | prettier | - | .prettierrc |
| Markdown | ✓ | prettier | - | .prettierrc |
| Bash | ✓ | - | shellcheck (future) | .editorconfig |

### Command Cheat Sheet

```bash
# Format all Python files
cd analyzer && uv run ruff format .

# Format all TypeScript/JavaScript files
cd cli && npm run format

# Check formatting without changes
cd analyzer && uv run ruff format --check .
cd cli && npm run format:check

# Lint with auto-fix
cd analyzer && uv run ruff check . --fix
cd cli && npm run lint -- --fix

# Run all quality checks
cd analyzer && uv run ruff format --check . && uv run ruff check . && uv run mypy src
cd cli && npm run format:check && npm run lint && npx tsc --noEmit
```

---

## Troubleshooting

### Problem: EditorConfig Not Working

**Symptoms:**
- Files saved with wrong indentation
- Line endings not converting to LF
- Trailing whitespace not trimmed

**Solution:**

1. **Check plugin installation:**
   - VS Code: Install "EditorConfig for VS Code" extension
   - Sublime: Install "EditorConfig" package
   - Vim: Install editorconfig-vim

2. **Verify .editorconfig location:**
   ```bash
   # Must be in project root
   ls -la .editorconfig
   ```

3. **Check `root = true` directive:**
   ```ini
   # Must be at top of .editorconfig
   root = true
   ```

4. **Test with simple file:**
   ```bash
   echo "test" > test.py
   # Open in editor, add spaces, save
   # Verify spaces converted to correct indentation
   ```

### Problem: Prettier and ESLint Conflict

**Symptoms:**
- Prettier formats code
- ESLint reports style violations
- Pre-commit hook fails

**Solution:**

Ensure `eslint-config-prettier` disables conflicting ESLint rules:

```javascript
// eslint.config.mjs
import eslintConfigPrettier from 'eslint-config-prettier';

export default [
  // ... other configs
  eslintConfigPrettier,  // MUST be last to disable conflicting rules
];
```

### Problem: Ruff Format Changes Code Semantics

**Symptoms:**
- Ruff changes string quotes, breaking code
- Formatted code has different behavior

**Solution:**

Ruff format is semantics-preserving by design. If formatting breaks code, it's a bug. Report to Ruff:

```bash
# Isolate problematic code
ruff format --isolated test_file.py

# Report issue: https://github.com/astral-sh/ruff/issues
```

Temporary workaround:

```python
# Disable formatting for specific section
# fmt: off
problematic_code = "..."
# fmt: on
```

### Problem: CI Fails on Formatting, But Passes Locally

**Symptoms:**
- Local `npm run format:check` passes
- CI fails with formatting errors
- No obvious differences in code

**Solution:**

Check line ending consistency:

```bash
# Check for CRLF
git ls-files -z | xargs -0 file | grep "CRLF"

# Configure git to use LF
git config core.autocrlf false

# Re-clone repository
git clone --config core.autocrlf=false <repo-url>
```

Ensure Prettier version matches:

```bash
# CI uses locked version from package-lock.json
npx prettier --version

# Update to match CI
npm ci  # Uses exact versions from package-lock.json
```

---

## Summary

DocImp's three-layer style enforcement ensures consistent formatting across all files:

1. **EditorConfig** - Basic formatting (indentation, line endings, final newline)
2. **Formatters** - Automated style fixes (Prettier, ruff format)
3. **Linters** - Style rule enforcement (ESLint, ruff check)

**Key Benefits:**

- **Zero configuration** for new contributors (EditorConfig + pre-commit hooks)
- **Automatic fixes** via pre-commit hooks (lint-staged)
- **CI/CD validation** blocks merges until formatting correct
- **Editor-agnostic** consistency (works in all editors)

**Integration Points:**

- Pre-commit hooks auto-format staged files
- CI/CD checks formatting on every push
- GitHub Actions blocks merge if formatting fails

**Next Steps**: See `INFRASTRUCTURE-DOCS_10-Development-Utilities.md` for Makefile targets and development scripts.
