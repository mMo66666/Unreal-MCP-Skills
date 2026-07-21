# Unreal MCP Skills

面向设计师、技术美术与内容创作者的 Unreal Engine 5.8 MCP 技能合集。

本仓库统一收录围绕 Unreal MCP、Codex 与可选 VibeUE 工具构建的工作流技能。每个 Skill 都可以独立安装和使用；它们分别负责连接诊断、Sequencer 镜头制作和关卡设计。

## Skills

| Skill | 作用 | 目录 |
| --- | --- | --- |
| Unreal MCP Navigator CN | 检查 Unreal 项目、编辑器进程、MCP 服务与工具集状态，并提供安全的故障诊断流程。 | [`skills/unreal-mcp-navigator-cn`](skills/unreal-mcp-navigator-cn) |
| Unreal MCP Cinematic CN | 将镜头描述、分镜和节奏需求转化为可执行、可检查的 UE5 Sequencer 工作流。 | [`skills/unreal-mcp-cinematic-cn`](skills/unreal-mcp-cinematic-cn) |
| Unreal MCP Level Design CN | 面向 UE5 关卡规划、场景审查、动线、PCG、植被、流送与性能验证。 | [`skills/unreal-mcp-level-design-cn`](skills/unreal-mcp-level-design-cn) |

## 仓库结构

```text
Unreal-MCP-Skills/
├── README.md
└── skills/
    ├── unreal-mcp-navigator-cn/
    ├── unreal-mcp-cinematic-cn/
    └── unreal-mcp-level-design-cn/
```

每个子目录都是一个完整、独立的 Codex Skill，并保留自己的 `SKILL.md`、`agents/`、`references/`、`scripts/` 和其他原始文件。

## 安装

### 安装单个 Skill

将需要的 Skill 子目录复制到个人 Codex Skills 目录：

```text
C:\Users\<你的用户名>\.codex\skills\
```

例如安装连接诊断 Skill：

```text
C:\Users\<你的用户名>\.codex\skills\unreal-mcp-navigator-cn\
```

### 安装全部 Skills

将 `skills/` 下的三个子目录全部复制到个人或项目级 Codex Skills 目录，然后刷新或重启 Codex。

## 使用建议

1. 首先使用 `unreal-mcp-navigator-cn` 检查项目、编辑器和 MCP 工具状态。
2. 制作 Sequencer 镜头时使用 `unreal-mcp-cinematic-cn`。
3. 规划、审查或迭代关卡时使用 `unreal-mcp-level-design-cn`。

## 兼容环境

- Unreal Engine 5.8
- Unreal MCP
- Codex 或其他兼容 MCP 的 AI 客户端
- VibeUE（可选，以当前项目实际提供的工具为准）

## 说明

本仓库只是统一组织和分发现有 Skills。`skills/` 内的内容来自原独立仓库，迁移时未修改其文件内容。
