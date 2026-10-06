# Marketing copy

Landing pages, app store listings, promotional video scripts (Rebecca produces the video), launch emails, social posts and product announcements. Marketing copy is held to the same sources rule as everything else: every claim is true, sourced and current.

## Honesty rules

- **No fake testimonials, users, logos or reviews.** Proof is real or absent.
- **No superlatives without a source**: "#1", "fastest", "most accurate" need a cited ranking or benchmark with its date; otherwise cut them. `banned-en.md` flags them with `--profile marketing`.
- **No unreleased features** unless labeled "coming soon". Google's style guide says don't pre-announce in documentation; in marketing, label it.
- **Numbers** show their basis: "2 seconds on a mid-range phone, measured October 2026".
- **Legal claims** (guarantees, security, compliance, privacy) get flagged for review.

## Landing pages

Write the message hierarchy before any copy, then hand Rebecca the copy with the hierarchy (she owns layout):

1. **Headline**: the promise to this reader, in their words.
2. **Subhead**: how it delivers, concretely.
3. **Primary action**: one verb-first CTA.
4. **Proof near the action**: real numbers, real customers, a real screenshot.
5. **How it works**: three steps or fewer, if needed.
6. **Objections answered**: the doubts this reader actually has.
7. **Second CTA** at the end.

The headline must match the promise of whatever sent the reader here (ad, email, store page). Give headline options using the strategy picker (`copy-strategies.md`): different strategies, each named, each with a reason.

## App store listings

Verified limits (Apple's product page guidance and Google Play's store listing best practices, checked 2026-10-06; re-check before shipping, they change):

| Field | Limit | Notes |
|---|---|---|
| App Store name | 30 characters | Strongest search signal |
| App Store subtitle | 30 characters | Shown under the name |
| App Store promotional text | 170 characters | Top of the description; editable without a new release; not used for search ranking |
| App Store keywords | 100 characters, comma-separated, no spaces | Some guides say 100 bytes; Hangul takes 3 bytes per syllable, so the script checks both. Improper keywords are a common rejection reason |
| App Store description | 4,000 characters | Don't stuff keywords |
| Google Play title | 30 characters | |
| Google Play short description | 80 characters | Summarize the biggest benefit |
| Google Play full description | 4,000 characters | Don't repeat the short description; the metadata policy applies to every translation |

Check: `readability_check.py limits listing.json` with ids `ios.name`, `ios.subtitle`, `ios.promo`, `ios.keywords`, `ios.description`, `play.title`, `play.short`, `play.full`. Write each language natively; a Korean listing is written for Korean searchers and their words, not translated.

## Video scripts

Two columns: what's on screen (for Rebecca) and what's said or captioned. From Microsoft's voice-video guidance: one intent per video, set up the problem in a relatable context in the first seconds, show the most common task the best way, keep something happening on screen, and skip the recap at the end. Time the script by reading it aloud at a natural pace; a 30-second script is short. Every on-screen claim is sourced. Mark visuals Rebecca must produce in the visual brief.

## Launch emails, announcements and social posts

Lead with what changed for the reader and why it helps, in the first line. One message per email. The subject line names the news. Social posts: one idea, written for the platform, no hashtag stuffing. For Korean advertising messages, follow the consent and "(광고)" labeling rules (`ux-writing.md` notifications).
