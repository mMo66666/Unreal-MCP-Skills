# VibeUE 5.8 扩展参考

VibeUE 5.8 是 UE 5.8 官方 Unreal MCP 的可选增强插件，不是官方 MCP 连接流程的替代品。

## 核心判断

AI 客户端仍连接官方 endpoint：

```text
http://127.0.0.1:8000/mcp
```

不要把 VibeUE 5.8 和旧版 VibeUE 文档里的独立 `127.0.0.1:8088/mcp` server 混用。UE 5.8 分支通常不需要单独 VibeUE server、API Key 或内置聊天窗口；如果界面要求密钥，先确认是不是旧版或误读旧文档。

## 什么时候建议评估

- 团队愿意安装第三方插件，并先在测试目录验证。
- 需要 Terrain、Landscape、Niagara、Animation、UMG、Blueprint、Enhanced Input、StateTree、Performance 等更高层工作流。
- 官方 Toolset 能力不够，需要项目内 Agent Skills 或 VibeUE runtime 补强。

只做基础连接、日志、简单资产检查时，不必安装 VibeUE。

## 安装前条件

1. 项目使用 Unreal Engine 5.8。
2. 官方 `ModelContextProtocol` 已连通。
3. `ToolsetRegistry` 已启用。
4. `All Toolsets` 或至少 `EditorToolset` 已启用。
5. 用户明确同意把第三方插件安装到当前项目。

## 验证顺序

安装并重启 UE 后，仍使用官方 8000 endpoint：

1. 调用 `list_toolsets`。
2. 检查是否出现 VibeUE 相关 Toolsets；名称以实时结果为准。
3. 对 `ToolsetRegistry.AgentSkillToolset` 调 `describe_toolset`。
4. 如有 `ListSkills` / `GetSkills`，列出项目内 Skills。
5. 只读取和当前任务匹配的 VibeUE Agent Skill。
6. 先做只读验证，再在 `/Game/MCP_Test` 做隔离写入测试。

## 使用注意

- VibeUE 不是必装依赖；没有安装时，官方 MCP 流程仍应正常继续。
- 不要假设 VibeUE 工具名、参数名或 Skill 名；以 live MCP 为准。
- 不要把 `Plugins/VibeUE/Content/Skills` 里的 Markdown 当作已加载指令；执行 live 任务时优先通过 `AgentSkillToolset` 读取。
- 涉及 Python code execution、批量编辑、保存、删除、重命名、项目配置或外部网络能力时，必须获得用户明确授权。
- 写操作超时后不要重试同一命令；先查日志、资产状态、dirty 状态和目标路径。

## 常见路由

| 任务 | 可能的 VibeUE Skill |
|---|---|
| Blueprint / 图表 / 变量 / 组件 | `blueprints`、`blueprint-graphs` |
| 材质 / 材质实例 | `materials` |
| UMG / MVVM | `umg-widgets` |
| Landscape / 地形数据 | `landscape`、`terrain-data` |
| Niagara | `niagara-emitters`、`niagara-systems` |
| Animation / Sequencer 相关 | `animation-editing`、`animsequence` |
| Enhanced Input / StateTree | `enhanced-input`、`state-trees` |
| 性能分析 | `profiling`、`frame-rate` |
| 关卡 Actor | `level-actors` |

这些名称只作候选，必须以 `AgentSkillToolset.ListSkills` 的实时返回为准。

## 排错

| 现象 | 处理 |
|---|---|
| `list_toolsets` 没有 VibeUE | 确认插件在当前项目 `Plugins/VibeUE`，已启用并重启 UE |
| 只看到 `ToolsetRegistry.AgentSkillToolset` | 先按官方 MCP 排错启用 `All Toolsets` / `EditorToolset` |
| VibeUE Skill 不出现 | 确认 `AgentSkillToolset` 是否有 `ListSkills`，再读 UE 日志 |
| 构建脚本失败 | 检查 UE 5.8 路径、`.uproject`、PowerShell 执行策略和编译日志 |
| 界面要求 API Key | 先确认是否装错旧版；AI 不应代管或公开密钥 |
