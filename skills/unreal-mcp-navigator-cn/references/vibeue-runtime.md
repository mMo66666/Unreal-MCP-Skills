# VibeUE 5.8 运行时参考

本文件用于 AI 已经确认项目安装并启用 VibeUE 5.8 后，执行具体 Unreal 编辑器任务。VibeUE 5.8 是 UE 官方 MCP endpoint 的扩展，不是独立 MCP server。

## 基本事实

- MCP URL 仍是 `http://127.0.0.1:8000/mcp`。
- 不使用旧版独立 `127.0.0.1:8088/mcp`。
- VibeUE 5.8 注册额外 Python services 和 Skill packs 到官方 MCP 栈。
- VibeUE 5.8 本地 Skill 自述为：没有单独 VibeUE server、没有 API Key、没有内置聊天窗口。
- 如果网页、截图或旧文档提到 API Key 或单独 server，先判断是否是旧版 VibeUE；UE 5.8 分支以项目内 `Plugins/VibeUE/Content/Skills/vibeue/SKILL.md` 和 live MCP 返回为准。

## 标准执行循环

1. 调 `list_toolsets`，确认官方 MCP 已连接。
2. 调 `describe_toolset` 查看 `ToolsetRegistry.AgentSkillToolset`。
3. 用 `AgentSkillToolset.ListSkills` 列出当前编辑器实际注册的 VibeUE Skills。
4. 每次具体 UE 编辑器操作前，根据本次操作用 `AgentSkillToolset.GetSkills` 读取一个或多个领域 Skill；这是操作前置步骤，不是可选优化，也不是只在任务开始时读一次。
5. 读取领域 Skill 后，查看其 frontmatter 中的 `vibeue_classes` / `unreal_classes`。
6. 用 `discover_python_class` 批量发现 live 方法签名；不要凭 Markdown 猜方法名。
7. 用 `execute_python_code` 执行 VibeUE Python services。
8. 对官方 Toolset 已覆盖的能力，继续用 `call_tool` 调官方 Toolset。
9. 写操作后 compile/save/read back。

如果 VibeUE 5.8 已启用，但 `AgentSkillToolset` 不存在、`ListSkills` 没有匹配 Skill、`GetSkills` 失败或 live MCP 没暴露 VibeUE 运行时工具，先向用户说明当前证据和回退原因，再使用官方 Toolset、live `describe_toolset` 或 Python fallback。不要把本地 `Plugins/VibeUE/Content/Skills` 文件夹当作 live Skill 已加载的证明。

这里的“具体 UE 编辑器操作”包括读取或修改当前关卡、Actor、资产、材质、蓝图、UMG、Niagara、Landscape、PCG、Animation、Input、StateTree、Gameplay Tags、性能数据等编辑器语义状态。连接探测、端口检查、`list_toolsets`、`describe_toolset`、读取 VibeUE Skill、客户端配置核对和日志基础排错不需要再触发一次 VibeUE Skill 读取。

## 效率和缓存

目标是减少 MCP 往返，但不牺牲正确性。

可在同一 MCP 会话内复用：

- `list_toolsets` 结果。
- `describe_toolset` 返回的 schema。
- `AgentSkillToolset.ListSkills` 的 Skill 名称映射。
- 已读取的 VibeUE Skill 正文和 sub-doc 正文。
- `discover_python_class` / `discover_python_function` / `discover_python_module` 结果。

这些缓存遇到以下情况必须失效：UE 重启、MCP 重连、`ModelContextProtocol.RefreshTools`、Toolset 调用返回 schema/参数错误、切换项目、启用/禁用插件、VibeUE Skill 读取失败后恢复、用户要求重新确认。

易变状态只短期复用：

- PIE 状态、当前关卡、dirty 状态、目标资产存在性、当前选择、Actor transform、Content Browser selection。
- 每个任务阶段开头读取一次；保存、关卡切换、编译、批量修改前，如果中间可能发生变化，再重新读取。
- 连续只读检查或连续低风险步骤之间，不要反复读取同一状态。

推荐把可合并的只读检查写成一次 Python 读操作，例如一次返回 PIE、当前关卡、dirty、目标资产是否存在和目录是否存在；不要拆成多个 MCP call。

## 三类工具分工

| 工具 | 用途 |
|---|---|
| `list_toolsets` / `describe_toolset` | 发现官方 Toolsets 和 schema |
| `call_tool` | 调官方 Toolset、读取 Agent Skills、执行资产/蓝图/日志等官方工具 |
| `discover_python_class` / `discover_python_function` / `discover_python_module` | 查询 VibeUE 或 UE Python live 签名 |
| `execute_python_code` | 执行 `unreal.*` Python，是 VibeUE services 的主工作方式 |

不要把 `call_tool` 和 `execute_python_code` 混为一谈：官方 Toolset 走 `call_tool`；VibeUE services 通常走 `execute_python_code`。

## 批量发现规则

`discover_python_class` 支持逗号分隔类名和 `method_filter`。为了减少 MCP 往返，优先一次发现多个类：

```text
class_name: "unreal.MaterialService, unreal.MaterialNodeService"
method_filter: "create|delete|compile|property|diagnostic|graph"
```

不要一个类一次、一个关键词一次地反复发现；这会让 MCP 显得非常慢。

## 领域 Skill 加载规则

| 任务 | 先 GetSkills |
|---|---|
| 材质、材质实例、材质图 | `materials` |
| Blueprint 资产、变量、组件、接口、事件分发器 | `blueprints` |
| Blueprint 节点图、Pin、连线、事件图 | `blueprint-graphs` |
| 新建/保存关卡、关卡 Actor、Level Editor 子系统 | `level-actors` |
| 地图 blockout、道路、POI、开放世界原型 | `map-blockout` |
| UMG Widget、UI 层级、MVVM | `umg-widgets` |
| Landscape、真实地形、自动地形材质 | `landscape`、`terrain-data`、`landscape-auto-material` |
| Niagara 系统或 emitter | `niagara-systems`、`niagara-emitters` |
| Animation、Montage、Skeleton | `animation-editing`、`animation-blueprint`、`animation-montage`、`skeleton` |
| Enhanced Input | `enhanced-input` |
| StateTree | `state-trees` |
| PCG | `pcg` |
| 性能、FPS、Insights trace | `profiling`、`frame-rate` |

如果领域 Skill 有 sub-doc 列表，例如 `materials/workflows.md` 或 `blueprints/introspection.md`，需要深入执行该领域任务时再用 `GetSkills` 读取对应 sub-doc。

对材质、蓝图、关卡、Actor、资产、UMG、Niagara、Landscape、PCG、Animation、Enhanced Input、StateTree、Gameplay Tags、性能分析等 VibeUE 覆盖领域，每次具体操作前都先加载最小匹配 Skill，再执行操作。查日志、端口、基础连接、只读 Toolset 发现、客户端配置核对等非领域操作不需要强制读取 VibeUE Skill。

## 官方 Toolset 优先的场景

VibeUE 5.8 中不少旧能力已经让位给官方 Toolset。遇到下面任务优先 `call_tool`：

| 任务 | 官方 Toolset |
|---|---|
| PIE 启停、PIE 状态、视口截图 | `EditorToolset.EditorAppToolset` |
| 日志读取、过滤、tail | `EditorToolset.LogsToolset` |
| 资产查找、保存、移动、导入 | `editor_toolset.toolsets.asset.AssetTools` |
| 创建基础材质、材质实例 | `editor_toolset.toolsets.material.*` |
| 创建 Blueprint、加变量、加函数图、编译 Blueprint | `editor_toolset.toolsets.blueprint.BlueprintTools` |
| 单个 Gameplay Tag 增删改查 | `GameplayTagsToolset` |

如果领域 Skill 说某个 VibeUE service 方法已经被 cut，必须改走官方 Toolset。

## 材质高频坑

- 修改已有材质前先导出并阅读当前材质图，不要盲目追加节点。
- `MaterialNodeService.create_parameter` / `create_function_call` 返回对象，连接时使用 `.id`。
- 材质函数输入要用 bare name，例如 `TextureObject`，不要用 `TextureObject (T2d)` 这种显示名。
- 非平凡材质连线后用 `MaterialNodeService.get_material_diagnostics(path)` 验证编译、纹理引用和错误；不要只靠 `get_used_textures`。
- 设置材质属性后检查返回值；`set_property` 返回 `False` 不一定抛异常。
- 最后执行 compile/save/read back。

## Blueprint 高频坑

- 官方 `BlueprintTools` 的 UObject/UClass 参数通常要传 `{ "refPath": "/Game/Dir/BP.BP" }`，不是裸字符串。
- Blueprint asset object path 需要 `/Game/Dir/BP.BP`；只有 package path `/Game/Dir/BP` 经常不够。
- VibeUE 的 `unreal.BlueprintService.*` Python 方法通常仍使用裸字符串路径。
- 创建 Blueprint、加变量、加函数图、编译 Blueprint 优先走官方 `BlueprintTools`。
- 节点级图编辑要额外加载 `blueprint-graphs`。
- CDO 读写返回和写入多为字符串；布尔 C++ 属性名在 `get_property` / `set_property` 中保留 `b` 前缀，例如 `bReplicates`。
- 编辑后必须 compile，检查 `success` / `num_errors`，再 save。

## 失败处理

| 现象 | 处理 |
|---|---|
| 找不到 VibeUE Skills | 重新 `list_toolsets`，确认 `AgentSkillToolset` 存在；检查插件启用和 UE 重启 |
| Skill 里写的 API 调不通 | 先 `discover_python_class` 查 live 签名；版本漂移时以 live 签名为准 |
| `execute_python_code` 超时 | 不要立即重复写操作；先查日志、资产状态和是否部分成功 |
| 官方 Toolset 和 VibeUE Skill 都能做 | 简单、低层资产操作优先官方 Toolset；领域高层流程按 VibeUE Skill |
| 文档与 live MCP 冲突 | live `describe_toolset`、`GetSkills`、`discover_python_class` 优先 |
| VibeUE 已启用但未读 Skill 就要操作 | 停止本次具体操作，先 `ListSkills` / `GetSkills`；读取不到时说明原因再回退 |
