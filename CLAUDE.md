# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **demo project** for knowledge sharing with VPs and engineers. It showcases multiple Claude Code agents simulating different SDLC roles, collaborating to build a URL shortener microservice from scratch. A single `/run-demo` skill orchestrates all 5 agents as background subagents within one Claude Code session.

**This is not a production project.** Prioritize demo-ability, clarity, and "wow factor" over production-readiness.

## Architecture

### Agent Roles

| Role | Responsibility | Works in |
|------|---------------|----------|
| **Product Manager** | Writes PRD, user stories, acceptance criteria | `docs/` |
| **Architect** | Designs API spec (OpenAPI), data model, system diagram | `docs/architecture/` |
| **Developer** | Implements the URL shortener service | `src/` |
| **QA Engineer** | Writes and runs tests, files bug reports | `tests/` |
| **DevOps** | Sets up Dockerfile, CI config, Makefile | project root |

### What Gets Built: URL Shortener Microservice

A simple REST API with endpoints:
- `POST /shorten` — create a short URL
- `GET /:code` — redirect to original URL
- `GET /:code/stats` — get click count

### Directory Structure

```
pixel-agent-demo/
├── CLAUDE.md
├── .claude/
│   ├── agents/            # Agent definitions (one per SDLC role)
│   │   ├── pm.md
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── qa.md
│   │   └── devops.md
│   └── skills/
│       ├── run-demo/      # Orchestrates all 5 agents
│       │   └── SKILL.md
│       └── prune/         # Resets generated artifacts
│           └── SKILL.md
├── docs/                  # PM and Architect outputs (generated)
│   ├── prd.md
│   └── architecture/
│       ├── api-spec.yaml
│       └── design.md
├── src/                   # Developer implementation (generated)
├── tests/                 # QA test suites (generated)
├── Dockerfile             # (generated)
└── Makefile               # (generated)
```

### Demo Flow

1. **PM agent** writes the PRD and user stories
2. **Architect agent** reads PRD, produces API spec and design doc
3. **Developer agent** reads architecture docs, implements the service
4. **QA agent** reads the spec, writes tests, runs them against the implementation
5. **DevOps agent** reads the codebase, creates Dockerfile, Makefile, and CI config

Each agent watches for its dependencies (upstream docs/code) before starting its work. All 5 agents run concurrently as background subagents.

## Running the Demo

### Prerequisites
- Claude Code CLI installed and configured

### Launching Agents
Run `/run-demo` in Claude Code. This will:
1. Prune any previous demo artifacts
2. Set up the Nix dev environment
3. Launch all 5 agents in the background concurrently

### Resetting Between Runs
Run `/prune` to remove all generated artifacts without relaunching agents.

## Conventions

- Agents communicate through files, not direct messaging — each agent reads docs/code produced by upstream agents
- Agent definitions live in `.claude/agents/` as markdown files with YAML frontmatter
- The tech stack for the URL shortener itself is flexible (Python/FastAPI or Node/Express are both fine) — pick whichever makes the demo clearest
- Agent prompts include explicit instructions to pause/poll for upstream artifacts before proceeding
