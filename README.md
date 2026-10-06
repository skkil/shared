# shared

skkil 조직의 모든 저장소가 함께 사용하는 설정과 규약을 모아두는 저장소입니다.

린트·포매터 규칙, TypeScript 기본 설정, 재사용 가능한 CI 워크플로, Terraform
모듈, 아키텍처 결정 기록(ADR), 그리고 에이전트 컨텍스트 중 조직 공통에 해당하는
부분이 여기에 위치합니다.

저장소마다 같은 설정을 복사해 두면 처음에는 같아 보여도 결국 조용히 어긋납니다.
어긋났다는 사실을 알려주는 신호도 없고, 고친 내용을 복사본들에 다시 퍼뜨릴 방법도
없습니다. 이 저장소는 그 복사를 참조로 바꾸기 위해 존재합니다.

## 핵심 원칙

**여기에 있는 것은 다른 저장소가 가리키는 대상입니다.** 사람이 파일을 복사해 가는
방식은 지원하지 않습니다. 모든 산출물은 도구가 스스로 해석할 수 있는 참조
경로를 가집니다.

```jsonc
// tsconfig.json
{ "extends": "@skkil/tsconfig/next" }
```

```yaml
# .github/workflows/ci.yml
jobs:
  build:
    uses: skkil/shared/.github/workflows/java-ci.yml@v1
```

```hcl
module "vpc" {
  source = "git::https://github.com/skkil/shared.git//modules/vpc?ref=v1"
}
```

### 예외: `templates/`

GitHub는 `.github/pull_request_template.md`, `ISSUE_TEMPLATE/`,
`copilot-instructions.md` 같은 파일에 대해 다른 저장소를 참조하는 방법을
제공하지 않습니다. 조직 전체에 적용되는 `.github` 특수 저장소를 쓰는 방법도
있지만, 이 조직은 그 방식을 택하지 않았습니다.

그래서 `templates/`만은 예외적으로 복사를 지원합니다. `skkil templates
install`([`skkil`](https://github.com/skkil/skkil))이 이 저장소를 얕게
clone하여 `skkil.yml`의 `templates.files`에 선언된 파일을 그대로 복사해
옵니다. 복사된 파일은 그 순간부터 가져간 저장소의 소유이며, 버전 고정도
재동기화도 없습니다 — 시간이 지나며 갈라지는 것이 의도된 동작입니다. 이
저장소의 다른 모든 산출물과 정반대이기 때문에, 적용 범위를 `.github/workflows/`
처럼 참조 메커니즘이 이미 있는 파일로 넓히지 않습니다. 자세한 기준은
[`AGENTS.md`](AGENTS.md)의 "The `templates/` exception"을 참고하세요.

## 에이전트 스킬

`skills/`의 스킬은 Claude Code 플러그인으로 배포됩니다. 이 저장소 전체가
플러그인 하나(`skkil`)이자 그 플러그인의 마켓플레이스(`skkil`)이며, 설치 ID는
`skkil@skkil`입니다. 마켓플레이스가 이 저장소를 가리키는 참조 메커니즘이므로
"복사하지 않고 참조한다"는 원칙을 그대로 따릅니다.

### 제공하는 스킬

| 스킬 | 호출 | 설명 |
| --- | --- | --- |
| `rebecca` | `/skkil:rebecca` | 리드 디자이너. 제품 이해, UI/UX, 브랜드, 모션, 에셋 생성, 디자인 리뷰 |
| `jennifer` | `/skkil:jennifer` | 기획자(PM). 무엇을 만들지 결정, 아이디어, PRD · 기획서, 피드백을 이슈로 정리, 리서치 |
| `vanessa` | `/skkil:vanessa` | 작가. 기술 문서, UX 라이팅, 카피, 한국어·영어 문서 |

플러그인 스킬의 정식 호출은 `/skkil:<스킬>`입니다. Claude Code 2.1.280에서는
이름이 겹치지 않으면 `/rebecca`처럼 접두어 없이도 호출됩니다. 다만 이 동작은
버전마다 달랐으므로 문서와 스크립트에는 `/skkil:<스킬>`을 씁니다.

### 설치

[`skkil`](https://github.com/skkil/skkil) CLI로 설치합니다.

```bash
skkil skills install    # 마켓플레이스 등록 + 플러그인 설치. 다시 실행해도 변화 없음
skkil skills doctor     # 설치 상태와 문제 해결 방법 확인
```

`skkil` 없이 직접 설치할 수도 있습니다. Claude Code 세션 안에서는 다음과 같이
실행합니다.

```text
/plugin marketplace add skkil/shared
/plugin install skkil@skkil
```

터미널에서는 다음 명령어를 씁니다.

```bash
claude plugin marketplace add skkil/shared
claude plugin install skkil@skkil
```

### 프로젝트 단위로 켜기

저장소에 아래 설정을 커밋하면, 그 폴더를 신뢰(trust)한 팀원에게 플러그인이
설치됩니다. `skkil skills enable`이 기존 키를 보존하며 이 내용을 병합해 줍니다.

```json
// .claude/settings.json
{
  "extraKnownMarketplaces": {
    "skkil": {
      "source": { "source": "github", "repo": "skkil/shared" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "skkil@skkil": true
  }
}
```

### 업데이트 방식

- 버전은 `.claude-plugin/plugin.json`의 `version` 하나로만 관리합니다. Claude
  Code는 이 값이 바뀔 때만 업데이트로 인식하므로, `templates/`만 바뀐 커밋은
  업데이트를 일으키지 않습니다.
- Anthropic 공식 마켓플레이스가 아닌 마켓플레이스는 **자동 업데이트가 기본으로
  꺼져** 있습니다. `/plugin` → Marketplaces → `skkil` → Enable auto-update로
  켭니다. 위의 프로젝트 설정을 쓰는 저장소에서는 `"autoUpdate": true`로 켜집니다.
- 수동으로는 `skkil skills update` 또는 `/plugin marketplace update skkil`을
  실행합니다. 새 버전은 Claude Code를 다시 시작하면 적용됩니다.

### claude.ai에서 쓰기

`skills-v<버전>` 태그마다 GitHub Release에 스킬별 `<스킬>-<버전>.skill` 파일이
올라갑니다. 이 파일을 claude.ai의 스킬 설정에서 업로드합니다. 직접 만들려면
`skkil skills pack --all`을 실행합니다.

### 다른 에이전트

마켓플레이스 기능이 없는 에이전트에는 `skkil`이 스킬 폴더를 복사하고
`.skkil-skill.json`으로 버전과 파일 해시를 기록합니다.

```bash
skkil skills install --agent cursor                    # ~/.cursor/skills
skkil skills install --agent copilot --scope project   # .github/skills
skkil skills update --agent cursor
```

| `--agent` | 프로젝트 폴더 | 사용자 폴더 |
| --- | --- | --- |
| `cursor` | `.cursor/skills/` | `~/.cursor/skills/` |
| `copilot` | `.github/skills/` | `~/.copilot/skills/` |
| `windsurf` | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| `opencode` | `.opencode/skills/` | `~/.config/opencode/skills/` |
| `codex` | `.agents/skills/` | `~/.agents/skills/` |
| `agents` (Amp, goose, Zed 등) | `.agents/skills/` | `~/.agents/skills/` |

Cursor, Copilot, OpenCode, Amp는 `.agents/skills/`와 `~/.claude/skills/`도
읽습니다. 같은 스킬을 한 에이전트가 읽는 폴더 두 곳에 설치하지 마세요.
[`npx skills add skkil/shared`](https://github.com/vercel-labs/skills)도 이
구조를 인식합니다(로컬 체크아웃으로 `rebecca`만 발견되는 것을 확인했습니다).
다만 이 방식은 마커를 남기지 않으므로 `skkil skills update`로 관리되지 않습니다.

### 문제 해결

- **이름 충돌**: `~/.claude/skills/`나 프로젝트의 `.claude/skills/`에 같은
  이름의 스킬이 있으면 그쪽이 플러그인보다 우선합니다. `skkil skills doctor`가
  찾아 줍니다. 복사본을 지우고 `/skkil:<스킬>`을 쓰세요.
- **업데이트가 안 들어올 때**: 자동 업데이트가 켜져 있는지 확인하고
  `skkil skills update`를 실행한 뒤 Claude Code를 다시 시작합니다.
- **저장소가 비공개로 바뀐 경우**: 각 사용자에게 읽기 권한이 필요합니다. Claude
  Code는 저장된 자격 증명으로 clone하며 프롬프트를 띄우지 않으므로,
  `gh auth setup-git`이나 ssh-agent에 등록된 SSH 키로
  `git ls-remote https://github.com/skkil/shared.git`이 프롬프트 없이 성공해야
  합니다.
- **조직 전체 배포(관리자)**: Claude Team · Enterprise의 Owner가 서버 관리
  설정이나 claude.ai 조직 설정 > Plugins & skills에서 이 마켓플레이스를 모든
  구성원에게 지정할 수 있습니다. 이 저장소는 그 설정을 바꾸지 않습니다.

스킬을 추가하거나 고치는 방법은 [`skills/README.md`](skills/README.md)를
참고하세요.

## `skkil` CLI와의 관계

[`skkil`](https://github.com/skkil/skkil)은 조직 공통 개발 도구이고, 이 저장소는
그 도구가 다루는 설정입니다. 역할이 겹치지 않도록 경계를 명확히 둡니다.

|          | `skkil`               | `shared`                  |
| -------- | --------------------- | ------------------------- |
| 역할     | 실행 (control plane)  | 선언 (data plane)         |
| 담는 것  | 동작하는 명령         | 참조되는 파일             |
| 배포 형태 | 버전이 찍힌 Go 바이너리 | 태그로 고정되는 파일     |
| 저장소별 입력 | `skkil.yml`      | 버전 핀                   |

동작하는 스크립트는 `skkil`에, 선언적인 설정은 `shared`에 둡니다.

## 현재 상태

이 저장소에는 `README.md`, `AGENTS.md`, `CLAUDE.md`, `templates/`, 그리고
Claude Code 플러그인으로 배포되는 `skills/`(`.claude-plugin/`, 스킬 전용
워크플로 `skills-ci.yml` · `skills-release.yml`)가 있습니다. 그 외의 배포
패키지나 재사용 워크플로는 아직 없습니다.

참조로 소비되는 인프라 중 가장 먼저 들어올 것은 실제로 두 곳 이상에서 쓰이는
항목이며, 합의된 시작점은 린트·포매터 설정입니다. `templates/`는 이 기준에서
예외입니다.

## 무엇을 넣을지 판단하는 기준

새로운 항목을 추가하기 전에 두 가지를 확인합니다.

1. **어떤 저장소가 이것을 무시하면 무엇이 깨지는가?**
   "아무것도 깨지지 않는다"면 그것은 인프라가 아니라 문서입니다. 문서도 이곳에
   둘 수 있지만, 문서로 분류하고 공용 인프라로 세지 않습니다.

2. **소비하는 쪽은 이것을 어떻게 가져오는가?**
   `extends`, `uses`, `source`처럼 도구가 해석하는 경로가 있어야 합니다. 해당
   경로가 없다면 아직 이 저장소에 들어올 준비가 되지 않은 것입니다.

판단 기준과 그 배경은 [`AGENTS.md`](AGENTS.md)에 자세히 정리되어 있습니다.

## 버전 정책

**태그로 릴리스하고, 사용하는 쪽은 태그를 고정합니다. `@main`은 사용하지
않습니다.** `templates/`는 설계상 유일한 예외입니다 — 위 "예외: `templates/`"
참고.

`@main`을 참조하면 이 저장소에 푸시가 일어날 때마다 모든 하위 저장소의 빌드가
동시에 바뀝니다. 이 저장소가 없애려고 했던 결합이 그대로 되살아납니다.

영향 범위에 따라 적용 방식이 달라집니다.

- 린트·포매터 규칙 — 잘못되어도 PR 하나가 번거로워지는 정도입니다.
- CI 워크플로 — 잘못되면 조직의 모든 빌드가 한 번에 멈춥니다.
- 배포 경로에 닿는 항목 — 잘못되면 모든 배포가 한 번에 멈칩니다. **저장소를
  하나씩 옮깁니다.** 한 저장소가 새 태그로 올라가 실제 배포를 몇 번 수행한
  뒤에 다음 저장소를 옮기며, 한 PR에서 동시에 바꾸지 않습니다.

## 사용하는 저장소

| 저장소                                          | 스택                            |
| ----------------------------------------------- | ------------------------------- |
| [`skkil`](https://github.com/skkil/skkil)       | Go 1.26, cobra, GoReleaser      |
| [`sync`](https://github.com/skkil/sync)         | Java 25 · Spring, Next.js, pnpm |
| [`tabs`](https://github.com/skkil/tabs)         | Java 26 · Spring, Flutter       |

새 항목을 추가하는 PR은 그것을 사용할 저장소를 함께 밝힙니다. 사용하는 곳이 없는
설정은 추가하지 않습니다. `templates/`의 PR 템플릿, 이슈 템플릿, Copilot
instructions는 이미 이것들을 갖고 있던 `sync`의 `.github/`를 일반화한 것이고,
`.github/`가 아직 없는 `tabs`와 `clip`이 다음으로 가져갈 대상입니다.

## 기여

- 커밋 메시지, PR 설명, 리뷰는 **한국어**로 작성합니다.
- `AGENTS.md`와 `docs/` 아래 문서는 **영어**로 작성합니다.
- 주석은 작성하지 않습니다. 설명이 필요한 결정은 주석이 아니라 `docs/adr/`의
  기록으로 남깁니다.
- 공개된 규약의 형태가 바뀔 때는 기존 버전을 수정하지 않고 새 버전을 나란히
  추가합니다.
