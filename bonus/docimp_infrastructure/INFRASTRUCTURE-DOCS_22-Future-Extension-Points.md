# Infrastructure Documentation: Future Extension Points

## Overview

DocImp's infrastructure is designed for extensibility. This document identifies clear extension points for adding new features, tools, quality checks, and documentation without disrupting existing architecture.

Each extension point includes file locations, templates, integration steps, and examples. Understanding these patterns enables developers to extend DocImp systematically while maintaining consistency, quality, and performance.

## 1. Adding New Commands

### Extension Point

**Location**: `cli/src/commands/<name>Command.ts`

**Integration Point**: `cli/src/index.ts` (register with Commander)

**Python Backend** (if needed): `analyzer/src/main.py` (add command handler)

---

### Template: TypeScript Command

**File**: `cli/src/commands/exampleCommand.ts`

```typescript
import { Command } from 'commander';
import { PythonBridge } from '../python-bridge/PythonBridge.js';
import { StateManager } from '../utils/StateManager.js';
import { TerminalDisplay } from '../display/TerminalDisplay.js';

/**
 * Implements the 'example' command for DocImp.
 *
 * Purpose: [Brief description of what this command does]
 * Usage: docimp example <path> [options]
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
      .description('Description of example command')
      .argument('<path>', 'Path argument description')
      .option('--flag', 'Flag description')
      .action(async (path: string, options: { flag?: boolean }) => {
        try {
          await this.execute(path, options);
        } catch (error) {
          this.display.error(`Error: ${error.message}`);
          process.exit(1);
        }
      });
  }

  /**
   * Core execution logic (testable, no process.exit).
   */
  async execute(
    path: string,
    options: { flag?: boolean }
  ): Promise<void> {
    this.display.info('Executing example command...');

    // Call Python backend (if needed)
    const result = await this.pythonBridge.callPython(
      'example',
      [path],
      { flag: options.flag }
    );

    // Process and display results
    this.display.success('Example command completed!');
  }
}
```

---

### Template: Python Backend Handler

**File**: `analyzer/src/main.py`

```python
def handle_example_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the 'example' command from TypeScript CLI.

    Args:
        args: Command arguments
            - path: str - Path to analyze
            - flag: bool - Optional flag

    Returns:
        JSON-serializable result dictionary
    """
    path = args.get('path')
    flag = args.get('flag', False)

    # Import dependencies (lazy import for performance)
    from src.analyzer import DocumentationAnalyzer

    # Execute logic
    analyzer = DocumentationAnalyzer(...)
    result = analyzer.example_operation(path, flag=flag)

    # Return structured result
    return {
        'status': 'success',
        'data': result.to_dict()
    }

# Register in command dispatch dictionary
COMMANDS = {
    'analyze': handle_analyze_command,
    'audit': handle_audit_command,
    'example': handle_example_command,  # Add here
}
```

---

### Integration Steps

1. **Create Command Class**: `cli/src/commands/exampleCommand.ts`
2. **Add Python Handler** (if needed): `analyzer/src/main.py`
3. **Add Tests**:
   - `cli/src/__tests__/commands/example-command.test.ts`
   - `analyzer/tests/test_example_command.py`
4. **Register in CLI Entry Point**: `cli/src/index.ts`
   ```typescript
   import { ExampleCommand } from './commands/exampleCommand.js';

   const exampleCommand = new ExampleCommand(pythonBridge, stateManager, display);
   exampleCommand.register(program);
   ```
5. **Update Documentation**: Add to README.md command list

---

## 2. Adding New Parsers

### Extension Point

**Location**: `analyzer/src/parsers/<language>_parser.py`

**Base Class**: `analyzer/src/parsers/base_parser.py` (inherit from `BaseParser`)

**Integration Point**: `analyzer/src/analyzer.py` (register in `DocumentationAnalyzer`)

---

### Template: Parser Class

**File**: `analyzer/src/parsers/go_parser.py`

```python
from typing import List
from .base_parser import BaseParser
from ..models import CodeItem

class GoParser(BaseParser):
    """
    Parser for Go files using go/ast (requires Go installed).

    Extracts:
    - Functions (func declarations)
    - Methods (func with receiver)
    - Structs (type declarations)
    """

    def parse_file(self, filepath: str) -> List[CodeItem]:
        """
        Parse a Go file and extract CodeItem objects.

        Args:
            filepath: Absolute path to Go file

        Returns:
            List of CodeItem objects (functions, methods, structs)

        Raises:
            SyntaxError: If Go file has syntax errors
            FileNotFoundError: If filepath does not exist
        """
        items = []

        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse Go AST (requires external tool or library)
        # Example: subprocess call to 'go-parser' tool
        import subprocess
        import json

        result = subprocess.run(
            ['go-parser', filepath],
            capture_output=True,
            text=True,
            check=True
        )

        ast_data = json.loads(result.stdout)

        # Extract functions
        for func in ast_data.get('functions', []):
            items.append(CodeItem(
                name=func['name'],
                type='function',
                filepath=filepath,
                line_number=func['line'],
                end_line=func['end_line'],
                language='go',
                complexity=self._calculate_complexity(func),
                impact_score=0.0,  # Calculated later
                has_docs=func.get('doc') is not None,
                parameters=func.get('params', []),
                return_type=func.get('return_type'),
                docstring=func.get('doc'),
                export_type='exported' if func['name'][0].isupper() else 'internal',
                module_system='go',
                audit_rating=None
            ))

        return items

    def _calculate_complexity(self, node: dict) -> int:
        """Calculate cyclomatic complexity for Go function."""
        # Simplified: count control flow keywords
        keywords = ['if', 'for', 'switch', 'case', 'select']
        return sum(node.get('keywords', {}).get(kw, 0) for kw in keywords) + 1
```

---

### Integration Steps

1. **Create Parser Class**: `analyzer/src/parsers/go_parser.py`
2. **Add Tests**: `analyzer/tests/test_parser_go.py`
3. **Add Test Samples**: `test-samples/edge-cases/go_patterns.go`
4. **Register Parser**: `analyzer/src/analyzer.py`
   ```python
   from src.parsers.python_parser import PythonParser
   from src.parsers.typescript_parser import TypeScriptParser
   from src.parsers.go_parser import GoParser  # Add import

   class DocumentationAnalyzer:
       def __init__(self, parsers=None):
           if parsers is None:
               parsers = [
                   PythonParser(),
                   TypeScriptParser(),
                   GoParser(),  # Add to default parsers
               ]
           self.parsers = parsers
   ```
5. **Update Documentation**: Add to CLAUDE.md supported languages section

---

## 3. Adding New Plugins

### Extension Point

**Location**: `plugins/<name>.js`

**Configuration**: `docimp.config.js` (register plugin)

**Hooks**:
- `beforeAccept(docstring, item, config)`: Validate before acceptance
- `afterWrite(filepath, item)`: Post-write hook

---

### Template: Validation Plugin

**File**: `plugins/validate-examples.js`

```javascript
/**
 * Plugin to ensure public functions have @example tags.
 *
 * Enforces documentation best practice: public APIs should include usage examples.
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
  // Only enforce for public/exported items
  if (item.export_type === 'internal') {
    return { accept: true };  // Skip internal items
  }

  // Check for @example tag
  const hasExample = /@example/i.test(docstring);

  if (!hasExample) {
    return {
      accept: false,
      reason: `Public ${item.type} '${item.name}' missing @example tag. ` +
              'Please add usage example for public APIs.',
    };
  }

  return { accept: true };
}

/**
 * Post-write hook (optional, called after documentation written).
 *
 * @param {string} filepath - File that was modified
 * @param {object} item - CodeItem that was documented
 */
export function afterWrite(filepath, item) {
  // Optional: Log successful documentation
  console.log(`✓ Documented ${item.type} '${item.name}' in ${filepath}`);
}

/**
 * Plugin metadata.
 */
export const metadata = {
  name: 'validate-examples',
  version: '1.0.0',
  description: 'Ensures public functions have @example tags',
};
```

---

### Integration Steps

1. **Create Plugin File**: `plugins/validate-examples.js`
2. **Add Tests**: `plugins/__tests__/validate-examples.test.js`
3. **Register in Config**: `docimp.config.js`
   ```javascript
   export default {
     plugins: [
       // Built-in plugins
       { name: 'validate-types', enabled: true },
       { name: 'jsdoc-style', enabled: true },

       // Custom plugin
       {
         name: 'validate-examples',
         enabled: true,
         path: './plugins/validate-examples.js',
         options: {
           enforceForPublicOnly: true,
         },
       },
     ],
   };
   ```
4. **Test Manually**: Run `docimp improve` and verify plugin executes
5. **Update Documentation**: Add to README.md plugins section

---

## 4. Adding Quality Rules

### Extension Point: Python (Ruff)

**Location**: `analyzer/pyproject.toml` or `ruff.toml`

**Documentation**: https://docs.astral.sh/ruff/rules/

**Template**:
```toml
# analyzer/pyproject.toml
[tool.ruff.lint]
select = [
  "E",      # pycodestyle errors
  "F",      # pyflakes
  "DTZ",    # flake8-datetimez
  "UP",     # pyupgrade
  "PTH",    # flake8-use-pathlib
  "I",      # isort
  "SIM",    # flake8-simplify
  "PERF",   # perflint
  "YTT",    # flake8-2020
  "B",      # flake8-bugbear (NEW)
]

# Add specific rule overrides if needed
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["B011"]  # Disable assert-false in tests
```

**Integration Steps**:
1. Add rule group to `select` array
2. Run `uv run ruff check . --select B` to preview violations
3. Fix violations: `uv run ruff check . --select B --fix`
4. Commit config and fixes together

---

### Extension Point: TypeScript (ESLint)

**Location**: `cli/eslint.config.mjs`

**Documentation**: https://eslint.org/docs/latest/rules/

**Template**:
```javascript
// cli/eslint.config.mjs
export default [
  // ... existing configs ...

  {
    files: ['src/**/*.ts'],
    rules: {
      // NEW: Enforce explicit return types
      '@typescript-eslint/explicit-function-return-type': 'error',

      // NEW: Disallow any type
      '@typescript-eslint/no-explicit-any': 'warn',

      // NEW: Enforce consistent naming
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'interface',
          format: ['PascalCase'],
        },
        {
          selector: 'typeAlias',
          format: ['PascalCase'],
        },
      ],
    },
  },
];
```

**Integration Steps**:
1. Add rules to `eslint.config.mjs`
2. Run `npm run lint` to preview violations
3. Fix violations: `npm run lint -- --fix`
4. Commit config and fixes together

---

## 5. Adding GitHub Actions Workflows

### Extension Point

**Location**: `.github/workflows/<name>.yml`

**Trigger Options**:
- `push` (on every push)
- `pull_request` (on PRs)
- `schedule` (cron-based)
- `workflow_dispatch` (manual trigger)

---

### Template: Security Scanning Workflow

**File**: `.github/workflows/security-scan.yml`

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # Run weekly on Sundays at 00:00 UTC
    - cron: '0 0 * * 0'

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: moderate
```

---

### Integration Steps

1. Create workflow file: `.github/workflows/security-scan.yml`
2. Commit and push to trigger first run
3. Verify in GitHub Actions tab
4. Add status badge to README.md (optional):
   ```markdown
   ![Security Scan](https://github.com/user/repo/actions/workflows/security-scan.yml/badge.svg)
   ```

---

## 6. Adding Documentation

### Extension Point: Pattern Documentation

**Location**: `docs/patterns/<topic>.md`

**Reference in**: `CLAUDE.md` (use `@docs/patterns/<topic>.md` import)

**Template**:
```markdown
# <Topic> Pattern

## Overview

[Brief 2-3 paragraph introduction explaining the pattern and why it's used]

## 1. Implementation

### Example: [Specific Use Case]

\`\`\`typescript
// Code example showing the pattern in action
\`\`\`

**Rationale**: [Why this approach is used]

## 2. Variations

### Variation 1: [Alternative Approach]

[Description and when to use]

\`\`\`python
# Code example for variation
\`\`\`

## Quick Reference

| Aspect          | Recommendation                    |
|-----------------|-----------------------------------|
| When to use     | [Scenarios]                       |
| When to avoid   | [Anti-patterns]                   |
| Performance     | [Considerations]                  |

## Troubleshooting

### Issue: [Common Problem]

**Symptom**: [What the user sees]

**Cause**: [Root cause]

**Solution**:
\`\`\`bash
# Commands to fix
\`\`\`

## Summary

- [Key takeaway 1]
- [Key takeaway 2]
- [Key takeaway 3]
```

---

### Extension Point: User Guide

**Location**: `docs/user-guide/<topic>.md`

**Audience**: End users (not developers)

**Template**:
```markdown
# <Topic> User Guide

## What is [Topic]?

[Plain-language explanation without technical jargon]

## Getting Started

### Prerequisites

- [Requirement 1]
- [Requirement 2]

### Basic Usage

\`\`\`bash
# Simple command example
docimp <command> [options]
\`\`\`

## Common Workflows

### Workflow 1: [Scenario]

1. Step 1 description
   \`\`\`bash
   command
   \`\`\`

2. Step 2 description
   \`\`\`bash
   command
   \`\`\`

## FAQ

**Q: [Common question]?**

A: [Clear answer with example if helpful]

## Troubleshooting

[Common issues and solutions in user-friendly language]
```

---

## 7. Configuration Hooks

### Hook: docimp.config.js

**Extensibility Points**:

1. **Per-Language Style Guides**:
   ```javascript
   export default {
     styleGuides: {
       python: 'google',     // or 'numpy', 'sphinx'
       typescript: 'jsdoc',  // or 'tsdoc'
       javascript: 'jsdoc',
       go: 'godoc',          // NEW LANGUAGE
     },
   };
   ```

2. **Plugin Configuration**:
   ```javascript
   export default {
     plugins: [
       {
         name: 'custom-validation',
         enabled: true,
         path: './plugins/custom-validation.js',
         options: {
           strictMode: true,
           customRule: 'value',
         },
       },
     ],
   };
   ```

3. **API Timeouts**:
   ```javascript
   export default {
     claude: {
       timeout: 30000,       // 30 seconds
       maxRetries: 3,
       retryDelay: 1000,     // 1 second
     },
   };
   ```

---

### Hook: .claude/skills/

**Custom Skills**:

**Location**: `.claude/skills/custom-skill/`

**Structure**:
```
.claude/skills/custom-skill/
├── SKILL.md              # Skill documentation
├── scripts/
│   └── helper.py         # Skill scripts
└── references/
    └── cheatsheet.md     # Reference materials
```

**Integration**: Symlink or copy to `.claude/skills/` in main worktree

---

## 8. Backward Compatibility Considerations

### Versioning Strategy

**DocImp Version Format**: `MAJOR.MINOR.PATCH-α`

**Compatibility Promises**:
- **MAJOR**: Breaking changes allowed (migration guide required)
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

---

### Deprecation Process

**Step 1: Mark Deprecated**:
```typescript
/**
 * @deprecated Use `newFunction()` instead. Will be removed in v2.0.0.
 */
export function oldFunction() {
  console.warn('oldFunction is deprecated, use newFunction instead');
  return newFunction();
}
```

**Step 2: Document in Changelog**:
```markdown
## [1.5.0] - 2025-11-15

### Deprecated
- `oldFunction()` deprecated in favor of `newFunction()` (to be removed in v2.0.0)
```

**Step 3: Remove in Next Major**:
```markdown
## [2.0.0] - 2026-01-15

### Breaking Changes
- **Removed** `oldFunction()` (deprecated since v1.5.0)
```

---

### Configuration Migration

**Automatic Migration** (Workflow State):

See `cli/src/utils/workflow-state-migrations.ts`:

```typescript
// Migration registry
const MIGRATIONS: Record<string, MigrationFunction> = {
  '1.0->1.1': migrate_1_0_to_1_1,
  '1.1->1.2': migrate_1_1_to_1_2,
  // Add new migrations here
};

function migrate_1_1_to_1_2(state: any): any {
  // Transform state from 1.1 to 1.2 schema
  return {
    ...state,
    schema_version: '1.2',
    new_field: 'default_value',
  };
}
```

**Manual Migration Commands**:
```bash
# Check schema version
docimp migrate-workflow-state --check

# Preview migration
docimp migrate-workflow-state --dry-run

# Apply migration
docimp migrate-workflow-state
```

---

## Quick Reference

### Extension Points Summary

| Component        | Location                          | Integration Point            | Template            |
|------------------|-----------------------------------|------------------------------|---------------------|
| Command          | `cli/src/commands/`               | `cli/src/index.ts`           | Section 1           |
| Parser           | `analyzer/src/parsers/`           | `analyzer/src/analyzer.py`   | Section 2           |
| Plugin           | `plugins/`                        | `docimp.config.js`           | Section 3           |
| Quality Rule     | `ruff.toml`, `eslint.config.mjs`  | N/A (automatic)              | Section 4           |
| GitHub Workflow  | `.github/workflows/`              | N/A (automatic)              | Section 5           |
| Pattern Docs     | `docs/patterns/`                  | `CLAUDE.md` (`@import`)      | Section 6           |
| User Guide       | `docs/user-guide/`                | README.md (link)             | Section 6           |

---

### Pre-Integration Checklist

Before adding any infrastructure component:

- [ ] Review existing patterns (don't reinvent)
- [ ] Check CLAUDE.md size (< 40K limit)
- [ ] Follow dependency injection pattern
- [ ] Add comprehensive tests (unit + integration)
- [ ] Update relevant documentation
- [ ] Verify CI passes with new addition
- [ ] Consider backward compatibility (deprecation if needed)
- [ ] Profile performance (if performance-sensitive)
- [ ] Add to Quick Reference tables (if user-facing)

---

### Common Anti-Patterns to Avoid

**Anti-Pattern 1: Global State**
```typescript
// ✗ WRONG
let globalConfig = {};  // Shared mutable state

// ✓ CORRECT
class ConfigManager {
  constructor(private config: Config) {}
  // Instance-based state
}
```

**Anti-Pattern 2: Process.exit in Business Logic**
```typescript
// ✗ WRONG
async function execute() {
  if (error) {
    process.exit(1);  // Not testable
  }
}

// ✓ CORRECT
async function execute(): Promise<void> {
  if (error) {
    throw new Error('...');  // Caller handles exit
  }
}
```

**Anti-Pattern 3: Hardcoded Paths**
```typescript
// ✗ WRONG
const auditFile = '.docimp-audit.json';  // Hardcoded

// ✓ CORRECT
const auditFile = StateManager.getAuditFile();  // Centralized
```

---

## Summary

DocImp provides clear extension points for future development:

- **Commands**: TypeScript CLI + Python backend + tests + registration
- **Parsers**: Language-specific classes inheriting from `BaseParser`
- **Plugins**: JavaScript hooks (`beforeAccept`, `afterWrite`) + config registration
- **Quality Rules**: Ruff (`ruff.toml`) and ESLint (`eslint.config.mjs`) configuration
- **GitHub Workflows**: YAML files in `.github/workflows/`
- **Documentation**: Pattern docs (`docs/patterns/`) + user guides (`docs/user-guide/`)
- **Configuration Hooks**: `docimp.config.js` for plugins, styles, timeouts

**Design Principles**:
- **Dependency Injection**: Constructor-based, explicit dependencies
- **Backward Compatibility**: Versioning, deprecation process, migration support
- **Testing**: Comprehensive coverage for all new components
- **Documentation**: Update CLAUDE.md, README.md, pattern docs

**Final Note**: This is the concluding section of the Infrastructure Documentation series. For ongoing questions, consult `INFRASTRUCTURE-README.md` for navigation across all 22 sections.
