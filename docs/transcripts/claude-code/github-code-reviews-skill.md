---
name: GitHub Code Reviews
description: Conduct deep, comprehensive code reviews examining architecture, quality, testing, security, and cross-cutting concerns
version: 1.0.0
---

# GitHub Code Reviews

Perform thorough, structured code reviews that examine code from multiple dimensions, then track findings appropriately.

## Review Process

**1. Perform comprehensive code review**

Examine the code deeply across all dimensions (see below).

**2. After identifying actionable feedback, research existing issues**

For each problem or enhancement identified:
- Search existing issues (open and closed)
- If related issue exists, link to it prominently

**3. Structure and save the review**

- Save detailed review to `.scratch/code-review-pr-{NUMBER}-{DATE}.md`
- Create `.scratch/` directory if needed (add to `.gitignore`)
- Post summary as PR comment

## Review Dimensions

Examine code across these dimensions:

### 1. Code Quality and Development Preferences

- Uses modern language features appropriately?
- Follows project conventions and style guides?
- Clear, descriptive naming?
- Appropriate use of comments and inline documentation?
- Avoids anti-patterns?

### 2. Code Architecture

- Follows established architectural patterns?
- Proper separation of concerns?
- Dependency injection used appropriately?
- Interfaces and abstractions at correct level?
- Module boundaries respected?

### 3. Test Coverage

- Adequate unit test coverage?
- Integration tests for component interactions?
- Edge cases tested?
- Error conditions tested?
- Tests are maintainable and clear?
- Included in end-to-end testing?

### 4. Documentation Quality

- Public APIs documented?
- Complex logic explained?
- Docstrings/JSDoc accurate and complete?
- Examples provided where helpful?
- README or other docs updated if needed?

### 5. Edge Cases

- Null/undefined handling?
- Empty collections handled?
- Boundary conditions tested?
- Concurrent access considered?
- Resource limits considered?

### 6. Error Handling

- Errors caught and handled appropriately?
- Error messages clear and actionable?
- Graceful degradation where possible?
- Logging sufficient for debugging?
- Resources cleaned up on error paths?

### 7. Performance & Scalability

- Algorithm complexity appropriate?
- Database queries efficient?
- Caching used where beneficial?
- Memory usage reasonable?
- Will this scale with growth?

### 8. Maintainability & Future-Proofing

- Code readable and understandable?
- Duplication minimized?
- Easy to modify without breaking?
- Dependencies managed well?
- Migration path for breaking changes?

### 9. Security & Safety

- Input validation and sanitization?
- SQL injection protection?
- XSS protection?
- Authentication/authorization correct?
- Secrets not hardcoded or committed?
- Rate limiting where needed?

### 10. Cross-Cutting Concerns

**These vary by project but require comparing code under review with other stable code in the system.**

**Common cross-cutting concerns:**

**Polyglot interactions:**
- Language boundaries handled correctly?
- Data serialization/deserialization safe?
- Type safety maintained across language boundaries?
- Example: Python processing JavaScript config files correctly?
- Example: TypeScript injecting dependencies into Python correctly?

**Pattern consistency:**
- Follows established patterns in the codebase?
- If deviates, is there clear justification?
- Example: Other modules use functional approach, but this uses OOP - why?
- Example: Other parsers follow specific abstraction pattern - does this one?

**Data structure consistency:**
- Uses established data models?
- Transformations between representations consistent?
- Naming conventions match related modules?

**API design consistency:**
- Error handling consistent with other APIs?
- Parameter ordering and naming consistent?
- Return types follow project conventions?

## Review Structure

### Detailed Review: `.scratch/code-review-pr-{NUMBER}-{ISO-8601-DATETIME-WITH-TZ-OFFSET}.md`

```markdown
# Code Review: PR #{NUMBER} - {TITLE}

**Reviewer:** Claude Code
**Date:** {DATE}
**PR:** {URL}

## Summary

Brief overview of changes and overall assessment.

## Blockers (Must fix before merge)

### 1. SQL Injection Vulnerability
- **File:** `src/db/queries.ts:67`
- **Dimension:** Security
- **Severity:** Blocker
- **Complexity:** Simple
- **Time Estimate:** 30 minutes
- **Fix Location:** This branch, before merge
- **Related Issue:** None found (searched "SQL injection", "query security")

**Description:**
Query uses string concatenation: `SELECT * FROM users WHERE id = ${userId}`
Vulnerable to SQL injection attacks.

**Recommendation:**
Use parameterized queries:
\```typescript
db.query('SELECT * FROM users WHERE id = ?', [userId])
\```

### 2. Inconsistent Pattern with Existing Parsers
- **File:** `src/parsers/new-parser.ts`
- **Dimension:** Cross-cutting (Pattern Consistency)
- **Severity:** Blocker
- **Complexity:** Moderate
- **Time Estimate:** 3 hours
- **Fix Location:** This branch, before merge
- **Related Issue:** As side effect of #123 (parser refactoring)

**Description:**
Other parsers (PythonParser, TypeScriptParser) inherit from BaseParser and implement
parse_file(). This parser doesn't follow that pattern, making it inconsistent with
established architecture.

As side effect of issue #123, the parser refactoring effort expects all parsers to
follow the BaseParser contract.

**Recommendation:**
Refactor to extend BaseParser and implement the standard interface.

## Critical (Should fix before merge)

### 1. Missing Test Coverage for Error Path
- **File:** `src/api/client.ts:45-60`
- **Dimension:** Test Coverage, Error Handling
- **Severity:** Critical
- **Complexity:** Moderate
- **Time Estimate:** 2 hours
- **Fix Location:** This branch or follow-up PR
- **Related Issue:** None found (searched "API client tests", "error handling")

**Description:**
Function handles network errors but tests only cover success case.
Missing tests for timeout, connection refused, malformed response.

**Recommendation:**
Add test cases for error conditions with mocked failures.

## Important (Fix soon after merge)

...

## Enhancements (Consider for future work)

...

## Positive Feedback

- Clean dependency injection in UserService
- Good use of TypeScript strict mode features
- Clear variable naming throughout
```

### PR Comment Summary

```markdown
## Code Review Summary

Detailed review: `.scratch/code-review-pr-123-2025-10-18.md`

### Blockers (2) - Must fix before merge
1. **SQL injection vulnerability** (queries.ts:67) - 30min, fix in this branch
2. **Inconsistent parser pattern** (new-parser.ts) - Related to #123 - 3hrs, fix in this branch

### Critical (1) - Should fix before merge
1. **Missing error test coverage** (client.ts:45-60) - 2hrs, this branch or follow-up

### Important (3) - Fix soon after merge
...

### Enhancements (2) - Consider for future
...

See detailed review for full analysis, recommendations, and time estimates.
```

## Severity Classifications

**Blocker:**
- Security vulnerabilities
- Breaking changes to public APIs
- Data loss risks
- Crashes or fatal errors
- Violates established architectural patterns without justification
- Cross-cutting concerns that break system consistency

**Critical:**
- Missing critical error handling
- Performance regressions
- Missing test coverage for important paths
- Documentation gaps for public APIs

**Important:**
- Code duplication
- Non-critical error handling gaps
- Maintainability issues
- Minor architectural inconsistencies

**Enhancement:**
- Performance optimizations
- Better logging
- Code style improvements
- Nice-to-have features

**Nitpick:**
- Variable naming preferences
- Comment formatting
- Minor style inconsistencies

## After Review: Issue Management

**For each finding, search existing issues:**

```bash
# Search for related issues
gh issue list --search "SQL injection"
gh issue list --state all --search "parser pattern"
```

**Link to existing issues prominently in review:**
- "Related to #123 (parser refactoring)"
- "As side effect of issue #456, this doesn't handle..."
- "Known issue #789 affects this code path"

**Create new issues only for untracked findings:**

```bash
gh issue create \
  --title "SQL injection vulnerability in query builder" \
  --body "Found in PR #123 code review.

**Severity:** Blocker
**Dimension:** Security
**Complexity:** Simple
**Time Estimate:** 30 minutes

See .scratch/code-review-pr-123-2025-10-18.md for details.

**File:** src/db/queries.ts:67
**Problem:** Using string concatenation for SQL queries
**Fix:** Use parameterized queries" \
  --label "security,blocker"
```

## Quick Reference

```bash
# 1. Perform comprehensive review examining all dimensions
#    (Code quality, architecture, tests, docs, edge cases,
#     error handling, performance, maintainability, security,
#     cross-cutting concerns)

# 2. Create .scratch directory if needed
mkdir -p .scratch
echo ".scratch/" >> .gitignore  # If not already there

# 3. Save detailed review
# .scratch/code-review-pr-{NUMBER}-{DATE}.md

# 4. Research existing issues for each finding
gh issue list --search "relevant keywords"
gh issue list --state all --search "..."

# 5. Create new issues for untracked findings
gh issue create --title "..." --body "..." --label "..."

# 6. Post summary to PR
gh pr comment {NUMBER} --body "$(cat summary.md)"
```

## Remember

- Review first, research issues second
- Examine all dimensions deeply
- Pay special attention to cross-cutting concerns
- Compare with stable code in the system
- Check for pattern consistency
- Classify by severity with time estimates
- Save detailed review to `.scratch/`
- Link to existing issues prominently
- Create new issues only for untracked findings
- Post summary to PR
- No emoji (developer-facing content)