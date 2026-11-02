# SFT 与后训练数据：让目标、样本和评估对齐

[讲解总目录](README.md)

<!-- chapter-meta:start -->
本章关联 **15 道题**，按知识点合并讲解，跨章可重复关联。以下为最新样本的宽主题频次，不是细题命中概率。

| 主要考点 | 牛客（13帖） | 小红书（17帖） | 知乎（11帖） |
| --- | --- | --- | --- |
| SFT 目标、数据组织与实现 | 高 4/13 | 中 3/17 | 未观察到 0/11 |
| LoRA / PEFT / 微调方法 | 高 5/13 | 低 1/17 | 中 3/11 |
| 模型评测、数据验证与能力保持 | 中 2/13 | 高 5/17 | 中 2/11 |

高 ≥4 帖、中 2–3、低 1；岗位优先级见原题。统计与来源见 [全网台账](../面试题库/08-全网来源与考频.md)。
<!-- chapter-meta:end -->

SFT 用示范回答训练条件生成能力。它与预训练可以使用相似的 token 级交叉熵，但数据条件、目标位置及希望塑造的行为不同。后训练不是只替换一个 loss；模板、角色和数据选择都会影响最终策略。

<a id="sft-loss"></a>

## 1. Assistant-only loss 的准确含义

<!-- q: S01 S02 S10 -->

<!-- question-links:start -->
对应面试题：[S01](../面试题库/03-SFT与后训练数据.md#S01)、[S02](../面试题库/03-SFT与后训练数据.md#S02)、[S10](../面试题库/03-SFT与后训练数据.md#S10)。
<!-- question-links:end -->

设一个序列含 system、user、assistant 和 padding token。模型可以把历史消息作为上下文，但只有指定 assistant 输出作为监督目标。可以写为：

```text
loss = -sum_t target_mask[t] * log pi(x_t | x_<t)
       / sum_t target_mask[t]
```

注意 mask 对应的是“被预测 token”，而非仅按输入位置方便地切一段。若手动使用 `logits[:,:-1]` 预测 `input_ids[:,1:]`，目标 mask 也必须相同地右移。EOS 常是需要学习的目标；padding 即使与 EOS 使用相同 ID，也不能仅按 ID 一刀切，应结合实际有效长度区分。

Attention mask 控制可见性；loss mask 控制哪些位置直接贡献目标函数；position ID 控制位置表示。屏蔽 user 的 loss，不会禁止 assistant 看 user，也不意味着 user token 对参数梯度没有任何间接影响。[TRL SFT Trainer](https://huggingface.co/docs/trl/main/en/sft_trainer)

一个最小训练流程包括：固定模板与 tokenizer → 构造目标 mask → batch/padding/packing → 前向 → 正确归一化 loss → backward → optimizer/scheduler → 定期生成评估 → 保存模型及模板版本。多轮对话要确认是监督所有 assistant 轮次，还是只监督最后一轮。

<a id="quality"></a>

## 2. 数据越多，为什么可能越差

<!-- q: S03 S06 S08 -->

<!-- question-links:start -->
对应面试题：[S03](../面试题库/03-SFT与后训练数据.md#S03)、[S06](../面试题库/03-SFT与后训练数据.md#S06)、[S08](../面试题库/03-SFT与后训练数据.md#S08)。
<!-- question-links:end -->

SFT 会学习示范中的内容和形式。若大量答案冗长、重复、自信但错误，loss 降低可能表示模型更好地模仿这些缺陷。数据质量至少包括任务正确性、指令遵循、格式一致性、多样性和可验证性。

清洗时应检查多轮角色错位、截断答案、错误工具返回、模板残片、重复近重复和评测泄漏。按来源与任务分桶，避免某个便宜的合成来源淹没关键任务。一个总体合格率 95% 的数据集，可能在最重要的工具调用子集只有 60%。

合成数据应保留教师、prompt、采样参数、过滤器和验证版本。拒绝采样指生成多个候选后保留满足条件的回答；它提高入选样本的平均质量，但也会改变分布，例如偏向短答案或验证器容易判定的任务。[InstructGPT 的示范与偏好数据流程](https://arxiv.org/abs/2203.02155)

若 loss 降而业务分数降，可以依次检查：训练评估模板是否一致；答案长度、拒答率和语言是否偏移；是否过拟合某些来源；原有通用能力是否下降。用固定 prompt 集保存多个 checkpoint 的实际生成样例，常比只看一条平均曲线更容易定位问题。

<a id="lora"></a>

## 3. LoRA 的低秩更新与首步梯度

<!-- q: S04 S05 E17 E18 -->

<!-- question-links:start -->
对应面试题：[S04](../面试题库/03-SFT与后训练数据.md#S04)、[S05](../面试题库/03-SFT与后训练数据.md#S05)、[E17](../面试题库/09-全网扩展-基础预训练与SFT.md#E17)、[E18](../面试题库/09-全网扩展-基础预训练与SFT.md#E18)。
<!-- question-links:end -->

对原权重 W，LoRA 使用 `W_eff = W + s BA`，其中 `A:[r,d_in]`、`B:[d_out,r]`，r 小于原矩阵维度，s 是缩放系数。以常见 `s=alpha/r` 为例，可训练参数从 `d_out*d_in` 变为 `r*(d_in+d_out)`，但前向仍需要原模型，所以它主要节省梯度和 optimizer state，而非自动删除全部基座显存。[LoRA](https://arxiv.org/abs/2106.09685)

设对 `BA` 的梯度为 G，则忽略缩放常数时：

```text
dL/dA = BᵀG
dL/dB = GAᵀ
```

若 A 随机、B 为零，初始增量为零，但 B 通常可得到非零梯度；若 A、B 同时为零，两边梯度都为零，在普通梯度更新下无法启动。PEFT 的具体初始化可配置，不能把某一种随机分布说成 LoRA 必然要求。[PEFT LoRA](https://huggingface.co/docs/peft/package_reference/lora)

Rank 决定更新子空间的容量，alpha 与归一化方式影响更新规模，target modules 决定哪些映射可被改变。调 rank 后还要检查实际 scale 是否变化，否则实验同时改变了容量和步幅。选全量或 LoRA 时，比较目标偏移幅度、显存预算、部署方式和验证表现，不能只按数据条数设阈值。

恢复旧 adapter，应同时恢复它所依附的 base revision 和必要的 optimizer 状态；先合并旧 adapter 再训练新 adapter，会产生新的基座状态和优化路径。量化基座的合并还可能引入舍入误差。只保存一个 `adapter.bin` 文件名不足以保证可复现。

<a id="distillation"></a>

## 4. 软标签蒸馏与文本蒸馏学的不是同一种信号

<!-- q: E19 -->

<!-- question-links:start -->
对应面试题：[E19](../面试题库/09-全网扩展-基础预训练与SFT.md#E19)。
<!-- question-links:end -->

软标签蒸馏让学生匹配教师的概率分布。温度 T 可以平滑概率，使非首选候选也提供信号；常见实现对蒸馏 KL 乘 `T²`，用于补偿温度对梯度尺度的影响。混合目标可写成 `a*CE(label) + b*T²*KL(teacher_T || student_T)`，其中权重仍需实验选择。[PyTorch 蒸馏教程](https://docs.pytorch.org/tutorials/beginner/knowledge_distillation_tutorial.html)

文本或思维链蒸馏则通常先采样教师文本，再把它当 SFT 目标。学生看到的是一条或几条离散轨迹，不是教师在每个位置的完整分布。教师答案可能正确但解释有问题，因此过程文本也需要检验。

如果教师和学生 tokenizer 不同，两个位置的词表维度和 token 边界可能不对应，不能直接对两份 logits 做逐词表 KL。可以选择文本层蒸馏、构造对齐机制或采用其他目标，但必须说明转换方法及其信息损失。

<a id="evaluation"></a>

## 5. 怎样验证能力保持，以及何时转 RL

<!-- q: S09 S11 E39 -->

<!-- question-links:start -->
对应面试题：[S09](../面试题库/03-SFT与后训练数据.md#S09)、[S11](../面试题库/03-SFT与后训练数据.md#S11)、[E39](../面试题库/10-全网扩展-RLHF算法.md#E39)。
<!-- question-links:end -->

评估至少应包含业务内任务、未见分布、通用能力、格式/工具正确率和成本指标。固定生成参数、预算与数据版本，避免新模型使用更多采样机会却被解释为单次能力更强。训练集、调参集和最终评估集要按问题来源及近重复关系隔离。

转入 RL 的条件不是 SFT loss 到了某个通用数值。更实际的判断是：当前模型能否以非零概率产生可用答案；任务是否有可靠奖励；错误是否有可优化的结构；rollout 和验证成本是否可接受。若模型几乎完全不理解工具协议，先补示范可能更直接；若已经能解部分题，但解法选择与验证不足，在线采样优化可能更适合。

“RL 是否产生新能力”不能仅凭几道成功案例回答。设计对照时固定起始 checkpoint、训练数据污染检查和推理预算，分别看 pass@1、pass@k 与固定时间/计算预算下的成功率。单次概率提高与可达解空间扩大是不同观察结果；有限采样无法证明模型绝不可能生成某种答案。

<a id="tools"></a>

## 6. 工具协议与训练轨迹的边界

<!-- q: E20 -->

<!-- question-links:start -->
对应面试题：[E20](../面试题库/09-全网扩展-基础预训练与SFT.md#E20)。
<!-- question-links:end -->

模型生成的 tool-call 文本只是动作请求；协议层负责解析、校验和传输；环境执行后产生观察。这三个层次应通过 call ID 关联，不能把“模型说已经执行”当作执行结果。

SFT 数据可监督正确的调用参数和后续回答；RL 的动作 mask 通常覆盖模型实际生成的 token，而工具观察属于环境输入。观察虽然不直接作为策略动作贡献 log-prob，仍可能影响后续动作和 credit assignment。轨迹应保留解析失败、执行失败和模型任务失败的区别。[verl Agent Loop](https://verl.readthedocs.io/en/latest/advance/agent_loop.html)

## 本章面试表达练习

拿一段“用户提问 → assistant 调工具 → 工具结果 → assistant 回答”的对话，标出 Attention 可见范围、监督目标和 policy action。再说明切换模板、LoRA adapter 或验证器版本后，哪些实验需要重新核对。
