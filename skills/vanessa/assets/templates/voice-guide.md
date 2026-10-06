# Voice and tone guide: <product>

_Last updated YYYY-MM-DD by Vanessa. Read before every writing task. Voice stays the same; tone changes with the reader's situation._

## Who we're talking to

<Main readers, one line each, in their words.>

## Voice: 3–5 traits

| Trait | We sound like | We don't sound like |
|---|---|---|
| <Plain> | "Your export is ready." | "Your data export process has been successfully completed!" |
| <Calm> | "We couldn't charge your card. Update it to keep your plan." | "Oops! Payment failed!!" |
| | | |

## Tone by situation

| Situation | Tone | Example |
|---|---|---|
| Errors and failures | Calm, specific, no jokes | |
| Money, data loss, security | Plain and serious | |
| Empty states and onboarding | Encouraging, action-first | |
| Success | Brief; celebrate only real milestones | |
| Marketing and launches | Confident, concrete, sourced | |

## Language and register

- English: <contractions yes/no; negative contractions; we/you>
- Korean: <해요체 in product UI / 합니다체 in docs / …; dialog dismiss button: 닫기 or 취소>

## Words we use and avoid

See `glossary.md`. Voice-level words to avoid: <e.g., "simply", "easy", 혁신적인>.

## Targets the checker reads

Edit the numbers; `readability_check.py` reads this block. Remove keys you don't need to change.

```vanessa-config
{
  "en": {"sentence_words_warn": 25, "paragraph_sentences_warn": 4,
         "grade_targets": {"end-user": 8, "marketing": 8, "internal": 10, "developer": null},
         "negative_contractions": "allow"},
  "ko": {"sentence_eojeol_warn": 17, "paragraph_sentences_warn": 4, "commas_per_sentence_warn": 0.8},
  "acronym_allowlist": ["OK"],
  "strategies_avoid": [],
  "extra_banned": [{"pattern": "\\bsynergy\\b", "level": "WARN", "why": "not our voice", "instead": "say what works together"}]
}
```

## Change log

- YYYY-MM-DD: <rule added and why, from which feedback>
