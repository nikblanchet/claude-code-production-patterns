# Workflow State Management Component Stack

**What it Represents**:
The layered architecture for tracking command execution state, enabling dependency validation (audit requires analyze), staleness detection (warn when analyze re-run invalidates audit), and incremental analysis (only re-analyze changed files).

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

**Key Concepts**:
- **CLI Commands**: Entry points that trigger workflow state updates
- **WorkflowValidator**: Business logic for validating command dependencies and detecting stale state
- **WorkflowStateManager**: Abstraction layer for atomic file operations with schema validation
- **WorkflowState File**: Persistent JSON file tracking all command executions

**State Lifecycle**:
1. Command executes (e.g., `docimp analyze`)
2. Validator checks prerequisites (none for analyze, analyze required for audit)
3. Command runs, generates results
4. StateManager atomically updates `workflow-state.json` with timestamp and file checksums
5. Next command (e.g., `docimp audit`) validates prerequisites against saved state

**Staleness Detection**:
- File checksums (SHA-256) detect when source files change
- Timestamp comparison detects when upstream commands re-run
- `docimp status` displays staleness warnings and actionable suggestions
