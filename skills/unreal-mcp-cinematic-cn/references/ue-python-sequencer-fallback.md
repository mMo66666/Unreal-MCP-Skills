# UE Python / Sequencer 原生回退

只在 MCP/VibeUE 参数符合公开 schema、但封装因版本或类型转换失败时读取。先读回半成品，不因报错直接重建或改镜头。

## 通用顺序

1. 检查工具 schema、参数和错误类型。
2. 读回 LevelSequence、Binding、Track、Section、Camera/Rig 和保存状态。
3. 用 live schema / `hasattr()` 检查当前 UE Python 能力。
4. 接口仍不明确时，优先检查当前 Engine 目录下 `Plugins/MovieScene/SequencerScripting/Content/Python` 的官方示例及同版本 Python API/引擎头文件，不照搬其他 UE 版本片段。
5. 只替换失败环节，保留有效半成品。
6. 保存并重新加载，按 `mcp-cinematic-execution.md` 完整验证。

写入调用即使最终返回异常，也可能已经完成前半段修改；回退或重试前必须重新读取目标 Binding、Track、Section、Key 和属性状态。

## LevelSequence

- 已有资产使用当前版本可用的加载 API，常见为 `EditorAssetLibrary.load_asset`；不要创建同名副本。
- 新建时先检查路径和同名资产；常见原生路径为 AssetTools + `LevelSequenceFactoryNew`，默认不覆盖。
- 立即设置并读回 Display Rate、Tick Resolution、Playback `[StartFrame, EndFrame)` 和 Duration。

## Binding 策略

- 已有场景 Actor 使用 Possessable。序列自带 CineCamera 可用 Spawnable，但必须先确认组件子 Binding 稳定；否则使用明确创建的 CineCameraActor Possessable。
- 复用 Binding 前解析到实际对象；显示名相同不代表对象相同。不得静默转换 Possessable/Spawnable。
- Spawnable CineCamera 缺少组件 Binding 时，用当前可用的 `add_possessable(component)`/父子 API 显式绑定 CineCameraComponent；清理临时 Binding 前先证明重复。
- Spawnable 的 Actor Template 存在时也不保证能直接取得 CineCameraComponent，组件子 Binding 的 Object Template 也可能为空；先做能力检查，不能访问模板组件时使用组件 Property Track。

## CameraCut

- 没有 `add_master_track()` 时使用 `add_track(unreal.MovieSceneCameraCutTrack)`。
- 优先用 `sequence.get_binding_id(binding)` 获取完整 ObjectBindingID，再调用 `set_camera_binding_id`；当前版本没有实例方法时，能力检查后再使用 `MovieSceneSequenceExtensions.get_binding_id(sequence, binding)`。不要传普通 Guid、字符串 Guid 或 `binding.get_id()`。
- 当前封装若在 `set_camera_cut_binding(section, camera_binding_id)` 报参数签名不一致，先确认半成品 Section，再按上一条局部回退。不要因封装报错新建第二个 CameraCut Section。
- `MovieSceneObjectBindingID` 不保证暴露 `is_valid()`；优先读回导出文本中的非零 Guid，并验证它能解析到唯一预期相机。
- 不用 Python `==` / `!=` 判断两个 UE `Guid` Struct 的值是否一致；包装对象可能在文本相同的情况下仍返回不相等。诊断时比较规范化的 `to_string()`，最终有效性以完整 `MovieSceneObjectBindingID` 能否通过 `resolve_binding_id()` 解析到预期 Binding 为准。
- 完成后执行 MCP 文件的 CameraCut 完整性验证。

## Transform 与属性轨道

- UE5.8 Transform Section 优先使用 `get_all_channels()`；通道名可能带后缀，按 `Location.X`、`Rotation.Y` 等语义前缀匹配。
- 焦距、Focus Method、ManualFocusDistance 和景深绑定到 CineCameraComponent 的真实属性，先 live schema 检查。
- FloatTrack 读回优先使用可用的 `get_property_name()` / `get_property_path()`；红轨道或无效路径先删除错误轨道，再按正确组件重建。
- Property Track 的 Display Name、Property Path 和 Channel Name 是三套信息。Key 写入前读取真实通道名；通道暴露为 `None` 时可按该实际名称操作，但必须独立验证 Property Path、Section 和 Key。
- `set_byte_track_enum` 若因 enum 加载参数失败，能力检查后可在原生轨道调用 `set_byte_track_enum(unreal.CameraFocusMethod.static_enum())`；Focus Method=`Manual` 的枚举值写入后仍需读回属性路径、Enum 和 Key。
- 重跑使用 set-or-replace，按 Binding、轨道类型、属性路径、Section 和帧位更新；不要追加重复对象。

## Rig 与 Look At

- Rig 的挂接和位置/朝向/焦点主控遵守 `ue5-camera-implementation.md`；写入后读回父子关系、相对 Transform、主控属性和 CameraCut 目标。
- 动态 Look At 不稳定时保留路径，使用少量 Rotation Key 烘焙视线并关闭 Tracking。常见计算入口为 `MathLibrary.find_look_at_rotation`，调用前仍做能力检查。
- 烘焙后执行 Yaw unwrap，验证切换帧连续且旧控制已关闭。

## 保存与停止条件

- 保存 LevelSequence 资产包并重新加载；重复验证 Playback、CameraCut、Binding、组件 Binding、参与的属性路径和关键 Key；只有存在结束状态要求时才验证 Completion Mode。
- 只有读回证明对象无效、重复或绑定错误时才清理；封装报错本身不是清理依据。
- 状态未知、原生 API 不可用、必须改插件/重启，或继续操作可能破坏正式资产时才停止并报告。
