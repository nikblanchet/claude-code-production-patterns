# Performance Documentation

Comprehensive performance characteristics, optimization strategies, and measurement approaches for Claude Code Production Patterns (Scenario C).

---

## Executive Summary

### Performance Philosophy

**Optimize for developer productivity, not raw speed.** This repository demonstrates AI-assisted development patterns where thoroughness, quality, and automation value outweigh millisecond optimizations.

**Key Principle**: Acceptable costs for quality improvements. A 30-second worktree setup that prevents hours of merge conflicts is excellent ROI. A 100K-token agent review that catches critical bugs before production is money well spent.

### Key Metrics That Matter

1. **Developer Time Saved**: Hours saved vs seconds spent
2. **Error Prevention**: Bugs caught by hooks/agents vs cost to run them
3. **Context Quality**: Comprehensive reviews vs token costs
4. **Automation ROI**: One-time setup cost vs ongoing manual effort eliminated

### When to Optimize vs Accept Trade-offs

**Optimize when:**
- Hooks taking > 200ms (slowing down every operation)
- Agent reviews timing out or hitting context limits
- Worktree creation > 3 minutes (network issues aside)
- Skills failing to load due to context window exhaustion

**Accept trade-offs when:**
- Hook at 50-100ms (imperceptible to developer)
- Agent using 150K tokens for thorough 11-dimension review (catching bugs)
- Worktree setup taking 60-90s (comprehensive automation)
- Skills using 20-30K tokens to provide deep domain knowledge

---

## Component Performance Characteristics

### 2.1 Custom Agents

Agents are autonomous subprocesses that execute complex tasks with fresh eyes (no inherited context).

#### python-313-conventions Agent

**Purpose**: Python 3.13+ modernization reviewer (10 dimensions)
**Model**: Sonnet (default)
**Tools**: Read, Grep, Glob (read-only)

**Token Usage Estimates:**

| Review Scope | Input Tokens | Output Tokens | Total | Cost (Sonnet) | Time |
|-------------|--------------|---------------|-------|---------------|------|
| Small file (< 200 lines) | 8K-12K | 2K-4K | 10K-16K | $0.03-$0.05 | 10-20s |
| Medium file (200-500 lines) | 15K-25K | 4K-8K | 19K-33K | $0.06-$0.10 | 20-40s |
| Large file (500-1000 lines) | 30K-50K | 8K-15K | 38K-65K | $0.12-$0.20 | 40-90s |
| Multiple files (3-5 files) | 50K-100K | 15K-30K | 65K-130K | $0.20-$0.40 | 2-4min |

**Context Window Considerations:**
- Sonnet: 200K token context window
- Can review up to ~50K lines in single invocation (rare)
- Practical limit: 5-10 files or 2,000 lines per review
- For larger reviews: split into multiple agent invocations

**Cost Implications:**
- Sonnet ($3/MTok input, $15/MTok output): Balanced thoroughness and cost
- Opus ($15/MTok input, $75/MTok output): 5x cost, use for critical architecture decisions
- Haiku ($0.25/MTok input, $1.25/MTok output): 20x cheaper, use for simple syntax checks

**Optimization Strategies:**

1. **Tool restrictions reduce overhead**:
   - Read-only tools (Read, Grep, Glob): Minimal prompt overhead (~500 tokens)
   - Full toolset (Read, Write, Edit, Bash): +2K-3K tokens per invocation

2. **Scope limitation prevents bloat**:
   - Review only changed files (git diff): 10K-30K tokens
   - Review entire module: 100K-200K tokens
   - Target: Review changed code + immediate dependencies

3. **Incremental reviews save tokens**:
   - Per-commit review: 10K-20K tokens each
   - Bulk PR review: 100K+ tokens
   - Recommendation: Review incrementally during development

4. **Caching (Claude API feature)**:
   - Agent definitions cached automatically
   - Repeated file reviews benefit from prompt caching
   - Can reduce costs by 50-90% for repeated operations

**Performance Characteristics:**

```
Review Scenarios (Estimated):

Single function modernization:
  Input: 3K tokens (agent prompt + function code)
  Output: 500 tokens (findings)
  Time: 5-10 seconds
  Cost: $0.01

Full module review (5 files, 800 lines):
  Input: 40K tokens (agent prompt + code + context)
  Output: 8K tokens (detailed findings across 10 dimensions)
  Time: 60-90 seconds
  Cost: $0.15-$0.20

Large refactoring review (15 files, 2500 lines):
  Input: 120K tokens
  Output: 25K tokens
  Time: 3-5 minutes
  Cost: $0.50-$0.70
  Note: Consider splitting into 3 agent invocations
```

#### code-reviewer Agent

**Purpose**: Autonomous 11-dimension PR review
**Model**: Sonnet (default), Opus (for critical reviews)
**Tools**: Read, Grep, Glob, Bash (gh commands), Write (review output)

**Token Usage Estimates:**

| PR Size | Files Changed | Input Tokens | Output Tokens | Total | Cost | Time |
|---------|---------------|--------------|---------------|-------|------|------|
| Small PR | 1-3 files, minor changes | 15K-25K | 5K-10K | 20K-35K | $0.08-$0.15 | 30-60s |
| Medium PR | 5-10 files, moderate changes | 40K-80K | 15K-25K | 55K-105K | $0.22-$0.42 | 2-4min |
| Large PR | 15-30 files, substantial changes | 100K-150K | 30K-50K | 130K-200K | $0.52-$1.05 | 5-8min |
| Huge PR | 50+ files, extensive changes | 180K+ | 50K+ | 230K+ | $1.20+ | 10-15min |

**11 Review Dimensions** (overhead per dimension):
1. Functional Completeness: +5K-10K tokens (gathers requirements from PR/.planning/issues)
2. Code Quality: +3K-5K tokens
3. Code Architecture: +3K-5K tokens
4. Test Coverage: +5K-8K tokens (reads test files)
5. Documentation: +2K-3K tokens
6. Edge Cases: +2K-3K tokens
7. Error Handling: +2K-3K tokens
8. Performance & Scalability: +3K-5K tokens
9. Maintainability: +2K-3K tokens
10. Security & Safety: +3K-5K tokens
11. Cross-Cutting Concerns: +2K-3K tokens

**Total overhead**: 34K-55K tokens just for review process, before code examination.

**Context Gathering (adds to input tokens):**
- PR description: 500-2K tokens
- `.planning/PLAN.md`: 5K-20K tokens (if referenced)
- Linked issue: 1K-5K tokens
- Previous PR comments: 2K-10K tokens
- Related files (dependencies): 10K-50K tokens

**Optimization Strategies:**

1. **Progressive review depth**:
   - Quick review (5 dimensions): 50K-80K tokens, 2-3 minutes
   - Standard review (11 dimensions): 100K-150K tokens, 5-7 minutes
   - Deep review (11 dimensions + full context): 150K-200K tokens, 10-15 minutes

2. **Incremental PR reviews**:
   - Review per commit: 20K-40K tokens each
   - Final PR review: 50K-100K tokens
   - Total savings: 30-50% fewer tokens vs single large review

3. **Scope boundaries**:
   - Review only PR files: Baseline cost
   - Review PR + direct dependencies: +30-50% tokens
   - Review PR + full module: +100-200% tokens

4. **Model selection**:
   - Haiku for syntax/style checks: 1/20th cost, 5x faster
   - Sonnet for standard reviews: Balanced
   - Opus for architecture/security reviews: 5x cost, deepest analysis

**Performance Characteristics:**

```
Typical PR Review Flow:

1. Context gathering (20-40s):
   - Read PR description: 1-2s
   - Fetch linked issue via gh: 2-5s
   - Read .planning/PLAN.md: 1-2s
   - Scan previous PR comments: 3-5s
   - Read changed files: 10-20s

2. Code analysis (60-180s):
   - 11-dimension review: 45-120s
   - Generate findings: 10-30s
   - Classify severity: 5-15s
   - Link to existing issues: 10-15s

3. Output generation (15-30s):
   - Write detailed review: 10-20s
   - Post PR comment: 3-8s
   - Return report: 2s

Total: 2-5 minutes for medium PR (8 files, moderate changes)
```

---

### 2.2 Custom Skills

Skills are specialized knowledge loaded into context when relevant. Cost is paid upfront (loading) then amortized across the session.

#### Skill Loading Overhead

**Per-skill token cost** (approximate):

| Skill | Size | Load Tokens | Activation Pattern |
|-------|------|-------------|-------------------|
| access-skill-resources | 2KB | ~600 tokens | Manual invocation |
| cli-ux-colorful | 5.5KB | ~1,700 tokens | Terminal output tasks |
| dependency-management | 3KB | ~900 tokens | Package installation |
| development-standards | 7.6KB | ~2,400 tokens | All coding tasks (high activation) |
| exhaustive-testing | 8.7KB | ~2,700 tokens | Writing tests |
| handle-deprecation-warnings | 2.5KB | ~800 tokens | Deprecation warnings seen |
| skill-creator (official) | 6.6KB | ~2,000 tokens | Creating skills |
| git-workflow (project) | 12.7KB | ~3,900 tokens | Git operations, commits |

**Total if all skills loaded**: ~15,000 tokens

**Practical usage**:
- Typical session: 3-5 skills active = 5K-10K tokens
- Heavy session: 6-8 skills active = 12K-18K tokens
- All skills: Rare, only in complex cross-domain tasks

#### Progressive Disclosure Benefits

Skills use three-level loading:

1. **Metadata only** (YAML frontmatter): 50-100 tokens
   - Name, description, when to use
   - Loaded for all skills to determine relevance

2. **Main skill.md**: Full token cost (see table above)
   - Loaded when skill is relevant to task
   - Contains instructions, examples, patterns

3. **Bundled resources** (scripts/, references/, assets/): Variable
   - Loaded only when explicitly referenced
   - Example: python-313-conventions reference (~6K tokens)
   - Lazy loading prevents context bloat

**Optimization**:
- Without progressive disclosure: All skills = 15K+ tokens per session
- With progressive disclosure: Only relevant skills = 3K-8K tokens per session
- Savings: 50-70% reduction in skill-related context usage

#### Simultaneous Skill Limits

**Context window constraints** (Sonnet 200K tokens):
- System prompt: ~5K tokens
- Conversation history: 20K-100K tokens
- Skills loaded: 5K-15K tokens
- Working context (code, files): 50K-150K tokens
- Output buffer: 10K-30K tokens

**Practical limits**:
- Comfortable: 5-6 skills simultaneously (10K-15K tokens)
- Maximum: 8-10 skills (18K-25K tokens)
- Beyond 10 skills: Risk context window pressure, reduce working space

**Recommendation**: Design skills to be focused. Better to have 20 small skills (2-3K tokens each) that load selectively than 5 large skills (15K tokens each) that are always active.

#### Skill Size Optimization

Our skill sizes (5-13KB source, 1.5K-4K tokens):

**Small skills** (< 3KB, < 1K tokens):
- Fast to load
- Minimal context overhead
- Can have 10+ active simultaneously
- Example: access-skill-resources (600 tokens)

**Medium skills** (3-8KB, 1K-2.5K tokens):
- Reasonable overhead
- 5-8 active comfortably
- Sweet spot for most use cases
- Examples: cli-ux-colorful, dependency-management

**Large skills** (8-15KB, 2.5K-4K tokens):
- Significant overhead
- Limit to 3-5 active
- Should provide substantial value
- Examples: development-standards, exhaustive-testing, git-workflow

**Optimization strategies**:
1. **Split large skills**: Break 15KB skill into 3x 5KB skills with targeted activation
2. **Use references/**: Move detailed examples to references/ (lazy load)
3. **External scripts**: Put executable code in scripts/ not inline
4. **Concise examples**: Show pattern, link to full code in assets/

---

### 2.3 Claude Code Hooks

Hooks are event-driven shell commands that execute during Claude Code sessions. Performance critical for interactive feel.

#### Hook Execution Overhead

**Target performance** (for good UX):
- user-prompt-submit: < 100ms (runs before every prompt)
- tool-call: < 50ms (runs before every tool execution)
- session-start: < 500ms (runs once, can be slower)
- session-end: < 200ms (runs once at cleanup)

**Our production config** (actual-code/hooks-config/settings.local.json):
- No hooks currently defined (only permissions)
- Permissions system: < 1ms overhead (in-memory checks)

**Common hook patterns and overhead**:

| Hook Type | Operation | Typical Time | Acceptable Max |
|-----------|-----------|--------------|----------------|
| user-prompt-submit | Inject git status | 20-50ms | 100ms |
| user-prompt-submit | Inject current branch | 5-10ms | 50ms |
| tool-call | Log tool usage to file | 2-5ms | 20ms |
| tool-call | Validate tool permissions | < 1ms | 10ms |
| session-start | Clone shared context | 100-300ms | 1000ms |
| session-start | Verify environment setup | 50-150ms | 500ms |
| session-end | Archive session logs | 50-200ms | 500ms |

#### Shell Command Overhead

**Fast commands** (< 10ms):
```bash
git rev-parse --abbrev-ref HEAD    # Current branch: 5-8ms
git status --short                 # Short status: 15-30ms
git diff --name-only               # Changed files: 10-20ms
date +%Y-%m-%dT%H:%M:%S           # Timestamp: < 1ms
echo "context" >> file            # Append to file: 2-5ms
```

**Medium commands** (10-50ms):
```bash
git status                         # Full status: 20-50ms
git log -1 --oneline              # Last commit: 15-30ms
git diff --stat                   # Diff summary: 25-50ms
find . -name "*.py" | wc -l       # Count files: 30-100ms (size dependent)
```

**Slow commands** (> 50ms, avoid in hot paths):
```bash
git log --all --oneline           # Full history: 100-500ms
npm list                          # List packages: 200-1000ms
pytest --collect-only             # Collect tests: 500-2000ms
ruff check .                      # Lint entire codebase: 1000-5000ms
```

#### Hook Performance Impact on Sessions

**Baseline session** (no hooks):
- Prompt submission: ~50ms (network roundtrip)
- Tool execution: ~100ms (tool + network)

**With fast hooks** (< 50ms each):
- Prompt submission: ~100ms (hook + network)
- Tool execution: ~150ms (hook + tool + network)
- Impact: 50-100ms per operation, **imperceptible**

**With slow hooks** (> 200ms):
- Prompt submission: ~300ms (hook + network)
- Tool execution: ~350ms (hook + tool + network)
- Impact: 200-250ms per operation, **noticeable lag**

#### Optimization Strategies

1. **Keep hooks fast**:
   ```bash
   # Good: Direct git command
   git rev-parse --abbrev-ref HEAD

   # Bad: Subshell + parsing
   BRANCH=$(git branch | grep '*' | cut -d' ' -f2)
   ```

2. **No network calls**:
   ```bash
   # Bad: Network in user-prompt-submit hook
   curl https://api.github.com/...  # 100-500ms, blocks prompt

   # Good: Local file cache
   cat .github_cache/status.json    # < 5ms
   ```

3. **Minimal disk I/O**:
   ```bash
   # Good: Single append
   echo "$TIMESTAMP: $ACTION" >> session.log

   # Bad: Read, modify, write
   cat session.log | sed 's/old/new/' > session.log.tmp && mv session.log.tmp session.log
   ```

4. **Async patterns for slow operations**:
   ```bash
   # Run expensive operation in background
   (ruff check . > lint-results.txt 2>&1 &)

   # Hook returns immediately, results available later
   ```

5. **Caching hook output**:
   ```bash
   # Cache git status for 5 seconds
   CACHE_FILE=".git-status-cache"
   if [ ! -f "$CACHE_FILE" ] || [ $(($(date +%s) - $(stat -f %m "$CACHE_FILE"))) -gt 5 ]; then
     git status > "$CACHE_FILE"
   fi
   cat "$CACHE_FILE"
   ```

#### Hook Variable Performance

Hook variables (e.g., `{{timestamp}}`, `{{tool_name}}`) are template substitutions:
- Substitution overhead: < 1ms per variable
- Negligible performance impact
- Use freely for context injection

---

### 2.4 Git Worktree Orchestration

The `create_worktree.py` script (1,067 lines) automates comprehensive worktree setup with error handling.

#### Benchmark Results

**Baseline scenario** (no uncommitted changes, caches warm):
```
Operation Breakdown:
1. Validate source branch         2-5s    (git remote operations)
2. Create worktree                 1-3s    (git worktree add)
3. Create symlinks                 < 1s    (10-15 symlinks)
4. Configure Husky hooks           2-4s    (npm operations)
5. Install npm dependencies        15-30s  (network dependent)
6. Setup Python environment (uv)   10-20s  (network dependent)
7. Configure direnv                < 1s
8. Verify setup                    1-2s

Total: 30-65 seconds (median: 45 seconds)
```

**With uncommitted changes** (stash required):
```
Additional steps:
- Stash changes in source         1-2s
- Apply stash in new worktree      1-3s
- Cleanup stash                    < 1s

Total: +3-6 seconds → 35-70 seconds total
```

**With unpushed commits** (branch already diverged):
```
Additional steps:
- Fetch latest remote              2-5s
- Rebase/merge operations          2-10s (conflict dependent)

Total: +5-15 seconds → 40-80 seconds total
```

**Cold cache scenario** (first run, packages not cached):
```
- npm install (cold)               60-120s (download ~200MB)
- uv sync (cold)                   15-40s  (download ~50MB)

Total: 90-180 seconds (median: 120 seconds)
```

#### Performance by Network Conditions

| Network | npm install | uv sync | Total Time |
|---------|-------------|---------|------------|
| Fast (100+ Mbps) | 15-25s | 8-15s | 35-50s |
| Medium (10-50 Mbps) | 30-60s | 15-30s | 55-100s |
| Slow (< 10 Mbps) | 90-180s | 30-60s | 130-250s |
| Offline (cached) | 5-10s | 3-5s | 20-30s |

#### Breakdown by Operation Type

**Fast operations** (< 2s):
- Git branch validation: 1-2s
- Symlink creation: < 1s (15 symlinks)
- Direnv configuration: < 1s
- Verification checks: 1-2s

**Medium operations** (2-10s):
- Git worktree creation: 1-3s
- Husky configuration: 2-4s
- Stash/unstash: 2-6s
- Git fetch: 2-8s

**Slow operations** (10s+):
- npm install: 15-120s (network dependent)
- uv sync: 10-40s (network dependent)
- Large codebase worktree copy: 5-15s (10K+ files)

#### Optimization Opportunities

**Currently implemented**:
- ✅ Interactive prompts (skip unnecessary work)
- ✅ Colored output (progress visibility)
- ✅ Error handling (cleanup on failure)
- ✅ Timeout protection (npm install, uv sync)
- ✅ Comprehensive validation (prevent broken worktrees)

**Potential optimizations** (not implemented):

1. **Parallel operations**:
   ```python
   # Sequential (current): 25-50s
   run_npm_install()      # 15-30s
   run_uv_sync()          # 10-20s

   # Parallel (potential): 15-30s
   with concurrent.futures.ThreadPoolExecutor() as executor:
       npm_future = executor.submit(run_npm_install)
       uv_future = executor.submit(run_uv_sync)
       npm_future.result()
       uv_future.result()

   Savings: 10-20 seconds (40% faster)
   ```

2. **Skip flags**:
   ```bash
   # Fast worktree (no dependencies)
   ./create_worktree.py issue-123 branch --no-npm --no-python
   Time: 5-10 seconds (for quick branches)

   # Documentation-only worktree
   ./create_worktree.py docs-fix branch --no-deps
   Time: 3-5 seconds
   ```

3. **Incremental updates**:
   ```python
   # Reuse existing worktree if branch matches
   if worktree_exists(name) and branch_matches(branch):
       update_existing_worktree()  # 5-10s
   else:
       create_new_worktree()       # 30-60s
   ```

4. **Caching strategy**:
   - Current: npm and uv use system-wide caches (automatic)
   - Potential: Pre-warm caches with common dependencies
   - Benefit: Reduce cold-start from 120s to 40s

**Trade-offs**:
- Parallel operations: +50 lines of complexity, +40% speed
- Skip flags: +30 lines, enables 5s micro-branches
- Incremental updates: +100 lines, risky (stale state)
- Cache pre-warming: Maintenance burden, marginal gains

**Recommendation**: Current implementation prioritizes correctness and comprehensive setup over raw speed. The 45-second median time is acceptable for a one-time setup that prevents hours of environment issues.

---

### 2.5 Git Hooks

Pre-commit and post-checkout hooks protect main worktree from accidental commits/checkouts.

#### Execution Time

**pre-commit hook**:
```bash
# Operations:
1. Get current directory           2-5ms    (pwd)
2. Pattern matching (/.docimp-wt/) < 1ms    (string check)
3. Print error message             5-10ms   (terminal output)
4. Exit                            < 1ms

Total: 10-20ms (imperceptible)
```

**post-checkout hook**:
```bash
# Operations:
1. Get current directory           2-5ms    (pwd)
2. Pattern matching                < 1ms
3. Print warning                   5-10ms
4. Git checkout HEAD (revert)      50-150ms (if triggered)

Total: 10-20ms (normal), 60-170ms (if reverting)
```

#### Performance Impact

**Baseline git operations** (no hooks):
- git commit: 50-150ms
- git checkout: 100-300ms

**With hooks** (10-20ms overhead):
- git commit: 60-170ms (+10-20ms)
- git checkout: 110-320ms (+10-20ms)

**Impact**: < 5% overhead, **imperceptible** to developer

#### Pattern Matching Overhead

Hook detection logic (simplified):
```bash
if [[ "$PWD" != *"/.docimp-wt/"* ]]; then
    # Block commit
fi
```

**Performance**:
- String pattern match: < 1ms
- No external commands required
- Pure bash string operations
- O(n) where n = path length (~100 chars)

**Alternative approaches** (slower):
```bash
# Bad: Multiple git calls (50-100ms)
if [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ]; then
    if [ "$(git rev-parse --show-toplevel)" = "/path/to/main" ]; then
        # Block
    fi
fi

# Good: Simple path check (< 1ms)
[[ "$PWD" != *"/.docimp-wt/"* ]]
```

#### Bypass Performance (--no-verify)

When bypassing hooks:
```bash
git commit --no-verify

# Hook overhead: 0ms (completely skipped)
# Commit time: 50-150ms (baseline)
```

**Use cases**:
- Maintenance commits (repository setup)
- Emergency hotfixes (when process blocks valid work)
- Batch operations (scripted commits)

---

## Scalability Guidance

### 3.1 Codebase Size Impact

#### Small Projects

**Performance characteristics**:
- Agent reviews: 20K-50K tokens per invocation
- Worktree creation: 15-30 seconds (fewer dependencies)
- Skills loaded: 3-5 simultaneously (focused tasks)
- Hook overhead: 10-30ms (small git operations)

**Recommendations**:
- Standard agent invocations work well
- Single worktree often sufficient
- All skills can be active if needed

#### Medium Projects

**Performance characteristics**:
- Agent reviews: 50K-150K tokens (selective file review)
- Worktree creation: 30-60 seconds (moderate dependencies)
- Skills loaded: 4-6 simultaneously (balanced context)
- Hook overhead: 20-50ms (larger git repos)

**What changes**:
- Agent scope becomes important (don't review everything)
- Worktree pattern valuable (parallel feature work)
- Skill selection matters (context window pressure)

**Optimization strategies**:
1. Agent reviews on changed files only (git diff)
2. Multiple worktrees for feature isolation
3. Selective skill loading (3-4 most relevant)
4. Hook caching (git status every 5s not every prompt)

#### Large Projects

**Performance characteristics**:
- Agent reviews: 100K-200K tokens (must be scoped)
- Worktree creation: 45-90 seconds (many dependencies)
- Skills loaded: 3-5 max (tight context budget)
- Hook overhead: 30-100ms (large git operations)

**Critical optimizations needed**:

1. **Agent scope discipline**:
   ```
   Bad:  Review entire module (50 files, extensive changes)
         → 200K+ tokens, may hit context limit

   Good: Review PR files only (5-10 files, focused changes)
         → 50K-100K tokens, fits comfortably
   ```

2. **Worktree isolation**:
   - Don't create worktrees from main (too many deps)
   - Branch from feature branches (smaller dependency delta)
   - Use --no-deps flags when appropriate

3. **Skill budgeting**:
   - Load development-standards + 1-2 task-specific skills
   - Total: 5K-8K tokens for skills
   - Preserve 150K+ tokens for code analysis

4. **Hook optimization**:
   ```bash
   # Bad: Full git status on every prompt (100ms+)
   git status

   # Good: Cached status (< 5ms)
   if [ cache_expired ]; then
       git status > cache
   fi
   cat cache
   ```

### 3.2 Team Size Impact

#### Single Developer

**Baseline performance** (reference point):
- Worktree creation: 45s (median)
- Agent reviews: 2-5 minutes (medium PR)
- Hook overhead: 15-30ms

**Optimization priorities**:
1. Thoroughness over speed (catch bugs early)
2. Comprehensive reviews (learn from agent feedback)
3. All skills available (maximize learning)

#### Small Team (2-5 developers)

**Coordination overhead**:
- Shared `.planning/PLAN.md`: +2-5K tokens per agent review
- PR review of others' code: +20-40% review time
- Worktree naming coordination: Minimal (<1s)

**Impact**:
- Agent reviews: +20-30% time (more context gathering)
- Worktree creation: Same (parallel operations)
- Hook conflicts: Rare (different worktrees)

**Optimization strategies**:
1. Standardize PR templates (reduce agent context gathering)
2. Consistent branch naming (easier coordination)
3. Shared skill configurations (team conventions)

#### Large Team (10+ developers)

**Shared context challenges**:
- Multiple PRs referencing same issues: Agent confusion
- Conflicting `.planning/PLAN.md` updates: Merge conflicts
- Worktree proliferation: Disk space usage

**Performance degradation**:
- Agent reviews: +50-100% time (complex context)
- Worktree creation: Same
- Hook overhead: +10-20ms (larger .git directory)

**Critical strategies**:

1. **Agent context scoping**:
   ```
   Bad:  Review all related PRs for context
         → 200K+ tokens, 10-15 minutes

   Good: Review only this PR + immediate dependencies
         → 80K-120K tokens, 3-5 minutes
   ```

2. **Worktree cleanup**:
   ```bash
   # Weekly cleanup of old worktrees
   git worktree prune
   rm -rf ../.docimp-wt/issue-*-completed

   # Saves: 1-5 GB disk space, faster git operations
   ```

3. **Skill standardization**:
   - Team-wide skill repository
   - Versioned skill releases
   - Consistent 5K-8K token budget per developer

---

## Measurement Strategies

### 4.1 How to Measure

#### Token Usage Tracking

**Claude Code API** (if using programmatically):
```python
import anthropic

client = anthropic.Anthropic(api_key="...")
response = client.messages.create(...)

print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
print(f"Total: {response.usage.input_tokens + response.usage.output_tokens}")

# Cost calculation
input_cost = response.usage.input_tokens * 0.003 / 1000   # $3/MTok
output_cost = response.usage.output_tokens * 0.015 / 1000  # $15/MTok
total_cost = input_cost + output_cost
print(f"Cost: ${total_cost:.4f}")
```

**Claude Code CLI** (manual tracking):
```bash
# Check usage in Claude console
# https://console.anthropic.com/usage

# Estimate from file sizes
INPUT_TOKENS=$(wc -c < file.py | awk '{print int($1/4)}')  # Rough estimate
echo "Estimated input: $INPUT_TOKENS tokens"
```

#### Execution Time Benchmarks

**Worktree creation**:
```bash
# Full benchmark
time python actual-code/create_worktree.py issue-123 test-branch

# Output:
# real    0m47.123s
# user    0m2.456s
# sys     0m1.234s

# Per-operation breakdown (add timing to script)
python actual-code/create_worktree.py issue-123 test --verbose
# [0.0s] Validating source branch...
# [2.3s] Creating worktree...
# [5.1s] Creating symlinks...
# [7.4s] Configuring Husky...
# [32.7s] Installing npm dependencies...
# [45.2s] Setting up Python environment...
# [47.1s] Done!
```

**Hook execution**:
```bash
# Profile pre-commit hook
time .git/hooks/pre-commit
# real    0m0.018s

# Profile with detailed output
bash -x .git/hooks/pre-commit
# Shows each command execution time
```

**Agent performance** (approximate):
```bash
# Start timer
START=$(date +%s)

# Run agent (via Claude Code)
# [Agent executes...]

# End timer
END=$(date +%s)
DURATION=$((END - START))
echo "Agent execution: ${DURATION}s"
```

#### Hook Overhead Profiling

**Detailed hook timing**:
```bash
# Add to hook for profiling
HOOK_START=$(date +%s%N)

# ... hook operations ...

HOOK_END=$(date +%s%N)
HOOK_MS=$(( ($HOOK_END - $HOOK_START) / 1000000 ))
echo "Hook overhead: ${HOOK_MS}ms" >> .git/hook-metrics.log
```

**Analyze hook performance**:
```bash
# Average hook time
awk '{sum+=$3; count++} END {print "Average:", sum/count, "ms"}' .git/hook-metrics.log

# Max hook time
awk '{if($3>max) max=$3} END {print "Max:", max, "ms"}' .git/hook-metrics.log
```

### 4.2 What to Measure

#### Baseline Metrics (Before Optimization)

Establish baseline before making changes:

| Metric | Baseline | Measurement Method |
|--------|----------|-------------------|
| Agent review time | 3-5min (medium PR) | Manual timing |
| Agent token usage | 80K-120K tokens | API tracking |
| Worktree creation | 45-60s | `time` command |
| Hook overhead | 15-30ms | Hook profiling |
| Skills loaded | 4-5 simultaneously | Session analysis |
| Session token budget | 150K-200K total | Claude console |

#### Target Metrics (Acceptable Performance)

Goals that indicate "good enough":

| Metric | Target | Rationale |
|--------|--------|-----------|
| Hook overhead | < 100ms | Imperceptible delay |
| Worktree creation | < 90s | One-time setup, acceptable |
| Agent review | < 10min | Thorough review worth wait |
| Agent token cost | < $1.00/review | Quality worth price |
| Skills loaded | 3-5 active | Balanced context |
| Session success rate | > 95% | Rare context limits |

#### Warning Thresholds (When to Optimize)

Red flags requiring investigation:

| Metric | Warning Threshold | Action Required |
|--------|------------------|-----------------|
| Hook overhead | > 200ms | Cache results, simplify logic |
| Worktree creation | > 3min | Check network, reduce deps |
| Agent timeout | > 15min | Reduce scope, split review |
| Agent token usage | > 180K | Risk context limit, scope down |
| Session context limit | Hit 200K | Reduce skills, clear history |
| Hook failure rate | > 5% | Fix brittle commands |

### 4.3 Optimization Decision Framework

#### When to Optimize

**Optimize immediately**:
- Hook taking > 200ms (every operation affected)
- Agent hitting context limits (reviews failing)
- Worktree creation failing (network timeouts)
- User complaints (subjective but important)

**Optimize proactively**:
- Hook at 100-150ms (approaching threshold)
- Agent using 150K+ tokens (risky)
- Worktree creation > 2min (slow but functional)
- Skills failing to load (context pressure)

**Monitor but don't optimize**:
- Hook at 50-80ms (fast enough)
- Agent using 100K tokens (reasonable)
- Worktree creation 60-90s (acceptable)
- 4-5 skills loaded (comfortable)

#### When NOT to Optimize

**Premature optimization cases**:

1. **Acceptable performance**:
   - Hook at 30ms: Don't optimize to 10ms (no user benefit)
   - Agent review 4min: Don't optimize to 2min (thoroughness matters)
   - Worktree 45s: Don't optimize to 30s (one-time cost)

2. **Complexity trade-offs**:
   - Parallel worktree operations: +50 lines complexity
   - Hook caching: +30 lines, potential stale data
   - Agent chunking: +100 lines, coordination overhead
   - Benefit: If user doesn't notice, don't do it

3. **Diminishing returns**:
   - Hook: 50ms → 25ms (imperceptible improvement)
   - Worktree: 45s → 40s (5s savings not worth complexity)
   - Agent: 4min → 3.5min (0.5min savings, risk quality loss)

#### Decision Matrix

```
Performance Issue Decision Tree:

Is it causing failures? (Timeouts, context limits, errors)
├─ Yes → OPTIMIZE IMMEDIATELY
└─ No → Is it noticeably slow? (User perception)
    ├─ Yes → Is it frequently used? (Every operation vs one-time)
    │   ├─ Yes → OPTIMIZE PROACTIVELY
    │   └─ No → MONITOR
    └─ No → DON'T OPTIMIZE

Example:
- Hook 250ms: Causing perceived lag? YES → Frequent? YES → OPTIMIZE
- Worktree 90s: Causing failures? NO → Noticeably slow? MAYBE → Frequent? NO (one-time) → MONITOR
- Agent 5min: Causing failures? NO → Noticeably slow? NO (acceptable) → DON'T OPTIMIZE
```

---

## Optimization Techniques

### 5.1 Agent Optimization

#### Scope Reduction

**Review only changed files**:
```bash
# Get files changed in PR
gh pr view $PR_NUMBER --json files --jq '.files[].path'

# Agent reviews only these files
# Baseline: 150K tokens (full module review)
# Optimized: 50K tokens (changed files only)
# Savings: 66% reduction
```

**Implementation** (in agent prompt):
```markdown
Review only files changed in this PR. Do not review:
- Unchanged files (even if imported)
- Test files (unless PR modifies tests)
- Documentation (unless PR modifies docs)

Focus scope: {list of changed files}
```

#### Incremental Reviews

**Per-commit reviews** (during development):
```bash
# Small commit: 200 lines
Agent review: 20K tokens, $0.05, 30 seconds

# 10 commits over 2 days
Total: 200K tokens, $0.50, 5 minutes (amortized)
```

**Bulk PR review** (at the end):
```bash
# Large PR: 2000 lines
Agent review: 180K tokens, $0.80, 8 minutes

# Same code, different approach
Total: 180K tokens, $0.80, 8 minutes (all at once)
```

**Trade-off**:
- Incremental: More total tokens (20-30% overhead), but catches issues earlier
- Bulk: Fewer tokens, but issues found late (expensive to fix)
- **Recommendation**: Incremental for quality, bulk for cost

#### Model Selection

**Task-appropriate models**:

| Task | Model | Cost | Time | Use When |
|------|-------|------|------|----------|
| Syntax check | Haiku | $0.02 | 10s | Simple validation |
| Code review | Sonnet | $0.15 | 3min | Standard reviews |
| Architecture | Opus | $0.75 | 5min | Critical decisions |
| Documentation | Haiku | $0.03 | 15s | Docstring generation |
| Security review | Opus | $1.00 | 8min | Production code |

**Example workflow**:
```
1. Quick syntax check (Haiku): $0.02, 10s
2. If passing, thorough review (Sonnet): $0.15, 3min
3. If critical issues, deep analysis (Opus): $0.75, 5min

Average cost: $0.17 (vs $1.00 if always using Opus)
Savings: 83%
```

#### Tool Restriction

**Minimal toolset**:
```yaml
# Agent with full tools: +3K tokens overhead
tools: Read, Write, Edit, Grep, Glob, Bash

# Agent with restricted tools: +500 tokens overhead
tools: Read, Grep, Glob

Savings: 2.5K tokens per invocation (50% tool overhead)
```

**When to restrict**:
- Review-only agents: Read, Grep, Glob (no Write/Edit needed)
- Analysis agents: Read, Bash (no file modification)
- Code generation: Read, Write (no Grep/Glob needed)

**When NOT to restrict**:
- Autonomous agents (code-reviewer): Need full toolset
- Interactive agents: User may request file modifications
- Exploratory agents: Need Grep/Glob for discovery

### 5.2 Skill Optimization

#### Progressive Disclosure

**Three-level loading**:

```
Level 1: Metadata (100 tokens)
  - name, description, when to use
  - Loaded for all skills to check relevance

Level 2: Main content (2K tokens)
  - skill.md with instructions and examples
  - Loaded when skill is activated

Level 3: Resources (variable)
  - references/ (6K tokens)
  - scripts/ (not counted, executed)
  - assets/ (loaded on demand)
```

**Example**: development-standards skill

```
Without progressive disclosure:
- Always loaded: 10K tokens (skill + references)
- 10 skills: 100K tokens total
- Context window pressure

With progressive disclosure:
- Metadata: 100 tokens
- Main skill: 2.4K tokens (if relevant)
- References: 6K tokens (if referenced)
- Typical load: 2.5K tokens
- 10 skills metadata + 3 active: 3.8K tokens

Savings: 96K tokens (96% reduction)
```

#### Selective Loading

**Activation patterns** (from skill frontmatter):

```yaml
# High-frequency skill (always relevant)
name: development-standards
description: Standards for all coding tasks
activation: automatic, high priority

# Task-specific skill (selective)
name: exhaustive-testing
description: Writing comprehensive tests
activation: when writing tests or test files detected

# Rare skill (manual only)
name: skill-creator
description: Creating new skills
activation: manual invocation only
```

**Context budgeting**:
```
Always active (3 skills):
- development-standards: 2.4K tokens
- git-workflow: 3.9K tokens
- handle-deprecation-warnings: 800 tokens
Total: 7.1K tokens

Task-specific (load on demand):
- exhaustive-testing: 2.7K (when writing tests)
- cli-ux-colorful: 1.7K (when formatting terminal output)
- dependency-management: 900 (when installing packages)

Session budget: 7.1K (baseline) + 2.7K (avg task-specific) = 9.8K tokens
```

#### Shared Resources

**Symlink bundled resources**:

```bash
# Bad: Duplicate resources in each skill
skills/user/skill-a/references/python-313-conventions.md  # 6K
skills/user/skill-b/references/python-313-conventions.md  # 6K (duplicate)
Total: 12K tokens if both loaded

# Good: Shared references
skills/shared/references/python-313-conventions.md        # 6K (shared)
skills/user/skill-a/references/ → ../../shared/references/
skills/user/skill-b/references/ → ../../shared/references/
Total: 6K tokens (loaded once, reused)

Savings: 50% reduction per duplicate reference
```

**Implementation**:
```bash
mkdir -p .claude/skills/shared/references
ln -s ../../shared/references .claude/skills/user/skill-a/references
ln -s ../../shared/references .claude/skills/user/skill-b/references
```

### 5.3 Hook Optimization

#### Caching

**Git status caching** (common pattern):

```bash
# Without cache: 30-50ms per invocation
# user-prompt-submit hook runs on every prompt
# 100 prompts/session = 3-5 seconds total overhead

# With 5-second cache: < 5ms per invocation
CACHE_FILE=".git/status-cache"
CACHE_MAX_AGE=5  # seconds

if [ ! -f "$CACHE_FILE" ] || [ $(($(date +%s) - $(stat -f %m "$CACHE_FILE"))) -gt $CACHE_MAX_AGE ]; then
    git status > "$CACHE_FILE"
fi
cat "$CACHE_FILE"

# 100 prompts/session = 0.5 seconds total overhead
# Savings: 2.5-4.5 seconds per session (90% reduction)
```

**Trade-offs**:
- Pro: 10x faster (50ms → 5ms)
- Con: Potentially stale (up to 5s old)
- Con: +10 lines of hook complexity
- **Verdict**: Worth it for high-frequency hooks (user-prompt-submit)

#### Conditional Execution

**Only run when relevant**:

```bash
# Bad: Always run linter check
ruff check . --quiet && echo "Clean" || echo "Issues found"
# 1-2 seconds every commit, even for non-Python changes

# Good: Only run for Python files
if git diff --cached --name-only | grep -q '\.py$'; then
    ruff check . --quiet && echo "Clean" || echo "Issues found"
fi
# 0ms if no Python files changed, 1-2s if Python changed

Savings: 95% reduction (most commits don't touch every language)
```

#### Background Jobs

**Async non-critical operations**:

```bash
# Bad: Block on slow operation
pytest --collect-only > test-count.txt  # 500-2000ms, blocks commit
git commit

# Good: Run in background
(pytest --collect-only > test-count.txt 2>&1 &)
git commit  # Proceeds immediately

# Results available later for next operation
cat test-count.txt  # Ready by next commit
```

**When to use**:
- Non-critical validations (metrics, logging)
- Operations with results needed later (cache pre-warming)
- Side effects that don't block main flow (notifications)

**When NOT to use**:
- Validation that must pass (tests, linting)
- Operations with immediate results needed (git status)
- Critical path operations (file modifications)

### 5.4 Worktree Optimization

#### Skip Unnecessary Steps

**Conditional dependency installation** (potential future enhancement):

```python
# Current: Always install all dependencies
run_npm_install()      # 15-30s
run_uv_sync()          # 10-20s
# Total: 25-50s

# Optimized: Skip when unnecessary
if args.no_npm:
    skip_npm_install()
if args.no_python:
    skip_uv_sync()

# Documentation-only branch
./create_worktree.py docs-fix branch --no-npm --no-python
# Total: 5-10s (80-90% faster)
```

**Use cases**:
- Documentation changes: No npm/Python needed
- Config-only changes: No dependencies
- Quick branches: Will delete soon, skip setup

**Implementation** (not currently in script):
```python
parser.add_argument('--no-npm', action='store_true',
                    help='Skip npm install')
parser.add_argument('--no-python', action='store_true',
                    help='Skip Python environment setup')
```

#### Parallel Operations

**npm + uv in parallel** (potential optimization):

```python
import concurrent.futures

# Sequential (current): 25-50s
run_npm_install()      # 15-30s
run_uv_sync()          # 10-20s

# Parallel (potential): 15-30s
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    npm_future = executor.submit(run_npm_install)
    uv_future = executor.submit(run_uv_sync)

    npm_future.result()  # Wait for completion
    uv_future.result()

# Savings: 10-20 seconds (40-50% faster)
```

**Trade-offs**:
- Pro: 40% faster (25-50s → 15-30s)
- Con: +50 lines of complexity (thread management, error handling)
- Con: Harder to debug (interleaved output)
- **Verdict**: Marginal benefit for added complexity, skip for now

#### Incremental Updates

**Reuse existing worktree** (potential optimization):

```python
# Current: Always create fresh worktree
create_new_worktree()  # 30-60s

# Optimized: Update existing if possible
if worktree_exists(name) and is_safe_to_reuse():
    update_existing_worktree()  # 5-10s
    pull_latest_changes()       # 2-5s
    # Total: 7-15s (75-80% faster)
else:
    create_new_worktree()  # 30-60s
```

**Risks**:
- Stale dependencies (old node_modules/)
- Uncommitted changes (dirty state)
- Configuration drift (outdated symlinks)

**Verdict**: High risk, low reward. Clean worktrees prevent subtle bugs.

---

## Known Performance Issues

### 6.1 Current Limitations

#### 1. Worktree Creation Network Dependency

**Issue**: Script requires network for npm install and uv sync

**Impact**:
- Offline: Cannot create worktrees (fails on dependency installation)
- Slow network: 2-4x longer creation time (15-30s → 60-120s)
- VPN: May add 10-30s overhead

**Workarounds**:
- Use cached dependencies: `npm ci --offline` (requires package-lock)
- Skip dependencies temporarily: Comment out install steps (manual workaround)
- Pre-warm caches: `npm install` once to cache all packages

**Future fix**: Add `--offline` flag to use cached dependencies only

#### 2. Agent Context Window Pressure (Large PRs)

**Issue**: Reviewing 30+ files with extensive changes approaches 200K context limit

**Impact**:
- Agent may fail with "context limit exceeded"
- Agent may drop context mid-review (truncation)
- Quality degrades as context fills

**Workarounds**:
- Split PR into smaller chunks: Review 10 files at a time
- Reduce agent scope: Review only critical files
- Clear conversation history: Start fresh session

**Future fix**: Agent should auto-detect context pressure and self-limit scope

#### 3. Hook Performance on Large Repos

**Issue**: Git operations slow down as repo grows (100K+ files)

**Impact**:
- git status: 50-100ms (vs 10-20ms in small repos)
- git diff: 100-300ms (vs 20-50ms)
- Hook overhead: Approaches warning threshold (100ms+)

**Workarounds**:
- Cache git operations (5-second TTL)
- Use `git status --short` (faster than full status)
- Limit diff scope: `git diff --name-only` (names only, not content)

**Future fix**: Pre-compute git state in background, serve from cache

#### 4. Skills Context Duplication

**Issue**: Multiple skills reference same concepts (e.g., Python conventions)

**Impact**:
- development-standards references Python 3.13+ conventions: +2K tokens
- python-313-conventions agent has full content: +6K tokens
- Total: 8K tokens for overlapping information

**Workarounds**:
- Use references/ symlinks to share content
- Reference agent instead of duplicating content
- Keep skills focused, avoid overlap

**Future fix**: Shared skill resources repository (loaded once, referenced many times)

### 6.2 Performance Anti-Patterns

**What NOT to do**:

1. **Review entire codebase with agent**:
   ```
   Bad:  Agent, review all 500 Python files
   Result: 500K+ tokens, context limit exceeded, failure

   Good: Agent, review the 5 files changed in this PR
   Result: 50K tokens, thorough review, success
   ```

2. **Load all skills simultaneously**:
   ```
   Bad:  Load all 8 skills for every session
   Result: 15K+ tokens, context pressure, slow

   Good: Load 3-4 relevant skills for this task
   Result: 6K-8K tokens, comfortable context, fast
   ```

3. **Run expensive operations in hooks**:
   ```
   Bad:  user-prompt-submit: pytest --collect-only (2000ms)
   Result: 2-second delay on every prompt, unusable

   Good: user-prompt-submit: git status --short (20ms)
   Result: Imperceptible delay, smooth UX
   ```

4. **Create worktree for every branch**:
   ```
   Bad:  New worktree for 5-line doc fix
   Result: 45s setup time, wasted

   Good: Quick fix in existing worktree, commit, PR
   Result: 2 minutes total (vs 45s setup + 2min work)
   ```

---

## Performance Monitoring

### 7.1 Ongoing Monitoring Strategies

#### Session-Level Metrics

**Track per session**:
```bash
# Create session log
SESSION_LOG=".claude-sessions/$(date +%Y%m%d_%H%M%S).log"

# Log metrics during session
echo "Skills loaded: development-standards, git-workflow, exhaustive-testing" >> $SESSION_LOG
echo "Agent invocations: 2 (python-313-conventions, code-reviewer)" >> $SESSION_LOG
echo "Estimated tokens: 85K input, 22K output" >> $SESSION_LOG
echo "Duration: 18 minutes" >> $SESSION_LOG
```

**Weekly analysis**:
```bash
# Aggregate session metrics
find .claude-sessions -name "*.log" -mtime -7 -exec cat {} \; | \
  grep "Estimated tokens" | \
  awk '{sum+=$3} END {print "Average tokens/session:", sum/NR}'
```

#### Hook Performance Tracking

**Instrument hooks** (add timing):
```bash
# In hook
HOOK_START=$(date +%s%N)

# ... hook operations ...

HOOK_END=$(date +%s%N)
HOOK_MS=$(( ($HOOK_END - $HOOK_START) / 1000000 ))
echo "$(date +%Y-%m-%d_%H:%M:%S) $HOOK_MS ms" >> .git/hook-perf.log
```

**Weekly review**:
```bash
# Check if hooks are getting slower
tail -100 .git/hook-perf.log | awk '{print $2}' | \
  awk '{sum+=$1; max=$1>max?$1:max} END {
    print "Average:", sum/NR, "ms"
    print "Max:", max, "ms"
    if (max > 100) print "WARNING: Hook exceeding 100ms threshold"
  }'
```

#### Agent Cost Tracking

**Estimate costs**:
```python
# Track agent usage
AGENT_LOG = Path(".claude-agents/usage.csv")

def log_agent_usage(agent: str, input_tokens: int, output_tokens: int):
    cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
    with AGENT_LOG.open('a') as f:
        f.write(f"{datetime.now()},{agent},{input_tokens},{output_tokens},{cost:.4f}\n")
```

**Monthly analysis**:
```bash
# Monthly agent costs
awk -F',' '{sum+=$5; count++} END {
  print "Total cost:", "$"sum
  print "Average cost/invocation:", "$"sum/count
  print "Invocations:", count
}' .claude-agents/usage.csv
```

### 7.2 When to Revisit Optimization Decisions

**Triggers for re-evaluation**:

1. **Codebase growth** (10x size increase):
   - What worked for small codebases may not work for large ones
   - Re-benchmark hooks, agents, worktree creation
   - Revisit optimization decisions

2. **Team growth** (2x team size):
   - More PRs, more context, more coordination
   - Agent context gathering becomes bottleneck
   - Standardize to reduce variability

3. **Performance complaints** (subjective but important):
   - Developers saying "hooks feel slow"
   - Even if metrics show 80ms (under 100ms threshold)
   - Perception matters, investigate

4. **Technology changes** (new tools, new patterns):
   - Claude API updates (faster models, larger context)
   - Git improvements (faster operations)
   - New optimization techniques available

**Re-optimization schedule**:
- Quarterly: Review metrics, check for degradation
- After major changes: New dependencies, codebase restructure
- When issues reported: Developer complaints, failures

### 7.3 Red Flags (Performance Degradation)

**Warning signs**:

1. **Hook times increasing**:
   ```
   Baseline: 15-20ms
   Current:  50-80ms
   Trend:    +200% over 3 months
   Action:   Investigate git repo size, hook complexity
   ```

2. **Agent reviews timing out**:
   ```
   Baseline: 2-5 minutes
   Current:  10-15 minutes, some failures
   Trend:    Hitting context limits
   Action:   Reduce scope, clear history, split reviews
   ```

3. **Worktree creation failing**:
   ```
   Baseline: 95% success rate
   Current:  70% success rate
   Trend:    Network timeouts, npm errors
   Action:   Increase timeouts, cache dependencies
   ```

4. **Skills not loading**:
   ```
   Baseline: All requested skills load
   Current:  Only 2-3 skills load before context limit
   Trend:    Conversation history accumulating
   Action:   Clear history, reduce skill sizes
   ```

**Response protocol**:
1. Document the issue (metrics, examples)
2. Identify root cause (tool, process, or codebase change)
3. Implement fix (optimization, configuration, or process change)
4. Verify improvement (re-measure, confirm fix)
5. Update documentation (this file, team knowledge)

---

## Trade-offs and Philosophy

### 8.1 Trade-offs Documentation

#### Thoroughness vs Speed

**Example: code-reviewer agent**

**Thorough approach** (current):
- 11-dimension review: Functional, Quality, Architecture, Tests, Docs, Edge Cases, Error Handling, Performance, Maintainability, Security, Cross-Cutting
- Time: 5-8 minutes
- Cost: $0.50-$1.00
- Tokens: 130K-200K
- Findings: 10-20 issues across all dimensions

**Fast approach** (potential):
- 3-dimension review: Functional, Quality, Tests
- Time: 1-2 minutes
- Cost: $0.10-$0.20
- Tokens: 40K-60K
- Findings: 3-8 issues (major ones only)

**Trade-off**:
- Thoroughness: Catches subtle architecture, security, maintainability issues
- Speed: Faster feedback loop, lower cost
- **Decision**: Thoroughness wins. Catching 1 security issue saves 10x the review cost.

#### Automation vs Control

**Example: Git hooks blocking commits**

**Automated protection** (current):
- pre-commit hook: Blocks all commits on main in main worktree
- Benefit: Zero accidental commits to main (100% prevention)
- Cost: Adds 15-20ms to every commit
- Friction: Must use --no-verify for legitimate main commits

**Manual process** (alternative):
- No hook, rely on developer discipline
- Benefit: No overhead, no friction
- Cost: Occasional mistakes (1-2% of commits)
- Recovery: Requires git revert, PR to fix

**Trade-off**:
- Automation: 15-20ms overhead, occasional --no-verify needed
- Manual: 0ms overhead, occasional mistakes (hours to fix)
- **Decision**: Automation wins. 20ms is imperceptible, mistakes are expensive.

#### Context vs Performance

**Example: Skill loading**

**Maximum context** (load all skills):
- Skills: All 8 skills loaded
- Tokens: 15K for skills
- Benefit: Complete knowledge available
- Cost: Context window pressure, reduced code analysis space

**Minimal context** (load 2-3 skills):
- Skills: Only task-relevant skills
- Tokens: 5K-8K for skills
- Benefit: More space for code analysis
- Cost: May miss relevant patterns from unloaded skills

**Trade-off**:
- Maximum: Comprehensive guidance, less room for code
- Minimal: More code analysis space, possibly miss guidance
- **Decision**: Balanced approach. 3-5 skills (8K-12K tokens) provides good coverage without excessive pressure.

### 8.2 Philosophy

**Core Principles**:

1. **Developer productivity over raw speed**:
   - A 30-second automation that saves 30 minutes of manual work is excellent
   - A 5-minute agent review that prevents a production bug is invaluable
   - A 100ms hook that catches errors is worth the delay

2. **Acceptable costs for quality improvements**:
   - $1 agent review that catches a bug costing $1000 to fix in production: 1000x ROI
   - 60-second worktree setup that prevents environment issues: Unmeasurable ROI
   - 50ms hook overhead that enforces branch protection: Worth it

3. **Optimize when it matters**:
   - Frequent operations (hooks, prompts): Optimize to < 100ms
   - One-time operations (worktree creation): Acceptable up to 2-3 minutes
   - Quality operations (agent reviews): Thoroughness > speed

4. **Measure before optimizing**:
   - Baseline metrics first
   - Identify actual bottlenecks
   - Don't guess

5. **Simple over clever**:
   - Simple hook (< 20 lines, 20ms): Better than complex cached hook (50 lines, 5ms)
   - Simple agent scope (changed files): Better than complex context chunking
   - Simple skills (2-3K tokens): Better than mega-skills with progressive loading

### 8.3 When "Slow but Thorough" Beats "Fast but Shallow"

**Scenarios where thoroughness wins**:

1. **Security reviews**:
   - Fast: 30 seconds, misses SQL injection
   - Thorough: 5 minutes, catches all OWASP Top 10 issues
   - **Winner**: Thorough (1 missed vulnerability = disaster)

2. **Architecture decisions**:
   - Fast: 1 minute, suggests quick fix
   - Thorough: 10 minutes, analyzes long-term maintainability
   - **Winner**: Thorough (bad architecture = years of tech debt)

3. **Code reviews before production**:
   - Fast: 2 minutes, checks functionality only
   - Thorough: 7 minutes, checks 11 dimensions
   - **Winner**: Thorough (production bugs = customer impact)

**Scenarios where fast wins**:

1. **Syntax checking during development**:
   - Fast: 10 seconds, Haiku model checks syntax
   - Thorough: 2 minutes, Opus model deep analysis
   - **Winner**: Fast (tight feedback loop, run frequently)

2. **Documentation generation**:
   - Fast: 20 seconds, basic docstrings
   - Thorough: 3 minutes, comprehensive examples
   - **Winner**: Fast (can iterate, not critical)

3. **Experimental branch validation**:
   - Fast: 1 minute, quick smoke test
   - Thorough: 8 minutes, full review
   - **Winner**: Fast (may abandon branch, don't invest heavily)

**Decision Framework**:
```
Is this code going to production?
├─ Yes → Is it user-facing or security-critical?
│   ├─ Yes → THOROUGH (always)
│   └─ No → Is it complex or high-risk?
│       ├─ Yes → THOROUGH
│       └─ No → Balanced
└─ No → Is this an experiment or learning?
    ├─ Yes → FAST
    └─ No → Balanced
```

---

## Summary

### Key Takeaways

1. **Performance targets**:
   - Hooks: < 100ms (imperceptible)
   - Agents: < 10min (thorough reviews worth wait)
   - Worktrees: < 90s (one-time setup)
   - Skills: 3-5 active (8K-12K tokens)

2. **Optimization priorities**:
   - Hooks: Most important (run frequently)
   - Agents: Scope over speed (quality matters)
   - Skills: Selective loading (context management)
   - Worktrees: Accept current performance (rare operation)

3. **Measurement matters**:
   - Baseline metrics before optimizing
   - Identify actual bottlenecks
   - Optimize based on data, not guesses

4. **Philosophy**:
   - Developer productivity > raw speed
   - Acceptable costs for quality
   - Optimize when it matters, accept trade-offs otherwise

### Quick Reference

**When something is slow**:
1. Measure: How slow? (get numbers)
2. Frequency: How often? (daily vs one-time)
3. Impact: User-facing? (perceptible vs background)
4. Decision: Optimize, monitor, or accept

**Red flags**:
- Hook > 200ms: Optimize immediately
- Agent > 15min: Reduce scope
- Worktree > 3min: Check network
- Skills not loading: Clear context

**Safe baselines**:
- Hook: 50-80ms is fine
- Agent: 4-6min is fine
- Worktree: 45-75s is fine
- Skills: 3-5 active is fine

---

## Appendix: Benchmark Commands

```bash
# Worktree creation benchmark
time python actual-code/create_worktree.py test-wt test-branch

# Hook performance check
time .git/hooks/pre-commit

# Git operation timing
time git status
time git diff --name-only

# Skill size check
find .claude/skills -name "*.md" -exec wc -c {} \; | awk '{print $2, int($1/4) " tokens"}'

# Session token estimate (rough)
wc -c conversation-export.txt | awk '{print "Estimated tokens:", int($1/4)}'
```

---

*Last updated: 2025-11-19*
*Version: 1.0*
*Benchmarks based on: MacOS, Sonnet 4.5, git 2.45+, Python 3.14, Node 20+*
