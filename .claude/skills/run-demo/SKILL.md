---
name: run-demo
description: Launch the full 5-agent SDLC demo
allowed-tools: Bash, Agent, Read, Write, Glob
---

# Run Demo

Launch all 5 SDLC agents to collaboratively build a URL shortener microservice from scratch.

## Steps

### 1. Prune all agent-generated artifacts

Remove all files produced by previous demo runs. Only delete these specific paths (whitelist approach):

```
rm -rf docs/ src/ tests/
rm -f Dockerfile Makefile requirements.txt
rm -rf .github/
rm -f *.db
```

### 2. Set up Nix dev environment

Create `flake.nix` with Python 3.11 and uv in the dev shell. Create `.envrc` with `use flake`. Then run:

```bash
git add flake.nix
direnv allow
```

Wait for the direnv environment to load before proceeding.

### 3. Launch all 5 agents concurrently

Use the Agent tool to launch all 5 agents **in the background** concurrently. Each agent has its own dependency polling logic built in, so they will self-coordinate:

1. **PM Agent** (`.claude/agents/pm.md`) — starts immediately, writes `docs/prd.md`
2. **Architect Agent** (`.claude/agents/architect.md`) — polls for `docs/prd.md`, then writes architecture docs
3. **Developer Agent** (`.claude/agents/developer.md`) — polls for architecture docs, then implements the service
4. **QA Agent** (`.claude/agents/qa.md`) — polls for `src/main.py` + API spec, then writes and runs tests
5. **DevOps Agent** (`.claude/agents/devops.md`) — polls for `src/main.py` + `requirements.txt`, then creates infra files

For each agent, use `subagent_type: "general-purpose"` and `run_in_background: true`. Pass the full content of the agent's `.md` file (after the frontmatter) as the prompt.

### 4. Report status

After launching all agents, report that all 5 agents are running in the background with their dependency chain:

```
PM -> Architect -> Developer -> QA + DevOps
```

The agents will coordinate through file polling. No further action is needed — they will complete autonomously.
