# Unreal MCP 操作剧本

本文件用于执行具体 UE 编辑器任务。统一流程是：读检查 -> 说明预期效果 -> 串行调用 -> 读回验证。不要并发调用 Unreal MCP。

## 通用执行协议

1. 先判断执行模式：需要编辑器状态和资产语义时用 live MCP；构建、Cook、Automation、Python commandlet 和日志解析优先命令行。
2. 用尽量少的只读调用确认环境：连接、当前关卡、选中对象、PIE 状态、目标资产是否存在；能合并成一次 Python 读操作时不要拆成多个 MCP call。
3. 陌生项目先检查 `AgentSkillToolset` 是否有项目内 Skill；匹配时优先遵守项目约定。
4. 如果项目启用 VibeUE 5.8，且即将执行材质、蓝图、关卡、Actor、资产、UMG、Niagara、Landscape、PCG、Animation、Enhanced Input、StateTree、Gameplay Tags、性能分析等具体 UE 编辑器操作，先确认该领域 Skill 是否已经在当前 MCP 会话中读取并缓存。未缓存、领域变化、UE/MCP 重连、schema 报错或高风险批量写操作时，通过 `AgentSkillToolset.GetSkills` 读取最小匹配领域 Skill；读取不到时说明原因再回退官方 Toolset/live schema。
5. 对用户说明将要修改什么。
6. 高风险编辑先获得明确授权。
7. 串行调用工具，每一步等结果返回。
8. 保存需要保存的资产。
9. 用单独的只读工具验证结果。
10. 总结创建/修改的路径、对象和未完成事项。

## 性能优化协议

- 在同一 MCP 会话中缓存稳定发现结果：Toolset 列表、Toolset schema、VibeUE Skill 名称映射、已读取 Skill 正文、Python class/function/module discovery。
- 遇到 UE 重启、MCP 重连、刷新工具、切换项目、插件启停、schema/参数错误、Skill 读取失败后恢复时，丢弃上述缓存并重新发现。
- PIE、当前关卡、dirty、资产存在性、选择、Actor transform 是易变状态，只在当前任务阶段短期复用。
- 每个任务开始检查一次 PIE；保存、关卡切换、编译、批量编辑前按风险复查。不要在连续低风险读操作之间重复检查 PIE。
- 目标路径、目录存在性、当前关卡和 dirty 状态尽量合并读取；创建后验证也尽量合并成一次只读检查。
- 成功路径不默认读日志；只有失败、warning、超时、返回不明或验证不一致时再读日志。
- 已知 Toolset 参数时不要反复 `describe_toolset`；只有首次使用、不确定 schema、参数错误、工具刷新或重连后再 describe。
- MCP 暂时不可用时不要固定 `Start-Sleep 20` 等待；改用短轮询检查端口/进程。若任务已经选择文件级降级路径，且不需要 live 编辑器状态，直接执行文件级验证，不再等待 MCP 恢复。

## 生产执行模式

优先按风险选择模式，避免每个操作都走最重流程。

| 模式 | 适用场景 | 最小检查 | 验证 |
|---|---|---|---|
| 快速 | 低风险、可撤销、单资产/单 Actor、测试目录操作 | 复用缓存；只检查目标存在性和必要上下文 | 读回目标属性或文件/资产存在 |
| 标准 | 保存资产、创建材质/蓝图节点、切换或创建关卡 | 任务开始合并检查 PIE/current/dirty/目标存在性；读取未缓存领域 Skill | 写后读回关键状态，不默认读日志 |
| 严格 | 删除、批量移动/重命名、批量保存/编译、改项目配置、生产关卡 | 明确授权、保存/备份提醒、重新确认 schema 和关键状态 | 读回结果、必要时日志/编译/测试 |
| 排错 | MCP 断连、超时、崩溃、工具缺失、验证不一致 | 端口、进程、日志、`list_toolsets` | 找到原因后回到对应模式 |

同一制作会话中，材质连续编辑、Actor 连续摆放、蓝图同图表连续改动时，不要每一步重读 VibeUE Skill、重查 PIE 或重跑 `describe_toolset`；只有保存、切图、编译、批量写、失败或用户手动改变编辑器状态后再刷新必要状态。

## 连接验证

1. 确认项目根和 `.uproject`。
2. 本地端口检查：`Test-NetConnection -ComputerName 127.0.0.1 -Port 8000`。
3. 调用 `list_toolsets`。
4. 如果只看到 `ToolsetRegistry.AgentSkillToolset`，停止具体编辑任务，转排错；如任务是读取项目内 Skill，可继续 `AgentSkillToolset`。
5. 如果看到目标 Toolset，继续 `describe_toolset`。

## 新建测试材质

1. 确认不在 PIE。
2. 调用 `MaterialTools.create_material`，目标目录优先 `/Game/MCP_Test`。
3. 调用 `AssetTools.save_assets` 保存材质。
4. 调用 `AssetTools.get_asset_class` 验证 class 为 `Material`。
5. 告诉用户资产路径。

## 新建菲尼尔材质

1. 创建材质，例如 `/Game/MCP_Test/M_MCP_Fresnel`。
2. 如果项目启用 VibeUE 5.8，先确认 `materials` Skill 和相关 class discovery 是否已有缓存；未缓存时通过 `AgentSkillToolset.GetSkills` 加载 `materials`，再批量发现 `unreal.MaterialService, unreal.MaterialNodeService` 的 live 签名。只有需要 VibeUE runtime 调用细节或回退策略时，才读取 `vibeue-runtime.md`。
3. 用 `MaterialTools.list_expression_classes` 或 VibeUE `MaterialNodeService.discover_types` 确认 `MaterialExpressionFresnel`、`MaterialExpressionConstant3Vector`、`MaterialExpressionMultiply`。
4. 用 `MaterialTools.add_expression` 或 VibeUE graph API 逐个创建 Fresnel、颜色、Multiply 节点。
5. 用 `ObjectTools.list_properties` 或 VibeUE property API 读取颜色节点属性。
6. 用 `ObjectTools.set_properties` 设置颜色；`values` 必须是 JSON 字符串。
7. 串行连接 Fresnel -> Multiply.A，颜色 -> Multiply.B。
8. 连接 Multiply 到 `MP_BaseColor`，需要发光效果时连接到 `MP_EmissiveColor`。
9. 调用 `MaterialTools.recompile` 或 `MaterialService.compile_material`。
10. 调用 `AssetTools.save_assets` 或 `EditorAssetLibrary.save_asset`。
11. 若使用 VibeUE 材质图能力，优先用 `MaterialNodeService.get_material_diagnostics(path)` 验证；否则读回材质 class 或输出连接验证。

## 新建测试关卡

1. 询问是否可以创建新关卡；如果用户没有指定名称，使用不易冲突的测试名，例如 `/Game/MCP_Test_Level/LV_NewLevel`，存在时追加递增后缀。
2. 先确认不在 PIE。
3. 如果项目启用 VibeUE 5.8，先通过 `AgentSkillToolset.GetSkills` 读取 `level-actors`；如果用户要做地图布局或 blockout，再读取 `map-blockout`。不要跳过 VibeUE Skill 后直接猜 Python API。
4. 读完 VibeUE `level-actors` 后，按“正常快速路径优先，异常保护兜底”执行。不要因为文档里有崩溃案例就默认走最慢路径；只有当前关卡是 `/Temp/Untitled_*`、刚崩溃恢复、刚重连 MCP、存在多个 UnrealEditor 进程或当前关卡未保存时，才启用临时关卡保护模式。
5. 读取当前关卡路径和 dirty/未保存状态。新建关卡会切换当前编辑器关卡；如果当前关卡有未保存修改，先询问是否保存当前关卡或取消操作。
6. 如果当前关卡是 `/Temp/Untitled_*`，进入“临时关卡保护模式”：禁止通过 MCP/Python 调用 `load_level`、`new_level`、`new_level_from_template` 或任何会关闭/替换当前 World 的接口。只能创建/复制 `.umap` 资产但不加载，或让设计师先手动打开一个已保存的稳定关卡/重启 UE 后再继续 live 加载。
7. 用 Asset/Editor 只读工具确认目标 package 不存在；如果存在，不要覆盖，改名或询问用户。
8. 如果用户只说“新建关卡”或希望得到常规 Basic Level，目标是从 `/Engine/Maps/Templates/Template_Default` 得到带地板、天空、灯光和 PlayerStart 的关卡，而不是调用 `new_level`。
9. 正常快速路径：当前关卡已保存稳定、无 dirty、非 PIE、UE 单实例、目标不存在时，按 VibeUE `level-actors` 建议调用 `LevelEditorSubsystem.new_level_from_template(target, "/Engine/Maps/Templates/Template_Default")`。
10. 如果正常快速路径不满足，先不要硬切换 World。根据失败原因选择：保存/关闭当前临时关卡、文件级复制生成 `.umap` 但不加载，或在用户明确同意后进入更严格的 live fallback。
11. 只有正常快速路径不可用但当前 World 仍稳定时，才考虑复制/duplicate 模板到目标后加载；复制不应覆盖已有目标，加载前仍需处理当前关卡 dirty 状态。
12. 如果 live API 名称或参数不确定，先用 live 能力确认 `unreal.LevelEditorSubsystem`、`unreal.UnrealEditorSubsystem`、`unreal.EditorLoadingAndSavingUtils`、`unreal.EditorAssetLibrary` 中实际可用的方法，不要凭记忆猜 API。
13. 如果用户明确要求空白关卡，且当前关卡不是 `/Temp/Untitled_*`，才使用 `LevelEditorSubsystem.new_level(target)`。
14. 不要使用 deprecated `unreal.EditorLevelLibrary`；Actor 操作使用 `EditorActorSubsystem`，保存当前关卡世界使用 `UnrealEditorSubsystem.get_editor_world()` + `EditorLoadingAndSavingUtils.save_map(world, target)` 或 `LevelEditorSubsystem.save_current_level()`。
15. Python fallback 会创建/保存 map，并可能切换当前编辑器关卡；调用前说明会切换关卡。若处于 `/Temp/Untitled_*`，只允许“不加载目标关卡”的创建/复制路径。
16. 如果 Python 返回 deprecation warning，不要直接判失败；记录 warning，继续用读工具验证当前关卡路径和资产存在性。但如果 warning 来自 `EditorLevelLibrary`，下次要改用非 deprecated API。
17. 如果使用 `EditorAssetLibrary.duplicate_asset` 复制关卡模板，注意它可能把返回的 `World` 对象留在 Python/UE 引用里。必须避免在 `/Temp/Untitled_*` 状态下 duplicate 后立即 `load_level` 或让设计师马上双击打开同一 `.umap`；`del` 返回值和 `gc.collect()` 只能作为补救尝试，不是已验证安全保证。
18. 如果出现 `World Memory Leaks`、UE assertion、MCP 端口断开或 UnrealEditor 进程消失，立即停止所有 UE 写操作；不要重试同一创建命令，也不要让设计师反复双击刚生成的 `.umap`。让用户重启 UE，确认只有一个 UnrealEditor 进程，再重新连接 MCP。
19. 保存关卡后，读回当前关卡路径、目标资产存在性和 asset class/world 类型验证。
20. 总结最终路径、是否切换当前关卡、是否出现 warning、是否已保存。

MCP 不可用时的低风险文件级降级路径：

- 只适用于测试/临时 Basic Level，且用户接受“不切换当前编辑器关卡，只生成 `.umap` 文件”。
- 源文件必须是已验证为 Basic Level 的稳定模板 `.umap`。优先使用项目固定模板：`Content/MCP_Templates/TPL_BasicLevel.umap`，对应资产路径 `/Game/MCP_Templates/TPL_BasicLevel`。
- 如果项目固定模板不存在，且只是测试/临时关卡，可在确认 UE 5.8 EngineRoot 后使用引擎模板文件：`Engine/Content/Maps/Templates/Template_Default.umap`。本机常见路径示例：`G:/Software/UE_5.8/Engine/Content/Maps/Templates/Template_Default.umap`。不要把这个路径硬编码到其他机器；先从 `.uproject`、UE 进程路径、日志或设计师确认推断 EngineRoot。
- 不要把目标目录中随手生成的 `LV_NewLevel_*` 当长期模板源。它们可能被设计师删除、移动、重命名，或只是某次测试产物。
- 如果固定模板不存在、被用户删除或无法证明是 Basic Level，停止文件级复制降级；改走 live MCP/UE 资产系统路径，或询问用户是否允许先重建固定模板。
- 目标 `.umap` 必须不存在；禁止覆盖已有文件。
- 用文件系统复制后，只验证文件存在、大小、时间戳或哈希；不要声称 UE 已加载该关卡或资产注册已刷新。
- 文件级复制发生在 UE 编辑器外部，Content Browser 可能不会立即显示新关卡。完成后必须提示设计师右键刷新 Content Browser、重新打开目录，或重启 UE；MCP 恢复后也可通过 live 资产系统刷新/打开并读回验证。
- MCP 恢复后，如果用户需要在编辑器里打开该关卡，再通过 live MCP 或让设计师手动打开，并读回验证。

关卡创建的判断规则：

- 用户说“新建关卡”可视为轻量写操作授权，但切换当前关卡前仍要处理当前关卡未保存状态。
- `SceneTools` 能加载/查询关卡不代表能创建关卡；没有 `create/new level` 工具时，不要硬猜工具名。
- `AssetTools` 能查找/保存/建目录不代表能创建 `.umap`；它没有 Level 创建接口时，转 Python fallback。
- 目标路径使用 package path，例如 `/Game/MCP_Test_Level/LV_NewLevel`；不要使用磁盘 `.umap` 绝对路径作为资产路径。
- “Basic/默认/常规”关卡必须来自模板 `/Engine/Maps/Templates/Template_Default`。当前关卡已保存稳定、无 dirty、非 PIE、UE 单实例、目标不存在时，`new_level_from_template` 是正常快速路径；空白关卡才使用 `new_level`。
- VibeUE `level-actors` 会把 `new_level_from_template` 写成 Basic Level 的推荐路径；本剧本接受这个正常路径，但当 live 状态不稳定或处于 `/Temp/Untitled_*` 时，本剧本覆盖 VibeUE 示例。
- 当前关卡为 `/Temp/Untitled_*`、刚崩溃恢复、刚重连 MCP、或存在多个 UnrealEditor 进程时，不要直接调用 `new_level_from_template`。
- 当前关卡为 `/Temp/Untitled_*` 时，也不要调用 `load_level` 加载刚复制/duplicate 出来的目标关卡；这和 `new_level_from_template` 属于同一类 World 替换风险。
- 在 `/Temp/Untitled_*` 状态下创建 Basic Level 的安全结果是“目标 `.umap` 已生成但未加载”。如果用户需要当前编辑器打开该关卡，让设计师先手动打开已保存稳定关卡或重启 UE，再通过 Content Browser 打开目标关卡。
- 如果已经选择文件级降级路径，不再等待 MCP 恢复，也不需要检查 PIE/dirty/current level；这些状态只影响 live 编辑器加载/保存，不影响单个新文件复制。
- live 编辑器路径的成功条件不是 Python 返回 true，而是当前关卡路径已切换到目标、目标资产存在、保存后 dirty 状态可接受。
- 文件级降级路径的成功条件是目标 `.umap` 文件存在、未覆盖旧文件、大小/时间戳或哈希与固定模板符合预期；它不能证明编辑器已加载或资产系统已刷新。最终说明里必须提醒刷新 Content Browser。
- 如果 live `duplicate_asset` 后用户双击刚生成关卡也崩溃，停止继续打开该文件；把它视为可能被 live 会话引用污染的测试产物。重启 UE 后优先删除并用文件级复制或稳定关卡下的受控流程重建。

## Actor 排列或变换

1. 用 Editor/App Toolset 读取当前选中 Actor。
2. 如果选中为空，停止并让用户选择 Actor。
3. 读每个 Actor 的 label 和 transform。
4. 说明排列规则，例如 X 轴间距 200。
5. 串行设置 transform。
6. 读回 transform 验证。

## 资产保存和批量修改

1. 批量操作前要求用户保存项目或确认已有版本控制。
2. 用 AssetTools 查询 dirty/editable/checked-out 状态。
3. 对每个资产串行处理。
4. 保存后查询 dirty 状态或 asset class/path。
5. 报告成功、失败、跳过列表。

## 读取蓝图逻辑

1. 用 `BlueprintTools.list_graphs` 读取图表。
2. 用 `BlueprintTools.get_graph` 获取目标 graph refPath。
3. 尝试 `read_graph_dsl`。
4. 如果 DSL 为空或失败，用 `find_nodes` + `get_node_infos`。
5. 需要一条执行链时，用 `get_connected_subgraph`。
6. 总结执行流和数据流，不要把节点位置当执行顺序。

## VibeUE 5.8 领域任务

1. 确认 VibeUE 已启用并重启 UE。
2. 调 `list_toolsets` 和 `describe_toolset`，确认 `AgentSkillToolset`、`execute_python_code`、`discover_python_class` 是否可用。
3. 用 `AgentSkillToolset.ListSkills` 列 live Skill。
4. 每个领域首次操作前，用 `AgentSkillToolset.GetSkills` 读取最小匹配领域 Skill，例如 `materials`、`blueprints`、`level-actors`、`asset-management`、`pcg`；同一会话同一领域复用缓存，除非 UE/MCP 重连、领域变化、schema 报错、高风险批量写操作或验证结果不一致。
5. 根据领域 Skill 的 `vibeue_classes` / `unreal_classes` 批量 `discover_python_class`。
6. 简单官方能力优先 `call_tool`，高层 VibeUE service 才用 `execute_python_code`。
7. 写操作后 compile/save/read back；不要只相信 Python 返回 true。

## 日志诊断

1. 优先用 `EditorToolset.LogsToolset.GetLogEntries`，`category: ""` 表示全部日志。
2. pattern 可用 `LogModelContextProtocol`、`LogToolsetRegistry`、`LogPython`、`Error`、`Warning`。
3. `LogHttp` telemetry 失败不单独判定为 MCP 失败。
4. 结合端口、进程、`list_toolsets` 结果判断。

## 自动化测试

1. 仅在用户要求时运行测试。
2. 调用 `DiscoverTests`。
3. 再调用 `ListTests`，不要因为 Discover 阶段有 UE warning 就立即判失败。
4. 运行具体测试前说明范围。
5. 等待状态完成后读取结果和日志。

## 自定义 Toolset 或 UE AgentSkill

1. 区分外部 Codex/Agent Skill 和 UE `UAgentSkill` 资产。
2. 读取 AgentSkill 可直接做；创建/更新 UE `UAgentSkill` 必须获得明确授权。
3. 新建 Python/C++ Toolset 属于技术流程，不在设计师默认流程中执行。
4. 新增 C++ `UFUNCTION` 后需要完整重启 UE。
