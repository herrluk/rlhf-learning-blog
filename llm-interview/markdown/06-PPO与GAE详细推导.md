# PPO 与 GAE：从策略梯度到训练张量

[讲解总目录](README.md)

<!-- chapter-meta:start -->
本章关联 **15 道题**，按知识点合并讲解，跨章可重复关联。以下为最新样本的宽主题频次，不是细题命中概率。

| 主要考点 | 牛客（13帖） | 小红书（17帖） | 知乎（11帖） |
| --- | --- | --- | --- |
| PPO / GRPO 原理与选型 | 高 8/13 | 高 4/17 | 中 3/11 |
| 优势函数 / GAE / 组内优势 | 中 3/13 | 中 2/17 | 中 2/11 |
| on-policy / off-policy 与策略差异 | 低 1/13 | 高 5/17 | 中 2/11 |

高 ≥4 帖、中 2–3、低 1；岗位优先级见原题。统计与来源见 [全网台账](../面试题库/08-全网来源与考频.md)。
<!-- chapter-meta:end -->

本章使用最大化收益的目标 J；代码通常最小化 `loss=-J`。先固定符号和终止语义，可以避免大部分“公式背对了、实现却相反”的问题。

<a id="mdp"></a>

## 1. 将文本生成写成 MDP

<!-- q: R03 R04 E38 -->

<!-- question-links:start -->
对应面试题：[R03](../面试题库/04-RLHF与强化学习算法.md#R03)、[R04](../面试题库/04-RLHF与强化学习算法.md#R04)、[E38](../面试题库/10-全网扩展-RLHF算法.md#E38)。
<!-- question-links:end -->

状态 s_t 包含 prompt、已经生成的前缀及必要的环境观察；动作 a_t 是下一个 token，或在更高层定义的一次完整工具动作；转移是在状态中加入动作并可能执行环境；reward 可以在每步、每轮或整条轨迹结束时给出。若把 token 和工具回合混合建模，必须说明一次“时间步”代表什么。

目标是最大化回报期望。最简单的 REINFORCE 梯度可写成 `E[return * grad log pi(action|state)]`。直觉是提高高回报动作的概率，但不同问题本身难度不同，直接使用回报会产生较大方差。

减去只依赖状态、而不依赖当前采样动作的 baseline，在适当条件下不改变策略梯度期望，因为 `E_a[grad log pi(a|s)]=0`。Actor-Critic 用价值函数 V(s) 近似这个基线，并帮助估计回报；PPO 则进一步限制使用一批旧样本更新策略的方式。基线如何估计与策略目标如何更新，是两个不同层次。

On-policy 指数据来自当前或足够接近的行为策略；off-policy 允许行为与目标策略不同，并依赖相应处理。它们不等于联网和断网，也不能与数据是否继续在线采集混为一谈。PPO 可以对一批样本做多轮小批量更新，但这不代表可以无条件使用任意旧 replay 数据。[PPO](https://arxiv.org/abs/1707.06347)

<a id="components"></a>

## 2. Actor、critic、reward 与四种策略身份

<!-- q: R01 R02 R21 -->

<!-- question-links:start -->
对应面试题：[R01](../面试题库/04-RLHF与强化学习算法.md#R01)、[R02](../面试题库/04-RLHF与强化学习算法.md#R02)、[R21](../面试题库/04-RLHF与强化学习算法.md#R21)。
<!-- question-links:end -->

Actor 是待优化策略；critic 预测从当前状态开始的预期回报；reward model 或规则评价动作结果；reference 提供偏离约束的参照。Critic 预测未来收益，RM 评价回答质量，二者输入输出语义和训练目标不同，不能只因为都输出标量就互换。

| 符号 | 含义 | 典型生命周期 |
| --- | --- | --- |
| pi_theta | 当前正在更新的策略 | 每个 optimizer step 改变 |
| pi_old | 本轮 PPO 比率的冻结分母策略 | 通常在本批更新期间固定 |
| pi_rollout | 真正生成数据的行为分布 | 由版本、推理后端和采样处理共同决定 |
| pi_ref | KL 或偏好目标中的参考策略 | 通常在较长阶段冻结 |

pi_old 与 pi_rollout 在理想同步实现中可以一致；异步和训推数值差异下未必一致。old log-prob 可以在采样或重算时保存，不意味着显存必须一直常驻一份完整 old model。reference 即使初始化与 old 相同，其语义也不同。[verl rollout correction](https://verl.readthedocs.io/en/latest/algo/rollout_corr.html)

一轮典型流程是：冻结采样版本 → 生成回答 → 评分并获取 old/ref log-prob 与 value → 计算 advantage/return → 多个 mini-batch 更新 actor/critic → 发布新权重。下游任何重排都必须同时携带 token、mask、概率、value、reward 和样本 ID。

<a id="gae"></a>

## 3. GAE 公式与一条完整手算轨迹

<!-- q: R06 E22 C04 -->

<!-- question-links:start -->
对应面试题：[R06](../面试题库/04-RLHF与强化学习算法.md#R06)、[E22](../面试题库/10-全网扩展-RLHF算法.md#E22)、[C04](../面试题库/06-手撕与白板练习.md#C04)。
<!-- question-links:end -->

定义一步 TD 残差 `delta_t=r_t+gamma*V(s_(t+1))-V(s_t)`。GAE 用未来 TD 残差的衰减和估计优势：

```text
A_t = delta_t + gamma*lambda*A_(t+1)
```

gamma 控制任务中未来奖励的折扣；lambda 控制优势估计中更远 TD 残差的权重。lambda=0 只使用一步 TD；在终止轨迹上 gamma=1、lambda=1 时，残差相消，得到完整回报减当前 value。中间值在方差、bootstrap 误差和估计跨度间取舍。[GAE](https://arxiv.org/abs/1506.02438)

手算一个 3 步轨迹，reward 为 `[0,0,1]`，value 为 `[0.2,0.3,0.4]`，最后真终止，取 gamma=1、lambda=0.9：

```text
delta_2 = 1 + 0 - 0.4 = 0.6
delta_1 = 0 + 0.4 - 0.3 = 0.1
delta_0 = 0 + 0.3 - 0.2 = 0.1

A_2 = 0.6
A_1 = 0.1 + 0.9*0.6 = 0.64
A_0 = 0.1 + 0.9*0.64 = 0.676
```

常见的 value regression target 取 `A+V_old`，本例为 `[0.876,0.94,1.0]`。它是由该估计器构造的 target，不应误称为所有位置都等于 1 的纯 Monte Carlo return。用于 actor 的 advantage 和用于 critic 的 target 通常应按设计 detach，避免反向传播到不该被更新的分支。

“PPO 是 MC 还是 TD”没有仅凭名字就唯一的答案：PPO 指策略更新目标，优势可以由不同估计器提供。回答应解释你使用的 return、GAE 和 critic bootstrap，而不是强行二选一。

<a id="termination"></a>

## 4. Terminal 与 truncation 为什么需要两个 mask

<!-- q: R07 R22 -->

<!-- question-links:start -->
对应面试题：[R07](../面试题库/04-RLHF与强化学习算法.md#R07)、[R22](../面试题库/04-RLHF与强化学习算法.md#R22)。
<!-- question-links:end -->

真终止表示任务已结束，例如定义为结束事件的 EOS；时间限制或采样长度限制可能只是当前片段结束，原任务仍可继续。若有有效的下一状态价值，后者可以 bootstrap；若产品定义将截断视为失败终止，则应按那个任务定义处理。工具超时也要区分环境故障和任务失败。

稳妥的递推将两种含义分开：

```text
delta_t = r_t + gamma*bootstrap_mask_t*V_next - V_t
A_t = delta_t + gamma*lambda*trace_continue_t*A_(t+1)
```

真终止时两个 mask 都为 0；非终止的采样片段边界，可令 bootstrap 为 1、trace_continue 为 0，防止把下一条独立轨迹的 GAE 接进来。片段内部通常都为 1。此区分与 Gymnasium 对终止/截断的建模一致。[终止处理说明](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)

举例：最后一步 reward=0，当前 value=0.4，下一状态 value=0.7。若任务真结束，delta=-0.4；若只是截断且 gamma=1，delta=0.3。混淆语义会让同一动作获得完全不同方向的优势。

多轮工具任务中，环境返回的观察可影响后续动作，但通常不作为策略直接生成的 action token。Policy loss mask 与优势沿时间传播的规则不能机械设成同一个数组：不训练观察 token 的 log-prob，不等于在观察位置必须切断所有回报传播。需要按模型的动作时间线定义递推。

<a id="ppo-clip"></a>

## 5. PPO clipping 的分段含义

<!-- q: R05 E21 C03 -->

<!-- question-links:start -->
对应面试题：[R05](../面试题库/04-RLHF与强化学习算法.md#R05)、[E21](../面试题库/10-全网扩展-RLHF算法.md#E21)、[C03](../面试题库/06-手撕与白板练习.md#C03)。
<!-- question-links:end -->

令 `rho=exp(logpi_theta-logpi_old)`，epsilon 为裁剪宽度，固定 advantage A。PPO 的单样本最大化目标为：

```text
J = min(rho*A, clip(rho,1-epsilon,1+epsilon)*A)
loss = -J
```

当 A>0，希望提高动作概率，但提高到上界后不继续奖励这种增长；当 A<0，希望降低概率，但降低到下界后不再奖励继续降低。裁剪是选择较保守的目标分支，不是把所有越界样本一概删除。

以下取 epsilon=0.2，忽略其他 loss，远离不可微拐点：

| A | rho | 原始项 | 裁剪项 | 被选项 | 对 rho 的导数 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.5 | 1.5 | 1.2 | 1.2 | 0 |
| 1 | 0.5 | 0.5 | 0.8 | 0.5 | 1 |
| -1 | 1.5 | -1.5 | -1.2 | -1.5 | -1 |
| -1 | 0.5 | -0.5 | -0.8 | -0.8 | 0 |

因此 ratio 超界不意味着梯度一定为零；即使该 surrogate 分支为常数，KL、entropy 等其他目标仍可能产生梯度。代码实现要避免错误地写成 `clip(rho)*A`，因为那丢失了 min 的分支行为。[PPO clipped objective](https://arxiv.org/abs/1707.06347)

PPO clipping 也不是对实际 KL 的硬约束。多个参数共享、多个 batch 更新和目标的其他项，都可能让策略明显变化。应监控 ratio 分布、clip fraction、KL、梯度和真实质量，并定义异常时减少更新或回退的策略。

<a id="implementation"></a>

## 6. 将目标落实到 batch 张量

<!-- q: R23 -->

<!-- question-links:start -->
对应面试题：[R23](../面试题库/04-RLHF与强化学习算法.md#R23)。
<!-- question-links:end -->

常见张量形状是 `[batch,response_length]`：current/old log-prob、advantage、action mask。Outcome reward 通常为 `[batch]`，value 可覆盖每个动作状态。广播 advantage 之前，要确认它是序列级还是 token 级；错误广播可能跑通计算，却改变 credit assignment。

actor 更新中通常重新计算 current log-prob，old log-prob 在这批更新中保持固定。若把 old 刷新为每个 mini-step 的 current 值，ratio 会被强行拉回 1，目标已经变化。critic 则按回报 target 学习，可独立检查 value error、explained variance 和目标尺度。

长程任务中，PPO 的 critic 可提供更细的状态相关估计，但需要额外模型和可靠训练信号；GRPO 可省去这个模型，却依赖组内比较并承担多个 rollout 的成本。任务长短本身不足以决定谁更好，应比较有效信号、验证成本和固定计算预算下的收益。

## 本章面试表达练习

先不看文档写出三步 GAE 数值，再写 PPO 的四行分段表。最后画出 pi_theta、pi_old、pi_rollout、pi_ref 的生命周期，并说明哪些概率必须固定、哪些需要在更新时重新计算。
