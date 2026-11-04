# HEVEN requirements profile

ISO/IEC/IEEE 29148-inspired tailoring; not certification or full conformance.
Select `requirements.enabled` and `profile` in `heven.toml`, then run `make requirements-init`.

| Profile | Levels |
|---|---|
| software | SW |
| stakeholder-software | STK → SW |
| system-software | SYS → SW |
| stakeholder-system-software | STK → SYS → SW |
| full | BR → STK → SYS → SW |

Preserve existing UIDs. New prefixes are BR/STK/SYS/SW; STR/SWR remain supported for existing documents. One file per selected level is enough initially. Add domain files only as needed, using that level's grammar. Profile changes require impact review; initialization never replaces an existing file. `.heven-profile` records the initialized profile.

Fields: UID, TITLE, STATEMENT, STATUS; optional RATIONALE, COMMENT and Parent relations. SW also requires CATEGORY: `Functional`, `Non-functional/Performance Efficiency` or `Non-functional/Other`. STK has no CATEGORY.

STATUS: Draft, In Review, Approved, Retired. New content is Draft. Only explicit approval changes status. Retired requires a reason in COMMENT. Draft may have incomplete parent coverage; all referenced parents must exist. Approved requirements need a parent at the nearest selected upper level, and approved upper-level requirements need child coverage. Software-only needs no artificial parents.

Write one testable obligation per statement; use units/conditions where relevant. Keep shared equations and interface contracts in referenced model/ICD documents. RATIONALE explains the current need; COMMENT holds review/TBD notes. A planned test is not a passed test. Keep unresolved decisions explicit.

`make requirements-check` validates grammar, UIDs, states, categories and relations, and exports HTML with pinned StrictDoc. Diagnostics also appear in `build/requirements-report.json`. `make serve` starts the local editor. ALL_FEATURES is enabled in the generated configuration; it does not guarantee Markdown/LaTeX rendering.

Issues own requirement links in the managed block described in `docs/requirements-workflow.md`; do not write reverse Issue links into requirement COMMENT fields. Glossary and selective ADRs retain their separate purposes.
