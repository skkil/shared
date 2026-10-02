# Running in Claude Code, Claude Chat, and Claude Design

Detect the environment from what is available: a shell and a repo → Claude Code; a sandbox container with
claude.ai artifact tools → Claude Chat; an artboard canvas with no shell → Claude Design.

## Claude Code (full capability)
- Workspace: `.design/` at the project root (add `.env.design` and optionally `.design/assets/` to `.gitignore`).
- Keys: `FAL_KEY` and `RD_API_KEY` in `.env.design`. Never echo them. `python scripts/media.py status` shows set/missing only.
- Scripts run from the skill folder: `python <skill-dir>/scripts/<script>.py ...`.
- Screenshots: `capture.py` (install Playwright once). Critic: a subagent with screenshots only.
- Companion skills worth installing: `npx skills add remotion-dev/skills`, `npx skills add https://github.com/greensock/gsap-skills`.
- Optional hard gate: offer to add a project hook that runs `slop_lint.py` on changed UI files after edits, so the
  gate fires even when the agent forgets.
- MCP: fal and Retro Diffusion have MCP servers; if connected, they still go through the spend protocol.

## Claude Chat (claude.ai)
- The code sandbox can install packages but cannot reach fal.ai or Retro Diffusion (`media.py run` fails at $0).
  Use the providers' MCP connectors if the user has connected them (same plan-and-approve protocol), or hand the
  user the spec and commands to run locally, then `assets.py import` the results they upload.
- All other scripts work in the sandbox: creative_roll, slop_lint, palette, post, assets.
- Deliver prototypes as HTML artifacts; deliver larger builds as files/zips; Remotion projects as source + commands.
- Screenshots may be unavailable; do the cold-read critic on the rendered artifact.
- `.design/` lives in the sandbox and resets between sessions; give the user DESIGN.md and the library manifest
  to keep, and ask them to re-upload next time.

## Claude Design (canvas, no shell)
- Scripts cannot run. Substitutes:
  - Randomness: ask the user for any three numbers (or use their message timestamp digits) and pick deck items by
    index from `assets/decks/decks.json` (number mod deck length). Never "pick something random" yourself.
  - Linting: walk the anti-slop.md catalog as a checklist against each artboard, explicitly.
  - Generation: write the plan table (asset, model, prompt, size, est. cost, purpose), get approval, and let the user
    generate through a connector or locally. Place correctly sized, labeled placeholders until assets arrive.
- Set up the design system first (tokens from DESIGN.md), then artboards. Hand off to Claude Code with the
  handoff spec (systems-and-handoff.md) for the build, lint, and asset pipeline.
