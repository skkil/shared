# Refinement passes

Users ask for adjectives: "bolder", "cleaner", "more polished". An adjective with nothing behind it gets read as
"add more", which is how gradients and glows arrive. Each pass below turns the word into specific moves and a
specific thing it must not do. Run one pass at a time, on the surface the user named, then lint and capture.

Refinement is not redesign. A pass keeps the direction in DESIGN.md. If the pass cannot succeed without changing
the THESIS, palette strategy or type roles, stop and say so: that is a new direction and goes back through Define.

| Pass | Means | Concrete moves | Never |
|---|---|---|---|
| **bolder** | Stronger hierarchy, more decisive | Raise the display size step 1-2 ramp stops; widen the gap between heading and body weights; give the signature element more area; cut competing elements | Add gradients, glows, more colors, or more motion |
| **quieter** | Less competition for attention | Drop one accent use per section; lower secondary text contrast within AA; collapse borders into spacing; slow or remove ambient motion | Wash out the primary action or the signature moment |
| **distill** | Fewer things, each doing more | Merge sections that make the same point; delete the weakest card, stat or badge; one CTA per viewport | Remove proof, states or accessibility affordances |
| **polish** | Details at the studio bar | Optical alignment of icons and text; consistent radius and shadow tiers; hanging punctuation; tabular numbers in data; focus rings drawn, not default; one subtraction per section | Introduce new components or new tokens |
| **harden** | Survives real content and real users | Long names, empty data, 200% text, RTL if shipped, slow network, error and offline states, 280px width without horizontal scroll | Hide overflow with `overflow: hidden` on the page |
| **clarify** | The user knows what to do next | Rewrite labels to name outcomes; make the primary action the most visible thing; put errors next to their cause; ask Vanessa for copy | Add tooltips or helper text to explain unclear design |
| **adapt** | Fits another platform or size | Re-compose, don't shrink: reorder by task, swap hover for tap, use the platform's navigation and controls (platforms.md) | Scale the desktop layout down |
| **delight** | One moment worth remembering | Place a single signature interaction at the moment of success or first value; give it a reduced-motion version | Animate high-frequency actions or add ambient decoration everywhere |

After every pass: `slop_lint.py --tokens .design/DESIGN.md`, `capture.py`, compare before and after screenshots
side by side, and report a `Before | After | Why` table for the changes that matter.
