---
name: run-qa
description: Launch the QA Engineer agent
allowed-tools: Agent, Read
---

# Run QA Agent

Launch the QA Engineer agent to write and run tests.

## Steps

1. Read `.claude/agents/qa.md` and extract the content after the YAML frontmatter
2. Launch the agent using the Agent tool with `subagent_type: "general-purpose"` and `run_in_background: true`, passing the prompt content
3. Report that the QA agent is running in the background and will poll for `src/main.py` and `docs/architecture/api-spec.yaml` before writing and running tests
