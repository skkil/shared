# Changelog

All notable changes to the `skkil` plugin. Versions follow `version` in
`.claude-plugin/plugin.json`; each release is tagged `skills-v<version>`.

## 0.4.0

- Rebecca: add refinement passes (bolder, quieter, distill, polish, harden, clarify, adapt, delight) as concrete moves.
- Rebecca: `slop_lint.py` gains `--tokens` (DESIGN.md color drift), `--github` annotations, stale-allowance reporting and a `scale-from-zero` rule.
- Rebecca: `capture.py` captures 1440/768/390 by default and adds `--overflow` for horizontal-scroll detection.
- Rebecca: interaction-frequency motion budget, one-trait rule for directions, pre-component token checkpoint, blind UX walkthrough.
- Rebecca: add `blender.py` and `references/blender.md` for real 3D modeling in headless Blender: previews, mesh checks, GLB export, turntables.
- Rebecca: add `draw.py` and `references/generative-art.md` for seeded code painting: ink wash, flow fields, contours, hatching.
- Rebecca: add `video_check.py` for encode checks, loop seams, frame sheets, safe zones and delivery re-encodes.
- Rebecca: `palette.py` gains `roles` (contrast-solved palettes) and `cvd` (color-blindness simulation).
- Rebecca: `slop_lint.py` gains layout-animation, outline-none, clickable-div, timer-animation, perpetual-motion and hover-no-transition rules.
- Rebecca: procedural three.js, exploded views and perf budgets; dembrandt token extraction; logo sheets at 16/32 px; component registry gates.

## 0.3.0

- Add `vanessa`, the writer skill.
- Point Jennifer's docs handoffs at Vanessa and have her answer Vanessa's clarification requests.
- Have Rebecca defer voice to `.vanessa/voice.md`, take Vanessa's visual briefs, and ask Vanessa for copy inside designs.

## 0.2.0

- Add `jennifer`, the product-manager skill.

## 0.1.0

- Add `rebecca`, the lead-designer skill.
