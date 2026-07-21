---
name: unreal-mcp-navigator-cn
description: Use when connecting AI agents such as Codex, Claude Code, Cursor, VS Code, Gemini, or MCP Inspector to Unreal MCP in Unreal Editor projects, especially UE 5.8 designer workflows, ModelContextProtocol setup, ToolsetRegistry discovery, All Toolsets diagnosis, slow MCP calls, terminal startup, or connection troubleshooting.
---

# Unreal MCP 导航员

## 定位

这个 Skill 是给设计师用的 Unreal MCP 连接导航说明。它只负责：确认项目和 UE 是否准备好、连接 MCP、发现 Toolset、判断卡点、给出下一步可执行操作。

它不是资产制作手册。材质、Niagara、Sequencer、关卡、蓝图等具体制作规则，应优先由项目内 AgentSkill、团队模板或用户当前要求决定；本 Skill 只保留连接和安全底线。

## 连接顺序

1. 当前会话已有 Unreal MCP 工具时，先做一次轻量 `list_toolsets`。
2. 调用成功且目标 Toolset 可见，即可进入任务；不再默认检查进程、端口或 `netstat`。
3. `list_toolsets` 失败时，先确认默认地址 `http://127.0.0.1:8000/mcp` 或项目指定端口是否可用。
4. 只有端口结果与用户反馈冲突、需要区分 UE 未运行与 MCP 未启动，或跨 Agent 状态不一致时，才检查 `.uproject`、UnrealEditor 进程、用户会话、主机和日志。
5. 需要参数或不确定工具能力时，再调用 `describe_toolset`；执行具体工具时用 `call_tool`，Unreal MCP 调用必须串行。

原始 HTTP、`curl`、`urllib` 和端口请求只用于连接诊断，不作为 UE 资产执行通道。客户端没有暴露原生 MCP 工具时，先修复客户端配置或重连；不要临时编写 SSE 解析器继续写资产。

只把当前 live `list_toolsets` / `describe_toolset` 当作真相。文档、记忆、截图或旧会话只能当线索，不能替代实时结果。

## 设计师优先

面向设计师时，先做足以回答当前问题的最小检测，再用简单结论告诉用户下一步。不要默认把项目、进程、端口、配置、日志和 Toolset 全部检查一遍，也不要一开始就抛 JSON、schema、Python API 或一串技术问题。

需要设计师亲自操作时，给具体菜单路径和可见结果，例如：`Edit > Plugins`、`Edit > Editor Preferences > General > Model Context Protocol`、UE 控制台命令、是否需要重启 UE。

## 常见判断

- 端口 8000 不通：UE 未打开、MCP server 未启动，或端口不是 8000。
- 只看到 `ToolsetRegistry.AgentSkillToolset`：MCP 已连接，但编辑器工具集可能没加载；通常需要启用 `All Toolsets` 或至少 `EditorToolset` 后重启 UE。
- UE 重启、崩溃、C++ rebuild、Live Coding 或 MCP 重连后：重新确认端口，重新 `list_toolsets`，不要沿用旧 session 或旧 schema。
- 工具返回体里出现 `success: false`、`error`、`warning`、`partial`、`required`、`could not`、`does not exist`、compiler errors：先当作失败或部分失败处理，不要只看 transport 成功。

## 跨 Agent 状态不一致

不同 Agent 可能运行在不同终端、权限、工作目录或会话里。一个 Agent 能看到 `.uproject`，不代表它一定能看到同一个 UE 进程、同一个 8000 端口或同一组 MCP Toolset。

遇到“用户明明打开 UE，但 Agent 说没打开 / 8000 不通 / 没工具”时，必须分层判断，不要直接下结论：

1. 项目文件存在：只能说明磁盘路径可见。
2. `UnrealEditor` 进程存在：只能说明 UE 正在运行。
3. `127.0.0.1:8000` 监听：说明 MCP HTTP server 已启动。
4. `list_toolsets` 有目标工具集：说明 MCP 连接和工具注册都可用。

如果两个 Agent 结果不同，让它们对比 `hostname`、`whoami`、当前目录、`.uproject` 路径、`UnrealEditor` 进程、`netstat` 端口结果和 `list_toolsets`。不要把“另一个 Agent 检测为空”自动解释成用户没打开 UE。

UE 5.8 官方 MCP 控制台命令优先使用：

- `ModelContextProtocol.StartServer 8000`
- `ModelContextProtocol.StopServer`
- `ModelContextProtocol.RefreshTools`
- `ModelContextProtocol.GenerateClientConfig All`

不要默认把 `mcp.start` / `mcp.restart` 当作官方命令；除非项目文档或 live UE 日志明确证明这些是当前项目提供的别名。

## 可选增强

VibeUE 5.8 只是 UE 5.8 官方 Unreal MCP 的可选增强，不是连接 MCP 的前置条件。只有用户要评估或项目已安装 VibeUE 时，才读取 `references/vibeue-58.md`。

如果 live MCP 暴露了 `ToolsetRegistry.AgentSkillToolset`，并且用户要做具体 UE 领域任务，可以先用它列出项目内 Agent Skills，再读取与任务匹配的项目 Skill。不要凭本地文件名假设项目 Skill 已加载。

## 轻量安全底线

- 不并发调用 Unreal MCP。
- 不覆盖、删除、批量移动/重命名或批量修改正式资产，除非用户明确确认。
- 写操作按“读当前状态 -> 最小修改 -> 保存/编译 -> 读回验证”闭环处理，不把调用成功当成完成。
- 写操作超时或返回不明时，不要盲目重试；先查日志、端口、进程和目标状态。
- 不要用可能启动 PIE/Simulate 的 API 做状态检查；写资产前确认编辑器不在播放或模拟。
- 不自动修改 `.uproject`、`DefaultEngine.ini` 或客户端配置，除非用户明确要求进入技术自动配置流程。
- 不创建或更新 UE `UAgentSkill` 资产，除非用户明确要求。

## 参考文件

- 给设计师讲连接和操作步骤：`references/designer-workflow.md`
- 配置客户端或解释 `GenerateClientConfig`：`references/configuration-reference.md`
- 判断请求是否属于 Unreal MCP：`references/triggers.md`
- 理解 `list_toolsets` / `describe_toolset` / `call_tool`：`references/mcp-tools.md`
- 快速判断常见 Toolset 用途：`references/toolset-map.md`
- 安装、启用或验证 VibeUE 5.8：`references/vibeue-58.md`
- 连接失败、工具缺失、MCP 慢、HTTP 断连、UE Terminal 异常：`references/troubleshooting.md`

## 最小验证

1. 优先调用 `list_toolsets`；成功且目标 Toolset 可见就停止连接诊断。
2. 只有调用失败时才检查端口；只有端口结论不足或与用户反馈冲突时才继续查进程、项目、会话和日志。
3. 需要 schema 时调 `describe_toolset`；用 `call_tool` 串行执行，如有写操作则写后读回验证。
