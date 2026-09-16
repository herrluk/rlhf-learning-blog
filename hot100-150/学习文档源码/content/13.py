from textwrap import dedent

CHAPTER = {
 'lead':'回溯把一个完整答案拆成一串选择。先定义当前路径代表什么，再规定下一步能选什么、何时收集答案，以及返回上一层时必须恢复哪些状态。',
 'intro':['学习顺序：78 子集 → 46 全排列 → 47 重复值排列 → 17 逐位置组合 → 39 可重复组合 → 22 合法括号 → 131 回文切分 → 93 IP 切分 → 79 网格路径 → 51 棋盘约束。每题都在同一套“选择、递归、撤销”框架中改变具体约束。','本章题目限制使递归深度较小：数组长度、字符串长度、棋盘行数都有限；组合总和的候选是至少 2 的正数，目标至多 40。这里使用递归能清晰呈现决策过程，不依赖人为调高 Python 的递归上限。','图中的一层通常表示一次选择，并不一定对应输入数组下标。排列的一层是结果位置，组合的 start 是候选下标下界，切分的 start 是尚未消费的字符串位置，三者不能混用。'],
 'sections':[
  {'title':'先确定五件事，再写递归','body':['状态：已选路径、剩余目标、已使用元素或冲突集合。选择：当前这一层能尝试的候选。结束：什么条件下形成完整答案。剪枝：什么条件能证明此分支不可能成功。撤销：哪些可变状态必须恢复。','一次分支的顺序是“加入选择→递归探索→撤销选择”。path.append 与 path.pop 应成对出现，used 或集合的修改也一样。','返回答案时保存快照。整数路径使用 path.copy()；字符路径可以用 join 生成不可变字符串。'], 'diagram':'当前状态\n  ├─ 选择 A → 修改状态 → 探索 → 撤销 A\n  ├─ 选择 B → 修改状态 → 探索 → 撤销 B\n  └─ 选择 C → 修改状态 → 探索 → 撤销 C'},
  {'title':'组合、排列、切分使用不同的下一步规则','body':['组合不关心顺序。让候选下标单调增加，就不会同时生成 [2,3] 和 [3,2]；允许重复取同一个候选时，递归仍从 i 开始。','排列关心顺序。每层都要从全部候选里找当前路径尚未使用的下标，不能用单调 start 禁止后面再选较小下标。','切分必须按原字符串顺序消费连续片段，下一层起点等于刚选片段末尾的后一位。'], 'diagram':'不重复组合：choose i → search(i+1)\n可重复组合：choose i → search(i)\n排列：choose 未使用的 i → used[i]=True\n切分：choose s[start:end+1] → search(end+1)'},
  {'title':'同层去重与同一路径重复使用是两回事','body':['[1,1,2] 中两个 1 是两个输入位置，同一排列可以都用，但交换这两个相同值不应产生新的答案。','同层去重规定：同一层从相同值的候选中只选一个代表。排序后，如果前一个同值位置没有在当前路径使用，就跳过后一个；如果前一个已经在路径里，后一个仍可以用于下一个位置。','不要用一个全局“见过这个值”的集合禁止所有重复值，那会连合法的 [1,1,2] 也删掉。']},
  {'title':'输出本身可能是主要成本','body':['子集有 2^n 个，全排列有 n! 个。即使搜索没有重复，完整返回它们也要付出存储每个答案的成本。','复杂度应同时计入搜索节点、路径复制或字符串拼接，以及输出结果；不能因为每次只做 append/pop 就写成 O(n)。','剪枝的依据必须来自题目约束。正数目标和可以因“当前候选大于剩余目标”停止，但包含负数时这个规则不再成立。']}
 ],
 'apis':[
  {'signature':'path.append(x) -> None；path.pop() -> 被移除的末尾元素','description':['append 原地追加一个元素，pop 从末尾移除并返回。用列表作当前路径，末端追加与撤销都是摊还 O(1)。','保存答案要使用 path.copy()。直接 append(path) 存的是同一列表引用，后续撤销会改变已经收集的答案。']},
  {'signature':'sorted(nums) -> 新的有序列表','description':['创建新列表后排序，保留输入 nums。区别于 nums.sort()：后者原地排序并返回 None。','47、39 使用排序后的邻近值或大小关系来去重、剪枝。排序不是装饰，删除排序步骤后相关 break 或相邻去重就不成立。']},
  {'signature':"''.join(path) -> str；'.'.join(parts) -> str",'description':['join 以给定分隔符把字符串列表连接为一个新字符串。括号和字母路径使用空分隔符，IP 段使用点。','join 的时间与最终字符串长度有关；它得到不可变的独立结果，随后 path.pop() 不会改变已保存字符串。']}
 ],
 'problems':[]
}

def checks(method, pairs, **options):
    return dict(method=method, cases=[dict(args=args,expected=expected) for args,expected in pairs], **options)

CHAPTER['problems'].append({
 'id':78,'slug':'subsets',
 'summary':'给定互不相同的整数，返回全部子集，包含空集。答案次序不限，每个子集不能重复。',
 'baseline':'枚举每个元素“选或不选”的二进制掩码可以得到所有子集。回溯则直接沿已选路径扩展，每个搜索节点代表一个子集，不必等路径达到固定长度才收集。',
 'insight':'path 保存当前已选元素，start 限制下一项只能从后面的下标选择。每进入 dfs 就保存 path，然后依次选择 i≥start，下一层从 i+1 继续。每个下标组合都按递增顺序出现，天然消除顺序重复。',
 'steps':['result=[]、path=[]，调用 dfs(0)。','进入 dfs(start) 时先保存当前 path 副本。','枚举 i 从 start 到末尾，加入 nums[i]。','递归 dfs(i+1)，返回后弹出刚加入的值。','所有分支结束后返回 result。'],
 'invariant':'path 对应严格递增的输入下标序列。加入更大的下标不会重复使用元素，任何子集都有唯一的递增下标表示，因此不重复；沿它的下标次序逐步选择，又保证每个子集都能到达。',
 'examples':[{'label':'每个搜索节点都能成为答案','input':'nums=[1,2,3]','output':'8 个子集：[]、[1]、[1,2]、[1,2,3]、[1,3]、[2]、[2,3]、[3]','frames':[
  {'title':'空路径也要保存','note':'根搜索节点对应空集，不能漏掉。','diagram':'[]\n├─ [1]\n├─ [2]\n└─ [3]','metrics':[['已保存','[[]]']]},
  {'title':'选择 1 后只向后扩展','note':'下一项可以是 2 或 3，不能再次选 1，也不再回头选择较小下标。','diagram':'[1]\n├─ [1,2]\n│  └─ [1,2,3]\n└─ [1,3]'},
  {'title':'返回根继续其他起点','note':'退出 [1] 分支后 path 恢复为空，继续选择 2、3。','table':{'headers':['根分支','产生的非空子集'],'rows':[['选1','[1]、[1,2]、[1,2,3]、[1,3]'],['选2','[2]、[2,3]'],['选3','[3]']]}}
 ]}],
 'walkthrough':['保存 path 放在 dfs 入口，所以长度 0、1、2、3 的子集都能收集。','dfs(i+1) 同时避免重复使用当前元素和产生顺序相反的同一子集。','即使输入没有排序也正确，因为单调的是输入下标，不要求数值递增。'],
 'code':'''
class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        result = []
        path = []
        # start 限制下一次只能选更右的数，避免同一子集以不同顺序出现。
        def dfs(start: int) -> None:
            # 每个递归状态本身都是一个子集，包括一开始的空集；必须保存副本。
            result.append(path.copy())
            for i in range(start, len(nums)):
                path.append(nums[i])
                # 选过下标 i 后从 i+1 继续，同一个元素不能重复使用。
                dfs(i + 1)
                # 撤销本次选择，恢复父状态，再尝试下一个候选。
                path.pop()
        dfs(0)
        return result
'''.strip(),
 'code_notes':['没有固定长度的成功条件；所有前缀都是合法子集。','len(nums)==start 时循环为空，自然返回，不需额外分支。','path.copy() 让不同答案独立，nums 保持原样。'],
 'pitfalls':['只在路径长度达到 n 时收集，漏掉短子集。','下一层仍从 0 开始，重复使用元素并生成顺序重复。','保存同一个 path 引用。'],
 'complexity':'时间 O(n·2^n)，输出中所有子集的总元素数为 n·2^(n-1)；辅助路径与递归栈 O(n)，输出空间 O(n·2^n)。',
 'quiz':{'question':'输入 [3,1] 是否必须排序才能避免重复？','answer':'不需要。只按下标向后选，得到 []、[3]、[3,1]、[1]，四个子集都唯一。'},
 'tests':checks('subsets',[([[1,2,3]],[[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]),([[0]],[[],[0]]),([[3,1]],[[],[3],[3,1],[1]])],compare='groups',preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':46,'slug':'permutations',
 'summary':'给定互不相同的整数，返回每个元素恰好使用一次的所有排列。顺序不同就是不同答案。',
 'baseline':'像子集一样限制下标只向后走，只能形成一种相对顺序，无法得到 [2,1,3]。排列需要在每个结果位置重新考虑所有尚未使用的元素。',
 'insight':'path 长度表示正在填写的结果位置，used[i] 表示输入下标 i 是否已被当前路径占用。每层遍历全部下标，选未使用项，完成选择后递归，退出时同时撤销 path 与 used。',
 'steps':['建立长度 n 的 used=False 数组。','若 path 长度为 n，保存副本并返回。','否则枚举全部 i，跳过 used[i]。','标记 i、追加 nums[i]，递归填下一个位置。','返回后弹出值并恢复 used[i]=False。'],
 'invariant':'path 包含互不相同的输入位置，used 恰好标识这些位置。每层选择一个剩余位置，所以长度 n 时正好用尽全部元素。任何排列都对应唯一的位置选择序列，所有未使用候选都被尝试，因此完整且不重复。',
 'examples':[{'label':'回到上一层时同时恢复两个状态','input':'nums=[1,2,3]','output':'6 个排列','frames':[
  {'title':'先固定第一个位置为 1','note':'used=[True,False,False]，第二个位置仍可选下标 1 或 2。','diagram':'[1]\n├─ [1,2] → [1,2,3]\n└─ [1,3] → [1,3,2]'},
  {'title':'从 [1,2,3] 回退','note':'弹出 3 并清除它的 used，再退出 2，才有机会在第二位选择 3。','table':{'headers':['状态','path','used'],'rows':[['完成','[1,2,3]','[T,T,T]'],['退出3','[1,2]','[T,T,F]'],['退出2','[1]','[T,F,F]']]}},
  {'title':'根层还要尝试 2、3','note':'所有首元素分别产生两个排列，共 3!=6。','table':{'headers':['首元素','对应排列'],'rows':[[1,'123、132'],[2,'213、231'],[3,'312、321']]}}
 ]}],
 'walkthrough':['这里不能把递归参数改成 i+1，因为先选下标 1 的值 2 后，下一位仍应允许选择下标 0 的值 1。','只撤销 path 而不撤销 used，会让其他分支以为该元素仍被占用。','题目元素不同，所以输入位置序列与输出值序列一一对应；47 将处理值重复后的额外问题。'],
 'code':'''
class Solution:
    def permute(self, nums: list[int]) -> list[list[int]]:
        n = len(nums)
        result, path = [], []
        # used 按下标标记当前排列已经用过的元素。
        used = [False] * n
        def dfs() -> None:
            # 选满 n 个位置才形成完整排列，保存路径快照。
            if len(path) == n:
                result.append(path.copy())
                return
            for i in range(n):
                # 当前路径用过的下标不能再次选，但其他分支仍可使用。
                if used[i]:
                    continue
                used[i] = True
                path.append(nums[i])
                dfs()
                # 递归返回后同时撤销路径与 used，保持每次尝试互不影响。
                path.pop()
                used[i] = False
        dfs()
        return result
'''.strip(),
 'code_notes':['used 按下标记录，恰好对应输入元素是否已放入当前排列。','函数对外返回 result，内部 dfs 只修改局部闭包里的列表，不返回一个排列。','叶子保存后立即 return，避免无意义的继续选择。'],
 'pitfalls':['沿用子集的 start 规则。','used 被当成全局永久访问状态。','只保存长度不足 n 的路径。'],
 'complexity':'时间 O(n·n!)，包括复制全部 n! 个长度 n 的答案；辅助空间 O(n)，输出 O(n·n!)。',
 'quiz':{'question':'已经选了 [2]，下一层还能选择输入第一个元素 1 吗？','answer':'能。它的 used 仍为 False，排列允许任意未使用下标出现在后续位置。'},
 'tests':checks('permute',[([[1,2,3]],[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]),([[0,1]],[[0,1],[1,0]]),([[-1]],[[-1]])],compare='sorted',preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':47,'slug':'permutations-ii',
 'summary':'输入可以包含重复值，返回所有不同的完整排列。相同值来自不同输入位置，但仅交换相同值的位置不会产生新答案。',
 'baseline':'照 46 生成所有位置排列，最后放进集合去重虽然可行，却已经重复搜索了许多相同值分支。应在搜索树的同一层就跳过重复选择。',
 'insight':'先排序，让相同值相邻。若 nums[i]==nums[i-1] 且前一个同值位置当前未使用，则这一层应由前一个位置代表这个值，跳过 i；若前一个已经在路径中，则 i 是该值的下一份，允许继续使用。',
 'steps':['用 sorted 创建排序副本，保留原输入。','仍用 used 保证每个位置只用一次。','对可选 i 再检查同层去重：i>0、与前项相等且前项未用时跳过。','选择、递归、撤销；长度 n 时保存副本。'],
 'invariant':'对于任意相同值的一组下标，路径中总是优先使用靠前的未使用位置。它固定了相同值副本的使用先后，却不限制这些值在最终排列中的位置。因此每个值序列恰好保留一种下标实现，合法排列不会丢失。',
 'examples':[{'label':'两个 1 要区分位置，但不重复答案','input':'nums=[1,1,2]','output':'[[1,1,2],[1,2,1],[2,1,1]]','frames':[
  {'title':'给相同值临时加位置标签','note':'1a、1b 的数值相同。根层选择 1a 后产生的值排列，与根层选择 1b 完全重叠。','array':['1a','1b',2],'active':[0],'array_label':'排序后位置 0、1、2'},
  {'title':'根层跳过 1b 分支','note':'此时 1a 未使用，选择值 1 应由 1a 代表。','diagram':'[]\n├─ 1a → 继续\n├─ 1b → 跳过同层重复\n└─ 2  → 继续'},
  {'title':'选过 1a 后，可以再选 1b','note':'used[0]=True，后一个 1 不再触发去重，这样保留合法 [1,1,2]。','table':{'headers':['路径','前一个1是否已用','后一个1能否选'],'rows':[['[]','否','跳过'],['[1a]','是','允许'],['[2]','否','先选1a']]}},
  {'title':'只留下三个不同值序列','note':'同一路径保留重复值份数，同一层去掉等价分支。','table':{'headers':['答案'],'rows':[['[1,1,2]'],['[1,2,1]'],['[2,1,1]']]}}
 ]}],
 'walkthrough':['去重条件中的 not used[i-1] 是关键，它表示前一个相同值仍可作为本层候选，所以当前位置不应抢先。','若前一个相同值已在更高层使用，当前层必须允许使用下一份，否则永远无法填满含重复值的排列。','排序只是把等价候选放在一起；真正保证唯一性的是每层固定代表的规则。'],
 'code':'''
class Solution:
    def permuteUnique(self, nums: list[int]) -> list[list[int]]:
        # 先排序副本，让相等值相邻，同时保留原输入顺序。
        values = sorted(nums)
        n = len(values)
        used = [False] * n
        result, path = [], []
        def dfs() -> None:
            if len(path) == n:
                result.append(path.copy())
                return
            for i in range(n):
                if used[i]:
                    continue
                # 同一层只让第一个尚未使用的相等值代表这一选择，避免重复排列。
                if i > 0 and values[i] == values[i - 1] and not used[i - 1]:
                    continue
                # 前一个相等值若已在当前路径中，则允许使用这一份，重复元素各有身份。
                used[i] = True
                path.append(values[i])
                dfs()
                # 一轮尝试结束，恢复路径和使用标记，继续枚举同层候选。
                path.pop()
                used[i] = False
        dfs()
        return result
'''.strip(),
 'code_notes':['values 是新列表，输入 nums 的顺序保持不变。','第一条 used 判断限制同一位置不能重用，第二条判断限制相同值的等价分支，二者职责不同。','实际答案数为 n! 除以各值出现次数的阶乘乘积。'],
 'pitfalls':['相同值一律跳过，导致丢失需要多份相同值的答案。','把 not used[i-1] 写成相反条件，却仍按同层去重逻辑解释。','未排序就比较相邻值，重复值未必相邻。'],
 'complexity':'保守最坏时间 O(n·n!+n log n)，重复值通常会减少搜索分支。辅助空间 O(n)。若有 U 个不同排列，输出空间 O(nU)，不能把含重复输入也一律说成实际输出 n! 个。',
 'quiz':{'question':'[1,1,1] 应返回几条？','answer':'一条 [1,1,1]。沿一条路径依次使用三个位置，其他仅交换相同值身份的同层分支全部跳过。'},
 'tests':checks('permuteUnique',[([[1,1,2]],[[1,1,2],[1,2,1],[2,1,1]]),([[2,1,2]],[[1,2,2],[2,1,2],[2,2,1]]),([[1,1,1]],[[1,1,1]]),([[0]],[[0]])],compare='sorted',preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':17,'slug':'letter-combinations-of-a-phone-number',
 'summary':'将数字串 2..9 的每一位替换为该按键上的一个字母，返回全部组合。每个数字位置恰好贡献一个字母，输出长度等于数字串长度。',
 'baseline':'可以逐轮把已有字符串与下一个按键的所有字母做笛卡尔积。回溯把每个数字位置作为一层，不断追加一个字母，到最后一位时保存完整字符串。',
 'insight':'位置 index 唯一决定本层的选择列表，path 保存前 index 位数字已经选定的字母。相同字母可以在不同位置出现，因此不需要 used 集合；重点是按位置推进，而不是从全局字母池中不重复取数。',
 'steps':['建立 2→abc、3→def 等完整按键映射。','dfs(index) 遍历当前数字对应的字母。','追加一个字母，递归 dfs(index+1)，返回后弹出。','index 等于数字串长度时 join 保存答案。'],
 'invariant':'path 的第 i 个字母总来自 digits[i] 对应的集合，且长度等于当前 index。每层选择一个字母后继续下一位，最终每条根到叶选择序列恰好对应一个合法组合；每个位置的全部选择都被遍历。',
 'examples':[{'label':'每个数字位置是一层','input':'digits="23"','output':'ad、ae、af、bd、be、bf、cd、ce、cf','frames':[
  {'title':'先选择数字 2 的字母','note':'第一层三个分支 a、b、c，不能直接从数字 3 的字母开始。','diagram':'空字符串\n├─ a\n├─ b\n└─ c'},
  {'title':'在 a 后选择数字 3 的字母','note':'第二层选择 d、e、f，分别得到 ad、ae、af；每次保存后撤销最后字母。','diagram':'a\n├─ ad → 保存\n├─ ae → 保存\n└─ af → 保存'},
  {'title':'其他首字母重复同样过程','note':'共有 3×3=9 个组合；如果按键为 7 或 9，对应层会有四个选择。','table':{'headers':['首字母','完整组合'],'rows':[['a','ad、ae、af'],['b','bd、be、bf'],['c','cd、ce、cf']]}}
 ]}],
 'walkthrough':['输入 "22" 中，两个位置都可以选 a，因此 "aa" 是合法答案；不能因为 a 在当前路径出现过就禁止它。','映射 7 为 pqrs、9 为 wxyz，若错误地假设所有数字都是三个字母，会漏掉结果。','当前题目保证数字串非空。代码额外兼容旧题单中的空输入，返回 []，不把空串当成一个电话号码组合。'],
 'code':'''
class Solution:
    def letterCombinations(self, digits: str) -> list[str]:
        # 空输入返回空列表，不是含一个空字符串的列表。
        if not digits:
            return []
        letters = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
                   '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
        result, path = [], []
        # index 表示下一位待翻译的数字，路径每层选择一个字母。
        def dfs(index: int) -> None:
            if index == len(digits):
                result.append(''.join(path))
                return
            # 只枚举当前数字对应的字母，不跨数字取字符。
            for char in letters[digits[index]]:
                path.append(char)
                dfs(index + 1)
                # 撤销这一位字母，让下一种字母从相同父状态出发。
                path.pop()
        dfs(0)
        return result
'''.strip(),
 'code_notes':['字典键是单字符数字，如 "2"，与 digits[index] 的类型一致。','本题无需排序去重，每个按键映射内没有重复字母，位置序列本身唯一。','join 只在完整路径时执行，不在每次进入下一层时反复拼接前缀。'],
 'pitfalls':['使用全局 used 禁止不同位置选相同字母。','遗漏 7、9 的第四个字母。','混淆数字值与字符串字典键。'],
 'complexity':'设 d 为位数，P 为每位字母数的乘积，时间 O(dP)，辅助空间 O(d)，输出 O(dP)。最坏每位四选，P=4^d。',
 'quiz':{'question':'digits="7" 有几个结果？','answer':'四个：p、q、r、s。不是所有电话按键都只有三个字母。'},
 'tests':checks('letterCombinations',[(('23',),['ad','ae','af','bd','be','bf','cd','ce','cf']),(('7',),list('pqrs')),(('2',),list('abc')),(('',),[])],compare='sorted')
})

CHAPTER['problems'].append({
 'id':39,'slug':'combination-sum',
 'summary':'从互不相同的正整数候选中选择若干数，使和为 target。每个候选可以重复使用，返回不同组合；[2,2,3] 与 [3,2,2] 算同一种。',
 'baseline':'每一步都从全部候选开始选择，会同时搜索同一组合的各种排列。若完全不限制次数，又没有利用正数剩余量，搜索终止与去重都不清晰。',
 'insight':'排序后用 start 保证路径的候选下标非递减；选 i 后继续从 i 开始，允许重复使用当前值。remain 每次减少一个正数，最终必定下降。若当前值大于 remain，后面更大的值也不可能加入，可直接 break。',
 'steps':['排序得到 values，dfs(start,remain) 描述剩余选择。','remain==0 时保存 path 并结束这一分支。','从 start 枚举 i，若 values[i]>remain，停止本层。','追加当前值，递归 dfs(i,remain-values[i])。','返回后撤销当前值，尝试下一候选。'],
 'invariant':'path 的候选下标始终非递减，remain=target-sum(path)。每个无序组合都有唯一的非递减表示，所以不会产生排列重复；保留 i 允许任意合法重复次数。所有候选为正，remain 严格下降，剪掉超过剩余目标的值不会丢失可行解。',
 'examples':[{'label':'允许重用，但不回头换顺序','input':'candidates=[2,3,6,7]，target=7','output':'[[2,2,3],[7]]','frames':[
  {'title':'先尝试候选 2','note':'下层仍从下标 0 开始，才能再次选 2。','diagram':'remain=7\n选2 → path=[2]，remain=5\n再选2 → path=[2,2]，remain=3'},
  {'title':'第三次 2 不能凑完，改选 3','note':'[2,2,2] 剩余 1，小于最小候选；回退后选择 3，得到 [2,2,3]。','table':{'headers':['路径','remain','处理'],'rows':[['[2,2,2]',1,'无候选可选，回退'],['[2,2,3]',0,'保存']] }},
  {'title':'[2,3] 后不能回头再选 2','note':'后续只能从 3 的位置继续，避免生成 [2,3,2] 这一重复组合。','diagram':'[2,3]，remain=2\n下一候选从 3 开始：3>2 → 停止\n[2,2,3] 已在其他分支覆盖'},
  {'title':'单独选择 7 也合法','note':'根层最终选择 7，remain=0，保存第二个答案。','table':{'headers':['组合','总和'],'rows':[['[2,2,3]',7],['[7]',7]]}}
 ]}],
 'walkthrough':['dfs(i,...) 与子集的 dfs(i+1,...) 只差一位，却决定当前候选能否重用。','不能在没有排序时使用 break；当前值过大不代表后面没有较小候选。','题目候选至少为 2，目标最多 40，所以最大递归深度不超过 20；零或负数会破坏这里的严格下降论证。'],
 'code':'''
class Solution:
    def combinationSum(self, candidates: list[int], target: int) -> list[list[int]]:
        # 正数排序后可按剩余目标剪枝；不修改传入候选数组。
        values = sorted(candidates)
        result, path = [], []
        # remain 是还需要凑出的和，start 限制组合按非递减顺序选择。
        def dfs(start: int, remain: int) -> None:
            if remain == 0:
                result.append(path.copy())
                return
            for i in range(start, len(values)):
                value = values[i]
                # 当前值已太大，后面更大，因此整段都可跳过。
                if value > remain:
                    break
                path.append(value)
                # 允许重复使用同一个候选，所以传 i，而不是 i+1。
                dfs(i, remain - value)
                # 撤销本次加入，再试下一个候选。
                path.pop()
        dfs(0, target)
        return result
'''.strip(),
 'code_notes':['使用 sorted 保留原候选列表，新的排序顺序只用于搜索。','remain 作为整数参数随调用传递，不需要退出时手动加回；path 是可变列表，必须 pop。','候选本身互不相同，不需要 47 的相邻重复值判断。'],
 'pitfalls':['下一层从 i+1 开始，禁止合法重复选择。','下一层从 0 开始，生成组合的排列重复。','将这个正数剪枝套用到含负数或零的候选集合。'],
 'complexity':'设 k 为候选数量，d=⌊target/min(candidates)⌋，P 为实际搜索的前缀状态数，S 为输出总元素数。时间 O(k log k+kP+S)，辅助空间 O(k+d)，输出 O(S)。P 最坏指数增长；一个保守上界是组合数 C(k+d,d)，表示长度至多 d 的非递减候选序列数。',
 'quiz':{'question':'为什么 remain 是整数不需要撤销，path 却需要？','answer':'每次调用的 remain 是独立的参数绑定，减法生成新整数；所有调用共享同一个 path 列表，追加会原地修改它，必须 pop 恢复。'},
 'tests':checks('combinationSum',[([[2,3,6,7],7],[[2,2,3],[7]]),([[2,3,5],8],[[2,2,2,2],[2,3,3],[3,5]]),([[2],1],[]),([[7,2,3],7],[[2,2,3],[7]])],compare='groups',preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':22,'slug':'generate-parentheses',
 'summary':'生成 n 对括号组成的全部合法字符串。除了左右数量都为 n，每个前缀都必须满足右括号数不超过左括号数。',
 'baseline':'枚举长度 2n 的所有左右括号串，再逐个检查合法性，要尝试 2^(2n) 个字符串。若一个前缀已经出现无法匹配的右括号，后面追加任何字符都无法修复，应立即禁止这个选择。',
 'insight':'维护 opened、closed。只要 opened<n 可以追加左括号；只有 closed<opened 才能追加右括号，因为必须有尚未匹配的左括号。这样搜索过程中每个前缀都合法，到长度 2n 时自然是完整合法答案。',
 'steps':['从 opened=closed=0 和空 path 开始。','路径长度达到 2n 时 join 保存。','opened<n 时尝试左括号，递归后撤销。','closed<opened 时尝试右括号，递归后撤销。'],
 'invariant':'始终有 0≤closed≤opened≤n。追加左括号不超过总额度，追加右括号时有可用的未匹配左括号，因此每个前缀合法。长度达到 2n 时只能 opened=closed=n，且所有合法括号串的每个前缀都符合这些选择规则，不会漏解。',
 'examples':[{'label':'前缀余额限制右括号','input':'n=3','output':'((()))、(()())、(())()、()(())、()()()','frames':[
  {'title':'根层不能选择右括号','note':'opened=closed=0，没有未匹配左括号。','diagram':'空串\n├─ ( → 可继续\n└─ ) → 禁止'},
  {'title':'数量相等时只能继续开括号','note':'前缀 () 的 opened=closed=1；再加 ) 会变成非法前缀 ())。','table':{'headers':['前缀','opened','closed','下一步'],'rows':[['(',1,0,'可选 ( 或 )'],['()',1,1,'只能选 ('],['(((',3,0,'只能选 )']]}},
  {'title':'两种约束一起控制搜索','note':'(() 已开两次闭一次，可以继续开，也可以先闭；最终收集五条。','table':{'headers':['完整答案'],'rows':[['((()))'],['(()())'],['(())()'],['()(())'],['()()()']]}}
 ]}],
 'walkthrough':['仅保证最终左右各 n 个不够，例如 ")(" 数量相等却不合法。','opened==n 后不能再开，但可以继续闭合直到 closed==n。','无需用栈重新验证每个结果，因为选择规则已经在构造过程中维持了匹配前缀条件。'],
 'code':'''
class Solution:
    def generateParenthesis(self, n: int) -> list[str]:
        result, path = [], []
        # opened、closed 分别记录已放入的左、右括号数量。
        def dfs(opened: int, closed: int) -> None:
            if len(path) == 2 * n:
                result.append(''.join(path))
                return
            # 左括号总共只能放 n 个。
            if opened < n:
                path.append('(')
                dfs(opened + 1, closed)
                # 当前分支搜索结束，删除刚加入的括号，恢复上一层状态。
                path.pop()
            # 右括号不能多于左括号，否则当前前缀已无法修复成合法括号串。
            if closed < opened:
                path.append(')')
                dfs(opened, closed + 1)
                path.pop()
        dfs(0, 0)
        return result
'''.strip(),
 'code_notes':['两个 if 不是 if/else：有些状态下两种选择都合法，都需要探索。','opened、closed 按值传递，path 的字符选择才需要手动撤销。','成功条件使用长度 2n，依靠不变量保证两种括号各为 n。'],
 'pitfalls':['仅检查 closed<n，忽略前缀匹配。','用 if/else 只保留一种合法选择。','生成所有字符串后再校验，却忽略搜索过程中可做的剪枝。'],
 'complexity':'设 Cn 为第 n 个卡特兰数，即合法答案数量。时间 O(n·Cn)，辅助空间 O(n)，输出 O(n·Cn)；每个答案长度为 2n。',
 'quiz':{'question':'前缀 (())，n=3，下一步可以追加右括号吗？','answer':'不能。opened=closed=2，所有左括号已经匹配；下一步只能追加第三个左括号。'},
 'tests':checks('generateParenthesis',[([1],['()']),([2],['(())','()()']),([3],['((()))','(()())','(())()','()(())','()()()'])],compare='sorted')
})

CHAPTER['problems'].append({
 'id':131,'slug':'palindrome-partitioning',
 'summary':'把字符串完整切分成若干连续非空片段，要求每一段都是回文，返回所有切分方式。不能跳过、重排或重复消费字符。',
 'baseline':'枚举相邻字符间所有切或不切的位置，再检查每个片段，能覆盖全部方案。但同一个区间是否回文会反复判断，可以先预处理，再只搜索合法片段。',
 'insight':'pal[i][j] 表示闭区间 s[i:j+1] 是否回文：两端相等，且中间回文；长度一或二只需比较两端。回溯的 start 表示尚未消费的第一个位置，枚举 end，仅当 pal[start][end] 为真时选择这段并继续 end+1。',
 'steps':['按左端点从右向左填 pal 表，确保内部区间先已知。','dfs(start) 枚举当前片段的所有 end≥start。','回文片段加入 path，递归处理后缀 end+1，结束后弹出片段。','start==n 表示刚好消费完整字符串，保存 path 副本。'],
 'invariant':'path 按原顺序覆盖 s[:start]，其中各段都已通过回文检查，互不重叠且没有空隙。选择 s[start:end+1] 恰好扩展到新的已消费前缀。所有合法划分都有唯一的连续切分端点序列，因此会被完整且唯一地搜索到。',
 'examples':[{'label':'片段回文与完整切分都要满足','input':'s="aab"','output':'[["a","a","b"],["aa","b"]]','frames':[
  {'title':'先识别可选回文段','note':'单字符都回文，aa 也回文；ab 与 aab 不回文。','table':{'headers':['区间','片段','pal'],'rows':[['[0,0]','a','True'],['[0,1]','aa','True'],['[0,2]','aab','False'],['[1,2]','ab','False']]}},
  {'title':'第一段选择单个 a','note':'剩余后缀 ab 只能切成 a、b，形成 [a,a,b]。','diagram':'start=0：选 "a"\nstart=1：选 "a"（"ab" 被剪掉）\nstart=2：选 "b"\nstart=3：保存 ["a","a","b"]'},
  {'title':'回退后第一段选择 aa','note':'第二条分支只需再消费 b，形成 [aa,b]。','diagram':'start=0：选 "aa"\nstart=2：选 "b"\nstart=3：保存 ["aa","b"]'}
 ]}],
 'walkthrough':['切分与子集不同：不能选择后面的片段却跳过 start 位置，否则不再是覆盖原串的划分。','pal 的计算从 i=n-1 往 0 走，因为 pal[i][j] 依赖更大的左下标 i+1；长度≤2 使用短路条件，避免访问不需要的内部区间。','切片会创建字符串，保存路径列表也有成本，因此复杂度必须计入指数数量的划分输出。'],
 'code':'''
class Solution:
    def partition(self, s: str) -> list[list[str]]:
        n = len(s)
        # pal[i][j] 表示闭区间 s[i:j+1] 是否回文，先预处理避免回溯时反复判断。
        pal = [[False] * n for _ in range(n)]
        # 从较大的起点往前算，确保内部区间 pal[i+1][j-1] 已经得到。
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
        result, path = [], []
        def dfs(start: int) -> None:
            # 全部字符都被切分后，保存各段组成的路径副本。
            if start == n:
                result.append(path.copy())
                return
            for end in range(start, n):
                # 本段不是回文就立即跳过；下一段必须从 end+1 连续开始。
                if not pal[start][end]:
                    continue
                path.append(s[start:end + 1])
                dfs(end + 1)
                # 撤销当前切分，尝试把本段延长到另一个终点。
                path.pop()
        dfs(0)
        return result
'''.strip(),
 'code_notes':['二维表使用独立行，不能用 [[False]*n]*n。','s[start:end+1] 是闭区间片段对应的半开切片，end+1 不可漏掉。','path 中字符串不可变，保存列表的浅拷贝足够隔离后续 append/pop。'],
 'pitfalls':['只验证整个字符串是否回文，漏掉多段划分。','下一段从 end 开始，重复消费一个字符。','从左向右填 pal 表却读取尚未计算的内部状态。'],
 'complexity':'预处理 O(n²)。最坏所有字符相同，有 2^(n-1) 种划分；计入切片和输出，总时间 O(n²+n·2^n)，辅助空间 O(n²)，输出空间保守 O(n·2^n)。',
 'quiz':{'question':'s="ab" 虽然本身不回文，答案会是空吗？','answer':'不会。单字符都回文，划分 ["a","b"] 始终合法。'},
 'tests':checks('partition',[(('aab',),[['a','a','b'],['aa','b']]),(('a',),[['a']]),(('ab',),[['a','b']]),(('aaa',),[['a','a','a'],['a','aa'],['aa','a'],['aaa']])],compare='sorted')
})

CHAPTER['problems'].append({
 'id':93,'slug':'restore-ip-addresses',
 'summary':'给纯数字串插入三个点，组成四段合法 IPv4 地址。每段 0..255，除单独的 "0" 外不能有前导零；原字符必须全部保留且顺序不变。',
 'baseline':'枚举三个切分位置再检查四段是正确方案。回溯则逐段尝试一到三位，利用段数、剩余长度、前导零和数值上限提前拒绝不可能的分支。',
 'insight':'start 表示未消费位置，parts 保存已确定的段。还剩 slots=4-len(parts) 段时，剩余字符必须介于 slots 与 3*slots 之间。当前段最多取三位；一旦以 0 开头就只能取一位，超过 255 后更长段也不合法。',
 'steps':['总长度不在 4..12 直接返回 []。','进入 dfs(start)，先检查剩余字符是否能装进剩余段。','已经四段且字符刚好用完时，用点连接保存。','枚举长度 1..3，检查前导零和数值上限，通过后选择该段。','递归处理剩余后缀，返回时撤销当前段。'],
 'invariant':'parts 始终由合法段组成，并按顺序完整覆盖原串已消费前缀。长度剪枝只排除每段一到三位也无法分配的情况；局部格式检查排除非法段。每个合法地址对应唯一的四段长度序列，最终完整消费时恰好被收集一次。',
 'examples':[{'label':'前导零不能被 int 掩盖','input':'s="010010"','output':'["0.10.0.10","0.100.1.0"]','frames':[
  {'title':'第一段只能选 0','note':'01、010 即使转成整数后在范围内，也仍违反原始文本不能有前导零的规则。','diagram':'010010\n第一段：0 ✓\n第一段：01 ✗\n第一段：010 ✗'},
  {'title':'第二段选择 10','note':'后缀 010 需分两段，下一段开头是零，所以只能选 0，再取 10。','table':{'headers':['已选段','剩余后缀','下一步'],'rows':[['[0,10]','010','取单独0'],['[0,10,0]','10','最后一段10']]}},
  {'title':'第二段选择 100','note':'剩余 10 分成 1、0，得到第二个合法地址。','table':{'headers':['结果'],'rows':[['0.10.0.10'],['0.100.1.0']]}}
 ]}],
 'walkthrough':['int("01")==1 不能证明这一段合法，必须先检查原字符串的前导零。','剩余段数为 0 时，长度检查会要求 remaining==0；这保证四段已经用完却仍有字符时不会误收集。','超过 255 后可以 break，因为继续在十进制整数末尾追加数字只会更大。前导零同理，当前长度不合法后更长长度也不能恢复。'],
 'code':'''
class Solution:
    def restoreIpAddresses(self, s: str) -> list[str]:
        if not 4 <= len(s) <= 12:
            return []
        result, parts = [], []
        def dfs(start: int) -> None:
            # slots 是还缺几段，remaining 是还剩几个字符。
            slots = 4 - len(parts)
            remaining = len(s) - start
            # 每段至少 1 位、至多 3 位，剩余字符数不合范围时直接剪枝。
            if not slots <= remaining <= 3 * slots:
                return
            if slots == 0:
                result.append('.'.join(parts))
                return
            for end in range(start, min(start + 3, len(s))):
                # 以 0 开头的段只能是单独的 0，不能继续扩成 01 或 00。
                if end > start and s[start] == '0':
                    break
                part = s[start:end + 1]
                # 数值已超界，继续加数字只会更大，因此结束这一层枚举。
                if int(part) > 255:
                    break
                parts.append(part)
                dfs(end + 1)
                # 回溯撤销本段，使下一种分段方式使用干净的路径。
                parts.pop()
        dfs(0)
        return result
'''.strip(),
 'code_notes':['parts 保留原始字符串片段，不将它们转整数再转回，避免改变原数字表示。','range 的终点不包含在内，最多尝试 end=start、start+1、start+2。','slots==0 前已经通过 remaining==0 检查，所以保存时一定完整消费。'],
 'pitfalls':['允许 "00" 或 "01"。','只有四段却未消费完整字符串时也保存。','任意重排数字，偏离“仅插入点”的要求。'],
 'complexity':'IPv4 固定四段、每段最多三位，搜索树最多四层、每层三选，可记时间 O(3^4)、辅助空间 O(4)；每个输出最多 15 个字符。这些都是固定上界，总长度超过 12 时直接返回。',
 'quiz':{'question':'"0000" 为什么只能还原成一个地址？','answer':'每个零都只能单独成为一段，因此唯一结果是 0.0.0.0。任何多位零段都含前导零。'},
 'tests':checks('restoreIpAddresses',[(('010010',),['0.10.0.10','0.100.1.0']),(('0000',),['0.0.0.0']),(('25525511135',),['255.255.11.135','255.255.111.35']),(('111',),[]),(('256256256256',),[])],compare='sorted')
})

CHAPTER['problems'].append({
 'id':79,'slug':'word-search',
 'summary':'在字符网格中沿上下左右相邻位置拼出 word。同一路径不能重复使用同一个格子，允许不同格子有相同字符。返回是否存在一条合法路径。',
 'baseline':'每个匹配首字母的格子都可作为起点，枚举后续四邻接路线。但若不记录当前路径占用位置，搜索可能来回重复利用同一格；若永久标记，又会错误禁止其他候选路径使用它。',
 'insight':'dfs(r,c,index) 表示在当前格匹配 word[index]。成功匹配且不是最后一位时，暂时把该格改成字母表以外的 #，然后探索下一位；无论子分支成功还是失败，返回前都恢复原字符。先用总格数和字符频次做必要条件剪枝，避免不可能的搜索。',
 'steps':['word 长度超过格子总数或任一字符需求超过网格次数时，直接 False。','从每个格子尝试 dfs(r,c,0)，边界不合法或字符不等立即 False。','匹配到 word 最后一位时返回 True。','否则保存原字符、标记 #，依次尝试四邻居匹配 index+1。','恢复字符，再返回本分支是否成功；有一个起点成功即可 True。'],
 'invariant':'进入递归时，所有标成 # 的格子恰好是当前路径已使用的祖先位置；它们不能再次匹配任何字母。退出恢复后，网格回到进入这一层之前的状态，其他分支可以重新使用这些位置。每步只走一条邻接边并增加一个字符下标，叶子成功就代表完整合法路径。',
 'examples':[{'label':'匹配成功也要逐层恢复','input':'board=["ABCE","SFCS","ADEE"]（每行实际为字符列表），word="ABCCED"','output':'True，返回后 board 保持原样','frames':[
  {'title':'从左上角匹配 A、B、C','note':'已使用的格子临时标成 #，它们不能再次参与同一路径。','grid':[['#','#','C','E'],['S','F','C','S'],['A','D','E','E']],'active_cells':[[0,2]],'metrics':[['已匹配','ABC']]},
  {'title':'向下匹配第二个 C，再匹配 E、D','note':'完整坐标是 (0,0)→(0,1)→(0,2)→(1,2)→(2,2)→(2,1)。不同位置的两个 C 都可用。','grid':[['#','#','#','E'],['S','F','#','S'],['A','D','#','E']],'active_cells':[[2,1]],'metrics':[['已匹配','ABCCED']]},
  {'title':'成功沿调用栈返回，也恢复字符','note':'最后一位未被覆盖；其余各层执行恢复后，输入矩阵与调用前完全一致。','grid':[list('ABCE'),list('SFCS'),list('ADEE')],'active_cells':[[0,0],[0,1],[0,2],[1,2],[2,2],[2,1]]}
 ]},{'label':'字母数量足够，不代表路径存在','input':'board=[["A","B","C","X","B"]]，word="ABCB"','output':'False','frames':[
  {'title':'走到 C 后不能回用左边 B','note':'左边 B 已标为 #，右边 X 不匹配下一字母。更远的另一个 B 不能隔着 X 跳过去。','grid':[['#','#','C','X','B']],'active_cells':[[0,2]],'metrics':[['下一字符','B']]},
  {'title':'失败后恢复路径','note':'字符频次只是必要条件，四邻接与不重复使用约束仍需搜索判断。','grid':[list('ABCXB')]}
 ]}],
 'walkthrough':['这与 200 的永久标记不同：一个格子在一条失败路径中用过，不意味着它在另一条路径中也不能用。','不要在找到成功孩子后直接 return True 而跳过恢复。先记录 found，再恢复当前格，再返回，能保持输入的只读效果。','频次剪枝只比较每个字符的供需，不证明字符之间连通；它负责提前排除明显不可能情况，DFS 负责真正的路径约束。'],
 'code':'''
from collections import Counter

class Solution:
    def exist(self, board: list[list[str]], word: str) -> bool:
        rows, cols = len(board), len(board[0])
        # 一个格子在路径中不能用两次，字符数超过格子数必然无解。
        if len(word) > rows * cols:
            return False
        available = Counter(char for row in board for char in row)
        needed = Counter(word)
        # 先检查字符总量是否足够，减少明显不可能的搜索。
        if any(needed[char] > available[char] for char in needed):
            return False
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        def dfs(r: int, c: int, index: int) -> bool:
            # 先判边界，再比较字符，避免越界或负下标误读。
            if not (0 <= r < rows and 0 <= c < cols):
                return False
            if board[r][c] != word[index]:
                return False
            if index == len(word) - 1:
                return True
            saved = board[r][c]
            # 临时标记当前路径用过的格子，其他分支回溯后仍可使用。
            board[r][c] = '#'
            found = False
            for dr, dc in directions:
                if dfs(r + dr, c + dc, index + 1):
                    found = True
                    break
            # 无论搜索成功或失败，都恢复原字符，保持输入棋盘不变。
            board[r][c] = saved
            return found
        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0):
                    return True
        return False
'''.strip(),
 'api':{'signature':'Counter(iterable)；counter[key] -> 次数','description':['Counter 从 collections 导入，将可迭代对象的元素计数。这里网格生成器依次提供每个字符，Counter(word) 统计目标需求。','Counter 读取不存在的键会返回 0。字母频次不足可以立即拒绝，但不能替代路径搜索。']},
 'code_notes':['# 不在题目允许的大小写英文字母中，因此能作为当前路径的临时占用标记。','最后一位成功时无需继续压入路径，也没有覆盖当前格，直接 True 是安全的。','题目保证 word 非空、网格非空，函数直接按这些约束处理。'],
 'pitfalls':['把访问标记永久保留。','成功时提前返回导致未恢复 board。','允许对角移动或跳过不匹配格子。','按字符值而不是格子位置去重，错误禁止同字母的不同格子。'],
 'complexity':'设 L 为单词长度。预检 O(mn+L)，搜索最坏可记 O(mn·3^L)：第一步至多四邻居，之后至少不能返回前一格。递归与临时状态 O(L)，频次表在固定英文字母表下为常数规模；board 返回时恢复。',
 'quiz':{'question':'一条分支已经找到答案，为什么还要恢复当前格？','answer':'恢复保证调用前后的输入一致，也使递归的“退出后状态不变”约定对成功和失败都成立；不能只在失败时撤销。'},
 'tests':checks('exist',[([[list('ABCE'),list('SFCS'),list('ADEE')],'ABCCED'],True),([[list('ABCE'),list('SFCS'),list('ADEE')],'SEE'],True),([[list('ABCXB')],'ABCB'],False),([[['A']],'A'],True),([[['A']],'AA'],False)],preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':51,'slug':'n-queens',
 'summary':'在 n×n 棋盘上放 n 个皇后，使任何两者不同行、不共列、不共对角线，返回全部棋盘。Q 表示皇后，点表示空位。',
 'baseline':'从 n² 个格子里任选 n 个，再两两检查冲突，会枚举大量显然不可能的棋盘。因为 n 个皇后不能同行，每行恰好放一个，可直接把搜索层定义为行号。',
 'insight':'逐行选择列，用三个集合记录已占用的 col、row-col、row+col。同行由逐行放一个自动保证；同列或同对角线的两个位置具有相同对应标识，集合查询就能在常数时间判断冲突。',
 'steps':['row=0 开始，三个占用集合与列路径 path 为空。','枚举当前行每个列 c；若列、差值或和值已占用，跳过。','登记三个标识并追加 c，递归下一行。','返回时删除三个标识并弹出 c。','row==n 时根据每行选择的列生成字符串棋盘，保存答案。'],
 'invariant':'递归进入 row 时，前 row 行各有一个皇后且互不攻击，三个集合恰好记录这些皇后的冲突标识。新选择通过三种检查，就不会攻击任何已有皇后；退出删除当前标识恢复父状态。所有行列选择均被遍历，因此返回全部合法布局且无重复。',
 'examples':[{'label':'列与两种对角线共同约束','input':'n=4','output':'两种布局；示例列序列 [1,3,0,2]','frames':[
  {'title':'第 0 行选择列 1','note':'登记 col=1、row-col=-1、row+col=1。下一行不能选同列 1，也不能选相邻对角列 0、2。','grid':[['.','Q','.','.'],['.','.','.','.'],['.','.','.','.'],['.','.','.','.']],'active_cells':[[0,1]]},
  {'title':'第 1 行只能选择列 3','note':'此分支接着选择第 2 行列 0，再选择第 3 行列 2。','table':{'headers':['row','col','row-col','row+col'],'rows':[[0,1,-1,1],[1,3,-2,4],[2,0,2,2],[3,2,1,5]]}},
  {'title':'第一个完整棋盘','note':'四个列互异，四个差值互异，四个和值互异。','grid':[['.','Q','.','.'],['.','.','.','Q'],['Q','.','.','.'],['.','.','Q','.']],'active_cells':[[0,1],[1,3],[2,0],[3,2]]},
  {'title':'回退继续得到另一种布局','note':'不能找到一张棋盘就停止；另一种列序列为 [2,0,3,1]。','grid':[['.','.','Q','.'],['Q','.','.','.'],['.','.','.','Q'],['.','Q','.','.']],'active_cells':[[0,2],[1,0],[2,3],[3,1]]}
 ]}],
 'walkthrough':['同一条左上到右下对角线满足 row-col 恒定；另一方向满足 row+col 恒定。无需每次扫描整张棋盘。','同一分支中三个标识都唯一，所以退出时可以安全 remove 当前值，不会误删另一个皇后的合法共享状态。','path 只存每行的列编号，成功时才创建 n 行字符串，避免每个搜索节点复制整张棋盘。'],
 'code':'''
class Solution:
    def solveNQueens(self, n: int) -> list[list[str]]:
        # 列、行减列、行加列三个集合分别记录已经被皇后占用的攻击线。
        columns, diagonal_diff, diagonal_sum = set(), set(), set()
        result, path = [], []
        def dfs(row: int) -> None:
            # 每行恰好放一枚皇后后，根据列下标生成完整棋盘字符串。
            if row == n:
                result.append(['.' * col + 'Q' + '.' * (n - col - 1) for col in path])
                return
            for col in range(n):
                # 同一条两种斜线分别具有相同的 row-col 或 row+col。
                diff, total = row - col, row + col
                # 任一攻击线已占用，这个位置就不能放皇后。
                if col in columns or diff in diagonal_diff or total in diagonal_sum:
                    continue
                columns.add(col)
                diagonal_diff.add(diff)
                diagonal_sum.add(total)
                path.append(col)
                dfs(row + 1)
                # 返回上一行时，必须同时撤销列和两种斜线的占用。
                path.pop()
                columns.remove(col)
                diagonal_diff.remove(diff)
                diagonal_sum.remove(total)
        dfs(0)
        return result
'''.strip(),
 'code_notes':['负的 row-col 是合法集合键，不需偏移到非负下标。','列路径顺序就是行顺序，生成棋盘时每个字符串长度都是 n。','set.remove 要求元素确实存在；选择前确认不冲突、进入后登记、退出时删除，保证这一前提。'],
 'pitfalls':['只检查行列，不检查对角线。','遗漏一个集合的撤销，错误剪掉后续分支。','把差值取绝对值，会把不同对角线混为一组。','只找到第一张棋盘就返回。'],
 'complexity':'设有 S 个合法棋盘。本实现每个搜索状态扫描 n 列，保守时间上界 O(n·n!+S·n²)；对角剪枝通常大幅减少状态。辅助空间 O(n)，输出每张棋盘 n² 个字符，共 O(S·n²)。',
 'quiz':{'question':'(0,1) 与 (1,0) 的 row-col 不同，为什么仍然冲突？','answer':'它们的 row+col 都等于 1，位于另一方向的同一条对角线。必须同时检查和与差。'},
 'tests':checks('solveNQueens',[([1],[['Q']]),([2],[]),([3],[]),([4],[['.Q..','...Q','Q...','..Q.'],['..Q.','Q...','...Q','.Q..']])],compare='sorted')
})
