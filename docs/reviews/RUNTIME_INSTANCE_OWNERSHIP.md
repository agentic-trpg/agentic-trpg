# Runtime instance ownership — 2026-10-22

## 2026-10-22 four fixes: transaction and local costs

Architecture Decision Status **[DECIDED]**, under
[MC §2.3a](../MODULE_CONTRACTS.md#23a-实例字段关联与局部准入-decided).
Implementation Status **[IMPLEMENTED in the paired SM branch]**. Documentation
continues the existing `docs/runtime-versioned-cache-keys` worktree at reviewed
`8b18c198a9d724c1bb5b48b25d1911b0ba338a5e`; SM continues
`refactor/session-memory-runtime` from reviewed/remote
`5137742d8126588047f04ff4699ee14a94d3058b`. No main merge/push, RE/Pages changes,
new branch, schema, pin, Session directory or parallel transaction system.
Delivered SM implementation: [a2a2fe00d5f051978a6f4738df25fc81d838361e](https://github.com/agentic-trpg/trpg-state-machine/commit/a2a2fe00d5f051978a6f4738df25fc81d838361e).
Earlier independent OPEN findings and measurements below are historical records;
this section supersedes the four findings only in its verified scope.

### Implemented protocol and actual consumers

SQL failure uses the requested **B protocol** in existing RuntimeConnection /
UnitOfWork: execute or executemany failure (including a parameter generator after
an earlier write) marks the write scope failed. Guards, write requirements and
pre-COMMIT checks forbid untrusted candidate reads/writes/commit even when the SQL
exception was caught. Existing savepoints retain pending values, immutable version
root, change-log length and prior failure flag. ROLLBACK TO a valid pre-failure
savepoint restores all of them and clears memo/derived candidates, allowing legal
continuation while preserving prior work. Without recovery the whole scope rolls
back. SQLite's ROLLBACK policy can already remove the transaction/savepoints;
cleanup handles that separately. RELEASE in existing finally blocks is allowed
only as cleanup and never clears failure or authorizes COMMIT. The error does not
permanently poison the Session. Unknown COMMIT and committed-but-unpublished
failure retain the original pause, original-key reconciliation and all-context
recovery fence. No per-statement full checkpoint was added.
First-persistence upgrade failures (BEGIN IMMEDIATE, fixed SQL snapshot pin or
savepoint recreation) mark the same scope failed: that upgrade may already have
ended its prepared reading transaction. Catching that error cannot reuse/publish
old RAM. Separate lock and snapshot-pin fault tests cover this boundary too.

StepActor → actor coordinate write → inventory maintenance now compares actual
OLD/NEW fields. Coordinates, character HP/max HP/XP and mechanical actor
action/equipment metadata do not affect the current InventoryState. Real owner
membership, core carried slugs/legacy-source rejection, object item/ownership/state,
old/new ancestor access, barred/locked, destruction zero-HP boundary and relevant
configs still maintain actual affected owners. Known inventory patches use both
owner sets; unknown aggregate writes retain shared conservative invalidation.
`_validated_rule_components` caches one fully strict typed result. Dictionary
projection and inventory_model reuse it with equivalent normalized selection keys;
owner filtering cannot introduce new IDs or invalid scalars. Duplicate IDs,
portable projection consistency, strict list→tuple-only adaptation and disclosure
remain. Full inventory output has its proportional copy/serialization cost.

Real NPC handoff → dispatch_npc_output → target guard selects only acting/target
IDs through the existing RAM identity index and current candidate scope. Both
pre-evaluation and pre-apply checks remain, with grants, perception, same-scene,
existence, fixed snapshot, OCC and retry semantics unchanged.

VersionMap supplies private root handles over immutable AVL nodes within the same
SessionMemory. Scope startup, savepoint/rollback and read/write publication fork
roots in O(1); lookup/advance copy at most O(log N) search paths, not full version
records. Roots have no historical overlay link; actual old scopes/savepoints alone
retain old nodes. Explicit pruning above capacity×32 retains live dependencies and
inventory's aggregate/membership/layout components. If the retained set exceeds
capacity×16, rebuildable caches are released; otherwise at least half a budget of
new entries precedes another prune. This hysteresis avoids full work on every
near-limit operation. Unload/recovery remain explicit lifecycle work. Composite
stamps, old-reader publication refusal and cross-connection generations remain.

### Matched measurements and corrected atomicity finding

The same final production fixtures ran against archived, unmodified `5137742/src`
and delivery code in the locked environment. Six old-source performance assertions
fail after valid successful actions, reproducing the issues. The original CHECK
probe also fails on old source with public `closed` / SQLite `open`, commit not
refused. Current probe gives `open` / `open`, commit refused. This is the evidence
for changing that specific earlier **unresolved** finding to **repaired**.
The older `e776fab1` 298/798 metadata-copy figure retains its historical meaning;
it is not this run's baseline.

| Slice / deterministic counter | 5137742 before | After |
|---|---|---|
| Step→inventory with 11 / 101 entries: full validations; entries validated | 2 / 2; 22 / 202 | 0 / 0; 0 / 0 |
| Same: RAM calls/rows | 26/25 ; 206/205 | 2/2 ; 2/2 |
| Same: version checks; inventory field builds | 154 / 1324; 1 / 1 | 6 / 6; 0 / 0 |
| Same: legitimate full output entries | 11 / 101 | 11 / 101 |
| Same box read, +0 / +100 unrelated loaded objects: version records copied | 300 / 900 | 0 / 0 |
| Local write/savepoint rollback/write/commit: version records copied | 900 / 2700 | 0 / 0 |
| NPC, +0 / +100 remote actors: two target-check returned records | 6 / 206 | 4 / 4 |
| Same whole dispatch: RAM accessed rows | 76 / 276 | 70 / 70 |

Step-following and local read slices use zero SQL SELECTs/rows; local reads remain
31 RAM calls/13 rows, 155 checks, no field rebuild or parse at either size. Local
write slice retains RAM 6/2, two checks, two UPDATEs, no domain SELECT. Both slices
enumerate zero full version records. Write path node construction is proportional
to changed-key paths (208 / 266 nodes in the final recorded run), so no claim of
zero allocation or N-independent tree updates. Whole NPC dispatch SQL remains
28 SELECTs/25 rows at both sizes and retains one one-entry inventory validation
and one snapshot build. Two target checks are retained; version checks 141→143
are fixed with unrelated growth; whole-dispatch RAM calls stay 114, rows become
70 at both sizes. Counters are SQL / returned rows, RAM calls /
rows, validations / entries, metadata copies / enumeration, and rebuilds separately.

### Acceptance boundaries

Final focused acceptance is **75 passed, exit 0**, using
`uv run --locked --no-sync pytest -q -s` on the six SM runtime four-fix, transaction
failure, version-map, versioned-input, ownership and field-maintenance files,
with unique local basetemp, JUnit output and `-o faulthandler_timeout=60`.
The separate **35-passed** upgrade/RNG/publication subset is not added again.
Tests cover ABORT/FAIL/ROLLBACK with/without savepoint recovery, trigger/FK
cascades, swallowed errors followed by read/write/commit, earlier legal work,
executemany/parameter failure, first-persistence lock/pin faults, RELEASE cleanup,
movement/HP/actions, true
quantity/charges, one validation shared by both consumers, pruning and immutable
AVL snapshots. Existing regression covers owner transfer/access/config, strict
negatives, other-owner growth, rollback/unload/restart, stale NPC grants/targets,
fixed readers, authorization, RNG, idempotency, SQLite commit and RAM publication
failures, including another connection's recovery. Final commands/results follow
below with the full union audit.

Cold aggregate ComponentInputs preparation, SQLite aggregate inventory storage,
real dependencies, full public lists/evidence and fixed external inputs retain
their existing costs. Native SQLite cursor/executescript mutation is not a
supported runtime bypass; migration/maintenance retains an explicit stop/reload
boundary. Controlled REPLACE/table maintenance stays conservative. This does not
claim multiplayer capacity, remote CI, live item-stack editing or unsupported
combat continuation recovery. Architecture decisions, implementation and this
finite acceptance are distinct; historical sections below remain dated evidence.

Whole-Session configuration replacement still traverses Store-retained versions
to select that Session's light-candidate stamps; controlled REPLACE/table invalidation also
retains its old broad scope. Neither is newly introduced by version roots or
included in the local fixed-target cost claims.

SQL is measured at real Connection.execute and fetched cursors. Step-following
and box read each retain BEGIN×1 / PRAGMA×3; the local write slice retains
BEGIN×2 / PRAGMA×5 / SAVEPOINT×2 / ROLLBACK TO×1 / RELEASE×1 / UPDATE×2.
NPC dispatch retains BEGIN×8 / PRAGMA×24 / SAVEPOINT×2 / RELEASE×1 /
SELECT×28 / UPDATE×59 / INSERT×49 at both sizes. Native commit()/rollback()
method calls are excluded from execute counts and tested separately for durable
semantics. These are not trigger trace repeats, and metadata SQL is not called zero.

### Final complete-source acceptance

Final SM locked-environment regression: **2,119 unique cases pass**, partitioned
**739 / 703 / 675 + 2 isolated**. Collection/JUnit union reports no missing,
unexpected, duplicate, failed, errored or skipped case. All **220** Python source,
test and example hashes remain unchanged throughout the final run, including
first-persistence upgrade protection. Historical migration cases are included;
no unavailable-Git-history case is described as passing. Focused 75 and fault
subset 35 are overlapping evidence and not added again to this total.

Actual commands use `uv run --locked --no-sync pytest -q`, sorted test files
assigned modulo three, unique local basetemps, JUnit output and
`-o faulthandler_timeout=60`. Main groups exclude only the two exact names
test_live_compatibility_baseline_vs_sm_frozen_verification and
test_real_vertical_pipeline_committed_observations_fresh_process_audit; those
original cases run separately and **both pass**, with unchanged assertions and
timeouts. This is partitioned complete acceptance, not skipped tests.

An intermediate concurrent run had one Windows native access violation
`0xC0000005` reading SRD files and one existing 30-second child-process timeout.
Those attempts are preserved as nonpassing evidence. The final isolated cases
pass; this repair does not claim to diagnose the native failure's root cause or
guarantee repeated concurrent whole-corpus stress. Early test-fixture mistakes
and the superseded RELEASE-cleanup error are not final acceptance evidence.

SM local evidence is `.test-tmp/four-fixes-complete-delivery-{0,1,2}.{log,xml}`,
`four-fixes-complete-isolated.*`, `four-fixes-complete-delivery-collection.txt`,
`four-fixes-complete-audit.json`, `four-fixes-complete-hashes.json`,
`four-fixes-complete-counts.json` and `four-fixes-complete-target.*`.
The unchanged archived baseline's seven expected failures are in
`four-fixes-final-before.log`; intermediate crash/timeout attempts remain in
`four-fixes-final-delivery-2-native-crash.log` / `four-fixes-final-delivery-1.log`.

Required Ruff check and format check (`uv run --locked --no-sync ruff check src tests examples`
and `uv run --locked --no-sync ruff format --check src tests examples`) exit 0,
220 files. Changed Markdown links/anchors/fences pass in both repos: **9 files /
137 local links**; staged/unstaged whitespace checks pass. Final pytest groups
only report the two existing Lark deprecations. No remote CI, dependency upgrade,
multiplayer load or unsupported combat recovery is claimed. Cold aggregate work,
full output, logarithmic metadata updates, controlled broad configuration
maintenance and the unassigned intermediate native failure remain explicit limits.

## Earlier acceptance records

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

## 2026-10-22 follow-up: managed versioned inputs

Architecture Decision Status: **[DECIDED]**, MC §2.3a. Implementation Status:
**[IMPLEMENTED] within the following production paths**, with the limits below.
SM starts at `refactor/session-memory-runtime@e776fab1`; this Doc branch starts
at `a593a9d9`. Fetch/remote ancestry proves `docs/runtime-instance-ownership`
has not entered main `5619e7a`; the authorized new branch
`docs/runtime-versioned-cache-keys` therefore includes its latest work directly.
No merge, main push, RE or Pages edits; existing worktrees/untracked files stay.

| Actual owner / consumer | Identity and dependencies | Modification / isolation / recovery |
|---|---|---|
| Scene.spatial.record/map/mechanical_map; GridMaps.scene, GridReader, GridService | Store, Session, Scene; existing RAM projection versions of persisted map and spatial qualification | Mechanical scene changes invalidate; actor/object position changes leave base geometry reusable; immutable PreparedGrid shared under original candidate/publication boundary |
| Scene.spatial dynamic blockers; local_topology | Indexed requested/edge-neighbor Actor and Schema40 cells, relevant door states, exclusions and handled thresholds | Local read-only blocked-set overlay shares the base; actual position/open state drives versions; diagonal/wall/multi-cell/shared-door semantics retained |
| Scene.lighting; public query_illumination/current_cell and full current_project/current_topology | Actual source/configuration/mode/position, enclosing transmission, ground geometry, doors and map dependencies | Original source/geometry fields and bounded cell/projection fields remain; visibility uses same-scope base topology, output still applies current authorization and disclosure |
| CharacterRuntime.inventory; public read_carried_items | Session + actor; affected-owner stamp plus aggregate fallback, actor membership and controlled layout stamps | World/container/actor changes invalidate old/new actual carriers; validated inventory patches target known owners; other aggregate writes conservatively invalidate; original component/portable consistency checks remain |
| CharacterFacts rule_components and _inventory_selection | Explicit owner sets and item-ID selections, component and relationship versions | Indexed ComponentInputs selects actual owners; inventory validates directly with strict tuple normalization; current outer cache retained, rollback discards candidate selections |
| Scene.spatial.sensory; EventCapture._perception_geometry | Scene/map version and MechanicalGrid model type | Complete sensory validation of original prepared data, no GridScene defaults promoted; later stages/old fixed maps remain isolated |
| Event phase evidence | Corresponding candidate stage and existing evidence/Signal identity | Detached full output, evidence JSON persists with the existing transaction; later cache updates/unload do not rewrite evidence |

The implementation uses existing SessionMemory/UnitOfWork owner replacement,
savepoints, bounded retention and post-SQLite-COMMIT publication. No second current
state, directory or transaction protocol. Map lookup no longer thaws/sorts/encodes
the whole grid for a few extra blockers. Current Grid, Light, combat-position and
event consumers pass the prepared input; explicit unknown-version dict/foundation
inputs retain exact content identification and never select by scene_id alone.
Inventory mutation capture follows actual old/new ancestry, durability, bars,
locks, configuration and actor facts. A transient synchronous attribution hint
lets the existing validated inventory writer advance only its known owners;
unknown aggregate writes retain a conservative fallback. Composite stamp retention
survives pruning. Old read scopes, failed candidates, repeated version numbers,
unload and cross-connection recovery use the existing isolation/generation fences.

### Deterministic measurements

Same final performance fixtures run against archived, unmodified `e776fab1/src`
and delivery code, in the locked environment. All 14 new performance assertions
fail on old source as expected and pass after the fix. Growth is 10 / 100 distant
blocked cells, unrelated objects, remote actors and another actor's inventory
entries; target geometry and its sources are fixed. Query slices include repeated
targets and one new local target where applicable.

| Production slice / count (10 / 100) | Before | After |
|---|---|---|
| Local movement input: encoded blocked records | 10 / 100 | 0 / 0 |
| Same: full map copies; sorted records | 1 / 1; 22 / 112 | 0 / 0; 12 / 12 local cells |
| Public single-cell Light: encoded blocked records; Scene copies | 30 / 300; 3 / 3 | 0 / 0; 0 / 0 |
| Sensory map: encoded blocked records; Scene copies | 20 / 200; 2 / 2 | 0 / 0; 0 / 0 |
| Target inventory output (11 / 101 entries): encoded entries; version checks | 11 / 101; 41 / 311 | 0 / 0; 4 / 4 |
| After another actor's actual transfer: target RAM queries/rows | 18 / 108 | 2 / 2 |
| Real StepActor: internal key blocked records; topology builds | 40 / 400; 1 / 1 | 0 / 0; 0 / 0 |
| Same: required evidence encodings; persisted blocked records | 1 / 1; 10 / 100 | unchanged |

Lookup encoding calls, equal at both sizes: local 1 -> 0, Light 3 -> 0,
small inventory 2 -> 0, sensory 2 -> 0, full target inventory 1 -> 0,
post-foreign-transfer target 5 -> 0, movement 4 -> 0. Movement's necessary
evidence encoding is separately counted and remains 1 -> 1.

SQL SELECTs/rows are unchanged: local slice 3/0 (new local cell preparation),
Light/sensory/inventory/foreign-inventory reads 0/0, movement 6/2. Local RAM
calls/rows stay 10/2 and checks 136. Light RAM 6/6 -> 3/3, checks 41 -> 44;
sensory RAM 2/2 -> 0/0, checks 0 -> 4. Full target inventory RAM remains 2/2;
foreign transfer target checks 33 -> 4. Movement RAM 49/29 -> 46/26, checks
133 -> 137. Each figure is identical in the two growth groups. Warm topology
construction and JSON-model parse counts were already zero; delivery's instrumented
Python InventoryState/MechanicalGrid validations are zero too. The separate
encoding/copy counters establish the removed work rather than merely “no parse”.

Dependency-check counts are actual SessionMemory.version calls, not SQL or
individual integer comparisons. Inventory compares a fixed four-part version
stamp plus memory generation; no per-entry dependency validation is hidden there.

SM's final targeted slice passes **47 tests**, including 22 new cases. It covers
actual command/event capture, owner/item selection separation, malformed/unprojected
source rejection, repeated candidate stages, savepoint/outer rollback, full sensory
fields, old fixed maps, unload/restart and cross-connection map recovery after
commit failure/unknown commit/publication failure. Existing four publisher failure
modes additionally verify old/current inventory models. Final full-suite and docs
checks are recorded in the following acceptance section.

### Scope and open work

Full inventory, map projections and evidence retain proportional output costs.
Cold ComponentInputs index construction and existing aggregate SQLite inventory
updates retain their actual storage cost; the hot target read after another
owner's domain patch does not rebuild them. Unattributed aggregate SQL/imports
conservatively invalidate owner models. Genuine Light/source/door and scene-passage
dependencies remain; no constant-cost claim across growing relevant sources or
geometry. External fixed inputs without versions may retain content keys.

Serialization retained for persistence/protocols, evidence integrity, idempotency
conflicts and bindings is intentional. Existing JSON strings remain decoder-cache
inputs. Casting/effect selection uses the pinned strict JSON-model route on an
actual rule_components rebuild; its valid outer results still reuse normally.
No rule/Schema/RE pin/public DTO or multiplayer/recovery scope expansion.

**Independent unresolved work:** NPC all-actor queries, whole version-dictionary
copies, and the reported caught SQL statement error followed by continued commit
causing possible RAM/SQLite divergence. None is fixed or accepted by these cache
tests. All earlier historical numbers, statuses and limitations retain their dates.

### Final managed-input acceptance

The final SM sources pass **2,091 unique tests**, disjoint sorted-file groups
**665 / 757 / 669**, all exit 0. Collection/JUnit union has no failed, errored,
skipped, duplicate, missing or unexpected cases. All 216 Python source/test/example
hashes remain unchanged throughout that run. Historical migration cases execute
without an environment-blocked/skipped case. A final 47-test focused run also
passes; it is already part of the full count. Earlier fixture/strict-model
compatibility failures are intermediate work, not final passing evidence.

Validation uses the existing locked environment (`uv run --locked --no-sync`),
repository-local unique basetemps, pytest/JUnit and actual source instrumentation.
Ruff check and format-check over src/tests/examples pass (216 files). Changed
Markdown links/anchors/fences across both repositories pass: 13 files / 170 local
links; diff whitespace checks pass. Two existing Lark deprecation warnings occur
per pytest group. These are local checks; remote CI and sustained multiplayer load
were not executed. This acceptance does not close any independent issue above.

Verified SM delivery: [`5137742d8126588047f04ff4699ee14a94d3058b`](https://github.com/agentic-trpg/trpg-state-machine/blob/5137742d8126588047f04ff4699ee14a94d3058b/docs/reviews/RUNTIME_INSTANCE_OWNERSHIP.md),
normally pushed on `refactor/session-memory-runtime` from `e776fab1`. This Doc
change remains separately on `docs/runtime-versioned-cache-keys` from `a593a9d9`;
the predecessor worktree/branch and both main branches are unchanged.
