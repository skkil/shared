# 한국어로 명확하게 쓰기 (Writing clear Korean)

Read this for every Korean deliverable. Korean organizes ideas differently from English, so you write Korean natively from the sources, never by translating an English draft. Sources: 국립국어원 한글 맞춤법(문화체육관광부 고시 제2017-12호)과 외래어 표기법(문교부 고시 제85-11호), 국립국어원 「한눈에 알아보는 공공언어 바로 쓰기」, Microsoft Korean Localization Style Guide, 쿠버네티스 문서 한글화 가이드, 토스 앱인토스 UI/UX 가이드의 UX 라이팅 원칙, KatFishNet (Park et al., ACL 2025), and measurements on Korean technical docs (see `standard.md` §2).

Contents: 1. Structure: 두괄식 · 2. Register · 3. Technical terms · 4. Acronyms · 5. Sentences · 6. 번역투 · 7. Spelling and spacing · 8. UI strings · 9. Readability proxies · 10. Machine-written Korean · 11. Where sources disagree

## 1. Structure: 두괄식

Put the conclusion first (두괄식) in reports, proposals, docs and emails. Korean workplace readers expect it, and it is the same point-first rule as English. Long documents open with a one-line summary (요약) or a 3–5 line summary box. Headings state the point, in noun-phrase or sentence form: "배포 키가 없으면 배포가 실패합니다" or "배포 실패 원인: 누락된 키", not "설정".

## 2. Register

Pick one register per document and keep it. The script warns when one register falls below 85% of sentences.

| Register | Ending | Use for | Source |
|---|---|---|---|
| 합니다체 (formal polite) | ~합니다, ~하세요 for requests | Developer docs, help articles, formal emails, error messages | Microsoft: error messages in "~니다" style; requests in ~세요 instead of ~십시오 |
| 해요체 (polite informal) | ~해요 | Product UI, onboarding, notifications, consumer marketing | Toss: every in-product string in 해요체 |
| 해라체 / 평서형 | ~한다 | Technical reference and open-source docs that already use it (Kubernetes Korean docs use 평어체) | 쿠버네티스 한글화 가이드 |
| 개조식 (noun endings) | ~함, ~임, ~필요, ~예정 | Reports, status updates, slides, meeting notes; one idea per line | Korean report convention |
| ~십시오 | | Legal text, EULAs, terms only | Microsoft |

개조식 drops subjects, which can blur who does what and turn guesses into confident fragments. Keep the actor on lines where responsibility matters ("(Minji) 10/7까지 원인 분석") and the source on lines with claims.

## 3. Technical terms

Korean technical writing keeps established technical terms in English or in Hangul transliteration rather than forcing Korean coinages. Decide each term once and record it in the glossary.

**Priority** (쿠버네티스 한글화 가이드): a natural Korean word (pure Korean, or a Sino-Korean or loanword already in use) → Korean with the English in parentheses → English alone. Never force an unnatural coinage.

**Pair Korean with English once, at first use** on the page, headings included: "훅(hook)", "컨피그맵(ConfigMap)". After that, Korean only.

**Leave in English, never transliterate:** anything the reader will type or copy: field names, file names, paths, commands, flags, API object names that aren't standard nouns, environment variables, error codes. Product and service names stay as the owner writes them (Microsoft): Windows Server, not 윈도우 서버 in product names; no "MS" or "VS" abbreviations.

**Transliterate with 외래어 표기법** when a loanword is the norm (서버, 캐시, 컨테이너). Its five rules: only the current 24 letters; one phoneme, one symbol; only ㄱ ㄴ ㄹ ㅁ ㅂ ㅅ ㅇ as final consonants; no tense consonants for plosives (파리, not 빠리); established spellings keep their customary form. Check 표준국어대사전 for established forms before inventing one.

**Prefer everyday words** for consumer audiences (Microsoft): "메일 주소" for e-mail address, "접근성" for accessibility.

## 4. Acronyms

Microsoft's rule: the acronym comes first, then the expansion in parentheses, at first use.
- If a Korean expansion is common, use it: USB(범용 직렬 버스), DN(고유 이름).
- Otherwise use the English expansion: MMC(Microsoft Management Console), RDL(Report Definition Language).
- No expansion in titles. No plural -s: "OEM 세 곳", not "OEMs".

## 5. Sentences

**One sentence, one idea.** Korean sentences grow long through chained connective endings (~하고, ~하며, ~해서, ~하는데). Split at the second connective when the ideas are separate.

**Verbs, not noun stacks.** Microsoft's guide turns modifiers into verbs ("보다 효율적인 문제 해결을 위해서" → "보다 효율적으로 문제를 해결하려면"), and Toss unpacks Sino-Korean noun stacks into verbs. LLM-written Korean is noun-heavy (KatFishNet), so this matters twice.

**Drop pronouns** when meaning stays clear (Microsoft): "Verify your entry" → "입력 내용을 확인하세요", not "당신의 입력을…". Korean rarely needs 당신, 그것, 그들.

**Fewer commas.** Korean uses fewer commas than English; split the sentence or use a connective ending instead. Human Korean averages well under one comma per sentence (0.37 in the calibration docs).

**Active over passive** (Toss: "됐어요" → "했어요"), except where Toss allows the passive: service ending or expiry, consequences of the user's own action, and reassurance in sensitive moments.

## 6. 번역투

These patterns make Korean sound translated. `banned-ko.md` holds the checkable list with levels; this is the reasoning.

| 번역투 | 자연스러운 표현 | Source |
|---|---|---|
| 조선은 태조에 의해 건국되었다 | 태조가 조선을 건국했다 | NIKL: make the agent the subject |
| 토론을 가지다, 시간을 가지다 | 토론하다, 시간을 보내다 | NIKL, for action nouns only |
| 사용 권한을 가지고 있지 않을 수 있습니다 | 권한이 없을 수 있습니다 | Microsoft |
| 이 앱에 대한 사용 권한 | 이 앱의 사용 권한 | Microsoft |
| 새로 고침 수행에 실패했습니다 | 새로 고치지 못했습니다 | Microsoft: no 수행 with action nouns |
| 이 문서는 기능들에 대한 개요를 제공합니다 | 이 문서에서는 기능을 간략하게 설명합니다 | Microsoft |
| 되어지다 | 되다 | Kubernetes guide: 이중 피동 |
| 짧은 다리를 가진 돼지 | 다리가 짧은 돼지 | Kubernetes guide |
| 교수와의 대화, 한국에서의 전쟁 | 교수와 나눈 대화, 한국 전쟁 | NIKL: particle + 의 |
| 배들, 사과들, 복숭아들이 있다 | 배, 사과, 복숭아가 있다 | Kubernetes guide: plural overuse |

**Don't over-correct.** NIKL does not treat 국적을 가지다, 직업을 가지다, or 기자 회견을 가지다 as 번역투. Flag only the patterns above, and read the sentence before changing it.

## 7. Spelling and spacing

Follow 한글 맞춤법. The spacing rules that matter most in technical writing:
- Words are spaced; particles attach (제2항, 제41항).
- Dependent nouns are spaced: 할 수 있다, 그런 것 같다, 할 때, 할 뿐 (제42항).
- Counters are spaced from numerals in words but may attach to digits: 세 개, 3개.
- Auxiliary verbs are spaced in principle, attaching allowed (제47항); choose one form per document.
- Proper nouns other than names may be spaced by word or unit (제49항: 국립 국어원 / 국립국어원); record the choice in the glossary.
- Compounds are written solid (Microsoft): 구름다리, 손가방.
- Frequent errors: 되요 → 돼요, 몇일 → 며칠, 금새 → 금세, 웬만하다.

## 8. UI strings

From Toss and Microsoft, with the conflicts in §11:
- **Endings:** one register for the whole product (usually 해요체 for consumer apps, 합니다체 for B2B and developer tools).
- **Casual honorifics** (Toss): avoid "~시겠어요?", 계시다 → 있다, 께 → 에게, except when asking about the user's context, guessing their situation, or asking for goodwill (surveys).
- **돼요, not 되어요**, for space (Toss).
- **Positive framing** (Toss): "~하면 할 수 있어요" over "안 돼요", except when a policy blocks the user, part of a feature is unavailable, or the negative reassures ("정보를 저장하지 않아요").
- **Buttons:** short verbs that predict the next screen. Toss forbids repeating the screen's message in the CTA.
- **Error messages** (Microsoft standard phrases): "~할 수 없습니다", "~하지 못했습니다", "찾을 수 없습니다", "~하는 동안 오류가 발생했습니다", and always what to do next.
- **Placeholders:** use dual particles because you don't know the inserted word: 을(를), 이(가), 은(는), 과(와), (으)로. Attach counters to number placeholders: "%d개", "%d일".
- **Keys:** "Shift 키" with a space; key combinations without 키: "Ctrl+C를 누르세요".
- **Accessibility:** "선택하세요" rather than "클릭하세요"; it works for every input method (Microsoft).

## 9. Readability proxies

English grade formulas don't work for Korean, and no Korean formula is validated and widely adopted. Korean readability studies rely on 어절 counts, sentence counts, the ratio of distinct 어절, vocabulary difficulty and morphological sentence complexity. `readability_check.py` therefore uses proxies:

| Proxy | Default | Basis |
|---|---|---|
| 어절 per sentence (WARN above) | 17 | About the 90th percentile of 1,060 sentences of well-regarded Korean technical docs; parallels the English 25-word cap |
| Characters per sentence (INFO above) | 90 | Twice the measured mean (44.7) |
| Commas per sentence, document average | 0.8 | KatFishNet direction; calibration docs average 0.37 |
| Register consistency | 85% | One register per document |
| "~적" words per sentence | 3 | Noun-stack signal |
| Line length on screen | ≤40 characters per line for CJK text | WCAG 1.4.8 |

## 10. Machine-written Korean

What gives it away: commas after every connective ending; nouns and Sino-Korean compounds where a verb would do; "~적" chains; every sentence ending the same way; formulaic openers ("오늘날 빠르게 변화하는…", "~에 대해 알아보겠습니다"); closers ("결론적으로 ~라고 할 수 있습니다", "도움이 되기를 바랍니다"); inflated words (혁신적인, 획기적인, 중요한 역할을 합니다). Fix the content first: what specific fact belongs in that sentence?

## 11. Where sources disagree

House styles conflict. Pick one per product, record it in the glossary or voice guide, and keep it.

| Question | Toss | Microsoft | Default |
|---|---|---|---|
| Left button of a dialog | 닫기 (취소 suggests cancelling the user's work) | [취소] | Toss for consumer apps, Microsoft for productivity and developer tools |
| Asking to continue | Avoid "~시겠어요?" | 계속하시겠습니까? | Follows the product register |
| UI register | 해요체 everywhere | 합니다체 with ~세요 requests | Voice guide decides |
