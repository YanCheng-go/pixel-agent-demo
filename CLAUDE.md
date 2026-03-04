# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **demo project** for knowledge sharing with VPs and engineers. It showcases multiple Claude Code agents simulating different SDLC roles, collaborating to build a video transcription CLI tool from scratch. The [Pixel Agents](https://github.com/pablodelucca/pixel-agents) VS Code extension visualizes each agent as an animated pixel character in a virtual office.

**This is not a production project.** Prioritize demo-ability, clarity, and "wow factor" over production-readiness.

## Architecture

### Agent Roles (each runs in its own VS Code terminal)

| Role | Responsibility | Works in |
|------|---------------|----------|
| **Product Manager** | Writes PRD, user stories, acceptance criteria | `docs/` |
| **Architect** | Designs pipeline architecture, component breakdown | `docs/architecture/` |
| **Developer** | Implements the video transcription CLI tool | `src/` |
| **QA Engineer** | Writes and runs tests, files bug reports | `tests/` |
| **DevOps** | Sets up Dockerfile, Makefile | project root |

### What Gets Built: Video Transcription CLI Tool

A CLI tool that extracts frames from a recorded video and uses a local vision LLM (Ollama + llama3.2-vision) to produce a timestamped markdown transcript describing what's happening on screen. Vision-only — no audio processing.

Usage: `python src/main.py --video recording.mp4 --interval 5 --model llama3.2-vision:11b`

### Directory Structure

```
pixel-agent-demo/
├── CLAUDE.md
├── docs/                  # PM and Architect outputs
│   ├── prd.md
│   └── architecture/
│       └── design.md
├── src/                   # Developer implementation
│   ├── main.py            # CLI entry point
│   ├── extractor.py       # ffmpeg frame extraction
│   ├── analyzer.py        # Ollama vision API calls
│   └── transcript.py      # Markdown assembly
├── tests/                 # QA test suites
├── Dockerfile
├── Makefile
└── scripts/               # Orchestration/demo helper scripts
    └── run-agents.sh
```

### Demo Flow

1. **PM agent** writes the PRD and user stories
2. **Architect agent** reads PRD, produces pipeline design doc
3. **Developer agent** reads architecture docs, implements the CLI tool
4. **QA agent** reads the code, writes tests, runs them
5. **DevOps agent** reads the codebase, creates Dockerfile and Makefile

Each agent watches for its dependencies (upstream docs/code) before starting its work. The Pixel Agents extension shows all five characters working in the virtual office simultaneously.

## Running the Demo

### Prerequisites
- VS Code with [Pixel Agents extension](https://marketplace.visualstudio.com/items?itemName=pablodelucca.pixel-agents)
- Claude Code CLI installed and configured
- Nix and direnv installed on the host machine
- Open this repo in VS Code

### Launching Agents
Open 5 separate VS Code terminals. In each terminal, run Claude Code with a role-specific prompt from `scripts/prompts/`. The Pixel Agents extension auto-detects each Claude Code instance and spawns a pixel character.

## Development Environment

- **Nix** and **direnv** must be installed on the host machine (prerequisites)
- `run-agents.sh` creates `flake.nix` and `.envrc` and runs `direnv allow` as a pre-step before launching agents
- This provides Python 3.12, ffmpeg, and uv automatically in every terminal opened in the project
- **uv** manages Python dependencies (replaces pip/venv)
- If a system dependency (e.g., a CLI tool) is missing, add it to `flake.nix` and run `direnv reload`. If it's not available in Nix, ask the user before installing at the system level.

## Conventions

- Agents communicate through files, not direct messaging — each agent reads docs/code produced by upstream agents
- Keep all agent prompt templates in `scripts/prompts/` as markdown files
- Tech stack: Python 3.12+, ffmpeg, Ollama with llama3.2-vision:11b
- **Always use `uv` for Python package management** — use `uv pip install` instead of `pip install`, `uv venv` instead of `python -m venv`, etc.
- Agent prompts should include explicit instructions to pause/poll for upstream artifacts before proceeding
