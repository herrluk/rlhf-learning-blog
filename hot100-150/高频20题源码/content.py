"""20 题的独立学习路径与导读；考频仅沿用已披露的样本统计。"""

RANKED = [(3,301),(146,226),(215,138),(53,117),(206,112),(300,107),
          (20,100),(200,94),(25,82),(15,79),(5,78),(23,74),(56,73),
          (19,68),(72,64),(42,64),(21,63),(102,61),(236,58),(121,52)]
SOURCE = 'https://onefly.top/zero2Leetcode/05_interview/coding/hot100-frequency-202608/index.html'

GROUPS = [
    dict(title='先学会维护状态', ids=[20,121,53,3],
         lead='从一趟扫描开始：每读入一个元素，只更新真正影响后续答案的状态。',
         body=['20 用栈记住尚未闭合的括号；121 记住今天之前的最低买价；53 记住必须在当前位置结尾的最大和；3 记住当前无重复窗口。四题都只扫一遍，但状态的含义完全不同。',
               '先用一句话定义变量，再决定更新顺序。例如 121 先尝试今天卖出，再更新最低买价；3 先把窗口恢复合法，再更新最长长度。状态含义明确，顺序才有依据。',
               '子数组、子串必须连续；子序列允许跳过元素。53 允许负数，窗口和不随扩张单调变化，不能照搬 3 的收缩条件。后面的 300 求子序列，问题又不同。'],
         diagram='读入一个元素 → 更新必要状态 → 恢复约束（如有） → 更新答案\n20：未匹配括号栈          121：历史最低价\n53：当前位置结尾的最优和   3：无重复的连续窗口',
         apis=[('list.append(value) -> None\nlist.pop() -> object', 'append 把一个元素追加到列表末尾；pop 删除并返回末尾元素，空列表调用会抛出 IndexError。二者配合就是栈。append 的返回值不是修改后的列表。'),
               ('enumerate(iterable, start: int = 0) -> enumerate\ndict.get(key, default=None) -> object', 'enumerate 逐个产生 (下标, 元素)，不先复制输入。dict.get 返回对应值，键不存在时返回 default，不会自动插入键。第 3 题用 get(ch, 0) 读取已有次数，再显式写回新次数。')]),
    dict(title='用有序性决定移动方向', ids=[15,56,42],
         lead='先证明可以舍弃哪些候选，再移动指针或合并区间。',
         body=['15 排序之后，固定一个数，用左右指针寻找剩下两个数：和太小只能增大左值，和太大只能减小右值。每次移动都排除一批不可能的配对。',
               '56 按区间起点排序，后来的区间只需与当前合并段比较。42 保留原来的柱子顺序，从两端维护最高墙；排序会破坏题意，不能因为同属这一模块就先排序。',
               '42 中“较低的一侧可以结算”说的是已经见过的两侧最高墙。当左侧最高墙不高于右侧最高墙，右边已经有足够高的挡板，当前左列的水量便确定了。'],
         diagram='15：和偏小 → left 右移；和偏大 → right 左移\n56：有交集 → 扩大右端；有间隙 → 新开一段\n42：left_max ≤ right_max → 结算左列；否则结算右列',
         apis=[('sorted(iterable, *, key=None, reverse: bool = False) -> list\nlist.sort(*, key=None, reverse: bool = False) -> None', 'sorted 返回新的排序列表，sort 原地调整已有列表。key 接收每个元素并返回排序依据；例如 lambda interval: interval[0] 按区间左端排序。sorted 对嵌套列表仅复制外层；第 56 题另建结果区间，才能避免改动输入中的内层列表。')]),
    dict(title='链表：先保住后继，再改连接', ids=[206,21,19,25,146],
         lead='先练一条边的反转，再练合并、删除、分组重连，最后组合成缓存。',
         body=['链表题中的变量保存节点引用。a = b 只是让两个变量指向同一个节点；a.next = b 则改变节点之间的边。这两种操作必须分清。页面用箭头展示链表，平台实际传入的是节点对象。',
               'dummy 是放在真实头节点之前的哨兵。它让“修改头节点”和“修改中间连接”可以使用同一套操作；返回的是 dummy.next。',
               '206 学会保存 nxt 再反转；21 学会用 tail 接结果；19 让慢指针停在待删节点的前驱；25 将这些操作限制在一组内；146 再加上 prev 反向连接和哈希定位。'],
         diagram='反转前：prev → 已反转前缀     cur → 当前节点 → nxt → 后缀\n先保存 nxt，再让 cur.next = prev\n推进后：prev → 当前节点 → 已反转前缀     cur → nxt → 后缀',
         apis=[('dict.pop(key, default=None) -> object', '返回并删除键对应的值；键不存在时返回给定的 default。与只读取的 get 不同，pop 会改变字典。LRU 的链表节点始终与哈希表中的节点是同一对象，不能各保存一份互不相干的副本。')]),
    dict(title='堆与选择：只整理需要的部分', ids=[215,23],
         lead='第 K 大不需要完整排序，K 路归并只需比较每一路当前最小的候选。',
         body=['215 的快速选择把目标改写成升序下标 n-k，每次划分为小于、等于、大于枢轴三段，只继续处理目标所在的一段。随机化给出期望线性时间，最坏情况仍是平方时间。',
               '215 的堆法保留最大的 k 个元素，用小顶堆快速淘汰其中最小者。23 则从各链当前头节点中选最小者；取出哪一路，就只补入那一路的后继。',
               'Python 的 heapq 是小顶堆，heap[0] 是最小值。堆只保证父节点不大于孩子，堆数组的其他位置没有完整排序。23 的 (value, source, node) 用来源编号打破同值平局，避免 Python 比较节点对象。'],
         diagram='215：全体元素 → [小于枢轴 | 等于枢轴 | 大于枢轴] → 留下目标段\n23：A 的当前头 ┐\n    B 的当前头 ├→ 小顶堆 → 取最小值 → 只补同一路后继\n    C 的当前头 ┘',
         apis=[('heapq.heapify(heap: list) -> None\nheapq.heappush(heap: list, item) -> None\nheapq.heappop(heap: list) -> object\nheapq.heapreplace(heap: list, item) -> object', 'heapify 在线性时间内原地建堆；heappush 插入；heappop 删除并返回最小项，空堆会报错。heapreplace 要求非空，会无条件弹出原最小项并插入新项，所以 215 的堆法必须先判断新值是否值得保留。'),
               ('random.randint(a: int, b: int) -> int', '返回闭区间 [a, b] 内的随机整数，两端都可能取到。215 用它选枢轴下标；可视化固定一次枢轴选择以方便复盘，提交代码仍使用随机枢轴。')]),
    dict(title='树与网格：明确遍历顺序', ids=[102,236,200],
         lead='按层处理、先处理孩子、遍历连通块，分别对应三种不同的搜索任务。',
         body=['102 用队列按层访问。开始一层时固定队列长度，内循环中新加入的孩子属于下一层。不能一边往队列加节点，一边把队列全部清空当作一层。',
               '236 要先获得左右子树的查找结果，再决定父节点返回什么，这是后序顺序。代码用显式栈的 expanded 标记区分“准备访问孩子”和“孩子已经完成”，避免深树依赖 Python 递归调用栈。',
               '200 的外层循环负责发现新岛，内层搜索负责标记整座岛。发现邻居时立即标记，再放入栈，可避免同一格被多个方向重复加入。'],
         diagram='102：队列先进先出 → 一层一层取节点\n236：先左、再右、最后合并父节点结果\n200：找到未访问陆地 → 岛数加一 → 标记全部连通陆地',
         apis=[('collections.deque(iterable=(), maxlen: int | None = None) -> deque\ndeque.append(value) -> None\ndeque.popleft() -> object', 'deque 创建双端队列，默认不限制长度。append 从右端加入，popleft 从左端删除并返回元素；空队列调用 popleft 会报错。两端操作为常数时间，102 不用需要移动后续元素的 list.pop(0)。')]),
    dict(title='进阶状态：长度、编辑与回文', ids=[300,72,5],
         lead='从能解释的基础状态出发，再理解二分、空间压缩和对称信息复用。',
         body=['300 把“每个下标结尾的最长长度”压缩为“每种长度能够拥有的最小末尾”，再用二分更新。tails 是一组最优末尾的摘要，不保证整体就是原序列的一条子序列。',
               '72 先理解二维表的上、左、左上分别代表哪种操作，再压缩到一行。覆盖旧值之前必须保存左上角；只背一个 min 表达式容易把新旧行混用。',
               '5 先想清楚围绕中心向两边扩展。Manacher 再利用已知回文的对称性，复用镜像半径并只检查未知部分。它是本手册理解成本最高的一题，安排最后；代码仍给出线性时间入口及中心扩展、二维 DP 对照。'],
         diagram='300：同样的长度，末尾越小，未来越容易接上新数\n72：当前格 ← 上方 / 左方 / 左上；压缩后仍保留这三个来源\n5：当前中心 ← 镜像已知半径 + 已知边界外的新比较',
         apis=[('bisect.bisect_left(a: list, x, lo: int = 0, hi: int | None = None) -> int', '在有序区间内返回第一个不小于 x 的位置；hi 省略时为 len(a)，这里的 None 表示省略上界。函数只查位置，不插入元素。若返回 len(tails)，才 append；遇到相等值时替换，严格递增长度不增加。')]),
]

BRIDGES = {
    20:'起点题。先画出尚未配对的左括号，感受“最后进入的必须最先处理”。',
    121:'从保存多个括号，过渡到只保存一个最有用的历史值：今天以前的最低价。',
    53:'与 121 一样保留历史摘要，但这里必须区分“以当前元素结尾”与“全局最优”。',
    3:'把一个状态扩成一段窗口。收缩时不能只移动 left，还要同步移除旧字符的次数。',
    15:'把窗口的单向移动思想迁移到有序数组；指针移动依据是和的大小，先掌握去重。',
    56:'继续使用排序带来的顺序信息；这次把一串互相重叠的区间压缩成一个当前合并段。',
    42:'双指针进阶。先解释为何较低最高墙一侧水位已确定，再写结算公式。',
    206:'进入链表之前，把数组下标暂时放下；这里操作的是节点之间的 next 边。',
    21:'复用 206 对节点引用的理解，用 tail 连接结果，并让来源指针各自向后走。',
    19:'引入哨兵和固定间距：目标是让 slow 停在待删节点之前，而不是停在目标本身。',
    25:'将 206 的反转限制在 k 个节点内，再用 19 的前驱视角接回前后两段。',
    146:'链表综合题。先用图解释摘除和插头，再加入字典定位；读命中也会改变使用顺序。',
    215:'先区分“找第 k 大”和“把全部元素排好”。可先学堆作对照，再完成三路快速选择。',
    23:'这是 21 的多路推广：两路比两个头，k 路用堆维护 k 个头，不必把所有节点一次放入堆。',
    102:'从线性链表进入树。用队列把分支按深度组织起来，先固定一层，再读取下一层。',
    236:'从按层访问转向先子后父。先定义每棵子树返回什么，再把递归返回过程翻译成显式栈。',
    200:'把树上的搜索推广到可能从多个方向重复到达的网格，增加“发现即标记”的约束。',
    300:'回到数组。用 53 的状态定义习惯先理解 O(n²) DP，再学习 tails 的压缩与二分。',
    72:'从一维序列状态扩展到两个字符串的前缀状态；先画二维表，再逐格对照滚动行。',
    5:'最后处理回文。先看中心扩展的对称关系，再研究哪些比较可以从镜像复用。',
}


def frame(title, note, **visual):
    return dict(title=title, note=note, **visual)


def quick_trace():
    nums=[3,2,1,5,6,4]; target=4; left=0; right=5; frames=[]
    frames.append(frame('目标不是完整排序', '第 2 大对应升序下标 6−2=4。下面固定每轮中间位置作为枢轴，展示一次合法分区过程；提交代码随机选枢轴。', array=nums.copy(), pointers={'target':target}))
    while left<=right:
        pivot=nums[(left+right)//2]; low=i=left; high=right
        frames.append(frame('选择枢轴', f'本轮只处理 [{left},{right}]，pivot={pivot}。low 到 i 之前是相等区，i 到 high 是未知区。',array=nums.copy(),active=list(range(left,right+1)),pointers={'low':low,'i':i,'high':high,'target':target},metrics=[['pivot',pivot]]))
        while i<=high:
            changed=i; value=nums[i]
            if value<pivot:
                nums[low],nums[i]=nums[i],nums[low];low+=1;i+=1
                note=f'{value} 小于 {pivot}：交换到小值区末尾，low 与 i 一起前进。'
            elif value>pivot:
                nums[i],nums[high]=nums[high],nums[i];high-=1
                note=f'{value} 大于 {pivot}：交换到右端，high 左移；换回的值还没看过，i 不能前进。'
            else:
                i+=1;note=f'{value} 等于枢轴：相等区向右扩大，只推进 i。'
            frames.append(frame('检查一个未知元素',note,array=nums.copy(),changed=changed,pointers={'low':low,'i':i,'high':high,'target':target},metrics=[['pivot',pivot]],diagram=f'小值区 [{left},{low}) | 相等区 [{low},{i})\n未知区 [{i},{high}] | 大值区 ({high},{right}]\n空区间表示该部分当前没有元素。'))
        if target<low: right=low-1
        elif target>high: left=high+1
        else:
            frames.append(frame('目标落入相等段',f'下标 {target} 位于 [{low},{high}]，返回 {nums[target]}。左右其他元素不必排好。',array=nums.copy(),active=list(range(low,high+1)),pointers={'target':target},metrics=[['第 2 大',nums[target]]]));break
    return dict(label='推荐代码：三路快速选择逐次分区',input='nums=[3,2,1,5,6,4], k=2',output='5',frames=frames)


def rain_trace():
    a=[4,2,0,3,2,5]; left=0;right=5;lm=rm=water=0; settled=[];frames=[]
    frames.append(frame('两端向中间扫描','绿色为已经结算的列；橙色为本轮结算列。先更新最高墙，再判断结算哪边。',array=a,pointers={'left':left,'right':right},metrics=[['总水量',0]]))
    while left<=right:
        lm=max(lm,a[left]);rm=max(rm,a[right]);pos=left if lm<=rm else right
        amount=(lm if lm<=rm else rm)-a[pos];water+=amount;settled.append(pos)
        frames.append(frame('结算左列' if lm<=rm else '结算右列',f'左侧最高墙 {lm}，右侧最高墙 {rm}。下标 {pos} 水量为 {min(lm,rm)}−{a[pos]}={amount}，累计 {water}；结算后移动这一侧。',array=a,active=settled.copy(),changed=pos,pointers={'left':left,'right':right},metrics=[['left_max',lm],['right_max',rm],['总水量',water]]))
        if lm<=rm:left+=1
        else:right-=1
    frames.append(frame('全部列已结算','逐列水量 0+2+4+1+2+0=9。每列只结算一次，不重复计算。',array=a,active=settled,metrics=[['结果',water]]))
    return dict(label='推荐代码：双指针逐列结算',input='height=[4,2,0,3,2,5]',output='9',frames=frames)


def tails_trace():
    from bisect import bisect_left
    a=[10,9,2,5,3,7,101,18]; tails=[];frames=[]
    frames.append(frame('每种长度只保留最小末尾','tails 初始为空；第 t 项表示长度 t+1 的最小末尾，不表示在原数组中的位置。',array=a,table={'headers':['长度','最小末尾'],'rows':[]}))
    for i,x in enumerate(a):
        before=tails.copy();pos=bisect_left(tails,x);added=pos==len(tails)
        if added:tails.append(x)
        else:tails[pos]=x
        frames.append(frame('追加：出现更长序列' if added else '替换：降低同长度末尾',f'读入 {x}。在 {before} 中，第一个 ≥{x} 的位置是 {pos}；'+('它等于当前长度，因此追加。' if added else '替换此位置，长度保持不变。'),array=a,changed=i,active=list(range(i+1)),table={'headers':['序列长度','该长度最小末尾'],'rows':[[j+1,v] for j,v in enumerate(tails)]},metrics=[['答案长度',len(tails)]]))
    return dict(label='推荐代码：tails 如何替换与增长',input='nums=[10,9,2,5,3,7,101,18]',output='4',frames=frames)


def edit_trace():
    s='cat'; t='cut'; dp=list(range(4));grid=[dp.copy()]+[['·']*4 for _ in range(3)];frames=[]
    frames.append(frame('初始化空串这一行','列依次表示空串、c、cu、cut；把空串变成这些前缀，分别需要 0、1、2、3 次插入。',grid=[['','∅','c','cu','cut']]+[[['∅','c','ca','cat'][i]]+row for i,row in enumerate(grid)],array=dp.copy()))
    for i,ch in enumerate(s,1):
        diagonal=dp[0];dp[0]=i;grid[i][0]=i
        for j,other in enumerate(t,1):
            above=dp[j];left=dp[j-1];old_diag=diagonal
            dp[j]=diagonal if ch==other else 1+min(above,left,diagonal)
            grid[i][j]=dp[j]
            frames.append(frame(f'计算 {s[:i]} → {t[:j]}',f'上方旧值={above}，左方新值={left}，左上旧值={old_diag}。'+(f'{ch} 与 {other} 相同，直接取左上 {dp[j]}。' if ch==other else f'字符不同，1+min({above},{left},{old_diag})={dp[j]}。')+f'写入后，把 diagonal 更新为刚才的上方值 {above}，供下一列使用。',grid=[['','∅','c','cu','cut']]+[[['∅','c','ca','cat'][r]]+row.copy() for r,row in enumerate(grid)],active_cells=[[i+1,j+1]],array=dp.copy(),changed=j,metrics=[['diagonal（覆盖前）',old_diag],['above（覆盖前）',above]],diagram=f'滚动数组下标 < {j}：当前行新值\n滚动数组下标 > {j}：上一行旧值\n下标 {j} 刚写成当前行值 {dp[j]}'))
            diagonal=above
    return dict(label='推荐代码：二维表与滚动数组同步看',input='word1="cat", word2="cut"',output='1',frames=frames)


def manacher_trace(s):
    t=[None]
    for ch in s:t.extend((ch,None))
    display=['◇' if x is None else x for x in t];radius=[0]*len(t);center=right=best_center=best_radius=0;frames=[]
    frames.append(frame('统一奇偶回文中心','图中 ◇ 代表代码里的 None 分隔符，它不可能等于原字符串字符。半径按变换后的格数计算。',array=display,diagram=f'原串：{s}\n变换后长度：2×{len(s)}+1={len(t)}'))
    for i in range(len(t)):
        old_right=right;mirror=2*center-i;seed=0
        if i<right:seed=min(radius[mirror],right-i);radius[i]=seed
        pairs=[]
        while i-radius[i]-1>=0 and i+radius[i]+1<len(t) and t[i-radius[i]-1]==t[i+radius[i]+1]:
            pairs.append((i-radius[i]-1,i+radius[i]+1));radius[i]+=1
        reuse=f'i={i} 在已知右边界 {old_right} 内，镜像位置 {mirror} 的半径为 {radius[mirror]}，可直接复用 min({radius[mirror]},{old_right-i})={seed}。' if i<old_right else f'i={i} 不在已知右边界 {old_right} 内，从半径 0 开始。'
        if i+radius[i]>right:center,right=i,i+radius[i]
        if radius[i]>best_radius:best_center,best_radius=i,radius[i]
        frames.append(frame(f'处理中心 i={i}',reuse+f'随后新验证 {len(pairs)} 对相等位置，最终半径 {radius[i]}；已知最右边界更新为 {right}。',array=display,active=list(range(i-radius[i],i+radius[i]+1)),changed=i,pointers={'i':i,'center':center,'right':right},metrics=[['复用半径',seed],['当前半径',radius[i]],['最长原串长度',best_radius]],diagram='新验证的对称位置：'+(', '.join(f'({a},{b})' for a,b in pairs) or '无')+'\n已知区域内由对称性保证的字符对，不重新逐个比较。'))
    start=(best_center-best_radius)//2;answer=s[start:start+best_radius]
    frames.append(frame('映射回原字符串',f'最长中心 {best_center}，半径 {best_radius}。起点=({best_center}−{best_radius})//2={start}，取原串长度 {best_radius}，得到 {answer}。',array=list(s),active=list(range(start,start+best_radius)),metrics=[['返回',answer]]))
    return dict(label=f'推荐代码：Manacher / {s}',input=f's="{s}"',output=f'"{answer}"',frames=frames)


def enrich(p):
    """只改独立手册中的拷贝，不覆盖原有 160 题内容。"""
    n=p['id']
    if n in (42,215,300,5):
        original_steps=p['steps']
        # 主线与推荐入口一致；原来的基础方案仍在关键观察中明确保留。
        p.setdefault('insight_sections',[]).append(dict(title='基础对照方案的步骤',body=original_steps))
        p['steps']=p['submission']['steps'].copy()
    if n==215:
        p['summary']='返回按降序排列后的第 k 个元素，重复数值分别占据名次，不是第 k 个不同数值。推荐代码使用随机三路快速选择，并保留小顶堆对照方法。'
        p['examples'].insert(0,quick_trace())
        p['invariant']=['一轮分区过程中，[left,low) 的值小于 pivot，[low,i) 等于 pivot，[i,high] 尚未检查，(high,right] 大于 pivot。只有未知区需要继续处理。', '分区结束后，相等区每个位置都应放 pivot。目标不在这一段时，可排除不含目标的一侧；不需要知道被排除区间内部的精确顺序。']
        p['walkthrough'].insert(0,'先看三路分区的演示：交换到右端后，i 停在原处，因为右端换回来的值还属于未知区。后两个例子展示堆法的候选维护。')
    elif n==42:
        p['summary']='非负整数数组表示单位宽度柱子的高度，求降雨后柱子之间最多能存多少水。推荐双指针：时间 O(n)、额外空间 O(1)；另保留按水层结算的单调栈对照。'
        p['examples'].insert(0,rain_trace())
        p['invariant']=['left 左边和 right 右边的列均已正确结算，尚未结算的是闭区间 [left,right]。', '先计入当前两根柱子：若 left_max≤right_max，左格已经有最高为 left_max 的左墙，右边又确知存在不低于它的墙，因此水位恰好由 left_max 限制；右侧情形对称。每轮只结算并移动一端。']
        p['walkthrough']=['优先看“推荐代码”例子：左墙 4、右墙 5，右边已够高，左侧各列水量依次为 0、2、4、1、2；最后最高柱水量为 0，总计 9。', '每轮先更新最高墙，再做减法，所以当前列不会得到负水量；移动的是最高墙较低的一端。', '单调栈对照演示按横向水层求和，双指针按竖向水列求和，二者只是在分解同一批水格。']
    elif n==300:
        p['examples'].insert(0,tails_trace())
        p['invariant']=['tails[t] 是处理过的前缀中，长度为 t+1 的严格递增子序列能达到的最小末尾。只保留最小末尾，不会失去未来接上更大元素的机会。', 'tails 严格递增，因此可以二分。找到第一个 ≥x 的位置 pos：前一长度的尾值 <x，可以接上 x；替换同长度尾值会更好或不变。没有这样的元素时追加，答案长度加一。']
        p['walkthrough'].insert(0,'推荐代码演示中，5 被 3 替换时长度仍为 2；101 被 18 替换时长度仍为 4。替换表示改善后续扩展条件，只有追加才增长答案。')
    elif n==72:
        p['examples'].insert(0,edit_trace())
        p['complexity']='设两串长度为 m、n。非空时滚动 DP 时间 O(mn)，含空串边界的统一上界 O((m+1)(n+1))；辅助空间 O(min(m,n)+1)。对照完整表辅助空间 O((m+1)(n+1))。'
    elif n==5:
        p['examples']=[manacher_trace('abacaba'),manacher_trace('aaaa')]+p['examples']
        p['insight_sections']+= [
            dict(title='为什么可以复用镜像半径',body=['先不用公式：已知一个大回文，它左右两半互为镜像。若当前位置 i 落在这个大回文里，那么它左侧对应位置 mirror 的小回文，在没有碰到大回文边界的范围内，也能镜像到 i 周围。', '但已知大回文右边界之外的字符还没有保证。即使镜像半径更大，也只能复用到 right-i，所以初始半径是 min(radius[mirror], right-i)。截断后，再像中心扩展一样逐对比较未知字符。'],diagram='已知大回文： [ 左边界 …… mirror …… center …… i …… right ]\n                                    mirror = 2×center−i\n镜像能保证的半径，必须截断到当前已知 right 以内。'),
            dict(title='right 和半径到底包含不包含边界',body=['这份代码的 right 是当前已知最远回文的最右格下标，包含这一格；半径 r 对应闭区间 [i-r,i+r]。测试下一对字符时看 i-r-1 与 i+r+1。', '变换后在字符之间及两端放 None，奇数与偶数长度回文都有单个中心。例如 aaaa 变成 ◇a◇a◇a◇a◇，中心下标 4、半径 4，对应原串长度 4；起点为 (4-4)//2=0。']),
            dict(title='为什么没有退化成平方时间',body=['镜像回文完全落在已知范围内时，其外侧不匹配也会被镜像，当前中心不需要重新逐对扩展。若半径触及已知边界，只有越过 right 的部分需要新比较。', '所有成功的新扩展推动最右边界前进，right 从不回退，最多前进 2n+1 格；每个中心至多再有一次失败比较。因此总时间 O(n)。'])]
        p['invariant']=['处理中心 i 前，之前中心的半径都已求出；center、right 表示已经处理的回文中覆盖到最右端的一个。', '镜像初始化只复用已知范围内确定相等的字符对，再通过边界检查和逐对比较得到当前中心的完整半径。best_radius 保存所有已完成中心的最大半径，因此遍历结束后得到最长回文。']
        p['walkthrough']=['先看 abacaba：中心 7 的半径达到 7，之后落在已知范围内的中心可以复用左侧镜像。图中 ◇ 只是 None 的显示方式。', '再看 aaaa：大量中心的回文触及已有 right，先继承一段，再向未知区域继续扩展；偶数回文无需特殊分支。', '半径是变换后的单侧格数，但恰好等于原串回文字符数；用 (best_center-best_radius)//2 找原串起点，只在最终返回时切片。', '后两个例子保留二维 DP 与奇偶中心的基础对照。代码入口 longestPalindrome 调用线性 Manacher；longestPalindromeCenter 与 longestPalindromeDP 是独立对照方法。']
    elif n==236:
        p.setdefault('insight_sections',[]).append(dict(title='把递归的“回来以后”翻译成显式栈',body=['(node, False) 表示第一次遇到节点：先把 (node, True) 压回栈，约定等孩子处理完后再汇总；接着依次压右、左孩子。因为栈后进先出，实际处理顺序是左、右、父。', '(node, True) 被弹出时，两边的结果已经在 matches 中。读出并删除孩子结果，只保存当前子树要交给父节点的一份结果。这样 matches 保存的是等待汇总的分支结果，而不是永久保存全树结果。'],diagram='第一次弹出父节点：  压入 父(待汇总)、右孩子、左孩子\n弹栈实际顺序：      左子树 → 右子树 → 父节点汇总\n左右各找到一个目标 → 父是 LCA\n仅一边有结果       → 向上传递该结果'))
    return p
