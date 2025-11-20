## Project Overview

**Goal**: Build an impact-driven documentation coverage tool that demonstrates:
- **Polyglot full-stack architecture** (Python + TypeScript + JavaScript as first-class citizens)
- **Clean dependency injection patterns** in multiple languages
- **AI integration with validation gates** (plugins catch Claude's mistakes)
- **JavaScript runtime expertise** (JSDoc type-checking, ESM/CJS, write patterns)
- **Terminal-first developer UX**
- **Built entirely with Claude Code** (16 instances, documented methodology)

**Timeline**: 3-4 days (~37-42 hours total)
- Code development: ~27-31 hours (16 Claude Code instances)
- Manual work: ~10-11 hours (dogfooding, pedagogy, application materials)

---

## Architecture Summary

```
docimp/
├── cli/                              # TypeScript CLI layer
│   ├── src/
│   │   ├── index.ts                 # Entry point (Commander.js)
│   │   ├── commands/                # Command implementations
│   │   │   ├── analyze.ts
│   │   │   ├── audit.ts
│   │   │   ├── plan.ts
│   │   │   └── improve.ts
│   │   ├── config/
│   │   │   ├── IConfig.ts
│   │   │   └── ConfigLoader.ts      # Loads JS config files
│   │   ├── plugins/
│   │   │   ├── IPlugin.ts
│   │   │   └── PluginManager.ts     # Loads & runs JS plugins
│   │   ├── display/
│   │   │   ├── IDisplay.ts
│   │   │   └── TerminalDisplay.ts
│   │   ├── python-bridge/
│   │   │   ├── IPythonBridge.ts
│   │   │   └── PythonBridge.ts
│   │   └── types/
│   │       └── analysis.ts
│   ├── parsers/
│   │   └── ts-js-parser-helper.ts   # Parses .ts, .js, .cjs, .mjs
│   ├── tsconfig.json                # allowJs + checkJs enabled
│   └── package.json
│
├── analyzer/                         # Python analysis engine
│   └── src/
│       ├── main.py                  # CLI interface
│       ├── models/
│       │   ├── code_item.py
│       │   └── analysis_result.py
│       ├── parsers/
│       │   ├── base_parser.py
│       │   ├── python_parser.py
│       │   └── typescript_parser.py # Calls Node.js helper
│       ├── scoring/
│       │   ├── impact_scorer.py
│       │   └── pattern_detector.py
│       ├── analysis/
│       │   ├── analyzer.py
│       │   └── coverage_calculator.py
│       ├── claude/
│       │   ├── claude_client.py
│       │   └── prompt_builder.py
│       └── writer/
│           └── docstring_writer.py  # Handles Python + JS write patterns
│
├── plugins/                          # JavaScript plugins
│   ├── validate-types.js            # Real JSDoc type-checking
│   ├── jsdoc-style.js               # Style enforcement
│   ├── lint-docstrings.js           # Linter integration
│   └── README.md                    # Plugin API + Security
│
├── examples/                         # Test files
│   ├── test_simple.py
│   ├── test_simple.ts
│   ├── test_javascript_patterns.js  # ESM + JSDoc types
│   └── test_commonjs.cjs            # CommonJS patterns
│
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Python dev/test dependencies
├── docimp.config.js                 # User configuration (JavaScript)
├── .github/workflows/ci.yml         # Node matrix + ESM/CJS tests
└── README.md
```

---

## Complete Execution Plan

---

## 📅 DAY 1: Foundation & Core Analysis

### **STEP 1: Project Setup & API Access**
**Type**: Manual setup  
**Time**: 30 minutes

**Tasks**:
- [X] Create GitHub repository `docimp`
- [X] Set up local development environment
- [X] Set up Python 3.13 environment
- [X] Verify Node.js 22
- [X] Get Claude API key from console.anthropic.com
- [X] Set `ANTHROPIC_API_KEY` environment variable
- [X] Create initial `.gitignore`

**Validation**:
```bash
python --version  # 3.13
node --version    # 22
echo $ANTHROPIC_API_KEY  # Should show key
```

---

### **STEP 2: README-Driven Development** 🤖
**Type**: **CLAUDE CODE INSTANCE 0**  
**Time**: 2 hours  
**Goal**: Define product vision, architecture, and user experience before code

**Contract**:

**Dependencies**: None

**Deliverable**: Complete README.md with architecture and proto-docstrings

**Done Criteria**:
- [X] README explains what DocImp does and why
- [X] Installation instructions (stub is fine)
- [X] Quick start guide showing expected UX
- [X] Architecture diagram showing TypeScript ↔ Python ↔ JavaScript
- [X] Each major class/function has one-sentence proto-docstring
- [X] Impact scoring algorithm explained
- [X] Plugin architecture previewed
- [X] "Built with Claude Code" section (placeholder)
- [X] Markdown renders cleanly on GitHub

**Files to Create**:
- `README.md`
- `.gitignore`
- `LICENSE`
- `requirements.txt` (stub with anthropic)

**Files to Modify**: None

**Rollback Plan**: Delete and start with simpler scope

**Validation**:
```bash
# Manual review checklist:
# - Can someone understand the project without seeing code?
# - Are proto-docstrings specific enough to guide implementation?
# - Does it look professional and well-organized?

git add README.md .gitignore LICENSE
git commit -m "docs: add README with architecture and proto-docstrings"
```

---

### **STEP 3: Python Data Models** 🤖
**Type**: **CLAUDE CODE INSTANCE 1**  
**Time**: 45-60 minutes  
**Goal**: Create type-safe data structures for code analysis results

**Contract**:

**Dependencies**: Step 2 (README defines data model)

**Deliverable**: Python package with dataclasses representing parsed code

**Done Criteria**:
- [X] `CodeItem` dataclass with fields:
  - `name`, `type`, `filepath`, `line_number`, `language`
  - `complexity`, `impact_score`, `has_docs`
  - `parameters`, `return_type`, `docstring`
  - `export_type` (for JS: 'named', 'default', 'commonjs')
  - `module_system` (for JS: 'esm', 'commonjs')
  - `audit_rating` (optional, for audit command results)
- [X] `AnalysisResult` dataclass with coverage metrics
- [X] Full type hints on all fields
- [X] JSON serialization support
- [X] `requirements.txt` in project root includes: `anthropic`, `typing-extensions`

**Note**: Fields like `is_public`, `has_decorators`, `is_async` omitted from MVP - can be added later for advanced pattern detection

**Files to Create**:
- `requirements.txt` (project root)
- `analyzer/src/__init__.py`
- `analyzer/src/models/__init__.py`
- `analyzer/src/models/code_item.py`
- `analyzer/src/models/analysis_result.py`

**Files to Modify**: None

**Rollback Plan**: Delete `analyzer/` directory and `requirements.txt`

**Validation**:
```bash
pip install -r requirements.txt

python -c "
from analyzer.src.models.code_item import CodeItem
import json

item = CodeItem(
    name='test_func',
    type='function',
    filepath='test.py',
    line_number=10,
    language='python',
    complexity=5,
    impact_score=75,
    has_docs=False,
    export_type='named',
    module_system='esm'
)

print(f'✓ Created CodeItem: {item.name}')
print(f'✓ Language: {item.language}')
print(f'✓ Export type: {item.export_type}')
"

git add requirements.txt analyzer/
git commit -m "feat: add Python data models with type-safe dataclasses"
```

---

### **STEP 4: Python Parser Foundation** 🤖
**Type**: **CLAUDE CODE INSTANCE 2**  
**Time**: 60-75 minutes  
**Goal**: Create abstract parser interface and Python AST parser

**Contract**:

**Dependencies**: Step 3 (needs CodeItem model)

**Deliverable**: Working Python parser extracting functions/classes with metadata

**Done Criteria**:
- [X] `BaseParser` abstract class defines interface
- [X] `PythonParser` implements `BaseParser` using AST
- [X] Extracts functions, classes, methods
- [X] Calculates cyclomatic complexity
- [X] Detects docstrings (presence and content)
- [X] Returns `List[CodeItem]` with `language='python'`
- [X] Handles malformed Python gracefully

**Note**: Decorator/async/DI pattern detection omitted from MVP - focus on complexity only

**Files to Create**:
- `analyzer/src/parsers/__init__.py`
- `analyzer/src/parsers/base_parser.py`
- `analyzer/src/parsers/python_parser.py`
- `examples/test_simple.py`

**Files to Modify**: None

**Rollback Plan**: Delete `parsers/`, revert examples

**Validation**:
```bash
cat > examples/test_simple.py << 'EOF'
"""Example module for testing."""

async def async_function(param1: str, param2: int = 5) -> bool:
    """An async function with parameters."""
    if param1:
        return True
    return False

class ExampleClass:
    def __init__(self, service: SomeService):
        """Constructor with dependency injection."""
        self.service = service
    
    @property
    def value(self):
        return self._value
EOF

python -c "
from analyzer.src.parsers.python_parser import PythonParser

parser = PythonParser()
items = parser.parse_file('examples/test_simple.py')

assert len(items) >= 2
assert all(item.language == 'python' for item in items)
assert all(item.complexity >= 1 for item in items)
assert any(item.has_docs for item in items)

print(f'✓ Parsed {len(items)} Python items')
for item in items:
    docs_status = '📝' if item.has_docs else '❌'
    print(f'  {docs_status} {item.type} {item.name}: complexity={item.complexity}')
"

git add analyzer/src/parsers/ examples/test_simple.py
git commit -m "feat: add Python AST parser with complexity detection"
```

---

### **STEP 5: TypeScript/JavaScript Parser** 🤖
**Type**: **CLAUDE CODE INSTANCE 3**  
**Time**: 90-120 minutes  
**Goal**: Parse TypeScript AND JavaScript with JSDoc type-checking

**Contract**:

**Dependencies**: Step 4 (needs BaseParser interface)

**Deliverable**: Parser handling .ts, .js, .cjs, .mjs with full JSDoc validation

**Done Criteria**:

**TypeScript Configuration**:
- [X] `cli/tsconfig.json` has:
  - `"allowJs": true` - Parse JavaScript files
  - `"checkJs": true` - Type-check JSDoc in .js files
  - `"resolveJsonModule": true`
  - `"module": "NodeNext"` - Deterministic ESM/CJS interop
  - `"moduleResolution": "NodeNext"`
  - `"strict": true`

**Parser Capabilities**:
- [X] Parses `.ts`, `.js`, `.cjs`, `.mjs` files
- [X] Validates JSDoc against actual signatures (param names must match)
- [X] Detects JSDoc type annotations (`@typedef`, `@template`, `@type`, `@param`, `@returns`)
- [X] Extracts functions, classes, methods, interfaces
- [X] Calculates cyclomatic complexity
- [X] Detects ESM exports (`export`, `export default`)
- [X] Detects CommonJS (`module.exports`, `exports.foo`)
- [X] Python wrapper spawns Node process and parses JSON
- [X] Handles malformed TS/JS gracefully
- [X] Returns `CodeItem` with `language='typescript'` or `'javascript'`

**Note**: Decorator/generic/async pattern detection omitted from MVP - focus on complexity and module system detection

**Files to Create**:
- `cli/package.json` (TypeScript, ts-node, dependencies)
- `cli/tsconfig.json` (with allowJs + checkJs)
- `cli/src/parsers/ts-js-parser-helper.ts`
- `analyzer/src/parsers/typescript_parser.py`
- `examples/test_simple.ts`
- `examples/test_javascript_patterns.js` (ESM with JSDoc types)
- `examples/test_commonjs.cjs` (CommonJS patterns)

**Files to Modify**: None

**Rollback Plan**: Delete TypeScript parser files, revert to Python-only

**Validation**:
```bash
# Create comprehensive JavaScript examples
cat > examples/test_javascript_patterns.js << 'EOF'
/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} name
 */

/**
 * Fetch user by ID
 * @param {string} userId - User identifier
 * @returns {Promise<User>} User object
 */
export async function fetchUser(userId) {
    return { id: userId, name: 'John' };
}

/**
 * Get first item from array
 * @template T
 * @param {T[]} items
 * @returns {T|undefined}
 */
export const first = (items) => items[0];

export class UserRepository {
    /**
     * @param {Database} db - Database connection
     */
    constructor(db) {
        this.db = db;
    }
    
    /**
     * Save user
     * @param {User} user
     * @returns {Promise<void>}
     */
    async save(user) {
        await this.db.insert(user);
    }
}
EOF

cat > examples/test_commonjs.cjs << 'EOF'
/**
 * Calculate sum
 * @param {number[]} numbers
 * @returns {number}
 */
function sum(numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

module.exports = {
    sum,
    /**
     * Calculate average
     * @param {number[]} numbers
     * @returns {number}
     */
    average(numbers) {
        return sum(numbers) / numbers.length;
    }
};
EOF

cat > examples/test_simple.ts << 'EOF'
interface Repository<T> {
    findById(id: string): Promise<T | null>;
}

export class UserService {
    constructor(
        private repo: Repository<User>,
        private logger: Logger
    ) {}
    
    async getUser(id: string): Promise<User> {
        return await this.repo.findById(id);
    }
}
EOF

# Test JSDoc validation catches errors
cat > examples/test_jsdoc_error.js << 'EOF'
/**
 * Add two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 */
function add(x, y) {  // Wrong param names!
    return x + y;
}
EOF

# Install and build
cd cli
npm install
npm run build

# Test parsing
cd ..
python -c "
from analyzer.src.parsers.typescript_parser import TypeScriptParser

parser = TypeScriptParser()

# Test ESM JavaScript
esm_items = parser.parse_file('examples/test_javascript_patterns.js')
print(f'✓ ESM JavaScript: {len(esm_items)} items')
assert all(item.export_type in ['named', 'default'] for item in esm_items)
assert all(item.module_system == 'esm' for item in esm_items)

# Test CommonJS
cjs_items = parser.parse_file('examples/test_commonjs.cjs')
print(f'✓ CommonJS: {len(cjs_items)} items')
assert all(item.module_system == 'commonjs' for item in cjs_items)
assert all(item.export_type == 'commonjs' for item in cjs_items)

# Test TypeScript
ts_items = parser.parse_file('examples/test_simple.ts')
print(f'✓ TypeScript: {len(ts_items)} items')
assert all(item.language == 'typescript' for item in ts_items)
assert all(item.complexity >= 1 for item in ts_items)

print('✓ All JavaScript/TypeScript parsing complete')
"

git add cli/ analyzer/src/parsers/typescript_parser.py examples/test_*.{ts,js,cjs}
git commit -m "feat: add TS/JS parser with JSDoc type-checking (allowJs + checkJs)"
```

---

### **STEP 6: Impact Scoring Engine** 🤖
**Type**: **CLAUDE CODE INSTANCE 4**
**Time**: 30-45 minutes
**Goal**: Calculate impact scores (0-100) based on cyclomatic complexity

**Contract**:

**Dependencies**: Step 3 (needs CodeItem model)

**Deliverable**: Simple scorer for MVP that prioritizes by complexity

**Done Criteria**:
- [X] `ImpactScorer` calculates 0-100 score based on cyclomatic complexity
- [X] Formula: `impact_score = min(100, cyclomatic_complexity * 5)`
- [X] Can optionally incorporate audit ratings if available
- [X] Configurable weights for complexity vs quality (defaults: 60/40)
- [X] Scores normalize to 0-100 range

**Formula**:
- **Without audit**: `score = min(100, complexity * 5)`
- **With audit**: `score = (0.6 * complexity_score) + (0.4 * quality_penalty)`
  - quality_penalty: No docs=100, Terrible=80, OK=40, Good=20, Excellent=0

**Files to Create**:
- `analyzer/src/scoring/__init__.py`
- `analyzer/src/scoring/impact_scorer.py`

**Files to Modify**: None

**Rollback Plan**: Delete `scoring/` directory, use dummy scores

**Note**: Pattern detection (DI, async, decorators, public/private) deferred to future enhancement

**Validation**:
```bash
python -c "
from analyzer.src.scoring.impact_scorer import ImpactScorer
from analyzer.src.models.code_item import CodeItem

scorer = ImpactScorer()

simple = CodeItem(
    name='add', type='function', filepath='test.py', line_number=1,
    language='python', complexity=1, impact_score=0, has_docs=False
)

complex = CodeItem(
    name='process_payment', type='function', filepath='service.py', line_number=10,
    language='python', complexity=15, impact_score=0, has_docs=False
)

simple_score = scorer.calculate_score(simple)
complex_score = scorer.calculate_score(complex)

assert 0 <= simple_score <= 100
assert 0 <= complex_score <= 100
assert complex_score > simple_score
assert simple_score == 5  # 1 * 5
assert complex_score == 75  # 15 * 5

print(f'✓ Simple (complexity 1): {simple_score}')
print(f'✓ Complex (complexity 15): {complex_score}')
"

git add analyzer/src/scoring/
git commit -m "feat: add simple complexity-based impact scoring for MVP"
```

---

## 📅 DAY 1 (Continued) / DAY 2: Core Orchestration

### **STEP 7: Core Analyzer with Dependency Injection** 🤖
**Type**: **CLAUDE CODE INSTANCE 5**  
**Time**: 60 minutes  
**Goal**: Orchestrate parsing and scoring with clean DI architecture

**Contract**:

**Dependencies**: Steps 4, 5, 6 (needs parsers and scorer)

**Deliverable**: `DocumentationAnalyzer` that produces `AnalysisResult`

**Done Criteria**:
- [X] `DocumentationAnalyzer` constructor accepts injected dependencies
- [X] Discovers Python/TypeScript/JavaScript files recursively
- [X] Skips: `node_modules/`, `venv/`, `__pycache__/`, `dist/`, `build/`
- [X] Parses files with appropriate parser based on extension
- [X] Handles `.py`, `.ts`, `.js`, `.cjs`, `.mjs`
- [X] Calculates impact scores for all items
- [X] Computes coverage metrics by language
- [X] Returns `AnalysisResult` with all data
- [X] Handles file read errors gracefully
- [X] Progress indicator for large codebases

**Files to Create**:
- `analyzer/src/analysis/__init__.py`
- `analyzer/src/analysis/analyzer.py`
- `analyzer/src/analysis/coverage_calculator.py`

**Files to Modify**: None

**Rollback Plan**: Delete `analysis/` directory

**Validation**:
```bash
python -c "
from analyzer.src.analysis.analyzer import DocumentationAnalyzer
from analyzer.src.parsers.python_parser import PythonParser
from analyzer.src.parsers.typescript_parser import TypeScriptParser
from analyzer.src.scoring.impact_scorer import ImpactScorer

analyzer = DocumentationAnalyzer(
    parsers={
        'python': PythonParser(),
        'typescript': TypeScriptParser(),
        'javascript': TypeScriptParser()
    },
    scorer=ImpactScorer()
)

result = analyzer.analyze('./examples')

print(f'✓ Analyzed {len(result.items)} items')
print(f'✓ Coverage: {result.coverage_percent:.1f}%')
print(f'✓ Python items: {len([i for i in result.items if i.language == \"python\"])}')
print(f'✓ TypeScript items: {len([i for i in result.items if i.language == \"typescript\"])}')
print(f'✓ JavaScript items: {len([i for i in result.items if i.language == \"javascript\"])}')

assert len(result.items) >= 5
"

git add analyzer/src/analysis/
git commit -m "feat: add core analyzer with dependency injection"
```

---

### **STEP 8: Python CLI Entry Point** 🤖
**Type**: **CLAUDE CODE INSTANCE 6**  
**Time**: 45 minutes  
**Goal**: Create command-line interface for Python analyzer

**Contract**:

**Dependencies**: Step 7 (needs DocumentationAnalyzer)

**Deliverable**: `python -m analyzer` CLI with analyze command

**Done Criteria**:
- [X] CLI uses `argparse` with subcommands
- [X] `analyze` command accepts directory path
- [X] Outputs JSON to stdout
- [X] `--format` flag: `json` or `summary`
- [X] `--verbose` flag for detailed output
- [X] Proper exit codes (0 = success, 1 = error)
- [X] Error messages to stderr, data to stdout

**Files to Create**:
- `analyzer/src/main.py`
- `analyzer/src/__main__.py`

**Files to Modify**: None

**Rollback Plan**: Delete CLI files

**Validation**:
```bash
python -m analyzer analyze ./examples --format json | jq '.coverage_percent'
python -m analyzer analyze ./examples --format summary

git add analyzer/src/main.py analyzer/src/__main__.py
git commit -m "feat: add Python CLI with analyze command"
```

---

### **STEP 9: TypeScript CLI Foundation** 🤖
**Type**: **CLAUDE CODE INSTANCE 7**  
**Time**: 45 minutes  
**Goal**: Set up TypeScript CLI with Commander.js

**Contract**:

**Dependencies**: None (independent)

**Deliverable**: Working TypeScript CLI skeleton

**Done Criteria**:
- [X] `package.json` with TypeScript, Commander.js, build scripts
- [X] `tsconfig.json` already has `allowJs + checkJs` from Step 5
- [X] Commander.js configured with subcommands
- [X] Each command has help text
- [X] Version flag works
- [X] Build process works (`npm run build`)

**Files to Create**:
- `cli/src/index.ts`
- `cli/src/commands/analyze.ts` (stub)
- `cli/src/commands/audit.ts` (stub)
- `cli/src/commands/plan.ts` (stub)
- `cli/src/commands/improve.ts` (stub)

**Files to Modify**:
- `cli/package.json` (add Commander.js)

**Rollback Plan**: Delete TypeScript CLI files

**Validation**:
```bash
cd cli
npm install
npm run build
node dist/index.js --help
node dist/index.js analyze --help

git add cli/src/index.ts cli/src/commands/
git commit -m "feat: add TypeScript CLI foundation with Commander.js"
```

---

### **STEP 10: Configuration System (JavaScript)** 🤖
**Type**: **CLAUDE CODE INSTANCE 7.5**  
**Time**: 90-120 minutes  
**Goal**: Load and validate user preferences from JavaScript config

**Contract**:

**Dependencies**: Step 9 (needs TypeScript CLI structure)

**Deliverable**: Config system loading `docimp.config.js` (JavaScript)

**Done Criteria**:
- [X] `IConfig` interface defines structure
- [X] `ConfigLoader` (TypeScript) loads JavaScript configs
- [X] Supports CommonJS (`module.exports`) and ESM (`export default`)
- [X] Validates config against schema
- [X] Provides sensible defaults
- [X] Example `docimp.config.js` with:
  - Style guide preference (including JSDoc styles)
  - JSDoc-specific options (`jsdocStyle` object)
  - Custom impact weights
  - Custom pattern detectors (example: Repository pattern)
  - Plugin paths
  - File exclusions
- [X] `--config` flag to specify config file
- [X] Clear error messages for invalid config

**JSDoc Style Options**:
```javascript
jsdocStyle: {
  preferredTags: { return: 'returns', arg: 'param' },
  requireDescriptions: true,
  requireExamples: 'public',  // 'all', 'public', 'none'
  enforceTypes: true
}
```

**Files to Create**:
- `cli/src/config/IConfig.ts`
- `cli/src/config/ConfigLoader.ts`
- `docimp.config.js` (example user config with JSDoc options)
- `cli/src/config/README.md`

**Files to Modify**:
- `cli/src/commands/analyze.ts` (accept --config flag)

**Rollback Plan**: Revert config system, use hardcoded defaults

**Validation**:
```bash
cat > docimp.config.js << 'EOF'
module.exports = {
  styleGuide: 'jsdoc',
  tone: 'concise',

  jsdocStyle: {
    preferredTags: { return: 'returns' },
    requireDescriptions: true,
    requireExamples: 'public',
    enforceTypes: true
  },

  impactWeights: {
    complexity: 0.6,  // Weight for cyclomatic complexity
    quality: 0.4      // Weight for audit quality rating
  },

  exclude: ['**/test_*.py', '**/node_modules/**', '**/__pycache__/**']
};
EOF

cd cli
npm run build
node dist/index.js analyze ../examples --config ../docimp.config.js

git add cli/src/config/ docimp.config.js
git commit -m "feat: add JavaScript configuration with JSDoc style options"
```

---

### **STEP 11: TypeScript-Python Bridge with DI** 🤖
**Type**: **CLAUDE CODE INSTANCE 8**  
**Time**: 75-90 minutes  
**Goal**: Enable TypeScript to call Python analyzer via subprocess

**Contract**:

**Dependencies**: Steps 8, 9 (needs both CLIs)

**Deliverable**: `PythonBridge` that spawns Python and parses results

**Done Criteria**:
- [X] `IPythonBridge` interface defines contract
- [X] `PythonBridge` implements interface
- [X] Spawns Python process with correct arguments
- [X] Passes config to Python side
- [X] Parses JSON response from stdout
- [X] Handles Python exceptions gracefully
- [X] TypeScript types for Python data structures
- [X] `analyze` command fully implemented with DI
- [X] End-to-end: TypeScript → Python → JSON → TypeScript

**Files to Create**:
- `cli/src/python-bridge/IPythonBridge.ts`
- `cli/src/python-bridge/PythonBridge.ts`
- `cli/src/types/analysis.ts`

**Files to Modify**:
- `cli/src/commands/analyze.ts` (full implementation)

**Rollback Plan**: Revert analyze.ts, delete python-bridge/

**Validation**:
```bash
cd cli
npm run build
node dist/index.js analyze ../examples
node dist/index.js analyze ../examples --config ../docimp.config.js

git add cli/src/python-bridge/ cli/src/types/ cli/src/commands/analyze.ts
git commit -m "feat: add TypeScript-Python bridge with dependency injection"
```

---

## 📅 DAY 2 (Continued): User Experience & AI Integration

### **STEP 12: Terminal Display System with DI** 🤖
**Type**: **CLAUDE CODE INSTANCE 9**  
**Time**: 60 minutes  
**Goal**: Beautiful, formatted terminal output

**Contract**:

**Dependencies**: Step 11 (needs working analyze command)

**Deliverable**: Display service for pretty-printing results

**Done Criteria**:
- [X] `IDisplay` interface defines contract
- [X] `TerminalDisplay` implements interface using chalk, cli-table3
- [X] Shows coverage percentage prominently
- [X] **Shows language breakdown** (Python/TypeScript/JavaScript/Skipped separately)
- [X] Lists undocumented items by priority
- [X] Progress bars and spinners
- [X] Commands inject `IDisplay` (no direct console.log)

**Output Example**:
```
┌─────────────────────────────────────────────┐
│  Documentation Coverage Analysis            │
├─────────────────────────────────────────────┤
│  Overall:        67.5% (27/40 documented)   │
│                                             │
│  By Language:                               │
│  • Python:       70.0% (14/20)              │
│  • TypeScript:   75.0% (9/12)               │
│  • JavaScript:   50.0% (4/8) ⚠️             │
└─────────────────────────────────────────────┘
```

**Files to Create**:
- `cli/src/display/IDisplay.ts`
- `cli/src/display/TerminalDisplay.ts`

**Files to Modify**:
- `cli/src/commands/analyze.ts` (inject display)
- `cli/package.json` (add chalk, cli-table3, ora)

**Rollback Plan**: Revert to plain console.log

**Validation**:
```bash
cd cli
npm install
npm run build
node dist/index.js analyze ../examples
# Should show pretty output with language breakdown

git add cli/src/display/ cli/package.json cli/src/commands/analyze.ts
git commit -m "feat: add terminal display with language-specific metrics"
```

---

### **STEP 13: Claude API Client** 🤖
**Type**: **CLAUDE CODE INSTANCE 10**  
**Time**: 75-90 minutes  
**Goal**: Integrate Claude for documentation suggestions

**Contract**:

**Dependencies**: Step 8 (needs Python CLI structure)

**Deliverable**: `ClaudeClient` that generates docstring suggestions

**Done Criteria**:
- [X] `ClaudeClient` with injected API key
- [X] `PromptBuilder` creates context-rich prompts
- [X] Includes code, surrounding context, style guide, tone
- [X] Handles JSDoc vs Python docstring styles
- [X] `suggest` command in Python CLI
- [X] Rate limiting and retry logic
- [X] Environment variable validation

**Files to Create**:
- `analyzer/src/claude/__init__.py`
- `analyzer/src/claude/claude_client.py`
- `analyzer/src/claude/prompt_builder.py`

**Files to Modify**:
- `analyzer/src/main.py` (add `suggest` command)

**Rollback Plan**: Delete claude/ directory

**Validation**:
```bash
export ANTHROPIC_API_KEY=sk-ant-...

python -m analyzer suggest examples/test_javascript_patterns.js:fetchUser \
  --style-guide jsdoc --tone concise

# Should output Claude-generated JSDoc

git add analyzer/src/claude/ analyzer/src/main.py
git commit -m "feat: add Claude API client with JSDoc support"
```

---

### **STEP 14: Plugin System (JavaScript)** 🤖
**Type**: **CLAUDE CODE INSTANCE 11**  
**Time**: 2.5-3 hours  
**Goal**: Extensible validation hooks with REAL JSDoc type-checking

**Contract**:

**Dependencies**: Steps 10, 13 (needs config and Claude)

**Deliverable**: Plugin architecture with TypeScript-powered validation

**Done Criteria**:

**TypeScript Plugin Infrastructure**:
- [X] `IPlugin` interface defines hooks
- [X] `PluginManager` (TypeScript) loads and executes plugins
- [X] Dynamic import of JavaScript files
- [X] Error isolation per plugin
- [X] `PluginResult` type with `accept`, `reason`, `autoFix`

**JavaScript Plugins** (2 MVP plugins):

1. **`plugins/validate-types.js`** - REAL JSDoc validation (MVP):
   - [X] Uses TypeScript compiler programmatically
   - [X] Creates in-memory TS program with `checkJs: true`
   - [X] Validates parameter names match
   - [X] Validates types are correct
   - [X] Generates auto-fix for common errors
   - [X] Returns specific error messages

2. **`plugins/jsdoc-style.js`** - Style enforcement (MVP):
   - [X] Checks preferred tag aliases (@returns vs @return)
   - [X] Validates descriptions end with punctuation
   - [X] Requires @example for public APIs with complexity > 5
   - [X] Respects `jsdocStyle` config options

**Note**: Linter integration (`lint-docstrings.js` with ruff/eslint) deferred to demonstrate framework extensibility without committing to specific linters in MVP

**Security**:
- [X] `plugins/README.md` with security section
- [X] Documents trust model
- [X] Notes no sandboxing (honest about trade-offs)
- [ ] `--unsafe-plugins` flag for external plugins (deferred - see issue #18 for related plugin timeout mechanism)
- [X] Default-safe: only load from config or ./plugins/

**Config Integration**:
- [X] Plugins loaded from config
- [X] Config validation
- [X] Clear error messages

**Files to Create**:
- `cli/src/plugins/IPlugin.ts`
- `cli/src/plugins/PluginManager.ts`
- `plugins/validate-types.js` (with real TS type-checking)
- `plugins/jsdoc-style.js`
- `plugins/README.md` (with Security section, includes example of linter integration for future)

**Files to Modify**:
- `docimp.config.js` (add plugins array)

**Rollback Plan**: Delete plugins/ and plugin manager

**Validation**:
```bash
# Test type validation plugin
cat > test-plugin-validation.js << 'EOF'
/**
 * Add numbers
 * @param {number} wrongName - First number
 * @param {number} b - Second number
 */
function add(correctName, b) {
    return correctName + b;
}
EOF

cd cli
npm run build
node -e "
const { PluginManager } = require('./dist/plugins/PluginManager');
const pm = new PluginManager();

(async () => {
  await pm.loadPlugins(['../plugins/validate-types.js']);
  
  const docstring = \`/**
 * @param {number} wrongName
 */\`;
  
  const item = {
    name: 'add',
    filepath: 'test.js',
    language: 'javascript',
    code: 'function add(correctName) {}'
  };
  
  const results = await pm.runHook('beforeAccept', docstring, item, {});
  console.log('Plugin result:', results);
  // Should fail due to parameter name mismatch
})();
"

git add cli/src/plugins/ plugins/ docimp.config.js
git commit -m "feat: add JavaScript plugin system with real JSDoc type-checking"
```

---

### **STEP 15: Audit Command** 🤖
**Type**: **CLAUDE CODE INSTANCE 12**  
**Time**: 60-75 minutes  
**Goal**: Quality audit workflow for existing documentation

**Contract**:

**Dependencies**: Step 11 (needs bridge and display)

**Deliverable**: Interactive audit that rates existing docs

**Done Criteria**:
- [X] `audit` command in Python finds items WITH docs
- [X] TypeScript CLI shows each docstring interactively
- [X] User rates: [1] Terrible, [2] OK, [3] Good, [4] Excellent, [S]kip, [Q]uit
- [X] Coverage calculator uses weighted scoring (deferred - scores already support audit ratings via ImpactScorer from Step 6)
- [X] Results persist to `.docimp-audit.json`
- [ ] **DEFERRED**: Can resume interrupted audit (future enhancement - shows all items for MVP)
- [X] Progress indicator (simple "Auditing X/Y" counter)

**Files to Create**:
- `cli/src/commands/audit.ts`
- `analyzer/src/audit/__init__.py`
- `analyzer/src/audit/quality_rater.py`

**Files to Modify**:
- `analyzer/src/main.py` (add `audit` command)
- `analyzer/src/analysis/coverage_calculator.py` (weighted coverage)

**Rollback Plan**: Delete audit files

**Validation**:
```bash
cd cli
npm run build
node dist/index.js audit ../examples
# Interactive rating workflow

git add cli/src/commands/audit.ts analyzer/src/audit/ analyzer/src/main.py
git commit -m "feat: add audit command for documentation quality"
```

---

## 📅 DAY 2 (Evening) / DAY 3: Interactive Workflow & Polish

### **STEP 16: Plan Command** 🤖
**Type**: **CLAUDE CODE INSTANCE 13**
**Time**: 45-60 minutes
**Goal**: Generate prioritized improvement plan for consumption by improve command

**Contract**:

**Dependencies**: Steps 11, 15 (needs analyze and audit)

**Deliverable**: Plan command that outputs machine-readable JSON

**Done Criteria**:
- [X] Combines missing docs + poor quality docs
- [X] Sorts by impact score (descending)
- [X] Outputs JSON to stdout (for piping to improve command)
- [X] Saves plan to `.docimp-plan.json` for improve to load
- [X] Plan includes all item metadata needed for improve workflow

**Files to Create**:
- [X] `cli/src/commands/plan.ts`
- [X] `analyzer/src/planning/__init__.py`
- [X] `analyzer/src/planning/plan_generator.py`

**Files to Modify**:
- [X] `analyzer/src/main.py` (add `plan` command)

**Rollback Plan**: Delete planning files

**Validation**:
```bash
cd cli
npm run build
node dist/index.js plan ../examples
# Should output JSON and save to .docimp-plan.json

# Verify plan file exists
test -f .docimp-plan.json && echo "✓ Plan file created"

git add cli/src/commands/plan.ts analyzer/src/planning/
git commit -m "feat: add plan command with JSON output"
```

---

### **STEP 17: Interactive Improve Workflow** 🤖
**Type**: **CLAUDE CODE INSTANCE 14**  
**Time**: 2.5-3 hours  
**Goal**: Full Phase 4 interactive session with plugin validation

**Contract**:

**Dependencies**: Steps 13, 14, 16 (needs Claude, plugins, plan)

**Deliverable**: Complete interactive improvement workflow

**Done Criteria**:

**Workflow**:
- [X] Collects global preferences at start (style guide, tone)
- [X] Loads plan from previous `docimp plan` command
- [X] Iterates through items sequentially in priority order
- [X] For each item:
  - [X] Shows code context
  - [X] Requests Claude suggestion
  - [X] Runs plugin validation
  - [X] Shows suggestion with validation errors (if any)
  - [X] User options: [A] Accept, [E] Edit (opens in editor), [R] Regenerate (prompts for feedback), [S] Skip, [Q] Quit
  - [X] If accepted/edited: writes to file
- [X] Continues to next item until complete or user quits

**Note**: Save/resume, progress tracking, manual and item selection are deferred to future enhancements.

**Writer (`analyzer/src/writer/docstring_writer.py`)**:
- [X] Python `apply` command writes docs to files
- [X] Handles Python docstrings (triple quotes)
- [X] **Handles JavaScript patterns**:
  - [X] `function foo() {}`
  - [X] `export function foo() {}`
  - [X] `export default function foo() {}`
  - [X] `module.exports = { foo() {} }`
  - [X] `const foo = () => {}` (JSDoc above const)
  - [X] Class methods (static, getters, setters)
  - [X] Object literal methods
  - [X] `.js`, `.cjs`, `.mjs` files
- [X] Preserves indentation
- [X] Idempotent (no duplicate comments)
- [X] Handles `/* */` and `/** */` styles
- [X] Creates backup before modification

**Files to Create**:
- [X] `cli/src/commands/improve.ts`
- [X] `cli/src/session/InteractiveSession.ts`
- [X] `cli/src/session/ProgressTracker.ts`
- [X] `cli/src/editor/EditorLauncher.ts`
- [X] `analyzer/src/writer/__init__.py`
- [X] `analyzer/src/writer/docstring_writer.py`

**Files to Modify**:
- [X] `analyzer/src/main.py` (add `apply` command)

**Rollback Plan**: Delete improve files, revert main.py

**Validation**:
```bash
cd cli
npm run build

# Test writer on JavaScript patterns
python -c "
from analyzer.src.writer.docstring_writer import DocstringWriter

writer = DocstringWriter()

# Test ESM function
js_code = 'export function add(a, b) { return a + b; }'
jsdoc = '/** Add numbers\\n * @param {number} a\\n * @param {number} b\\n */'
result = writer.insert_docstring(js_code, jsdoc, 'function', 'add')
assert '/**' in result
assert 'export function' in result
print('✓ ESM function write works')

# Test arrow function
arrow_code = 'const multiply = (x, y) => x * y;'
arrow_doc = '/** Multiply\\n * @param {number} x\\n * @param {number} y\\n */'
result = writer.insert_docstring(arrow_code, arrow_doc, 'function', 'multiply')
assert result.index('/**') < result.index('const')
print('✓ Arrow function write works')
"

# Full interactive test
export ANTHROPIC_API_KEY=sk-ant-...
node dist/index.js improve ../examples

# Should:
# 1. Collect preferences
# 2. Show items
# 3. Request Claude suggestions
# 4. Run plugin validations
# 5. Write back to files

git add cli/src/commands/improve.ts cli/src/session/ cli/src/editor/
git add analyzer/src/writer/ analyzer/src/main.py
git commit -m "feat: add interactive improve with JS write patterns"
```

---

### **STEP 18: Testing & CI/CD** 🤖
**Type**: **CLAUDE CODE INSTANCE 15**
**Time**: 2-2.5 hours
**Goal**: Comprehensive tests and CI matrix

**Contract**:

**Dependencies**: All previous instances

**Deliverable**: Test suite and automated CI pipeline

**Done Criteria**:

**Python Tests** (pytest):
- [X] Parser smoke tests (Python, TS, JS)
- [X] Scorer monotonicity (complex > simple)
- [X] Coverage calculator tests
- [X] **JavaScript integration test** (analyze JS project)
- [X] **Writer tests for JS patterns** (7+ test cases)
- [X] Mock Claude client for deterministic tests
- [X] ~10-12 focused tests total

**TypeScript Tests** (Jest):
- [X] Config loader tests
- [X] Plugin manager tests (issue #19)
- [X] **JSDoc validation test** (checkJs enforcement)
- [X] **ESM/CJS detection tests**
- [X] **JSDoc type extraction tests**
- [X] Python bridge mock tests
- [X] Display formatting tests
- [X] **Improve workflow component tests** (InteractiveSession, ProgressTracker, EditorLauncher - issue #40)
- [X] ~10-12 focused tests total
- [X] Relocate test-plugins.js to proper test directory (issue #17)

**Optional Enhancements (deferred from Step 14)**:
- [ ] Add timeout mechanism for plugin hooks (issue #18) - low priority, may defer beyond Step 18

**GitHub Actions CI**:
- [X] Python: 3.13 (can expand matrix later if needed)
- [X] Node: 22 (can expand matrix later if needed)
- [X] **Module system matrix: CommonJS vs ESM**
- [X] Linting: ruff, eslint, **eslint-plugin-jsdoc**
- [X] Type checking: mypy, tsc --noEmit
- [X] Build verification
- [X] Badge in README

**Files to Create**:
- `analyzer/tests/__init__.py`
- `analyzer/tests/test_parsers.py`
- `analyzer/tests/test_scoring.py`
- `analyzer/tests/test_coverage.py`
- `analyzer/tests/test_javascript_integration.py`
- `analyzer/tests/test_writer.py` (JS write patterns)
- `cli/src/__tests__/config.test.ts`
- `cli/src/__tests__/plugins.test.ts`
- `cli/src/__tests__/javascript-handling.test.ts`
- `cli/src/__tests__/bridge.test.ts`
- `.github/workflows/ci.yml`
- `analyzer/pytest.ini`
- `cli/jest.config.js`
- `cli/.eslintrc.js` (with jsdoc plugin)

**Files to Modify**:
- `README.md` (add CI badge)
- `cli/package.json` (add jest, eslint-plugin-jsdoc)

**Rollback Plan**: Delete tests and CI

**Validation**:
```bash
# Python tests
cd analyzer
pytest -v

# TypeScript tests
cd ../cli
npm test

# Linting
cd ../analyzer
ruff check .

cd ../cli
npm run lint
npm run lint:jsdoc

# Push and verify CI
git add analyzer/tests/ cli/src/__tests__/ .github/
git commit -m "test: comprehensive test suite with JS validation"
git push
# Check GitHub Actions - all checks should pass

git add README.md
git commit -m "docs: add CI badge"
```

---

### **STEP 19: Final Documentation Polish** 🤖
**Type**: **CLAUDE CODE INSTANCE 16**  
**Time**: 90-120 minutes  
**Goal**: Production-ready documentation

**Contract**:

**Dependencies**: All previous instances

**Deliverable**: Complete, polished documentation

**Done Criteria**:

**README.md**:
- [ ] Real usage examples (not stubs)
- [ ] Installation instructions tested
- [ ] All commands documented
- [ ] Architecture diagram updated
- [ ] Impact scoring formula
- [ ] **JavaScript/JSDoc handling highlighted**
- [ ] Plugin system documentation
- [ ] Configuration guide
- [ ] Troubleshooting section
- [ ] "Built with Claude Code" section (placeholder for now)
- [ ] Known limitations
- [ ] Future improvements

**Inline Documentation**:
- [ ] All Python functions have NumPy-style docstrings
- [ ] **All TypeScript functions have JSDoc**
- [ ] **All JavaScript plugins fully documented**
- [ ] Examples for complex functions
- [ ] Type annotations complete

**Plugin Documentation**:
- [ ] `plugins/README.md` comprehensive
- [ ] Hook lifecycle explained
- [ ] **Security section** (trust model, no sandboxing)
- [ ] Examples for each hook
- [ ] Common patterns

**Config Documentation**:
- [ ] All options explained in `docimp.config.js`
- [ ] **JSDoc style options documented**
- [ ] Default values listed
- [ ] Examples provided

**Files to Modify**:
- `README.md` (comprehensive update)
- All Python files (add/improve docstrings)
- All TypeScript files (add/improve JSDoc)
- `plugins/README.md` (complete guide)
- `docimp.config.js` (extensive comments)

**Rollback Plan**: Revert documentation changes

**Validation**:
```bash
# Test all examples in README
# Verify links work
# Check GitHub rendering

git add -A
git commit -m "docs: comprehensive documentation with JS/JSDoc emphasis"
```

---

## 📅 DAY 3: Dogfooding & Pedagogy Artifacts

### **STEP 20: Dogfooding - Use DocImp on Itself**
**Type**: Manual  
**Time**: 2.5-3 hours

**Tasks**:
1. **Analysis**: Run analyze, document coverage
2. **Audit**: Rate existing docs, note quality issues
3. **Plan**: Generate improvement plan, save it
4. **Improve**: Work through 10-15 high-impact items
   - Test all workflow paths
   - **Verify plugin catches JSDoc errors**
   - Document plugin effectiveness
5. **Re-analysis**: Measure improvement
6. **Document**: Create `DOGFOODING.md` with:
   - Metrics (before/after)
   - Process notes
   - **JavaScript/JSDoc issues found**
   - Plugin catches (real bugs Claude made)
   - Lessons learned
   - Screenshots

**Deliverables**:
- `DOGFOODING.md`
- Screenshots in `docs/images/`
- Updated docstrings in codebase
- Git commit showing improvements

---

### **STEP 21: OSS Case Study**
**Type**: Manual  
**Time**: 2-3 hours

**Tasks**:
1. Choose small Python or TypeScript/JavaScript project
2. Clone and analyze
3. Improve 5-10 high-impact items
4. Create `CASE_STUDY.md` with:
   - Project intro
   - Initial/final metrics
   - Process narrative
   - Before/after code examples
   - Time spent
   - Lessons learned

**Deliverables**:
- `CASE_STUDY.md`
- Before/after diffs

---

### **STEP 22: Terminal Session Recordings**
**Type**: Manual  
**Time**: 1-2 hours

**Recordings** (use asciinema or screen recording):
1. **Quick Start** (2-3 min): Install → analyze → improve → coverage improvement
2. **Plugin Validation** (2-3 min): Claude generates → plugin catches error → auto-fix → accept
3. **JavaScript/JSDoc** (2 min): Analyzing JS project, writing JSDoc with validation

**Deliverables**:
- 3 video files or asciinema recordings
- Links in README

---

### **STEP 23: Context-Flow Diagram**
**Type**: Manual  
**Time**: 1 hour

**Create diagram showing**:
- How DocImp chunks context for Claude
- Prompt construction
- Plugin validation flow
- Write-back process
- **Emphasize JavaScript handling**

**Deliverable**:
- `docs/context-flow.md` with diagram

---

### **STEP 24: Claude Code Playbook**
**Type**: Manual  
**Time**: 2-3 hours

**Create `CLAUDE_CODE_PLAYBOOK.md`**:
1. **Introduction**: What is Claude Code, why use it
2. **Five Patterns**: Session atomicity, contracts, progressive context, escape hatches, test before merge
3. **Five Anti-Patterns**: What not to do
4. **Prompt Patterns**: With examples
5. **Real Examples from DocImp**: Successes and struggles
6. **Metrics**: Time, success rate, observations

**Deliverable**:
- `CLAUDE_CODE_PLAYBOOK.md`

---

### **STEP 25: DEVELOPMENT.md - "Built with Claude Code"**
**Type**: Manual  
**Time**: 1-2 hours

**Create `DEVELOPMENT.md`**:
1. Project context and goals
2. Development process (instance-by-instance)
3. Instance breakdown with times
4. Lessons learned
5. **JavaScript-specific challenges** (ESM/CJS, JSDoc validation, write patterns)
6. Challenges and solutions
7. Metrics
8. Recommendations for others

**Deliverable**:
- `DEVELOPMENT.md`

---

## 📅 DAY 3-4: Application Materials

### **STEP 26: Polish README for Application**
**Type**: Manual  
**Time**: 2 hours

**Add "Why This Qualifies Me" Section**:
Map job requirements to project artifacts with exact JD language and direct code links.

Example structure:
```markdown
## Why This Project Demonstrates My Qualifications

**"Software engineering-level code comprehension"**
→ [Multi-file architecture with DI], [Parser implementations]

**"Strong full-stack: Python, TypeScript, JavaScript"**
→ Python: [AST parsing, scoring, Claude client]
→ TypeScript: [CLI, bridge, display]
→ JavaScript: [Config system, plugins with REAL type-checking]

**"JavaScript the language, not just TS that parses .js"**
→ Proof: [checkJs enforcement], [ESM/CJS handling], [JSDoc write patterns]
→ Tests: [7+ JS write tests], [CI matrix for module systems]

**"Context management strategies"**
→ [Context-flow diagram], [instance atomicity], [playbook patterns]

**"Create multimedia technical content"**
→ [Terminal recordings], [Diagrams], [Playbook], [Plugin API docs]
```

**Deliverable**:
- Updated `README.md` optimized for application

---

### **STEP 27: Create Demo GIF/Video**
**Type**: Manual  
**Time**: 1 hour

**30-second demo showing**:
- Analyze (33% coverage)
- Plan (prioritized)
- Improve (interactive with plugin validation)
- Re-analyze (91% coverage)

**Deliverable**:
- `demo.gif` embedded in README

---

### **STEP 28: Final Repository Polish**
**Type**: Manual  
**Time**: 1-2 hours

**Checklist**:
- [ ] Repository structure complete
- [ ] All documentation present
- [ ] GitHub settings configured
- [ ] CI badge shows passing
- [ ] All links work
- [ ] Images load
- [ ] Clean commit history
- [ ] Release v1.0.0 created

**Deliverable**:
- Production-ready GitHub repository

---

### **STEP 29: Application Cover Letter Addendum**
**Type**: Manual  
**Time**: 1 hour

**Create `APPLICATION_NOTES.md` (private)**:
1. Elevator pitch
2. Key talking points
3. Project stats
4. Story arc for interviews
5. Anticipated Q&A

**Deliverable**:
- Talking points for application

---

### **STEP 30: Write Final Cover Letter**
**Type**: Manual  
**Time**: 2 hours

**Integrate DocImp into cover letter**:
- Opening hook
- Project integration (2 paragraphs)
- Experience bridge
- Unique value proposition
- **Emphasize JavaScript competence**
- Closing

**Deliverable**:
- Application-ready cover letter

---

### **STEP 31: LinkedIn/Portfolio Integration**
**Type**: Manual  
**Time**: 1 hour

**Optional but recommended**:
- LinkedIn post
- Portfolio site update
- Pin repository on GitHub

**Deliverable**:
- Increased visibility

---

## Timeline Summary

### Total Time: ~37-42 hours

**Development (Claude Code)**:
- Instances 0-16: ~27-31 hours

**Manual Work**:
- Setup & dogfooding: ~6 hours
- Case study: ~2-3 hours
- Recordings: ~2 hours
- Diagrams: ~1 hour
- Playbook: ~2-3 hours
- DEVELOPMENT.md: ~1-2 hours
- Application materials: ~4-5 hours

### Day-by-Day

**Day 1** (~10-12 hours): Steps 1-6 (Foundation)
**Day 2** (~13-15 hours): Steps 7-17 (Core + Interactive)
**Day 3** (~9-11 hours): Steps 18-25 (Testing + Pedagogy)
**Day 4** (~5-7 hours): Steps 26-31 (Application prep)

---

## JavaScript Excellence Checklist

Before submitting, verify JavaScript competence is unmistakable:

**Parser**:
- [ ] `allowJs: true` and `checkJs: true` in tsconfig
- [ ] Validates JSDoc parameter names
- [ ] Handles .js, .cjs, .mjs files
- [ ] Detects ESM vs CommonJS
- [ ] Extracts @typedef, @template, @type

**Writer**:
- [ ] 7+ JavaScript write pattern tests pass
- [ ] Handles ESM exports
- [ ] Handles CommonJS
- [ ] Handles arrow functions correctly
- [ ] Idempotent (no duplicates)

**Plugins**:
- [ ] validate-types.js uses TS compiler for REAL checking
- [ ] jsdoc-style.js enforces rules
- [ ] Security documented honestly

**Tests**:
- [ ] JavaScript-specific unit tests
- [ ] Integration test with JS project
- [ ] CI matrix tests both module systems
- [ ] eslint-plugin-jsdoc runs

**Documentation**:
- [ ] README highlights JS handling
- [ ] JSDoc examples throughout
- [ ] Plugin README has security section
- [ ] Config shows jsdocStyle options

---

## Key Talking Points

**For Application/Interview**:

1. **"I understand JavaScript runtime semantics"**
   - checkJs enforcement
   - ESM/CJS handling
   - CI tests both module systems

2. **"I type-check JSDoc, not just parse it"**
   - Plugin uses TS compiler
   - Tests catch parameter mismatches
   - Real validation, not cosmetic

3. **"I handle JavaScript write patterns correctly"**
   - 7+ test cases
   - Export styles, arrow functions, classes
   - Idempotent, preserves formatting

4. **"I thought about plugin security"**
   - Security section in docs
   - Honest about no sandboxing
   - --unsafe-plugins flag

5. **"I validate JavaScript documentation quality"**
   - JSDoc validation with real type-checking
   - Style enforcement
   - Tests show plugins catch real issues

---

## Risk Mitigation

**If time gets tight, protect**:
1. Parser with checkJs validation ✅
2. JSDoc validation plugin ✅
3. Writer with JS patterns ✅
4. Tests proving JS handling ✅
5. CI matrix ✅

**Can defer**:
- Multiple JSDoc styles
- Advanced auto-fix
- CJS/ESM daemon optimization
- Additional JS examples

---

## Success Criteria

**Technical**:
- ✅ All 3 languages (Python/TS/JS) as first-class citizens
- ✅ DI in Python and TypeScript
- ✅ JavaScript runtime competence unmistakable
- ✅ 20+ source files, clean architecture
- ✅ ~80%+ test coverage
- ✅ CI passing with Node + module system matrix

**Claude Code**:
- ✅ 16 documented instances
- ✅ Playbook with patterns/anti-patterns
- ✅ Real lessons learned

**Pedagogy**:
- ✅ Comprehensive README
- ✅ 3 terminal recordings
- ✅ Context-flow diagram
- ✅ Playbook
- ✅ 2 case studies

**Application**:
- ✅ "Why This Qualifies Me" section
- ✅ Cover letter integration
- ✅ Professional repository
- ✅ Demo materials ready