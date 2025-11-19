# Infrastructure Documentation: Planning & Documentation

## Overview

DocImp uses a **structured planning system** to manage complex, multi-phase development with Claude Code. This system enables:

- **Session atomicity** - Each Claude Code instance completes a specific deliverable
- **Progress tracking** - Checkboxes preserve progress across sessions
- **Contract-based development** - Clear inputs, outputs, and rollback plans
- **Progressive context** - Build complexity incrementally

**Key Planning Files:**
- **PLAN.md** (gitignored) - 31-step execution plan with progress tracking
- **development-workflow.md** - Claude Code methodology documentation
- **workflow-state-master-plan.md** - Detailed workflow state implementation plan
- **ARCHITECTURE_DIAGRAMS.md** - Visual architecture diagrams

---

## 1. PLAN.md Structure

### Purpose

**PLAN.md is a gitignored working document** that tracks the complete development plan with granular checkboxes for each substep.

**Key Characteristics:**
- **Gitignored** - Not committed to version control (personal working document)
- **Checkbox-based** - Track completion at substep granularity
- **Session-resumable** - Next Claude Code instance sees exact progress
- **51KB detailed** - Comprehensive plan with 31 steps

### Structure

**PLAN.md Format:**

```markdown
# DocImp Implementation Plan

## Overview

31-step execution plan with 16 Claude Code instances.
Estimated 37-42 hours total (27-31 hours code, 10-11 hours manual).

---

## Phase 1: Core Infrastructure (Steps 1-8)

### Step 1: Project Setup & Base Architecture
**Instance**: 1 | **Status**: Complete | **Time**: 2-3 hours

Deliverables:
- [X] Initialize Python project with pyproject.toml
- [X] Create BaseParser abstract class
- [X] Implement PythonParser using AST
- [X] Create test file structure
- [X] Add pytest configuration
- [X] Verify tests pass

**Rollback**: Delete analyzer/ directory

---

### Step 2: TypeScript Parser Implementation
**Instance**: 2 | **Status**: Complete | **Time**: 3-4 hours

Deliverables:
- [X] Create TypeScriptParser class
- [X] Integrate TypeScript compiler API
- [X] Handle CommonJS and ESM module systems
- [X] Detect export types (named, default, commonjs)
- [X] Add comprehensive tests
- [X] Verify JSDoc extraction works

**Rollback**: Revert to Step 1 commit

---

### Step 3: Impact Scoring Algorithm
**Instance**: 3 | **Status**: Complete | **Time**: 2 hours

Deliverables:
- [X] Implement ImpactScorer class
- [X] Calculate complexity-based scores (0-100)
- [X] Add audit rating integration
- [X] Verify monotonicity (higher complexity → higher score)
- [ ] Performance benchmark (<100ms for 1000 items)

**Rollback**: Revert ImpactScorer, use simple complexity*5

---

## Phase 2: CLI & Workflow (Steps 9-16)

### Step 9: TypeScript CLI Foundation
**Instance**: 4 | **Status**: In Progress | **Time**: 3-4 hours

Deliverables:
- [X] Setup TypeScript project with tsconfig.json
- [X] Implement Commander.js CLI framework
- [X] Create PythonBridge for subprocess communication
- [ ] Add analyze command
- [ ] Add tests for CLI parsing
- [ ] Verify end-to-end workflow

**Rollback**: Delete cli/ directory, use Python CLI only

---

[... 22 more steps ...]

---

## Checkpoint Tracking

| Phase | Steps | Completed | Remaining | Status |
|-------|-------|-----------|-----------|--------|
| Phase 1: Core | 1-8 | 8 | 0 | ✓ Complete |
| Phase 2: CLI | 9-16 | 7 | 1 | In Progress |
| Phase 3: Advanced | 17-24 | 0 | 8 | Not Started |
| Phase 4: Polish | 25-31 | 0 | 7 | Not Started |

**Overall Progress**: 15/31 steps (48%)
```

### Tracking Guidelines

**CRITICAL: Update checkboxes as you complete substeps, not at the end.**

**Process:**

1. **Mark immediately** after completing each substep
2. **Don't batch** updates at end of step
3. **Use simple `[X]` notation** - no "COMPLETE:" prefixes
4. **Preserve context** if session ends mid-step

**Example Workflow:**

```markdown
# Start of step - all unchecked
- [ ] Create BaseParser abstract class
- [ ] Implement PythonParser using AST
- [ ] Create test file

# After creating BaseParser
- [X] Create BaseParser abstract class  ← Mark immediately
- [ ] Implement PythonParser using AST
- [ ] Create test file

# After implementing PythonParser
- [X] Create BaseParser abstract class
- [X] Implement PythonParser using AST  ← Mark immediately
- [ ] Create test file
```

**Why This Matters:**

If a Claude Code session ends mid-step (timeout, error, context limit), the next instance can:
1. Read PLAN.md
2. See exactly what was completed
3. Resume from last unchecked item
4. Continue without redoing work

### Step Structure

**Each step includes:**

1. **Metadata**
   - Instance number
   - Status (Not Started, In Progress, Complete)
   - Estimated time

2. **Deliverables**
   - Granular checkboxes for each substep
   - Clear completion criteria
   - Links to files/tests

3. **Rollback Plan**
   - How to undo changes if step fails
   - Minimum viable fallback state

4. **Dependencies**
   - Which prior steps must be complete
   - Which files/systems are required

### Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| Not Started | No work done yet | Read step, plan approach |
| In Progress | Some deliverables checked | Complete remaining checkboxes |
| Complete | All deliverables checked | Move to next step |
| Blocked | Waiting on external dependency | Document blocker, skip for now |

---

## 2. Development Workflow Documentation

### File: development-workflow.md

**Location:** `.planning/development-workflow.md`

**Purpose:** Explains the Claude Code methodology used to build DocImp.

**Contents:**

```markdown
# Development Workflow

This project is being built using **Claude Code** (claude.ai/code) with:
- **Session atomicity**: Each instance completes a specific deliverable
- **Contract-based development**: Clear inputs, outputs, rollback plans
- **Progressive context**: Build complexity incrementally
- **Test-first validation**: Validate at each step

See `PLAN.md` for the complete 31-step execution plan with 16 Claude Code instances.

## Tracking Progress in PLAN.md

**CRITICAL: Update PLAN.md checkboxes as you complete substeps, not at the end.**

**PLAN.md is gitignored** - it's a working document for tracking progress, not
part of the public repository.

### Process

1. When you complete a substep, immediately mark it as `[X]` in PLAN.md
2. Mark checkboxes as you go, not in batch at the end of a step
3. This preserves progress if context is lost mid-step
4. Use simple `[X]` notation - do NOT add "COMPLETE:" or other prefixes
```

### Key Principles

**1. Session Atomicity**

Each Claude Code instance completes a **well-defined deliverable**:
- Not too small (avoid context thrashing)
- Not too large (avoid incomplete sessions)
- Clear success criteria

**Example:**
- ✓ Good: "Implement TypeScript parser with module system detection (3-4 hours)"
- ✗ Too small: "Add one function to parser (10 minutes)"
- ✗ Too large: "Implement entire CLI layer (10+ hours)"

**2. Contract-Based Development**

Each step has an explicit contract:
- **Inputs**: What exists before step starts
- **Outputs**: What will exist after step completes
- **Rollback**: How to undo if step fails

**Example:**

```markdown
### Step 5: Docstring Writer
**Instance**: 3

**Inputs**:
- Parsers exist (Step 1-2)
- CodeItem model defined (Step 3)
- Test infrastructure ready (Step 1)

**Outputs**:
- DocstringWriter class with write_docstring() method
- Backup file creation (.bak files)
- Idempotent writes (no duplicate docstrings)
- 15+ tests covering edge cases

**Rollback**:
- Delete analyzer/src/writer/docstring_writer.py
- Remove import from analyzer/src/main.py
- Revert to manual docstring insertion
```

**3. Progressive Context**

Build complexity incrementally:
- Start with simple, isolated components
- Add integrations only after components work
- Test each layer before adding next

**Example Progression:**

```
Phase 1: Isolated Components
├─ Step 1: PythonParser (standalone)
├─ Step 2: TypeScriptParser (standalone)
└─ Step 3: ImpactScorer (standalone)

Phase 2: Integration
├─ Step 4: DocumentationAnalyzer (uses parsers + scorer)
└─ Step 5: CLI (uses analyzer)

Phase 3: Advanced Features
├─ Step 6: Session Resume (adds to CLI)
└─ Step 7: Transaction System (adds to CLI)
```

**4. Test-First Validation**

Validate at each step:
- Write tests before or during implementation
- Verify tests pass before marking step complete
- Add integration tests after each phase

---

## 3. Specialized Planning Documents

### workflow-state-master-plan.md

**Purpose:** Detailed implementation plan for workflow state tracking feature (Phase 3.6-3.14).

**Structure:**

```markdown
# Workflow State Management Master Plan

## Overview
Comprehensive plan for workflow state tracking, schema versioning, and
incremental analysis features.

## Phases
- Phase 3.6: Enhanced --apply-audit Edge Cases (Issue #370)
- Phase 3.7: Schema Migration Utilities (Issue #375)
- Phase 3.8: --dry-run Flag (Issue #376)
- Phase 3.9: File-Level Checksum Staleness (PR #387)
- Phase 3.10: docimp status Command (Issue #374)
- Phase 3.11: Cross-Command Integration Tests (PR #391)
- Phase 3.12: Documentation Updates (PR #392)
- Phase 3.13: (Future) Workflow History Export/Import
- Phase 3.14: Workflow History Management

## Phase 3.7: Schema Migration Utilities (Issue #375)

### Substeps
- [X] Design migration registry pattern
- [X] Implement buildMigrationPath()
- [X] Implement applyMigrations()
- [X] Add migration_log tracking
- [X] Create migrate-workflow-state command
- [X] Add --dry-run, --check, --version, --force flags
- [X] Write 42 tests (15 TS + 15 Python + 12 command)
- [X] Update documentation

### Files Modified
- cli/src/types/workflow-state-migrations.ts (new)
- analyzer/src/models/workflow_state_migrations.py (new)
- cli/src/commands/migrate-workflow-state.ts (new)

### Testing
- Unit: Migration function behavior
- Integration: Auto-migration on load
- Command: CLI flag handling
```

**Use Case:** When implementing a complex feature spanning multiple sub-issues, create a specialized plan to track substeps.

### ARCHITECTURE_DIAGRAMS.md

**Purpose:** Visual diagrams of system architecture.

**Contents:**

```markdown
# Architecture Diagrams

## Three-Layer Polyglot Architecture

```
┌────────────────────────────────────────────────┐
│         TypeScript CLI Layer                   │
│  Commander, ConfigLoader, PluginManager        │
│  PythonBridge, TerminalDisplay                 │
└──────────────┬─────────────────────────────────┘
               │ JSON subprocess communication
               v
┌────────────────────────────────────────────────┐
│         Python Analysis Engine                 │
│  Parsers, ImpactScorer, Analyzer               │
│  ClaudeClient, DocstringWriter                 │
└──────────────┬─────────────────────────────────┘
               │
               v
┌────────────────────────────────────────────────┐
│    JavaScript Config & Plugins                 │
│  docimp.config.js, validation plugins          │
└────────────────────────────────────────────────┘
```

## Data Flow: Analyze Command

[... more diagrams ...]
```

**Use Case:** Visual reference for understanding system architecture.

---

## 4. Planning Directory Structure

**Location:** `.planning/` (gitignored)

**Structure:**

```
.planning/
├── PLAN.md                          # Main execution plan (gitignored)
├── development-workflow.md          # Methodology documentation
├── workflow-state-master-plan.md    # Feature-specific plan
├── ARCHITECTURE_DIAGRAMS.md         # Visual architecture
├── INFRASTRUCTURE-DOCS_*.md         # Detailed infrastructure docs
└── INFRASTRUCTURE-README.md         # Index/navigation

(Note: INFRASTRUCTURE_BEST_EXAMPLES.md relocated to bonus/ directory for visibility)
```

**Why Gitignored?**

- **Personal working documents** - Different developers have different planning styles
- **Progress tracking** - Checkboxes are individual progress, not team state
- **Avoid conflicts** - Multiple developers shouldn't merge PLAN.md changes
- **Noise reduction** - Frequent checkbox updates clutter git history

**What's NOT Gitignored?**

- `development-workflow.md` - Methodology applies to all contributors
- Architecture diagrams - Shared understanding of system design
- Infrastructure docs - Onboarding documentation

---

## 5. Planning Workflow

### Starting a New Phase

**1. Read PLAN.md**

```bash
vim .planning/PLAN.md
# Navigate to current phase
# Review deliverables and dependencies
```

**2. Identify Current Step**

```markdown
### Step 9: TypeScript CLI Foundation
**Instance**: 4 | **Status**: In Progress | **Time**: 3-4 hours

Deliverables:
- [X] Setup TypeScript project with tsconfig.json
- [X] Implement Commander.js CLI framework
- [X] Create PythonBridge for subprocess communication
- [ ] Add analyze command  ← START HERE
- [ ] Add tests for CLI parsing
- [ ] Verify end-to-end workflow
```

**3. Work on Substep**

```bash
# Implement "Add analyze command"
vim cli/src/commands/analyze.ts
# ... implementation ...

# Test
cd cli && npm test
```

**4. Mark Complete Immediately**

```markdown
- [X] Add analyze command  ← Mark as soon as tests pass
```

**5. Move to Next Substep**

Repeat steps 3-4 for each remaining substep.

### Completing a Step

**1. Verify All Deliverables Checked**

```markdown
Deliverables:
- [X] Setup TypeScript project with tsconfig.json
- [X] Implement Commander.js CLI framework
- [X] Create PythonBridge for subprocess communication
- [X] Add analyze command
- [X] Add tests for CLI parsing
- [X] Verify end-to-end workflow  ← All checked!
```

**2. Update Step Status**

```markdown
### Step 9: TypeScript CLI Foundation
**Instance**: 4 | **Status**: Complete | **Time**: 3-4 hours
```

**3. Create Git Commit**

```bash
git add .
git commit -m "Complete Step 9: TypeScript CLI Foundation"
git push
```

**4. Update Checkpoint Tracking**

```markdown
## Checkpoint Tracking

| Phase | Steps | Completed | Remaining | Status |
|-------|-------|-----------|-----------|--------|
| Phase 2: CLI | 9-16 | 8 | 0 | ✓ Complete |  ← Update
```

### Handling Blocked Steps

**When a step is blocked:**

```markdown
### Step 15: CI/CD Integration
**Instance**: 8 | **Status**: Blocked | **Time**: 2 hours

Deliverables:
- [ ] Create GitHub Actions workflow
- [ ] Add Python test job
- [ ] Add TypeScript test job

**Blocker**: Waiting for repository access to configure GitHub Actions secrets
**Workaround**: Skip for now, implement locally with secrets in .env file
**Unblock Date**: Expected by 2025-11-20
```

**Skip and revisit later:**

1. Mark step as "Blocked" with clear reason
2. Document workaround if available
3. Move to next non-blocked step
4. Revisit when blocker resolved

---

## 6. Integration with Claude Code

### Reading PLAN.md in Sessions

**Claude Code reads PLAN.md automatically** when:
- Session starts
- User mentions "check PLAN.md"
- Planning context needed

**Example prompt from user:**

```
Check PLAN.md and continue with the next unchecked substep.
```

**Claude Code response:**

```
I've read PLAN.md. Currently on Step 9: TypeScript CLI Foundation.

Next unchecked substep:
- [ ] Add analyze command

I'll now implement the analyze command in cli/src/commands/analyze.ts.
```

### Updating PLAN.md During Session

**Claude Code updates PLAN.md** by:
1. Reading current content
2. Modifying checkbox ([ ] → [X])
3. Writing updated content

**User confirmation:**

```
✓ Marked "Add analyze command" as complete in PLAN.md
```

### Session Handoff

**At end of session, Claude Code provides handoff:**

```
## Session Summary

**Completed:**
- [X] Add analyze command
- [X] Add tests for CLI parsing

**Remaining:**
- [ ] Verify end-to-end workflow

**Next Steps:**
1. Run full integration test: docimp analyze ./examples
2. Fix any issues found
3. Mark final substep complete
4. Update step status to "Complete"
```

**Next Claude Code instance reads PLAN.md and continues from remaining substep.**

---

## Quick Reference

### Planning File Locations

| File | Location | Purpose | Gitignored? |
|------|----------|---------|-------------|
| PLAN.md | `.planning/PLAN.md` | Main execution plan with checkboxes | Yes |
| development-workflow.md | `.planning/development-workflow.md` | Methodology documentation | No |
| workflow-state-master-plan.md | `.planning/workflow-state-master-plan.md` | Feature-specific plan | Yes |
| ARCHITECTURE_DIAGRAMS.md | `.planning/ARCHITECTURE_DIAGRAMS.md` | Visual diagrams | No |

### Checkbox Syntax

```markdown
- [ ] Unchecked (not started)
- [X] Checked (complete)
- [-] Skipped (intentionally skipped)
- [?] Uncertain (needs investigation)
```

**Note:** Use only `[ ]` and `[X]` in PLAN.md for consistency.

### Step Status Values

```markdown
**Status**: Not Started    # No deliverables checked
**Status**: In Progress    # Some deliverables checked
**Status**: Complete       # All deliverables checked
**Status**: Blocked        # Waiting on external dependency
```

---

## Troubleshooting

### Problem: PLAN.md and Codebase Out of Sync

**Symptoms:**
- Checkboxes marked complete
- Files mentioned in deliverables don't exist
- Tests failing

**Solution:**

1. **Review git history:**
   ```bash
   git log --oneline --all
   # Find last commit matching PLAN.md progress
   ```

2. **Identify discrepancy:**
   - Was step marked complete prematurely?
   - Were files deleted/moved?

3. **Sync PLAN.md to reality:**
   ```markdown
   - [X] Create BaseParser abstract class
   - [ ] Implement PythonParser using AST  ← Uncheck if not done
   - [ ] Create test file
   ```

4. **Resume from correct checkpoint**

### Problem: Lost PLAN.md Progress

**Symptoms:**
- PLAN.md file deleted
- All checkboxes unchecked after git operation

**Solution:**

1. **Check git reflog:**
   ```bash
   git reflog
   # Find commit where PLAN.md had progress
   ```

2. **Restore from backup:**
   ```bash
   # If using Time Machine or similar
   cp ~/.Trash/PLAN.md .planning/PLAN.md
   ```

3. **Reconstruct from git commits:**
   ```bash
   git log --oneline --all
   # Review commit messages
   # Manually check completed substeps in PLAN.md
   ```

4. **Prevention:**
   - Commit code frequently (preserves git history)
   - Use `git stash` instead of discarding changes

---

## Summary

DocImp's planning system enables **structured, resumable development** with Claude Code:

- **PLAN.md** - 31-step execution plan with granular checkboxes (gitignored)
- **development-workflow.md** - Claude Code methodology (committed)
- **workflow-state-master-plan.md** - Feature-specific plans (gitignored)
- **ARCHITECTURE_DIAGRAMS.md** - Visual architecture (committed)

**Key Benefits:**

- **Session resumable** - Next Claude Code instance sees exact progress
- **Contract-based** - Clear inputs, outputs, rollback plans
- **Progressive context** - Build complexity incrementally
- **Test-first** - Validate at each step

**Critical Practice:**

**Update PLAN.md checkboxes immediately after completing each substep, not at the end.**

**Next Steps**: See `INFRASTRUCTURE-DOCS_12-State-Configuration-Files.md` for .gitignore, .prettierignore, and other configuration files.
