---
name: run-developer
description: Launch the Developer agent
allowed-tools: Agent, Read
---

# Run Developer Agent

Launch the Developer agent to implement the URL shortener service.

## Steps

1. Read `.claude/agents/developer.md` and extract the content after the YAML frontmatter
2. Launch the agent using the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`, passing the prompt content
3. Report that the Developer agent is running in the background and will poll for `docs/architecture/design.md` and `docs/architecture/api-spec.yaml` before implementing the service in `src/`
