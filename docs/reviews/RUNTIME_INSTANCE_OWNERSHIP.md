# Runtime instance ownership — 2026-10-22

Architecture Decision Status: **[DECIDED]**, authoritative rules in
[MC §2.3a](../MODULE_CONTRACTS.md#23a-实例字段关联与局部准入-decided).
Documentation baseline: `origin/main@5619e7aa840ca6b6474877be39d73a6dcfd1f085`;
delivery branch: `docs/runtime-instance-ownership`. Original untracked requirements
and worktrees are preserved. This branch is not merged to main.

Implementation Status of the named owner fields and consumers below:
**[IMPLEMENTED]** on the SM delivery branch. This is a bounded implementation
statement; it does not close all C-25/C-27/DS work or the unsupported systems listed
below. Executed acceptance is recorded separately in the final delivery entry.

SM baseline: `refactor/session-memory-runtime@16c305999e5ac17ef4194a3113eeb60b9ed36902`.
Verified delivery source: `c64f9d7975cad55e536e0e4ea7a056fed79bd384` on that same branch.
Existing SessionMemory, UnitOfWork, candidate/savepoint and durable publication
are retained. No Rule Engine repository, Pages, public DTO, schema version,
dependency pin or rules semantics is changed.

## Implemented consumer mapping

| Owner field | Production path | Validity / lifecycle |
|---|---|---|
| ObjectRuntime.facts / definition | WorldFacts / InstanceData → public views and original domain services | Indexed current/candidate facts; immutable owner replacements |
| Object.container.contents / own_weight / contents_weight / total_weight | get_object / list_scene_objects; ContainerService candidate capacity | Parent-indexed contents; instance weight/quantity and affected descendant dependencies; no whole-candidate key |
| Object.mechanism.configuration | Scene automatic index and World component reverse index | Static persisted trigger/component links; activation status read separately |
| Scene.objects.direct / contributors | Local directories, capability discovery and list consumers | Ground roots separate from carrier/container descendants |
| Scene.spatial.map / mechanical_map / occupants / object_positions / cells / blockers | GridReader, local_topology, movement admission, environment protection and views | Existing map pool and Schema40 cell lookup; narrow projection dependencies |
| Scene.environment.facts / inputs / protection / cells / ranges | Existing public area/cell/unit/height queries | Original source/protection/provider version protocol, height/disclosure parameters, bounded results |
| Scene.lighting.sources / geometry / cells / projection | Public illumination, targeted object/door/area visibility, noncombat RE Snapshot, staged noncombat evidence | Target-cell composition shares immutable geometry through a read-only lighting overlay; explicitly complete maps retain original visibility/uncertainty |
| Scene.mechanisms.index | Automatic admitted events | Scene membership version plus selected instance configurations; empty result reusable |
| World.mechanisms.index | Cross-scene component destruction | Configured mechanisms only; not an all-object/all-capability scan |

Fields are stored under the existing bounded SessionMemory budget and published
by the existing transaction. They are not independent mutable authorities.
TEMP change capture updates relevant dependency versions, including original/new
scene associations and parent/carrier moves. A candidate reuses only unchanged
subtrees from its exact originating scope/stage; changed ancestors compute from
the detached candidate. Savepoint/outer rollback cannot publish candidates.

Shared recovery generations invalidate other connections on their own threads;
an older read scope cannot republish after a recovery even if no SQL version
changed. Committed/unknown outcomes, receipts and pause semantics remain explicit.

## Evidence and limits

The corresponding SM [implementation inventory and acceptance report](https://github.com/agentic-trpg/trpg-state-machine/blob/c64f9d7975cad55e536e0e4ea7a056fed79bd384/docs/reviews/RUNTIME_INSTANCE_OWNERSHIP.md)
records exact executed tests, counts and final implementation SHA. This document
does not convert historical 10 October acceptance figures into new results.

Cold capability association discovery follows indexed scene roots, carriers and
parent relations and enumerates the necessary directory on a cold association revision;
hot validity uses maintained Scene association versions, not per-object probing.
Cold whole-map geometry and explicit full-map projections still depend on their
declared scene scope; single-cell light composition does not fill the map.
Budget is scalar retained payload, not a complete Python heap guarantee. There
is no standalone unload_scene API; existing Session unload/LRU/cold loading remain.
Complete Effects/Activity lifecycles, general Cell instances, multiplayer protocol
and active-combat crash continuation remain outside this change.

## Final executed acceptance

The fixed SM runtime/tests/examples pass **2,059 unique tests in 92 files**:
three disjoint file groups of 633 / 738 / 688. Collection/JUnit union has zero
missing, unexpected, duplicate, failed, errored or skipped nodes; hashes did not
change during acceptance. Ruff check and format (214 files), both repositories'
Markdown links/anchors/fences (18 files / 172 local links), and staged/unstaged
diff checks pass. These are local checks, not GitHub Actions results. Only two
existing Lark deprecation warnings occur per group. Intermediate failures and
focused runs are not counted again.

Public scale measurements hold the target fixed while adding 150 unrelated
objects and 150 remote actors. Ten hot object reads perform 0 fact SELECTs,
0 fetched rows, 0 JSON/model parses and 0 instance computations in both groups;
20 Put/Take commands perform 180 SELECTs / 80 fetched rows in both groups.
Four commands execute 8,356 SQLite VM instructions in both groups. Event JSON,
necessary persistence/constraints, cold directory discovery and complete requested
results retain explicit costs. The fixed SM report separates these counters,
retained payload and tracemalloc measurements and supplies reproduction commands.

The complete SM suite includes candidate/savepoint rollback, old fixed inputs,
cross-scene movement, mechanism state/configuration/damage, unknown weight,
restart/unload and real RE/RNG/authorization/receipt regressions. New tests cover
A publication failure followed by B recovery, partial/completed publication failure,
unknown commit, failed recovery, old-reader publication fencing and old Driver
invalidation on the owning thread. Schema, dependency lock, public DTO and rules
remain unchanged. This docs branch is committed/pushed separately without merging.
