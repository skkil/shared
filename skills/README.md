# skills

조직 공통 에이전트 스킬입니다. 이 폴더의 각 하위 폴더가 스킬 하나이며, 저장소
전체가 Claude Code 플러그인 `skkil@skkil`로 배포됩니다. 설치 방법은 저장소
[README](../README.md#에이전트-스킬)를 참고하세요.

## 스킬 추가하기

`shared` 체크아웃 안에서 실행합니다.

```bash
skkil skills new design-review --description "디자인 리뷰. 화면이나 시안을 평가할 때 사용한다."
```

`templates/skill/`을 복사해 `skills/design-review/`를 만들고 frontmatter를
채웁니다. 이어서 `SKILL.md` 본문을 작성하고, 아래 버전 규칙에 따라
`.claude-plugin/plugin.json`의 `version`을 올리고 `CHANGELOG.md`에 항목을
추가합니다.

## Frontmatter 규칙

- `name`: 소문자, 숫자, 하이픈만 사용하며 64자 이하입니다. **폴더 이름과
  같아야** 합니다.
- `description`: 비어 있으면 안 되고 1024자 이하입니다. 무엇을 하는지와 언제
  쓰는지를 함께 적습니다. Claude는 이 문장을 보고 스킬을 고릅니다.
- 값에 `: `(콜론 + 공백)이 들어가면 **반드시 따옴표로 감쌉니다.** 따옴표가 없으면
  YAML 파싱이 깨집니다.
- 허용 키: `name`, `description`, `license`, `allowed-tools`, `metadata`,
  `compatibility`, 그리고 Claude Code 전용 키(`disable-model-invocation`,
  `user-invocable`, `model`, `argument-hint` 등). 그 밖의 키는 경고가 납니다.

## 비밀 값

API 키를 저장소에 넣지 않습니다. 스크립트는 각 사용자 머신의 gitignore된 env
파일(예: `.env.design`)이나 환경 변수에서 키를 읽습니다. `skkil skills validate`와
CI의 gitleaks가 키처럼 보이는 값과 `.env` 파일을 막습니다.

## 스크립트

- `scripts/`의 각 스크립트는 `--help`에 0으로 종료해야 합니다. CI가 확인합니다.
- 필요한 패키지는 스킬 폴더의 `requirements.txt`에 적습니다. CI는
  `.github/skills-ci-requirements.txt`의 공통 패키지와 함께 설치합니다.
- 테스트가 있으면 스킬 폴더의 `tests/`에 둡니다. CI가 pytest로 실행합니다.
- 루트의 `evals/` 폴더, `__pycache__/`, `node_modules/`, `*.pyc`, `.DS_Store`는
  `.skill` 패키지에서 제외됩니다.

## 검증

```bash
skkil skills validate --all                     # 모든 스킬과 매니페스트
skkil skills validate --all --against origin/main  # 버전 · CHANGELOG 확인까지
claude plugin validate . --strict               # Claude Code 자체 검증
```

## 버전 규칙

버전은 `.claude-plugin/plugin.json`의 `version` 하나뿐입니다(marketplace.json에는
적지 않습니다). `skills/<스킬>/`이나 `.claude-plugin/`을 바꾸는 PR은 반드시 버전을
올리고 `CHANGELOG.md`에 항목을 추가해야 하며, CI가 이를 확인합니다.

| 변경 | 올릴 자리 |
| --- | --- |
| 버그 수정, 문구 · 설명 수정 | patch (`0.1.0` → `0.1.1`) |
| 새 스킬, 새 기능 | minor (`0.1.1` → `0.2.0`) |
| 스킬 삭제 · 이름 변경, 스크립트 인터페이스 호환성 깨짐 | major (`0.2.0` → `1.0.0`) |

릴리스는 `skills-v<버전>` 태그를 푸시하면 `skills-release.yml`이 스킬별
`.skill` 파일을 만들어 GitHub Release에 올립니다.
