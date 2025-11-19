# Claude Code Config Pattern: External Documentation Imports

## The 40KB Character Limit Challenge

**Constraint**: CLAUDE.md must stay under 40,000 characters

**Current size**: 27,792 bytes (27.8 KB) - 69.5% of limit used

**Check size**:
```bash
wc -c CLAUDE.md
# Output: 27792 CLAUDE.md
```

## The External Import Pattern

**Problem**: DocImp has complex architecture requiring extensive documentation. Inline documentation would exceed 40KB.

**Solution**: Use `@docs/patterns/*.md` imports for detailed explanations.

## CLAUDE.md Structure with Imports

```markdown
# CLAUDE.md

**Character Limit: 40.0k characters (absolute maximum) for CLAUDE.md specifically.**

## Commands

[Core commands documented inline: ~3KB]
docimp analyze ./src
docimp audit ./src
docimp plan ./src
docimp improve ./src

## Error Handling Architecture

**Three-layer pattern**: Core functions (throw) → Command wrappers (exit codes) → Entry point (process.exit)

- @docs/patterns/error-handling.md

## Dependency Injection Pattern

**Core Principle**: All dependencies passed as required parameters

- @docs/patterns/dependency-injection.md

## Transaction System Architecture

**Side-car Git repository** in `.docimp/state/.git` for rollback capability

- @docs/patterns/transaction-integration.md
```

## External Documentation Files

| File | Size | Purpose |
|------|------|---------|
| `error-handling.md` | 3.2 KB | Three-layer error pattern |
| `dependency-injection.md` | 4.1 KB | DI across Python/TypeScript |
| `testing-strategy.md` | 5.7 KB | Test organization |
| `transaction-integration.md` | 8.9 KB | Git-based rollback system |
| `session-resume.md` | 6.2 KB | Resume capability architecture |
| `workflow-state-management.md` | 12.4 KB | State tracking, schema versioning |
| **Total external** | **40.5 KB** | |

**Total Documentation**: 27.8KB (CLAUDE.md) + 40.5KB (external) = **68.3KB**

## How Auto-Loading Works

1. Claude Code reads CLAUDE.md on session start (27.8KB loaded)
2. When code mentions `@docs/patterns/error-handling.md`, Claude Code auto-loads it
3. Loaded content added to context window on-demand
4. Maximum import depth: 5 hops (prevents infinite loops)
