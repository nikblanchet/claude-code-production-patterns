# CLAUDE_CONTEXT.md

Private context and preferences for Claude Code when working on DocImp. This file is gitignored and not part of the public repository.

## Project Purpose

**DocImp is a portfolio project for job hunting**, specifically targeting the **"Technical Documentation & Content Engineer, Claude Code"** position at Anthropic.

### Why This Matters
- Every technical decision should demonstrate skills mentioned in the job listing
- The project must show I can build sophisticated systems even in languages where I have minimal experience
- Time constraint: Must be completed before the job listing closes
- **Scope control is critical** - demonstrate necessary skills, but ship it

### Job Requirements Being Demonstrated

From the Anthropic job listing:

1. **"Strong full-stack development skills with proficiency in Python, TypeScript, and JavaScript"**
   - This is why all three languages are in the project design
   - Python: my strong suit (excellent experience)
   - TypeScript/JavaScript: minimal experience, demonstrating I can learn and build with Claude Code

2. **"Strong understanding of codebase architecture, dependency management, and project organization principles"**
   - Polyglot architecture with clear separation of concerns
   - Constructor-based dependency injection throughout
   - Clean module boundaries between Python engine, TypeScript CLI, JavaScript plugins

3. **"Ability to create comprehensive workflow documentation"**
   - README-driven development approach
   - CLAUDE.md as detailed technical documentation
   - Plan to run DocImp on itself to improve its own documentation

4. **"Deep understanding of modern software development practices, including version control, CI/CD, testing, and code review processes"**
   - Git workflow with feature branches and clean main history
   - Test coverage in both Python and TypeScript
   - CI/CD with GitHub Actions
   - Pull requests with squash merges

5. **"Contributions to open-source projects related to AI-powered development tools"**
   - DocImp itself is an AI-powered development tool
   - Built with Claude Code, for improving code documentation

6. **Sophisticated architectures with "advanced design patterns" and dependency injection**
   - Constructor injection in Python and TypeScript
   - Plugin system with hooks
   - Strategy pattern for parsers
   - Bridge pattern for Python-TypeScript communication

7. **"Ability to read and understand code at the level our senior engineers write it"**
   - Will be demonstrated through code quality and architectural decisions
   - Commentary on design choices in documentation
   - Understanding of why patterns are used, not just copying them

## My Technical Background

- **Python**: Excellent - strong foundation in best practices and design patterns
- **TypeScript**: Minimal experience - learning through this project
- **JavaScript**: Minimal experience - learning through this project

**Strategy**: Use Claude Code to handle TypeScript/JavaScript implementation while I:
- Critique design choices using universal software engineering principles
- Ask for education on TypeScript/JavaScript-specific patterns and syntax
- Demonstrate ability to work effectively in languages I'm still learning

### How to Handle My Questions

When I ask about TypeScript/JavaScript decisions or code:
1. Explain the reasoning clearly
2. Connect it to broader software engineering principles where applicable
3. If I request it, draft a prompt for the Claude macOS app for deeper exploration without consuming Claude Code context

## README-Driven Development Philosophy

This project is being built using **README-driven development**:
1. Define what the tool should do in the README first
2. Build to match the README specification
3. Use the tool on itself to improve its own documentation
4. Document the process and results

This demonstrates:
- Ability to create comprehensive documentation (job requirement)
- Practical application of an AI documentation tool
- "Eating our own dog food"

## Scope Control

**Time is a constraint.** The project must:
- Demonstrate all required technical skills
- Look polished and professional
- Actually work end-to-end
- NOT have every possible feature
- NOT be over-engineered

**When making decisions:**
- Ask: "Does this demonstrate a required skill?"
- Ask: "Is this necessary for the MVP?"
- Prefer: Reliable working solutions over error-prone ones
- Prefer: Professional code over kludgy solutions
- Remember: Shipping is a feature

## Known Simplifications

These are intentional trade-offs for scope control:

1. **Plugin security**: No sandboxing (documented limitation)
2. **Impact scoring**: Basic complexity-based in MVP (pattern detection is future work)
3. **Style guides**: NumPy and JSDoc only (others are future work)
4. **Improve workflow**: Sequential only, no save/resume (future enhancement)

These limitations are documented in CLAUDE.md to show awareness of the trade-offs.

## Writing Context for DocImp

**Background**: User has 17 years of technical writing experience. Writing quality matters.

**DocImp-Specific Tone**:
- Professional tone throughout (this is a portfolio project)
- Technical accuracy is critical
- Clear, concise language demonstrates communication skills to potential employers
- Proper grammar and punctuation
- Avoid hedging language ("perhaps," "maybe," "might") unless genuine uncertainty exists
- Be direct: "This implements X" not "This should implement X"

## Error Handling and Debugging

When something doesn't work:
1. **Check the actual error message** - Don't assume what went wrong
2. **Verify assumptions** - Test imports, check file paths, confirm environment
3. **Incremental fixes** - Make one change at a time and test
4. **Explain your reasoning** - Help the user understand what you're investigating

When tests fail:
1. Read the test output carefully
2. Identify the specific assertion or error
3. Explain what the test expects vs. what it's getting
4. Propose a targeted fix

## Context Management

**When context gets long:**
- Summarize key decisions and their rationale
- Reference file locations for implementation details
- Ask if we should start fresh for next logical unit of work

**Before suggesting major refactors:**
- Explain why the current approach is problematic
- Outline the benefits of the refactor
- Estimate scope of changes
- Get approval before proceeding

## Questions and Clarifications

**Always ask when:**
- Requirements are ambiguous
- Multiple valid approaches exist with different tradeoffs
- A decision will significantly impact architecture
- You're unsure about user preferences

**Don't ask when:**
- It's a standard pattern for the language/framework
- The existing codebase shows clear precedent
- It's covered explicitly in this document
