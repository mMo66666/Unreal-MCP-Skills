# Unreal MCP 排错参考

用于连接失败、工具缺失、MCP 变慢、HTTP 断连、UE Terminal 异常或日志诊断。

## 本地检查

在项目根目录运行：

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000
Get-Process UnrealEditor -ErrorAction SilentlyContinue
```

读取最新日志：

```powershell
$log = (Get-ChildItem Saved\Logs -Filter *.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
Select-String -LiteralPath $log -Pattern 'LogModelContextProtocol|LogToolsetRegistry|LogPython|Error|Warning' | Select-Object -Last 120
```

## 常见问题

| 现象 | 判断 | 处理 |
|---|---|---|
| 端口 8000 不通 | MCP server 没启动或 UE 已退出 | 启动 UE，启用 Auto Start，或执行 `ModelContextProtocol.StartServer 8000` |
| 只看到 `ToolsetRegistry.AgentSkillToolset` | server 正常，编辑器工具集没加载 | 启用 `All Toolsets` 或 `EditorToolset`，重启 UE |
| Toolset 数量明显偏少 | ToolsetRegistry 可能还在收集 | 等一下或刷新后重新 `list_toolsets` |
| `Unknown session id` | UE 重启、崩溃或 rebuild 后 session 失效 | 重连客户端，重新 `list_toolsets` |
| `describe_toolset` 很慢 | schema 大或 UE 正忙 | 等待；已知参数时减少 describe |
| HTTP transport failed | 并发调用、UE 卡住或编辑器退出 | 停止盲目重试，查进程和端口 |
| 写操作超时或空响应 | 可能未执行、已执行或部分执行 | 先读目标状态，不要立刻重放 |
| 保存后读回不一致 | 可能未编译、未标 dirty、读到了旧磁盘状态或资产扫描未刷新 | 先确认保存/编译结果，再用只读工具或日志复核 |
| 调用状态检查后持续超时 | 可能误触发 PIE/Simulate 或 UE 主线程忙 | 停止写资产，让用户确认并停止播放/模拟 |
| 多个 `UnrealEditor.exe` | 打开了多个项目实例或残留进程 | 不继续写资产，让用户只保留目标项目实例 |
| schema 与文档不同 | UE/MCP/Toolset 版本漂移 | 以 live `describe_toolset` 为准 |
| UE Terminal 中文乱码 | 终端编码不匹配 | 执行 `chcp 65001` 或改用外部终端 |
| `codex` 一闪退出 | UE Terminal PATH 找不到 Codex | 设置 PATH 或用外部 PowerShell/Windows Terminal |

## 诊断顺序

1. 客户端已暴露 MCP 工具时先调用 `list_toolsets`；成功且目标 Toolset 可见就停止连接诊断。
2. 调用失败时确认 `127.0.0.1:8000` 可访问，再检查 UE 进程和目标项目。
3. 按需确认 `ModelContextProtocol`、`ToolsetRegistry`、`All Toolsets` 或 `EditorToolset` 已启用，且客户端从项目根目录启动。
4. 如果刚启用插件或刚热重载，执行 `ModelContextProtocol.RefreshTools` 后重连客户端。
5. 如果仍旧异常，重启 UE 和 AI 客户端。

不要用 `curl`、`urllib` 或临时 SSE 解析器代替客户端 MCP 会话执行资产操作；这些只能辅助判断地址是否可达。

## 跨 Agent 误判

如果一个 Agent 说“UE 没打开”或“8000 不通”，但用户确认 UE 已打开，不要立刻否定用户。先区分四层状态：

| 层级 | 只能说明什么 | 不能说明什么 |
|---|---|---|
| `.uproject` 存在 | Agent 能看到项目文件 | UE 已打开 |
| `UnrealEditor` 进程存在 | UE 正在运行 | 打开的是目标项目、MCP 已启动 |
| `127.0.0.1:8000` 监听 | MCP HTTP server 已启动 | Toolset 已完整注册 |
| `list_toolsets` 有目标工具集 | MCP 可用且工具已注册 | 写操作已经成功 |

让两个 Agent 对比这些信息：`hostname`、`whoami`、当前目录、`.uproject` 绝对路径、`UnrealEditor` PID、`netstat -ano | findstr :8000`、`list_toolsets`。如果这些不一致，优先解释为运行环境或检测时机不同。

端口不通时，给设计师的下一步优先是：在 UE 控制台执行 `ModelContextProtocol.StartServer 8000`，或到 `Edit > Editor Preferences > General > Model Context Protocol` 勾选 `Auto Start Server`。不要默认要求输入 `mcp.start`，除非当前项目明确提供了这个别名。

## 慢和超时

UE MCP 常见慢点：UE 主线程串行、首次懒加载、Asset Registry 扫描、大 schema、All Toolsets 噪音。

处理原则：

- 不并发调用 Unreal MCP。
- 已知参数时少用 `describe_toolset`。
- 读操作超时可在确认进程和端口正常后最多重试一次。
- 写操作超时不要重试同一写命令，先查结果。
- UE 正在编译、导入、加载地图或弹窗时，先让用户处理编辑器状态。
- 不要用 `editor_play_simulate()` 之类可能启动 PIE/Simulate 的 API 检查状态。

## 停止条件

遇到以下情况先停，不继续写资产：

- `UnrealEditor` 进程不存在或端口 8000 不通。
- 刚启用或变更插件，需要用户重启 UE。
- HTTP 连续失败或 session 明显陈旧。
- 用户要求公网暴露 MCP。
- 用户要求高风险编辑但没有明确授权。
- 出现 UE assertion、World Memory Leaks、编辑器崩溃或多个 UE 实例。
