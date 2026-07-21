# Unreal MCP Toolset 地图

这些只是常见候选。执行前必须先用 `list_toolsets` 确认存在，再用 `describe_toolset` 看实时参数。

| 任务 | 常见 Toolset | 通俗理解 |
|---|---|---|
| 编辑器状态、选择、视口、Content Browser、PIE | `EditorToolset.EditorAppToolset` | 看编辑器当前在做什么 |
| 日志 | `EditorToolset.LogsToolset` | 读 UE 日志，判断为什么失败 |
| 当前关卡、场景 Actor 查询 | `editor_toolset.toolsets.scene.SceneTools` | 看关卡和场景里的对象 |
| Actor transform、bounds、组件、attachment | `editor_toolset.toolsets.actor.ActorTools` | 移动/检查场景物体 |
| 资产存在、保存、复制、依赖、dirty 状态 | `editor_toolset.toolsets.asset.AssetTools` | 管 Content Browser 里的资产 |
| Blueprint 图、变量、编译 | `editor_toolset.toolsets.blueprint.BlueprintTools` | 看或改蓝图 |
| 材质、材质实例、表达式节点、参数 | `editor_toolset.toolsets.material.*` | 看或改材质 |
| Niagara 系统/Emitter | `NiagaraToolsets` | 看或改粒子特效 |
| 自动化测试 | `AutomationTestToolset.AutomationTestToolset` | 跑 UE 自动化测试 |
| Live Coding | `LiveCodingToolset.LiveCodingToolset` | 触发或查看 C++ 热编译 |
| 项目内 Agent Skills | `ToolsetRegistry.AgentSkillToolset` | 读取项目自己的 AI 工作规则 |

## 选择方法

1. 先从用户需求判断领域。
2. `list_toolsets` 看候选是否存在。
3. 不存在时，不要硬调；先判断是否需要启用插件并重启 UE。
4. 存在时，`describe_toolset` 获取实时 schema。
5. 写操作后用只读工具验证。

## 边界

- `MCPClientToolset` 是 UE 反向连接其他 MCP server 的能力，不是 Codex 控制 UE 所需的 server。
- 没有通用 UFUNCTION 调用工具时，不要承诺能直接调用任意 native/editor 方法。
- 没有对应 Toolset 时，先说清限制，再决定是否需要项目内 AgentSkill、VibeUE、Blueprint 或 Python fallback。
