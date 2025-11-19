# User Agents

User agents are global autonomous subprocesses available across all projects. They provide cross-project capabilities for language-specific or framework-specific tasks.

## Agents in This Collection

### python-313-conventions
**Type**: Python 3.13+ modernization reviewer
**Focus**: Semantic patterns and design that automation cannot check

**Purpose**: Expert Python code reviewer enforcing modern idioms and catching old patterns. Focuses on higher-level design patterns and modern practices that require semantic understanding, not just syntax.

**When to invoke**:
- IMMEDIATELY after writing or modifying Python code
- Before creating PRs with Python changes
- When requested to review Python code for modern conventions
- During refactoring efforts to modernize legacy Python
- When you see potential old idioms to modernize

**What automation already handles**:
- **Ruff**: Syntax, style (PEP 8), basic modernization, common anti-patterns
- **mypy**: Type checking correctness, missing annotations

**What this agent checks** (the semantic layer):

**10 Review Dimensions**:

1. **Typing Design**
   - Misuse of `Any` or overly-broad types
   - Overuse of `TypedDict`/`dataclass` where `Protocol` fits better
   - Complex nested generics harming readability
   - Type aliases for intermediate types: `type UserMap = dict[int, User]`

2. **API and Function Design**
   - Functions mixing concerns (I/O, logic, formatting)
   - Too many positional arguments or hidden defaults
   - Implicit resource lifecycles
   - Leaky abstractions

3. **Error Handling and Contracts**
   - Bare or over-broad `except Exception`
   - Swallowing exceptions silently
   - Assertions in production code
   - Returning sentinel values instead of raising

4. **Asynchronous and Concurrency Logic**
   - Blocking I/O inside async functions
   - Detached tasks or missing `await`
   - Unbounded concurrency or parallelism

5. **Control Flow and Readability**
   - Deeply nested `if`/`else`/`try` structures
   - Flag variables as implicit state machines
   - Side effects inside comprehensions

6. **Data and Collection Semantics**
   - Mutating collections while iterating
   - Relying on implicit ordering in sets/dicts
   - Manual caching instead of `@cache`/`@lru_cache`

7. **Architectural Cohesion**
   - Functions/classes with too many responsibilities
   - Hidden global state or implicit singletons
   - Tight coupling between modules
   - Reimplementing stdlib behavior

8. **Testing and Contracts**
   - Non-deterministic tests (time, randomness, I/O)
   - Missing failure-path tests
   - Assertions with unclear messages

9. **Maintainability and Clarity**
   - Comments explaining *what* instead of *why*
   - Clever or overly compressed one-liners
   - Undocumented module/function purpose

10. **Ethical and Safety Considerations**
    - Misleading names
    - Hidden side effects (network, subprocess, filesystem)
    - Serialization/deserialization without validation

**Output format**:
```markdown
**[Dimension Name]** - [Severity: High/Medium/Low]
Location: filename.py:line_number
Issue: [Describe the old pattern or problem]
Modern alternative: [Show the Python 3.13+ approach]
Rationale: [Why the modern approach is better]
```

**Reviewer checklist**:
- [ ] Function and class boundaries make logical sense
- [ ] Exceptions are explicit and meaningful
- [ ] Async code never blocks or leaks tasks
- [ ] No hidden global state or circular dependencies
- [ ] Comments describe intent, not implementation
- [ ] Typing reflects true contracts
- [ ] No magical or surprising behavior left unexplained

---

## User Agents vs Project Agents

| Aspect | User Agents | Project Agents |
|--------|-------------|----------------|
| **Location** | `~/.claude/agents/` | `.claude/agents/` in project |
| **Scope** | Language/framework best practices | Project-specific tasks |
| **Examples** | python-313-conventions, security-scanner | code-reviewer, deploy-orchestrator |
| **Versioned** | No (user's local machine) | Yes (committed to repo) |
| **Standards** | Industry best practices | Project conventions |
| **Customization** | Personal preferences | Team agreements |

## Usage

User agents are automatically available in all projects. Claude will invoke them when tasks match their descriptions.

### Installation

```bash
# Copy to user agents directory
cp python-313-conventions.md ~/.claude/agents/

# Or symlink
cd ~/.claude/agents/
ln -s /path/to/custom-agents/python-313-conventions.md
```

### Integration with development-standards Skill

The python-313-conventions agent is referenced by the development-standards skill:

```markdown
## Language-Specific Quality Standards

**Python 3.13+:** See `references/python-313-conventions.md` for modern
idiom enforcement covering typing design, API contracts, error handling...
```

This creates a workflow:
1. **development-standards skill** loaded automatically
2. Mentions Python conventions reference
3. Claude loads or invokes **python-313-conventions agent** when reviewing Python code
4. Agent catches semantic issues automation misses

## Agent Best Practices

### When to Create User Agents

**Good user agent candidates**:
- Language-specific modernization (Python 3.13+, TypeScript 5+, etc.)
- Security scanning with framework knowledge
- Performance analysis for specific tech stacks
- Accessibility review for web frameworks
- API design review for REST/GraphQL

**Bad user agent candidates**:
- Project-specific workflows (use project agents)
- Simple checks automation handles (use linters)
- One-time tasks (just do them)

### Complementary to Automation

User agents should focus on what automation cannot check:
- **Automation**: Syntax, style, type correctness
- **Agents**: Design, semantics, architecture, intent

**Example**: Python type checking
- **mypy**: Types are correct and consistent
- **python-313-conventions**: Types reflect actual contracts, avoid `Any` abuse, use appropriate constructs

## Example: Using python-313-conventions

```markdown
User: "I just wrote a new Python module for database queries"

Claude: Let me review it for modern Python 3.13+ conventions.

[Spawns python-313-conventions agent]

[Agent reviews code and returns:]

**Typing Design** - Severity: Medium
Location: db/queries.py:23
Issue: Using `dict[str, Any]` for query results
Modern alternative: Define `Protocol` or `TypedDict` for query result structure
Rationale: Provides type safety and IDE autocomplete for result access

**API and Function Design** - Severity: High
Location: db/queries.py:45
Issue: `execute_query()` mixes query execution, result formatting, and logging
Modern alternative: Separate into `_execute()`, `_format_results()`, `_log_query()`
Rationale: Single responsibility, easier to test, clearer separation of concerns

**Error Handling** - Severity: High
Location: db/queries.py:67
Issue: Bare `except Exception:` swallows all errors
Modern alternative: `except DatabaseError as e:` with specific exception types
Rationale: Catches expected errors only, allows unexpected errors to bubble up

Claude: Found 3 issues to address. Want me to help fix them?
```

## Creating User Agents

Follow the same pattern as project agents:

1. **Define scope**: What semantic patterns to check
2. **Specify when to invoke**: After code changes, before PRs, etc.
3. **Choose model**: Usually sonnet for code review
4. **Limit tools**: Typically Read, Grep, Glob for review agents
5. **Write comprehensive instructions**: Review dimensions, output format, examples
6. **Test on real code**: Iterate based on findings

## Summary

User agents provide cross-project capabilities that extend Claude's understanding of language-specific and framework-specific best practices. They catch semantic issues that automation misses, enforce modern idioms, and maintain code quality standards.

The python-313-conventions agent exemplifies this:
- Focuses on what automation cannot check (design, semantics, architecture)
- 10 review dimensions covering typing to ethics
- Modern Python 3.13+ idioms and patterns
- Integration with skills (development-standards)
- Complements rather than duplicates automation (Ruff, mypy)

Well-designed user agents make Claude feel like a language expert who knows not just the syntax, but the philosophy, idioms, and evolving best practices of the technology stack.
