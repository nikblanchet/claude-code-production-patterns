# Infrastructure Documentation: Standardization & Documentation Patterns

## Overview

DocImp's infrastructure follows consistent patterns across codebases, languages, and tools. This standardization enables:

- **Predictable behavior** across Python, TypeScript, and JavaScript
- **Easy onboarding** via clear, documented patterns
- **Maintainable complexity** through separation of concerns
- **Evolution-ready architecture** with schema versioning and migration

This document catalogs the five major standardization patterns that form the backbone of DocImp's infrastructure:

1. **External Documentation Pattern** - Managing CLAUDE.md size limits
2. **Error Handling Pattern** - Three-layer architecture
3. **Dependency Injection Pattern** - Constructor injection with entry-point instantiation
4. **Configuration System** - JavaScript-based configuration
5. **Schema Versioning** - Workflow state and session state migration

---

## 1. External Documentation Pattern

### Problem Statement

**CLAUDE.md has a 40,000 character absolute maximum.** When project documentation exceeds this limit:
- Claude Code cannot read the file completely
- Critical guidance gets truncated
- Development workflow breaks

**Challenge**: DocImp has 68KB+ of technical documentation across multiple patterns.

### Solution Architecture

**Modular documentation with import references:**

```
CLAUDE.md (27.8 KB)
├─ Core commands and quick reference
├─ Architecture overview
└─ Import references: @docs/patterns/filename.md

docs/patterns/ (public, committed)
├─ error-handling.md (2.3 KB)
├─ dependency-injection.md (7.1 KB)
├─ testing-strategy.md (2.8 KB)
├─ transaction-integration.md (14.2 KB)
├─ session-resume.md (23.5 KB)
└─ workflow-state-management.md (28.9 KB)

Total: 27.8 KB (CLAUDE.md) + 78.8 KB (patterns) = 106.6 KB documentation
```

### Implementation Details

**CLAUDE.md Import Syntax:**

```markdown
## Error Handling Architecture

**Three-layer pattern**: Core functions → Command wrappers → Entry point.
Special case: UserCancellationError exits with code 0.

- @docs/patterns/error-handling.md
```

**Key Rules:**

1. **Character limit**: Keep CLAUDE.md under 40K characters
   - Check with: `wc -c CLAUDE.md`
   - Current: 27,792 bytes (69% capacity)

2. **Import depth**: Maximum 5 hops
   - Prevents circular references
   - Keeps documentation traversable

3. **What stays in CLAUDE.md**:
   - Commands and quick reference
   - Architecture overview
   - Common patterns (add parser, plugin, command)
   - Critical constraints (uv run prefix, Node 24+)

4. **What goes in docs/patterns/**:
   - Detailed implementation guides
   - Workflow examples
   - Design decision rationale
   - Testing strategies
   - Edge cases and troubleshooting

### Maintenance Workflow

**When to Update CLAUDE.md:**

- Architecture changes (new layers, data flows)
- New critical commands or workflows
- Major feature additions requiring immediate context
- Breaking changes to existing patterns

**How to Add External Docs:**

```bash
# 1. Check current size
wc -c CLAUDE.md
# Output: 27792 CLAUDE.md

# 2. If approaching 40K (35K+ is yellow zone):
#    Move detailed content to docs/patterns/

# 3. Create pattern file
vim docs/patterns/new-pattern.md

# 4. Add import reference in CLAUDE.md
echo "- @docs/patterns/new-pattern.md" >> CLAUDE.md

# 5. Commit both files
git add CLAUDE.md docs/patterns/new-pattern.md
git commit -m "Add new-pattern documentation"
```

**Quarterly Review:**

- Every 3 months or on major features
- Check CLAUDE.md size: `wc -c CLAUDE.md`
- Prune outdated content
- Move detailed examples to pattern files
- Update cross-references

### File Structure Example

**CLAUDE.md (Excerpt):**

```markdown
## Testing Strategy

**Commands**: `cd analyzer && uv run pytest -v` (Python), `cd cli && uv run npm test` (Jest)

**Test organization**: Python (`analyzer/tests/test_*.py`), TypeScript (`cli/src/__tests__/*.test.ts`).
Always create permanent test files, never ad-hoc validation scripts.

**Malformed syntax testing**: Gracefully handles syntax errors (parsers raise, analyzer tracks in
`parse_failures`, continues with valid files). Use `--strict` flag for CI/CD.

- @docs/patterns/testing-strategy.md
- @docs/development/TESTING.md
```

**docs/patterns/testing-strategy.md (Full Detail):**

```markdown
# Testing Strategy

## Test Organization (CRITICAL)

**Always create permanent test files, never ad-hoc validation scripts.** Tests must run in CI/CD,
catch regressions, and document expected behavior.

### Python Tests (`analyzer/tests/test_*.py`)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Enable src.* imports
from src.parsers.python_parser import PythonParser
```

**Guidelines:**
- Import from `src.*` not `analyzer.src.*`
- Use `Path(__file__).parent.parent.parent` for project root in fixtures
- Focus: Parsers, scorer monotonicity, coverage calc, JSDoc writer patterns

[... 50+ more lines of detailed testing guidance ...]
```

### Benefits

**For Claude Code:**
- All documentation accessible within 40K limit
- Quick reference always available
- Detailed patterns on-demand

**For Developers:**
- Comprehensive documentation in one place
- Clear separation: quick reference vs deep dive
- Easy to update without breaking size limits

**For Maintenance:**
- Modular updates (change one pattern file)
- Version control friendly (smaller diffs)
- Can refactor docs without touching CLAUDE.md

### Monitoring and Alerts

**Character Count Script:**

```bash
#!/bin/bash
# .github/workflows/check-claude-md-size.yml

CLAUDE_MD="CLAUDE.md"
MAX_CHARS=40000
WARN_CHARS=35000

CHAR_COUNT=$(wc -c < "$CLAUDE_MD" | tr -d ' ')

if [ "$CHAR_COUNT" -ge "$MAX_CHARS" ]; then
  echo "ERROR: CLAUDE.md exceeds 40K character limit ($CHAR_COUNT chars)"
  exit 1
elif [ "$CHAR_COUNT" -ge "$WARN_CHARS" ]; then
  echo "WARNING: CLAUDE.md approaching limit ($CHAR_COUNT / $MAX_CHARS chars)"
  exit 0
else
  echo "OK: CLAUDE.md size: $CHAR_COUNT / $MAX_CHARS chars"
fi
```

**Pre-commit Hook Integration:**

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Check CLAUDE.md size before commit
if git diff --cached --name-only | grep -q "^CLAUDE.md$"; then
  CHAR_COUNT=$(wc -c < CLAUDE.md | tr -d ' ')
  if [ "$CHAR_COUNT" -gt 40000 ]; then
    echo "ERROR: CLAUDE.md exceeds 40K limit ($CHAR_COUNT chars)"
    echo "Move content to docs/patterns/ before committing"
    exit 1
  fi
fi
```

---

## 2. Error Handling Pattern

### Three-Layer Architecture

DocImp uses a consistent three-layer error handling pattern across all CLI commands:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Core Functions (Business Logic)              │
│  - Throws errors for exceptional conditions             │
│  - No knowledge of exit codes or process lifecycle      │
│  - Pure business logic, testable in isolation           │
└────────────────────┬────────────────────────────────────┘
                     │ throw Error
                     v
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Command Wrappers (CLI Interface)             │
│  - Catches errors from Core functions                   │
│  - Converts to exit codes (0 = success, 1 = error)      │
│  - Displays errors using display.showError()            │
└────────────────────┬────────────────────────────────────┘
                     │ return EXIT_CODE
                     v
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Entry Point (Process Lifecycle)              │
│  - Checks exit codes from Command wrappers              │
│  - Calls process.exit() ONLY when exitCode !== 0        │
│  - Only place in codebase where process.exit() called   │
└─────────────────────────────────────────────────────────┘
```

### Implementation Details

**Layer 1: Core Functions (Example: analyzeCore)**

```typescript
// cli/src/commands/analyzeCore.ts
export async function analyzeCore(
  path: string,
  options: AnalyzeOptions,
  bridge: IPythonBridge,
  display: IDisplay,
  configLoader: IConfigLoader
): Promise<void> {
  // Throws errors, never returns exit codes
  if (!existsSync(path)) {
    throw new Error(`Path not found: ${path}`);
  }

  const config = await configLoader.load(options.config);
  if (!config) {
    throw new Error('Failed to load configuration');
  }

  const result = await bridge.analyze({ path, config });
  if (!result) {
    throw new Error('Analysis failed');
  }

  display.showAnalysisResult(result);
  // No return value - success is implicit (no throw)
}
```

**Layer 2: Command Wrapper (Example: analyzeCommand)**

```typescript
// cli/src/commands/analyzeCommand.ts
import { EXIT_CODE } from '../constants/exitCodes.js';

export async function analyzeCommand(
  path: string,
  options: AnalyzeOptions,
  bridge: IPythonBridge,
  display: IDisplay,
  configLoader: IConfigLoader
): Promise<ExitCode> {
  try {
    await analyzeCore(path, options, bridge, display, configLoader);
    return EXIT_CODE.SUCCESS; // 0
  } catch (error) {
    display.showError(error.message);
    return EXIT_CODE.ERROR; // 1
  }
}
```

**Layer 3: Entry Point (index.ts)**

```typescript
// cli/src/index.ts
program
  .command('analyze')
  .argument('<path>', 'Path to analyze')
  .action(async (path, options) => {
    const display = new TerminalDisplay();
    const configLoader = new ConfigLoader();
    const config = await configLoader.load(options.config);
    const bridge = new PythonBridge(undefined, undefined, config);

    const exitCode = await analyzeCommand(path, options, bridge, display, configLoader);

    if (exitCode !== EXIT_CODE.SUCCESS) {
      process.exit(exitCode); // ONLY place process.exit() called
    }
  });
```

### Exit Code Constants

**File: cli/src/constants/exitCodes.ts**

```typescript
export const EXIT_CODE = {
  SUCCESS: 0,          // Command completed successfully
  ERROR: 1,            // Command encountered an error
  USER_CANCELLED: 0,   // User cancelled (not an error)
} as const;

export type ExitCode = typeof EXIT_CODE[keyof typeof EXIT_CODE];
```

All command functions return `Promise<ExitCode>` for type safety.

### Special Case: UserCancellationError

Interactive commands (audit, improve) have prompts where users can cancel (ESC, Ctrl+C). User cancellations are **not errors**, so they exit with code 0:

```typescript
// cli/src/session/InteractiveSession.ts
export class InteractiveSession {
  async processItem(item: PlanItem): Promise<void> {
    const response = await prompts({
      type: 'select',
      name: 'action',
      message: 'What would you like to do?',
      choices: [
        { title: 'Accept', value: 'accept' },
        { title: 'Skip', value: 'skip' },
        { title: 'Quit', value: 'quit' },
      ],
    });

    if (response.action === 'quit' || !response.action) {
      throw new UserCancellationError('User quit session');
    }
  }
}

// cli/src/commands/improveCommand.ts
export async function improveCommand(...): Promise<ExitCode> {
  try {
    await improveCore(...);
    return EXIT_CODE.SUCCESS;
  } catch (error) {
    if (error instanceof UserCancellationError) {
      display.showMessage('Session cancelled by user');
      return EXIT_CODE.USER_CANCELLED; // 0 - not an error
    }
    display.showError(error.message);
    return EXIT_CODE.ERROR;
  }
}
```

### Testing Benefits

This architecture **eliminates the need to mock process.exit()** in tests:

**Unit Tests (Core Functions):**

```typescript
// cli/src/__tests__/commands/analyze.test.ts
describe('analyzeCore', () => {
  it('throws when path does not exist', async () => {
    await expect(
      analyzeCore('/nonexistent', options, mockBridge, mockDisplay, mockConfigLoader)
    ).rejects.toThrow('Path not found');
  });

  it('throws when config loading fails', async () => {
    mockConfigLoader.load.mockResolvedValue(null);
    await expect(
      analyzeCore('/path', options, mockBridge, mockDisplay, mockConfigLoader)
    ).rejects.toThrow('Failed to load configuration');
  });
});
```

**Integration Tests (Command Wrappers):**

```typescript
describe('analyzeCommand', () => {
  it('returns ERROR exit code when path does not exist', async () => {
    const exitCode = await analyzeCommand(
      '/nonexistent', options, mockBridge, mockDisplay, mockConfigLoader
    );
    expect(exitCode).toBe(EXIT_CODE.ERROR);
  });

  it('returns SUCCESS exit code on successful analysis', async () => {
    const exitCode = await analyzeCommand(
      '/path', options, mockBridge, mockDisplay, mockConfigLoader
    );
    expect(exitCode).toBe(EXIT_CODE.SUCCESS);
  });
});
```

**No process.exit mocking needed** - tests are simpler, faster, and more maintainable.

### Adoption Across Commands

All CLI commands follow this pattern:

| Command | Core Function | Command Wrapper | Exit Codes |
|---------|--------------|-----------------|------------|
| analyze | `analyzeCore()` | `analyzeCommand()` | SUCCESS, ERROR |
| audit | `auditCore()` | `auditCommand()` | SUCCESS, ERROR, USER_CANCELLED |
| plan | `planCore()` | `planCommand()` | SUCCESS, ERROR |
| improve | `improveCore()` | `improveCommand()` | SUCCESS, ERROR, USER_CANCELLED |
| status | `statusCore()` | `statusCommand()` | SUCCESS, ERROR |

---

## 3. Dependency Injection Pattern

### Core Principle

**All dependencies passed as required parameters.** Only entry points (main.py, index.ts) instantiate objects.

**Benefits:**
- **Testability**: Tests inject mocks, production injects real implementations
- **No hidden dependencies**: All dependencies explicit in function signatures
- **Single instantiation point**: Easy to trace where objects are created
- **Compile-time safety**: TypeScript/mypy catch missing dependencies

### Python Implementation

**Core functions accept dependencies via required parameters:**

```python
# analyzer/src/main.py
def cmd_analyze(
    args: argparse.Namespace,
    parsers: dict,
    scorer: ImpactScorer,
    state_manager: WorkflowStateManager  # All dependencies explicit
) -> int:
    """Execute analyze command with injected dependencies."""
    analyzer = create_analyzer(parsers, scorer)
    result = analyzer.analyze(args.path)

    # Update workflow state
    state_manager.update_command_state('analyze', result)
    return 0

def create_analyzer(
    parsers: dict,
    scorer: ImpactScorer
) -> DocumentationAnalyzer:
    """Factory function - no internal instantiation."""
    return DocumentationAnalyzer(
        parsers=parsers,
        scorer=scorer
    )
```

**Entry point instantiates all dependencies ONCE:**

```python
# analyzer/src/main.py:main()
def main(argv: Optional[list] = None) -> int:
    """Entry point - ONLY place that instantiates objects."""
    args = parse_args(argv)

    # Instantiate dependencies once
    parsers = {
        'python': PythonParser(),
        'typescript': TypeScriptParser(),
        'javascript': TypeScriptParser()
    }
    scorer = ImpactScorer()
    state_manager = WorkflowStateManager()

    # Dispatch commands with injected dependencies
    if args.command == 'analyze':
        return cmd_analyze(args, parsers, scorer, state_manager)
    elif args.command == 'audit':
        return cmd_audit(args, parsers, scorer, state_manager)
    # ...
```

### TypeScript Implementation

**Core functions accept dependencies as required parameters:**

```typescript
// cli/src/commands/analyzeCore.ts
export async function analyzeCore(
  path: string,
  options: AnalyzeOptions,
  bridge: IPythonBridge,          // Required parameter
  display: IDisplay,               // Required parameter
  configLoader: IConfigLoader,     // Required parameter
  stateManager: IWorkflowStateManager  // Required parameter
): Promise<void> {
  const config = await configLoader.load(options.config);
  const result = await bridge.analyze({ path, config });
  display.showAnalysisResult(result);

  // Update workflow state
  await stateManager.updateCommandState('analyze', {
    timestamp: new Date().toISOString(),
    item_count: result.total_items,
    file_checksums: result.file_checksums,
  });
}
```

**Entry point instantiates dependencies:**

```typescript
// cli/src/index.ts
program
  .command('analyze')
  .action(async (path, options) => {
    // Instantiate dependencies at entry point
    const display = new TerminalDisplay();
    const configLoader = new ConfigLoader();
    const config = await configLoader.load(options.config);
    const bridge = new PythonBridge(undefined, undefined, config);
    const stateManager = new WorkflowStateManager();

    // Call command with injected dependencies
    await analyzeCommand(path, options, bridge, display, configLoader, stateManager);
  });
```

### Testing with Dependency Injection

**Python Unit Tests:**

```python
# analyzer/tests/test_analyzer.py
def test_analyze_command():
    """Test analyze command with mocked dependencies."""
    # Mock dependencies
    mock_parsers = {
        'python': MockParser(),
        'typescript': MockParser()
    }
    mock_scorer = MockScorer()
    mock_state_manager = MockStateManager()

    # Call function with mocks
    exit_code = cmd_analyze(
        args=MockArgs(path='./test'),
        parsers=mock_parsers,
        scorer=mock_scorer,
        state_manager=mock_state_manager
    )

    assert exit_code == 0
    assert mock_state_manager.update_called
```

**TypeScript Unit Tests:**

```typescript
// cli/src/__tests__/commands/analyze.test.ts
describe('analyzeCore', () => {
  it('updates workflow state after successful analysis', async () => {
    // Mock dependencies
    const mockBridge = createMockPythonBridge();
    const mockDisplay = createMockDisplay();
    const mockConfigLoader = createMockConfigLoader();
    const mockStateManager = createMockStateManager();

    // Call function with mocks
    await analyzeCore(
      '/path',
      options,
      mockBridge,
      mockDisplay,
      mockConfigLoader,
      mockStateManager
    );

    // Verify behavior
    expect(mockStateManager.updateCommandState).toHaveBeenCalledWith(
      'analyze',
      expect.objectContaining({ item_count: 23 })
    );
  });
});
```

### Acceptable Exceptions

**1. Module-Level Performance Caches (Plugin Layer)**

```javascript
// plugins/validate-types.js
let languageServiceCache = new Map();
let cacheAccessOrder = [];
const documentRegistry = ts.createDocumentRegistry();

// Factory captures dependencies in closure, cache stays at module level
export default function createPlugin(ts, parseJSDoc) {
  return {
    name: 'validate-types',
    hooks: {
      beforeAccept: (docstring, item, config) => {
        // Uses module-level cache across invocations
        const languageService = getOrCreateLanguageService(item.filepath);
        // ...
      }
    }
  };
}
```

**Rationale**: Caches must persist across multiple validation calls for performance. Recreating them per-factory would defeat their purpose.

**2. Optional Dependencies with Defaults (Backward Compatibility)**

```python
# analyzer/src/plan.py
def generate_plan(
    result: AnalysisResult,
    audit_file: Optional[Path] = None,
    quality_threshold: int = 2
) -> PlanResult:
    """Generate plan without DI for simple internal utilities."""
    if audit_results:
        scorer = ImpactScorer()  # Simple utility, no DI needed
        # ... use scorer
```

**Rationale**: Not every dependency needs injection. Simple utility classes like `ImpactScorer` with no external dependencies or state can be instantiated internally. DI is reserved for dependencies that need mocking in tests (parsers, API clients, file system) or configuration (timeouts, paths).

**3. Environment Variable Fallback Pattern (Hybrid DI)**

```python
# analyzer/src/parsers/typescript_parser.py
class TypeScriptParser(BaseParser):
    def __init__(self, helper_path: Optional[Path] = None):
        """Three-tier resolution strategy:
        1. Explicit parameter (highest priority, for DI)
        2. Environment variable (for CI/CD)
        3. Auto-detection fallback (for development)
        """
        if helper_path:
            self.helper_path = helper_path
        else:
            env_path = os.environ.get('DOCIMP_TS_HELPER_PATH')
            if env_path:
                self.helper_path = Path(env_path)
            else:
                self.helper_path = self._find_helper()

        if not self.helper_path.exists():
            raise FileNotFoundError(f"Helper not found at {self.helper_path}")
```

**Rationale**: Balances flexibility (works in development, CI/CD, and future pip installations), testability (tests inject mock paths), and backward compatibility (existing code continues to work).

---

## 4. Configuration System

### JavaScript-Based Configuration

DocImp uses **JavaScript configuration files** (not JSON) to allow custom logic and functions.

**File: docimp.config.js**

```javascript
// Supports both CommonJS and ESM:
// - CommonJS: module.exports = { ... };
// - ESM: export default { ... };

export default {
  // Per-language style guides
  styleGuides: {
    python: 'google',           // 4 options: google, numpy-rest, numpy-markdown, sphinx
    javascript: 'jsdoc-vanilla', // 3 options: jsdoc-vanilla, jsdoc-google, jsdoc-closure
    typescript: 'tsdoc-typedoc', // 3 options: tsdoc-typedoc, tsdoc-aedoc, jsdoc-ts
  },

  // Tone: concise, detailed, friendly
  tone: 'concise',

  // JSDoc style enforcement
  jsdocStyle: {
    preferredTags: { return: 'returns', arg: 'param' },
    requireDescriptions: true,
    requireExamples: 'public',  // Options: all, public, none
    enforceTypes: true,
  },

  // Audit code display configuration
  audit: {
    showCode: {
      mode: 'truncated',  // Options: complete, truncated, signature, on-demand
      maxLines: 20,
    },
  },

  // Claude API configuration
  claude: {
    timeout: 30.0,      // seconds
    maxRetries: 3,
    retryDelay: 1.0,    // seconds, exponential backoff
  },

  // Transaction system git timeouts
  transaction: {
    git: {
      baseTimeout: 30000,   // milliseconds (30s)
      fastScale: 0.167,     // fast ops: 5s (baseTimeout * 0.167)
      slowScale: 4.0,       // slow ops: 120s (baseTimeout * 4.0)
      maxTimeout: 300000,   // absolute cap: 5 minutes
    },
  },

  // Impact scoring weights (must sum to 1.0)
  impactWeights: {
    complexity: 0.6,  // 60% weight
    quality: 0.4,     // 40% weight
  },

  // Validation plugins
  plugins: [
    './plugins/validate-types.js',
    './plugins/jsdoc-style.js',
  ],

  // File exclusion patterns (glob syntax)
  exclude: [
    '**/test_*.py',
    '**/*.test.ts',
    '**/node_modules/**',
    '**/.venv/**',
  ],
};
```

### Configuration Loading

**TypeScript: cli/src/config/ConfigLoader.ts**

```typescript
export class ConfigLoader implements IConfigLoader {
  async load(configPath?: string): Promise<IConfig> {
    const resolvedPath = this.resolveConfigPath(configPath);

    // Dynamic import supports both CommonJS and ESM
    const configModule = await import(pathToFileURL(resolvedPath).href);
    const userConfig = configModule.default || configModule;

    // Merge with defaults
    const config = this.mergeWithDefaults(userConfig);

    // Validate configuration
    this.validateConfig(config);

    return config;
  }

  private validateConfig(config: IConfig): void {
    // Validate impact weights sum to 1.0 (±0.01 tolerance)
    const totalWeight = config.impactWeights.complexity + config.impactWeights.quality;
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      console.warn(
        `Warning: Impact weights sum to ${totalWeight}, expected 1.0. ` +
        `Adjust complexity (${config.impactWeights.complexity}) ` +
        `and quality (${config.impactWeights.quality}) weights.`
      );
    }

    // Validate plugin paths exist
    for (const pluginPath of config.plugins) {
      if (!existsSync(pluginPath)) {
        throw new Error(`Plugin not found: ${pluginPath}`);
      }
    }
  }
}
```

### Configuration Use Cases

**1. Style Guide Customization**

```javascript
// docimp.config.js for NumPy project
export default {
  styleGuides: {
    python: 'numpy-rest',  // Override: use NumPy style instead of Google
    javascript: 'jsdoc-google',
    typescript: 'tsdoc-typedoc',
  },
};
```

**2. Slow Network Adjustments**

```javascript
// Increase timeouts for slow connections
export default {
  claude: {
    timeout: 60.0,      // 2x default
    maxRetries: 5,      // More retries
    retryDelay: 2.0,    // Longer delays
  },
};
```

**3. Large Repository Optimization**

```javascript
// Increase git operation timeouts for large repos
export default {
  transaction: {
    git: {
      baseTimeout: 60000,    // 60s base (vs default 30s)
      slowScale: 6.0,        // 360s for slow ops (vs default 120s)
      maxTimeout: 600000,    // 10 minutes cap
    },
  },
};
```

**4. Custom Plugin Development**

```javascript
// Add custom validation plugin
export default {
  plugins: [
    './plugins/validate-types.js',      // Built-in
    './plugins/jsdoc-style.js',         // Built-in
    './plugins/company-style.js',       // Custom
  ],
};
```

### Configuration Hot Reload

DocImp **does not support hot reload** of configuration. Changes to `docimp.config.js` require restarting the CLI command.

**Rationale**: Configuration changes affect critical behavior (style guides, scoring weights, plugin loading). Hot reload could cause inconsistent state mid-session.

---

## 5. Schema Versioning and Migration

### Problem Statement

As DocImp evolves, data structures change:
- Workflow state adds new fields
- Session state changes structure
- Command output JSON schema updates

**Without versioning:**
- Breaking changes require manual file deletion
- Users lose progress data
- Upgrade friction

**With versioning:**
- Automatic migration on load
- Backward compatibility
- No manual intervention

### Workflow State Versioning

**Current Version: 1.0**

```json
{
  "schema_version": "1.0",
  "migration_log": [],
  "last_analyze": {
    "timestamp": "2025-11-12T14:30:00Z",
    "item_count": 23,
    "file_checksums": { "src/file.py": "abc123..." }
  },
  "last_audit": null,
  "last_plan": null,
  "last_improve": null
}
```

**Migration Log Tracks Applied Migrations:**

```json
{
  "schema_version": "1.1",
  "migration_log": [
    {
      "from_version": "1.0",
      "to_version": "1.1",
      "applied_at": "2025-11-10T15:30:00Z",
      "description": "Add file_checksums to command states"
    }
  ],
  "last_analyze": { ... }
}
```

### Migration Registry Pattern

**TypeScript: cli/src/types/workflow-state-migrations.ts**

```typescript
export type MigrationFn = (state: WorkflowState) => WorkflowState;

export const WORKFLOW_STATE_MIGRATIONS: Record<string, MigrationFn> = {
  "1.0->1.1": migrate_1_0_to_1_1,
  "1.1->1.2": migrate_1_1_to_1_2,
};

function migrate_1_0_to_1_1(state: WorkflowState): WorkflowState {
  // Add file_checksums field to command states
  if (state.last_analyze && !state.last_analyze.file_checksums) {
    state.last_analyze.file_checksums = {};
  }
  // Update schema version
  state.schema_version = "1.1";
  // Add migration log entry
  state.migration_log.push({
    from_version: "1.0",
    to_version: "1.1",
    applied_at: new Date().toISOString(),
    description: "Add file_checksums to command states"
  });
  return state;
}

export function buildMigrationPath(from: string, to: string): string[] {
  // Constructs sequential migration chain: ["1.0->1.1", "1.1->1.2"]
  const versions = ["1.0", "1.1", "1.2"];
  const fromIndex = versions.indexOf(from);
  const toIndex = versions.indexOf(to);

  if (fromIndex === -1 || toIndex === -1 || fromIndex >= toIndex) {
    throw new Error(`Invalid migration path: ${from} -> ${to}`);
  }

  const path: string[] = [];
  for (let i = fromIndex; i < toIndex; i++) {
    path.push(`${versions[i]}->${versions[i + 1]}`);
  }
  return path;
}

export function applyMigrations(state: WorkflowState, path: string[]): WorkflowState {
  let migratedState = state;
  for (const migration of path) {
    const migrateFn = WORKFLOW_STATE_MIGRATIONS[migration];
    if (!migrateFn) {
      throw new Error(`Migration not found: ${migration}`);
    }
    migratedState = migrateFn(migratedState);
  }
  return migratedState;
}
```

**Python: analyzer/src/models/workflow_state_migrations.py**

```python
from typing import Dict, Callable
from dataclasses import replace

MigrationFn = Callable[[WorkflowState], WorkflowState]

WORKFLOW_STATE_MIGRATIONS: Dict[str, MigrationFn] = {
    "1.0->1.1": migrate_1_0_to_1_1,
    "1.1->1.2": migrate_1_1_to_1_2,
}

def migrate_1_0_to_1_1(state: WorkflowState) -> WorkflowState:
    """Add file_checksums field to command states."""
    if state.last_analyze and not hasattr(state.last_analyze, 'file_checksums'):
        state.last_analyze.file_checksums = {}

    state.schema_version = "1.1"
    state.migration_log.append(MigrationLogEntry(
        from_version="1.0",
        to_version="1.1",
        applied_at=datetime.now(timezone.utc).isoformat(),
        description="Add file_checksums to command states"
    ))
    return state

def build_migration_path(from_version: str, to_version: str) -> List[str]:
    """Construct sequential migration chain."""
    versions = ["1.0", "1.1", "1.2"]
    from_idx = versions.index(from_version)
    to_idx = versions.index(to_version)

    if from_idx >= to_idx:
        raise ValueError(f"Invalid migration path: {from_version} -> {to_version}")

    return [f"{versions[i]}->{versions[i+1]}" for i in range(from_idx, to_idx)]

def apply_migrations(state: WorkflowState, path: List[str]) -> WorkflowState:
    """Apply sequential migrations."""
    migrated_state = state
    for migration in path:
        migrate_fn = WORKFLOW_STATE_MIGRATIONS.get(migration)
        if not migrate_fn:
            raise ValueError(f"Migration not found: {migration}")
        migrated_state = migrate_fn(migrated_state)
    return migrated_state
```

### Auto-Migration on Load

**TypeScript: WorkflowStateManager**

```typescript
export class WorkflowStateManager {
  static async load(docimpDir: string): Promise<WorkflowState> {
    const workflowFile = path.join(docimpDir, 'workflow-state.json');

    if (!existsSync(workflowFile)) {
      return this.createEmpty();
    }

    const content = await fs.readFile(workflowFile, 'utf8');
    let state = JSON.parse(content) as WorkflowState;

    // Auto-migrate if needed
    if (state.schema_version !== CURRENT_VERSION) {
      const migrationPath = buildMigrationPath(state.schema_version, CURRENT_VERSION);
      state = applyMigrations(state, migrationPath);

      // Save migrated state
      await this.save(state, docimpDir);
    }

    return state;
  }
}
```

**Python: WorkflowStateManager**

```python
class WorkflowStateManager:
    @staticmethod
    def load(docimp_dir: Path) -> WorkflowState:
        workflow_file = docimp_dir / "workflow-state.json"

        if not workflow_file.exists():
            return WorkflowStateManager.create_empty()

        with open(workflow_file, 'r') as f:
            data = json.load(f)

        state = WorkflowState.from_dict(data)

        # Auto-migrate if needed
        if state.schema_version != CURRENT_VERSION:
            migration_path = build_migration_path(state.schema_version, CURRENT_VERSION)
            state = apply_migrations(state, migration_path)

            # Save migrated state
            WorkflowStateManager.save(state, docimp_dir)

        return state
```

### Manual Migration Command

**Command: docimp migrate-workflow-state**

```bash
# Check if migration needed (CI/CD mode, exit code 0 or 1)
docimp migrate-workflow-state --check

# Preview migration without changes
docimp migrate-workflow-state --dry-run

# Migrate to specific version
docimp migrate-workflow-state --version 1.1

# Skip confirmation prompt
docimp migrate-workflow-state --force
```

**Implementation: cli/src/commands/migrate-workflow-state.ts**

```typescript
export async function migrateWorkflowStateCommand(
  options: MigrateOptions
): Promise<ExitCode> {
  const state = await WorkflowStateManager.load('.docimp');

  if (options.check) {
    // Check mode: exit code 0 if up-to-date, 1 if migration needed
    if (state.schema_version === CURRENT_VERSION) {
      console.log(`Workflow state is up-to-date (version ${CURRENT_VERSION})`);
      return EXIT_CODE.SUCCESS;
    } else {
      console.log(`Migration needed: ${state.schema_version} -> ${CURRENT_VERSION}`);
      return EXIT_CODE.ERROR;
    }
  }

  if (options.dryRun) {
    // Dry-run: show what would be migrated
    const migrationPath = buildMigrationPath(state.schema_version, CURRENT_VERSION);
    console.log(`Would apply migrations: ${migrationPath.join(' -> ')}`);
    return EXIT_CODE.SUCCESS;
  }

  // Perform migration
  const targetVersion = options.version || CURRENT_VERSION;
  const migrationPath = buildMigrationPath(state.schema_version, targetVersion);

  if (!options.force) {
    const confirmed = await confirmMigration(state.schema_version, targetVersion);
    if (!confirmed) {
      console.log('Migration cancelled');
      return EXIT_CODE.USER_CANCELLED;
    }
  }

  const migratedState = applyMigrations(state, migrationPath);
  await WorkflowStateManager.save(migratedState, '.docimp');

  console.log(`Successfully migrated: ${state.schema_version} -> ${targetVersion}`);
  return EXIT_CODE.SUCCESS;
}
```

### Migration Testing Strategy

**Unit Tests: Migration Functions**

```typescript
// cli/src/__tests__/workflow-state-migrations.test.ts
describe('migrate_1_0_to_1_1', () => {
  it('adds file_checksums field', () => {
    const state: WorkflowState = {
      schema_version: '1.0',
      migration_log: [],
      last_analyze: { timestamp: '2025-11-12T14:30:00Z', item_count: 23 },
      last_audit: null,
      last_plan: null,
      last_improve: null,
    };

    const migrated = migrate_1_0_to_1_1(state);

    expect(migrated.schema_version).toBe('1.1');
    expect(migrated.last_analyze?.file_checksums).toEqual({});
    expect(migrated.migration_log).toHaveLength(1);
    expect(migrated.migration_log[0].from_version).toBe('1.0');
    expect(migrated.migration_log[0].to_version).toBe('1.1');
  });
});
```

**Integration Tests: Auto-Migration**

```typescript
// cli/src/__tests__/workflow-state-manager.test.ts
describe('WorkflowStateManager.load', () => {
  it('auto-migrates v1.0 state to v1.1', async () => {
    // Create v1.0 state file
    const v1State = {
      schema_version: '1.0',
      migration_log: [],
      last_analyze: { timestamp: '2025-11-12T14:30:00Z', item_count: 23 },
    };
    await fs.writeFile('.docimp/workflow-state.json', JSON.stringify(v1State));

    // Load state (should auto-migrate)
    const state = await WorkflowStateManager.load('.docimp');

    expect(state.schema_version).toBe('1.1');
    expect(state.last_analyze?.file_checksums).toBeDefined();
    expect(state.migration_log).toHaveLength(1);

    // Verify file was updated
    const savedContent = await fs.readFile('.docimp/workflow-state.json', 'utf8');
    const savedState = JSON.parse(savedContent);
    expect(savedState.schema_version).toBe('1.1');
  });
});
```

---

## Quick Reference

### Pattern Checklist

When implementing new features:

- [ ] **Error Handling**: Core function throws, Command wrapper catches, Entry point checks exit code
- [ ] **Dependency Injection**: All dependencies passed as required parameters, entry point instantiates
- [ ] **Configuration**: New options added to docimp.config.js with defaults and validation
- [ ] **Documentation**: Keep CLAUDE.md under 40K, move details to docs/patterns/
- [ ] **Schema Versioning**: If data structure changes, add migration function

### File Locations

| Pattern | TypeScript Location | Python Location |
|---------|---------------------|-----------------|
| Error Handling | `cli/src/constants/exitCodes.ts` | N/A (TypeScript-only) |
| Dependency Injection | `cli/src/index.ts` (entry point) | `analyzer/src/main.py` (entry point) |
| Configuration | `cli/src/config/ConfigLoader.ts` | N/A (TypeScript loads, Python receives) |
| Schema Versioning | `cli/src/types/workflow-state-migrations.ts` | `analyzer/src/models/workflow_state_migrations.py` |
| External Docs Pattern | `CLAUDE.md` + `docs/patterns/*.md` | N/A (documentation-only) |

### Common Maintenance Tasks

**1. Add New CLI Command**

```bash
# 1. Create Core function (throws errors)
vim cli/src/commands/newCore.ts

# 2. Create Command wrapper (returns exit codes)
vim cli/src/commands/newCommand.ts

# 3. Register in entry point (instantiate dependencies)
vim cli/src/index.ts

# 4. Add tests
vim cli/src/__tests__/commands/new.test.ts
```

**2. Add Configuration Option**

```bash
# 1. Update config interface
vim cli/src/config/IConfig.ts

# 2. Add default value
vim cli/src/config/ConfigLoader.ts

# 3. Add validation logic
vim cli/src/config/ConfigLoader.ts:validateConfig()

# 4. Document in docimp.config.js comments
vim docimp.config.js
```

**3. Migrate Workflow State Schema**

```bash
# 1. Increment CURRENT_VERSION
vim cli/src/types/workflow-state.ts
# Update: export const CURRENT_VERSION = "1.2";

# 2. Add migration function
vim cli/src/types/workflow-state-migrations.ts
# Add: function migrate_1_1_to_1_2(state) { ... }

# 3. Register migration
vim cli/src/types/workflow-state-migrations.ts
# Add: "1.1->1.2": migrate_1_1_to_1_2

# 4. Mirror in Python
vim analyzer/src/models/workflow_state_migrations.py

# 5. Add tests
vim cli/src/__tests__/workflow-state-migrations.test.ts
```

**4. CLAUDE.md Size Management**

```bash
# 1. Check current size
wc -c CLAUDE.md

# 2. If approaching 40K (35K+ is yellow zone):
#    Identify section with detailed content

# 3. Extract to pattern file
vim docs/patterns/new-pattern.md

# 4. Replace with summary + import in CLAUDE.md
vim CLAUDE.md
# Add: - @docs/patterns/new-pattern.md

# 5. Commit both files
git add CLAUDE.md docs/patterns/new-pattern.md
git commit -m "Extract new-pattern to external docs"
```

---

## Troubleshooting

### Problem: CLAUDE.md Exceeds 40K Limit

**Symptoms:**
- `wc -c CLAUDE.md` shows > 40,000 characters
- Claude Code truncates documentation
- Critical guidance missing in sessions

**Solution:**

1. **Identify verbose sections:**
   ```bash
   # Count lines per section
   grep -n "^## " CLAUDE.md | while read line; do
     start=$(echo $line | cut -d: -f1)
     end=$(tail -n +$((start+1)) CLAUDE.md | grep -n "^## " | head -1 | cut -d: -f1)
     section=$(echo $line | cut -d: -f2-)
     if [ -n "$end" ]; then
       lines=$((end - 1))
     else
       lines=$(wc -l < CLAUDE.md | awk '{print $1 - '$start'}')
     fi
     echo "$lines lines: $section"
   done | sort -rn
   ```

2. **Extract large sections to docs/patterns/**

3. **Replace with summary + import reference**

4. **Verify size:**
   ```bash
   wc -c CLAUDE.md
   # Should be < 40,000
   ```

### Problem: Migration Function Not Found

**Symptoms:**
- Error: "Migration not found: 1.0->1.1"
- WorkflowStateManager fails to load

**Solution:**

1. **Check migration registry:**
   ```typescript
   // cli/src/types/workflow-state-migrations.ts
   console.log(Object.keys(WORKFLOW_STATE_MIGRATIONS));
   // Should include: ["1.0->1.1", "1.1->1.2", ...]
   ```

2. **Verify migration function exists:**
   ```typescript
   function migrate_1_0_to_1_1(state: WorkflowState): WorkflowState {
     // Implementation...
   }
   ```

3. **Register in WORKFLOW_STATE_MIGRATIONS:**
   ```typescript
   export const WORKFLOW_STATE_MIGRATIONS: Record<string, MigrationFn> = {
     "1.0->1.1": migrate_1_0_to_1_1,  // Add this line
   };
   ```

### Problem: process.exit() Called in Tests

**Symptoms:**
- Test suite exits prematurely
- Cannot test error cases
- Coverage incomplete

**Solution:**

DO NOT call process.exit() in testable code. Follow three-layer error handling:

```typescript
// WRONG: process.exit() in command function
export async function analyzeCommand(...): Promise<void> {
  try {
    await analyzeCore(...);
  } catch (error) {
    console.error(error.message);
    process.exit(1); // BAD - untestable
  }
}

// RIGHT: Return exit code
export async function analyzeCommand(...): Promise<ExitCode> {
  try {
    await analyzeCore(...);
    return EXIT_CODE.SUCCESS;
  } catch (error) {
    display.showError(error.message);
    return EXIT_CODE.ERROR; // GOOD - testable
  }
}
```

### Problem: Circular Dependency Injection

**Symptoms:**
- TypeScript error: "Cannot access 'X' before initialization"
- Runtime error: "X is not a constructor"

**Solution:**

DO NOT create circular dependencies. If A needs B and B needs A, extract common logic to C:

```typescript
// WRONG: Circular dependency
// analyzer.ts
import { Scorer } from './scorer';
export class Analyzer {
  constructor(private scorer: Scorer) {}
}

// scorer.ts
import { Analyzer } from './analyzer';
export class Scorer {
  constructor(private analyzer: Analyzer) {} // Circular!
}

// RIGHT: Extract common logic
// shared-types.ts
export interface IScoreable {
  complexity: number;
}

// analyzer.ts
import { Scorer } from './scorer';
export class Analyzer {
  constructor(private scorer: Scorer) {}
}

// scorer.ts
import { IScoreable } from './shared-types';
export class Scorer {
  score(item: IScoreable): number {
    return item.complexity * 5;
  }
}
```

---

## Summary

DocImp's standardization patterns ensure consistency across:

1. **External Documentation Pattern**: Keeps CLAUDE.md under 40K limit via modular docs in docs/patterns/
2. **Error Handling Pattern**: Three-layer architecture (Core → Command → Entry) for testable error handling
3. **Dependency Injection Pattern**: Constructor injection with entry-point instantiation for testability
4. **Configuration System**: JavaScript-based config files for custom logic and validation
5. **Schema Versioning**: Auto-migration on load with manual CLI command for workflow state evolution

These patterns work together to create a maintainable, evolvable codebase:

- **For Developers**: Clear patterns to follow when adding features
- **For Maintenance**: Predictable locations and structures
- **For Evolution**: Schema versioning enables backward-compatible changes
- **For Testing**: DI and error handling patterns make code testable

**Next Steps**: See `INFRASTRUCTURE-DOCS_8-Test-Infrastructure.md` for comprehensive testing patterns across all layers.
