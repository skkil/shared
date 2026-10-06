# UX writing

Microcopy, error messages, empty states, tooltips, confirmations, loading and success states, onboarding flows, notifications and push messages, transactional emails, feature and product names, accessibility text, and strings files ready for translation.

UI text is read in a hurry, mid-task, often on a phone. Every word either helps the user do the next thing or gets in the way. Write from the user's side: name things by what users understand, not by how the system is built ("notifications", not "webhook config").

## Before writing any string

Know: where it appears (screen, component, state), who sees it and in what state of mind (calm, rushed, worried about money), what happens next, the character limit (from the design or the component; ask Rebecca if unknown), and the glossary term for every concept in it. The product's real behavior is the source: read the code or the spec for what actually happens, the real limits, the real error causes.

## Patterns

**Buttons and CTAs.** A verb plus an object that names the outcome: "Save changes", "Send invoice", not "Submit" or "OK". The label must let the user predict the next screen (Toss), and the same action keeps the same name through the flow: a "Publish" button produces a "Published" confirmation (Anthropic's frontend-design skill). Don't repeat the screen's message inside the button.

**Error messages.** What happened, why (if the user can act on it), and what to do next, in plain words. No blame, no vague "Something went wrong", no codes without meaning (keep codes for support, after the explanation). Calm tone; errors don't need jokes. Apologize only when the product failed the user, once.

| Don't | Do |
|---|---|
| Upload failed (413). | The file is larger than 25 MB. Choose a smaller file or compress it. |
| Invalid ID | Enter your ID like this: name@example.com (Microsoft's example) |
| 오류가 발생했습니다. | 파일이 25MB보다 커서 올릴 수 없어요. 더 작은 파일을 선택해 주세요. |

Korean error phrasing follows Microsoft's standard forms (`language-ko.md` §8): "~할 수 없습니다", "~하지 못했습니다", "찾을 수 없습니다", "~하는 동안 오류가 발생했습니다", adapted to the product's register.

**Empty states.** What this place is for, why it's empty, and the one action that fills it: "No invoices yet. Create your first invoice to bill a client." An empty screen is an invitation to act.

**Confirmations.** Name the action and the consequence: "Delete 3 files? You can't undo this." Label the buttons with the actions: "Delete files" / "Keep files", not "OK" / "Cancel". In Korean consumer apps following Toss, the dismiss button is "닫기", because "취소" can read as cancelling the user's work; record the product's choice in the glossary.

**Tooltips.** Only for information the label can't carry; never repeat the label. One or two short sentences.

**Loading and progress.** Say what's happening and set an expectation when the wait is long: "Uploading 3 of 12 photos". Korean progress text uses "~하는 중…" (Microsoft). Don't show a loading animation when nothing is being waited for (Toss).

**Success.** Confirm what happened, briefly, and offer the next step if there is one. Celebrate in proportion; a saved setting isn't a party.

**Onboarding flows.** One concept per screen, each tied to an action the user takes now. Ask only for what's needed now. Let users skip.

**Notifications and push.** Lead with the value or the event, in the first few words (they truncate). Respect consent; in Korea, advertising messages need prior consent, an "(광고)" label and an easy opt-out under the Information and Communications Network Act (see Jennifer's Korea notes when available). No pleading or guilt to keep users (Toss lists these as dark patterns).

**Transactional emails.** The subject says what happened ("Your refund of $40 is on its way"). The first line repeats it with the key detail; then what the user needs to do, if anything; then support.

**Feature and product names.** Prefer descriptive names that say what the thing does; an evocative name needs a descriptive subtitle. Check the glossary and existing names for collisions; check the Korean version reads naturally; flag trademark checks for legal. Use the strategy picker (`copy-strategies.md`) when the user wants options.

## Accessibility text

- **Alt text** says what the image communicates in context, not what it looks like pixel by pixel: "Revenue doubled from Q1 to Q3" for a chart. Decorative images get empty alt (`alt=""`).
- **Icon-only buttons** need an accessible name: `aria-label="Close"` / `"닫기"`.
- **Generic verbs that work for every input:** "select", not "click" (Microsoft); "선택하세요" in Korean.
- **Links** say where they go.
- **Screen readers** read symbols oddly; spell out "and" rather than "&" in labels (Microsoft).

## Strings files for translation

Write strings so translators and other languages' grammar can work with them:

- **Whole sentences, never assembled from fragments.** "You have {count} new messages" is one string; "You have " + count + " new messages" breaks languages with different word order.
- **Named placeholders** (`{count}`, `{name}`) with a translator comment explaining each.
- **Plurals** through the platform's plural mechanism (ICU MessageFormat, Android plurals, iOS stringsdict), never "message(s)".
- **Korean placeholders** need dual particles, because you don't know the inserted word: "{name}을(를)", "{app}이(가)" (Microsoft), or rephrase to avoid the particle.
- **Comments for context**: where the string appears, the limit, the tone.
- **One key per meaning**, even if the English text is identical in two places; translations may differ.
- **Keep keys stable** and descriptive (`invoice.delete.confirm.title`).

Check limits with `readability_check.py limits strings.json --limits limits.json` (or `.strings`, `strings.xml`).

## Output format for UI copy requests

For each string: the recommended text, the character count against its limit, and when the wording is a real choice, one alternative with the trade-off. Add translator notes for anything ambiguous. Explain the key choice in one sentence.
