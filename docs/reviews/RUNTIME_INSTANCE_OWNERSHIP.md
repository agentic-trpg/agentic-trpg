# Runtime instance ownership — 2026-10-22

The [follow-up evidence](#2026-10-22-follow-up-field-validity-and-local-associations)
below records the second performance repair. Earlier numbers retain their original
time, source and measurement scope.

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
## 2026-10-22 follow-up: field validity and local associations

Architecture Decision Status **[DECIDED]**, MC §2.3a. Implementation Status
**[IMPLEMENTED]**, within the named domains and measured scope below. Docs starts
at `80bd39c551dd62cb53bfd2d4a18f4c4c3a00182a` on the existing
`docs/runtime-instance-ownership` worktree; SM starts at
`c64f9d7975cad55e536e0e4ea7a056fed79bd384` on the existing
`refactor/session-memory-runtime`. No new branch/main merge/RE or Pages change.
Verified delivery source and executed validation are recorded below after completion.

### Maintenance and ownership

Weight field validity is maintained by real quantity/item/configuration and parent
changes, invalidating the object plus old/new ancestors. Hits compare one object
field version; computed leaves are private to that computation, so enclosing
view/admission caches do not inherit all descendants. Unknown remains None;
detached candidate capacity, actual destruction consequences and permission rules
remain. Scene.mechanisms.index uses a maintained scene version and immutable
mapping/tuple/frozen-trigger buckets; automatic events look up the relevant entry,
without whole-index copy or every-configuration validity probes. Relevant changes
may lazily rebuild the actual scene mechanism index; eligibility/status/uses/order
and the existing World component index retain their original responsibilities.
Region lookup uses the destination cell; object-operation lookup uses the concrete
event type and object ID, so a same-category event at a different target also
selects no candidates. Region preparation/storage costs its configured cell links.

Scene.objects.capabilities contains light/mechanism IDs derived only from existing
object position/parent/carrier, actor scene and capability membership facts. A
cross-scene move visits the moving subtree/carried subtrees through existing
parent/member indexes and patches loaded old/new scenes. Same-scene movement
does not change membership; selected light/ancestor/state/configuration dependencies
still handle shading, position, accessibility, mode and enabled changes. Capability
insertion/deletion patches its actual scene. Cold/evicted associations are prepared
from persisted instance facts, not Package defaults. No independently writable
directory, Session or transaction authority is introduced.

The actual light call chain also exposed negative spatial/configuration dependencies
for every ground object inside cached geometry. Scene.lighting.candidates now has
a change-maintained ground-geometry version; nonground empty-bag transfer leaves it
valid. Ground pose/state, durability/configuration and relevant lifecycle/layout
changes invalidate it. Map, door, source and shading checks stay separate.

Facts, association patches and field invalidation share the existing UnitOfWork
candidate/savepoint/durable commit/RAM publication. Old indices and fixed inputs
remain immutable. A patch never validates an already-stale association. Failure,
unknown commit and cross-connection recovery retain the preceding shared recovery
generation and publication fence. Unload/restart rebuild these derived fields.
Controlled REPLACE is conservatively invalidated as maintenance compatibility;
normal commands do not scan scenes or audit Sessions to maintain these fields.

### New deterministic measurements

Same locked runtime and production paths before/after; baseline source is a read-only
archive of `c64f9d7`. The eight new performance cases reproduce failures on the
baseline. Version checks, copied records, RAM calls/rows, SQL and computation bodies
are separate counters, not proxies for one another or timing assertions.

RAM calls count the SessionMemory.select interface, including cold requests that
also execute SQL; visited RAM rows and fetched SQL rows stay separate. Copy counts
refer to trigger-index records, not legitimate complete-map/event output copies.
Trigger repr calls independently detect retention-budget traversal. Immutable
fields cache their conservative payload charge on production/replacement; owners
reuse those charges and grouped dependency references without formatting all
retained values or flattening every dependency leaf. Actual payload still counts
toward the existing limits. An initial zero-copy fix still formatted 10/100 records;
that separately reproduced cost is removed too.

| Measurement | Before small / large | After small / large |
|---|---:|---:|
| Warm weight scalar, 10 / 100 contents: dependency checks | 31 / 301 | 1 / 1 |
| Same scalar: SQL/rows/RAM queries/weight recomputations | all zero | all zero |
| Real nonmatching movement, 10 / 100 mechanisms: copied records | 10 / 100 | 0 / 0 |
| Same movement: trigger records formatted for budget accounting | 10 / 100 | 0 / 0 |
| Same-category region event outside all configured cells: candidates | 10 / 100 | 0 / 0 |
| Same command: all dependency checks | 121 / 211 | 111 / 111 |
| Same command: SQL SELECTs / rows; RAM calls / rows | 26 / 5; 78 / 32 in both | unchanged |
| Four empty-bag Put/Take commands, unrelated growth 0 / 100: discovery calls | 8 / 8 | 0 / 0 |
| Same commands: RAM query calls | 350 / 750 | 284 / 284 |
| Same commands: dependency checks | 1,902 / 6,302 | 972 / 972 |
| Same commands: RAM rows | 202 / 202 | 180 / 180 |
| Same commands: SQL SELECTs / rows | 36 / 16 in both | unchanged |
| Same commands: scene index / light source rebuilds | 4 / 4 in both | 0 / 0 in both |

Growth adds 100 unrelated objects (50 local) and 100 remote actors. Commands use
receipt versions; a separately requested full SessionView has its real full-output
cost and is outside this slice. Weight repeat and warmed get/list regressions cover
upper-cache reuse. Necessary facts/configuration/contents/candidate computations
remain: 28 instance computations before versus 16 after for four commands in both
growth groups. SessionMemory content JSON/model decoding and fixed Snapshot wrapper
build counters are zero; retained new event JSON work is not a zero-work claim. These
figures do not replace the earlier historical 15/115 discovery RAM-call example,
10,302 candidate-key records, 2,059-test acceptance or prior SQL benchmark.

### Limits

Cold associations and invalidated whole-map geometry retain their actual preparation
cost. Moving subtree maintenance, capability tuple replacement and relevant scene
mechanism index rebuilding cost the actual subtree/members/triggers. Ground geometry
invalidation is conservative for ground configuration/state and scene-instance metadata changes. Complete lists,
mechanical/evidence maps and aggregate admission retain legitimate output/dependency
cost. No public partial-stack/live capability editing, scene-unload API or multiplayer
performance claim is added; the previous product/heap/recovery limitations remain.

### Final follow-up delivery

Verified and normally pushed SM source:
[`e776fab1ede6ec8fc8ca5a46cb34410a85031de1`](https://github.com/agentic-trpg/trpg-state-machine/blob/e776fab1ede6ec8fc8ca5a46cb34410a85031de1/docs/reviews/RUNTIME_INSTANCE_OWNERSHIP.md)
on `refactor/session-memory-runtime`, starting at the reviewed `c64f9d7`.
This documentation update remains on `docs/runtime-instance-ownership`, starting
at `80bd39c`; neither branch is merged to main. Existing untracked work is preserved.

Final fixed sources pass **2,069 unique tests in 93 files**, in disjoint file
groups **650 / 725 / 694**, all exit 0. Collection/JUnit union has no missing,
unexpected, duplicate, failed, errored or skipped cases. All 215 Python
source/test/example hashes remain unchanged during this final run. Historical
migration cases are included with no environment-blocked/skipped cases. A final
60-test field/mechanism/recovery slice also passes and is not counted twice.
Earlier complete/interrupted runs before the final budget/target lookup fixes are
intermediate evidence only. The eight final performance cases intentionally fail
on the old archived source and pass on the delivery source.

Ruff check/format-check over src/tests/examples (215 files), changed Markdown
links/anchors/fences across both repositories (12 files / 148 local links), and
staged/unstaged diff whitespace checks pass. The original locked environment and
repository-local basetemps were used. Two existing Lark deprecation warnings occur
per test group. These are local checks, not GitHub Actions or sustained multiplayer
load evidence. Schema/DTO/RE pin and rules remain unchanged; the above cold,
subtree/region-index, full-output and heap boundaries still apply.
