# Worktree Setup Patterns: Greenfield vs Retrofit

This guide shows two approaches for setting up git worktrees with Claude Code integration: starting fresh (greenfield) and adapting existing repositories (retrofit).

---

## Greenfield: Starting Fresh (Recommended)

**When to use**: New projects, or when you can reorganize your repository structure.

### Visual Structure

```
<project-root>/                         # Bare git repository
│
├── HEAD                                # Bare repo metadata
├── config
├── refs/
├── objects/
├── hooks/
│   ├── pre-commit                      # Worktree protection hooks
│   └── post-checkout
│
├── main/                               # Main worktree (reference branch)
│   ├── .git                            # → points to ../worktrees/main
│   │
│   ├── src/                            # Project source code
│   │   ├── components/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── tests/
│   │
│   ├── docs/                           # Committed documentation
│   │
│   ├── .claude/                        # Claude Code configuration (committed)
│   │   ├── settings.local.json        # Project-specific settings
│   │   ├── skills/                     # Project skills (committed)
│   │   │   ├── git-workflow/
│   │   │   │   └── skill.md
│   │   │   └── deployment/
│   │   │       └── skill.md
│   │   └── agents/                     # Project agents (committed)
│   │       ├── code-reviewer.md
│   │       └── test-generator.md
│   │
│   ├── .planning/                      # Development plans (gitignored, optional)
│   │   └── feature-x-plan.md
│   │
│   ├── .scratch/                       # Temporary work files (gitignored, optional)
│   │   └── notes.md
│   │
│   ├── CLAUDE.md                       # Technical docs for Claude Code (committed)
│   ├── pyproject.toml
│   ├── .gitignore
│   └── README.md
│
├── feature-x/                          # Feature worktree
│   ├── .git                            # → points to ../worktrees/feature-x
│   ├── src/
│   ├── tests/
│   ├── .claude/                        # Same as main (from git)
│   ├── .planning/                      # Worktree-specific (gitignored)
│   ├── .scratch/                       # Worktree-specific (gitignored)
│   ├── CLAUDE.md                       # Same as main (from git)
│   └── ...
│
├── bugfix-y/                           # Another feature worktree
│   ├── .git                            # → points to ../worktrees/bugfix-y
│   ├── src/
│   └── ...
│
└── worktrees/                          # Git worktree metadata
    ├── main/
    ├── feature-x/
    └── bugfix-y/
```

**User-Level Configuration** (outside repository):
```
~/.claude/                              # Global Claude Code config
├── skills/                             # User skills (all projects)
│   ├── my-personal-skill/
│   └── code-style-checker/
└── agents/                             # User agents (all projects)
    └── personal-reviewer.md
```

### Key Benefits

1. **Simplicity**: No symlinks needed - configuration comes from git
2. **Version Control**: `.claude/` configuration tracked with your code
3. **Easy Onboarding**: `git clone`, `git worktree add`, done
4. **Git-Native Sharing**: Committed files shared automatically across worktrees
5. **Low Maintenance**: Fewer moving parts, less to break

### Setup Steps

```bash
# Initialize bare repo
git init --bare myproject
cd myproject

# Create main worktree
git worktree add main -b main
cd main

# Set up project structure
mkdir -p .claude/skills .claude/agents
# Add your skills, agents, configuration
git add .
git commit -m "Initial commit with worktree structure"

# Create feature worktrees as needed
cd ..
git worktree add feature-x -b feature-x
```

### Configuration Locations

- **Project skills**: `.claude/skills/` (committed)
- **Project agents**: `.claude/agents/` (committed)
- **Project settings**: `.claude/settings.local.json` (committed)
- **User skills**: `~/.claude/skills/` (global, outside repo)
- **User agents**: `~/.claude/agents/` (global, outside repo)

### Alternative: Keep Project Config Out of Git

If you don't want to commit project-specific skills/agents but still want to share them across worktrees:

**Option 1**: Use `.git/info/exclude` instead of `.gitignore`

```bash
# Add specific paths to git's exclude file (per-repo, not committed)
echo ".claude/skills/my-experimental-skill/" >> .git/info/exclude
echo ".claude/agents/work-in-progress.md" >> .git/info/exclude
```

This keeps files out of git without adding them to `.gitignore` (which would be committed and affect all developers).

**Option 2**: Use user-level skills/agents in `~/.claude/` instead of project-level.

---

## Retrofit: Adapting Existing Repos

**Enterprise Recommendation**: For most teams adopting Claude Code, **re-cloning your repository as a bare repo** (greenfield approach) is the most sensible option. Only retrofit if re-cloning is truly not feasible.

**When to retrofit**: Only when re-cloning is not possible due to:
- Idiosyncratic, undocumented development environment setup
- Legacy tooling hardcoded to specific paths that cannot be updated
- Other constraints that make reorganization impossible

### Example: One Retrofit Approach

The example below shows **one way** a project called "DocImp" was retrofitted. This approach uses a `.docimp-shared/` directory for symlinked files - **this pattern is unusual and not necessarily the best approach**, but it illustrates the complexity of retrofitting:

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

### Why More Complex

1. **Preserves existing structure**: Can't reorganize without breaking workflows
2. **Symlink-based sharing**: Configuration not committed, so symlinks provide sharing
3. **Project-specific paths**: Pattern uses project name (`.docimp-wt/` not generic)
4. **More setup**: Each worktree needs symlinks configured

### Important: Consider Re-cloning First

**Before retrofitting**, seriously consider re-cloning your repository as a bare repo (greenfield approach). This is usually:
- **Simpler**: No symlink complexity
- **More maintainable**: Git-native configuration sharing
- **Better for teams**: Easier onboarding, clearer structure
- **Lower risk long-term**: Fewer things to break

### When Retrofit Makes Sense

Only retrofit if re-cloning is genuinely not feasible:
- Development environment setup is undocumented and idiosyncratic
- Critical tooling hardcoded to specific paths that cannot be changed
- Legal/compliance constraints on repository reorganization
- Team genuinely cannot afford any setup disruption

### Retrofit Tradeoffs

**Advantages:**
- Preserves existing directory structure and workflows
- Can keep application state directories (like `.docimp/`)
- More flexible about what's committed vs gitignored
- Familiar structure for existing team members

**Disadvantages:**
- More complex mental model (symlink indirection)
- Higher setup overhead (symlinks for each worktree)
- More maintenance (symlinks can break)
- Not git-native (configuration sharing via filesystem)

---

## Side-by-Side Comparison

```
GREENFIELD (Recommended)                    RETROFIT (Existing Repos)
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

<project-root>/  (bare repo)                <project-root>/
│                                           │
├── main/                                   ├── myproject/            (original repo location)
│   ├── .git →                              │   ├── .git/
│   ├── src/                                │   ├── src/              (existing code structure)
│   ├── tests/                              │   ├── tests/
│   ├── .claude/                            │   ├── .myproject/       (app state, gitignored)
│   │   ├── settings.local.json            │   │   └── state/.git    (side-car git)
│   │   ├── skills/  (committed)           │   ├── CLAUDE.md →       (symlinked)
│   │   └── agents/  (committed)           │   ├── .planning →       (symlinked)
│   ├── .planning/   (gitignored)          │   ├── .scratch →        (symlinked)
│   ├── .scratch/    (gitignored)          │   └── .claude/ →        (symlinked)
│   ├── CLAUDE.md    (committed)           │
│   └── README.md                           ├── .myproject-shared/   (shared config directory)
│                                           │   ├── CLAUDE.md         (actual location)
├── feature-x/                              │   ├── .planning/        (actual location)
│   ├── .git →                              │   ├── .scratch/         (actual location)
│   ├── src/         (from git)            │   └── .claude/          (actual location)
│   ├── .claude/     (from git)            │       ├── settings.local.json
│   ├── .planning/   (worktree-specific)   │       ├── skills/
│   ├── .scratch/    (worktree-specific)   │       └── agents/
│   └── CLAUDE.md    (from git)            │
│                                           ├── .myproject-wt/        (worktrees directory)
├── bugfix-y/                               │   ├── issue-123/
│   └── ...                                 │   │   ├── .git →
│                                           │   │   ├── src/          (from git)
└── worktrees/       (git metadata)        │   │   ├── CLAUDE.md →   (symlinked)
    ├── main/                               │   │   ├── .planning →   (symlinked)
    ├── feature-x/                          │   │   └── .claude/ →    (symlinked)
    └── bugfix-y/                           │   │
                                            │   └── issue-456/
                                            │       └── ...
                                            │
                                            └── worktrees/            (git metadata)
```

### Quick Comparison Table

| Aspect                  | Greenfield                    | Retrofit                         |
|-------------------------|-------------------------------|----------------------------------|
| **Setup Complexity**    | Low - straightforward         | High - requires symlink setup    |
| **Config Location**     | `.claude/` in each worktree   | `.project-shared/` separate dir  |
| **Config Sharing**      | Git (committed files)         | Symlinks (gitignored files)      |
| **Symlink Management**  | None needed                   | Required for every worktree      |
| **Version Control**     | `.claude/` committed          | `.claude/` gitignored            |
| **Mental Model**        | Simple - files where expected | Complex - indirection            |
| **Team Onboarding**     | Clone, add worktree, done     | Clone, convert, symlink, done    |
| **Maintenance**         | Minimal                       | Symlink breakage possible        |
| **Migration Cost**      | N/A (new project)             | High (requires conversion)       |

---

## Migration Path: Retrofit → Greenfield

Retrofit patterns can be migrated to greenfield structure over time:

1. **Commit configuration**: Move `.project-shared/.claude/` contents to main worktree `.claude/`, commit to git
2. **Update worktrees**: Pull latest to get committed `.claude/` configuration
3. **Remove symlinks**: Delete symlinks in each worktree (files now come from git)
4. **Remove shared directory**: Delete `.project-shared/` (no longer needed)
5. **Update tooling**: Update scripts/docs that reference old paths
6. **Optional**: Reorganize to bare repo structure if desired

This migration can be done incrementally and doesn't require a full repository reorganization.

---

## Recommendation

**For enterprise Claude Code adoption**:

1. **New projects**: Always use greenfield approach
2. **Existing projects**: Re-clone as bare repo (effectively greenfield)
3. **Only if re-cloning impossible**: Use retrofit patterns

**The vast majority of teams should re-clone rather than retrofit.** The time spent on a clean re-clone (hours to a few days) is usually less than the long-term maintenance cost of a complex retrofit with symlinks.

Retrofit only makes sense when:
- Development environment setup is truly undocumented and cannot be reconstructed
- Critical infrastructure hard-depends on specific paths
- Team has no ability to handle any repository reorganization

The greenfield pattern is not just ideal - it's the practical choice for almost all situations.

---

## Notes

**About this repository's structure**: This repository uses a special documentation pattern where actual code lives in `actual-code/` with symlinks from `.claude/`. This makes the code more accessible for documentation purposes. **This is not part of either greenfield or retrofit patterns** - it's specific to this repository's role as a documentation/teaching resource.

**User vs Project configuration**: Remember that Claude Code supports both:
- **User-level** (`~/.claude/`): Personal preferences, skills/agents used across all projects
- **Project-level** (`.claude/` in repo): Team-shared skills/agents, project-specific settings

Choose the appropriate level based on whether configuration should be personal or shared with your team.
