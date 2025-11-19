# Infrastructure Documentation: Integration Sequences

## Overview

This document provides step-by-step integration sequences for common development tasks in the DocImp project. Each sequence represents a complete workflow from initial change through CI validation, incorporating git hooks, quality checks, testing infrastructure, and deployment.

Understanding these sequences helps developers navigate the polyglot architecture efficiently, ensures consistent quality practices, and prevents common integration pitfalls. The sequences integrate all infrastructure components documented in previous sections.

## 1. Adding a New Command

### Complete Workflow

Adding a new command to DocImp involves coordinating TypeScript CLI components, Python analyzer backend, testing infrastructure, and CI/CD validation.

```
┌─────────────────────────────────────────────────────────────────┐
│                    New Command Integration Flow                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Create TypeScript │
                   │    Command Class     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Implement Python  │
                   │    Backend Logic     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Add Tests (TS+Py) │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Register in CLI   │
                   │    Entry Point       │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. Git Commit        │
                   │    (lint-staged)     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 6. CI Validation     │
                   │    (5 jobs pass)     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 7. PR Review & Merge │
                   └──────────────────────┘
```

### Step 1: Create TypeScript Command Class

**File Location**: `cli/src/commands/<name>Command.ts`

**Template**:
```typescript
// cli/src/commands/exampleCommand.ts
import { Command } from 'commander';
import { PythonBridge } from '../python-bridge/PythonBridge.js';
import { StateManager } from '../utils/StateManager.js';
import { TerminalDisplay } from '../display/TerminalDisplay.js';

/**
 * Implements the 'example' command for DocImp.
 */
export class ExampleCommand {
  constructor(
    private readonly pythonBridge: PythonBridge,
    private readonly stateManager: StateManager,
    private readonly display: TerminalDisplay
  ) {}

  /**
   * Registers the 'example' command with Commander.
   */
  register(program: Command): void {
    program
      .command('example')
      .description('Example command description')
      .argument('<path>', 'Path to analyze')
      .option('--flag', 'Example flag')
      .action(async (path: string, options: { flag?: boolean }) => {
        await this.execute(path, options);
      });
  }

  /**
   * Core execution logic (testable, no process.exit).
   */
  async execute(
    path: string,
    options: { flag?: boolean }
  ): Promise<void> {
    // Implementation here
    this.display.info('Executing example command...');

    // Call Python backend
    const result = await this.pythonBridge.callPython(
      'example',
      [path],
      { flag: options.flag }
    );

    // Display results
    this.display.success('Example command completed!');
  }
}
```

**Key Principles**:
- Constructor injection for all dependencies (PythonBridge, StateManager, TerminalDisplay)
- Separate `register()` and `execute()` methods (error handling pattern)
- No `process.exit()` in `execute()` (testability)
- Commander auto-converts kebab-case (`--my-flag`) to camelCase (`options.myFlag`)

### Step 2: Implement Python Backend Logic

**File Location**: `analyzer/src/main.py`

**Add Command Handler**:
```python
# analyzer/src/main.py
def handle_example_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the 'example' command from TypeScript CLI."""
    path = args.get('path')
    flag = args.get('flag', False)

    # Import dependencies
    from src.analyzer import DocumentationAnalyzer
    from src.parsers.python_parser import PythonParser
    from src.parsers.typescript_parser import TypeScriptParser

    # Create analyzer instance
    analyzer = DocumentationAnalyzer(
        parsers=[PythonParser(), TypeScriptParser()]
    )

    # Execute logic
    result = analyzer.example_operation(path, flag=flag)

    # Return JSON-serializable result
    return {
        'status': 'success',
        'data': result.to_dict()
    }

# Register in command dispatch
COMMANDS = {
    'analyze': handle_analyze_command,
    'audit': handle_audit_command,
    'example': handle_example_command,  # Add here
}
```

**Communication Protocol**:
- TypeScript sends: `{ command: 'example', args: { path: '...', flag: true } }`
- Python returns: `{ status: 'success', data: {...} }` via stdout
- Errors: `{ status: 'error', message: '...', details: {...} }`

### Step 3: Add Tests

**TypeScript Tests**: `cli/src/__tests__/commands/example-command.test.ts`

```typescript
import { ExampleCommand } from '../../commands/exampleCommand.js';
import { PythonBridge } from '../../python-bridge/PythonBridge.js';
import { StateManager } from '../../utils/StateManager.js';
import { TerminalDisplay } from '../../display/TerminalDisplay.js';

describe('ExampleCommand', () => {
  let command: ExampleCommand;
  let mockPythonBridge: jest.Mocked<PythonBridge>;
  let mockStateManager: jest.Mocked<StateManager>;
  let mockDisplay: jest.Mocked<TerminalDisplay>;

  beforeEach(() => {
    // Create mocks
    mockPythonBridge = {
      callPython: jest.fn(),
    } as any;

    mockStateManager = {} as any;
    mockDisplay = {
      info: jest.fn(),
      success: jest.fn(),
      error: jest.fn(),
    } as any;

    // Instantiate with mocks
    command = new ExampleCommand(
      mockPythonBridge,
      mockStateManager,
      mockDisplay
    );
  });

  it('should execute example command successfully', async () => {
    // Arrange
    mockPythonBridge.callPython.mockResolvedValue({
      status: 'success',
      data: { result: 'example output' },
    });

    // Act
    await command.execute('/path/to/code', { flag: true });

    // Assert
    expect(mockPythonBridge.callPython).toHaveBeenCalledWith(
      'example',
      ['/path/to/code'],
      { flag: true }
    );
    expect(mockDisplay.success).toHaveBeenCalledWith(
      'Example command completed!'
    );
  });
});
```

**Python Tests**: `analyzer/tests/test_example_command.py`

```python
import pytest
from src.main import handle_example_command

def test_example_command_success():
    """Test example command executes successfully."""
    args = {
        'path': 'test-samples/example-project',
        'flag': True
    }

    result = handle_example_command(args)

    assert result['status'] == 'success'
    assert 'data' in result
    assert result['data']['result'] == 'expected output'

def test_example_command_invalid_path():
    """Test example command handles invalid path."""
    args = {
        'path': '/nonexistent/path',
        'flag': False
    }

    with pytest.raises(FileNotFoundError):
        handle_example_command(args)
```

### Step 4: Register in CLI Entry Point

**File**: `cli/src/index.ts`

```typescript
// cli/src/index.ts
import { ExampleCommand } from './commands/exampleCommand.js';

// Instantiate dependencies (single instantiation point)
const pythonBridge = new PythonBridge(config);
const stateManager = new StateManager(config);
const display = new TerminalDisplay();

// Instantiate command
const exampleCommand = new ExampleCommand(
  pythonBridge,
  stateManager,
  display
);

// Register with Commander
exampleCommand.register(program);

// Parse arguments
program.parse();
```

### Step 5: Git Commit (Automated Quality Checks)

**Commit Process**:
```bash
# Stage changes
git add cli/src/commands/exampleCommand.ts
git add cli/src/__tests__/commands/example-command.test.ts
git add analyzer/src/main.py
git add analyzer/tests/test_example_command.py
git add cli/src/index.ts

# Commit (triggers lint-staged pre-commit hook)
git commit -m "Add 'example' command with TypeScript and Python integration

Implements new 'example' command that demonstrates:
- TypeScript CLI command structure
- Python backend integration
- Comprehensive test coverage
- Error handling patterns

Tests: 6 new tests (3 TS, 3 Python)
"
```

**Automated Checks (lint-staged)**:
```
Running tasks for staged files...
  ✔ Prettier: cli/src/commands/exampleCommand.ts
  ✔ ESLint: cli/src/commands/exampleCommand.ts
  ✔ Ruff format: analyzer/src/main.py
  ✔ Ruff check: analyzer/src/main.py
✔ All tasks passed!
```

### Step 6: CI Validation (GitHub Actions)

**Workflow**: `.github/workflows/ci.yml` runs 5 jobs

```
Job 1: Python Tests
  ✓ Lint (ruff check)
  ✓ Format check (ruff format --check)
  ✓ Type check (mypy)
  ✓ Tests (pytest) - Including new test_example_command.py

Job 2: TypeScript Tests
  ✓ Lint (eslint)
  ✓ Format check (prettier)
  ✓ JSDoc lint
  ✓ Type check (tsc --noEmit)
  ✓ Build (npm run build)
  ✓ Tests (jest) - Including new example-command.test.ts
  ✓ Integration tests

Job 3: Integration Test
  ✓ E2E pipeline test (docimp analyze)

Job 4: Module System Tests
  ✓ ESM/CommonJS detection

Job 5: Workflow Validation
  ✓ test-workflows.sh
```

**Time**: ~4-6 minutes for all jobs (parallel execution)

### Step 7: PR Review & Merge

**PR Template**:
```markdown
## Summary
Adds new `docimp example` command with full TypeScript/Python integration.

## Changes
- **TypeScript**: `ExampleCommand` class with dependency injection
- **Python**: `handle_example_command()` in main.py
- **Tests**: 6 new tests (3 TS, 3 Python)
- **CI**: All 5 jobs passing

## Testing
- [x] Unit tests pass locally (jest + pytest)
- [x] Integration tests pass
- [x] CI validates all jobs
- [x] Manual testing: `docimp example ./test-samples/example-project`

## Checklist
- [x] Follows dependency injection pattern
- [x] Error handling implemented
- [x] Tests provide >80% coverage
- [x] Documentation updated (if needed)
```

**Review Criteria** (See INFRASTRUCTURE-DOCS_3-Claude-Code-Config.md):
- Dependency injection compliance
- Error handling pattern adherence
- Test coverage adequacy
- TypeScript/Python integration correctness

---

## 2. Modifying a Parser

### Complete Workflow

Parsers are critical components that extract `CodeItem` objects from source files. Changes require careful validation across multiple languages and edge cases.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Parser Modification Flow                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Edit Parser Code  │
                   │    (Python)          │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Add Unit Tests    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Add Edge-Case     │
                   │    Test Samples      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Run Local Tests   │
                   │    (pytest -v)       │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. Test Against      │
                   │    Real Codebases    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 6. Git Commit        │
                   │    (ruff format)     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 7. CI: Module System │
                   │    & Workflow Tests  │
                   └──────────────────────┘
```

### Step 1: Edit Parser Code

**Example: Adding Async Function Support to PythonParser**

**File**: `analyzer/src/parsers/python_parser.py`

```python
# analyzer/src/parsers/python_parser.py
import ast
from typing import List
from .base_parser import BaseParser
from ..models import CodeItem

class PythonParser(BaseParser):
    """Parser for Python files using AST."""

    def parse_file(self, filepath: str) -> List[CodeItem]:
        """Parse a Python file and extract CodeItem objects."""
        items = []

        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                items.append(self._extract_function(node, filepath))
            elif isinstance(node, ast.AsyncFunctionDef):  # NEW
                items.append(self._extract_async_function(node, filepath))
            elif isinstance(node, ast.ClassDef):
                items.append(self._extract_class(node, filepath))

        return items

    def _extract_async_function(
        self, node: ast.AsyncFunctionDef, filepath: str
    ) -> CodeItem:
        """Extract CodeItem from async function definition."""
        return CodeItem(
            name=node.name,
            type='function',  # Treat async as regular function
            filepath=filepath,
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            language='python',
            complexity=self._calculate_complexity(node),
            impact_score=0.0,  # Calculated later
            has_docs=ast.get_docstring(node) is not None,
            parameters=[arg.arg for arg in node.args.args],
            return_type=self._extract_return_annotation(node),
            docstring=ast.get_docstring(node),
            export_type='internal',
            module_system='unknown',
            audit_rating=None
        )
```

**Rationale**:
- `ast.AsyncFunctionDef` represents `async def` functions
- Treated as regular functions (type='function') for documentation purposes
- Complexity calculation applies same logic as sync functions

### Step 2: Add Unit Tests

**File**: `analyzer/tests/test_parser_python.py`

```python
# analyzer/tests/test_parser_python.py
import pytest
from src.parsers.python_parser import PythonParser

def test_parse_async_function():
    """Test parsing async function definitions."""
    code = '''
async def fetch_data(url: str) -> dict:
    """Fetch data from URL asynchronously."""
    return await http.get(url)
'''

    parser = PythonParser()
    # Create temp file with code
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False
    ) as f:
        f.write(code)
        filepath = f.name

    try:
        items = parser.parse_file(filepath)

        assert len(items) == 1
        assert items[0].name == 'fetch_data'
        assert items[0].type == 'function'
        assert items[0].has_docs is True
        assert items[0].parameters == ['url']
        assert items[0].return_type == 'dict'
    finally:
        os.unlink(filepath)

def test_parse_async_function_without_docs():
    """Test async function without docstring."""
    code = '''
async def process():
    await task()
'''

    parser = PythonParser()
    # ... similar setup ...

    items = parser.parse_file(filepath)
    assert items[0].has_docs is False
```

### Step 3: Add Edge-Case Test Samples

**File**: `test-samples/edge-cases/python_async_patterns.py`

```python
# test-samples/edge-cases/python_async_patterns.py
"""Edge cases for async function parsing."""

# Basic async function
async def simple_async():
    """Simple async function."""
    pass

# Async function with complex signature
async def complex_async(
    param1: str,
    param2: int = 10,
    *args,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """Complex async signature."""
    pass

# Async method in class
class AsyncHandler:
    async def handle(self, data):
        """Async method."""
        pass

    @staticmethod
    async def static_async():
        """Static async method."""
        pass

# Async generator
async def async_generator():
    """Async generator function."""
    yield 1

# Nested async function
async def outer():
    """Outer async function."""
    async def inner():
        """Inner async function."""
        pass
    await inner()
```

**Purpose**: Validate parser handles:
- Basic async functions
- Complex signatures
- Async methods (instance, static)
- Async generators
- Nested async functions

### Step 4: Run Local Tests

**Commands**:
```bash
# Run all parser tests
uv run pytest analyzer/tests/test_parser_python.py -v

# Run specific test
uv run pytest analyzer/tests/test_parser_python.py::test_parse_async_function -v

# Run with coverage
uv run pytest analyzer/tests/test_parser_python.py -v \
  --cov=analyzer/src/parsers/python_parser \
  --cov-report=term-missing
```

**Expected Output**:
```
test_parser_python.py::test_parse_async_function PASSED           [ 20%]
test_parser_python.py::test_parse_async_function_without_docs PASSED [ 40%]
test_parser_python.py::test_parse_class PASSED                    [ 60%]
test_parser_python.py::test_parse_nested_functions PASSED         [ 80%]
test_parser_python.py::test_parse_edge_cases PASSED               [100%]

---------- coverage: platform darwin, python 3.13.0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
analyzer/src/parsers/python_parser.py      87      2    98%   45, 102
---------------------------------------------------------------------
TOTAL                                      87      2    98%
```

### Step 5: Test Against Real Codebases

**Validation Commands**:
```bash
# Test against DocImp's own Python code
docimp analyze analyzer/src --format json > /tmp/analysis.json

# Verify async functions detected
jq '.items[] | select(.name | contains("async"))' /tmp/analysis.json

# Test against external projects
docimp analyze ~/Code/external-project/src --format json

# Check for parsing errors
jq '.parse_failures' /tmp/analysis.json
```

**Validation Criteria**:
- No new parse failures introduced
- Async functions correctly identified
- Complexity scores reasonable
- No false positives/negatives

### Step 6: Git Commit

```bash
# Stage changes
git add analyzer/src/parsers/python_parser.py
git add analyzer/tests/test_parser_python.py
git add test-samples/edge-cases/python_async_patterns.py

# Commit (ruff auto-formats via lint-staged)
git commit -m "Add async function support to PythonParser

Extends PythonParser to correctly handle async function definitions:
- Detects ast.AsyncFunctionDef nodes
- Extracts parameters, return types, docstrings
- Calculates complexity for async functions
- Treats async as regular functions for documentation

Tests: 2 new unit tests + edge-case sample file
Coverage: 98% on python_parser.py
"
```

### Step 7: CI Validation

**Module System Tests** (Job 4 in CI):
```yaml
# .github/workflows/ci.yml (excerpt)
- name: Test Module System Detection
  run: |
    uv run python -c "
    from src.parsers.python_parser import PythonParser
    parser = PythonParser()
    items = parser.parse_file('test-samples/edge-cases/python_async_patterns.py')
    assert any(item.name == 'simple_async' for item in items)
    assert any(item.name == 'complex_async' for item in items)
    print('✓ Async function parsing validated')
    "
```

**Workflow Validation Tests** (Job 5 in CI):
```bash
# test-samples/test-workflows.sh validates end-to-end parsing
./test-samples/test-workflows.sh
```

---

## 3. Adding a New Plugin

### Complete Workflow

Plugins extend DocImp's validation capabilities through JavaScript hooks. This sequence demonstrates adding a custom validation plugin.

```
┌─────────────────────────────────────────────────────────────────┐
│                      New Plugin Integration                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Create Plugin File│
                   │    (JavaScript)      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Implement Hooks   │
                   │    (beforeAccept)    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Add Plugin Tests  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Register in Config│
                   │    (docimp.config.js)│
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. Test Manually     │
                   │    (docimp improve)  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 6. Commit & CI Check │
                   └──────────────────────┘
```

### Step 1: Create Plugin File

**File**: `plugins/validate-length.js`

```javascript
/**
 * Plugin to validate docstring length constraints.
 *
 * Ensures documentation is neither too brief (< 20 chars) nor
 * excessively verbose (> 500 chars).
 */

/**
 * Validate docstring before accepting it.
 *
 * @param {string} docstring - Generated documentation
 * @param {object} item - CodeItem being documented
 * @param {object} config - DocImp configuration
 * @returns {{accept: boolean, reason?: string, autoFix?: string}}
 */
export function beforeAccept(docstring, item, config) {
  const MIN_LENGTH = 20;
  const MAX_LENGTH = 500;

  const length = docstring.trim().length;

  // Too brief
  if (length < MIN_LENGTH) {
    return {
      accept: false,
      reason: `Docstring too brief (${length} chars, minimum ${MIN_LENGTH}). ` +
              'Please provide more detailed explanation.',
    };
  }

  // Too verbose
  if (length > MAX_LENGTH) {
    return {
      accept: false,
      reason: `Docstring too verbose (${length} chars, maximum ${MAX_LENGTH}). ` +
              'Please be more concise.',
    };
  }

  // Valid length
  return { accept: true };
}

/**
 * Plugin metadata.
 */
export const metadata = {
  name: 'validate-length',
  version: '1.0.0',
  description: 'Validates docstring length constraints',
};
```

**Key Features**:
- ESM export format (`export function`)
- Returns `PluginResult` object
- `accept: false` blocks documentation acceptance
- `reason` provides user feedback

### Step 2: Implement Advanced Hooks

**Example: Auto-Fix Capability**

```javascript
// plugins/validate-length.js (enhanced)
export function beforeAccept(docstring, item, config) {
  const MIN_LENGTH = 20;
  const MAX_LENGTH = 500;

  const trimmed = docstring.trim();
  const length = trimmed.length;

  // Too brief - no auto-fix (needs human expansion)
  if (length < MIN_LENGTH) {
    return {
      accept: false,
      reason: `Docstring too brief (${length} chars, minimum ${MIN_LENGTH})`,
    };
  }

  // Too verbose - offer auto-fix (truncate with ellipsis)
  if (length > MAX_LENGTH) {
    const truncated = trimmed.substring(0, MAX_LENGTH - 3) + '...';

    return {
      accept: false,
      reason: `Docstring too verbose (${length} chars, maximum ${MAX_LENGTH})`,
      autoFix: truncated,  // Suggested fix
    };
  }

  return { accept: true };
}
```

**Auto-Fix Behavior**:
- User sees: "Docstring too verbose (532 chars, maximum 500)"
- Option: `[A]ccept auto-fix` to use truncated version
- Alternative: `[R]egenerate` to get new suggestion from Claude

### Step 3: Add Plugin Tests

**File**: `plugins/__tests__/validate-length.test.js`

```javascript
// plugins/__tests__/validate-length.test.js
import { beforeAccept, metadata } from '../validate-length.js';

describe('validate-length plugin', () => {
  const mockItem = {
    name: 'exampleFunction',
    type: 'function',
    filepath: 'example.ts',
  };

  const mockConfig = {};

  it('should accept docstring with valid length', () => {
    const docstring = 'This is a valid docstring with sufficient detail.';

    const result = beforeAccept(docstring, mockItem, mockConfig);

    expect(result.accept).toBe(true);
    expect(result.reason).toBeUndefined();
  });

  it('should reject docstring that is too brief', () => {
    const docstring = 'Too short';

    const result = beforeAccept(docstring, mockItem, mockConfig);

    expect(result.accept).toBe(false);
    expect(result.reason).toContain('too brief');
    expect(result.reason).toContain('9 chars');
  });

  it('should reject docstring that is too verbose', () => {
    const docstring = 'x'.repeat(550);  // 550 chars

    const result = beforeAccept(docstring, mockItem, mockConfig);

    expect(result.accept).toBe(false);
    expect(result.reason).toContain('too verbose');
    expect(result.reason).toContain('550 chars');
  });

  it('should provide auto-fix for verbose docstrings', () => {
    const docstring = 'x'.repeat(550);

    const result = beforeAccept(docstring, mockItem, mockConfig);

    expect(result.autoFix).toBeDefined();
    expect(result.autoFix.length).toBe(500);
    expect(result.autoFix).toMatch(/\.\.\.$/);  // Ends with ellipsis
  });

  it('should export correct metadata', () => {
    expect(metadata.name).toBe('validate-length');
    expect(metadata.version).toBe('1.0.0');
  });
});
```

**Run Tests**:
```bash
cd plugins
npm test validate-length.test.js
```

### Step 4: Register in Configuration

**File**: `docimp.config.js`

```javascript
// docimp.config.js
export default {
  // ... other config ...

  plugins: [
    // Built-in plugins
    {
      name: 'validate-types',
      enabled: true,
      options: {
        strictMode: true,
        checkJSDoc: true,
      },
    },
    {
      name: 'jsdoc-style',
      enabled: true,
      options: {
        requireDescriptions: true,
        requireExamples: false,
      },
    },

    // Custom plugin
    {
      name: 'validate-length',
      enabled: true,
      path: './plugins/validate-length.js',  // Relative path
      options: {
        // Plugin-specific options (if needed)
        minLength: 20,
        maxLength: 500,
      },
    },
  ],
};
```

**Plugin Loading**:
- `name`: Plugin identifier
- `enabled`: Toggle plugin on/off
- `path`: Relative to project root (for custom plugins)
- `options`: Passed to plugin hooks as `config.pluginOptions[name]`

### Step 5: Manual Testing

**Test Command**:
```bash
# Run improve command with new plugin active
docimp improve ./test-samples/example-project --python-style google

# Expected behavior:
# 1. Claude generates docstring
# 2. validate-types checks JSDoc types
# 3. jsdoc-style enforces style rules
# 4. validate-length checks length constraints
# 5. User prompted to [A]ccept, [E]dit, [R]egenerate, [S]kip
```

**Test Cases**:

**Case 1: Brief Docstring (Should Reject)**
```
Generated Documentation:
  """Brief docs."""

Plugin Validation Failed:
  [validate-length] Docstring too brief (12 chars, minimum 20).
  Please provide more detailed explanation.

Options:
  [R]egenerate - Get new suggestion from Claude
  [E]dit - Manually edit docstring
  [S]kip - Skip this item
  [Q]uit - Exit improve session
```

**Case 2: Verbose Docstring (Should Offer Auto-Fix)**
```
Generated Documentation:
  """This is an extremely long docstring that goes on and on with
  excessive detail about trivial implementation specifics that would
  be better suited for inline comments rather than API documentation...
  [550 chars total]"""

Plugin Validation Failed:
  [validate-length] Docstring too verbose (550 chars, maximum 500)

Auto-fix available (truncated to 500 chars with ellipsis)

Options:
  [A]ccept auto-fix - Use truncated version
  [R]egenerate - Get new suggestion from Claude
  [E]dit - Manually edit docstring
  [S]kip - Skip this item
  [Q]uit - Exit improve session
```

**Case 3: Valid Docstring (Should Accept)**
```
Generated Documentation:
  """
  Calculates the Fibonacci number at position n.

  Uses memoization to avoid redundant calculations. Time complexity
  is O(n) and space complexity is O(n) due to memoization cache.
  """

All plugin validations passed ✓

Options:
  [A]ccept - Write documentation to file
  [E]dit - Manually edit before accepting
  [R]egenerate - Get different suggestion
  [S]kip - Skip this item
  [Q]uit - Exit improve session
```

### Step 6: Commit & CI Validation

**Commit**:
```bash
git add plugins/validate-length.js
git add plugins/__tests__/validate-length.test.js
git add docimp.config.js

git commit -m "Add validate-length plugin for docstring size constraints

Implements custom validation plugin:
- Enforces minimum 20 chars, maximum 500 chars
- Provides auto-fix for overly verbose docstrings
- Comprehensive test coverage (5 test cases)

Integration:
- Registered in docimp.config.js
- Manually tested with 'docimp improve'
- Works alongside built-in validate-types and jsdoc-style plugins
"
```

**CI Checks**:
- **JavaScript linting**: ESLint validates plugin code
- **JavaScript tests**: Jest runs plugin tests
- **Integration test**: E2E workflow includes plugin execution

---

## 4. Updating Quality Rules

### Complete Workflow

Quality rules (Ruff, ESLint, Prettier, TypeScript) ensure code consistency. Changes must apply retroactively to entire codebase.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Quality Rules Update Flow                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Modify Config File│
                   │    (ruff.toml, etc.) │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Apply to Codebase │
                   │    (auto-fix)        │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Run Quality Check │
                   │    (make quality)    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Commit Changes    │
                   │    (config + fixes)  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. CI Validates      │
                   │    (all repos pass)  │
                   └──────────────────────┘
```

### Example 1: Adding Python Quality Rule

**Scenario**: Enforce timezone-aware datetime usage

**Step 1: Modify Ruff Configuration**

**File**: `analyzer/pyproject.toml`

```toml
# analyzer/pyproject.toml
[tool.ruff.lint]
select = [
  "E",      # pycodestyle errors
  "F",      # pyflakes
  "DTZ",    # flake8-datetimez (NEW: enforce timezone awareness)
  "UP",     # pyupgrade
  "PTH",    # flake8-use-pathlib
  "I",      # isort
  "SIM",    # flake8-simplify
  "PERF",   # perflint
  "YTT"     # flake8-2020
]
ignore = [
  # Add exceptions if needed
  # "DTZ001",  # datetime.datetime() without tzinfo
]
```

**Step 2: Run Ruff and Fix Violations**

```bash
# Check for violations
uv run ruff check analyzer/ --select DTZ

# Expected output:
analyzer/src/utils/state_manager.py:45:15: DTZ005 datetime.datetime.now() called without a timezone
analyzer/src/cli.py:102:9: DTZ003 datetime.datetime.utcnow() is deprecated
Found 2 errors.

# Apply auto-fixes (if available)
uv run ruff check analyzer/ --select DTZ --fix

# Manual fixes required for some violations
# Edit analyzer/src/utils/state_manager.py:
# Before:
timestamp = datetime.now()

# After:
from datetime import timezone
timestamp = datetime.now(timezone.utc)

# Edit analyzer/src/cli.py:
# Before:
timestamp = datetime.utcnow()

# After:
timestamp = datetime.now(timezone.utc)
```

**Step 3: Run Full Quality Check**

```bash
# Run all quality checks
make quality

# Output:
Linting...
✓ All lint checks passed!

Type checking...
✓ mypy found no issues

Running tests...
============================= 187 passed in 4.23s =============================
✓ All tests passed!
```

**Step 4: Commit Changes**

```bash
git add analyzer/pyproject.toml
git add analyzer/src/utils/state_manager.py
git add analyzer/src/cli.py

git commit -m "Enforce timezone-aware datetime usage (Ruff DTZ rules)

Adds flake8-datetimez (DTZ) rule group to Ruff configuration:
- Detects datetime.now() without timezone
- Flags deprecated datetime.utcnow()
- Ensures all datetime objects are timezone-aware

Fixes:
- state_manager.py: Use datetime.now(timezone.utc)
- cli.py: Replace utcnow() with now(timezone.utc)

All tests pass with new stricter rules.
"
```

### Example 2: Adding TypeScript Quality Rule

**Scenario**: Enforce explicit return types on exported functions

**Step 1: Modify TypeScript Configuration**

**File**: `cli/tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,  // NEW: stricter array/object access
    "exactOptionalPropertyTypes": true  // NEW: stricter optional properties
  }
}
```

**Step 2: Fix TypeScript Errors**

```bash
# Check for new errors
cd cli
npx tsc --noEmit

# Expected output:
src/commands/analyzeCommand.ts:45:7 - error TS2339: Property may be undefined
src/utils/StateManager.ts:102:5 - error TS2375: Type 'undefined' is not assignable

# Fix violations:
# Before:
const items = result.items;  // May be undefined with noUncheckedIndexedAccess

# After:
const items = result.items ?? [];  // Explicitly handle undefined

# Before (exactOptionalPropertyTypes):
interface Config {
  timeout?: number;  // Can be number | undefined
}
const config: Config = { timeout: undefined };  // ERROR

# After:
const config: Config = {};  // Omit optional property instead
```

**Step 3: Validate Formatting and Linting**

```bash
# Format check
npm run format:check

# Lint
npm run lint

# Build
npm run build

# All tests
npm run test:all
```

**Step 4: Commit Changes**

```bash
git add cli/tsconfig.json
git add cli/src/commands/analyzeCommand.ts
git add cli/src/utils/StateManager.ts

git commit -m "Enable stricter TypeScript compiler checks

Enables two additional strict checks:
- noUncheckedIndexedAccess: Prevent undefined access errors
- exactOptionalPropertyTypes: Stricter optional property handling

Fixes:
- analyzeCommand.ts: Add nullish coalescing for array access
- StateManager.ts: Omit optional properties instead of setting undefined

Build and tests pass with stricter type checking.
"
```

### Example 3: Updating ESLint Rules

**Scenario**: Enforce consistent import ordering

**Step 1: Update ESLint Configuration**

**File**: `cli/eslint.config.mjs`

```javascript
// cli/eslint.config.mjs
import importPlugin from 'eslint-plugin-import';

export default [
  // ... other configs ...

  {
    plugins: {
      import: importPlugin,
    },
    rules: {
      // Import ordering
      'import/order': [
        'error',
        {
          groups: [
            'builtin',   // Node.js built-ins (fs, path)
            'external',  // node_modules
            'internal',  // Aliased imports (@/...)
            'parent',    // ../
            'sibling',   // ./
            'index',     // ./index
          ],
          'newlines-between': 'always',  // Require blank lines between groups
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
        },
      ],

      // No default exports (prefer named exports)
      'import/no-default-export': 'warn',

      // Enforce .js extensions in imports (ESM requirement)
      'import/extensions': ['error', 'ignorePackages'],
    },
  },
];
```

**Step 2: Auto-Fix Import Violations**

```bash
# Check violations
cd cli
npm run lint

# Output:
src/commands/analyzeCommand.ts
  5:1  error  Run autofix to sort imports  import/order
  12:1 error  Run autofix to sort imports  import/order

# Auto-fix
npm run lint -- --fix

# Before:
import { TerminalDisplay } from '../display/TerminalDisplay.js';
import { readFileSync } from 'fs';
import { PythonBridge } from '../python-bridge/PythonBridge.js';
import chalk from 'chalk';

// After (alphabetized, grouped, blank lines):
import { readFileSync } from 'fs';

import chalk from 'chalk';

import { PythonBridge } from '../python-bridge/PythonBridge.js';
import { TerminalDisplay } from '../display/TerminalDisplay.js';
```

**Step 3: Commit Changes**

```bash
git add cli/eslint.config.mjs
git add cli/src/**/*.ts  # Import order fixes

git commit -m "Enforce consistent import ordering (ESLint import plugin)

Configures eslint-plugin-import for consistent import statements:
- Alphabetical ordering within groups
- Blank lines between import groups (builtin, external, internal)
- Enforce .js extensions for ESM compatibility
- Warn on default exports (prefer named exports)

Auto-fixed 47 files with import order violations.
All tests pass.
"
```

---

## 5. Updating Dependencies

### Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Dependency Update Flow                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Check for Updates │
                   │    (npm outdated)    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Update Lockfiles  │
                   │    (uv add, npm)     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Run Tests Locally │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Review Changelog  │
                   │    (breaking changes)│
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. Commit Lockfiles  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 6. CI Validates      │
                   └──────────────────────┘
```

### Python Dependencies (uv)

**Step 1: Check for Updates**

```bash
# List outdated packages
uv pip list --outdated

# Output:
Package         Version   Latest
anthropic       0.72.0    0.85.0
pydantic        2.12.3    2.15.1
pytest          7.4.0     8.0.2
```

**Step 2: Update Dependencies**

```bash
# Update specific package
uv add "anthropic>=0.85.0,<1.0.0"

# Or update all in pyproject.toml and regenerate lock
uv pip compile pyproject.toml -o requirements.lock
uv pip compile pyproject.toml --extra dev -o requirements-dev.lock

# Sync environment
uv pip sync requirements-dev.lock
```

**Step 3: Test**

```bash
uv run pytest -v
uv run ruff check .
uv run mypy src --ignore-missing-imports
```

**Step 4: Review Breaking Changes**

```bash
# Check anthropic changelog
# https://github.com/anthropics/anthropic-sdk-python/releases

# Key changes in 0.85.0:
# - New streaming API
# - Deprecated: client.completions (use client.messages)
# - Breaking: timeout parameter renamed to http_timeout
```

**Step 5: Adapt Code to Breaking Changes**

```python
# analyzer/src/claude.py
# Before:
client = anthropic.Client(
    api_key=api_key,
    timeout=30
)

# After (0.85.0):
client = anthropic.Client(
    api_key=api_key,
    http_timeout=30  # Renamed parameter
)
```

**Step 6: Commit**

```bash
git add pyproject.toml requirements.lock requirements-dev.lock uv.lock
git add analyzer/src/claude.py  # Breaking change adaptation

git commit -m "Update anthropic SDK to 0.85.0

Updates:
- anthropic: 0.72.0 → 0.85.0
- pydantic: 2.12.3 → 2.15.1
- pytest: 7.4.0 → 8.0.2

Breaking Changes:
- Renamed 'timeout' to 'http_timeout' in Client constructor
- Updated claude.py to use new parameter name

All tests pass with updated dependencies.
"
```

### TypeScript Dependencies (npm)

**Step 1: Check for Updates**

```bash
cd cli
npm outdated

# Output:
Package               Current  Wanted  Latest
@types/node           24.0.0   24.5.3  24.5.3
eslint                9.0.0    9.2.1   9.2.1
typescript            5.7.2    5.7.5   5.7.5
```

**Step 2: Update**

```bash
# Update specific package
npm install typescript@latest

# Update all to 'wanted' versions (respects semver in package.json)
npm update

# Update all to 'latest' (may break compatibility)
npm install <package>@latest
```

**Step 3: Regenerate Lockfile**

```bash
# After npm update or npm install
# package-lock.json automatically updated

# Verify lockfile consistency
npm ci  # Clean install from lockfile
```

**Step 4: Test**

```bash
npm run build
npm run lint
npm test
npm run test:integration
```

**Step 5: Commit**

```bash
git add cli/package.json cli/package-lock.json

git commit -m "Update TypeScript dependencies

Updates:
- typescript: 5.7.2 → 5.7.5 (patch)
- eslint: 9.0.0 → 9.2.1 (minor)
- @types/node: 24.0.0 → 24.5.3 (patch)

No breaking changes. All tests pass.
"
```

---

## 6. Adding Documentation

### Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Documentation Addition Flow                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 1. Create .md File   │
                   │    (docs/patterns/)  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 2. Write Content     │
                   │    (examples, code)  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 3. Reference in      │
                   │    CLAUDE.md         │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 4. Check CLAUDE.md   │
                   │    Size (< 40K)      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ 5. Commit Both Files │
                   └──────────────────────┘
```

### Example: Adding New Pattern Documentation

**Step 1: Create Documentation File**

**File**: `docs/patterns/caching-strategy.md`

```markdown
# Caching Strategy

## Overview

DocImp employs selective caching to optimize performance while maintaining
correctness. This document details the caching patterns used across the system.

## 1. Plugin Validation Cache

### Location
`plugins/validate-types.js`

### Pattern
Module-level performance cache (documented exception to DI pattern)

### Implementation
\`\`\`javascript
// Cache TypeScript compiler programs (expensive to create)
const compilerCache = new Map();

export function beforeAccept(docstring, item, config) {
  const filepath = item.filepath;

  // Check cache
  if (compilerCache.has(filepath)) {
    return compilerCache.get(filepath);
  }

  // Create program (expensive)
  const program = createTypeScriptProgram(filepath);

  // Cache for reuse
  compilerCache.set(filepath, program);

  return program;
}
\`\`\`

### Rationale
- TypeScript program creation is expensive (100-500ms)
- Same file validated multiple times during improve session
- Cache hit rate: 80-90% in typical sessions
- Invalidation: Not needed (session lifetime only)

## 2. Checksum Cache

### Location
`analyzer/src/utils/state_manager.py`

### Pattern
File-level checksum memoization

### Implementation
\`\`\`python
class StateManager:
    def __init__(self):
        self._checksum_cache = {}

    def calculate_checksum(self, filepath: str) -> str:
        # Check cache
        if filepath in self._checksum_cache:
            return self._checksum_cache[filepath]

        # Calculate SHA-256
        with open(filepath, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        # Cache
        self._checksum_cache[filepath] = checksum
        return checksum
\`\`\`

### Cache Invalidation
- Cleared on new command execution
- Per-process lifetime only
- File modifications detected via timestamp in incremental mode

## Quick Reference

| Cache Type         | Location            | Lifetime   | Invalidation      |
|--------------------|---------------------|------------|-------------------|
| TypeScript Program | validate-types.js   | Session    | None (session end)|
| File Checksums     | state_manager.py    | Process    | New command run   |
| Workflow State     | .docimp/workflow-state.json | Persistent | File modifications|

## Summary

- **Plugin cache**: Session-scoped, no invalidation needed
- **Checksum cache**: Process-scoped, cleared on new command
- **Workflow state**: Persistent, invalidated by file changes
```

**Step 2: Reference in CLAUDE.md**

**File**: `CLAUDE.md`

```markdown
## Dependency Injection Pattern

**Core Principle**: All dependencies passed as required parameters; only entry points (main.py, index.ts) instantiate objects.

**Documented exceptions**: Module-level performance caches (plugin layer), optional dependencies with defaults (backward compatibility), environment variable fallback pattern (TypeScriptParser hybrid approach).

- @docs/patterns/dependency-injection.md
- @docs/patterns/caching-strategy.md  <!-- NEW REFERENCE -->
```

**Step 3: Check CLAUDE.md Size**

```bash
wc -c CLAUDE.md

# Output:
28456 CLAUDE.md

# Status: 28.5K / 40K (71% - safe margin)
```

**Step 4: Commit**

```bash
git add docs/patterns/caching-strategy.md
git add CLAUDE.md

git commit -m "Add caching strategy documentation

Documents three caching patterns used in DocImp:
1. Plugin validation cache (TypeScript program reuse)
2. Checksum cache (SHA-256 memoization)
3. Workflow state cache (persistent file tracking)

Includes rationale, implementation examples, and invalidation strategies.

Referenced in CLAUDE.md under Dependency Injection section.
CLAUDE.md size: 28.5K / 40K (71%)
"
```

---

## 7. Troubleshooting Integration Issues

### Common Issues and Solutions

#### Issue 1: lint-staged Fails on Commit

**Symptom**:
```
$ git commit -m "Add feature"
✖ eslint --fix:
  /path/to/file.ts
    45:12  error  Missing return type  @typescript-eslint/explicit-function-return-type

husky - pre-commit hook exited with code 1 (error)
```

**Solution**:
```bash
# Fix ESLint errors manually
npm run lint -- --fix

# Or bypass pre-commit for emergency commits (NOT RECOMMENDED)
git commit --no-verify -m "WIP: debugging issue"
```

#### Issue 2: CI Fails but Local Tests Pass

**Symptom**:
```
CI Python Tests: FAILED
  E   ModuleNotFoundError: No module named 'anthropic'
```

**Cause**: Lockfile out of sync with pyproject.toml

**Solution**:
```bash
# Regenerate lockfiles
uv pip compile pyproject.toml -o requirements.lock
uv pip compile pyproject.toml --extra dev -o requirements-dev.lock

# Commit lockfiles
git add requirements.lock requirements-dev.lock
git commit -m "Sync lockfiles with pyproject.toml"
```

#### Issue 3: Module System Tests Fail After Parser Change

**Symptom**:
```
CI Module System Tests: FAILED
  AssertionError: assert False
  assert any(item.module_system == 'esm' for item in items)
```

**Cause**: Parser not correctly setting `module_system` field

**Solution**:
```python
# analyzer/src/parsers/typescript_parser.py
def _determine_module_system(self, tree: Any) -> str:
    """Detect ESM vs CommonJS."""
    has_esm = any(
        isinstance(node, (ast.Export, ast.Import))
        for node in ast.walk(tree)
    )
    return 'esm' if has_esm else 'commonjs'

# Update CodeItem creation:
item = CodeItem(
    # ... other fields ...
    module_system=self._determine_module_system(tree)  # Add this
)
```

---

## Quick Reference

### Integration Sequences Summary

| Task                    | Key Files Modified                          | Tests Required       | CI Jobs Affected |
|-------------------------|---------------------------------------------|----------------------|------------------|
| Add Command             | `*Command.ts`, `main.py`, `index.ts`        | TS + Python          | All 5 jobs       |
| Modify Parser           | `*_parser.py`, `test_parser_*.py`           | Python + E2E         | Jobs 1, 3, 4, 5  |
| Add Plugin              | `plugins/*.js`, `docimp.config.js`          | JavaScript           | Job 2            |
| Update Quality Rules    | `ruff.toml`, `eslint.config.mjs`, etc.      | All                  | Jobs 1, 2        |
| Update Dependencies     | `pyproject.toml`, `package.json`, lockfiles | All                  | All 5 jobs       |
| Add Documentation       | `docs/patterns/*.md`, `CLAUDE.md`           | None (manual review) | None             |

### Command Cheatsheet

```bash
# Local Development
make quality                          # Run all quality checks
uv run pytest -v --cov                # Python tests with coverage
cd cli && npm run test:all            # TypeScript + integration tests

# Quality Checks
uv run ruff format .                  # Format Python code
uv run ruff check . --fix             # Lint Python with auto-fix
cd cli && npm run format              # Format TypeScript/JavaScript
cd cli && npm run lint -- --fix       # Lint with auto-fix

# Dependency Management
uv add "package>=1.0.0,<2.0.0"        # Add Python dependency
cd cli && npm install package@latest  # Add TypeScript dependency
uv pip sync requirements-dev.lock     # Sync Python environment
cd cli && npm ci                      # Clean install from lockfile

# Documentation
wc -c CLAUDE.md                       # Check CLAUDE.md size (< 40K)
```

---

## Summary

Integration sequences provide step-by-step workflows for common development tasks:

- **New Command**: TypeScript CLI + Python backend + tests + registration
- **Parser Modification**: Code changes + unit tests + edge-case samples + CI validation
- **Plugin Addition**: JavaScript implementation + tests + configuration + manual testing
- **Quality Rules**: Config update + codebase application + commit + CI validation
- **Dependency Updates**: Check outdated + update lockfiles + adapt breaking changes + test
- **Documentation**: Create .md file + reference in CLAUDE.md + size check + commit

All sequences integrate git hooks (lint-staged), quality checks (Ruff, ESLint), testing infrastructure (pytest, Jest), and CI/CD validation (GitHub Actions). Following these patterns ensures consistent quality and prevents integration failures.

**Next Steps**: See `INFRASTRUCTURE-DOCS_18-Critical-Dependencies.md` for detailed dependency requirements and constraints.
