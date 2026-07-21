# Unreal MCP Skill 路由

先把用户需求归为最小领域，再读取对应 VibeUE Skill 或本 Skill reference。不要全量读取 VibeUE Skills，也不要因为不确定就读所有参考文件。

## 执行顺序

1. 判断任务是否需要 live UE 编辑器状态；纯说明、配置核对、文件级测试关卡复制不需要 live MCP。
2. 判断风险模式：快速、标准、严格、排错。
3. 选择 1-2 个最小领域 Skill；复合任务按阶段读取，不要预读全部。
4. 同一 MCP 会话、同一项目、同一领域复用已读取 Skill、Toolset schema 和 class discovery。
5. 只有 UE/MCP 重连、切换项目、领域变化、schema 报错、高风险批量写操作或验证不一致时重新读取。

## VibeUE 领域路由

| 需求 | 读取 Skill |
|---|---|
| 材质、材质实例、材质节点 | `materials` |
| Actor 摆放、移动、Transform、关卡内对象 | `level-actors` |
| 灰盒、道路、房间、POI、地图布局 | `map-blockout`；需要摆 Actor 时再读 `level-actors` |
| 蓝图资产、变量、组件、父类 | `blueprints` |
| 蓝图图表、节点、连线、执行流 | `blueprint-graphs` |
| 资产导入、移动、重命名、保存、查询 | `asset-management` |
| UMG/UI Widget | `umg-widgets` |
| Niagara 系统/发射器 | `niagara-systems` / `niagara-emitters` |
| Landscape 地形编辑 | `landscape` |
| 地形自动材质/地形材质 | `landscape-auto-material` / `landscape-materials` |
| 真实地形、高度图、地图数据 | `terrain-data` |
| PCG | `pcg` |
| Enhanced Input | `enhanced-input` |
| Gameplay Tags | `gameplay-tags` |
| StateTree | `state-trees` |
| 动画蓝图、蒙太奇、AnimSequence、Skeleton | `animation-blueprint` / `animation-montage` / `animsequence` / `skeleton` |
| MetaSound、Sound Cue | `metasounds` / `sound-cues` |
| 视口、相机、截图 | `viewport` |
| PIE/运行验证 | `pie-testing` |
| 性能分析、帧率 | `profiling` / `frame-rate` |
| 项目/引擎设置 | `project-settings` / `engine-settings` |

## 本 Skill Reference 路由

| 需求 | 读取 reference |
|---|---|
| 设计师首次/再次连接 | `designer-workflow.md` |
| 客户端配置、Codex/Claude/Cursor/Gemini 差异 | `configuration-reference.md` |
| 判断是否是 UE/MCP 任务 | `triggers.md` |
| Toolset/call_tool 参数、蓝图读取、材质调用坑 | `mcp-tools.md` |
| 具体编辑器操作流程 | `operation-playbooks.md` |
| VibeUE 安装/启用/验证 | `vibeue-58.md` |
| VibeUE runtime 类发现或回退策略 | `vibeue-runtime.md` |
| 编译、Cook、Automation、命令行验证 | `automation-reference.md` |
| 连接失败、慢、断连、崩溃、工具缺失 | `troubleshooting.md` |

## 禁止项

- 不要全量读取 VibeUE Skills。
- 不要把 VibeUE Skill 当作无条件最高优先级；如果 VibeUE 示例与本 Skill 的安全边界冲突，尤其 `level-actors` 里的 `new_level_from_template` / `load_level` / `__TempSwitch` 示例，以本 Skill 的临时关卡保护模式为准。
- 不要正常路径默认读取 `troubleshooting.md`。
- 不要每步重复 `describe_toolset`、PIE 检查或 `GetSkills`。
- 不要把测试产物 `LV_NewLevel_*` 当长期模板源。
- 不要把文件级 `.umap` 复制说成 UE 编辑器已加载或资产系统已刷新。
