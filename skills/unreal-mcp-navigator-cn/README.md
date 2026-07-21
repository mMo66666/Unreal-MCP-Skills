# Unreal MCP Navigator

`unreal-mcp-navigator-cn` is a designer-friendly Codex skill for connecting AI agents to Unreal Engine 5.8 through Unreal MCP.

Its job is simple: verify the project, editor process, MCP endpoint, and registered toolsets before an agent starts changing Unreal assets. It focuses on connection, discovery, diagnosis, and safe handoff. It is not a material, Niagara, Sequencer, Blueprint, or level-production manual.

## Who It Is For

- Designers, technical artists, and content creators working in Unreal Engine 5.8.
- Codex, Claude Code, Cursor, VS Code, Gemini, or MCP Inspector users who need to connect to Unreal Editor.
- Teams troubleshooting missing toolsets, stale sessions, slow MCP calls, port issues, or Unreal terminal problems.

## What It Does

- Confirms that the current directory contains an Unreal project.
- Checks whether Unreal Editor is running the intended project.
- Verifies the default MCP endpoint: `http://127.0.0.1:8000/mcp`.
- Guides agents through `list_toolsets`, `describe_toolset`, and `call_tool`.
- Distinguishes project visibility, editor process state, port availability, and toolset registration.
- Diagnoses common states such as missing `All Toolsets`, stale sessions, schema drift, and HTTP transport failures.
- Gives designers clear menu paths and next actions instead of raw technical errors.

## What It Does Not Do

- Define detailed asset-production rules.
- Build complex materials, Niagara systems, Sequencer structures, or Blueprints from scratch.
- Modify `.uproject`, `DefaultEngine.ini`, or client configuration unless the user explicitly requests technical setup.
- Create or update Unreal `UAgentSkill` assets unless explicitly requested.

## Recommended Workflow

1. Confirm that the current directory contains a `.uproject` file.
2. Confirm that Unreal Editor is running the target project.
3. Check `http://127.0.0.1:8000/mcp`.
4. Call `list_toolsets` and treat the live result as the source of truth.
5. Call `describe_toolset` only when the tool schema or parameters are unclear.
6. Execute Unreal MCP calls serially.
7. For write operations, read the current state, make the smallest change, save or compile, and read back the result.

## Common Diagnosis Model

| Check | What It Proves |
|---|---|
| `.uproject` exists | The agent can see the project files. |
| `UnrealEditor` process exists | Unreal Editor is running. |
| Port `8000` is listening | The Unreal MCP HTTP server is running. |
| `list_toolsets` returns the required toolsets | MCP is connected and the tools are registered. |

Do not treat one layer as proof of the next. For example, seeing a `.uproject` file does not prove that Unreal Editor or the MCP server is running.

## Unreal Engine 5.8 MCP Commands

Use the official console commands when available:

```text
ModelContextProtocol.StartServer 8000
ModelContextProtocol.StopServer
ModelContextProtocol.RefreshTools
ModelContextProtocol.GenerateClientConfig All
```

Do not assume `mcp.start` or `mcp.restart` are official commands unless the current project documents or exposes them as aliases.

## Safety Rules

- Run Unreal MCP calls serially.
- Trust live `list_toolsets` and `describe_toolset` results over old documentation or cached schemas.
- Do not overwrite, delete, move, rename, or batch-edit production assets without explicit confirmation.
- Do not blindly repeat a timed-out write operation; inspect logs and the target state first.
- Do not create or save assets while Unreal Editor is in Play or Simulate mode.
- Treat `success: false`, errors, warnings, partial results, and compiler errors as incomplete work.

## Installation

Clone or download this repository, then copy it into your Codex skills directory as `unreal-mcp-navigator-cn`.

Example for PowerShell:

```powershell
Copy-Item -Recurse -Force "Unreal-MCP-Navigator" "$env:USERPROFILE\.codex\skills\unreal-mcp-navigator-cn"
```

Restart or refresh Codex after installation so the skill can be discovered.

## Example Prompts

```text
Use $unreal-mcp-navigator-cn to check whether Unreal MCP is connected and tell me the next step.
```

```text
My agent only sees ToolsetRegistry.AgentSkillToolset. Check whether All Toolsets or EditorToolset is missing.
```

```text
Run a read-only check of the current Unreal project, editor process, MCP port, and registered toolsets.
```

## Repository Structure

```text
Unreal-MCP-Navigator/
  SKILL.md
  agents/
    openai.yaml
  references/
    configuration-reference.md
    designer-workflow.md
    mcp-tools.md
    toolset-map.md
    triggers.md
    troubleshooting.md
    vibeue-58.md
```

## Design Principle

Connect first, inspect live state, make the smallest safe change, and verify the result.
