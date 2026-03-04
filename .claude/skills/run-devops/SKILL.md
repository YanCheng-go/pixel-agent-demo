---
name: run-devops
description: Launch the DevOps Engineer agent
allowed-tools: Agent, Read
---

# Run DevOps Agent

Launch the DevOps Engineer agent to create Dockerfile, Makefile, and CI config.

## Steps

1. Read `.claude/agents/devops.md` and extract the content after the YAML frontmatter
2. Launch the agent using the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`, passing the prompt content
3. Report that the DevOps agent is running in the background and will poll for `src/main.py` and `requirements.txt` before creating infrastructure files
