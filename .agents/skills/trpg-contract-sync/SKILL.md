---
name: trpg-contract-sync
description: Synchronize TRPG architecture, cross-repository interfaces, implementation status and review evidence.
---

# Contract synchronization

Read AGENTS.md, `docs/MODULE_CONTRACTS.md`, scope/domain docs and
`docs/CODE_DOCUMENTATION.md` from this repository root (three directories above
this skill). Locate SM/RE siblings against the logical parallel workspace. Report
inaccessible sources; do not treat branch labels or historical reports as current code.

Record each repository's cwd, remote, branch, exact HEAD, fetched main and dirty state.
Inspect actual source/tests, public interfaces, dependency pins and relevant acceptance/
Progress. Distinguish target architecture, verified current implementation, dated history
and unverified inference. Reconcile DOC/domain/Progress/interface/binding differences;
keep architecture decision, implementation and acceptance statuses separate.

Decide whether each repository really needs edits. Preserve dated evidence and scope;
add current findings rather than silently rewriting old results. Check obsolete paths,
links/anchors and cross-worktree instructions. Reference authority sections instead of
copying a second contract. Documentation synchronization never authorizes business logic,
schema/dependency changes, main merges or writes to an unrequested repository.

Validate changed Markdown and applicable strict docs builds. For source explanations,
use the code-documentation workflow installed in each implementation workspace; do not
assume sibling skills are automatically discovered. Deliver baselines/branches, findings,
exact checks and evidence limits, scoped commits/pushes only when authorized by the task.

For structural, ownership or cross-repository interface changes, start from each
affected repository's `docs/SYSTEM_OVERVIEW.md`, then the relevant contracts/source.
Include the corresponding overviews and their navigation in synchronization checks;
keep them concise navigation, not a second authority or a complete call graph.
