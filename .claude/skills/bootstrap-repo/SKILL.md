---
name: bootstrap-repo
description: Use when setting up or rerunning bootstrap for a new private repository created from the heven-common template.
---

# bootstrap-repo — 새 private repo 초기 설정

`heven-common`에서 만든 private repo의 GitHub 설정과 선택한 repo 전용 Notion hub을 한 흐름으로
초기화한다. public/internal target은 어떤 mutation도 하기 전에 거부한다.

요청 문구:

> 이 repo의 `bootstrap-repo` skill을 사용해서 `skku-heven/<new-repo>`를 부트스트랩해줘.

정본:

- Canonical Notion parent: [repo wiki](https://app.notion.com/p/39c3bf06830080b5a024c7ad91855240)
- Common Notion guide/template: [공통 가이드](https://app.notion.com/p/39c3bf068300807c9e5bcf6b469f94ee)
- Bootstrap/runner operations: [Operations](https://app.notion.com/p/39c3bf068300815fb880e1d20602e662)

Notion ON인 경우에만 canonical parent인 repo wiki 아래에 repo 전용 문서 hub를 준비한다. 공통 Notion 가이드 링크는 항상 유지한다.

## HEVEN optional integrations

Read docs/workflow.md when present. Ask once for NOTION_MODE (enabled/disabled) along with Discord notifications/mentions and CODEX_REVIEW; reuse explicit prior user choices. Record selections in that file. When requirement levels are already selected, record them there too; otherwise the requirements session selects them later.

- NOTION_MODE=enabled: follow the Notion contract below, including MCP readback. Existing script callers without NOTION_MODE keep enabled behavior for compatibility.
- NOTION_MODE=disabled: skip Notion fetch/create/readback and sections 2–3; do not request credentials or a connection. Replace the repo hub placeholder in README/AGENTS with `사용 안 함 (NOTION_MODE=disabled)` and use an empty default for NOTION_GUIDE_URL in runner context. Leave NOTION_REPO_URL and NOTION_PROJECT_INFO_URL unset. Keep shared Notion guide links as optional references. GitHub bootstrap, Projects and selected Discord configuration and required Project status automation still run normally.
- No mode weakens private/template/admin provenance or Project schema validation. Notion-dependent completion checks apply only when enabled.

## Local StrictDoc

Read `heven.toml`: StrictDoc defaults OFF. Reuse the user's selected requirement levels; when enabled, select the matching profile and run `make requirements-init`. This creates only missing templates, never requirement UIDs or approved content. For a distribution-only repo, keep OFF unless requested otherwise. Record the choice in docs/workflow.md.

Requires uv and make (Windows: WSL). If uv is absent, install it using the official uv installation instructions, then verify `uv --version`; do not pipe an uninspected remote script into a shell. The shared CLI uses isolated Python 3.11, independently of the project's ROS/Python runtime. `make requirements-check`, `make docs` and `make serve` install pinned StrictDoc only when ON. OFF skips successfully. Start the server only when requested. A requested smoke test includes initialization, validation and export in an isolated test repo.

## 1. One-shot bootstrap inputs

Collect target repo, REPO_PURPOSE, and optional Notion/Discord/Codex review modes in one request.

- Notion mode: NOTION_MODE is enabled or disabled
- Target repo: owner/repo
- Repository purpose: exact one-line REPO_PURPOSE
- Discord notifications mode: DISCORD_NOTIFICATIONS is enabled or disabled
- Discord mentions mode: DISCORD_MENTIONS is enabled or disabled
- Codex PR review: CODEX_REVIEW is enabled or disabled; this never disables Project status transitions. The shell defaults omitted CODEX_REVIEW to disabled for existing callers.
- Project status automation is mandatory: collect PROJECT_PAT and RUNNER_SCRIPTS; do not ask for a runner ON/OFF choice.

Explicit opt-outs: ask for every mode; disabled must be selected explicitly and never inferred from silence.
mentions enabled에는 notifications enabled가 필요하다. enabled mode의 조건부 값도 같은
요청에서 식별하고, disabled mode의 조건부 값은 받지 않는다.

After template creation, wait until GitHub reports the template source, the `dev` branch and repository contents before cloning/preflight (generation is asynchronous). Retry read-only checks for up to 60 seconds; if still incomplete, report pending generation rather than changing the default branch or weakening provenance checks.

### Target provenance preflight

Target REST metadata must prove private visibility, default dev, admin access, and template_repository.full_name skku-heven/heven-common.
Provenance preflight completes before any Notion mutation.

Notion page를 만들거나 재사용하기 전에 repo root에서 다음 read-only preflight를 실행한다.
이 mode는 target과 `gh` 인증만 사용하며 bootstrap input, secret, Notion URL을 요구하지 않는다.

```bash
.claude/skills/bootstrap-repo/scripts/bootstrap-repo.sh --preflight-only skku-heven/<new-repo>
```

read-only preflight가 하나라도 다르면 secret을 요청하거나 Notion/GitHub를 mutation하지
않고 종료한다.

### Authentication and runner preparation

Check existing authentication before requesting a new token. The CLI's `gh project` commands may need `read:org` for organization lookup as well as `project`; the Actions `PROJECT_PAT` needs `project` and access to the target private repo (`repo` for a classic PAT). Reuse an appropriate existing token; a new token per repository is not required. Report the actual failing command and error rather than treating every failure as missing Project permission.

Before installing a runner, inspect both GitHub registration/access and the chosen host's service/process/install paths. Reuse a suitable existing runner. Organization runners may require additional organization administration permission; repository runners are another option. Follow the available permissions and project setup instead of assuming one deployment model.

### Enabled secret injection

Only DISCORD_WEBHOOK and PROJECT_PAT are plaintext secrets.
Request missing conditional values only through secure environment/secret input, never plaintext chat/docs.
Ask the user to inject only DISCORD_WEBHOOK and PROJECT_PAT through host secure env/secret input.
Verify each enabled secret is present without printing its value.
If host secure input is unavailable, stop before mutation.

- notifications enabled: `DISCORD_WEBHOOK` 필요
- Project status automation: `PROJECT_PAT` 필요
- mentions enabled: non-secret `DISCORD_USER_MAP` 필요
- Project status automation: non-secret `RUNNER_SCRIPTS` 필요

DISCORD_USER_MAP and RUNNER_SCRIPTS are conditional non-secret values; do not persist their values in durable docs.
환경 주입 뒤에는 값이 set/non-empty인지 조건식으로만 확인하고 echo, command argv,
report에 값을 노출하지 않는다.

Local fallback: provide a read -s same-shell wrapper that invokes bootstrap before unsetting secrets.
host에 secure input 기능이 없으면 agent는 실행을 중단하고, 사용자가 non-secret env를 먼저
export한 로컬 terminal의 같은 shell에서 다음 wrapper를 실행하도록 안내한다.

```bash
bootstrap_with_local_secrets() (
  trap 'unset DISCORD_WEBHOOK PROJECT_PAT' EXIT
  local target="$1" rc=0

  if [[ "${DISCORD_NOTIFICATIONS:-}" == enabled ]]; then
    IFS= read -r -s -p 'Discord webhook: ' DISCORD_WEBHOOK || return
    printf '\n' >&2
    export DISCORD_WEBHOOK
  fi
  IFS= read -r -s -p 'Project PAT: ' PROJECT_PAT || return
  printf '\n' >&2
  export PROJECT_PAT

  [[ "${DISCORD_NOTIFICATIONS:-}" != enabled || -n "${DISCORD_WEBHOOK:-}" ]] || return 1
  [[ -n "${PROJECT_PAT:-}" ]] || return 1

  .claude/skills/bootstrap-repo/scripts/bootstrap-repo.sh "$target" || rc=$?
  return "$rc"
)
bootstrap_with_local_secrets skku-heven/<new-repo>
unset -f bootstrap_with_local_secrets
```

## 2. Notion hub contract

NOTION_MODE=enabled일 때만 Notion MCP로 canonical parent와 common guide/template을 fetch한다. target의 repo 이름만
hub title로 사용하고 canonical parent의 direct child만 열거한다.

For the repo hub exact direct-child title match: 0 -> create, 1 -> reuse, and 2+ -> fail.
부분 일치나 workspace 전체 search 결과로 대신하지 않는다.

선택한 hub 바로 아래의 exact title `Project Info`도 0개면 common template에서 만들고,
1개면 덮어쓰지 않고 재사용하며, 2개 이상이면 중단한다.
Create or reuse Project Info from the common template and read it back.

## Repository metadata

hub에는 다음 canonical serialization을 가진 section을 정확히 하나만 둔다.

- GitHub: https://github.com/<owner>/<repo>
- Purpose: <exact REPO_PURPOSE>
- Common guide: https://app.notion.com/p/39c3bf068300807c9e5bcf6b469f94ee
- Project Info: <exact direct-child Project Info URL>

GitHub 값은 target에서 파생하고 Purpose 값은 입력받은 `REPO_PURPOSE`와 정확히 같아야
한다. Project Info에는 앞에서 read back한 direct child URL만 기록한다.

### Reuse and readback

The hub must contain exactly one ## Repository metadata section with exactly one canonical GitHub, Purpose, Common guide, and Project Info bullet.
Repository metadata section count: 0 -> insert this section, 1 -> verify and upsert only missing canonical bullets, and 2+ -> fail.
Preserve all unrelated hub content on reuse.
Upsert only missing canonical metadata bullets.
Fail closed on conflicting or ambiguous existing metadata.
Duplicate canonical metadata labels or values conflicting with expected values fail.

section이 없으면 위 heading과 네 bullet을 삽입한다. 하나면 각 label을 exact match로
parse해 없는 bullet만 추가한다. 같은 label이 여러 번 나오거나 기대값과 다른 값이면
overwrite하지 않고 중단한다. 다른 section, block, child, 사람 문서는 삭제·재배열하지 않는다.

Readback parses only the exact ## Repository metadata section and verifies all four canonical bullets plus exact parent, title, hub page ID, and Project Info page ID before NOTION_REPO_URL is used.
readback은 exact section의 네 값, hub의 canonical parent와 repo title, hub/Project Info의
서로 다른 page ID, Project Info의 exact title과 direct-parent 관계를 모두 확인한다. 모두
통과한 뒤에만 선택한 hub URL을 `NOTION_REPO_URL`, child URL을
`NOTION_PROJECT_INFO_URL`로 사용한다.

Trust boundary: Notion MCP readback is authoritative for the repo hub parent/title and Project Info direct-child relationship.
The shell script does not read Notion; it validates only canonical URL form, distinct page IDs, common-page exclusion, and versioned placement.
따라서 MCP readback을 완료할 수 없으면 direct script 실행도 허용하지 않는다.

Only Notion-dependent work blocks when MCP is unavailable; normal code, CI, and runner work continues.
MCP가 없거나 create/reuse/readback이 실패하면 curl/browser scraping으로 우회하지 않고
이 bootstrap만 GitHub mutation 전에 중단한다.

## 3. Versioned repo hub URL

Only the repo hub URL is versioned in README, AGENTS, and runner context.
The Project Info URL must differ from the repo hub URL and is verified only as its direct child; never version it in those three files.
Write NOTION_REPO_URL into README.md, AGENTS.md, and ops/runner/repo-context.sh before invoking the script.
README 링크에는 검증된 repo hub URL만 기록한다.

세 파일의 `<NOTION_REPO_URL>` placeholder만 exact hub URL로 교체하고 read back한다.
세 값은 hub URL과 같아야 하며 Project Info URL과는 달라야 한다. 공통 URL은 보존한다.

## 4. GitHub 설정

목적·선택 설정과 필수 PROJECT_PAT·RUNNER_SCRIPTS를 같은 environment에 준비하고 실행한다. Notion ON일 때만 검증된 NOTION_REPO_URL·NOTION_PROJECT_INFO_URL을 추가한다. 스크립트는 ON인 경우 두 URL과 문서의 hub 필드를 다시 확인한다.

```bash
.claude/skills/bootstrap-repo/scripts/bootstrap-repo.sh skku-heven/<new-repo>
```

script는 입력과 provenance를 다시 fail-closed 검증하고 다음을 멱등 적용한다.

- `main` branch 생성, default `dev`, Wiki off, merge 후 branch 삭제
- squash option 활성화; 기존 merge/rebase 허용 여부는 변경하지 않음
- `agent-proposed`, `agent-stale`, `agent-keep` labels
- enabled 기능의 repo secrets/variables와 Discord mode gate variables
- org Project #14 `[TEMPLATE] heven-common`의 identity와 Project #14 자체의 정확한 5개 Status와 필수 enabled non-Auto-add workflow 검증
- `<repo> Roadmap`이 없으면 복사하고 복사 직후 같은 schema를 read-back한 뒤 연결;
  정확히 하나면 검증 후 재사용

## 5. 완료 전 확인

1. `<repo> Roadmap`의 Auto-add workflow만 GitHub UI에서 설정한다.
   - filter: `is:issue is:open`
   - status: `Backlog`
   - 나머지 Status/workflow는 Project #14에서 복사된다.
2. Notion ON일 때만 exact `## Repository metadata` section의 네 canonical bullet과 parent/title/IDs를 다시 확인한다.
3. Notion ON일 때만 세 versioned 파일에는 hub URL만 있고 Project Info URL은 없는지 확인한다.
4. README의 이름·목적·시작 안내를 해당 프로젝트에 맞춘다. bootstrap만 요청된 경우 요구사항이나 구현을 만들지 않고, 아직 없는 build/run/test 절차를 추측하지 않는다.
5. 의도한 팀원이 private repo와 Project 모두에 접근 가능한지 확인한다.
6. Runner completion verifies the bootstrap script wrote enabled repo secrets/variables without printing values, then deploys the runner.
   Project 상태 전환을 위해 bootstrap script가 쓴 secret/variable 이름과 존재 여부를 값 출력 없이
   검증한 뒤 `ops/runner/README.md`에 따라 runner를 배포한다. credential을 다시 설정하지 않는다.
   org runner의 public repository access는 항상 차단한다.
   organization plan이 Selected repositories를 지원하면 대상 private repo만 허용한다.
7. 상태 전환은 연결 이슈가 있는 PR로 확인한다. 첫 bootstrap PR도 검증에 쓸 수 있으며, Ready로 전환하기 전에 이슈를 연결한다.
8. 결과를 보고하되 secret과 environment-specific conditional 값은 출력하지 않는다.

When Codex review is enabled, verify the runner has an authenticated Codex CLI and deploy `codex-pr-review.sh` with its prompt/context dependencies from `ops/runner/README.md`. OFF only disables review; mandatory Project status automation remains active.
