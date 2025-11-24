# Retrofit Worktree Structure (Adapting Existing Repos)

**What it Represents**:
One example of adding worktree orchestration to an existing repository. This shows how DocImp (a production codebase) was retrofitted with worktrees. This approach is more complex than greenfield and uses an unusual pattern (`.myproject-shared/` for symlinked files) that worked for this specific case but may not be the best approach for all retrofits.

**Diagram**:

```
<project-root>/
│
├── docimp/                                    # Main worktree (existing repo converted)
│   ├── .git/                                  # Original git repository
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
│       ├── skills/ ───────────────┤
│       └── agents/ ───────────────┤
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
│   │   └── ARCHITECTURE_DIAGRAMS.md
│   │
│   ├── .scratch/                              # Temporary work files
│   │   ├── pr-391-summary.md
│   │   └── code-review-*.md
│   │
│   └── .claude/
│       ├── settings.local.json                # Claude Code settings
│       ├── skills/                            # Project skills
│       │   └── git-workflow/
│       └── agents/                            # Project agents
│           └── docimp-reviewer.md
│
├── .docimp-wt/                                # Additional worktrees
│   ├── issue-293/                             # Feature branch worktrees
│   │   ├── .git → ../../docimp/.git
│   │   ├── analyzer/
│   │   ├── cli/
│   │   ├── CLAUDE.md → ../../.docimp-shared/CLAUDE.md
│   │   ├── .planning → ../../.docimp-shared/.planning
│   │   └── .claude/ → ../../.docimp-shared/.claude/
│   │
│   ├── issue-300/
│   └── ...
│
└── <alternate-path>/docimp-wt-issue-305/      # Worktree in different location
    ├── .git → <project-root>/docimp/.git
    ├── CLAUDE.md → <project-root>/.docimp-shared/CLAUDE.md
    └── ...
```

**Key Characteristics**:

**Retrofit Complexity**:
- Main worktree keeps original structure (`docimp/` directory)
- Separate `.docimp-shared/` directory for cross-worktree config
- Extensive symlink network to share configuration
- Project-specific naming (`.docimp-wt/`, `.docimp-shared/`)

**Symlink Strategy**:
- **CLAUDE.md**: Technical documentation symlinked from `.docimp-shared/`
- **CLAUDE_CONTEXT.md**: User workflow preferences symlinked
- **WARP.md**: Alias to CLAUDE.md for Warp terminal integration
- **.planning/**, **.scratch/**: Shared directories symlinked to prevent duplication
- **.claude/**: Entire directory symlinked for consistent settings/skills/agents

**Why More Complex**:
1. **Preserving existing structure**: Can't move `docimp/` without breaking workflows
2. **Gitignored sharing**: Config not committed, so symlinks needed instead of git
3. **Project-specific paths**: Pattern uses project name (`.docimp-wt/` not generic)
4. **Application state**: `.docimp/` state directory with side-car git repo
5. **Multiple worktree locations**: Some in `.docimp-wt/`, some in alternate paths

**Tradeoffs**:
- **More flexible**: Can keep existing directory structure
- **More configuration**: Symlinks must be set up for each worktree
- **More maintenance**: Broken symlinks possible if shared dir moves
- **Not git-native**: Configuration sharing via filesystem, not version control

**Important Note About `.myproject-shared/` Pattern**:
This example uses a separate `.myproject-shared/` directory for symlinked files. **This pattern is unusual and not necessarily recommended.** It worked for DocImp's specific constraints but adds complexity. Most retrofits should consider re-cloning the repository instead (see below).

**When to Use This Pattern**:
- Only when re-cloning is not feasible
- Development environment setup is idiosyncratic and undocumented
- Critical tooling hardcoded to specific paths that cannot be changed
- Team cannot afford downtime for repository reorganization

**Better Alternative: Re-clone to Greenfield**:
For most enterprise adoptions of Claude Code, **re-cloning the repository as a bare repo** is the most sensible approach:
- Simpler structure with no symlink complexity
- Git-native configuration sharing
- Easier team onboarding
- Lower long-term maintenance

Only retrofit if something truly prevents re-cloning (e.g., undocumented dev environment setup, legacy tooling that cannot be updated).

**Migration Considerations** (if you must retrofit):
- Requires converting existing repo to bare repo (or moving it)
- Must create shared directory structure
- Must set up symlinks in each worktree
- May need to update tooling that hardcodes paths
- More setup overhead, but preserves working structure
