# Level Doctor 只读场景体检

用户要求“体检当前场景”“检查场景问题”“批量验收”或完成大批摆放后读取。v0.1 只生成证据和候选，不修改关卡。

## 执行

1. 确认当前 World，且编辑器不在 PIE/Simulate。
2. 用 live discovery 确认 `EditorActorSubsystem` 与 Actor Bounds API 可用。
3. 通过 `execute_python_code` 执行 [level_doctor.py](../scripts/level_doctor.py) 的完整源码；代码必须以 `import unreal` 开始。若 Unreal 进程可访问 Skill 路径，也可在 `import unreal` 后读取并 `exec(compile(...))`。
4. 记录 stdout 中的 `LEVEL_DOCTOR_REPORT`，读取 `<Project>/Saved/LevelDoctor/*.json` 摘要。
5. 按严重度筛选候选，用局部透视、玩家视角和必要的 PIE 复核；不要直接把候选当结论。
6. 汇报报告路径、Actor 数、候选数量、已复核问题和仍需人工判断的项目。

## v0.1 自动检查

- 当前关卡 Actor、Class、静态网格路径、Transform 与世界 Bounds 清单。
- 负缩放、强非均匀缩放和同类别尺寸离群候选。
- 小型道具接近或超过家具中位尺寸的语义尺度倒挂候选。
- 排除 Ground/Road 等承载对象后的 AABB 重叠粗筛。
- 相同网格位于近似相同位置的重复生成候选。

## 严重度

- `P0_CANDIDATE`：高风险候选，优先截图复核；仍不是自动定罪。
- `P1_CANDIDATE`：明显异常候选，结合场景语义复核。
- `REVIEW_MODULE_SEAM`：可能是合法模块接缝，检查收口、穿模、Z-fighting 和碰撞。

## 不得伪装成自动完成

脚本不检查真实网格形状、地表射线、Pivot、材质 UV、视觉构图、导航、触发、流送或性能。必须沿用本 Skill 的截图、射线、PIE 和质量 Gate 补齐证据。

名称分类只是启发式：资产名无法识别时保留 `unknown`，不要为了提高命中率猜资产语义。AABB 包含空体积，空心建筑内部道具可能被误报。

## 修复边界

v0.1 脚本绝不移动、缩放、删除、重命名或保存 Actor/资产。用户明确要求修复时，以报告为输入，先建立 Transaction、Checkpoint 或隔离 Data Layer，再按现有分阶段流程修复已复核问题并重新运行 Level Doctor。没有复核证据时不得批量自动修复。
