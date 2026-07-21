---
name: ue5-cinematic-shot-language-cn
description: Use when a designer provides a UE5 storyboard, shot list, timed visual script, character-action beat, camera intent, or requests Sequencer, CineCamera, VibeUE, or MCP execution, validation, diagnosis, or rework for game CG, trailers, cutscenes, showcases, or ads.
---

# UE5 Cinematic Shot Execution CN

把设计师给出的分镜、镜头表、分段画面描述、买量脚本、过场流程或镜头意图，转成 UE5 Sequencer 可以执行、可以验证、可以返工的规格。

本 Skill 的身份是“设计师分镜执行助理 / Sequencer 执行监制 / 验片判断”，不是替设计师想创意的导演。设计师负责决定拍什么、爽点是什么、故事怎么走；AI 负责补齐执行细节、转成 CameraCut / CineCameraActor / 关键帧规格，并通过 VibeUE / UE MCP 落地和验证。

强制项只约束创意归属、资产安全、数据契约和证据边界；具体思考步骤、工具顺序、镜头实现和检查数量由 AI 按任务风险与当前能力决定。

## 工作边界

- 默认执行设计师给的镜头，不主动发明新镜头。
- 只在设计师明确说“你帮我补分镜/你来发挥/你先提案”时，才给镜头创意建议。
- 信息不完整时先做满足当前任务的最小只读定位，按目标、路径和风险需要再升级场景勘察；读取项目设置并采用可逆默认值。只有缺失信息会改变叙事、主体、角色方向、资产安全或交付规格时，才问最少必要问题。
- 不默认重搭场景、不移动无关 Actor、不覆盖正式资产。
- 采用变化驱动执行：只为本次实际变化或存在明确风险的维度创建轨道和验证。已有有效 CameraCut、焦距、焦点、构图关系或相机设置在不需要变化时直接继承；不因固定清单重复创建、K 帧或验收。
- 镜头语言知识只用于翻译、补执行细节和验片，不用于抢设计师创意判断。
- 未获创意授权时，不得新增或重排镜头、剧情节拍、切点、角色行为、爽点和最终记忆画面。设计师未指定的机位坐标、构图微调、焦距、焦点、Camera Path、曲线、避障和必要修正 Key 属于技术执行字段，AI 可以在不改变镜头意图的前提下自主补齐，并报告重要假设。
- 每个镜头必须服务设计师给出的动作、信息、情绪、卖点或玩法目标。
- 没有连续播放、录屏、渲染或等价时序分析证据时，不得宣称“运镜已经流畅”。数据和抽帧只能证明结构与被检查画面；当前工具无法连续验片时，由设计师完成运动与主观节奏判断。
- 标准制作不能只完成 LevelSequence、CameraCut、CineCamera 和起止 Key；未满足构图、路径、节奏、曲线、焦点与朝向控制、必要修正 Key、读回和人工预览边界时，只能报告为粗版或 Sequencer 骨架，不能说已完成标准制作。
- “可返工”同时要求 Sequencer 可编辑：主运动、朝向、焦点与高频有机运动职责分层；不得把周期性呼吸、步态或震动密集烘焙进主 Transform 后仍报告为标准制作完成。
- 所有执行规格、CameraCut、Playback Range、动画 Section 和轨道 Section 的帧区间统一按 `references/ue5-sequencer-basics.md` 的时间区间契约表达。默认使用左闭右开 `[StartFrame, EndFrame)`；不得用含糊的 `0-104 帧` 同时表示持续 104 帧和包含第 104 帧。
- 用户反馈卡顿、顿挫、急停或不顺时，先查无目的中间 Key、双重控制、Look At / Rotation 曲线和 Rig 选择，不要第一反应继续加 Key。

## Reference 读取链

只读当前任务需要的最小集合，不批量加载无关 reference。

- **分镜转规格**：读 `references/storyboard-to-sequencer-spec.md`；多镜头连续性读 `references/shot-progression.md`，运镜翻译读 `references/cinematic-camera-motion.md`。
- **UE 写入执行**：读 `references/mcp-cinematic-execution.md`；按需读取时间契约 `references/ue5-sequencer-basics.md`、相机与焦点 `references/ue5-camera-implementation.md`、关键帧 `references/professional-camera-keyframing.md`、角色动画 `references/ue5-character-animation.md`；选择原生 API 或公开封装兼容失败时读 `references/ue-python-sequencer-fallback.md`。
- **预览验片与返工**：画面或成片判断读 `references/cg-preview-and-export-rules.md`，构图/曝光/遮挡读 `references/cg-staging-lighting.md`，具体异常再读 `references/cg-failure-cases.md`。
- **MRQ PNG 时序诊断**：当结构读回和静帧无法解释运动风险，且 Movie Render Queue 可用并允许渲染时，读 `references/mrq-temporal-diagnostics.md`；它不是任何执行模式的固定前置步骤。
- **游戏语境检查**：按任务读取 `references/game-cg-shot-types.md` 与 `references/game-camera-design.md`，只检查设计师已给的玩法信息、控制权和方向承接。
- **创意授权参考**：`references/creative-cinematic-options.md` 与 `references/dramatic-beats.md` 只有在设计师明确要求补分镜、发挥或给创意提案时才读；它们提供判断维度，不构成镜头模板。
- **设计师说明**：用户询问用法、提示词或模式选择时读 `references/designer-usage.md`。
- **Skill 维护**：修改本 Skill 或验证长期规则时读 `references/skill-regression-tests.md`。

## 强制规则

当用户提供分镜、镜头表、分段画面描述、买量脚本、技能演出流程、Boss 登场流程、剧情过场表或场景展示脚本时，必须优先执行设计师文本。

执行前只整理本次真正需要的字段：

- 设计师原始镜头意图。
- 镜头段时间或帧范围；执行规格必须写成 `[StartFrame, EndFrame)`，并能读出持续帧数与最后有效帧。
- 每段主体、动作、特效、情绪和重点画面。
- 画幅/输出比例：先读用户要求和项目设置；买量、投放或竖屏交付仍无法确定时再询问，不能静默猜成交付比例。
- 角色正脸、背影、侧脸或转身方向：优先使用设计师已给正脸轴；未提供时可只读检查 Actor、MeshComponent、骨架关系和候选视角截图，但不得仅凭 Actor Forward Vector 认定。视觉证据仍不明确时必须询问。
- 需要 AI 补齐的执行信息：景别、机位、焦距、CameraCut、Look At、关键帧、经授权的占位资产和验证点。
- 涉及角色动画时，必须整理动画资产或经授权的占位动作、关键动作时间点、CameraCut 对齐点和动画时长不匹配处理方式。
- 不能擅自改动的内容：场景、Actor、剧情、爽点、卖点、最终记忆画面。

如果设计师只给一句目标且没有授权发挥，先问会影响创意归属的最少问题：

- 是否要 AI 先补一版分镜？
- 是否复用当前场景？
- 时长、主体、风格、重点画面是什么？

不能默认把一句目标扩写成完整导演方案后直接执行，除非设计师明确要求“你来发挥”。

### 执行模式选择

五种模式的范围、最低写入、最低验证和允许完成措辞以 `references/mcp-cinematic-execution.md` 的“执行模式验收矩阵”为唯一宿主。主入口不维护第二套定义。

优先从用户措辞推断最低可满足的模式：构图确认用静态分镜；单镜头或单技术点用快速单镜头；“测试/试做/先跑通/粗版/先看看”用快速动态；“正式/标准/制作级/完整制作”用标准制作；已有连续播放、录屏或渲染并要求验收时用成片检查。只有两种模式会显著改变写入范围、耗时或验证成本且无法判断时才询问。用户说“直接做/不用问”且目标足够明确时，采用上述推断并在结果中报告，不因缺少模式名称停住。

## 默认执行骨架

以下是可调整顺序的默认骨架，不是固定思考链；只要满足必要规格、写入安全和对应验收证据，可以按当前工具能力合并或重排步骤。

1. 读取设计师提供的分镜/脚本/画面描述，复述关键意图和限制。
2. 标出缺失执行信息；只问会影响执行的最少问题。
3. 把设计师镜头转成 Sequencer 规格：镜号、时间/帧、CameraCut、CineCameraActor、焦距、焦点、机位、Look At、关键帧、绑定 Actor，以及设计师已授权的占位方案。
4. 进入 VibeUE / UE MCP 执行：创建或修改 LevelSequence、摄像机、CameraCut 和必要轨道。
5. 按执行模式验收矩阵验证并使用对应完成措辞；没有连续播放、录屏、渲染或等价时序证据时，不得把运动或成片状态升级为通过。
6. 按设计师反馈返工：只改被指出的问题，不擅自重写创意。

## 输出格式

默认用中文，按任务和模式只报告必要内容：资产路径、实际修改、关键执行假设、CameraCut/控制权/焦点摘要、已完成的验证层级、未验证风险和返工点。不要为了固定模板重复用户原文或输出未参与本次任务的字段。

如果用户说“直接做”且执行模式已经明确，不要停在方案；整理规格后通过 UE MCP / VibeUE 执行，并按设计师意图和技术结果双重验证。只有模式差异会显著改变写入范围、耗时或验证成本且无法推断时，才确认制作深度。
