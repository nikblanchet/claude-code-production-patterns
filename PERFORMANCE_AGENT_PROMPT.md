# Performance Documentation Agent Prompt

Use this prompt with a Task tool call to generate comprehensive performance documentation:

```markdown
You are a technical documentation specialist creating performance documentation for the Claude Code Production Patterns repository (Scenario C compliance).

## Your Mission

Create a comprehensive performance documentation file at `docs/PERFORMANCE.md` that covers performance characteristics, optimization strategies, and measurement approaches for all components in the repository.

## Context

This repository demonstrates advanced Claude Code integration patterns:
- Custom agents (python-313-conventions, code-reviewer)
- Custom skills (8 skills across user/official/project)
- Claude Code hooks (permissions system, event-driven workflows)
- Git worktree orchestration (create_worktree.py - 1,067 lines)
- Git hooks (pre-commit, post-checkout)

## Required Sections

### 1. Executive Summary
- Performance philosophy for AI-assisted development
- Key metrics that matter
- When to optimize vs accept trade-offs

### 2. Component Performance Characteristics

#### 2.1 Custom Agents
**For each agent (python-313-conventions, code-reviewer):**
- Estimated token usage (input/output)
- Expected execution time (fast/medium/slow operations)
- Context window considerations (how much code can be reviewed at once)
- Cost implications (Sonnet vs Opus vs Haiku)
- Optimization strategies:
  - When to use tool restrictions to reduce overhead
  - When to split large reviews into chunks
  - Caching strategies for repeated operations

**Provide specific estimates:**
- Small file review (< 200 lines): X tokens, Y seconds
- Medium review (200-1000 lines): X tokens, Y seconds
- Large review (1000+ lines): X tokens, Y seconds
- Full PR review (10-50 files): X tokens, Y minutes

#### 2.2 Custom Skills
**For skill loading:**
- Overhead per skill (token cost of loading into context)
- Progressive disclosure benefits
- When to use bundled resources vs inline content
- Skill activation patterns (automatic vs manual)

**Provide guidance:**
- How many skills can be active simultaneously?
- Impact of skill size (our skills range 5-13KB)
- Optimization: references/ vs inline documentation

#### 2.3 Claude Code Hooks
**Hook execution overhead:**
- Per-hook execution time targets (< 100ms guideline)
- Shell command overhead
- When hooks slow down sessions
- Optimization strategies:
  - Keep hooks fast (no network calls, minimal disk I/O)
  - Async patterns for slow operations
  - Caching hook output

**Measure and document:**
- user-prompt-submit hook: Target < X ms
- tool-call hook: Target < X ms
- session-start hook: Target < X ms (can be slower, runs once)

#### 2.4 Git Worktree Orchestration
**create_worktree.py performance:**
- Benchmark actual execution time:
  - Fast path (no uncommitted changes): X seconds
  - With uncommitted changes (stash/apply): Y seconds
  - With npm install: Z seconds
  - With uv sync (Python env): W seconds
  - Full setup (all steps): Total seconds

**Breakdown by operation:**
- Git worktree creation: X ms
- Symlink creation: X ms
- Husky setup: X ms
- npm install: X seconds (network-dependent)
- uv sync: X seconds
- direnv setup: X ms

**Optimization opportunities:**
- Parallel operations (which steps can run concurrently?)
- Skip steps when unnecessary (--no-npm, --no-python flags?)
- Caching strategies (uv cache, npm cache)

#### 2.5 Git Hooks
**pre-commit and post-checkout:**
- Execution time: < X ms (must be fast)
- Pattern matching overhead
- When to use --no-verify bypass

### 3. Scalability Guidance

#### 3.1 Codebase Size Impact
**Document performance across scales:**
- Small projects (< 10K LOC): Performance characteristics
- Medium projects (10K-100K LOC): What changes, what to watch
- Large projects (100K+ LOC): Critical optimizations needed

#### 3.2 Team Size Impact
- Single developer: Baseline performance
- Small team (2-5): Coordination overhead
- Large team (10+): Shared context challenges

### 4. Measurement Strategies

#### 4.1 How to Measure
**Provide practical instructions:**
- Token usage: How to track with Claude API
- Execution time: Bash commands to benchmark
- Hook overhead: How to profile
- Agent performance: How to measure end-to-end

**Example measurement commands:**
```bash
# Time worktree creation
time python actual-code/create_worktree.py issue-123 test-branch

# Profile hook execution
time .git/hooks/pre-commit

# Measure agent token usage
# [Instructions for checking Claude API usage]
```

#### 4.2 What to Measure
- Baseline metrics (before optimization)
- Target metrics (acceptable performance)
- Warning thresholds (when to optimize)

#### 4.3 Optimization Decision Framework
**When to optimize:**
- Hook taking > 100ms
- Agent reviews timing out
- Worktree creation > 2 minutes
- Skills not loading due to context limits

**When NOT to optimize:**
- Hook at 50ms (fast enough)
- Agent using 100K tokens for thorough review (acceptable cost)
- One-time setup taking 60 seconds (acceptable for automation)

### 5. Optimization Techniques

#### 5.1 Agent Optimization
- Scope reduction (review only changed files)
- Incremental reviews (review commits individually)
- Model selection (Haiku for simple checks, Sonnet for depth)
- Tool restriction (limit available tools to reduce overhead)

#### 5.2 Skill Optimization
- Progressive disclosure (metadata → main → references)
- Selective loading (only load relevant skills)
- Shared resources (references/ symlinked across skills)

#### 5.3 Hook Optimization
- Caching (save expensive computation results)
- Conditional execution (only run when relevant)
- Background jobs (for non-critical operations)

#### 5.4 Worktree Optimization
- Skip unnecessary steps (--no-deps flag)
- Parallel operations (npm + uv in parallel)
- Incremental updates (reuse existing worktrees)

### 6. Known Performance Issues

**Document current limitations:**
- What's slow and why
- Workarounds available
- Future optimization plans

### 7. Performance Monitoring

**Ongoing monitoring strategies:**
- How to track performance over time
- When to revisit optimization decisions
- Red flags that indicate degradation

### 8. Trade-offs and Philosophy

**Document the trade-offs:**
- Thoroughness vs speed (code-reviewer is comprehensive, not fast)
- Automation vs control (hooks add overhead but prevent errors)
- Context vs performance (more skills = more capability but higher token cost)

**Philosophy:**
- Optimize for developer productivity, not raw speed
- Acceptable costs for quality improvements
- When "slow but thorough" beats "fast but shallow"

## Implementation Instructions

1. **Benchmark real operations:**
   - Run create_worktree.py and time each step
   - Test hook execution with time command
   - Estimate agent token usage based on file sizes

2. **Provide concrete numbers:**
   - Don't say "fast" - say "< 50ms"
   - Don't say "expensive" - say "~50K tokens"
   - Include ranges: "10-30 seconds depending on network"

3. **Include examples:**
   - Show actual benchmark commands
   - Provide sample measurements
   - Include optimization before/after comparisons

4. **Be honest about limitations:**
   - Document what's slow
   - Explain why it's slow
   - Provide workarounds

5. **Make it actionable:**
   - Each section should enable decisions
   - Provide clear thresholds for optimization
   - Include "what to do when X is slow"

## Output Format

Create `docs/PERFORMANCE.md` with:
- Clear section headers
- Concrete metrics (numbers, not adjectives)
- Actionable optimization guidance
- Decision frameworks
- Measurement commands
- Before/after examples where relevant

## Success Criteria

A developer reading this should be able to:
1. Understand performance characteristics of each component
2. Measure their own usage patterns
3. Make informed optimization decisions
4. Know when performance is "good enough"
5. Debug performance issues independently

## Additional Context

Review these files for implementation details:
- `actual-code/create_worktree.py` (1,067 lines) - main performance-sensitive code
- `actual-code/agents/*/README.md` - agent architecture
- `actual-code/hooks-config/README.md` - hook patterns
- `actual-code/skills/*/README.md` - skill structure

Use git grep, file reading, and code analysis to gather accurate information. Do NOT make up numbers - either benchmark them or clearly mark as estimates.

## Deliverable

Create comprehensive `docs/PERFORMANCE.md` that addresses all sections with concrete, actionable performance guidance for the Claude Code Production Patterns repository.
```

---

## Usage

To generate the performance documentation, use:

```bash
# In Claude Code session:
Task tool with:
  subagent_type: "general-purpose"
  description: "Generate performance documentation"
  prompt: [paste content from above]
```

Or copy the markdown content between the triple backticks and provide it as a prompt to an agent.
