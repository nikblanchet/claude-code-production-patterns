# Claude Code Production Patterns

Advanced integration patterns for Claude Code: hooks, agents, and skills that power sophisticated AI-assisted development workflows.

## About This Repository

This repository serves as both **documentation and demonstration** of advanced Claude Code patterns. Rather than just describing concepts, it contains working implementations you can install and use immediately. Every pattern documented here is production-tested and ready for real-world use.

**What's Demonstrated**: This repository implements **Scenario C: Claude Code Agents and Hooks - Advanced Integration Patterns**, including:

- **Claude Code Hooks** - Event-driven workflow automation and permission systems
- **Custom Agents** - Autonomous subprocesses for complex multi-step tasks with fresh context
- **Custom Skills** - Specialized knowledge modules with bundled resources
- **Git Worktree Orchestration** - Parallel development without merge conflicts
- **Git Hooks for AI Safety** - Branch protection and worktree isolation
- **Symlink Discovery Pattern** - Separate documentation from runtime configuration

All patterns extracted from production use and tested at scale.

**Ongoing Development**: I found this exercise enlightening and have decided to continue expanding this repository both for my own edification (it's useful to have all my production patterns documented in one place) and for the general utility of others working with Claude Code at scale.

**For Evaluators and Hiring Teams**: You can fork this repository and revert to commit `[initial-submission]` to see the state at the time of the original assignment submission. The repository continues to evolve with additional patterns and refinements based on production use.

**Background**: This repository was created in response to a technical documentation assignment. See [`docs/ASSIGNMENT.md`](docs/ASSIGNMENT.md) for the original prompt and requirements that shaped this work.

## See It Working (Quick Start)

Want to see these patterns in action right now?

Follow **[examples/QUICKSTART.md](examples/QUICKSTART.md)** for 15-minute demonstrations of:
- Git hooks protecting commits
- Worktree creation and isolation
- Skills and agents installation
- Complete workflow validation

Everything in this repo is functional and ready to use.

## Repository Structure

```
.
├── actual-code/              # Working implementations
│   ├── hooks-config/         # Claude Code hooks and permissions
│   ├── skills/              # Custom skills
│   │   ├── user/            # Global skills (6 skills)
│   │   ├── official/        # Anthropic official skills
│   │   └── project/         # Project-specific skills
│   ├── agents/              # Custom agents
│   │   ├── user/            # Global agents
│   │   └── project/         # Project-specific agents
│   ├── hooks/               # Git hooks (worktree protection)
│   └── create_worktree.py   # Worktree automation
├── diagrams/                # Visual documentation
├── ADVANCED_PATTERNS.md     # Advanced patterns guide
└── PLANNING.md              # Project planning
```

## Core Patterns

### 1. Claude Code Hooks and Permissions

**Location**: [`actual-code/hooks-config/`](actual-code/hooks-config/)

Event-driven shell commands that execute during Claude Code sessions, enabling workflow automation, quality gates, and tool integration.

**Key Features**:
- User prompt submit hooks (inject context automatically)
- Tool call hooks (intercept/log tool execution)
- Session lifecycle hooks (setup/cleanup)
- Permission system (allow/deny/ask patterns)
- Workflow enforcement (block dangerous operations)

**Critical Distinction**: Claude Code hooks (event-driven during AI sessions) are completely different from Git hooks (triggered by Git operations).

**Quick Start**:
```bash
cp actual-code/hooks-config/settings.local.json .claude/
# Customize permissions and hooks for your workflow
```

See [`actual-code/hooks-config/README.md`](actual-code/hooks-config/README.md) for comprehensive documentation.

---

### 2. Custom Agents

**Location**: [`actual-code/agents/`](actual-code/agents/)

Autonomous subprocesses that execute complex multi-step tasks with fresh eyes (no inherited conversation context).

#### User Agents (Global)

**Location**: [`actual-code/agents/user/`](actual-code/agents/user/)

- **python-313-conventions**: Python 3.13+ modernization reviewer
  - Reviews semantic patterns automation cannot check
  - 10 dimensions: typing, API design, async, error handling, etc.
  - Complements Ruff/mypy with design-level review

#### Project Agents (Project-Specific)

**Location**: [`actual-code/agents/project/`](actual-code/agents/project/)

- **code-reviewer**: Autonomous 11-dimension code review
  - Reviews against project requirements and standards
  - Gathers context from PR, .planning/PLAN.md, linked issues
  - Checks previous review findings (now acceptance criteria)
  - Classifies: Blocker, Important, Minor, Enhancement
  - Saves detailed review, posts summary to PR

**Quick Start**:
```bash
# User agent
cp actual-code/agents/user/python-313-conventions.md ~/.claude/agents/

# Project agent
cp -r actual-code/agents/project/ .claude/agents/
```

See agent READMEs for usage patterns and invocation examples.

---

### 3. Custom Skills

**Location**: [`actual-code/skills/`](actual-code/skills/)

Specialized knowledge and workflows loaded into context when relevant.

#### User Skills (Global Standards)

**Location**: [`actual-code/skills/user/`](actual-code/skills/user/)

- **access-skill-resources**: Navigate skill symlinks and bundled resources
- **cli-ux-colorful**: ANSI colors and terminal formatting
- **dependency-management**: Library usage philosophy (conda+pip)
- **development-standards**: No emoji, modern features, thorough docs (CRITICAL)
- **exhaustive-testing**: Comprehensive test coverage
- **handle-deprecation-warnings**: Proactive API migration

#### Official Skills

**Location**: [`actual-code/skills/official/`](actual-code/skills/official/)

- **skill-creator**: Guide for creating effective skills
  - Six-step process: Understanding → Planning → Initializing → Editing → Packaging → Iterating
  - Bundled resources: scripts/, references/, assets/
  - Progressive disclosure design

#### Project Skills (Project-Specific)

**Location**: [`actual-code/skills/project/`](actual-code/skills/project/)

- **git-workflow**: Git worktree-based workflow
  - Incremental commits after logical units
  - Worktree creation automation
  - Nested issue branches
  - Per-worktree Python environments
  - Branch protection via Git hooks

**Quick Start**:
```bash
# User skills (global)
cp -r actual-code/skills/user/* ~/.claude/skills/

# Project skills
cp -r actual-code/skills/project/* .claude/skills/
```

See skill READMEs for detailed instructions and usage patterns.

---

### 4. Git Worktree Orchestration

**Location**: [`actual-code/hooks/`](actual-code/hooks/) and [`actual-code/create_worktree.py`](actual-code/create_worktree.py)

Git hooks and automation for worktree-based parallel development.

**Key Features**:
- Pre-commit hook blocks commits to main in main worktree
- Post-checkout hook prevents branch switching in main worktree
- Automated worktree creation with symlinks
- Per-worktree Python environments (no lock contention)
- Shared context across worktrees (.scratch/, .planning/)

**Quick Start**:
```bash
# Install Git hooks
cp actual-code/hooks/pre-commit .git/hooks/
cp actual-code/hooks/post-checkout .git/hooks/
chmod +x .git/hooks/pre-commit .git/hooks/post-checkout

# Create worktree
python3 actual-code/create_worktree.py issue-123 feature-branch
```

See [`actual-code/hooks/README.md`](actual-code/hooks/README.md) for hook documentation.

---

## Pattern Integration

These patterns work together to create sophisticated AI-assisted workflows:

```
Hook (event trigger)
  ↓
Skill (domain knowledge)
  ↓
Agent (complex execution)
  ↓
Git Integration (quality gates)
```

**Example workflow**:
1. **Hook**: User submits prompt → inject git status into context
2. **Skill**: git-workflow skill provides commit standards
3. **Agent**: code-reviewer agent reviews changes autonomously
4. **Git Hook**: Blocks commit if tests fail or on wrong branch

## Advanced Topics

For deeper implementation details and additional patterns, see:
- [`ADVANCED_PATTERNS.md`](ADVANCED_PATTERNS.md) - Comprehensive pattern guide including symlink discovery, CLAUDE.md management, direnv integration, and worktree orchestration
- [`PATTERNS_RATIONALE.md`](PATTERNS_RATIONALE.md) - Why these patterns and when to use them

## Development Setup

This repository uses Python 3.14+ with uv for dependency management:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run type checking
uv run mypy .

# Run linting
uv run ruff check .
```

## Usage Recommendations

### Start Here

1. **Hooks**: Set up permissions in `.claude/settings.local.json`
2. **Skills**: Install development-standards and exhaustive-testing for all projects
3. **Agents**: Add python-313-conventions for Python projects
4. **Git Integration**: If using worktrees, install hooks and create_worktree.py

### Common Combinations

**Python Development**:
- Skills: development-standards, exhaustive-testing, dependency-management
- Agents: python-313-conventions, code-reviewer
- Hooks: Block direct pip usage, enforce uv

**Multi-feature Development**:
- Git: Worktree orchestration with create_worktree.py
- Skills: git-workflow for commit standards
- Hooks: Branch protection, context injection

**Team Quality Standards**:
- Skills: development-standards (no emoji!), exhaustive-testing
- Agents: code-reviewer (11-dimension review)
- Hooks: Require test passage before commits

## Contributing

These patterns are extracted from real production usage. When contributing:

1. Ensure patterns are production-tested
2. Include clear documentation with examples
3. Provide both benefits and trade-offs
4. Add diagrams for complex workflows
5. Follow development-standards (no emoji, modern features, thorough docs)

## License

This project is intended for educational and reference purposes.

## Summary

This repository demonstrates advanced Claude Code integration patterns that go beyond basic code generation:

- **Hooks** enable event-driven workflow automation
- **Agents** provide autonomous task execution with fresh eyes
- **Skills** capture specialized knowledge and standards
- **Git integration** enforces quality gates and enables parallel development

Combined, these patterns create a powerful framework for AI-assisted development that maintains high quality standards while maximizing productivity.
