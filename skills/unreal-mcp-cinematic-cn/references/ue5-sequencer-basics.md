# UE5 Sequencer 基础

本文件记录本 Skill 的 UE5 Sequencer 基础契约。资产创建、Binding、轨道写入和保存可由 VibeUE、UE MCP 或 `mcp-cinematic-execution.md` 定义的 UE Python 原生回退完成。

## LevelSequence

- `LevelSequence` 是 UE5 里承载镜头、动画轨道、Camera Cut、Actor 绑定的资产。
- 新建 LevelSequence 前确定 Content Browser 路径：优先用户或项目约定，否则按 MCP 执行规则使用安全默认目录。
- 文件名可以由 AI 自动命名。部分 `create_level_sequence` 封装会先删除同名资产，调用前必须检查存在性；同名冲突时追加 `_01`、`_02`，不得默认覆盖。
- 用户只要方案时，不创建资产。

## CameraActor 与 CineCameraActor

- 普通动画不一定需要摄像机。
- 用户要求电影感、分镜、运镜、镜头语言时，通常需要 `CineCameraActor`。
- 用户明确要求无摄像机时，不创建 CameraActor，也不加 CameraCutTrack。
- 如果只是物体 Transform 动画，摄像机不是默认需求。

## 创建与幂等

- `create_camera`、添加 CameraCut Track 等高层接口可能自动生成 Actor/Component Binding、Transform、Spawn、焦距、焦点、光圈或默认 Section。每次创建后先读回现有 Binding、Track、Section 和范围，只补缺失项。
- 重跑使用 set-or-replace：按 Binding、轨道类型、Property Path、Section 范围和帧位更新；不得假设新对象内部为空，也不得无条件追加同类轨道或 CameraCut Section。
- Binding 以 GUID、内部名称、Display Name、父子关系和实际对象类型共同识别；Display Name 不等于内部名称，也不能单独证明绑定正确。

## CameraCutTrack

- 多镜头剪辑必须有 CameraCut。
- 每段 CameraCut 要有明确 `[StartFrame, EndFrame)` 和可解析到目标 CineCameraActor 的 Binding。
- 不主动增加设计师未要求的碎切；设计师给定的切点按原规格执行，只有结构错误或用户要求诊断时才评估切点理由。
- 验证时需要确认是否误加摄像机，或用户要求有摄像机却没有 CameraCut。
- UE Python 版本可能没有 `LevelSequence.add_master_track()`；执行层应使用 live API 检查，必要时改用 `add_track(unreal.MovieSceneCameraCutTrack)`。
- CameraCut 结构验证统一按 `mcp-cinematic-execution.md` 的“CameraCut 完整性验证”执行，包括全范围覆盖、边界两侧画面、Binding 解析和保存重载。

## 轨道边界

- 本 Skill 给规格，不直接写轨道细节。
- 常见执行轨道包括 Camera Transform、CameraCut、Actor Transform、可见性、焦距/景深参数。
- Actor Transform 动画需要缓存进入序列前的原始 Transform，但不得默认在最后有效帧 K 回原位。
- 复杂动作要先拆阶段，再写 key，不要把“先 A 再 B”混成同时发生。

## 状态恢复与完成模式

- `Restore State`：序列停止或离开有效范围后恢复进入序列前的状态。优先使用 Sequence/Section 的 Completion Mode 或 Pre-Animated State 机制，不用可见关键帧模拟。
- `Keep State`：序列结束后保持最后求值状态。必须由设计师或玩法需求明确选择，并读回实际 Completion Mode。
- `Project Default`：只有项目已有明确约定时才可使用；报告中写出最终解析结果，不能只写“默认”。
- 只有设计师明确要求角色或物体在画面内执行“回位动作”，才允许在有效帧段内 K 回原 Transform；这属于可见动作，不属于状态恢复。
- 只有序列结束后的状态会影响已有场景 Actor、角色动画、车辆、门、机关、玩法状态或连续过场时，才强制选择并读回 Completion Mode。纯摄像机、CameraCut、焦距、焦点和独立 CameraRig 在没有结束状态要求时继承项目默认，不逐 Section 设置或专项验证。
- 涉及结束状态时，检查最后有效帧没有非预期回跳，并把画面内最后一帧与序列停止后的恢复/保持行为分开报告。设计师要求的关门、回位或收起等可见动作仍按正常关键帧执行，不能用状态恢复代替。

## 帧率和时间

- 分镜可以先用秒表达，交付时转换成帧。
- 默认使用项目 Sequencer 默认帧率；设计师明确指定帧率时才覆盖。
- 如果执行层无法读取项目或现有 Sequence 的帧率，先保留秒级规格并继续不依赖帧率的只读工作；帧率会影响写入范围、动画对齐或交付时必须询问，不静默使用 24fps 等通用默认值。
- 每个镜头段必须有起始时间、结束时间或持续时间。
- 批量镜头或批量 Actor 动画要控制总时长，避免节奏失控。

## 时间区间契约

- 规格层统一使用左闭右开区间 `[StartFrame, EndFrame)`：包含 `StartFrame`，不包含 `EndFrame`。
- 持续帧数固定为 `DurationFrames = EndFrame - StartFrame`。从第 0 帧开始的 N 帧内容写成 `[0, N)`，整数显示帧的最后有效帧是 `N - 1`。
- 示例：104 帧写成 `[0,104)`，有效帧为 `0-103`；507 帧写成 `[0,507)`，有效帧为 `0-506`；30fps 的 20 秒写成 `[0,600)`，有效帧为 `0-599`。
- 多段 CameraCut 默认首尾相接：上一段的 `EndFrame` 等于下一段的 `StartFrame`。例如 `[0,72)`、`[72,150)`；除非设计师明确要求空段或叠加，不允许出现意外空洞或重叠。
- 单个 Key 位于某个帧点，不是帧区间。区间的 `EndFrame` 默认不参与该 Section 的画面求值；需要结尾画面 Key 时，整数显示帧通常写在 `EndFrame - 1` 或更早的有效帧上。
- 分镜文字中的 `0-104`、`28-72` 等旧写法必须在执行前正规化为 `[0,104)`、`[28,72)`；如果原文无法判断结束帧是否包含，先根据用户给出的“持续 N 帧”或总时长消歧，仍不明确时询问，不能静默多算或少算一帧。
- 原生 UE Python 新建或修改 Section 时，优先用 `set_range(StartFrame, EndFrame)` 一次写入范围并立即读回；若只能分别设置起止帧，也必须以最终 Start/End/Duration 读回为准，不能把调用未报错当作成功。

## 三种时间率不要混用

- `Display Rate`：设计师和 Sequencer 时间轴看到的帧率，用于镜头段、CameraCut 和报告。
- `Tick Resolution`：MovieScene 内部保存时间的精度，不等同于显示帧率；写入和读回时使用 UE 的 FrameRate/FrameTime 转换，不手写浮点秒累积。
- 动画源采样率：AnimSequence 自己的采样频率，可能与 Display Rate 不同；不能把动画接口返回的采样点数量直接当成 Sequencer 持续帧数。
- 秒转换到显示帧时，优先使用 UE 的帧率转换能力。若边界不是整数显示帧，必须记录量化方式，并让相邻 CameraCut 复用同一个量化后的边界，避免缝隙或重叠。
- 如果 MCP、VibeUE 或某个 UE API 使用包含结束帧等不同语义，只在执行适配层转换；规格表、结果报告和跨文件交流仍统一使用 `[StartFrame, EndFrame)`。

## 时间读回最低要求

- 读回 `Display Rate`、`Tick Resolution`、Playback Range 的 Start/End/Duration。
- 读回每段 CameraCut 和关键 Section 的 Start/End/Duration，并验证 `Duration = End - Start`。
- 报告总持续帧数、最后有效显示帧，以及 CameraCut 是否连续、是否存在意外空洞或重叠。
- 动画任务额外报告动画时长、源采样率、接口返回的采样点/帧计数及 Sequencer Section 持续帧数；这些数值不一致时说明语义，不擅自改 Play Rate。

## 执行安全索引

- 范围、Key、保存、截图验证、旋转映射和 UE5.8 时间轴预览风险，统一见 `mcp-cinematic-execution.md`。
