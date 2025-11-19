# Official Skills

Official skills are provided by Anthropic and offer guidance on using Claude Code features effectively.

## Skills in This Collection

### skill-creator
**Purpose**: Guide for creating effective skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

**When to use**: When users want to create a new skill (or update an existing skill).

**Key concepts**:
- Skills are modular packages providing specialized workflows and domain expertise
- Anatomy: `skill.md` (required) + optional bundled resources (scripts/, references/, assets/)
- Progressive disclosure: metadata → SKILL.md → bundled resources as needed
- Six-step creation process: Understanding → Planning → Initializing → Editing → Packaging → Iterating

**Skill creation process**:
1. **Understanding** - Gather concrete examples of how the skill will be used
2. **Planning** - Identify reusable resources (scripts, references, assets)
3. **Initializing** - Run `init_skill.py` to generate template structure
4. **Editing** - Implement bundled resources and update SKILL.md
5. **Packaging** - Run `package_skill.py` to validate and create distributable zip
6. **Iterating** - Test, gather feedback, improve

**Bundled resources**:
- `scripts/` - Executable code for deterministic reliability or repeated rewrites
- `references/` - Documentation to load into context as needed
- `assets/` - Files used in output (templates, boilerplate, etc.)

**Writing style**: Use imperative/infinitive form (verb-first instructions), not second person. Objective, instructional language.

---

## Usage

The skill-creator skill helps you build custom skills that capture organizational knowledge, workflows, and best practices.

### When to Create a Skill

Create a skill when:
- You find yourself repeatedly explaining the same workflow
- Domain-specific knowledge needs to be consistently available
- You have scripts or assets that are frequently rewritten
- You want to capture company policies or standards
- You need to integrate with specific tools or file formats

### Skill vs Agent vs Hook

**Skill**: Specialized knowledge and workflows loaded into context
- Example: Brand guidelines, database schemas, workflow procedures

**Agent**: Autonomous subprocess with specific tools and goals (see `../agents/`)
- Example: Code reviewer, test generator, documentation writer

**Hook**: Event-driven command that runs during Claude Code sessions (see `../hooks-config/`)
- Example: Inject git status on prompt submit, log tool usage

Often these work together:
- Hook triggers workflow based on event
- Skill provides domain knowledge
- Agent executes complex multi-step tasks

### Example Custom Skills

**Examples of good skill candidates**:
- `brand-guidelines` - Company brand assets and style guides
- `database-schema` - Table schemas, relationships, query patterns
- `api-docs` - Internal API documentation and usage examples
- `security-policies` - Security standards and compliance requirements
- `deploy-workflow` - Deployment procedures and runbooks

**Not good skill candidates**:
- One-time tasks (just do them directly)
- Simple information that fits in a short message
- Frequently changing information (better in regular docs)
- Proprietary secrets (use environment variables instead)

## Installation

Official skills can be installed from Anthropic's skill repository:

```bash
cd ~/.claude/skills/
ln -s /path/to/anthropic-official-skills/skill-creator
```

## Creating Skills with skill-creator

Follow the six-step process documented in the skill:

```
1. Understand the skill with concrete examples
2. Plan reusable skill contents
3. Initialize with init_skill.py
4. Edit SKILL.md and bundled resources
5. Package with package_skill.py
6. Iterate based on usage
```

The skill includes detailed guidance on:
- Metadata quality (name and description trigger when skill loads)
- Progressive disclosure design (manage context efficiently)
- Bundled resource best practices
- Packaging and validation

## Resources

- Anthropic Official Skills Repository: https://github.com/anthropics/claude-skills
- Custom skill examples: See `../user/` and `../project/`
- Skill bundled resources guide: See `../user/access-skill-resources/`

## Summary

The skill-creator skill is your guide to extending Claude's capabilities through custom skills. It transforms general AI assistance into specialized expertise tailored to your domain, organization, and workflows.

Well-designed skills make Claude feel like a team member who knows your systems, follows your standards, and understands your domain - because they do.
