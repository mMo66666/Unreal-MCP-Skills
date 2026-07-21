# UE5 角色动画协同

用于设计师镜头涉及角色动作、转身、登场、攻击、表演或动画资产时，把角色动画和 CameraCut 对齐。只记录最小执行规则，不替代动画系统文档。

## 最小规则

- 角色动画需求必须写清：角色 Actor、动画资产或占位动作、起止时间、关键动作帧、是否保持最终姿态。
- 如果设计师说“第 N 秒转身 / 抬头 / 出手 / 命中 / 落地时切镜”，CameraCut 必须对齐该动作时间点，而不是平均分段。
- 动画时长和镜头时长不一致时，优先保持动画实际帧率和 Play Rate，通过镜头范围、CameraCut 或非破坏性留白协调；只有必须裁切、拉伸、循环或改变动作节奏时才询问设计师。
- 动画资产缺失时，先完成不依赖动作内容的结构规格并报告缺口。只有设计师已授权占位或任务明确是占位验证时，才使用 Idle、TPose、现有近似动画或文字标注；不得自行新增角色行为。
- 涉及正脸、背影、侧脸或转身方向时，按 `ue5-camera-implementation.md` 的角色朝向规则执行：优先使用设计师信息和候选视角证据，仍无法可靠确认时再询问。
- 设计师明确表示已替换动画、Skeletal Mesh 或绑定后，重新读取当前 Actor 的实际资产路径、时长、采样率和 Play Rate；不得沿用替换前的勘察结果，也不得按旧资产名称判断新内容。
- Root Motion 关闭且 Actor Transform 静止，只能证明 Actor 本体未移动；骨盆、Root、头部或其他骨骼仍可能产生显著画面位移。角色跟拍、近景裁切和焦点设计应按关键姿势采样真实骨骼/包围盒轨迹，不能只看 Actor Location。

## 动画帧数与采样点

- 动画 Section 和 CameraCut 统一使用 `[StartFrame, EndFrame)`；持续帧数为 `EndFrame - StartFrame`，规则见 `ue5-sequencer-basics.md`。
- 必须分别读取并报告：动画时长（秒）、动画源采样率、动画接口返回的帧/采样点计数、Sequencer Display Rate、动画 Section `[StartFrame, EndFrame)` 和 Section 持续帧数。
- `get_num_frames()`、DataModel 帧数或类似接口的结果可能表示采样点、姿势数量或源数据计数，不能仅凭该数字决定 Playback Range，也不能看到 `508` 就自动把设计师给的 507 帧改成 508 帧。
- 当“持续 N 帧”和“源采样点数量”相差 1 时，先按左闭右开区间检查是否只是末端采样点语义；再核对动画时长与源采样率。仍无法解释时报告差异并询问，不修改 Play Rate、不静默裁切。
- 动画 Section 写入后读回 Start/End/Duration、Start Offset、End Offset 和 Play Rate；用户要求保持原动画速度时，Play Rate 必须保持原值。
- 写入动画 Section 的 Play Rate 前先检查属性类型。UE5.8 中若 `MovieSceneSkeletalAnimationParams.play_rate` 为 `MovieSceneTimeWarpVariant`，用 `set_fixed_play_rate()`，并在可用时用 `to_fixed_play_rate()` 读回；只有数值类型才直接写浮点数。
- 角色或动画轨道结束后的状态按 `ue5-sequencer-basics.md` 的 Completion Mode 执行；不得在最后有效帧自动 K 回原 Transform 或默认切回 Idle。

## SkeletalMeshActor 读取兼容

UE5.8 / MCP 环境里，部分 `SkeletalMeshActor` 不一定暴露常规 `get_components()`、组件 `get_component_location()` 或同名封装方法。读取角色时优先尝试 `actor.skeletal_mesh_component`、bounds、editor property 和 `get_components_by_class()` 等路径；单个 API 失败不能直接判断“场景里没有角色”。如果位置、包围盒或组件读取不完整，报告兼容限制并换只读路径复核。
## Sequencer 规格字段

角色动画镜头至少补充：

- Skeletal Mesh / Character / Blueprint Actor 绑定方式。
- 动画资产路径或占位方式。
- Anim Track / Montage / Actor Transform 是否需要写入。
- 动画 Section `[StartFrame, EndFrame)`、持续帧数、最后有效帧、关键动作帧和 CameraCut 对齐点。
- 动画与镜头时长不匹配时的设计师选择。

## 验证

- 结构验证：角色 Actor 是否绑定，动画轨道是否存在，动画 Section 的 Start/End/Duration 是否符合 `[StartFrame, EndFrame)`，并覆盖计划帧段。
- 状态验证：只有动画结束状态会影响已有场景、角色后续行为或连续过场时，才读回 Completion Mode，并分别检查最后有效帧姿态与序列停止后的恢复结果；没有结束状态要求时继承项目默认。
- 画面验证：关键动作帧是否在画面内，是否被遮挡、裁切或焦点虚化。
- 位移验证：角色动画可能改变可见重心时，抽查 Root/Hips/Head 或包围盒在关键姿势的世界位置，并据此检查构图、距离和焦点。
- 运动验证：相机运动不要抢走关键动作阅读时间；动作发生前后要留足可读帧。
