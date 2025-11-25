# Greenfield vs Retrofit: Side-by-Side Comparison

**What it Shows**:
The structural differences between a clean worktree setup (greenfield) and one example of retrofitting an existing repository. The retrofit example uses an unusual `.myproject-shared/` pattern for symlinked files.

**Enterprise Recommendation**: For most teams, re-cloning as a bare repo (greenfield) is the sensible choice. Only retrofit if re-cloning is genuinely not feasible.

**Diagram** (max 120 characters wide):

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

**Key Differences**:

| Aspect                  | Greenfield                    | Retrofit                         |
|-------------------------|-------------------------------|----------------------------------|
| **Repository Type**     | Bare repo from start          | Converted from normal repo       |
| **Main Worktree**       | `main/` (clean name)          | `myproject/` (original name)     |
| **Config Location**     | `.claude/` (in each worktree) | `.myproject-shared/` (separate)  |
| **Config Sharing**      | Git (committed files)         | Symlinks (gitignored files)      |
| **Setup Complexity**    | Low - straightforward         | High - requires symlink setup    |
| **Worktree Pattern**    | `/<name>/` (any subfolder)    | `/.myproject-wt/` (project-specific) |
| **Directory Count**     | 2-3 levels                    | 3-4 levels with shared dirs      |
| **Symlink Management**  | None needed                   | Required for every worktree      |
| **Version Control**     | `.claude/` committed          | `.claude/` gitignored            |
| **Mental Model**        | Simple - files where expected | Complex - indirection via symlinks |
| **Team Onboarding**     | Clone, add worktree, done     | Clone, convert, symlink, done    |
| **Maintenance**         | Minimal                       | Symlink breakage possible        |

**When to Choose Each**:

**Choose Greenfield If**:
- Starting a new project
- Can reorganize repository structure
- Want simplest possible setup
- Prefer git-native configuration sharing
- Team values ease of onboarding

**Choose Retrofit If** (rare cases only):
- Re-cloning is genuinely not feasible
- Development environment setup is undocumented and cannot be reconstructed
- Critical tooling hard-depends on specific paths and cannot be updated
- Legal/compliance constraints prevent repository reorganization

**Better Alternative**:
For most existing repositories, **re-clone as a bare repo** rather than retrofit. This gives you the greenfield structure with:
- No symlink complexity
- Git-native configuration sharing
- Easier team onboarding
- Lower long-term maintenance

The time investment for re-cloning (hours to days) is usually less than the ongoing cost of maintaining a complex retrofit.

**Migration Path**:
If you started with retrofit and want to migrate to greenfield:
1. Commit `.claude/` configuration to git
2. Remove `.myproject-shared/` directory
3. Update worktrees to use git-tracked config
4. Remove symlinks (files now come from git)
5. Optionally reorganize to bare repo structure

**Best Practice**:
**Re-clone as bare repo** for both new projects and existing repositories. Only retrofit when re-cloning is truly impossible.
