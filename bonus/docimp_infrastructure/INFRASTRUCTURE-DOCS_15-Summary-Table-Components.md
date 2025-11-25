# Infrastructure Documentation: Summary Table - Infrastructure Components

## Overview

This document provides a comprehensive inventory of all infrastructure components in the DocImp project, organized by category for quick reference. Each component is documented with:

- **File/Location**: Absolute or relative path
- **Type**: File type or technology
- **Purpose**: What the component does
- **Key Settings**: Critical configuration options
- **Dependencies**: What it requires or references
- **Maintenance Notes**: Update frequency and considerations

This reference serves as:
- **Onboarding Guide**: New contributors can quickly locate critical files
- **Maintenance Index**: Systematic review of all infrastructure components
- **Debugging Tool**: Trace issues by identifying relevant configuration files
- **Extension Planning**: Identify where to add new infrastructure

---

## Table of Contents

1. [Git Infrastructure](#git-infrastructure)
2. [Claude Code Configuration](#claude-code-configuration)
3. [Python Quality Tools](#python-quality-tools)
4. [TypeScript/JavaScript Quality Tools](#typescriptjavascript-quality-tools)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Development Workflow Automation](#development-workflow-automation)
7. [Package Management](#package-management)
8. [Editor & Formatting](#editor--formatting)
9. [Documentation](#documentation)
10. [Test Infrastructure](#test-infrastructure)
11. [State Management](#state-management)
12. [Utilities & Scripts](#utilities--scripts)
13. [Ignore Files](#ignore-files)

---

## Git Infrastructure

### Main Repository Hooks

| Component       | File/Location                                                          | Type  | Purpose                                                              | Maintenance                        |
|-----------------|------------------------------------------------------------------------|-------|----------------------------------------------------------------------|------------------------------------|
| Pre-commit hook | `/Users/nik/Documents/Code/Polyglot/docimp/.git/hooks/pre-commit`       | Bash  | Blocks commits to main branch in main worktree                       | Update when adding new worktrees   |
| Post-checkout   | `/Users/nik/Documents/Code/Polyglot/docimp/.git/hooks/post-checkout`    | Bash  | Prevents branch checkouts other than main in main worktree           | Rarely updated                     |

**Key Settings:**
```bash
# Worktree detection pattern (both hooks)
if [[ "$PWD" != *"/.docimp-wt/"* ]]; then
    # Main worktree - enforce restrictions
fi
```

**Dependencies:**
- Git 2.28+ (worktree support)
- Bash shell

**Maintenance Notes:**
- Review when git workflow changes
- Test in new worktrees after updates
- Coordinate with Husky configuration

### Husky Setup

| Component         | File/Location                                                     | Type  | Purpose                                           | Maintenance                      |
|-------------------|-------------------------------------------------------------------|-------|---------------------------------------------------|----------------------------------|
| Pre-commit disp.  | `/Users/nik/Documents/Code/Polyglot/docimp/.husky/pre-commit`      | Bash  | Dispatcher: calls protected hook + lint-staged    | Update when adding new hooks     |
| Post-checkout d.  | `/Users/nik/Documents/Code/Polyglot/docimp/.husky/post-checkout`   | Bash  | Dispatcher: calls protected hook                  | Rarely updated                   |
| Setup README      | `/Users/nik/Documents/Code/Polyglot/docimp/.husky/README.md`       | MD    | Instructions for per-worktree Husky config        | Update when workflow changes     |
| Generated hooks   | `/Users/nik/Documents/Code/Polyglot/docimp/.husky/_/` (gitignored) | Dir   | Per-worktree generated files                      | Auto-generated, no manual edits  |

**Key Settings:**
```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname "$0")/_/husky.sh"

# Call protected hook
.git/hooks/pre-commit || exit 1

# Run lint-staged
npx lint-staged
```

**Dependencies:**
- Husky v9.1.7+
- npm/npx
- Git with `extensions.worktreeConfig = true`

**Maintenance Notes:**
- Per-worktree setup: `git config --worktree core.hooksPath .husky/_`
- Run `npx husky` in each worktree after creation

### Lint-Staged Integration

| Component      | File/Location                                                | Type        | Purpose                                  | Maintenance                     |
|----------------|--------------------------------------------------------------|-------------|------------------------------------------|---------------------------------|
| Configuration  | `/Users/nik/Documents/Code/Polyglot/docimp/cli/package.json` | JSON (npm)  | Pre-commit linting/formatting for staged | Update when adding file types   |

**Key Settings:**
```json
"lint-staged": {
  "*.{ts,js,mjs,cjs}": ["prettier --write", "eslint --fix"],
  "*.py": ["ruff format", "ruff check --fix"]
}
```

**Dependencies:**
- lint-staged npm package
- prettier, eslint, ruff

**Maintenance Notes:**
- Add new file patterns as project evolves
- Ensure tools referenced are installed
- Test with `npx lint-staged --debug`

---

## Claude Code Configuration

### Directory Structure

| Component         | File/Location                                                              | Type    | Purpose                                         | Maintenance                    |
|-------------------|----------------------------------------------------------------------------|---------|-------------------------------------------------|--------------------------------|
| Agents            | `/Users/nik/Documents/Code/Polyglot/docimp/.claude/agents` (symlink)       | Symlink | Specialized agent configs                       | Managed in .docimp-shared/     |
| Settings          | `/Users/nik/Documents/Code/Polyglot/docimp/.claude/settings.local.json`    | Symlink | Permission whitelist, tool access patterns      | Update when adding permissions |
| Skills            | `/Users/nik/Documents/Code/Polyglot/docimp/.claude/skills` (symlink)       | Symlink | Custom skills for Claude Code                   | Managed in .docimp-shared/     |

**Symlink Targets:**
```bash
agents/ → ../../.docimp-shared/.claude/agents
settings.local.json → /Users/nik/Code/Polyglot/.docimp-shared/.claude/settings.local.json
skills/ → ../../.docimp-shared/.claude/skills
```

**Rationale**: Shared infrastructure stored in `.docimp-shared/` allows cross-project reuse while maintaining per-repo symlinks for independence.

### Permission Configuration

| Component | File/Location                                                            | Type | Purpose                          | Maintenance                               |
|-----------|--------------------------------------------------------------------------|------|----------------------------------|-------------------------------------------|
| Settings  | `/Users/nik/Code/Polyglot/.docimp-shared/.claude/settings.local.json`    | JSON | Permissions for tools and skills | Update when granting new capabilities     |

**Key Settings:**
```json
{
  "allowedTools": [
    "Bash(docimp analyze:*)",
    "Bash(uv run pytest:*)",
    "Bash(gh pr create:*)",
    "Glob(//Users/nik/Code/Polyglot/.docimp-shared/**)",
    "Read(//Users/nik/Code/repos/custom-claude-skills/**)",
    "Skill(git-workflow)"
  ]
}
```

**Dependencies:**
- Claude Code CLI
- Bash commands on system PATH

**Maintenance Notes:**
- Use wildcard patterns for flexibility
- Test new permissions before committing
- Document rationale for broad permissions

### CLAUDE.md Configuration

| Component  | File/Location                                              | Type | Purpose                              | Maintenance                           |
|------------|------------------------------------------------------------|------|--------------------------------------|---------------------------------------|
| Main guide | `/Users/nik/Documents/Code/Polyglot/docimp/CLAUDE.md`       | MD   | Technical guide for Claude Code      | Update when architecture changes      |

**Key Settings:**
- Character limit: 40,000 bytes (absolute maximum)
- Current size: 27,792 bytes (~27.8 KB)
- Imports: `@docs/patterns/filename.md` pattern
- Supporting files: `docs/patterns/` (public, committed)

**Dependencies:**
- External docs in `docs/patterns/`

**Maintenance Notes:**
- Check size: `wc -c CLAUDE.md`
- Move detailed content to `docs/patterns/` if exceeding 40K
- Maximum import depth: 5 hops

### CLAUDE_CONTEXT.md

| Component       | File/Location                                                  | Type | Purpose                        | Maintenance                      |
|-----------------|----------------------------------------------------------------|------|--------------------------------|----------------------------------|
| Private context | `/Users/nik/Documents/Code/Polyglot/docimp/CLAUDE_CONTEXT.md`  | MD   | Private project context        | Update as project evolves        |

**Key Settings:**
- Gitignored (private)
- Contains: project context, job requirements, developer profile, writing context

**Dependencies:** None

**Maintenance Notes:**
- Never commit (gitignored)
- Update when project goals or constraints change

---

## Python Quality Tools

### Ruff Configuration

| Component       | File/Location                                                         | Type | Purpose                       | Maintenance                          |
|-----------------|-----------------------------------------------------------------------|------|-------------------------------|--------------------------------------|
| Root config     | `/Users/nik/Documents/Code/Polyglot/docimp/ruff.toml`                  | TOML | Global Ruff linting rules     | Update when adding exclusions        |
| Analyzer config | `/Users/nik/Documents/Code/Polyglot/docimp/analyzer/pyproject.toml`   | TOML | Analyzer-specific Ruff config | Update when adding rule groups       |

**Key Settings (ruff.toml):**
```toml
exclude = [
  "test-samples/malformed",
  "test-samples/mixed-valid-invalid",
  ".venv", "venv", "__pycache__"
]
```

**Key Settings (analyzer/pyproject.toml):**
```toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "DTZ", "UP", "PTH", "I", "SIM", "PERF", "YTT"]
```

**Rule Groups:**
- E: pycodestyle errors
- F: pyflakes
- DTZ: flake8-datetimez
- UP: pyupgrade
- PTH: flake8-use-pathlib
- I: isort
- SIM: flake8-simplify
- PERF: perflint
- YTT: flake8-2020

**Dependencies:**
- ruff >=0.1.0

**Maintenance Notes:**
- Review excluded directories periodically
- Add new rule groups cautiously (can introduce many violations)

### Pytest Configuration

| Component   | File/Location                                                     | Type | Purpose                | Maintenance                      |
|-------------|-------------------------------------------------------------------|------|------------------------|----------------------------------|
| pytest.ini  | `/Users/nik/Documents/Code/Polyglot/docimp/analyzer/pytest.ini`    | INI  | Test discovery, markers| Update when adding markers       |
| pyproject   | `/Users/nik/Documents/Code/Polyglot/docimp/pyproject.toml`         | TOML | Pytest config          | Coordinate with pytest.ini       |

**Key Settings (pytest.ini):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --strict-markers --tb=short
markers =
  unit: Unit tests
  integration: Integration tests
  slow: Tests that take a long time to run
```

**Dependencies:**
- pytest >=7.4.0
- pytest-cov >=4.1.0 (for coverage)

**Maintenance Notes:**
- Add markers for new test categories
- Keep `python_files` pattern consistent

### MyPy Configuration

| Component | File/Location                                           | Type | Purpose           | Maintenance                    |
|-----------|---------------------------------------------------------|------|-------------------|--------------------------------|
| Config    | `/Users/nik/Documents/Code/Polyglot/docimp/pyproject.toml` | TOML | Type checking     | Update when adding modules     |

**Key Settings:**
```toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

**Dependencies:**
- mypy >=1.7.0

**Maintenance Notes:**
- Enable stricter checks incrementally
- Maintain `ignore_missing_imports = true` for untyped dependencies

---

## TypeScript/JavaScript Quality Tools

### TypeScript Configuration

| Component | File/Location                                             | Type | Purpose                  | Maintenance                         |
|-----------|-----------------------------------------------------------|------|--------------------------|-------------------------------------|
| Config    | `/Users/nik/Documents/Code/Polyglot/docimp/cli/tsconfig.json` | JSON | TypeScript compilation   | Update when changing module system  |

**Key Settings:**
```json
{
  "compilerOptions": {
    "target": "ES2024",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "allowJs": true,
    "checkJs": true,  // CRITICAL: Real JSDoc validation
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**Dependencies:**
- typescript >=5.3.3

**Maintenance Notes:**
- **checkJs: true** is critical for JSDoc validation (not cosmetic)
- Keep module/moduleResolution in sync (both NodeNext)

### ESLint Configuration

| Component | File/Location                                                | Type | Purpose          | Maintenance                        |
|-----------|--------------------------------------------------------------|------|------------------|------------------------------------|
| Config    | `/Users/nik/Documents/Code/Polyglot/docimp/cli/eslint.config.mjs` | MJS  | ESLint flat config | Update when adding plugins         |

**Key Settings:**
```javascript
export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  jsdocPlugin.configs['flat/recommended'],
  unicornPlugin.configs['flat/recommended'],
  nodePlugin.configs['flat/recommended'],
  promisePlugin.configs['flat/recommended'],
  importPlugin.configs.recommended,
  prettierConfig
];
```

**Plugin Stack:**
- @eslint/js
- @typescript-eslint/eslint-plugin
- eslint-plugin-jsdoc
- eslint-plugin-unicorn
- eslint-plugin-n (Node.js)
- eslint-plugin-promise
- eslint-plugin-import
- eslint-config-prettier

**Dependencies:**
- ESLint v9+ (flat config format)
- All plugins listed above

**Maintenance Notes:**
- New flat config format (ESLint v9+)
- Customize unicorn rules (can be overly strict)
- Different JSDoc rules for .ts vs. .js files

### Prettier Configuration

| Component | File/Location                                          | Type | Purpose         | Maintenance               |
|-----------|--------------------------------------------------------|------|-----------------|---------------------------|
| Config    | `/Users/nik/Documents/Code/Polyglot/docimp/.prettierrc` | JSON | Code formatting | Rarely updated            |

**Key Settings:**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "overrides": [
    { "files": "*.json", "options": { "printWidth": 100 } },
    { "files": "*.md", "options": { "printWidth": 88, "proseWrap": "always" } }
  ]
}
```

**Dependencies:**
- prettier >=3.1.0

**Maintenance Notes:**
- Overrides for specific file types
- Coordinate with EditorConfig settings

### Jest Configuration

| Component | File/Location                                             | Type | Purpose       | Maintenance                      |
|-----------|-----------------------------------------------------------|------|---------------|----------------------------------|
| Config    | `/Users/nik/Documents/Code/Polyglot/docimp/cli/jest.config.js` | JS   | Jest test runner | Update when adding test patterns |

**Key Settings:**
```javascript
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  maxWorkers: 1,  // Sequential execution (shared state)
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};
```

**Dependencies:**
- jest >=29.7.0
- ts-jest >=29.1.1

**Maintenance Notes:**
- `maxWorkers: 1` critical for integration tests (shared .docimp/state)
- Update `moduleNameMapper` when adding aliases

---

## CI/CD Pipeline

### GitHub Actions Workflow

| Component | File/Location                                                     | Type | Purpose       | Maintenance                    |
|-----------|-------------------------------------------------------------------|------|---------------|--------------------------------|
| CI config | `/Users/nik/Documents/Code/Polyglot/docimp/.github/workflows/ci.yml` | YAML | CI/CD pipeline| Update when adding test jobs   |

**Key Jobs:**

| Job Name              | Purpose                          | Key Commands                                   |
|-----------------------|----------------------------------|------------------------------------------------|
| python-tests          | Python linting, type checking    | `uv run ruff`, `uv run mypy`, `uv run pytest` |
| typescript-tests      | TS linting, type checking, tests | `npm run lint`, `npx tsc`, `npm test`          |
| integration           | E2E integration test             | `docimp analyze ../examples`                   |
| module-system-tests   | ESM/CommonJS detection           | Python parser tests                            |
| workflow-validation   | Workflow E2E tests               | `./test-samples/test-workflows.sh`             |

**Dependencies:**
- GitHub Actions
- Python 3.13
- Node 24
- uv v0.9.8+

**Maintenance Notes:**
- Jobs run in parallel (faster CI)
- Cache npm dependencies (faster installs)
- Update Python/Node versions carefully

---

## Development Workflow Automation

### Git Workflow Skill

| Component          | File/Location                                                                     | Type   | Purpose                          | Maintenance                   |
|--------------------|-----------------------------------------------------------------------------------|--------|----------------------------------|-------------------------------|
| Skill doc          | `/Users/nik/Code/repos/custom-claude-skills/.../git-workflow/SKILL.md`           | MD     | Workflow documentation           | Update when workflow changes  |
| Worktree script    | `.../git-workflow/scripts/create_worktree.py`                                     | Python | Create worktrees with symlinks   | Update when adding symlinks   |
| Hook installer     | `.../git-workflow/scripts/install_hooks.py`                                       | Python | Install git hooks                | Rarely updated                |
| Pre-commit source  | `.../git-workflow/scripts/hooks/pre-commit`                                       | Bash   | Hook source                      | Update with .git/hooks version|

**Key Features:**
- Creates worktree in `../.docimp-wt/<name>/`
- Symlinks: .envrc, pyproject.toml, requirements*.lock, package.json, node_modules
- Isolated .venv/ per worktree
- Configures Husky hooks

**Dependencies:**
- Python 3.8+
- Git 2.28+
- uv, npm

**Maintenance Notes:**
- Update symlink list when adding shared config files
- Test in new worktrees after changes

### Direnv Integration

| Component | File/Location                                      | Type | Purpose             | Maintenance                  |
|-----------|----------------------------------------------------|------|---------------------|------------------------------|
| .envrc    | `/Users/nik/Documents/Code/Polyglot/docimp/.envrc`  | Bash | Tool interception   | Update when adding tools     |

**Key Functionality:**
```bash
# Intercepts
python → uv run python
pytest → uv run pytest
ruff → uv run ruff
mypy → uv run mypy

# Blocks
pip → Error (use uv add / uv pip)

# Node version management
Reads .nvmrc, adds Node to PATH
```

**Dependencies:**
- direnv
- uv
- nvm

**Maintenance Notes:**
- Run `direnv allow` after updates
- Test interceptors: `which python` should show `.direnv/bin/python`

### Node Version Pinning

| Component | File/Location                                    | Type | Purpose         | Maintenance                     |
|-----------|--------------------------------------------------|------|-----------------|---------------------------------|
| .nvmrc    | `/Users/nik/Documents/Code/Polyglot/docimp/.nvmrc` | Text | Node version pin| Update when upgrading Node      |

**Key Settings:**
```
24.11.0
```

**Rationale**: Exact version (not `24`) prevents automatic upgrades that lose global packages.

**Update Procedure:**
```bash
echo "24.12.0" > .nvmrc
nvm install 24.12.0 --reinstall-packages-from=24.11.0
git add .nvmrc
git commit -m "Update Node to 24.12.0"
```

**Maintenance Notes:**
- Coordinate with npm package requirements
- Test global packages after upgrade

### Python Version Management

| Component      | File/Location                                              | Type | Purpose          | Maintenance                |
|----------------|------------------------------------------------------------|------|------------------|----------------------------|
| .python-version| `/Users/nik/Documents/Code/Polyglot/docimp/.python-version` | Text | Python version   | Update when upgrading Python|

**Key Settings:**
```
3.13
```

**Dependencies:**
- pyenv

**Maintenance Notes:**
- Update when upgrading Python
- Ensure uv supports new version

---

## Package Management

### UV Setup (Python)

| Component       | File/Location                                                  | Type | Purpose                  | Maintenance                      |
|-----------------|----------------------------------------------------------------|------|--------------------------|----------------------------------|
| pyproject.toml  | `/Users/nik/Documents/Code/Polyglot/docimp/pyproject.toml`      | TOML | Python project metadata  | Update when changing deps        |
| uv.lock         | `/Users/nik/Documents/Code/Polyglot/docimp/uv.lock`             | TOML | uv native lockfile       | Auto-generated                   |
| requirements    | `/Users/nik/Documents/Code/Polyglot/docimp/requirements.lock`   | Text | Runtime dependencies     | Auto-generated                   |
| requirements-dev| `/Users/nik/Documents/Code/Polyglot/docimp/requirements-dev.lock`| Text | Dev dependencies        | Auto-generated                   |

**Key Dependencies:**
```toml
dependencies = [
  "anthropic>=0.72.0,<1.0.0",
  "pydantic>=2.12.3,<3.0.0",
  "pydantic-core>=2.41.4,<3.0.0",
  "typing-extensions>=4.9.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=7.4.0",
  "pytest-cov>=4.1.0",
  "ruff>=0.1.0",
  "mypy>=1.7.0"
]
```

**Maintenance Commands:**
```bash
uv pip compile pyproject.toml -o requirements.lock
uv pip compile pyproject.toml --extra dev -o requirements-dev.lock
uv pip sync requirements-dev.lock
```

**Dependencies:**
- uv v0.9.8+

**Maintenance Notes:**
- Commit all lock files together
- Update lockfiles after pyproject.toml changes

### NPM Setup (TypeScript/JavaScript)

| Component       | File/Location                                                  | Type | Purpose                  | Maintenance                   |
|-----------------|----------------------------------------------------------------|------|--------------------------|-------------------------------|
| package.json    | `/Users/nik/Documents/Code/Polyglot/docimp/cli/package.json`    | JSON | Node.js project metadata | Update when changing deps     |
| package-lock    | `/Users/nik/Documents/Code/Polyglot/docimp/cli/package-lock.json`| JSON | npm lockfile            | Auto-generated                |

**Key Scripts:**
```json
"scripts": {
  "build": "tsc",
  "test": "jest",
  "test:integration": "node --test src/__tests__/integration/*.mjs",
  "lint": "eslint src --ext .ts",
  "format": "prettier --write ..."
}
```

**Key Dependencies:**
- commander (CLI)
- chalk (colors)
- typescript
- jest (testing)

**Maintenance Commands:**
```bash
npm ci  # (install from lockfile)
npm install <package>  # (add dependency)
npm update  # (update all)
```

**Dependencies:**
- npm (bundled with Node.js)

**Maintenance Notes:**
- Use `npm ci` in CI/CD (reproducible)
- Commit package-lock.json alongside package.json

---

## Editor & Formatting

### EditorConfig

| Component   | File/Location                                           | Type | Purpose                  | Maintenance              |
|-------------|---------------------------------------------------------|------|--------------------------|--------------------------|
| .editorconfig| `/Users/nik/Documents/Code/Polyglot/docimp/.editorconfig` | INI  | Cross-editor consistency | Rarely updated           |

**Key Settings:**

| Language              | Indent | Size | Max Line |
|-----------------------|--------|------|----------|
| Python                | space  | 4    | 88       |
| TypeScript/JavaScript | space  | 2    | 80       |
| JSON                  | space  | 2    | -        |
| Markdown              | space  | -    | 88       |

**Dependencies:** None (editor plugin support)

**Maintenance Notes:**
- Coordinate with Prettier/Ruff settings
- Update when adding new file types

---

## Documentation

### External Documentation Pattern

| Component            | File/Location                                              | Type | Purpose                        | Maintenance                    |
|----------------------|------------------------------------------------------------|------|--------------------------------|--------------------------------|
| Error handling       | `docs/patterns/error-handling.md`                          | MD   | Three-layer error pattern      | Update when pattern changes    |
| Dependency injection | `docs/patterns/dependency-injection.md`                    | MD   | DI pattern across languages    | Update when exceptions added   |
| Testing strategy     | `docs/patterns/testing-strategy.md`                        | MD   | Test organization              | Update when adding test types  |
| Transactions         | `docs/patterns/transaction-integration.md`                 | MD   | Session management, rollback   | Update when workflow changes   |
| Session resume       | `docs/patterns/session-resume.md`                          | MD   | Resume capability architecture | Update when adding resume modes|
| Workflow state       | `docs/patterns/workflow-state-management.md`               | MD   | State tracking, migrations     | Update when schema changes     |

**Import Pattern in CLAUDE.md:**
```markdown
- @docs/patterns/error-handling.md
```

**Dependencies:** None

**Maintenance Notes:**
- Keep under 40K characters total (CLAUDE.md + imports)
- Maximum import depth: 5 hops

### Public Documentation

| Component       | File/Location                               | Type | Purpose                     | Maintenance                  |
|-----------------|---------------------------------------------|------|-----------------------------|------------------------------|
| JSON schema     | `docs/json-schema.md`                       | MD   | JSON schema reference       | Update when schema changes   |
| User guide      | `docs/user-guide/`                          | Dir  | User-facing docs            | Update when features added   |
| Quality control | `docs/quality-control/`                     | Dir  | 6 quality setup guides      | Update when tools updated    |

**Maintenance Notes:**
- Keep user guide synchronized with features
- Validate JSON examples in json-schema.md

---

## Test Infrastructure

### Python Tests

| Component       | File/Location                                         | Type | Purpose              | Maintenance                  |
|-----------------|-------------------------------------------------------|------|----------------------|------------------------------|
| Test directory  | `/Users/nik/Documents/Code/Polyglot/docimp/analyzer/tests/` | Dir  | 46+ test files       | Add tests for new features   |

**Key Test Files:**
- `test_analyzer.py` - Core analyzer
- `test_parser_*.py` - Parser-specific tests
- `test_audit*.py` - Audit command tests
- `test_workflow_state.py` - State tracking tests

**Test Markers:**
```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
```

**Dependencies:**
- pytest
- pytest-cov

**Maintenance Notes:**
- Add markers for new test categories
- Maintain 80%+ code coverage

### TypeScript Tests

| Component      | File/Location                                             | Type | Purpose           | Maintenance                 |
|----------------|-----------------------------------------------------------|------|-------------------|-----------------------------|
| Test directory | `/Users/nik/Documents/Code/Polyglot/docimp/cli/src/__tests__/` | Dir  | 27+ test files    | Add tests for new features  |

**Key Directories:**
- `commands/` - Command tests
- `config/` - Configuration tests
- `integration/` - E2E tests
- `fixtures/` - Test fixtures

**Dependencies:**
- jest
- ts-jest

**Maintenance Notes:**
- Keep integration tests sequential (maxWorkers: 1)
- Mock external dependencies (Python subprocess, Claude API)

### Test Samples & E2E

| Component              | File/Location                                              | Type | Purpose                   | Maintenance                  |
|------------------------|------------------------------------------------------------|------|---------------------------|------------------------------|
| Workflow test script   | `test-samples/test-workflows.sh`                           | Bash | E2E workflow validation   | Update when adding workflows |
| Edge cases             | `test-samples/edge-cases/`                                 | Dir  | Complex parsing scenarios | Add edge cases as found      |
| Example project        | `test-samples/example-project/`                            | Dir  | Full project for testing  | Keep representative          |

**Maintenance Notes:**
- Run E2E tests in CI/CD
- Add edge cases when parser fails

---

## State Management

### State Directory

| Component           | File/Location                                        | Type | Purpose                           | Maintenance              |
|---------------------|------------------------------------------------------|------|-----------------------------------|--------------------------|
| Session reports     | `.docimp/session-reports/`                           | Dir  | Analysis/audit/plan results       | Auto-managed             |
| Workflow state      | `.docimp/workflow-state.json`                        | JSON | Command execution tracking        | Auto-updated             |
| History snapshots   | `.docimp/history/`                                   | Dir  | Timestamped workflow snapshots    | Auto-pruned              |
| Transaction repo    | `.docimp/state/.git/`                                | Dir  | Side-car Git for transactions     | Auto-managed             |

**Key Files:**
- `analyze-latest.json` - Latest analysis
- `audit.json` - Audit ratings
- `plan.json` - Improvement plan
- `audit-session-{uuid}.json` - Audit session state
- `improve-session-{uuid}.json` - Improve session state

**Dependencies:**
- StateManager utilities (Python + TypeScript)

**Maintenance Notes:**
- Never manually edit state files
- Use `docimp` commands to manage state

---

## Utilities & Scripts

### Makefile

| Component | File/Location                                    | Type     | Purpose              | Maintenance        |
|-----------|--------------------------------------------------|----------|----------------------|--------------------|
| Makefile  | `/Users/nik/Documents/Code/Polyglot/docimp/Makefile` | Makefile | Development targets  | Add targets as needed|

**Targets:**
- `make setup` - Create environment
- `make lint` - Run ruff
- `make test` - Run pytest
- `make quality` - All quality checks

**Dependencies:**
- GNU Make
- uv

**Maintenance Notes:**
- Keep synchronized with CI/CD commands
- Add targets for common operations

---

## Ignore Files

### Git Ignore

| Component  | File/Location                                       | Type | Purpose         | Maintenance                  |
|------------|-----------------------------------------------------|------|-----------------|------------------------------|
| .gitignore | `/Users/nik/Documents/Code/Polyglot/docimp/.gitignore` | Text | Git exclusions  | Update when adding artifacts |

**Key Exclusions:**
- Dependencies: `node_modules/`, `.venv/`
- Build: `cli/dist/`, `*.pyc`
- State: `.docimp/`
- Cache: `.ruff_cache/`, `.pytest_cache/`

**Maintenance Notes:**
- Never ignore lock files
- Keep state directory gitignored

### Prettier Ignore

| Component       | File/Location                                             | Type | Purpose              | Maintenance                 |
|-----------------|-----------------------------------------------------------|------|----------------------|-----------------------------|
| .prettierignore | `/Users/nik/Documents/Code/Polyglot/docimp/.prettierignore` | Text | Format exclusions    | Update when adding artifacts|

**Key Exclusions:**
- Dependencies
- Build outputs
- Test fixtures with intentional formatting issues

**Maintenance Notes:**
- Coordinate with .gitignore
- Exclude files with specific formatting needs

---

## Quick Reference

### Critical Files by Category

| Category         | Critical Files                                                                     |
|------------------|------------------------------------------------------------------------------------|
| Git              | `.git/hooks/pre-commit`, `.husky/pre-commit`, `cli/package.json` (lint-staged)    |
| Claude           | `CLAUDE.md`, `.claude/settings.local.json`                                         |
| Python Quality   | `ruff.toml`, `analyzer/pyproject.toml`, `pytest.ini`                               |
| TS/JS Quality    | `cli/tsconfig.json`, `cli/eslint.config.mjs`, `.prettierrc`                        |
| CI/CD            | `.github/workflows/ci.yml`                                                         |
| Package Mgmt     | `pyproject.toml`, `requirements*.lock`, `cli/package.json`, `cli/package-lock.json`|
| State            | `.docimp/workflow-state.json`, `.docimp/session-reports/`                          |

### Update Frequency

| Frequency   | Components                                                                        |
|-------------|-----------------------------------------------------------------------------------|
| Weekly      | Lock files (dependency updates), test files                                       |
| Monthly     | Quality configs (ruff, eslint), CI/CD workflow                                    |
| Quarterly   | CLAUDE.md, documentation patterns                                                 |
| As needed   | Git hooks, worktree scripts, Makefile                                             |
| Never       | .editorconfig, .nvmrc (unless upgrading versions)                                 |

---

## Summary

DocImp's infrastructure comprises **80+ components** organized into 13 categories:

1. **Git Infrastructure**: 5 components (hooks, Husky, lint-staged)
2. **Claude Code Configuration**: 4 components (settings, CLAUDE.md, context)
3. **Python Quality Tools**: 3 configurations (ruff, pytest, mypy)
4. **TypeScript/JavaScript Quality Tools**: 4 configurations (tsconfig, eslint, prettier, jest)
5. **CI/CD Pipeline**: 1 workflow file with 5 jobs
6. **Development Workflow Automation**: 4 components (git-workflow skill, direnv, version pinning)
7. **Package Management**: 6 files (pyproject, lock files, package.json)
8. **Editor & Formatting**: 1 component (EditorConfig)
9. **Documentation**: 9 files (patterns + public docs)
10. **Test Infrastructure**: 73+ test files across Python + TypeScript
11. **State Management**: 4 directories in `.docimp/`
12. **Utilities & Scripts**: 1 Makefile
13. **Ignore Files**: 2 files (.gitignore, .prettierignore)

**Key Maintenance Principles:**
- Commit lock files alongside package manifests
- Keep quality configs synchronized (EditorConfig, Prettier, Ruff)
- Update CLAUDE.md when architecture changes
- Test infrastructure changes in worktrees before merging
- Review CI/CD workflow quarterly

**Next Steps**: See `INFRASTRUCTURE-DOCS_16-Key-Metrics.md` for quantitative project metrics and performance targets.
