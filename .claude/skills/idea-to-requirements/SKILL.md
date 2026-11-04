---
name: idea-to-requirements
description: Turn an idea or existing discussion into requirements through a questioning session, recording selected requirement levels in StrictDoc. Use before implementation or when revising requirements.
---

# Idea → Requirements

HEVEN adaptation of `grill-with-docs` and [grill-me](references/grill-me.md) (the latter is an entrypoint for `grilling`): use the interview in [grilling](references/grilling.md) and the terminology/decision work in [domain-modeling](references/domain-modeling.md). Read both before starting. The reference files describe the discipline; execute it here rather than requiring separately installed skills or a particular Skill tool.

## HEVEN integration

Run this skill only when explicitly requested.

1. Read the repo's `docs/workflow.md` settings and existing discussion, requirements, glossary and relevant code. If requirement levels have not been selected, ask which of business, stakeholder, system and software to use. Record that choice once; do not silently add omitted levels.
2. Run the upstream interview: ask the currently answerable questions in numbered rounds with recommendations, investigate facts in the repo, and wait for decisions before dependent questions. Use available tools to investigate; delegation is optional, not a new dependency.
Continue rounds until every decision branch in the agreed scope is resolved and the user confirms shared understanding. Do not stop merely because a first requirements draft exists. If the user pauses or defers a decision, record it as unresolved rather than inventing an answer.

3. Enable the selected profile in `heven.toml` and run `make requirements-init` before writing. A profile change requires reviewing existing files with the user; never overwrite them. Keep the upstream glossary and selective ADR behavior. In addition, write settled requirements into `docs/requirements/*.sdoc` using [the requirements profile](references/requirements-profile.md). Existing UIDs and formats take precedence. Leave unresolved choices explicit; do not invent answers to finish a document.
4. Run `make requirements-check`; inspect `build/requirements-report.json`. Keep all new requirements Draft until explicit review/approval. Show the changed requirements and unresolved choices. Confirm shared understanding as in the upstream interview. This session writes requirements, not product implementation or GitHub issues.

Notion, when enabled, supplies repo context; StrictDoc remains the requirement source of truth. When disabled, use repo files without asking for a Notion connection. Discord and runner behavior stays in the existing workflows.

Next: use `requirements-to-issues` for the reviewed scope. Do not automatically invoke the next stage.
