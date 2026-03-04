# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **demo project** for knowledge sharing with VPs and engineers. It showcases multiple Claude Code agents simulating different SDLC roles, collaborating to build a URL shortener microservice from scratch. The [Pixel Agents](https://github.com/pablodelucca/pixel-agents) VS Code extension visualizes each agent as an animated pixel character in a virtual office.

**This is not a production project.** Prioritize demo-ability, clarity, and "wow factor" over production-readiness.

## Architecture

### Agent Roles (each runs in its own VS Code terminal)

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
├── docs/                  # PM and Architect outputs
│   ├── prd.md
│   └── architecture/
│       ├── api-spec.yaml
│       └── design.md
├── src/                   # Developer implementation
├── tests/                 # QA test suites
├── Dockerfile
├── Makefile
└── scripts/               # Orchestration/demo helper scripts
    └── run-agents.sh
```

### Demo Flow

1. **PM agent** writes the PRD and user stories
2. **Architect agent** reads PRD, produces API spec and design doc
3. **Developer agent** reads architecture docs, implements the service
4. **QA agent** reads the spec, writes tests, runs them against the implementation
5. **DevOps agent** reads the codebase, creates Dockerfile, Makefile, and CI config

Each agent watches for its dependencies (upstream docs/code) before starting its work. The Pixel Agents extension shows all five characters working in the virtual office simultaneously.

## Running the Demo

### Prerequisites
- VS Code with [Pixel Agents extension](https://marketplace.visualstudio.com/items?itemName=pablodelucca.pixel-agents)
- Claude Code CLI installed and configured
- Open this repo in VS Code

### Launching Agents
Open 5 separate VS Code terminals. In each terminal, run Claude Code with a role-specific prompt from `scripts/prompts/`. The Pixel Agents extension auto-detects each Claude Code instance and spawns a pixel character.

## Conventions

- Agents communicate through files, not direct messaging — each agent reads docs/code produced by upstream agents
- Keep all agent prompt templates in `scripts/prompts/` as markdown files
- The tech stack for the URL shortener itself is flexible (Python/FastAPI or Node/Express are both fine) — pick whichever makes the demo clearest
- Agent prompts should include explicit instructions to pause/poll for upstream artifacts before proceeding
