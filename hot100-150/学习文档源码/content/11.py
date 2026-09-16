from textwrap import dedent

NODE = dedent('''
from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

''')

def solution(body, extra=''):
    return extra + NODE + dedent(body).strip()

TREE = '    1\n   / \\\n  2   3\n / \\   \\\n4   5   6'
SAMPLE = [1, 2, 3, 4, 5, None, 6]

def checks(method, pairs, **options):
    return dict(adapter='tree', method=method, preserve_tree=True,
                cases=[dict(args=args, expected=expected) for args, expected in pairs], **options)

CHAPTER = {
 'lead':'先明确访问节点的时机，再区分向下传递的条件与向上返回的子树信息。树题的难点通常不是写出递归，而是说明每次调用或每个栈帧到底负责什么。',
 'intro':['学习路径：144 前序 → 94 中序 → 145 后序 → 102 层序 → 103 锯齿 → 199 右视图 → 958 完全性 → 104 深度 → 110 平衡 → 226 翻转 → 101 对称 → 543 直径 → 98 验证 BST → 230 第 k 小 → 108 有序数组建树 → 105 前序中序建树 → 112、113、129 根到叶路径 → 236 最近公共祖先 → 437 任意起点路径 → 124 最大路径和 → 114 展开 → 297 序列化。','每份代码包含完整 TreeNode 与所需导入，可以独立提交。代码接收根节点引用，图中的 [1,2,3,null,4] 是按队列展开非空父节点的展示格式，不是函数实际接收的列表。None 表示缺少孩子，数值 0 仍然是一个真实节点。','本章用显式栈讲清递归的执行过程。可能退化成长链的题采用迭代主解，避免 Python 默认递归深度影响有效输入；108 每次平分区间，递归深度只有 O(log n)，可以直接使用递归。'],
 'sections':[
  {'title':'先给函数或状态一句准确的定义','body':['向下传递：当前深度、从根累积的数值、祖先给出的上下界。这些信息在进入孩子之前已经知道。','向上返回：子树高度、可延伸的一条路径贡献、子树是否满足条件。这些信息需要孩子处理完后才能得到。','全局答案可以与返回值不同。直径可能同时使用左右两臂；返回给父节点的高度只能选择其中较长的一臂。'], 'diagram':'祖先条件、路径前缀\n         ↓ 向下传递\n       当前节点\n      /        \\\n  左子树      右子树\n      \\        /\n         ↑ 向上汇总\n   高度、单臂贡献、子树结论'},
  {'title':'前中后序只是处理根的时机不同','body':['前序：根→左→右，先处理当前节点，适合复制、编码和向下传递状态。中序：左→根→右，在 BST 上得到严格递增序列。后序：左→右→根，适合依赖孩子结果的计算。','显式栈是后进先出。想让左子树先处理，就把右子树先压入。后序还可以给节点加“孩子是否展开”的标记，第二次遇到它时再汇总。'], 'diagram':'节点 x 的处理顺序\n前序：处理 x → 左子树 → 右子树\n中序：左子树 → 处理 x → 右子树\n后序：左子树 → 右子树 → 处理 x'},
  {'title':'层序必须冻结这一层的数量','body':['BFS 用 deque 保存等待处理的节点。每层开始先取 size=len(queue)，随后只弹出 size 个节点；本轮追加的孩子属于下一层。','如果一边追加孩子，一边用“队列非空”作为本层结束条件，就会把后续所有层吞到同一层里。右视图、锯齿层序都建立在清晰的层边界上。'], 'diagram':'本层开始：queue = [2, 3]，size = 2\n弹出 2 后：queue = [3, 4, 5]\n弹出 3 后：queue = [4, 5, 6]\n本层结束；孩子留到下一层'},
  {'title':'空间复杂度要说明高度与宽度','body':['记 n 为节点数，h 为最大根到叶节点数，w 为最大层宽。普通 DFS 的显式栈一般是 O(h)，BFS 队列是 O(w)，二者最坏都可能达到 O(n)。','结果列表不等于辅助空间：遍历返回 n 个值需要 O(n) 输出空间；如果还建立每个节点的高度表，则应另计 O(n) 辅助空间。','本章高度汇总会在父节点取到孩子结果后删除它们，让已完成且已使用的子树信息及时退出。不要因为用了字典就自动报 O(1)，也不要忽略显式栈。']}
 ],
 'apis':[
  {'signature':'deque(iterable=())；append(x)；popleft() -> 最左侧元素','description':['from collections import deque 创建双端队列。append 从右端加入，popleft 从左端移除并返回，端点操作为 O(1)。队列为空时 popleft 会报错，所以先用 while queue 或冻结的有效数量保证存在元素。','list.pop(0) 会搬移剩余元素，不适合反复执行的层序遍历。DFS 则可以直接使用 list.append 与 list.pop() 操作末端。']},
  {'signature':'mapping.pop(key, default) -> 被删除的值，或 default','description':['本章用 height.pop(child, 0) 读取已经计算出的孩子高度并删除该条目。空孩子没有对应键，返回默认高度 0。','普通 TreeNode 没有覆盖相等比较，字典键按对象身份区分。两个 val 相同的节点仍是两个不同键。']},
  {'signature':'path.copy() -> 新的浅拷贝列表','description':['路径元素是整数时，复制列表就足以保存此刻的路径。后续对 path 的 append/pop 不会改变已经保存的列表。','直接 answer.append(path) 会让多个结果指向同一个可变列表；回溯清空 path 后，旧答案也会跟着变空。']}
 ],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':144, 'slug':'binary-tree-preorder-traversal',
 'summary':'返回二叉树的前序遍历数值：先根，再完整遍历左子树，最后完整遍历右子树。空树返回空列表。',
 'baseline':'递归直接写“记录根、递归左、递归右”即可，时间已经是 O(n)。迭代的目的不是降低时间，而是把隐含的调用栈显式表达出来，并掌握题目要求的迭代变体。',
 'insight':'栈保存尚未处理的子树根。弹出一个根时立即记录它，再把右孩子、左孩子依次压栈。后入栈的左孩子先处理，它的后代也会压在等待中的右子树上方。',
 'steps':['空根直接返回 []；否则初始化 stack=[root]。','弹出 node，把 node.val 加入结果。','若右孩子存在先压右，再压左孩子。','重复到栈空，返回结果。'],
 'invariant':'每轮栈顶是前序中下一棵待遍历子树的根。记录根后，左子树全部工作排在右子树之前；左子树递归产生的新工作又排在更早等待的右子树之前，因此每个根都先于自己的左右后代输出。',
 'examples':[{'label':'右先入栈，左先出栈','input':'root=[1,2,3,4,5,null,6]','output':'[1,2,4,5,3,6]','frames':[
  {'title':'初始化','note':'栈从左到右表示栈底到栈顶，初始为 [1]。','diagram':TREE,'metrics':[['stack','[1]'],['结果','[]']]},
  {'title':'访问 1，再压右 3、左 2','note':'下一次弹出的是 2；3 暂时等待。','diagram':TREE,'metrics':[['stack','[3,2]'],['结果','[1]']]},
  {'title':'访问 2，再压 5、4','note':'栈变成 [3,5,4]，先完成左边的 4，再完成 5。','table':{'headers':['操作','栈（右端顶）','结果'],'rows':[['弹 2','[3,5,4]','[1,2]'],['弹 4','[3,5]','[1,2,4]'],['弹 5','[3]','[1,2,4,5]']]}},
  {'title':'最后处理右子树','note':'访问 3 后压入其右孩子 6，最终访问 6。','array':[1,2,4,5,3,6],'active':[4,5]}
 ]}],
 'walkthrough':['记录 1 只代表根处理完了，并不代表整棵树处理完了。栈中的 3 和 2 保留两个尚未完成的子任务。','3 在栈底等待时，2 的孩子 5、4 被压到它上面，保证整个左子树连续完成。','若按左、右顺序压栈，得到的是根→右→左，这与本题要求不同。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def preorderTraversal(self, root: Optional[TreeNode]) -> list[int]:
        if root is None:
            return []
        result = []
        # 栈后进先出，所以先放右孩子、后放左孩子，才能按根左右访问。
        stack = [root]
        while stack:
            node = stack.pop()
            # 前序在弹出节点时立刻记录根，再安排它的孩子。
            result.append(node.val)
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
        return result
'''.strip(),
 'code_notes':['只将非空节点压栈，所以弹出后可以直接读取 val。','stack 保存节点引用，result 保存整数；没有修改树的任何边。','这里 list[int] 是返回列表的类型标注，不会把 TreeNode 自动转为整数。'],
 'pitfalls':['混淆压栈顺序与访问顺序。','把遍历写成按层输出，树形稍复杂时顺序就不同。','以 node.val 是否为真判断节点存在，会漏掉值为 0 的节点。'],
 'complexity':'时间 O(n)；辅助栈 O(h)，最坏 O(n)；输出列表另占 O(n)。',
 'quiz':{'question':'只有右链 1→2→3 时，会因为“先压右”而反向输出吗？','answer':'不会。每次先弹出并记录当前根，再压入唯一右孩子，输出仍然是 [1,2,3]。'},
 'tests':checks('preorderTraversal',[([SAMPLE],[1,2,4,5,3,6]),([[]],[]),([[0]],[0]),([[1,None,2,3]],[1,2,3])])
})

CHAPTER['problems'].append({
 'id':94,'slug':'binary-tree-inorder-traversal',
 'summary':'返回左子树→根→右子树的中序遍历。一般二叉树的中序结果不一定有序；只有满足 BST 条件时才有额外的有序性质。',
 'baseline':'递归会先进入左孩子，等它返回才记录当前节点。若迭代时一弹栈就记录初始根，会错误地变成前序，因此需要额外保留尚未处理的祖先。',
 'insight':'cur 指向接下来要展开的子树，stack 保存正在等待左子树完成的祖先。沿左链只压栈、不输出；走到空位置后，栈顶的左子树已经完成，这时才输出根并转到右子树。',
 'steps':['cur=root，stack 与 result 为空。','只要 cur 非空，就压入 cur 并沿 left 前进。','左链走完后弹出一个节点，记录它的 val。','cur 转到刚弹出节点的 right，重复“走左链”。','cur 为空且栈也空时结束。'],
 'invariant':'栈中的节点还未输出，栈顶是最近的等待祖先；它的左侧任务完成后才能弹出。弹出后立即转入它的右子树，在右子树完成前不会处理更高祖先，从而保持每棵子树的左→根→右次序。',
 'examples':[{'label':'沿左链暂存祖先','input':'root=[1,2,3,4,5,null,6]','output':'[4,2,5,1,3,6]','frames':[
  {'title':'先压 1、2、4','note':'cur 走到 4.left=None，尚未输出任何值。','diagram':TREE,'metrics':[['stack','[1,2,4]'],['结果','[]']]},
  {'title':'输出 4，然后回到 2','note':'4 无右孩子，下一次弹出 2；输出 2 后转到右孩子 5。','table':{'headers':['弹出','下一棵子树','结果'],'rows':[[4,'None','[4]'],[2,5,'[4,2]']]}},
  {'title':'5 完成后才输出祖先 1','note':'5 的整棵子树完成，左子树 2 才算遍历完。','array':[4,2,5,1],'active':[2,3]},
  {'title':'展开 1 的右子树','note':'3 没有左孩子，输出 3，再转向 6。','array':[4,2,5,1,3,6],'active':[4,5]}
 ]}],
 'walkthrough':['压栈是记住“回来后还要输出这个根”，不是访问完成。1 会在栈底等待 2、4、5 全部处理完。','外循环必须是 cur 存在或者 stack 非空。cur=None 可能只是暂时到达一个空孩子，此时栈里还有祖先待处理。','中序序列 [4,2,5,1,3,6] 并未递增，说明遍历顺序与 BST 的数值约束是不同概念。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> list[int]:
        result = []
        stack = []
        cur = root
        # cur 处理当前分支，栈保存回头还需访问的祖先。
        while cur is not None or stack:
            # 先一路走到最左，把沿途根节点留在栈中等待。
            while cur is not None:
                stack.append(cur)
                cur = cur.left
            # 左子树已经处理完，现在才访问根，随后转向右子树。
            cur = stack.pop()
            result.append(cur.val)
            cur = cur.right
        return result
'''.strip(),
 'code_notes':['内循环结束时 cur 为 None，但外循环保证栈里有可弹出的节点。','cur=cur.right 可能得到 None，这时下一轮会直接回到祖先。','一个节点只入栈、出栈各一次，嵌套 while 并不意味着 O(n²)。'],
 'pitfalls':['外循环写成 and 会过早结束。','压栈时输出节点，会破坏左子树先完成的要求。','弹出后忘记进入右子树，会漏掉节点。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，输出空间 O(n)。',
 'quiz':{'question':'为什么不在压入 1 时就输出 1？','answer':'因为 1 的左子树尚未完成。中序要求它的所有左侧后代都在 1 之前输出，所以需要暂存在栈中等待。'},
 'tests':checks('inorderTraversal',[([SAMPLE],[4,2,5,1,3,6]),([[]],[]),([[0]],[0]),([[1,None,2,3]],[1,3,2])])
})

CHAPTER['problems'].append({
 'id':145,'slug':'binary-tree-postorder-traversal',
 'summary':'返回左子树→右子树→根的后序遍历。后序是计算子树高度、直径和路径贡献的基础，因为处理根时两个孩子的结果都已就绪。',
 'baseline':'递归在两次孩子调用返回后记录根，最自然。迭代若只保存节点而不保存处理阶段，就难以判断再次遇到根时孩子是否已经完成。',
 'insight':'栈帧使用 (node, expanded)。False 表示还要展开孩子；True 表示孩子的工作已安排在自己上方，下一次弹出时即可处理根。压入顺序是根 True、右 False、左 False。',
 'steps':['空树返回 []；将 (root,False) 入栈。','弹出未展开帧：先压回 (node,True)，再压右孩子、左孩子的未展开帧。','弹出已展开帧：把 node.val 加入结果。','栈空表示所有节点完成。'],
 'invariant':'对每个 True 帧，它的全部孩子任务都在它上方，必须先完成并弹出；所以 True 帧弹出时左右子树已经输出。兄弟任务按右先压、左后压安排，又保证左子树早于右子树。',
 'examples':[{'label':'根节点需要等待孩子','input':'root=[1,2,3,4,5,null,6]','output':'[4,5,2,6,3,1]','frames':[
  {'title':'展开 1，把它的完成动作留在栈底','note':'F 表示展开，T 表示完成。栈右端为顶。','diagram':TREE,'metrics':[['stack','[(1,T),(3,F),(2,F)]']]},
  {'title':'展开 2，再完成叶子 4、5','note':'2 的完成动作等到 4、5 后面，不能展开 2 时就输出它。','table':{'headers':['完成动作','结果'],'rows':[['4,T','[4]'],['5,T','[4,5]'],['2,T','[4,5,2]']]}},
  {'title':'完成右子树，再完成根','note':'6 先于 3，左右子树都结束后才输出 1。','array':[4,5,2,6,3,1],'active':[3,4,5]}
 ]}],
 'walkthrough':['叶子也经历 False→True 两个阶段，只是它没有孩子可安排，所以 True 紧接着被弹出。','每个节点最多产生两个帧处理，总工作仍然与节点数成正比。','后续题可以把 result.append 改成“读取两个孩子结果并合成当前结果”，遍历骨架保持不变。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def postorderTraversal(self, root: Optional[TreeNode]) -> list[int]:
        if root is None:
            return []
        result = []
        # False 表示首次遇到节点，True 表示孩子已处理、该访问根了。
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            # 后序必须等左右子树完成，才能把根加入结果。
            if expanded:
                result.append(node.val)
                continue
            # 压栈顺序是根的返回事件、右孩子、左孩子；弹出时恰好左右根。
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        return result
'''.strip(),
 'code_notes':['expanded 标记的是执行阶段，没有写入 TreeNode 本身。','continue 保证已完成的帧不会再次安排孩子，否则会无限重复。','栈保留的是沿当前路径等待的祖先和兄弟任务，规模为 O(h)。'],
 'pitfalls':['先压孩子再压根 True，会让根立刻弹出，退化为前序。','True 分支忘记跳过展开逻辑，导致同一节点反复处理。','仅反转前序“根左右”得到“右左根”，不是后序；若使用反转技巧，必须先产生“根右左”。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，输出列表 O(n)。',
 'quiz':{'question':'如果每个节点要返回高度，应在哪个分支计算？','answer':'在 expanded=True 的分支；此时左右孩子都已经处理完，可以读取它们的高度并取较大值加一。'},
 'tests':checks('postorderTraversal',[([SAMPLE],[4,5,2,6,3,1]),([[]],[]),([[0]],[0]),([[1,None,2,3]],[3,2,1])])
})

CHAPTER['problems'].append({
 'id':102,'slug':'binary-tree-level-order-traversal',
 'summary':'返回按深度分组的节点值；每层从左到右，结果是二维列表。',
 'baseline':'DFS 带深度参数也能把值放到对应层，时间 O(n)。BFS 的队列天然按深度递增处理，关键是把连续队列流划分成独立层。',
 'insight':'一层开始时队列恰好保存这一层所有节点。冻结 size 后只弹 size 次，期间加入的孩子就完整留给下一层。',
 'steps':['空树返回 []；queue 初始只放 root。','保存 size=len(queue)，新建本层 level=[]。','弹出 size 个节点，记录值，按左、右顺序追加非空孩子。','把 level 加入 result，继续下一层。'],
 'invariant':'每层开始，队列按从左到右顺序保存同一深度的全部节点。先处理靠左父节点并按左→右加入孩子，会生成下一层从左到右的顺序；冻结次数保证不会把下一层提前弹出。',
 'examples':[{'label':'孩子属于下一轮','input':'root=[1,2,3,4,5,null,6]','output':'[[1],[2,3],[4,5,6]]','frames':[
  {'title':'第 1 层','note':'size=1，只弹根 1，孩子 2、3 留在队列。','diagram':TREE,'metrics':[['本层','[1]'],['下一层队列','[2,3]']]},
  {'title':'第 2 层冻结 size=2','note':'处理 2 后队列变成 [3,4,5]，但本层仅剩一次弹出。','table':{'headers':['弹出节点','本层结果','队列'],'rows':[[2,'[2]','[3,4,5]'],[3,'[2,3]','[4,5,6]']]}},
  {'title':'第 3 层','note':'重新取 size=3，输出三个叶子，队列变空。','table':{'headers':['深度','值'],'rows':[[1,'[1]'],[2,'[2,3]'],[3,'[4,5,6]']]}}
 ]}],
 'walkthrough':['处理 2 时产生的 4、5 已经在队列中，但它们排在尚未处理的同层节点 3 后面。','for range(size) 的次数在进入循环前确定，因此本轮队列长度变化不会改变层边界。','每层都创建新 level，避免多个结果引用同一个被清空或继续追加的列表。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        if root is None:
            return []
        # 队列先进先出，先处理完当前层，再处理刚加入的下一层。
        queue = deque([root])
        result = []
        while queue:
            # 固定本层节点数，不能把内循环中新加入的孩子也算入本层。
            size = len(queue)
            # 每层创建独立列表，避免多层结果共享同一个容器。
            level = []
            for _ in range(size):
                node = queue.popleft()
                level.append(node.val)
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
            result.append(level)
        return result
'''.strip(),
 'code_notes':['range(size) 只控制弹出本层节点，不需要保存每个节点的深度。','popleft 对应先进先出，换成 pop 会改成深度优先。','None 孩子不进入本题的队列，因为输出只包含真实节点。'],
 'pitfalls':['用 while queue 作为内部层循环，会把所有层混在一起。','使用 list.pop(0) 反复搬移元素，宽树上容易产生额外开销。','复用一个 level 对象收集所有层。'],
 'complexity':'时间 O(n)，队列辅助空间 O(w)，输出 O(n)。队列可能同时包含本层剩余节点和下一层部分节点，但数量仍为 O(w)。',
 'quiz':{'question':'处理第二层时队列出现三个元素，是否说明第二层有三个节点？','answer':'不说明。队列中可能已经混入下一层孩子；本层数量以开始时冻结的 size=2 为准。'},
 'tests':checks('levelOrder',[([SAMPLE],[[1],[2,3],[4,5,6]]),([[]],[]),([[0]],[[0]]),([[1,None,2,3]],[[1],[2],[3]])])
})

CHAPTER['problems'].append({
 'id':103,'slug':'binary-tree-zigzag-level-order-traversal',
 'summary':'从根层开始交替输出方向：第一层左到右，第二层右到左，第三层左到右，依次交替。',
 'baseline':'每层都改变孩子入队顺序并不容易保持正确。队列中不同父节点的先后关系也会影响下一层，单纯交换 left/right 的追加顺序无法统一解决。',
 'insight':'保持 BFS 队列始终从左到右，只改变本层结果写入的位置。若当前方向向右，写 index=i；若反向，写 index=size-1-i。这样遍历过程与展示方向分开，层边界仍沿用 102。',
 'steps':['队列初始化根，left_to_right=True。','每层新建长度为 size 的列表。','从左到右弹出节点，根据方向计算该值在列表中的位置。','孩子始终按左、右入队；层结束保存列表并切换方向。'],
 'invariant':'队列的节点顺序始终与普通层序一致。对一层的第 i 个节点，反向位置 size-1-i 恰好把顺序一一逆转，不重复、不遗漏；方向只在完整一层结束后翻转。',
 'examples':[{'label':'只改变写入位置','input':'root=[1,2,3,4,5,null,6]','output':'[[1],[3,2],[4,5,6]]','frames':[
  {'title':'根层正向','note':'1 写入下标 0；下一层队列仍为 [2,3]。','diagram':TREE,'metrics':[['方向','左→右']]},
  {'title':'第二层反向写入','note':'节点 2 先弹出，但写到下标 1；节点 3 后弹出，写到下标 0。','table':{'headers':['弹出顺序 i','值','写入下标','level'],'rows':[[0,2,1,'[空,2]'],[1,3,0,'[3,2]']]}},
  {'title':'第三层恢复正向','note':'孩子一直按普通顺序排队，所以直接得到 [4,5,6]。','array':[4,5,6],'active':[0,1,2]}
 ]}],
 'walkthrough':['第二层的输出 [3,2] 并不表示先从队列弹出 3；代码实际仍然先处理 2。','每个输出位置都是唯一的，因此预分配中的 0 会全部被覆盖；树节点本身为 0 也没有歧义。','也可以先收集普通 level，再对隔层执行 level.reverse()，整棵树总反转成本仍然 O(n)。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        if root is None:
            return []
        queue = deque([root])
        result = []
        # 只改变当前层的写入方向，队列仍按正常从左到右扩展。
        left_to_right = True
        while queue:
            size = len(queue)
            # 预分配这一层的结果，反向时按对应下标写入，不做头部插入。
            level = [0] * size
            for i in range(size):
                node = queue.popleft()
                # 正向写 i，反向写 size-1-i，实现锯齿顺序。
                index = i if left_to_right else size - 1 - i
                level[index] = node.val
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
            result.append(level)
            # 这一层结束后，切换下一层的方向。
            left_to_right = not left_to_right
        return result
'''.strip(),
 'code_notes':['条件表达式根据当前层方向选择整数下标，不修改队列。','方向翻转放在 for 循环之后，每层只翻转一次。','level 包含整数，使用 [0]*size 不会出现共享可变子列表的问题。'],
 'pitfalls':['每处理一个节点就翻转方向。','同时反转队列和输出位置，导致重复反转。','以为 size-1-i 是树节点下标；它只是本层结果的位置。'],
 'complexity':'时间 O(n)，辅助空间 O(w)，输出 O(n)。',
 'quiz':{'question':'只有一个节点的一层需要切换方向吗？','answer':'需要。虽然单节点这一层正反输出相同，下一层的方向仍取决于层数奇偶。'},
 'tests':checks('zigzagLevelOrder',[([SAMPLE],[[1],[3,2],[4,5,6]]),([[]],[]),([[0]],[[0]]),([[1,2,3,4,None,None,5]],[[1],[3,2],[4,5]])])
})

CHAPTER['problems'].append({
 'id':199,'slug':'binary-tree-right-side-view',
 'summary':'从树的右侧观察，返回每个深度最右边的真实节点值，从上到下排列。它不等于不断沿 root.right 行走。',
 'baseline':'先执行完整层序再取每层最后一项能够解决，但保存所有层包含不需要的输出。可以在 BFS 过程中只记录每层最后弹出的节点。',
 'insight':'普通层序按左到右处理。冻结一层 size 后，当 i=size-1 时，当前节点就是本层最右节点，无论它属于根的左子树还是右子树。',
 'steps':['空树返回 []；队列保存根。','冻结 size，按普通层序弹出并追加左右孩子。','当本层处理到最后一个节点时记录值。','下一层重复，得到每个深度一个答案。'],
 'invariant':'每层队列顺序是从左到右；最后一个真实节点右边没有同层节点遮挡，因此可见。下一层重新独立选择最右节点，不依赖上一层可见节点是否拥有孩子。',
 'examples':[{'label':'右子树结束后，左边深处仍可见','input':'root=[1,2,3,4]','output':'[1,3,4]','frames':[
  {'title':'右边的 3 没有孩子','note':'第三层只有左子树里的 4，它也能从右侧看到。','diagram':'    1\n   / \\\n  2   3\n /\n4'},
  {'title':'逐层选择最后一项','note':'每层重新考虑所有节点，不能只延续上一层的右孩子。','table':{'headers':['层','从左到右','记录'],'rows':[[1,'[1]',1],[2,'[2,3]',3],[3,'[4]',4]]}},
  {'title':'形成右视图','note':'4 不在根的右链上，但它是最深层唯一节点。','array':[1,3,4],'active':[2]}
 ]}],
 'walkthrough':['根层只有 1，所以记录 1；第二层 2、3 中记录最后的 3；第三层仅有 4，记录 4。','右视图保留的是每层位置极值，不是最大数值。把节点值改成负数或重复值不影响选择规则。','也可用优先访问右子树的 DFS，每个深度只记录第一次遇见的节点；本章主解复用层序模板。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> list[int]:
        if root is None:
            return []
        queue = deque([root])
        result = []
        while queue:
            # 每轮只读取当前层的固定节点数。
            size = len(queue)
            for i in range(size):
                node = queue.popleft()
                # 孩子按先左后右入队，因此本层最后弹出的节点从右边可见。
                if i == size - 1:
                    result.append(node.val)
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
        return result
'''.strip(),
 'code_notes':['size 在入孩子前固定，i==size-1 才能稳定表示最后一个。','结果列表只存每层一项，没有保存完整二维层序。','左右入队顺序必须与“记录最后一项”的约定一致。'],
 'pitfalls':['只沿 right 走会漏掉左子树更深的层。','取 max(level) 会把位置问题误解成数值问题。','右先入队时仍记录最后节点，会得到左视图。'],
 'complexity':'时间 O(n)，队列辅助空间 O(w)，输出空间 O(h)。',
 'quiz':{'question':'把入队顺序改成右、左后，该记录每层哪一项才能保持右视图？','answer':'应记录第一项，因为此时本层从右向左处理。必须同时调整选择规则。'},
 'tests':checks('rightSideView',[([[1,2,3,4]],[1,3,4]),([SAMPLE],[1,3,6]),([[]],[]),([[0]],[0])])
})

CHAPTER['problems'].append({
 'id':958,'slug':'check-completeness-of-a-binary-tree',
 'summary':'判断二叉树是否完全：除最后一层外每层填满，最后一层的节点从左向右连续排列，中间不能留空位。',
 'baseline':'给节点按完全二叉树数组规则编号，检查最大编号是否等于节点数，也可以判断；但偏斜树的编号会指数增长。直接观察 BFS 中空位置与非空节点的先后关系更直观。',
 'insight':'完全二叉树的层序位置序列一定先出现全部非空节点，随后全部为空。一旦遇到第一个 None，之后若又遇到真实节点，就说明存在一个更靠后的节点越过了空位。',
 'steps':['把 root 入队，gap=False。','弹出 None 时设置 gap=True，不再为这个空位加入孩子。','弹出真实节点时，若 gap 已经为 True，立即返回 False。','否则将它的 left、right 都加入队列，包含 None。','队列耗尽且没有违反条件，返回 True。'],
 'invariant':'gap 表示已处理的层序位置中是否出现空位。gap=False 时当前非空前缀连续；gap=True 后只允许空位置。所有真实节点的左右位置都被按序加入，任何缺口后的真实节点最终都会被发现。',
 'examples':[{'label':'缺左孩子却有右孩子','input':'root=[1,2,3,4,5,null,6]','output':'False','frames':[
  {'title':'树的第三层出现内部空位','note':'3.left 缺失，但其右孩子 6 仍存在。','diagram':TREE},
  {'title':'读到第一个 None','note':'处理完 1、2、3、4、5，随后读到 3 的左侧空位，gap=True。','array':[1,2,3,4,5,'None',6],'active':[5],'pointers':{'当前':5}},
  {'title':'空位后再次出现 6','note':'6 是真实节点且 gap 已经置位，立即返回 False。','array':[1,2,3,4,5,'None',6],'active':[6]}
 ]},{'label':'最后一层只缺最右端','input':'root=[1,2,3,4,5,6]','output':'True','frames':[
  {'title':'真实节点连续出现','note':'第一个空位是 3.right；后续所有出队项也是 None。','diagram':'    1\n   / \\\n  2   3\n / \\ /\n4  5 6'},
  {'title':'空位以后没有真实节点','note':'序列满足“非空前缀 + 全空后缀”，完全性成立。','array':[1,2,3,4,5,6,'None','None','…'],'active':[6,7,8]}
 ]}],
 'walkthrough':['普通层序会跳过 None，但本题正是要检查缺失位置，所以必须保留真实节点的两个孩子位置。','空位置本身不能继续产生两个空孩子，否则队列永远不会结束。','完全二叉树不要求每个节点有两个孩子，也不要求最后一层填满；关键是空位只能集中在末尾。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isCompleteTree(self, root: Optional[TreeNode]) -> bool:
        queue = deque([root])
        # gap 表示层序遍历中是否已经出现第一个空位置。
        gap = False
        while queue:
            node = queue.popleft()
            # 空孩子也必须入队，否则会丢失树中间缺位置的信息。
            if node is None:
                gap = True
                continue
            # 出现空位后又出现非空节点，就不满足完全二叉树从左填满的要求。
            if gap:
                return False
            queue.append(node.left)
            queue.append(node.right)
        return True
'''.strip(),
 'code_notes':['node is None 区分空节点与值为 0 的真实节点。','遇到空位只设置状态，不立即返回 False，因为尾部空位完全合法。','题目保证非空；代码对空树也返回 True，与通常的完全性定义一致。'],
 'pitfalls':['将“完全”误解为“满”，错误拒绝最后一层未填满的树。','入队时过滤 None，会丢掉要验证的缺口。','发现任何 None 都立即失败，几乎所有有限树都会被误判。'],
 'complexity':'时间 O(n)，真实节点各出队一次，每个真实节点最多产生两个孩子位置；辅助队列 O(w)，最坏 O(n)。',
 'quiz':{'question':'root=[1,null,2] 是否完全？','answer':'不是。根的左位置先出现空位，后面还有真实右孩子 2，违反最后一层必须从左连续排列。'},
 'tests':checks('isCompleteTree',[([SAMPLE],False),([[1,2,3,4,5,6]],True),([[1,None,2]],False),([[1,2]],True),([[0]],True),([[]],True)])
})

CHAPTER['problems'].append({
 'id':104,'slug':'maximum-depth-of-binary-tree',
 'summary':'求从根到最远叶子的路径上节点数量。空树深度为 0，只有根的树深度为 1；这里统计节点数，不是边数。',
 'baseline':'层序遍历每完成一层就加一，也能得到答案。DFS 则把当前路径的深度一起压栈，直接对所有遇到的深度取最大值，不需要保存完整路径。',
 'insight':'根的深度为 1，孩子深度恒为父深度加一。每个节点只有一个父节点，因此沿唯一的根到节点路径传播深度即可。等价的子树方程是 H(node)=1+max(H(left),H(right))，但主解采用向下传递，避免长链上的递归深度问题。',
 'steps':['空树返回 0；stack=[(root,1)]，best=0。','弹出节点和深度，用 depth 更新 best。','将非空孩子与 depth+1 一起压栈。','遍历结束返回最大深度。'],
 'invariant':'每个栈帧保存的 depth 都等于真实根到该节点的节点数：根初值正确，每条父子边使数量恰好多一。best 是所有已处理节点的最大深度，最终覆盖全部节点，其中最深节点必是叶子。',
 'examples':[{'label':'深度计节点数','input':'root=[1,2,3,4,5,null,6]','output':'3','frames':[
  {'title':'根从 1 开始','note':'空树才是 0；非空根所在层是第 1 层。','diagram':TREE,'metrics':[['当前节点',1],['depth',1],['best',1]]},
  {'title':'进入 2，再进入 4','note':'每跨一条父子边，携带的深度增加一。','table':{'headers':['节点','路径','深度'],'rows':[[1,'1',1],[2,'1→2',2],[4,'1→2→4',3]]}},
  {'title':'其他分支最多也是 3','note':'1→2→5 与 1→3→6 都有 3 个节点，最终 best=3。','array':[1,2,4],'active':[0,1,2],'array_label':'一条达到最大深度的路径'}
 ]}],
 'walkthrough':['在示例中根到 4 只有两条边，却有三个节点；把根深度设为 0 会整体少一。','到达 4 后，栈里的 5、3 仍各自携带正确深度，不需要一个全局 depth 加减来模拟回退。','节点上有负数、重复值或者零都不影响深度，因为只看连接关系。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        best = 0
        # 栈项保存节点与它的深度，根节点深度为 1。
        stack = [(root, 1)]
        while stack:
            node, depth = stack.pop()
            # 每个节点只看一次，记录经过的最大深度。
            best = max(best, depth)
            if node.right is not None:
                # 孩子深度为父亲深度加一；显式栈不受 Python 递归深度限制。
                stack.append((node.right, depth + 1))
            if node.left is not None:
                stack.append((node.left, depth + 1))
        return best
'''.strip(),
 'code_notes':['每个帧的 depth 是独立整数，处理另一分支时不会被当前分支修改。','不必只在叶子更新 best，因为任何内部节点的深度都不超过其后代。','max 接收两个整数并返回较大值，不会原地更新变量，所以写 best=max(...)。'],
 'pitfalls':['把深度定义成边数。','用一个 depth 变量每弹出节点就加一，结果变成处理节点数。','认为树一定平衡，忽略题目允许退化长链。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，最坏 O(n)；不保存输出路径。',
 'quiz':{'question':'同一棵树用向下深度与向上高度计算，最终答案是否相同？','answer':'相同。最大根到节点深度等于以根为起点的子树高度；不同的是状态传播方向和计算时机。'},
 'tests':checks('maxDepth',[([SAMPLE],3),([[]],0),([[0]],1),([[1,None,2,None,3]],3)])
})

CHAPTER['problems'].append({
 'id':110,'slug':'balanced-binary-tree',
 'summary':'判断每个节点的左右子树高度差是否都不超过 1。只检查根的两边高度不足以判断整棵树平衡。',
 'baseline':'对每个节点单独从头计算左右高度会重复遍历后代，偏斜情况下可达到 O(n²)。后序让孩子高度计算一次、直接交给父节点，能把总时间降到 O(n)。',
 'insight':'先获得左右高度 L、R：若 abs(L-R)>1，整棵树立刻不平衡；否则当前高度是 1+max(L,R)。用后序的展开标记等待孩子，height 表暂存已完成子树的返回值。',
 'steps':['空树返回 True；将根的未展开帧入栈。','遇到未展开帧，安排根的完成帧及左右孩子。','完成帧读取并删除孩子高度，空孩子取 0。','高度差超过 1 立即 False；否则保存当前高度。','全部节点通过检查，返回 True。'],
 'invariant':'一个节点进入完成阶段时，孩子已经通过平衡检查，且对应高度正确。再验证当前高度差即可证明以它为根的整棵子树平衡。任何节点失败都意味着全树不满足“每个节点”的要求。',
 'examples':[{'label':'从叶子向上汇总','input':'root=[1,2,null,3]','output':'False','frames':[
  {'title':'根下方是一条左链','note':'先等到叶子 3 完成，再回到 2，最后判断 1。','diagram':'1\n/\n2\n/\n3'},
  {'title':'叶子 3 高度为 1','note':'两个空孩子高度均为 0，高度差 0。','table':{'headers':['完成节点','L','R','高度','平衡'],'rows':[[3,0,0,1,'是'],[2,1,0,2,'是']]}},
  {'title':'根的高度差为 2','note':'L=2、R=0，差值超过 1，返回 False。','table':{'headers':['完成节点','L','R','差值','结论'],'rows':[[1,2,0,2,'不平衡']]}}
 ]}],
 'walkthrough':['节点 2 本身通过检查，不代表其祖先 1 也会通过；每个节点都需要比较两边高度。','读取 height.pop(child,0) 后删除孩子结果，是因为孩子只有当前这个父节点，未来不会再次需要这个高度。','同时存活的高度值对应正在等待汇总的祖先的已完成兄弟子树，因此与 DFS 栈一起占 O(h)，不需要保留全树的高度表。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        if root is None:
            return True
        # 保存已经处理完子树的高度，空子树默认高度为 0。
        height = {}
        # 用“进入/返回”标记模拟后序，保证先算孩子再算父亲。
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
            else:
                # 孩子高度只被父亲使用一次，读取后移除以释放已经完成的状态。
                left = height.pop(node.left, 0)
                right = height.pop(node.right, 0)
                # 任一节点两侧高度差超过 1，整棵树就不平衡。
                if abs(left - right) > 1:
                    return False
                # 子树高度为较高孩子加当前节点这一层。
                height[node] = 1 + max(left, right)
        return True
'''.strip(),
 'code_notes':['height 的键是节点对象，重复数值不会相互覆盖。','abs(left-right) 检查左右任何一侧过高的情况。','提前返回 False 不会破坏输入树，因为栈和高度表都是局部辅助状态。'],
 'pitfalls':['只比较根的左右高度。','每次汇总重新遍历整棵孩子子树，造成重复工作。','用 node.val 作为高度表键，重复值时误取别的节点结果。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，最坏 O(n)。高度值在父节点使用后被删除；若改为全部保留，字典空间就会变成 O(n)。',
 'quiz':{'question':'左右子树高度都为 4，能立刻判断整棵树平衡吗？','answer':'不能，还必须保证左右子树内部每个节点也满足高度差条件。后序检查把这一条件包含在孩子已通过的结论里。'},
 'tests':checks('isBalanced',[([[1,2,None,3]],False),([[3,9,20,None,None,15,7]],True),([[1,2,2,3,3,None,None,4,4]],False),([[]],True),([[0]],True)])
})

CHAPTER['problems'].append({
 'id':226,'slug':'invert-binary-tree',
 'summary':'对每个节点交换左右子树，原地翻转整棵二叉树，返回原根节点。仅交换根的两个孩子不能完成整树翻转。',
 'baseline':'新建一棵镜像树也能表达结果，但需要 O(n) 新节点。题目允许修改连接，可以在原节点上交换 left、right，每个节点做一次常数操作。',
 'insight':'一棵树的镜像等于：根保持不变，原右子树的镜像放到左边，原左子树的镜像放到右边。因此局部交换必须在全部节点上执行。DFS 栈负责确保每个节点都得到处理。',
 'steps':['空树返回 None；栈中放根。','弹出节点，以同时赋值交换左右孩子引用。','把交换后的两个非空孩子加入栈，继续翻转它们内部。','返回 root。'],
 'invariant':'已处理节点的左右引用已互换，未处理节点保持原局部连接。交换不会创建或丢弃节点，只改变同一对孩子的方向；栈仍包含所有未完成子树入口，最终每个节点恰好交换一次。',
 'examples':[{'label':'每个分叉都要交换','input':'root=[4,2,7,1,3,6,9]','output':'[4,7,2,9,6,3,1]','frames':[
  {'title':'原树','note':'根下面有两个独立子树，先交换它们的位置。','diagram':'    4\n   / \\\n  2   7\n / \\ / \\\n1  3 6  9'},
  {'title':'只交换根仍未完成','note':'7 内部还是左 6、右 9，2 内部还是左 1、右 3，都需要继续交换。','diagram':'    4\n   / \\\n  7   2\n / \\ / \\\n6  9 1  3'},
  {'title':'全部分叉翻转','note':'最终左边是 7 的镜像，右边是 2 的镜像，节点值未改。','diagram':'    4\n   / \\\n  7   2\n / \\ / \\\n9  6 3  1'}
 ]}],
 'walkthrough':['交换根的两个引用会移动整个子树入口，子树内部暂时没有变化，所以必须继续深入。','叶子的 left、right 都是 None，交换后仍然是 None，统一处理即可。','再次翻转最终树应恢复原树的全部连接，这是一个很好的验证性质。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if root is None:
            return None
        stack = [root]
        while stack:
            node = stack.pop()
            # 每个节点交换自己的左右孩子，递归意义上的左右子树也会逐个交换。
            node.left, node.right = node.right, node.left
            if node.right is not None:
                # 把交换后的非空孩子继续送入栈，确保每个节点都处理一次。
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
        return root
'''.strip(),
 'code_notes':['同时赋值先计算右侧两个原引用，再写入左侧，不会因先覆盖一个孩子而丢失它。','返回 root 是原来的根对象；它的后代连接发生变化。','栈中压入交换后的孩子即可，因为无论左右顺序如何，每棵子树都必须翻转。'],
 'pitfalls':['只交换根，不继续处理后代。','依次写 node.left=node.right、node.right=node.left，会让两边都指向原右孩子。','交换节点值不能替代交换子树结构。'],
 'complexity':'时间 O(n)，辅助栈 O(h)，复用全部原节点，没有创建镜像结果节点。',
 'quiz':{'question':'原树只有左孩子时，翻转后应怎样？','answer':'该孩子变成右孩子，原左引用变成 None；孩子自己的子树也要继续翻转。'},
 'tests':{'adapter':'tree','method':'invertTree','result':'tree','reuse_nodes':True,'cases':[{'args':[[4,2,7,1,3,6,9]],'expected':[4,7,2,9,6,3,1]},{'args':[[]],'expected':[]},{'args':[[0]],'expected':[0]},{'args':[[1,2,None,3]],'expected':[1,None,2,None,3]}]}
})

CHAPTER['problems'].append({
 'id':101,'slug':'symmetric-tree',
 'summary':'判断一棵树是否沿根的竖直中轴镜像对称，既要求对应位置的值相等，也要求空孩子的位置对应。',
 'baseline':'每层仅收集非空值再判断回文会漏掉结构。例如 [1,2,2,null,3,null,3] 每层非空值都像回文，但两侧的 3 都在各自右边，并不互为镜像。',
 'insight':'成对比较镜像位置 a、b：两者都空则匹配，只有一空则失败，数值不同也失败。都非空且值相同后，继续比较外侧 a.left 与 b.right、内侧 a.right 与 b.left。',
 'steps':['空树返回 True；队列初始化 (root.left,root.right)。','弹出镜像位置对，处理两空、一空和值不等。','若匹配，把外侧与内侧两个位置对加入队列。','所有位置对都匹配则 True。'],
 'invariant':'队列里每一对节点占据关于根轴对称的位置。根的两个孩子满足此位置关系；从一对位置向外或向内走一步仍然形成镜像位置。检查所有位置的空实与数值，就能完整判断镜像。',
 'examples':[{'label':'相同数值不代表相同形状','input':'root=[1,2,2,null,3,null,3]','output':'False','frames':[
  {'title':'两个 3 都是右孩子','note':'左边 2 的右孩子应当对应右边 2 的左孩子，但右边这个位置为空。','diagram':'    1\n   / \\\n  2   2\n   \\   \\\n    3   3'},
  {'title':'先比较两个 2','note':'值相同，只能说明这一对通过；还要继续比较孩子位置。','table':{'headers':['比较项','左位置','右镜像位置','结论'],'rows':[['当前根',2,2,'继续'],['外侧','None',3,'失败'],['内侧',3,'None','也不匹配']]}},
  {'title':'结构不同，返回 False','note':'把空位丢弃就无法发现这一错误。','array':['None',3,'None',3],'active':[0,3]}
 ]}],
 'walkthrough':['合法对称树 [1,2,2,3,4,4,3] 中，外侧 3 对 3，内侧 4 对 4，两对都匹配。','比较的是镜像位置，因此不能把 a.left 与 b.left 配对；那是在比较两棵树同方向是否相同。','两个位置都空意味着该分支已经匹配完成，不再产生新的比较任务。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        if root is None:
            return True
        # 队列每项是一对应该互为镜像的节点。
        queue = deque([(root.left, root.right)])
        while queue:
            a, b = queue.popleft()
            # 两个位置同时为空才相互对称。
            if a is None and b is None:
                continue
            # 仅一边为空或值不同，立即判定不对称。
            if a is None or b is None or a.val != b.val:
                return False
            # 比较外侧与外侧、内侧与内侧，不能把相同方向的孩子配在一起。
            queue.append((a.left, b.right))
            queue.append((a.right, b.left))
        return True
'''.strip(),
 'code_notes':['or 短路保证只有 a、b 都非空时才读取两者的 val。','比较值使用 !=；空对象使用 is None，含义不同。','队列保存一对位置，空位置仍保留以比较结构。'],
 'pitfalls':['只比较每层非空值是否回文。','把左右子树当成同方向结构比较。','在确认节点存在之前访问 .val。'],
 'complexity':'时间 O(n)，队列辅助空间 O(w)，最坏 O(n)。',
 'quiz':{'question':'左右子树根值都为 2，但一边缺孩子，另一边对应位置有值为 0 的节点，是否匹配？','answer':'不匹配。0 是真实节点，None 是缺失位置，结构已经不同。'},
 'tests':checks('isSymmetric',[([[1,2,2,None,3,None,3]],False),([[1,2,2,3,4,4,3]],True),([[]],True),([[0]],True),([[1,0,None]],False)])
})

CHAPTER['problems'].append({
 'id':543,'slug':'diameter-of-binary-tree',
 'summary':'求任意两个节点间最长简单路径的边数。路径可以不经过根，也可以只包含一个节点，此时边数为 0。',
 'baseline':'枚举每对节点并寻找路径会做大量重复工作。任意路径都有一个离根最近的转折节点，围绕这个节点把路径拆成左、右两臂，就能逐节点计算候选。',
 'insight':'若左右子树高度按节点数记为 L、R，经过当前节点的最长路径边数恰好是 L+R。传给父节点的高度则是 1+max(L,R)，因为向上延伸的路径只能选择一条臂。',
 'steps':['空树返回 0；后序计算孩子高度。','节点完成时取出 L、R，更新 best=max(best,L+R)。','保存当前高度 1+max(L,R)，供父节点使用。','返回全局 best。'],
 'invariant':'后序保证 L、R 是对应子树可向下延伸的最大节点数。任何路径都有唯一最高转折点，在该点的左右两臂长度之和不超过 L+R；遍历所有节点取最大值，覆盖所有可能的最高转折点。',
 'examples':[{'label':'返回高度，更新边数','input':'root=[1,2,3,4,5]','output':'3','frames':[
  {'title':'候选路径 4→2→1→3','note':'这条路径有四个节点、三条边，题目返回 3。','diagram':'    1\n   / \\\n  2   3\n / \\\n4   5'},
  {'title':'节点 2 的两种数值不同','note':'L=R=1，经过 2 的候选边数是 2，返回给 1 的高度也是 2，但公式含义不同。','table':{'headers':['节点','L','R','候选 L+R','返回高度'],'rows':[[4,0,0,0,1],[5,0,0,0,1],[2,1,1,2,2]]}},
  {'title':'根汇总得到直径 3','note':'根左高度 2、右高度 1，候选 3 更新全局答案。','table':{'headers':['节点','L','R','候选','全局 best'],'rows':[[3,0,0,0,2],[1,2,1,3,3]]}}
 ]}],
 'walkthrough':['子树高度按节点数计算，连接当前节点到该子树最深叶子时，边数恰好等于这个高度，因此两臂候选不再额外加一。','当前高度不能写成 L+R+1，否则传给父节点的是一条已经分叉的路径，无法再合法地接到父节点。','只返回根处的候选会漏掉整条最长路径位于某个内部子树的情况，因此需要独立维护 best。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        # 高度按节点数记录，直径按边数记录，二者不能混淆。
        height = {}
        best = 0
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            # 先安排左右子树，返回当前节点时孩子高度才已知。
            if not expanded:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
            else:
                left = height.pop(node.left, 0)
                right = height.pop(node.right, 0)
                # 经过当前节点的最长路径有 left+right 条边，不再额外加一。
                best = max(best, left + right)
                # 向父亲返回的是单侧高度，只能选择更高的那个孩子。
                height[node] = 1 + max(left, right)
        return best
'''.strip(),
 'code_notes':['best 初始为 0，兼容空树或单节点。','height.pop 在父节点使用后释放孩子结果，避免保存全部历史高度。','代码不记录路径本身，只计算长度，因为题目没有要求返回节点序列。'],
 'pitfalls':['把答案写成 L+R+1，混淆节点数与边数。','把双臂长度当成传给父节点的高度。','只在根处更新答案。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，最坏 O(n)。',
 'quiz':{'question':'单节点树的高度与直径分别是多少？','answer':'高度为 1，直径为 0。高度计根到叶的节点数，直径计路径边数。'},
 'tests':checks('diameterOfBinaryTree',[([[1,2,3,4,5]],3),([SAMPLE],4),([[]],0),([[0]],0),([[1,None,2,None,3]],2)])
})

CHAPTER['problems'].append({
 'id':98,'slug':'validate-binary-search-tree',
 'summary':'判断整棵树是否满足严格 BST：每个节点的全部左后代都小于它，全部右后代都大于它。相等值不允许。',
 'baseline':'只比较当前节点与直接孩子会漏掉祖先约束。例如根 5 的右孩子 7 有左孩子 4，4<7 没问题，但 4 位于 5 的右子树，必须同时满足 4>5。',
 'insight':'给每棵子树携带一个由全部祖先共同确定的开区间 (low,high)。当前值必须落在区间内；左孩子继承 low 并将 high 缩小为当前值，右孩子继承 high 并将 low 提高为当前值。',
 'steps':['根的区间初始化为负无穷到正无穷。','弹出 (node,low,high)，检查 low<node.val<high。','左孩子携带 (low,node.val)，右孩子携带 (node.val,high)。','任何节点越界立即 False，否则遍历结束 True。'],
 'invariant':'每个栈帧的区间是其所有祖先对该位置约束的交集。左转增加上界，右转增加下界，原有另一侧边界保留，因此不会丢失更高祖先的限制。全体节点通过区间检查正好等价于严格 BST 定义。',
 'examples':[{'label':'直接父子合法，祖先关系非法','input':'root=[5,1,7,null,null,4,8]','output':'False','frames':[
  {'title':'4 落在根 5 的右子树','note':'虽然 4<7，仍然违反整个右子树都大于 5 的要求。','diagram':'    5\n   / \\\n  1   7\n     / \\\n    4   8'},
  {'title':'携带祖先留下的范围','note':'到 7 时下界已是 5；进入 7 的左孩子只把上界改成 7。','table':{'headers':['节点','必须满足','是否通过'],'rows':[[5,'-∞ < 5 < +∞','是'],[7,'5 < 7 < +∞','是'],[4,'5 < 4 < 7','否']]}},
  {'title':'错误在数值 4，不在父子比较','note':'不能把左孩子区间重置成 (-∞,7)，那会丢掉根的限制。','array':[5,4,7],'active':[1],'array_label':'要求 4 应落在开区间 (5,7)，实际不满足'}
 ]}],
 'walkthrough':['每次只更新一个边界，另一边来自更早的祖先。这个“继承”是上下界法的核心。','边界必须严格，小于等于的写法会错误接受重复值，例如 [2,2,3]。','另一种等价方法是沿中序遍历检查值严格递增；单次查询主解可以选任一种，不需要先排序掩盖结构错误。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        if root is None:
            return True
        # 每个节点继承所有祖先给出的开区间 (low,high)。
        stack = [(root, float('-inf'), float('inf'))]
        while stack:
            node, low, high = stack.pop()
            # 必须严格在范围内；BST 不允许相等值，也不只检查直接父子。
            if not low < node.val < high:
                return False
            if node.right is not None:
                # 右子树下界提高到当前值，上界仍继承祖先限制。
                stack.append((node.right, node.val, high))
            if node.left is not None:
                # 左子树上界降低到当前值，下界仍继承祖先限制。
                stack.append((node.left, low, node.val))
        return True
'''.strip(),
 'code_notes':['Python 链式比较 low<x<high 同时验证两个严格不等式。','无穷边界不会与题目允许的最小、最大整数冲突。','范围只存在于栈帧，输入节点与结构保持不变。'],
 'pitfalls':['只比较直接孩子。','下降时重置另一侧界限。','允许相等值，或用一个合法整数作排他边界而误伤极值。'],
 'complexity':'时间 O(n)，辅助栈 O(h)，最坏 O(n)。',
 'quiz':{'question':'[2,1,2] 是否是本题认可的 BST？','answer':'不是。右子树必须严格大于根，右孩子与根相等违反条件。'},
 'tests':checks('isValidBST',[([[5,1,7,None,None,4,8]],False),([[2,1,3]],True),([[2,1,2]],False),([[-2147483648,None,2147483647]],True),([[]],True)])
})

CHAPTER['problems'].append({
 'id':230,'slug':'kth-smallest-element-in-a-bst',
 'summary':'给定合法 BST 和从 1 开始的排名 k，返回第 k 小的节点值。题目保证 1≤k≤节点数。',
 'baseline':'中序遍历收集所有值，再取 result[k-1] 正确，但保存了全部节点且不会提前结束。既然中序天然递增，输出到第 k 个时就已确定答案。',
 'insight':'复用 94 的迭代中序。每弹出并正式访问一个节点，k 减一；变为零时返回当前值。压栈只是等待左子树完成，不能在压栈时计排名。',
 'steps':['cur=root，stack=[]。','一路向左压栈，找到当前最小的未访问节点。','弹出，k 减一；若为零立即返回。','否则转入右子树，继续中序。'],
 'invariant':'每次弹出的节点是所有尚未输出节点中的最小值，因为它的左侧已完成，而右侧及更高祖先都更大。第 k 次输出因此恰好是全树第 k 小。',
 'examples':[{'label':'只需访问前三个排名','input':'root=[5,3,6,2,4,null,null,1], k=3','output':'3','frames':[
  {'title':'先沿左边压栈','note':'栈为 [5,3,2,1]，但此时没有任何节点获得访问排名。','diagram':'      5\n     / \\\n    3   6\n   / \\\n  2   4\n /\n1'},
  {'title':'逐次弹出才扣减 k','note':'1 是第一个，2 是第二个，3 是第三个。','table':{'headers':['访问值','原 k','减一后'],'rows':[[1,3,2],[2,2,1],[3,1,0]]}},
  {'title':'返回 3，停止遍历','note':'4、5、6 的排名更靠后，不必继续访问。','array':[1,2,3,4,5,6],'active':[2],'pointers':{'第3小':2}}
 ]}],
 'walkthrough':['虽然根 5 最先压栈，但它的排名不是 1；排名由中序弹出顺序决定。','提前退出只省去未访问部分，前往最左节点仍可能走 h 步，所以不能简单说时间总是 O(k)。','若树频繁更新且频繁查第 k 小，可在平衡搜索树节点维护子树大小，用左子树数量决定向哪边走。普通 BST 未必平衡，只有保证高度后才能承诺对数查询。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        stack = []
        cur = root
        while cur is not None or stack:
            # BST 的中序遍历按值从小到大，先走到当前最左节点。
            while cur is not None:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            # 每弹出一个节点，就消耗一个排名；重复操作不需要完整排序。
            k -= 1
            # 找到第 k 小后立即返回，不再遍历更大的节点。
            if k == 0:
                return cur.val
            cur = cur.right
        raise ValueError('k must be within the number of nodes')
'''.strip(),
 'code_notes':['返回整数 cur.val，而不是 TreeNode 对象。','不创建完整中序结果列表，直接消费访问次序。','末尾异常仅用于本地误传非法 k；题目有效输入一定会在循环里返回。'],
 'pitfalls':['压栈时扣减 k。','把从 1 开始的 k 当成列表下标。','忽略题目已保证 BST，反而额外排序全部值。'],
 'complexity':'时间 O(h+k)，最坏 O(n)；辅助栈 O(h)。',
 'quiz':{'question':'k=1 时，时间一定是 O(1) 吗？','answer':'不是。仍要沿左链找到最小节点，可能走 h 个节点；左偏长链中 h=n。'},
 'tests':checks('kthSmallest',[([[5,3,6,2,4,None,None,1],3],3),([[3,1,4,None,2],1],1),([[3,1,4,None,2],4],4),([[0],1],0)])
})

CHAPTER['problems'].append({
 'id':108,'slug':'convert-sorted-array-to-binary-search-tree',
 'summary':'把严格递增数组构造成高度平衡的 BST。答案不唯一：偶数长度时可以选两个中间值中的任一个作为根。',
 'baseline':'从小到大把值逐个插入普通 BST，会形成右链，既不平衡，构建时间也可能 O(n²)。应利用完整有序数组直接均匀划分左右子树。',
 'insight':'区间中点作根：中点左边的值全部更小，右边全部更大，天然满足 BST。左右区间长度最多相差一，并在每层继续平分，形成高度平衡结构。',
 'steps':['定义 build(left,right) 构造半开区间 nums[left:right]。','left>=right 表示空区间，返回 None。','mid=(left+right)//2，新建根 nums[mid]。','递归构造 [left,mid) 与 [mid+1,right) 并连接左右孩子。','返回根，初始调用 build(0,len(nums))。'],
 'invariant':'build 返回的树恰好包含对应区间元素，其中序等于原区间。递归保证两边各自是平衡 BST，中点分隔保证整体严格有序；按长度近乎均分产生的两边高度差不超过一。',
 'examples':[{'label':'中点分隔两个子问题','input':'nums=[-10,-3,0,5,9]','output':'一种合法结果：[0,-3,9,-10,null,5]','frames':[
  {'title':'根选择中点 0','note':'[0,5) 的 mid=2；左区间下标 [0,2)，右区间 [3,5)。','array':[-10,-3,0,5,9],'active':[2],'pointers':{'mid':2}},
  {'title':'左右长度都是 2','note':'本实现半开中点选择靠右的中间值，因此左根为 -3，右根为 9。','table':{'headers':['区间','mid','根'],'rows':[['[0,2)',1,-3],['[3,5)',4,9]]}},
  {'title':'单元素区间生成叶子','note':'最终中序仍为原有序数组，各节点左右高度差最多 1。','diagram':'     0\n    / \\\n  -3   9\n  /   /\n-10  5'}
 ]}],
 'walkthrough':['这次使用递归是因为每次区间减半，深度 O(log n)，不会像任意输入树那样退化到 O(n) 深。','传左右下标而不创建 nums[:mid] 切片，避免每层复制数组元素。','官方展示的另一种树也可能正确；验证构造题需要看有序性、平衡性和元素覆盖，不能只认一种层序形状。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def sortedArrayToBST(self, nums: list[int]) -> Optional[TreeNode]:
        def build(left: int, right: int) -> Optional[TreeNode]:
            # 使用左闭右开区间，空区间返回空子树。
            if left >= right:
                return None
            # 选中间值作根，使左右节点数尽量接近，保证高度平衡。
            mid = (left + right) // 2
            node = TreeNode(nums[mid])
            # 传下标范围而不切片，避免每层复制数组；中点不进入任何孩子。
            node.left = build(left, mid)
            node.right = build(mid + 1, right)
            return node

        return build(0, len(nums))
'''.strip(),
 'code_notes':['嵌套函数读取外层 nums，没有修改它，因此不需要 nonlocal。','中点已用作根，两个递归区间都必须排除 mid。','每个数组元素仅被选为根一次，恰好创建 n 个节点。'],
 'pitfalls':['按有序输入逐个插入导致链形结构。','递归右区间从 mid 开始，重复包含当前根甚至无法缩小。','把不同但合法的平衡形状误认为错误。'],
 'complexity':'时间 O(n)，递归辅助空间 O(log n)，新建的输出节点空间 O(n)。不切片，因此没有额外的区间数组复制。',
 'quiz':{'question':'nums=[1,3] 时根选 1 或 3，哪一个正确？','answer':'都正确。根 1 配右孩子 3，或根 3 配左孩子 1，都满足 BST 和高度平衡。本实现选 3。'},
 'tests':checks('sortedArrayToBST',[([[-10,-3,0,5,9]],[0,-3,9,-10,None,5]),([[1,3]],[3,1]),([[0]],[0]),([[]],[])],tree_args=[],result='tree',preserve_args=[0])
})

CHAPTER['problems'].append({
 'id':105,'slug':'construct-binary-tree-from-preorder-and-inorder-traversal',
 'summary':'给定同一棵树的前序和中序遍历，节点值互不相同，恢复这棵树。输入保证合法；返回新建根节点。',
 'baseline':'前序首值是根，在中序中找到根后可分割左右子树，递归构建。若每次用 index 线性查找并切片，偏斜输入可能 O(n²)；即便使用下标表优化，Python 递归仍可能遇到深树。',
 'insight':'前序决定新节点创建顺序，中序决定何时结束向左深入并返回祖先。栈保存等待完成中序访问的祖先，j 指向下一个应当中序访问的值。若栈顶值不等于 inorder[j]，下一前序值是它的左孩子；相等时连续弹出已到中序时机的祖先，下一值应接到最后弹出节点的右边。',
 'steps':['用 preorder[0] 创建根并压栈，j=0。','依次读取剩余前序值，创建新节点。','若栈顶还未到中序访问时机，接为栈顶左孩子。','否则持续弹出与 inorder[j] 匹配的栈顶并推进 j，把新节点接为最后弹出的节点的右孩子。','压入新节点，重复；返回根。'],
 'invariant':'已经创建的节点严格遵循前序，栈是其中尚未完成中序访问的祖先链。栈顶不匹配下一中序值说明左侧尚有节点；匹配时可以结束该节点左侧并访问它，连续匹配对应逐层返回。下一个前序节点属于最后返回祖先尚未开始的右子树。唯一值让匹配没有歧义。',
 'examples':[{'label':'中序告诉我们何时返回祖先','input':'preorder=[3,9,20,15,7]；inorder=[9,3,15,20,7]','output':'[3,9,20,null,null,15,7]','frames':[
  {'title':'建立 3，再把 9 接在左边','note':'栈顶 3 不等于下一个中序值 9，说明要继续向左。','diagram':'  3\n /\n9','metrics':[['stack','[3,9]'],['j',0]]},
  {'title':'处理 20 前连续弹出 9、3','note':'9 匹配 inorder[0]，3 匹配 inorder[1]；下一节点 20 接到最后弹出的 3 的右侧。','table':{'headers':['弹出','j 更新','下一中序值'],'rows':[[9,'0→1',3],[3,'1→2',15]]}},
  {'title':'15 接到 20 左边','note':'20 不等于当前中序值 15，所以继续进入左子树。','diagram':'    3\n   / \\\n  9  20\n     /\n    15'},
  {'title':'弹出 15、20，再接右孩子 7','note':'最后得到的前序与中序都必须与输入一致。','diagram':'    3\n   / \\\n  9  20\n     / \\\n    15  7'}
 ]}],
 'walkthrough':['创建 20 时不能只弹一次。如果仅弹出 9，就会把 20 错接成 9 的右孩子，而中序已明确 9 后紧接祖先 3。','while 中最后一个被弹出的节点就是下一右子树的父节点，必须保留该引用。','这不是“根据数值大小”构造 BST。3、9、20 的大小没有决定作用，依据是两个遍历的顺序。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def buildTree(self, preorder: list[int], inorder: list[int]) -> Optional[TreeNode]:
        if not preorder:
            return None
        root = TreeNode(preorder[0])
        # 栈保留尚未完成中序访问的祖先，j 指向下一个中序值。
        stack = [root]
        j = 0
        for i in range(1, len(preorder)):
            node = TreeNode(preorder[i])
            # 栈顶还没在中序遇到，新的前序节点仍属于它的左子树。
            if stack[-1].val != inorder[j]:
                stack[-1].left = node
            else:
                parent = stack.pop()
                j += 1
                # 连续弹出已经完成左侧访问的祖先，找到该连接右孩子的位置。
                while stack and stack[-1].val == inorder[j]:
                    parent = stack.pop()
                    j += 1
                # 新节点作为最后一个弹出祖先的右孩子。
                parent.right = node
            stack.append(node)
        return root
'''.strip(),
 'code_notes':['每个节点入栈、出栈最多一次，连续弹出总计 O(n)。','合法输入下创建新节点前最多弹出已创建的 i 个节点，j≤i<n，因此读取 inorder[j] 安全。','没有使用 preorder[1:] 切片，两个输入数组保持原样。'],
 'pitfalls':['只弹一个匹配节点，错接右子树。','把前序和中序当成数值排序信息。','忽略节点值唯一这一前提；有重复时值匹配不能唯一定位结构。'],
 'complexity':'时间 O(n)，辅助栈 O(h)，最坏 O(n)；新建输出树 O(n)。',
 'quiz':{'question':'preorder=[1,2,3]、inorder=[1,2,3] 应构造什么形状？','answer':'每个新值到来前，前一节点都已到中序访问时机，所以逐次接为右孩子，得到 1→右2→右3。'},
 'tests':checks('buildTree',[([[3,9,20,15,7],[9,3,15,20,7]],[3,9,20,None,None,15,7]),([[1,2,3],[1,2,3]],[1,None,2,None,3]),([[1,2,3],[3,2,1]],[1,2,None,3]),([[-1],[-1]],[-1]),([[],[]],[])],tree_args=[],result='tree',preserve_args=[0,1])
})

CHAPTER['problems'].append({
 'id':112,'slug':'path-sum',
 'summary':'判断是否存在从根开始、在叶子结束的路径，使节点值之和等于 targetSum。叶子必须同时没有左右孩子。',
 'baseline':'枚举所有根到叶路径，保存路径列表后逐条求和，会重复保存公共前缀。判断存在性只需要当前累计和，不需要记录每个节点序列。',
 'insight':'每个 DFS 帧携带“到父节点为止的累计和”。进入当前节点加上 val；只有当前节点是叶子时，才与目标比较。数值允许负数，暂时超过目标也可能在后面被负数抵消。',
 'steps':['空树返回 False；根帧携带前缀和 0。','弹出节点，把当前值加到前缀和。','若是叶子且和等于目标，立即 True。','否则将非空孩子与更新后的和压栈。','全部叶子都不满足时 False。'],
 'invariant':'帧中的前缀和来自根到当前节点父亲的唯一连接路径，加上 node.val 后恰好是根到当前节点之和。只在叶子比较，保证所有候选都符合题目的完整路径定义。',
 'examples':[{'label':'中途满足目标不能停','input':'root=[1,2]，targetSum=1','output':'False','frames':[
  {'title':'根的累计和已是 1','note':'根还有左孩子，所以它不是允许的路径终点。','diagram':'1  ← 当前累计和 1，但不是叶子\n/\n2'},
  {'title':'到叶子后累计和为 3','note':'唯一合法根到叶路径是 1→2，和不等于目标 1。','array':[1,2],'active':[0,1],'metrics':[['路径和',3],['目标',1]]}
 ]},{'label':'负数可以拉回目标','input':'root=[1,-2,3]，targetSum=-1','output':'True','frames':[
  {'title':'不能因为根值大于目标而剪枝','note':'1>-1，但左边的 -2 会把累计和降到 -1。','diagram':'   1\n  / \\\n-2   3'},
  {'title':'叶子 -2 处匹配','note':'1+(-2)=-1，找到一条完整路径即可返回。','array':[1,-2],'active':[0,1],'metrics':[['路径和',-1]]}
 ]}],
 'walkthrough':['路径和不是“任意一段”之和；本题必须包含根，并且最后一个节点必须是叶子。','left is None and right is None 才表示叶子，使用 or 会把单孩子节点误认为叶子。','提前返回 True 只表达找到一条路径，113 则需要继续收集全部符合的路径。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        if root is None:
            return False
        # prefix 只包括到父节点为止的路径和。
        stack = [(root, 0)]
        while stack:
            node, prefix = stack.pop()
            # 访问当前节点时再把它的值加进去。
            total = prefix + node.val
            # 只有到叶节点才允许匹配，中间节点恰好等于目标也不算。
            if node.left is None and node.right is None:
                if total == targetSum:
                    return True
            if node.right is not None:
                stack.append((node.right, total))
            if node.left is not None:
                stack.append((node.left, total))
        return False
'''.strip(),
 'code_notes':['帧中的整数状态独立，不需要访问完一条路径后手动减去节点值。','空树没有根到叶路径，即使目标为 0 也返回 False。','只读输入树，不修改 val 来保存累计和。'],
 'pitfalls':['在内部节点累计和相等时就返回 True。','使用单侧为空作为叶子条件。','包含负数时仍按 total>target 剪枝。'],
 'complexity':'时间 O(n)，辅助栈 O(h)，最坏 O(n)。',
 'quiz':{'question':'空树且 targetSum=0，是否存在和为零的根到叶路径？','answer':'不存在。空路径没有根和叶，不属于本题允许的路径。'},
 'tests':checks('hasPathSum',[([[1,2],1],False),([[1,-2,3],-1],True),([[],0],False),([[0],0],True),([SAMPLE,9],False)])
})

CHAPTER['problems'].append({
 'id':113,'slug':'path-sum-ii',
 'summary':'返回所有从根到叶、节点和等于目标的路径，每条路径用整数列表表示。不能在找到第一条之后停止。',
 'baseline':'给每个孩子复制一份完整路径，代码简单但公共前缀被反复复制，长链上即使答案很少也可能累计 O(n²) 复制成本。回溯可维护一份当前路径，只在命中答案时复制。',
 'insight':'显式栈除了进入帧，还安排退出帧。进入节点时 path.append(val)，处理完整棵子树后由退出帧 path.pop()。答案使用 path.copy() 固定当时的值，避免后续回溯修改旧结果。',
 'steps':['根的进入帧携带累计和 0，path 与 result 为空。','进入节点：追加值并更新和；若是合法叶子，复制 path 保存。','先压当前退出帧，再压右、左孩子进入帧。','退出节点：从 path 移除末尾值，恢复到父节点路径。','遍历结束返回所有保存的路径。'],
 'invariant':'进入帧执行前 path 恰好是根到父节点的路径，追加后成为根到当前节点的路径。退出帧排在所有后代任务之下，保证整棵子树结束才移除当前值，因而下一兄弟分支不会继承上一分支的后缀。',
 'examples':[{'label':'保存答案后仍要恢复路径','input':'root=[1,2,3,4,5,null,3]，targetSum=7','output':'[[1,2,4],[1,3,3]]','frames':[
  {'title':'左侧找到第一条路径','note':'1+2+4=7，保存 [1,2,4] 的副本。','diagram':'    1\n   / \\\n  2   3\n / \\   \\\n4   5   3','metrics':[['path','[1,2,4]']]},
  {'title':'退出 4，再探索 5','note':'退出 4 后 path=[1,2]；进入 5 得到 [1,2,5]，和为 8，不保存。','table':{'headers':['动作','path','已保存结果'],'rows':[['退出 4','[1,2]','[[1,2,4]]'],['进入 5','[1,2,5]','[[1,2,4]]'],['退出 5、2','[1]','[[1,2,4]]']]}},
  {'title':'右侧找到第二条路径','note':'两个 3 是不同节点，路径 [1,3,3] 合法；前一份副本保持原样。','table':{'headers':['路径','总和'],'rows':[['[1,2,4]',7],['[1,3,3]',7]]}}
 ]}],
 'walkthrough':['栈中的退出帧相当于递归函数返回前的“撤销选择”，它与进入动作配对。','只有命中叶子时才复制路径，令成本与实际输出长度对应；没有命中的长链不反复复制前缀。','两条不同节点路径可以有完全相同的值序列，题目要求每条路径都返回，不能擅自用集合去重。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> list[list[int]]:
        if root is None:
            return []
        result = []
        # 维护当前根到节点的一条路径，进入追加，退出弹出。
        path = []
        stack = [(root, 0, False)]
        while stack:
            node, prefix, exiting = stack.pop()
            # 显式返回事件负责回溯，防止左子树路径残留到右子树。
            if exiting:
                path.pop()
                continue
            total = prefix + node.val
            path.append(node.val)
            if node.left is None and node.right is None and total == targetSum:
                # 命中答案时复制快照，否则后续回溯会改坏已保存的答案。
                result.append(path.copy())
            # 先压退出事件，再压右左孩子，确保当前路径保留到两个孩子都处理完。
            stack.append((node, total, True))
            if node.right is not None:
                stack.append((node.right, total, False))
            if node.left is not None:
                stack.append((node.left, total, False))
        return result
'''.strip(),
 'code_notes':['退出帧的 prefix 不参与计算，只负责配对撤销 path 的最后一项。','path.copy() 新建列表；整数元素不需要深拷贝。','右先压、左后压产生先左后右的答案顺序，本题允许路径顺序不同。'],
 'pitfalls':['直接 append(path)，所有答案共享同一列表。','退出帧先于孩子执行，导致路径缺少祖先。','每个节点都复制整条路径却把时间仍写成 O(n)。'],
 'complexity':'设所有返回路径的长度总和为 S，时间 O(n+S)，辅助空间 O(h)，输出空间 O(S)。S 最坏可达 O(n²)，不能忽略保存答案的成本。',
 'quiz':{'question':'保存第一条 path 后，为什么修改 path 不会改变已保存答案？','answer':'因为保存的是 path.copy() 产生的新列表，两份列表的结构独立；列表里的整数不可变。'},
 'tests':checks('pathSum',[([[1,2,3,4,5,None,3],7],[[1,2,4],[1,3,3]]),([[1,2],1],[]),([[],0],[]),([[0,0,0],0],[[0,0],[0,0]]),([[1,-2,3],-1],[[1,-2]])],compare='sorted')
})

CHAPTER['problems'].append({
 'id':129,'slug':'sum-root-to-leaf-numbers',
 'summary':'每个节点是 0..9 的一位数字，根到叶路径按顺序组成十进制整数，返回这些整数之和。例如 1→2 表示 12，不是 1+2。',
 'baseline':'收集每条路径并拼字符串，再转整数可行，但需要额外维护路径文本。逐位追加数字本来就对应“原数乘 10 加当前数字”，可以直接累计数值。',
 'insight':'帧携带父路径组成的数字 prefix。进入当前节点后 number=prefix*10+node.val；若是叶子，将整个 number 加到总和，否则把它传给孩子。共享前缀在不同路径中分别按位扩展。',
 'steps':['从 (root,0) 开始 DFS。','当前数字等于 prefix*10+val。','只有到叶子才计入 answer。','非叶子把 number 传给左右孩子，最终返回 answer。'],
 'invariant':'prefix 是根到父节点数字序列的十进制值，乘十把已有位整体左移，再加一位 node.val，恰好得到当前路径数字。每个叶子只访问一次，故每条根到叶数字恰好累加一次。',
 'examples':[{'label':'数字追加与普通求和不同','input':'root=[4,9,0,5,1]','output':'1026','frames':[
  {'title':'根数字为 4','note':'向左到 9 形成 49，向右到 0 形成 40。','diagram':'    4\n   / \\\n  9   0\n / \\\n5   1'},
  {'title':'两个左侧叶子','note':'49×10+5=495，49×10+1=491。它们共享前缀 49，但各自形成完整数字。','table':{'headers':['路径','计算','计入总和'],'rows':[['4→9→5','49×10+5',495],['4→9→1','49×10+1',491]]}},
  {'title':'右侧叶子 0 也要计入','note':'4×10+0=40，合计 495+491+40=1026。','array':[495,491,40],'active':[0,1,2],'metrics':[['总和',1026]]}
 ]}],
 'walkthrough':['节点 9 是内部节点，不能把 49 单独加到答案，否则多算了一条未到叶子的路径。','数字 0 是合法一位。路径 1→0→2 形成 102，不能跳过零变成 12。','本题数字深度最多 10，并保证总答案落在 32 位整数范围；Python 整数无需手动处理溢出。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        answer = 0
        stack = [(root, 0)]
        while stack:
            node, prefix = stack.pop()
            # 路径数字每向下一层，就把已有数字左移一位十进制再加当前数字。
            number = prefix * 10 + node.val
            # 只在叶节点结算一条完整路径，避免重复计算公共前缀。
            if node.left is None and node.right is None:
                answer += number
            if node.right is not None:
                stack.append((node.right, number))
            if node.left is not None:
                stack.append((node.left, number))
        return answer
'''.strip(),
 'code_notes':['number 与 answer 含义不同：前者是一条当前路径的数字，后者累加完整叶子数字。','不修改 node.val，避免把原始一位数字覆盖成多位前缀。','每条栈帧携带自己的 prefix，因此兄弟路径互不污染。'],
 'pitfalls':['把拼数字写成 prefix+val。','内部节点也加入答案。','认为值为 0 的节点不存在。'],
 'complexity':'在题目的有界数字范围内，时间 O(n)，辅助栈 O(h)。',
 'quiz':{'question':'路径 0→0→7 代表多少，前导零要特殊删除吗？','answer':'代表 7。按 number=number*10+digit 计算会自然处理前导零，不需要额外删除。'},
 'tests':checks('sumNumbers',[([[4,9,0,5,1]],1026),([[1,2,3]],25),([[1,0,None,2]],102),([[0]],0),([SAMPLE],385)])
})

CHAPTER['problems'].append({
 'id':236,'slug':'lowest-common-ancestor-of-a-binary-tree',
 'summary':'给定树中的两个不同节点对象 p、q，返回最近公共祖先对象。一个节点可以是自己的祖先；题目保证 p、q 都在树中。',
 'baseline':'建立父节点表，收集 p 的祖先，再沿 q 向上找第一个交点，是正确的 O(n) 时间与空间方案。若从子树返回“发现了谁”，则可以在后序汇总时直接定位两条寻找路径的交汇处。',
 'insight':'子树返回三类结果：没找到则 None；只找到一个目标则返回该目标；已经找到二者则返回它们的最近公共祖先。当前节点若就是 p 或 q，返回它；否则左右各有结果时返回当前节点，只有一边有结果时向上传递那一边。',
 'steps':['按后序展开整棵树，matches 保存孩子返回值。','完成节点时读取并删除左右结果。','若当前节点是 p 或 q，返回当前节点引用。','否则左右都有结果时保存当前节点；只存在一侧时保存该侧结果。','根的返回结果就是 LCA。'],
 'invariant':'对已经完成的子树，返回值总结其中包含的目标：零个为空，一个为该目标，两个为最近交汇点。左右分居时当前节点是最低的共同祖先；若当前节点本身是目标且另一目标在其后代中，它自己就是答案。已找到的交汇点可以原样向上传递，不会被更高祖先替换。',
 'examples':[{'label':'两个目标在同一大子树内','input':'root=[3,5,1,6,2,0,8,null,null,7,4]；p=节点7，q=节点4','output':'原节点 2','frames':[
  {'title':'目标都在 5 的右子树','note':'这里数字唯一便于展示，但算法返回并比较节点对象。','diagram':'       3\n      / \\\n     5   1\n    / \\ / \\\n   6  2 0  8\n     / \\\n    7   4'},
  {'title':'7 与 4 分别向上返回自己','note':'节点 2 的左右结果都非空，因此在 2 首次合流。','table':{'headers':['完成节点','左结果','右结果','返回'],'rows':[[7,'None','None','节点7'],[4,'None','None','节点4'],[2,'节点7','节点4','节点2']]}},
  {'title':'更高祖先原样传递 2','note':'5 只有右边返回 2，3 只有左边返回 2，最终仍是节点 2。','diagram':'节点2 → 传给5 → 传给3 → 返回原节点2'}
 ]}],
 'walkthrough':['若 p=5、q=4，处理节点 5 时自身就是目标，因此返回 5，包含了“自己是祖先”的情形。','必须依赖题目保证两个目标存在。若只找到 p 而 q 不存在，这个简化返回协议仍会返回 p，不能直接推广到目标可能缺失的变体。','对象身份用 is 判断，返回值也是节点引用，不能只返回某个整数 val。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
        # 记录子树中发现的目标节点或已经确定的最近公共祖先。
        matches = {}
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            # 先处理左右子树，返回时合并两边的查找结果。
            if not expanded:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
            else:
                left = matches.pop(node.left, None)
                right = matches.pop(node.right, None)
                # 按对象身份匹配目标；目标本身也可以是另一个目标的祖先。
                if node is p or node is q:
                    matches[node] = node
                # 两个目标分处左右子树，当前节点就是两条路径第一次汇合的位置。
                elif left is not None and right is not None:
                    matches[node] = node
                else:
                    # 仅一边发现目标，就把那边的结果继续向上传递。
                    matches[node] = left if left is not None else right
        return matches[root]
'''.strip(),
 'code_notes':['None 在 matches 中表示该已完成子树没有目标，与节点数值 0 无关。','读取孩子结果后删除，空间与仍等待汇总的路径相关。','即使当前节点已经是目标，本实现仍统一处理孩子，方便解释完整后序协议。'],
 'pitfalls':['只比较节点数值来表达身份。','忽略 p 是 q 祖先的情况。','把一个目标可能缺失的变体也直接使用同样返回规则。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，最坏 O(n)。',
 'quiz':{'question':'p 在左子树、q 在右子树时，为什么根就是最近公共祖先？','answer':'任何低于根的节点都只处于其中一棵子树，不能同时覆盖两边；根是两条祖先链第一次合流的位置。'},
 'tests':checks('lowestCommonAncestor',[([[3,5,1,6,2,0,8,None,None,7,4],9,10],4),([[3,5,1,6,2,0,8,None,None,7,4],1,10],1),([[3,5,1,6,2,0,8,None,None,7,4],1,2],0),([[1,2],0,1],0)],node_args=[1,2],result='node')
})

CHAPTER['problems'].append({
 'id':437,'slug':'path-sum-iii',
 'summary':'统计和等于 targetSum 的向下路径数量。路径可以从任意节点开始，也可以在任意节点结束，但只能沿父到子的方向，不能跨兄弟分支。',
 'baseline':'枚举每个节点作为起点，再向下搜索所有后代，长链中会重复访问 O(n²) 次。沿当前根路径维护前缀和次数，就能在到达每个终点时一次统计所有合法起点。',
 'insight':'当前根到节点的前缀和为 total。若某个严格在当前节点之前的祖先前缀等于 total-targetSum，两者相减就得到一条以当前节点结束的目标路径。freq 只保存当前祖先链上的前缀次数，进入节点后增加，离开该子树时撤销。',
 'steps':['freq={0:1} 表示根之前的空前缀。','进入节点计算 total，先将 freq[total-target] 加到答案。','再增加 freq[total]，供后代查询。','压入退出帧及左右孩子进入帧。','退出时减少当前 total 的次数，为兄弟分支恢复祖先状态。'],
 'invariant':'进入节点查询前，freq 恰好包含根之前以及当前节点所有严格祖先的前缀和，并保留重复次数。每个匹配前缀对应唯一向下起点。退出撤销确保兄弟分支的前缀不会混入当前祖先链，路径不会非法跨分支。',
 'examples':[{'label':'相同前缀代表不同起点','input':'root=[0,0,null,0]，targetSum=0','output':'6','frames':[
  {'title':'根之前已有一个零前缀','note':'freq[0]=1。所有节点值都是 0，但路径起点不同仍应分别计数。','diagram':'0（A）\n/\n0（B）\n/\n0（C）'},
  {'title':'进入节点前先查询','note':'A 有 1 条，B 有 2 条，C 有 3 条以自己结束的零和路径。','table':{'headers':['终点','查询前 freq[0]','新增路径','累积'],'rows':[['A',1,'A',1],['B',2,'B；A→B',3],['C',3,'C；B→C；A→B→C',6]]}},
  {'title':'退出时逐层恢复次数','note':'C、B、A 退出后 freq[0] 从 4 依次降到 3、2、1，空前缀保留。','table':{'headers':['退出','freq[0]'],'rows':[['C',3],['B',2],['A',1]]}}
 ]},{'label':'兄弟分支不能互相配对','input':'root=[0,0,0]，targetSum=0','output':'5','frames':[
  {'title':'左右叶子各新增两条','note':'根 1 条；左叶子 2 条；右叶子 2 条。左叶子的前缀必须先退出，不能成为右叶子的起点。','diagram':'   0（根）\n  / \\\n0（左）0（右）','metrics':[['总数','1+2+2=5']]}
 ]}],
 'walkthrough':['查询必须在插入当前前缀之前。否则 target=0 时会把当前前缀与自己配对，多算长度为零的路径。','字典保存次数而不是是否出现。连续零会产生相同前缀，它们对应不同起点，必须全部计入。','退出帧在整个子树结束之后才撤销当前前缀，因此当前前缀会同时服务左右后代，但左分支更深的前缀不会泄漏到右分支。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        if root is None:
            return 0
        # 空前缀出现一次，允许路径从根开始；这里只统计当前祖先路径上的前缀。
        freq = {0: 1}
        answer = 0
        stack = [(root, 0, False)]
        while stack:
            node, prefix, exiting = stack.pop()
            # 退出节点时撤销它的前缀次数，防止另一分支与本分支错误配对。
            if exiting:
                freq[prefix] -= 1
                if freq[prefix] == 0:
                    del freq[prefix]
                continue
            total = prefix + node.val
            # 当前前缀减目标和，就是需要寻找的旧前缀；其次数决定新增路径数。
            answer += freq.get(total - targetSum, 0)
            # 先查后存，避免把当前节点与自己配成空路径。
            freq[total] = freq.get(total, 0) + 1
            stack.append((node, total, True))
            if node.right is not None:
                stack.append((node.right, total, False))
            if node.left is not None:
                stack.append((node.left, total, False))
        return answer
'''.strip(),
 'code_notes':['进入帧 prefix 表示父前缀；退出帧 prefix 保存的是当前 total，两种阶段的字段含义要区分。','次数归零后删除键，让字典只保留当前祖先链的信息。','负数不影响前缀相减关系，本题不能硬套正数滑动窗口。'],
 'pitfalls':['用 set 丢失相同前缀的多个起点。','先插入后查询，target=0 时多算空路径。','忘记退出撤销，统计到跨兄弟分支的非法路径。'],
 'complexity':'在字典平均 O(1) 操作假设下，时间 O(n)，辅助空间 O(h)，最坏 O(n)。',
 'quiz':{'question':'三节点零链为什么是 6 条，不是 3 条？','answer':'以三个节点分别作为终点，起点可以有 1、2、3 种，共 1+2+3=6；题目允许从内部节点开始。'},
 'tests':checks('pathSum',[([[0,0,None,0],0],6),([[0,0,0],0],5),([[10,5,-3,3,2,None,11,3,-2,None,1],8],3),([[],0],0),([[1,-1],0],1)])
})

CHAPTER['problems'].append({
 'id':124,'slug':'binary-tree-maximum-path-sum',
 'summary':'在非空二叉树中选择任意一条非空简单路径，求节点值总和的最大值。路径可以不经过根，可以只选一个节点，但不能重复节点或形成分叉。',
 'baseline':'枚举路径端点再求和会重复计算许多共同子路径。像直径一样按路径的最高转折节点分类，可以把每个候选拆成当前值加左右两条可选贡献。',
 'insight':'定义 gain(node) 为必须从 node 开始、向下只走一条分支的最大和。负的孩子贡献可以丢弃，L=max(0,gain(left))，R=max(0,gain(right))。当前候选为 node.val+L+R，返回父节点却只能给 node.val+max(L,R)。',
 'steps':['用后序取得孩子的单臂贡献；全局 best 初始为负无穷。','读取 L、R 并截断为不小于零。','用当前值加双臂更新全局 best。','保存当前值加较大单臂作为 gain。','全部节点处理完返回 best。'],
 'invariant':'gain 的路径必须包含当前节点，且最多选择一个孩子，才能继续接到父节点而不产生三叉。全局候选在当前节点转折时最多接左右两臂，覆盖所有最高转折点。候选始终含 node.val，保证路径非空，即使全树为负也不会错误选择空路径。',
 'examples':[{'label':'最佳路径位于内部子树','input':'root=[-10,9,20,null,null,15,7]','output':'42','frames':[
  {'title':'20 的左右都有正贡献','note':'最佳路径 15→20→7 不经过根 -10。','diagram':'    -10\n    / \\\n   9  20\n      / \\\n     15  7'},
  {'title':'双臂候选与单臂返回不同','note':'经过 20 的完整候选为 42，但向根延伸只能带 20+15=35。','table':{'headers':['节点','L','R','全局候选','返回 gain'],'rows':[[15,0,0,15,15],[7,0,0,7,7],[20,15,7,42,35]]}},
  {'title':'根候选只有 34','note':'-10+9+35=34，小于已经找到的 42；最终保留子树中的答案。','table':{'headers':['节点','候选','全局 best'],'rows':[[-10,34,42]]}}
 ]},{'label':'全负数也必须选一个节点','input':'root=[-3,-5,-2]','output':'-2','frames':[
  {'title':'负孩子贡献舍弃，当前节点仍保留','note':'每个候选至少包含自己，最大值是单节点 -2，不能返回 0。','array':[-3,-5,-2],'active':[2],'metrics':[['答案',-2]]}
 ]}],
 'walkthrough':['如果把 42 返回给 -10 再接上 9，就会形成同时经过 15、7、父节点的三叉，已经不是一条路径。','截断负贡献意味着可以不进入那个孩子，不意味着可以把当前节点也丢掉。','best 不能初始为 0，因为题目要求非空路径；全负输入的正确答案仍然是负数。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def maxPathSum(self, root: TreeNode) -> int:
        gain = {}
        # 路径至少包含一个节点，全是负数时答案也不能错误地初始化为 0。
        best = float('-inf')
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            # 用后序先算孩子能提供的最大单侧贡献。
            if not expanded:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
            else:
                # 负贡献不如不接这条边，左右两侧都可以独立放弃。
                left = max(0, gain.pop(node.left, 0))
                right = max(0, gain.pop(node.right, 0))
                # 作为路径最高点时，可以同时接左右两侧，更新全局答案。
                best = max(best, node.val + left + right)
                # 传给父亲的路径只能走一侧，不能把一个分叉继续向上当成路径。
                gain[node] = node.val + max(left, right)
        return best
'''.strip(),
 'code_notes':['题目保证非空，所以至少处理一次整数候选，最终 best 是整数而不是无穷值。','删除已使用孩子贡献，让辅助状态只保留尚未汇总的路径信息。','整个实现没有 Python 递归调用，允许题目中的深链结构。'],
 'pitfalls':['把双臂路径作为返回值继续接父节点。','把 best 初始化成 0。','只计算必须经过根的路径。'],
 'complexity':'时间 O(n)，辅助空间 O(h)，最坏 O(n)。',
 'quiz':{'question':'node.val=-5，左孩子贡献为 10 时，gain 应为 0、5 还是 10？','answer':'应为 5。gain 定义要求包含当前节点，因此必须加上 -5；是否舍弃整个这条贡献由它的父节点决定。'},
 'tests':checks('maxPathSum',[([[-10,9,20,None,None,15,7]],42),([[-3,-5,-2]],-2),([[1,2,3]],6),([[-3]],-3),([[2,-1]],2)])
})

CHAPTER['problems'].append({
 'id':114,'slug':'flatten-binary-tree-to-linked-list',
 'summary':'将二叉树原地展开为前序顺序的右链：每个 left 都变成 None，right 指向下一个原节点。接口直接修改输入并返回 None，不新建 ListNode。',
 'baseline':'按 144 的前序用栈逐个取出原节点，再把上一节点的 right 接到当前节点，能用 O(h) 辅助空间完成。进阶要求 O(1) 空间，可以直接把尚未处理的右子树接到左子树的续接位置。',
 'insight':'前序在根之后先走左子树、再走右子树。若 cur 有左孩子，沿左子树的 right 找到最右节点 pred，将原右子树接到 pred.right；然后把整棵左子树搬到 cur.right 并清空 cur.left。后续继续处理右链，会逐步展开这棵搬来的子树。',
 'steps':['cur=root，沿当前 right 方向推进。','若 cur.left 存在，令 pred=cur.left，并沿 pred.right 走到空处。','先令 pred.right=cur.right，保留原右子树的入口。','再令 cur.right=cur.left、cur.left=None。','cur=cur.right，直到所有节点处理完；无返回值。'],
 'invariant':'cur 之前的部分已经是正确前序右链且 left 为空。将左子树置于右侧、原右子树接在其最右续接位置，保持尚未处理部分的前序不变；左子树内部仍会在后续迭代中展开，所以不要求这次一次性把整棵左子树变成链。',
 'examples':[{'label':'先保存右子树，再搬左子树','input':'root=[1,2,5,3,4,null,6]','output':'原地 right 链：1→2→3→4→5→6；所有 left=None','frames':[
  {'title':'根 1 的左子树先于右子树','note':'左子树从 2 开始，沿 right 找到续接节点 4。','diagram':'    1\n   / \\\n  2   5\n / \\   \\\n3   4   6'},
  {'title':'先把 4.right 接到 5','note':'随后让 1.right 指向 2、清空 1.left。原右子树 5→6 已经有新的入口。','diagram':'1 → 2\n   / \\\n  3   4 → 5 → 6'},
  {'title':'在节点 2 重复相同步骤','note':'将 2 的原右段 4→5→6 接到 3.right，再搬左孩子 3。','diagram':'1 → 2 → 3 → 4 → 5 → 6\n所有箭头均为 right；所有 left 均为 None'}
 ]}],
 'walkthrough':['pred 是沿左子树右边找到的续接点，不一定已经是该子树前序的最后节点。若 pred 自己还有左子树，后续处理 pred 时会先展开它的左边，再走刚接上的原右子树，顺序仍然正确。','三句改边有依赖：必须在覆盖 cur.right 之前，把原右子树保存到 pred.right。','内层 while 虽嵌在外层中，但用于查找续接点的原右边不会在后续左子树查找中反复扫描；这些右链扫描总计 O(n)，外层也只处理每个节点一次。'],
 'code':'''

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        cur = root
        while cur is not None:
            if cur.left is not None:
                # 把左子树移到右边前，先找到左子树最右侧可衔接原右子树的位置。
                pred = cur.left
                while pred.right is not None:
                    pred = pred.right
                # 先保留原右子树，再把整棵左子树搬到右侧。
                pred.right = cur.right
                cur.right = cur.left
                # 题目要求展开后所有 left 都为空。
                cur.left = None
            cur = cur.right

    # 对照：前序栈版本，时间 O(n)，辅助空间 O(h)。
    # 对照方法：用栈按前序取节点，直接串成右链，但需要额外栈空间。
    def flattenStack(self, root: Optional[TreeNode]) -> None:
        if root is None:
            return
        stack = [root]
        previous = None
        while stack:
            node = stack.pop()
            # 先右后左入栈，弹出时才能按前序先访问左侧。
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
            if previous is not None:
                # 把上一访问节点接到当前节点，逐步形成前序链表。
                previous.right = node
            node.left = None
            previous = node
        previous.right = None
'''.strip(),
 'code_notes':['主方法没有 return root，Python 函数自然返回 None，与原地接口一致。','保留全部 TreeNode 对象及 val，只重新连接左右引用。','栈版本先保存原左右孩子，再清空 left 或修改前驱连接，保证不会丢失待处理入口。'],
 'pitfalls':['先覆盖 right，丢失原右子树。','忘记把 left 清空，结果仍是树而不是指定右链。','把每个节点 val 复制到新链表，未按要求复用原节点。'],
 'complexity':'主方法时间 O(n)，额外空间 O(1)；内层右链查找总计线性。完整对照方法 flattenStack 时间 O(n)，辅助空间 O(h)，最坏 O(n)。两者均原地复用节点。',
 'quiz':{'question':'输入只有右链时，主方法会改变哪些连接？','answer':'不会改变任何连接。每个 cur.left 都为空，只沿 right 向后走，原链已经符合前序展开要求。'},
 'tests':{'adapter':'tree','method':'flatten','result':'flatten','cases':[{'args':[[1,2,5,3,4,None,6]],'expected':[1,2,3,4,5,6]},{'args':[SAMPLE],'expected':[1,2,4,5,3,6]},{'args':[[]],'expected':[]},{'args':[[0]],'expected':[0]},{'args':[[1,2,5,None,3,None,None,4]],'expected':[1,2,3,4,5]}]}
})

CHAPTER['problems'].append({
 'id':297,'slug':'serialize-and-deserialize-binary-tree',
 'summary':'实现 Codec.serialize(root) 将树转为字符串，以及 Codec.deserialize(data) 从字符串恢复同样的节点值和左右结构。编码格式可自行设计，不要求复用原节点身份。',
 'baseline':'只记录前序或层序的非空值不足以恢复一般二叉树。根 1 配左孩子 2，与根 1 配右孩子 2，都可能得到值序列 [1,2]，所以必须保存结构信息。',
 'insight':'采用包含空位的 BFS 编码：真实节点写十进制值，空位置写 #，字段用逗号分隔。每个真实父节点在序列中恰好产生两个后续孩子字段。解码时按同样队列顺序，每次为父节点消费两个字段，遇 # 不创建节点。',
 'steps':['序列化将 root 入队；真实节点输出值并追加左右位置，空位置只输出 #。','用逗号 join 全部字段，空树编码为单独的 #。','反序列化先 split，若首字段为 # 返回 None。','创建根并入队；每次弹出父节点，读取两个孩子字段，非 # 时创建并入队。','返回新根，两个接口通过字符串传递全部信息，不依赖隐藏状态。'],
 'invariant':'序列化队列与解码队列具有相同的真实节点次序。根值恢复后，每次两字段按固定左、右顺序确定一个父节点的两个孩子位置；由此归纳可以逐层唯一恢复所有值与空位。负号和多位整数由逗号分隔，# 不与任何整数混淆。',
 'examples':[{'label':'空位决定左右关系','input':'root=[1,null,2,3]','output':'编码 "1,#,2,3,#,#,#"；解码恢复 [1,null,2,3]','frames':[
  {'title':'原树并不连续填满','note':'1 的左孩子为空，右孩子为 2；2 的左孩子为 3。','diagram':'1\n \\\n  2\n /\n3'},
  {'title':'BFS 输出位置字段','note':'空位置输出 # 后不再产生孩子，编码能有限结束。','array':['1','#','2','3','#','#','#'],'active':[1,4,5,6],'array_label':'以逗号连接成字符串'},
  {'title':'解码每个真实父节点消费两项','note':'空孩子没有进入解码队列；只有新建的真实孩子会等待自己的两个字段。','table':{'headers':['父节点','左字段','右字段','结果'],'rows':[[1,'#','2','仅建右孩子2'],[2,'3','#','仅建左孩子3'],[3,'#','#','叶子']]}},
  {'title':'得到新的节点对象','note':'结构与值相同，引用身份不同；换一个 Codec 实例也能从相同字符串解码。','diagram':'新1\n \\\n  新2\n /\n新3'}
 ]}],
 'walkthrough':['该格式保留末尾所有空位。n 个真实节点共有 2n 个孩子位置，加上根字段，总计 2n+1 个字段，其中 n+1 个是 #；空树也符合 1 个字段。','解码不能按照“每个数组下标 i 对应 2i+1、2i+2”来索引，因为空孩子没有继续展开。必须按真实父节点队列消费两个字段。','deserialize 接收本协议 serialize 产生的合法字符串。通用网络解析器还需校验非法字段与缺失输入；那些不是此题接口要求。'],
 'code':'''
from collections import deque

from typing import Optional

# 平台传入 TreeNode 对象；层序数组只是题目展示树的方式。
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        # 序列化采用层序，并用 # 保留空孩子的位置，才能还原原结构。
        fields = []
        queue = deque([root])
        while queue:
            node = queue.popleft()
            # 空位置也写入字符串；不能只记录非空节点值。
            if node is None:
                fields.append('#')
                continue
            fields.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
        return ','.join(fields)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        # 反序列化按相同顺序读取，每个非空父节点接收两个孩子字段。
        fields = data.split(',')
        # 根字段为空，表示整棵树为空。
        if fields[0] == '#':
            return None
        root = TreeNode(int(fields[0]))
        queue = deque([root])
        i = 1
        while queue:
            # 按层序取父节点，后续两个字段分别属于它的左、右孩子。
            parent = queue.popleft()
            if fields[i] != '#':
                parent.left = TreeNode(int(fields[i]))
                queue.append(parent.left)
            if fields[i + 1] != '#':
                parent.right = TreeNode(int(fields[i + 1]))
                queue.append(parent.right)
            # 每处理一个父节点恰好消费两个位置，新建的非空孩子再入队。
            i += 2
        return root
'''.strip(),
 'api':{'signature':"','.join(fields) -> str；data.split(',') -> list[str]；int(token) -> int",'description':['join 要求字段都是字符串，并用逗号连接。split 以逗号切回字段列表，不会自动将数字转换为整数。','int 可以解析本题中带负号的十进制值；必须先排除 #。采用分隔符后，值 12、-3 不会被误拆成单个字符。']},
 'code_notes':['类名与接口为 Codec，不是 Solution；两种方法都完整给出。','serialize 不缓存 root 或对象映射，deserialize 在新实例上同样可用。','反序列化为每个非 # 字段创建独立节点，相同值也不会被合并成同一对象。'],
 'pitfalls':['只输出非空值，丢失结构。','将空节点继续扩成两个空孩子，队列无法结束。','解码时把数字当成单字符，无法支持负数和多位数。','依赖同一个 Codec 实例里保存的原树，使字符串本身无法恢复树。'],
 'complexity':'设编码字符数为 L，序列化与反序列化时间均 O(L)。在题目值范围有界时 L=O(n)。字段列表及字符串占 O(L)，BFS 队列占 O(w)，解码输出树另占 O(n)。',
 'quiz':{'question':'为什么不能用节点值作字典键，把解码节点按值复用？','answer':'树可以含有多个同值节点，它们处在不同位置。按值复用会把树变成共享节点的图，结构和身份关系都错误。'},
 'tests':checks('serialize',[([[1,None,2,3]],[1,None,2,3]),([[1,2,3,None,None,4,5]],[1,2,3,None,None,4,5]),([[]],[]),([[-12,-12,0]],[-12,-12,0]),([[0]],[0])],result='codec',**{'class':'Codec'})
})
