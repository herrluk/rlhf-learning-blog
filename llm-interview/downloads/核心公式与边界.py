"""纯 Python 数学参考：用于核对讲解，不包含自动微分或 GPU kernel。"""
import codecs
from collections import Counter
import json
import math


def softplus(x):
    return max(x, 0.0) + math.log1p(math.exp(-abs(x)))


def ppo_objective(ratio, advantage, epsilon=0.2):
    clipped = min(max(ratio, 1.0 - epsilon), 1.0 + epsilon)
    return min(ratio * advantage, clipped * advantage)


def gae(rewards, values, next_values, bootstrap, trace, gamma=1.0, lam=0.9):
    n = len(rewards)
    if not all(len(x) == n for x in [values, next_values, bootstrap, trace]):
        raise ValueError('所有数组必须对应同一动作时间线')
    result, carry = [0.0] * n, 0.0
    for t in reversed(range(n)):
        delta = rewards[t] + gamma * bootstrap[t] * next_values[t] - values[t]
        carry = delta + gamma * lam * trace[t] * carry
        result[t] = carry
    return result


def group_advantage(rewards, standardize=True, epsilon=1e-8):
    if len(rewards) < 2:
        raise ValueError('组内比较至少需要两个回答')
    mean = sum(rewards) / len(rewards)
    centered = [r - mean for r in rewards]
    if not standardize:
        return centered
    std = math.sqrt(sum(x*x for x in centered) / len(centered))
    return [x / (std + epsilon) for x in centered]


def dpo_loss(log_w, log_l, ref_w, ref_l, beta=0.1):
    margin = beta * ((log_w - ref_w) - (log_l - ref_l))
    return softplus(-margin)


def kl_estimators(p, q):
    if len(p) != len(q) or not p or min(p + q) <= 0:
        raise ValueError('示例要求两个相同大小且严格为正的分布')
    if not (math.isclose(sum(p), 1.0) and math.isclose(sum(q), 1.0)):
        raise ValueError('概率必须归一化')
    ell = [math.log(a / b) for a, b in zip(p, q)]
    k1 = sum(a * x for a, x in zip(p, ell))
    k2 = sum(a * 0.5 * x*x for a, x in zip(p, ell))
    k3 = sum(a * (math.exp(-x) + x - 1) for a, x in zip(p, ell))
    return k1, k2, k3


def block_stats(xs):
    if not xs:
        return -math.inf, 0.0
    m = max(xs)
    return m, sum(math.exp(x-m) for x in xs)


def merge_stats(a, b):
    ma, la = a
    mb, lb = b
    if la == 0:
        return b
    if lb == 0:
        return a
    m = max(ma, mb)
    return m, math.exp(ma-m)*la + math.exp(mb-m)*lb


def adamw_scalar(theta, gradient, m, v, step, lr=0.001,
                 beta1=0.9, beta2=0.999, epsilon=1e-8, decay=0.01):
    m = beta1*m + (1-beta1)*gradient
    v = beta2*v + (1-beta2)*gradient*gradient
    mh = m / (1-beta1**step)
    vh = v / (1-beta2**step)
    theta = (1-lr*decay)*theta - lr*mh/(math.sqrt(vh)+epsilon)
    return theta, m, v


def merge_pair(tokens, pair):
    result, i = [], 0
    while i < len(tokens):
        if i+1 < len(tokens) and (tokens[i], tokens[i+1]) == pair:
            result.append(tokens[i] + tokens[i+1])
            i += 2
        else:
            result.append(tokens[i])
            i += 1
    return result


def train_bpe(texts, num_merges):
    # 从完整字节表起步；本教学版本不进行文本归一化或特殊 token 处理。
    corpus = [[bytes([b]) for b in s.encode('utf-8')] for s in texts]
    merges = []
    for _ in range(num_merges):
        counts = Counter(pair for row in corpus for pair in zip(row, row[1:]))
        if not counts:
            break
        pair = min(counts, key=lambda p: (-counts[p], p))
        merges.append(pair)
        corpus = [merge_pair(row, pair) for row in corpus]
    return merges


def encode_bpe(text, merges):
    tokens = [bytes([b]) for b in text.encode('utf-8')]
    ranks = {pair: rank for rank, pair in enumerate(merges)}
    while len(tokens) > 1:
        pairs = set(zip(tokens, tokens[1:])) & ranks.keys()
        if not pairs:
            break
        pair = min(pairs, key=ranks.get)
        tokens = merge_pair(tokens, pair)
    return tokens


class ToolJSONBuffer:
    """单个 JSON 对象的边界状态机；finish 后再校验业务 schema，不执行工具。"""
    def __init__(self, max_bytes=65536):
        self.decoder = codecs.getincrementaldecoder('utf-8')()
        self.max_bytes = max_bytes
        self.nbytes = 0
        self.text = []
        self.started = self.complete = self.in_string = self.escaped = False
        self.depth = 0

    def _consume(self, text):
        for ch in text:
            self.text.append(ch)
            if self.complete:
                if not ch.isspace():
                    raise ValueError('单对象协议不接受额外载荷')
                continue
            if not self.started:
                if ch.isspace():
                    continue
                if ch != '{':
                    raise ValueError('顶层必须为对象')
                self.started, self.depth = True, 1
                continue
            if self.in_string:
                if self.escaped:
                    self.escaped = False
                elif ch == chr(92):
                    self.escaped = True
                elif ch == '"':
                    self.in_string = False
            elif ch == '"':
                self.in_string = True
            elif ch in '{[':
                self.depth += 1
            elif ch in '}]':
                self.depth -= 1
                if self.depth == 0:
                    self.complete = True

    def feed(self, chunk):
        self.nbytes += len(chunk)
        if self.nbytes > self.max_bytes:
            raise ValueError('载荷过长')
        self._consume(self.decoder.decode(chunk))

    def finish(self):
        self._consume(self.decoder.decode(b'', final=True))
        if not self.complete:
            raise ValueError('JSON 尚未完整结束')
        value = json.loads(''.join(self.text))
        if not isinstance(value, dict):
            raise ValueError('顶层必须为对象')
        return value


def close(actual, expected, tol=1e-7):
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError((actual, expected))


def run_checks():
    # 用有限差分核对四个分支的导数，避免只复述实现自身。
    for ratio, advantage, expected_value, expected_gradient in [
        (1.5, 1, 1.2, 0), (0.5, 1, 0.5, 1),
        (1.5, -1, -1.5, -1), (0.5, -1, -0.8, 0),
    ]:
        close(ppo_objective(ratio, advantage), expected_value)
        h = 1e-5
        numerical = (ppo_objective(ratio+h, advantage)-ppo_objective(ratio-h, advantage))/(2*h)
        close(numerical, expected_gradient)
    a = gae([0,0,1], [0.2,0.3,0.4], [0.3,0.4,0], [1,1,0], [1,1,0])
    gae_example = a
    for x, y in zip(a, [0.676,0.64,0.6]): close(x, y)
    # 真终止与截断的差别；片段边界不串到下一条轨迹。
    close(gae([0], [.4], [.7], [0], [0])[0], -.4)
    close(gae([0], [.4], [.7], [1], [0])[0], .3)
    a = gae([0,99], [.4,0], [.7,0], [1,0], [0,0])
    close(a[0], .3)
    close(sum(group_advantage([0,0,0,1])), 0)
    assert group_advantage([1,1,1]) == [0,0,0]
    assert group_advantage([0,10], False) == [-5,5]
    before = dpo_loss(math.log(.2), math.log(.2), math.log(.25), math.log(.25))
    after = dpo_loss(math.log(.18), math.log(.1), math.log(.25), math.log(.25))
    assert after < before
    k1, k2, k3 = kl_estimators([.8,.2], [.5,.5])
    close(k1, .19274475702175753)
    close(k3, k1)
    assert not math.isclose(k2, k1)
    full = block_stats([1000,1001,999])
    merged = merge_stats(block_stats([1000,1001]), block_stats([999]))
    for x,y in zip(full, merged): close(x,y)
    assert merge_stats(block_stats([]), block_stats([])) == (-math.inf, 0)
    close((2+24)/(2+8), 2.6)
    close(sum([2*2/10, 2*24/10])/2, 2.6)
    close((2/2+24/8)/2, 2.0)
    # 一阶线性 token loss 的手工梯度：DDP 缩放与全局拼接一致。
    close((2*1/4 + 2*(3+5+7)/4)/2, (1+3+5+7)/4)
    assert not math.isclose((1 + (3+5+7)/3)/2, (1+3+5+7)/4)
    theta, m, v = adamw_scalar(1.0, 2.0, 0.0, 0.0, 1)
    close(theta, .99999 - .001*2/(2+1e-8))
    merges = train_bpe(['banana banana', '你好世界', 'banana!'], 16)
    for text in ['banana', '  你好\n世界!', '🧠 new token', '']:
        assert b''.join(encode_bpe(text, merges)).decode('utf-8') == text
    obj = {'name': 'search', 'arguments': {'q': '中文 "引号" {花括号} \\ 路径'}}
    raw = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    for size in [1,2,7,len(raw)]:
        parser = ToolJSONBuffer()
        for i in range(0,len(raw),size): parser.feed(raw[i:i+size])
        assert parser.finish() == obj
    for invalid in [b'{"a":', b'{"a":1} {"b":2}', b'{"a":]}']:
        try:
            parser = ToolJSONBuffer()
            parser.feed(invalid)
            parser.finish()
        except (ValueError, UnicodeError):
            pass
        else:
            raise AssertionError('应拒绝不完整或非法对象')
    print('通过：PPO 分段梯度、GAE 终止/截断、GRPO、DPO、KL、online softmax、全局归一化、AdamW、BPE、流式 JSON。')
    print('GAE=', gae_example, 'KL=', round(k1, 6), 'DPO=', round(before, 6), '->', round(after, 6))


if __name__ == '__main__':
    run_checks()
