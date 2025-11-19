# Infrastructure Documentation: Test Infrastructure

## Overview

DocImp has a comprehensive multi-layer test infrastructure across Python, TypeScript, JavaScript, and Bash. Testing is not just a quality gate - it's a **design tool** that enforces clean architecture through dependency injection and testability.

**Test Philosophy:**
- **Always create permanent test files, never ad-hoc validation scripts**
- **Tests must run in CI/CD, catch regressions, and document expected behavior**
- **Test at the right layer**: Unit tests for logic, integration tests for boundaries, E2E tests for workflows

**Test Coverage:**
- **Python**: 42 test files, 476+ tests (analyzer layer)
- **TypeScript**: 50+ test files, 447+ tests (CLI layer)
- **JavaScript**: 3 test files for plugins
- **Bash**: 8 E2E test scripts for manual validation
- **Total**: 923+ automated tests + 8 manual test scripts

---

## 1. Python Test Infrastructure

### Organization

**Location**: `analyzer/tests/test_*.py`

**Test Files** (42 total):

| Category | Files | Focus |
|----------|-------|-------|
| Core Analysis | test_analyzer.py, test_parsers.py, test_typescript_parser.py, test_typescript_parser_edge_cases.py | Parser functionality, file discovery, language detection |
| Workflow State | test_workflow_state_manager.py, test_workflow_state_migrations.py, test_checksum_staleness.py, test_cmd_status.py | Workflow tracking, schema versioning, staleness detection |
| Session Resume | test_audit_session_state.py, test_improve_session_state.py, test_session_state_manager.py, test_file_tracker.py | Session persistence, file invalidation |
| Transaction System | test_transaction_manager.py, test_transaction_lifecycle.py, test_git_integration.py, test_post_squash_rollback.py, test_individual_rollback.py | Git operations, rollback, conflict resolution |
| Scoring & Planning | test_scoring.py, test_plan_generator.py, test_coverage.py | Impact scoring, plan generation, coverage calculation |
| Writer & Integration | test_writer.py, test_prompt_builder.py, test_improve_integration.py, test_javascript_integration.py | Docstring writing, JSDoc insertion, end-to-end improve workflow |
| CLI Commands | test_audit.py, test_cli.py, test_analyze_auto_clean.py, test_rollback_cli.py, test_suggest_command.py, test_main_migrate.py | Command-line interface, flag handling, user input |
| Claude API | test_claude_client.py, test_response_parser.py | API communication, retry logic, response parsing |
| Models & Serialization | test_models.py, test_json_serialization.py, test_schema_versioning.py | Data model validation, JSON serialization |
| Edge Cases & Robustness | test_graceful_degradation.py, test_conflict_resolution.py, test_backup_cleanup.py, test_di_compliance.py | Error handling, transaction conflicts, dependency injection validation |
| State Management | test_state_manager.py | File path utilities, StateManager |

### Configuration

**File: analyzer/pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
markers =
  unit: Unit tests
  integration: Integration tests
  slow: Tests that take a long time to run
```

**Ruff Configuration (pyproject.toml):**

```toml
[tool.ruff]
exclude = [".venv", "venv", "__pycache__", ".pytest_cache"]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "F",     # pyflakes
    "DTZ",   # flake8-datetimez - timezone-aware datetime
    "UP",    # pyupgrade - modernize syntax
    "PTH",   # flake8-use-pathlib - prefer Path over os.path
    "I",     # isort - import sorting
    "SIM",   # flake8-simplify - code simplification
    "PERF",  # perflint - performance anti-patterns
    "YTT",   # flake8-2020 - modern version checks
]
ignore = []
```

### Test Structure

**Import Pattern (CRITICAL):**

```python
import sys
from pathlib import Path

# Enable src.* imports (NOT analyzer.src.*)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.python_parser import PythonParser
from src.analysis.documentation_analyzer import DocumentationAnalyzer
from src.scoring.impact_scorer import ImpactScorer
```

**Rationale**: Tests run from `analyzer/` directory, so `sys.path` manipulation enables `src.*` imports without package installation.

### Example Test File

**File: analyzer/tests/test_parsers.py (excerpt)**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.python_parser import PythonParser
from src.models.code_item import CodeItem

import pytest


class TestPythonParser:
    """Unit tests for PythonParser."""

    def test_parse_simple_function(self, tmp_path):
        """Test parsing a simple function."""
        code = '''
def calculate(a, b):
    """Add two numbers."""
    return a + b
'''
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        parser = PythonParser()
        items = parser.parse_file(str(file_path))

        assert len(items) == 1
        item = items[0]
        assert item.name == "calculate"
        assert item.type == "function"
        assert item.has_docs is True
        assert item.parameters == ["a", "b"]
        assert item.docstring == "Add two numbers."

    def test_parse_function_without_docs(self, tmp_path):
        """Test parsing function without documentation."""
        code = '''
def multiply(x, y):
    return x * y
'''
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        parser = PythonParser()
        items = parser.parse_file(str(file_path))

        assert len(items) == 1
        assert items[0].has_docs is False
        assert items[0].docstring is None

    def test_parse_class_with_methods(self, tmp_path):
        """Test parsing class with multiple methods."""
        code = '''
class Calculator:
    """A simple calculator."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
'''
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        parser = PythonParser()
        items = parser.parse_file(str(file_path))

        assert len(items) == 3  # class + 2 methods
        assert items[0].type == "class"
        assert items[0].name == "Calculator"
        assert items[1].type == "method"
        assert items[1].name == "add"
        assert items[2].type == "method"
        assert items[2].name == "subtract"

    def test_parse_syntax_error(self, tmp_path):
        """Test parser raises SyntaxError for invalid Python."""
        code = '''
def broken(
    # Missing closing parenthesis
'''
        file_path = tmp_path / "broken.py"
        file_path.write_text(code)

        parser = PythonParser()
        with pytest.raises(SyntaxError):
            parser.parse_file(str(file_path))


@pytest.mark.integration
class TestParserIntegration:
    """Integration tests for parser interactions with analyzer."""

    def test_analyzer_handles_syntax_errors(self, tmp_path):
        """Test analyzer tracks syntax errors in parse_failures."""
        # Create valid and invalid files
        (tmp_path / "valid.py").write_text("def foo(): pass")
        (tmp_path / "invalid.py").write_text("def broken(")

        from src.analysis.documentation_analyzer import DocumentationAnalyzer
        from src.scoring.impact_scorer import ImpactScorer

        analyzer = DocumentationAnalyzer(
            parsers={'python': PythonParser()},
            scorer=ImpactScorer()
        )
        result = analyzer.analyze(str(tmp_path))

        # Valid file analyzed successfully
        assert len(result.items) >= 1
        assert result.items[0].name == "foo"

        # Invalid file tracked in parse_failures
        assert len(result.parse_failures) == 1
        assert "invalid.py" in result.parse_failures[0].filepath
        assert "SyntaxError" in result.parse_failures[0].error
```

### Running Python Tests

**Commands:**

```bash
# Run all tests
cd analyzer
uv run pytest -v

# Run specific test file
uv run pytest tests/test_parsers.py -v

# Run tests by marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"

# Run with coverage
uv run pytest --cov=src --cov-report=term --cov-report=html

# Run specific test function
uv run pytest tests/test_parsers.py::TestPythonParser::test_parse_simple_function -v
```

**CI/CD Integration** (.github/workflows/ci.yml):

```yaml
python-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    - uses: astral-sh/setup-uv@v5
      with:
        version: '0.9.8'
    - name: Install dependencies
      run: |
        cd analyzer
        uv pip sync requirements-dev.lock
        uv pip install -e .
    - name: Lint with ruff
      run: cd analyzer && uv run ruff check .
    - name: Format check with ruff
      run: cd analyzer && uv run ruff format --check .
    - name: Type check with mypy
      run: cd analyzer && uv run mypy src --ignore-missing-imports
    - name: Run tests with coverage
      run: cd analyzer && uv run pytest -v --cov=src --cov-report=term
```

### Python Testing Best Practices

**1. Use Dependency Injection for Testability**

```python
# GOOD: Dependencies injected, easy to mock
def cmd_analyze(
    args: argparse.Namespace,
    parsers: dict,
    scorer: ImpactScorer
) -> int:
    analyzer = create_analyzer(parsers, scorer)
    result = analyzer.analyze(args.path)
    return 0

# Test with mocks:
def test_cmd_analyze():
    mock_parsers = {'python': MockParser()}
    mock_scorer = MockScorer()
    exit_code = cmd_analyze(mock_args, mock_parsers, mock_scorer)
    assert exit_code == 0
```

**2. Use tmp_path Fixture for File Operations**

```python
def test_write_docstring(tmp_path):
    """Test docstring writing to file."""
    file_path = tmp_path / "test.py"
    file_path.write_text("def foo(): pass")

    writer = DocstringWriter()
    writer.write_docstring(str(file_path), "\"\"\"Add docstring.\"\"\"", line=1)

    content = file_path.read_text()
    assert "\"\"\"Add docstring.\"\"\"" in content
```

**3. Test Edge Cases and Error Paths**

```python
def test_parser_handles_empty_file(tmp_path):
    """Test parser returns empty list for empty file."""
    file_path = tmp_path / "empty.py"
    file_path.write_text("")

    parser = PythonParser()
    items = parser.parse_file(str(file_path))
    assert items == []

def test_parser_raises_on_nonexistent_file():
    """Test parser raises FileNotFoundError for missing file."""
    parser = PythonParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/nonexistent/file.py")
```

**4. Use Parametrize for Multiple Test Cases**

```python
@pytest.mark.parametrize("complexity,expected_score", [
    (1, 5),
    (5, 25),
    (10, 50),
    (15, 75),
    (20, 100),
    (25, 100),  # Capped at 100
])
def test_complexity_score_calculation(complexity, expected_score):
    """Test impact score calculation for various complexity values."""
    scorer = ImpactScorer()
    score = scorer.calculate_complexity_score(complexity)
    assert score == expected_score
```

---

## 2. TypeScript Test Infrastructure

### Organization

**Location**: `cli/src/__tests__/`

**Directory Structure:**

```
cli/src/__tests__/
├── commands/          # Command-specific tests
│   ├── audit-helpers.test.ts
│   ├── improve-resume-helpers.test.ts
│   ├── status.test.ts
│   ├── migrate-workflow-state.test.ts
│   ├── analyze-incremental-dry-run.test.ts
│   ├── audit-incremental-save.test.ts
│   └── improve.test.ts
├── config/            # Configuration loading & validation
│   ├── ConfigLoader.test.ts
│   ├── ConfigValidator.test.ts
│   └── ConfigErrorClassifier.test.ts
├── display/           # Terminal display and formatting
│   ├── TerminalDisplay.test.ts
│   └── display.test.ts
├── editor/            # Editor integration
│   └── EditorLauncher.test.ts
├── integration/       # Cross-component integration tests
│   ├── audit-sessions.test.ts
│   ├── improve-sessions.test.ts
│   ├── audit-resume-auto-detect.test.ts
│   ├── audit-resume-flags.test.ts
│   ├── audit-resume-workflow.test.ts
│   ├── audit-session-control.test.ts
│   ├── cross-workflow-resume.test.ts
│   ├── git-timeout-config.test.ts
│   ├── transaction-lifecycle.test.ts
│   ├── transaction-recording.test.ts
│   ├── workflow-state-integration.test.ts
│   └── PythonBridge.integration.test.ts
├── parsers/           # Parser tests
│   └── ts-js-parser.test.ts
├── plugins/           # Plugin system tests
│   └── PluginManager.test.ts
├── python-bridge/     # Python subprocess communication
│   ├── PythonBridge.test.ts
│   └── PythonBridge.suggest.feedback.test.ts
├── session/           # Interactive session management
│   ├── InteractiveSession.test.ts
│   ├── interactive-session-state.test.ts
│   └── ProgressTracker.test.ts
├── types/             # Type and data model tests
│   ├── audit-session-state.test.ts
│   └── improve-session-state.test.ts
├── utils/             # Utility function tests
│   ├── CodeExtractor.test.ts
│   ├── PathValidator.test.ts
│   ├── terminalWidth.test.ts
│   ├── file-tracker.test.ts
│   └── session-state-manager.test.ts
├── analyze-apply-audit.test.ts
├── analyze-command.test.ts
├── analyze-incremental.test.ts
├── audit-command.test.ts
├── plan-command.test.ts
├── rollback-commands.test.ts
├── state-manager.test.ts
├── workflow-state-manager.test.ts
├── workflow-state-migrations.test.ts
├── workflow-validator.test.ts
├── performance.bench.test.ts  # Performance benchmarks
└── setup.ts           # Global Jest setup
```

### Jest Configuration

**File: cli/jest.config.js**

```javascript
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],

  // CRITICAL: Sequential execution prevents race conditions
  // Integration tests share .docimp/state directory via Python subprocess
  maxWorkers: 1,

  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',      // ESM .js extensions
    '^@/(.*)$': '<rootDir>/src/$1'     // @ alias
  },

  transform: {
    '^.+\\.ts$': [
      'ts-jest',
      {
        useESM: true,
        tsconfig: {
          module: 'esnext',
          isolatedModules: true,
        },
      },
    ],
    '^.+\\.js$': [
      'ts-jest',
      {
        useESM: true,
        tsconfig: {
          module: 'esnext',
          allowJs: true,
        },
      },
    ],
  },

  transformIgnorePatterns: [
    'node_modules/(?!(chalk|cli-table3|ora|prompts|uuid|ansi-regex|strip-ansi|ansi-styles|#ansi-styles)/)',
  ],

  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).ts',
    '**/?(*.)+(spec|test).js',
  ],

  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts',  // Entry point excluded
  ],

  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
};
```

**Key Configuration Decisions:**

1. **maxWorkers: 1** - Sequential execution prevents race conditions in integration tests that share `.docimp/state/` via Python subprocess
2. **ESM preset** - Supports ES modules with TypeScript
3. **transformIgnorePatterns** - Transforms ESM-only packages (chalk, ora, etc.)
4. **setupFilesAfterEnv** - Global Jest setup for test utilities

### Example Test File

**File: cli/src/__tests__/commands/status.test.ts (excerpt)**

```typescript
import { statusCore } from '../../commands/statusCore.js';
import { createMockPythonBridge } from '../__mocks__/PythonBridge.js';
import { createMockDisplay } from '../__mocks__/Display.js';
import { WorkflowStatusResult } from '../../types/workflow-state.js';

describe('statusCore', () => {
  let mockBridge: any;
  let mockDisplay: any;

  beforeEach(() => {
    mockBridge = createMockPythonBridge();
    mockDisplay = createMockDisplay();
  });

  it('displays empty workflow state', async () => {
    const emptyResult: WorkflowStatusResult = {
      schema_version: '1.0',
      last_analyze: null,
      last_audit: null,
      last_plan: null,
      last_improve: null,
      staleness_warnings: [],
      suggestions: ['Run \'docimp analyze\' to start'],
    };

    mockBridge.getWorkflowStatus.mockResolvedValue(emptyResult);

    await statusCore({}, mockBridge, mockDisplay);

    expect(mockDisplay.showWorkflowStatus).toHaveBeenCalledWith(emptyResult);
  });

  it('displays full workflow state', async () => {
    const fullResult: WorkflowStatusResult = {
      schema_version: '1.0',
      last_analyze: {
        timestamp: '2025-11-12T14:30:00Z',
        item_count: 23,
        file_count: 5,
      },
      last_audit: {
        timestamp: '2025-11-12T15:30:00Z',
        item_count: 18,
      },
      last_plan: {
        timestamp: '2025-11-12T16:00:00Z',
        item_count: 12,
      },
      last_improve: {
        timestamp: '2025-11-12T16:30:00Z',
        changes_count: 8,
      },
      staleness_warnings: [],
      suggestions: [],
    };

    mockBridge.getWorkflowStatus.mockResolvedValue(fullResult);

    await statusCore({}, mockBridge, mockDisplay);

    expect(mockDisplay.showWorkflowStatus).toHaveBeenCalledWith(fullResult);
    expect(mockDisplay.showWorkflowStatus).toHaveBeenCalledTimes(1);
  });

  it('displays staleness warnings', async () => {
    const staleResult: WorkflowStatusResult = {
      schema_version: '1.0',
      last_analyze: {
        timestamp: '2025-11-12T16:00:00Z',
        item_count: 23,
        file_count: 5,
      },
      last_audit: {
        timestamp: '2025-11-12T15:30:00Z',
        item_count: 18,
      },
      last_plan: null,
      last_improve: null,
      staleness_warnings: [
        {
          command: 'audit',
          reason: 'analyze re-run since audit completed',
        },
      ],
      suggestions: [
        "Run 'docimp audit' to refresh ratings",
      ],
    };

    mockBridge.getWorkflowStatus.mockResolvedValue(staleResult);

    await statusCore({}, mockBridge, mockDisplay);

    expect(mockDisplay.showWorkflowStatus).toHaveBeenCalledWith(
      expect.objectContaining({
        staleness_warnings: expect.arrayContaining([
          expect.objectContaining({
            command: 'audit',
            reason: expect.stringContaining('analyze re-run'),
          }),
        ]),
      })
    );
  });

  it('outputs JSON when --json flag set', async () => {
    const result: WorkflowStatusResult = {
      schema_version: '1.0',
      last_analyze: { timestamp: '2025-11-12T14:30:00Z', item_count: 23, file_count: 5 },
      last_audit: null,
      last_plan: null,
      last_improve: null,
      staleness_warnings: [],
      suggestions: [],
    };

    mockBridge.getWorkflowStatus.mockResolvedValue(result);

    await statusCore({ json: true }, mockBridge, mockDisplay);

    // When --json flag set, showWorkflowStatus should NOT be called
    expect(mockDisplay.showWorkflowStatus).not.toHaveBeenCalled();

    // Instead, raw JSON should be logged to console
    expect(mockDisplay.showMessage).toHaveBeenCalledWith(
      expect.stringContaining('"schema_version": "1.0"')
    );
  });

  it('handles missing workflow-state.json gracefully', async () => {
    mockBridge.getWorkflowStatus.mockRejectedValue(
      new Error('workflow-state.json not found')
    );

    await statusCore({}, mockBridge, mockDisplay);

    expect(mockDisplay.showError).toHaveBeenCalledWith(
      expect.stringContaining('not found')
    );
  });

  it('handles corrupted workflow-state.json', async () => {
    mockBridge.getWorkflowStatus.mockRejectedValue(
      new Error('Invalid JSON in workflow-state.json')
    );

    await statusCore({}, mockBridge, mockDisplay);

    expect(mockDisplay.showError).toHaveBeenCalledWith(
      expect.stringContaining('Invalid JSON')
    );
  });
});
```

### Running TypeScript Tests

**Commands:**

```bash
# Run all tests
cd cli
uv run npm test

# Run specific test file
uv run npm test -- status.test.ts

# Run tests matching pattern
uv run npm test -- --testNamePattern="staleness"

# Run with coverage
uv run npm test -- --coverage

# Run in watch mode (development)
uv run npm test -- --watch

# Run specific test suite
uv run npm test -- --testPathPattern="integration"
```

**CI/CD Integration** (.github/workflows/ci.yml):

```yaml
typescript-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '24'
    - name: Install dependencies
      run: cd cli && npm ci
    - name: Lint with ESLint
      run: cd cli && npm run lint
    - name: Format check with Prettier
      run: cd cli && npm run format:check
    - name: Type check with TypeScript
      run: cd cli && npx tsc --noEmit
    - name: Build CLI
      run: cd cli && npm run build
    - name: Run unit tests
      run: cd cli && npm test
    - name: Run integration tests
      run: cd cli && npm run test:integration
```

### TypeScript Testing Best Practices

**1. Mock External Dependencies**

```typescript
// Create mock factories in __mocks__/ directory
// cli/src/__tests__/__mocks__/PythonBridge.ts
export function createMockPythonBridge() {
  return {
    analyze: jest.fn(),
    audit: jest.fn(),
    plan: jest.fn(),
    improve: jest.fn(),
    getWorkflowStatus: jest.fn(),
    beginTransaction: jest.fn(),
    recordWrite: jest.fn(),
    commitTransaction: jest.fn(),
  };
}

// Use in tests
import { createMockPythonBridge } from '../__mocks__/PythonBridge.js';

describe('analyzeCommand', () => {
  let mockBridge: any;

  beforeEach(() => {
    mockBridge = createMockPythonBridge();
  });

  it('calls bridge.analyze with correct arguments', async () => {
    mockBridge.analyze.mockResolvedValue({ total_items: 23 });

    await analyzeCommand('/path', options, mockBridge, mockDisplay, mockConfigLoader);

    expect(mockBridge.analyze).toHaveBeenCalledWith({
      path: '/path',
      config: expect.any(Object),
    });
  });
});
```

**2. Use Type-Safe Mocks**

```typescript
// cli/src/__tests__/__mocks__/Display.ts
import { IDisplay } from '../../display/IDisplay.js';

export function createMockDisplay(): jest.Mocked<IDisplay> {
  return {
    showMessage: jest.fn(),
    showError: jest.fn(),
    showWarning: jest.fn(),
    showAnalysisResult: jest.fn(),
    showWorkflowStatus: jest.fn(),
    showProgress: jest.fn(),
  } as jest.Mocked<IDisplay>;
}
```

**3. Test Error Handling Paths**

```typescript
describe('analyzeCommand error handling', () => {
  it('returns ERROR exit code when Python bridge fails', async () => {
    mockBridge.analyze.mockRejectedValue(new Error('Python subprocess crashed'));

    const exitCode = await analyzeCommand('/path', options, mockBridge, mockDisplay, mockConfigLoader);

    expect(exitCode).toBe(EXIT_CODE.ERROR);
    expect(mockDisplay.showError).toHaveBeenCalledWith(
      expect.stringContaining('Python subprocess crashed')
    );
  });

  it('returns ERROR exit code when config loading fails', async () => {
    mockConfigLoader.load.mockRejectedValue(new Error('Invalid config'));

    const exitCode = await analyzeCommand('/path', options, mockBridge, mockDisplay, mockConfigLoader);

    expect(exitCode).toBe(EXIT_CODE.ERROR);
    expect(mockDisplay.showError).toHaveBeenCalled();
  });
});
```

**4. Test Integration Points**

```typescript
// cli/src/__tests__/integration/workflow-state-integration.test.ts
describe('Workflow State Integration', () => {
  beforeEach(async () => {
    // Setup temp directory with clean .docimp/ state
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'docimp-test-'));
    await fs.mkdir(path.join(tempDir, '.docimp'), { recursive: true });
  });

  afterEach(async () => {
    // Cleanup
    await fs.rm(tempDir, { recursive: true, force: true });
  });

  it('updates workflow state after analyze command', async () => {
    // Run analyze command
    await analyzeCore(
      tempDir,
      { incremental: false },
      mockBridge,
      mockDisplay,
      mockConfigLoader,
      stateManager
    );

    // Verify workflow state updated
    const state = await WorkflowStateManager.load(path.join(tempDir, '.docimp'));
    expect(state.last_analyze).toBeDefined();
    expect(state.last_analyze?.item_count).toBeGreaterThan(0);
    expect(state.last_analyze?.file_checksums).toBeDefined();
  });

  it('detects stale audit after analyze re-run', async () => {
    // Run analyze → audit → analyze sequence
    await analyzeCore(...);
    await auditCore(...);
    await analyzeCore(...);  // Re-run analyze

    // Check staleness
    const validation = await WorkflowValidator.validatePlanPrerequisites(
      path.join(tempDir, '.docimp')
    );

    expect(validation.warnings).toContainEqual(
      expect.objectContaining({
        command: 'audit',
        reason: expect.stringContaining('analyze re-run'),
      })
    );
  });
});
```

---

## 3. JavaScript Plugin Tests

### Organization

**Location**: `plugins/__tests__/`

**Test Files:**

- `validate-types.test.js` - JSDoc type validation plugin
- `jsdoc-style.test.js` - JSDoc style enforcement plugin
- `cache-performance.test.js` - Language service cache tests

### Example Plugin Test

**File: plugins/__tests__/validate-types.test.js (excerpt)**

```javascript
import validateTypesPlugin from '../validate-types.js';
import ts from 'typescript';

describe('validate-types plugin', () => {
  let plugin;

  beforeEach(() => {
    plugin = validateTypesPlugin.default.hooks.beforeAccept;
  });

  it('accepts valid JSDoc types', () => {
    const docstring = `
/**
 * Calculate sum of two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
`;

    const item = {
      name: 'add',
      type: 'function',
      filepath: '/test/add.js',
      parameters: ['a', 'b'],
      return_type: 'number',
    };

    const result = plugin(docstring, item, {});

    expect(result.accept).toBe(true);
    expect(result.reason).toBeUndefined();
  });

  it('rejects JSDoc with parameter name mismatch', () => {
    const docstring = `
/**
 * Calculate sum
 * @param {number} x - First number (WRONG NAME)
 * @param {number} y - Second number (WRONG NAME)
 * @returns {number} Sum
 */
`;

    const item = {
      name: 'add',
      type: 'function',
      filepath: '/test/add.js',
      parameters: ['a', 'b'],  // Actual params: a, b
      return_type: 'number',
    };

    const result = plugin(docstring, item, {});

    expect(result.accept).toBe(false);
    expect(result.reason).toContain('parameter name mismatch');
    expect(result.reason).toContain('Expected: a, b');
    expect(result.reason).toContain('Found: x, y');
  });

  it('rejects invalid JSDoc type syntax', () => {
    const docstring = `
/**
 * Invalid types
 * @param {number[} arr - Invalid array syntax
 * @returns {string
 */
`;

    const item = {
      name: 'process',
      type: 'function',
      filepath: '/test/process.js',
      parameters: ['arr'],
      return_type: 'string',
    };

    const result = plugin(docstring, item, {});

    expect(result.accept).toBe(false);
    expect(result.reason).toContain('Invalid JSDoc type');
  });

  it('provides auto-fix suggestions', () => {
    const docstring = `
/**
 * Calculate sum
 * @param a - First number (MISSING TYPE)
 * @param b - Second number (MISSING TYPE)
 * @returns Sum (MISSING TYPE)
 */
`;

    const item = {
      name: 'add',
      type: 'function',
      filepath: '/test/add.js',
      parameters: ['a', 'b'],
      return_type: 'number',
    };

    const result = plugin(docstring, item, {});

    expect(result.accept).toBe(false);
    expect(result.autoFix).toBeDefined();
    expect(result.autoFix).toContain('@param {number} a');
    expect(result.autoFix).toContain('@param {number} b');
    expect(result.autoFix).toContain('@returns {number}');
  });
});
```

### Running Plugin Tests

```bash
# Run all plugin tests
cd plugins
uv run npm test

# Run specific plugin test
uv run npm test -- validate-types.test.js

# Run with coverage
uv run npm test -- --coverage
```

---

## 4. End-to-End Bash Tests

### Organization

**Location**: `test-samples/`

**Test Scripts** (8 total):

| Script | Purpose |
|--------|---------|
| test-workflows.sh | Full workflow validation (analyze → audit → plan → improve) |
| test-workflows-improve.sh | Improve workflow with API calls (requires ANTHROPIC_API_KEY) |
| test-audit-resume.sh | Audit resume capability |
| test-resume-improve.sh | Improve resume with file modification |
| test-workflow-state-integration.sh | Workflow state updates and staleness detection |
| test-undo-integration.sh | Interactive undo feature |
| test-prompt-wordings.sh | Prompt generation validation |
| test-path-resolution.sh | Path handling edge cases |

### Example E2E Test Script

**File: test-samples/test-workflows.sh (excerpt)**

```bash
#!/bin/bash
set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup
echo -e "${YELLOW}Setting up test environment...${NC}"
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# Create sample Python project
mkdir -p src
cat > src/calculator.py <<'EOF'
def add(a, b):
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

class Calculator:
    def subtract(self, a, b):
        return a - b
EOF

echo -e "${GREEN}✓ Test environment created${NC}"

# Test 1: Analyze command
echo -e "${YELLOW}Test 1: Running docimp analyze...${NC}"
docimp analyze ./src --format json > analyze-result.json

# Validate JSON output
if ! jq '.' analyze-result.json > /dev/null 2>&1; then
  echo -e "${RED}✗ Test 1 FAILED: Invalid JSON output${NC}"
  exit 1
fi

# Check expected fields
TOTAL_ITEMS=$(jq '.total_items' analyze-result.json)
COVERAGE=$(jq '.coverage_percent' analyze-result.json)

if [ "$TOTAL_ITEMS" -lt 3 ]; then
  echo -e "${RED}✗ Test 1 FAILED: Expected at least 3 items, got $TOTAL_ITEMS${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Test 1 PASSED: analyze command ($TOTAL_ITEMS items, ${COVERAGE}% coverage)${NC}"

# Test 2: Workflow state creation
echo -e "${YELLOW}Test 2: Checking workflow state...${NC}"
if [ ! -f ".docimp/workflow-state.json" ]; then
  echo -e "${RED}✗ Test 2 FAILED: workflow-state.json not created${NC}"
  exit 1
fi

# Validate workflow state structure
SCHEMA_VERSION=$(jq -r '.schema_version' .docimp/workflow-state.json)
if [ "$SCHEMA_VERSION" != "1.0" ]; then
  echo -e "${RED}✗ Test 2 FAILED: Invalid schema version${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Test 2 PASSED: workflow state created${NC}"

# Test 3: Status command
echo -e "${YELLOW}Test 3: Running docimp status...${NC}"
STATUS_OUTPUT=$(docimp status)

if ! echo "$STATUS_OUTPUT" | grep -q "analyze:.*✓ Run"; then
  echo -e "${RED}✗ Test 3 FAILED: analyze status not shown${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Test 3 PASSED: status command${NC}"

# Test 4: Incremental analysis
echo -e "${YELLOW}Test 4: Testing incremental analysis...${NC}"

# Modify one file
echo "def divide(a, b): return a / b" >> src/calculator.py

# Run incremental analysis
docimp analyze ./src --incremental --format json > analyze-incremental.json

# Verify only one file re-analyzed
FILES_ANALYZED=$(jq '.items | map(.filepath) | unique | length' analyze-incremental.json)
if [ "$FILES_ANALYZED" -ne 1 ]; then
  echo -e "${RED}✗ Test 4 FAILED: Expected 1 file analyzed, got $FILES_ANALYZED${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Test 4 PASSED: incremental analysis${NC}"

# Cleanup
cd /
rm -rf "$TEST_DIR"
echo -e "${GREEN}All tests passed!${NC}"
```

### Running E2E Tests

```bash
# Run all E2E tests
cd test-samples
./test-workflows.sh

# Run specific test
./test-audit-resume.sh

# Run with debugging
bash -x ./test-workflows.sh
```

**CI/CD Integration** (.github/workflows/ci.yml):

```yaml
workflow-validation:
  runs-on: ubuntu-latest
  needs: [python-tests, typescript-tests]
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    - uses: astral-sh/setup-node@v4
      with:
        node-version: '24'
    - uses: astral-sh/setup-uv@v5
      with:
        version: '0.9.8'
    - name: Install dependencies
      run: |
        cd analyzer && uv pip sync requirements-dev.lock && uv pip install -e .
        cd ../cli && npm ci && npm run build
    - name: Install jq
      run: sudo apt-get install -y jq
    - name: Run workflow validation tests
      run: ./test-samples/test-workflows.sh
```

---

## Quick Reference

### Running All Tests

```bash
# Python tests
cd analyzer && uv run pytest -v

# TypeScript tests
cd cli && uv run npm test

# Plugin tests
cd plugins && uv run npm test

# E2E tests
cd test-samples && ./test-workflows.sh

# All tests in CI/CD
./.github/workflows/ci.yml
```

### Test File Locations

| Layer | Location | Count |
|-------|----------|-------|
| Python Unit | `analyzer/tests/test_*.py` | 42 files, 476+ tests |
| TypeScript Unit | `cli/src/__tests__/**/*.test.ts` | 50+ files, 447+ tests |
| JavaScript Plugin | `plugins/__tests__/*.test.js` | 3 files |
| E2E Bash | `test-samples/*.sh` | 8 scripts |

### Common Test Commands

```bash
# Run tests with coverage
cd analyzer && uv run pytest --cov=src --cov-report=term
cd cli && uv run npm test -- --coverage

# Run specific test file
cd analyzer && uv run pytest tests/test_parsers.py -v
cd cli && uv run npm test -- status.test.ts

# Run tests by marker/pattern
cd analyzer && uv run pytest -m integration
cd cli && uv run npm test -- --testPathPattern="integration"

# Run tests in watch mode
cd cli && uv run npm test -- --watch
```

---

## Troubleshooting

### Problem: Tests Pass Locally But Fail in CI

**Symptoms:**
- All tests pass on development machine
- CI/CD pipeline shows failures
- Errors like "ENOENT: no such file or directory"

**Solution:**

Check for absolute path dependencies:

```typescript
// WRONG: Absolute path (breaks in CI)
const configPath = '/Users/me/project/docimp.config.js';

// RIGHT: Relative path
const configPath = path.join(process.cwd(), 'docimp.config.js');
```

Ensure temp directories cleaned up:

```typescript
afterEach(async () => {
  await fs.rm(tempDir, { recursive: true, force: true });
});
```

### Problem: Jest Tests Timeout

**Symptoms:**
- Tests hang indefinitely
- Jest timeout error after 5 seconds

**Solution:**

Increase timeout for slow tests:

```typescript
it('runs slow operation', async () => {
  // Increase timeout to 30 seconds
  jest.setTimeout(30000);
  await slowOperation();
}, 30000); // Also set timeout here
```

Or configure globally in jest.config.js:

```javascript
export default {
  testTimeout: 10000, // 10 seconds default
};
```

### Problem: Python Tests Can't Import src Modules

**Symptoms:**
- `ModuleNotFoundError: No module named 'src'`
- Tests run in IDE but fail in CLI

**Solution:**

Add sys.path manipulation at top of test file:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.python_parser import PythonParser  # Now works
```

### Problem: Mock Not Working as Expected

**Symptoms:**
- Mock function not called
- Original function executes instead of mock

**Solution:**

Ensure correct import path for mocking:

```typescript
// WRONG: Mocking re-exported function
import { analyze } from './commands/index.js';
jest.mock('./commands/index.js');  // Doesn't work

// RIGHT: Mock at source
import { analyzeCore } from './commands/analyzeCore.js';
jest.mock('./commands/analyzeCore.js');  // Works
```

Verify mock setup:

```typescript
beforeEach(() => {
  jest.clearAllMocks();  // Clear previous test's mock calls
  mockFunction.mockReset();  // Reset implementation
  mockFunction.mockResolvedValue(mockData);  // Set return value
});
```

---

## Summary

DocImp's test infrastructure provides comprehensive coverage across four testing layers:

1. **Python Unit Tests** (476+ tests): Parser logic, scoring algorithms, data models
2. **TypeScript Unit Tests** (447+ tests): CLI commands, configuration, session management
3. **JavaScript Plugin Tests** (3 files): JSDoc validation, style enforcement
4. **E2E Bash Tests** (8 scripts): Full workflow validation, manual testing

**Key Testing Patterns:**

- **Dependency Injection**: All tests use DI for easy mocking
- **Sequential Execution**: Jest runs tests sequentially (maxWorkers: 1) to prevent race conditions
- **Comprehensive Coverage**: Unit, integration, and E2E tests at every layer
- **CI/CD Integration**: All tests run in GitHub Actions on every push

**Next Steps**: See `INFRASTRUCTURE-DOCS_9-EditorConfig-Style-Enforcement.md` for cross-editor consistency patterns.
