# 设计师 Unreal MCP 连接指南

本文件给设计师或陪设计师操作的 AI 使用。目标是把 UE 5.8 的 Unreal MCP 连上、确认工具可用，并把问题说成人能操作的下一步。

## 默认策略

先让 AI 检测，再让设计师补操作。不要先问一堆技术问题；设计师通常不知道端口、schema、Toolset 是否加载。

客户端已有 Unreal MCP 工具时，AI 先调用一次 `list_toolsets`；成功后直接进入任务。只有调用失败或结果与用户反馈冲突时，才按需检查端口、UE 进程、项目、客户端配置和最新日志。检测后只汇报结论和下一步。

## 设计师需要亲自做的事

只有这些情况才让设计师操作：

- UE 没打开，或打开的不是目标项目。
- 插件没启用，需要在 `Edit > Plugins` 勾选并重启。
- MCP server 没启动，需要在 `Edit > Editor Preferences > General > Model Context Protocol` 勾选 `Auto Start Server`。
- 需要在 UE 控制台执行 `ModelContextProtocol.GenerateClientConfig All`。
- 需要保存项目、关闭/重启 UE、处理弹窗、停止 Play/Simulate。
- 用户决定安装或启用 VibeUE 5.8 等第三方增强插件。

给设计师的话要具体，例如：

“请打开 `Edit > Plugins`，搜索 `Unreal MCP` 或 `ModelContextProtocol`，确认已启用；再搜索 `All Toolsets`，启用后按 UE 提示重启。重启后告诉我‘已重启’即可。”

## 首次连接

1. 用 UE 5.8 打开目标项目。
2. 在 `Edit > Plugins` 确认启用 `Unreal MCP` / `ModelContextProtocol`、`ToolsetRegistry`、`All Toolsets` 或 `EditorToolset`。
3. 在 `Edit > Editor Preferences > General > Model Context Protocol` 确认 `Auto Start Server` 已启用，端口为 `8000`，路径为 `/mcp`。
4. 如客户端配置缺失，在 UE 控制台执行：`ModelContextProtocol.GenerateClientConfig All`。
5. 从项目根目录重新启动 AI 客户端。
6. 让 AI 调 `list_toolsets`，确认不只是 `ToolsetRegistry.AgentSkillToolset`。

## 再次连接

AI 先调用 `list_toolsets`；失败后再检查端口和进程，并按结论让设计师：

- UE 未打开：用 UE 5.8 打开目标项目。
- 端口不通：在 UE 控制台执行 `ModelContextProtocol.StartServer 8000`。
- 只看到 `ToolsetRegistry.AgentSkillToolset`：启用 `All Toolsets` 或 `EditorToolset` 后重启 UE。
- 配置陈旧：执行 `ModelContextProtocol.GenerateClientConfig All`，再从项目根目录重启 AI 客户端。

如果用户说“UE 明明打开了”，但某个 Agent 检测为空，先按跨 Agent 状态不一致处理：项目文件存在、UE 进程、8000 端口、`list_toolsets` 是四件不同的事。不要把文件可见当作 UE 已打开，也不要把端口不通直接说成 UE 没打开。

## 连接成功的信号

- AI 能列出多个 Unreal Toolset。
- AI 能读当前关卡、当前选择或日志。
- AI 不再只报告“没有工具”或“只有 AgentSkillToolset”。

## VibeUE 5.8 怎么说

VibeUE 5.8 是可选增强，不是必装项。可以这样解释：

“我们先把 UE 5.8 官方 MCP 连通。VibeUE 5.8 是可选增强，适合地形、UI、蓝图、Niagara、动画、性能等更复杂流程。如果暂时不装，官方 MCP 仍然可以使用。”

如果用户要评估安装，再读取 `vibeue-58.md`。

## 设计师注意事项

- 不要同时让多个 AI 客户端操作同一个 UE 编辑器。
- AI 正在操作时，等它完成或失败后再追加新命令。
- 不要把 MCP 地址暴露到公网。
- 重要资产先在测试目录验证，不要直接批量改正式内容。
- 不要在 Play/Simulate 模式中让 AI 创建、保存、编译或批量修改资产。
- UE Terminal 只是可选便利；外部 PowerShell / Windows Terminal 通常更稳定。

## 遇到问题怎么转述

| 看到的情况 | 通俗说法 |
|---|---|
| 只看到 `ToolsetRegistry.AgentSkillToolset` | “MCP 连上了，但编辑器工具集可能没启用或没重启。” |
| 连不上 `127.0.0.1:8000/mcp` | “MCP server 可能没启动，或端口不是 8000。” |
| AI 操作很慢 | “UE MCP 本来是串行的，等当前操作结束，不要连续催多个命令。” |
| UE Terminal 中文乱码或 `codex` 一闪退出 | “UE 内置终端 PATH/编码有问题，先用外部终端跑 AI。” |
| AI 要改很多资产 | “先保存项目，并让 AI 说清楚会改哪些资产。” |
