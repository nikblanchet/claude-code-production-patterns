# Project Agents

Project agents are custom autonomous subprocesses that handle complex, multi-step tasks specific to your project. They operate in isolated contexts with specific tools and goals.

## Agents in This Collection

### code-reviewer
**Type**: Autonomous code review specialist
**Model**: sonnet
**Tools**: Read, Grep, Glob, Bash, Write

**Purpose**: Expert code review across 11 dimensions with fresh eyes. Operates completely autonomously from requirements gathering through posting review to PR.

**When to invoke**:
- IMMEDIATELY after writing or modifying significant code
- Before creating pull requests
- When explicitly requested to perform code review
- After completing features or bug fixes

**Key features**:

**Autonomous operation**:
- NO inherited conversation context (fresh eyes every time)
- Completes entire review process without stopping for confirmation
- Only asks questions if requirements source cannot be determined

**11-dimension review**:
1. **Functional Completeness** (checked FIRST) - All requirements met, stays in scope
2. **Code Quality** - Modern features, conventions, clear naming
3. **Code Architecture** - Patterns, separation of concerns, DI
4. **Test Coverage** - Adequate tests, edge cases, error conditions
5. **Documentation** - APIs documented, complex logic explained
6. **Edge Cases** - Null handling, boundaries, concurrent access
7. **Error Handling** - Appropriate catching, clear messages, cleanup
8. **Performance & Scalability** - Algorithm complexity, caching, memory
9. **Maintainability** - Readable, minimal duplication, easy to modify
10. **Security & Safety** - Input validation, no hardcoded secrets, auth/authz
11. **Cross-Cutting Concerns** - Pattern consistency, polyglot interactions

**Review process**:
1. Understand requirements from PR description, `.planning/PLAN.md`, or linked issue
2. Check PR comments for previous review findings (now part of acceptance criteria)
3. Document all requirements and scope boundaries
4. Examine code across all 11 dimensions
5. Classify findings: Blocker, Important, Minor, Enhancement
6. Research existing issues to link findings
7. Save detailed review to `.scratch/code-review-pr-{NUMBER}-{TIMESTAMP}.md`
8. Post concise summary to PR as comment
9. Return final report to caller

**Handoff contract**:
- **Input**: PR number (required), optional areas of concern
- **Output**: Path to detailed review file, verdict summary, finding counts

**Scope checking**:
- Flags out-of-scope features for removal to separate PR
- Ensures PR stays focused on its defined goal
- Verifies previous review blockers were fixed (now acceptance criteria)

**Severity classification**:
- **Blocker**: Must fix before merge (missing requirements, unfixed previous blockers, security, crashes, out-of-scope features)
- **Important**: Fix immediately after merge (too large for this PR)
- **Minor**: Address later (maintainability, inconsistencies)
- **Enhancement**: Impact/effort matrix for future improvements

**Requirements sources**:
- **Plan step**: Read `.planning/PLAN.md` for step details and acceptance criteria
- **Issue fix**: Read linked issue via `gh issue view`
- **Previous reviews**: All PR comments (fixing blockers is now required)

**Output format**:
```markdown
# Code Review: PR #X

**[Verdict]** / **Fix N things before merge**

[Optional summary with kudos]

## Findings

**Blockers (N):**
1. [Description with file:line]
2. ...

**Important (N):**
...

See detailed review: `.scratch/code-review-pr-{NUMBER}-{TIMESTAMP}.md`
```

---

## What Are Agents?

Agents are autonomous subprocesses that:
- Run in isolated contexts (no inherited conversation history)
- Have specific tools and model assignments
- Execute complete workflows without stopping for confirmation
- Return results to the caller when done

### Agents vs Skills vs Hooks

| Feature | Agents | Skills | Hooks |
|---------|--------|--------|-------|
| **What** | Autonomous subprocess | Knowledge loaded into context | Event-driven command |
| **When** | Complex multi-step tasks | Provide specialized knowledge | Respond to Claude Code events |
| **Context** | Isolated (fresh eyes) | Shared with main conversation | Runs in shell |
| **Example** | Code reviewer, test generator | Git workflow, brand guidelines | Inject git status on prompt |
| **Invocation** | Task tool with subagent_type | Automatic when relevant | Automatic on event |
| **Output** | Final report to caller | Available in context | stdout/stderr |

### Integration

Agents work well with skills and hooks:
- **Hook** triggers workflow ("new PR created")
- **Skill** provides domain knowledge ("code review standards")
- **Agent** executes complex task ("autonomous review across 11 dimensions")

## Project Agents vs User Agents

| Aspect | Project Agents | User Agents |
|--------|---------------|-------------|
| **Location** | `.claude/agents/` in project repo | `~/.claude/agents/` globally |
| **Scope** | Project-specific tasks | Cross-project capabilities |
| **Examples** | code-reviewer, deploy-orchestrator | python-313-conventions, security-scanner |
| **Versioned** | Yes (committed to git) | No (user's local machine) |
| **Shared** | All team members | Individual developer |
| **Customization** | Project conventions, tools, workflows | Language/framework best practices |

## Agent Anatomy

Agents are defined in markdown files with YAML frontmatter:

```markdown
---
name: code-reviewer
description: When to use this agent
model: sonnet
tools: Read, Grep, Glob, Bash, Write
---

# Agent Instructions

Detailed instructions for the agent...
```

**Required frontmatter**:
- `name`: Agent identifier
- `description`: When to invoke (critical for automatic invocation)
- `model`: sonnet, opus, or haiku
- `tools`: Comma-separated list of allowed tools

**Instructions**: Detailed guidance on:
- Role and responsibilities
- When to invoke (proactive vs on-request)
- Input/output contract
- Process steps
- Best practices
- Examples

## Usage

### Invoking an Agent

```bash
# From Claude Code conversation
Use the Task tool with subagent_type='code-reviewer'
```

Claude can invoke agents:
- Automatically when description matches the task
- When explicitly requested by user
- When another agent delegates work

### Agent Best Practices

**Design for autonomy**:
- Complete entire workflow without stopping
- Only ask questions if truly unable to proceed
- Document clear input/output contracts
- Provide comprehensive instructions

**Fresh eyes principle**:
- Agents don't inherit conversation context
- Must gather all information themselves
- Ensures objective, unbiased execution
- Prevents assumptions from main conversation

**Tool restrictions**:
- Limit tools to what's necessary
- Prevents scope creep and confusion
- Makes agent behavior predictable
- Improves performance (fewer options)

**Model selection**:
- **Sonnet**: Balance of capability and cost (default)
- **Opus**: Complex reasoning, critical decisions
- **Haiku**: Simple, straightforward tasks

## Creating Project Agents

Good project agent candidates:
- **Code reviewer**: Review against project-specific standards
- **Deploy orchestrator**: Handle deployment workflows
- **Test generator**: Generate tests following project patterns
- **Documentation writer**: Write docs in project style
- **Refactoring assistant**: Modernize code following project architecture

Bad agent candidates:
- Simple one-step tasks (just do them directly)
- Tasks requiring extensive back-and-forth
- Tasks better suited for skills (knowledge) or hooks (events)

## Example: Using code-reviewer

```markdown
User: "I just created PR #42 for the display system feature"

Claude: I'll review PR #42 using the code-reviewer agent.

[Spawns code-reviewer agent with PR number]

[Agent autonomously:]
1. Reads PR description
2. Finds requirements in .planning/PLAN.md step 15
3. Checks previous PR comments
4. Reviews code across 11 dimensions
5. Classifies findings
6. Saves detailed review to .scratch/code-review-pr-42-2025-01-19T14:30:00-08:00.md
7. Posts summary to PR
8. Returns report

Claude: Review complete! Found 2 blockers and 3 minor issues.
See `.scratch/code-review-pr-42-2025-01-19T14:30:00-08:00.md`

**Blockers:**
1. Missing test for async error handling (test_display.py)
2. Out-of-scope: Progress bar animation (should be separate PR)

I've posted the summary to PR #42. Want me to help fix the blockers?
```

## Summary

Project agents automate complex, multi-step tasks specific to your project's workflows and standards. They operate autonomously with fresh eyes, ensuring consistent quality and freeing developers to focus on implementation rather than process.

The code-reviewer agent demonstrates a sophisticated pattern:
- Autonomous operation from start to finish
- Context gathering from multiple sources
- Comprehensive multi-dimension review
- Integration with project workflow (.planning/, .scratch/, PR comments)
- Clear severity classification
- Detailed documentation with actionable findings

Well-designed project agents feel like having an expert team member who knows your project deeply, follows your standards religiously, and never gets tired of thoroughness.
