# Unreal MCP 配置参考

本文件用于核对 Unreal MCP 的 UE 端设置、客户端配置文件、控制台命令和 Terminal 启动方式。它是配置参考，不是自动配置脚本；默认不要自动改 `.uproject`、`DefaultEngine.ini` 或客户端配置文件。

## UE 端设置

在 UE 5.8 中打开 `Edit > Editor Preferences > General > Model Context Protocol`。

| 设置 | 推荐值 | 说明 |
|---|---|---|
| Auto Start Server | true | 编辑器启动时自动启动 MCP server |
| Server Port Number | 8000 | 默认端口 |
| Server URL Path | `/mcp` | 默认路径 |
| Enable Tool Search | true | 只暴露 `list_toolsets`、`describe_toolset`、`call_tool` 三个元工具 |

如果端口冲突，可让技术同学改端口；客户端配置 URL 必须同步变化。

## UE 控制台命令

| 命令 | 用途 |
|---|---|
| `ModelContextProtocol.StartServer [port]` | 启动 server，可选覆盖端口 |
| `ModelContextProtocol.StopServer` | 停止 server 并关闭 session |
| `ModelContextProtocol.RefreshTools` | 重新扫描 Toolset；用于启用工具、热重载、Game Feature 激活后 |
| `ModelContextProtocol.GenerateClientConfig <Client|All>` | 生成客户端配置 |

支持的客户端名：`ClaudeCode`、`Cursor`、`VSCode`、`Gemini`、`Codex`、`All`。

## 客户端配置文件

| 客户端 | 文件 | 典型形状 |
|---|---|---|
| Claude Code | `.mcp.json` | `"type": "http", "url": "http://127.0.0.1:8000/mcp"` |
| Codex | `.codex/config.toml` | `[mcp_servers.unreal-mcp]` + `url = ".../mcp"` |
| Cursor | `.cursor/mcp.json` | `"url": "http://127.0.0.1:8000/mcp"` |
| VS Code | `.vscode/mcp.json` | `"url": "http://127.0.0.1:8000/mcp"` |
| Gemini | `.gemini/settings.json` | `"httpUrl": "http://127.0.0.1:8000/mcp"` |

JSON 配置通常可合并；Codex TOML 生成常见为一次性写入，已存在时可能拒绝覆盖。遇到 Codex 配置陈旧时，优先让用户或技术同学手动确认后编辑。

## 项目发现

在编辑配置前，先确认项目根：

1. 游戏项目根通常包含一个 `.uproject`。
2. 源码引擎根通常包含 `GenerateProjectFiles.bat`、`.sh` 或 `.command`。
3. 不要把裸 `Engine/` 目录当成唯一根标志。
4. 安装版/Launcher 引擎项目的 `.codex/config.toml` 通常应放在 `.uproject` 同级目录。
5. 源码引擎工作区可能把配置放在工作区根；先看用户从哪里启动 AI 客户端。

只读探针优先于编辑配置：读取 `.uproject`、`.codex/config.toml`、`Saved/Config/*Editor/EditorPerProjectUserSettings.ini`、最新 `Saved/Logs/*.log`，再决定是否需要用户手动修改。

## Codex 项目配置示例

```toml
[mcp_servers.unreal-mcp]
url = "http://127.0.0.1:8000/mcp"
```

Codex 必须从包含该 `.codex/config.toml` 的项目根目录启动，或者使用能读取该项目配置的 Codex 桌面线程。

如果 Codex CLI 可用，也可由技术同学注册本地 HTTP MCP：

```powershell
codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp
```

注册后需要重启或重连 Codex，当前会话不一定立刻看到新 MCP。

## Claude/Cursor/VS Code/Gemini JSON 示例

```json
{
  "mcpServers": {
    "unreal-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Cursor/VS Code 有时不需要 `type` 字段；以客户端实际文档和生成结果为准。

## UE 内置 Terminal

Terminal 插件只是便利，不是 MCP 必需条件。Windows 下 Startup Commands 推荐顺序：

```cmd
chcp 65001
set TERM=xterm-256color
set PATH=%LOCALAPPDATA%\Microsoft\WindowsApps;%APPDATA%\npm;%PATH%
cd /d "<项目根目录>"
codex
```

如果 `codex` 立刻返回提示符，通常是 PATH 找不到 Codex；如果中文乱码，通常是编码问题。外部 Windows Terminal / PowerShell 更稳定。

## 启动前检查

1. UE 5.8 项目已打开。
2. `Unreal MCP` / `ModelContextProtocol`、`ToolsetRegistry` 已启用。
3. `All Toolsets` 或至少 `EditorToolset` 已启用。
4. server 端口和客户端 URL 一致。
5. AI 客户端从配置所在项目根目录启动。
6. 当前会话已经重连，能看到 MCP server 或 tool-search 元工具。

## VibeUE 5.8 可选增强

VibeUE 5.8 不是单独的 MCP 连接入口；按它的 5.8 流程安装后，AI 仍连接官方 endpoint：

```text
http://127.0.0.1:8000/mcp
```

如果用户要安装或验证 VibeUE 5.8，读取 `vibeue-58.md`。不要把旧版 VibeUE 的 `127.0.0.1:8088/mcp` 配置写进官方 UE 5.8 MCP 客户端配置，除非用户明确说明使用旧版独立 VibeUE server。

## 不做的事

- 不默认写 `.uproject` 插件数组。
- 不默认写 `Config/DefaultEngine.ini`。
- 不默认删除或覆盖 `.codex/config.toml`。
- 不为设计师提供自动配置脚本入口。
