# Greenfield vs. Retrofit Approach

## What's Documented Here

This repository documents a **retrofit pattern** - adding worktree orchestration to an existing repository (DocImp). The `.shared/` directory with symlinks was the practical solution for an established codebase.

## Greenfield Approach (Not Implemented)

If starting fresh, I would:

1. **Initialize as bare repo from start** - Avoid retrofit complexity
2. **Structure `.shared/` in initial commit** - Bake it into the design
3. **Template worktrees from script** - No manual conversion needed
4. **Simplified symlink strategy** - Fewer indirections
5. **Document in CONTRIBUTING.md** - Clear onboarding

## Why Show the Retrofit?

**Most real teams are retrofitting, not starting fresh.** This pattern shows practical adaptation to existing codebases, which is more valuable than theoretical optimization.

The retrofit approach is battle-tested on 17K+ lines of production code. The greenfield approach is architectural idealization.

## Key Differences

| Aspect | Retrofit (Documented) | Greenfield (Ideal) |
|--------|---------------------|-------------------|
| `.shared/` creation | Manual post-setup | Initial commit |
| Symlink complexity | Moderate | Lower |
| Learning curve | Steeper | Gentler |
| Production tested | Yes (DocImp) | No |
| Migration cost | High | N/A |