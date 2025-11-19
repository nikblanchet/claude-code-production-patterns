# Repository Worktree and Symlink Structure

**What it Represents**:
The physical file system layout of the DocImp repository, showing how worktrees, symlinks, and shared configuration enable multi-branch development with consistent Claude Code settings.

**Diagram**:

```
/Users/nik/Documents/Code/Polygot/
│
├── docimp/                                    # Main worktree
│   ├── .git/                                  # Git repository
│   │
│   ├── analyzer/                              # Python analysis engine
│   │   ├── src/
│   │   │   ├── parsers/                       # AST parsers
│   │   │   ├── utils/                         # State managers
│   │   │   └── main.py                        # CLI entry point
│   │   └── tests/
│   │
│   ├── cli/                                   # TypeScript CLI
│   │   ├── src/
│   │   │   ├── commands/                      # Command implementations
│   │   │   ├── utils/                         # StateManager, PythonBridge
│   │   │   └── index.ts                       # Entry point
│   │   └── __tests__/
│   │
│   ├── plugins/                               # JavaScript validation plugins
│   │   ├── validate-types.js                  # JSDoc type checking
│   │   └── jsdoc-style.js                     # Style enforcement
│   │
│   ├── docs/                                  # Committed documentation
│   │   └── patterns/                          # Architecture docs
│   │
│   ├── .docimp/                               # State directory (gitignored)
│   │   ├── session-reports/                   # Session JSON files
│   │   ├── workflow-state.json                # Command execution tracking
│   │   ├── history/                           # Workflow state snapshots
│   │   └── state/.git/                        # Side-car Git for transactions
│   │
│   ├── CLAUDE.md ─────────────────┐           # Symlinks to shared config
│   ├── CLAUDE_CONTEXT.md ─────────┤
│   ├── WARP.md ───────────────────┤
│   ├── .planning ─────────────────┤
│   ├── .scratch ──────────────────┤
│   │                              │
│   └── .claude/                   │
│       ├── settings.local.json ───┤
│       ├── skills ────────────────┤
│       └── agents ────────────────┤
│                                  │
├── .docimp-shared/                │           # Shared config (gitignored)
│   │                              │
│   ├── CLAUDE.md ←────────────────┘           # Technical docs for Claude Code
│   ├── CLAUDE_CONTEXT.md                      # User workflow preferences
│   │
│   ├── .planning/                             # Development plans
│   │   ├── PLAN.md                            # 31-step execution plan
│   │   ├── workflow-state-master-plan.md      # Phase tracking
│   │   ├── development-workflow.md            # Claude Code workflow
│   │   └── ARCHITECTURE_DIAGRAMS.md           # This file
│   │
│   ├── .scratch/                              # Temporary work files
│   │   ├── pr-391-summary.md
│   │   └── code-review-*.md
│   │
│   └── .claude/
│       ├── settings.local.json                # Claude Code settings
│       ├── skills/
│       │   └── git-workflow ──────────────┐   # Symlink to external skill
│       └── agents/                        │
│                                          │
├── .docimp-wt/                              │   # Additional worktrees
│   ├── issue-293/                           │   # Feature branch worktrees
│   ├── issue-300/                           │
│   └── ...                                  │
│                                            │
└── /Users/nik/Code/Polygot/docimp           │   # Alternate worktree path
                                             │
                                             │
/Users/nik/Code/repos/custom-claude-skills/  │   # External skills repository
└── project-scope/docimp/                    │
    └── git-workflow/ ───────────────────────┘   # Source of git-workflow skill
```

**Key Concepts**:

**Worktree Structure**:
- **Main worktree**: `/Users/nik/Documents/Code/Polygot/docimp/` - primary development location
- **Additional worktrees**: `.docimp-wt/issue-*/` - parallel development on different branches
- **Alternate path**: `/Users/nik/Code/Polygot/docimp` - same repo, different filesystem location

**Symlink Patterns**:
- **CLAUDE.md**: Technical documentation for Claude Code (40k char limit) - symlinked to shared location
- **WARP.md**: Alias to CLAUDE.md for Warp terminal integration
- **CLAUDE_CONTEXT.md**: User workflow preferences (gitignored) - shared across worktrees
- **.planning/**: Development plans and progress tracking - shared to maintain consistency
- **.scratch/**: Temporary work files, code reviews - shared for cross-worktree access
- **.claude/skills**: Custom Claude Code skills - pulled from external repository
- **.claude/settings.local.json**: User-specific Claude Code settings - shared for consistent behavior

**State Directory (.docimp/)**:
- **session-reports/**: JSON files for audit/improve sessions
- **workflow-state.json**: Command execution tracking (timestamps, checksums)
- **history/**: Timestamped snapshots for debugging and recovery
- **state/.git/**: Side-car Git repository for transaction tracking (never touches main `.git/`)

**External Integrations**:
- **git-workflow skill**: Symlinked from `/Users/nik/Code/repos/custom-claude-skills/project-scope/docimp/git-workflow`
- Provides standardized Git commands for worktree management, branch operations, PR creation

**Benefits**:
1. **Consistent Configuration**: Same CLAUDE.md, skills, and settings across all worktrees
2. **Parallel Development**: Work on multiple branches simultaneously with shared context
3. **Settings Isolation**: User preferences (gitignored) separate from project code
4. **Reusable Skills**: Custom Claude Code skills shared across projects
5. **Centralized Planning**: Single source of truth for development plans and progress

**File Sharing Strategy**:
- **Committed files** (docs/, README.md): In main repo, shared via Git
- **Gitignored config** (CLAUDE.md, .planning/): In `.docimp-shared/`, shared via symlinks
- **User preferences** (settings.local.json): Absolute path symlinks for cross-worktree consistency
- **External skills**: Relative symlinks to custom skills repository
