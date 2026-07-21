# UE5 摄像机实现参考

## 推荐对象

- 电影镜头优先使用 `CineCameraActor`。
- 多镜头剪辑使用 `LevelSequence` + `CameraCutTrack`。
- 只做物体动画且用户明确不要摄像机时，不创建 CameraActor。

## 常用参数

- 焦距 18-24mm：广角，空间感强，容易夸张透视。
- 焦距 35mm：自然叙事，适合中景和跟拍。
- 焦距 50mm：更接近人物/物体观察，适合情绪镜头。
- 焦距 70-100mm：压缩空间，适合特写、凝视、压迫。
- 景深：只在需要强调主体时使用，避免把关键动作虚掉。主体距离变化时同步设置手动焦点距离。

## CineCamera 属性绑定

- CineCamera 的焦距、焦点、景深参数通常在 `CineCameraComponent` 上，不要默认把 FloatTrack 绑定到 `CineCameraActor` 本体。
- 焦距不要硬写 `FocalLength`；先 live schema 检查当前组件可动画属性，常见属性名是 `CurrentFocalLength`。
- 手动焦点距离也要确认真实属性路径；`FocusSettings.ManualFocusDistance` 看起来合理，但必须以当前 UE 版本读回结果为准。
- 写 ManualFocusDistance 前必须确认并读回 Focus Method 已设置为 `Manual`；常见路径可能位于 `FocusSettings.FocusMethod`，以当前版本 live schema 为准。仅有距离 Key、但 Focus Method 不是 Manual，判定为焦点未生效。
- 如果 Sequencer 轨道或属性显示红色，通常说明绑定对象或属性路径错误；删除错误 FloatTrack，重新绑定到正确组件/属性，并读回验证。
- 写入后报告真实绑定对象、属性路径和 Key 数量；不要只报告“焦距/焦点已设置”。

## 焦点生效契约

- 焦点目标必须是有画面语义的空间点，例如脸、眼睛、胸口、出拳手臂、车辆驾驶室或明确道具；不得默认把 Actor Origin 当作正确焦点。
- ManualFocusDistance 使用 UE 世界距离，通常为厘米。每个焦点 Key 的值应来自相机位置到焦点目标空间点的距离，并在主体距离变化、切镜、近景、推拉或焦距变化时重新计算。
- 手动焦点方案必须同时验证：Focus Method=`Manual`、ManualFocusDistance 属性路径、单位/数值、Section Range、Key 数量和起始/中段/结束前风险帧的主体清晰度。
- Tracking Focus 与 ManualFocusDistance 是两种焦点主控方式。同一 CameraCut 区间只保留一个焦点主控；切换前先烘焙或确认切换帧，再关闭旧控制。
- 浅景深不是默认要求。光圈过大导致脸、拳、动作范围或关键道具部分发虚时，优先收小光圈或降低景深强度，再调整焦点 Key；不要用 Location/Rotation Key 修焦点。
- 焦距变化还要检查镜头预设允许范围和 Filmback；属性写入成功但超出镜头约束时，不得报告为有效焦距。

## 相机控制权唯一

每个 CameraCut 区间在写 Key 前必须声明位置、朝向和焦点的主控来源。每类控制默认只能有一个主控。

| 控制维度 | 可选主控 | 禁止组合 |
|---|---|---|
| 位置路径 | CineCamera Transform / CameraRig_Crane / CameraRig_Rail / Spline Path | 同时大量 K 世界 Location 与 Rig Progress/Yaw/Arm |
| 朝向 | Rotation Key / Look At Tracking / Rig Orientation | 动态 Look At 与密集 Rotation Key 同时控制；Rig 朝向与相机 Rotation 无说明叠加 |
| 焦点 | ManualFocusDistance / Tracking Focus | 两套焦点系统在同一区间同时生效 |

- Rig 控制位置时，CineCamera 只允许保留有明确构图职责的相对 Transform；不得再用世界 Location 硬拼同一条路径。
- Look At Tracking 控制朝向时，不添加与其竞争的 Rotation Key。需要回退为 Rotation 时，先在风险帧烘焙 Look At 结果、做 Yaw unwrap、读回 Rotation，再关闭 Tracking。
- 控制权在同一镜头内切换时，必须写明切换帧、旧主控关闭状态、新主控起始值和切换前后画面连续性；无法证明连续时不切换。
- 结果报告必须逐镜写出：位置主控、朝向主控、焦点主控，以及是否发现双重控制。

## 画幅与 Filmback

- 用户未指定输出比例时先读取现有 Sequence、项目渲染设置或明确的交付上下文；普通镜头仍无约定时可采用 16:9 并报告假设。
- 买量、投放、短视频或竖屏交付仍无法确认 9:16、1:1、4:5 等比例时必须询问；不要默认把 16:9 构图直接用于竖屏。
- 竖屏构图优先保证主体、动作结果、UI 安全区和最终记忆画面可读；机位可更近，但不要让角色头顶、武器、特效或关键道具被裁掉。
- 需要精确输出比例时，通过 CineCamera Filmback、传感器比例或项目渲染设置配合实现；具体 API 以当前 UE 版本 live schema 为准。

## 角色朝向

- MCP 读取到的 Actor Rotation、Forward Vector 或骨骼数据不能稳定等同于“角色正面/背面”，因为模型导入轴向、动画姿态和绑定方式可能不同。
- 镜头依赖正脸、背影、转身方向、侧脸角度或英雄姿态时，优先使用设计师已给正脸轴。未提供时可以只读检查 SkeletalMeshComponent 相对旋转、骨架/Root 关系，并从 `+X/-X/+Y/-Y` 候选视角获取截图辅助判断。
- Actor Forward Vector、资产命名或单一旋转数据不能单独作为结论。候选截图能清楚读到脸、眼睛、胸口和背部关系时，可以采用并报告视觉依据；视觉仍不明确、角色遮脸、处于转身动作或标准制作风险较高时，必须询问设计师。
- 如果设计师明确角色正脸轴为本地 `+Y`，正面机位应位于角色本地 `+Y` 一侧并看向角色；背面机位位于本地 `-Y` 一侧。Actor 有世界旋转时，先把本地轴转换到世界方向，不要把机位侧和拍摄朝向反过来。
- 写完依赖正脸/背影/侧脸的机位后，必须做画面语义校验：脸、眼睛、胸口朝向、背部轮廓或侧脸角度是否符合设计师需求。若截图/录屏反馈与数据方向判断冲突，优先相信清晰画面反馈并修正机位侧、Look At 或 Rotation。

## CameraCut 转场

- 默认使用硬切，保持动作和视线连续。
- 只有设计师明确要求相机间平滑过渡时，才启用 CameraCut Track 的 `Can Blend` 并允许 CameraCut Section 重叠。CameraCut Blend 会同时混合相机 Transform 与 CineCameraComponent 属性；写入后必须检查重叠范围、两侧 Binding、焦距、景深和焦点连续性，不能只验证位置旋转。
- 只有设计师明确要求黑场、白场、淡入淡出或梦境/回忆式过渡时，才添加 Fade Track 或等效转场。
- 转场必须有目的：隐藏时空跳跃、制造闪白冲击、做章节停顿或服务情绪；不要为了“更电影感”默认加 dissolve。
- 写入后按 `ue5-sequencer-basics.md` 的时间区间契约读回转场和 CameraCut 的 `[StartFrame, EndFrame)`、持续帧数及覆盖关系。

## Camera Shake Track

- 高频呼吸、步态、手持或冲击优先作为 CineCamera Binding 下的 `MovieSceneCameraShakeTrack` 独立存在，不写入主 Transform。
- Section 使用 `MovieSceneCameraShakeSection`；写入并读回 `shake_data.shake_class`、`play_scale`、`play_space` 和 `[StartFrame, EndFrame)`。Shake BP/资产必须保存，Class 能解析到预期类型。
- `CameraShakeBase` 的 Root Pattern 按运动语义选择：Wave 表达平滑周期运动，Perlin 表达不规则噪声，Sequence 使用可精确编排的 Camera Animation Sequence，Composite 分层组合多种 Pattern；以当前 UE live schema 为准，`LegacyCameraShake` 仅作为兼容候选。先用短 Section 完成创建、绑定、MRQ/播放生效的端到端能力测试，再用于正式长镜头。
- 不同频率或运动语义优先使用不同 Shake 资产或 Section；`play_scale` 只调强度，不能证明频率已经改变。
- 封装或 BP 创建失败时，只回退高频有机层并保留主路径；回退顺序与可编辑性验收见 `professional-camera-keyframing.md`。

## 环绕镜头 Rig 选择

当镜头围绕单个角色、道具、车辆或小主体做半环绕、摇臂、绕拍时，根据路径形状、遮挡、可用 API、返工成本和现有工程模式，在 Crane、Rail/Spline 或 CineCamera Transform 中选择；不要把任一 Rig 当成镜头类型的固定答案。

Crane 已经控制环绕时，CineCamera Rotation 默认只 K 起点和终点；不要习惯性补中段 Rotation Key。只有预览证明主体出画、构图失控或遮挡无法读懂时，才允许加中段 Rotation Key，并在交付报告里说明原因。

当镜头沿道路、街区、建筑群、战场、地图区域等大空间穿行、侧绕或复杂路径移动时，优先 `CameraRig_Rail` / spline path。若本该围绕单个主体却选择 Rail，必须说明原因，例如半径过大、空间遮挡、需要沿路径避障或主体不是稳定中心点。

Crane/Rail 写入后必须读回：Rig Actor、CineCamera 挂接/父子关系、相机相对 Transform、实际主控属性名称与路径、Section Range、Key 数量和 CameraCut 目标。`current_position_on_rail`、Crane Yaw/Arm/Pitch 等属性以 live schema 为准，不硬编码版本假设。
## Camera Path 控制方式

执行前先选择路径控制方式，不要默认直接给 CineCameraActor 世界 Location 打帧。

| 镜头类型 | 优先方案 | 不推荐 |
|---|---|---|
| 推镜 / 拉镜 / 升降 | CineCamera Transform 或符合项目模式的 Rig；使用最小有效主控集合 | 为了“更电影感”堆无目的 Location Key |
| 半环绕 / Orbit | 按半径、遮挡、路径复杂度和工具能力选择 Crane、Rail/Spline 或 Transform | 无视控制权、只按镜头名称固定 Rig |
| 弧线推进 / 侧绕 / 穿街 | CameraRig_Rail 或 spline path | 默认 3-5 个世界坐标 Key |
| 低机位掠过揭示 | CameraRig_Rail + 少量前景控制点 | 长时间遮挡主体的密集 Key |
| Dolly Zoom | 简单路径用 Transform + 焦距 + 手动焦点距离；复杂路径用 Rail + 焦距 + 手动焦点距离 | 只改焦距或只移动相机 |

## 验证索引

时间与 CameraCut 按 `ue5-sequencer-basics.md`，Key 与曲线按 `professional-camera-keyframing.md`，画面和曝光按 `cg-staging-lighting.md`，执行读回按 `mcp-cinematic-execution.md`。本文件不重复维护交付清单和通用风险表。
