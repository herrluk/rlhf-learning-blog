# 奖励模型与 DPO：偏好怎样变成优化信号

[讲解总目录](README.md)

<!-- chapter-meta:start -->
本章关联 **18 道题**，按知识点合并讲解，跨章可重复关联。以下为最新样本的宽主题频次，不是细题命中概率。

| 主要考点 | 牛客（13帖） | 小红书（17帖） | 知乎（11帖） |
| --- | --- | --- | --- |
| 奖励模型 / 奖励设计 | 高 6/13 | 中 3/17 | 低 1/11 |
| DPO 原理或与在线 RL 比较 | 高 4/13 | 低 1/17 | 低 1/11 |

高 ≥4 帖、中 2–3、低 1；岗位优先级见原题。统计与来源见 [全网台账](../面试题库/08-全网来源与考频.md)。
<!-- chapter-meta:end -->

本章要区分三件事：真实希望提升的质量、对质量的代理评分，以及使用这个评分更新策略的目标函数。训练能稳定提高代理分数，并不自动证明真实质量提高。

<a id="reward-model"></a>

## 1. 从偏好对到 Bradley–Terry loss

<!-- q: R10 S07 E32 -->

<!-- question-links:start -->
对应面试题：[R10](../面试题库/04-RLHF与强化学习算法.md#R10)、[S07](../面试题库/03-SFT与后训练数据.md#S07)、[E32](../面试题库/10-全网扩展-RLHF算法.md#E32)。
<!-- question-links:end -->

一条偏好数据通常包含同一个 prompt x、较优回答 y_w 和较差回答 y_l。标注可以来自人工、规则辅助或模型评审，但必须明确“优”的标准。若正负回答连任务条件都不同，就不能直接把差异归因于回答质量。

奖励模型输出标量 r(x,y)。Bradley–Terry 假设偏好概率为：

```text
P(y_w 优于 y_l | x) = sigmoid(r_w-r_l)
L_RM = -log sigmoid(r_w-r_l) = softplus(-(r_w-r_l))
```

它不是简单最大化 `r_w-r_l`。令差值为 d，loss 对 d 的导数为 `sigmoid(d)-1`；当正例已明显更优时，梯度趋近于零，而直接负差值没有这种饱和结构。[InstructGPT](https://arxiv.org/abs/2203.02155)

两个回答的 reward 同时加常数，偏好概率不变。因此单靠成对排序无法识别所有绝对分数含义。`reward=5` 不自然等于“80% 正确”；跨 prompt、跨 RM 版本比较平均 reward 时需要校准和额外验证。

构造偏好对时，应匹配任务、避免训练评测污染，记录标签置信度、平局与错误标注。很容易区分的负例可以帮助初期学习，但如果全是明显胡言乱语，模型可能只学会识别表面错误，无法改善两个高质量回答之间的选择。

<a id="reward-source"></a>

## 2. ORM、PRM、RLHF、RLAIF 与 RLVR

<!-- q: R11 R24 -->

<!-- question-links:start -->
对应面试题：[R11](../面试题库/04-RLHF与强化学习算法.md#R11)、[R24](../面试题库/04-RLHF与强化学习算法.md#R24)。
<!-- question-links:end -->

Outcome reward 对最终结果评分，接口简单，适合答案或测试用例可验证的任务；但若只在最后给 0/1，早期动作的贡献难以区分。Process reward 对中间步骤评价，能提供更细的信号，但步骤边界、正确性标注和模型调用成本更复杂。[过程监督研究](https://arxiv.org/abs/2305.20050)

RLHF 强调人类反馈来源，常通过偏好数据训练 RM 后使用；RLAIF 使用 AI 反馈；RLVR 使用可验证结果，例如单元测试或确定的数学答案。它们是奖励来源与训练流程的描述，不是 PPO/GRPO 的互斥替代算法。规则奖励也可能被利用，例如只匹配最终字符串却没检验推导或程序行为。[Constitutional AI](https://arxiv.org/abs/2212.08073)、[DeepSeek-R1](https://arxiv.org/abs/2501.12948)

组合奖励可以包含正确性、格式和长度等项，但系数改变会改变最优行为。若格式奖励远大于任务奖励，模型可能稳定输出格式正确的错误答案。最有用的监控是逐分量统计和真实任务成功率，而非只有合成后的一个数。

<a id="reward-failure"></a>

## 3. Reward hacking、评分偏差与奖励漂移

<!-- q: R12 R26 E25 E33 E34 E35 -->

<!-- question-links:start -->
对应面试题：[R12](../面试题库/04-RLHF与强化学习算法.md#R12)、[R26](../面试题库/04-RLHF与强化学习算法.md#R26)、[E25](../面试题库/10-全网扩展-RLHF算法.md#E25)、[E33](../面试题库/10-全网扩展-RLHF算法.md#E33)、[E34](../面试题库/10-全网扩展-RLHF算法.md#E34)、[E35](../面试题库/10-全网扩展-RLHF算法.md#E35)。
<!-- question-links:end -->

当 reward 上升而独立成功率下降，应先建立可区分的假设。例如模型是否输出了验证器识别的关键词、变得更长、更重复，或利用了测试环境漏洞；再用独立验证器、人类盲审、未见任务与对抗案例逐一检验。

RewardBench 等基准评估奖励模型对不同任务和回答对的判断能力，但它与“被策略连续优化后的可靠性”不是同一个问题。策略会主动集中到评分器有漏洞的区域，所以高离线基准分数仍需在线优化压力测试。[RewardBench](https://arxiv.org/abs/2403.13787)

对于 LLM-as-a-judge，可以交换答案顺序检查位置偏置；用等长或按长度分桶的答案检查冗长偏好；隐藏候选模型名称并改变来源检查自偏好；重复评分检查随机性。记录 judge 版本、prompt 和解析逻辑，才能解释评分变化。[MT-Bench 与模型评审研究](https://arxiv.org/abs/2306.05685)

若 RM 与 policy 都持续更新，上一轮的 0.8 和这一轮的 0.8 可能已不是相同尺度。应保存 reward model version、必要时对固定校准集重评分，并明确旧样本是否重评。更新评分器不必然错误，但会让优化目标随时间移动，不能继续按“固定 reward”的假设解释全部曲线。

奖励饱和也有不同原因：任务确实已学会、任务过易、评分器无法分辨，或策略找到了漏洞。查看全对/全错组比例、独立验证、任务难度分桶及生成多样性。只有训练 reward 一条曲线时，这些情况很难区分。

<a id="dpo"></a>

## 4. DPO 为什么可以省去显式奖励训练

<!-- q: R13 C06 -->

<!-- question-links:start -->
对应面试题：[R13](../面试题库/04-RLHF与强化学习算法.md#R13)、[C06](../面试题库/06-手撕与白板练习.md#C06)。
<!-- question-links:end -->

考虑固定 prompt 下的 KL 正则化目标：最大化 `E_pi[r] - beta*KL(pi || pi_ref)`。在相应假设下，最优策略满足 `pi*(y) ∝ pi_ref(y)*exp(r(y)/beta)`。将它反解为 reward 的形式：

```text
r(x,y) = beta*log(pi*(y|x)/pi_ref(y|x)) + 只依赖 x 的常数
```

对同一 prompt 的两个回答取差，常数消失；代回偏好概率，就得到直接以策略概率参数化的偏好 loss：

```text
delta = [log pi_theta(y_w|x)-log pi_ref(y_w|x)]
      - [log pi_theta(y_l|x)-log pi_ref(y_l|x)]
L_DPO = -log sigmoid(beta*delta)
```

这说明 DPO 使用策略相对于 reference 的对数概率变化表达偏好，而不需要在标准流程中先单独训练一个标量 RM 再跑在线 PPO。[DPO 原论文](https://arxiv.org/abs/2305.18290)

序列 log-prob 通常是回答 token 的条件 log-prob 求和；prompt 为条件，不作为回答目标重复计分。policy 需要梯度，reference 通常冻结。实现可缓存固定参考策略的 log-prob，但必须绑定 tokenizer、模板与 reference revision，否则缓存失去语义。

这里的解析关系依赖目标和偏好建模假设，不意味着离线数据有限时一定学到真实奖励，也不意味着 DPO 在所有场景优于在线 RL。部署能力仍需生成评估。

<a id="dpo-bias"></a>

## 5. DPO 的 beta、长度偏差与 chosen 概率

<!-- q: R14 E29 E30 E31 -->

<!-- question-links:start -->
对应面试题：[R14](../面试题库/04-RLHF与强化学习算法.md#R14)、[E29](../面试题库/10-全网扩展-RLHF算法.md#E29)、[E30](../面试题库/10-全网扩展-RLHF算法.md#E30)、[E31](../面试题库/10-全网扩展-RLHF算法.md#E31)。
<!-- question-links:end -->

从固定 reward 的 KL 正则化问题看，beta 控制偏离参考分布的代价；从实际 DPO loss 看，它又缩放 sigmoid 的输入和梯度。因而不能只背“beta 越小更新越猛”这种单一方向结论，必须结合当前 margin、学习率和数据观察。

设 reference 对两个回答给出相同概率。policy 中 chosen 从 0.20 降到 0.18，rejected 从 0.20 降到 0.10。chosen 的绝对概率下降了，但两者概率比从 1 提升到 1.8，偏好 margin 反而改善。剩余概率可以转移到其他回答，所以这不违反归一化。DPO loss 降低不保证每个 chosen 的绝对概率都上升。

负例在当前模型下已经极不可能，也不自动说明它没有训练价值；需要看相对于 reference 的变化、另一边的概率和最终 margin。当 `beta*delta` 已很大，sigmoid loss 的梯度会饱和；错标 hard negative 则可能提供很强但错误的训练信号。

长度偏差来自数据与目标的共同作用。序列 log-prob 求和通常随长度积累更多负项；正负样本长度与任务成功相关时，模型可能学到长度捷径。除以 token 数会改变优化对象，并非无代价的修补。可以先做长度匹配、按长度差分桶和生成质量检查，再比较明确命名的 loss 变体。[TRL DPO Trainer](https://huggingface.co/docs/trl/main/en/dpo_trainer)

对于 GUI/Agent 轨迹，还需分清模型生成动作、环境观察与中间步骤是否进入概率和长度计算。把大量 tool observation 当作待优化回答，会使长度问题与错误 mask 混在一起。

<a id="choice"></a>

## 6. SFT、DPO、PPO、GRPO 的选择

<!-- q: R15 -->

<!-- question-links:start -->
对应面试题：[R15](../面试题库/04-RLHF与强化学习算法.md#R15)。
<!-- question-links:end -->

| 方法 | 主要学习信号 | 适合先问的问题 |
| --- | --- | --- |
| SFT | 正确示范的 token | 模型是否已经会基本任务和协议？ |
| DPO | 成对偏好及参考概率 | 偏好数据是否覆盖目标场景，长度/来源是否有偏差？ |
| PPO | 在线回报与 critic 优势 | 价值估计是否可靠，系统能否承担各组件成本？ |
| GRPO | 同 prompt 多回答的相对回报 | 组内是否有差异，采样与验证是否划算？ |

这是决策维度，不是固定阶段表。已有高质量偏好对时可以直接比较 DPO；任务可低成本验证且策略已有一定成功率时，可探索在线 RL。长任务需要更细 credit assignment 时，critic 的价值值得评估，但仍要测它的误差和额外成本。

## 本章面试表达练习

手写 BT 与 DPO 两个 loss，并标出各自的训练参数；再给一个“loss 降而 chosen 概率也降”的数值例子。最后解释一次 reward hacking 事件应怎样用独立证据确认。
