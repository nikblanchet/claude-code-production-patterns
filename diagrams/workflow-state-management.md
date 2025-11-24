# Workflow State Management Component Stack

**What it Represents**:
The layered architecture for tracking command execution state, enabling dependency validation, staleness detection, and incremental analysis.

**Pattern Overview**: This pattern enables CLI tools to track command execution dependencies and detect file changes between runs. Applicable to build systems, test runners, code analysis tools, and any workflow with dependent steps.

**Example Implementation**: This document uses DocImp (a code documentation tool) as a concrete example, but the pattern is generic and adaptable to any CLI tool with multi-step workflows.

---

## Generic Pattern

**Architecture Layers**:

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Commands                               │
│  tool build, tool test, tool deploy with validation          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│               WorkflowValidator                               │
│  - Validate prerequisites       - Check dependencies         │
│  - Detect stale state           - Provide error messages     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           WorkflowStateManager                                │
│  - loadState()          - Atomic reads with validation       │
│  - saveState()          - Atomic writes (temp + rename)      │
│  - updateCommandState() - Update single command state        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           WorkflowState File (.tool-name/workflow-state.json) │
│  - schema_version                                            │
│  - command execution history with timestamps                 │
│  - file checksums for change detection                       │
└──────────────────────────────────────────────────────────────┘
```

**Key Concepts**:
- **CLI Commands**: Entry points that trigger workflow state updates (e.g., `tool build`, `tool test`, `tool deploy`)
- **WorkflowValidator**: Business logic for validating command dependencies and detecting stale state
- **WorkflowStateManager**: Abstraction layer for atomic file operations with schema validation
- **WorkflowState File**: Persistent JSON file tracking all command executions (e.g., `.tool-name/workflow-state.json`)

**Generic State Lifecycle**:
1. Command executes (e.g., `tool build`)
2. Validator checks prerequisites (dependencies on prior commands)
3. Command runs, generates results
4. StateManager atomically updates `workflow-state.json` with timestamp and file checksums
5. Next command (e.g., `tool test`) validates prerequisites against saved state

**Staleness Detection**:
- File checksums (SHA-256 or similar) detect when source files change
- Timestamp comparison detects when upstream commands re-run
- Status command displays staleness warnings and actionable suggestions

---

## DocImp Implementation Example

**Diagram**:

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Commands (TypeScript)                  │
│  analyze, audit, plan, improve with validation               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│               WorkflowValidator (TypeScript)                  │
│  - validateAuditPrerequisites()   - Prerequisites checking   │
│  - validatePlanPrerequisites()    - Stale detection          │
│  - checkStaleAnalysis()           - Helpful error messages   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           WorkflowStateManager (TS + Python)                  │
│  - loadWorkflowState()    - Atomic reads with Zod validation │
│  - saveWorkflowState()    - Atomic writes (temp + rename)    │
│  - updateCommandState()   - Update single command state      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           WorkflowState File (.docimp/workflow-state.json)    │
│  - schema_version: "1.0"                                     │
│  - last_analyze, last_audit, last_plan, last_improve         │
│  - Each: { timestamp, item_count, file_checksums }           │
└──────────────────────────────────────────────────────────────┘
```

**DocImp-Specific Details**:
- **CLI Commands**: `analyze`, `audit`, `plan`, `improve` with validation
- **WorkflowValidator**: TypeScript implementation with methods like `validateAuditPrerequisites()`, `validatePlanPrerequisites()`, `checkStaleAnalysis()`
- **WorkflowStateManager**: Dual TypeScript + Python implementation with Zod schema validation
- **WorkflowState File**: `.docimp/workflow-state.json` with `last_analyze`, `last_audit`, `last_plan`, `last_improve` fields

**DocImp State Lifecycle**:
1. Command executes (e.g., `docimp analyze`)
2. Validator checks prerequisites (none for analyze, analyze required for audit)
3. Command runs, generates results
4. StateManager atomically updates `workflow-state.json` with timestamp and file checksums
5. Next command (e.g., `docimp audit`) validates prerequisites against saved state

**DocImp Staleness Detection**:
- File checksums (SHA-256) detect when source files change
- Timestamp comparison detects when upstream commands re-run
- `docimp status` displays staleness warnings and actionable suggestions
