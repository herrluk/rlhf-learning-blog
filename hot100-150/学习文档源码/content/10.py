from textwrap import dedent

CHAPTER={
 'lead':'排序决定所有元素的位置，Top K 只保留一部分候选，多路归并每次只比较各路最小的未读元素。理解需要维护的信息量，才能选择合适的堆或分区算法。',
 'intro':['学习顺序：912 手写排序与堆结构 → 215 第 k 大 → 347 按频次筛选 → 973 按距离筛选 → 23 合并有序链 → 378 有序矩阵的第 k 小。','第 912 题给出堆排序、归并排序、随机三路快速排序三种完整实现；第 215 题进一步把快速排序的“两边都处理”改成快速选择的“只处理目标所在一边”。','本章统一使用 Python 3.12 的小顶堆接口。需要模拟最大优先级时对比较键取负，不依赖较新版本才增加的最大堆专用函数。每个方法都说明是否修改输入。'],
 'sections':[
  {'title':'堆只保证父子关系，不保证数组整体有序','body':['小顶堆的每个父元素不大于孩子，因此根是全局最小值；同层兄弟之间没有排序要求。读取 heap[1] 不能当作读取第二小值。','数组下标 i 的孩子为 2i+1、2i+2，父亲为 (i−1)//2。用这些关系就能在一个列表内表示完全二叉树，不需要真的创建树节点。'],'diagram':'小顶堆示例：[2,5,3,9,7]\n       2(0)\n      /    \\\n   5(1)    3(2)\n   /  \\\n9(3) 7(4)\n根最小，但数组 [2,5,3,9,7] 并非升序'},
  {'title':'堆顶应该是保留集合中最想淘汰的对象','body':['要保留最大的 k 个值，用小顶堆暴露其中最小者，新值只有更大才值得替换它。要保留最近的 k 个点，则应暴露其中最远者，用负距离在小顶堆中实现。','多路归并的目标不同：需要取下一项最小值，所以把各路当前最小未读项放进小顶堆；取出一项后，只补入同一路的下一项。']},
  {'title':'比较键与原始对象分开保存','body':['堆项可以是元组，Python 按字段从左到右比较。频次题用 (频次,数值)，点集用 (负距离,下标)，链表用 (节点值,来源编号,节点)。','如果只用 (节点值,节点)，相同值会让比较继续落到两个普通 ListNode 对象上，可能抛出 TypeError。加入可比较且能区分并列候选的编号，才能让比较在对象字段之前结束。']}
 ],
 'apis':[{'signature':'heapq.heapify(heap: list) -> None','description':['原地将列表调整成小顶堆，时间 O(n)，返回 None；不能把返回值重新赋给 heap。']},{'signature':'heapq.heappush(heap: list, item) -> None\nheapq.heappop(heap: list) -> item','description':['heappush 插入一项并维护堆；heappop 删除并返回最小项。两者调整成本 O(log n)，空堆 pop 会抛出 IndexError。heap[0] 只读取堆顶，成本 O(1)。']},{'signature':'heapq.heapreplace(heap: list, item) -> old_min\nheapq.heappushpop(heap: list, item) -> min_item','description':['heapreplace 必定移除原堆顶再放入新项，要求堆非空；因此保留最大 k 项时，调用前先判断新值是否更大。','heappushpop 相当于先加入再移除最小项。两者语义不同：旧堆顶为 5、新值为 2 时，heapreplace 留下 2，heappushpop 留下 5。']}],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':912,'slug':'sort-an-array',
 'summary':'不使用内置排序函数，将整数数组升序排列。主方法手写堆排序，保证最坏 O(n log n) 时间、O(1) 辅助空间；同类中另给归并与随机三路快排，比较三者的性质。',
 'baseline':'冒泡、选择、插入排序都可能需要 O(n²) 次操作。直接调用 sort 或 sorted 虽然方便，但绕过本题要求的排序实现。需要用分治或堆结构，把每一轮处理的成本控制下来。',
 'insight':['堆排序：先把整个数组建成大顶堆，堆顶就是当前最大值。把它与未排序区末尾交换，末尾位置便永久确定；缩小堆的范围，再把新根下沉，重复即可得到升序后缀。','归并排序：长度 1 的段本来有序，每轮两两合并相邻有序段，把段长翻倍。快速排序：围绕 pivot 把区间分成 <、=、> 三段，只继续排序左右两段，相等段已在最终数值范围内。'],
 'steps':['主解用 sift(root,end) 修复半开区间 [0,end) 中以 root 为根的大顶堆：每次选择较大孩子，若孩子更大就交换并向下继续。','从最后一个非叶节点 n//2−1 向前下沉，线性建堆。','将堆顶与当前末尾 end 交换，把 end 排除出堆，再从根下沉修复。','直到未排序区只剩一项，返回原数组。','比较方法：归并使用一个临时数组；三路快排随机选 pivot，并先处理较小分区、把较大分区压栈以控制栈深度。'],
 'invariant':['堆排序每轮开始时，前缀 [0,end] 是大顶堆，后缀 (end,n) 已升序且其中每项不小于前缀任何项。交换后最大值落到 end，缩小范围并下沉恢复前缀堆性质，升序后缀扩大一项。','sift 调用时两个孩子的子树已经是堆，只有当前根可能偏小；与较大孩子交换后，上方位置满足大顶堆关系，唯一可能违反的位置随 root 向下移动。'],
 'examples':[{'label':'大顶堆每次确定一个最大值的位置','input':'nums=[4,1,3,2]，使用 sortArray','output':'[1,2,3,4]','frames':[
  {'title':'先从下往上建大顶堆','note':'下标 1 的值 1 与孩子 2 交换，得到 [4,2,3,1]；根 4 已不小于两个孩子。','diagram':'       4\n      / \\\n     2   3\n    /\n   1','array':[4,2,3,1]},
  {'title':'把最大值 4 交换到末尾','note':'交换根与下标 3 后，前缀 [1,2,3] 需要修复；根 1 与较大孩子 3 交换，得到 [3,2,1,4]。','array':[3,2,1,4],'active':[3],'metrics':[['已确定后缀','[4]']]},
  {'title':'再把 3 放到下标 2','note':'交换后前缀为 [1,2]，下沉变成 [2,1]；后缀 [3,4] 已经升序。','array':[2,1,3,4],'active':[2,3]},
  {'title':'最后交换 2 与 1','note':'只剩一个元素时无需再下沉，整个数组升序。','array':[1,2,3,4],'active':[0,1,2,3]}
 ]},{'label':'归并按段长 1、2、4 扩大','input':'nums=[5,1,4,2,3]，使用 sortArrayMerge','output':'[1,2,3,4,5]','frames':[
  {'title':'先合并长度 1 的相邻段','note':'[5] 与 [1] 合并为 [1,5]；[4] 与 [2] 合并为 [2,4]；最后 [3] 单独保留。','diagram':'[1,5] [2,4] [3]'},
  {'title':'再合并两个长度 2 的段','note':'[1,5] 与 [2,4] 归并为 [1,2,4,5]，尾段仍为 [3]。','diagram':'[1,2,4,5] [3]'},
  {'title':'长度 4 的段与尾段合并','note':'最终得到 [1,2,3,4,5]。临时数组保存本轮输出，整轮完成后再写回原数组。','array':[1,2,3,4,5]}
 ]},{'label':'三路快排的一次分区，示意 pivot=3','input':'nums=[3,1,3,2,5,3,4]，本轮随机选中 3','output':'分成 [1,2]、[3,3,3]、[4,5] 后继续两侧','frames':[
  {'title':'先把小于 3 的值移到左区','note':'扫描并交换 1、2 后，得到 [1,2,3,3,5,3,4]；等于区中的 3 无需继续排序。','array':[1,2,3,3,5,3,4],'active':[0,1]},
  {'title':'大于 3 的值送到右区','note':'5、4 被交换到右边；从右边换来的未知值仍需检查，不能直接推进扫描指针。','array':[1,2,3,3,3,4,5],'active':[5,6]},
  {'title':'只对 < 和 > 两段继续','note':'相等段 [3,3,3] 已经确定，避免全相等输入反复退化成只消除一个元素。随机选择可能产生不同中间分区，但最终排序结果相同。','diagram':'[1,2] < 3    [3,3,3] = 3    [4,5] > 3'}
 ]}],
 'walkthrough':['建堆不是从头到尾各做一次完整排序。叶节点天然是堆，从最后一个父节点向前下沉，可以保证处理父节点时孩子已经有效。大多数节点靠近叶子，只需下沉很少层，总建堆成本为 O(n)。','大顶堆用于升序排序，因为每次取出的最大值放在最右端；直接把最大值依次写到结果开头才会得到降序。','归并中相等时先取左段，因而稳定；堆排序与这里的交换式三路快排不保证稳定。','随机快排只有期望时间保证，最坏仍可能 O(n²)。主接口选择堆排序以保留最坏 O(n log n) 与常数辅助空间。'],
 'code':'''
from random import randint

class Solution:
    def sortArray(self, nums: list[int]) -> list[int]:
        # 把 root 沿较大孩子方向下沉，维护 [0,end) 内的大顶堆。
        def sift(root: int, end: int) -> None:
            while root * 2 + 1 < end:
                child = root * 2 + 1
                # 左右孩子都存在时，必须与较大的那个比较。
                if child + 1 < end and nums[child + 1] > nums[child]:
                    child += 1
                # 父节点已经不小于最大孩子，下沉结束。
                if nums[root] >= nums[child]:
                    break
                nums[root], nums[child] = nums[child], nums[root]
                root = child

        n = len(nums)
        # 从最后一个非叶节点向前建堆，孩子处理完再处理父亲。
        for root in range(n // 2 - 1, -1, -1):
            sift(root, n)
        # 把堆顶最大值换到末尾，然后缩小堆范围。
        for end in range(n - 1, 0, -1):
            nums[0], nums[end] = nums[end], nums[0]
            sift(0, end)
        return nums

    # 对照方法：稳定归并排序，使用 O(n) 临时数组。
    def sortArrayMerge(self, nums: list[int]) -> list[int]:
        n = len(nums)
        temp = [0] * n
        # 每轮把相邻两个 width 长的有序段合并。
        width = 1
        while width < n:
            for left in range(0, n, width * 2):
                mid = min(left + width, n)
                right = min(left + width * 2, n)
                i, j = left, mid
                for out in range(left, right):
                    # 左段还有值且不大于右段时先取左段，相等时也先取左段以保证稳定。
                    if i < mid and (j >= right or nums[i] <= nums[j]):
                        temp[out] = nums[i]
                        i += 1
                    else:
                        temp[out] = nums[j]
                        j += 1
            # 用切片赋值写回原列表，保留调用方持有的列表对象。
            nums[:] = temp
            width *= 2
        return nums

    # 对照方法：随机三路快排，平均 O(n log n)，最坏仍可能平方级。
    def sortArrayQuick(self, nums: list[int]) -> list[int]:
        stack = [(0, len(nums) - 1)]
        while stack:
            left, right = stack.pop()
            while left < right:
                # 随机选基准，减少有序输入反复产生极端分区的机会。
                pivot = nums[randint(left, right)]
                # 小于区在左、等于区在中、大于区在右，i 扫描未知区域。
                low, i, high = left, left, right
                while i <= high:
                    if nums[i] < pivot:
                        nums[low], nums[i] = nums[i], nums[low]
                        low += 1
                        i += 1
                    elif nums[i] > pivot:
                        nums[i], nums[high] = nums[high], nums[i]
                        high -= 1
                    else:
                        i += 1
                # 小段立即处理，大段暂存栈中，使显式栈深度保持对数级。
                if low - left < right - high:
                    stack.append((high + 1, right))
                    right = low - 1
                else:
                    stack.append((left, low - 1))
                    left = high + 1
        return nums
'''.strip(),
 'api':{'signature':'random.randint(a: int, b: int) -> int','description':['返回闭区间 [a,b] 中的随机整数，两个端点都可能取到。快排先读取这个位置的数值作为 pivot，之后即使该位置被交换，pivot 数值仍固定。','随机性只影响中间分区与运行成本，不影响最后应得到的排序结果。']},
 'code_notes':['三个方法都原地修改 nums，并返回同一个列表对象；主接口是 sortArray。','sift 的 end 是排除端点，已确定的后缀不会再次参加堆调整。','nums[:]=temp 更新原列表内容，而 nums=temp 只会改变局部变量绑定，调用者原列表不会随之改指向。','快排把较大分区压栈，立即处理较小分区。每次继续嵌入的当前区间至多减半，因此显式栈为 O(log n)，而非最坏 O(n)。'],
 'pitfalls':['把已经放入有序后缀的元素仍算进堆范围，会把已确定位置重新打乱。','下沉时与较小孩子交换，不能保证大顶堆性质。','归并写入原数组却同时读取尚未合并的原值，可能覆盖未读数据；本代码整轮写入 temp 后才统一回写。','随机快排不能声称最坏 O(n log n)，三路划分改善重复值，但不取消极端随机划分的可能性。'],
 'complexity':'堆排序最坏时间 O(n log n)、辅助空间 O(1)。归并排序时间 O(n log n)、辅助空间 O(n)，稳定。三路随机快排期望 O(n log n)、最坏 O(n²)，当前处理较小段的实现使辅助栈 O(log n)，不稳定。',
 'quiz':{'question':'为什么堆排序建大顶堆，却得到升序结果？','answer':'每次取出的当前最大值被放到未排序区最右端，依次占据从右到左的位置，因此最终从左到右是升序。'},
 'tests':{'method':'sortArray','cases':[{'args':[[4,1,3,2]],'expected':[1,2,3,4]},{'args':[[5,1,1,2,0,0]],'expected':[0,0,1,1,2,5]},{'args':[[-3,0,-1]],'expected':[-3,-1,0]},{'args':[[1]],'expected':[1]},{'args':[[7,7,7]],'expected':[7,7,7]}]}
})

CHAPTER['problems'].append({
 'id':215,'slug':'kth-largest-element-in-an-array',
 'summary':'返回按降序排列后的第 k 个元素，重复数值分别占据名次，不是第 k 个不同数值。给出大小为 k 的小顶堆主解，以及原地随机快速选择变体。',
 'baseline':'整体排序后读取 nums[n-k] 可以解决，但为其他 n−1 个位置排序做了额外工作。若只关心前 k 大，维护这 k 个候选就够了；快速选择还能只划分目标所在的区域。',
 'insight':['小顶堆保存已经读过元素中最大的 k 个，堆顶是这批候选里最小的，也就是第 k 大。新值不大于堆顶时不值得替换；更大时用它淘汰堆顶。','快速选择把目标换成升序下标 target=n−k。每轮三路分区后，若 target 在相等段中，答案就是 pivot；否则只保留目标所在的一侧，无需继续排序另一侧。'],
 'steps':['堆未满时直接插入元素。','堆已满后，仅当新值大于 heap[0] 时调用 heapreplace 替换最小候选。','所有元素处理完，返回 heap[0]。','快速选择变体每轮随机选 pivot，划分 <、=、> 三段，再根据 target 缩小闭区间，直到落在相等段。'],
 'invariant':'堆法处理完任意前缀后，堆恰好保留该前缀中最大的 min(k,前缀长度) 个值，重复项按出现次数保留。堆满时，一个不超过当前最小候选的新值不能进入前 k；更大值替换最小候选后，保留集合仍正确。快速选择始终保留包含目标顺序统计量的区间，丢弃的部分全部位于目标的另一侧。',
 'examples':[{'label':'前两大中的较小值就是第二大','input':'nums=[3,2,1,5,6,4]，k=2','output':'5','frames':[
  {'title':'先保留 3、2，堆顶为 2','note':'小顶堆 [2,3] 保存当前最大的两项，堆顶暴露最容易被淘汰的候选。','diagram':'   2\n  /\n 3','metrics':[['候选','{2,3}']]},
  {'title':'1 不足以进入前两大','note':'1≤2，忽略它，不改变候选集合。','array':[2,3],'array_label':'堆数组'},
  {'title':'5 替换 2，6 再替换 3','note':'读 5 后候选为 {3,5}；读 6 后为 {5,6}，堆顶从 2 升到 3、再升到 5。','table':{'headers':['新值','候选集合','堆顶'],'rows':[[5,'{3,5}',3],[6,'{5,6}',5]]}},
  {'title':'4 被忽略，返回堆顶 5','note':'最终前两大是 6、5。堆没有给所有元素排序，但已经包含所需顺序统计量。','array':[5,6],'metrics':[['第 2 大',5]]}
 ]},{'label':'重复数值照样占名次','input':'nums=[5,5,4]，k=2','output':'5','frames':[
  {'title':'两个 5 都进入堆','note':'它们来自两次出现，必须保留两份；不能先转成 set。','array':[5,5]},
  {'title':'4 不进入候选，第二大仍为 5','note':'降序序列为 [5,5,4]，第二个位置的值是 5。','diagram':'第 1 大：5\n第 2 大：5\n第 3 大：4'}
 ]}],
 'walkthrough':['“保留最大的 k 个”使用小顶堆，是因为我们要快速找到保留集合里最差的那一项，而不是每次取全局最大值。','heapreplace 会无条件删除旧堆顶，所以必须先判断 value>heap[0]。若把较小新值也放进去，就破坏了前 k 大不变量。','快速选择的 target 是升序下标 n-k，例如 n=6、k=2 时 target=4。分区只有相等段已经定位，左右两段内部不需要有序。'],
 'code':'''
from heapq import heappush, heapreplace
from random import randint

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        # 第 k 大等价于升序下标 len(nums)-k，不需要完整排序。
        target = len(nums) - k
        left, right = 0, len(nums) - 1
        while left <= right:
            # 随机基准配合三路划分，重复值会一次归入相等区域。
            pivot = nums[randint(left, right)]
            # [left,low) 小于基准，[low,i) 等于基准，[i,high] 未知。
            low, i, high = left, left, right
            while i <= high:
                if nums[i] < pivot:
                    nums[low], nums[i] = nums[i], nums[low]
                    low += 1
                    i += 1
                elif nums[i] > pivot:
                    # 换回来的值尚未检查，缩小 high 后不能同时推进 i。
                    nums[i], nums[high] = nums[high], nums[i]
                    high -= 1
                else:
                    i += 1
            # 只继续搜索含目标下标的一侧，相等区域命中后可直接返回。
            if target < low:
                right = low - 1
            elif target > high:
                left = high + 1
            else:
                return nums[target]

    def findKthLargestHeap(self, nums: list[int], k: int) -> int:
        # 对照堆法：只保留最大的 k 个数，小顶堆堆顶就是它们的最小值。
        heap = []
        for value in nums:
            if len(heap) < k:
                heappush(heap, value)
            # 新值更大才替换堆顶；更小的值不可能进入前 k 大。
            elif value > heap[0]:
                heapreplace(heap, value)
        return heap[0]

    def findKthLargestQuick(self, nums: list[int], k: int) -> int:
        # 保留具名接口便于对照；默认提交入口已经使用同一高效实现。
        return self.findKthLargest(nums, k)
'''.strip(),
 'code_notes':['默认 findKthLargest 使用随机三路快速选择；findKthLargestHeap 是保留输入的对照实现。', 'low、high 界定等于枢轴的区间；遇到大值与右侧交换后，换回来的值尚未检查，i 不前进。', '随机化给出期望线性时间，不应写成最坏 O(n)；三路划分可以一次处理大量重复值。'],
 'pitfalls':['先去重会把题目变成第 k 个不同值。','用大顶堆保留 k 个，却从堆顶淘汰元素，会不断淘汰自己想保留的最大值。','快速选择的目标不是 k，也不是 k−1，而是升序下标 n−k。'],
 'complexity':'快速选择期望时间 O(n)、最坏 O(n²)，辅助空间 O(1)，会修改输入。堆法时间 O(n log(k+1))、辅助空间 O(k)，保留输入。',
 'quiz':{'question':'k=1 时，堆顶保存什么？','answer':'保存目前见过的最大值。每次更大值到来就替换唯一的候选，因此退化成一次求最大值的线性扫描。'},
 'tests':{'method': 'findKthLargest', 'cases': [{'args': [[3, 2, 1, 5, 6, 4], 2], 'expected': 5}, {'args': [[5, 5, 4], 2], 'expected': 5}, {'args': [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], 'expected': 4}, {'args': [[-3, -1, -2], 3], 'expected': -3}, {'args': [[1], 1], 'expected': 1}], 'permutation_args': [0]}
,
 'submission': {'name': '随机三路快速选择', 'why': '默认提交入口改为平均线性时间的快速选择，会原地重排 nums。若需要保留输入或处理流式数据，可使用 findKthLargestHeap；它的最坏时间界更稳定。', 'steps': ['把第 k 大转成升序位置 target=n-k。', '随机选一个枢轴，原地划分为小于、等于、大于三个区间。', '目标位置在相等区间就返回，否则只处理包含目标的一侧。'], 'diagram': '[ < pivot | = pivot | > pivot ]\n只保留含 target 的一段，不完整排序'},
})

CHAPTER['problems'].append({
 'id':347,'slug':'top-k-frequent-elements',
 'summary':'返回出现频率最高的 k 个不同数值，输出顺序不限，题目保证所选集合唯一。比较依据是出现次数，不是数值大小。主解使用频次桶达到线性时间，另给小顶堆变体。',
 'baseline':'先统计频次，再把所有不同值按频次排序，时间 O(n+u log u)，u 为不同值数量。频次只可能在 1..n 之间，可以直接作为桶下标，从高频桶往低频桶取值，避免比较排序。',
 'insight':'将 value→frequency 的映射倒过来，建立 frequency→这一频次的所有值。频率最高的桶先被访问，累计取到 k 个就停止。堆变体则只保留当前频次最高的 k 个候选，堆顶暴露频次最低者，两种方法都基于同一张计数表。',
 'steps':['用 Counter 统计每个不同值出现几次。','建立 n+1 个独立空桶，把每个 value 放入 buckets[frequency]。','从频次 n 向 1 遍历，把桶内的值依次加入答案，达到 k 个即返回。','堆变体以 (frequency,value) 为键；容量未满时压入，否则仅用更好的候选替换堆顶。'],
 'invariant':'桶法开始处理频次 f 时，所有更高频次的值都已被依序考虑，当前桶内每个值的频次恰好为 f。因此逐个输出不会越过一个更高频候选。堆法在每个不同值处理后，保存已处理集合中最好的 min(k,已处理数量) 项，比较键的第一项就是频次。',
 'examples':[{'label':'按频次倒置映射','input':'nums=[1,1,1,2,2,3]，k=2','output':'[1,2]，顺序不限','frames':[
  {'title':'先统计出现次数','note':'1 出现 3 次，2 出现 2 次，3 出现 1 次。数值较大的 3 反而频率最低。','table':{'headers':['值','频次'],'rows':[[1,3],[2,2],[3,1]]}},
  {'title':'放入以频次为下标的桶','note':'桶 1 保存 [3]，桶 2 保存 [2]，桶 3 保存 [1]；桶 4、5、6 为空。','table':{'headers':['频次桶','内容'],'rows':[[6,'[]'],[5,'[]'],[4,'[]'],[3,'[1]'],[2,'[2]'],[1,'[3]']]}},
  {'title':'从高频桶向下取值','note':'跳过空桶，从桶 3 取出 1，再从桶 2 取出 2，此时已有 k=2 项，直接返回。','array':[1,2],'array_label':'按频次选出的不同数值'}
 ]},{'label':'最高频值之间可以并列','input':'nums=[1,1,2,2,3]，k=2','output':'[1,2]，顺序不限','frames':[
  {'title':'频次 2 的桶里有两个值','note':'1、2 都在桶 2，3 在桶 1。高频集合仍唯一，桶内顺序不影响答案。','diagram':'bucket[2] = [1,2]\nbucket[1] = [3]'},
  {'title':'同一个桶取出两项后结束','note':'题目保证所选集合唯一，但不要求所有值的频次互不相同。','array':[1,2]}
 ]}],
 'walkthrough':['计数表把 n 个输入元素压缩成 u 个候选；堆里应放每个不同值的一条记录，不能把原数组每次出现都当成独立候选。','buckets=[[] for ...] 为每个频次创建不同列表。若写 [[]]*(n+1)，所有桶会引用同一个列表，往一个桶添加元素会让所有桶看起来一起变化。','小顶堆法在 k 接近 u、u 接近 n 时仍可能达到 O(n log n)。若要严格满足题目比 O(n log n) 更好的进阶要求，使用本题的桶主解。'],
 'code':'''
from collections import Counter
from heapq import heappush, heapreplace

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        # 先统计每个值出现的次数；频次最大不会超过数组长度。
        frequencies = Counter(nums)
        # 第 f 个桶保存出现 f 次的所有不同值，各桶必须是独立列表。
        buckets = [[] for _ in range(len(nums) + 1)]
        for value, frequency in frequencies.items():
            buckets[frequency].append(value)
        answer = []
        # 从高频桶向低频桶取，取满 k 个立即结束。
        for frequency in range(len(nums), 0, -1):
            for value in buckets[frequency]:
                answer.append(value)
                if len(answer) == k:
                    return answer

    # 对照方法：对不同值维护大小为 k 的堆，节省桶数组但增加堆操作。
    def topKFrequentHeap(self, nums: list[int], k: int) -> list[int]:
        heap = []
        for value, frequency in Counter(nums).items():
            # 元组优先比较频次，值只在频次相同时充当稳定的可比较项。
            item = (frequency, value)
            if len(heap) < k:
                heappush(heap, item)
            elif item > heap[0]:
                heapreplace(heap, item)
        return [value for frequency, value in heap]
'''.strip(),
 'api':{'signature':'collections.Counter(iterable) -> Counter\nmapping.items() -> dict_items','description':['Counter 对可哈希元素计数，得到“值→次数”的字典类对象，不会修改输入数组。items 提供键值对迭代视图，循环中的 value、frequency 分别接收一个数值和它的出现次数。','本题不需要 Counter.most_common，手动建立桶或维护堆才能展示算法。']},
 'code_notes':['桶下标上限为 n，因为任一数值最多出现 n 次；桶 0 不会存放实际候选。','堆元组第二项 value 只用于频次并列时提供确定的比较顺序，题目不要求按这个顺序输出。','两个方法都只读输入，返回的是不同值构成的新列表。'],
 'pitfalls':['把 (value,frequency) 当堆键会按数值大小筛选，偏离频次目标。','把次数为 k 的值误当答案，混淆了“取 k 项”和“频次等于 k”。','使用共享空列表创建桶会破坏各频次之间的隔离。'],
 'complexity':'主解平均时间 O(n)、空间 O(n)，其中计数表 O(u)，桶槽 O(n)，全部桶元素共 u 项。堆变体平均时间 O(n+u log(k+1))、辅助空间 O(u+k)，输出另计。',
 'quiz':{'question':'题目保证答案唯一，是否意味着所有频次都不同？','answer':'不是。只要选中集合在第 k 名边界处唯一即可，集合内部可以并列，例如频次为 2、2、1 且 k=2 时，两项高频值都必须选中。'},
 'tests':{'method':'topKFrequent','compare':'sorted','preserve_args':[0],'cases':[{'args':[[1,1,1,2,2,3],2],'expected':[1,2]},{'args':[[1,1,2,2,3],2],'expected':[1,2]},{'args':[[1],1],'expected':[1]},{'args':[[-1,-1,2],1],'expected':[-1]},{'args':[[4,3,2],3],'expected':[4,3,2]}]}
})

CHAPTER['problems'].append({
 'id':973,'slug':'k-closest-points-to-origin',
 'summary':'返回距离原点最近的 k 个二维点，顺序不限。题目保证选中答案唯一（忽略输出顺序）；比较距离时不需要开平方。',
 'baseline':'按距离排序全部点后取前 k 项，时间 O(n log n)。如果只需要最近 k 项，可以保留容量为 k 的候选堆，随时淘汰其中最远的点。',
 'insight':'欧氏距离的平方 x²+y² 与距离有相同大小关系，使用整数平方和避免浮点计算。我们要淘汰最大距离，因此把距离平方取负放进小顶堆：距离越大，负数越小，越容易位于堆顶。',
 'steps':['为每个点计算 distance=x*x+y*y，堆项使用 (-distance,index)。','堆未满时直接压入。','堆已满时比较新距离与 -heap[0][0]；只有新点更近才替换堆顶。','结束后根据堆中下标取回原始点，输出顺序无需排序。'],
 'invariant':'处理完任意前缀后，堆保存其中最近的 min(k,已处理数量) 个点，堆顶的负距离对应保留集合中最远者。更远的新点不能改进候选集合；更近的新点替换最远者后，仍保留正确的前 k 近集合。',
 'examples':[{'label':'在候选集合里淘汰最远点','input':'points=[[3,3],[5,-1],[-2,4]]，k=2','output':'[[3,3],[-2,4]]，顺序不限','frames':[
  {'title':'只比较距离平方','note':'三个点的平方距离分别为 18、26、20；顺序与开平方后的距离一致。','table':{'headers':['点','距离平方'],'rows':[['(3,3)',18],['(5,-1)',26],['(-2,4)',20]]}},
  {'title':'前两个点进入堆，最远者在根','note':'负距离堆为 [(-26,1),(-18,0)]，堆顶 -26 表示距离平方 26 的点最应该被淘汰。','diagram':'堆顶：(-26,1) → 点 (5,-1)\n另项：(-18,0) → 点 (3,3)'},
  {'title':'新点距离 20，比 26 更近','note':'用 (-20,2) 替换堆顶，保留平方距离 18、20 的两个点。输出可以按堆内任意顺序。','table':{'headers':['最终保留点','平方距离'],'rows':[['(3,3)',18],['(-2,4)',20]]}}
 ]},{'label':'坐标正负不影响平方距离比较','input':'points=[[1,3],[-2,2]]，k=1','output':'[[-2,2]]','frames':[
  {'title':'在坐标网格中标出两点','note':'网格从左到右 x=-3..3，从上到下 y=3..-3；O 为原点，A=(1,3)，B=(-2,2)。','grid':[['·','·','·','·','A','·','·'],['·','B','·','·','·','·','·'],['·','·','·','·','·','·','·'],['·','·','·','O','·','·','·'],['·','·','·','·','·','·','·'],['·','·','·','·','·','·','·'],['·','·','·','·','·','·','·']],'active_cells':[[1,1]]},
  {'title':'B 的距离平方更小','note':'A 为 1²+3²=10，B 为 (-2)²+2²=8。负坐标不能直接与正坐标比较大小，需要比较完整距离键。','diagram':'8 < 10 → 选择 B=(-2,2)'}
 ]}],
 'walkthrough':['第 215 题保留最大值时直接用正值小顶堆；这里保留最小距离，必须反转比较键，使最差候选仍在根。','堆中保存 index 可以避免复制整个点，也让并列负距离有整数下标可比较。返回时再按下标找回点坐标。','本题不需要计算平方根；平方根在非负数上严格递增，所以比较平方距离完全等价。'],
 'code':'''
from heapq import heappush, heapreplace

class Solution:
    def kClosest(self, points: list[list[int]], k: int) -> list[list[int]]:
        # 保留 k 个最近点；用负距离把小顶堆变成“最远候选在顶”的堆。
        heap = []
        for index, (x, y) in enumerate(points):
            # 比较平方距离即可，避免开平方与浮点误差。
            distance = x * x + y * y
            # 用下标取回原点，也避免元组继续比较列表内容。
            item = (-distance, index)
            if len(heap) < k:
                heappush(heap, item)
            # 新点比当前最远候选更近时才替换；输入点序保持不变。
            elif distance < -heap[0][0]:
                heapreplace(heap, item)
        return [points[index] for negative_distance, index in heap]
'''.strip(),
 'code_notes':['enumerate 给出点的原下标，(x,y) 同时解包两个坐标。','比较新点时使用正距离 distance 与恢复后的正堆顶距离，避免双重负号造成不等号方向错误。','方法不修改输入；返回外层列表是新的，内部坐标列表引用原 points 中的对应点。题目不要求深拷贝。'],
 'pitfalls':['用正距离小顶堆然后删除堆顶，会淘汰最近的点。','只比较 x 或只比较 y 都不能代表到原点的距离。','输出不要求有序，堆数组本身也不是从近到远排好的列表。'],
 'complexity':'时间 O(n log(k+1))，辅助堆 O(k)，输出 O(k)。平方距离按题目坐标范围使用精确整数计算。',
 'quiz':{'question':'堆顶第一项是 -26 时，它代表当前最近还是最远的候选？','answer':'代表最远候选，真实距离平方为 26。负数越小，对应的正距离越大，这正是负键模拟大顶堆的目的。'},
 'tests':{'method':'kClosest','compare':'sorted','preserve_args':[0],'cases':[{'args':[[[3,3],[5,-1],[-2,4]],2],'expected':[[3,3],[-2,4]]},{'args':[[[1,3],[-2,2]],1],'expected':[[-2,2]]},{'args':[[[0,0],[1,1]],1],'expected':[[0,0]]},{'args':[[[-1,0],[1,0]],2],'expected':[[-1,0],[1,0]]},{'args':[[[2,-3]],1],'expected':[[2,-3]]}]}
})

CHAPTER['problems'].append({
 'id':23,'slug':'merge-k-sorted-lists',
 'summary':'输入是 k 条有序链表的头节点列表，合并成一条升序链。各路可以为空，也可能 k=0。主解用堆维护每路最小的未读节点，重接原节点构成结果。',
 'baseline':'每次扫描全部 k 个当前头寻找最小值，需要 O(Nk) 时间；依次把第一条结果与下一条链合并，也可能多次扫描越来越长的结果。小顶堆把每次选最小候选降为对数成本。',
 'insight':'每条链本来有序，它后面的节点不可能比当前头更小。因此下一输出节点必定属于各路当前头之一。堆只需要保存每条非空链一个候选；某路头被取出后，再用同一路的后继补上。',
 'steps':['把每条非空链的 (node.val,source,node) 放进初始列表，heapify 成小顶堆。','创建 dummy 和结果尾 tail。','弹出最小候选，先保存其原后继 following，再把该节点接到 tail 后。','若 following 存在，以相同 source 编号把后继入堆。','直到堆空，令 tail.next=None，返回 dummy.next。'],
 'invariant':'堆在每轮开始时恰好保存每条尚未耗尽链的第一个未输出节点。每路后续值不小于它的候选，所以堆顶是所有剩余节点中的最小者。输出后只推进对应来源，恢复“每路一个候选”的不变量；结果前缀保持升序且每个原节点只输出一次。',
 'examples':[{'label':'每次只推进被选中的一路','input':'[[1,4,5],[1,3,4],[2,6]]','output':'1→1→2→3→4→4→5→6','frames':[
  {'title':'初始只把三个头入堆','note':'候选为 A:1、B:1、C:2。后面的 4、3、6 还不必进入堆。','diagram':'A：1 → 4 → 5\nB：1 → 3 → 4\nC：2 → 6\n堆中来源：A、B、C 各一个'},
  {'title':'取出 A 的 1，补入 A 的 4','note':'两个头值相等时，来源编号 0 小于 1，先取 A。堆不需要比较两个 ListNode 对象。','table':{'headers':['输出前缀','剩余候选'],'rows':[['1(A)','1(B),2(C),4(A)']]}},
  {'title':'再取 B 的 1、C 的 2、B 的 3','note':'每次只补入同一路后继，候选依次变化；输出目前为 1、1、2、3。','table':{'headers':['新输出','补入'],'rows':[['1(B)','3(B)'],['2(C)','6(C)'],['3(B)','4(B)']]}},
  {'title':'两路的 4 仍分别输出','note':'重复数值不去重，两个 4 是不同节点。继续得到 4、4、5、6，最终所有来源耗尽。','diagram':'1(A) → 1(B) → 2(C) → 3(B) → 4(A) → 4(B) → 5(A) → 6(C)'}
 ]},{'label':'空来源不占堆位置','input':'[[],[2],[]]','output':'2','frames':[
  {'title':'只加入第二条链的头','note':'空链的头为 None，不能读取 val，也无需放入堆。','diagram':'heap=[(2,1,节点2)]'},
  {'title':'取出唯一节点后堆空','note':'该节点没有后继，不补入任何内容，返回原节点 2。','diagram':'dummy → 原节点 2 → None'}
 ]}],
 'walkthrough':['source 既告诉我们来自哪一路，也为相同值提供可比较的第二字段。任一时刻每路最多一个候选，因此同一 source 不会同时出现两次，比较永远不需要继续到 Node 字段。','先保存 following 再接链，保证后续重连不会让我们丢失原链中尚未读取的入口。','本解法复用节点，会改变原链连接。输出必须保留全部节点和数值次数，不能通过新建同值节点掩盖重接是否正确。','平衡地两两分治合并也能达到 O(N log k)；与顺序一条条累计合并不同，它让每个节点只参与对数层合并。'],
 'code':'''
from heapq import heapify, heappop, heappush
from typing import Optional

class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def mergeKLists(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]:
        # 每条有序链表只放一个当前未读节点，堆大小至多为链表数。
        heap = []
        for source, node in enumerate(lists):
            if node is not None:
                # source 是链表编号，值相等时用于打破平局，避免比较节点对象。
                heap.append((node.val, source, node))
        heapify(heap)
        # 哨兵方便追加节点，结果复用输入节点，不复制整条链表。
        dummy = ListNode()
        tail = dummy
        while heap:
            value, source, node = heappop(heap)
            # 重连前保存这条链表的后继，下次只需把这个后继送入堆。
            following = node.next
            tail.next = node
            tail = node
            # 刚弹出的链表才需要补一个候选，其他链表的候选不变。
            if following is not None:
                heappush(heap, (following.val, source, following))
        # 显式终止结果链，保证尾节点不残留旧连接。
        tail.next = None
        return dummy.next
'''.strip(),
 'code_notes':['heapify 返回 None，代码只调用它，不写 heap=heapify(heap)。','初始列表为 k 个头，实际参数元素是节点对象而非页面显示的数值数组。','空输入或全部为空时，堆循环不执行，dummy.next 仍为 None。'],
 'pitfalls':['直接使用 (node.val,node) 会在相同值时尝试比较普通节点对象。','把全部节点都提前放进堆，会从 O(k) 辅助候选扩大到 O(N)，浪费各路已经有序的条件。','把同值候选当成重复数据删除，会减少原输入节点数量。'],
 'complexity':'设节点总数 N、输入路数 k、非空路数 q。时间 O(k+N log(q+1))，包含扫描全部来源；辅助堆 O(q)，只新建一个哑节点，输出复用原节点。',
 'quiz':{'question':'为什么弹出 A 的头之后，只需要补入 A 的后继，而不重新读取所有路？','answer':'其他来源的候选没有变化，它们仍是各自最小未读项。只有 A 消耗了一项，需要让其下一项成为新的候选。'},
 'tests':{'adapter':'linked','mode':'list_of_lists','method':'mergeKLists','reuse_nodes':True,'cases':[{'args':[[[1,4,5],[1,3,4],[2,6]]],'expected':[1,1,2,3,4,4,5,6]},{'args':[[]],'expected':[]},{'args':[[[]]],'expected':[]},{'args':[[[],[2],[]]],'expected':[2]},{'args':[[[7,7],[7],[7,7]]],'expected':[7,7,7,7,7],'expected_indices':[0,1,2,3,4]}]}
})

CHAPTER['problems'].append({
 'id':378,'slug':'kth-smallest-element-in-a-sorted-matrix',
 'summary':'方阵每行、每列均非递减，求全部 n² 个元素中的第 k 小值，重复值分别计数。主解把各行作为有序流归并；另给按值二分的 O(1) 辅助空间方法。',
 'baseline':'展平并排序全部元素需要 O(n²) 额外空间，超过题目希望的空间规模。按行取当前最小未读值，只需 n 个堆候选；若同时利用行列有序，还能快速统计不大于一个试探值的元素数量。',
 'insight':['堆法与第 23 题相同：每行起点入堆，弹出 (value,row,col) 后，只加入同行下一列。第 k 次弹出的 value 就是答案，不需要构造完整排序结果。','按值二分：定义 count(x)=矩阵中 ≤x 的元素数量。x 越大，count 不减；要找第一个使 count(x)≥k 的整数 x。利用行列有序，从左下角阶梯扫描可在 O(n) 时间完成一次计数。'],
 'steps':['堆对照方法：把每行首项 (matrix[row][0],row,0) 建成小顶堆。','重复 k 次弹出最小项，若该行仍有下一列则入堆；返回最后弹出的值。','推荐二分方法：low=左上角、high=右下角，计算 mid。','从左下角统计 ≤mid 的数量：当前值≤mid 时，这一列上方所有 r+1 项都合格，累加并右移；否则上移。','count≥k 时 high=mid，否则 low=mid+1；最终返回 low。'],
 'invariant':['堆中每行恰有一个最小未读候选，每次弹出都是全矩阵剩余元素的最小值，因此第 k 次弹出正确，位置不同的相等值会分别弹出。','二分始终保留第 k 小值：若 ≤mid 的元素至少 k 个，答案不大于 mid；否则答案严格大于 mid。计数时，行列单调性保证从左下角一次移动即可排除一行的当前候选或一次统计一整列的合格前缀，累计不会重计同一位置。'],
 'examples':[{'label':'三条有序流只弹出前八项','input':'matrix=[[1,5,9],[10,11,13],[12,13,15]]，k=8','output':'13','frames':[
  {'title':'每行只取第一项作候选','note':'初始候选为 (1,0,0)、(10,1,0)、(12,2,0)。每行后续元素只会更大或相等。','grid':[[1,5,9],[10,11,13],[12,13,15]],'active_cells':[[0,0],[1,0],[2,0]]},
  {'title':'第一行依次输出 1、5、9','note':'每次弹出后补入该行下一列，这三个值都比其他行当前首项小。第一行耗尽后不再占堆位置。','table':{'headers':['名次',1,2,3],'rows':[['值',1,5,9]]}},
  {'title':'继续输出 10、11、12','note':'第二行推进到 13，第三行的 12 随后被弹出并补入另一个 13。','grid':[[1,5,9],[10,11,13],[12,13,15]],'active_cells':[[1,2],[2,1]],'metrics':[['已输出','1,5,9,10,11,12']]},
  {'title':'两个 13 占第七、第八名','note':'它们位于不同位置，不能去重。第八次弹出仍为 13，立即得到所求值。','table':{'headers':['名次',7,8],'rows':[['值',13,13]]}}
 ]},{'label':'按值二分不要求 mid 出现在矩阵中','input':'相同矩阵与 k=8，使用 kthSmallestBinary','output':'13','frames':[
  {'title':'试探 mid=8，只有两项不超过它','note':'8 不是矩阵中的元素，但 count(8)=2<8，说明答案更大，low 从 1 改为 9。','grid':[[1,5,9],[10,11,13],[12,13,15]],'active_cells':[[0,0],[0,1]]},
  {'title':'继续按计数缩小值域','note':'每次计数包含等于 mid 的全部重复项，不能用严格小于代替。','table':{'headers':['low','high','mid','count(≤mid)','更新'],'rows':[[9,15,12,6,'low=13'],[13,15,14,8,'high=14'],[13,14,13,8,'high=13']]}},
  {'title':'low 与 high 同为 13','note':'第一个累计数量达到 k 的值必是某个矩阵值，因为计数只在遇到矩阵中实际出现的值时增加。','diagram':'count(12)=6 < 8\ncount(13)=8 ≥ 8\n最小可行值：13'}
 ]}],
 'walkthrough':['按行归并只依赖每行有序；二分计数同时利用每行与每列有序。相同输入结构可以提供不同强度的可利用条件。','计数从左下角开始，若 matrix[r][c]≤mid，则本列 0..r 都合格，一次加入 r+1，再进入下一列；若太大，则当前行在当前列不合格，需要向上缩小行范围。','二分变量表示数值，不是矩阵下标。即使 mid 落在不存在的整数间隙，计数谓词仍有效；最终阈值对应第 k 小实际元素。','n=1 或所有元素相等时，二分可能一轮也不执行，两个角落本身就给出唯一值。'],
 'code':'''
from heapq import heapify, heappop, heappush

class Solution:
    def kthSmallest(self, matrix: list[list[int]], k: int) -> int:
        n = len(matrix)
        # 按数值范围二分，寻找“至少有 k 个数不大于它”的最小值。
        low, high = matrix[0][0], matrix[-1][-1]
        while low < high:
            mid = (low + high) // 2
            # 从左下角统计 ≤mid 的元素数，一次排除一行或一列。
            row, col, count = n - 1, 0, 0
            while row >= 0 and col < n:
                if matrix[row][col] <= mid:
                    # 当前格 ≤mid，则这一列从第 0 行到 row 行都满足条件。
                    count += row + 1
                    col += 1
                else:
                    row -= 1
            # 候选值已经够大，保留 mid 并缩小上界；否则提高下界。
            if count >= k:
                high = mid
            else:
                low = mid + 1
        return low

    def kthSmallestHeap(self, matrix: list[list[int]], k: int) -> int:
        n = len(matrix)
        # 对照堆法：每行只放最小的尚未弹出值，逐次归并有序行。
        heap = [(matrix[row][0], row, 0) for row in range(n)]
        heapify(heap)
        # 第 k 次弹出的值就是第 k 小，重复值也各占一个排名。
        for _ in range(k):
            value, row, col = heappop(heap)
            if col + 1 < n:
                heappush(heap, (matrix[row][col + 1], row, col + 1))
        return value

    def kthSmallestBinary(self, matrix: list[list[int]], k: int) -> int:
        # 保留具名接口便于对照；默认提交入口已经使用同一高效实现。
        return self.kthSmallest(matrix, k)
'''.strip(),
 'code_notes':['默认 kthSmallest 使用按值二分；kthSmallestHeap 保留按行归并的对照方法。', 'count+=row+1 一次计入同一列上方的全部合格元素，重复值照常各占一个排名。', '二分求的是最小可行值，mid 未必出现在矩阵中，但最后收敛值一定是对应排名的元素。'],
 'pitfalls':['把重复值去掉会改变名次，第七与第八小都可能是 13。','把矩阵直接视为一维整体有序数组做下标二分不成立，下一行首项未必大于上一行尾项。','计数成功后应 high=mid 保留当前可行值，不能无依据地排除 mid。'],
 'complexity':'按值二分时间 O(n log(V+1))、辅助空间 O(1)，V 为最大值与最小值之差。堆法时间 O(n+k log n)、辅助空间 O(n)。',
 'quiz':{'question':'为什么 count(mid) 可能一次从 6 跳到 8？','answer':'矩阵里可能有两个相同值，例如两个 13。阈值从 12 变到 13 时，两项同时纳入计数；第七小和第八小因此都是 13。'},
 'tests':{'method':'kthSmallest','preserve_args':[0],'cases':[{'args':[[[1,5,9],[10,11,13],[12,13,15]],8],'expected':13},{'args':[[[-5]],1],'expected':-5},{'args':[[[1,1],[1,1]],3],'expected':1},{'args':[[[1,3],[2,4]],2],'expected':2},{'args':[[[-5,-2],[-3,0]],4],'expected':0}]}
,
 'submission': {'name': '按值二分与阶梯计数', 'why': '默认使用常数辅助空间的按值二分，同时利用行列有序。值域很宽而 k 很小时，kthSmallestHeap 可能更合适；两者没有对全部输入都成立的时间优劣顺序。', 'steps': ['答案位于左上角最小值与右下角最大值之间。', '对候选 mid，从左下角用 O(n) 时间统计 ≤mid 的元素数。', '计数至少为 k 就缩小上界，否则增大下界；最终得到第 k 小的实际值。'], 'diagram': '计数(mid) < k → mid 太小\n计数(mid) ≥ k → 保留 mid 并向更小值搜索'},
})
