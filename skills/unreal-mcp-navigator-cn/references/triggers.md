# Unreal MCP 触发与项目识别参考

本文件用于判断一个请求是否应该进入 Unreal MCP 工作流，以及在陌生目录里确认 Unreal 项目根。它只负责识别和路由，不负责执行编辑器修改。

## 强触发信号

看到以下内容时，优先按 Unreal 项目处理：

- 文件扩展名：`.uproject`、`.uplugin`、`.umap`、`.uasset`。
- 配置文件：`DefaultEngine.ini`、`DefaultGame.ini`、`DefaultEditor.ini`、`EditorPerProjectUserSettings.ini`。
- 目录：`Content/`、`Config/`、`Saved/`、`Source/`、`Plugins/`、`Intermediate/`、`Binaries/`、`DerivedDataCache/`。
- C++ 工程文件：`*.Build.cs`、`*.Target.cs`、`GenerateProjectFiles.bat`、`GenerateProjectFiles.sh`、`GenerateProjectFiles.command`。
- UE 词汇：Content Browser、Outliner、Details、World Settings、PIE、Simulate、Viewport、Blueprint Graph、Material Editor、Niagara、Sequencer、Control Rig、State Tree、Behavior Tree、GAS、Automation Test、Cook、RunUAT。

## 反射和 C++ 信号

看到以下标记时，通常需要考虑 UHT/UBT、Live Coding、Editor 重启或 schema 刷新：

- `UCLASS`、`USTRUCT`、`UENUM`、`UINTERFACE`、`GENERATED_BODY`。
- `UPROPERTY`、`UFUNCTION`、`UObject`、`AActor`、`UActorComponent`、`UGameInstance`、`UWorld`。
- 新增或修改 `UFUNCTION(meta = (AICallable))` 后，不要期待 live MCP 立刻发现；通常需要编译并重启 UE。

## 常见资产命名前缀

这些前缀不能单独证明任务必须用 MCP，但能帮助判断领域和 Toolset：

| 前缀 | 常见含义 |
|---|---|
| `BP_`、`BPI_`、`ABP_` | Blueprint、Blueprint Interface、Animation Blueprint |
| `WBP_` | Widget Blueprint / UMG |
| `M_`、`MI_`、`MF_` | Material、Material Instance、Material Function |
| `T_`、`RT_` | Texture、Render Target |
| `NS_`、`PS_`、`FX_` | Niagara、Particle、特效 |
| `SM_`、`SK_`、`S_` | Static Mesh、Skeletal Mesh、Sound |
| `DA_`、`DT_` | Data Asset、Data Table |
| `BT_`、`BB_`、`EQS_` | Behavior Tree、Blackboard、EQS |
| `L_`、`LV_`、`SEQ_`、`LS_` | Level、Level Variant、Sequencer、Level Sequence |

## 不应触发的情况

- 用户只问概念解释，例如“蓝图是什么”“材质节点怎么理解”，且不需要检查项目或编辑器状态。
- Unity、Godot、Blender、Houdini 任务，除非用户明确要求迁移到 Unreal。
- 普通软件设计里的“蓝图”“架构图”“流程图”，不是 Unreal Blueprint。
- 只需要改文本、Markdown、配置说明，不涉及 UE 项目状态或资产。

## 项目根判断

从当前目录向上找根目录：

1. 看到一个 `.uproject`，通常把它所在目录当作游戏项目根。
2. 看到 `GenerateProjectFiles.*`，可能是 UE 源码根或大型源码工作区。
3. 不要只因为有 `Engine/` 目录就认定为根；源码树和插件目录里可能嵌套多个 `Engine` 路径。
4. 对安装版/Launcher 引擎项目，MCP 客户端配置通常在 `.uproject` 同级目录。
5. 对源码引擎工作区，配置可能在源码工作区根，也可能在具体 `.uproject` 同级；先读现有 `.codex/config.toml` 和用户启动位置。

## 路由口诀

- 需要当前编辑器状态、关卡、Actor、Content Browser、Blueprint 图表、材质图、视口、PIE：用 live MCP。
- 需要编译、Cook、Automation Test、Python commandlet、日志分析、CI：优先命令行/headless。
- 不确定：先做只读项目发现和 `list_toolsets`，不要直接写资产。
