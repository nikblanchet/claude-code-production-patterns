# Claude Code Hooks and Permissions Configuration

This directory demonstrates Claude Code's hooks and permissions system - a key feature for advanced workflow automation.

## What Are Claude Code Hooks?

Claude Code hooks are **event-driven shell commands** that execute in response to Claude Code events during development sessions. They enable sophisticated workflow automation, quality gates, and integration with development tooling.

### CRITICAL DISTINCTION: Claude Code Hooks vs Git Hooks

**These are completely different technologies:**

| Feature | Claude Code Hooks | Git Hooks |
|---------|------------------|-----------|
| **What they are** | Event triggers in Claude Code sessions | Event triggers in Git operations |
| **Configuration** | `.claude/settings.local.json` | `.git/hooks/` scripts |
| **When they run** | During AI assistance (prompt submit, tool execution) | During Git operations (commit, push, checkout) |
| **Example events** | `user-prompt-submit`, `tool-call`, `session-start` | `pre-commit`, `post-checkout`, `pre-push` |
| **Use cases** | Workflow automation, context injection, quality gates | Branch protection, code formatting, commit validation |

## Permissions System

Claude Code's permissions system controls which tools Claude can use without asking permission.

### Permission Categories

**`allow`**: Tools Claude can use freely without user approval
- Test commands (pytest, npm test)
- Read-only Git operations (log, status, diff)
- File reading tools (Read, Glob, Grep)
- Safe diagnostic tools

**`deny`**: Tools Claude cannot use (blocked completely)
- Direct Python/pip execution (enforces using uv)
- Destructive operations without wrapper
- Uncontrolled installations

**`ask`**: Tools that require user approval each time
- Write operations (git commit, git push)
- Package installation (uv add)
- PR creation (gh pr create)

### Example Configuration

See `settings.local.json` for a production example from a large-scale codebase.

## Common Hook Use Cases

### 1. User Prompt Submit Hook

Execute commands when the user submits a prompt to Claude.

**Use cases:**
- Inject current git status into context
- Load relevant documentation based on keywords
- Check for uncommitted changes
- Validate environment setup

**Example:**
```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "git status --short"
    }
  }
}
```

### 2. Tool Call Hook

Intercept or log tool calls before Claude executes them.

**Use cases:**
- Log all tool usage for audit trails
- Validate tool parameters
- Inject additional context
- Prevent certain tool combinations

**Example:**
```json
{
  "hooks": {
    "tool-call": {
      "command": "echo '[TOOL CALL] {{tool_name}} at {{timestamp}}' >> .claude/tool-log.txt"
    }
  }
}
```

### 3. Session Start Hook

Run setup commands when Claude Code session starts.

**Use cases:**
- Verify dependencies installed
- Check for updates to documentation
- Load project-specific context
- Validate development environment

**Example:**
```json
{
  "hooks": {
    "session-start": {
      "command": "scripts/validate-env.sh"
    }
  }
}
```

### 4. Session End Hook

Cleanup or logging when session ends.

**Use cases:**
- Save session summary
- Clean up temporary files
- Update usage metrics
- Archive conversation logs

**Example:**
```json
{
  "hooks": {
    "session-end": {
      "command": "scripts/save-session-summary.sh"
    }
  }
}
```

## Advanced Patterns

### Pattern 1: Context Injection Based on Working Directory

Automatically load relevant documentation when working in specific directories.

```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "if [[ $(pwd) == *'/analyzer'* ]]; then cat docs/analyzer-context.md; fi"
    }
  }
}
```

### Pattern 2: Pre-Flight Validation

Ensure tests pass before allowing commits.

```json
{
  "permissions": {
    "ask": ["Bash(git commit:*)"]
  },
  "hooks": {
    "before-tool": {
      "command": "if [[ '{{tool_name}}' == 'Bash(git commit'* ]]; then npm test || exit 1; fi"
    }
  }
}
```

### Pattern 3: Workflow State Tracking

Track what Claude is working on across sessions.

```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "echo '{{timestamp}}: {{prompt}}' >> .claude/session-log.md"
    }
  }
}
```

### Pattern 4: Deny Dangerous Operations, Redirect to Safe Alternatives

Block direct Python/pip usage, enforce uv-based workflow.

```json
{
  "permissions": {
    "deny": [
      "Bash(python:*::*)",
      "Bash(pip:*::*)"
    ],
    "allow": [
      "Bash(uv run python:*)",
      "Bash(uv run pytest:*)"
    ]
  }
}
```

This pattern ensures:
- All Python execution goes through uv (virtual environment management)
- No accidental global package installations
- Consistent dependency management across the project
- Educational error messages when Claude attempts blocked commands

## Best Practices

### 1. Keep Hooks Fast

Hooks run synchronously and block Claude's workflow. Keep execution under 1 second.

**Good**: `git status --short` (fast)
**Bad**: `npm install && npm test` (slow)

### 2. Use Hooks for Workflow Automation, Not Complex Logic

Hooks should trigger scripts, not contain complex logic inline.

**Good**:
```json
{
  "hooks": {
    "session-start": {
      "command": "scripts/setup-session.sh"
    }
  }
}
```

**Bad**:
```json
{
  "hooks": {
    "session-start": {
      "command": "if [ ! -f .env ]; then cp .env.example .env && sed -i '' 's/API_KEY=/API_KEY=test/' .env; fi && npm install && npm run build"
    }
  }
}
```

### 3. Fail Gracefully

Hooks that fail should not break Claude Code sessions.

```bash
#!/bin/bash
# scripts/validate-env.sh

# Exit 0 even if validation fails, just warn
if ! command -v node &> /dev/null; then
  echo "WARNING: Node.js not found" >&2
fi

exit 0
```

### 4. Document Hook Behavior

Add comments to settings.local.json explaining what each hook does and why.

```json
{
  "hooks": {
    "user-prompt-submit": {
      "command": "git status --short",
      "_comment": "Inject git status so Claude knows about uncommitted changes"
    }
  }
}
```

### 5. Use Permissions to Enforce Workflows

Combine permissions with hooks to create guard rails.

```json
{
  "permissions": {
    "deny": ["Bash(pip:*::*)"],
    "allow": ["Bash(uv pip:*)"]
  }
}
```

This pattern:
- Prevents Claude from using pip directly
- Forces usage of uv (project's chosen tool)
- Provides educational error when blocked command attempted

## Hook Variables

Hooks have access to context variables (implementation-dependent):

- `{{timestamp}}` - Current timestamp
- `{{tool_name}}` - Name of tool being called
- `{{prompt}}` - User's prompt text
- `{{working_directory}}` - Current working directory

Check Claude Code documentation for the complete list of available variables.

## Integration with Other Patterns

Hooks work best when combined with:

1. **Custom Agents** - Hooks can trigger agent execution
2. **Skills** - Hooks can load skill context based on working directory
3. **MCP Servers** - Hooks can validate MCP server availability
4. **Permissions** - Hooks can enforce permission policies

## Troubleshooting

### Hook Not Running

1. Check `.claude/settings.local.json` syntax (valid JSON)
2. Verify hook command is executable
3. Check Claude Code logs for errors
4. Test hook command manually in terminal

### Hook Causing Performance Issues

1. Profile hook execution time
2. Move slow operations to background
3. Cache results when possible
4. Consider removing hook if not essential

### Permission Denied Errors

1. Verify file permissions on hook scripts
2. Check that paths are correct
3. Ensure scripts have shebang line (`#!/bin/bash`)
4. Test with `bash -x scripts/hook.sh` for debugging

## Example Production Configuration

The included `settings.local.json` shows a real configuration from a large-scale polyglot codebase (Python + TypeScript + JavaScript) with:

- Test command permissions (pytest, npm test, ruff, mypy)
- Git operation permissions (read-only allowed, write requires approval)
- GitHub CLI permissions (read issues/PRs, require approval for writes)
- Blocked direct Python/pip usage (enforces uv workflow)
- Skill permissions (development-standards, exhaustive-testing, etc.)
- Additional directories for worktree access

## Next Steps

1. Copy `settings.local.json` to your project's `.claude/` directory
2. Customize permissions for your workflow
3. Add hooks for your specific use cases
4. Test thoroughly before relying on hooks for critical workflows
5. Document hook behavior for team members

## Resources

- Claude Code Hooks Documentation: [Link when available]
- MCP Server Integration: [Link when available]
- Custom Agents: See `../agents/` directory
- Skills: See `../skills/` directory

## Summary

Claude Code hooks enable sophisticated workflow automation that goes far beyond basic code generation:

- **Event-driven**: Respond to user actions and tool executions
- **Workflow enforcement**: Prevent anti-patterns, guide best practices
- **Context injection**: Load relevant information automatically
- **Quality gates**: Validate before destructive operations
- **Audit trails**: Log tool usage and decisions

Combined with custom agents and skills, hooks create a powerful framework for AI-assisted development that maintains quality standards while maximizing productivity.
