# 工具与能力路由

需要选择 Unreal MCP / VibeUE 能力时读取。表中的名字只是候选；live `list_toolsets`、`ListSkills` 和 discovery 才是当前真相。

## 发现顺序

1. `list_toolsets`：确认当前可用 Toolset。
2. `ToolsetRegistry.AgentSkillToolset.ListSkills`：获取项目内 Agent Skill 摘要。
3. `GetSkills`：只加载本阶段需要的 Skill。
4. narrow discovery：发现相关 `unreal.<Name>Service` 的精确方法与参数。
5. 实施：同一原子阶段优先批处理，MCP 调用保持串行。
6. 读回与截图：结构检查用只读 API，可见结果用截图工具。

## 任务路由表

| 地编任务 | 候选能力 | 首选验证 |
|---|---|---|
| 当前关卡、选择、Actor 清单 | Epic Editor/Actor/Scene Toolset，EditorActorSubsystem | World 路径、Actor 标签与 Transform 读回 |
| 资产查找、保存、引用 | Epic Asset Toolset，EditorAssetLibrary/Subsystem | 资产存在、包路径、dirty/save 状态 |
| Landscape 创建、导入、雕刻、图层 | VibeUE `landscape`、LandscapeService | 分辨率、Bounds、高度范围、图层权重与截图 |
| 真实地理高度和水系 | VibeUE `terrain-data` | 坐标、heightmap 分辨率、水体落点和尺度 |
| 程序化地图白盒 | VibeUE `map-blockout`、MapBlockoutService | 实现非 stub、阶段 Gate、输出文件、物化后读回 |
| 道路、河流、铁路样条 | Landscape/Water/Spline 相关服务或原生 API | 控制点、连接性、坡度、交叉和截图 |
| Actor/POI/建筑布置 | VibeUE `level-actors` 或原生 Actor 工具 | 数量、类、标签、Transform、重叠检查 |
| 场景体检与批量验收 | `scripts/level_doctor.py` + 编辑器 Python | JSON 报告、局部视图、射线与 PIE 复核 |
| 植被实例 | VibeUE `foliage`、FoliageService | FoliageType、实例数量、密度、禁放区 |
| PCG 生态与散布 | VibeUE `pcg`、PCG 原生 API | Graph/Volume/参数、生成结果、可重复性 |
| 材质与 Landscape 自动材质 | `materials`、`landscape-materials`、`landscape-auto-material` | 编译、实例参数、图层绑定、视觉截图 |
| World Partition / Data Layers | Epic World/Level 工具或原生子系统 | Grid/Data Layer/加载状态和跨单元引用 |
| 视口构图与截图 | Epic `CaptureViewport`，VibeUE `viewport` | 俯视、玩家视角、带网格/标签的图像 |
| PIE、碰撞、导航 | Epic PIE 工具，VibeUE `pie-testing` | 可进入、阻挡/穿模、路径、日志 |
| 性能与 Insights | VibeUE `frame-rate`、`profiling`、PerformanceService | Game/Render/GPU 帧耗、瓶颈判定、trace |

## 选择执行通道

- 用 `call_tool`：加载 Agent Skills、调用必须由 MCP 返回图片的截图工具、少量一次性原生 Toolset 操作。
- 用编辑器 Python：同阶段的多步 Actor/资产/服务操作、批量读回、幂等检查和统一日志。
- 用原生 Epic Toolset：VibeUE 不重复提供的通用 Actor、资产、截图、PIE 和日志能力。
- 不用原始 HTTP：只可诊断 endpoint 是否可达，不可替代 MCP 会话执行资产修改。

## VibeUE 执行约束

- 代码以 `import unreal` 开始。
- 先发现类和方法，再调用；不要从旧文档复制签名。
- 每个原子阶段输出：`CREATED`、`MODIFIED`、`SKIPPED`、`FAILED`、`VERIFIED`。
- 创建前查重；修改前读旧值；保存后再用磁盘型扫描或 metadata 验证。
- Python 没有天然回滚。live 有 Transaction/Checkpoint 时使用；没有时缩小批次并保留对象清单。
- 同样参数、同样结果连续失败两次后停止，转为诊断；不要第三次盲试。

## Live 调用陷阱

- `call_tool` 的 `toolset_name` 使用完整名，`tool_name` 使用短名，例如 `CaptureViewport`。
- 当前截图实现应同时传 `captureTransform` 与完整 `annotations`；禁用网格/标签时把数值设为 0，不省略对象。
- Lit 透视截图出现 TAA/时序拖影时，先用 Unlit + Realtime Off 判断几何，完成后恢复视图；不要误判为资产损坏。
- 资产前缀不可靠；加载对象后再判断 `StaticMesh`、`SkeletalMesh` 或 Blueprint Class。
- Pivot 不统一时，设置 Mesh/旋转/缩放后读取 Actor Bounds，再校正中心和落地高度。
