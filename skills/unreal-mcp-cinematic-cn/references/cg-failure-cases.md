# CG 失败诊断索引

先判断问题属于镜头表达、Sequencer 结构、执行兼容、画面安全还是预览采集。案例只提供诊断入口；修复步骤以对应正式宿主为准。

## 快速分类

- A 到 B 自由飞行、全程无职责：查运动规划与标准制作门槛。
- 卡顿、顿挫、急停、反向抽动：查无目的 Key、曲线、双重控制和 Yaw。
- 黑/白屏、纯天空/地面/墙面、穿模、长遮挡：查 CameraCut、路径和画面安全。
- 轨道红色、Binding 无效、MCP 报类型错误：查执行兼容，不先改镜头。
- 截图正常但播放异常：需要真实运动证据，也要排查录屏/播放器采集链。

## 误触发 PIE/Simulate

症状：调用“检查播放状态”后 MCP 连续超时。优先检查是否误用 `editor_play_simulate()` 启动了 PIE/Simulate；停止写入，让用户手动结束播放后再做轻量连接检查。正式规则见 `mcp-cinematic-execution.md`。

## UE5.8 Sequencer API 变化

症状：`get_channels` 不存在、CameraCut Guid 转换失败或轨道存在但没有 Key。按 `ue-python-sequencer-fallback.md` 读回半成品、检查 live API，并只替换失败环节；不要重建整套 Sequence。

## 高层创建后重复轨道或 Section

症状：创建 CineCamera/CameraCut 后再次无条件添加，出现双 Transform、双焦点或重叠 CameraCut。按 `ue5-sequencer-basics.md` 的创建与幂等契约，先读回自动生成对象，再 set-or-replace 并删除已证明多余的对象。

## Property Track 通道或 Enum 封装异常

症状：Property Path 正确但 Channel Name 为 `None`，或 `set_camera_cut_binding` / `set_byte_track_enum` schema 正确却在运行时报参数或 enum 加载错误。保留半成品，按 `ue-python-sequencer-fallback.md` 使用实际通道名或局部原生 API，并保存重载验证。

## Orbit 用 Location Key 硬拼

症状：弧线镜头被多个无职责 Location Key 切成碎曲线。删除无职责 Key，按 `ue5-camera-implementation.md` 在 Crane、Rail/Spline 或 Transform 中选择合适主控，再按 `professional-camera-keyframing.md` 重建连续路径。

## 正脸语义错误

症状：结构正确但设计师反馈背对、侧反或不是正脸。优先相信画面反馈，回查设计师确认的正脸轴、机位侧和 Look At；不要用 Actor Forward Vector 辩解。

## 数据正常但播放不顺

截图和 Key 数量不能证明运动连续。等待真实播放、录屏或渲染；反馈卡顿时先查无目的 Key、控制权和曲线，不继续堆 Key。见 `professional-camera-keyframing.md`。

## 主 Transform 出现周期性密集 Key

症状：呼吸、步态、手持或震动被高频烘焙到 Camera Transform，多条通道布满周期性 Key，设计师难以修改主路径。按 `professional-camera-keyframing.md` 分离主运动与有机层，优先改用 Camera Shake Track；能力不足时使用可单独关闭和删除的 Additive/子序列，密集烘焙只作为隔离的最后回退。

## Rail + 动态 Look At 崩溃

UE5.8 播放中涉及 CinematicCamera/Sequencer 的数组越界时，保留 Rail 路径，把视线烘焙为少量 Rotation，关闭动态 Tracking 并分段验证。见原生回退与相机控制权规则。

## 焦点发虚

ManualFocusDistance 轨道存在不代表焦点生效。按 `ue5-camera-implementation.md` 检查 Focus Method、语义焦点目标、厘米距离、光圈、镜头范围和风险帧清晰度；不要用 Location/Rotation Key 修焦点。

## 焦距/焦点轨道变红

优先判定为 CineCameraComponent Binding 或真实属性路径错误。按 live schema 重建错误轨道并读回 property path、Section 和 Key；不要改构图或 CameraCut。

## Dolly Zoom / 相机双重控制

抖动、视线漂移或旋转抢控制时，按“相机控制权唯一”检查位置、朝向、焦点三类主控。Look At/Rotation、Transform/Rig、Manual/Tracking Focus 均不得无说明叠加。

## 预览采集链误判

录屏掉帧、窗口裁切、播放器复帧或错误 seek 会伪造卡顿/静止。先确认完整分辨率、稳定帧率和时间真实变化，再改 Sequencer。

## 结尾急刹

最后画面稳定不代表到位过程稳定。若设计师要求落稳，把主要位移、转向、焦距和焦点变化提前完成，最后 10%-15% 只做已要求的减速/稳定；不靠密集末尾 Key 抢救。

## Yaw 跨 180/-180

环绕镜头突然反向时先查 Yaw unwrap，例如 `-145 -> -180 -> -215`，不要用新增 Location Key 掩盖旋转断点。

## 结构成功但只是骨架

只有 LevelSequence、CameraCut、CineCamera 和起止 Key 不等于标准制作。按模式矩阵补齐设计师要求的路径、控制权、曲线、焦点、状态和风险帧验证。

## SkeletalMeshActor 读取失败

单个组件 API 失败不能判定场景无角色。改用 `skeletal_mesh_component`、bounds、editor property 或 `get_components_by_class()` 等只读路径复核，见 `ue5-character-animation.md`。

## 处理顺序

1. 先分清镜头、结构、执行、画面或预览采集问题。
2. 结构先修 Binding/Range；画面先修相机/焦点/曝光；运动问题必须结合真实播放证据。
3. 设计师反馈背对、切手、过高或看不清时，优先修画面语义，不用“结构正常”否定反馈。
