---
name: run-pm
description: Launch the Product Manager agent
allowed-tools: Agent, Read
---

# Run PM Agent

Launch the Product Manager agent to write the PRD.

## Steps

1. Read `.claude/agents/pm.md` and extract the content after the YAML frontmatter
2. Launch the agent using the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`, passing the prompt content
3. Report that the PM agent is running in the background and will produce `docs/prd.md`
