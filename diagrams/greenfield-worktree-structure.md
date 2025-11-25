# Greenfield Worktree Structure (Recommended)

**What it Represents**:
The clean, purpose-built structure for a repository initialized with bare repo + worktrees from the start. This is the recommended approach for new projects.

**Diagram**:

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

**Key Characteristics**:

**Clean Structure**:
- No `.shared/` directory needed - everything is in the right place from the start
- No complex symlink indirections
- `.claude/` configuration committed directly to git
- Simpler mental model for new team members

**Configuration Strategy**:
- **Project config** (`.claude/skills/`, `.claude/agents/`): Committed to git, shared via git itself
- **User config** (`~/.claude/`): Global, outside repository, personal preferences
- **Temporary files** (`.planning/`, `.scratch/`): Gitignored, per-worktree or shared as needed

**Worktree Isolation**:
- Each worktree is a separate directory under the bare repo root
- Worktrees share committed files via git (no symlinks needed)
- Worktrees can have independent `.planning/` and `.scratch/` directories if gitignored

**Benefits**:
1. **Simplicity**: No symlink management, configuration is where you expect it
2. **Git-native sharing**: Committed config shared via git's normal mechanisms
3. **Easy onboarding**: `git clone`, `git worktree add`, done
4. **Version control**: `.claude/` configuration is versioned with your code
5. **Lower maintenance**: Fewer moving parts, less to break

**Setup Process**:
```bash
# Initialize bare repo
git init --bare myproject
cd myproject

# Create main worktree
git worktree add main -b main

# Set up project structure in main
cd main
mkdir -p .claude/skills .claude/agents
# Add skills, agents, hooks
git add .
git commit -m "Initial commit with worktree structure"

# Create feature worktrees as needed
cd ..
git worktree add feature-x -b feature-x
```

**When to Use This Pattern**:
- Starting a new project
- Team wants Claude Code configuration versioned
- Prefer git-native sharing over symlinks
- Want the simplest possible setup
