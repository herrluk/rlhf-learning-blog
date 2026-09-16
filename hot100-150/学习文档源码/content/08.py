from textwrap import dedent

NODE=dedent('''
from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

''')

CHAPTER={
 'lead':'本章把链表基础操作组合成完整算法：先明确每段的边界，再决定哪些节点保留、反转、复制或归并。写代码前先画出原连接和目标连接。',
 'intro':['学习顺序：92 指定区间反转 → 25 完整分组反转 → 82 按重复组删除 → 143 两半交替重排 → 138 复制引用关系 → 148 自底向上归并排序。每题都要明确当前段的前驱、尾节点和下一段入口。','先完成第 07 章的 206、21、83、876、234。这里不再把反转和找中点当成孤立模板，而是解释它们在更大问题中承担什么职责。','节点图中的字母代表对象身份，数字代表 val。重排题必须移动原节点；复制题必须创建全新节点。虽然两者都可能输出相同数值序列，验证要求恰好相反。'],
 'sections':[
  {'title':'局部操作的四个锚点','body':['把待处理区间看成 before→first→…→last→after。before 用于接入新头，first 常在反转后变成新尾，last 常变成新头，after 保存尚未处理后缀的入口。','改动前先保存后缀入口。是否需要真正断开由算法决定：局部反转可以把初始 prev 设为 after，直接形成正确的新尾连接；归并排序为了限定两段的范围，通常要把各段尾部置为 None。'],'diagram':'修改前：before → first → ... → last → after\n反转后：before → last  → ... → first → after'},
  {'title':'区间是否够长，要在修改之前判断','body':['第 25 题最后不足 k 个节点必须保持原样，因此先向前探查 k 个节点，再决定是否反转。不能先改一半才发现节点不够，除非另行实现完整回滚。','第 92 题已经保证 left、right 是合法位置，不需要再做不足区间的探查。题目保证能省掉哪些分支，应与需要自己维护的条件分开。'],'diagram':'探查边界（只读）\n    ├─ 不满足 → 原样返回\n    └─ 满足   → 保存后缀 → 修改 → 接回'},
  {'title':'空间复杂度要算辅助表和调用栈','body':['复制 n 个节点的输出本来就占 O(n)；再建旧节点到新节点的哈希表，会额外使用 O(n) 辅助空间。交织复制可以省去这张表，但需要临时修改并恢复输入连接。','链表递归归并排序的分治栈为 O(log n)，不是 O(1)。本章给出的第 148 题完整代码采用自底向上迭代归并，满足常数辅助空间的进阶要求。']}
 ],
 'apis':[{'signature':'ListNode(val: int = 0, next: Optional[ListNode] = None) -> ListNode','description':['val 是节点值，next 是后继节点或 None。返回新对象；仅创建节点不会自动连接现有链表。每份普通链表解法都包含这一标准定义。']},{'signature':'range(stop: int) -> range\nrange(start: int, stop: int, step: int = 1) -> range','description':['range 产生按步长递进、但不包含 stop 的整数序列视图，不分配包含全部整数的列表。range(right-left) 表示恰好执行区间长度减一轮头插。','循环变量写 _ 表示本算法只需要重复次数，不使用该轮的编号；它仍然是普通变量名。']}],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':92,'slug':'reverse-linked-list-ii',
 'summary':'反转链表中从第 left 个到第 right 个节点的连接，两端位置均从 1 开始计数。区间以外节点的相对顺序不变，题目保证 1≤left≤right≤链长。',
 'baseline':'把整个链表保存到数组，再反转指定片段并接回需要 O(n) 空间。也可以使用第 206 题的逐边反转，但要额外记录区间两端并重连。头插法在固定前驱之后逐个搬节点，能同时完成反转与接回。',
 'insight':'找到区间前驱 before，将原第 left 个节点记为 tail。tail 始终留在已反转小段的末尾，每轮把 tail.next 摘下，插到 before 后面。原区间中的节点按出现顺序逐个被插到前端，最终自然逆序，而 tail.next 始终接住尚未搬动部分。',
 'steps':['用 dummy 指向 head，before 从 dummy 前进 left−1 步。','tail=before.next，它是原区间首节点，也是最终的区间尾节点。','重复 right−left 次：moving=tail.next；先让 tail.next=moving.next 跳过 moving。','将 moving.next=before.next，再令 before.next=moving，把它插到区间当前头之前。','返回 dummy.next。若 left=right，搬动次数为零，原链不变。'],
 'invariant':'完成 t 次搬动后，before 后面的前 t+1 个区间节点，等于原位置 left..left+t 的逆序；tail 仍是原 left 节点，位于这段末尾，它的 next 指向下一未处理节点。一次摘下并头插扩展这个逆序段，不影响 before 之前的前缀和剩余后缀。t 达到 right−left 时，目标区间恰好全部反转。',
 'examples':[{'label':'把 2→3→4 反转','input':'1→2→3→4→5，left=2，right=4','output':'1→4→3→2→5','frames':[
  {'title':'固定前驱 1 与原首节点 2','note':'before 指向 1，tail 指向 2。只需要搬动后面的 3、4，共 right−left=2 次。','diagram':'dummy → 1 → 2 → 3 → 4 → 5 → None\n        ↑ before\n            ↑ tail'},
  {'title':'摘下 3，让 2 接住 4','note':'moving=3，先令 2.next=4，避免丢失后缀。moving 变量仍保存节点 3 的引用。','diagram':'dummy → 1 → 2 ─────→ 4 → 5\nmoving → 3'},
  {'title':'把 3 插到 before 后','note':'3.next 指向当前区间头 2，1.next 改为 3。区间前两项已逆序，tail 仍指向 2。','diagram':'dummy → 1 → 3 → 2 → 4 → 5\n        ↑ before  ↑ tail'},
  {'title':'再摘下 4，插到区间最前面','note':'2.next 改为 5，4.next 指向 3，1.next 指向 4。两次搬动完成，后缀 5 自动接在新尾 2 后。','diagram':'dummy → 1 → 4 → 3 → 2 → 5 → None\n        ↑ before      ↑ tail'}
 ]},{'label':'区间从头开始','input':'A(7)→B(7)→C(8)，left=1，right=2','output':'B(7)→A(7)→C(8)','frames':[
  {'title':'before 就是 dummy','note':'left−1=0，不移动 before。两个 7 的值相同，但仍要交换原节点身份。','diagram':'dummy → A(7) → B(7) → C(8)'},
  {'title':'dummy.next 改为 B','note':'把 B 摘下后插到 dummy 后，返回新的头 B。只比较 [7,7,8] 看不出这一修改。','diagram':'dummy → B(7) → A(7) → C(8) → None'}
 ]}],
 'walkthrough':['before 和 tail 在整个反转循环中都不前进：before 固定区间插入位置，tail 固定原首节点。真正不断变化的是 tail.next。','区间长度为 right−left+1，第一项已经构成长度为 1 的逆序段，因此只需搬动剩余 right−left 项。','必须先摘下 moving，再把它插到前面。若直接把 moving.next 指向当前区间头而未更新 tail.next，可能造成节点之间的环。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        # before 定位到反转区间之前，之后始终不动。
        before = dummy
        for _ in range(left - 1):
            before = before.next
        # 原区间首节点最终会成为尾节点，后续不断抽取它的下一个节点。
        tail = before.next
        for _ in range(right - left):
            # 把 moving 从 tail 后面摘下，再插到区间最前面。
            moving = tail.next
            # 先接好 moving 后面的节点，保存未反转部分。
            tail.next = moving.next
            moving.next = before.next
            # 更新区间新头；重复 right-left 次就反转完成。
            before.next = moving
        return dummy.next
'''.strip(),
 'code_notes':['所有位置合法性由题目保证；反转循环中 tail.next 必然存在。','before.next 每轮变成新的区间头，tail 对象却一直不变。','dummy 统一处理 left=1 时的头节点变化，最终不出现在返回链中。'],
 'pitfalls':['把 tail 跟着 moving 移动会破坏“从固定尾后面摘下下一项”的含义。','循环 right−left+1 次会多搬动一个区间外节点，甚至读取 None。','位置从 1 开始，而 before 应位于第 left−1 个节点，前进次数不要混用数组下标。'],
 'complexity':'时间 O(n)，定位前驱与反转的总操作不超过线性量级；额外空间 O(1)，复用原节点。',
 'quiz':{'question':'left=right 时为什么不需要单独分支？','answer':'反转循环的 range(right-left) 为空。定位前驱后直接返回 dummy.next，原有连接完全没有变化。'},
 'tests':{'adapter':'linked','method':'reverseBetween','reuse_nodes':True,'cases':[{'args':[[1,2,3,4,5],2,4],'expected':[1,4,3,2,5],'expected_indices':[0,3,2,1,4]},{'args':[[7,7,8],1,2],'expected':[7,7,8],'expected_indices':[1,0,2]},{'args':[[5],1,1],'expected':[5]},{'args':[[1,2,3],1,3],'expected':[3,2,1]},{'args':[[1,2,3],3,3],'expected':[1,2,3]}]}
})

CHAPTER['problems'].append({
 'id':25,'slug':'reverse-nodes-in-k-group',
 'summary':'每 k 个节点作为一组反转，最后不足 k 个节点的后缀保持原样。题目保证 1≤k≤链长，只能改变节点连接，不能交换 val 代替反转。',
 'baseline':'把节点保存到数组后分组逆序会使用 O(n) 空间。直接边走边反转则可能在最后一组改到一半才发现不足 k 个，需要回滚。先只读探查完整组，再修改，可以避免这类不必要的状态。',
 'insight':'group_prev 是当前组的前驱。先从它出发走 k 步得到 kth；如果走空，剩余后缀不足一组，直接返回。保存 group_next=kth.next 后，反转半开区间 [group_prev.next,group_next)，并把反转中的初始 prev 设为 group_next，让原组首自动接住后缀。',
 'steps':['创建 dummy，group_prev=dummy。','从 group_prev 沿 next 探查 k 次；任一次到 None 就原样结束。','保存 kth.next 为 group_next，原组首为 old_first。','令 prev=group_next、cur=old_first，按第 206 题的方式反转，直到 cur is group_next。','group_prev.next=kth 接入新组头；group_prev=old_first 移到新组尾，继续下一组。'],
 'invariant':'每轮开始时，group_prev 及以前的完整组已正确反转，之后的节点尚未修改。只读探查确保本轮有完整 k 个节点。反转过程中 prev 是已反转片段的头，该片段的末尾接到 group_next；cur 是本组未反转部分的头。完成后 kth 是新头、old_first 是新尾，重连并移动前驱恢复同样的组间边界。',
 'examples':[{'label':'完整三节点组与不足组分开处理','input':'1→2→3→4→5，k=3','output':'3→2→1→4→5','frames':[
  {'title':'探查三个节点，先确定组尾','note':'group_prev=dummy，走三步到 kth=3。保存 group_next=4，当前组为 1、2、3。','diagram':'dummy → [1 → 2 → 3] → 4 → 5 → None\n↑ group_prev     ↑ kth  ↑ group_next'},
  {'title':'把初始 prev 指向 4','note':'处理节点 1 时就令 1.next=4，为反转后的组尾提前接好后缀；原节点 2 由 nxt 保存。','diagram':'已反转：1 → 4 → 5 → None\n未处理：2 → 3 → 4 → ...\n边界：遇到原节点 4 就停止'},
  {'title':'继续把 2、3 接到前面','note':'2.next=1，再令 3.next=2，cur 最终到原节点 4。组内反转结束，不能再处理 4。','diagram':'prev → 3 → 2 → 1 → 4 → 5 → None\ncur  ─────────────→ 4'},
  {'title':'接好新组头，前驱移到新组尾','note':'dummy.next=3，group_prev=old_first=1。下一组从 4 开始。','diagram':'dummy → 3 → 2 → 1 → 4 → 5 → None\n                  ↑ group_prev'},
  {'title':'下一次探查不足三个，保持 4→5','note':'从 1 出发探查到 4、5 后，第三步为 None。探查期间没有改边，因此直接返回当前结果。','diagram':'完成组：[3 → 2 → 1]\n不足组：[4 → 5] 保持原顺序'}
 ]},{'label':'k=2 就是两两交换','input':'1→2→3→4→5，k=2','output':'2→1→4→3→5','frames':[
  {'title':'两组各含两个节点','note':'第一组 1、2 反转，第二组 3、4 反转，末尾 5 不足两个。','diagram':'[1 → 2] [3 → 4] [5]\n    ↓       ↓     不动'},
  {'title':'与第 24 题相同的输出','note':'本算法把两两交换推广到任意合法 k，保留节点身份。','diagram':'2 → 1 → 4 → 3 → 5 → None'}
 ]}],
 'walkthrough':['group_next 是一个节点引用，不是某个数值；停止条件必须按身份比较，因为组内可能有多个同值节点。','old_first 必须在更新 group_prev.next 前保存。反转后它成为新尾，下一组前驱应该移到这里，不能仍留在新头 kth。','预检查和反转都扫描当前组，但每个节点最多被探查与反转各一次，乘以常数仍是 O(n)，不是 O(nk)。最后不足组只额外探查一次。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        # group_prev 是当前组的前驱，组头反转后会改变。
        group_prev = dummy
        while True:
            # 先确认还剩完整的 k 个节点，不足一组时整段保持原样。
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if kth is None:
                    return dummy.next
            # 保存下一组起点，它同时也是本组反转时的停止边界。
            group_next = kth.next
            old_first = group_prev.next
            # 把 prev 初始化为下一组起点，旧组头反转后会自然接上后段。
            prev, cur = group_next, old_first
            while cur is not group_next:
                # 先保留原后继，再反转当前边。
                nxt = cur.next
                cur.next = prev
                prev = cur
                cur = nxt
            # 原来的第 k 个节点现在是组头，让组前驱接上它。
            group_prev.next = kth
            # 原组头现在变成组尾，作为下一组的前驱继续处理。
            group_prev = old_first
'''.strip(),
 'code_notes':['外层循环由“不足一组”分支返回，k=1 也会每轮推进一个节点，因此不会原地无限循环。','prev=group_next 避免反转后再额外修补新尾的 next。','内层循环只覆盖已经确认存在的 k 个节点，因此每次 cur.next 访问安全。'],
 'pitfalls':['先反转再判断数量，会错误修改最后不足 k 个的节点。','把 group_prev 移到 kth 会再次处理已完成的节点；新尾是 old_first。','反转终点应是 group_next，不能看到某个相同 val 就停止。'],
 'complexity':'时间 O(n)，每个完整组做一次边界探查和一次反转；额外空间 O(1)，没有递归栈或节点数组。',
 'quiz':{'question':'为什么最后不足一组可以直接返回，而不用重新接回后缀？','answer':'前一组的原首节点在反转时已接到 group_next。下一轮仅做只读探查，后缀从未被改动，原连接已经是正确连接。'},
 'tests':{'adapter':'linked','method':'reverseKGroup','reuse_nodes':True,'cases':[{'args':[[1,2,3,4,5],3],'expected':[3,2,1,4,5],'expected_indices':[2,1,0,3,4]},{'args':[[1,2,3,4,5],2],'expected':[2,1,4,3,5]},{'args':[[1,2,3],1],'expected':[1,2,3]},{'args':[[7,7,7,7],4],'expected':[7,7,7,7],'expected_indices':[3,2,1,0]},{'args':[[1],1],'expected':[1]}]}
})

CHAPTER['problems'].append({
 'id':82,'slug':'remove-duplicates-from-sorted-list-ii',
 'summary':'从有序链表中删除所有出现过重复的数值对应的节点，只保留在原链中恰好出现一次的值。1→1→2 应变成 2；不是第 83 题的 1→2。',
 'baseline':'先统计每个数值出现次数，再保留次数为一的节点需要额外哈希表。排序保证同值节点连续出现，完整扫描一段就能判断这一值是唯一还是重复。',
 'insight':'before 指向已经确定保留的最后一个节点，cur 指向待判断组的开头。先找到同值组末尾 end：若 end is cur，组内只有一个节点，保留它；否则从 before 直接跳到整组之后，删除这一组的全部节点。',
 'steps':['dummy.next=head，before=dummy，cur=head。','从 cur 出发推进 end，直到后继不存在或后继值不同，得到完整同值组。','保存 after=end.next。','若 end is cur，保留这一项并令 before=cur；否则令 before.next=after 跳过整组，before 不动。','cur=after，继续判断下一组，最后返回 dummy.next。'],
 'invariant':'每轮开始时，before 及以前的返回前缀恰好包含已处理部分中只出现一次的数值，before.next 指向当前待判断组。排序使一个值的全部出现都在该组内。单节点组保留，长组整体跳过；两种操作都不会把重复值留进结果，并保持原有升序。',
 'examples':[{'label':'头部与中部重复组都整段删除','input':'1→1→2→3→3→4','output':'2→4','frames':[
  {'title':'第一组有两个 1','note':'before=dummy，cur 指向第一个 1，end 走到第二个 1。二者不是同一节点，整组需要删除。','diagram':'dummy → [1 → 1] → 2 → 3 → 3 → 4\n↑ before'},
  {'title':'dummy 直接连到 2','note':'before.next=2；before 保持在 dummy。下一组只有一个 2，保留它后 before 才前进到 2。','diagram':'dummy → 2 → [3 → 3] → 4\n        ↑ before'},
  {'title':'两个 3 再次整体跳过','note':'cur、end 分别是两个不同的 3 节点，令 2.next=4，before 仍为 2。','diagram':'dummy → 2 ─────────→ 4 → None'},
  {'title':'单独的 4 保留','note':'最后一组 end is cur，before 到 4，cur=None。返回 dummy.next，得到 2→4。','diagram':'dummy → 2 → 4 → None'}
 ]},{'label':'全部重复后可能返回空链','input':'7→7→7','output':'None','frames':[
  {'title':'同值组覆盖整个链表','note':'end 一直走到最后一个 7，after=None。该组不是单节点。','diagram':'dummy → [7 → 7 → 7] → None'},
  {'title':'dummy.next 被设为 None','note':'所有节点都应删除，本题允许最终结果为空。','diagram':'dummy → None\n返回 None'}
 ]}],
 'walkthrough':['与第 83 题相比，本题不能在看到第一个节点时就认定它应保留，需要先看完同值组。','删除后 before 不前进，因为它仍是结果中最后一个保留节点。若前进到被删除组中的节点，后续修改就可能作用在结果链之外。','外层每次跳到下一组，内层只走当前组，所有组互不重叠；两层 while 的总扫描仍然线性。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        # before 是最后一个确认保留的节点；重复组可能出现在头部。
        before = dummy
        cur = head
        while cur is not None:
            end = cur
            # 先找到同值组末尾，再决定整组保留还是删除。
            while end.next is not None and end.next.val == cur.val:
                end = end.next
            after = end.next
            # 组里只有一个节点才保留它，并推进 before。
            if end is cur:
                before = cur
            else:
                # 组里有重复值时整组绕过，before 不动以便继续删除相邻重复组。
                before.next = after
            cur = after
        return dummy.next
'''.strip(),
 'code_notes':['end is cur 判断组是否只有一个节点，不能用 end.val==cur.val，因为整个组本来就同值。','after 在处理保留或删除分支之前统一保存，两个分支都能从相同位置继续。','dummy 支持删除头部多组重复值，以及全部节点都删除的情况。'],
 'pitfalls':['复用第 83 题“同值只跳过后继”的逻辑，会错误保留重复值的一份。','删除一组后移动 before 到 end，会把前驱放在已经不属于结果的节点上。','无序链表不保证同值相邻，不能直接使用此分组方案。'],
 'complexity':'时间 O(n)，额外空间 O(1)，返回链复用原来唯一值的节点。',
 'quiz':{'question':'1→1→2→2→3 中，before 在处理前两组时会移动吗？','answer':'不会。两组都被删除，before 一直是 dummy，dummy.next 依次改为第一个 2、再改为 3。只有确认 3 是单节点组后，before 才移动到 3。'},
 'tests':{'adapter':'linked','method':'deleteDuplicates','reuse_nodes':True,'cases':[{'args':[[1,1,2,3,3,4]],'expected':[2,4],'expected_indices':[2,5]},{'args':[[7,7,7]],'expected':[]},{'args':[[]],'expected':[]},{'args':[[1,2,3]],'expected':[1,2,3]},{'args':[[1,1,2,2,3]],'expected':[3]}]}
})

CHAPTER['problems'].append({
 'id':143,'slug':'reorder-list',
 'summary':'将原链按“第一个、最后一个、第二个、倒数第二个……”的顺序原地重排。不能修改节点值；方法返回 None，结果通过原 head 指向的链体现。',
 'baseline':'每次扫描到尾节点，把它搬到前端，再处理内部剩余部分，需要反复扫描，时间 O(n²)。若先用节点数组双端取数，可以线性完成但占 O(n) 空间。把后半段反转后，所有要从尾部取的节点就能按 next 顺序获取。',
 'insight':'目标顺序交替来自原链前半段的正序与后半段的逆序。先用快慢指针分成前半段和后半段，前者在奇数长度时多一个节点；反转后半段，再把两条链交替连接。最后多出的中间节点自然留在末尾。',
 'steps':['零个或一个节点无需修改，返回。','slow=fast=head，用 fast.next、fast.next.next 定位前半段末尾。保存后半段入口，并令 slow.next=None 断开。','用迭代反转后半段，得到 second。','first 从 head 出发；每轮先保存 first_next、second_next，再连接 first→second→first_next。','两个游标推进到保存的后继，直到 second 耗尽；不返回新的头节点。'],
 'invariant':'分割后前半段有 ceil(n/2) 个节点，后半段有 floor(n/2) 个；反转后的后半段依次是原链的最后、倒数第二……节点。合并完成 t 轮后，前 2t 个结果节点已经交替取自两边；first、second 分别指向各自剩余入口。先保存两个后继再改边，使任何一边都不会丢失。后半段先结束，前半段至多剩一个中心节点。',
 'examples':[{'label':'五节点原地重排','input':'A(1)→B(2)→C(3)→D(4)→E(5)','output':'A(1)→E(5)→B(2)→D(4)→C(3)，返回 None','frames':[
  {'title':'在 C 后断开','note':'slow 停在前半段末尾 C。保存 D 后令 C.next=None，形成互不重叠的两条链。','diagram':'前半：A(1) → B(2) → C(3) → None\n后半：D(4) → E(5) → None'},
  {'title':'反转后半段，先取得原尾 E','note':'后半段变成 E→D，对应目标顺序中的第 2、4 个位置。','diagram':'first  → A(1) → B(2) → C(3)\nsecond → E(5) → D(4)'},
  {'title':'先保存 B、D，再连接 A→E→B','note':'first_next=B、second_next=D，修改两条边后 first=B、second=D。两个未处理入口都被保留。','diagram':'A(1) → E(5) → B(2) → C(3)\n                 ↑ first\nsecond → D(4)'},
  {'title':'连接 B→D→C，后半段耗尽','note':'second_next=None，合并结束。前半段多出的中心 C 已接在末尾，它的 next 在分割时设为了 None。','diagram':'A(1) → E(5) → B(2) → D(4) → C(3) → None'}
 ]},{'label':'偶数长度没有多余中心','input':'1→2→3→4','output':'1→4→2→3','frames':[
  {'title':'两段长度各为二','note':'先分成 1→2、3→4，反转后半段为 4→3。','diagram':'1 → 2 → None\n4 → 3 → None'},
  {'title':'两轮交替连接','note':'依次连成 1→4→2，再接成 2→3→None，两个游标同时耗尽。','diagram':'1 → 4 → 2 → 3 → None'}
 ]}],
 'walkthrough':['分割时断开 slow.next 很关键。如果前半段还连着后半段，后续反转和交替连接可能把某个节点再次连回已经处理的区域，形成环。','first_next 必须在 first.next=second 前保存，否则再读 first.next 得到的是新插入的 second，而不是前半段原后继。second_next 同理。','第 234 题为比较而反转，最后要恢复；本题的目标就是重排，因此反转与交替合并构成最终结果，不做恢复。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        if head is None or head.next is None:
            return
        slow = fast = head
        # 先找前半段末尾，保证前半段不短于后半段。
        while fast.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next
        cur = slow.next
        # 先断开链表，避免交替连接后形成环。
        slow.next = None
        second = None
        # 把后半段原地反转，才能按最后、倒数第二的次序取节点。
        while cur is not None:
            # 反转每条边之前保存后继。
            nxt = cur.next
            cur.next = second
            second = cur
            cur = nxt
        first = head
        # 按“前半段一个、反转后半段一个”的顺序交织。
        while second is not None:
            # 改 next 之前，同时保存两边剩余链表的入口。
            first_next = first.next
            second_next = second.next
            first.next = second
            second.next = first_next
            first = first_next
            second = second_next
'''.strip(),
 'code_notes':['返回类型为 None，函数结束时隐式返回 None；头节点仍是原来的第一个节点，调用方从 head 读取修改后的连接。','前半段不少于后半段，因此只要 second 存在，first 就一定存在。','所有阶段只更改 next，不修改 val，也不创建有效结果节点。'],
 'pitfalls':['每轮再去寻找尾节点会退化到 O(n²)。','忘记断开两段，可能留下指向已处理节点的旧边。','改边后才保存后继，会丢失尚未合并部分。','用一个新 head 返回结果，不能代替题目要求的原地修改接口。'],
 'complexity':'时间 O(n)，找中点、半段反转和合并都是线性；额外空间 O(1)。',
 'quiz':{'question':'奇数长度时为什么让前半段多一个节点？','answer':'目标顺序最后留下原中心节点。让它属于前半段，交替插入后半段耗尽后，它就自然位于结果末尾，不需要额外处理第二条链的剩余节点。'},
 'tests':{'adapter':'linked','method':'reorderList','inplace':True,'reuse_nodes':True,'cases':[{'args':[[1,2,3,4,5]],'expected':[1,5,2,4,3],'expected_indices':[0,4,1,3,2]},{'args':[[1,2,3,4]],'expected':[1,4,2,3]},{'args':[[7,7,7]],'expected':[7,7,7],'expected_indices':[0,2,1]},{'args':[[1]],'expected':[1]},{'args':[[1,2]],'expected':[1,2]}]}
})

CHAPTER['problems'].append({
 'id':138,'slug':'copy-list-with-random-pointer',
 'summary':'每个节点除了 next，还有一个可以指向任意原节点或 None 的 random。创建结构完全对应的深拷贝：新节点的 next、random 都只能指向新节点或 None，不能指回原链。',
 'baseline':'只复制 val 和 next 得到的普通链表，缺少 random 关系；直接把旧 random 赋给新 random 则会指回原对象，也不是深拷贝。复制一个节点时，它的 random 目标可能还没有被扫描到，因此不能只按从左到右的单次顺序直接连接。',
 'insight':'先建立“旧节点对象→对应新节点对象”的映射，再翻译全部边。第一遍只创建所有新节点，不连接 random；第二遍把 old.next、old.random 分别通过映射换成新节点引用。把 None 映射为 None，可以统一处理空边和空链。',
 'steps':['初始化 copies={None:None}。','沿 next 扫描原链，为每个原节点 cur 创建 Node(cur.val)，保存到 copies[cur]。','再次从 head 扫描：copies[cur].next=copies[cur.next]；copies[cur].random=copies[cur.random]。','返回 copies[head]；原链任何字段都不需要修改。'],
 'invariant':'第一遍结束后，每个可达原节点都有且只有一个独立新副本，映射以身份为键，因此同值节点不会混淆。第二遍处理 old 时，把每条 old→target 的边变成 copies[old]→copies[target]。全部目标副本已存在，所以前向、后向、自指以及 random 构成的环都能用相同规则连接，并且没有边指回原链。',
 'examples':[{'label':'同值节点、自指与前向 random','input':'A(7)→B(7)→C(9)，random：A→C，B→B，C→A','output':'A′(7)→B′(7)→C′(9)，random：A′→C′，B′→B′，C′→A′','frames':[
  {'title':'先分清节点值与节点身份','note':'A、B 都是 7，但必须创建两个副本。random 的目标由对象引用决定，不能按 val 查找。','diagram':'next：A(7) → B(7) → C(9) → None\nrandom：A → C，B → B，C → A'},
  {'title':'第一遍只创建节点与映射','note':'此时 A′、B′、C′ 的 next 和 random 都是 None，但每个目标已经有了新版本。','table':{'headers':['旧节点键','新节点值'],'rows':[['None','None'],['A(7)','A′(7)'],['B(7)','B′(7)'],['C(9)','C′(9)']]}},
  {'title':'翻译 A 的两条边','note':'原 A.next=B，所以新 A′.next=B′；原 A.random=C，所以新 A′.random=C′。C 即使在原链后面，它的副本也已存在。','diagram':'A.next=B     → A′.next=B′\nA.random=C   → A′.random=C′'},
  {'title':'翻译自指与回指','note':'B.random=B 变成 B′.random=B′；C.random=A 变成 C′.random=A′，没有边跨回原链。','diagram':'新 next：A′(7) → B′(7) → C′(9) → None\n新 random：A′ → C′，B′ → B′，C′ → A′'},
  {'title':'新旧对象完全隔离','note':'新旧链展示的数值和 random 下标相同，但节点身份集合必须不相交。修改新节点值不会改变原节点。','table':{'headers':['检查项','结果'],'rows':[['A′ is A','False'],['B′.random is B′','True'],['C′.random is A','False']]}}
 ]}],
 'walkthrough':['题目输入展示中的 [val,random_index] 是测试器的序列化形式。方法实际收到 head，random 是节点引用，不是一个整数下标。','只沿 next 遍历，不沿 random 递归，因此 random 自指或形成环不会导致无限遍历。题目的 next 主链仍然是一条有限链。','copies 的键必须是原节点对象。若写 copies[cur.val]，例子中的 A、B 会占用同一个键，丢失一对一关系。','第一遍只分配、第二遍连边，是处理“引用可能指向尚未处理对象”的通用办法，后续图克隆也会遇到类似问题。'],
 'code':'''
from typing import Optional

# LeetCode 提供同样接口的 Node；默认对象身份可用作字典键。
class Node:
    def __init__(self, x: int, next: Optional['Node'] = None, random: Optional['Node'] = None):
        self.val = x
        self.next = next
        self.random = random

class Solution:
    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:
        # 第一轮：把副本插在每个原节点后面，原节点.next 就能直接找到副本。
        cur = head
        while cur is not None:
            following = cur.next
            cur.next = Node(cur.val, following)
            cur = following
        # 第二轮：若原节点 random 指向 R，副本 random 就指向 R.next。
        cur = head
        while cur is not None:
            clone = cur.next
            clone.random = cur.random.next if cur.random is not None else None
            cur = clone.next
        # 第三轮：拆开两条链，同时恢复输入链表原来的 next。
        clone_head = head.next if head is not None else None
        cur = head
        while cur is not None:
            clone = cur.next
            following = clone.next
            cur.next = following
            clone.next = following.next if following is not None else None
            cur = following
        return clone_head

    def copyRandomListHash(self, head: Optional[Node]) -> Optional[Node]:
        # 对照哈希方法：用“旧节点身份 → 新节点”显式保存映射，None 映射到 None。
        copies = {None: None}
        cur = head
        while cur is not None:
            # 先为所有节点建立副本，下一轮才能随意连接任意 random 指针。
            copies[cur] = Node(cur.val)
            cur = cur.next
        cur = head
        while cur is not None:
            # 连接的必须是副本节点，不能把原链表节点接入副本。
            copies[cur].next = copies[cur.next]
            copies[cur].random = copies[cur.random]
            cur = cur.next
        return copies[head]
'''.strip(),
 'api':{'signature':'mapping[key] -> value\nmapping[key] = value','description':['字典用键查找对应值；键必须可哈希。这里 Node 未定义按 val 比较的 __eq__，使用默认对象身份语义，同值的不同节点仍是不同键。','读取不存在的键会抛出 KeyError，所以第一遍要先为全部节点建映射，并预先加入 None:None。第二遍再读 next 和 random 的目标时，所有键都已经存在。']},
 'code_notes':['默认方法分三轮执行，必须先插入全部副本，才能通过 random.next 安全定位任意目标副本。', '拆分时先保存 following，再恢复原节点的 next，并把副本接到下一个副本。', '前文的哈希映射例子对应 copyRandomListHash，适合要求全程不改输入的场景。'],
 'pitfalls':['new.random=old.random 是浅层引用复用，会把新链指回旧链。','用 val 作映射键会在重复数值下丢节点。','第一遍只建已经遇到的节点并立即访问前向 random 的副本，可能查不到键。','只比较输出序列无法证明深拷贝，还要检查新旧身份不重叠、所有新边都留在新节点集合中。'],
 'complexity':'交织复制时间 O(n)，除必须创建的 n 个输出节点外，辅助空间 O(1)；中途暂改 next，结束时恢复原链。哈希对照方法时间 O(n)、辅助空间 O(n)，全程不改原链。',
 'alternative':'常数辅助空间变体分三遍：①将每个副本插在原节点之后，形成 A→A′→B→B′；②若 A.random=R，则 A′.random=R.next，因为 R.next 就是 R′；③拆开交织链，同时恢复全部原 next 并连接新 next。它省掉映射表，但临时修改输入，且拆分必须同时保住新旧后继。副本节点的 O(n) 输出空间仍然存在。先掌握本题主解的一对一映射，再用这个相邻位置关系替代哈希查找。',
 'quiz':{'question':'B.random=B 的自指，复制后应该指向 B 还是 B′？','answer':'应该指向 B′。深拷贝保持“指向自己的副本”这一关系，不能让新节点指向原 B；表达式 copies[B.random] 正好得到 copies[B]，也就是 B′。'},
 'tests':{'adapter':'random_linked','method':'copyRandomList','cases':[{'args':[[[7,2],[7,1],[9,0]]],'expected':[[7,2],[7,1],[9,0]]},{'args':[[]],'expected':[]},{'args':[[[1,0]]],'expected':[[1,0]]},{'args':[[[1,None]]],'expected':[[1,None]]},{'args':[[[7,None],[13,0],[11,4],[10,2],[1,0]]],'expected':[[7,None],[13,0],[11,4],[10,2],[1,0]]}]}
,
 'submission': {'name': '交织复制与恢复原链', 'why': '默认采用 O(1) 辅助空间的交织法。它会短暂修改 next 后完整恢复；若输入在复制期间不能改变，可选 copyRandomListHash 对照方法。', 'steps': ['在每个原节点之后插入它的副本。', '利用 random.next 找到随机目标的副本。', '拆分原链和副本链，恢复所有原 next，返回副本头。'], 'diagram': '原链：A → B → C\n交织：A → A′ → B → B′ → C → C′\n拆分：A → B → C    与    A′ → B′ → C′'},
})

CHAPTER['problems'].append({
 'id':148,'slug':'sort-list',
 'summary':'将链表按节点值非递减排序。完整解法采用自底向上的归并排序，达到 O(n log n) 时间与 O(1) 辅助空间，并复用原节点。',
 'baseline':'插入排序容易实现，但逆序输入会使每次插入都扫描很远，最坏 O(n²)。转成数组后调用排序需要 O(n) 辅助空间。链表擅长顺序读取和重接两段，归并排序能直接利用第 21 题的合并过程。',
 'insight':['一个节点本身有序。先把相邻的长度 1 的有序段两两合并，得到长度至多 2 的有序段；再合并长度 2 的段，得到长度至多 4 的段，按 1、2、4、8……扩大。直到段长覆盖全部链表，整条链即有序。','自顶向下递归先切半再回溯合并，也能达到 O(n log n)，但调用栈占 O(log n)。把段长作为外层循环状态，自底向上就能避免递归栈。关键是每次先切出 left、right 两段并保存 rest，再用 prev 把归并结果接入本轮输出。'],
 'steps':['先顺序统计链长 n，创建 dummy 指向 head，size=1。','定义 split(node,size)：从 node 开始保留至多 size 个节点，切断尾部 next，返回剩余后缀入口。','定义 merge(a,b,tail)：把两条已断开的有序链合并到 tail 后，返回合并后的尾节点。','每一轮从 dummy.next 开始，依次切出 left、right，并把后续入口保存为 cur；合并这两段后更新 prev。','本轮所有节点处理完后 size*=2，直到 size≥n，返回 dummy.next。'],
 'invariant':['外层一轮开始时，链表按从头每 size 个节点划分为若干有序段，最后一段可以更短。size=1 时显然成立。内层每次取相邻两段，通过稳定归并形成一个长度至多 2×size 的有序段，并按原分段顺序连接。整轮结束便为下一轮建立段长翻倍的不变量。','split 真正把段尾设为 None，使 merge 只处理这一对段；cur 在合并之前保存剩余未处理后缀。prev 始终是本轮已处理前缀的尾，合并返回新尾后，下一对能直接接在正确位置。'],
 'examples':[{'label':'从单节点段逐轮扩大','input':'4→2→1→3→0','output':'0→1→2→3→4','frames':[
  {'title':'size=1，每个节点都是有序段','note':'第一轮分为 [4]、[2]、[1]、[3]、[0]。最后一个段没有配对段，也作为有序段保留。','diagram':'[4] [2] [1] [3] [0]'},
  {'title':'合并成长度至多 2 的段','note':'4 与 2 合并为 2→4；1 与 3 合并为 1→3；0 与空链合并仍为 0。','diagram':'[2 → 4] [1 → 3] [0]\n当前链：2 → 4 → 1 → 3 → 0'},
  {'title':'size=2，切出两条独立链','note':'left=2→4→None，right=1→3→None，cur 保留指向 0。切断边界，保证本次 merge 不会把 0 混入。','diagram':'left：2 → 4 → None\nright：1 → 3 → None\nrest：0 → None'},
  {'title':'合并为长度至多 4 的段','note':'归并前两段得到 1→2→3→4，剩余 0 单独保留。本轮结束后只有两个有序段。','diagram':'[1 → 2 → 3 → 4] [0]'},
  {'title':'size=4，最后一轮合并','note':'比较两段头，先取 0，再接入 1→2→3→4。size 随后变成 8≥5，所有节点属于同一个有序段。','diagram':'[0 → 1 → 2 → 3 → 4] → None'}
 ]},{'label':'相同值保留原相对顺序','input':'A(2)→B(1)→C(2)','output':'B(1)→A(2)→C(2)','frames':[
  {'title':'第一轮产生 [B,A] 和 [C]','note':'两个值为 2 的节点仍是不同对象，后续比较相等时先选左段 A。','diagram':'[B(1) → A(2)] [C(2)]'},
  {'title':'使用 <= 保证左段同值优先','note':'结果 B→A→C，A 原来在 C 前，排序后仍保持这个顺序。本题只要求有序，这个实现还具有稳定性。','diagram':'B(1) → A(2) → C(2) → None'}
 ]}],
 'walkthrough':['split 的 size 是最多保留的节点数，不是需要走的边数。保留第一个节点后只需再走 size−1 条边；不足 size 时停在现有尾节点。','切 right 之前，left 已经断开；切出 right 后要先保存 cur，再去合并。否则合并改变 next 后，原来的后续入口可能无法恢复。','merge 的 tail 是本轮已合并前缀的尾。它接入一个节点就前进；剩余一条链整体接上之后，再走到真正尾部返回。','寻找合并尾部虽然增加一次局部扫描，但同一轮所有段总长为 n，每个节点仍只被常数次访问，所以每轮 O(n)，共 O(log n) 轮。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # 切出至多 size 个节点并断开，返回下一段起点。
        def split(node: Optional[ListNode], size: int) -> Optional[ListNode]:
            if node is None:
                return None
            for _ in range(size - 1):
                if node.next is None:
                    break
                node = node.next
            rest = node.next
            # 每段独立终止，后续归并不会误读到下一段。
            node.next = None
            return rest

        # 把两段有序链表接到 tail 后面，返回新的结果尾部。
        def merge(a: Optional[ListNode], b: Optional[ListNode], tail: ListNode) -> ListNode:
            while a is not None and b is not None:
                # 相等时先取左段，保证归并排序稳定。
                if a.val <= b.val:
                    tail.next = a
                    a = a.next
                else:
                    tail.next = b
                    b = b.next
                tail = tail.next
            tail.next = a if a is not None else b
            while tail.next is not None:
                tail = tail.next
            return tail

        # 先数链表长度，以便迭代控制归并段长。
        n = 0
        cur = head
        while cur is not None:
            n += 1
            cur = cur.next
        dummy = ListNode(0, head)
        # 自底向上从单节点段开始归并，避免递归调用栈。
        size = 1
        while size < n:
            prev = dummy
            cur = dummy.next
            while cur is not None:
                left = cur
                # 切出左右两段，并提前保存剩余未处理部分的入口。
                right = split(left, size)
                cur = split(right, size)
                prev = merge(left, right, prev)
            # 一轮完成后，有序段长度翻倍，总共只需对数轮。
            size *= 2
        return dummy.next
'''.strip(),
 'code_notes':['两个辅助函数都是普通调用，不递归，最多同时存在固定数量的调用帧与引用。','每轮从 dummy.next 重新开始，因为上一轮可能改变链头。','right 可以是 None，split 与 merge 都允许空段，因此末尾不足两段不需要特殊拼接分支。','只创建一个 dummy；所有排序结果节点都来自原输入，val 保持不变。'],
 'pitfalls':['递归归并排序的栈不是常数空间，不能直接用它证明 O(1) 辅助空间。','split 不断链会使 merge 越过本轮段边界，破坏分段不变量。','归并前不保存 rest，会因重接 next 丢掉尚未处理的节点。','size 不翻倍或每轮不重置 prev、cur，都会破坏下一轮的处理范围。'],
 'complexity':'时间 O(n log n)，统计长度 O(n)，每轮切段和归并 O(n)，共 O(log n) 轮。辅助空间 O(1)，没有数组、递归栈或新结果链。',
 'quiz':{'question':'n=5、size=2 时，最后只剩一个节点 0，merge 收到什么？','answer':'left 指向 0，split(left,2) 返回 None，因此 right=None；cur=split(None,2) 也为 None。merge 把 left 接到前缀后并返回 0，正确保留不足一对的尾段。'},
 'tests':{'adapter':'linked','method':'sortList','reuse_nodes':True,'cases':[{'args':[[4,2,1,3,0]],'expected':[0,1,2,3,4],'expected_indices':[4,2,1,3,0]},{'args':[[2,1,2]],'expected':[1,2,2],'expected_indices':[1,0,2]},{'args':[[]],'expected':[]},{'args':[[1]],'expected':[1]},{'args':[[5,4,3,2,1]],'expected':[1,2,3,4,5]},{'args':[[-1,5,3,4,0]],'expected':[-1,0,3,4,5]}]}
})
