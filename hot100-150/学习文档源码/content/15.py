from textwrap import dedent

def checks(method,pairs,**options):
    return dict(method=method,cases=[dict(args=args,expected=expected) for args,expected in pairs],**options)

CHAPTER={
 'lead':'动态规划把大量重复的选择过程压缩成有限状态。关键不是背递推式，而是说明每个状态代表哪些方案，以及为什么这些信息足够支持下一步。',
 'intro':['本章 20 题分为线性递推、选择与状态机、背包与前缀可达、网格、双序列、区间六段。每题先明确状态含义，再讲转移、边界、计算顺序，最后才压缩空间。','相同的 dp[i] 在不同题里可以表示方案数、最优值、可达性或必须以 i 结尾的答案。不要跨题沿用一个模糊的“到这里的最优解”。','代码默认保留输入。本章只有局部 DP 表或滚动变量被更新。300 默认使用 O(n log n) 二分并保留基础 DP；5 默认使用 O(n) Manacher，并保留区间 DP 和中心扩展。其余数学与空间优化均在推荐提交解法处解释，基础图示用于学习状态关系。'],
 'sections':[
  {'title':'五步写出一个可解释的 DP','body':['状态：用一句完整的话解释下标、范围和限制，例如“必须以 i 结尾的非空连续子数组最大和”。','转移：按最后一步或当前是否选择分类，说明不遗漏合法方案，也不引入非法方案。','初始化：为空前缀、首元素、首行首列或不可能状态赋值；默认全零并不总正确。','顺序：一个状态计算时，它依赖的旧状态必须已经得到，并且还没有被错误覆盖。','答案与压缩：先确定答案在最后一格、整表最大值还是若干结束状态的最大值，再判断哪些旧状态以后不再需要。'], 'diagram':'明确状态语义\n    ↓\n分类最后一步，推导转移\n    ↓\n设置合法起点与不可达值\n    ↓\n按依赖顺序计算\n    ↓\n取答案；最后考虑滚动压缩'},
  {'title':'初始化表达的是数学含义','body':['计数题的 dp[0]=1 常表示一种空方案，它让后续选择有起点；最小代价的 dp[0]=0 表示不做任何操作成本为零。','可达性用 True/False；最少次数中不可达状态常用正无穷或不可能达到的大值；股票的非法持仓/卖出状态用负无穷。','53 和 152 要求非空子数组，因此从 nums[0] 初始化最大值；用 0 会把不存在的空子数组加入候选。']},
  {'title':'连续、可跳过与区间是三种状态','body':['子数组/子串必须连续：53、152、718 的结尾状态一旦断开，就必须重开或归零。','子序列允许跳过元素：300 从较早下标衔接，1143 可以舍弃某一边的末字符。','区间状态描述整个 s[i:j+1]：5 的两端相等还需要内部区间为回文，不能直接使用前缀匹配的转移。']},
  {'title':'压缩空间之前，先画出旧值依赖','body':['0/1 背包每件最多一次，容量倒序才能读取上一轮；完全背包允许重复，可正序使用当前轮已经更新的较小容量。','网格一行压缩中，更新前 dp[c] 是上方，更新后 dp[c-1] 是左方；需要左上角时另存旧值。','Python a,b=表达式1,表达式2 会先计算右侧再赋值，适合同时更新滚动状态。分成两行时，第二行可能误用新状态。'], 'diagram':'更新 dp[c] 之前：\n   旧 dp[c] = 上方\n新 dp[c-1] = 左方\n       prev = 旧左上方\n\n先保存旧 dp[c]，更新后再推进 prev'}
 ],
 'apis':[
  {'signature':'[0] * n 与 [[0] * n for _ in range(m)]','description':['整数不可变，一维重复零可以安全地按下标赋值。二维表每行必须分别创建。','[[0]*n]*m 会重复引用同一个内层列表；修改一个格子时多行一起变化，不适合作为独立 DP 行。']},
  {'signature':'range(start, stop, step)；float("inf")','description':['range 不包含 stop。倒序容量通常是 range(target,x-1,-1)，才能包含容量 x。','正无穷用于不可达的最小化状态，负无穷用于不可达的最大化状态；有效转移会用有限值取代它们。']}
 ],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':70,'slug':'climbing-stairs',
 'summary':'一次可上 1 或 2 级台阶，求恰好到第 n 级的不同走法数。先走 1 再走 2 与先走 2 再走 1 是不同方案。',
 'baseline':'递归枚举最后走 1 级或 2 级时，f(n-2) 等子问题会在很多分支中重复计算，形成指数级工作。相同剩余台阶的答案只需要求一次。',
 'insight':'定义 f(i) 为到第 i 级的方案数。最后一步只有 1 或 2 两种互斥情况，分别来自 i-1 和 i-2，因此 f(i)=f(i-1)+f(i-2)。只依赖前两项，可以滚动保存。',
 'steps':['设 f(0)=1，表示停在起点的一种空方案；f(1)=1。','用 previous=1、current=1 表示 f(0)、f(1)。','从 i=2 到 n，计算 next=previous+current，再将前两项向前滚动。','返回 current。'],
 'invariant':'计算第 i 项之前，previous=f(i-2)，current=f(i-1)。任意到 i 的路线都恰好属于最后走 1 级或最后走 2 级之一；删去最后一步后分别与前两个状态的路线一一对应，故相加不漏不重。',
 'examples':[{'label':'按最后一步分组','input':'n=4','output':'5','frames':[
  {'title':'4 级的路线来自两个更小问题','note':'到 3 的每种路线接 1，到 2 的每种路线接 2，两类末步不同。','diagram':'f(3)=3 ── 再走1级 ──┐\n                    ├→ f(4)=5\nf(2)=2 ── 再走2级 ──┘'},
  {'title':'从小到大填出递推值','note':'f(0)=1 不是题目要求返回 0 级答案，而是让“直接走 2 级”有一个空前缀来源。','table':{'headers':['i',0,1,2,3,4],'rows':[['f(i)',1,1,2,3,5]]}},
  {'title':'只保留相邻两项','note':'计算 f(4) 时只要 f(2)=2 与 f(3)=3；之后旧 f(2) 不再使用。','array':[2,3,5],'pointers':{'旧 previous':0,'旧 current':1,'新 current':2}}
 ]}],
 'walkthrough':['把问题看成最后一步分类，比枚举最开始的路线更容易得到下标依赖。','n=1 时循环不执行，current=1 正好是答案；n=2 时得到 2。','每轮同时更新两个变量，确保右侧使用的都是上一轮值。'],
 'code':'''
class Solution:
    def climbStairs(self, n: int) -> int:
        # 分别保存到前两阶、前一阶的走法；0 阶与 1 阶都设为 1。
        previous, current = 1, 1
        for i in range(2, n + 1):
            # 下一阶可从前一阶走一步，或从前两阶走两步到达。
            previous, current = current, previous + current
        return current
'''.strip(),
 'code_notes':['range(2,n+1) 包含第 n 项。','右侧先整体求值，所以 current 的新值不会影响同一次赋值右侧的 previous+current。','题目 n≥1，初始化直接覆盖最小合法输入。'],
 'pitfalls':['把 1+2 与 2+1 当成同一种组合。','令 f(0)=0 后仍使用原转移，使 f(2) 少算直接跳两级。','分两行更新 previous、current，第二行误读新 previous。'],
 'complexity':'时间 O(n)，额外空间 O(1)，在本题 n≤45 的范围内整数运算按常数计。',
 'quiz':{'question':'到第 5 级为何是 f(4)+f(3)，而不是 f(4)+1？','answer':'最后跨两级前可以用任意一种到第 3 级的路线，因此贡献 f(3) 种，不是固定的一种。'},
 'tests':checks('climbStairs',[([1],1),([2],2),([4],5),([5],8),([45],1836311903)])
})

CHAPTER['problems'].append({
 'id':118,'slug':'pascals-triangle',
 'summary':'返回杨辉三角的前 numRows 行。每行两端为 1，内部元素等于上一行与它相邻的两个元素之和。',
 'baseline':'逐个元素递归向上求值会反复计算同一个位置。题目本来就要求输出所有行，可以按行生成并直接复用上一行结果。',
 'insight':'用从 0 开始的行号 r，第 r 行长 r+1。内部位置 c 满足 row[c]=previous[c-1]+previous[c]。先创建全 1 的新行，再只填内部位置，首尾边界自然成立。',
 'steps':['result 初始为空。','对 r=0..numRows-1，新建长度 r+1 的全 1 行。','对 c=1..r-1，从 result[-1] 的相邻位置求和。','把完整新行追加到 result，最后返回全部行。'],
 'invariant':'开始第 r 轮时，result 已准确保存前 r 行。新行两端按定义是 1，所有内部值只读取已经完成的上一行，因此整行正确；每次新建列表，后续写入也不会改变旧行。',
 'examples':[{'label':'一行生成下一行','input':'numRows=5','output':'[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]','frames':[
  {'title':'先固定新行两端','note':'第 4 行用零基下标 r=4，长度为 5。两个端点不需要访问越界邻居。','array':[1,'?', '?','?',1],'active':[0,4]},
  {'title':'内部值来自上一行相邻两项','note':'上方是旧行，下方是新行。中间的 6 来自旧行的 3+3，不是新行中的值。','diagram':'    1   3   3   1\n     \\ / \\ / \\ /\n  1   4   6   4   1'},
  {'title':'保存五行完整结果','note':'每一行都是独立列表，结果要求保留全部行，不能只返回滚动的最后一行。','diagram':'        1\n      1   1\n    1   2   1\n  1   3   3   1\n1   4   6   4   1'}
 ]}],
 'walkthrough':['r=0 时 row=[1]，内部循环为空，不会读取还不存在的 result[-1]。','r=1 时同样没有内部位置，直接得到 [1,1]。从 r=2 起才开始相邻求和。','上一行存在 result 中，因此无须另开一份相同长度的缓存。空间分析必须计入题目要求返回的所有行。'],
 'code':'''
class Solution:
    def generate(self, numRows: int) -> list[list[int]]:
        result = []
        for r in range(numRows):
            # 每行两端恒为 1，每次创建新行，不能让不同行共享列表。
            row = [1] * (r + 1)
            for c in range(1, r):
                # 内部位置等于上一行左上、右上两个数之和。
                row[c] = result[-1][c - 1] + result[-1][c]
            result.append(row)
        return result
'''.strip(),
 'code_notes':['range(1,r) 排除新行的两个端点 0、r。','row 每轮重新创建；追加后不再修改这一行。','列表内重复的整数 1 不可变，按下标替换不会影响其他格子。'],
 'pitfalls':['把 numRows 当成最后行的零基编号，多生成一行。','内部循环包含端点，读取上一行越界位置。','重复追加同一个可变 row，并在后续原地改写。'],
 'complexity':'时间 O(R²)，返回结果占 O(R²) 空间，其中 R=numRows；不另复制历史行。',
 'quiz':{'question':'第 r 行为何只算 c=1..r-1？','answer':'第 r 行的有效下标是 0..r，两端按定义为 1，只有内部位置同时有上一行的两个来源。'},
 'tests':checks('generate',[([1],[[1]]),([2],[[1],[1,1]]),([3],[[1],[1,1],[1,2,1]]),([5],[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]])])
})

CHAPTER['problems'].append({
 'id':53,'slug':'maximum-subarray',
 'summary':'找出和最大的非空连续子数组，返回它的和。元素可以为负，不能跳过中间元素，也不能用空数组获得 0。',
 'baseline':'枚举左右端点并累计区间和需要 O(n²)。对固定右端点 i，所有候选要么只有 nums[i]，要么续接某个以 i-1 结尾的连续子数组，只需保留其中最优者。',
 'insight':'ending 是必须以当前位置结尾的最大和，best 是所有已处理结尾的最大值。转移 ending=max(x,old_ending+x)：旧前缀有帮助就续接，否则从当前元素重新开始。',
 'steps':['ending=best=nums[0]，保证候选非空。','从下标 1 开始，计算以当前 x 结尾的两种可能。','更新 ending 后，用它更新全局 best。','返回 best，而不是最后一个 ending。'],
 'invariant':'任何以 i 结尾的非空连续子数组，若长度超过 1，去掉最后元素后必以 i-1 结尾。加上相同 x 不改变各旧候选和的大小关系，因此旧最大 ending 足以代表所有续接候选；与单独 x 比较即得当前最优。',
 'examples':[{'label':'续接与重开','input':'nums=[-2,1,-3,4,-1,2,1,-5,4]','output':'6','frames':[
  {'title':'负前缀会让新段变差','note':'在 4 之前 ending=-2，续接得 2，重新开始得 4，因此选择从 4 开始。','table':{'headers':['x','旧 ending','续接','重开','新 ending'],'rows':[[1,-2,-1,1,1],[-3,1,-2,-3,-2],[4,-2,2,4,4]]}},
  {'title':'中间负数可以保留','note':'4 后接 -1 得 3，仍比单独 -1 好；继续接 2、1 得到 6。不能遇到任意负数就断开。','array':[-2,1,-3,4,-1,2,1,-5,4],'active':[3,4,5,6],'metrics':[['最大和',6]]},
  {'title':'结尾状态不等于全局答案','note':'末尾的 ending=5，之前出现过 best=6，所以必须独立维护全局最大值。','table':{'headers':['处理 x','ending','best'],'rows':[[4,4,4],[-1,3,4],[2,5,5],[1,6,6],[-5,1,6],[4,5,6]]}}
 ]},{'label':'全负数也必须选一个','input':'nums=[-5,-2,-7]','output':'-2','frames':[
  {'title':'零不是合法候选','note':'最优子数组是单元素 [-2]，使用 best=0 会错误接受空子数组。','array':[-5,-2,-7],'active':[1]}
 ]}],
 'walkthrough':['ending 的“必须以 i 结尾”是转移成立的关键，不能把之前任意位置的 best 直接加到 x 上，否则可能跨过中间元素。','遇到负数不一定重开；比较的是旧段总和是否有帮助。','输入非空，从首元素初始化并跳过首元素循环，避免重复计算它。'],
 'code':'''
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        # ending 必须以当前位置结尾，best 才是整个前缀的最大值；初始化防止全负数误判。
        ending = best = nums[0]
        for i in range(1, len(nums)):
            # 前面接上反而更差时，就从当前元素重新开始。
            ending = max(nums[i], ending + nums[i])
            best = max(best, ending)
        return best
'''.strip(),
 'code_notes':['没有 nums[1:] 切片，空间确实为常数。','局部变量 ending 与 best 分别对应结尾最优和全局最优。','不修改 nums，也不需要真正保存最优子数组；若要求返回范围，可在重开时记录起点。'],
 'pitfalls':['best 初始为 0，处理全负数错误。','拿 best+x 作为续接候选，破坏连续性。','只返回最后的 ending。'],
 'complexity':'时间 O(n)，额外空间 O(1)。',
 'quiz':{'question':'[4,-1,2] 是否应在 -1 处重开？','answer':'不应。到 -1 时续接和为 3，比单独 -1 大，最终整个区间和为 5。'},
 'tests':checks('maxSubArray',[([[-2,1,-3,4,-1,2,1,-5,4]],6),([[-5,-2,-7]],-2),([[1]],1),([[0,0]],0),([[5,4,-1,7,8]],23)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':152,'slug':'maximum-product-subarray',
 'summary':'求非空连续子数组的最大乘积。允许正数、负数和零；题目保证任意子数组乘积在 32 位整数范围内。',
 'baseline':'枚举全部连续区间并累计乘积需要 O(n²)。照搬最大子数组和只保留最大结尾乘积会丢失信息，因为乘负数会反转大小关系，旧的最小值可能变成新的最大值。',
 'insight':'同时维护以当前位置结尾的最大乘积 high 和最小乘积 low。对新数 x，完整候选为 x、old_high*x、old_low*x；分别取最大和最小，再更新全局 best。',
 'steps':['high=low=best=nums[0]。','保存三个候选，全部由旧 high、low 计算。','high 取候选最大值，low 取最小值。','更新 best=max(best,high)，最后返回 best。'],
 'invariant':'任意当前结尾的区间要么从 x 开始，要么续接上一位置的区间。乘正数保持旧候选顺序，乘负数反转顺序，乘零使所有续接候选归零；因此旧最大和最小值足以确定所有续接结果的两端极值。',
 'examples':[{'label':'旧最小值乘负数成为最大值','input':'nums=[-2,3,-4]','output':'24','frames':[
  {'title':'处理 3 时要保留 -6','note':'最大结尾乘积是单独 3，但最小的 -6 不能丢掉。','table':{'headers':['x','候选','high','low'],'rows':[[-2,'初始化',-2,-2],[3,'3, -6, -6',3,-6]]}},
  {'title':'遇到 -4，最小值翻成最大值','note':'(-6)×(-4)=24，比 3×(-4)=-12 大。','table':{'headers':['新候选','值'],'rows':[['单独 -4',-4],['旧 high × -4',-12],['旧 low × -4',24]]}},
  {'title':'整个连续区间实现 24','note':'保存 low 只是为了未来转移，它不一定是当前返回的最优值。','array':[-2,3,-4],'active':[0,1,2],'metrics':[['best',24]]}
 ]},{'label':'零会切断跨越的乘积','input':'nums=[-2,0,-1]','output':'0','frames':[
  {'title':'不能跳过中间的零','note':'[-2,-1] 不是连续子数组；所有跨过零的乘积都为零，最大答案为 0。','array':[-2,0,-1],'active':[1]}
 ]}],
 'walkthrough':['high 和 low 必须从同一轮旧值推导，不能先覆盖 high 再用它计算 low。','遇到零时三个候选都为零；下一项仍可通过单独 x 的候选重新开始，所以不需要额外重置分支。','best 仍独立保存历史最优，最终一项的 high 可能已经下降。'],
 'code':'''
class Solution:
    def maxProduct(self, nums: list[int]) -> int:
        # 同时保留以当前位置结尾的最大、最小乘积，因为乘负数会反转大小。
        high = low = best = nums[0]
        for i in range(1, len(nums)):
            x = nums[i]
            # 先用旧的 high、low 算出三个候选，再同时更新，不能提前覆盖旧值。
            candidates = (x, high * x, low * x)
            high = max(candidates)
            low = min(candidates)
            # high 只负责以当前元素结尾，best 还需保留更早位置结束的最优答案。
            best = max(best, high)
        return best
'''.strip(),
 'code_notes':['candidates 元组先计算完成，再覆盖两个状态，避免新旧混用。','固定三个候选占常数空间。','单个负数也属于合法非空区间，从首元素初始化即可正确返回它。'],
 'pitfalls':['只保留最大乘积。','把最小值初始化成 0 或 1，引入不存在的空区间。','看到零就丢掉此前 best。','不保存旧状态就连续覆盖 high、low。'],
 'complexity':'时间 O(n)，额外空间 O(1)；题目限制乘积范围，整数运算按常数计。',
 'quiz':{'question':'[-2,3,-4] 在读到 3 后，为什么要保存 -6？','answer':'它虽然目前较小，但下一步乘 -4 会得到 24，成为最大候选。'},
 'tests':checks('maxProduct',[([[-2,3,-4]],24),([[2,3,-2,4]],6),([[-2,0,-1]],0),([[-2]],-2),([[0,2]],2)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':198,'slug':'house-robber',
 'summary':'一排房屋各有非负金额，不能选择相邻两间，求能取走的最大总金额。返回金额，不要求具体房屋方案。',
 'baseline':'每间房选或不选的枚举有指数数量。只按奇偶位置选一组也不可靠，例如 [2,1,1,2] 最优选首尾，金额 4，超过任一固定奇偶组。',
 'insight':'定义 f(i) 为前 i 间房的最大金额。当前房是下标 i-1：不选得 f(i-1)，选则必须跳过上一间，得 f(i-2)+nums[i-1]。比较两种合法类别，只保留前两项。',
 'steps':['before_previous=previous=0，表示尚未选房的基础状态。','依次读金额 money，current=max(previous,before_previous+money)。','滚动为 before_previous=previous、previous=current。','返回 previous。'],
 'invariant':'处理当前房之前，previous 是已处理所有房的最优金额，before_previous 是少处理最后一间时的最优金额。不选当前时保留 previous；选当前时接在 before_previous 的方案后，保证与上一间不相邻。两类覆盖所有合法方案。',
 'examples':[{'label':'当前不选也可能最优','input':'nums=[2,7,9,3,1]','output':'12','frames':[
  {'title':'逐间比较选与不选','note':'选 9 时接到前两间之前的状态 2，得到 11；不能接到包含相邻 7 的状态。','table':{'headers':['money','不选','选','current'],'rows':[[2,0,2,2],[7,2,7,7],[9,7,11,11],[3,11,10,11],[1,11,12,12]]}},
  {'title':'最优方案为 2、9、1','note':'相邻限制只禁止紧挨的房屋，并不要求固定隔一间选一次。','array':[2,7,9,3,1],'active':[0,2,4],'metrics':[['总额',12]]}
 ]},{'label':'不固定选奇数或偶数位置','input':'nums=[2,1,1,2]','output':'4','frames':[
  {'title':'两端可以同时选','note':'首尾不相邻，选 2+2 得 4；固定奇偶组都只能得 3。','array':[2,1,1,2],'active':[0,3]}
 ]}],
 'walkthrough':['状态是前缀里可以自由选择的最优值，允许不选当前房；这与 53 必须以当前元素结尾的含义不同。','所有金额非负，空前缀收益为 0，自然处理金额为零的房屋。','先计算 current，再滚动两个旧值，不会让当前金额被重复选择。'],
 'code':'''
class Solution:
    def rob(self, nums: list[int]) -> int:
        # 分别保存到前两间、前一间为止的最大收益。
        before_previous = previous = 0
        for money in nums:
            # 不偷当前间就沿用 previous；偷则只能接前两间的答案。
            current = max(previous, before_previous + money)
            # 滚动更新两个历史状态，不需要整张 DP 表。
            before_previous, previous = previous, current
        return previous
'''.strip(),
 'code_notes':['循环开始前两个零用于统一处理第一间，不代表额外的真实房屋。','previous 单调不减，因为不选当前总是合法。','代码只累计最优值；若要还原选择，需要额外保存决策或完整状态表。'],
 'pitfalls':['直接把所有正金额相加。','当前 money 加到 previous，可能同时选择相邻两间。','假设最优一定是所有奇数位或所有偶数位。'],
 'complexity':'时间 O(n)，额外空间 O(1)。',
 'quiz':{'question':'[2,1,1,2] 的最优方案为何能混用不同奇偶位置？','answer':'限制是两两不相邻，而非必须统一奇偶；下标 0、3 相差 3，合法且金额最大。'},
 'tests':checks('rob',[([[2,7,9,3,1]],12),([[1,2,3,1]],4),([[2,1,1,2]],4),([[0]],0),([[400]],400)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':213,'slug':'house-robber-ii',
 'summary':'房屋围成一圈，首尾也相邻，其他规则同 198。求不能同时选择相邻房屋时的最大总金额。',
 'baseline':'直接套用线性解可能同时选择首尾，例如 [2,3,2] 会误得 4。若枚举是否选每间房仍是指数复杂度，但新增约束只涉及首尾这一对。',
 'insight':'任何合法方案至少不选首尾之一，因此分别求“不选末项”的线性区间 [0,n-1) 与“不选首项”的线性区间 [1,n)，取最大值。两类允许重叠，不要求被允许的另一个端点一定选。',
 'steps':['n=1 单独返回唯一房屋金额。','定义线性辅助函数 linear(start,stop)，只遍历半开区间。','使用 198 的选/不选滚动转移。','返回 max(linear(0,n-1),linear(1,n))。'],
 'invariant':'合法环形方案不可能同时含首尾，故必落在两个子问题之一；反过来，每个子问题排除了一个端点，线性不相邻也保证环形不相邻。因此两类最优值的最大值恰好等于环形最优，而非近似。',
 'examples':[{'label':'拆掉首尾冲突','input':'nums=[2,3,2]','output':'3','frames':[
  {'title':'首尾的 2 不能一起取','note':'环形多了一条 0 与 2 的邻接关系。','diagram':'下标 0:2 ─── 下标 1:3\n    ╲             ╱\n       下标 2:2'},
  {'title':'两个线性子问题各排除一端','note':'不是强制选首项或末项，而是限制可选范围。','table':{'headers':['子问题','允许数组','最优'],'rows':[['不选末项','[2,3]',3],['不选首项','[3,2]',3]]}},
  {'title':'取较大者得到 3','note':'选择中间的 3 同时属于两类，但求最大值时重复出现不影响答案。','array':[2,3,2],'active':[1]}
 ]}],
 'walkthrough':['拆分条件是“至少排除一个端点”，不等价于“必须选一个端点”。最优可能只取中间房。','两个长度 n-1 的线性问题各 O(n)，总时间仍是 O(n)。','使用下标范围而非 nums[:-1]、nums[1:]，避免创建两份切片并错误宣称 O(1) 空间。','n=1 必须单独处理，否则两个排除端点的区间都为空，遗漏唯一房屋。'],
 'code':'''
class Solution:
    def rob(self, nums: list[int]) -> int:
        n = len(nums)
        # 只有一间时，两种去头去尾区间都会为空，必须单独返回这间金额。
        if n == 1:
            return nums[0]
        # 计算左闭右开的一段普通打家劫舍，不创建子数组切片。
        def linear(start: int, stop: int) -> int:
            before_previous = previous = 0
            for i in range(start, stop):
                # 每间仍然在“不偷”和“偷并跳过前一间”之间取最大值。
                current = max(previous, before_previous + nums[i])
                before_previous, previous = previous, current
            return previous
        # 环上首尾不能同时偷，分别计算不选尾间、不选首间的最大收益。
        return max(linear(0, n - 1), linear(1, n))
'''.strip(),
 'code_notes':['嵌套函数读取外层 nums，不复制输入，也不修改它。','两个 linear 调用的局部滚动状态各自从零开始。','n=2 时两个范围各只有一间，正确返回较大金额。'],
 'pitfalls':['直接按线性数组计算，忽略首尾邻接。','把两次结果相加，重复选择不兼容方案。','误以为第一类必须选择首项。','漏掉单元素边界或用切片后仍报常数空间。'],
 'complexity':'时间 O(n)，额外空间 O(1)。',
 'quiz':{'question':'[1,100,1] 拆成两类后，是否强迫选择某个端点？','answer':'不会。两类都允许只选中间的 100；拆分只排除一端，不强制选另一端。'},
 'tests':checks('rob',[([[2,3,2]],3),([[1,2,3,1]],4),([[1,100,1]],100),([[9]],9),([[2,7]],7)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':309,'slug':'best-time-to-buy-and-sell-stock-with-cooldown',
 'summary':'允许多次股票交易，同时最多持有一股；卖出后的第二天禁止买入，必须冷冻一天。求最终不持股时的最大利润。',
 'baseline':'122 的累加正相邻差不再成立，例如卖出赚取一次上涨后，第二天可能恰好是低价买点，却因冷冻无法买入。必须保留会影响明天行动资格的状态。',
 'insight':'用每日结束状态：hold 表示持股，sold 表示恰好今天卖出，rest 表示不持股且今天未卖出。今天买入只能来自昨天 rest；昨天 sold 今天只能进入 rest，不能直接买入。',
 'steps':['从第 0 天初始化 hold=-prices[0]、sold=-∞、rest=0。','对今天价格 p：new_hold=max(hold,rest-p)。','new_sold=hold+p；new_rest=max(rest,sold)，右侧全部是昨天值。','同时替换三个状态。','最终返回 max(sold,rest)，不把未出售股票计入利润。'],
 'invariant':'三类按当天结束时的持仓及是否当天卖出互斥分类。继续持有或合法买入构成 hold；只有昨天持股才能今天卖出；休息来自昨天休息或昨天卖出后的冷冻。每条合法交易路线都对应这些转移，且不存在 sold→次日买入的非法边。',
 'examples':[{'label':'卖出后不能立刻抢低价','input':'prices=[1,2,3,0,2]','output':'3','frames':[
  {'title':'状态机限制可以买入的来源','note':'图中的边都从昨天到今天。sold 到 rest 消耗一天冷冻，rest 才能在下一天买入。','diagram':'昨天 hold ── 卖出 +p ──→ 今天 sold\n昨天 sold ── 冷冻一天 ──→ 今天 rest\n昨天 rest ── 买入 -p ──→ 今天 hold\n昨天 hold ── 继续持有 ──→ 今天 hold\n昨天 rest ── 继续休息 ──→ 今天 rest'},
  {'title':'逐天比较同一结束状态的收益','note':'利润相同但持仓或冷冻资格不同的路线，不能过早合并。','table':{'headers':['日/价格','hold','sold','rest'],'rows':[['0 / 1',-1,'−∞',0],['1 / 2',-1,1,0],['2 / 3',-1,2,1],['3 / 0',1,-1,2],['4 / 2',1,3,2]]}},
  {'title':'一条最优路线实现利润 3','note':'1 买、2 卖，价格 3 当天冷冻；0 买、2 卖，总利润 1+2=3。','array':[1,2,3,0,2],'pointers':{'买':0,'卖':1,'冷冻':2,'再买':3,'再卖':4}}
 ]}],
 'walkthrough':['rest 是“今天结束不持股且今天没卖”，即使今天正在冷冻，到明天也已可买，所以它能作为下一轮买入来源。','sold 只表示今天刚卖，不能把历史所有不持股利润统统放进它。','第 0 天无法先买后在更晚时刻完成一笔跨日交易，因此 sold 初始化不可达；不交易的 rest=0 保证不会被迫亏损。','同时赋值保证今天 rest 不会被今天 new_hold 误用，避免绕过冷冻。'],
 'code':'''
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        # hold 为持有股票的收益，sold 为今天刚卖出，rest 为今天休息且未持有。
        hold = -prices[0]
        # 第 0 天不可能已经完成卖出，用负无穷标记不可达状态。
        sold = float('-inf')
        rest = 0
        for i in range(1, len(prices)):
            price = prices[i]
            # 右侧全部使用昨天状态，一次赋值避免把今天卖出的结果拿去今天买入。
            hold, sold, rest = (
                # 只能从昨天的 rest 买入，昨天刚卖出的 sold 今天必须冷冻。
                max(hold, rest - price),
                hold + price,
                max(rest, sold),
            )
        # 最终不能持有股票；卖出状态与休息状态取更优值。
        return max(sold, rest)
'''.strip(),
 'code_notes':['多行元组右侧先全部求值，三个转移都使用上一天状态。','hold 可为正，表示此前利润减去当前持仓买价后的净现金，不是股票本身价格。','单日输入直接返回 max(-∞,0)=0，类型和数值都是合法的整数答案。'],
 'pitfalls':['继续累加每个正差，忽略冷冻。','从昨天 sold 直接计算今天买入。','用更新后的 hold 计算 sold，混合当天动作。','最终返回 hold，把尚未卖出的仓位当成已实现收益。'],
 'complexity':'时间 O(n)，额外空间 O(1)。',
 'quiz':{'question':'为什么不能把 sold 与 rest 永久合并成一个 cash 状态？','answer':'它们明天的买入资格不同；sold 明天必须冷冻，rest 明天可以直接买入。合并会丢掉影响后续合法性的必要信息。'},
 'tests':checks('maxProfit',[([[1,2,3,0,2]],3),([[1]],0),([[2,1]],0),([[1,2]],1),([[1,2,4]],3)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':300,'slug':'longest-increasing-subsequence',
 'summary':'求严格递增子序列的最大长度。可以跳过元素，但必须保持原来的下标顺序；相等数不能让长度增加。',
 'baseline':'枚举所有下标子集要 O(2^n)。固定最后一个下标 i 后，最优子序列只需接到某个更早且值更小的位置，从而用每个结尾的最长长度概括大量方案。',
 'insight':'入门状态 dp[i] 是必须以 nums[i] 结尾的最长长度，初始为 1。枚举 j<i 且 nums[j]<nums[i]，用 dp[j]+1 更新。进阶把相同长度的候选压缩成最小尾值 tails，用二分定位新数可改进的长度。',
 'steps':['创建 n 个 1，每个元素单独就是长度 1 的序列。','从左到右计算 i，枚举它之前的 j。','只有 nums[j]<nums[i] 才能衔接，更新 dp[i]。','返回 max(dp)。','理解主解后再看 lengthOfLISBinary：对 x 找 tails 中第一个 >=x 的位置，替换它或在末尾追加。'],
 'invariant':'DP 中，任意以 i 结尾的长度大于 1 的递增子序列，都有某个合法前驱 j；枚举所有 j 取最大即可。二分版中 tails[k] 是已读前缀里长度 k+1 的递增子序列的最小尾值；同长度下尾值越小，越容易接上未来元素，因此替换为更小尾值不会丢失可实现的最优长度。',
 'examples':[{'label':'每个结尾有独立长度','input':'nums=[10,9,2,5,3,7,101,18]','output':'4','frames':[
  {'title':'枚举更小的合法前驱','note':'7 可以接在 5 或 3 后，得到长度 3；101 和 18 都可接在 7 后得到 4。','table':{'headers':['nums',10,9,2,5,3,7,101,18],'rows':[['dp',1,1,1,2,2,3,4,4]]}},
  {'title':'二分版维护同长度最小尾值','note':'读到 3 时，用 3 替换长度 2 的旧尾值 5；读到 18 时替换长度 4 的旧尾值 101。长度都不减少。','table':{'headers':['读入','tails'],'rows':[[10,'[10]'],[9,'[9]'],[2,'[2]'],[5,'[2,5]'],[3,'[2,3]'],[7,'[2,3,7]'],[101,'[2,3,7,101]'],[18,'[2,3,7,18]']]}},
  {'title':'长度 4 是可实现的','note':'例如选下标 2、4、5、7，得到 2、3、7、18。','array':[10,9,2,5,3,7,101,18],'active':[2,4,5,7]}
 ]},{'label':'相等元素只替换，不延长','input':'nums=[7,7,7]','output':'1','frames':[
  {'title':'严格递增排除相等衔接','note':'bisect_left 总是找到下标 0，三个 7 最终仍只有长度 1。','table':{'headers':['已读数量','tails','长度'],'rows':[[1,'[7]',1],[2,'[7]',1],[3,'[7]',1]]}}
 ]}],
 'walkthrough':['DP 的答案不一定在最后一项。例如 [1,2,3,0] 的最后 dp 为 1，但全局答案为 3。','tails 递增：更长递增序列的末项必须比它前一项大，而前一项又不小于该长度可实现的最小尾值。因此可以二分查找。','对 x 找第一个 >=x 的位置 pos。前面长度 pos 的最小尾值严格小于 x，可以接上 x；用 x 改善长度 pos+1 的尾值。若 pos 等于当前长度，则得到更长序列。','tails 各项代表不同长度的最优尾值，整体未必是原数组的一条真实子序列。例如 [3,5,6,2,4] 最终 tails=[2,4,6]，但 6 出现在 2 之前。长度正确，直接返回 tails 作为路径却不正确。'],
 'code':'''
from bisect import bisect_left

class Solution:
    def lengthOfLIS(self, nums: list[int]) -> int:
        # tails[t] 是长度为 t+1 的递增子序列能达到的最小末尾值。
        tails = []
        for x in nums:
            # 找第一个 ≥x 的位置；相等时替换而不追加，保证严格递增。
            position = bisect_left(tails, x)
            if position == len(tails):
                tails.append(x)
            else:
                # 用更小末尾保留未来扩展机会；tails 本身不一定是原数组的一条子序列。
                tails[position] = x
        return len(tails)

    def lengthOfLISDP(self, nums: list[int]) -> int:
        # 对照 DP：dp[i] 是以 nums[i] 结尾的最长严格递增子序列长度。
        dp = [1] * len(nums)
        for i in range(len(nums)):
            for j in range(i):
                # 只有严格更小的前项才能接上，相等值不增加长度。
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    def lengthOfLISBinary(self, nums: list[int]) -> int:
        # 保留具名接口便于对照；默认提交入口已经使用同一高效实现。
        return self.lengthOfLIS(nums)
'''.strip(),
 'api':{'signature':'bisect_left(sorted_list,x) -> 第一个 >=x 的位置','description':['输入列表必须有序；返回值也可能等于长度，表示 x 比所有现有值都大。','本题原地替换一个尾值或在末尾追加，没有使用 insert 在中间移动元素。若希望平台使用进阶解，可把 lengthOfLIS 的方法体替换为 return self.lengthOfLISBinary(nums)，并保留下面的辅助方法。']},
 'code_notes':['默认 lengthOfLIS 使用 tails 与 bisect_left；lengthOfLISDP 对应前面的基础状态转移。', 'bisect_left 返回第一个不小于 x 的位置，相等时替换，不能错误地增加长度。', 'tails 只保存各长度的最小末尾，不保证其全部元素共同构成原数组的一条子序列。'],
 'pitfalls':['排序原数组再去重，丢失原先顺序限制。','用 <= 衔接相等值，写成最长非递减序列。','把 tails 当成一定可直接输出的路径。','二分后执行中间插入，既改变语义又增加移动成本。'],
 'complexity':'默认二分方法时间 O(n log n)、额外空间 O(n)。对照 DP 时间 O(n²)、空间 O(n)。',
 'quiz':{'question':'[1,2,2,3] 的严格递增长度是 3 还是 4？','answer':'是 3，相等的两个 2 不能同时出现在严格递增序列中。DP 用 <，二分用 bisect_left 都体现这个限制。'},
 'tests':checks('lengthOfLIS',[([[10,9,2,5,3,7,101,18]],4),([[7,7,7]],1),([[1,2,3,0]],3),([[3,5,6,2,4]],3),([[1,2,2,3]],3)],preserve_args=[0])
,
 'submission': {'name': '最小末尾数组与二分', 'why': '默认入口改为 O(n log n)。前面的二维选择关系说明为什么保留较小末尾更有利，lengthOfLISDP 保留 O(n²) 状态转移作对照。', 'steps': ['tails[t] 记录长度 t+1 的严格递增子序列所能拥有的最小末尾。', '用 bisect_left 找到第一个 ≥x 的位置，替换它以降低末尾。', '如果所有末尾都小于 x，就追加一项；tails 的长度就是答案。'], 'diagram': 'tails=[2,5,7]，读到 3 → [2,3,7]\n读到 8 → [2,3,7,8]\n替换让末尾更小；追加才增加长度'},
})

CHAPTER['problems'].append({
 'id':322,'slug':'coin-change',
 'summary':'每种面值的硬币数量无限，凑出恰好 amount 的最少硬币数；无法凑出返回 -1，amount=0 返回 0。所有面值为正数。',
 'baseline':'总选最大面值可能失败：[1,3,4] 凑 6，贪心用 4+1+1 要三枚，但 3+3 只要两枚。枚举所有硬币序列又会反复求相同剩余金额。',
 'insight':'dp[a] 表示凑出金额 a 的最少枚数。按最后一枚硬币 c 分类，前面必须凑出 a-c，候选为 dp[a-c]+1。正面值保证 a-c<a，按金额递增就能读取已完成状态。',
 'steps':['dp[0]=0，其余设为 amount+1，表示不可达。','从 a=1 到 amount 枚举目标金额。','对每个 c≤a，更新 dp[a]=min(dp[a],dp[a-c]+1)。','最终若 dp[amount] 仍为哨兵则返回 -1，否则返回枚数。'],
 'invariant':'计算 a 时，所有更小金额的最少枚数已经正确。任意可行方案删去最后一枚 c 后得到金额 a-c 的方案；使用该金额的最少枚数不会更差。反向地，任何可达 a-c 加一枚 c 都合法，因此取最小值得到恰好的最优答案。',
 'examples':[{'label':'比较所有最后一枚','input':'coins=[1,3,4], amount=6','output':'2','frames':[
  {'title':'金额从小到大完成','note':'这里 ∞ 表示初始不可达，完成后的 dp 如表。','table':{'headers':['金额',0,1,2,3,4,5,6],'rows':[['最少枚数',0,1,2,1,1,2,2]]}},
  {'title':'凑 6 的最后一枚可以不同','note':'用 3 作为最后一枚时，前面的 3 只需一枚，合计两枚。','table':{'headers':['最后一枚 c','前面金额','候选枚数'],'rows':[[1,5,'2+1=3'],[3,3,'1+1=2'],[4,2,'2+1=3']]}},
  {'title':'同一面值可以重复使用','note':'3+3 实现最优，不需要为某个面值设置 used 标记。','array':[3,3],'active':[0,1],'metrics':[['金额',6],['枚数',2]]}
 ]},{'label':'不可达不能当成零枚','input':'coins=[2], amount=3','output':'-1','frames':[
  {'title':'奇数金额没有来源','note':'dp[1] 不可达，dp[3] 从它再加一枚也不可达。','table':{'headers':['金额',0,1,2,3],'rows':[['最少枚数',0,'∞',1,'∞']]}}
 ]}],
 'walkthrough':['面值至少为 1，任何合法解的枚数不超过 amount，所以 amount+1 是安全的整数哨兵。','不可达值加一会更大，min 不会把它误认为更优；无需单独判断每个来源是否可达。','这里求最少枚数，多种排列指向相同数值不影响 min。若变成“组合数量”，外层与内层的循环顺序会影响是否重复计数，不能机械照搬。'],
 'code':'''
class Solution:
    def coinChange(self, coins: list[int], amount: int) -> int:
        # amount+1 超过任何可能的最少硬币数，用作不可达哨兵。
        unreachable = amount + 1
        dp = [unreachable] * (amount + 1)
        # 凑出金额 0 不需要硬币，这是后续所有转移的起点。
        dp[0] = 0
        # 先算小金额，再尝试最后使用哪一枚硬币，允许同种币多次使用。
        for total in range(1, amount + 1):
            for coin in coins:
                if coin <= total:
                    # 在凑出 total-coin 的最少枚数上再加一枚当前硬币。
                    dp[total] = min(dp[total], dp[total - coin] + 1)
        # 若最终仍是哨兵值，说明该金额无法被凑出。
        return -1 if dp[amount] == unreachable else dp[amount]
'''.strip(),
 'code_notes':['数组含金额 0，因此长度是 amount+1。','先检查 coin<=total，防止负下标被 Python 当作从尾部访问。','amount=0 时主循环为空，直接返回 dp[0]=0。'],
 'pitfalls':['使用未经证明的最大面值贪心。','其余 dp 初始化为 0，误认为所有金额已能免费凑出。','缺少面值范围检查，发生负下标访问。','把无限次使用误写成每枚一次。'],
 'complexity':'设金额 A、面值数 k，时间 O(Ak)，额外空间 O(A)。',
 'quiz':{'question':'为什么 [1,3,4] 凑 6 不能只尝试最后一枚 4？','answer':'最后用 4 需要前面再凑 2，共三枚；最后用 3 可接一个 3，只需两枚。最大面值不保证最少枚数。'},
 'tests':checks('coinChange',[([[1,3,4],6],2),([[1,2,5],11],3),([[2],3],-1),([[1],0],0),([[2147483647],2],-1)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':279,'slug':'perfect-squares',
 'summary':'用若干正完全平方数之和表示 n，平方数允许重复，求最少项数。例如 12=4+4+4，需要 3 项。',
 'baseline':'总取不超过剩余值的最大平方数不可靠：12 先取 9 会留下 1+1+1，共四项。可以把 1、4、9…视为 322 中允许无限使用的面值，比较全部选择。',
 'insight':'dp[t] 表示凑出整数 t 的最少平方数项数。最后一项是 q² 时，候选为 dp[t-q²]+1。把所有不超过 n 的正平方数预先生成，再按目标值递增计算。',
 'steps':['生成 1² 到 floor(sqrt(n))²。','dp[0]=0，其余先设为 n+1。','枚举 total=1..n，再枚举不大于 total 的平方数。','取所有 dp[total-square]+1 的最小值，返回 dp[n]。'],
 'invariant':'任何 total 的表示都能按最后一个平方数分类，去掉它得到更小总和；相反，可行的较小总和加上该平方数得到合法表示。由于 1 始终可用，每个非负总和都可达，转移得到的有限最小值是准确答案。',
 'examples':[{'label':'较小平方数的重复可能更省','input':'n=12','output':'3','frames':[
  {'title':'候选平方数为 1、4、9','note':'不是枚举任意正整数，也不把 0 放进候选，因为 0 不会减少剩余量。','array':[1,4,9]},
  {'title':'凑 12 时比较三个来源','note':'来源状态已算出：dp[11]=3，dp[8]=2，dp[3]=3。最后选 4 时最好。','table':{'headers':['最后平方数','剩余','总项数'],'rows':[[1,11,4],[4,8,3],[9,3,4]]}},
  {'title':'三份 4 达到最优','note':'候选没有使用次数上限，4 可以被选三次。','array':[4,4,4],'active':[0,1,2],'metrics':[['总和',12],['项数',3]]}
 ]}],
 'walkthrough':['这道题的新增工作只是生成合法“面值”，最少项数转移与零钱兑换一致。','平方数按递增生成，一旦 square>total，后面都更大，可以 break。','若 n 本身是平方数，来源 dp[0]+1 会使答案为 1，不需要专门提前返回。'],
 'code':'''
from math import isqrt

class Solution:
    def numSquares(self, n: int) -> int:
        # 一个平方数就够时，答案已经最小；isqrt 返回精确整数平方根。
        root = isqrt(n)
        if root * root == n:
            return 1
        # 四平方和定理保证答案至多为 4。
        # 去掉所有因子 4 后，若余数形如 8b+7，则必须用 4 个。
        reduced = n
        while reduced % 4 == 0:
            reduced //= 4
        if reduced % 8 == 7:
            return 4
        # 枚举第一个平方数，精确检查剩余数是不是另一个平方数。
        for first in range(1, root + 1):
            remaining = n - first * first
            second = isqrt(remaining)
            if second * second == remaining:
                return 2
        # 已排除 1、2、4；按三平方和定理，此时恰好需要 3 个。
        return 3

    def numSquaresDP(self, n: int) -> int:
        # 对照 DP：预先列出不超过 n 的平方数，后续视为可重复使用的硬币。
        squares = [value * value for value in range(1, isqrt(n) + 1)]
        dp = [n + 1] * (n + 1)
        # 和为 0 时使用 0 个平方数，为转移提供起点。
        dp[0] = 0
        for total in range(1, n + 1):
            for square in squares:
                # 平方数已按升序列出，超过当前和后可直接停止本轮枚举。
                if square > total:
                    break
                # 最后取 square 时，总个数等于剩余和的最优个数加一。
                dp[total] = min(dp[total], dp[total - square] + 1)
        return dp[n]
'''.strip(),
 'api':{'signature':'math.isqrt(n) -> floor(sqrt(n))','description':['直接返回精确整数平方根，避免浮点开方再取整的精度顾虑。','range 的右边界加 1，使 n 为完全平方数时不会漏掉它自己。']},
 'code_notes':['默认 numSquares 使用数论分类；numSquaresDP 保留原来的完全背包转移。', '三平方和定理说明：非负整数能写成三个平方数之和，当且仅当不形如 4^a(8b+7)。允许平方数为 0，所以还要单独排除只需 1 或 2 个的情况。', 'isqrt 返回向下取整的精确整数根，再检查 root*root==n，避免浮点误差。'],
 'pitfalls':['每次取最大平方数。','生成平方数时漏掉等于 n 的情况。','把平方数只能使用一次。','把开方后的数 q 而不是 q² 加入候选。'],
 'complexity':'数论方法枚举 O(√n) 个候选并调用整数平方根；在题目整数范围的常用分析下时间 O(√n)、辅助空间 O(1)。若分析任意大整数，还需计入 isqrt 与乘除的位复杂度。对照 DP 时间 O(n√n)、空间 O(n)。',
 'quiz':{'question':'n=13 时，最后选 9 对应哪个旧状态？','answer':'对应 dp[4]，4 本身是一项平方数，因此 dp[4]+1=2，表示 4+9。'},
 'tests':checks('numSquares',[([12],3),([13],2),([1],1),([16],1),([7],4)])
,
 'submission': {'name': '平方数定理与精确平方根', 'why': '默认采用数论判定，依赖四平方和定理与三平方和定理；它不从普通 DP 转移直接推出来。numSquaresDP 保留无需数论前提的动态规划对照。', 'steps': ['先判断 n 是否本身就是完全平方数，答案为 1。', '不断除去因子 4，若剩下的数模 8 为 7，则不能由三个平方数表示，答案为 4。', '枚举一个平方数，若剩余也是平方数则答案为 2；否则答案为 3。'], 'diagram': '12：不是平方，去掉因子 4 得 3，非 8b+7\n无法拆成两个平方 → 4+4+4，答案 3\n7：7 mod 8 = 7 → 必须四个平方，答案 4'},
})

CHAPTER['problems'].append({
 'id':416,'slug':'partition-equal-subset-sum',
 'summary':'把正整数数组中的每个元素分到两个子集，使两边总和相同，判断是否可行。每个下标对应一件独立元素，即使值相同，也只能使用该下标一次。',
 'baseline':'枚举每个元素放在哪边有 2^n 种方案。两边等和意味着只需找总和一半的子集；如果总和为奇数，可以直接排除。',
 'insight':'令 target=sum(nums)//2，reachable[t] 表示用已经处理的元素能否恰好凑出 t。加入 x 时可不选它，或从旧 reachable[t-x] 选它一次。压成一行后，容量 t 必须倒序，才能读取尚未用过本轮 x 的旧值。',
 'steps':['总和为奇数则 False。','reachable[0]=True，其他容量为 False。','每个 x 遍历容量 target、target-1…x。','更新 reachable[t]=reachable[t] or reachable[t-x]。','返回 reachable[target]。'],
 'invariant':'处理 x 前，每格只使用此前元素。倒序更新 t 时，更小的 t-x 尚未在本轮更新，仍是旧轮值，因此从它转移最多加入当前 x 一次；原 reachable[t] 对应不选 x。两类合并后恰好包含所有已处理元素的可达子集和。',
 'examples':[{'label':'一个下标只能使用一次','input':'nums=[1,2,5]','output':'False','frames':[
  {'title':'目标为总和的一半 4','note':'容量 0 由空集实现，其他容量初始不可达。','table':{'headers':['容量',0,1,2,3,4],'rows':[['初始','T','F','F','F','F']]}},
  {'title':'处理 1 时倒序扫描','note':'先看 4、3、2，它们的旧来源都为 False；最后才把容量 1 标为 True。不会把这个 1 连续用四次。','table':{'headers':['容量',0,1,2,3,4],'rows':[['使用前','T','F','F','F','F'],['处理 1 后','T','T','F','F','F']]}},
  {'title':'处理 2 后仍无法凑出 4','note':'新增 2 和 1+2=3。最后的 5 超过目标，不能加入任何容量，因此答案 False。','table':{'headers':['容量',0,1,2,3,4],'rows':[['处理 2 后','T','T','T','T','F'],['处理 5 后','T','T','T','T','F']]}}
 ]},{'label':'相同值可来自不同元素','input':'nums=[1,5,11,5]','output':'True','frames':[
  {'title':'两边都能得到 11','note':'可以取单独的 11，剩下 1、5、5 总和也是 11；两个 5 是不同下标。','array':[1,5,11,5],'active':[2],'metrics':[['一边',11],['另一边','1+5+5=11']]}
 ]}],
 'walkthrough':['只需找到一边：所有元素总和为 2×target，选中一边为 target，剩余元素必为 target。','若正序容量更新，处理 x=1 时先产生 reachable[1]，接着又拿这个新值产生 reachable[2]，就把同一元素重复使用，变成完全背包语义。','x>target 时 range(target,x-1,-1) 为空，正确跳过它；这只说明它不能属于正在构造的一边。'],
 'code':'''
class Solution:
    def canPartition(self, nums: list[int]) -> bool:
        # 等分等价于能否选出总和的一半；总和为奇数时直接失败。
        # 总和为奇数就无法等分；否则只需判断能否选出一半总和。
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        reachable = 1  # 第 c 位为 1 表示和 c 可达；初始只有和 0 可达。
        mask = (1 << (target + 1)) - 1
        for value in nums:
            # 原状态表示不选 value，左移后的状态表示每个旧可达和加上 value。
            # 右侧一次性使用旧 reachable，因此同一个元素只会选一次。
            reachable = (reachable | (reachable << value)) & mask
            if (reachable >> target) & 1:
                return True
        return False

    def canPartitionDP(self, nums: list[int]) -> bool:
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        # 对照背包 DP：reachable[c] 表示用已经处理的元素能否凑出和 c。
        reachable = [False] * (target + 1)
        reachable[0] = True
        for x in nums:
            # 必须倒序更新，确保每个元素只用一次，不能在同一轮反复选择。
            for capacity in range(target, x - 1, -1):
                reachable[capacity] = reachable[capacity] or reachable[capacity - x]
        return reachable[target]
'''.strip(),
 'code_notes':['默认使用整数位集合，canPartitionDP 对应前面的布尔数组倒序转移。', 'mask 丢弃超过 target 的位；原题元素均为正数，超过目标的和不会再减回目标。', '位移与按位或在 Python 大整数上按位数花费成本，不应声称每个数只需真正的 O(1) 时间。'],
 'pitfalls':['总和奇数仍向下取整后求子集。','容量正序导致重复使用当前元素。','用 set(nums) 去重，丢掉可分别选择的重复值。','把能凑出不超过 target 当成恰好 target。'],
 'complexity':'位集合的长度为 target+1 位，设机器字宽为 w，主要位运算时间约 O(n·⌈target/w⌉)、空间 O(target/w) 个机器字；Python 大整数位运算不是 O(1)。布尔数组对照方法时间 O(n·target)、空间 O(target)。',
 'quiz':{'question':'为什么处理一个 2 时不能从本轮刚得到的 reachable[2] 再得到 reachable[4]？','answer':'那相当于把同一个下标的 2 选了两次。倒序读取旧轮来源，保证本轮最多用一次。'},
 'tests':checks('canPartition',[([[1,2,5]],False),([[1,5,11,5]],True),([[1,2,3,5]],False),([[2,2]],True),([[1]],False)],preserve_args=[0])
,
 'submission': {'name': '整数位集合压缩 0/1 背包', 'why': 'Python 大整数可把一整行布尔状态放进二进制位。转移仍是选或不选当前数，利用位移在底层批量更新，canPartitionDP 保留倒序背包数组对照。', 'steps': ['最低位设为 1，代表空集可以凑出 0。', '左移 value 位，表示每个旧可达和都加上 value。', '与旧状态按位或，保留选与不选两种情况，最后检查 target 位。'], 'diagram': '旧状态：和 0、2 可达\n读到 3：新增和 3、5\n合并后：和 0、2、3、5 可达'},
})

CHAPTER['problems'].append({
 'id':139,'slug':'word-break',
 'summary':'判断 s 能否完全拆成字典中的若干单词，允许同一单词重复使用。每段必须连续，所有段按原顺序覆盖整个字符串。',
 'baseline':'枚举所有切分点可能有 2^(n-1) 种方案，很多分支到达同一个前缀位置后会重复探索后缀。总优先匹配最长单词也可能把剩余字符串逼入死路。',
 'insight':'dp[end] 表示前缀 s[:end] 能否拆分。枚举最后一段的起点 start，只要 dp[start] 为 True 且 s[start:end] 在字典中，当前前缀就可达。最后一段长度不会超过字典最长词 L，因此只需看最近 L 个起点。',
 'steps':['字典转成集合 words，计算最长词长度 L。','dp[0]=True，表示空前缀已成功拆完。','依次计算 end=1..n。','枚举 start=max(0,end-L)..end-1，找到一个合法来源即置 True 并 break。','返回 dp[n]，只有整个字符串拆完才成功。'],
 'invariant':'任意成功拆分的非空前缀都有最后一个单词。删去它后，剩余前缀必须可拆；反之，可拆前缀加一个字典单词得到合法更长前缀。所有字典词非空，来源 start<end，因此按 end 递增不存在循环依赖。',
 'examples':[{'label':'最长匹配可能走进死路','input':'s="cars", wordDict=["car","ca","rs"]','output':'True','frames':[
  {'title':'最长词 car 留下无法匹配的 s','note':'贪心只选 car 会失败，但不能据此宣布不存在其他拆法。','diagram':'cars\n├─ car | s  → s 不在字典\n└─ ca  | rs → 两段都在字典'},
  {'title':'保存所有可达前缀位置','note':'长度 2 的 ca 和长度 3 的 car 都可达，后续分别继续尝试。','table':{'headers':['前缀长度',0,1,2,3,4],'rows':[['前缀','空','c','ca','car','cars'],['dp','T','F','T','T','T']]}},
  {'title':'最后一段 rs 接到可达 ca 后','note':'start=2，dp[2]=True，s[2:4]="rs" 在字典，故 dp[4]=True。','array':list('cars'),'active':[2,3],'metrics':[['已拆前缀','ca'],['最后一段','rs']]}
 ]},{'label':'同一词允许再次使用','input':'s="applepenapple", wordDict=["apple","pen"]','output':'True','frames':[
  {'title':'重复使用 apple 不需要消耗字典项','note':'字典是可用词集合，不是每词只能拿一次的物品。','diagram':'apple | pen | apple\n  0→5    5→8    8→13'}
 ]}],
 'walkthrough':['dp 的下标是前缀长度，也就是切分线位置，所以有 n+1 个状态，最后答案位于 dp[n]。','dp[start] 为 False 时不必创建切片；and 的短路求值跳过无效来源。','已找到一个来源即可 break，因为本题只判存在性，不计拆分数量，也不返回所有方案。','Python 的字符串切片会创建子串，首次集合查询还需要对子串计算散列。每个候选长度至多 L，不能忽略这部分成本。'],
 'code':'''
class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        # 对照切片 DP：集合加速单词查询，最长单词长度限制需要尝试的起点范围。
        words = set(wordDict)
        longest = max(map(len, wordDict))
        dp = [False] * (len(s) + 1)
        # 空前缀可被拆分，后续第一个单词才能从这里接上。
        dp[0] = True
        for end in range(1, len(s) + 1):
            for start in range(max(0, end - longest), end):
                # 只有前缀已经可拆分，而且接上的一段是完整单词，终点才可达。
                if dp[start] and s[start:end] in words:
                    dp[end] = True
                    break
        return dp[-1]
'''.strip(),
 'api':{'signature':'s[start:end]；set(wordDict)','description':['切片包含 start，不包含 end，正好对应两个切分线之间的最后一段。','集合用于平均快速成员查询，但字符串长度相关的切片和散列成本仍存在。字典由题目保证非空，max 可直接使用。']},
 'code_notes':['最长词限制只剪掉不可能出现在字典里的长片段，不丢失合法拆分。','dp[-1] 就是 dp[len(s)]，不是原字符串最后字符的位置。','集合不会在使用单词后删除它，允许重复匹配。'],
 'pitfalls':['用最长词优先贪心代替所有可达前缀。','把 dp[0] 设为 False，导致任何第一段都无来源。','只找到某个可拆前缀就返回成功，没有覆盖全串。','把使用过的单词从字典删除。'],
 'complexity':'设字符串长 n、最长词长 L、字典词数 D、字典字符总数 S。平均时间 O(S+nL²)，计入子串切片和散列；额外空间 O(n+D+L)，集合保存已有字符串引用，临时子串最长 L。',
 'quiz':{'question':'s="cars" 时 dp[3]=True，为什么仍要保留 dp[2]？','answer':'car 留下的 s 无法匹配，但 ca 后可以接 rs；不同切分线有不同后续机会，不能只保留最长可达前缀。'},
 'tests':checks('wordBreak',[(['cars',['car','ca','rs']],True),(['leetcode',['leet','code']],True),(['applepenapple',['apple','pen']],True),(['catsandog',['cats','dog','sand','and','cat']],False),(['a',['b']],False)],preserve_args=[1])
})

CHAPTER['problems'].append({
 'id':62,'slug':'unique-paths',
 'summary':'机器人从 m×n 网格左上角到右下角，每次只能向右或向下，求不同路径数量。没有障碍，也不能回头。',
 'baseline':'逐条枚举路径会多次来到同一个格子；该格子的后续选择与此前路线无关。可以把所有到达方式的数量存到一个状态，再传递给后续位置。',
 'insight':'ways[r][c] 表示到格子 (r,c) 的路径数。最后一步来自上方或左方，两类互斥，所以相加。首行只能一路向右，首列只能一路向下，都为 1；压成一行后 dp[c] 是上方，dp[c-1] 是刚更新的左方。',
 'steps':['用 n 个 1 初始化 dp，代表首行各格的唯一走法。','从第 1 行开始逐行处理。','每行从 c=1 到 n-1 更新 dp[c]+=dp[c-1]，首列保持 1。','返回 dp[n-1]。'],
 'invariant':'计算一行的列 c 前，dp[c] 仍是上一行同列的路径数，dp[c-1] 已是本行左格的路径数。两者相加对应最后一步方向的完整分类；从左往右更新确保两个来源含义正确。',
 'examples':[{'label':'一行数组保存上下两代状态','input':'m=3, n=3','output':'6','frames':[
  {'title':'首行和首列各只有一种走法','note':'起点的一种空移动路线使首行、首列都能延续为 1。','grid':[[1,1,1],[1,'?','?'],[1,'?','?']],'active_cells':[[0,0],[0,1],[0,2],[1,0],[2,0]]},
  {'title':'从上方与左方相加','note':'中心为 1+1=2，第二行最右为上方 1 加左方 2，得到 3。','grid':[[1,1,1],[1,2,3],[1,'?','?']],'active_cells':[[1,1],[1,2]]},
  {'title':'终点共有 3+3=6 条','note':'完整表只用于讲解；代码最终一行 dp=[1,3,6] 已足够。','grid':[[1,1,1],[1,2,3],[1,3,6]],'active_cells':[[2,2]]}
 ]}],
 'walkthrough':['方向限制让依赖图没有环，按行从上到下、列从左到右就能完成。','单行或单列都只有一种路径；m=1 时外循环为空，n=1 时内循环为空。','m=n=1 已经位于终点，不走任何一步也是一种合法路径，因此答案是 1。'],
 'code':'''
from math import comb

class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        # 任一路径都恰好向下 m-1 步、向右 n-1 步。
        # 在总共 m+n-2 个位置里选择哪些步向下，每种选择唯一对应一条路径。
        # math.comb 返回精确整数，避免用阶乘相除产生浮点误差。
        return comb(m + n - 2, min(m - 1, n - 1))

    def uniquePathsDP(self, m: int, n: int) -> int:
        # 对照网格 DP：第一行只有一直向右这一种走法。
        dp = [1] * n
        for r in range(1, m):
            for c in range(1, n):
                # 更新前 dp[c] 是上方，更新后的 dp[c-1] 是左方，两者走法相加。
                dp[c] += dp[c - 1]
        return dp[-1]
'''.strip(),
 'code_notes':['默认 uniquePaths 使用 math.comb；uniquePathsDP 对应前面的网格状态推导。', 'comb(n,k) 返回整数，直接按组合数定义计数；不通过浮点除法计算。', '此优化依赖网格无障碍，障碍会破坏“任意步序都合法”的条件。'],
 'pitfalls':['用 min 或 max 合并来源，混淆计数与最优化。','首行初始化为零，所有后续状态跟着归零。','压缩后倒序更新列，读取到上一行左格而非当前左格。'],
 'complexity':'组合计数直接计算 C(m+n-2,min(m-1,n-1))，无需访问 m×n 网格；具体时间与大整数乘除实现有关，不将库调用记为 O(1)。对照滚动 DP 时间 O(mn)、空间 O(n)。',
 'quiz':{'question':'3×1 的网格为何不需要进入列更新循环？','answer':'只有首列，唯一走法是持续向下；初始 dp=[1] 已能沿每行保持正确答案。'},
 'tests':checks('uniquePaths',[([3,3],6),([3,7],28),([1,1],1),([1,9],1),([8,1],1)])
,
 'submission': {'name': '精确组合计数', 'why': '无障碍网格中，所有合法路径的步数与两种方向数量都相同，可以直接计数，不必扫描整张网格。有障碍的第 63 题不能沿用这个公式。', 'steps': ['总步数为 m+n-2，其中 m-1 步向下。', '选出这些向下步骤的位置，其他位置全部向右。', '用 Python 3.12 的 math.comb 精确计算组合数。'], 'diagram': '3×3 网格：共 4 步，任选 2 步向下\nDDRR、DRDR、DRRD、RDDR、RDRD、RRDD → 6 条'},
})

CHAPTER['problems'].append({
 'id':63,'slug':'unique-paths-ii',
 'summary':'在 62 的网格中加入障碍，0 可通过、1 不可通过，仍只能向右或向下。返回到终点的路径数，起点或终点被堵时答案为 0。',
 'baseline':'直接使用“首行首列都为 1”的初始化会忽略障碍后方已无法到达的格子。需要让每个障碍主动截断路径传播，首行首列也遵守这个规则。',
 'insight':'沿用一行路径计数：遇到障碍就令 dp[c]=0，否则将上方 dp[c] 与左方 dp[c-1] 相加。先只令 dp[0]=1，相当于给起点一个虚拟来源，再从第一个格子开始统一处理。',
 'steps':['dp 为 n 个零，只设置 dp[0]=1。','逐行逐列扫描包括起点在内的每格。','若障碍为 1，直接把 dp[c] 清零。','否则 c>0 时执行 dp[c]+=dp[c-1]；首列只保留上方来源。','返回末列状态。'],
 'invariant':'障碍格没有任何合法到达路径，状态必须为零。非障碍格的合法路径按最后一步来自上或左分类；压缩数组分别保留这两个方向的正确计数。起点的虚拟 1 会在起点被堵时清除，也会被后续首行/首列障碍阻断。',
 'examples':[{'label':'障碍清零，阻断向后传播','input':'obstacleGrid=[[0,0,0],[0,1,0],[0,0,0]]','output':'2','frames':[
  {'title':'中间格不可通过','note':'此图是原始障碍网格，1 表示墙；后续图展示的是路径计数。','grid':[[0,0,0],[0,1,0],[0,0,0]],'active_cells':[[1,1]]},
  {'title':'中间的路径计数归零','note':'第二行最右只能从上方到达，不能穿过中间障碍，所以计数为 1。','grid':[[1,1,1],[1,0,1],['?','?','?']],'active_cells':[[1,1],[1,2]]},
  {'title':'终点由两侧各一条汇合','note':'沿上边再向下，或沿左边再向右，共两条。','grid':[[1,1,1],[1,0,1],[1,1,2]],'active_cells':[[2,2]]}
 ]},{'label':'首行障碍后方不可达','input':'obstacleGrid=[[0,1,0]]','output':'0','frames':[
  {'title':'不能把整条首行预先设为 1','note':'中间清零后，右格既无上方来源，也无左方路径，仍为零。','table':{'headers':['列',0,1,2],'rows':[['障碍',0,1,0],['路径数',1,0,0]]}}
 ]}],
 'walkthrough':['障碍时必须赋零，不能只是 continue；dp[c] 原来保存上方路径，直接跳过会让这些路径穿墙。','首列没有左邻居，不相加；如果首列遇到障碍，它下方的首列也持续为零。','输入和 DP 表含义不同：原网格里的 1 是障碍，计数表里的 1 是一条路径，图中逐步注明了这一区别。'],
 'code':'''
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: list[list[int]]) -> int:
        n = len(obstacleGrid[0])
        dp = [0] * n
        # 把起点外的虚拟入口设为一种走法；若起点有障碍，第一轮会清零。
        dp[0] = 1
        for row in obstacleGrid:
            for c in range(n):
                # 障碍格无法经过，必须把此前上方贡献也清零。
                if row[c] == 1:
                    dp[c] = 0
                elif c > 0:
                    # 非障碍格的走法来自上方旧值与左方新值。
                    dp[c] += dp[c - 1]
        return dp[-1]
'''.strip(),
 'code_notes':['不需要提前单独判断起点、终点，障碍分支已统一处理。','遍历 row 只读取输入，不把计数覆盖回障碍网格。','elif 确保清零的障碍格不会再加上左侧路径。'],
 'pitfalls':['障碍格只跳过、不清除旧状态。','首行首列无条件初始化为 1。','清零后仍执行相加，让墙重新出现路径。'],
 'complexity':'时间 O(mn)，额外空间 O(n)。题目保证答案不超过 2×10^9。',
 'quiz':{'question':'起点是障碍时，初始 dp[0]=1 会不会产生一条假路径？','answer':'不会。处理起点时障碍分支立即把它清零，后续所有格子都失去可达来源。'},
 'tests':checks('uniquePathsWithObstacles',[([[[0,0,0],[0,1,0],[0,0,0]]],2),([[[0,1,0]]],0),([[[1]]],0),([[[0]]],1),([[[0,0],[0,1]]],0)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':64,'slug':'minimum-path-sum',
 'summary':'从非负权值网格左上到右下，只能向右或向下，求路径经过的所有格子之和的最小值，包括起点与终点。',
 'baseline':'只挑下一格较小值的贪心可能走向后续高代价区域；枚举所有路径又会重复考虑相同终点。需要比较到每个格子的完整前缀代价，而非只比较相邻格子的值。',
 'insight':'cost[r][c] 是到当前格子的最小累计和。最后来自上方或左方，取两者较小代价再加当前格值。压成一行时保持上方旧值与左方新值；不存在的来源用正无穷排除。',
 'steps':['dp 初始全为正无穷，仅 dp[0]=0，作为起点的虚拟零代价来源。','逐行从左到右处理格子。','above=dp[c]，left=dp[c-1]（首列则为正无穷）。','dp[c]=min(above,left)+grid[r][c]。','返回末列状态。'],
 'invariant':'固定最后进入方向后，当前格值对所有候选相同，因此该方向只需保留最小前缀代价。两方向取最小不遗漏最优路径；边界的正无穷禁止从网格外“免费进入”，唯一起点虚拟来源负责开启计算。',
 'examples':[{'label':'累计代价不能只看下一格','input':'grid=[[1,3,1],[1,5,1],[4,2,1]]','output':'7','frames':[
  {'title':'原网格的格子代价','note':'路径需要把经过的全部格值相加，不只是终点值。','grid':[[1,3,1],[1,5,1],[4,2,1]]},
  {'title':'每格记录完整前缀最小和','note':'中心为 min(4,2)+5=7；右中为 min(5,7)+1=6。','grid':[[1,4,5],[2,7,6],[6,8,7]],'active_cells':[[1,1],[1,2],[2,2]]},
  {'title':'沿上边再向下实现 7','note':'起点下方的 1 看起来比右方 3 小，但直接贪选下方并不能保证全局最优。','grid':[[1,3,1],[1,5,1],[4,2,1]],'active_cells':[[0,0],[0,1],[0,2],[1,2],[2,2]],'metrics':[['路径和','1+3+1+1+1=7']]}
 ]}],
 'walkthrough':['首行除了起点，above 都为无穷，因此只能从左累计；首列 left 为无穷，因此只能从上累计。','起点会计算 min(0,∞)+grid[0][0]，确保起点本身被算一次。','虽然只用一行数组，图中完整二维表更容易理解来源。每次更新后不再需要该格旧的上方值，所以可以覆盖。'],
 'code':'''
class Solution:
    def minPathSum(self, grid: list[list[int]]) -> int:
        n = len(grid[0])
        # 不可达位置用正无穷，防止越界一侧被错误当成零成本。
        dp = [float('inf')] * n
        # 起点之前的虚拟成本为 0，第一格会加上自己的值。
        dp[0] = 0
        for row in grid:
            for c in range(n):
                # 当前位置只能从上方或左方进入；第一列没有左邻居。
                left = dp[c - 1] if c > 0 else float('inf')
                # 更新前 dp[c] 是上一行的成本，选更小入口再加当前格成本。
                dp[c] = min(dp[c], left) + row[c]
        return dp[-1]
'''.strip(),
 'code_notes':['每格至少存在一条从起点沿上/左前缀到达的有效路线，完成后 dp 中相关值为整数。','不改 grid，方便调用者保留原始代价网格。','首列单独排除左邻居，避免 Python 负下标读取末列。'],
 'pitfalls':['用相邻格值大小作贪心决策。','dp 全初始化为 0，让首行任意位置获得虚假的零代价上方来源。','忘记加当前格，或起点重复计入。'],
 'complexity':'时间 O(mn)，额外空间 O(n)。',
 'quiz':{'question':'为什么首列的 left 要用无穷，而不是 0？','answer':'首列没有左侧来源。设为 0 等于允许从网格外免费进入任意行，会遗漏此前累计代价。'},
 'tests':checks('minPathSum',[([[[1,3,1],[1,5,1],[4,2,1]]],7),([[[1,2,3],[4,5,6]]],12),([[[5]]],5),([[[0,0]]],0),([[[1],[2],[3]]],6)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':221,'slug':'maximal-square',
 'summary':'在由字符 "0"、"1" 组成的矩阵中，找全部为 "1" 的最大正方形，返回面积。格子是字符串字符，不是整数。',
 'baseline':'枚举左上角和边长，再扫描内部所有格子会重复检查大量区域。固定右下角后，一个大正方形必须同时得到上方、左方、左上方的足够大正方形支撑。',
 'insight':'side[r][c] 表示以该格为右下角的全 1 正方形最大边长。若格值为 0 则为 0；若为 1，则为 1+min(上、左、左上)。保存全局最大边长，最后平方。',
 'steps':['一行 dp 长 n+1，最左额外位置为零，统一首列边界。','每行开始 diagonal=0，表示网格外的旧左上角。','更新列 c 前保存 above=dp[c]。','遇到 "1" 则 dp[c]=min(above,dp[c-1],diagonal)+1，否则 dp[c]=0。','更新最大边长，再令 diagonal=above，为下一列保留旧左上角。'],
 'invariant':'若当前能形成边长 k 的正方形，去掉最下行、最右列后，上、左、左上三个对应区域都至少支持 k-1，因此它们的最小值给出上限。反过来，三个边长 t 的全 1 区域加当前 1 能覆盖边长 t+1 的整个正方形，所以上限可达到。',
 'examples':[{'label':'最薄弱的邻居限制扩张','input':'matrix=[list("011"),list("111"),list("111")]','output':'4','frames':[
  {'title':'左上角的零阻止 3×3','note':'list("011") 表示字符列表 ["0","1","1"]。其余八格虽为 1，整个矩阵也不是全 1 正方形。','grid':[['0','1','1'],['1','1','1'],['1','1','1']],'active_cells':[[0,0]]},
  {'title':'边长状态由三个方向的最小值决定','note':'右下角上方=2、左方=2、左上=1，所以只得 min(2,2,1)+1=2。','grid':[[0,1,1],[1,1,2],[1,2,2]],'active_cells':[[1,2],[2,1],[1,1],[2,2]]},
  {'title':'返回面积 2²=4','note':'例如右下的 2×2 全为 1。最大边长状态不一定出现在最后一格，因此另外维护 best。','grid':[['0','1','1'],['1','1','1'],['1','1','1']],'active_cells':[[1,1],[1,2],[2,1],[2,2]],'metrics':[['边长',2],['面积',4]]}
 ]}],
 'walkthrough':['只取上、左会忽略内部左上缺口；取 max 会忽略最短的限制方向，均可能构造出不存在的大正方形。','压缩后 dp[c-1] 已经是本行左方，旧左上必须另存 diagonal，不能再从 dp[c-1] 取。','above 在更新前保存，更新后再交给 diagonal。即使当前格为零，也要推进 diagonal，使下一列仍获得正确旧值。','padding dp[0]=0 永不覆盖，每行 diagonal 又从 0 开始，因此首行首列自然最多形成边长 1。'],
 'code':'''
class Solution:
    def maximalSquare(self, matrix: list[list[str]]) -> int:
        n = len(matrix[0])
        # 多留一格哨兵处理左边界，dp[c] 存以对应格为右下角的最大正方形边长。
        dp = [0] * (n + 1)
        best = 0
        for row in matrix:
            diagonal = 0
            for c in range(1, n + 1):
                # 覆盖当前列之前先保存上方旧值，下一列要把它作为左上角。
                above = dp[c]
                if row[c - 1] == '1':
                    # 当前为 1 时，上、左、左上三边都必须支持扩展，因此取最小值加一。
                    dp[c] = min(above, dp[c - 1], diagonal) + 1
                    best = max(best, dp[c])
                else:
                    dp[c] = 0
                # 左上角只在更新当前格之后前进，不能提前覆盖。
                diagonal = above
        # 题目返回面积，DP 记录的是边长，最后需要平方。
        return best * best
'''.strip(),
 'code_notes':['DP 列 c 对应原矩阵列 c-1，额外零列只负责边界。','比较字符 "1"；若误用整数 1，所有格子都会走清零分支。','返回 best*best，把边长转成面积。'],
 'pitfalls':['用 max 代替 min，或者漏掉左上来源。','更新后再保存 above，误把新值当旧对角线。','遇到零不清除旧 dp[c]。','只返回最后一格或返回边长。'],
 'complexity':'时间 O(mn)，额外空间 O(n)。',
 'quiz':{'question':'上、左边长都是 2，左上只有 1，当前格为 1，最大边长是多少？','answer':'是 2。左上缺口使边长 3 的内部无法保证全 1，必须取三个方向的最小值再加 1。'},
 'tests':checks('maximalSquare',[([[list('011'),list('111'),list('111')]],4),([[list('10100'),list('10111'),list('11111'),list('10010')]],4),([[['0']]],0),([[['1']]],1),([[list('11'),list('11')]],4)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':1143,'slug':'longest-common-subsequence',
 'summary':'求两个字符串的最长公共子序列长度。允许分别跳过字符，但必须保持各自在原串中的相对顺序，不要求连续。',
 'baseline':'枚举一个字符串所有子序列，再检查是否出现在另一个中，会产生指数数量。用两个前缀长度定位子问题，可避免重复考虑同一对剩余范围。',
 'insight':'dp[i][j] 表示 text1[:i] 与 text2[:j] 的 LCS 长度。末字符相等时配对，取 dp[i-1][j-1]+1；不等时不可能把这两个末字符作为同一对，至少舍弃其中一边末尾，取上方与左方的较大值。',
 'steps':['创建 (m+1)×(n+1) 零表，首行首列表示一边为空。','从 i=1、j=1 开始递增填表。','若 text1[i-1]==text2[j-1]，用左上+1。','否则用 max(dp[i-1][j],dp[i][j-1])。','返回 dp[m][n]。'],
 'invariant':'末字符不等时，任何公共序列至少不使用其中一边末字符，两个缩短前缀的状态覆盖全部可能。末字符相等时，可以取一个把这对末字符配在一起的最优方案：若原方案最后的该字符使用了更早位置，可把匹配向后移动，不影响此前顺序；去掉末配对后剩余最优长度就是左上状态。',
 'examples':[{'label':'允许跨过不匹配字符','input':'text1="abcde", text2="ace"','output':'3','frames':[
  {'title':'状态下标是前缀长度','note':'空前缀与任何前缀的公共子序列都只有长度 0。表中行表示 text1 的前缀，列表示 text2 的前缀。','table':{'headers':['前缀','空','a','ac','ace'],'rows':[['空',0,0,0,0],['a',0,1,1,1],['ab',0,1,1,1]]}},
  {'title':'相等接左上，不等沿上或左保留','note':'读到 c 与 c 相等，接在 a 后得到 2；d 不匹配也不会清零，因为允许跳过 d。','table':{'headers':['前缀','空','a','ac','ace'],'rows':[['abc',0,1,2,2],['abcd',0,1,2,2],['abcde',0,1,2,3]]}},
  {'title':'公共序列 ace 长度为 3','note':'在第一串跳过 b、d；第二串所有字符均保留，顺序一致。','panels':[{'heading':'text1','array':list('abcde'),'active':[0,2,4]},{'heading':'text2','array':list('ace'),'active':[0,1,2]}]}
 ]}],
 'walkthrough':['dp[i][j] 描述两个完整前缀的最优值，不强制公共序列以它们的末字符结尾，因此不相等时可以保留上方或左方结果。','匹配判断要用 i-1、j-1，因为状态多了空前缀这一行和一列。','首行首列作为边界，转移时无须单独处理越界或空串来源。','本解保留完整二维表以对应推导；如果只求长度，可像 221 那样保存旧左上值压成一行，但还原一条公共序列通常需要额外路径信息。'],
 'code':'''
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        # 把较短字符串放在列上，DP 数组只需要 O(min(m,n)) 空间。
        if len(text1) < len(text2):
            text1, text2 = text2, text1
        dp = [0] * (len(text2) + 1)
        for char in text1:
            diagonal = 0
            for j, other in enumerate(text2, 1):
                # 更新前 dp[j] 是上一行同列，dp[j-1] 已是当前行左邻。
                above = dp[j]
                if char == other:
                    dp[j] = diagonal + 1
                else:
                    dp[j] = max(above, dp[j - 1])
                # 下一列的左上角，正是本列尚未覆盖前的上方值。
                diagonal = above
        return dp[-1]

    def longestCommonSubsequenceTable(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        # 对照二维 DP：dp[i][j] 为两个字符串对应前缀的最长公共子序列长度。
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # 末尾相等时，在去掉两边末尾的共同子序列后接上该字符。
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    # 末尾不等时，只能分别舍弃一边的末尾，取较长的结果。
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[m][n]
'''.strip(),
 'code_notes':['默认入口使用一维滚动表，完整二维表保留在 longestCommonSubsequenceTable。', 'above 必须在覆盖 dp[j] 之前保存，diagonal 必须在本格计算完成后更新。', '两串互换不影响最长公共子序列长度，因此让短串作为列可以减少空间。'],
 'pitfalls':['不相等时清零，误写成公共连续子串。','末字符相等时直接用上方+1，可能重复使用第二串字符。','忘记空前缀导致 i-1/j-1 越界或负下标。'],
 'complexity':'默认滚动 DP 时间 O(mn)、额外空间 O(min(m,n))。对照完整表时间 O(mn)、空间 O(mn)。',
 'quiz':{'question':'"abc" 与 "ac" 的最长公共子序列长度为什么是 2？','answer':'可以在第一串跳过 b，保留 a、c，顺序不变。若要求连续子串，答案才是 1。'},
 'tests':checks('longestCommonSubsequence',[(['abcde','ace'],3),(['abc','abc'],3),(['abc','def'],0),(['abc','ac'],2),(['aaaa','aa'],2)])
,
 'submission': {'name': '一维滚动 DP', 'why': '转移仍然来自原二维表，只保留当前需要的上方、左方、左上角。完整表方法 longestCommonSubsequenceTable 用于对照图示。', 'steps': ['让较短字符串作为列，创建一行 DP。', '每次覆盖前保存 above；diagonal 保存旧左上角。', '匹配时取 diagonal+1，不匹配时取上方和左方较大值。'], 'diagram': '旧左上 diagonal | 旧上方 above\n当前左侧 dp[j-1] | 待更新 dp[j]'},
})

CHAPTER['problems'].append({
 'id':718,'slug':'maximum-length-of-repeated-subarray',
 'summary':'求同时出现在两个整数数组中的最长连续子数组长度。允许从不同下标开始，但匹配段内部不能跳过任何元素。',
 'baseline':'枚举两个起点，再逐个向后比较，最坏 O(mn·min(m,n))。与 LCS 不同，连续要求让“必须在两个当前位置同时结束”的后缀长度成为合适状态。',
 'insight':'dp[i][j] 表示必须以 nums1[i-1]、nums2[j-1] 结尾的最长公共连续后缀。末值相等时接左上+1，否则直接为 0。主解压成一行，j 倒序更新，使 dp[j-1] 仍是上一行左上值；全局 best 收集每个结尾的答案。',
 'steps':['dp 初始 n+1 个零，best=0。','依次读 nums1 的每个 x。','j 从 n 倒序到 1：相等时 dp[j]=dp[j-1]+1，否则 dp[j]=0。','每格更新 best。','返回 best，不能只返回 dp[n]。'],
 'invariant':'两个结尾不同，不存在长度至少 1 的相同连续后缀，状态只能归零；结尾相同，去掉末项后必须继续在两边前一位置同时结束，所以只能来自旧左上。倒序让该来源尚未覆盖，且 best 始终保存全部结尾中的最大长度。',
 'examples':[{'label':'不相等时连续段必须断开','input':'nums1=[1,2,3,2,1], nums2=[3,2,1,4,7]','output':'3','frames':[
  {'title':'公共连续段是 3、2、1','note':'两边的起点不同，内部三个元素却必须逐个相邻匹配。','panels':[{'heading':'nums1','array':[1,2,3,2,1],'active':[2,3,4]},{'heading':'nums2','array':[3,2,1,4,7],'active':[0,1,2]}]},
  {'title':'沿 DP 对角线累积长度','note':'下标表使用前缀长度 i、j。三个匹配状态依次来自左上，长度 1→2→3。','table':{'headers':['匹配结尾','i','j','后缀长度'],'rows':[['3 与 3',3,1,1],['2 与 2',4,2,2],['1 与 1',5,3,3]]}},
  {'title':'末尾不匹配不应丢掉历史 best','note':'两个数组最后分别为 1、7，右下角状态是 0，但较早的结尾已经出现长度 3。','table':{'headers':['状态','值'],'rows':[['dp[5][3]',3],['dp[5][5]',0],['全局 best',3]]}}
 ]},{'label':'倒序防止同一行被重复使用','input':'nums1=[1], nums2=[1,1]','output':'1','frames':[
  {'title':'同一个 1 不能被接两次','note':'j=2 先读旧 dp[1]=0，得 1；再更新 j=1。若正序，j=2 会误读新 dp[1]=1 而得 2。','table':{'headers':['时刻','dp[0]','dp[1]','dp[2]'],'rows':[['初始',0,0,0],['更新 j=2',0,0,1],['更新 j=1',0,1,1]]}}
 ]}],
 'walkthrough':['LCS 不匹配时可以跳过元素，所以取上/左最大值；本题一旦跳过就破坏连续性，因此必须归零。','倒序是一行压缩的实现选择，二维表并不需要倒序；目的是保留上一行来源，而不是数组本身必须反向匹配。','全局最长段可能在任意一对位置结束，所以单独维护 best。'],
 'code':'''
class Solution:
    def findLength(self, nums1: list[int], nums2: list[int]) -> int:
        n = len(nums2)
        # dp[j] 记录以当前 nums1 元素与 nums2[j-1] 结尾的连续匹配长度。
        dp = [0] * (n + 1)
        best = 0
        for x in nums1:
            # 倒序更新，让 dp[j-1] 仍来自上一行，而不是当前行。
            for j in range(n, 0, -1):
                if x == nums2[j - 1]:
                    dp[j] = dp[j - 1] + 1
                    best = max(best, dp[j])
                else:
                    # 必须连续；当前元素不等就归零，不能像子序列那样跳过。
                    dp[j] = 0
        return best
'''.strip(),
 'code_notes':['dp[0] 固定为 0，对应空前缀后缀长度。','更新 best 放在相等分支即可，不相等产生 0 不会超过非负 best。','只读取两个输入数组；也可交换两者使 DP 沿较短数组分配。'],
 'pitfalls':['不相等时取上/左最大值，变成子序列。','一行压缩时正序更新且不保存旧对角线。','只返回右下角状态，遗漏早先结束的最优段。'],
 'complexity':'时间 O(mn)，额外空间 O(n)，n 为 nums2 长度。',
 'quiz':{'question':'[1,2,3] 与 [1,3] 的公共连续子数组最长是多少？','answer':'是 1。虽然公共子序列 [1,3] 长度为 2，但它在第一数组中不连续。'},
 'tests':checks('findLength',[([[1,2,3,2,1],[3,2,1,4,7]],3),([[1],[1,1]],1),([[1,2,3],[1,3]],1),([[0,0,0],[0,0]],2),([[1],[2]],0)],preserve_args=[0,1])
})

CHAPTER['problems'].append({
 'id':72,'slug':'edit-distance',
 'summary':'把 word1 变成 word2，可以插入、删除或替换一个字符，每次成本 1，求最少操作数。允许输入空字符串，不提供相邻交换操作。',
 'baseline':'枚举所有编辑序列会重复到达相同前缀转换状态，还可能做插入后删除等无意义循环。用已处理的两边前缀长度记录进度，可以只考虑有序的字符对齐。',
 'insight':'dp[i][j] 表示把 word1[:i] 变成 word2[:j] 的最小成本。末字符相同直接沿左上；不同则在删除源末字符、补上目标末字符、替换源末字符三种对齐方式中选最小，再加 1。',
 'steps':['首列 dp[i][0]=i，全部删除；首行 dp[0][j]=j，全部插入。','从 i=1、j=1 开始递增。','相同：dp[i][j]=dp[i-1][j-1]。','不同：取 dp[i-1][j]（删除）、dp[i][j-1]（插入）、dp[i-1][j-1]（替换）的最小值加 1。','返回完整前缀 dp[m][n]。'],
 'invariant':'最优字符对齐的末端只能是源字符对空位（删除）、空位对目标字符（插入）、两字符相互对应（相同零成本或不同替换）。删掉这个末端对齐后是更小前缀问题；枚举这些类别既覆盖所有有效转换，也能从子问题解构造真实操作。',
 'examples':[{'label':'每种操作缩短不同的前缀','input':'word1="cat", word2="cut"','output':'1','frames':[
  {'title':'先初始化与空串的转换','note':'空串变成 cut 要插入 3 次；cat 变空串要删除 3 次。','table':{'headers':['源 / 目标','空','c','cu','cut'],'rows':[['空',0,1,2,3],['c',1,'?','?','?'],['ca',2,'?','?','?'],['cat',3,'?','?','?']]}},
  {'title':'a 与 u 不同，替换来自左上','note':'c→c 成本 0，替换 a 为 u 加 1，使 ca→cu 成本为 1。','table':{'headers':['源 / 目标','空','c','cu','cut'],'rows':[['空',0,1,2,3],['c',1,0,1,2],['ca',2,1,1,2],['cat',3,2,2,1]]}},
  {'title':'末尾 t 相同，沿左上保留成本','note':'cat→cut 只需替换中间一个字符。相同的末尾无需增加操作数。','panels':[{'heading':'源','array':list('cat'),'active':[1]},{'heading':'目标','array':list('cut'),'active':[1]}]}
 ]},{'label':'三种转移的方向','input':'word1="ab", word2="a"','output':'1','frames':[
  {'title':'删除对应上方状态','note':'先把源前缀 a 变成目标 a，成本 0，再删除源中多出的 b，成本加 1。','diagram':'dp[2][1]：ab → a\n删除 b：dp[1][1] + 1 = 1\n\n插入来源缩短目标前缀 j\n删除来源缩短源前缀 i\n替换来源同时缩短 i、j'}
 ]}],
 'walkthrough':['插入为什么来自左方：先把全部 i 个源字符变成目标前 j-1 个，再追加目标第 j 个字符；源前缀长度不减少。','删除为什么来自上方：当前源末字符不参与目标，先转换源的前 i-1 个，再去掉它。','替换或相同匹配都消耗两边各一个字符，所以看左上。理解消耗哪边，比背“上删左插”更可靠。','空串是题目合法输入，边界初始化本身就给出答案，不能依赖进入内层循环才产生结果。'],
 'code':'''
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        # 编辑距离对称，短串作为列可以减少滚动表空间。
        if len(word1) < len(word2):
            word1, word2 = word2, word1
        dp = list(range(len(word2) + 1))
        for i, char in enumerate(word1, 1):
            diagonal = dp[0]
            dp[0] = i  # 当前前缀变为空串，需要删除 i 次。
            for j, other in enumerate(word2, 1):
                above = dp[j]  # 覆盖前先保存上一行同列值。
                if char == other:
                    dp[j] = diagonal
                else:
                    # 上方：删 word1 末尾；左方：插入；左上：替换。
                    dp[j] = 1 + min(above, dp[j - 1], diagonal)
                diagonal = above
        return dp[-1]

    def minDistanceTable(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        # 对照二维 DP：把 word1 的前 i 个字符变成 word2 前 j 个字符的最少编辑次数。
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            # 变成空串只能删掉这 i 个字符；空串变为 j 个字符则需插入 j 次。
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                # 末尾相等，不需操作，直接继承左上角的编辑距离。
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # 末尾不等时比较删除、插入、替换三种操作，操作本身花费 1 次。
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],
                        dp[i][j - 1],
                        dp[i - 1][j - 1],
                    )
        return dp[m][n]
'''.strip(),
 'code_notes':['默认 minDistance 使用一维表，minDistanceTable 保留完整二维状态。', '上方旧值必须先保存到 above，再覆盖 dp[j]；否则下一列会拿错左上角。', '此题只允许插入、删除、替换，不包含交换相邻字符。'],
 'pitfalls':['首行首列全为零，相当于免费插入或删除。','把相等字符也加一次替换成本。','把相邻交换看成一次允许操作；本题没有该操作。','用 2×LCS 的公式计算，忽略本题允许成本为 1 的替换。'],
 'complexity':'默认滚动 DP 时间 O(mn)、辅助空间 O(min(m,n))。对照完整表时间 O(mn)、辅助空间 O(mn)。',
 'quiz':{'question':'"ab" 变成 "ba" 是否可以一次交换完成？','answer':'不可以，本题不允许交换。可以替换两次，最少成本为 2。'},
 'tests':checks('minDistance',[(['cat','cut'],1),(['horse','ros'],3),(['','abc'],3),(['abc',''],3),(['',''],0),(['ab','ba'],2)])
,
 'submission': {'name': '滚动行编辑距离', 'why': '默认方法保留原状态转移，只压缩存储；minDistanceTable 保留完整二维表，方便对照增删改三种路径。', 'steps': ['初始化把空串变成目标各前缀的插入次数。', '处理新行时更新空串列，并保存左上角旧值。', '相同字符沿左上角，不同字符在删除、插入、替换之间取最少操作数。'], 'diagram': '删除：上一行同列 + 1\n插入：当前行左列 + 1\n替换：上一行左列 + 1'},
})

CHAPTER['problems'].append({
 'id':5,'slug':'longest-palindromic-substring',
 'summary':'返回最长的连续回文子串。回文从两端向内读相同；最长答案可能不唯一，返回任意一个即可。输入非空且包含数字、大小写英文字母，比较区分大小写。',
 'baseline':'枚举 O(n²) 个区间，再逐个反转或双指针验证，要 O(n³)。多个区间共享内部回文判断，可以用区间 DP；也可以从每个可能中心向外扩展，复用已经确认的对称部分。',
 'insight':'区间状态 palindrome[left][right] 表示整段 s[left:right+1] 是否回文。两端必须相同，并且长度为 2 或内部区间已是回文；单字符先初始化为 True。按长度递增保证内部状态先算好。中心扩展则枚举单字符中心和两字符间隙，覆盖奇偶两类。',
 'steps':['创建 n×n 布尔表，将对角线设 True；最长初始为首字符。','长度从 2 到 n，依次枚举起点和终点。','端点相同且内部满足条件时，标记回文并更新最长区间。','循环结束后只切片一次返回答案。','进阶 longestPalindromeCenter 对每个 i 分别扩展 (i,i) 与 (i,i+1)，记录最大左右范围。'],
 'invariant':'长度为 1 必为回文；长度为 2 只需端点相同；更长回文当且仅当端点相同且删去两端后仍回文。按长度归纳即可证明整张表。中心版中任何回文都有唯一字符中心或间隙中心，扩展每个中心直到首次不匹配，就枚举到该中心可实现的最大回文。',
 'examples':[{'label':'偶数回文的中心在两个字符之间','input':'s="cbbd"','output':'"bb"','frames':[
  {'title':'单字符区间先为 True','note':'区间表仅使用 left≤right 的上三角。下三角不对应本题的非空区间。','table':{'headers':['left / right',0,1,2,3],'rows':[[0,'T','?','?','?'],[1,'—','T','?','?'],[2,'—','—','T','?'],[3,'—','—','—','T']]}},
  {'title':'长度 2 中只有 bb 相等','note':'left=1、right=2，端点都是 b，长度为 2 可直接确认。更长区间的外端均不相等。','array':list('cbbd'),'active':[1,2],'pointers':{'left':1,'right':2}},
  {'title':'中心扩展从间隙开始','note':'中心 (1,2) 先匹配 b、b，扩到 (0,3) 时 c≠d 停止，最终有效范围为 [1,2]。','diagram':'c  b | b  d\n   ← 匹配 →\nc 与 d 不同，停止\n返回 s[1:3] = "bb"'}
 ]},{'label':'多个最长答案均合法','input':'s="babad"','output':'"bab"（"aba" 也合法）','frames':[
  {'title':'两个长度 3 的回文','note':'代码仅在更长时更新，因此保留先发现的 bab；这不影响最优长度。','table':{'headers':['区间','子串','是否回文'],'rows':[['[0,2]','bab','是'],['[1,3]','aba','是'],['[0,4]','babad','否']]}}
 ]}],
 'walkthrough':['状态描述完整闭区间，而不是“前缀里的最长回文”；只有布尔的内部回文事实才能直接用于端点扩张。','若改为按 left 遍历，必须从右往左，确保 left+1 已完成；本解按长度递增，依赖顺序更直观。','中心扩展停止时 left、right 已经越界或不匹配，真正有效范围是 left+1 到 right-1，长度为 right-left-1。','只保留一个最优范围，最后再切片；若每次扩展都截取候选子串，会引入额外复制成本。','如果希望平台运行中心扩展版，可把入口 longestPalindrome 的方法体改为 return self.longestPalindromeCenter(s)，并保留该辅助方法。'],
 'code':'''
class Solution:
    def longestPalindrome(self, s: str) -> str:
        if not s:
            return ''
        # Manacher：插入 None 分隔符，让奇数、偶数回文都拥有一个明确中心。
        # None 不可能等于字符串中的字符，所以也支持输入本身包含 # 等符号。
        transformed = [None]
        for char in s:
            transformed.extend((char, None))
        radius = [0] * len(transformed)
        center = right = 0
        best_center = best_radius = 0
        for i in range(len(transformed)):
            if i < right:
                # 已知回文关于 center 对称，先复用镜像中心的半径。
                # 镜像信息不能越过当前已知右边界，所以取两者较小值。
                mirror = 2 * center - i
                radius[i] = min(radius[mirror], right - i)
            # 从尚未验证的下一对开始扩展，不重复比较已由镜像保证的内部区域。
            while (i - radius[i] - 1 >= 0
                   and i + radius[i] + 1 < len(transformed)
                   and transformed[i - radius[i] - 1] == transformed[i + radius[i] + 1]):
                radius[i] += 1
            if i + radius[i] > right:
                center, right = i, i + radius[i]
            if radius[i] > best_radius:
                best_center, best_radius = i, radius[i]
        # 分隔符表示下，半径恰好等于原串回文长度；除以 2 映射回原下标。
        start = (best_center - best_radius) // 2
        return s[start:start + best_radius]

    def longestPalindromeDP(self, s: str) -> str:
        n = len(s)
        # 对照区间 DP：记录每个闭区间是否回文，空间为平方级。
        palindrome = [[False] * n for _ in range(n)]
        for i in range(n):
            palindrome[i][i] = True
        best_start, best_length = 0, 1
        # 按区间长度从短到长推导，内部区间的结果才已经计算过。
        for length in range(2, n + 1):
            for left in range(n - length + 1):
                right = left + length - 1
                if s[left] == s[right] and (
                    # 相邻两个相同字符直接是回文，不读取无效的内部区间。
                    length == 2 or palindrome[left + 1][right - 1]
                ):
                    palindrome[left][right] = True
                    if length > best_length:
                        best_start, best_length = left, length
        return s[best_start:best_start + best_length]

    # 对照中心扩展：枚举奇数与偶数两种中心，空间小，但最坏会重复比较很多次。
    def longestPalindromeCenter(self, s: str) -> str:
        best_start, best_length = 0, 1
        for center in range(len(s)):
            # 同一个字符为中心处理奇回文；两个字符之间为中心处理偶回文。
            for left, right in ((center, center), (center, center + 1)):
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    left -= 1
                    right += 1
                # 退出时左右指针各越过一个有效位置，所以实际长度减去两侧越界量。
                length = right - left - 1
                if length > best_length:
                    best_start, best_length = left + 1, length
        return s[best_start:best_start + best_length]
'''.strip(),
 'code_notes':['默认 longestPalindrome 是 Manacher；longestPalindromeDP、longestPalindromeCenter 分别保留两种教学对照。', '镜像半径截断到 right-i：已知大回文之外尚无对称保证，必须继续实际比较。', '镜像范围内的比较被复用，扩展超过已知边界时 right 只会右移，因此所有成功的新扩展合计为线性量级；每个中心还至多产生一次失败比较。', '变换中原字符与 None 交替，半径正好对应原串回文长度，起点用 (center-radius)//2 还原。'],
 'pitfalls':['只检查两端相等，忽略内部是否回文。','中心扩展只写 (i,i)，漏掉 bb、abba。','停止后仍把 left/right 当成有效边界。','混淆回文子串与可跳过字符的回文子序列。'],
 'complexity':'默认 Manacher 时间 O(n)、辅助空间 O(n)，返回子串占 O(k)。对照中心扩展最坏时间 O(n²)、辅助空间 O(1)；区间 DP 时间与空间均为 O(n²)。',
 'quiz':{'question':'为什么 "abca" 两端相等却不是回文？','answer':'内部 "bc" 不是回文；端点相等只是必要条件，长度超过 2 时还必须检查内部区间。'},
 'tests':checks('longestPalindrome',[(['cbbd'],'bb'),(['babad'],'bab'),(['a'],'a'),(['aaaa'],'aaaa'),(['abca'],'a'),(['Aa'],'A')])
,
 'submission': {'name': 'Manacher 线性时间算法', 'why': '默认采用 Manacher 消除中心扩展中的重复比较。前面的区间 DP 可视化对应 longestPalindromeDP，另保留 longestPalindromeCenter 帮助理解“以中心向两边扩展”。', 'steps': ['在字符间和两端插入不会与字符相等的分隔符，把两类回文中心统一起来。', '维护当前覆盖最靠右的回文中心 center 与边界 right。', '新中心在已知范围内时，先复用它的镜像半径，但最多只能到 right。', '从边界外继续比较；扩得更远时更新 center 与 right，并记录最长半径。'], 'diagram': '原串：a b b a\n变换：· a · b · b · a ·\n中心：        ↑\n变换半径 4 → 原串回文长度 4\n已知大回文内部对称，镜像结果可复用；边界外才需要新比较。'},
})
