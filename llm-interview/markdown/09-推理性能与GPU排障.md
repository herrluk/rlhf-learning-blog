# 推理、GPU 与性能排障：把局部提速连到实际收益

[讲解总目录](README.md)

<!-- chapter-meta:start -->
本章关联 **18 道题**，按知识点合并讲解，跨章可重复关联。以下为最新样本的宽主题频次，不是细题命中概率。

| 主要考点 | 牛客（13帖） | 小红书（17帖） | 知乎（11帖） |
| --- | --- | --- | --- |
| 推理框架与推理加速 | 中 3/13 | 中 3/17 | 高 5/11 |
| 系统瓶颈分析与性能归因 | 未观察到 0/13 | 中 3/17 | 高 5/11 |
| CUDA / GPU 算子实现 | 未观察到 0/13 | 中 2/17 | 高 5/11 |

高 ≥4 帖、中 2–3、低 1；岗位优先级见原题。统计与来源见 [全网台账](../面试题库/08-全网来源与考频.md)。
<!-- chapter-meta:end -->

性能面试要先给负载与目标，再给瓶颈证据和修改。孤立的 kernel 时间、GPU utilization 或 cache hit rate，都不足以证明系统收益。

<a id="serving"></a>

## 1. Continuous batching、prefix cache 与 PD 分离

<!-- q: I09 I24 E50 -->

<!-- question-links:start -->
对应面试题：[I09](../面试题库/05-RL-Infra系统与排障.md#I09)、[I24](../面试题库/05-RL-Infra系统与排障.md#I24)、[E50](../面试题库/11-全网扩展-RLInfra与手撕.md#E50)。
<!-- question-links:end -->

传统静态 batch 等整批请求完成，短请求结束后可能留下空槽；continuous batching 在生成迭代边界更新活跃请求，减少空槽，但还需要处理公平性、KV 容量和新请求的 prefill。

Prefix cache 复用相同前缀的已有计算与 KV。命中率高却仍慢，可能是共享前缀很短、输出 decode 很长、查找与调度成本高，或其他 verifier 阶段成为瓶颈。应区分按请求计数的 hit rate 与实际复用 token 比例；一个只复用 10 token 的命中，与复用 8000 token 的命中价值不同。

Chunked prefill 把较长 prompt 的预填充分块，与 decode 工作交错，以控制长 prefill 对其他请求的干扰；chunk 太小可能降低矩阵乘效率和增加调度开销。PD 分离让 prefill 与 decode 使用不同资源，便于分别控制延迟，但需要传输 KV 和平衡两侧容量。它不能被概括成必然提高吞吐。[vLLM PD 分离说明](https://docs.vllm.ai/en/latest/features/disagg_prefill/)

EP 则是在 MoE expert 维度分布计算，它解决的分片与路由问题不同。实际可以组合 PD 与 EP，但“都用了分离”不是两者等价的证据。

<a id="slo"></a>

## 2. TTFT、TPOT、goodput 与长尾

<!-- q: I26 I22 -->

<!-- question-links:start -->
对应面试题：[I26](../面试题库/05-RL-Infra系统与排障.md#I26)、[I22](../面试题库/05-RL-Infra系统与排障.md#I22)。
<!-- question-links:end -->

TTFT 是请求进入系统后到首个 token 的时间，含排队与 prefill；TPOT 描述输出 token 的生成间隔，具体统计常按每请求平均或分位数定义。报告时应写明是否包含网络、排队和最后一个 token，以及分位数基于请求还是 token。

如果把并发从 32 增到 128，总 tokens/s 可能上升，但 TTFT/TPOT 的 P99 超过服务目标。此时用户可接受的吞吐不一定提高。Goodput 可以定义为满足约定 SLO 的请求完成量或 token 量，分母和超时处理都应固定。

对 RL，还需加入数据效用：生成多了但有效 group 更少、策略滞后更高，也可能降低学习效率。一次优化至少比较同模型、同长度分布、同 GPU 和同质量条件下的端到端耗时，并确认采样与 loss 语义没有一起变化。

<a id="speculative"></a>

## 3. Acceptance rate 高，投机解码为何仍可能更慢

<!-- q: E51 -->

<!-- question-links:start -->
对应面试题：[E51](../面试题库/11-全网扩展-RLInfra与手撕.md#E51)。
<!-- question-links:end -->

投机解码先由 drafter 提供候选，再由目标模型验证。成本不仅是目标模型原本的 decode，还包含 draft、验证、拒绝处理、通信与调度。可用下式建立简单预算：

```text
平均每接受 token 成本
≈ (draft时间 + target验证时间 + 通信调度时间) / 每轮实际输出token数
```

提高 draft 长度可能增加每轮接受 token 数，却使验证更贵、拒绝更多或 KV 更大。Acceptance rate 是比例，不能代替分子分母的实际时间。应同时看接受长度、每轮输出量和每轮耗时。[投机解码论文](https://arxiv.org/abs/2211.17192)

将 draft 与 target 分到不同设备，可以释放目标卡算力，也增加通信、流水线和请求状态管理。是否划算取决于模型比例、带宽、batch、候选长度和目标 SLO；不能从接受率一个数字判断。

<a id="roofline"></a>

## 4. Roofline、occupancy 与融合

<!-- q: I20 E44 E46 -->

<!-- question-links:start -->
对应面试题：[I20](../面试题库/05-RL-Infra系统与排障.md#I20)、[E44](../面试题库/11-全网扩展-RLInfra与手撕.md#E44)、[E46](../面试题库/11-全网扩展-RLInfra与手撕.md#E46)。
<!-- question-links:end -->

算术强度是 FLOPs 与数据移动字节数之比。Roofline 用计算上限与带宽上限判断一个算子更可能受哪类资源限制。实际还可能受访存延迟、launch、小 shape、同步或串行依赖限制，所以应结合时间线和硬件计数器。

Occupancy 描述活跃 warp 相对于资源上限的比例，有助于理解延迟隐藏，但更高并不一定更快。为了增加活跃 block 而缩小 tile 或限制寄存器，可能增加 spill、重复读写或减少指令级并行。目标应是有效吞吐，而不是 occupancy 最大化。[NVIDIA CUDA 性能指南](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

融合可以减少 launch 和中间 HBM 写入。假设 A→B→C，而 B 的输出也被另一个分支 D 使用，融合 ABC 后仍可能要输出 B，或让 D 重算。此时要画 consumer 图，比较输出、重算与寄存器压力，不能只数“原来三个 kernel，现在一个”。

大词表 log-prob/entropy 也可能成为瓶颈。只需目标 token log-prob 时，可以研究分块 logsumexp 与目标项读取，避免不必要地保存完整 probability；精确 entropy 则需要涉及完整分布的相应归约。两者的计算需求不同，优化不能偷偷把精确熵替换为采样近似。

<a id="timing"></a>

## 5. 正确计时与 CUDA Graph hang

<!-- q: E45 I25 -->

<!-- question-links:start -->
对应面试题：[E45](../面试题库/11-全网扩展-RLInfra与手撕.md#E45)、[I25](../面试题库/05-RL-Infra系统与排障.md#I25)。
<!-- question-links:end -->

CPU 发起 CUDA kernel 后通常异步返回，因此普通 CPU 计时器可能只测到提交时间。测设备执行可使用 CUDA event，并保证结束事件完成后读取；测端到端则应明确同步边界及数据准备是否计入。多个 stream 之间需要显式依赖或等到所有相关工作完成，单个 stream 的结束 event 不会自动代表其他独立 stream 已结束。[PyTorch CUDA 语义](https://docs.pytorch.org/docs/2.14/notes/cuda.html)

Benchmark 应有 warmup，固定输入和 shape，考虑频率变化、缓存状态及测量噪声。Profiler 可能改变执行开销，因此先用它定位，再用较低干扰的计时方式验证收益。

CUDA Graph 捕获并重放一段执行，减少 CPU 提交开销，但对地址、依赖和可捕获操作有约束。多卡 TP hang 可以按以下顺序缩小范围：关闭 Graph 验证 eager；缩到单卡；检查各 rank 捕获/重放路径与 collective 顺序；检查条件分支、静态 buffer、stream/event 依赖及设备同步标记。若某 rank 等待一个永远不会由本次重放更新的标记，仅增加 timeout 没有用。[CUDA Graph 文档](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)

每一步只改变一个因素并保留最小复现。Graph 本身不是网络错误的证据，多卡出现 hang 也不自动说明 NCCL 库有 bug。

<a id="kernels"></a>

## 6. GPU 手撕的核心：访存、归约、同步与边界

<!-- q: C10 E47 E55 E56 E58 -->

<!-- question-links:start -->
对应面试题：[C10](../面试题库/06-手撕与白板练习.md#C10)、[E47](../面试题库/11-全网扩展-RLInfra与手撕.md#E47)、[E55](../面试题库/11-全网扩展-RLInfra与手撕.md#E55)、[E56](../面试题库/11-全网扩展-RLInfra与手撕.md#E56)、[E58](../面试题库/11-全网扩展-RLInfra与手撕.md#E58)。
<!-- question-links:end -->

**逐行最大值。** 可以先让一个 block 负责一行，线程跨步读取若干列，在寄存器内求局部最大值，再做 warp 归约、共享内存汇总各 warp 结果，最终写一个值。FP16 输入可以转换为 FP32 比较；无有效元素用负无穷作单位元。需要定义 NaN 处理、非整齐列数和很长行的多 block 方案。

**Histogram。** 10 个桶的全局 atomic 实现简单，但所有输入落同一桶时争用严重。可以每个 block 在 shared memory 维护局部桶，再合并到全局。需要初始化、同步和足够宽的计数类型；短数组时额外准备成本可能反而更高。

**Exclusive scan 与 compaction。** 对 mask `[1,0,1,1]`，exclusive prefix sum 为 `[0,1,1,2]`，保留元素分别写入 0、1、2 号位置。跨 block 时先算局部 scan 与 block 总和，再 scan block 总和，最后加偏移。不能让普通 block 间共享内存同步，因为 shared memory 只属于本 block。

**方差与 RMSNorm。** 方差可以通过中心化或 Welford 合并统计避免 `E[x²]-E[x]²` 在大偏置小方差下严重抵消；RMSNorm 不减均值，只需要均方。把“归约平方和”直接当成方差实现是语义错误。

**Transpose。** 合并 global memory 访问关注 warp 访问的地址范围；shared memory bank conflict 关注同一指令访问的 bank 映射。在经典 32-bank、4 字节元素的教学布局里，tile 加一列 padding 常能改变列访问冲突；数据类型、访问宽度和架构不同则需重新分析。Swizzle 是更一般的地址映射变换，不能脱离布局背答案。[CUDA shared memory 与归约原则](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

手撕先给正确、可验证的方案，再讨论优化。验收必须包含非 2 的幂长度、尾部 tile、空输入或最小输入、高冲突数据和混合精度边界。

<a id="online-softmax"></a>

## 7. Online softmax 的统计量如何合并

<!-- q: E57 -->

<!-- question-links:start -->
对应面试题：[E57](../面试题库/11-全网扩展-RLInfra与手撕.md#E57)。
<!-- question-links:end -->

一个块保存 `m=max(x)` 与 `l=sum exp(x-m)`。两个块 A、B 合并时：

```text
m = max(m_A,m_B)
l = exp(m_A-m)*l_A + exp(m_B-m)*l_B
```

例如 A=`[1000,1001]`，B=`[999]`，分别计算后按上式合并，与一次性稳定 softmax 的分母相同。若还维护未归一化的加权 value 和 o，则对 o 使用同样的 rescale，最终用 o/l 得到 Attention 输出。这说明不必把所有分数一起落到 HBM，仍可逐块得到结果。[FlashAttention](https://arxiv.org/abs/2205.14135)

全 mask 块可以视为空统计量，但两个空块合并必须专门处理，避免负无穷之间相减。第 10 章的 CPU 数学示例验证了块合并与全量结果的一致性；GPU 性能仍需在实际硬件上测量。

<a id="regression"></a>

## 8. Tokens/s 下降 10% 的回归检查

<!-- q: E54 -->

<!-- question-links:start -->
对应面试题：[E54](../面试题库/11-全网扩展-RLInfra与手撕.md#E54)。
<!-- question-links:end -->

先锁定模型、输入长度分布、并发、镜像、驱动、拓扑与 warmup，重复测量得到噪声范围。接着分解数据加载、prefill、decode、reward、forward/backward、通信和 optimizer 时间，看下降来自哪个阶段。

如果只在某些长度触发，检查 kernel 选择和 padding；如果扩卡才出现，检查通信和负载不均；如果刚恢复 checkpoint 后出现，检查 cache、编译与初始化状态。性能验证还要有相应数值或质量对照，防止通过改变生成长度、mask 或采样偷偷换了工作量。

回归报告应包含可重现配置、原版本/新版本、置信区间或重复结果、瓶颈证据、修复效果与回退条件。无需为每个微小代码改动扩建复杂测试系统，但真实影响训练结果或关键吞吐的修改应有针对性验证。

## 本章面试表达练习

选择一个实际优化，依次回答：瓶颈证据是什么；优化改变了什么计算或数据移动；为什么不会改变目标语义；单算子和端到端分别提升多少；在什么长度、并发或硬件上不再划算。
