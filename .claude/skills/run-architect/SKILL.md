---
name: run-architect
description: Launch the Architect agent
allowed-tools: Agent, Read
---

# Run Architect Agent

Launch the Architect agent to design the API spec and system architecture.

## Steps

1. Read `.claude/agents/architect.md` and extract the content after the YAML frontmatter
2. Launch the agent using the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`, passing the prompt content
3. Report that the Architect agent is running in the background and will poll for `docs/prd.md` before producing `docs/architecture/design.md` and `docs/architecture/api-spec.yaml`
