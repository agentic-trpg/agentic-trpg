<!-- Current entry, 2026-10-27: dated NOT IMPLEMENTED/branch-only notes below
retain their historical scope. Current SM main b9ae704 contains the scoped SessionMemory,
instance-field and passage-index implementation; this prose batch does not close its
remaining recovery/multiplayer limits. Resolve required sibling documents from the
logical parallel workspace. -->

# Documentation maintenance

- Runtime owner fields and local-query/admission rules are authoritative in MC §2.3a. Read that section before changing caches, snapshots, indices or domain consumers. Follow instance associations and existing indices from the target; do not replace local checks with Session/Scene scans. Distinguish actual consumer migration from added fields. Preserve per-mutation SQLite persistence, candidate/savepoint isolation, fixed inputs and all-context recovery invalidation; retain cold loading and bounded retention. Current branch evidence is in `docs/reviews/RUNTIME_INSTANCE_OWNERSHIP.md`.

- `docs/MODULE_CONTRACTS.md` is the highest cross-module architecture, ownership and target-contract authority. `docs/MVP_SCOPE.md` owns product scope; domain documents refine those boundaries.
- Read the relevant current architecture before editing. Treat `[DECIDED]` rules as binding; keep `[PROPOSED]` / `[OPEN]` unsettled. Record Implementation Status separately as `[IMPLEMENTED]`, `[PARTIALLY IMPLEMENTED]` or `[NOT IMPLEMENTED]`.
- Verify current capability claims against the corresponding repository's exact source SHA, tests and appropriate acceptance evidence. Historical reviews, old branches and implementation accidents cannot override current decisions. Preserve dated evidence, especially the v0.4 review; add a new dated finding instead of rewriting history.
- Current interfaces versus target examples are indexed in Module Contracts §1.6. Do not freeze OPEN APIs/schema, infer runtime versions from proposed examples, or downgrade target architecture to current limitations.
- Generic Full Audit, local admission, query, snapshot/cache and shared-finalize rules live in Module Contracts §2.3 and §6.5–§6.6. Domain docs should reference these rules and add only domain-specific applications.
- Before design or implementation, read [Module Contracts](docs/MODULE_CONTRACTS.md), the relevant domain docs and the [unified references](docs/REFERENCES.md). For rule behavior, consult the relevant original passages of the bound version; small changes do not require reading every rulebook. For lore, confirm the Package's adopted setting, era and adventure edition.
- Cache, Snapshot, query scope and state persistence follow Module Contracts §2.3–§2.4. Distinguish official rules, explicit project adaptations, engineering choices, target design and current implementation; identify conflicts with project decisions instead of silently changing rules/architecture. Report inaccessible or unverified sources; never label memory or inference as verified. External references are for development research and do not introduce ordinary runtime online rule lookup.
- Before edits, record cwd, branch, HEAD, remote/main baseline and dirty files. Use an independent branch; preserve unrelated work with an isolated worktree when needed. Never reset, stash, rebase, force push or merge main without explicit task authorization.
- Documentation edits do not authorize code, schema, dependencies or CI changes in this or sibling repositories. Read sibling repositories only to establish evidence unless writes are explicitly requested.
- Check changed Markdown headings, relative links/anchors, fences, tables and `git diff --check`; use existing applicable docs tooling. Do not run unrelated integration suites for docs-only work or claim static review as runtime validation.
- Stage only authorized task files, inspect the staged diff, and commit/push within the authorized scope. Never automatically merge main. Report each repository's starting baseline, branch, final SHA, checks actually executed, remote result and remaining differences; distinguish local evidence from remote CI.

## Session memory runtime target (2026-10-21)

- Follow MC §0.3, §2.3–§2.4 and §6: loaded valid active facts, queries/checks, RE inputs, actor views, Snapshot construction and derived inputs use one consistent Session RAM scope. Do not reread/reassemble the same SQL facts to validate every memory read. Candidates and previously supplied fixed inputs remain isolated.
- Every mutation incrementally persists facts/versions/RNG/required evidence/Receipt/Outbox/reliable work in a short SQLite transaction, then publishes RAM before normal success/current projections. A live process with committed SQL but failed RAM publication must pause that Session and reconcile/rebuild, never continue on stale memory or report an uncommitted failure. SQLite and RAM are not one ACID transaction.
- Keep domain ownership, Stateless RE, Package/Ruleset bindings, OCC/idempotency and single-player MVP. Complete memory runtime and cross-command weight/mechanism reuse remain NOT IMPLEMENTED until proven. Concrete structures/API/version granularity remain OPEN.
- Future implementation evidence must inspect SQL, current RAM, old references/fixed inputs, indexes, caches and recovery together; cover every write entry including NPC Meta/Task, time and maintenance. Maintenance/import/migration requires a stop/reload boundary. Use the existing C-25/C-27/A2/DS tracks, not a duplicate backlog.

## Source documentation maintenance (2026-10-27)

- Follow [the shared source documentation standard](docs/CODE_DOCUMENTATION.md).
  New modules/classes/functions need proportionate docstrings; changed responsibilities,
  inputs/outputs, side effects or constraints require synchronized explanations. Preserve
  stronger existing constraints and review prose against implementation. Plans belong in
  contracts; current docstrings are the future index's maintained functional explanation.
- Use the applicable repository workflows in `.agents/skills/`: `trpg-contract-sync`.
  Read each matching SKILL.md explicitly when needed; these mandatory requirements do
  not depend on automatic triggering. Resolve sibling DOC paths from the logical workspace
  root. Keep the SM/RE documentation workflow copies consistent with the one shared standard.
