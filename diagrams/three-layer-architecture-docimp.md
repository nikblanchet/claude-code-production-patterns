# Three-Layer Polyglot Architecture

**What it Represents**:
The core architecture of DocImp, showing how the system separates concerns across three programming languages: TypeScript for the CLI interface, Python for analysis engine, and JavaScript for configuration and validation plugins.

**Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     TypeScript CLI Layer                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Commander.js • Config Loader (JS) • Plugin Manager       │  │
│  │  Python Bridge • Terminal Display • Interactive Session   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↕                                  │
│                   Subprocess Communication                       │
│                              ↕                                  │
│                    Python Analysis Engine                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  AST Parsers • Impact Scorer • Coverage Calculator        │  │
│  │  Claude Client • Docstring Writer                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↕                                  │
│                      File System & APIs                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  .py .ts .js .cjs .mjs files • Claude API                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↕                                  │
│                  JavaScript Config & Plugins                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  docimp.config.js • validate-types.js • jsdoc-style.js    │  │
│  │  TypeScript Compiler (for JSDoc validation)               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Concepts**:
- **TypeScript CLI Layer**: User-facing commands, configuration loading, plugin management, subprocess orchestration, terminal UI
- **Python Analysis Engine**: Heavy lifting for code parsing (AST), impact scoring, coverage calculation, Claude API interaction
- **JavaScript Config & Plugins**: User-controlled configuration files and validation plugins with full Node.js access
- **Subprocess Communication**: JSON-based communication between TypeScript and Python layers
- **File System & APIs**: Source code files and external API integrations

**Data Flow**:
1. User runs `docimp analyze ./code`
2. TypeScript CLI loads `docimp.config.js`
3. Python Bridge spawns Python subprocess
4. Python Analyzer discovers files, routes to language-specific parsers
5. Parsers extract `CodeItem` objects with impact scores
6. Results returned as JSON to CLI for display
