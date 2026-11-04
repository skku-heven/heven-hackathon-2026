---
name: requirements-to-issues
description: Split reviewed requirements into GitHub implementation issues with acceptance criteria and blocking dependencies, ready for the HEVEN issue-worker workflow.
---

# Requirements → Issues

Read [upstream to-tickets](references/to-tickets.md) and follow its slicing, dependency analysis and breakdown review. The following are the HEVEN substitutions; do not introduce another tracker or triage state machine.

1. Read `docs/workflow.md`, the selected StrictDoc requirements, existing issues and Project state. Use requirement UIDs as references; the issue is an implementation task, not a replacement specification. If a required choice is unresolved, return that question to `idea-to-requirements` instead of guessing it.
2. Draft independently verifiable vertical slices and their genuine blocking edges, as upstream does. Check existing issues before proposing duplicates. Show title, requirement IDs, outcome, acceptance criteria and blockers for each proposed issue. Review the breakdown with the user as upstream requests.
3. When StrictDoc is ON, run `make requirements-check` and use the managed UID block in `docs/requirements-workflow.md`. Zero UIDs are allowed; unknown UIDs are errors. Issue bodies own the links; do not add reverse Issue references to requirement COMMENT fields. Publish the approved breakdown to this repo's GitHub Issues, blockers first. Use the repo's existing Issue Type/template. Each issue links the exact requirements document revision and UIDs, and names its verification outcome. Prefer native blocking relationships where available; otherwise retain a readable `Blocked by: #...` list. Reject circular dependencies.
4. Use the existing Project: Backlog → Ready → In progress → In review → Done. Do not create upstream `ready-for-agent` or triage labels. New issues start in Backlog under the existing project workflow; identify which have no unfinished blockers. Move them to Ready only when the user authorizes that transition. Preserve existing parent issue state.
5. Verify the created Issue bodies and run `make requirements-sync` (dry-run). PR UID blocks are synchronized by the trusted-base workflow after linking with `Resolves #N`; closed Issue links remain valid. Hand off one Ready issue number to `issue-worker`. That skill owns branch/draft-PR claiming. Do not create branches or PRs here.

Dependencies are already part of `to-tickets`; no separate sequencing skill is required. Requirements, UIDs and verification links remain in StrictDoc. Optional Notion/Discord integrations use existing repo settings, not additional copies of the specification.
