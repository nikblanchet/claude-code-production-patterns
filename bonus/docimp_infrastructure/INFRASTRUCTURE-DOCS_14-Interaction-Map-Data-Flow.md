# Infrastructure Documentation: Interaction Map & Data Flow

## Overview

DocImp's infrastructure operates as a cohesive ecosystem where multiple systems—git hooks, Claude Code configuration, quality checks, CI/CD pipelines, and package management—interact to support polyglot development. Understanding these interactions is critical for effective maintenance, debugging, and extension of the project.

This document provides comprehensive visualization and explanation of:

- **Component Interaction Architecture**: How files, tools, and systems reference each other
- **Data Flow Patterns**: Movement of data through the polyglot stack (TypeScript ↔ Python ↔ JavaScript)
- **Workflow Sequences**: Step-by-step execution paths for common development tasks
- **State Management Flow**: How `.docimp/` state directory integrates with git and commands
- **Integration Points**: Where different infrastructure components coordinate

**Why This Matters:**
- **Debugging**: Trace issues through multi-layer interactions
- **Onboarding**: New contributors understand system holistically
- **Extension**: Identify correct integration points for new features
- **Maintenance**: Prevent breaking changes by understanding dependencies

---

## Component Interaction Architecture

### Interaction Diagram

The following ASCII diagram illustrates the complete infrastructure component graph, showing file locations, symlinks, and data flow directions:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SHARED INFRASTRUCTURE                                   │
│                    /Users/nik/Documents/Code/Polyglot/.docimp-shared/            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────────────────┐  ┌────────────────────────────────────┐ │
│  │  .claude/                         │  │  .planning/                        │ │
│  ├───────────────────────────────────┤  ├────────────────────────────────────┤ │
│  │  • settings.local.json            │  │  • PLAN.md (gitignored)            │ │
│  │    - Permission whitelist         │  │    - 31-step execution plan        │ │
│  │    - Bash command allowlist       │  │    - Checkbox progress tracking    │ │
│  │    - Tool access patterns         │  │                                    │ │
│  │                                   │  │  • development-workflow.md         │ │
│  │  • skills/                        │  │    - Claude Code methodology       │ │
│  │    - Symlink targets for projects │  │    - Session atomicity docs        │ │
│  │                                   │  │                                    │ │
│  │  • agents/                        │  │  • workflow-state-master-plan.md   │ │
│  │    - Specialized agent configs    │  │    - Workflow state architecture   │ │
│  └───────────────────────────────────┘  └────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓ (symlinks)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            MAIN REPOSITORY                                      │
│                /Users/nik/Documents/Code/Polyglot/docimp/                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  GIT HOOKS & WORKFLOW PROTECTION                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .git/hooks/                                                            │   │
│  │  ├── pre-commit          → Blocks main commits in main worktree        │   │
│  │  └── post-checkout       → Prevents branch checkouts in main worktree  │   │
│  │                                                                         │   │
│  │  .husky/                                                                │   │
│  │  ├── pre-commit          → Dispatcher: calls protected hook + lint-staged │ │
│  │  ├── post-checkout       → Dispatcher: calls protected hook            │   │
│  │  ├── README.md           → Setup instructions for per-worktree config  │   │
│  │  └── _/                  → Per-worktree generated files (gitignored)   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    ↓ (triggers)                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  cli/package.json → lint-staged configuration                          │   │
│  │  {                                                                      │   │
│  │    "lint-staged": {                                                     │   │
│  │      "*.{ts,js}": ["prettier --write", "eslint --fix"],                │   │
│  │      "*.py": ["ruff format", "ruff check --fix"]                       │   │
│  │    }                                                                    │   │
│  │  }                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ENVIRONMENT & VERSION MANAGEMENT                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .envrc                 → direnv tool interception                      │   │
│  │  ├── Intercepts: python, python3, pytest, ruff, mypy → uv run          │   │
│  │  ├── Blocks: pip (use uv add / uv pip)                                 │   │
│  │  └── Manages: Node version from .nvmrc                                 │   │
│  │                                                                         │   │
│  │  .nvmrc                 → Node 24.11.0 (exact pin)                      │   │
│  │  .python-version        → Python 3.13 (pyenv)                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    ↓ (configures)                               │
│  EDITOR & FORMATTING CONSISTENCY                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .editorconfig          → Cross-editor settings                         │   │
│  │  ├── Python: 4 spaces, line length 88                                  │   │
│  │  ├── TypeScript/JS: 2 spaces, line length 80                           │   │
│  │  └── Global: UTF-8, LF line endings                                    │   │
│  │                                                                         │   │
│  │  .prettierrc            → Prettier formatting rules                     │   │
│  │  .prettierignore        → Files excluded from formatting                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  CI/CD AUTOMATION                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .github/workflows/ci.yml                                               │   │
│  │  ├── Job: Python Tests (3.13)                                          │   │
│  │  │   - uv run ruff check analyzer/                                     │   │
│  │  │   - uv run mypy analyzer/src                                        │   │
│  │  │   - uv run pytest -v --cov                                          │   │
│  │  │                                                                      │   │
│  │  ├── Job: TypeScript Tests                                             │   │
│  │  │   - npm run lint                                                    │   │
│  │  │   - npx tsc --noEmit                                                │   │
│  │  │   - npm test                                                        │   │
│  │  │   - npm run test:integration                                        │   │
│  │  │                                                                      │   │
│  │  ├── Job: Integration Test (Python + TypeScript)                      │   │
│  │  │   - Runs full docimp analyze ../examples                            │   │
│  │  │                                                                      │   │
│  │  ├── Job: Module System Matrix Tests                                  │   │
│  │  │   - Tests ESM/CommonJS detection                                    │   │
│  │  │                                                                      │   │
│  │  └── Job: Workflow Validation                                          │   │
│  │      - Runs ./test-samples/test-workflows.sh                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  PYTHON ANALYZER ENGINE                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  analyzer/                                                              │   │
│  │  ├── pyproject.toml     → Python project config, dependencies          │   │
│  │  ├── pytest.ini         → Test discovery, markers                      │   │
│  │  │                                                                      │   │
│  │  ├── src/                                                               │   │
│  │  │   ├── parsers/       → PythonParser, TypeScriptParser               │   │
│  │  │   ├── analyzer.py    → DocumentationAnalyzer (orchestrator)         │   │
│  │  │   ├── impact_scorer.py → Impact calculation (0-100)                 │   │
│  │  │   ├── claude_client.py → Anthropic API client                       │   │
│  │  │   └── docstring_writer.py → JSDoc/docstring insertion               │   │
│  │  │                                                                      │   │
│  │  └── tests/             → 46+ test files                               │   │
│  │      ├── test_analyzer.py                                              │   │
│  │      ├── test_parser_*.py                                              │   │
│  │      └── test_audit*.py                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    ↕ (JSON subprocess communication)            │
│  TYPESCRIPT CLI LAYER                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  cli/                                                                   │   │
│  │  ├── package.json       → npm scripts, dependencies, lint-staged       │   │
│  │  ├── tsconfig.json      → TypeScript config (checkJs: true)            │   │
│  │  ├── eslint.config.mjs  → ESLint flat config (7 plugins)               │   │
│  │  ├── jest.config.js     → Jest ESM preset, sequential execution        │   │
│  │  │                                                                      │   │
│  │  ├── src/                                                               │   │
│  │  │   ├── index.ts       → CLI entry point (Commander.js)               │   │
│  │  │   ├── commands/      → AnalyzeCommand, AuditCommand, etc.           │   │
│  │  │   ├── python-bridge/ → Subprocess communication                     │   │
│  │  │   ├── config/        → ConfigLoader (docimp.config.js)              │   │
│  │  │   ├── plugins/       → PluginManager                                │   │
│  │  │   ├── display/       → TerminalDisplay (output formatting)          │   │
│  │  │   └── utils/         → StateManager, WorkflowStateManager           │   │
│  │  │                                                                      │   │
│  │  └── src/__tests__/    → 27+ test files                                │   │
│  │      ├── commands/                                                      │   │
│  │      ├── config/                                                        │   │
│  │      └── integration/                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    ↕ (loads/validates)                          │
│  JAVASCRIPT PLUGINS & CONFIGURATION                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  plugins/                                                               │   │
│  │  ├── validate-types.js  → JSDoc type-checking (TypeScript compiler)    │   │
│  │  ├── jsdoc-style.js     → Style enforcement (tags, punctuation)        │   │
│  │  └── __tests__/         → Plugin tests                                 │   │
│  │                                                                         │   │
│  │  docimp.config.js       → User configuration                           │   │
│  │  ├── styleGuides        → Per-language doc styles                      │   │
│  │  ├── tone               → Documentation tone                           │   │
│  │  ├── claude             → API timeout/retry                            │   │
│  │  ├── pythonBridge       → Subprocess timeouts                          │   │
│  │  ├── workflowHistory    → History snapshot config                      │   │
│  │  └── plugins            → Plugin list                                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  QUALITY CONFIGURATION                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ruff.toml              → Python linting config (root)                  │   │
│  │  pyproject.toml         → Python project config (root)                  │   │
│  │  .prettierrc            → JavaScript/TypeScript formatting              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  DOCUMENTATION                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CLAUDE.md              → 27.8KB technical guide for Claude Code        │   │
│  │  CLAUDE_CONTEXT.md      → Private project context (gitignored)          │   │
│  │                                                                         │   │
│  │  docs/                                                                  │   │
│  │  ├── patterns/          → External docs imported by CLAUDE.md          │   │
│  │  │   ├── error-handling.md                                             │   │
│  │  │   ├── dependency-injection.md                                       │   │
│  │  │   ├── testing-strategy.md                                           │   │
│  │  │   ├── transaction-integration.md                                    │   │
│  │  │   ├── session-resume.md                                             │   │
│  │  │   └── workflow-state-management.md                                  │   │
│  │  │                                                                      │   │
│  │  ├── json-schema.md     → JSON schema reference                        │   │
│  │  ├── user-guide/        → User-facing documentation                    │   │
│  │  └── quality-control/   → 6 quality setup guides                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  TEST INFRASTRUCTURE                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  test-samples/                                                          │   │
│  │  ├── test-workflows.sh           → E2E workflow validation (CI)         │   │
│  │  ├── test-audit-resume.sh        → Resume capability tests              │   │
│  │  ├── test-resume-improve.sh      → Improve workflow resume tests        │   │
│  │  ├── test-prompt-wordings.sh     → Prompt generation tests              │   │
│  │  ├── test-workflow-state-integration.sh → State tracking tests          │   │
│  │  ├── test-validate-types-cache.js → Type validation caching tests       │   │
│  │  │                                                                      │   │
│  │  ├── edge-cases/                 → Complex parsing scenarios            │   │
│  │  │   ├── typescript_generics.ts                                        │   │
│  │  │   ├── javascript_complex_jsdoc.js                                   │   │
│  │  │   └── mixed_module_systems.js                                       │   │
│  │  │                                                                      │   │
│  │  └── example-project/            → Full project for workflow validation│   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  STATE DIRECTORY (.docimp/ - gitignored)                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .docimp/                                                               │   │
│  │  ├── session-reports/                                                   │   │
│  │  │   ├── analyze-latest.json      → Latest analysis results             │   │
│  │  │   ├── audit.json                → Audit ratings (1-4 scale)          │   │
│  │  │   ├── plan.json                 → Prioritized improvement plan       │   │
│  │  │   ├── audit-session-{uuid}.json → Audit session state                │   │
│  │  │   └── improve-session-{uuid}.json → Improve session state            │   │
│  │  │                                                                      │   │
│  │  ├── workflow-state.json          → Command execution tracking          │   │
│  │  │   ├── last_analyze: {timestamp, item_count, file_checksums}         │   │
│  │  │   ├── last_audit: {timestamp, item_count, file_checksums}           │   │
│  │  │   ├── last_plan: {timestamp, item_count}                            │   │
│  │  │   └── last_improve: {timestamp, item_count}                         │   │
│  │  │                                                                      │   │
│  │  ├── history/                     → Timestamped workflow state snapshots│   │
│  │  │   └── workflow-state-YYYY-MM-DDTHH-MM-SS-MMMZ.json                  │   │
│  │  │                                                                      │   │
│  │  └── state/.git/                  → Side-car Git repository             │   │
│  │      └── refs/heads/docimp/session-{uuid} → Transaction branches        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  DEVELOPMENT UTILITIES                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Makefile               → Development targets                           │   │
│  │  ├── make setup         → Create environment, install deps              │   │
│  │  ├── make lint          → Run ruff linting                              │   │
│  │  ├── make test          → Run pytest                                    │   │
│  │  └── make quality       → All quality checks (lint + typecheck + test)  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  IGNORE FILES                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  .gitignore             → Comprehensive exclude list                    │   │
│  │  .prettierignore        → Format-specific exclusions                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↕ (symlinks in worktrees)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FEATURE WORKTREES                                        │
│            /Users/nik/Documents/Code/Polyglot/.docimp-wt/                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  issue-243/                                                                     │
│  ├── .venv/                    → Isolated Python environment                   │
│  ├── cli/node_modules/         → Symlink to main worktree                      │
│  ├── .envrc                    → Symlink to main                               │
│  ├── pyproject.toml            → Symlink to main                               │
│  ├── requirements*.lock        → Symlink to main                               │
│  ├── package.json              → Symlink to main                               │
│  ├── package-lock.json         → Symlink to main                               │
│  └── .husky/_/                 → Per-worktree Husky generated files            │
│                                                                                 │
│  issue-221/                                                                     │
│  └── (same structure as issue-243)                                             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Relationship Legend

| Symbol | Meaning                                              |
|--------|------------------------------------------------------|
| →      | Triggers, calls, or executes                         |
| ↔      | Bidirectional data exchange                          |
| ↓      | One-way data flow                                    |
| ↕      | Two-way data flow with feedback                      |
| Symlink| File exists in one location, referenced from another |

---

## Data Flow Patterns

### TypeScript CLI ↔ Python Analyzer Communication

DocImp's polyglot architecture requires seamless communication between the TypeScript CLI and Python analysis engine. This is achieved through **JSON subprocess communication**.

#### Analyze Command Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  User runs: docimp analyze ./src                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. TypeScript CLI (cli/src/index.ts)                                      │
│     - Commander.js parses arguments                                        │
│     - Creates AnalyzeCommand instance                                      │
│     - Loads docimp.config.js configuration                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. AnalyzeCommand.execute(options)                                        │
│     - Validates target directory exists                                    │
│     - Checks workflow state prerequisites                                  │
│     - Prompts for audit.json cleanup (if needed)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. PythonBridge.analyze(targetPath, options)                              │
│     - Spawns Python subprocess: uv run python -m analyzer.main analyze     │
│     - Passes JSON via stdin:                                               │
│       {                                                                    │
│         "command": "analyze",                                              │
│         "target": "./src",                                                 │
│         "incremental": false,                                              │
│         "applyAudit": false,                                               │
│         "config": {...}  // docimp.config.js contents                      │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Python Analyzer (analyzer/src/main.py)                                 │
│     - Receives JSON from stdin                                             │
│     - Creates DocumentationAnalyzer instance                               │
│     - Discovers files (glob patterns, respects .gitignore)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Parser Routing (DocumentationAnalyzer.analyze_directory)               │
│     - .py files → PythonParser (AST parsing)                               │
│     - .ts/.js/.mjs/.cjs → TypeScriptParser (TypeScript compiler API)      │
│     - Each parser extracts CodeItem objects:                               │
│       {                                                                    │
│         "name": "calculateTotal",                                          │
│         "type": "function",                                                │
│         "filepath": "src/utils.ts",                                        │
│         "line_number": 42,                                                 │
│         "end_line": 56,                                                    │
│         "language": "typescript",                                          │
│         "complexity": 8,                                                   │
│         "has_docs": false,                                                 │
│         "parameters": ["a", "b"],                                          │
│         "return_type": "number",                                           │
│         "export_type": "named",                                            │
│         "module_system": "esm"                                             │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. Impact Scoring (ImpactScorer.calculate_score)                          │
│     - Without audit: score = min(100, complexity * 5)                      │
│     - With audit: score = (0.6 × complexity_score) + (0.4 × penalty)       │
│     - Adds impact_score field to CodeItem                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. Result Aggregation (DocumentationAnalyzer.analyze_directory)           │
│     - Collects all CodeItem objects                                        │
│     - Calculates coverage metrics:                                         │
│       {                                                                    │
│         "total_items": 150,                                                │
│         "documented_items": 75,                                            │
│         "coverage_percent": 50.0,                                          │
│         "by_language": {                                                   │
│           "python": {"total": 60, "documented": 30, "coverage": 50.0},    │
│           "typescript": {"total": 90, "documented": 45, "coverage": 50.0} │
│         },                                                                 │
│         "parse_failures": [...]                                            │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  8. State Persistence (StateManager.save_analysis_result)                  │
│     - Writes .docimp/session-reports/analyze-latest.json                   │
│     - Updates .docimp/workflow-state.json:                                 │
│       {                                                                    │
│         "last_analyze": {                                                  │
│           "timestamp": "2025-11-19T10:30:00Z",                             │
│           "item_count": 150,                                               │
│           "file_checksums": {                                              │
│             "src/utils.ts": "sha256:abc123...",                            │
│             "src/analyzer.py": "sha256:def456..."                          │
│           }                                                                │
│         }                                                                  │
│       }                                                                    │
│     - Saves history snapshot: .docimp/history/workflow-state-{timestamp}.json │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  9. JSON Output to stdout (Python → TypeScript)                            │
│     - Serializes AnalysisResult to JSON                                    │
│     - Writes to stdout (captured by TypeScript subprocess)                 │
│     {                                                                      │
│       "items": [...],  // Array of CodeItem objects                        │
│       "coverage_percent": 50.0,                                            │
│       "total_items": 150,                                                  │
│       "documented_items": 75,                                              │
│       "by_language": {...},                                                │
│       "parse_failures": [...]                                              │
│     }                                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  10. TypeScript Parsing (PythonBridge.analyze)                             │
│      - Reads stdout JSON from Python subprocess                            │
│      - Parses with JSON.parse()                                            │
│      - Validates with Zod schema (runtime type checking)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  11. Display Formatting (TerminalDisplay.showAnalysisResults)              │
│      - Renders colored output with chalk                                   │
│      - Shows coverage percentage, language breakdown                       │
│      - Lists undocumented items sorted by impact score                     │
│      - Displays parse failures (if any)                                    │
│                                                                            │
│      Output Example:                                                       │
│      ┌─────────────────────────────────────────────────────────────────┐  │
│      │ Analysis Complete                                               │  │
│      │                                                                 │  │
│      │ Coverage: 50.0% (75/150 items documented)                       │  │
│      │                                                                 │  │
│      │ By Language:                                                    │  │
│      │   Python:     50.0% (30/60)                                     │  │
│      │   TypeScript: 50.0% (45/90)                                     │  │
│      │                                                                 │  │
│      │ Top Undocumented Items (by impact):                             │  │
│      │   1. calculateTotal (src/utils.ts:42) - Score: 75               │  │
│      │   2. parseConfig (src/config.py:15) - Score: 60                 │  │
│      └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- **JSON Communication**: Language-agnostic, easy to validate and debug
- **Stdin/Stdout Protocol**: Clean separation (stdin = input, stdout = data, stderr = logs)
- **Stateless Subprocess**: Python process exits after each command (no persistent state)
- **Zod Validation**: Runtime type checking prevents TypeScript from processing malformed data

#### Improve Command Flow (with Plugin Validation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  User runs: docimp improve ./src                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. TypeScript CLI: ImproveCommand.execute()                               │
│     - Loads plan.json from .docimp/session-reports/                        │
│     - Prompts to resume existing session (if improve-session-*.json exists)│
│     - Initializes transaction system (side-car .git repository)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Iterate through PlanItem objects                                       │
│     - For each undocumented item (sorted by impact_score descending):      │
│       {                                                                    │
│         "name": "calculateTotal",                                          │
│         "filepath": "src/utils.ts",                                        │
│         "line_number": 42,                                                 │
│         "complexity": 8,                                                   │
│         "impact_score": 75,                                                │
│         "language": "typescript"                                           │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. PromptBuilder.createPrompt(item, config)                               │
│     - Reads source code from filepath                                      │
│     - Extracts function/class definition                                   │
│     - Builds prompt:                                                       │
│       "Generate TypeScript JSDoc documentation for this function:          │
│        [code excerpt]                                                      │
│        Style: concise, tone: professional                                  │
│        Requirements: @param tags, @returns tag, description"               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. PythonBridge.generateDocstring(prompt)                                 │
│     - Sends JSON to Python subprocess:                                     │
│       {                                                                    │
│         "command": "generate_docstring",                                   │
│         "prompt": "...",                                                   │
│         "config": { "claude": { "timeout": 30000, "maxRetries": 3 } }     │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Python: ClaudeClient.generate_docstring(prompt)                        │
│     - Calls Anthropic API (Claude Sonnet 4.5)                              │
│     - Receives suggestion:                                                 │
│       /**                                                                  │
│        * Calculates the total sum of two numbers.                          │
│        * @param a - First number                                           │
│        * @param b - Second number                                          │
│        * @returns Sum of a and b                                           │
│        */                                                                  │
│     - Returns JSON to TypeScript via stdout                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. TypeScript: PluginManager.validate(docstring, item)                    │
│     - Loads plugins from docimp.config.js:                                 │
│       ["validate-types.js", "jsdoc-style.js"]                              │
│     - Runs each plugin's beforeAccept hook:                                │
│                                                                            │
│       validate-types.js:                                                   │
│       - Creates temporary .ts file with docstring + function               │
│       - Runs TypeScript compiler with checkJs: true                        │
│       - Checks for type errors                                             │
│       - Returns: { accept: true, reason: "Type-checking passed" }          │
│                                                                            │
│       jsdoc-style.js:                                                      │
│       - Validates tag aliases (@return vs. @returns)                       │
│       - Checks punctuation (descriptions end with period)                  │
│       - Requires @example for public APIs                                  │
│       - Returns: { accept: true } (or { accept: false, reason: "..." })    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ (if validation passes)
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. Interactive Prompt (if --non-interactive not set)                      │
│     - Display suggestion to user                                           │
│     - Prompt: [A]ccept, [E]dit, [R]egenerate, [S]kip, [U]ndo, [Q]uit      │
│     - User selects [A]ccept                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  8. PythonBridge.writeDocstring(filepath, line_number, docstring)          │
│     - Sends JSON to Python subprocess:                                     │
│       {                                                                    │
│         "command": "write_docstring",                                      │
│         "filepath": "src/utils.ts",                                        │
│         "line_number": 42,                                                 │
│         "docstring": "/** ... */",                                         │
│         "language": "typescript"                                           │
│       }                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  9. Python: DocstringWriter.insert_docstring()                             │
│     - Reads source file                                                    │
│     - Inserts docstring at correct indentation level (line 41)             │
│     - Writes file back to disk                                             │
│     - Returns: { success: true, filepath: "src/utils.ts" }                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  10. TypeScript: TransactionManager.recordChange()                         │
│      - Commits change to .docimp/state/.git:                               │
│        git --git-dir=.docimp/state/.git \                                  │
│            --work-tree=. \                                                 │
│            add src/utils.ts                                                │
│        git --git-dir=.docimp/state/.git commit -m \                        │
│            "Document calculateTotal in src/utils.ts:42"                    │
│      - Stores commit hash for rollback capability                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  11. PluginManager.runAfterWriteHooks(filepath, item)                      │
│      - Executes afterWrite hooks from plugins (if any)                     │
│      - Logs results to session state                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  12. Update Session State                                                  │
│      - Saves to .docimp/session-reports/improve-session-{uuid}.json:       │
│        {                                                                   │
│          "session_id": "abc123",                                           │
│          "current_index": 5,                                               │
│          "completed_items": [                                              │
│            { "filepath": "src/utils.ts", "line": 42, "action": "accept" }  │
│          ]                                                                 │
│        }                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ (repeat for next item)
┌─────────────────────────────────────────────────────────────────────────────┐
│  13. Session Completion                                                    │
│      - Updates .docimp/workflow-state.json:                                │
│        {                                                                   │
│          "last_improve": {                                                 │
│            "timestamp": "2025-11-19T11:00:00Z",                            │
│            "item_count": 20  // items improved                             │
│          }                                                                 │
│        }                                                                   │
│      - Displays summary:                                                   │
│        "Improve session complete: 20 items documented, 5 skipped"          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Data Flow Features:**
- **Multi-Layer Validation**: TypeScript schema validation + JavaScript plugin validation
- **Transaction Tracking**: Side-car Git repository for rollback capability
- **Session Persistence**: Resume capability via improve-session-{uuid}.json
- **Interactive Workflow**: User controls acceptance, can undo changes

---

## Workflow Sequences

### Development Session Workflow (10 Steps)

This sequence shows a complete development cycle from worktree creation to PR merge:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 1: Create Feature Worktree                                           │
└─────────────────────────────────────────────────────────────────────────────┘
$ cd /Users/nik/Documents/Code/Polyglot/docimp
$ python3 .claude/skills/git-workflow/scripts/create_worktree.py \
    issue-243 feature/issue-243-add-jsx-support

# Script actions:
# - Creates worktree in ../.docimp-wt/issue-243/
# - Symlinks: .envrc, pyproject.toml, requirements*.lock, package.json, node_modules
# - Creates isolated .venv/
# - Configures Husky hooks (git config --worktree core.hooksPath .husky/_)
# - Runs npx husky to generate dispatcher files
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 2: direnv Loads Environment                                          │
└─────────────────────────────────────────────────────────────────────────────┘
$ cd /Users/nik/Documents/Code/Polyglot/.docimp-wt/issue-243
$ direnv allow  # (prompts on first entry)

# .envrc actions:
# - Intercepts python → uv run python
# - Intercepts pytest → uv run pytest
# - Blocks pip (shows error: use uv add / uv pip)
# - Adds Node 24.11.0 to PATH (from .nvmrc)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 3: Developer Edits Code                                              │
└─────────────────────────────────────────────────────────────────────────────┘
$ code analyzer/src/parsers/jsx_parser.py  # (new file)
$ code cli/src/commands/analyzeCommand.ts  # (edit existing)

# Changes:
# - Add JSX parser class
# - Register in DocumentationAnalyzer
# - Update CLI command to support .jsx extension
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 4: Run Local Tests                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
$ uv run pytest -v analyzer/tests/test_parser_jsx.py
# .envrc intercepts → uv run pytest
# Tests pass

$ cd cli && npm test
# Jest runs TypeScript tests
# All pass
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 5: Commit Changes                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
$ git add analyzer/src/parsers/jsx_parser.py
$ git add analyzer/tests/test_parser_jsx.py
$ git add cli/src/commands/analyzeCommand.ts
$ git commit -m "Add JSX parser support (Issue #243)"

# Pre-commit hook triggers:
# 1. .husky/pre-commit dispatcher executes
# 2. Calls .git/hooks/pre-commit (checks not on main in main worktree - passes)
# 3. Runs lint-staged:
#    - analyzer/src/parsers/jsx_parser.py → ruff format, ruff check --fix
#    - cli/src/commands/analyzeCommand.ts → prettier --write, eslint --fix
# 4. Auto-formatted files staged
# 5. Commit succeeds
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 6: Push to Remote                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
$ git push origin feature/issue-243-add-jsx-support

# Pushes to GitHub
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 7: GitHub Actions CI Runs                                            │
└─────────────────────────────────────────────────────────────────────────────┘
# .github/workflows/ci.yml triggers on push:

Job: python-tests
  - uv run ruff check analyzer/  ✓
  - uv run mypy analyzer/src     ✓
  - uv run pytest -v --cov       ✓

Job: typescript-tests
  - npm run lint                 ✓
  - npx tsc --noEmit             ✓
  - npm test                     ✓

Job: integration
  - docimp analyze ../examples   ✓

Job: module-system-tests
  - Tests ESM/CommonJS detection ✓

Job: workflow-validation
  - ./test-samples/test-workflows.sh ✓

# All jobs pass ✓
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 8: Create Pull Request                                               │
└─────────────────────────────────────────────────────────────────────────────┘
$ gh pr create --title "Add JSX parser support (Issue #243)" \
    --body "Adds JSXParser to support .jsx file analysis..."

# PR created: https://github.com/user/docimp/pull/243
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 9: Code Review & Approval                                            │
└─────────────────────────────────────────────────────────────────────────────┘
# Reviewer comments, requests changes
# Developer addresses feedback in worktree
# Pushes additional commits
# CI re-runs, passes
# Reviewer approves
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 10: Squash-Merge to Main                                             │
└─────────────────────────────────────────────────────────────────────────────┘
$ gh pr merge 243 --squash --delete-branch

# Actions:
# - Squashes all commits into single commit on main
# - Deletes remote feature/issue-243-add-jsx-support branch
# - Local worktree remains (manual cleanup)

# Manual cleanup (optional):
$ cd /Users/nik/Documents/Code/Polyglot/docimp
$ git worktree remove ../.docimp-wt/issue-243
```

**Workflow Benefits:**
- **Parallel Development**: Multiple worktrees, isolated environments
- **Automated Quality**: Pre-commit hooks + CI/CD catch issues early
- **Consistent Formatting**: lint-staged auto-fixes before commit
- **Transaction Safety**: Main worktree protected from accidental commits/checkouts

---

## State Management Flow

### Workflow State Tracking

The `.docimp/workflow-state.json` file coordinates dependencies between commands and detects stale data:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Command Execution: docimp analyze ./src                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Python: WorkflowStateManager.update_command_state("analyze", ...)      │
│     - Calculates SHA-256 checksums for all analyzed files                   │
│     - Writes to .docimp/workflow-state.json:                                │
│       {                                                                    │
│         "schema_version": "1.0",                                           │
│         "last_analyze": {                                                  │
│           "timestamp": "2025-11-19T10:30:00Z",                             │
│           "item_count": 150,                                               │
│           "file_checksums": {                                              │
│             "src/utils.ts": "abc123...",                                   │
│             "src/config.py": "def456..."                                   │
│           }                                                                │
│         }                                                                  │
│       }                                                                    │
│     - Saves snapshot: .docimp/history/workflow-state-2025-11-19T10-30-00-123Z.json │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  User Edits Files                                                          │
│  - Modifies src/utils.ts                                                   │
│  - Modifies src/analyzer.py                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Command Execution: docimp audit ./src                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. TypeScript: WorkflowValidator.validateAuditPrerequisites()             │
│     - Loads .docimp/workflow-state.json                                    │
│     - Checks if last_analyze exists → ✓ (exists from step 1)               │
│     - Compares current file checksums vs. last_analyze.file_checksums:     │
│       - src/utils.ts: current="xyz789..." vs. stored="abc123..." → CHANGED │
│       - src/analyzer.py: not in analyze (new file) → CHANGED               │
│     - Detects staleness → Prompts user:                                    │
│       "Analysis is stale (2 files changed). Re-run analyze? [Y/n]"         │
│     - User chooses [Y] → Runs docimp analyze --incremental                 │
│     - User chooses [n] → Proceeds with audit (shows warning)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Python: WorkflowStateManager.update_command_state("audit", ...)        │
│     - Records audit execution:                                             │
│       {                                                                    │
│         "last_audit": {                                                    │
│           "timestamp": "2025-11-19T11:00:00Z",                             │
│           "item_count": 18,  // items rated                                │
│           "file_checksums": {                                              │
│             "src/utils.ts": "xyz789...",  // current checksums             │
│             "src/config.py": "ghi012..."                                   │
│           }                                                                │
│         }                                                                  │
│       }                                                                    │
│     - Saves snapshot: .docimp/history/workflow-state-2025-11-19T11-00-00-456Z.json │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  Command Execution: docimp status                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. TypeScript: StatusCommand.execute()                                    │
│     - Loads .docimp/workflow-state.json                                    │
│     - Compares timestamps and checksums                                    │
│     - Displays:                                                            │
│       ┌─────────────────────────────────────────────────────────────────┐ │
│       │ analyze:  ✓ Run 30 minutes ago (150 items, 100 files)          │ │
│       │ audit:    ✓ Run just now (18 items rated)                      │ │
│       │ plan:     ✗ Not run yet                                        │ │
│       │ improve:  ✗ Not run yet                                        │ │
│       │                                                                 │ │
│       │ Staleness Warnings: None                                       │ │
│       │                                                                 │ │
│       │ Suggestions:                                                    │ │
│       │   → Run 'docimp plan' to generate improvement plan             │ │
│       └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

**State Management Principles:**
- **Checksum-Based Staleness**: File-level detection (not timestamp)
- **Command Dependencies**: audit requires analyze, plan requires audit (optional), improve requires plan
- **History Snapshots**: Automatic archival for debugging and recovery
- **Schema Versioning**: Forward compatibility with schema_version field

---

## Integration Points

### Git Hooks ↔ Lint-Staged

```
Developer commits code
        ↓
.husky/pre-commit (dispatcher)
        ↓
.git/hooks/pre-commit (main worktree check)
        ↓ (if worktree check passes)
lint-staged (from cli/package.json)
        ↓
Prettier formats staged files
        ↓
ESLint/Ruff fixes staged files
        ↓
Auto-formatted files added to commit
        ↓
Commit succeeds
```

### CI/CD ↔ Workflow Validation

```
PR pushed to GitHub
        ↓
.github/workflows/ci.yml triggers
        ↓
Jobs run in parallel:
  - python-tests (ruff, mypy, pytest)
  - typescript-tests (eslint, tsc, jest)
  - integration (full docimp analyze)
        ↓
Workflow Validation Job runs:
  - ./test-samples/test-workflows.sh
  - Executes: analyze → audit → plan → improve (E2E)
  - Validates JSON output format
  - Checks workflow state consistency
        ↓
All jobs pass → PR ready for review
Any job fails → PR blocked
```

### Plugin Validation ↔ DocstringWriter

```
Claude generates docstring
        ↓
PluginManager.validate(docstring, item)
        ↓
For each plugin in docimp.config.js.plugins:
  - validate-types.js:
    - Creates temp .ts file with docstring + code
    - Runs TypeScript compiler (checkJs: true)
    - Returns: { accept: true/false, reason: "..." }
  - jsdoc-style.js:
    - Validates tag aliases, punctuation
    - Checks @example for public APIs
    - Returns: { accept: true/false, reason: "..." }
        ↓
If all plugins accept → Proceed to user prompt
If any plugin rejects → Show rejection reason, skip to [R]egenerate
        ↓ (if user accepts)
DocstringWriter.insert_docstring(filepath, line, docstring)
        ↓
File written to disk
        ↓
TransactionManager.recordChange() → Commits to .docimp/state/.git
        ↓
PluginManager.runAfterWriteHooks(filepath, item)
```

---

## Troubleshooting

### Issue: Workflow State Out of Sync

**Symptom**: `docimp status` shows stale warnings despite re-running analyze.

**Solution**:

```bash
# Nuclear option: reset workflow state
rm .docimp/workflow-state.json
docimp analyze ./src  # Recreates workflow state

# Verify
docimp status
# Output: analyze ✓ Run just now
```

### Issue: Subprocess Communication Failure

**Symptom**: TypeScript CLI shows "Failed to parse Python output".

**Solution**:

```bash
# Debug Python subprocess directly
uv run python -m analyzer.main analyze << 'EOF'
{
  "command": "analyze",
  "target": "./src",
  "config": {}
}
EOF

# Check stderr for errors
# Common issues:
# - Missing dependencies (uv pip sync requirements-dev.lock)
# - Syntax errors in analyzer code
# - Invalid JSON in config
```

### Issue: Git Hooks Not Triggering in Worktree

**Symptom**: Pre-commit hook doesn't run in feature worktree.

**Solution**:

```bash
# From worktree directory
cd /Users/nik/Documents/Code/Polyglot/.docimp-wt/issue-243

# Verify Husky config
git config --worktree --get core.hooksPath
# Output: /Users/nik/Documents/Code/Polyglot/.docimp-wt/issue-243/.husky/_

# If empty, reconfigure:
git config --worktree core.hooksPath "$(git rev-parse --show-toplevel)/.husky/_"
npx husky
```

---

## Quick Reference

### Data Flow Checkpoints

| Checkpoint                     | Input                              | Output                              | Verification                           |
|--------------------------------|------------------------------------|-------------------------------------|----------------------------------------|
| CLI argument parsing           | `docimp analyze ./src`             | `options` object                    | `console.log(options)`                 |
| Python subprocess spawn        | JSON via stdin                     | JSON via stdout                     | `uv run python -m analyzer.main ...`   |
| Parser routing                 | File extension                     | `CodeItem` objects                  | Check `parse_failures` array           |
| Impact scoring                 | `complexity`, `audit_rating`       | `impact_score` (0-100)              | Verify score calculation manually      |
| Plugin validation              | `docstring`, `item`                | `{ accept: bool, reason: string }`  | Run plugin standalone                  |
| Transaction commit             | File path, change                  | Git commit hash                     | `git --git-dir=.docimp/state/.git log` |
| Workflow state update          | Command name, checksums            | `workflow-state.json`               | `cat .docimp/workflow-state.json`      |

### Critical Integration Files

| File                            | Purpose                                  | Consumers                        |
|---------------------------------|------------------------------------------|----------------------------------|
| `.docimp/workflow-state.json`   | Command execution tracking               | status, audit, plan, improve     |
| `.docimp/session-reports/*.json`| Analysis/audit/plan results              | audit, plan, improve             |
| `docimp.config.js`              | User configuration                       | CLI, Python analyzer, plugins    |
| `package.json` (lint-staged)    | Pre-commit formatting                    | Husky, git hooks                 |
| `.envrc`                        | Tool interception                        | direnv, shell commands           |

---

## Summary

DocImp's infrastructure operates as a tightly integrated ecosystem where:

1. **Git hooks** coordinate with **lint-staged** for automated formatting
2. **TypeScript CLI** communicates with **Python analyzer** via JSON subprocess protocol
3. **JavaScript plugins** validate AI-generated documentation before acceptance
4. **Workflow state** tracks command execution and detects stale data
5. **CI/CD pipelines** validate all quality checks and workflow sequences
6. **Per-worktree environments** enable parallel development with shared lock files

**Key Integration Patterns:**
- JSON for cross-language data exchange
- Symlinks for shared configuration across worktrees
- Side-car Git repository for transaction tracking
- Checksum-based staleness detection
- Multi-layer validation (TypeScript schema + JavaScript plugins + Python business logic)

**Next Steps**: See `INFRASTRUCTURE-DOCS_15-Summary-Table-Components.md` for a complete component inventory organized by category.
