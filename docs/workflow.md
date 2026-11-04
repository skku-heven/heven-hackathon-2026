# HEVEN skill workflow

`bootstrap-repo` → `idea-to-requirements` → `requirements-to-issues` → `issue-worker`

- Bootstrap: configure GitHub and required Project status automation; choose repo Notion/Discord settings for the derived repo.
- Idea to requirements: upstream grilling + domain modeling, with StrictDoc output.
- Requirements to issues: upstream to-tickets, including dependency ordering, adapted to our Project.
- Issue worker: existing Ready issue → branch → draft PR → implementation/verification workflow.

## Per-repository choices

A derived repo records its choices here during bootstrap or first requirements session:

- StrictDoc: OFF by default; `heven.toml` is the machine-readable source.
- Requirement levels: select a profile when enabling StrictDoc; see [requirements workflow](requirements-workflow.md).
- Requirement source: docs/requirements/*.sdoc (StrictDoc).
- Issue tracker: this repository's GitHub Issues and linked Project.
- Repository Notion hub: not selected (enabled / disabled).
- Discord notifications / mentions: not selected (enabled / disabled, separately).
- Codex PR review: not selected (enabled / disabled; defaults to disabled for direct script callers).
- Project status automation: required (self-hosted runner + PROJECT_PAT + RUNNER_SCRIPTS).
- Common Notion guides: retained regardless of repository hub choice.

Do not infer disabled from an unanswered choice. Existing explicit user choices carry forward.
For example, a software-focused project can select stakeholder + software and disable the optional integrations. Record actual choices in each derived repository; this example is not a team-wide default. A participant distribution repo need not duplicate the development requirements.

## Boundaries

The source skills are pinned in THIRD_PARTY_NOTICES.md. The HEVEN additions are limited to selected requirement levels/StrictDoc output and the existing GitHub/integration contracts.
ISO/IEC/IEEE 29148 inspires requirement organization; selecting levels is project tailoring, not a claim of full standards conformance.
`to-spec` is not a separate stage: StrictDoc is the specification. `triage` is not installed: its labels/state machine would duplicate our Project. `to-tickets` already declares blockers.

Use `handoff` explicitly when moving to another session/agent. It is independent of the development stages and writes to the OS temporary directory, not this repository.

Use `teach` explicitly for guided learning in a chosen teaching directory. `process-improvement` is a [usable, incomplete draft](../.claude/skills/process-improvement/SKILL.md), primarily informed by Atlassian retrospectives, for questioning and shared improvements to heven-common.
