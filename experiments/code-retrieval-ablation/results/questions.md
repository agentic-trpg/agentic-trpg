# 逐问题检索结果

入口计入相关集合；标注不是穷尽调用图。>50 表示本路 Top-50 未出现。完整 Top-10 节点 ID 见 per-question.json；Top-50 在本地 .local/complete-rankings.json。

## Q01 — development — 容器重量

我想显示一个箱子连同里面物品的当前总重量，应该从哪里读？

English: Read the current total weight of a container including its contents.

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| T | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | ContainerService.current_weight@149=2 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.333 | 0.667 | ContainerService.current_weight@149=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.current_weight@149 | 1 | 1 | 1 | 1 | 1 | 2 | 3 |
| ContainerService.own_weight@136 | 2 | 3 | 3 | 3 | 5 | 4 | 10 |
| WorldFacts.contents@1120 | >50 | 48 | 25 | 24 | >50 | 11 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | ContainerService.current_weight@149=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | ContainerService.current_weight@149=1 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | ContainerService.current_weight@149=1 |
| T | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | ContainerService.current_weight@149=3 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | ContainerService.current_weight@149=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.current_weight@149 | 1 | 1 | 1 | 1 | 1 | 3 | 3 |
| ContainerService.own_weight@136 | 3 | 5 | 3 | 4 | 4 | 4 | 5 |
| WorldFacts.contents@1120 | 14 | 30 | 14 | 7 | 8 | 11 | 24 |

## Q02 — development — 容器重量

修改物品数量后，之前缓存的箱子重量为什么会失效？

English: After an item quantity changes, how is cached container weight invalidated?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | SessionMemory._weight_changes@786=2 |
| B | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | SessionMemory._weight_changes@786=2 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | SessionMemory._weight_changes@786=2 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | SessionMemory._weight_changes@786=1 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._weight_changes@786=1 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | SessionMemory._weight_changes@786=1 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory._weight_changes@786=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._weight_changes@786 | 2 | 2 | 2 | 1 | 1 | 1 | 1 |
| SessionMemory.changed@1158 | 10 | 19 | 10 | 10 | 11 | 10 | 42 |
| ContainerService.current_weight@149 | 5 | 4 | 4 | 5 | 5 | 5 | 23 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | SessionMemory._weight_changes@786=2 |
| B | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | SessionMemory._weight_changes@786=2 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | SessionMemory._weight_changes@786=2 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | SessionMemory._weight_changes@786=2 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._weight_changes@786=1 |
| T | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | SessionMemory._weight_changes@786=2 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SessionMemory._weight_changes@786=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._weight_changes@786 | 2 | 2 | 2 | 2 | 1 | 2 | 1 |
| SessionMemory.changed@1158 | 12 | 26 | 15 | 9 | 12 | 18 | 44 |
| ContainerService.current_weight@149 | 4 | 3 | 3 | 4 | 5 | 5 | 10 |

## Q03 — development — 嵌套容器

把装着东西的小箱子放进大箱子时，哪里检查深度和容量？

English: Where are depth and capacity checked when moving a filled box into another container?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 1.000 | 0.125 | 0.250 | 0.500 | ContainerService.validate@341=8 |
| B | 1.000 | 1.000 | 0.250 | 0.500 | 0.500 | ContainerService.validate@341=4 |
| C | 1.000 | 1.000 | 0.250 | 0.500 | 0.500 | ContainerService.validate@341=4 |
| D | 1.000 | 1.000 | 0.333 | 0.500 | 0.500 | ContainerService.validate@341=3 |
| E | 0.000 | 0.000 | 0.000 | 0.250 | 0.250 | ContainerService.validate@341=22 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | ContainerService.validate@341=1 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.250 | 0.250 | ContainerService.validate@341=>50 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.validate@341 | 8 | 4 | 4 | 3 | 22 | 1 | >50 |
| ContainerService.audit@224 | 1 | 1 | 1 | 2 | 1 | 5 | 3 |
| ContainmentState.relocate@44 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |
| ContainerService.subtree@213 | >50 | >50 | 43 | >50 | 44 | >50 | 21 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.500 | 0.500 | ContainerService.validate@341=3 |
| B | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | ContainerService.validate@341=2 |
| C | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | ContainerService.validate@341=2 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | ContainerService.validate@341=1 |
| E | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | ContainerService.validate@341=2 |
| T | 1.000 | 1.000 | 1.000 | 0.250 | 0.500 | ContainerService.validate@341=1 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.250 | 0.500 | ContainerService.validate@341=14 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.validate@341 | 3 | 2 | 2 | 1 | 2 | 1 | 14 |
| ContainerService.audit@224 | 1 | 1 | 1 | 3 | 1 | 9 | 3 |
| ContainmentState.relocate@44 | >50 | 37 | 47 | 33 | >50 | 16 | >50 |
| ContainerService.subtree@213 | >50 | >50 | 29 | 50 | 23 | 29 | 9 |

## Q04 — development — 嵌套容器

外层箱子关闭后，怎样阻止直接拿走内层物品？

English: How is taking an inner item prevented when an outer container is closed?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | ContainerService.reachable@76=28; WorldFacts.item_accessible@1108=2 |
| B | 1.000 | 1.000 | 0.250 | 0.667 | 0.667 | ContainerService.reachable@76=4; WorldFacts.item_accessible@1108=5 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | ContainerService.reachable@76=4; WorldFacts.item_accessible@1108=2 |
| D | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | ContainerService.reachable@76=16; WorldFacts.item_accessible@1108=3 |
| E | 0.000 | 1.000 | 0.100 | 0.000 | 0.333 | ContainerService.reachable@76=>50; WorldFacts.item_accessible@1108=10 |
| T | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ContainerService.reachable@76=18; WorldFacts.item_accessible@1108=13 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ContainerService.reachable@76=>50; WorldFacts.item_accessible@1108=>50 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.reachable@76 | 28 | 4 | 4 | 16 | >50 | 18 | >50 |
| WorldFacts.item_accessible@1108 | 2 | 5 | 2 | 3 | 10 | 13 | >50 |
| ContainerService.require_contents_access@100 | >50 | 16 | 20 | 42 | >50 | 20 | 30 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | ContainerService.reachable@76=18; WorldFacts.item_accessible@1108=2 |
| B | 1.000 | 1.000 | 0.333 | 0.333 | 1.000 | ContainerService.reachable@76=3; WorldFacts.item_accessible@1108=10 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | ContainerService.reachable@76=2; WorldFacts.item_accessible@1108=5 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | ContainerService.reachable@76=5; WorldFacts.item_accessible@1108=2 |
| E | 1.000 | 1.000 | 0.333 | 0.333 | 0.667 | ContainerService.reachable@76=35; WorldFacts.item_accessible@1108=3 |
| T | 1.000 | 1.000 | 0.250 | 0.333 | 0.667 | ContainerService.reachable@76=4; WorldFacts.item_accessible@1108=15 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ContainerService.reachable@76=>50; WorldFacts.item_accessible@1108=28 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.reachable@76 | 18 | 3 | 2 | 5 | 35 | 4 | >50 |
| WorldFacts.item_accessible@1108 | 2 | 10 | 5 | 2 | 3 | 15 | 28 |
| ContainerService.require_contents_access@100 | 27 | 7 | 9 | 8 | 7 | 6 | 15 |

## Q05 — development — 环境快照

给玩家查询某一小片区域的天气时，权限和可见范围在哪里检查？

English: Where are authorization and visibility checked for a player weather query over a small area?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | EnvironmentService.query_area@729=2 |
| B | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | EnvironmentService.query_area@729=3 |
| C | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | EnvironmentService.query_area@729=2 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | EnvironmentService.query_area@729=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | EnvironmentService.query_area@729=1 |
| T | 0.000 | 1.000 | 0.143 | 0.000 | 0.333 | EnvironmentService.query_area@729=7 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService.query_area@729=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService.query_area@729 | 2 | 3 | 2 | 1 | 1 | 7 | 1 |
| EnvironmentService.query_cell@767 | >50 | >50 | >50 | >50 | 14 | >50 | 2 |
| EnvironmentService._cell@543 | >50 | >50 | >50 | >50 | >50 | >50 | 31 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | EnvironmentService.query_area@729=3 |
| B | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | EnvironmentService.query_area@729=3 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | EnvironmentService.query_area@729=1 |
| D | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | EnvironmentService.query_area@729=2 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | EnvironmentService.query_area@729=1 |
| T | 0.000 | 1.000 | 0.167 | 0.000 | 0.333 | EnvironmentService.query_area@729=6 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService.query_area@729=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService.query_area@729 | 3 | 3 | 1 | 2 | 1 | 6 | 1 |
| EnvironmentService.query_cell@767 | >50 | >50 | >50 | >50 | 19 | >50 | 2 |
| EnvironmentService._cell@543 | >50 | >50 | >50 | >50 | >50 | >50 | 38 |

## Q06 — development — 环境快照

环境结果能否跨查询复用，哪里决定提供方和版本是否有效？

English: What decides whether environment results can be reused across queries with valid providers and versions?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.250 | 0.500 | EnvironmentService._query_cache@169=3 |
| B | 1.000 | 1.000 | 1.000 | 0.750 | 0.750 | EnvironmentService._query_cache@169=1 |
| C | 1.000 | 1.000 | 1.000 | 0.750 | 0.750 | EnvironmentService._query_cache@169=1 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 1.000 | EnvironmentService._query_cache@169=1 |
| E | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | EnvironmentService._query_cache@169=2 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | EnvironmentService._query_cache@169=1 |
| BM25 | 1.000 | 1.000 | 0.250 | 0.500 | 0.500 | EnvironmentService._query_cache@169=4 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService._query_cache@169 | 3 | 1 | 1 | 1 | 2 | 1 | 4 |
| EnvironmentVersions.cacheable@208 | 6 | 2 | 2 | 2 | 1 | 2 | 1 |
| EnvironmentVersions.current@158 | 39 | >50 | 47 | 9 | 17 | 6 | 25 |
| EnvironmentService._environment_inputs@198 | 14 | 4 | 3 | 7 | 14 | 16 | 43 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | EnvironmentService._query_cache@169=1 |
| B | 1.000 | 1.000 | 1.000 | 0.750 | 0.750 | EnvironmentService._query_cache@169=1 |
| C | 1.000 | 1.000 | 0.500 | 0.750 | 0.750 | EnvironmentService._query_cache@169=2 |
| D | 1.000 | 1.000 | 0.500 | 0.500 | 1.000 | EnvironmentService._query_cache@169=2 |
| E | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | EnvironmentService._query_cache@169=2 |
| T | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | EnvironmentService._query_cache@169=3 |
| BM25 | 1.000 | 1.000 | 0.200 | 0.500 | 0.500 | EnvironmentService._query_cache@169=5 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService._query_cache@169 | 1 | 1 | 2 | 2 | 2 | 3 | 5 |
| EnvironmentVersions.cacheable@208 | 2 | 2 | 1 | 1 | 1 | 1 | 1 |
| EnvironmentVersions.current@158 | 43 | >50 | 38 | 9 | 16 | 5 | 18 |
| EnvironmentService._environment_inputs@198 | 12 | 5 | 4 | 7 | 11 | 23 | 28 |

## Q07 — development — 光照

想知道角色看得到的某个格子有多亮，应调用哪一层？

English: Which entry reads illumination of a cell visible to an actor?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=3; LightService.query_illumination@261=1 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | StateMachine.get_illumination@481=6; LightService.query_illumination@261=1 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=5; LightService.query_illumination@261=1 |
| D | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=3; LightService.query_illumination@261=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | StateMachine.get_illumination@481=14; LightService.query_illumination@261=1 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | StateMachine.get_illumination@481=3; LightService.query_illumination@261=1 |
| BM25 | 0.000 | 1.000 | 0.143 | 0.000 | 0.333 | StateMachine.get_illumination@481=>50; LightService.query_illumination@261=7 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| StateMachine.get_illumination@481 | 3 | 6 | 5 | 3 | 14 | 3 | >50 |
| LightService.query_illumination@261 | 1 | 1 | 1 | 1 | 1 | 1 | 7 |
| LightService.current_cell@89 | 4 | 3 | 3 | 5 | 16 | 8 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=2; LightService.query_illumination@261=1 |
| B | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=4; LightService.query_illumination@261=1 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=3; LightService.query_illumination@261=1 |
| D | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | StateMachine.get_illumination@481=1; LightService.query_illumination@261=2 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | StateMachine.get_illumination@481=4; LightService.query_illumination@261=1 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | StateMachine.get_illumination@481=1; LightService.query_illumination@261=2 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | StateMachine.get_illumination@481=22; LightService.query_illumination@261=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| StateMachine.get_illumination@481 | 2 | 4 | 3 | 1 | 4 | 1 | 22 |
| LightService.query_illumination@261 | 1 | 1 | 1 | 2 | 1 | 2 | 1 |
| LightService.current_cell@89 | 3 | 3 | 4 | 4 | 11 | 6 | >50 |

## Q08 — development — 光照

灯放进不透光的容器里后，场景里的光源集合在哪里排除它？

English: Where are emitters inside opaque containers excluded from the scene light-source collection?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService.sources@35=1 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService.sources@35=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService.sources@35=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService.sources@35=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | LightService.sources@35=1 |
| T | 1.000 | 1.000 | 0.500 | 0.333 | 0.667 | LightService.sources@35=2 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | LightService.sources@35=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LightService.sources@35 | 1 | 1 | 1 | 1 | 1 | 2 | 1 |
| WorldFacts.placement@1080 | >50 | >50 | >50 | >50 | 28 | >50 | 12 |
| SessionMemory._light_candidate_changes@645 | 2 | 5 | 5 | 4 | 16 | 9 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService.sources@35=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | LightService.sources@35=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | LightService.sources@35=1 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | LightService.sources@35=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | LightService.sources@35=1 |
| T | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | LightService.sources@35=1 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | LightService.sources@35=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LightService.sources@35 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| WorldFacts.placement@1080 | >50 | >50 | >50 | >50 | >50 | >50 | 38 |
| SessionMemory._light_candidate_changes@645 | 4 | 10 | 7 | 7 | 20 | 13 | >50 |

## Q09 — development — 机关索引

移动事件触发陷阱时，哪里按位置取候选而不是逐个运行所有机关？

English: Where does movement-triggered trap dispatch select candidates by location instead of executing every mechanism?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | MechanismService.automatic@554=1 |
| B | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | MechanismService.automatic@554=1 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | MechanismService.automatic@554=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | MechanismService.automatic@554=1 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | MechanismService.automatic@554=1 |
| T | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | MechanismService.automatic@554=1 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | MechanismService.automatic@554=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MechanismService.automatic@554 | 1 | 1 | 1 | 1 | 1 | 1 | 2 |
| MechanismService._scene_index@47 | 10 | 4 | 4 | 9 | 25 | 33 | >50 |
| MechanismService._activate@219 | 2 | 3 | 3 | 2 | 4 | 12 | 19 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | MechanismService.automatic@554=1 |
| B | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | MechanismService.automatic@554=1 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | MechanismService.automatic@554=1 |
| D | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | MechanismService.automatic@554=1 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | MechanismService.automatic@554=1 |
| T | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | MechanismService.automatic@554=1 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | MechanismService.automatic@554=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MechanismService.automatic@554 | 1 | 1 | 1 | 1 | 1 | 1 | 3 |
| MechanismService._scene_index@47 | 7 | 2 | 3 | 3 | 23 | 16 | >50 |
| MechanismService._activate@219 | 3 | 3 | 2 | 2 | 3 | 7 | 17 |

## Q10 — development — 机关索引

某个部件损坏后，哪里找到依赖该部件的跨场景机关？

English: Where are cross-scene mechanisms linked to a destroyed component found?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | MechanismService.component_destroyed@501=3 |
| B | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| E | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | MechanismService.component_destroyed@501=1 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | MechanismService.component_destroyed@501=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MechanismService.component_destroyed@501 | 3 | 2 | 2 | 2 | 2 | 1 | 3 |
| MechanismService._build_index@529 | 1 | 1 | 1 | 1 | 1 | 2 | 1 |
| MechanismService._batch_index@547 | >50 | >50 | >50 | >50 | 46 | >50 | 25 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| B | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | MechanismService.component_destroyed@501=1 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| E | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | MechanismService.component_destroyed@501=1 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | MechanismService.component_destroyed@501=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MechanismService.component_destroyed@501 | 2 | 2 | 1 | 2 | 2 | 1 | 2 |
| MechanismService._build_index@529 | 1 | 1 | 2 | 1 | 1 | 2 | 1 |
| MechanismService._batch_index@547 | >50 | >50 | >50 | >50 | 30 | 50 | 13 |

## Q11 — development — 空间查询

只检查一步移动附近的动态阻挡，如何避免构造整场景视图？

English: How can a single movement step inspect nearby dynamic blockers without building a whole-scene view?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| B | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| C | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| E | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| T | 1.000 | 1.000 | 0.333 | 0.500 | 0.500 | GridService.local_topology@503=3 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GridService.local_topology@503 | 1 | 1 | 1 | 1 | 1 | 3 | 1 |
| GridReader.cell_occupants@400 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| B | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| C | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| E | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | GridService.local_topology@503=1 |
| T | 1.000 | 1.000 | 0.250 | 0.500 | 0.500 | GridService.local_topology@503=4 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | GridService.local_topology@503=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GridService.local_topology@503 | 1 | 1 | 1 | 1 | 1 | 4 | 2 |
| GridReader.cell_occupants@400 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |

## Q12 — development — 空间查询

已经拿到固定网格视图，查某格被谁占用是否还要遍历所有实体？

English: With a fixed grid view, how are occupants of one cell found without scanning every entity?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 1.000 | 0.125 | 0.333 | 0.667 | GridView.occupied@148=8 |
| B | 1.000 | 1.000 | 0.250 | 0.333 | 1.000 | GridView.occupied@148=4 |
| C | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | GridView.occupied@148=3 |
| D | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | GridView.occupied@148=3 |
| E | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | GridView.occupied@148=4 |
| T | 1.000 | 1.000 | 0.333 | 0.667 | 1.000 | GridView.occupied@148=3 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.333 | 0.667 | GridView.occupied@148=20 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GridView.occupied@148 | 8 | 4 | 3 | 3 | 4 | 3 | 20 |
| GridView.__post_init__@86 | 2 | 6 | 4 | 2 | 1 | 6 | 4 |
| GridView.entity_cells@154 | 18 | 8 | 1 | 4 | 3 | 1 | 6 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.667 | 1.000 | GridView.occupied@148=3 |
| B | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | GridView.occupied@148=2 |
| C | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | GridView.occupied@148=4 |
| D | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | GridView.occupied@148=2 |
| E | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | GridView.occupied@148=4 |
| T | 1.000 | 1.000 | 0.333 | 0.667 | 1.000 | GridView.occupied@148=3 |
| BM25 | 0.000 | 1.000 | 0.125 | 0.667 | 1.000 | GridView.occupied@148=8 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GridView.occupied@148 | 3 | 2 | 4 | 2 | 4 | 3 | 8 |
| GridView.__post_init__@86 | 1 | 5 | 3 | 3 | 1 | 6 | 2 |
| GridView.entity_cells@154 | 7 | 7 | 1 | 4 | 3 | 1 | 3 |

## Q13 — development — 库存版本

角色掉血或换位置后为什么不必重新构造库存模型？

English: Why need actor HP or position changes not rebuild the inventory model?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=2 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=1 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SessionMemory._inventory_changes@414=1 |
| E | 0.000 | 1.000 | 0.111 | 0.333 | 0.667 | SessionMemory._inventory_changes@414=9 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=1 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=>50 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._inventory_changes@414 | 2 | 1 | 1 | 1 | 9 | 1 | >50 |
| CharacterFacts.inventory_model@425 | 26 | 20 | 11 | 9 | 1 | 3 | 4 |
| SessionMemory.maintained_dependency@377 | 12 | 43 | 31 | 26 | 28 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SessionMemory._inventory_changes@414=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=1 |
| E | 1.000 | 1.000 | 0.200 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=5 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=1 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=36 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._inventory_changes@414 | 1 | 1 | 1 | 1 | 5 | 1 | 36 |
| CharacterFacts.inventory_model@425 | 15 | 11 | 6 | 4 | 2 | 2 | 2 |
| SessionMemory.maintained_dependency@377 | 22 | >50 | >50 | 42 | 44 | >50 | >50 |

## Q14 — development — 库存版本

物品换主人时，世界归属和角色库存投影怎样一起更新？

English: How are world ownership and character inventory projections updated together on item transfer?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.250 | 0.500 | 0.750 | ContainerService.operate@372=10; CharacterFacts.project_item_transfer@449=4 |
| B | 0.000 | 1.000 | 0.143 | 0.250 | 0.500 | ContainerService.operate@372=12; CharacterFacts.project_item_transfer@449=7 |
| C | 1.000 | 1.000 | 0.500 | 0.500 | 0.750 | ContainerService.operate@372=13; CharacterFacts.project_item_transfer@449=2 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | ContainerService.operate@372=28; CharacterFacts.project_item_transfer@449=1 |
| E | 1.000 | 1.000 | 1.000 | 0.750 | 1.000 | ContainerService.operate@372=4; CharacterFacts.project_item_transfer@449=1 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | ContainerService.operate@372=>50; CharacterFacts.project_item_transfer@449=1 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.750 | 1.000 | ContainerService.operate@372=2; CharacterFacts.project_item_transfer@449=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.operate@372 | 10 | 12 | 13 | 28 | 4 | >50 | 2 |
| CharacterFacts.project_item_transfer@449 | 4 | 7 | 2 | 1 | 1 | 1 | 3 |
| WorldFacts.transfer_item@1329 | 17 | 14 | 8 | 9 | 6 | 7 | 4 |
| CharacterFacts.sync_inventory_change@468 | 1 | 1 | 1 | 2 | 3 | 4 | 10 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 1.000 | ContainerService.operate@372=7; CharacterFacts.project_item_transfer@449=1 |
| B | 1.000 | 1.000 | 0.333 | 0.500 | 1.000 | ContainerService.operate@372=9; CharacterFacts.project_item_transfer@449=3 |
| C | 1.000 | 1.000 | 1.000 | 0.500 | 1.000 | ContainerService.operate@372=8; CharacterFacts.project_item_transfer@449=1 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | ContainerService.operate@372=13; CharacterFacts.project_item_transfer@449=1 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | ContainerService.operate@372=4; CharacterFacts.project_item_transfer@449=1 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | ContainerService.operate@372=29; CharacterFacts.project_item_transfer@449=1 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.750 | 1.000 | ContainerService.operate@372=2; CharacterFacts.project_item_transfer@449=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.operate@372 | 7 | 9 | 8 | 13 | 4 | 29 | 2 |
| CharacterFacts.project_item_transfer@449 | 1 | 3 | 1 | 1 | 1 | 1 | 3 |
| WorldFacts.transfer_item@1329 | 10 | 10 | 6 | 6 | 5 | 4 | 4 |
| CharacterFacts.sync_inventory_change@468 | 2 | 4 | 3 | 3 | 3 | 6 | 7 |

## Q15 — development — 事务失败

SQL 报错被业务层捕获之后，哪里防止继续提交已经不可信的候选？

English: After application code catches a SQL error, what prevents committing an untrusted candidate?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 1.000 | 0.143 | 0.000 | 0.667 | RuntimeConnection.execute@1412=7; UnitOfWork.check_usable@485=14 |
| B | 0.000 | 1.000 | 0.125 | 0.000 | 0.333 | RuntimeConnection.execute@1412=12; UnitOfWork.check_usable@485=8 |
| C | 1.000 | 1.000 | 0.250 | 0.333 | 1.000 | RuntimeConnection.execute@1412=9; UnitOfWork.check_usable@485=4 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | RuntimeConnection.execute@1412=3; UnitOfWork.check_usable@485=2 |
| E | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | RuntimeConnection.execute@1412=21; UnitOfWork.check_usable@485=3 |
| T | 0.000 | 1.000 | 0.167 | 0.000 | 0.333 | RuntimeConnection.execute@1412=15; UnitOfWork.check_usable@485=6 |
| BM25 | 0.000 | 1.000 | 0.111 | 0.000 | 0.333 | RuntimeConnection.execute@1412=>50; UnitOfWork.check_usable@485=9 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 7 | 12 | 9 | 3 | 21 | 15 | >50 |
| UnitOfWork.check_usable@485 | 14 | 8 | 4 | 2 | 3 | 6 | 9 |
| SqliteStore._transaction_scope@279 | 9 | 11 | 8 | 24 | 2 | >50 | 13 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.200 | 0.667 | 0.667 | RuntimeConnection.execute@1412=5; UnitOfWork.check_usable@485=15 |
| B | 1.000 | 1.000 | 0.200 | 0.667 | 1.000 | RuntimeConnection.execute@1412=9; UnitOfWork.check_usable@485=5 |
| C | 1.000 | 1.000 | 0.200 | 0.667 | 1.000 | RuntimeConnection.execute@1412=7; UnitOfWork.check_usable@485=5 |
| D | 1.000 | 1.000 | 0.333 | 0.333 | 0.667 | RuntimeConnection.execute@1412=6; UnitOfWork.check_usable@485=3 |
| E | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | RuntimeConnection.execute@1412=17; UnitOfWork.check_usable@485=3 |
| T | 0.000 | 1.000 | 0.143 | 0.000 | 0.333 | RuntimeConnection.execute@1412=23; UnitOfWork.check_usable@485=7 |
| BM25 | 0.000 | 1.000 | 0.100 | 0.000 | 0.333 | RuntimeConnection.execute@1412=>50; UnitOfWork.check_usable@485=10 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 5 | 9 | 7 | 6 | 17 | 23 | >50 |
| UnitOfWork.check_usable@485 | 15 | 5 | 5 | 3 | 3 | 7 | 10 |
| SqliteStore._transaction_scope@279 | 4 | 4 | 4 | 17 | 2 | >50 | 19 |

## Q16 — development — 事务失败

准备好候选到真正开始持久写入之间，怎样发现另一连接已经改了事实？

English: How is a foreign writer detected between candidate preparation and starting durable persistence?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=1 |
| B | 1.000 | 1.000 | 0.333 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=3 |
| C | 1.000 | 1.000 | 0.500 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=2 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |
| T | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=2 |
| BM25 | 1.000 | 1.000 | 0.250 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=4 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore.begin_persistence@387 | 1 | 3 | 2 | 1 | 1 | 2 | 4 |
| RuntimeConnection.execute@1412 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |
| SqliteStore._transaction_scope@279 | 9 | 8 | 8 | 24 | 18 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=1 |
| B | 1.000 | 1.000 | 0.500 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=2 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SqliteStore.begin_persistence@387=1 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |
| T | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore.begin_persistence@387=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore.begin_persistence@387 | 1 | 2 | 1 | 1 | 1 | 1 | 1 |
| RuntimeConnection.execute@1412 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |
| SqliteStore._transaction_scope@279 | 8 | 8 | 10 | 21 | 18 | >50 | >50 |

## Q17 — development — 保存点回滚

局部效果失败回到保存点后，内存版本和候选事实在哪里一起恢复？

English: Where are candidate facts and memory versions restored together after rollback to a savepoint?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | RuntimeConnection.execute@1412=11 |
| B | 1.000 | 1.000 | 0.333 | 0.500 | 0.500 | RuntimeConnection.execute@1412=3 |
| C | 1.000 | 1.000 | 0.333 | 0.500 | 0.500 | RuntimeConnection.execute@1412=3 |
| D | 0.000 | 1.000 | 0.111 | 0.000 | 1.000 | RuntimeConnection.execute@1412=9 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |
| T | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | RuntimeConnection.execute@1412=25 |
| BM25 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 11 | 3 | 3 | 9 | 1 | 25 | 1 |
| UnitOfWork.savepoint@516 | 17 | 30 | 24 | 6 | 3 | 14 | 2 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | RuntimeConnection.execute@1412=11 |
| B | 1.000 | 1.000 | 0.200 | 0.500 | 0.500 | RuntimeConnection.execute@1412=5 |
| C | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | RuntimeConnection.execute@1412=2 |
| D | 0.000 | 1.000 | 0.167 | 0.500 | 1.000 | RuntimeConnection.execute@1412=6 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |
| T | 0.000 | 0.000 | 0.000 | 0.500 | 0.500 | RuntimeConnection.execute@1412=28 |
| BM25 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 11 | 5 | 2 | 6 | 1 | 28 | 1 |
| UnitOfWork.savepoint@516 | 12 | 27 | 24 | 4 | 2 | 5 | 2 |

## Q18 — development — 保存点回滚

保存点回滚后之前算过的派生结果为什么不能继续被发布？

English: Why are earlier derived results prevented from publication after savepoint rollback?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | RuntimeConnection.execute@1412=38 |
| B | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=>50 |
| C | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=38 |
| D | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=>50 |
| E | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=12 |
| T | 0.000 | 0.000 | 0.000 | 0.333 | 0.667 | RuntimeConnection.execute@1412=>50 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=24 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 38 | >50 | 38 | >50 | 12 | >50 | 24 |
| DerivedCache.resolve@31 | 12 | 3 | 3 | 4 | 3 | 8 | 3 |
| DerivedCache.publish@49 | 3 | 1 | 1 | 1 | 1 | 1 | 1 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.000 | 0.000 | 0.000 | 0.333 | 0.667 | RuntimeConnection.execute@1412=26 |
| B | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=>50 |
| C | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=28 |
| D | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=49 |
| E | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=12 |
| T | 0.000 | 0.000 | 0.000 | 0.333 | 0.667 | RuntimeConnection.execute@1412=>50 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=20 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 26 | >50 | 28 | 49 | 12 | >50 | 20 |
| DerivedCache.resolve@31 | 9 | 3 | 3 | 2 | 2 | 8 | 3 |
| DerivedCache.publish@49 | 2 | 1 | 1 | 1 | 1 | 1 | 1 |

## Q19 — development — RAM 发布

数据库提交已经成功但内存发布异常时，哪里把会话暂停？

English: Where is a session paused if durable database commit succeeded but RAM publication failed?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.250 | 0.500 | SqliteStore._transaction_scope@279=3 |
| B | 1.000 | 1.000 | 0.200 | 0.750 | 0.750 | SqliteStore._transaction_scope@279=5 |
| C | 1.000 | 1.000 | 0.250 | 0.750 | 1.000 | SqliteStore._transaction_scope@279=4 |
| D | 0.000 | 0.000 | 0.000 | 0.750 | 0.750 | SqliteStore._transaction_scope@279=14 |
| E | 1.000 | 1.000 | 1.000 | 0.250 | 0.750 | SqliteStore._transaction_scope@279=1 |
| T | 0.000 | 0.000 | 0.000 | 0.500 | 0.750 | SqliteStore._transaction_scope@279=>50 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.250 | 0.250 | SqliteStore._transaction_scope@279=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore._transaction_scope@279 | 3 | 5 | 4 | 14 | 1 | >50 | 2 |
| SessionMemory.publish@1330 | 11 | 3 | 3 | 2 | 25 | 2 | >50 |
| SessionMemory.pause@308 | 6 | 1 | 1 | 1 | 9 | 1 | 43 |
| SessionMemory.guard@284 | 14 | 15 | 9 | 3 | 10 | 8 | 48 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.250 | 0.750 | SqliteStore._transaction_scope@279=2 |
| B | 1.000 | 1.000 | 0.200 | 0.750 | 1.000 | SqliteStore._transaction_scope@279=5 |
| C | 1.000 | 1.000 | 0.250 | 0.750 | 1.000 | SqliteStore._transaction_scope@279=4 |
| D | 0.000 | 0.000 | 0.000 | 0.750 | 0.750 | SqliteStore._transaction_scope@279=15 |
| E | 1.000 | 1.000 | 1.000 | 0.250 | 0.750 | SqliteStore._transaction_scope@279=1 |
| T | 0.000 | 0.000 | 0.000 | 0.500 | 0.750 | SqliteStore._transaction_scope@279=>50 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.250 | 0.250 | SqliteStore._transaction_scope@279=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore._transaction_scope@279 | 2 | 5 | 4 | 15 | 1 | >50 | 2 |
| SessionMemory.publish@1330 | 21 | 3 | 2 | 4 | 13 | 2 | 32 |
| SessionMemory.pause@308 | 6 | 1 | 1 | 1 | 8 | 1 | 39 |
| SessionMemory.guard@284 | 7 | 10 | 8 | 2 | 10 | 9 | 40 |

## Q20 — development — 恢复

另一个连接完成恢复之后，旧连接如何知道自己的缓存已过期？

English: After another connection recovers, how does an old connection invalidate its stale caches?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SessionMemory.sync_recovery@320=1 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| E | 1.000 | 1.000 | 0.500 | 0.333 | 0.667 | SessionMemory.sync_recovery@320=2 |
| T | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| BM25 | 0.000 | 1.000 | 0.111 | 0.000 | 0.333 | SessionMemory.sync_recovery@320=9 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory.sync_recovery@320 | 1 | 1 | 1 | 1 | 2 | 1 | 9 |
| SqliteStore.reconciliation@419 | 18 | 26 | 8 | 36 | 8 | >50 | 46 |
| SqliteStore._transaction_scope@279 | 14 | 12 | 21 | 30 | 26 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | SessionMemory.sync_recovery@320=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| D | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| E | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |
| T | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=3 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SessionMemory.sync_recovery@320=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory.sync_recovery@320 | 1 | 1 | 1 | 1 | 1 | 3 | 1 |
| SqliteStore.reconciliation@419 | 10 | 22 | 11 | 26 | 22 | >50 | >50 |
| SqliteStore._transaction_scope@279 | 11 | 13 | 17 | 28 | 24 | >50 | >50 |

## Q21 — heldout — 容器重量

某件物品没有明确重量时，箱子的总重量会当零算还是保留未知？

English: Does a missing item weight become zero or propagate unknown to a container total?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | ContainerService.current_weight@149=3 |
| B | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainerService.current_weight@149=2 |
| C | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainerService.current_weight@149=4 |
| D | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainerService.current_weight@149=4 |
| E | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainerService.current_weight@149=4 |
| T | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainerService.current_weight@149=4 |
| BM25 | 0.000 | 1.000 | 0.143 | 0.333 | 1.000 | ContainerService.current_weight@149=7 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.current_weight@149 | 3 | 2 | 4 | 4 | 4 | 4 | 7 |
| ContainerService.own_weight@136 | 5 | 5 | 3 | 5 | 3 | 3 | 2 |
| ContainerService._weight@176 | 1 | 1 | 1 | 3 | 5 | 5 | 10 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainerService.current_weight@149=2 |
| B | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainerService.current_weight@149=2 |
| C | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | ContainerService.current_weight@149=3 |
| D | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainerService.current_weight@149=4 |
| E | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | ContainerService.current_weight@149=3 |
| T | 1.000 | 1.000 | 0.200 | 1.000 | 1.000 | ContainerService.current_weight@149=5 |
| BM25 | 1.000 | 1.000 | 0.250 | 0.667 | 1.000 | ContainerService.current_weight@149=4 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainerService.current_weight@149 | 2 | 2 | 3 | 4 | 3 | 5 | 4 |
| ContainerService.own_weight@136 | 5 | 5 | 4 | 5 | 5 | 3 | 3 |
| ContainerService._weight@176 | 1 | 1 | 1 | 2 | 4 | 4 | 6 |

## Q22 — heldout — 嵌套容器

候选里移动嵌套箱子后，哪些祖先的旧重量不能继续用？

English: After a nested box moves in a candidate, which ancestor weights can no longer be reused?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | ContainmentState.relocate@44=2 |
| B | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainmentState.relocate@44=2 |
| C | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainmentState.relocate@44=2 |
| D | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | ContainmentState.relocate@44=3 |
| E | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | ContainmentState.relocate@44=2 |
| T | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainmentState.relocate@44=4 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.667 | 1.000 | ContainmentState.relocate@44=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainmentState.relocate@44 | 2 | 2 | 2 | 3 | 2 | 4 | 3 |
| ContainerService._weight@176 | 4 | 3 | 3 | 2 | 3 | 2 | 2 |
| ContainmentState.relocate.<locals>.ancestors@45 | 10 | 4 | 4 | 4 | 6 | 1 | 10 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 1.000 | ContainmentState.relocate@44=2 |
| B | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainmentState.relocate@44=2 |
| C | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainmentState.relocate@44=2 |
| D | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | ContainmentState.relocate@44=2 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | ContainmentState.relocate@44=1 |
| T | 1.000 | 1.000 | 0.250 | 1.000 | 1.000 | ContainmentState.relocate@44=4 |
| BM25 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | ContainmentState.relocate@44=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ContainmentState.relocate@44 | 2 | 2 | 2 | 2 | 1 | 4 | 1 |
| ContainerService._weight@176 | 6 | 3 | 3 | 3 | 3 | 2 | 3 |
| ContainmentState.relocate.<locals>.ancestors@45 | 9 | 4 | 4 | 4 | 4 | 1 | 4 |

## Q23 — heldout — 环境快照

隐藏的天气来源会怎样影响玩家看到的结果，为什么不能暴露来源标识？

English: How do hidden weather sources affect public results without exposing source identities?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=2; EnvironmentService._public@693=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=2; EnvironmentService._public@693=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=3 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=5 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=3; EnvironmentService._public@693=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService._disclosure_inputs@669 | 1 | 2 | 2 | 1 | 1 | 1 | 3 |
| EnvironmentService._public@693 | 2 | 1 | 1 | 3 | 2 | 5 | 2 |
| EnvironmentService._environment_inputs@198 | 46 | 19 | 15 | >50 | >50 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=2 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | EnvironmentService._disclosure_inputs@669=1; EnvironmentService._public@693=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EnvironmentService._disclosure_inputs@669 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| EnvironmentService._public@693 | 2 | 2 | 2 | 2 | 2 | 2 | 3 |
| EnvironmentService._environment_inputs@198 | 26 | 12 | 7 | 17 | 46 | 24 | >50 |

## Q24 — heldout — 光照

单格光照中遮挡不确定时，哪里保留未知而不是直接判亮或暗？

English: Where does cell illumination preserve unknown when occlusion geometry is uncertain?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | LightService._illuminate_cell@102=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.667 | LightService._illuminate_cell@102=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService._illuminate_cell@102=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService._illuminate_cell@102=1 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | LightService._illuminate_cell@102=1 |
| T | 1.000 | 1.000 | 0.250 | 0.333 | 0.667 | LightService._illuminate_cell@102=4 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService._illuminate_cell@102=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LightService._illuminate_cell@102 | 1 | 1 | 1 | 1 | 1 | 4 | 1 |
| LightService.current_cell@89 | 14 | 16 | 14 | 11 | 4 | 20 | 5 |
| LightService.query_illumination@261 | 9 | 6 | 3 | 5 | 5 | 8 | 11 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | LightService._illuminate_cell@102=1 |
| B | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | LightService._illuminate_cell@102=1 |
| C | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | LightService._illuminate_cell@102=1 |
| D | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | LightService._illuminate_cell@102=1 |
| E | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | LightService._illuminate_cell@102=1 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | LightService._illuminate_cell@102=1 |
| BM25 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | LightService._illuminate_cell@102=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LightService._illuminate_cell@102 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| LightService.current_cell@89 | 5 | 8 | 8 | 5 | 3 | 12 | 3 |
| LightService.query_illumination@261 | 4 | 4 | 3 | 2 | 4 | 2 | 4 |

## Q25 — heldout — 机关索引

机关事件索引第一次准备好后，怎样安全地读取它而不复制整张表？

English: After a mechanism event index is prepared, how is it read safely without copying the whole table?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=>50; MechanismService._scene_index@47=3 |
| B | 1.000 | 1.000 | 0.500 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=>50; MechanismService._scene_index@47=2 |
| C | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=41; MechanismService._scene_index@47=1 |
| D | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=22; MechanismService._scene_index@47=1 |
| E | 1.000 | 1.000 | 0.200 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=16; MechanismService._scene_index@47=5 |
| T | 1.000 | 1.000 | 0.250 | 0.500 | 0.750 | TriggerIndex.__deepcopy__@99=8; MechanismService._scene_index@47=4 |
| BM25 | 1.000 | 1.000 | 0.200 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=5; MechanismService._scene_index@47=21 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TriggerIndex.__deepcopy__@99 | >50 | >50 | 41 | 22 | 16 | 8 | 5 |
| MechanismService._scene_index@47 | 3 | 2 | 1 | 1 | 5 | 4 | 21 |
| TriggerIndex.__getitem__@90 | >50 | 43 | 15 | 20 | 26 | 2 | 13 |
| resolve_field@228 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=>50; MechanismService._scene_index@47=1 |
| B | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=>50; MechanismService._scene_index@47=1 |
| C | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=>50; MechanismService._scene_index@47=1 |
| D | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=25; MechanismService._scene_index@47=1 |
| E | 1.000 | 1.000 | 0.200 | 0.250 | 0.250 | TriggerIndex.__deepcopy__@99=21; MechanismService._scene_index@47=5 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.750 | TriggerIndex.__deepcopy__@99=10; MechanismService._scene_index@47=1 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.250 | 0.500 | TriggerIndex.__deepcopy__@99=3; MechanismService._scene_index@47=15 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TriggerIndex.__deepcopy__@99 | >50 | >50 | >50 | 25 | 21 | 10 | 3 |
| MechanismService._scene_index@47 | 1 | 1 | 1 | 1 | 5 | 1 | 15 |
| TriggerIndex.__getitem__@90 | >50 | >50 | 17 | 21 | 24 | 5 | 8 |
| resolve_field@228 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |

## Q26 — heldout — 空间查询

多格物体旋转后，哪里检查新占地与周围角色或物体是否冲突？

English: Where are a rotated multi-cell object footprint and nearby occupancy conflicts checked?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.500 | 0.750 | ObjectSpatialService.check_candidate@491=3; ObjectSpatialService.validate_placement@589=6 |
| B | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=5; ObjectSpatialService.validate_placement@589=3 |
| C | 1.000 | 1.000 | 0.500 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=4; ObjectSpatialService.validate_placement@589=2 |
| D | 1.000 | 1.000 | 0.500 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=2; ObjectSpatialService.validate_placement@589=4 |
| E | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | ObjectSpatialService.check_candidate@491=1; ObjectSpatialService.validate_placement@589=2 |
| T | 1.000 | 1.000 | 0.500 | 0.750 | 1.000 | ObjectSpatialService.check_candidate@491=2; ObjectSpatialService.validate_placement@589=5 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.250 | 0.250 | ObjectSpatialService.check_candidate@491=1; ObjectSpatialService.validate_placement@589=30 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ObjectSpatialService.check_candidate@491 | 3 | 5 | 4 | 2 | 1 | 2 | 1 |
| ObjectSpatialService.validate_placement@589 | 6 | 3 | 2 | 4 | 2 | 5 | 30 |
| ObjectSpatialService._touching@571 | >50 | 44 | >50 | 20 | >50 | 8 | >50 |
| ObjectSpatialService._check_shape@543 | 5 | 4 | 5 | 3 | 16 | 4 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=3; ObjectSpatialService.validate_placement@589=5 |
| B | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=3; ObjectSpatialService.validate_placement@589=5 |
| C | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=3; ObjectSpatialService.validate_placement@589=4 |
| D | 1.000 | 1.000 | 0.333 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=3; ObjectSpatialService.validate_placement@589=4 |
| E | 1.000 | 1.000 | 1.000 | 0.750 | 0.750 | ObjectSpatialService.check_candidate@491=1; ObjectSpatialService.validate_placement@589=2 |
| T | 1.000 | 1.000 | 0.200 | 0.500 | 1.000 | ObjectSpatialService.check_candidate@491=5; ObjectSpatialService.validate_placement@589=7 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | ObjectSpatialService.check_candidate@491=1; ObjectSpatialService.validate_placement@589=5 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ObjectSpatialService.check_candidate@491 | 3 | 3 | 3 | 3 | 1 | 5 | 1 |
| ObjectSpatialService.validate_placement@589 | 5 | 5 | 4 | 4 | 2 | 7 | 5 |
| ObjectSpatialService._touching@571 | >50 | 33 | >50 | 23 | >50 | 9 | >50 |
| ObjectSpatialService._check_shape@543 | 2 | 2 | 2 | 2 | 5 | 2 | 23 |

## Q27 — heldout — 库存版本

关闭角色携带的箱子后，如何让里面物品的可访问库存投影失效？

English: How does closing a carried container invalidate accessibility in its owner inventory projection?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | SessionMemory._inventory_changes@414=3 |
| B | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | SessionMemory._inventory_changes@414=1 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | SessionMemory._inventory_changes@414=1 |
| D | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | SessionMemory._inventory_changes@414=1 |
| E | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=3 |
| T | 1.000 | 1.000 | 1.000 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=1 |
| BM25 | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | SessionMemory._inventory_changes@414=12 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._inventory_changes@414 | 3 | 1 | 1 | 1 | 3 | 1 | 12 |
| CharacterFacts.prepare_inventory_change@400 | 1 | 3 | 4 | 2 | 1 | 4 | 5 |
| CharacterFacts.sync_inventory_change@468 | 5 | 4 | 3 | 7 | 16 | 12 | 44 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | SessionMemory._inventory_changes@414=2 |
| B | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | SessionMemory._inventory_changes@414=2 |
| C | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | SessionMemory._inventory_changes@414=2 |
| D | 1.000 | 1.000 | 0.500 | 0.667 | 1.000 | SessionMemory._inventory_changes@414=2 |
| E | 1.000 | 1.000 | 0.333 | 0.667 | 1.000 | SessionMemory._inventory_changes@414=3 |
| T | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | SessionMemory._inventory_changes@414=3 |
| BM25 | 0.000 | 1.000 | 0.100 | 0.333 | 0.667 | SessionMemory._inventory_changes@414=10 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SessionMemory._inventory_changes@414 | 2 | 2 | 2 | 2 | 3 | 3 | 10 |
| CharacterFacts.prepare_inventory_change@400 | 1 | 4 | 6 | 1 | 1 | 4 | 3 |
| CharacterFacts.sync_inventory_change@468 | 5 | 5 | 4 | 7 | 7 | 19 | 20 |

## Q28 — heldout — 事务失败

持久提交抛错但数据库已经退出事务时，为什么不能直接重试当作失败？

English: Why must a commit exception after the database leaves its transaction be reconciled before retry?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=2 |
| B | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=3 |
| C | 1.000 | 1.000 | 0.500 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=2 |
| D | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=3 |
| E | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=3 |
| T | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | SqliteStore._transaction_scope@279=16 |
| BM25 | 0.000 | 1.000 | 0.100 | 0.000 | 0.333 | SqliteStore._transaction_scope@279=10 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore._transaction_scope@279 | 2 | 3 | 2 | 3 | 3 | 16 | 10 |
| SessionMemory.pause@308 | >50 | 46 | 46 | >50 | >50 | 33 | >50 |
| SessionRuntime.receipt@312 | >50 | >50 | >50 | >50 | >50 | 48 | >50 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=1 |
| B | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=1 |
| C | 1.000 | 1.000 | 1.000 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=1 |
| D | 1.000 | 1.000 | 0.250 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=4 |
| E | 1.000 | 1.000 | 0.333 | 0.333 | 0.333 | SqliteStore._transaction_scope@279=3 |
| T | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | SqliteStore._transaction_scope@279=11 |
| BM25 | 0.000 | 1.000 | 0.111 | 0.000 | 0.333 | SqliteStore._transaction_scope@279=9 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SqliteStore._transaction_scope@279 | 1 | 1 | 1 | 4 | 3 | 11 | 9 |
| SessionMemory.pause@308 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |
| SessionRuntime.receipt@312 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |

## Q29 — heldout — 保存点回滚

一个 SQL 失败之后回滚到失败之前的保存点，为什么同一事务还能继续？

English: Why may a transaction continue after rolling back a SQL failure to an earlier valid savepoint?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | RuntimeConnection.execute@1412=1 |
| B | 0.000 | 1.000 | 0.167 | 0.667 | 1.000 | RuntimeConnection.execute@1412=6 |
| C | 1.000 | 1.000 | 0.500 | 1.000 | 1.000 | RuntimeConnection.execute@1412=2 |
| D | 0.000 | 1.000 | 0.143 | 0.667 | 1.000 | RuntimeConnection.execute@1412=7 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | RuntimeConnection.execute@1412=1 |
| T | 0.000 | 0.000 | 0.000 | 0.333 | 0.667 | RuntimeConnection.execute@1412=20 |
| BM25 | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | RuntimeConnection.execute@1412=3 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 1 | 6 | 2 | 7 | 1 | 20 | 3 |
| UnitOfWork.savepoint@516 | 7 | 5 | 5 | 2 | 2 | 2 | 1 |
| UnitOfWork.check_usable@485 | 5 | 1 | 1 | 4 | 8 | 6 | 18 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |
| B | 0.000 | 1.000 | 0.167 | 0.667 | 1.000 | RuntimeConnection.execute@1412=6 |
| C | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | RuntimeConnection.execute@1412=1 |
| D | 0.000 | 1.000 | 0.143 | 0.667 | 1.000 | RuntimeConnection.execute@1412=7 |
| E | 1.000 | 1.000 | 1.000 | 0.667 | 1.000 | RuntimeConnection.execute@1412=1 |
| T | 0.000 | 0.000 | 0.000 | 0.667 | 0.667 | RuntimeConnection.execute@1412=23 |
| BM25 | 1.000 | 1.000 | 0.500 | 0.667 | 0.667 | RuntimeConnection.execute@1412=2 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RuntimeConnection.execute@1412 | 1 | 6 | 1 | 7 | 1 | 23 | 2 |
| UnitOfWork.savepoint@516 | 3 | 1 | 4 | 1 | 2 | 1 | 1 |
| UnitOfWork.check_usable@485 | 4 | 2 | 2 | 3 | 7 | 5 | 21 |

## Q30 — heldout — 恢复

想卸载会话内存再从已有存档恢复，哪里保证不重新套用初始模板？

English: Where do unloading and resuming a saved session avoid reapplying initialization templates?

### zh

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=1; StateMachine.resume_session@414=2 |
| B | 1.000 | 1.000 | 0.333 | 0.250 | 0.500 | StateMachine.unload_session@381=3; StateMachine.resume_session@414=6 |
| C | 1.000 | 1.000 | 0.500 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=3 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=1; StateMachine.resume_session@414=3 |
| E | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| T | 1.000 | 1.000 | 0.333 | 0.250 | 0.250 | StateMachine.unload_session@381=3; StateMachine.resume_session@414=17 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| StateMachine.unload_session@381 | 1 | 3 | 2 | 1 | 2 | 3 | 2 |
| StateMachine.resume_session@414 | 2 | 6 | 3 | 3 | 1 | 17 | 1 |
| SqliteStore.release_memory@452 | 45 | >50 | >50 | >50 | >50 | >50 | >50 |
| SqliteStore.reconciliation@419 | >50 | >50 | >50 | >50 | >50 | >50 | 42 |

### expanded

| 组 | Hit5 | Hit10 | MRR10 | Recall5 | Recall10 | 入口排名 |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| B | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| C | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| D | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| E | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |
| T | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=1; StateMachine.resume_session@414=2 |
| BM25 | 1.000 | 1.000 | 1.000 | 0.500 | 0.500 | StateMachine.unload_session@381=2; StateMachine.resume_session@414=1 |

| 标注相关节点 | A | B | C | D | E | T | BM25 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| StateMachine.unload_session@381 | 2 | 2 | 2 | 2 | 2 | 1 | 2 |
| StateMachine.resume_session@414 | 1 | 1 | 1 | 1 | 1 | 2 | 1 |
| SqliteStore.release_memory@452 | >50 | >50 | >50 | >50 | >50 | >50 | >50 |
| SqliteStore.reconciliation@419 | 48 | >50 | >50 | >50 | >50 | >50 | >50 |
