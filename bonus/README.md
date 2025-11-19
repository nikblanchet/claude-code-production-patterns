# Bonus Materials

This folder contains deep reference materials demonstrating advanced Claude Code usage patterns and production infrastructure automation.

## Contents

### SIMPLE-TIPS_Attention-chime.md

Practical implementation guide for audio notifications in Claude Code using the hook system. Shows how to play attention chimes when Claude Code needs input, useful for managing multiple instances.

### docimp_infrastructure/

Comprehensive infrastructure documentation (23 files, 78,813 words) for a production-grade polyglot development environment integrated with Claude Code.

**Start here:** `docimp_infrastructure/INFRASTRUCTURE-README.md`

**What's covered:**
- **Git worktree workflows** - Automated worktree creation, path-based branch protection, change transfer logic
- **Claude Code integration** - 265 permission rules, external documentation patterns to exceed CLAUDE.md limits, symlink architecture
- **Direnv tool interception** - Transparent command redirection, educational error blocking, per-worktree isolation
- **Quality enforcement** - Dual-layer (local + CI/CD) enforcement with ruff, mypy, pytest, ESLint, Prettier, Jest
- **CI/CD pipeline** - 5 GitHub Actions jobs with parallel execution
- **Development utilities** - Scripts, state management, maintenance procedures

**Best examples:** See `INFRASTRUCTURE_BEST_EXAMPLES.md` for the three most sophisticated components with implementation details.

## Purpose

These materials demonstrate production-ready patterns for teams using Claude Code at scale. Each document is a comprehensive reference—expect detailed implementation specifics, edge case handling, and maintenance procedures rather than high-level overviews.
