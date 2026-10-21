# 规则、世界观与工程参考资料

核对日期：**2026-10-21（Asia/Shanghai）**。本页是统一查阅入口；[Module Contracts](./MODULE_CONTRACTS.md) 仍拥有跨模块架构／状态所有权，规则目标与当前实现分开取证，[MVP Scope](./MVP_SCOPE.md) 拥有产品范围。外部资料提供依据和方法，不自动改变项目决定、规则集绑定或当前 Session 事实。

## 查阅与登记要求

- 设计或实现前先读 MC 和对应领域文档。涉及规则行为时查绑定版本的相关原文，不要求每次小改动读完全部规则书；涉及世界观时先确认具体 Package 的设定与版本。
- 分别记录官方规则、项目明确改编、工程选择、目标设计与当前实现。发现资料与项目规定冲突时指出差异，不静默改规则或架构；需变更时另行明确决定。
- 记录标题、作者／机构、链接或合法本地来源、版本／版次、章节／页码、核对日期、用途／模块及核实程度。不能访问的原文明确标为未核实；不把模型记忆、推测、产品介绍页或搜索摘要当作机制验收。
- 本页要求开发阶段查阅；普通游戏运行时使用本地批准的素材和显式绑定，不因此新增联网查规则依赖。缓存、Snapshot、索引、查询范围与保存边界遵循 [MC §2.3–§2.4](./MODULE_CONTRACTS.md#23-运行时数据复用派生-snapshot-与版本有效性-decided)。

## A. D&D 规则依据

**项目当前明确基线保持 PHB 2024、DMG 2024、MM 2025、SRD 5.2.1。** 本任务不升级规则、不修改规则数据、不改变 Package／Session 的 RulesetBinding。SRD 条目存在不代表 RE 已支持，RE 某切片通过也不代表 SM 已接入。

| 标题／来源与链接 | 版本与已核实程度（2026-10-21） | 用途与适用范围 |
|---|---|---|
| Wizards / D&D Beyond — [System Reference Document](https://www.dndbeyond.com/srd) | 已读取官方发布／下载入口，当前提供 v5.2.1；入口会变化，机制核对使用下列固定 PDF | 确认来源与版本；全部规则模块 |
| Wizards — [System Reference Document 5.2.1 固定英文 PDF](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf) | 已读取下表相关章节及页码；不是整本逐条验收 | 开放规则原文；RE 机械规则、SM World／对象／时间／感知输入 |
| D&D Beyond — [Updates in the Player's Handbook (2024)](https://www.dndbeyond.com/posts/1810-updates-in-the-players-handbook-2024) | 已核对官方版本说明；**PHB 2024 完整正文未读取／未逐章核实** | 确认采用版本；具体职业／行动／装备规则仍须相应原文，不能用说明页代替 |
| Wizards WPN — [2024 Dungeon Master's Guide](https://wpn.wizards.com/en/products/2024-dungeon-masters-guide) | 已核对产品版本信息；**DMG 2024 完整正文未读取／未逐章核实** | GM、环境、物体、陷阱主题的后续原文查阅入口；产品信息不证明具体机制 |
| D&D Beyond — [Updates in the Monster Manual (2025)](https://www.dndbeyond.com/posts/1913-updates-in-the-monster-manual-2025) | 已核对官方版本说明；**MM 2025 完整正文未读取／未逐章核实** | 怪物 stat block／能力的版本追踪；具体非 SRD 能力需合法原文另核 |

以下页码使用该英文 PDF 印刷页码（本文件与阅读器页序一致），章节为查阅定位；只记录相关主题，不复制整章或冒险正文。

| 主题 | SRD 5.2.1 章节／页码 | 用途与适用模块／核实边界 |
|---|---|---|
| 物体互动 | [Exploration — Interacting with Objects, pp.11–12](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=11) | 已核对条目；WorldObject／Openable／Container 的情境与操作前提，不能统一推定所有互动免费 |
| 行动成本 | [Actions, pp.9–10；Combat — Your Turn, pp.13–14](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=9) | 已核对行动与物体互动时序入口；RE／Combat Handler；具体操作再核对应物品／能力文本，不推定战斗取放已接线 |
| 负重与装备 | [Equipment, pp.89–101（Adventuring Gear pp.94–99）；Carrying Capacity, p.178](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=178) | 已核对负重条目与装备／重量表位置；Container、Character、RE。角色负重、容器容量与物品外部重量贡献分别处理；不是所有装备逐项核实 |
| 光照与感官 | [Vision and Light, p.11；Cover, p.15；Rules Glossary 对应感官条目](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=11) | 已核对光照与 Cover；Light／Perception／Spatial／RE；特殊感官逐项查阅，未宣称全部例外已核实 |
| 物体受损 | [Breaking Objects, pp.177–178；Damage Threshold, p.180](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=177) | 已核对条目和表位置；Durability／RE。实际材质、伤害与破坏后果需逐项映射；不因有条目便声称真实物体攻击已实现 |
| 环境 | [Gameplay Toolbox — Environmental Effects, pp.195–196](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=195) | 已核对章节范围；Environment／WorldTime／RE；项目环境字段和防护投影是工程表达，不是官方数据 Schema |
| 陷阱 | [Gameplay Toolbox — Traps, pp.199–201](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=199) | 已核对章节与示例入口；Mechanism／World／RE；选用陷阱的触发、解除、DC 和后果逐项查原文，未验收全部陷阱 |
| 持续效果 | [Spells — Duration, p.106；Concentration, p.179](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf#page=106) | 已核对持续时间／专注条目；Effects／RE／时间协调；具体法术的重复触发、区域、终止条件仍查其条目及当前支持 |

**官方、改编与实现的边界：** 原文决定官方规则出处；项目明确改编须另列原规则、改编、理由、适用 Package／ruleset 及批准状态。Container 统一两层嵌套、未知测量的拒绝策略、局部准入及缓存方案是项目约束／工程选择，不能标为 SRD 原文。当前能力须核对 RE 的 [capabilities.md（固定 SHA）](https://github.com/agentic-trpg/trpg-rules-engine/blob/f18e0ad0d0bb6641efb050b51bf919dd41a8631f/docs/capabilities.md)、对应源码／测试和真实消费者；该矩阵也是实现资料，不是官方规则依据。本次仅有限静态查阅，见 [MC §1.7](./MODULE_CONTRACTS.md#17-2026-10-21-运行时复用与资料核对)，没有重新运行 RE／SM 业务验收。

## B. 世界观与冒险资料

采用 D&D 规则不自动采用任何特定世界观。正式设定由具体 Package 的已批准来源确定；创作参考不直接成为事实，也不绕过实例化／授权。禁止凭 Codex 记忆补入当前 Session 地名、人物、历史或秘密，禁止将某一冒险设定硬编码成通用引擎规则。

| 已有采用／候选资料 | 来源、版本与核实程度（2026-10-21） | 用途与适用范围 |
|---|---|---|
| First Blush（D&D Duet） | 项目采用依据为 [MVP Scope](./MVP_SCOPE.md) 的既有决定；本次未读取合法冒险正文，未确认具体出版版本、世界／年代或全部改编 | 保留首个本地私有 MVP 验收场景的选择；不据此新增任何世界设定或公开剧情。具体 Package 制作前补核，不宣称已完成整部冒险适配 |
| 具体 Package 的设定书／冒险正文／项目原创资料 | 本次未提供可核实的具体 Package 来源清单，保持待确认；不默认采用 Forgotten Realms、Greyhawk 或其他世界 | 按下列登记要求，在合法私有材料中逐项记录；通用引擎只处理批准的结构和事实 |

每个 Package 的人工来源清单应记录：资料标题、作者／出版方、合法来源链接或本地定位、版次／修订、采用的世界与年代、涉及章节／页码、采用范围、项目改编与差异、核对人／日期及未核实项；再明确标为“正式采用”或“创作参考”。这是审阅要求，**不是本次新增或冻结的机器字段／Loader Schema**，也不要求公开受限制的本地路径或正文。创建／初始化／恢复和来源引用边界见 [Adventure Package Schema](./ADVENTURE_PACKAGE_SCHEMA.md) 与 MC §2.4。

本次不新增未经确认的世界设定，不复制完整冒险内容；已有 First Blush 正文、地图与实质性改编的私有保存约束继续适用。

## C. 工程设计参考

以下资料用于方法研究；本项目采用的具体决策以 MC 和领域文档为准，不因框架示例引入新的执行器、权威状态或后端依赖。

| 标题／作者或机构／链接 | 版本或核对日期与已核实程度 | 用途与适用范围 |
|---|---|---|
| Robert Nystrom — [Game Programming Patterns: Dirty Flag](https://gameprogrammingpatterns.com/dirty-flag.html) | 2026-10-21；直接打开失败，经作者站点的搜索索引正文核对 Intent、The Pattern、When to Use It 及失效／内存讨论；未核实实时完整页面 | 理解派生结果缓存、依赖变化、按需重算和增量维护的取舍；空间／环境／容器等。项目增量前提仍由 MC §2.3 约束 |
| SQLite — [Isolation In SQLite](https://www.sqlite.org/isolation.html) | 2026-10-21；已读取隔离与 WAL snapshot isolation 相关正文 | 事务隔离、旧读取一致性与缓存发布边界；Store／UnitOfWork／缓存消费者。数据库隔离本身不自动保证应用缓存安全 |
| Epic Games — [Saving and Loading Your Game](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine) | 2026-10-21；页面显示 UE 5.8，已读取 SaveGame／保存加载及异步保存相关说明 | 运行状态与存档设计参考；Session／领域保存和恢复。不采用 Unreal API／存储布局，不改变 MVP 的战斗恢复边界 |

共同原则和领域应用：[MC §2.3](./MODULE_CONTRACTS.md#23-运行时数据复用派生-snapshot-与版本有效性-decided)、[World Container](./WORLD_SUBSYSTEM_DESIGN.md#21b-容器重量派生与跨操作复用)、[State Machine Architecture](./STATE_MACHINE_ARCHITECTURE.md)。资料不能访问或发生版本变化时，保留未核实说明并按任务重新核对，不静默升级项目决定。
