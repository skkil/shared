# Korea playbook

Contents: 1. Language and register · 2. Document conventions · 3. Platforms and user habits · 4. Sources · 5. Regulation flags · 6. University and lab context · 7. Example: 개조식 weekly report

## 1. Language and register

- Ask which language a document should be in before drafting (SKILL.md, Language). In conversation, follow the human's language.
- Write Korean documents natively in Korean structure, not translated English. Tech teams commonly keep certain terms in English (PRD, MVP, KPI, OKR, API, A/B 테스트); follow the team's existing usage, and define a term in parentheses on first use if the audience is non-technical.
- Register: reports to leadership, partners, and government programs use 합쇼체 (~습니다) or 개조식 (~함, ~임); team chat and informal notes use 해요체. Never mix registers within one document. User-facing product copy follows the product's voice guide (usually 해요체).
- Titles and names: use roles and honorifics appropriately in external documents (e.g., 교수님, 대표님, 담당자님); in internal documents, follow team convention.

## 2. Document conventions

- **두괄식:** conclusion and request first. A one-line summary box at the top of anything longer than a page.
- **개조식:** itemized, noun-ending lines with a consistent symbol hierarchy (`□` → `○` → `-` → `·`) or the team's numbering (`1.` → `가.` → `1)`). Keep evidence labels and the actor on lines where responsibility or certainty matters (see `writing-reports.md` section 7).
- **변경 이력** (change history) at the top of every spec.
- Deliverable names and contents: see `specs-and-deliverables.md` section 1 (기획 개요서, 서비스 기획서, 요구사항 정의서, 정책서, 정보구조도, 화면설계서, 기능명세서, 이벤트 정의서, QA 시나리오, WBS, 출시 계획서, 출시 회고).
- **화면설계서:** commonly 16:9 slides (PowerPoint or Figma): a top bar with screen ID, screen name, and navigation path; the wireframe on the left; a numbered description table on the right. IA is commonly a spreadsheet with depth columns (1 depth, 2 depth, 3 depth), screen IDs, and access conditions.
- Dates as `2026.10.02.` or `10/2(금)`; times in 24-hour format in formal documents. Money in 원 with thousands separators (e.g., 1,200,000원), or 만원/억원 units in summaries.

## 3. Platforms and user habits

Check current data before quoting any share or usage number (Mobile Index, WiseApp, Naver DataLab); these change and are on the do-not-invent list.

- **Search and content:** Naver is central for Korean research, alongside Google. Naver blogs, cafes, and 지식iN shape purchase research; YouTube matters for how-to content.
- **Messaging and sharing:** KakaoTalk is the default for sharing and notifications; KakaoTalk business messages (알림톡, 친구톡) require a business channel and approved templates.
- **Login and identity:** social login with Kakao, Naver, Google, and Apple is expected; identity verification (본인인증) through mobile carriers or apps such as PASS is common for age- or identity-sensitive services.
- **Payments:** card payments plus easy-pay services (KakaoPay, Naver Pay, Toss Pay, Samsung Pay); a payment gateway (PG) contract is usually needed for web payments.
- **App stores:** Google Play and the App Store, plus ONE store for some categories.
- **Communities:** Disquiet and GeekNews (startups and builders), OKKY and Velog (developers), Clien (tech-savvy general users), Blind (workplace), Everytime (university students), and topic-specific Naver cafes.
- **Calendar:** lunar holidays (설날, 추석) shift each year and depress usage for some products and spike it for others; the academic year runs March-June and September-December with midterm and final exam peaks; the 수능 is in November.

## 4. Sources

See `market-research.md` section 2 for the full table (Naver DataLab, Mobile Index, WiseApp, KOSIS, data.go.kr, DART, THE VC, Innoforest, K-Startup). Also: 국가법령정보센터 (law.go.kr) for statutes, 개인정보보호위원회 (pipc.go.kr) for privacy guidance, and the Ministry of Science and ICT (과기정통부) for AI policy.

## 5. Regulation flags

Jennifer flags these for professional review; she doesn't give legal advice. When a feature touches one, the PRD's risk section names it and Sasha reviews it.

- **Personal Information Protection Act (개인정보 보호법, PIPA):** collection needs a stated purpose, the items collected, the retention period, and consent (with the right to refuse explained); stricter rules for sensitive information and unique identifiers such as resident registration numbers; children under 14 need a legal guardian's consent; a published privacy policy (개인정보 처리방침); disclosure and consent rules for transfers abroad; breach notification duties.
- **AI Basic Act (인공지능 기본법):** in force since January 22, 2026, with administrative fines (up to KRW 30 million) deferred for a grace period of at least one year. Products using generative AI must give users advance notice that the service uses it and label generated output, with exceptions when AI use is obvious or for purely internal use. Services that may count as "high-impact" AI need a prior review and carry heavier duties (risk management, human oversight, explanation). Detailed guidance is still developing; check current guidance before launch.
- **Information and Communications Network Act (정보통신망법):** advertising messages need prior consent, an "(광고)" label, an easy opt-out, and separate consent for sending at night.
- **E-commerce rules (전자상거래법):** subscription, auto-renewal, free-trial-to-paid conversion, and refund or withdrawal rules affect pricing and billing flows.
- **Location information (위치정보법):** services using location data may need reporting or licensing.
- **Accessibility:** Korean web accessibility standards and disability-discrimination obligations apply to many services, especially public-facing and public-sector ones.

## 6. University and lab context

- **Research ethics:** when interviews or surveys with real people are part of academic research (or results may be published), approval from the institution's IRB (기관생명윤리위원회) may be required before contacting participants. Ask before recruiting.
- **Industry-academia collaboration (산학협력):** proposals follow the partner's or the university's 산학협력단 templates; contracts and IP terms go through the 산학협력단 and legal review.
- **Startup support:** university startup support centers (창업지원단) run programs, mentoring, and space; many government programs have student or pre-founder tracks.
- **Students as a segment:** price sensitivity, semester rhythms, group projects, and Everytime as the main community.

## 7. Example: 개조식 weekly report

```
□ 요약: sync 2.4 출시 일정 정상(On track), 단 iOS 백그라운드 동기화 리스크 1건 확인
□ 진행 현황
  ○ 오프라인 큐 기능 개발 완료, QA 진행 중 [Quinn, 10/7 완료 예정]
  ○ 주간 활성 동기화 사용자 1,840명, 전주 대비 6% 증가 [measured, 9/22-9/28]
□ 리스크
  ○ (Emil) iOS 백그라운드 실행 제한으로 대용량 파일 동기화 지연 가능성 높음
    - 대응: 10/4까지 원인 분석 후 범위 조정 여부 결정
□ 의사결정 요청
  ○ 2.4 범위에서 대용량 파일(1GB 초과) 지원 제외 여부: 10/5(일)까지 회신 요청
```
