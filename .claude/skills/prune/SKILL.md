---
name: prune
description: Remove all agent-generated artifacts for a clean demo reset
allowed-tools: Bash
---

# Prune

Remove all agent-generated artifacts to reset the project for a fresh demo run.

## Steps

Run the following commands to remove all generated files (whitelist approach — only delete known agent outputs):

```bash
rm -rf docs/ src/ tests/
rm -f Dockerfile Makefile requirements.txt
rm -rf .github/
rm -f *.db
```

After pruning, confirm what was removed:

- `docs/` — PRD, architecture docs
- `src/` — application code
- `tests/` — test suites
- `Dockerfile`, `Makefile` — DevOps config
- `requirements.txt` — Python dependencies
- `.github/` — CI workflows
- `*.db` — SQLite databases

Report that the project is clean and ready for a new demo run.
