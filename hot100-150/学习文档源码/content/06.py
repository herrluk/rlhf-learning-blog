from textwrap import dedent

def frame(a, left, right, mid, title, note, half_open=False):
    return {'title':title,'note':note,'array':a,'active':list(range(left,right if half_open else right+1)),
            'pointers':{'left':left,'right':right,**({'mid':mid} if mid is not None else {})},
            'metrics':[['搜索区间',f'[{left},{right}{")" if half_open else "]"}'],['mid','无' if mid is None else mid]]}

CHAPTER={
 'lead':'二分的核心是每次排除一半仍可能含有答案的位置。先写清搜索对象与区间含义，再决定 mid 是否应该保留。',
 'intro':['二分查找不仅用于有序数组。搜索对象也可以是插入位置、平方根的候选值、吃香蕉的速度，或两个数组之间的分割线。无论形式如何，必须解释判断条件为什么允许排除一半。','本章先学 704 的精确查找，再学 35、34 的边界查找；69、875 迁移到答案范围；74、240 比较两种矩阵有序性；153、33 研究旋转数组；162 用局部坡度保留峰值；最后挑战第 4 题的分割线。','240 的阶梯搜索每次排除一行或一列，并不把候选空间减半，时间是 O(m+n)。它与 74 放在一起是为了理解有序条件如何决定可用的排除方式。'],
 'sections':[
  {'title':'闭区间与左闭右开都正确，但不能混搭','body':['精确查找的闭区间 [left,right] 从 [0,n−1] 开始，只要 left≤right 就还有候选。已经检查过 mid 且不相等时，保留左边要写 right=mid−1，保留右边要写 left=mid+1。','边界查找常用左闭右开 [left,right)。初始 [0,n)，只在 left<right 时循环。若 mid 已经满足“至少为 target”，mid 可能就是第一个满足者，应写 right=mid；否则写 left=mid+1。结束时 left==right 是边界位置，允许等于 n。'],'diagram':'闭区间找元素：     [ left ... mid ... right ]\n不相等后排除 mid： right=mid−1 或 left=mid+1\n\n左闭右开找边界：   [ left ... mid ... right )\nmid 可能是边界：   right=mid\nmid 肯定不是边界： left=mid+1'},
  {'title':'每轮问两个问题','body':['答案为什么仍在新区间里？这证明没有漏解。区间是否严格缩短？这保证不会死循环。例如向下取整 mid 后写 left=mid，在 left+1=right 时就可能停住。','不要把所有题压成同一个条件。35 寻找第一个真；69 寻找最后一个真；162 的坡度序列甚至不必全局单调，依靠的是被保留区间中至少存在一个峰值。']},
  {'title':'学习路径中的前置关系','body':['35 的边界模板是 34 两次定位的基础；69 帮助理解在数值范围上二分，875 则把单次判断扩展成扫描全部输入。','74 可以按行展平后全局有序，240 只保证各行各列分别有序。153 定位旋转点，33 再处理旋转数组中的目标。第 4 题需要同时保持两边数量与大小关系，适合最后学习。']}
 ],
 'apis':[{'signature':'divmod(a: int, b: int) -> tuple[int, int]','description':['对整数返回商与余数组成的二元组，等价于 (a//b,a%b)，b 不能为 0。第 74 题用 divmod(index,列数) 得到行号与列号。','中点统一用 left+(right-left)//2，向下取整。Python 整数不会像固定宽度整型那样溢出，但这一写法也便于迁移到 Go 等语言。']}],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':704,'slug':'binary-search',
 'summary':'给定升序且元素互不相同的整数数组 nums，返回 target 的下标；找不到返回 −1。要求 O(log n) 时间，因此不能逐项扫描。',
 'baseline':'从头到尾比较每个元素可以 O(n) 找到答案，但没有利用数组有序性。查看中间元素后，目标与它的大小关系会告诉我们另一半绝无可能。',
 'insight':'若 nums[mid]<target，则 mid 以及它左边的元素都不大于 nums[mid]，都小于目标；它们可以一起排除。若 nums[mid]>target，则 mid 及其右侧都太大。只有相等时立刻返回。',
 'steps':['初始化闭区间 left=0、right=n−1，表示所有位置都还可能是目标。','当 left≤right 时计算 mid，读取 nums[mid]。','若相等返回 mid；若中点太小，令 left=mid+1；若中点太大，令 right=mid−1。','区间为空时还没找到，说明所有可能位置都已排除，返回 −1。'],
 'invariant':'每轮开始时，若目标存在，它必在闭区间 [left,right] 中。每次依据有序性排除一半，并排除已经确认不相等的 mid。循环严格缩短候选数；区间变空后仍未命中，就能断定目标不存在。',
 'examples':[{'label':'命中右半边','input':'nums=[-1,0,3,5,9,12], target=9','output':'4','frames':[
  frame([-1,0,3,5,9,12],0,5,2,'第一轮：中点值 3 太小','下标 0、1、2 的值都不超过 3，全部排除，下一轮 left=3。'),
  frame([-1,0,3,5,9,12],3,5,4,'第二轮：命中 9','nums[4]=9，直接返回下标 4。注意返回的是位置，不是数值 9。')
 ]},{'label':'最终只剩一个仍需检查的位置','input':'nums=[1,3,5], target=4','output':'-1','frames':[
  frame([1,3,5],0,2,1,'3 太小','排除下标 0、1，候选区间变为 [2,2]。'),
  frame([1,3,5],2,2,2,'最后一个元素 5 太大','right=1，接下来 left=2>right=1，候选为空，返回 −1。')
 ]}],
 'walkthrough':['目标 9 比中点 3 大，并不是说下一步只看紧挨着 3 的 5，而是把整个左半边一起跳过。第二轮直接落到下标 4。','查找 4 时，最后区间 [2,2] 仍包含一个候选，需要进入循环检查 5。因此闭区间精确查找不能把条件随意改成 left<right。','每次更新都使用 mid±1，因为 mid 本轮已经确认不等于目标，不必再保留。'],
 'code':'''
class Solution:
    def search(self, nums: list[int], target: int) -> int:
        # 候选范围是闭区间 [left,right]，所以只剩一项时也要检查。
        left, right = 0, len(nums) - 1
        while left <= right:
            # 每次查看中点，将仍可能含答案的区间缩小一半。
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid
            # 中点已偏小，连同左半边一起排除；否则排除右半边。
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        # 区间耗尽仍未命中，说明目标不存在。
        return -1
'''.strip(),
 'code_notes':['left、right 都是包含在候选中的下标。right 初始为 len(nums)−1，不能写 len(nums)。','相等分支先返回，后面的大小分支不需要再次考虑相等。','循环退出只说明候选区间为空，不能直接返回 left 当作命中位置；那种返回值属于插入位置题。'],
 'pitfalls':['闭区间的 while left≤right 与 mid±1 更新是一套约定，不能混入边界模板的 right=mid。','nums 必须满足题目给定的升序性质，不能在任意数组上直接使用。','题目保证无重复值；若改为找重复目标的第一个位置，相等时立即返回就不够了。'],
 'complexity':'时间 O(log n)，每次将候选数约减半；额外空间 O(1)。',
 'quiz':{'question':'如果数组只有 [7]，target=7，while left<right 会怎样？','answer':'初始 left=right=0，循环不会执行，随后错误返回 −1。闭区间里左右端相等仍表示有一个候选，所以这里必须用 ≤。'},
 'tests':{'method':'search','cases':[{'args':[[-1,0,3,5,9,12],9],'expected':4},{'args':[[1,3,5],4],'expected':-1},{'args':[[7],7],'expected':0},{'args':[[7],8],'expected':-1},{'args':[[1,2],1],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':35,'slug':'search-insert-position',
 'summary':'在升序且无重复元素的数组中找 target；存在时返回下标，不存在时返回按升序插入的位置。允许插在最前面或末尾，答案范围是 0 到 n。',
 'baseline':'从左到右找到第一个大于等于 target 的元素即可返回其位置，若全都小于目标则返回 n，时间 O(n)。这个描述已经给出了统一目标：不必把“存在”和“不存在”写成两套算法。',
 'insight':'把每个位置是否满足 nums[i]≥target 看作布尔条件，有序数组保证形状是“若干假，接着全是真”。答案就是第一个真的位置；如果没有真，使用 n 作为末尾边界。',
 'steps':['初始化 left=0、right=n，搜索区间采用左闭右开。','当 left<right 时计算 mid。若 nums[mid]<target，mid 及左侧都不满足，令 left=mid+1。','否则 nums[mid]≥target，mid 可能就是第一个满足者，令 right=mid，把边界向左逼近。','left==right 时分界已经确定，返回 left；它可能等于 n，但不必读取 nums[n]。'],
 'invariant':'始终有：所有 i<left 的元素都小于 target；所有 i≥right 的数组元素都大于等于 target。中间部分尚未确定。每轮缩小未知区间，结束后两类之间唯一分界就是插入位置。right=n 时第二条在空后缀上自然成立。',
 'examples':[{'label':'目标落在两个元素之间','input':'nums=[1,3,5,6], target=2','output':'1','frames':[
  frame([1,3,5,6],0,4,2,'mid=2，值 5 已满足 ≥2','答案不会在 5 的右边；mid 仍可能是边界，所以 right=2。',True),
  frame([1,3,5,6],0,2,1,'mid=1，值 3 也满足','继续尝试更早的位置，right=1。',True),
  frame([1,3,5,6],0,1,0,'mid=0，值 1 太小','left=1。左右边界重合，返回 1，插入后为 [1,2,3,5,6]。',True)
 ]},{'label':'允许插在末尾','input':'nums=[1,3,5,6], target=7','output':'4','frames':[
  frame([1,3,5,6],0,4,2,'5 小于 7','排除下标 0..2，left=3。',True),
  frame([1,3,5,6],3,4,3,'6 仍小于 7','left=4，与 right 重合。返回长度 n=4 作为插入位置，不访问 nums[4]。',True)
 ]}],
 'walkthrough':['target=2 时 5、3 都满足“至少为 2”，但它们的下标只是边界的上限，不能因为满足就立即返回。还需继续向左寻找。','检查 1 后确认它太小，最早可插的位置就是它后面，即下标 1。','target=7 时，所有位置都被归入“小于目标”一侧，所以边界在整个数组之后，结果是 n。'],
 'code':'''
class Solution:
    def searchInsert(self, nums: list[int], target: int) -> int:
        # 维护左闭右开区间，答案允许是 len(nums)，表示插在末尾。
        left, right = 0, len(nums)
        while left < right:
            mid = left + (right - left) // 2
            # 严格小于 target 的位置不可能是第一个插入位置。
            if nums[mid] < target:
                left = mid + 1
            else:
                # 中点已经不小于 target，它自己仍可能是答案，不能排除。
                right = mid
        return left
'''.strip(),
 'code_notes':['right 初始为 n 是合法的边界位置，循环只在 left<right 时读取 mid，所以 mid 始终小于 n。','right=mid 表示找到一个满足条件的位置，答案可能就是它；这里若减一，会跳过真正的分界。','返回 left 不要求 nums[left]==target，因为本题也要处理不存在时的插入位置。'],
 'pitfalls':['条件是第一个 ≥target，若写成 >target，目标存在时会返回它的后面。','退出后不要无条件访问 nums[left]，因为 left 可能为 n。','把数组切片传给递归会产生拷贝，并打乱原始下标；本解法只移动边界。'],
 'complexity':'时间 O(log n)，额外空间 O(1)。',
 'quiz':{'question':'如果输入允许重复元素，这份代码返回哪一个插入位置？','answer':'仍返回第一个大于等于 target 的位置，即所有相等元素之前的位置。它正是 lower bound；因此同一模板可以用于第 34 题的左边界。'},
 'tests':{'method':'searchInsert','cases':[{'args':[[1,3,5,6],2],'expected':1},{'args':[[1,3,5,6],5],'expected':2},{'args':[[1,3,5,6],7],'expected':4},{'args':[[1,3,5,6],0],'expected':0},{'args':[[1],1],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':34,'slug':'find-first-and-last-position-of-element-in-sorted-array',
 'summary':'升序数组可以包含重复值，返回 target 第一次和最后一次出现的下标。目标不存在时返回 [-1,-1]，要求 O(log n) 时间。',
 'baseline':'普通二分找到一个 target 后，再向两边线性扩张直到遇到不同值，最坏会扫描整个数组，例如数组全是 target。为了满足对数时间，左右两端都要用边界二分定位。',
 'insight':'把目标区间写成半开形式 [first_ge,first_gt)：first_ge 是第一个 ≥target 的位置，first_gt 是第一个 >target 的位置。两者之间全部等于 target，最后一个出现位置就是 first_gt−1。如果 first_ge 已经越界或其值不是目标，说明没有这段相等区间。',
 'steps':['定义 boundary(after_equal)，使用左闭右开区间 [0,n) 查找一个分界位置。','after_equal=False 时，把小于 target 的值归到左边，找到第一个 ≥target 的位置。','after_equal=True 时，把等于 target 的值也归到左边，找到第一个 >target 的位置。','先求 start=boundary(False)。若 start==n 或 nums[start]!=target，返回 [-1,-1]。','再求 end=boundary(True)−1，返回 [start,end]。不要对结果继续做线性扩张。'],
 'invariant':'两次调用都把数组分为“应跳过的左侧”和“满足边界条件的右侧”。第一次左侧为 <target，第二次左侧为 ≤target。数组有序保证两种划分各有唯一分界，因此相等区间正好被两个分界夹住。',
 'examples':[{'label':'重复的 8 占据下标 3、4','input':'nums=[5,7,7,8,8,10], target=8','output':'[3,4]','frames':[
  frame([5,7,7,8,8,10],0,6,3,'左边界：8 已经满足 ≥8','保留 mid 的可能性，right=3。相等时不能直接返回，因为左侧还可能有 8。',True),
  frame([5,7,7,8,8,10],0,3,1,'左边界：7 太小','left=2；仍需检查下标 2。',True),
  frame([5,7,7,8,8,10],2,3,2,'左边界确定为 3','下标 2 仍是 7，left=3，与 right 重合。start=3，且 nums[3]=8。',True),
  frame([5,7,7,8,8,10],0,6,3,'右边界：这次相等也要跳过','要找第一个 >8，所以值为 8 的 mid 属于左侧，left=4。',True),
  frame([5,7,7,8,8,10],4,6,5,'10 满足 >8','right=5，保留它作为可能分界。',True),
  frame([5,7,7,8,8,10],4,5,4,'第一个 >8 的位置是 5','下标 4 是 8，继续跳过，left=5。因此最后一个 8 在 5−1=4。',True),
  {'title':'两个边界夹住所有相等元素','note':'相等区间为 [3,5)，转换成题目要求的首尾闭区间就是 [3,4]。','array':[5,7,7,8,8,10],'active':[3,4],'pointers':{'first':3,'last':4,'first_gt':5}}
 ]}],
 'walkthrough':['两次二分的唯一判断差别是相等时向哪边移动。找左边界把相等值留在右侧，找超过目标的边界把相等值跳到左侧。','右边界函数得到 5，并不表示 8 出现在下标 5，而是从这里开始值严格大于 8，所以需要减一。','若 target=6，第一个 ≥6 的位置是下标 1，但 nums[1]=7。存在插入位置不代表存在目标，必须做一次命中检查。'],
 'code':'''
class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        # False 找第一个 ≥target 的位置；True 找第一个 >target 的位置。
        def boundary(after_equal: bool) -> int:
            left, right = 0, len(nums)
            while left < right:
                mid = left + (right - left) // 2
                # 开启 after_equal 时，等于 target 的位置也要继续向右跳过。
                if nums[mid] < target or (after_equal and nums[mid] == target):
                    left = mid + 1
                else:
                    right = mid
            return left

        start = boundary(False)
        # 左边界可能指向末尾或更大的值，要先确认目标确实存在。
        if start == len(nums) or nums[start] != target:
            return [-1, -1]
        # 第一个严格更大位置的前一格，就是最后一个 target。
        end = boundary(True) - 1
        return [start, end]
'''.strip(),
 'code_notes':['局部函数从外层读取 nums 与 target；每次调用重新初始化 left、right，两次搜索相互独立。','after_equal=True 表示将相等元素也放入跳过的左半边，因此得到的是相等区间之后的位置。','or 会短路求值：start==len(nums) 时不会继续读取 nums[start]。这也自然处理了空数组。'],
 'pitfalls':['普通二分相等时立即返回，只找到某一个位置，不能保证最左或最右。','先二分再向两侧线性扫描会退化到 O(n)，全相等数组最容易暴露这个问题。','右边界是第一个严格大于目标的位置，返回最后出现下标时要减一。'],
 'complexity':'两次 O(log n) 搜索，合计仍为 O(log n)；额外空间 O(1)。空数组直接由空区间流程处理。',
 'quiz':{'question':'nums=[8,8,8] 时，两个 boundary 分别返回什么？','answer':'boundary(False) 返回 0，boundary(True) 返回 3，最终范围是 [0,2]。右边界允许等于数组长度，它表示相等区间之后的位置，不是可读取的数组下标。'},
 'tests':{'method':'searchRange','cases':[{'args':[[5,7,7,8,8,10],8],'expected':[3,4]},{'args':[[5,7,7,8,8,10],6],'expected':[-1,-1]},{'args':[[],0],'expected':[-1,-1]},{'args':[[8,8,8],8],'expected':[0,2]},{'args':[[1],2],'expected':[-1,-1]},{'args':[[0,0,1],0],'expected':[0,1]}]}
})

CHAPTER['problems'].append({
 'id':69,'slug':'sqrtx',
 'summary':'给定非负整数 x，返回它的非负平方根的整数部分，也就是最大的整数 y，使 y²≤x。不能调用平方根或幂函数来直接求答案。',
 'baseline':'从 0 起逐个尝试整数 y，直到 (y+1)²>x，时间 O(√x)。候选值是否可行具有单调性：小的 y 可行，大到超过平方根之后都不可行，因此无需顺次试遍。',
 'insight':'要找的不是数组下标，而是整数答案 y。搜索范围可以取 [0,x]。条件 y²≤x 在这个范围内先真后假，答案就是最后一个真的位置。每次得到一个可行 mid，就保存它，再尝试更大的候选。',
 'steps':['初始化 left=0、right=x、answer=0，采用闭区间候选范围。0 对任何非负 x 都是可行下界。','计算 mid 与 mid²。若 mid²≤x，说明 mid 可行，保存 answer=mid，并令 left=mid+1 寻找更大的可行值。','若 mid²>x，mid 及更大的数都不可行，令 right=mid−1。','候选区间为空后返回保存的最大可行 answer。恰好为完全平方数时也符合这套判断。'],
 'invariant':'answer 始终是已经确认可行的最大候选；大于 right 的候选已被证明不可行，可能改进 answer 的未知值仍保留在搜索区间。可行时向右探索、不可行时向左收缩，最后便得到最大满足 y²≤x 的整数。',
 'examples':[{'label':'8 的整数平方根','input':'x=8','output':'2','frames':[
  {'title':'候选中点 4 太大','note':'初始 [0,8]，4²=16>8，排除 4..8，right=3。这里数组格子显示的是候选答案值。','array':list(range(9)),'active':list(range(9)),'pointers':{'mid':4},'metrics':[['answer',0]]},
  {'title':'中点 1 可行，继续向右','note':'[0,3] 的中点为 1，1²≤8，answer=1，left=2。找到可行值还不能停，因为可能有更大的整数。','array':list(range(9)),'active':list(range(4)),'pointers':{'mid':1},'metrics':[['answer',1]]},
  {'title':'中点 2 仍可行','note':'[2,3] 的中点为 2，2²=4≤8，answer=2，left=3。','array':list(range(9)),'active':[2,3],'pointers':{'mid':2},'metrics':[['answer',2]]},
  {'title':'3 不可行，最终答案为 2','note':'3²=9>8，right=2。此时 left=3>right=2，没有未检查的更大可行数，返回 2。','array':list(range(9)),'active':[3],'pointers':{'mid':3},'equation':'2² ≤ 8 < 3²'}
 ]}],
 'walkthrough':['本题中可行条件是平方不超过 x，和第 35 题“至少为 target”的方向相反。不能只复制比较符号而不重新分析要找第一个真还是最后一个真。','2 可行只能说明答案至少为 2，还需确认 3 不可行。直到候选为空才能确定最大值。','x=0 时唯一候选 mid=0，可行并保存为 0，随后结束；x=1 时最后保存为 1，无需额外分支。'],
 'code':'''
class Solution:
    def mySqrt(self, x: int) -> int:
        left, right = 0, x
        # 保存最后一次确认满足 mid²≤x 的候选，避免使用浮点平方根。
        answer = 0
        while left <= right:
            mid = left + (right - left) // 2
            # 当前值合法，但还可能有更大的合法整数，继续搜右边。
            if mid * mid <= x:
                answer = mid
                left = mid + 1
            else:
                # 平方已经过大，当前值及更大的数都要排除。
                right = mid - 1
        return answer
'''.strip(),
 'code_notes':['answer 只在确认 mid 可行时更新，不会保存超过真实平方根的数。','Python 整数支持任意精度，mid*mid 不会发生固定宽度整型溢出；迁移到其他语言时要用足够宽的类型，或在 mid>0 时比较 mid≤x//mid。','全程只使用整数运算，避免浮点平方根在边界值附近的舍入问题。'],
 'pitfalls':['题目要向下取整，不是四舍五入：√8 接近 2.83，答案仍为 2。','mid²<x 少了等号，会在完全平方数处把正确答案误判为不可行。','如果改用 x//mid 判断，需要先处理 mid=0，避免除零。'],
 'complexity':'在题目限定整数范围的常规运算模型下，时间 O(log(x+2))，额外空间 O(1)。这里加 2 是为了让 x=0 时的记法也包含常数工作量。',
 'quiz':{'question':'怎样用两个整数不等式验证返回值 y，而不用浮点数？','answer':'验证 y*y≤x 且 (y+1)*(y+1)>x。第一条说明 y 可行，第二条说明下一个整数已经不可行，二者共同说明 y 是向下取整的平方根。'},
 'tests':{'method':'mySqrt','cases':[{'args':[8],'expected':2},{'args':[4],'expected':2},{'args':[0],'expected':0},{'args':[1],'expected':1},{'args':[2147395600],'expected':46340},{'args':[2147483647],'expected':46340}]}
})

CHAPTER['problems'].append({
 'id':875,'slug':'koko-eating-bananas',
 'summary':'有若干堆香蕉，每小时选择一堆，最多吃 k 根；若这一堆不足 k 根，吃完后这一小时也不能接着吃另一堆。求在 h 小时内吃完全部香蕉的最小整数速度 k。题目保证 h 不小于堆数。',
 'baseline':'从速度 1 到最大堆大小逐个尝试，每种速度都扫描全部堆，时间 O(nM)，M 为最大堆大小。堆很大时逐速尝试不可行，但速度越大，所需小时数不会增加。',
 'insight':'一堆 p 根以速度 k 吃完需要向上取整 p/k 小时，整数写法是 (p+k−1)//k。总时间是每堆时间分别取整后相加。条件“总时间≤h”随 k 增大从假变真，所求就是第一个可行速度。',
 'steps':['候选速度下界取 1，上界取 max(piles)。因为 h≥堆数，上界一定能在每堆一小时内完成。','在闭区间 [left,right] 中取 mid，扫描所有堆，累计 hours += (p+mid−1)//mid。','若 hours≤h，mid 已经可行，但可能还能更慢，所以令 right=mid 保留它。','若 hours>h，mid 以及更慢的速度都不可行，令 left=mid+1。','当 left==right，最小可行速度确定，返回 left。'],
 'invariant':'区间中始终包含最小可行速度，right 始终是可行速度。若 mid 可行，则最小可行值不会大于 mid；若 mid 不可行，则更小速度也不可能可行。每轮严格缩短区间，最终左右相遇于第一个可行值。',
 'examples':[{'label':'逐步逼近最小速度 4','input':'piles=[3,6,7,11], h=8','output':'4','frames':[
  {'title':'速度 6 可以完成','note':'候选区间 [1,11]，mid=6，每堆分别需要 1、1、2、2 小时，总计 6≤8，保留 [1,6]。','array':[3,6,7,11],'table':{'headers':['每堆香蕉','3','6','7','11'],'rows':[['以速度 6 所需小时',1,1,2,2]]},'metrics':[['总时间',6],['新的速度区间','[1,6]']]},
  {'title':'速度 3 太慢','note':'[1,6] 的中点为 3，每堆需要 1、2、3、4 小时，总计 10>8，排除速度 1..3。','array':[3,6,7,11],'metrics':[['每堆小时','1+2+3+4'],['总时间',10],['新区间','[4,6]']]},
  {'title':'速度 5 可行，但继续寻找更小','note':'[4,6] 的中点为 5，总时间 1+2+2+3=8。right=5，留下 [4,5]。','array':[3,6,7,11],'metrics':[['速度',5],['总时间',8],['新区间','[4,5]']]},
  {'title':'速度 4 仍可行，左右相遇','note':'速度 4 的每堆时间也是 1、2、2、3，总计 8。right=4，与 left 相同，返回 4。速度 3 已被证明不够。','array':[3,6,7,11],'table':{'headers':['速度','3','4','5','6'],'rows':[['总小时数',10,8,8,6],['≤8 小时','否','是','是','是']]}}
 ]}],
 'walkthrough':['每堆的不足一小时部分不能与其他堆合并。因此速度 4 时 3 根要一小时，6 根要两小时，7 根要两小时，11 根要三小时。','总香蕉数为 27，直接做 ceil(27/4)=7 会少算一小时，因为那种计算允许在一小时内跨堆吃，不符合题意。','速度 4 和 5 的总时间相同，说明可行性只需单调，不要求时间严格递减。二分依然能找到平台最左端。'],
 'code':'''
class Solution:
    def minEatingSpeed(self, piles: list[int], h: int) -> int:
        # 每小时速度至少 1、至多最大堆大小，最小可行速度一定在这个范围。
        left, right = 1, max(piles)
        while left < right:
            mid = left + (right - left) // 2
            hours = 0
            for p in piles:
                # 每堆分别向上取整；本小时吃完一堆后不能接着吃另一堆。
                hours += (p + mid - 1) // mid
            # 当前速度可行，保留它并尝试更慢；否则必须加速。
            if hours <= h:
                right = mid
            else:
                left = mid + 1
        return left
'''.strip(),
 'code_notes':['速度下界从 1 开始，避免除以零。max(piles) 是一个确定可行的上界，依赖 h≥堆数的题目保证。','(p+mid−1)//mid 用整数完成正数除法的向上取整。例如 p=6、mid=4 时结果为 2。','while left<right 与 right=mid 配合：可行中点不能丢弃，因为它本身可能就是最慢可行速度。'],
 'pitfalls':['必须逐堆向上取整再求和，不能先把香蕉总数相加后统一取整。','hours<h 写成严格小于会排除恰好在 h 小时完成的最优速度。','不要把答案当成数组中的某个堆大小。最优速度可能根本不出现在 piles 中，例如本例的 4。'],
 'complexity':'令 n 为堆数，M 为最大堆大小，时间 O(n log(M+1))，每次二分要 O(n) 计算时间；额外空间 O(1)。',
 'quiz':{'question':'如果 h 恰好等于堆数，最小速度是多少？','answer':'每堆都至少占一小时，不能有任何堆需要两小时，因此速度必须至少为最大堆大小；取 max(piles) 正好可行，所以它就是答案。'},
 'tests':{'method':'minEatingSpeed','cases':[{'args':[[3,6,7,11],8],'expected':4},{'args':[[30,11,23,4,20],5],'expected':30},{'args':[[30,11,23,4,20],6],'expected':23},{'args':[[1,1],3],'expected':1},{'args':[[1000000000],2],'expected':500000000}]}
})

CHAPTER['problems'].append({
 'id':74,'slug':'search-a-2d-matrix',
 'summary':'矩阵每行从左到右非递减，并且每行第一个数严格大于上一行最后一个数。判断 target 是否存在，要求 O(log(mn)) 时间。',
 'baseline':'直接遍历所有格子需要 O(mn)。可以先二分定位可能所在的行，再在那一行二分；另一种更统一的办法是把整张矩阵当成一个虚拟有序数组。这个“虚拟”很关键，不必真的分配一维数组。',
 'insight':'由于行首大于上一行行尾，按行拼接所有元素后仍然全局有序。若每行 n 列，虚拟下标 index 对应行 index//n、列 index%n，于是可对 [0,mn−1] 直接做普通二分。',
 'steps':['读取行数 m、列数 n，把候选下标范围设为 [0,mn−1]。','计算虚拟中点 mid，用 divmod(mid,n) 得到实际行 r、列 c。','比较 matrix[r][c] 与 target，相等返回 True；太小则 left=mid+1，太大则 right=mid−1。','闭区间为空时返回 False。整个过程中不创建展平列表。'],
 'invariant':'按行映射是虚拟下标与矩阵坐标的一一对应，且题目两条有序条件共同保证映射后的序列非递减。因此普通二分排除左右半边的论证完全适用，每次读取虚拟位置只需 O(1) 的下标换算。',
 'examples':[{'label':'虚拟下标映射到矩阵','input':'matrix=[[1,3,5],[7,9,11]], target=9','output':'True','frames':[
  {'title':'只在逻辑上展平','note':'两行三列映射为 [1,3,5,7,9,11]。这里用一维图帮助理解，实际代码仍读取原矩阵。','grid':[[1,3,5],[7,9,11]],'diagram':'虚拟下标：0  1  2 | 3  4  5\n实际坐标：(0,0)..(0,2) | (1,0)..(1,2)'},
  {'title':'mid=2，映射到 (0,2)','note':'初始范围 [0,5]，2//3=0、2%3=2，读到 5<9，因此排除虚拟下标 0..2。','grid':[[1,3,5],[7,9,11]],'active_cells':[[0,2]],'metrics':[['left',3],['right',5]]},
  {'title':'mid=4，映射到 (1,1)','note':'4//3=1、4%3=1，matrix[1][1]=9，找到目标返回 True。','grid':[[1,3,5],[7,9,11]],'active_cells':[[1,1]],'metrics':[['虚拟下标',4],['实际坐标','(1,1)']]}
 ]}],
 'walkthrough':['第一轮读虚拟下标 2，相当于检查第一行最后一格。它小于目标，因此整个第一行都可排除。','第二轮读虚拟下标 4。下标除以列数的商表示跨过多少完整行，余数表示在当前行走了几格。','矩阵如果只有一行，这个映射会自然退化为普通数组二分；只有一列时余数恒为 0。'],
 'code':'''
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        # 题目保证每行开头大于前一行末尾，因此可视作一个有序数组。
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1
        while left <= right:
            mid = left + (right - left) // 2
            # 用商和余数把虚拟一维下标还原为行、列，不复制矩阵。
            r, c = divmod(mid, n)
            value = matrix[r][c]
            if value == target:
                return True
            # 按虚拟有序数组做标准二分，一次排除一半元素。
            if value < target:
                left = mid + 1
            else:
                right = mid - 1
        return False
'''.strip(),
 'code_notes':['divmod 的除数必须是列数 n，因为每 n 个连续虚拟位置才构成一行；使用行数 m 会在非方阵上出错。','right=m*n−1 是最后一个虚拟元素下标；不是 m*n，也不是某个行号或列号。','本题返回 bool，找到时返回 True 即可，无需把虚拟下标转换成题目输出。'],
 'pitfalls':['只保证每行和每列分别有序还不足以保证按行拼接有序，第 240 题就是这种情况。','真正用列表推导式展平矩阵需要 O(mn) 时间和空间，即使随后二分很快，总过程也不符合本题的目标复杂度。','用方阵作为唯一测试会掩盖行数、列数混用问题，应测试 2×3 或 3×4。'],
 'complexity':'时间 O(log(mn))，虚拟空间每轮减半；额外空间 O(1)。',
 'quiz':{'question':'[[1,4],[2,5]] 每行每列都递增，可以用本题虚拟二分吗？','answer':'不可以。按行拼接得到 [1,4,2,5]，不是有序数组；第二行首元素 2 不大于上一行尾元素 4，违反本题额外的跨行条件。应考虑第 240 题的排除方法。'},
 'tests':{'method':'searchMatrix','cases':[{'args':[[[1,3,5],[7,9,11]],9],'expected':True},{'args':[[[1,3,5],[7,9,11]],8],'expected':False},{'args':[[[1]],1],'expected':True},{'args':[[[1],[3],[5]],4],'expected':False},{'args':[[[1,3,5]],5],'expected':True}]}
})

CHAPTER['problems'].append({
 'id':240,'slug':'search-a-2d-matrix-ii',
 'summary':'矩阵每行从左到右递增、每列从上到下递增，判断 target 是否出现。与第 74 题不同，本题不保证下一行首元素大于上一行尾元素。',
 'baseline':'每行单独二分需要 O(m log n)，是一种正确方案。把矩阵直接按行展平后做一次二分则不正确，因为行与行之间可能数值交错。若同时利用行和列的顺序，可以每次排除一整行或一整列。',
 'insight':'从右上角开始，当前位置是剩余首行的最大值，也是剩余最右列的最小值。若它大于目标，它下面整列都更大，应向左；若它小于目标，它左边整行都更小，应向下。每次比较因此有唯一明确的排除方向。',
 'steps':['初始化 r=0、c=n−1，候选区域是行 r..m−1、列 0..c 的矩形。','读取右上角 matrix[r][c]。相等则返回 True。','若当前值大于 target，当前列剩余部分全部太大，令 c-=1。','若当前值小于 target，当前行剩余部分全部太小，令 r+=1。','当 r 到达 m 或 c 小于 0，候选矩形为空，返回 False。'],
 'invariant':'若目标存在，它始终位于行 [r,m−1]、列 [0,c] 的剩余矩形。当前角点过大时，列有序性允许删除这一列；过小时，行有序性允许删除这一行。两种移动都不排除可能含目标的位置，且每次至少减少一行或一列。',
 'examples':[{'label':'右上角一路排除到目标 6','input':'matrix=[[1,4,7,11],[2,5,8,12],[3,6,9,16]], target=6','output':'True','frames':[
  {'title':'(0,3)=11 太大，排除最右列','note':'这一列剩余的 12、16 都不小于 11，也不可能是 6。向左到 (0,2)。','grid':[[1,4,7,11],[2,5,8,12],[3,6,9,16]],'active_cells':[[0,3],[1,3],[2,3]],'metrics':[['移动','c:3→2']]},
  {'title':'(0,2)=7 仍太大','note':'第 2 列的 7、8、9 都大于 6，再排除这一列。','grid':[[1,4,7,11],[2,5,8,12],[3,6,9,16]],'active_cells':[[0,2],[1,2],[2,2]],'metrics':[['移动','c:2→1']]},
  {'title':'(0,1)=4 太小，排除剩余首行','note':'第 0 行剩余的 [1,4] 都小于 6。已排除的右侧列无需再看，直接向下。','grid':[[1,4,7,11],[2,5,8,12],[3,6,9,16]],'active_cells':[[0,0],[0,1]],'metrics':[['移动','r:0→1']]},
  {'title':'(1,1)=5 太小，继续向下','note':'第 1 行剩余的 [2,5] 也都小于 6，排除这两个候选。','grid':[[1,4,7,11],[2,5,8,12],[3,6,9,16]],'active_cells':[[1,0],[1,1]],'metrics':[['移动','r:1→2']]},
  {'title':'(2,1)=6，找到目标','note':'只经过五次角点比较就确定存在。整个路径只向左或向下，绝不需要回头。','grid':[[1,4,7,11],[2,5,8,12],[3,6,9,16]],'active_cells':[[2,1]],'diagram':'访问角点：11 → 7 → 4 → 5 → 6'}
 ]}],
 'walkthrough':['看见 11 太大时，不能删除它所在整行，因为行内较小的元素仍可能等于目标。可以删除的是它下面全部不小于 11 的这一列。','看见 4 太小时，不能删除整列，因为下面可能有更大的目标；可以删除的是其左边全部不大于 4 的这一行。','右上角把两种大小关系分别导向左、下两个方向。左上角的右边和下边都更大，无法凭一次比较唯一确定应该排哪一边。'],
 'code':'''
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        m, n = len(matrix), len(matrix[0])
        # 从右上角开始：左边更小，下边更大，两个方向可分别排除。
        r, c = 0, n - 1
        while r < m and c >= 0:
            value = matrix[r][c]
            if value == target:
                return True
            # 当前值偏大，所在列下面更大，整列都可以跳过。
            if value > target:
                c -= 1
            else:
                # 当前值偏小，所在行左边更小，整行都可以跳过。
                r += 1
        return False
'''.strip(),
 'code_notes':['循环只需检查 r<m 和 c≥0，因为 r 从 0 开始只增大，c 从 n−1 开始只减小，另一侧边界天然不会越界。','同名 searchMatrix 是本题提交接口，每题代码单独提交；它与第 74 题的条件和实现不同。','每步只读一个角点，没有创建候选子矩阵或 visited 表。'],
 'pitfalls':['把大小对应的移动方向写反，会排掉可能含有答案的行或列。','该方法不是二分，候选数不保证每次减半，不能标注 O(log(mn))。','从左上角开始并按大小随意选右或下，没有相同的排除依据。'],
 'complexity':'时间 O(m+n)，r 最多前进 m 次，c 最多后退 n 次；额外空间 O(1)。',
 'alternative':'也可以从左下角开始：过大时向上，过小时向右。每行二分的 O(m log n) 方案同样正确，某些狭长矩阵上也值得比较；核心是依据给定有序性选择搜索方式。',
 'quiz':{'question':'为什么本题不能把第一行末尾小于 target 当作整张矩阵无解？','answer':'第一行末尾只是第一行最大值，后续行可以出现更大值。只能排除第一行，不能排除后续行。阶梯搜索用 r+=1 保留下面的候选。'},
 'tests':{'method':'searchMatrix','cases':[{'args':[[[1,4,7,11],[2,5,8,12],[3,6,9,16]],6],'expected':True},{'args':[[[1,4],[2,5]],2],'expected':True},{'args':[[[1,4],[2,5]],3],'expected':False},{'args':[[[1],[3],[5]],5],'expected':True},{'args':[[[1,3,5]],0],'expected':False}]}
})

CHAPTER['problems'].append({
 'id':153,'slug':'find-minimum-in-rotated-sorted-array',
 'summary':'严格升序、元素互不相同的数组经过若干次旋转，寻找最小值。旋转零次或一整圈也可能发生，要求 O(log n) 时间。',
 'baseline':'直接使用 min(nums) 需要 O(n) 时间。观察相邻元素的下降点也可以找到最小值，但顺序扫描下降点仍是线性。旋转后只有一处从较大段跳到较小段，可以通过中点与右端值判断最小值在哪一侧。',
 'insight':'比较 nums[mid] 与 nums[right]。如果中点更大，说明从 mid 到 right 跨越了旋转断点，最小值必在 mid 右边；如果中点更小，则 mid..right 这段有序，最小值不可能在 mid 之后，应保留左侧连同 mid。',
 'steps':['用闭区间 [left,right]=[0,n−1] 保留最小值候选，循环条件为 left<right。','计算向下取整的 mid。因为 left<right，所以 mid<right，可以比较两个不同位置。','若 nums[mid]>nums[right]，令 left=mid+1；mid 肯定不是最小值。','否则令 right=mid，mid 本身可能是最小值，不能跳过。','左右相遇后返回 nums[left]，题目要求最小值而不是它的下标。'],
 'invariant':'最小值始终处在闭区间中。中点大于右端时，右端所在的低值段至少有一个数小于中点，断点在右半边；中点小于右端时，mid 之后是递增段，不会出现比 mid 更小的元素，所以最小值在 left..mid。无重复且 mid<right，比较时不会出现相等歧义。',
 'examples':[{'label':'断点位于右半边','input':'nums=[4,5,6,7,0,1,2]','output':'0','frames':[
  frame([4,5,6,7,0,1,2],0,6,3,'7 大于右端 2','mid 位于高值段，最小值一定在右半边。left=4。'),
  frame([4,5,6,7,0,1,2],4,6,5,'1 小于右端 2','[1,2] 已经有序，中点之后没有更小值；right=5，保留中点。'),
  frame([4,5,6,7,0,1,2],4,5,4,'0 小于右端 1','right=4，与 left 相同。返回 nums[4]=0。')
 ]},{'label':'没有旋转也使用同一逻辑','input':'nums=[1,2,3]','output':'1','frames':[
  frame([1,2,3],0,2,1,'2 小于右端 3','最小值在左边或中点，right=1。'),
  frame([1,2,3],0,1,0,'1 小于右端 2','right=0，返回 nums[0]=1。无需专门寻找一定存在的下降点。')
 ]}],
 'walkthrough':['第一次比较 7 与 2，大值出现在小值前面，证明断点尚在这两者之间，因此可一口气丢弃 4、5、6、7。','剩余 [0,1,2] 虽然已经有序，统一逻辑仍能工作：不断保留左半边，最终来到 0。','两元素 [2,1] 时 mid 在左端，比较结果大于右端，left=mid+1 正好前进到最小值，不会死循环。'],
 'code':'''
class Solution:
    def findMin(self, nums: list[int]) -> int:
        # 最小值始终在闭区间内；原题元素互不相同。
        left, right = 0, len(nums) - 1
        while left < right:
            mid = left + (right - left) // 2
            # 中点位于旋转前的较大段，最小值一定严格在右边。
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                # 中点落在较小段，自己可能最小，所以保留 mid。
                right = mid
        return nums[left]
'''.strip(),
 'code_notes':['比较参照是当前 right，不是一个不随搜索区间变化的局部相邻值。区间缩小时，右端依然提供判定半边的参照。','right=mid 保留最小值恰好在 mid 的可能性。','只剩一个候选就已经确定最小值，不需要再做相邻比较，因此 while 使用 <。'],
 'pitfalls':['题目不要求一定发生有效旋转，不能只在找到 nums[i]>nums[i+1] 时返回而漏掉有序输入。','返回值是 nums[left]，不是 left。','若允许重复元素，nums[mid]==nums[right] 时无法依同一判断排除一半，需要额外处理，最坏可能退化为 O(n)。'],
 'complexity':'时间 O(log n)，额外空间 O(1)。这一最坏时间保证依赖元素互不相同。',
 'quiz':{'question':'为什么中点小于右端时写 right=mid，而不是 mid−1？','answer':'中点本身可能就是最小值，例如 [3,1,2] 的初始 mid=1，值为 1。写 mid−1 会把真正答案排除。保留 mid 后继续缩小区间才正确。'},
 'tests':{'method':'findMin','cases':[{'args':[[4,5,6,7,0,1,2]],'expected':0},{'args':[[1,2,3]],'expected':1},{'args':[[2,1]],'expected':1},{'args':[[3,1,2]],'expected':1},{'args':[[7]],'expected':7}]}
})

CHAPTER['problems'].append({
 'id':33,'slug':'search-in-rotated-sorted-array',
 'summary':'严格升序且元素互不相同的数组经过旋转，在其中查找 target，存在返回下标，不存在返回 −1，要求 O(log n) 时间。这里不只找最小值，而是定位任意目标。',
 'baseline':'线性查找 O(n)；也可以先用第 153 题定位最小值，把数组分成两段有序区间，再选择其中一段二分。更直接的方法是在每一轮识别哪一半有序，然后判断目标是否处在该有序范围。',
 'insight':'旋转断点至多一个，因此以 mid 为界，左半边或右半边至少有一边有序。若 nums[left]≤nums[mid]，左半边有序；否则右半边有序。在已经确认有序的那一半，用端点值就能判断目标是否可能在里面。',
 'steps':['初始化闭区间 [0,n−1]。每轮先检查 nums[mid]==target，命中立即返回。','若 nums[left]≤nums[mid]，确认左半边有序。target 落在 nums[left]≤target<nums[mid] 时向左搜，否则向右搜。','否则右半边有序。target 落在 nums[mid]<target≤nums[right] 时向右搜，否则向左搜。','因为 mid 已确认不等于目标，所有分支均用 mid−1 或 mid+1 排除它。','候选区间为空则返回 −1。'],
 'invariant':'若目标存在，它始终在当前候选区间。每轮先确认一半有序，再用该半边的端点值判断目标范围；若目标不在这段有序范围，它只能去另一半。无重复值保证端点判断不会因为相等大段而产生歧义。',
 'examples':[{'label':'先排除有序但不含目标的左半边','input':'nums=[4,5,6,7,0,1,2], target=0','output':'4','frames':[
  frame([4,5,6,7,0,1,2],0,6,3,'左半边 [4,5,6,7] 有序','4≤7，但目标 0 不在 [4,7) 内，故它不在左半边。left=4。'),
  frame([4,5,6,7,0,1,2],4,6,5,'左半边 [0,1] 有序且含目标范围','0≤target<1 成立，right=4。虽然右半边也有序，确认一半并据此排除已经足够。'),
  frame([4,5,6,7,0,1,2],4,4,4,'命中目标 0','返回下标 4。闭区间只有一个位置时仍要检查相等。')
 ]},{'label':'两元素与有序判断中的等号','input':'nums=[3,1], target=1','output':'1','frames':[
  frame([3,1],0,1,0,'mid 与 left 是同一位置','nums[left]≤nums[mid] 成立，单元素左半边也算有序。target 不在 [3,3) 内，left=1。'),
  frame([3,1],1,1,1,'命中下标 1','若判断左半边有序时遗漏等号，可能误认右半边 [3,1] 有序并错误排除目标。')
 ]}],
 'walkthrough':['第一轮并不要求整个数组有序；只需要知道左半边 [4,5,6,7] 有序，而 0 不在它的值域中，就能把它排除。','第二轮已经落入低值段 [0,1,2]，仍复用相同分支。不必在代码里先判断“现在已经完全有序了”。','两元素例子说明 nums[left]≤nums[mid] 的等号用于识别单元素有序半边，而目标范围里排除 mid 的严格不等号来自“已检查中点不相等”。'],
 'code':'''
class Solution:
    def search(self, nums: list[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid
            # 无重复元素时，左右两段至少有一段有序；先判断左段。
            if nums[left] <= nums[mid]:
                # 目标落在左侧有序范围内，才向左收缩；否则去右侧。
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                # 左侧无序则右侧必有序，用右段范围决定去留。
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1
        return -1
'''.strip(),
 'code_notes':['Python 支持链式比较 a≤target<b，其含义是两个比较同时成立。这里直接表达目标是否属于有序半边的值域。','外层分支是在识别有序半边，内层分支才是在判断目标范围；先说清这两个问题，代码就不只是四个难记的方向。','所有区间更新都排除 mid，因此最大候选数约减半，且单元素区间仍能终止。'],
 'pitfalls':['不要因为 nums[mid]>target 就直接向左。中点可能在高值段而目标在右侧低值段。','识别左半边有序时需要 ≤，否则 [3,1] 这类两元素输入容易错。','若扩展题允许重复值，端点相等时可能无法判断哪一半严格有序，要另行处理。'],
 'complexity':'时间 O(log n)，额外空间 O(1)，依赖无重复元素的条件。',
 'quiz':{'question':'nums=[4,5,6,7,0,1,2]，mid 值为 7，target=1，为什么不能因 7>1 就向左？','answer':'7 左边虽然都是比 7 小的高值段元素，但 1 位于旋转之后的右侧低值段。必须先识别左半边有序，再发现 1 不在 [4,7) 中，才能正确选择右侧。'},
 'tests':{'method':'search','cases':[{'args':[[4,5,6,7,0,1,2],0],'expected':4},{'args':[[4,5,6,7,0,1,2],3],'expected':-1},{'args':[[3,1],1],'expected':1},{'args':[[1],1],'expected':0},{'args':[[1,2,3],3],'expected':2},{'args':[[5,1,2,3,4],5],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':162,'slug':'find-peak-element',
 'summary':'寻找一个严格大于相邻元素的峰值，返回它的下标。有多个峰值时返回任意一个即可。数组两端外侧视为负无穷，题目保证相邻元素不相等，并要求 O(log n) 时间。',
 'baseline':'顺序检查每个元素是否大于左右邻居需要 O(n)。找全局最大值也能得到某个峰值，但仍是线性。题目只要求任意峰值，不必保留所有峰值候选，这让我们能根据中间的上升或下降方向保留必有峰值的一半。',
 'insight':'比较 nums[mid] 和 nums[mid+1]。若向右上升，则沿右侧继续上升，最终要么遇到下降形成峰值，要么一直升到最右端，最右端与外侧负无穷相比也是峰值。若向右下降，则 mid 或其左侧一定能保留一个峰值。注意坡度本身可以反复变化，不是在二分一个全局单调的坡度数组。',
 'steps':['初始化闭区间 [0,n−1]，其中一定至少有一个峰值。','当 left<right 时取向下取整的 mid，因此 mid+1≤right，不会访问越界。','若 nums[mid]<nums[mid+1]，朝上升方向保留右侧，令 left=mid+1。','否则向右下降，保留左侧连同 mid，令 right=mid。','只剩一个位置时返回其下标。不要返回最大值，也不需要找出全部峰值。'],
 'invariant':'保持区间左边界比它外侧左邻居高，右边界比它外侧右邻居高，数组之外按负无穷处理。向右上升时新 left=mid+1 高于被排除的 mid；向右下降时新 right=mid 高于被排除的 mid+1。区间两端都向内部围住一个山峰，最终唯一位置必高于两侧邻居。',
 'examples':[{'label':'多个峰值，只保留其中一个','input':'nums=[1,2,1,3,5,6,4]','output':'本解法返回 5；下标 1 也符合题意','frames':[
  frame([1,2,1,3,5,6,4],0,6,3,'3 → 5 向右上升','比较下标 3、4，保留 [4,6]。左边下标 1 虽然也是峰值，但题目只需要任意一个，可以舍弃它。'),
  frame([1,2,1,3,5,6,4],4,6,5,'6 → 4 向右下降','mid=5 本身就可能是峰值，right=5，保留 [4,5]。'),
  frame([1,2,1,3,5,6,4],4,5,4,'5 → 6 向右上升','left=5，与 right 重合。下标 5 的值为 6，大于左邻 5 和右邻 4。')
 ]},{'label':'严格递增数组的峰值在端点','input':'nums=[1,2,3]','output':'2','frames':[
  frame([1,2,3],0,2,1,'2 → 3 向右上升','left=2，剩余下标 2。右端外侧视作负无穷，所以最后的 3 是峰值。'),
  {'title':'端点也是合法峰值','note':'题目允许端点：3>2，且 3>负无穷。只寻找内部转折点会漏掉这种输入。','array':[1,2,3],'active':[2],'diagram':'1 < 2 < 3 > −∞'}
 ]}],
 'walkthrough':['初始数组有两个峰值，算法第一轮把较早的一个排除了。这不违反正确性，因为目标是找到任意峰值。','每轮保留的区间仍有比外侧邻居更高的两端，从这个区间的最大值出发就能保证至少存在一个严格局部峰值，相邻元素不等确保不是平坦平台。','当只剩下标 5，左右边界的两条性质合并成它严格高于左右相邻值，所以无需额外线性验证才返回。'],
 'code':'''
class Solution:
    def findPeakElement(self, nums: list[int]) -> int:
        left, right = 0, len(nums) - 1
        while left < right:
            mid = left + (right - left) // 2
            # 当前向右上坡，沿这个方向必能遇到某个峰值。
            if nums[mid] < nums[mid + 1]:
                left = mid + 1
            else:
                # 当前向右下坡，峰值在左边或就是 mid，必须保留中点。
                right = mid
        return left
'''.strip(),
 'code_notes':['mid 向下取整且 left<right，保证 mid<right，所以 mid+1 合法。这是相邻比较不会越界的依据。','else 在题目条件下表示严格下降，因为相邻元素不相等；不是把任意相等平台也当作严格峰值。','返回 left 是峰值下标。它不一定是全局最大值的下标，也不一定是最左峰值。'],
 'pitfalls':['不能认为原数组必须有序，本题允许反复上升下降。','nums[mid]<nums[mid+1] 的真假也不保证全局单调，正确性来自“保留区间仍有峰值”。','若把条件推广到允许相邻相等，原证明会失效，平坦数组甚至没有严格峰值，需要重新定义题意或算法。'],
 'complexity':'时间 O(log n)，每轮保留不超过约一半的位置；额外空间 O(1)。',
 'quiz':{'question':'如果本题改为返回最左边的峰值，这份代码还能保证正确吗？','answer':'不能。本例第一轮已丢弃下标 1 的峰值而返回下标 5。原算法只保证保留某个峰值，无法保证保留最左峰值，需求改变后必须重新论证。'},
 'tests':{'method':'findPeakElement','cases':[{'args':[[1,2,1,3,5,6,4]],'expected':5},{'args':[[1,2,3,1]],'expected':2},{'args':[[1,2,3]],'expected':2},{'args':[[3,2,1]],'expected':0},{'args':[[7]],'expected':0},{'args':[[1,3,2,4,1]],'expected':3}]}
})

CHAPTER['problems'].append({
 'id':4,'slug':'median-of-two-sorted-arrays',
 'summary':'给定两个升序数组，返回合在一起后的中位数。总长度为奇数时取中间那个值，为偶数时取中间两个值的平均数。允许其中一个数组为空，但总长度至少为 1，要求对数级时间。',
 'baseline':'像归并排序一样合并两个数组，时间 O(m+n)、空间 O(m+n)。也可以只用双指针走到中间，省下输出空间，但时间仍是线性。为了达到对数时间，不能逐个找出前半部分的所有值，需要直接定位左右两半的分割位置。',
 'insight':['中位数只关心两个条件：左右两半数量平衡，且左边所有值都不大于右边所有值。假设从 A 取前 i 个、从 B 取前 j 个放左边。令 left_size=(m+n+1)//2，并规定 i+j=left_size，左边就会与右边同样多，或恰好多一个。','i 确定后 j 自动确定，所以只需二分 i。两个数组内部已经有序，剩下只需检查跨数组的两条关系：A 左边最大值≤B 右边最小值，B 左边最大值≤A 右边最小值。两条都成立时，分割线就正确了。'],
 'steps':['先确保 A 是较短数组，长度 m≤n。二分的是“取多少个 A 元素到左边”，所以 i 的范围是 0..m，共 m+1 个切分位置。','固定左半总数 left_size=(m+n+1)//2。每轮取 i=(left+right)//2，令 j=left_size−i。','读取切分线周围四个值：A[i−1]、A[i]、B[j−1]、B[j]。若切在某数组最左侧，把其左值视为负无穷；若切在最右侧，把其右值视为正无穷。','若 A_left≤B_right 且 B_left≤A_right，分割正确。总长度奇数时返回 max(A_left,B_left)；偶数时返回它与 min(A_right,B_right) 的平均数。','若 A_left>B_right，说明从 A 取到左边的元素过多，应减小 i，令 right=i−1。否则 B_left>A_right，说明从 A 取少了，应增大 i，令 left=i+1。'],
 'invariant':['始终只搜索可能产生正确分割的 i，且 j 由数量条件唯一决定。m≤n 保证所有 i∈[0,m] 对应的 j 都在 [0,n] 内，无需额外修补越界切分。','若 A_left>B_right，增大 i 会让 A_left 不减，同时 j 减小使 B_right 不增，因此错误不可能被右移修复，必须左移。反方向同理。二分由此安全排除半边。','正确分割时，A 与 B 内部有序，加上两条跨数组比较，就能保证整个左半不大于整个右半。数量条件让中位数必在分割线邻近，因而无需真的合并两数组。'],
 'examples':[{'label':'11 个数：只调整两次分割','input':'A=[1,3,8,9,15], B=[7,11,18,19,21,25]','output':'11.0','frames':[
  {'title':'先固定左半总共 6 个','note':'总长度 11，左边取 (11+1)//2=6 个，比右边多一个。只需找到符合大小关系的两条切分线。','diagram':'A: 1  3  8  9  15\nB: 7  11  18  19  21  25\n\nA 左侧取 i 个，B 左侧取 j=6−i 个。','metrics':[['左半数量',6],['右半数量',5]]},
  {'title':'尝试 i=2，j=4：A 取少了','note':'左侧 A 最大值 3≤右侧 B 最小值 21，但左侧 B 最大值 19>右侧 A 最小值 8。19 不应排在 8 左边，需要把更多 A 元素划到左边。','diagram':'A: 1  3       | 8  9  15\nB: 7  11  18  19 | 21  25\n\nA_left=3  A_right=8\nB_left=19 B_right=21\n19 > 8：i 需要增大，候选 i 从 [0,5] 变成 [3,5]。'},
  {'title':'尝试 i=4，j=2：两条关系都成立','note':'9≤18 且 11≤15。左侧共有 [1,3,8,9] 与 [7,11] 六个数，最大值为 11；右侧的所有数都至少为 15。','diagram':'A: 1  3  8  9 | 15\nB: 7  11      | 18  19  21  25\n\nmax(left)=max(9,11)=11\nmin(right)=min(15,18)=15','equation':'总长度为奇数 → 中位数 = 左半最大值 = 11.0'}
 ]},{'label':'偶数长度：分割线两侧取平均','input':'A=[1,2], B=[3,4]','output':'2.5','frames':[
  {'title':'i=1、j=1，跨数组关系不成立','note':'A 左边 [1]、右边 [2]；B 左边 [3]、右边 [4]。3>2，A 取少了，要增加 i。','diagram':'A: 1 | 2\nB: 3 | 4\n\nB_left=3 > A_right=2'},
  {'title':'i=2、j=0，使用边界哨兵','note':'A 全部放左边，B 全部放右边。A 右侧为空视为 +∞，B 左侧为空视为 −∞，两条比较自然成立。','diagram':'A: 1  2 | +∞\nB: −∞   | 3  4\n\n左半最大 2，右半最小 3','equation':'中位数 = (2+3)/2 = 2.5'}
 ]},{'label':'短数组为空','input':'A=[], B=[2,4,6]','output':'4.0','frames':[
  {'title':'只有一种 A 的切法 i=0','note':'左半需要 2 个元素，所以 j=2。A 的左右边界用负、正无穷表示，B 在 4 和 6 之间分割，左半最大为 4。','diagram':'A: −∞ | +∞\nB: 2  4 | 6\n\nmax(−∞,4)=4 → 返回 4.0'}
 ]}],
 'walkthrough':['11 元素例子中，i=2 时左半虽然已经有 6 个元素，但它们不是最小的 6 个：19 被放在左边，8 却在右边。数量正确还不够，必须检查大小关系。','把 i 增大到 4 后，j 自动减小到 2。这样在总数量不变的同时，用较小的 A 元素替换过大的 B 左侧元素，最终满足两条跨数组条件。','奇数长度规定左侧多一个，故中位数取左侧最大值。偶数长度左右相同多，中间两个数分别是左侧最大和右侧最小。','i、j 表示左边取了多少个，不是左边最后一个下标。左侧最后下标分别为 i−1、j−1，这也是边界特判的来源。'],
 'code':'''
class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        a, b = nums1, nums2
        # 只在较短数组上二分，使另一数组的分割位置始终合法。
        if len(a) > len(b):
            a, b = b, a
        m, n = len(a), len(b)
        # 左半部分多放一个元素；总数为奇数时，中位数就是左半最大值。
        left_size = (m + n + 1) // 2
        left, right = 0, m
        while left <= right:
            i = left + (right - left) // 2
            # a 左边取 i 个、b 左边取 j 个，合起来恰好为 left_size。
            j = left_size - i
            # 分割靠边时用无穷小/大作哨兵，统一处理空的一侧。
            a_left = a[i - 1] if i > 0 else float('-inf')
            a_right = a[i] if i < m else float('inf')
            b_left = b[j - 1] if j > 0 else float('-inf')
            b_right = b[j] if j < n else float('inf')

            # 两条交叉不等式都成立，说明左半所有值不大于右半所有值。
            if a_left <= b_right and b_left <= a_right:
                if (m + n) % 2 == 1:
                    return float(max(a_left, b_left))
                return (max(a_left, b_left) + min(a_right, b_right)) / 2
            # a 左边取多了，要左移分割；反之需要右移。
            if a_left > b_right:
                right = i - 1
            else:
                left = i + 1
        raise ValueError('输入需为有序数组，且总长度至少为 1')
'''.strip(),
 'api':{'signature':'float(x) -> float','description':['float 可将整数或表示数字的字符串转换成浮点数；float("inf") 与 float("-inf") 分别构造正、负无穷。这里仅把它们用作空半边的比较哨兵，不是真实数组元素。','题目保证总长度至少为 1，因此正确分割后用于返回的中间元素一定来自非空数据，不会把无穷当作实际中位数。该代码按题目约束使用，不通过末尾异常全面验证任意无序输入。']},
 'code_notes':['a,b=nums1,nums2 与后续交换只改变局部引用，不复制、不排序、不修改输入，因此不会暗中增加线性预处理。','搜索范围是 [0,m] 而不是 [0,m−1]，因为取零个与取全部 m 个都是合法切法。','条件表达式先判断 i>0 才读取 a[i−1]，避免 i=0 时 Python 负下标悄悄读到末尾元素。其他边界也同理。','两条跨数组比较使用 ≤，重复值也能正确分割。偶数答案用 / 保留小数，不能用 // 截断。','m≤n 时 left_size 不小于 m 且不大于 n，因此 0≤left_size−i≤n。交换成短数组二分同时保证了 j 的合法性与更小的搜索范围。'],
 'pitfalls':['只平衡左右数量而不检查交叉大小，会把“左半”误认为“较小的一半”。','把 j 写成 left_size−i−1 是把元素个数与下标混淆，容易让总数量少一。','没有用短数组做二分时，j 可能落在 0..n 之外，必须另行收紧 i 的合法范围。','不能把两个数组各自的中位数取平均代替合并后的中位数，长度与数值分布都会影响整体中间位置。'],
 'complexity':'时间 O(log(min(m,n)+2))，在较短数组的 m+1 个切分位置中二分；额外空间 O(1)。不需要合并数组。',
 'quiz':{'question':'为什么 A_left>B_right 时必须减小 i，而不是增加 i？','answer':'增加 i 会让 A 左侧最大值不变或更大；同时 j 减小，B 右侧最小值不变或更小，错误只会维持或加重。减小 i 才能把偏大的 A 元素移回右边，并把更多 B 元素划到左边。'},
 'tests':{'method':'findMedianSortedArrays','cases':[{'args':[[1,3,8,9,15],[7,11,18,19,21,25]],'expected':11.0},{'args':[[1,2],[3,4]],'expected':2.5},{'args':[[1,3],[2]],'expected':2.0},{'args':[[],[2,4,6]],'expected':4.0},{'args':[[0,0],[0,0]],'expected':0.0},{'args':[[-5,-3],[-2]],'expected':-3.0},{'args':[[2],[]],'expected':2.0}]}
})
