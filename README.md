# Unreal MCP Skills

A collection of Unreal Engine 5.8 MCP skills for designers, technical artists, and content creators.

This repository brings together workflow skills built around Unreal MCP, Codex, and optional VibeUE tools. Each skill can be installed and used independently. Together, they cover connection diagnostics, Sequencer cinematic production, and level design.

## Skills

| Skill | Purpose | Directory |
| --- | --- | --- |
| Unreal MCP Navigator CN | Checks the Unreal project, editor process, MCP service, and registered toolsets, then provides a safe troubleshooting workflow. | [`skills/unreal-mcp-navigator-cn`](skills/unreal-mcp-navigator-cn) |
| Unreal MCP Cinematic CN | Translates shot descriptions, storyboards, and pacing requirements into executable and reviewable UE5 Sequencer workflows. | [`skills/unreal-mcp-cinematic-cn`](skills/unreal-mcp-cinematic-cn) |
| Unreal MCP Level Design CN | Supports UE5 level planning, scene auditing, routes, PCG, foliage, streaming, and performance validation. | [`skills/unreal-mcp-level-design-cn`](skills/unreal-mcp-level-design-cn) |

## Repository Structure

```text
Unreal-MCP-Skills/
├── README.md
└── skills/
    ├── unreal-mcp-navigator-cn/
    ├── unreal-mcp-cinematic-cn/
    └── unreal-mcp-level-design-cn/
```

Each subdirectory is a complete, standalone Codex skill. It retains its original `SKILL.md`, `agents/`, `references/`, `scripts/`, and any other source files.

## Installation

### Install One Skill

Copy the required skill directory into your personal Codex skills directory:

```text
C:\Users\<your-username>\.codex\skills\
```

For example, to install the connection and diagnostics skill:

```text
C:\Users\<your-username>\.codex\skills\unreal-mcp-navigator-cn\
```

### Install All Skills

Copy all three subdirectories from `skills/` into your personal or project-level Codex skills directory, then refresh or restart Codex.

## Recommended Workflow

1. Start with `unreal-mcp-navigator-cn` to verify the project, editor, MCP service, and available toolsets.
2. Use `unreal-mcp-cinematic-cn` for Sequencer shots, cameras, and cinematic animation.
3. Use `unreal-mcp-level-design-cn` for level planning, auditing, and iteration.

## Compatibility

- Unreal Engine 5.8
- Unreal MCP
- Codex or another MCP-compatible AI client
- VibeUE (optional and dependent on the toolsets available in the current project)

## Notes

This repository only organizes and distributes the existing skills as a unified collection. The files under `skills/` were copied from their original standalone repositories without modification.
