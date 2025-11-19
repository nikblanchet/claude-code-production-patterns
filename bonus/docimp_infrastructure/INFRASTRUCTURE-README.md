# DocImp Development Infrastructure Inventory

**Complete documentation of the development infrastructure for the DocImp project.**

---

## Quick Start

**New to DocImp infrastructure?** Start here:

1. **Read**: `../INFRASTRUCTURE_BEST_EXAMPLES.md` - The 3 most impressive components with detailed explanations
2. **Scan**: `INFRASTRUCTURE-DOCS_1-Overview.md` - High-level architecture and philosophy
3. **Deep dive**: Topic-specific docs below based on your needs

---

## Documentation Files

### Best Examples (Start Here!)

**File**: `../INFRASTRUCTURE_BEST_EXAMPLES.md` (24,000 words)

**Purpose**: Showcase the 3 most impressive and sophisticated infrastructure components

**Contents**:
1. **Git Hooks + Worktree Workflow** (7,500 words)
   - Path-based branch protection
   - Two-layer hook system (protected + Husky)
   - Worktree creation orchestrator (1067-line Python script)
   - Change transfer logic (uncommitted + unpushed detection)
   - Per-worktree environment isolation

2. **Claude Code Configuration** (8,000 words)
   - Permission whitelist architecture (256 allow, 6 deny, 3 ask)
   - Symlink infrastructure (single source of truth)
   - External documentation pattern (68KB total in 27.8KB CLAUDE.md)
   - Public/private separation (CLAUDE.md vs CLAUDE_CONTEXT.md)

3. **Direnv Integration** (8,500 words)
   - Transparent tool interception (PATH injection)
   - Recursion prevention mechanism
   - Helpful error blocking (pip → uv add)
   - Node version auto-switching
   - Per-worktree isolation

**Why special**: Non-obvious solutions to real development challenges that most teams struggle with

**Read if**: You want to understand the most impressive patterns first

---

### Overview & Architecture

**File**: `INFRASTRUCTURE-DOCS_1-Overview.md` (5,500 words)

**Purpose**: High-level introduction to infrastructure philosophy and structure

**Contents**:
- Executive summary
- Infrastructure philosophy (automation over discipline, worktree-based parallel development)
- Project structure (polyglot architecture diagram)
- Infrastructure layers (6 layers explained)
- Key metrics (CLAUDE.md size, test counts, tool versions)
- Unique patterns (path-based detection, external docs, tool interception, change transfer, permission whitelist)
- Maintenance procedures (CLAUDE.md size management, worktree creation, Node/quality updates)

**Read if**: You're new to the project or need a refresher on overall architecture

---

### Git Hooks & Worktree Management

**File**: `INFRASTRUCTURE-DOCS_2-Git-Hooks.md` (7,800 words)

**Purpose**: Complete reference for git hook system and worktree workflow

**Contents**:
- Hook architecture (two-layer: protected + Husky)
- Protected hooks (pre-commit, post-checkout) with full code
- Husky integration (dispatchers, lint-staged)
- Per-worktree hook configuration
- Hook installation (automatic + manual)
- Testing hooks (6 test scenarios)
- Troubleshooting (4 common problems)
- Hook bypass scenarios

**Read if**: You need to understand or modify git hooks, debug hook issues, or create new worktrees

---

### Claude Code Configuration

**File**: `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md` (9,200 words)

**Purpose**: Complete reference for Claude Code permissions, symlinks, and documentation management

**Contents**:
- **Layer 1**: Permission whitelist (allow/deny/ask patterns, 256 rules documented)
- **Layer 2**: Symlink infrastructure (directory structure, symlink creation)
- **Layer 3**: CLAUDE.md external documentation pattern (40K limit management, @docs imports)
- **Layer 4**: CLAUDE_CONTEXT.md (public/private separation)
- Session initialization flow (what happens when Claude Code starts)
- Configuration updates (permissions, CLAUDE.md, CLAUDE_CONTEXT.md)
- Troubleshooting (broken symlinks, permission denied, missing changes)

**Read if**: You need to update permissions, manage CLAUDE.md size, understand Claude Code setup, or debug configuration issues

---

### Quality Checks & Linting

**File**: `INFRASTRUCTURE-DOCS_4-Quality-Checks.md` (8,100 words)

**Purpose**: Complete reference for all quality tools (Python + TypeScript/JavaScript)

**Contents**:
- **Python**: ruff (8 rule groups), mypy (strict mode), pytest (46+ tests)
- **TypeScript/JavaScript**: ESLint (7 plugins), Prettier, TypeScript compiler, Jest (27+ tests)
- Pre-commit integration (lint-staged)
- CI/CD integration (GitHub Actions quality gates)
- Running tools (local + CI commands)
- Example violations and fixes
- Configuration files explained

**Read if**: You need to add quality rules, understand linting errors, configure tools, or debug test failures

---

### CI/CD Pipeline

**File**: `INFRASTRUCTURE-DOCS_5-CI-CD.md` (6,700 words)

**Purpose**: Complete reference for GitHub Actions CI/CD pipeline

**Contents**:
- **5 jobs documented**: python-tests, typescript-tests, integration-test, module-system-matrix, workflow-validation
- Job dependency graph (parallel vs sequential)
- Setup steps (Python, Node, uv, npm)
- Quality checks per job
- Caching strategy (npm + uv)
- Environment variables (DOCIMP_ANALYZER_PATH)
- Typical CI timeline (best/worst case)
- Pull request protection rules
- Local CI simulation
- Debugging CI failures

**Read if**: You need to understand CI failures, modify workflows, add CI checks, or optimize CI performance

---

### Direnv Integration

**File**: `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md` (7,400 words)

**Purpose**: Complete reference for direnv tool interception and environment management

**Contents**:
- Tool interception architecture (PATH injection)
- Python tool interceptors (python, pip, pytest, ruff, mypy) with full code
- Recursion prevention mechanism
- Node version auto-switching (.nvmrc)
- Per-worktree environment isolation
- Session startup flow
- Dual enforcement (direnv + Claude Code permissions)
- Benefits of direnv integration
- Troubleshooting (5 common problems)

**Read if**: You need to understand tool interception, debug direnv issues, modify interceptors, or add new tools

---

### Standardization Patterns

**File**: `INFRASTRUCTURE-DOCS_7-Standardization-Patterns.md`

**Purpose**: Common patterns and conventions enforced across the codebase

**Read if**: You need to understand project-wide conventions and standardization approaches

---

### Test Infrastructure

**File**: `INFRASTRUCTURE-DOCS_8-Test-Infrastructure.md`

**Purpose**: Complete testing strategy and organization

**Read if**: You need to understand test organization, add new tests, or debug test failures

---

### EditorConfig & Style

**File**: `INFRASTRUCTURE-DOCS_9-EditorConfig-Style.md`

**Purpose**: Editor configuration and style enforcement

**Read if**: You need to configure editor settings or understand style rules

---

### Development Utilities

**File**: `INFRASTRUCTURE-DOCS_10-Development-Utilities.md`

**Purpose**: Development scripts and utilities

**Read if**: You need to use or modify development utilities

---

### Planning & Documentation

**File**: `INFRASTRUCTURE-DOCS_11-Planning-Documentation.md`

**Purpose**: Planning infrastructure and documentation patterns

**Read if**: You need to understand project planning or documentation structure

---

### State & Configuration Files

**File**: `INFRASTRUCTURE-DOCS_12-State-Configuration-Files.md`

**Purpose**: State management and configuration file reference

**Read if**: You need to understand state persistence or configuration management

---

### Dependency Lock Files

**File**: `INFRASTRUCTURE-DOCS_13-Dependency-Lock-Files.md` (~8,300 words)

**Purpose**: Complete reference for dependency lock file management (Python uv + Node.js npm)

**Contents**:
- **Python (uv)**: uv.lock, requirements.lock, requirements-dev.lock architecture
- **Node.js (npm)**: package-lock.json structure and workflows
- Adding/updating/removing dependencies
- Per-worktree environment isolation (isolated .venv, shared node_modules)
- Lock file conflict resolution strategies
- Syncing environments across worktrees
- Troubleshooting dependency issues
- Best practices (commit hygiene, update cadence, security scanning)

**Read if**: You need to manage dependencies, resolve lock file conflicts, understand environment setup, or debug dependency issues

---

### Interaction Map & Data Flow

**File**: `INFRASTRUCTURE-DOCS_14-Interaction-Map-Data-Flow.md` (~9,500 words)

**Purpose**: Component interaction architecture and data flow visualization

**Contents**:
- **Component Interaction Diagram**: Complete ASCII map of all infrastructure components
- **Data Flow Patterns**: TypeScript CLI ↔ Python analyzer ↔ JavaScript plugins
- **Workflow Sequences**: 10-step development session (worktree → commit → CI → PR → merge)
- **Analyze Command Flow**: 11-step data flow (CLI → subprocess → parsers → impact scoring → JSON output)
- **Improve Command Flow**: 13-step workflow (plan → Claude → validation → write → transaction)
- **State Management Flow**: Workflow state tracking and staleness detection
- **Integration Points**: Git hooks ↔ lint-staged, CI/CD ↔ workflow validation, plugin validation ↔ docstring writer

**Read if**: You need to understand how components interact, trace data flow for debugging, understand workflow sequences, or identify integration points for new features

---

### Summary Table: Infrastructure Components

**File**: `INFRASTRUCTURE-DOCS_15-Summary-Table-Components.md` (~7,000 words)

**Purpose**: Comprehensive inventory of all infrastructure components organized by category

**Contents**:
- **13 Categories**: Git, Claude Code, Python Quality, TypeScript Quality, CI/CD, Development Workflow, Package Management, Editor/Formatting, Documentation, Test Infrastructure, State Management, Utilities, Ignore Files
- **80+ Components**: Each with file location, type, purpose, key settings, dependencies, maintenance notes
- **Quick Reference Tables**: Critical files by category, update frequency, component relationships
- **File Locations**: Absolute paths for every configuration file
- **Maintenance Procedures**: Update frequency and considerations per component

**Read if**: You need to quickly locate configuration files, understand component relationships, plan maintenance tasks, or get an overview of the entire infrastructure

---

### Key Metrics

**File**: `INFRASTRUCTURE-DOCS_16-Key-Metrics.md` (~8,200 words)

**Purpose**: Quantitative project metrics, performance targets, and technical constraints

**Contents**:
- **Code Quality Metrics**: Ruff rule groups (8), ESLint plugins (7), zero-tolerance violations
- **Test Coverage**: Python (85% unit, 75% integration), TypeScript (80% unit, 65% integration)
- **Build Performance**: TypeScript build (~5s), Python setup (~15s), npm install (~25s with cache)
- **CI/CD Performance**: Total runtime (~4 minutes), cache hit rates (~90% npm, ~85% uv)
- **Dependency Versions**: Python 3.13, Node 24.11.0, version constraints and update cadence
- **File Size Limits**: CLAUDE.md (27.8KB / 40KB max), .docimp/ directory (~5MB), lock files
- **Performance Benchmarks**: Workflow state operations (<100ms), incremental analysis (90-95% speedup)
- **Trends Over Time**: Growth metrics, performance improvements, coverage trends

**Read if**: You need to understand project scale, monitor infrastructure health, set performance targets, plan upgrades, or benchmark against baselines

---

### Integration Sequences

**File**: `INFRASTRUCTURE-DOCS_17-Integration-Sequences.md` (~8,400 words)

**Purpose**: Step-by-step workflows for common development tasks integrating all infrastructure components

**Contents**:
- **Adding New Command**: 7-step workflow (TypeScript CLI + Python backend + tests + CI)
- **Modifying Parser**: 7-step workflow (code changes + tests + edge cases + validation)
- **Adding Plugin**: 6-step workflow (JavaScript implementation + tests + config + manual testing)
- **Updating Quality Rules**: 5-step workflow (config modification + codebase application + validation)
- **Updating Dependencies**: 6-step workflow (check + update + test + breaking changes + commit)
- **Adding Documentation**: 5-step workflow (create file + content + reference + size check)
- **Troubleshooting**: Common integration issues (lint-staged failures, CI failures, module system tests)

**Read if**: You need to add commands/parsers/plugins, update dependencies/quality rules, add documentation, or debug integration failures

---

### Critical Dependencies & Constraints

**File**: `INFRASTRUCTURE-DOCS_18-Critical-Dependencies-Constraints.md` (~6,900 words)

**Purpose**: Complete catalog of dependencies, version constraints, compatibility requirements, and upgrade procedures

**Contents**:
- **Python Dependencies**: anthropic (Claude API), pydantic (validation), pytest/ruff/mypy (quality)
- **TypeScript Dependencies**: commander, chalk/ora (ESM-only), prompts, uuid, zod, jest/eslint
- **Version Constraints**: Node 24+, Python 3.13+, Git 2.28+, uv 0.9.8+, ESLint 9+, Husky 9.1.7+
- **Compatibility Matrices**: Python 3.11-3.13, Node 20-24, ESM vs CommonJS support
- **Breaking Change Scenarios**: Major version updates (anthropic 1.0, ESLint v10, TypeScript v6)
- **Dependency Audit**: Security procedures (npm audit, uv pip list --outdated), license compliance

**Read if**: You need to understand dependency requirements, update dependencies, handle breaking changes, audit security, or debug version conflicts

---

### Maintenance Procedures

**File**: `INFRASTRUCTURE-DOCS_19-Maintenance-Procedures.md` (~6,100 words)

**Purpose**: Step-by-step procedures for ongoing infrastructure maintenance tasks

**Contents**:
- **Adding Git Hooks**: 5-step procedure (protected hook + Husky dispatcher + testing + documentation)
- **Updating Node Version**: 5-step procedure (.nvmrc + install + global migration + testing + CI)
- **Updating CLAUDE.md**: 6-step procedure (assess + external docs + reference + size check + commit)
- **Onboarding Worktree**: 6-step procedure (create_worktree.py + git config + Husky + direnv + verification)
- **Dependency Updates**: Weekly/monthly/quarterly schedules (security, patches, minors, majors)
- **CI/CD Maintenance**: Adding jobs, updating actions, verification
- **Maintenance Checklist**: Weekly, monthly, quarterly, as-needed tasks

**Read if**: You need to maintain infrastructure, update tools, add hooks, manage CLAUDE.md size, create worktrees, or schedule dependency updates

---

### Security & Isolation

**File**: `INFRASTRUCTURE-DOCS_20-Security-Isolation.md` (~6,600 words)

**Purpose**: Security model, isolation strategies, threat models, and incident response

**Contents**:
- **Main Worktree Protection**: Pre-commit/post-checkout hooks, bypass procedures, worktree detection
- **Environment Isolation**: Per-worktree .venv, direnv scope, Node version separation, state isolation
- **Dependency Management**: Lockfile strategy (SHA-256 hashes), Claude Code whitelisting, no bare pip
- **Plugin System**: No sandboxing (intentional), whitelist approach, symlink resolution, code review checklist
- **Credential Handling**: .env files (gitignored), CI secrets, .gitignore philosophy (no credential patterns)
- **Access Controls**: Claude Code permissions, file system boundaries
- **Incident Response**: Credential committed (revoke + regenerate), malicious plugin detected (IOC check)

**Read if**: You need to understand security boundaries, configure permissions, handle credentials, review plugin code, or respond to security incidents

---

### Performance Considerations

**File**: `INFRASTRUCTURE-DOCS_21-Performance-Considerations.md` (~5,900 words)

**Purpose**: Performance optimizations, benchmarks, bottleneck identification, and trade-offs

**Contents**:
- **CI/CD Performance**: 4-5 minute pipeline (parallel jobs, caching, no matrix), baseline metrics
- **Test Execution**: Sequential Jest (stability over speed), pytest markers (unit vs integration)
- **Linting & Formatting**: lint-staged (staged files only), Ruff (10× faster than black+flake8)
- **Incremental Analysis**: 90% time savings (5 changed files in 100-file codebase)
- **Caching Strategies**: Plugin validation cache (10-100× speedup), workflow state persistence
- **Performance Benchmarks**: Automated regression detection, target metrics
- **Bottleneck Identification**: Python profiling (cProfile), TypeScript profiling (Node.js built-in)
- **Trade-offs Matrix**: Speed gains vs costs for each optimization

**Read if**: You need to optimize performance, debug slow CI, understand caching, identify bottlenecks, or evaluate trade-offs

---

### Future Extension Points

**File**: `INFRASTRUCTURE-DOCS_22-Future-Extension-Points.md` (~6,400 words)

**Purpose**: Clear extension points for adding features without disrupting architecture

**Contents**:
- **Adding Commands**: TypeScript + Python templates, integration steps, 7 locations modified
- **Adding Parsers**: Language parser template, BaseParser inheritance, registration procedure
- **Adding Plugins**: Validation plugin template, beforeAccept/afterWrite hooks, config registration
- **Adding Quality Rules**: Ruff (Python) and ESLint (TypeScript) configuration templates
- **Adding GitHub Workflows**: Security scanning template, trigger options, status badges
- **Adding Documentation**: Pattern docs (docs/patterns/), user guides (docs/user-guide/)
- **Configuration Hooks**: docimp.config.js, .claude/skills/, CLAUDE.md
- **Backward Compatibility**: Versioning strategy, deprecation process, migration commands

**Read if**: You need to extend DocImp (new commands/parsers/plugins), add infrastructure components, understand extension patterns, or maintain backward compatibility

---

## Document Sizes

| File | Words | Purpose |
|------|-------|---------|
| `../INFRASTRUCTURE_BEST_EXAMPLES.md` | 24,000 | Top 3 most impressive components |
| `INFRASTRUCTURE-DOCS_1-Overview.md` | 5,500 | Architecture and philosophy |
| `INFRASTRUCTURE-DOCS_2-Git-Hooks.md` | 7,800 | Git hooks and worktree workflow |
| `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md` | 9,200 | Permissions and documentation |
| `INFRASTRUCTURE-DOCS_4-Quality-Checks.md` | 8,100 | Linting, formatting, testing |
| `INFRASTRUCTURE-DOCS_5-CI-CD.md` | 6,700 | GitHub Actions pipeline |
| `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md` | 7,400 | Tool interception and environment |
| `INFRASTRUCTURE-DOCS_7-Standardization-Patterns.md` | TBD | Standardization patterns |
| `INFRASTRUCTURE-DOCS_8-Test-Infrastructure.md` | TBD | Testing strategy and organization |
| `INFRASTRUCTURE-DOCS_9-EditorConfig-Style.md` | TBD | Editor configuration and style |
| `INFRASTRUCTURE-DOCS_10-Development-Utilities.md` | TBD | Development scripts and utilities |
| `INFRASTRUCTURE-DOCS_11-Planning-Documentation.md` | TBD | Planning and documentation patterns |
| `INFRASTRUCTURE-DOCS_12-State-Configuration-Files.md` | TBD | State management and config files |
| `INFRASTRUCTURE-DOCS_13-Dependency-Lock-Files.md` | 8,300 | Dependency lock file management |
| `INFRASTRUCTURE-DOCS_14-Interaction-Map-Data-Flow.md` | 9,500 | Component interactions and data flow |
| `INFRASTRUCTURE-DOCS_15-Summary-Table-Components.md` | 7,000 | Complete component inventory |
| `INFRASTRUCTURE-DOCS_16-Key-Metrics.md` | 8,200 | Project metrics and performance targets |
| `INFRASTRUCTURE-DOCS_17-Integration-Sequences.md` | 8,400 | Step-by-step integration workflows |
| `INFRASTRUCTURE-DOCS_18-Critical-Dependencies-Constraints.md` | 6,900 | Dependency catalog and constraints |
| `INFRASTRUCTURE-DOCS_19-Maintenance-Procedures.md` | 6,100 | Infrastructure maintenance procedures |
| `INFRASTRUCTURE-DOCS_20-Security-Isolation.md` | 6,600 | Security model and isolation strategies |
| `INFRASTRUCTURE-DOCS_21-Performance-Considerations.md` | 5,900 | Performance optimization and benchmarks |
| `INFRASTRUCTURE-DOCS_22-Future-Extension-Points.md` | 6,400 | Extension points and templates |
| **Total (completed)** | **142,000** | **Complete infrastructure documentation** |

---

## Quick Reference: Component Locations

### Git Hooks
- **Protected hooks**: `.git/hooks/pre-commit`, `.git/hooks/post-checkout`
- **Husky dispatchers**: `.husky/pre-commit`, `.husky/post-checkout`
- **Lint-staged config**: `cli/package.json` ("lint-staged" section)

### Claude Code
- **Permissions**: `.docimp-shared/.claude/settings.local.json` (symlinked to `.claude/settings.local.json`)
- **Technical docs**: `.docimp-shared/CLAUDE.md` (27.8KB, symlinked)
- **Private context**: `.docimp-shared/CLAUDE_CONTEXT.md` (gitignored, symlinked)
- **External docs**: `docs/patterns/*.md` (6 files, 40.5KB)

### Quality Tools
- **Python ruff**: `ruff.toml` (root), `analyzer/pyproject.toml` (tool.ruff)
- **Python mypy**: `analyzer/pyproject.toml` (tool.mypy)
- **Python pytest**: `analyzer/pytest.ini`
- **TypeScript ESLint**: `cli/eslint.config.mjs`
- **Prettier**: `.prettierrc`
- **TypeScript**: `cli/tsconfig.json`
- **Jest**: `cli/jest.config.js`

### CI/CD
- **GitHub Actions**: `.github/workflows/ci.yml`

### Direnv
- **Configuration**: `.envrc` (root)
- **Interceptors**: `.direnv/bin/` (generated, gitignored)

### Development Workflow
- **Worktree creation**: `.claude/skills/git-workflow/scripts/create_worktree.py`
- **Node version**: `.nvmrc`
- **Python version**: `.python-version`

---

## Quick Reference: Common Tasks

### Creating a New Worktree
```bash
python3 .claude/skills/git-workflow/scripts/create_worktree.py issue-300 feature-config
```

**See**: `INFRASTRUCTURE-DOCS_2-Git-Hooks.md` (Testing Hooks section)

### Updating CLAUDE.md (Approaching 40K Limit)
1. Check size: `wc -c CLAUDE.md`
2. Identify verbose sections
3. Create external doc: `docs/patterns/new-file.md`
4. Replace with import: `@docs/patterns/new-file.md`
5. Commit both files

**See**: `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md` (Maintenance section)

### Adding New Quality Rule
**Python**:
```bash
# Edit ruff.toml or analyzer/pyproject.toml
# Apply: uv run ruff check . --fix && uv run ruff format .
```

**TypeScript**:
```bash
# Edit cli/eslint.config.mjs
# Apply: npm run lint -- --fix
```

**See**: `INFRASTRUCTURE-DOCS_4-Quality-Checks.md`

### Debugging CI Failure
1. Check which job failed (python-tests, typescript-tests, etc.)
2. Read error message in CI logs
3. Reproduce locally (see "Local CI Simulation" in INFRASTRUCTURE-DOCS_5-CI-CD.md)
4. Fix issue, push, re-run CI

**See**: `INFRASTRUCTURE-DOCS_5-CI-CD.md` (Debugging CI Failures section)

### Fixing direnv Interception
```bash
# If not loading: direnv allow
# If outdated: direnv allow (force reload)
# If interceptor broken: edit .envrc, then direnv allow
```

**See**: `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md` (Troubleshooting section)

---

## Reading Paths

### For New Contributors

**Path 1: Quick Start (30 minutes)**
1. Read: `INFRASTRUCTURE-DOCS_1-Overview.md`
2. Scan: `../INFRASTRUCTURE_BEST_EXAMPLES.md` (introduction of each section)
3. Try: Create a worktree, run quality checks, observe direnv interception

**Path 2: Deep Dive (2-3 hours)**
1. Read: `../INFRASTRUCTURE_BEST_EXAMPLES.md` (all 3 sections)
2. Read: Topic-specific docs based on role (e.g., Git Hooks for workflow, Quality Checks for testing)

### For Job Interviewers / Reviewers

**Path: Showcase (1 hour)**
1. **Start**: `../INFRASTRUCTURE_BEST_EXAMPLES.md`
   - Read section 1 (Git Hooks + Worktree Workflow) - 20 minutes
   - Read section 2 (Claude Code Configuration) - 20 minutes
   - Read section 3 (Direnv Integration) - 20 minutes
2. **Context**: `INFRASTRUCTURE-DOCS_1-Overview.md` (Key Metrics, Unique Patterns) - 10 minutes

**What this demonstrates**:
- Sophisticated problem-solving (path-based detection, external docs pattern, tool interception)
- Full-stack expertise (Python, TypeScript, JavaScript, Bash, Git)
- DevOps skills (CI/CD, environment management, automation)
- Documentation quality (68,700 words of technical documentation)
- Attention to detail (recursion prevention, per-worktree isolation, educational errors)

### For Debugging / Maintenance

**Path: Problem-Specific**

| Problem | Read |
|---------|------|
| Hook not blocking main commits | `INFRASTRUCTURE-DOCS_2-Git-Hooks.md` (Troubleshooting) |
| Claude Code permission denied | `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md` (Permission Flow) |
| Linting error | `INFRASTRUCTURE-DOCS_4-Quality-Checks.md` (Example Violations) |
| CI failure | `INFRASTRUCTURE-DOCS_5-CI-CD.md` (Debugging CI Failures) |
| direnv not intercepting | `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md` (Troubleshooting) |

---

## Infrastructure Philosophy Summary

### Core Principles

1. **Automation Over Discipline**
   - Don't rely on developers remembering rules
   - Use tool interception, git hooks, CI/CD to enforce correctness
   - Make the correct path the easy path

2. **Worktree-Based Parallel Development**
   - Main worktree protected (read-only reference state)
   - Feature worktrees for all development work
   - Per-worktree environment isolation (Python .venv, Node node_modules)
   - Multiple Claude Code instances working simultaneously

3. **Educational Infrastructure**
   - Error messages teach correct workflow
   - Helpful redirects instead of silent failures
   - Documentation generated from infrastructure code

4. **Single Source of Truth**
   - Symlinked configurations (no duplication)
   - Shared infrastructure directory (.docimp-shared/)
   - External documentation imports (@docs/patterns/)

5. **Polyglot Quality Standards**
   - Python: ruff (8 rule groups), mypy, pytest
   - TypeScript: ESLint (7 plugins), Prettier, Jest, strict tsconfig
   - JavaScript: Real JSDoc type-checking via TypeScript compiler

### Key Innovations

**1. Path-Based Worktree Detection** (Git Hooks):
```bash
if [[ ! "$current_worktree" =~ /.docimp-wt/ ]]; then
    # Main worktree - block operation
fi
```

**Why innovative**: Robust, maintainable, obvious (vs fragile git metadata checks)

**2. External Documentation Imports** (Claude Code):
```markdown
## Error Handling
- @docs/patterns/error-handling.md
```

**Why innovative**: Stays under 40KB CLAUDE.md limit while providing 68KB total docs

**3. Transparent Tool Interception** (direnv):
```bash
PATH_add .direnv/bin  # Highest priority
exec uv run python "$@"  # After PATH scrubbing
```

**Why innovative**: 100% enforcement, zero manual compliance, transparent to users

---

## Metrics & Statistics

### Infrastructure Scale

| Metric | Count |
|--------|-------|
| Documentation files | 23 (19 sections complete, 4 in progress) |
| Total documentation | 142,000+ words |
| Git hooks | 4 (2 protected + 2 Husky) |
| Python quality tools | 3 (ruff, mypy, pytest) |
| TypeScript quality tools | 4 (ESLint, Prettier, tsc, Jest) |
| CI/CD jobs | 5 |
| ESLint plugins | 7 |
| Ruff rule groups | 8 |
| Python test files | 46+ |
| TypeScript test files | 27+ |
| E2E test scripts | 5 |
| Claude Code permissions | 265 (256 allow + 6 deny + 3 ask) |
| Symlinked files | 7 per worktree |
| Tool interceptors | 6 (python, pip, pytest, ruff, mypy, Node) |

### Code Quality

| Tool | Purpose | Coverage |
|------|---------|----------|
| ruff | Linting + formatting | 8 rule groups, Python 3.13+ |
| mypy | Type checking | Strict mode, warn on Any |
| pytest | Testing | 46+ test files, unit + integration |
| ESLint | Linting | 7 plugins, flat config |
| Prettier | Formatting | 2-space, single quotes, LF |
| TypeScript | Type checking | checkJs:true, strict mode |
| Jest | Testing | 27+ test files, ESM preset |

### Automation Coverage

| Layer | Tool | Enforcement |
|-------|------|-------------|
| Pre-commit | lint-staged | Auto-fix on commit |
| Git hooks | Protected hooks | Block main commits |
| direnv | Tool interceptors | Redirect to uv run |
| Claude Code | Permissions | Block dangerous operations |
| CI/CD | GitHub Actions | Block PRs with violations |

---

## Common Patterns Across Infrastructure

### 1. Dual Enforcement

**Pattern**: Enforce constraints at multiple layers (belt + suspenders)

**Examples**:
- Git hooks (local) + GitHub Actions (remote)
- direnv interception (local) + Claude Code permissions (AI)
- ruff format (pre-commit) + GitHub Actions (CI)

**Benefit**: No single point of failure, defense in depth

### 2. Educational Errors

**Pattern**: Error messages teach correct workflow

**Examples**:
- Git hook: "Cannot commit on main... use create_worktree.py"
- direnv: "✗ Bare 'pip' detected! Use 'uv add <package>'"
- Claude Code: Permission denied → shows correct alternative

**Benefit**: Developers learn from errors, reduce future violations

### 3. Per-Worktree Isolation

**Pattern**: Each worktree has independent environment

**Examples**:
- Separate `.venv/` (no lock contention)
- Separate `.direnv/bin/` (independent interceptors)
- Separate `node_modules/` (dependency testing)

**Benefit**: Parallel development enabled, no conflicts

### 4. Single Source of Truth

**Pattern**: One authoritative source, everything else symlinks/references

**Examples**:
- CLAUDE.md symlinked to `.docimp-shared/CLAUDE.md`
- Permissions symlinked to `.docimp-shared/.claude/settings.local.json`
- External docs referenced via `@docs/patterns/*.md`

**Benefit**: No synchronization issues, no divergence

### 5. Transparency to Users

**Pattern**: Infrastructure works invisibly until it prevents mistakes

**Examples**:
- direnv redirects bare `python` → `uv run python` (user types familiar command)
- Symlinks appear as regular files (user edits CLAUDE.md, applies everywhere)
- Pre-commit hooks auto-fix violations (user commits, code auto-formatted)

**Benefit**: Low friction, high enforcement

---

## Next Steps After Reading

### For Contributors

1. **Set up local environment**:
   - Install direnv, allow `.envrc`
   - Create test worktree
   - Run quality checks locally

2. **Make a test change**:
   - Modify a file
   - Commit (observe lint-staged)
   - Create PR (observe CI)

3. **Read topic-specific docs** based on your work

### For Reviewers

1. **Understand the unique patterns**:
   - Path-based worktree detection
   - External documentation imports
   - Transparent tool interception

2. **See it in action**:
   - Try creating a worktree
   - Attempt to commit on main (observe block)
   - Type bare `python` (observe redirect)

3. **Review the scope**:
   - 68,700 words of documentation
   - 7 major infrastructure components
   - 265 Claude Code permissions
   - 5 CI/CD jobs

### For Maintenance

1. **Bookmark this README** - Central navigation hub

2. **Use Quick Reference sections** - Fast lookup for common tasks

3. **Follow maintenance procedures** - CLAUDE.md size management, worktree creation, etc.

---

## Contributing to Infrastructure Docs

### When to Update These Docs

**Always update** when:
- Adding new infrastructure component (new git hook, quality tool, CI job)
- Changing existing patterns (hook logic, permissions, interceptors)
- Adding/removing tools (ESLint plugin, ruff rule group)

**Consider updating** when:
- Fixing bugs in infrastructure (document the fix)
- Discovering non-obvious patterns (add to BEST_EXAMPLES)
- Adding troubleshooting solutions (add to Troubleshooting sections)

### How to Update

1. **Identify affected docs**:
   - New git hook → `INFRASTRUCTURE-DOCS_2-Git-Hooks.md`
   - New permission → `INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md`
   - New quality tool → `INFRASTRUCTURE-DOCS_4-Quality-Checks.md`
   - New CI job → `INFRASTRUCTURE-DOCS_5-CI-CD.md`
   - New interceptor → `INFRASTRUCTURE-DOCS_6-Direnv-Integration.md`

2. **Update docs**:
   - Add new section or expand existing
   - Include code blocks (show, don't just tell)
   - Explain rationale (why this approach)
   - Update metrics/statistics

3. **Update this README**:
   - Update Quick Reference if needed
   - Update metrics/statistics
   - Add to Common Tasks if applicable

4. **Commit**:
   ```bash
   git add .planning/INFRASTRUCTURE-*.md
   git commit -m "Document [new component/change]"
   ```

---

## Conclusion

This infrastructure represents **142,000+ words** of documented development automation across **23 sections** (19 complete):

1. **Best Examples** - Top 3 most impressive infrastructure components (24,000 words)
2. **Overview** - Architecture and infrastructure philosophy (5,500 words)
3. **Git Hooks** - Two-layer protection with worktree workflow (7,800 words)
4. **Claude Code Config** - Permission whitelist + documentation management (9,200 words)
5. **Quality Checks** - 8 tools across Python and TypeScript/JavaScript (8,100 words)
6. **CI/CD** - 5 GitHub Actions jobs with parallel/sequential execution (6,700 words)
7. **Direnv Integration** - 6 tool interceptors with transparent enforcement (7,400 words)
8. **Standardization Patterns** - Common patterns and conventions (in progress)
9. **Test Infrastructure** - Testing strategy and organization (in progress)
10. **EditorConfig & Style** - Editor configuration and style enforcement (in progress)
11. **Development Utilities** - Development scripts and utilities (in progress)
12. **Planning & Documentation** - Planning infrastructure and documentation patterns (in progress)
13. **State & Configuration** - State management and configuration files (in progress)
14. **Dependency Lock Files** - Complete uv/npm lock file management (8,300 words)
15. **Interaction Map & Data Flow** - Component interactions and workflow sequences (9,500 words)
16. **Summary Table** - Complete component inventory across 13 categories (7,000 words)
17. **Key Metrics** - Quantitative metrics, performance targets, and constraints (8,200 words)
18. **Integration Sequences** - Step-by-step workflows for common tasks (8,400 words)
19. **Critical Dependencies** - Dependency catalog, constraints, and upgrade procedures (6,900 words)
20. **Maintenance Procedures** - Infrastructure maintenance and update procedures (6,100 words)
21. **Security & Isolation** - Security model, threats, and incident response (6,600 words)
22. **Performance Considerations** - Optimization strategies and benchmarks (5,900 words)
23. **Future Extension Points** - Templates and patterns for extending infrastructure (6,400 words)

**Key achievements**:
- ✅ 100% workflow compliance (automation over discipline)
- ✅ Zero manual environment management (direnv + per-worktree isolation)
- ✅ Educational infrastructure (error messages teach correct workflow)
- ✅ Parallel development enabled (multiple Claude Code instances)
- ✅ Single source of truth (symlinks + external docs)
- ✅ Comprehensive documentation (142,000 words across 23 sections)

**For questions or issues**: See topic-specific documentation above or create an issue.
