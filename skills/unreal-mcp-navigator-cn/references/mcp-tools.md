# Unreal MCP 工具参考

本文件只解释官方 MCP 的三步工具发现方式。当前项目到底有哪些工具，永远以 live `list_toolsets` 为准。

## Tool Search 模式

默认情况下，AI 客户端通常只看到三个元工具：

| 元工具 | 用途 |
|---|---|
| `list_toolsets` | 列出当前可用 Toolset |
| `describe_toolset` | 查看某个 Toolset 的工具和参数 |
| `call_tool` | 调用某个 Toolset 里的具体工具 |

标准 `call_tool` 形状：

```json
{
  "toolset_name": "editor_toolset.toolsets.scene.SceneTools",
  "tool_name": "get_current_level",
  "arguments": {}
}
```

`toolset_name` 用完整 Toolset 名，`tool_name` 用短工具名。不要把完整限定名塞进 `tool_name`。

## 调用规则

1. 不知道有什么工具：先 `list_toolsets`。
2. 知道 Toolset 但不清楚参数：再 `describe_toolset`。
3. 已知工具和参数：直接 `call_tool`。
4. 写操作完成后：用只读工具读回验证。
5. 文档和 live schema 冲突时：以 live `describe_toolset` 为准。

不要并发调用 Unreal MCP。UE 编辑器端很多操作会同步到主线程，并发更容易超时或打乱状态。

客户端已经暴露这些 MCP 工具时，直接调用它们；不要用 `curl`、`urllib` 或临时脚本直连 `/mcp` 并手工解析 SSE。原始 HTTP 只用于判断地址是否可达，不能替代客户端 MCP 会话、schema 管理和结构化结果处理。

同一会话内，工具 schema 在首次使用时读取并缓存；只有重连、schema 报错或工具版本变化时才重新 `describe_toolset`。批量 Key 或同类属性优先一次批量调用，避免逐 Key 往返。

## 写操作闭环

UE 资产操作不要只看调用返回。通用闭环是：先读当前状态，做最小修改，必要时保存或编译，再用只读工具读回验证。若验证工具读取的是磁盘状态，例如 dump、资产扫描或 metadata，先保存再验证，避免读到旧版本。

## 成败判断

MCP transport 成功不代表工具成功。返回内容里如果出现这些信号，要先当作失败或部分失败处理：

- `success: false`
- `error` / `warning` / `partial`
- `required` / `could not` / `does not exist`
- compiler errors、Blueprint errors、Python exceptions

写操作超时或返回空不要直接重放同一命令。先用只读工具检查目标资产或关卡状态；连接本身异常时再查端口、进程和日志。

## AgentSkillToolset

`ToolsetRegistry.AgentSkillToolset` 用来读取项目内 UE `UAgentSkill`。它和外部 Codex Skill 不是同一种东西。

如果用户要做具体 UE 领域任务，并且 live Toolset 里有 AgentSkillToolset，可以：

1. `describe_toolset` 看是否有 `ListSkills` / `GetSkills`。
2. 列出项目内 Skills。
3. 只读取和当前任务匹配的项目 Skill。
4. 项目 Skill 的制作规则优先，但仍遵守串行调用、写后验证和高风险授权。

如果只看到 AgentSkillToolset，通常不是“完全没连上”，而是编辑器工具集没加载。

## All Toolsets

`All Toolsets` 适合设计师首次连接和排查“工具没加载”。它会暴露更多能力，也会增加 schema 噪音和启动成本。

启用后仍然要靠 `list_toolsets` / `describe_toolset` 精确选择工具，不要凭名字猜参数。
