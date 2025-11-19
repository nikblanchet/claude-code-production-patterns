# User Skills

User skills are global skills available to Claude across all projects. They're stored in `~/.claude/skills/` and provide general development standards, workflows, and practices.

## Skills in This Collection

### access-skill-resources
**Purpose**: Navigate skill symlinks and locate bundled resources (scripts, references, assets).

**When to use**: When a skill mentions bundled resources but you can't immediately find them. Teaches standard skill directory structure and symlink navigation.

**Key concepts**:
- Standard skill structure: `scripts/`, `references/`, `assets/`
- Following symlinks transparently
- Locating resources in user vs project skills

---

### cli-ux-colorful
**Purpose**: Design colorful CLI output with ANSI colors, syntax highlighting, and terminal formatting.

**When to use**: When designing CLI output, formatting terminal messages, or building command-line interfaces.

**Key concepts**:
- Standard color conventions (red=error, yellow=warning, green=success, blue=info)
- Syntax highlighting for code excerpts
- Libraries: `rich` (Python), `chalk` (Node.js)
- Graceful degradation and NO_COLOR support
- ANSI colors are good, emoji presentation characters are not (see development-standards)

---

### dependency-management
**Purpose**: Philosophy for using dependencies freely rather than reinventing the wheel.

**When to use**: When adding dependencies, installing packages, or evaluating whether to use a library.

**Key concepts**:
- Default to using existing libraries over reimplementing
- For Python: Prefer conda over pip, maintain separate requirements files
- Evaluate quality with common sense (maintenance, docs, API design)
- Stay reasonably current with updates
- Coding is building with Legos, not creating from scratch

---

### development-standards
**Purpose**: Core standards enforced across all development work.

**When to use**: Always - applies to all code, commits, PRs, issues, and documentation.

**CRITICAL standards**:
1. **NO EMOJI** in developer-facing content (code/docs/PRs/issues/commits) or CLI output
   - Test: If it renders in color on a smartphone, don't use it
   - Signals "AI wrote this and a human didn't review"
   - Emoticons are fine: :) :( ^_^ ¯\_(ツ)_/¯

2. **Use modern language features** - Be an early adopter when features improve clarity

3. **Write thorough documentation** - Extensive docs are expected and valued

**Why this matters**: These standards maintain professionalism and code quality across projects.

---

### exhaustive-testing
**Purpose**: Comprehensive test coverage across multiple testing dimensions.

**When to use**: When writing tests, implementing features, or before creating pull requests.

**Key concepts**:
- Tests are not optional - 60% time on tests is acceptable
- Cover: unit, integration, regression, end-to-end, and manual tests
- Document manual tests with step-by-step procedures
- Watch for deprecation warnings in test output
- All tests must pass before merge
- Write tests alongside implementation, not after

---

### handle-deprecation-warnings
**Purpose**: Address deprecation warnings immediately rather than accumulating technical debt.

**When to use**: When seeing deprecation warnings in test output, CI/CD logs, or development.

**Key concepts**:
- Read the warning carefully and check migration guides
- Update code to use recommended APIs immediately
- Don't suppress warnings - fix the underlying issue
- If can't fix immediately, create a tracking issue
- Proactive migration is easier than forced refactoring
- Deprecation warnings are advance notice - respect that

---

## Usage

Skills are automatically available to Claude in all projects. Claude will use them when relevant tasks arise.

### Installation

User skills are typically installed as symlinks:

```bash
cd ~/.claude/skills/
ln -s /path/to/custom-claude-skills/global-scope/access-skill-resources
ln -s /path/to/custom-claude-skills/global-scope/cli-ux-colorful
# ... etc
```

Or copied directly:

```bash
cp -r /path/to/custom-claude-skills/global-scope/* ~/.claude/skills/
```

### Skill Structure

Each skill directory contains:
- `skill.md` (required) - Skill instructions with YAML frontmatter
- `scripts/` (optional) - Executable code for repetitive tasks
- `references/` (optional) - Documentation loaded as needed
- `assets/` (optional) - Files used in output (templates, etc.)

## Integration

These skills work together to maintain consistent quality:

- **development-standards** defines the baseline (no emoji, modern features, thorough docs)
- **exhaustive-testing** ensures quality through comprehensive tests
- **handle-deprecation-warnings** keeps code current during testing
- **dependency-management** guides library choices
- **cli-ux-colorful** ensures good UX for terminal tools
- **access-skill-resources** helps navigate skill internals

## Creating Your Own User Skills

See the `skill-creator` skill in `../official/skill-creator/` for guidance on creating effective skills.

## Next Steps

1. Review each skill's `skill.md` for detailed instructions
2. Install skills in `~/.claude/skills/` for global availability
3. Customize or extend skills for your workflow
4. Create new skills following the skill-creator guidance

## Summary

User skills provide cross-project standards and workflows that maintain consistency and quality across all development work. They represent organizational knowledge and best practices that extend Claude's capabilities beyond general coding assistance.
