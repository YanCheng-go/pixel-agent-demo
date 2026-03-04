#!/usr/bin/env bash
# run-agents.sh — Launch all 5 SDLC agents for the Pixel Agents demo
#
# Requirements: macOS, VS Code with Pixel Agents extension, Claude Code CLI
# Usage:
#   bash scripts/run-agents.sh          — clean artifacts + walk through launching each agent
#   bash scripts/run-agents.sh prune    — only remove generated files (reset for fresh demo)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# --- Prune: remove all agent-generated artifacts ---
prune() {
  echo "=== Pruning all agent-generated artifacts ==="
  rm -rf docs/ src/ tests/
  rm -f Dockerfile Makefile requirements.txt flake.nix flake.lock .envrc
  rm -rf .direnv/
  rm -rf output/ frames/
  rm -f *.db
  echo "Removed:"
  echo "  docs/                        (PRD, architecture)"
  echo "  src/                         (application code)"
  echo "  tests/                       (test suites)"
  echo "  Dockerfile, Makefile         (DevOps config)"
  echo "  flake.nix, .envrc, .direnv/  (Nix dev environment)"
  echo "  requirements.txt             (dependencies)"
  echo "  output/, frames/             (generated transcripts and temp frames)"
  echo ""
  echo "Project is clean and ready for a new demo run."
}

if [[ "${1:-}" == "prune" ]]; then
  prune
  exit 0
fi

# --- Normal mode: guided agent launch ---
echo "=== Pixel Agent Demo — Video Transcription Tool ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# --- Check prerequisites ---
for cmd in nix direnv; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd is not installed. Please install it first."
    exit 1
  fi
done

# Ensure prompt files exist
for role in pm architect developer qa devops; do
  if [[ ! -f "scripts/prompts/${role}.md" ]]; then
    echo "ERROR: Missing prompt file: scripts/prompts/${role}.md"
    exit 1
  fi
done

# Clean previous artifacts
prune
echo ""

# --- Set up dev environment ---
echo "=== Setting up dev environment ==="

if [[ ! -f "flake.nix" ]]; then
  cat > flake.nix <<'FLAKE'
{
  description = "Video transcription CLI tool dev environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.python312
              pkgs.ffmpeg
              pkgs.uv
            ];
          };
        });
    };
}
FLAKE
  echo "Created flake.nix"
fi

if [[ ! -f ".envrc" ]]; then
  echo "use flake" > .envrc
  echo "Created .envrc"
fi

direnv allow
echo "Dev environment ready (Python 3.12, ffmpeg, uv via Nix)"
echo ""

# --- Walk through each agent ---
ROLES=("pm" "architect" "developer" "qa" "devops")
LABELS=("Product Manager" "Architect" "Developer" "QA Engineer" "DevOps Engineer")

echo "We'll launch 5 agents one at a time."
echo "For each agent:"
echo "  1. Click '+ Agent' in the Pixel Agents panel (opens a claude session)"
echo "  2. The prompt is copied to your clipboard — paste (Cmd+V) and press Enter"
echo ""
echo "---"

for i in "${!ROLES[@]}"; do
  role="${ROLES[$i]}"
  label="${LABELS[$i]}"
  prompt_path="${PROJECT_ROOT}/scripts/prompts/${role}.md"
  num=$((i + 1))

  echo ""
  echo "[$num/5] ${label}"
  echo "  -> Click '+ Agent' in Pixel Agents panel"

  # Copy the prompt content (not a command) to clipboard
  cat "$prompt_path" | pbcopy

  echo "  -> Prompt copied to clipboard! Paste (Cmd+V) into the claude session and press Enter."
  echo ""

  if [[ $num -lt 5 ]]; then
    read -rp "  Press Enter here when ready for the next agent..."
  else
    read -rp "  Press Enter here when done..."
  fi
done

echo ""
echo "=== All 5 agents launched! ==="
echo ""
echo "Agent coordination (via file polling):"
echo "  PM           -> writes docs/prd.md"
echo "  Architect    -> waits for PRD -> writes pipeline design doc"
echo "  Developer    -> waits for architecture -> implements CLI transcription tool"
echo "  QA Engineer  -> waits for code -> writes and runs tests"
echo "  DevOps       -> waits for code -> creates Dockerfile, Makefile"
