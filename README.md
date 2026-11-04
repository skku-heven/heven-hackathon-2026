# heven-common

HEVEN 팀의 private GitHub repository template이다. 새 저장소를 만든 뒤 프로젝트에 맞는 README와 빌드·테스트 CI를 작성한다.

## 스킬

| 스킬 | 용도 |
|---|---|
| [bootstrap-repo](.claude/skills/bootstrap-repo/SKILL.md) | 새 저장소의 GitHub·Project·연동 설정 |
| [idea-to-requirements](.claude/skills/idea-to-requirements/SKILL.md) | 질문을 통해 요구사항을 구체화하고 StrictDoc에 기록 |
| [requirements-to-issues](.claude/skills/requirements-to-issues/SKILL.md) | 요구사항을 검증 가능한 이슈로 나누고 의존관계 정리 |
| [issue-worker](.claude/skills/issue-worker/SKILL.md) | Ready 이슈의 브랜치·Draft PR 생성 또는 기존 PR 재사용 |
| [handoff](.claude/skills/handoff/SKILL.md) | 다음 세션을 위한 인수인계 문서 작성 |
| [teach](.claude/skills/teach/SKILL.md) | 학습 목표·수업·학습 기록 관리 |
| [process-improvement](.claude/skills/process-improvement/SKILL.md) | 회고를 통해 공통 프로세스 개선 제안 — 미완성 초안 |

`bootstrap-repo` → `idea-to-requirements` → `requirements-to-issues` → `issue-worker` 순서로 진행한다. `handoff`와 `teach`는 명시적으로 요청해 사용한다. `handoff`는 OS 임시 디렉터리에, `teach`는 실행한 디렉터리에 결과를 저장한다.

## 시작하기

1. **Use this template**로 `skku-heven/<new-repo>` private 저장소를 만든다.
2. 저장소를 clone하고 Codex 또는 Claude Code에 요청한다.

> 이 repo의 bootstrap-repo skill을 사용해서 skku-heven/<new-repo>를 부트스트랩해줘.

스킬은 목적과 선택 기능을 확인하고 `dev`·`main`, 기본 브랜치, Wiki OFF, merge 후 브랜치 자동 삭제, label, Roadmap을 설정한다. Project #14를 복사하거나 기존 Roadmap을 재사용한다. Project 복사·연결에는 CLI의 Project 쓰기 권한이 필요하다.

상태 전환에는 self-hosted runner, `PROJECT_PAT` secret(project + repo 권한), `RUNNER_SCRIPTS` variable이 필요하다. bootstrap에서 설정·배포를 확인한다. 비밀값은 채팅이나 문서에 적지 않는다. 직접 스크립트를 실행할 때의 입력 조건은 [bootstrap 스킬](.claude/skills/bootstrap-repo/SKILL.md)을 따른다.

## 선택 기능

| 기능 | ON | OFF |
|---|---|---|
| StrictDoc | 선택한 요구사항 계층·문법 검사·Issue/PR UID 연결 | 관련 설치·검사·동기화 건너뛰기 |
| 저장소 전용 Notion | 전용 hub와 Project Info 생성·사용 | 저장소 문서 사용 |
| Discord 알림 | PR 등 이벤트 알림 | 알림 없음 |
| Codex 자동 PR 리뷰 | Ready PR을 Codex로 리뷰 (runner의 Codex CLI 인증·배포 필요) | 자동 리뷰 없음 |
| Discord 멘션 | 알림에서 사용자 멘션 (알림 ON 필요) | 멘션 없음 |

선택은 [docs/workflow.md](docs/workflow.md)에 기록한다. OFF는 관련 실행을 끄는 것이며 파일을 삭제하지 않는다. **공통 Notion 가이드 링크는 저장소 전용 Notion 선택과 무관하게 유지한다.**

- 이 repository의 Notion hub: `<NOTION_REPO_URL>`

`agent-proposed` 이슈의 자동 stale/close는 기본 OFF다. 필요한 저장소에서만 `ENABLE_STALE_AUTOMATION=true`를 설정한다. ON이면 7일 무활동 후 경고, 추가 7일 후 종료한다. Codex 자동 리뷰는 `ENABLE_CODEX_REVIEW=true/false`로 제어하며 기본 OFF다. Project 상태 전환과는 독립적이다.

## bootstrap 이후

- Roadmap의 Auto-add workflow에 이 저장소를 선택하고 `is:issue is:open` 필터를 설정한다. 추가된 이슈는 Backlog로 이동한다.
- 실제 setup/build/run/test에 맞게 README와 CI를 작성한다. 파생 저장소에서는 프로젝트에 맞는 빌드·테스트 job을 구성한다.
- 상태 전환 Actions와 runner 연결을 확인한다. PR은 기본 브랜치 `dev`를 대상으로 만들고 `Resolves #번호`로 이슈를 연결한다.

## 작업 흐름

이슈는 `Backlog → Ready → In progress → In review → Done`으로 관리한다. Ready 이슈를 `issue-worker`로 시작하고 Draft PR에서 작업한다. 검증 후 Ready for review로 전환하여 리뷰를 요청한다. PR 상태에 따라 연결된 이슈의 Project 상태가 동기화된다.

## 운영 자동화

`ops/runner/`는 운영 스크립트·프롬프트·배포 설정을 관리한다.

| 구성 | 역할 |
|---|---|
| `agent-tick` | 개발 문맥을 검토하고 이슈 제안 생성 |
| `systemd/` | 이슈 제안 생성기의 정기 실행 |
| `codex-pr-review.sh` | Codex PR 리뷰 |
| `pr-set-in-review.sh` | PR과 연결된 이슈의 Project 상태 동기화 |

이슈 제안 생성기는 별도 배포·타이머 설정으로 운영한다. runner 환경과 배포 절차는 [운영 문서](ops/runner/README.md)를 따른다.

## StrictDoc

`heven.toml`에서 ON/OFF와 계층을 선택한다. 기본 OFF이며, 참가자 배포 저장소처럼 요구사항 정본이 필요 없는 곳에서는 OFF로 유지한다.

```bash
make requirements-init   # ON인 경우 없는 템플릿만 생성
make requirements-check  # 문법·UID·관계 검사와 HTML 생성
make serve              # http://127.0.0.1:5111/, 종료 Ctrl+C
make docs               # HTML 내보내기
make requirements-sync  # Issue → PR UID 동기화 미리보기
```

uv와 make가 필요하다(Windows: WSL). uv는 도구용 Python 3.11을 준비하며 프로젝트의 Python/ROS 환경과 분리한다. StrictDoc 0.30.4는 ON일 때만 `build/requirements-venv/`에 설치한다. 서버 포트는 `make serve PORT=5112`로 바꾼다.

[요구사항 설정·Issue/PR 연결](docs/requirements-workflow.md)을 따른다. 검증 결과는 Actions에 표시하지만 필수 merge check로 자동 지정하지 않는다.

## 검증과 문서

공통 저장소 CI는 템플릿 구조·셸 문법과 bootstrap·issue-worker·상태 전환의 동작 테스트를 실행한다. gtest·CTest 등 프로젝트 테스트는 각 저장소에서 추가한다.

- [에이전트 규칙](AGENTS.md) · [요구사항 작업 흐름](docs/workflow.md) · [runner 운영](ops/runner/README.md)
- [공통 Notion 가이드](https://app.notion.com/p/39c3bf068300807c9e5bcf6b469f94ee) · [repo wiki](https://app.notion.com/p/39c3bf06830080b5a024c7ad91855240)
- [Getting Started](https://app.notion.com/p/39c3bf06830081fb8e76d5c9a1be6d82) · [Team Workflow](https://app.notion.com/p/39c3bf068300810db8adc15fce65450d) · [Operations](https://app.notion.com/p/39c3bf068300815fb880e1d20602e662)
