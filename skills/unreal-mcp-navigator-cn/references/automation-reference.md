# Unreal 命令行与自动化参考

本文件用于判断何时不用 live MCP，而改用 Unreal 命令行、UBT、UAT、Automation Test、Python commandlet 或日志解析。它面向技术同学和 AI 智能体；设计师默认不需要执行这些命令。

## 执行模式路由

| 任务 | 推荐执行方式 | 原因 |
|---|---|---|
| 查看当前关卡、选中 Actor、Content Browser、Blueprint 图表、材质图 | live MCP | 需要编辑器内语义状态 |
| 新建或修改材质、关卡、Actor、Blueprint 资产 | live MCP | 需要编辑器事务和资产系统 |
| C++ 编译、模块构建 | UBT / IDE / Live Coding Toolset | 命令行结果更可控 |
| Automation Test、Functional Test | `UnrealEditor-Cmd` 或 Automation Toolset | 可保存日志和结果 |
| Cook、Package、BuildGraph、RunUAT | UAT / 命令行 | 不需要完整编辑器 UI |
| Python 数据验证、资产扫描 | `UnrealEditor-Cmd` commandlet | 可 headless 运行 |
| 日志分析、端口检查、配置检查 | PowerShell / shell | 只读、快速、低风险 |

不要为了能用 MCP 而启动完整编辑器去跑构建、Cook 或纯命令行测试。live MCP 适合“编辑器里现在是什么、帮我改这个资产、读这个图表”。

## Headless 原则

命令行任务应满足：

1. 有明确的项目根或 `.uproject` 路径。
2. 输出日志写到 `Saved/Logs`、`Saved/Automation`、`Saved/AgentRuns` 或用户指定目录。
3. 设置合理 timeout。
4. 返回 exit code、耗时、日志路径和关键错误摘要。
5. 不打开不必要的编辑器或游戏窗口；测试确实需要渲染时再取消 NullRHI。

## 常见命令形状

Automation Test 示例：

```powershell
"&C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "G:\Project\MyProject.uproject" `
  -Unattended -NullRHI -ExecCmds="Automation RunTests Project; Quit" -log
```

Python commandlet 示例：

```powershell
"&C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "G:\Project\MyProject.uproject" `
  -Unattended -NullRHI -run=pythonscript -script="G:\Project\Scripts\validate_content.py" -log
```

Cook 示例：

```powershell
"&C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun `
  -project="G:\Project\MyProject.uproject" -noP4 -platform=Win64 -clientconfig=Development `
  -cook -stage -pak -archive -archivedirectory="G:\Project\Saved\CookSmoke"
```

这些命令是形状参考；执行前必须根据用户项目路径、引擎路径和目标平台调整。

## Timeout 和重试

- 端口探针、进程检查、配置读取：短 timeout，失败可重试。
- 只读 MCP 调用：超时后确认 UE 进程和端口仍在，可重试一次。
- 写入 MCP 调用：超时后不要盲目重试，因为可能已经在编辑器里成功或部分成功；先读日志和资产状态。
- 构建、Cook、Automation：超时后保留日志路径、命令、exit code、耗时；必要时终止进程树。
- 遇到大规模 schema 漂移、未知工具参数或编辑器处于编译/加载/模态窗口时，停手并说明需要用户处理。

## 与 MCP 的配合

推荐顺序：

1. 用命令行做项目发现、版本、配置和日志只读检查。
2. 用 live MCP 做 `list_toolsets` 和目标 Toolset schema 检查。
3. 对需要编辑器状态的任务，用 live MCP 执行。
4. 对编译、测试、Cook，用命令行执行并把日志摘要反馈给用户。

如果命令行检查已经显示项目不可编译、插件缺失或 UE 版本不对，不要继续做编辑器写操作。
