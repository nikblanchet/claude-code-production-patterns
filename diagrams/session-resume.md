# Session Resume Component Stack

**What it Represents**:
The architecture for pausing and resuming interactive workflows. Uses file checksums to detect changes during pauses and automatically re-process modified files on resume.

**Pattern Overview**: This pattern enables interactive CLI workflows to pause and resume gracefully, with automatic detection of changed files. Applicable to code review tools, interactive wizards, long-running processes, and any command that benefits from pause/resume functionality.

**Example Implementation**: This document uses DocImp's audit workflow as a concrete example, but the pattern is generic and adaptable to any interactive CLI tool.

---

## Generic Pattern

**Architecture Layers**:

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Commands                               │
│  tool review --resume, tool interview --resume, etc.         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│               SessionStateManager                             │
│  - save_session_state() - Atomic writes (temp + rename)      │
│  - load_session_state() - JSON parse + validation            │
│  - list_sessions()      - Sorted by started_at               │
│  - get_latest_session() - Most recent session helper         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│                  FileTracker                                  │
│  - create_snapshot()    - File checksums + modification time │
│  - detect_changes()     - Compare checksums and timestamps   │
│  - get_changed_items()  - Filter item list                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           Session State Files (.tool-name/sessions/)          │
│  {command}-session-{uuid}.json - In-progress sessions        │
└──────────────────────────────────────────────────────────────┘
```

**Key Concepts**:
- **CLI Commands**: Interactive workflows that support pause/resume (e.g., `tool review --resume`, `tool interview --resume`)
- **SessionStateManager**: Manages session persistence and retrieval with atomic file operations
- **FileTracker**: Detects file changes between pause and resume using checksums (SHA-256 or similar)
- **Session State Files**: UUID-based JSON files storing in-progress work (e.g., `.tool-name/sessions/{command}-session-{uuid}.json`)

**Generic Session Lifecycle**:
1. User starts interactive command (e.g., `tool review ./src`)
2. User processes first N items, then quits
3. SessionStateManager saves progress to session file
4. FileTracker creates snapshot of file checksums
5. User modifies source files
6. User runs command with `--resume` flag
7. FileTracker detects changed files
8. System re-processes only changed files
9. User continues from next item with fresh data for changed files

**Common Resume Flags**:
- `--resume`: Continue most recent session
- `--new`: Start fresh session (ignore existing)
- `--clear-session`: Delete existing session and start fresh
- `--list-sessions`: Show all available sessions

---

## DocImp Implementation Example

**Diagram**:

```
┌──────────────────────────────────────────────────────────────┐
│                    CLI Commands (TypeScript)                  │
│  audit --resume, improve --resume, list-sessions, etc.       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│               SessionStateManager (TS + Python)               │
│  - save_session_state() - Atomic writes (temp + rename)      │
│  - load_session_state() - JSON parse + Zod validation        │
│  - list_sessions()      - Sorted by started_at               │
│  - get_latest_session() - Most recent session helper         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│                  FileTracker (TS + Python)                    │
│  - create_snapshot()    - SHA256 checksum + mtime           │
│  - detect_changes()     - Compare checksums and timestamps   │
│  - get_changed_items()  - Filter CodeItem list               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│           Session State Files (.docimp/session-reports/)      │
│  audit-session-{uuid}.json     - In-progress audit sessions  │
│  improve-session-{uuid}.json   - In-progress improve sessions│
└──────────────────────────────────────────────────────────────┘
```

**DocImp-Specific Details**:
- **CLI Commands**: `audit --resume`, `improve --resume`, `list-sessions` (TypeScript)
- **SessionStateManager**: Dual TypeScript + Python implementation with Zod validation
- **FileTracker**: SHA-256 checksums with mtime comparison (TypeScript + Python)
- **Session State Files**: `.docimp/session-reports/audit-session-{uuid}.json` and `improve-session-{uuid}.json`

**DocImp Session Lifecycle**:
1. User starts `docimp audit ./src`
2. User rates first 5 items, then quits [Q]
3. SessionStateManager saves progress to `audit-session-{uuid}.json`
4. FileTracker creates snapshot of file checksums
5. User modifies 2 source files
6. User runs `docimp audit ./src --resume`
7. FileTracker detects 2 changed files
8. System re-analyzes those 2 files only
9. User continues from item 6 with fresh data for changed files

**DocImp Resume Flags**:
- `--resume`: Continue most recent session
- `--new`: Start fresh session (ignore existing)
- `--clear-session`: Delete existing session and start fresh
