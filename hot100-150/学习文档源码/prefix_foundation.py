"""第 04 章的前缀和入门导读；HTML 内嵌，不增加力扣题目。"""
CODE = '''def build_prefix_sum(nums: list[int]) -> list[int]:
    # prefix[t] 表示前 t 个元素的和，比原数组多一个“空前缀”。
    prefix = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        # 旧前缀加上当前元素，得到前 i+1 个元素的和。
        prefix[i + 1] = prefix[i] + x
    return prefix


def range_sum(prefix: list[int], left: int, right: int) -> int:
    # 查询原数组的闭区间 [left, right]，两端都包含。
    # 前提：0 <= left <= right < 原数组长度，prefix 已正确构建。
    # 先取到 right 的全部元素，再减去 left 之前的共同前缀。
    return prefix[right + 1] - prefix[left]


nums = [2, -1, 3, 4]
prefix = build_prefix_sum(nums)  # 只构建一次，后续查询复用同一张表。
print(prefix)                   # [0, 2, 1, 4, 8]
print(range_sum(prefix, 1, 3))   # -1 + 3 + 4 = 6
print(range_sum(prefix, 0, 2))   # 2 - 1 + 3 = 4
'''.strip()


def render(highlight):
    body = '''<div class="prefix-foundation" id="prefix-foundation">
<p class="tag">基础先修 · 先理解这一段，再开始做题</p>
<h3 id="prefix-definition">1. 前缀和是什么：把“从开头加到哪里”存下来</h3>
<p>先只看一个数组 <code>nums = [2, -1, 3, 4]</code>。“前缀”就是从数组开头连续取出的一段：可以取 0 个、1 个、2 个……直到全部元素。把每一段的和记录下来，就得到<strong>前缀和数组</strong>。</p>
<p>本章统一定义：<strong><code>prefix[t]</code> 是原数组前 <code>t</code> 个元素的和</strong>。这里的 <code>t</code> 是元素个数，不是这段里最后一个元素的下标。前 <code>t</code> 个元素的下标是 <code>0</code> 到 <code>t-1</code>。</p>
<div class="scroll-table" tabindex="0" role="region" aria-label="前缀和定义表"><table><thead><tr><th>t：取多少个</th><th>取到的原数组下标</th><th>计算过程</th><th>prefix[t]</th></tr></thead><tbody>
<tr><td>0</td><td>没有元素，空前缀</td><td>空和</td><td>0</td></tr>
<tr><td>1</td><td>0</td><td>2</td><td>2</td></tr>
<tr><td>2</td><td>0、1</td><td>2 + (-1)</td><td>1</td></tr>
<tr><td>3</td><td>0、1、2</td><td>2 + (-1) + 3</td><td>4</td></tr>
<tr><td>4</td><td>0、1、2、3</td><td>2 + (-1) + 3 + 4</td><td>8</td></tr>
</tbody></table></div><p class="small">窄屏可左右滑动查看完整表格。</p>
<pre class="diagram">原数组：i 是元素下标
i             0   1   2   3
nums[i]       2  -1   3   4

前缀表：t 是取了多少个元素
t             0   1   2   3   4
prefix[t]     0   2   1   4   8
              ↑
         取 0 个元素，和为 0

例如 prefix[2] = nums[0] + nums[1] = 1
不是 nums[0] + nums[1] + nums[2]。</pre>
<div class="note"><strong>为什么数组要多开一格？</strong><p>长度为 n 的原数组有 n+1 个前缀，包括取 0 个元素的空前缀。令 prefix[0]=0 后，从下标 0 开始的区间也可以使用同一条减法公式；它有明确含义，不是为了凑下标而随便补的 0。</p></div>

<h3 id="prefix-construction">2. 怎样构建：旧前缀加上一个新元素</h3>
<p>前两个数的和，不必再把第一个数重算一遍：在前一个累计值上加本次数值即可。扫描原数组下标 <code>i</code> 时，<code>prefix[i]</code> 已经包含前 <code>i</code> 个数，再加上 <code>nums[i]</code>，就得到了前 <code>i+1</code> 个数的和。</p>
<div class="equation">prefix[0] = 0<br>prefix[i + 1] = prefix[i] + nums[i]</div>
<p>把每个前缀都重新从头求和，需要 1+2+…+n 次加法，也就是 O(n²)。按上面的递推构建，每个元素只加一次，时间 O(n)，保存表的空间 O(n)。负数、零都能正常参与累计；前缀和不要求递增。</p>
<div class="prefix-lab demo" id="prefix-build-lab"><div class="demo-head"><h4>动手推演：一格一格填前缀表</h4><label class="prefix-controls" hidden>切换数组<select id="prefix-build-example"><option value="0">[2, -1, 3, 4]</option><option value="1">[0, 0, 0]</option><option value="2">[-2, 5, -3, 4]</option></select></label></div>
<div class="prefix-build-view"><pre class="diagram">nums   = [2, -1, 3, 4]
prefix = [0, ?, ?, ?, ?]
先确定空前缀 prefix[0]=0，再从左向右填表。</pre></div>
<div class="control-row prefix-controls" hidden><button type="button" data-prefix-build="reset">重新开始</button><button type="button" data-prefix-build="prev">上一步</button><button class="primary" type="button" data-prefix-build="next">下一步</button><button type="button" data-prefix-build="last">看完整表</button><span id="prefix-build-count" class="small" role="status" aria-live="polite">已加入 0 / 4 个元素</span></div></div>

<h3 id="prefix-query">3. 为什么两个前缀相减，就是区间的和</h3>
<p>现在求原数组下标 <code>[1,3]</code> 的和，目标是 <code>[-1,3,4]</code>。先取“从开头到下标 3”的全部元素，即前 4 个元素；其中多拿了下标 1 之前的元素 <code>[2]</code>，把这部分减掉即可。</p>
<pre class="diagram">prefix[4] = 2 + (-1) + 3 + 4 = 8
prefix[1] = 2                = 2
两式共同的前半段都是 2。

相减抵消共同的 2：
prefix[4] - prefix[1] = (-1) + 3 + 4 = 6
                        └ 目标区间 [1,3] ┘</pre>
<p>一般地，右端点是 <code>right</code>，要包含它，就取前 <code>right+1</code> 个元素；左端点是 <code>left</code>，要删去它之前的元素，就减掉前 <code>left</code> 个元素。因此：</p>
<div class="equation">sum(nums[left … right])<br>= prefix[right + 1] - prefix[left]</div>
<p><strong>这里的 <code>[left,right]</code> 是闭区间，两端都要取。</strong>长度是 <code>right-left+1</code>。例如只取下标 2，和为 <code>prefix[3]-prefix[2]=4-1=3</code>；从下标 0 取到 2，和为 <code>prefix[3]-prefix[0]=4-0=4</code>。</p>
<div class="prefix-lab demo" id="prefix-query-lab"><div class="demo-head"><h4>试一试：调整端点，观察哪部分被抵消</h4></div><div class="prefix-controls prefix-query-controls" hidden><label>数组<select id="prefix-query-example"><option value="0">[2, -1, 3, 4]</option><option value="1">[0, 0, 0]</option><option value="2">[-2, 5, -3, 4]</option></select></label><label>左端点 left<select id="prefix-left"><option value="0">0</option><option value="1" selected>1</option><option value="2">2</option><option value="3">3</option></select></label><label>右端点 right<select id="prefix-right"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3" selected>3</option></select></label></div>
<div class="prefix-query-view"><pre class="diagram">nums = [2, -1, 3, 4]
目标 [1,3]：[-1, 3, 4]
prefix[4] - prefix[1] = 8 - 2 = 6</pre></div></div>
<p class="small">演示始终保留合法的非空闭区间；若新左端点超过右端点，会把右端点一起移过来，反向操作同理。</p>

<h3>4. 为什么有的代码写 prefix[right]，不写 right+1</h3>
<p>先看它的区间约定。Python 切片 <code>nums[left:end]</code> 包含 left、不包含 end，是左闭右开的 <code>[left,end)</code>。这种情况下取前 end 个元素就够了，公式变成 <code>prefix[end]-prefix[left]</code>。两种写法只是右端点含义不同，不能交叉混用。</p>
<div class="scroll-table" tabindex="0" role="region" aria-label="两种区间约定对照表"><table><thead><tr><th>区间约定</th><th>包含的原数组下标</th><th>公式</th><th>同一个例子</th></tr></thead><tbody><tr><td>闭区间 [left,right]</td><td>left 到 right</td><td>prefix[right+1]−prefix[left]</td><td>[1,3] → 8−2=6</td></tr><tr><td>半开区间 [left,end)</td><td>left 到 end−1</td><td>prefix[end]−prefix[left]</td><td>[1,4) → 8−2=6</td></tr></tbody></table></div><p class="small">窄屏可左右滑动查看完整表格。</p>
<div class="pitfall"><strong>下标与前缀值是两件不同的事</strong><p>prefix 的下标 t 表示取了多少个数，范围是 0..n；prefix[t] 是这些数的和，可能为负，也可能重复。后面字典以“前缀值”为键，例如 -2，并不是在访问数组下标 -2。</p></div>

<h3 id="prefix-code">5. Python 3.12 基础代码：构建一次，查询多次</h3>
<p><code>build_prefix_sum(nums)</code> 接收整数列表，返回长度为 n+1 的前缀表，不修改 nums。<code>range_sum(prefix,left,right)</code> 接收已构建的表与原数组闭区间，返回该区间的整数和；调用前应保证端点合法。</p>
<details class="solution" open><summary>前缀和基础代码 · 中文注释 · 可直接运行</summary>
<div class="code-block"><div class="code-toolbar"><span class="code-language">Python 3.12 · 前缀和入门</span><button type="button" class="copy-code" data-copy-code="prefix-basics" aria-label="复制前缀和基础代码" hidden>复制代码</button></div><pre><code class="python" id="python-prefix-basics" data-foundation-code="prefix-sum">'''
    body += highlight(CODE)
    body += '''</code></pre><p class="copy-status" role="status" aria-live="polite"></p></div></details>
<p><code>[0] * (len(nums)+1)</code> 创建表，<code>enumerate(nums)</code> 依次给出下标 i 和当前值 x。前缀表初始化中的后续 0 只是待填位置，构建过程中它们会被真实累计值覆盖。</p>
<p><strong>多次查询才体现预处理价值：</strong>n 个元素、q 次查询，先构建一次需要 O(n)，每次查两个表值并相减需要 O(1)，总时间 O(n+q)，空间 O(n)。如果每次调用查询都重新构建前缀表，或者用 <code>sum(nums[left:right+1])</code> 重新扫描，就不是 O(1) 查询。</p>

<h3>6. 前缀和能做什么，不能自动解决什么</h3>
<p>它适合在数组内容不变时反复查询连续区间的和，也能把“找区间”转换成“找两个前缀之间的关系”。负数、零不影响相减抵消的关系，后面的 560 正是利用这一点。</p>
<p>但<strong>有了前缀表，并不代表所有区间题都自动变成 O(n)</strong>。如果仍枚举全部左右端点，就有 O(n²) 个候选，只是每个候选求和变快了。560 还要借助哈希计数，将“枚举旧起点”进一步变成一次查询。</p>
<p>若原数组频繁修改，一个值改变会使它后面所有前缀和失效；基础前缀表不适合直接承担大量更新。前缀最小值、最大值也不能照搬相减，例如数组 [1,5,2] 的两个相关前缀最小值都是 1，相减得到 0，却不能还原区间 [1,2] 的最小值 2。</p>
<details class="quiz"><summary>基础自测：nums=[2,-1,3,4]，prefix[3] 是多少？闭区间 [1,2] 的和该减哪两项？</summary><p>prefix[3] 是前 3 个元素的和，2-1+3=4。区间 [1,2] 包含 -1 和 3，应算 prefix[3]-prefix[1]=4-2=2。prefix[2]-prefix[1] 只会取到下标 1，漏掉下标 2。</p></details>
</div>'''
    return body
