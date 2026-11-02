# 模型基础：从 token 到一次生成

[讲解总目录](README.md)

<!-- chapter-meta:start -->
本章关联 **20 道题**，按知识点合并讲解，跨章可重复关联。以下为最新样本的宽主题频次，不是细题命中概率。

| 主要考点 | 牛客（13帖） | 小红书（17帖） | 知乎（11帖） |
| --- | --- | --- | --- |
| Transformer / Attention | 高 5/13 | 高 8/17 | 高 10/11 |
| KV Cache 与显存分析/优化 | 中 3/13 | 高 4/17 | 中 3/11 |
| 模型架构比较 | 中 3/13 | 中 2/17 | 中 3/11 |

高 ≥4 帖、中 2–3、低 1；岗位优先级见原题。统计与来源见 [全网台账](../面试题库/08-全网来源与考频.md)。
<!-- chapter-meta:end -->

读完本章，应能从张量形状解释一次前向，并估算生成时的主要内存。RL Infra 中的 log-prob、显存和训推偏差，最终都会回到这些基础操作。

<a id="forward"></a>

## 1. Transformer 的一次前向到底做了什么

<!-- q: B01 B02 B03 B14 -->

<!-- question-links:start -->
对应面试题：[B01](../面试题库/01-大模型基础.md#B01)、[B02](../面试题库/01-大模型基础.md#B02)、[B03](../面试题库/01-大模型基础.md#B03)、[B14](../面试题库/01-大模型基础.md#B14)。
<!-- question-links:end -->

设输入 token ID 是 `[B,L]`，B 是 batch size，L 是序列长度；词嵌入将其变为 `[B,L,d]`。以常见 pre-norm decoder block 为例，先对隐藏状态归一化，再做 Attention，加回残差，然后再经过归一化、MLP 和第二条残差路径。最后的 LM head 将隐藏维度映射到词表维度，得到 `[B,L,V]` 的 logits。

Attention 的 Q 表示当前位置需要什么信息，K 表示每个位置可供匹配的特征，V 是实际参与加权汇总的信息。若头数为 H，每头维度为 D，则 Q/K/V 可写成 `[B,H,L,D]`，且常见设置下 d=HD。单头计算为：

```text
scores = Q Kᵀ / sqrt(D) + attention_mask
probabilities = softmax(scores, dim=key_position)
output = probabilities V
```

结果拼接各头并经过输出投影。Self-attention 的 Q/K/V 来自同一段隐藏状态；cross-attention 的 Q 来自查询序列，K/V 来自另一段序列，分数矩阵可为 `[L_query,L_key]`，不要求两者等长。[Transformer 原论文](https://arxiv.org/abs/1706.03762)

为什么除以 `sqrt(D)`？在分量近似独立、均值为零、方差为一的简化条件下，D 个乘积之和的方差约为 D。缩放使分数规模不随头维度直接膨胀，避免 softmax 过早集中。真实训练不严格满足上述假设，但这个方差计算解释了设计动机。

计算复杂度要分项说：Q/K/V 与输出投影约为 `O(BLd²)`；分数与加权汇总约为 `O(BL²d)`。因此短序列、大隐藏维度时，不能仅凭 Attention 的 L² 就断言它占全部耗时。MLP 通常含两个或三个大矩阵乘，也可能贡献大量计算。

Causal LM 在位置 t 只能读取不晚于 t 的输入，用于预测后续 token；Prefix LM 可让前缀内部双向可见，生成区保持因果；encoder-decoder 则将输入编码和输出生成分开。选型同时影响训练目标、mask、缓存和服务方式，不能仅以“decoder-only 流行”解释。

MLP 提供逐位置的非线性特征变换。SwiGLU 可概括为 `SiLU(xW_gate) ⊙ (xW_up)` 再经过下降投影；“门控”改变信息通过方式，并不是跨 token 聚合。残差则让每层学习对已有表示的增量，同时提供梯度路径。

<a id="tokenizer"></a>

## 2. Tokenizer 与词表为什么会造成工程问题

<!-- q: B04 E01 E59 -->

<!-- question-links:start -->
对应面试题：[B04](../面试题库/01-大模型基础.md#B04)、[E01](../面试题库/09-全网扩展-基础预训练与SFT.md#E01)、[E59](../面试题库/11-全网扩展-RLInfra与手撕.md#E59)。
<!-- question-links:end -->

Tokenizer 将字符串映射为离散 ID。BPE 迭代合并高频相邻符号；WordPiece 的训练选择规则与具体实现有关，常见编码采用最长匹配；Unigram 从候选子词集合及概率出发优化词表。SentencePiece 是工具与文本建模方式，支持 BPE、Unigram 等算法，不能将它与 BPE 简单列为互斥的四种算法。流水线还包含归一化、预分词、特殊 token 和解码。[Tokenizers pipeline](https://huggingface.co/docs/tokenizers/pipeline)、[SentencePiece](https://github.com/google/sentencepiece)

例如 `"hello world"` 与 `"hello  world"` 是否编码相同，取决于空白归一化和预分词器。训练和推理即使加载同一权重，只要模板多了一个换行或特殊 token，后续 log-prob 就不再是在比较同一条件分布。

扩词表相当于改变 embedding 的行数；如果 LM head 与 embedding 共享权重，要同步保持共享关系，否则还要扩展另一份输出矩阵。工程上需要同时版本化 tokenizer、特殊 token ID、embedding 和模型配置。保留旧 token ID 有助于复用已有参数，但不能替代对编码规则变化的检查。

新增 token 的向量通常需要初始化并继续训练。若仅扩词表而完全冻结相关参数，新词可能长期没有有效表示。恢复 checkpoint 时还要判断 optimizer state 的形状是否匹配。面试中可以用“词表从 32,000 扩到 32,100”画出多出的 100 行，说明为什么只换 tokenizer 文件不够。

<a id="position-norm"></a>

## 3. 位置编码、归一化与稳定 softmax

<!-- q: B05 B06 B15 -->

<!-- question-links:start -->
对应面试题：[B05](../面试题库/01-大模型基础.md#B05)、[B06](../面试题库/01-大模型基础.md#B06)、[B15](../面试题库/01-大模型基础.md#B15)。
<!-- question-links:end -->

不含位置机制的 Attention 无法仅靠 token 内容区分顺序。RoPE 对 Q/K 的成对维度做与位置相关的旋转。若旋转矩阵为 R，则旋转后的点积包含 `R(m)ᵀR(n)=R(n−m)`，使相对位移进入匹配分数。这里是数学关系，不意味着模型自动掌握任意长度；上下文扩展还涉及频率修改、训练长度分布与评估。[RoFormer](https://arxiv.org/abs/2104.09864)

LayerNorm 沿单个 token 的隐藏维度计算均值和方差；BatchNorm 常依赖 batch 及相关统计维度。生成服务的 batch 可变且序列长度不齐，前者更方便保持逐 token 的归一化语义。RMSNorm 则按均方根缩放，不执行减均值：

```text
LayerNorm(x) = (x - mean(x)) / sqrt(var(x)+eps) * weight + bias
RMSNorm(x)   = x / sqrt(mean(x²)+eps) * weight
```

不要说 RMSNorm 与 LayerNorm 完全等价，它们对整体偏移的响应不同。[RMSNorm 论文](https://arxiv.org/abs/1910.07467)

稳定 softmax 使用 `m=max(x)`：`exp(x_i-m)/sum_j exp(x_j-m)`。例如 logits 为 `[1000,1001]`，直接指数容易溢出，减去 1001 后只计算 `exp(-1)` 与 1。log-softmax 应直接用 `x_i-logsumexp(x)`，避免先得到很小的概率再取 log。

如果一整行都被 mask 成负无穷，`-inf-(-inf)` 会产生 NaN。正确实现需要定义全 mask 行的输出和 loss 行为，不能期待稳定 softmax 公式自动处理所有 mask 边界。

<a id="kv"></a>

## 4. MHA、GQA、MLA 与 KV Cache 的显存账

<!-- q: B07 B08 B16 B17 -->

<!-- question-links:start -->
对应面试题：[B07](../面试题库/01-大模型基础.md#B07)、[B08](../面试题库/01-大模型基础.md#B08)、[B16](../面试题库/01-大模型基础.md#B16)、[B17](../面试题库/01-大模型基础.md#B17)。
<!-- question-links:end -->

自回归 decode 每步只增加一个新 token。历史 token 的 K/V 在固定模型和前缀下可复用，因此缓存它们，避免每步重新计算整个前缀。Q 是当前查询，通常无需像历史 K/V 那样保留。不同层有各自的缓存。

在统一 batch 长度的简化条件下：

```text
KV 字节数 = 2 × 层数 × batch × 缓存长度 × KV头数 × 每头维度 × 每元素字节数
```

例：32 层、batch=8、长度=4096、8 个 KV 头、每头 128 维、BF16 为 2 字节，得到 4 GiB。若改成 32 个 KV 头，其他不变，则为 16 GiB。这里只算张量有效载荷，不包含页表、碎片、临时 buffer 与副本。

MHA 的每个 query head 配一组 K/V；MQA 的所有 query head 共享一组 K/V；GQA 在两者之间分组共享。因此保持 query head 数不变也可降低缓存。实际 TP 布局还可能复制 KV 头，不能未经检查直接再除以 TP 度。[GQA 论文](https://arxiv.org/abs/2305.13245)

MLA 缓存压缩后的潜变量，并通过投影及位置相关分支支持 Attention。它改变了缓存表示和计算路径，不能把上面的传统 KV 公式直接套上“更少的头”。应按实际缓存张量逐项计数，检查解耦的位置分量是否另存。[DeepSeek-V2](https://arxiv.org/html/2405.04434v5)

参数显存相对固定；激活显存跟训练 batch、序列长度和重计算策略相关；KV Cache 跟推理中活跃序列及其长度相关。7B BF16 权重约 14 GB，不代表 14 GB 显存就能完成训练或任意并发的推理。

<a id="attention-io"></a>

## 5. FlashAttention 与 PagedAttention 优化了不同对象

<!-- q: B09 B10 B11 -->

<!-- question-links:start -->
对应面试题：[B09](../面试题库/01-大模型基础.md#B09)、[B10](../面试题库/01-大模型基础.md#B10)、[B11](../面试题库/01-大模型基础.md#B11)。
<!-- question-links:end -->

朴素 Attention 会显式保存 L×L 分数或概率矩阵，在 HBM 与计算单元间搬运大量中间结果。FlashAttention 分块处理 Q/K/V，维护在线 softmax 的统计量，减少大中间矩阵的落盘与重读。它仍计算精确的稠密 Attention，只是在浮点舍入允许的范围内改变计算组织；并没有将稠密 Attention 的全部计算量变成线性。[FlashAttention](https://arxiv.org/abs/2205.14135)

PagedAttention 主要处理 KV Cache 的物理分配与逻辑寻址：一条序列的逻辑连续缓存可映射到多个物理块，减少为最大长度预留连续空间造成的浪费，也便于前缀共享。它不能保证每种负载都获得同样收益。[PagedAttention](https://arxiv.org/abs/2309.06180)

Prefill 一次处理多个输入位置，矩阵乘的计算规模较大；decode 每次新增位置较少，又要读取历史缓存。在小 batch 下，decode 容易受权重和 KV 读取带宽限制；增加并发后，矩阵乘效率、KV 容量和排队时间共同决定性能。应结合实际 shape、GPU 和并发判断瓶颈。

<a id="sampling-moe"></a>

## 6. 采样、MoE 与量化如何影响 RL

<!-- q: B12 B13 B18 -->

<!-- question-links:start -->
对应面试题：[B12](../面试题库/01-大模型基础.md#B12)、[B13](../面试题库/01-大模型基础.md#B13)、[B18](../面试题库/01-大模型基础.md#B18)。
<!-- question-links:end -->

temperature 对 logits 做除法后再 softmax；top-k 保留概率最大的 k 项；top-p 保留累计概率达到阈值的候选集合，然后重新归一化。这些操作改变真正产生动作的分布。RL 保存的 log-prob 必须说明对应哪一步，否则重要性比率可能比较两个不同对象。详细例子见 RL 系统章节。

MoE 的 router 为 token 选择部分 expert，专家执行各自的 MLP，再合并输出。总参数多不等于每个 token 都使用全部参数，但路由、负载不均、token dispatch 与通信会增加成本。落在少数 expert 的 token 太多，可能产生热点或容量限制；低精度差异也可能改变 top-k 路由选择。[Switch Transformer](https://arxiv.org/abs/2101.03961)

量化要区分权重、激活与 KV Cache，及其 scale 是离线校准、在线计算还是训练学习。FP8/FP4 是数值格式族，不自动代表“无需校准”。存储变小后，反量化、scale 读取和 kernel 选择也会消耗时间。比较收益时，应同时给出精度、内存、TTFT/TPOT 与固定 SLO 下的吞吐。[TensorRT-LLM FP8 指南](https://nvidia.github.io/TensorRT-LLM/performance/performance-tuning-guide/fp8-quantization.html)

## 本章面试表达练习

用三分钟讲清：一个 batch 的 prompt 如何变成 logits；生成到第 4096 个 token 时哪些状态仍在显存；若从 MHA 改成 GQA，哪些内存项会变，哪些不会。回答时先画形状，再做容量估算，最后讨论实际 kernel 和布局带来的偏差。
