from textwrap import dedent

NODE = dedent('''
from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

''')

CHAPTER = {
 'lead':'链表题真正移动的是引用，真正修改的是 next。先学会保存后继、使用哑节点，再理解快慢指针的距离与节点身份，最后组合成删除、判环和回文判断。',
 'intro':['建议顺序：206 反转 → 21 合并 → 83 去重 → 876 中点 → 19 倒数第 n 个 → 24 两两交换 → 2 两数相加 → 160 相交 → 141 判环 → 142 环入口 → 234 回文。前七题练习读写连接，后四题练习身份、距离与组合。','图中 A、B、C 等字母表示不同节点对象，括号内数字才是 val。两个节点可以具有相同数值；只有引用指向同一个对象，才表示相交或再次访问同一节点。','本章每份代码都包含标准 ListNode 定义、类型导入和完整 Solution，可以独立阅读并提交。LeetCode 调用方法时传入的是节点对象；页面上 [1,2,3] 只是链表的输入展示方式，不是方法实际收到的 Python list。'],
 'sections':[
  {'title':'赋值给变量与修改节点是两件事','body':['cur = cur.next 只让变量 cur 改指向，链表结构没有变化。cur.next = prev 修改 cur 所指节点的出边，所有持有这个节点引用的变量都会看到新连接。','反转前必须保存 nxt = cur.next。若先覆盖 cur.next，再通过它向前走，读到的已经是反向连接，原后缀就失去了访问入口。'], 'diagram':'改变量：cur = cur.next\nA → B → C       A → B → C\n↑ cur              ↑ cur\n\n改连接：cur.next = prev\nprev → ...       prev ← cur    nxt → 未处理后缀'},
  {'title':'哑节点统一处理头节点变化','body':['dummy 是临时增加的前驱节点，dummy.next 指向真正的头。删除头节点与删除内部节点都变成修改某个前驱的 next，不必维护两套分支。','dummy.val 没有业务含义；返回的是 dummy.next。创建一个哑节点只占常数空间，不能把它作为结果中的有效节点。'], 'diagram':'dummy → head → 第二个节点 → ...\n  ↑ 前驱\n删除 head：dummy.next = head.next\n返回 dummy.next'},
  {'title':'快慢指针需要明确起点与停止条件','body':['同从 head 出发，slow 每轮一步、fast 每轮两步，while fast and fast.next 会在偶数长度时得到第二个中点。若要前半段末尾，可以让 fast 从 head.next 出发，或者用不同的停止条件。','判环时二者起初就指向同一个头节点，所以必须先移动再检查是否相遇。检查身份用 is，不用 val 相等。','Python 的 and 从左到右短路：先确认 fast 不是 None，再读取 fast.next，才能安全访问可能不存在的后继。'], 'diagram':'安全条件：fast is not None\n                 ↓ 才能读取\n           fast.next is not None\n                 ↓\n           fast = fast.next.next'}
 ],
 'apis':[{'signature':'ListNode(val: int = 0, next: Optional[ListNode] = None) -> ListNode','description':['构造一个节点对象，val 是保存的数值，next 是后继节点引用或 None。调用后返回新节点，不会自动加入现有链表，必须通过某个 next 连接它。','Optional[ListNode] 等价于 ListNode | None，描述“可能为空的节点引用”；类型标注不会在运行时自动进行空值检查。访问 .next 前仍需由条件保证对象存在。']},{'signature':'a is b -> bool','description':['is 判断两个引用是否指向同一对象；== 判断值是否相等，并可能调用对象自定义的比较方法。相交、环入口等题目要求节点身份，明确使用 is 最直接。','None 表示没有后继。它与值为 0 的节点不同，不能把 node.val==0 当成链表结束条件。']}],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':206,'slug':'reverse-linked-list',
 'summary':'给定单链表头节点，反转全部 next 连接，返回新的头节点。空链表返回 None；节点的数值和对象身份都应保留。',
 'baseline':'先把节点放进数组，再按相反顺序连接可以完成任务，但需要 O(n) 额外空间。实际上每次只需记住已反转部分的头、当前节点和原后继，三个引用就够了。',
 'insight':'把链表分成已经反转的前缀与尚未处理的后缀。prev 指向反转后的前缀头，cur 指向未处理的第一项。每轮把 cur 从后缀取下，接到 prev 前面，两个区域之间的边界向后移动一格。',
 'steps':['初始化 prev=None、cur=head，已反转前缀为空。','保存 nxt=cur.next，让剩余后缀始终有可访问入口。','把 cur.next 改为 prev，完成当前节点的方向反转。','prev=cur、cur=nxt，重复直到 cur 为 None。','返回 prev，它是最后处理的原尾节点，也是新头。'],
 'invariant':'每轮开始时，prev 链完整保存原链表已处理前缀的逆序，cur 链完整保存原链表未处理后缀的原顺序，两者节点集合互不重叠。先保存 nxt 再反转 next，使当前节点加入 prev 链而不丢失后缀。结束时后缀为空，prev 包含全部节点的逆序。',
 'examples':[{'label':'三条边依次转向','input':'A(1) → B(2) → C(3) → None','output':'C(3) → B(2) → A(1) → None','frames':[
  {'title':'反转前缀为空','note':'prev=None，cur=A；当前整条链都属于未处理后缀。','diagram':'prev → None\ncur  → A(1) → B(2) → C(3) → None'},
  {'title':'先保留 B，再把 A 指向 None','note':'nxt=B。修改 A.next=None 后，B 和 C 仍可通过 nxt 找到。推进变量后 prev=A、cur=B。','diagram':'prev → A(1) → None\ncur  → B(2) → C(3) → None'},
  {'title':'B 接到已经反转的 A 前面','note':'先保存 C，再令 B.next=A。prev=B，cur=C，已反转的前缀扩大为 B→A。','diagram':'prev → B(2) → A(1) → None\ncur  → C(3) → None'},
  {'title':'处理 C，返回 prev','note':'C 原后继为 None，反转后 cur=None，循环结束；返回的引用必须是 C，而不是原来的 head=A。','diagram':'prev → C(3) → B(2) → A(1) → None\ncur  → None'}
 ]}],
 'walkthrough':['第一轮把 A.next 设为 None，也完成了新尾节点的终止边。后续只需把新处理节点连到它前面。','head 变量仍指向 A，反转不会让这个变量自动变成 C。返回 prev 是算法的一部分，而不是可以省略的形式步骤。','若先 cur.next=prev 再 nxt=cur.next，nxt 保存的将是 prev，原来的 B、C 可能无法继续访问。这解释了四句更新的依赖顺序。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # prev 指向已经反转部分的头，cur 指向尚未处理的节点。
        prev = None
        cur = head
        while cur is not None:
            # 先保存后继，再改 next；否则剩余链表会丢失。
            nxt = cur.next
            # 让当前节点指向前一个节点，完成这一条边的反转。
            cur.next = prev
            # 已反转部分向前扩展，再让 cur 去处理刚保存的后继。
            prev = cur
            cur = nxt
        # 循环结束时 cur 为空，prev 就是新头；只改指针，不复制节点。
        return prev
'''.strip(),
 'code_notes':['nxt 是引用，不是复制一个节点；整段算法没有创建结果节点。','循环条件先保证 cur 存在，循环体才能读取 cur.next。','空链表的 cur 初始为 None，循环不执行，prev 仍为 None，自然得到正确结果。'],
 'pitfalls':['改 next 前没有保存后继会断开访问路径。','返回 head 会得到原头节点，反转后它只剩一个节点长的后缀。','只反转数值无法证明完成了要求的连接修改，也不能迁移到不能修改节点值的题目。'],
 'complexity':'时间 O(n)，每个节点处理一次；额外空间 O(1)，只保留固定数量的引用。',
 'alternative':'递归也能反转，但要解释回溯时 head.next.next=head 和 head.next=None，且需要 O(n) 调用栈。Python 对很长链表容易触及递归深度限制，面试主解优先掌握迭代。',
 'quiz':{'question':'只有一个节点时，反转需要创建新节点吗？','answer':'不需要。该节点的 next 原本就是 None，循环把它再次指向 None，然后返回同一个节点对象。'},
 'tests':{'adapter':'linked','method':'reverseList','reuse_nodes':True,'cases':[{'args':[[1,2,3]],'expected':[3,2,1]},{'args':[[]],'expected':[]},{'args':[[1]],'expected':[1]},{'args':[[1,1,2]],'expected':[2,1,1]}]}
})

CHAPTER['problems'].append({
 'id':21,'slug':'merge-two-sorted-lists',
 'summary':'把两个非递减有序链表合并为一个有序链表，连接原有节点，返回合并后的头。任一输入可以为空。',
 'baseline':'把所有数值收集到数组并排序，再创建新链表，既忽略了两边已有的有序性，也额外复制了节点。两个当前头节点中较小的那个，一定就是剩余全部节点中最小的候选。',
 'insight':'维护一个已经排好序的结果前缀，其尾节点为 tail；a、b 分别指向两边未合并的第一项。每次取较小头节点接到 tail 后，等价于归并排序的合并步骤。哑节点让第一次接入与后续接入使用相同代码。',
 'steps':['创建 dummy，tail=dummy，令 a、b 指向两条输入链。','两边都非空时比较 a.val 与 b.val，把较小节点接到 tail.next，然后推进被选一侧。','把 tail 推进到刚接入的节点。','一边为空后，将另一边剩余整段接到 tail.next，不需要逐个复制。','返回 dummy.next，跳过临时哑节点。'],
 'invariant':'每轮开始时，从 dummy.next 到 tail 的已选前缀非递减，并且包含已经消耗的全部节点；a、b 是尚未选择部分的头。已选最大值不大于两边未选头，选两者较小值仍保持有序。剩余一条链本身有序且全部不小于结果前缀末尾，因此可以整段接入。',
 'examples':[{'label':'相同数值也对应不同节点','input':'A1(1)→A2(3)；B1(1)→B2(2)→B3(4)','output':'1→1→2→3→4','frames':[
  {'title':'创建不参与结果的哑节点','note':'tail=dummy。两边头都为 1，代码选择左链 A1，不会删除另一边的 B1。','diagram':'dummy   a → A1(1) → A2(3)\n        b → B1(1) → B2(2) → B3(4)'},
  {'title':'先选 A1，再选 B1','note':'第一轮 a 前进到 3，第二轮 b 的 1 更小。结果前缀含两个值为 1 的不同节点。','diagram':'dummy → A1(1) → B1(1)\n                   ↑ tail\na → A2(3)\nb → B2(2) → B3(4)'},
  {'title':'接入 B2，再接入 A2','note':'2<3，先选 B2；随后 3<4，选 A2。此时左链已经耗尽。','diagram':'结果前缀：1 → 1 → 2 → 3\n                         ↑ tail\nb → B3(4)'},
  {'title':'整体接入右边剩余链','note':'tail.next=b，把剩余 4 接上。返回 dummy.next，它指向原节点 A1。','diagram':'dummy → A1(1) → B1(1) → B2(2) → A2(3) → B3(4) → None'}
 ]}],
 'walkthrough':['图中结果前缀截止于 tail，未完成时 tail 原有 next 可能仍连着原链后缀；下一轮会按需要更新它。讨论不变量时应明确前缀范围，不能误以为每轮 tail.next 都是 None。','同值时选择哪一边都能保持数值有序。代码用 <= 优先左链，保留各链内部原相对顺序。','算法会重接原节点，因此调用后不要假设两条输入仍是互不关联的原链。这是复用节点带来的可见修改。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        # 哨兵统一处理空结果与头节点，tail 始终指向结果尾部。
        dummy = ListNode()
        tail = dummy
        a, b = list1, list2
        while a is not None and b is not None:
            # 每次接入较小节点；相等时先接 a，保持各链表内部顺序。
            if a.val <= b.val:
                tail.next = a
                a = a.next
            else:
                tail.next = b
                b = b.next
            # 尾指针只在接好节点后推进。
            tail = tail.next
        # 一条链表耗尽后，另一条的剩余部分已经有序，可以整段接上。
        tail.next = a if a is not None else b
        return dummy.next
'''.strip(),
 'code_notes':['只创建一个 dummy，所有有效结果节点来自输入。','先推进被选一侧，再推进 tail；两者分别代表未合并区与已合并区，含义不同。','一边为空时直接接另一边，保证未选后缀不会丢失。'],
 'pitfalls':['不能把相同值当成重复项去掉；本题要求保留两条链的全部节点。','忘记 tail=tail.next 会反复覆盖同一个连接，前面接入的节点会丢失。','返回 dummy 会额外带上一个不属于结果的零值节点。'],
 'complexity':'时间 O(m+n)，额外空间 O(1)，复用输入节点；没有长度为 m+n 的新结果节点分配。',
 'quiz':{'question':'一条链为空、另一条为 1→2 时，循环会执行吗？','answer':'不会。直接把非空链接到 dummy.next 并返回其原头节点，结果仍为同一条 1→2 链。'},
 'tests':{'adapter':'linked','method':'mergeTwoLists','linked_args':[0,1],'reuse_nodes':True,'cases':[{'args':[[1,3],[1,2,4]],'expected':[1,1,2,3,4]},{'args':[[],[]],'expected':[]},{'args':[[],[0]],'expected':[0]},{'args':[[-3,-1,2],[-2,2,2]],'expected':[-3,-2,-1,2,2,2]}]}
})

CHAPTER['problems'].append({
 'id':83,'slug':'remove-duplicates-from-sorted-list',
 'summary':'给定非递减有序链表，让每个不同数值只保留一个节点，返回去重后的头。此题保留重复值的一份，与第 82 题“出现重复就全部删除”不同。',
 'baseline':'用集合判断是否见过某个数值需要 O(n) 额外空间。有序条件保证相同值连续出现，因此只要比较当前保留节点与它的后继，无需记住所有历史数值。',
 'insight':'cur 表示当前这段相同数值中保留的第一个节点。若后继同值，就让 cur.next 跳过后继，但 cur 不动，继续检查新后继；只有后继值不同，才将 cur 推到下一段。',
 'steps':['cur=head。只有 cur 与 cur.next 都存在时才比较相邻节点。','若数值相等，令 cur.next=cur.next.next，跳过多余节点。','若数值不同，令 cur=cur.next，开始处理下一段。','扫描结束后返回原 head；只保留第一份，因此非空链表的头不会被删除。'],
 'invariant':'cur 之前的数值段已各保留一个节点，cur 是当前段保留的代表。删除同值后继不会移除该段的最后一份；保持 cur 不动，可以继续消除任意多个连续重复项。遇到不同值说明当前段结束，有序性保证这个值以后不会再出现。',
 'examples':[{'label':'连续三个 1 不能只跳过一个','input':'A(1)→B(1)→C(1)→D(2)→E(3)→F(3)','output':'A(1)→D(2)→E(3)','frames':[
  {'title':'A 是数值 1 的保留代表','note':'A 与 B 同值，让 A.next 从 B 改成 C，cur 仍指向 A。','diagram':'cur → A(1) ─────→ C(1) → D(2) → E(3) → F(3)\n      被跳过：B(1)'},
  {'title':'新后继 C 仍然与 A 同值','note':'再次修改 A.next，跳到 D。若上一轮移动 cur，就会漏掉这一比较。','diagram':'cur → A(1) → D(2) → E(3) → F(3)\n      被跳过：B(1)、C(1)'},
  {'title':'不同值推进，相同值继续删除','note':'A 与 D 不同，cur 到 D；D 与 E 不同，cur 到 E；E 与 F 相同，跳过 F。','diagram':'A(1) → D(2) → E(3) → None\n                 ↑ cur'},
  {'title':'保留每段的第一份','note':'返回原节点 A。所有多余节点只是从返回链中移除，不需要修改它们的 val。','array':[1,2,3],'array_label':'返回链中的值'}
 ]}],
 'walkthrough':['一次循环只有“跳过一个重复节点”或“前进到一个新数值”两种动作。两种动作都会缩短剩余待处理工作，总时间仍然线性。','这里没有删除 cur 本身，所以不需要 dummy；第 82 题可能删除头部整段，到时哑节点才更有价值。','删除连接不等于立即销毁 Python 对象。如果外部还有变量引用被跳过节点，它仍然存在，只是不再位于返回链中。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # 当前节点作为这一组重复值保留的代表。
        cur = head
        while cur is not None and cur.next is not None:
            if cur.val == cur.next.val:
                # 绕过重复节点；cur 不前进，因为后面可能仍是同一个值。
                cur.next = cur.next.next
            else:
                # 只有看到不同值，才进入下一组。
                cur = cur.next
        return head
'''.strip(),
 'code_notes':['cur.next.next 可以是 None，这是删除尾部重复项时的合法连接目标。','相等分支不推进 cur，用同一个代表继续检查整个重复段。','非空输入至少保留头节点；空输入直接返回 None。'],
 'pitfalls':['删除后无条件推进 cur，会在 1→1→1 中留下一份多余重复。','算法依赖排序；1→2→1 的相同值不相邻，不能用本解法对无序链表全局去重。','不要把本题写成删除所有重复值的第 82 题，1→1→2 在本题中应变成 1→2。'],
 'complexity':'时间 O(n)，额外空间 O(1)，每个数值段保留原有的一个节点。',
 'quiz':{'question':'输入 2→2→2 时，cur 会向后移动几次？','answer':'零次。它始终指向第一个 2，连续跳过后两个节点，直到 cur.next 为 None；结果只保留原来的首节点。'},
 'tests':{'adapter':'linked','method':'deleteDuplicates','reuse_nodes':True,'cases':[{'args':[[1,1,1,2,3,3]],'expected':[1,2,3]},{'args':[[]],'expected':[]},{'args':[[2,2,2]],'expected':[2]},{'args':[[-1,0,1]],'expected':[-1,0,1]}]}
})

CHAPTER['problems'].append({
 'id':876,'slug':'middle-of-the-linked-list',
 'summary':'返回非空链表的中间节点。偶数长度有两个中点时，题目要求返回第二个中点，即下标 n//2 的原节点。',
 'baseline':'先遍历一次统计 n，再从头走 n//2 步也能做到 O(n) 时间、O(1) 空间。快慢指针把计数与定位合并为一次扫描，并且可以作为链表分割与回文判断的前置方法。',
 'insight':'让 slow 和 fast 同时从头出发，每轮分别走一步和两步。fast 能走的完整两步次数恰好是 n//2，因此结束时 slow 位于下标 n//2，不需要显式知道 n。',
 'steps':['slow=fast=head。','只要 fast 和 fast.next 都存在，就令 slow 走一步、fast 走两步。','fast 到达 None 或最后一个节点时退出，返回 slow 对象。'],
 'invariant':'完成 t 轮后，slow 位于从头走 t 条边的位置，fast 位于走 2t 条边的位置或刚好越过尾部到 None。长度为 2k 时可以完成 k 轮，slow 在下标 k；长度为 2k+1 时也完成 k 轮，slow 在下标 k。因此两种情况都返回 n//2。',
 'examples':[{'label':'偶数长度选第二个中点','input':'1→2→3→4→5→6','output':'原来的节点 4（从它往后为 4→5→6）','frames':[
  {'title':'两指针同从下标 0 出发','note':'slow=fast=节点 1。起点决定了偶数情况下的中点选择。','array':[1,2,3,4,5,6],'pointers':{'slow':0,'fast':0}},
  {'title':'完成一轮和两轮','note':'第一轮 slow=2、fast=3；第二轮 slow=3、fast=5，此时 fast 还有后继，可以再走两步。','array':[1,2,3,4,5,6],'pointers':{'slow':2,'fast':4}},
  {'title':'第三轮 fast 到 None','note':'slow 到节点 4，fast 从 5 经 6 到 None，退出。两个中点为 3 与 4，返回第二个 4。','diagram':'1 → 2 → 3 → 4 → 5 → 6 → None\n            ↑ slow          ↑ fast'},
  {'title':'返回节点，不是只返回数值','note':'返回的是原链中的节点 4，其 next 仍为节点 5。题目用 [4,5,6] 展示返回节点之后的链。','diagram':'返回引用 → 原节点 4 → 原节点 5 → 原节点 6 → None'}
 ]},{'label':'奇数长度只有一个中点','input':'1→2→3→4→5','output':'原来的节点 3','frames':[
  {'title':'两轮后 fast 在尾节点','note':'slow=3、fast=5，fast.next 为 None，不能再执行一轮。','array':[1,2,3,4,5],'pointers':{'slow':2,'fast':4}},
  {'title':'返回下标 2','note':'n//2=5//2=2，左右各有两个节点，位置唯一。','diagram':'1 → 2   [3]   4 → 5\n左侧 2 个       右侧 2 个'}
 ]}],
 'walkthrough':['偶数长度时 fast 变成 None 是正常终止，不是异常。必须先检查 fast，才能进一步读取它的 next。','若让 fast 从 head.next 出发，偶数长度会返回第一个中点。这种变体适合寻找前半段尾，但直接照搬到本题会返回错误位置。','两趟遍历也是正确主解，快慢指针的价值在于一次扫描和后续方法组合，不应误称它把 O(n) 降成了更小的复杂度。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # slow 每次一步、fast 每次两步，两者从头出发。
        slow = fast = head
        # 先检查 fast 及其后继，才能安全地走两步。
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
        # fast 到末尾时 slow 位于中间；偶数长度时返回第二个中点。
        return slow
'''.strip(),
 'code_notes':['slow=fast=head 让两个变量引用同一个节点，不会复制节点。之后分别赋值，二者会指向不同位置。','整个方法只改局部变量，不改任何节点的 next 或 val。','虽然题目保证非空，这段代码对 None 也会自然返回 None。'],
 'pitfalls':['停止条件和起点要配套，不能背一句“快两步慢一步”就忽略偶数中点。','返回 slow.val 会把节点接口错误地变成整数。','用相同数值来查找“中点节点”会在重复值输入中失效，中点由位置决定。'],
 'complexity':'时间 O(n)，额外空间 O(1)，原链连接保持不变。',
 'quiz':{'question':'两个节点 7→7 的中点是哪一个？','answer':'是第二个原节点。两个 val 都是 7，但节点身份不同；必须返回走一步到达的那个节点。'},
 'tests':{'adapter':'linked','method':'middleNode','result':'index','preserve_links':True,'cases':[{'args':[[1,2,3,4,5,6]],'expected':3},{'args':[[1,2,3,4,5]],'expected':2},{'args':[[7,7]],'expected':1},{'args':[[1]],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':19,'slug':'remove-nth-node-from-end-of-list',
 'summary':'删除链表倒数第 n 个节点并返回新头。题目保证链表非空，且 n 在 1..链表长度之间，因此不需要设计非法 n 的返回规则。',
 'baseline':'先统计长度 L，再找到正数第 L−n+1 个节点的前驱，需要两次扫描。可以让两个指针保持固定间距，把“离末尾 n 个节点”转换成同步到达关系，一次扫描定位前驱。',
 'insight':'删除单链表节点需要它的前驱，而不只是目标本身。引入 dummy 并让 fast 先比 slow 多走 n+1 条边；之后同步前进。fast 到 None 时，slow 恰好位于目标前驱。n+1 包含了从前驱走到目标的那一步。',
 'steps':['dummy.next=head，fast=slow=dummy。','fast 先走 n+1 步，建立两指针的固定距离。','只要 fast 不为 None，fast 和 slow 同时走一步。','目标为 slow.next，令 slow.next=slow.next.next 跳过它。','返回 dummy.next，兼容删除原头节点。'],
 'invariant':'把 dummy 的位置记为 −1、原节点位置记为 0..L−1、None 位置记为 L。建立间距后 fast 的位置比 slow 大 n+1；同步移动保持差值。结束时 fast=L，所以 slow=L−n−1，恰好是倒数第 n 个节点（位置 L−n）的前驱。若删除头，slow 的位置为 −1，也就是 dummy。',
 'examples':[{'label':'删除倒数第二个节点','input':'1→2→3→4→5，n=2','output':'1→2→3→5','frames':[
  {'title':'从 dummy 建立三条边的间距','note':'fast 先走 n+1=3 步，来到值为 3 的节点；slow 仍为 dummy。','diagram':'dummy → 1 → 2 → 3 → 4 → 5 → None\n↑ slow          ↑ fast'},
  {'title':'保持间距同步走','note':'接着三轮分别得到 (slow,fast)=(1,4)、(2,5)、(3,None)。','table':{'headers':['同步轮次','slow','fast'],'rows':[[1,1,4],[2,2,5],[3,3,'None']]}},
  {'title':'slow 停在目标前驱 3','note':'要删除的是 slow.next，也就是 4；把 3.next 改为 5。','diagram':'1 → 2 → 3 ─────→ 5 → None\n          被跳过：4'},
  {'title':'从 dummy.next 返回结果','note':'原头 1 仍被保留，返回链为 1→2→3→5。','array':[1,2,3,5],'array_label':'返回链中的值'}
 ]},{'label':'删除头节点也走相同代码','input':'7→8，n=2','output':'8','frames':[
  {'title':'fast 提前走三步就到 None','note':'slow 还在 dummy，同步循环不执行。目标正是 dummy.next 指向的 7。','diagram':'dummy → 7 → 8 → None\n↑ slow            ↑ fast'},
  {'title':'修改 dummy.next','note':'dummy.next 改为 8，返回它即可。若没有 dummy，就必须单独更新 head。','diagram':'dummy ─────→ 8 → None\n返回 dummy.next'}
 ]}],
 'walkthrough':['n=1 时 fast 先领先两条边，最终 slow 在尾节点前一位，删除的是尾节点。','n=L 时 fast 提前到 None，slow 不动，统一删除头节点。L=1、n=1 时 dummy.next 被设为 None，返回空链。','另一种写法让 fast 领先 n 步并在 fast.next 为 None 时停止，也可以正确；不能把那种提前步数与这里的停止条件混用。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        # 在头前加哨兵，删除头节点也能使用相同的重连操作。
        dummy = ListNode(0, head)
        slow = fast = dummy
        # fast 领先 n+1 条边，停到 None 时 slow 恰在待删节点之前。
        for _ in range(n + 1):
            fast = fast.next
        # 保持两指针间距不变，一起移动到链表末端。
        while fast is not None:
            slow = slow.next
            fast = fast.next
        # 跳过目标节点；不需要修改任何节点值。
        slow.next = slow.next.next
        return dummy.next
'''.strip(),
 'code_notes':['题目保证 1≤n≤L，因此提前移动的每次属性访问都合法，最后一步允许结果成为 None。','slow 指向前驱，slow.next 必定存在；被删除节点的后继可以是 None。','方法只重接一条边，其他保留节点的相对顺序不变。'],
 'pitfalls':['领先 n 还是 n+1，要与从哪里出发、何时停止一起推导。','找到目标后仅令目标变量等于 None，不会改变前驱的 next，链表仍然包含它。','返回旧 head 会在删除头节点时给出错误结果。'],
 'complexity':'时间 O(L)，fast 总共走到链尾，slow 跟随一段；额外空间 O(1)。',
 'quiz':{'question':'链长为 5、n=5 时 slow 最终在哪？','answer':'在 dummy。fast 先走 6 条边到 None，后续同步循环不执行，dummy.next 恰好是要删除的头节点。'},
 'tests':{'adapter':'linked','method':'removeNthFromEnd','reuse_nodes':True,'cases':[{'args':[[1,2,3,4,5],2],'expected':[1,2,3,5]},{'args':[[7,8],2],'expected':[8]},{'args':[[1],1],'expected':[]},{'args':[[1,2,3],1],'expected':[1,2]}]}
})

CHAPTER['problems'].append({
 'id':24,'slug':'swap-nodes-in-pairs',
 'summary':'把相邻节点两两交换，返回新头。只能调整节点连接，不能通过交换 val 代替节点交换；奇数长度最后一个节点保持原位。',
 'baseline':'保存所有节点到数组，再按交换后的顺序连接需要 O(n) 空间。每次交换只影响一对节点及其前驱与后继，局部保存三个引用就可以在原链上完成。',
 'insight':'假设当前局部为 prev→a→b→rest，目标为 prev→b→a→rest。先保存 a、b，就能逐条改边而不丢失节点。交换完成后 a 变成这一对的尾，也是下一对的前驱，因此 prev 应更新为 a。',
 'steps':['创建 dummy 指向 head，prev=dummy。','仅在 prev.next 和 prev.next.next 都存在时进入一轮，确保有完整一对。','保存 a=prev.next、b=a.next；先让 a.next=b.next 接住剩余后缀。','令 b.next=a，再令 prev.next=b，完成局部重排。','prev=a，继续下一对；最后返回 dummy.next。'],
 'invariant':'每轮开始时，prev 及之前的节点已经按对交换完成，prev.next 是尚未处理部分的头。当前 a、b 被完整保留，并把 a 接到原 b 的后继，保证后缀不丢失；prev→b→a 的连接完成后，这一对属于已处理前缀，prev=a 恢复同样的边界形式。',
 'examples':[{'label':'五个节点中最后一个不交换','input':'A(1)→B(2)→C(3)→D(4)→E(5)','output':'B(2)→A(1)→D(4)→C(3)→E(5)','frames':[
  {'title':'保存第一对 A、B','note':'prev=dummy，a=A，b=B。希望交换的是对象位置，A.val 与 B.val 始终不变。','diagram':'dummy → A(1) → B(2) → C(3) → D(4) → E(5)\n↑ prev  ↑ a     ↑ b'},
  {'title':'先给 A 接上剩余后缀','note':'a.next=b.next，使 A 指向 C。B 仍由局部变量 b 保存，不会丢失。','diagram':'dummy → A(1) → C(3) → D(4) → E(5)\nb → B(2) ─────→ C(3)'},
  {'title':'B 指向 A，前驱指向 B','note':'两条边补齐后局部成为 dummy→B→A→C。prev 更新到 A，不能更新到 B。','diagram':'dummy → B(2) → A(1) → C(3) → D(4) → E(5)\n                 ↑ prev'},
  {'title':'按同样规则交换 C、D','note':'下一对是 C、D，交换后 prev=C。只剩 E 一个节点，不满足两节点条件，结束。','diagram':'dummy → B(2) → A(1) → D(4) → C(3) → E(5) → None\n                                   ↑ prev'}
 ]}],
 'walkthrough':['交换 a、b 的变量名不会改变链表结构，必须实际修改 next。','先让 a 接住后缀，再反向连接 b→a，可以避免中间形成 a↔b 的环。即使采用其他顺序，也必须保存访问后缀的引用。','dummy 负责交换第一对时更新头，后面的每一对都只修改前驱的 next，因此没有特殊的“首对”分支。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        # prev 始终是当前待交换这一对的前驱。
        prev = dummy
        # 必须还剩两个节点才能交换；单独的尾节点原样保留。
        while prev.next is not None and prev.next.next is not None:
            a = prev.next
            b = a.next
            # 原来 prev→a→b→后段；先让 a 接住后段，避免丢链。
            a.next = b.next
            # 再接成 b→a，最后让前驱 prev 指向新的组头 b。
            b.next = a
            prev.next = b
            # a 交换后变成组尾，下一轮它就是新一对的前驱。
            prev = a
        return dummy.next
'''.strip(),
 'code_notes':['prev 是已处理前缀的尾，a、b 是当前一对，三个变量职责固定。','没有对 val 赋值，所以即使两个节点值相同，它们的对象位置也确实发生交换。','空链与单节点链不会进入循环，dummy.next 保持原头。'],
 'pitfalls':['只交换 a、b 变量或者 val，都没有完成题目要求的节点重排。','prev 更新成 b 会让下一轮又碰到已处理节点；交换后的尾是 a。','不检查第二个节点就读取 b.next，会在奇数尾部出错。'],
 'complexity':'时间 O(n)，每轮完成两个节点；额外空间 O(1)。',
 'quiz':{'question':'A(7)→B(7) 的数值展示交换前后一样，如何判断是否真的交换？','answer':'应检查返回头是否为原 B，B.next 是否为原 A，以及 A.next 是否为 None；只比较 [7,7] 看不出身份变化。'},
 'tests':{'adapter':'linked','method':'swapPairs','reuse_nodes':True,'cases':[{'args':[[1,2,3,4,5]],'expected':[2,1,4,3,5]},{'args':[[]],'expected':[]},{'args':[[1]],'expected':[1]},{'args':[[7,7]],'expected':[7,7]}]}
})

CHAPTER['problems'].append({
 'id':2,'slug':'add-two-numbers',
 'summary':'两条非空链表分别按低位在前存储非负整数，每个节点保存一个 0..9 的数字。返回同样按低位在前表示的和，不把整条链转换为整数。',
 'baseline':'先把两个链表还原成大整数再相加，会绕过逐位计算，也不便迁移到固定宽度整数语言。题目已经按低位在前排列，直接从头模拟加法即可。',
 'insight':'加法的每一列只依赖两边当前数字与上一列的进位。缺失的高位视为 0，计算 total=x+y+carry，个位为 total%10、下一列进位为 total//10。只要任一链还有节点或进位非零，就还有一列未处理。',
 'steps':['创建 dummy、tail，carry=0，a、b 指向两条输入链。','读取当前数字，不存在的一侧使用 0。','用 divmod(x+y+carry,10) 同时得到下一列进位和当前结果位，创建一个结果节点接到 tail 后。','推进存在的输入指针，tail 也前进。','两链和进位都耗尽后返回 dummy.next。'],
 'invariant':'完成 k 轮后，结果链准确保存两个输入之和最低 k 位；carry 保存尚未写入的高位贡献。每轮处理下一列并把除以 10 的商传给更高位，保持数值等式。结束时输入高位和进位都为空，全部和已写入结果。',
 'examples':[{'label':'长度不同且最后还有进位','input':'9→9（99），1（1）','output':'0→0→1（100）','frames':[
  {'title':'头节点就是个位','note':'a.val=9、b.val=1，carry=0，总和 10。结果先创建 0，下一列 carry=1。','diagram':'输入：9 → 9\n      1\n结果：0\n进位：1'},
  {'title':'较短输入已经读完','note':'b=None，十位用 y=0；9+0+1=10，再创建 0，carry 仍为 1。','diagram':'结果：0 → 0\n输入：a=None，b=None\n进位：1'},
  {'title':'单独写出最终进位','note':'两边都空，但 carry=1，仍执行一轮，创建节点 1。此后 carry=0，才真正结束。','diagram':'结果：0 → 0 → 1 → None\n数值：0×1 + 0×10 + 1×100 = 100'}
 ]},{'label':'普通逐位相加','input':'2→4→3（342），5→6→4（465）','output':'7→0→8（807）','frames':[
  {'title':'按个位、十位、百位依次计算','note':'个位 2+5=7；十位 4+6=10 写 0 进 1；百位 3+4+1=8。','table':{'headers':['数位','总和','写入','下一进位'],'rows':[['个',7,7,0],['十',10,0,1],['百',8,8,0]]}},
  {'title':'结果也保持低位在前','note':'头是个位 7，所以返回链为 7→0→8，不能反转为 8→0→7。','diagram':'7 → 0 → 8\n└个位  └百位'}
 ]}],
 'walkthrough':['这与第 415 题字符串相加维护相同的进位状态，但字符串要从末尾读取，链表在本题中直接从头读取。输入表示决定读取方向。','每轮 total 最大为 9+9+1=19，因此 carry 始终是 0 或 1，不依赖完整整数有多少位。','创建新的结果节点，使两条输入保持原结构。返回链的每一位属于独立新节点，不会与输入发生意外共享。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        tail = dummy
        a, b = l1, l2
        # carry 保存进位；两个链表按低位到高位读取。
        carry = 0
        # 节点都用完后，如果仍有进位，也必须再创建一位。
        while a is not None or b is not None or carry:
            # 较短的链表读完后，用 0 参与剩余位的相加。
            x = a.val if a is not None else 0
            y = b.val if b is not None else 0
            # 商是新进位，余数是当前结果位。
            carry, digit = divmod(x + y + carry, 10)
            # 新建结果节点，不改动两条输入链表。
            tail.next = ListNode(digit)
            tail = tail.next
            if a is not None:
                a = a.next
            if b is not None:
                b = b.next
        return dummy.next
'''.strip(),
 'api':{'signature':'divmod(a: int, b: int) -> tuple[int, int]','description':['返回 (a//b,a%b)，顺序是商在前、余数在后。这里除数为 10，总和为非负整数，所以商是下一位进位，余数是当前结果位。','同时赋值 carry,digit=divmod(...) 会先算出右侧完整结果，再更新左侧变量，因此表达式中的 carry 仍是上一列进位。']},
 'code_notes':['三个 or 条件覆盖不等长输入与最终进位，不能写成两条链都存在才继续。','ListNode(digit) 每次创建一位；dummy 只负责统一连接入口，不属于结果。','a、b 的移动不修改输入节点；本解法额外创建的是输出链。'],
 'pitfalls':['两条链的 while 条件写成 and，会在较短输入结束时丢掉剩余高位。','漏掉 carry 条件会把 99+1 错写成 0→0。','本题低位在前，不需要在最后把结果反转。'],
 'complexity':'时间 O(max(m,n))；除返回结果外辅助空间 O(1)，新结果链占 O(max(m,n)) 空间，最多多出一位。',
 'quiz':{'question':'0 加 0 会不会因为 carry=0 而不进入循环？','answer':'会进入，因为两条输入都各有一个值为 0 的节点。它们不是 None，因此创建一个结果零节点后才退出。'},
 'tests':{'adapter':'linked','method':'addTwoNumbers','linked_args':[0,1],'new_nodes':True,'preserve_links':True,'cases':[{'args':[[9,9],[1]],'expected':[0,0,1]},{'args':[[2,4,3],[5,6,4]],'expected':[7,0,8]},{'args':[[0],[0]],'expected':[0]},{'args':[[1],[9,9,9]],'expected':[0,0,0,1]}]}
})

CHAPTER['problems'].append({
 'id':160,'slug':'intersection-of-two-linked-lists',
 'summary':'两条无环单链表可能共享同一段尾部。返回第一个共享节点；如果没有共享节点则返回 None。判断依据是节点对象身份，调用结束后必须保留原连接。',
 'baseline':'把 A 的所有节点引用放进集合，再顺着 B 找第一次出现在集合中的节点，可以 O(m+n) 时间完成，但需要 O(m) 空间。两指针换到另一条链继续走，可以消除两条前缀的长度差，用 O(1) 空间对齐。',
 'insight':['若公共尾部长 c，A 独有前缀长 a，B 独有前缀长 b，则沿 A 再沿 B 的指针在第二段到达公共入口前，经过 a+c+b 个节点距离对应的部分；另一指针沿 B 再沿 A，经过 b+c+a，对应长度相同。两边各经历一次到 None 再切换头的步骤，不影响对齐。','因此 p 从 A 出发，走空后转到 B；q 从 B 出发，走空后转到 A。它们最终会在同一个共享节点相遇，或在没有相交时同时成为 None。整个过程无需修改任何 next。'],
 'steps':['p=headA，q=headB。','只要 p is not q，就让每个指针各走一步：非空时走 next，为 None 时切换到另一条链的头。','退出时 p 与 q 是同一个引用；返回 p，可能是公共节点，也可能是 None。'],
 'invariant':'每个指针依次遍历两条链，只改变起步顺序，不改变各链内的次序。若独有前缀等长，会在第一遍进入公共尾时相遇；否则切换后两条已走路径的长度差被抵消，在第一次共享节点处对齐。若无公共节点，两条路径包含相同总数的节点与相同的一次切换，最终同时到 None。非共享前缀的节点身份不同，不会误判提前相遇。',
 'examples':[{'label':'值相同不等于相交','input':'A1(4)→A2(1)→C1(8)→C2(5)；B1(1)→C1(8)→C2(5)','output':'原节点 C1(8)','frames':[
  {'title':'两条独有前缀共享 C1 之后的节点','note':'A2 与 B1 的 val 都是 1，却是两个对象。C1、C2 才是两条链共同引用的节点。','diagram':'A1(4) → A2(1) ─┐\n                ├→ C1(8) → C2(5) → None\n        B1(1) ──┘'},
  {'title':'第一遍因前缀不等长而错开','note':'两指针同时前进，q 先到 None，下一轮才切换到 headA。','table':{'headers':['完成轮数','p','q'],'rows':[[0,'A1','B1'],[1,'A2','C1'],[2,'C1','C2'],[3,'C2','None']]}},
  {'title':'分别切换头节点，抵消长度差','note':'第 4 轮 p=None、q=A1；第 5 轮 p=B1、q=A2。虽然它们数值都为 1，但 p is q 仍为 False。','table':{'headers':['完成轮数','p','q'],'rows':[[4,'None','A1'],[5,'B1(1)','A2(1)']]}},
  {'title':'下一轮同时到 C1','note':'第 6 轮两者都指向原节点 C1，循环结束。返回 C1，原链的所有 next 均未修改。','diagram':'p ─┐\n   ├→ C1(8) → C2(5) → None\nq ─┘'}
 ]},{'label':'相同数值的独立链仍不相交','input':'A(7)→None；B(7)→None，A 与 B 是不同对象','output':'None','frames':[
  {'title':'初始数值相同，身份不同','note':'不能因 p.val==q.val 就返回任何一个节点。','diagram':'p → A(7) → None\nq → B(7) → None'},
  {'title':'一步后同时到 None','note':'这组链长相同，一轮就同时走空。p is q 为 True，返回 None，表示没有共同节点。','diagram':'p → None ← q\n结果：没有交点'}
 ]}],
 'walkthrough':['公共部分必须是同一批节点，而不是两份数值相同的后缀。测试构造时必须让两条链真的指向同一个 C1。','代码在指针已经为 None 的那一轮切换头，而不是在尾节点处提前切换。这样无交点时两个 None 可以直接被循环条件识别。','题目保证无环；若把有环链表交给本解法，指针可能永远无法走空，不能把它当作任意链表相交问题的完整解法。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def getIntersectionNode(self, headA: Optional[ListNode], headB: Optional[ListNode]) -> Optional[ListNode]:
        # 比较的是节点身份，不是节点保存的值。
        p, q = headA, headB
        # 各走完 A+B 与 B+A，长度差会抵消；有交点时会在交点相遇。
        while p is not q:
            # 走到 None 后换到另一条链表的头，不提前在尾节点换头。
            p = p.next if p is not None else headB
            q = q.next if q is not None else headA
        # 无交点时两者最终同时为 None，也会退出循环。
        return p
'''.strip(),
 'code_notes':['is not 比较节点身份，也允许两个 None 在无交点时相等。','没有写入任何 .next 或 .val，满足结构保持要求。','交点若就是两个头共同指向的节点，循环一轮也不执行，直接返回该头。'],
 'pitfalls':['比较 val 会把两条独立链中的相同数值误判成相交。','临时把一条链尾接到另一条头会改变结构，若采用那种思路还必须完整恢复；本解法不需要这种修改。','只让较长链指针走快一步并不能持续对齐未知长度差，换头的依据是两条完整路径总长相等。'],
 'complexity':'时间 O(m+n)，每个指针至多遍历两条链及一次切换；额外空间 O(1)。',
 'quiz':{'question':'若两个头就是同一个对象，应该返回它还是继续寻找下一个共享节点？','answer':'直接返回它。题目要第一个相交节点，公共头已经是最早交点，初始 p is q 就满足退出条件。'},
 'tests':{'adapter':'linked','method':'getIntersectionNode','mode':'intersection','result':'shared','preserve_links':True,'cases':[{'args':[[4,1],[1],[8,5]],'expected':'shared'},{'args':[[7],[7],[]],'expected':None},{'args':[[],[],[1,2]],'expected':'shared'},{'args':[[1,2,3],[4],[]],'expected':None},{'args':[[],[9],[2,3]],'expected':'shared'}]}
})

CHAPTER['problems'].append({
 'id':141,'slug':'linked-list-cycle',
 'summary':'判断沿 next 不断前进是否会重复到达同一个节点。示例中的 pos 只是测试器连接尾部的位置，不是方法参数；方法只能从 head 观察链接。',
 'baseline':'用集合记录已经访问的节点引用，遇到同一对象第二次出现就返回 True，需要 O(n) 空间。快慢指针通过相对速度判断环，只需两个引用。',
 'insight':'如果无环，走得快的指针最终会到 None；如果有环，两指针最终都进入环。此后 fast 每轮比 slow 多走一步，它们在环内的相对位置每轮前进一格，至多一个环长就会对齐。',
 'steps':['slow=fast=head，但不要在移动前把初始同位置当成有环。','只要 fast 和 fast.next 都存在，slow 走一步，fast 走两步。','移动后若 slow is fast，返回 True。','fast 无法继续走两步则返回 False。'],
 'invariant':'两个指针每轮累计路程分别为 t、2t。无环链上不同路程不能到同一节点；有环时，在 slow 进入环后，两者位置差按模环长每轮增加 1，因此必然成为 0。检测的是相同节点引用，而非可能重复的数值。',
 'examples':[{'label':'相遇可以发生在入口之外','input':'A(3)→B(2)→C(0)→D(-4)，D.next=B','output':'True','frames':[
  {'title':'环的入口是 B','note':'尾节点 D 指回 B，环中共有 B、C、D 三个节点；A 在环外。','diagram':'A(3) → B(2) → C(0) → D(-4)\n       ↑                 │\n       └─────────────────┘'},
  {'title':'第一轮到 B 与 C','note':'slow 走一步到 B；fast 走两步到 C。两者不同，继续。','table':{'headers':['轮次','slow','fast'],'rows':[[0,'A','A'],[1,'B','C']]}},
  {'title':'第三轮在 D 相遇','note':'第二轮 slow=C、fast=B；第三轮 slow=D、fast=D，确认有环。相遇点 D 并不是入口 B。','table':{'headers':['轮次','slow','fast'],'rows':[[2,'C','B'],[3,'D','D']]}},
  {'title':'本题只需返回布尔值','note':'已经证明环存在，直接返回 True。寻找入口还需要第 142 题的第二阶段。','diagram':'首次相遇 D → 证明有环\n环入口 B   → 需要继续定位'}
 ]},{'label':'重复值并不构成环','input':'A(1)→B(1)→C(1)→None','output':'False','frames':[
  {'title':'一轮后 slow=B，fast=C','note':'二者数值都是 1，但引用不同，不能判环。','diagram':'A(1) → B(1) → C(1) → None\n       ↑ slow  ↑ fast'},
  {'title':'fast.next 为 None，结束','note':'没有边指向先前节点，fast 不能继续两步，返回 False。','diagram':'fast → C(1) → None\n结果：无环'}
 ]}],
 'walkthrough':['初始 slow 与 fast 同在 head，无论链是否有环都相等，所以相遇判断必须放在一次移动之后。','在环中，fast 可能越过 slow 而不是恰好停在其位置吗？两者每轮相对只前进一格，按模环长变化必然经过零，因此不会一直错过。','单节点自环也能检测：两者移动后仍指向该节点，第一次循环就返回 True；单节点无环则不会进入循环。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        # 快慢指针从同一头节点出发，但必须先移动再判断是否相遇。
        slow = fast = head
        # 无环时快指针会先碰到空节点，从而结束循环。
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            # 有环时快指针每轮在环内追近一步，最终与慢指针指向同一节点。
            if slow is fast:
                return True
        return False
'''.strip(),
 'code_notes':['fast.next.next 可以合法地得到 None，下一次循环条件负责停止。','不存在可直接读取的 pos 字段，代码没有依赖测试器的构造信息。','没有更改原连接，也没有为每个节点保存访问标记。'],
 'pitfalls':['移动前检查相等会把任意非空链都判成有环。','比较 slow.val 与 fast.val 会在大量重复值的无环链上误判。','只检查 fast.next 而不先检查 fast，可能对 None 访问属性。'],
 'complexity':'时间 O(n)，n 表示可达的不同节点数；入环后至多再走一个环长就相遇。额外空间 O(1)。',
 'quiz':{'question':'检测到相遇就能直接返回该节点作为环入口吗？','answer':'不能。例子中的入口是 B，但首次相遇在 D。第 141 题只返回 True；入口定位需要额外的距离推导。'},
 'tests':{'adapter':'linked','method':'hasCycle','result':'scalar','preserve_links':True,'cases':[{'args':[[3,2,0,-4]],'cycle_pos':1,'expected':True},{'args':[[1,1,1]],'expected':False},{'args':[[1]],'cycle_pos':0,'expected':True},{'args':[[1]],'expected':False},{'args':[[]],'expected':False}]}
})

CHAPTER['problems'].append({
 'id':142,'slug':'linked-list-cycle-ii',
 'summary':'若链表有环，返回环入口的原节点；无环返回 None。不能修改链表，且方法没有 pos 参数。先判断有环，再定位入口，两个阶段使用不同的速度规则。',
 'baseline':'保存已访问节点的集合，第一次再次遇到的节点就是环入口，但需要 O(n) 空间。第 141 题的快慢指针能找到一次相遇，结合路程同余关系还能用常数空间找到入口。',
 'insight':['设头到入口的距离为 a，环长为 c；首次相遇时 slow 总共走 t 步，fast 走 2t 步。它们停在同一个环节点，路程差 t 必须是 c 的整数倍，即 t≡0（mod c）。slow 在环内相对入口的位置为 (t−a) mod c，因此从相遇点再走 a 步恰好回到入口。','令 finder 从头出发，slow 留在相遇点，两者改成每次都走一步。a 步后 finder 到入口，slow 也到入口；在 finder 尚未入环时，一个在环外、一个在环内，不可能提前相遇。因此这次相遇必定是入口。'],
 'steps':['使用快两步、慢一步的循环寻找首次相遇；若快指针先走空，返回 None。','相遇后令 finder=head，slow 保留相遇位置。','只要 finder is not slow，两者各走一步。','返回再次相遇的原节点；若入口就是 head，第二阶段可能不需要移动。'],
 'invariant':'第一阶段保持 fast 路程为 slow 的两倍，非空相遇保证 t 是环长的倍数。第二阶段走了 s 步时，finder 在头之后 s 步，slow 在相遇点之后 s 步；两者在 s=a 时同到入口，且 s<a 时 finder 在无环前缀、slow 在环内，身份不可能相同。',
 'examples':[{'label':'从 D 相遇点走回 B 入口','input':'A(3)→B(2)→C(0)→D(-4)，D.next=B','output':'原节点 B(2)','frames':[
  {'title':'第一阶段沿用判环的三轮','note':'(slow,fast) 依次为 (B,C)、(C,B)、(D,D)，在 D 相遇。此时 a=1、c=3，slow 已走 t=3。','diagram':'A → B → C → D\n    ↑       │\n    └───────┘\n相遇点：D；入口：B'},
  {'title':'把新指针放到头 A','note':'finder=A，slow=D。第二阶段两个指针都改成一步，不能继续让一个走两步。','diagram':'finder → A → B → C → D ← slow\n             ↑       │\n             └───────┘'},
  {'title':'各走一步，在 B 相遇','note':'finder 从 A 到 B；slow 从 D 沿环边到 B。返回这个同一个 B 对象。','diagram':'finder ─┐\n        ├→ B → C → D\nslow ───┘  ↑       │\n           └───────┘'},
  {'title':'核对距离关系','note':'相遇点 D 相对入口 B 向前两步，再走 a=1 步便完成一整圈，回到 B。','diagram':'入口 B → C → D → B 入口\n       已走 2 步  再走 1 步\n头部 A ─────────→ B 入口\n          1 步','equation':'t=3，c=3；(t−a)+a=2+1=3≡0（mod 3）'}
 ]},{'label':'环从头开始','input':'A(1)→B(2)→A(1)…','output':'原节点 A(1)','frames':[
  {'title':'两轮后在 A 相遇','note':'slow 的路程为 2，恰好一圈；fast 的路程为 4，恰好两圈。','table':{'headers':['轮次','slow','fast'],'rows':[[1,'B','A'],[2,'A','A']]}},
  {'title':'第二阶段立即结束','note':'finder=head=A，slow 也在 A，入口距离 a=0，无需再移动，直接返回 A。','diagram':'head = finder = slow = 环入口 A'}
 ]}],
 'walkthrough':['推导使用 t 而不强行写 t=a+b，是为了允许 slow 相遇前已经在环中多走若干圈；同余关系在所有前缀长度下都成立。','相遇点到入口未必只走一段不超过一圈的路径。当 a 大于环长时，slow 会多绕几圈，但走 a 步后的模位置仍然是入口。','finder 在无环前缀上不能与环内 slow 相遇，这不仅证明“入口是一个相遇点”，也证明它是第二阶段遇到的第一个相遇点。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            # 第一次相遇只能说明有环，这个节点不一定是入口。
            if slow is fast:
                # 让一个指针回到头部，另一个留在相遇点，两者改为每次一步。
                finder = head
                # 按环长同余关系，两者会在环入口相遇，而不是再快慢走。
                while finder is not slow:
                    finder = finder.next
                    slow = slow.next
                return finder
        # 快指针先遇到空节点，说明无环。
        return None
'''.strip(),
 'code_notes':['内层循环只在已确认存在环后执行，slow 始终在环内，不会走到 None。','finder 与 slow 在第二阶段都一步，这对应“从两处各走 a 步”的证明。','返回 finder 节点对象，而不是它的数值或一个重新创建的同值节点。'],
 'pitfalls':['首次相遇只能证明环存在，直接返回 slow 会在入口不等于相遇点时失败。','第二阶段若继续保持两倍速度，前面的距离对齐证明不再成立。','用值比较无法区分环中不同的同值节点，必须用身份。'],
 'complexity':'时间 O(a+c)，第一阶段线性找到相遇，第二阶段走 a 步；额外空间 O(1)，原链不变。',
 'quiz':{'question':'无环时是否需要启动第二阶段？','answer':'不需要。fast 或 fast.next 成为 None 后，第一阶段自然结束并返回 None；没有相遇点就没有第二阶段的距离依据。'},
 'tests':{'adapter':'linked','method':'detectCycle','result':'index','preserve_links':True,'cases':[{'args':[[3,2,0,-4]],'cycle_pos':1,'expected':1},{'args':[[1,2]],'cycle_pos':0,'expected':0},{'args':[[7,7,7]],'cycle_pos':2,'expected':2},{'args':[[1]],'expected':None},{'args':[[]],'expected':None}]}
})

CHAPTER['problems'].append({
 'id':234,'slug':'palindrome-linked-list',
 'summary':'判断链表节点值从前往后与从后往前是否一致。目标是 O(n) 时间、O(1) 辅助空间；本解法比较后还会恢复输入连接，便于调用方继续使用原链。',
 'baseline':'把节点值放入数组，再比较数组与逆序数组非常直接，但占 O(n) 空间。单链表无法从尾向前走，可以把后半段暂时反转，让两个方向的对应位置都能够通过 next 顺序读取。',
 'insight':'把问题拆成找前半段末尾、断开并反转后半段、逐项比较、恢复连接四步。奇数长度的中心值没有配对对象，比较时只走较短的后半段，因此自然忽略中心。即使发现不匹配，也先保存 False，完成恢复后再返回。',
 'steps':['零个或一个节点直接返回 True。slow=fast=head，用 fast.next 与 fast.next.next 的存在性定位前半段末尾；奇数时 slow 停在中心。','保存 second_start=slow.next，并将 slow.next=None 临时断开两段。','用第 206 题的迭代方法反转 second_start，得到 second。','p 从 head、q 从 second 出发，比较到 q 为 None；遇到不等记录 result=False 并结束比较。','再次反转 second，把 slow.next 接回恢复后的后半段，最后返回 result。'],
 'invariant':['分割后前半段长度为 ceil(n/2)，后半段为 floor(n/2)。后半段反转后，其第 j 项对应原链倒数第 j+1 项；前半段第 j 项对应原链正数第 j+1 项，两者数值相等恰好就是回文的成对条件。','比较到后半段结束时，所有必要的对都已检查；奇数中心未被比较也不影响回文性。反转操作可逆，再反转同一批节点并接回原分界，能够恢复全部原有 next。'],
 'examples':[{'label':'奇数长度忽略中心并恢复原链','input':'A(1)→B(2)→C(3)→D(2)→E(1)','output':'True，原链连接保持不变','frames':[
  {'title':'找到前半段末尾 C','note':'使用本题的停止条件，两轮后 slow=C、fast=E。C 是奇数中心，后半段从 D 开始。','diagram':'A(1) → B(2) → C(3) → D(2) → E(1)\n                 ↑ slow          ↑ fast'},
  {'title':'断开后把 D→E 反转','note':'C.next=None，前半段 A→B→C；反转得到 E→D，两个独立链可同步比较。','diagram':'前半段：A(1) → B(2) → C(3) → None\n后半段：E(1) → D(2) → None'},
  {'title':'比较 A 与 E、B 与 D','note':'1=1、2=2，q 已到 None，停止比较。中心 C 的 3 无需寻找配对节点。','table':{'headers':['前半段','反转后半段','是否相等'],'rows':[['A(1)','E(1)','是'],['B(2)','D(2)','是']]}},
  {'title':'再次反转并接回 C.next','note':'E→D 再反转回 D→E，把 C.next=D。原节点、数值和每条连接全部恢复，返回 True。','diagram':'A(1) → B(2) → C(3) → D(2) → E(1) → None'}
 ]},{'label':'不匹配也要恢复','input':'1→2→3→4','output':'False，仍恢复为 1→2→3→4','frames':[
  {'title':'分成 1→2 与 3→4，再反转后半段','note':'得到前半段 1→2、后半段 4→3。第一对 1 与 4 就不相等。','diagram':'p → 1 → 2 → None\nq → 4 → 3 → None\n1 != 4 → result=False'},
  {'title':'退出比较，继续执行恢复步骤','note':'用 break 离开比较循环，不能在这里直接 return False，否则输入会留在断开状态。','diagram':'恢复 3 → 4\n把 2.next 接到 3\n原链：1 → 2 → 3 → 4 → None'}
 ]}],
 'walkthrough':['与第 876 题不同，这里希望得到前半段的最后一个节点。偶数长度 4 时 slow 应停在第 2 个节点，才能分成两个长度相等的半段。','反转后只要 q 非空，就一定还有对应的 p，因为前半段从不比后半段短。','second 必须保留为反转后半段的头，比较过程用 q 向后走，不能把唯一的恢复入口消耗掉。','恢复不是回文判定的数学必要步骤，但它使函数在返回布尔值的同时保留原输入，避免隐藏的结构副作用。代码和复杂度分析都包含恢复成本。'],
 'code':'''

from typing import Optional

# LeetCode 提供同样接口的 ListNode；保留此定义也便于本地运行。
class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        if head is None or head.next is None:
            return True

        # 原地反转指定后半段，用于从尾向头比较；结束后还要恢复。
        def reverse(node: Optional[ListNode]) -> Optional[ListNode]:
            prev = None
            while node is not None:
                # 先保留后继，再反向连接，防止丢失未处理的链条。
                nxt = node.next
                node.next = prev
                prev = node
                node = nxt
            return prev

        slow = fast = head
        # 这种停止条件让 slow 停在前半段末尾，奇数长度时包含中点。
        while fast.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next
        second_start = slow.next
        # 先断开两段，避免反转与遍历时仍沿旧连接串到另一半。
        slow.next = None
        second = reverse(second_start)
        p, q = head, second
        result = True
        # 后半段不会比前半段长，只需比较到后半段结束。
        while q is not None:
            if p.val != q.val:
                result = False
                break
            p = p.next
            q = q.next
        # 即使中途发现不相等，也恢复原链表，然后才返回结果。
        slow.next = reverse(second)
        return result
'''.strip(),
 'code_notes':['这里 fast 初始非空，且只有确认 fast.next.next 非空时才赋值给 fast，所以循环内始终能读取 fast.next。','局部 reverse 使用迭代，避免递归栈使空间变成 O(n)。','两次反转处理的是同一批后半段节点，恢复时不创建副本。','比较不等时用 break 保留后续恢复动作，最后统一 return。'],
 'pitfalls':['直接照搬第二中点模板并把 slow.next 当后半段，会在偶数长度时分错边界。','反转后忘记恢复，调用方看到的输入链会被截短或重排。','发现不等立即 return False，会跳过恢复；需要把结果和清理动作分开。','把比较写到 p 也必须走空，会在奇数长度中心处要求不存在的配对。'],
 'complexity':'时间 O(n)，定位、两次半段反转和比较的总工作仍为线性；除固定引用和布尔值外空间 O(1)。原链在函数返回前恢复。',
 'quiz':{'question':'为什么保存 second 后，还要另设 q 用于比较？','answer':'q 会一路前进，最后成为 None 或停在不匹配位置。second 保留反转后半段的起点，才能在任何比较结果下完整反转回来。'},
 'tests':{'adapter':'linked','method':'isPalindrome','result':'scalar','preserve_links':True,'cases':[{'args':[[1,2,3,2,1]],'expected':True},{'args':[[1,2,2,1]],'expected':True},{'args':[[1,2,3,4]],'expected':False},{'args':[[1,2]],'expected':False},{'args':[[7]],'expected':True},{'args':[[1,1]],'expected':True}]}
})
