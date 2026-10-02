# Critique and quality assurance

## 1. The loop
build → capture screenshots → `slop_lint.py` (must pass) → fresh critic → fix the top gaps → repeat.
Stop when the critic scores ≥ 8.5/10 and lint passes, or after 2 critic rounds (then present with the remaining
gaps stated honestly). More rounds tend to churn rather than improve.

## 2. Fresh-context critic
- Spawn a subagent (Claude Code: Task/agent tool) with ONLY the screenshots, optional reference images that set the
  bar, a one-paragraph brief, and `assets/templates/critic-prompt.md`. No code, no conversation history.
- Reference images matter: comparing against 1-3 examples of excellent work in the same aesthetic produces sharper,
  more useful critique than an abstract bar.
- Without subagents (Chat, Design): do a deliberate cold read. Write the critic prompt's sections yourself,
  looking only at the rendered output, and assume the work is not done.
- Act on gaps that serve the brief; ignore suggestions that would add decoration or contradict DESIGN.md.

## 3. Rubric (score each 0-10; the critic's overall score is not an average)
1. First impression and the 5-second test.
2. Hierarchy and composition (one focal point, clear reading order).
3. Distinctiveness (memory test: a specific thing, not a mood; no category defaults).
4. Product truth (shows the real product, real proof, no invented claims).
5. Craft details (type, spacing, alignment, states, browser surfaces).
6. Copy (specific, voice-consistent, no tells).
7. Motion (purposeful, one signature moment, reduced-motion path).
8. Accessibility (section 4).
9. Platform fit (conventions in Operate mode; responsive; native expectations).

## 4. Accessibility floor (WCAG 2.2 AA, quick list)
- Contrast: text 4.5:1 (large 3:1), UI components and meaningful graphics 3:1 (`palette.py`).
- Keyboard: everything operable; visible focus that is not obscured by sticky headers (2.4.11); logical order.
- Target size: at least 24×24 CSS px (2.5.8); 44pt iOS / 48dp Android recommended.
- Dragging has a single-pointer alternative (2.5.7).
- Names and roles: labels on inputs, alt text on meaningful images, decorative images hidden, headings in order.
- Motion: reduced-motion path; no flashing > 3/s; pause for anything moving > 5s.
- Text resizes to 200% without loss; supports Dynamic Type / font scaling on native.
- Errors identified in text with suggestions; accessible authentication (no puzzle-only logins).

## 5. Pre-delivery checklist (copy into the response or a file and check off)
- [ ] Brief and user promise met; the first viewport answers what/who/what to do
- [ ] DESIGN.md updated (tokens, decisions, allowances)
- [ ] `slop_lint.py` passes; every WARN reviewed; allowances quote the brief
- [ ] Critic score ≥ 8.5 or 2 rounds done, with remaining gaps listed
- [ ] Every claim has real proof; no placeholder people/companies/stats
- [ ] All states designed (empty, loading, error, success; hover/focus/active/disabled)
- [ ] Contrast matrix checked; keyboard path works; reduced motion works
- [ ] Mobile and desktop screenshots reviewed
- [ ] Assets: library ids recorded, rated, licenses noted, spend reported
- [ ] Subtraction pass done (one decorative element removed per section, if any remained)
