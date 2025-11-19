# Session Resume Component Stack

**What it Represents**:
The architecture for pausing and resuming interactive workflows (audit and improve commands). Uses file checksums to detect changes during pauses and automatically re-analyze modified files on resume.

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

**Key Concepts**:
- **CLI Commands**: Interactive workflows that support pause/resume
- **SessionStateManager**: Manages session persistence and retrieval
- **FileTracker**: Detects file changes between pause and resume using checksums
- **Session State Files**: UUID-based JSON files storing in-progress work

**Session Lifecycle**:
1. User starts `docimp audit ./src`
2. User rates first 5 items, then quits [Q]
3. SessionStateManager saves progress to `audit-session-{uuid}.json`
4. FileTracker creates snapshot of file checksums
5. User modifies 2 source files
6. User runs `docimp audit ./src --resume`
7. FileTracker detects 2 changed files
8. System re-analyzes those 2 files only
9. User continues from item 6 with fresh data for changed files

**Resume Flags**:
- `--resume`: Continue most recent session
- `--new`: Start fresh session (ignore existing)
- `--clear-session`: Delete existing session and start fresh
