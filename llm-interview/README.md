# 大模型与 RL Infra · HTML 图解文档

从 [阅读首页](index.html) 开始。在线阅读：https://herrluk.github.io/rlhf-learning-blog/llm-interview/ 。全部内容随本目录发布，HTML 中内嵌样式、SVG 和交互脚本。

10 个专题保留 Markdown 详细讲解，增加 34 幅专题 SVG 与 1 幅首页学习路线图。8 个可调例子涵盖 KV Cache、DPO、GAE、PPO、GRPO、KL、异步队列、Roofline。每幅图下有三步读图解释。

| 专题 | 图解数 | 内容 |
| --- | ---: | --- |
| [模型与 Attention](01-foundations.html) | 3 | 从 token 到 logits，连接张量形状、可见性和推理内存。 |
| [预训练数据与优化](02-pretraining.html) | 3 | 把训练目标、数据处理、有效 token 与优化器步骤对应起来。 |
| [分布式训练与显存](03-distributed.html) | 4 | 从显存账出发，理解参数分片、矩阵并行、流水线与恢复。 |
| [SFT 与后训练数据](04-sft.html) | 3 | 从监督目标到低秩更新，检查模板、样本、协议与评估。 |
| [奖励模型与 DPO](05-reward-dpo.html) | 3 | 区分真实质量、代理奖励和偏好目标，读懂 DPO 的相对概率。 |
| [PPO 与 GAE 推导](06-ppo-gae.html) | 3 | 沿时间线计算优势，再用分段曲线理解 PPO 的更新边界。 |
| [GRPO、KL 与变体](07-grpo-kl.html) | 4 | 看清组内比较、归一化权重、KL 期望与梯度的区别。 |
| [RL Infra 架构与一致性](08-rl-infra.html) | 4 | 把算法落到经验记录、版本切换、队列背压和更新提交。 |
| [推理性能与 GPU 排障](09-gpu-performance.html) | 4 | 从服务延迟到计算上限，用证据连接局部优化与端到端收益。 |
| [代码与手算练习](10-code-lab.html) | 3 | 用独立小例子验证 mask、递推、编码与流式协议边界。 |

- [172 题索引](questions.html)：按题号或关键词检索，再跳到讲解。
- [来源与考频](sources.html)：保留牛客、小红书、知乎、公众号等来源和样本口径。
- 每张图的“保存 SVG”导出当前参数与主题；默认版本也保存在 svg 目录。
- “打印”可使用浏览器另存为 PDF；打印自动使用浅色。窄屏图表可横向滚动。
- markdown 目录保存本次讲解原文；downloads 目录包含可运行的 Python 学习例子。

HTML 生成日期：2026-09-12。来源与考频快照：2026-09-08；本轮生成 HTML 没有重新采样面经。

[返回博客首页](../index.html)
