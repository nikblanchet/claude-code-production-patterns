# Why These Patterns

## The Problem: AI-Assisted Development at Scale

Large codebases (100K+ lines) working with Claude Code agents face unique challenges:

1. **Context Management**: Claude has token limits, making full-codebase context impossible
2. **Parallel Development**: Running multiple agents serially is slow; running them in parallel creates merge conflicts
3. **Quality Control**: AI-generated code needs consistent standards across multiple agent instances
4. **Workflow Coordination**: Without automation, developers spend time on manual setup and context switching

These patterns emerged from production use addressing these exact challenges.

## The Solution: Integration Patterns

### Core Claude Code Features

**Hooks** solve workflow automation:
- Automatically inject relevant context (git status, environment info) into every agent interaction
- Enforce permissions and safety checks before AI executes commands
- Trigger external tools based on AI actions

**Agents** solve complex task execution:
- Autonomous subprocesses with fresh context (no inherited conversation baggage)
- Can execute multi-step workflows independently
- Specialized agents for different review dimensions (code quality, Python conventions, etc.)

**Skills** solve knowledge capture:
- Reusable knowledge modules that agents can invoke when needed
- Bundle scripts, references, and documentation together
- Share standards across projects and team members

### Supporting Infrastructure

**Git Worktree Orchestration** solves parallel development:
- Multiple agents work simultaneously on different branches without conflicts
- Path-based detection protects main branch from accidental commits
- Shared context across worktrees maintains consistency

**CLAUDE.md Context Management** solves documentation limits:
- External imports bypass the 40KB character limit
- Modular documentation that can be updated independently
- Shared across all worktrees via symlinks

**Direnv Tool Interception** solves workflow enforcement:
- PATH manipulation intercepts commands before execution
- Provides helpful error messages instead of silent failures
- Guides developers toward correct workflow

## Why This Approach

### Value Proposition

1. **Parallel Agent Execution**: Run 4-7+ Claude Code instances simultaneously without merge conflicts
2. **Consistent Quality**: Same standards, hooks, and agents across all instances
3. **Reduced Context Switching**: Automation handles repetitive setup and validation
4. **Portable Patterns**: Works across projects and team members

### Real-World Validation

These patterns have been refined through production use in polyglot codebases (Python/TypeScript/JavaScript) where:
- Multiple features develop in parallel
- Code quality standards must remain consistent
- Developers need fast iteration cycles
- Context management is critical

For a narrative example of these patterns in practice, see [DocImp](https://github.com/nikblanchet/docimp), a reference implementation demonstrating the patterns in a real codebase. However, this repository is self-contained—you don't need DocImp to understand or use these patterns.

## When to Use These Patterns

**Use these patterns when:**
- Working on large codebases (10K+ lines) where full context is impossible
- Coordinating multiple development efforts in parallel
- Need consistent code quality across multiple AI-assisted workflows
- Team is adopting Claude Code and needs standardization

**Skip these patterns when:**
- Working on small projects (<5K lines) where complexity isn't justified
- Single-developer, single-feature workflow where parallel development isn't needed
- Team isn't using Claude Code extensively
- Existing workflow automation is sufficient

## Trade-offs

**Benefits:**
- Dramatically faster parallel development
- Consistent quality and standards
- Reduced manual setup and context management
- Portable across projects

**Costs:**
- Initial setup complexity (git hooks, worktree scripts, symlinks)
- Learning curve for team members unfamiliar with git worktrees
- Maintenance overhead for hook and agent updates
- Platform dependencies (tested on macOS/Linux only)

## The Bottom Line

These patterns represent a production-tested approach to AI-assisted development at scale. They're not theoretical—they're what actually works when you need multiple Claude Code instances collaborating effectively on a large codebase while maintaining quality and consistency.
