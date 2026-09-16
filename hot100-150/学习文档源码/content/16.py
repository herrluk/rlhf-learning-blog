from textwrap import dedent

def sequence(constructor, operations, expected):
    return dict(constructor=constructor,operations=[dict(method=name,args=args) for name,args in operations],expected=expected)

def design(name,cases):
    return {'adapter':'design','class':name,'method':'operations','cases':cases}

CHAPTER={
 'lead':'设计题要求一个对象在多次调用之间保持正确状态。先写清每个接口做什么，再选择能同时满足查询、更新和时间复杂度要求的结构。',
 'intro':['建议顺序：155 辅助最小栈 → 232 双栈队列 → 208 前缀树 → 146 LRU → 295 双堆中位数 → 460 LFU。前面学过的栈、链表、哈希和堆，会在这里组合成长期维护的对象。','所有代码块均包含题目要求的完整类及必要辅助类、导入，可以各自独立提交。设计题不使用 Solution 包装；平台创建对象后依次调用公开方法。','例子使用 Python 的 None、True、False。平台输入输出中的 null、true、false 是对应的 JSON 表示。构造器与无返回值的修改操作显示为 None；这并不表示操作失败。'],
 'sections':[
  {'title':'从接口倒推结构，而不是先背代码','body':['先列出要做的操作及成本：LRU 需要按键查找、把已知节点移到一端、从另一端淘汰。哈希表解决定位，双向链表解决重排。','再写不变量：哈希表与链表包含相同真实节点；双堆保存同一批数据的左右两半；最小栈的每一层保留对应前缀的最小值。','最后逐个分析操作如何暂时改变结构、如何恢复不变量。判断设计是否正确，要观察连续调用，而不只是某一次返回值。'], 'diagram':'接口和复杂度要求\n       ↓\n需要支持的基本操作\n       ↓\n组合结构 + 对象状态\n       ↓\n每次公开调用结束都恢复不变量'},
  {'title':'三种复杂度措辞要分清','body':['O(1) 平均时间：哈希定位依赖散列的平均表现，LRU/LFU 通常使用这个口径。','均摊 O(1)：某一次队列 pop 可能搬运很多元素，但一整段操作中每个元素只被搬运一次，总成本与操作数同阶。','O(log n) 更新、O(1) 查询：双堆把维护工作放在 addNum，findMedian 只看堆顶。不能因为取中位数只读两个数，就把整个结构说成所有操作 O(1)。']},
  {'title':'LRU 与 LFU 的淘汰依据','body':['LRU 只比较最近一次使用时间，最久未访问的先淘汰。命中的 get 和更新已有键的 put 都刷新顺序。','LFU 先比较累计使用次数；只有次数相同，才比较最近使用时间。新键从频次 1 开始，命中的 get 与更新已有键的 put 都增加频次。','例如 A 被访问 10 次但较早，B 被访问 1 次但较晚：LRU 可能淘汰 A，LFU 会优先淘汰 B。两题共享顺序维护技巧，但判定规则不同。']}
 ],
 'apis':[
  {'signature':'self.field = ...：把状态保存到当前实例','description':['每次公开调用都从同一个实例读取和更新这些字段。写在 __init__ 中的 self.items=[] 会为每个实例创建独立列表。','不要把可变列表或字典写成所有对象共享的类属性，否则两个缓存或两个栈会互相污染。']},
  {'signature':'list.append(x)、list.pop()、items[-1]','description':['在列表尾部模拟栈顶。append 为均摊常数时间，尾部 pop 为均摊常数时间，读取最后元素为常数时间。','232 只用栈顶操作；pop(0) 会移动其余元素，也不符合只用栈的限制。']}
 ],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':155,'slug':'min-stack',
 'summary':'实现 MinStack，支持 push、pop、top 与 getMin。既要遵守后进先出，也要快速读取当前栈内最小值。题目保证弹出和查询时非空。',
 'baseline':'用普通栈保存值，再在 getMin 中调用 min(stack)，一次查询要 O(n)。只保存一个全局最小值也不够：当这个最小值被弹出，无法直接知道之前的最小值。',
 'insight':'用一个同样高的辅助栈 mins。第 i 层保存 values[0:i+1] 的最小值，相当于为每个入栈时刻保存一份最小值快照。弹出一层后，上一层的快照自然恢复。',
 'steps':['创建 values 与 mins 两个空栈。','push(val)：先计算 val 与旧最小值的较小者，再向两个栈各压入一个值。','pop()：两个栈同步弹出。','top() 读 values[-1]；getMin() 读 mins[-1]。'],
 'invariant':'两个栈长度始终相同，且 mins[i]=min(values[:i+1])。入栈时用旧前缀最小值与新元素比较，得到新前缀最小值；出栈只删除最后一层，不改变之前各层的含义。因此栈顶快照始终就是当前最小值。',
 'examples':[{'label':'弹出最小值后自动恢复','input':'push(3), push(1), push(2), getMin(), pop(), pop(), getMin()','output':'None, None, None, 1, None, None, 3','frames':[
  {'title':'每层保存自己的前缀最小值','note':'图中从左到右为栈底到栈顶。压入 2 时，最小值仍然是 1。','panels':[{'heading':'values','array':[3,1,2],'active':[2]},{'heading':'mins','array':[3,1,1],'active':[2]}]},
  {'title':'弹出 2，最小值还是 1','note':'两个栈各弹一次，两个栈顶仍对应同一个深度。','panels':[{'heading':'values','array':[3,1]},{'heading':'mins','array':[3,1]}]},
  {'title':'再弹出 1，恢复为 3','note':'无需重新扫描 values，读取 mins 的栈顶即可。','panels':[{'heading':'values','array':[3]},{'heading':'mins','array':[3]}],'metrics':[['getMin()',3]]}
 ]},{'label':'重复最小值不能一起消失','input':'push(2), push(1), push(1), pop(), getMin()','output':'None, None, None, None, 1','frames':[
  {'title':'两个 1 分别占据一层','note':'弹出后来的 1，先前的 1 还在，因此最小值仍为 1。','table':{'headers':['状态','values','mins'],'rows':[['弹出前','[2,1,1]','[2,1,1]'],['弹出后','[2,1]','[2,1]']]}}
 ]}],
 'walkthrough':['如果只在遇到严格更小值时保存最小值，重复的 1 会给出栈恢复带来额外计数问题。本解每层都保存快照，让入栈、出栈一一对应。','push 中必须先读取旧 mins 的栈顶，再追加新快照；第一次入栈没有旧最小值，直接使用 val。','pop 的接口不要求返回被删元素，所以代码不写 return。top 只读取而不移除。'],
 'code':'''
class MinStack:
    def __init__(self):
        # values 存真实元素，mins 同步存每个栈深度下的最小值快照。
        self.values = []
        self.mins = []

    def push(self, val: int) -> None:
        # 新深度的最小值来自新元素与旧最小值，重复最小值也要记录。
        current_min = val if not self.mins else min(val, self.mins[-1])
        self.values.append(val)
        self.mins.append(current_min)

    def pop(self) -> None:
        # 两个栈同步弹出，较早的最小值会自然恢复。
        self.values.pop()
        self.mins.pop()

    def top(self) -> int:
        return self.values[-1]

    def getMin(self) -> int:
        # 原题保证非空时查询；栈顶快照就是当前全栈最小值。
        return self.mins[-1]
'''.strip(),
 'code_notes':['两个列表在 __init__ 里分别创建，不共享同一个对象。','条件表达式 val if not self.mins else ... 避免第一次压入时访问空栈。','min(a,b) 只比较两个整数，属于常数工作；min(self.values) 才会遍历整个栈。'],
 'pitfalls':['弹出 values 时忘记同步弹出 mins。','重复最小值只记录一次，却仍在每次弹出时删除最小值记录。','把 top 写成 pop，导致查询悄悄修改结构。'],
 'complexity':'抽象栈模型下各操作 O(1)，空间 O(n)。Python list 的尾部追加和弹出按动态数组均摊 O(1) 计，扩缩容可能使个别调用更慢；top 与 getMin 为最坏 O(1)。',
 'quiz':{'question':'values=[4,2,5,1] 时，mins 应是什么？弹出一次后最小值是多少？','answer':'mins=[4,2,2,1]。弹出后 mins=[4,2,2]，最小值恢复为 2。'},
 'tests':design('MinStack',[
  sequence([], [('push',[3]),('push',[1]),('push',[2]),('getMin',[]),('pop',[]),('pop',[]),('getMin',[])],[None,None,None,1,None,None,3]),
  sequence([], [('push',[2]),('push',[1]),('push',[1]),('pop',[]),('getMin',[])],[None,None,None,None,1]),
  sequence([], [('push',[-2]),('push',[0]),('push',[-3]),('getMin',[]),('pop',[]),('top',[]),('getMin',[])],[None,None,None,-3,None,0,-2]),
  sequence([], [('push',[-2147483648]),('top',[]),('getMin',[]),('pop',[]),('push',[2147483647]),('getMin',[])],[None,-2147483648,-2147483648,None,None,2147483647])
 ])
})

CHAPTER['problems'].append({
 'id':232,'slug':'implement-queue-using-stacks',
 'summary':'只使用两个栈的标准操作实现先进先出的 MyQueue，提供 push、pop、peek 和 empty。pop 与 peek 调用时保证队列非空。',
 'baseline':'如果每次出队都把全部元素来回倒腾，单次操作可能反复处理同一批元素，连续出队总计 O(n²)。关键是让已经翻转好的旧元素保持顺序，直到它们全部出队。',
 'insight':'incoming 接收新元素，outgoing 负责出队。只有 outgoing 为空时，才把 incoming 的所有元素逐个弹出并压入 outgoing；一次翻转后，最早入队的元素正好成为 outgoing 栈顶。',
 'steps':['push(x) 只压入 incoming。','pop/peek 先调用 _move；若 outgoing 非空则什么也不搬。','需要搬运时，将 incoming 逐个弹入 outgoing，直到 incoming 为空。','pop 弹出 outgoing 栈顶；peek 只读取它。','两栈都空时，empty 才为 True。'],
 'invariant':'队列从队首到队尾的逻辑顺序，始终为“outgoing 从栈顶到栈底，再接 incoming 从栈底到栈顶”。outgoing 中的元素都比 incoming 更早入队；因此非空时不能混入新元素，清空后再整体翻转 incoming 才能保持先后关系。',
 'examples':[{'label':'旧输出栈未空时，新元素先等待','input':'push(1), push(2), peek(), push(3), pop(), pop(), pop(), empty()','output':'None, None, 1, None, 1, 2, 3, True','frames':[
  {'title':'新元素进入输入栈','note':'图中每个栈都是左底右顶。此时逻辑队列为 1→2。','panels':[{'heading':'incoming','array':[1,2]},{'heading':'outgoing','diagram':'空'}]},
  {'title':'peek 第一次触发翻转','note':'依次弹出 2、1，outgoing 变成 [2,1]，栈顶 1 就是队首。peek 不弹出它。','panels':[{'heading':'incoming','diagram':'空'},{'heading':'outgoing','array':[2,1],'active':[1]}]},
  {'title':'push(3) 只修改 incoming','note':'outgoing 仍有旧元素 1、2，不能把 3 搬到它们上面。逻辑队列仍为 1→2→3。','panels':[{'heading':'incoming','array':[3]},{'heading':'outgoing','array':[2,1]}]},
  {'title':'先弹旧元素，再搬新元素','note':'前两次 pop 返回 1、2；第三次才把 3 搬过去并返回。两栈最终都空。','table':{'headers':['调用','是否搬运','返回'],'rows':[['pop()','否',1],['pop()','否',2],['pop()','是：3',3],['empty()','否','True']]}}
 ]}],
 'walkthrough':['两次栈顺序反转实现先进先出：新元素从 incoming 顶部弹出后，被压到 outgoing 底部，早到的最后被搬运，因此位于 outgoing 顶部。','_move 是公共的准备步骤，peek 和 pop 都调用它，避免两份逻辑写出不一致的条件。','每个元素最多经历一次压入 incoming、一次从 incoming 弹出、一次压入 outgoing、一次从 outgoing 弹出，因此一段操作的总搬运成本为线性。'],
 'code':'''
class MyQueue:
    def __init__(self):
        # incoming 接收新元素，outgoing 负责按队列顺序提供旧元素。
        self.incoming = []
        self.outgoing = []

    def push(self, x: int) -> None:
        self.incoming.append(x)

    def _move(self) -> None:
        # 只有输出栈为空才搬运，不能把新元素混到尚未取完的旧元素前面。
        if not self.outgoing:
            while self.incoming:
                # 连续弹出并压入会反转顺序，最早入队的元素来到输出栈顶。
                self.outgoing.append(self.incoming.pop())

    def pop(self) -> int:
        # 需要出队或查看队首时再按需搬运，每个元素最多搬一次。
        self._move()
        return self.outgoing.pop()

    def peek(self) -> int:
        self._move()
        return self.outgoing[-1]

    def empty(self) -> bool:
        # 两个栈都为空，整个队列才为空。
        return not self.incoming and not self.outgoing
'''.strip(),
 'code_notes':['方法名 _move 的单下划线表示内部辅助方法的命名约定，不是 Python 的强制私有访问控制。','not self.incoming and not self.outgoing 返回布尔值，两个条件必须同时满足。','整个主解没有从列表头部读取或删除，也没有用切片反转代替栈操作。'],
 'pitfalls':['outgoing 没空也搬运，把新元素放到了旧元素之前。','每次 pop 后把剩余元素搬回 incoming，失去均摊优势。','只检查 incoming 是否为空来判断整个队列为空。'],
 'complexity':'push、pop、peek 均摊 O(1)，empty 最坏 O(1)。某次 pop/peek 触发 n 个元素搬运时可达 O(n)；空间 O(n)。Python 动态列表的扩缩容也计入均摊成本。',
 'quiz':{'question':'incoming=[3,4]、outgoing=[2,1]，现在 peek 应该返回什么？需要搬运吗？','answer':'返回 outgoing 栈顶 1，不搬运。队列逻辑顺序为 1、2、3、4。'},
 'tests':design('MyQueue',[
  sequence([], [('push',[1]),('push',[2]),('peek',[]),('push',[3]),('pop',[]),('pop',[]),('pop',[]),('empty',[])],[None,None,1,None,1,2,3,True]),
  sequence([], [('empty',[]),('push',[9]),('peek',[]),('peek',[]),('pop',[]),('empty',[])],[True,None,9,9,9,True]),
  sequence([], [('push',[1]),('pop',[]),('push',[2]),('pop',[]),('empty',[])],[None,1,None,2,True]),
  sequence([], [('push',[2]),('push',[2]),('pop',[]),('empty',[]),('pop',[]),('empty',[])],[None,None,2,False,2,True])
 ])
})

CHAPTER['problems'].append({
 'id':208,'slug':'implement-trie-prefix-tree',
 'summary':'实现 Trie，支持插入单词、查询完整单词、查询是否存在给定前缀。输入均为非空小写英文字符串；重复插入同一个单词不需要重复计数。',
 'baseline':'用 set 保存完整单词，精确查询很方便，但 startsWith 需要检查许多已存单词。若大量字符串共享前缀，可以把相同前缀保存为同一条路径，查询时只读取给定字符串的字符。',
 'insight':'每个节点代表一个前缀，children 将下一个字符映射到子节点。is_word 表示该路径是否曾作为完整单词插入。沿路径能走到底，只能说明前缀存在；完整匹配还必须检查终点的 is_word。',
 'steps':['根节点代表空前缀，不保存字母。','insert 从根逐字走，缺少对应孩子时创建节点，最后设置 is_word=True。','公共 _walk(text) 沿字符路径前进，遇到缺边返回 None。','search 要求找到节点且 is_word 为 True。','startsWith 只要求路径存在。'],
 'invariant':'从根沿字符 c1…ck 到达的唯一节点，表示前缀 c1…ck。创建节点只会为已有前缀增加下一字符，不改变既有路径；只有完整插入结束的位置才标为单词。因此路径与前缀对应，词尾标记与已插入完整单词对应。',
 'examples':[{'label':'有路径不等于有完整单词','input':'insert("apple"), search("app"), startsWith("app"), insert("app"), search("app")','output':'None, False, True, None, True','frames':[
  {'title':'插入 apple，只标记最后的 e','note':'星号表示 is_word=True；app 对应的第二个 p 节点暂时没有星号。','diagram':'root\n └─ a\n     └─ p\n         └─ p  ← app 的终点\n             └─ l\n                 └─ e ★'},
  {'title':'两种查询检查的条件不同','note':'都能沿 a→p→p 走到底，但 search 还要检查词尾标记。','table':{'headers':['查询','路径存在','词尾标记','结果'],'rows':[['search("app")','是','否','False'],['startsWith("app")','是','不要求','True']]}},
  {'title':'插入 app，不需要新节点','note':'共享已有 a→p→p 路径，只把第二个 p 标为词尾；apple 仍然存在。','diagram':'root\n └─ a\n     └─ p\n         └─ p ★  ← app\n             └─ l\n                 └─ e ★  ← apple'}
 ]},{'label':'共享前缀之后可以分叉','input':'insert("cat"), insert("car"), search("cap"), startsWith("ca")','output':'None, None, False, True','frames':[
  {'title':'缺少 p 边才是真正的路径失败','note':'cat 与 car 共享 ca 节点，但查询 cap 在最后一步失败。','diagram':'root → c → a\n             ├─ t ★\n             └─ r ★\n             p 边不存在'}
 ]}],
 'walkthrough':['节点本身不需要重复保存完整前缀，根到该节点的路径已经编码了前缀。每个节点仅存孩子映射和词尾布尔值。','node=child 是让局部变量指向已有节点，不是复制整棵树；修改 node.is_word 会更新树中的真实节点。','_walk 只读取结构；search 和 startsWith 都不能在查询失败时顺便创建节点。','单词最长可到 2000 个字符，本解使用循环，避免长单词形成递归深度问题。'],
 'code':'''
from typing import Optional

class TrieNode:
    def __init__(self):
        # 每个节点用“字符 → 孩子节点”的字典表示下一步，is_word 标记完整单词结束。
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            # 插入时才创建缺失节点，多个单词可以复用相同前缀。
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        # 走完单词后单独标记结束，前缀存在不代表单词存在。
        node.is_word = True

    # 查询只沿已有节点行走，缺失即失败，不能悄悄创建节点。
    def _walk(self, text: str) -> Optional[TrieNode]:
        node = self.root
        for char in text:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        # 完整单词查询还要检查结束标志；前缀查询只需路径存在。
        return node is not None and node.is_word

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
'''.strip(),
 'api':{'signature':'Optional[TrieNode]；node is not None and node.is_word','description':['Optional[T] 表示返回 T 类型对象或 None，是类型提示，不会自动创建节点。','and 短路求值：node 为 None 时不会再读取 node.is_word，避免属性访问错误。']},
 'code_notes':['每个 TrieNode 都有自己的 children 字典。','重复插入只再次设置 True，不会产生重复路径。','根代表空前缀；本题字符串非空，主讲与测试按该约束，不额外定义空串接口协议。'],
 'pitfalls':['把路径存在直接当成完整单词存在。','插入时把沿途每个节点都标为词尾，误认为所有前缀都已插入。','所有节点共享同一个 children 字典。','在查询中使用会自动创建节点的逻辑，让读操作修改结构。'],
 'complexity':'单次 insert、search、startsWith 的平均时间为 O(L)，L 是该次输入长度，按字符字典平均常数查询计。若插入字符总数为 S，结构总空间 O(S)，共享前缀会减少实际节点数；查询额外空间 O(1)。',
 'quiz':{'question':'先插入 car，再插入 cart，search("car") 是否仍为 True？','answer':'仍为 True。插入 cart 会沿已有 car 路径添加 t，但不会清除 r 节点的词尾标记。'},
 'tests':design('Trie',[
  sequence([], [('insert',['apple']),('search',['app']),('startsWith',['app']),('insert',['app']),('search',['app']),('search',['apple'])],[None,False,True,None,True,True]),
  sequence([], [('insert',['cat']),('insert',['car']),('search',['cap']),('startsWith',['ca'])],[None,None,False,True]),
  sequence([], [('search',['a']),('startsWith',['a']),('insert',['a']),('insert',['a']),('search',['a']),('search',['aa'])],[False,False,None,None,True,False]),
  sequence([], [('insert',['car']),('insert',['cart']),('search',['car']),('search',['cart']),('startsWith',['cars'])],[None,None,True,True,False])
 ])
})

CHAPTER['problems'].append({
 'id':146,'slug':'lru-cache',
 'summary':'实现容量固定的 LRUCache。get 命中返回值并刷新使用时间，未命中返回 -1；put 插入或更新。新键导致超容量时，淘汰最久未使用的键。题目容量为正数，要求 get/put 平均 O(1)。',
 'baseline':'用列表保存最近使用顺序，访问某个键后要先查找再移到一端，删除中间元素会需要 O(n)。只用哈希表又无法直接定位最久未使用的键，因此需要同时保存定位关系和使用顺序。',
 'insight':'字典 nodes 将 key 映射到真实链表节点；双向链表保存从最近使用到最久未使用的顺序。已知节点可以 O(1) 摘除并插到头部，尾部就是淘汰对象。两个哨兵让空表、单节点与多节点复用同一组接线操作。',
 'steps':['创建 head、tail 两个哨兵并连接，nodes 初始为空。','get 未命中直接返回 -1；命中则 _touch 将节点移到 head 后，再返回值。','put 已有键时更新 value，并 _touch；不增加节点数。','put 新键时创建节点，加入字典和 head 后。','如果超容量，摘下 tail.prev，并从字典删除对应 key。'],
 'invariant':'每次公开操作结束时，head 到 tail 之间的真实节点与 nodes 一一对应；每个节点的前后引用互相一致，节点顺序按最近使用时间递减，真实节点数不超过容量。命中节点移头、插入节点放头均对应“刚使用”；从尾部删除恰好淘汰最久未使用项。',
 'examples':[{'label':'get 会改变下一次淘汰对象','input':'capacity=2；put(1,10), put(2,20), get(1), put(3,30), get(2)','output':'None, None, 10, None, -1','frames':[
  {'title':'插入两项后，2 最近使用','note':'左端靠近 head 是最近使用，右端靠近 tail 是最久未使用；哨兵不存缓存数据。','diagram':'head ⇄ [2:20] ⇄ [1:10] ⇄ tail\n        最近        最久\nnodes：1→节点1，2→节点2'},
  {'title':'get(1) 把同一个节点移到头部','note':'先从原位置摘下节点 1，再插在 head 后。值仍为 10，节点总数仍为 2。','diagram':'head ⇄ [1:10] ⇄ [2:20] ⇄ tail\n        最近        最久','metrics':[['返回',10]]},
  {'title':'插入 3 后淘汰尾部的 2','note':'将节点 2 同时从链表与字典删除；get(2) 才会正确返回 -1。','diagram':'head ⇄ [3:30] ⇄ [1:10] ⇄ tail\nnodes：1→节点1，3→节点3\n淘汰 key=2'}
 ]},{'label':'更新已有键也刷新顺序','input':'capacity=2；put(1,10), put(2,20), put(1,99), put(3,30), get(1), get(2)','output':'None, None, None, None, 99, -1','frames':[
  {'title':'更新不是再创建一个同键节点','note':'把节点 1 的值改为 99 并移头，后续插入 3 淘汰的是 2。','table':{'headers':['调用后','从最近到最久','节点数'],'rows':[['put(2,20)','2:20 → 1:10',2],['put(1,99)','1:99 → 2:20',2],['put(3,30)','3:30 → 1:99',2]]}}
 ]}],
 'walkthrough':['摘除 x 时，保存 left=x.prev 与 right=x.next，再令 left.next=right、right.prev=left。只需修改相邻节点，不必从表头寻找 x。','插入头部时，把 x 放到 head 与旧 first 之间：先设置 x.prev/x.next，再让 head.next 和 first.prev 指向 x。','_touch 复用“摘除+插头”，即使节点原本已经在头部，也能按相同规则处理。','淘汰时必须从尾节点取得 key，再删除字典项。只删链表会使 get 仍命中旧节点；只删字典会让链表保留幽灵节点。','这里完整手写双向链表，是为了能解释每条引用的作用；Python OrderedDict 也能表达 LRU 顺序，但面试可能继续要求解释其底层结构。'],
 'code':'''
class Node:
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # 哈希表按 key 定位节点；双向链表维护从最近使用到最久未使用的顺序。
        self.nodes = {}
        # 头尾哨兵不存真实缓存项，让插入和删除都无需单独处理边界。
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    # 只摘下链表节点，不在这里改哈希表；移动节点和真正淘汰都要复用它。
    def _remove(self, node: Node) -> None:
        left, right = node.prev, node.next
        # 先把左右邻居接起来，再清理节点旧指针。
        left.next = right
        right.prev = left
        node.prev = None
        node.next = None

    # 头哨兵之后代表最近使用，把节点插到这里。
    def _add_front(self, node: Node) -> None:
        first = self.head.next
        node.prev = self.head
        node.next = first
        self.head.next = node
        first.prev = node

    # 读或更新已有键都算使用：先摘下，再移到头部。
    def _touch(self, node: Node) -> None:
        self._remove(node)
        self._add_front(node)

    def get(self, key: int) -> int:
        # 缓存未命中按接口返回 -1，不能创建新条目。
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self._touch(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        # 已存在的键只更新值并刷新最近使用顺序，不增加容量。
        if key in self.nodes:
            node = self.nodes[key]
            node.value = value
            self._touch(node)
            return
        node = Node(key, value)
        self.nodes[key] = node
        self._add_front(node)
        if len(self.nodes) > self.capacity:
            # 超出容量时淘汰尾部最久未使用节点，链表与哈希表必须同步删除。
            victim = self.tail.prev
            self._remove(victim)
            del self.nodes[victim.key]
'''.strip(),
 'code_notes':['字典存的是节点对象引用，_touch 移动的是同一个对象，不复制 key/value。','哨兵也用 Node 创建，但永远不加入 nodes；因此真实 key=0 与哨兵默认 key=0 不会混淆。','_remove 清除被摘节点的前后引用，使其暂时处于脱离状态；_add_front 会重新设置引用。','新键先插入再判断是否超容量，因此内部会短暂有 capacity+1 项，公开 put 结束时已恢复容量约束。'],
 'pitfalls':['get 只返回值、不刷新顺序。','更新已有键时又创建第二个节点，或无端淘汰其他键。','只修改 next、不修改对应 prev，使反向链断开。','把链表头尾的“最近/最久”方向写反。'],
 'complexity':'get 与 put 平均 O(1)，每次只做常数次哈希操作和指针更新；容量为 C 时空间 O(C)。哈希操作采用平均时间口径。',
 'quiz':{'question':'容量 2，依次 put(1,1)、put(2,2)、get(1)、put(2,22)、put(3,3)，谁被淘汰？','answer':'key=1。get(1) 曾使 1 最近，但后来的 put(2,22) 又刷新了 2，所以插入 3 时 1 最久未使用。'},
 'tests':design('LRUCache',[
  sequence([2],[('put',[1,10]),('put',[2,20]),('get',[1]),('put',[3,30]),('get',[2])],[None,None,10,None,-1]),
  sequence([2],[('put',[1,10]),('put',[2,20]),('put',[1,99]),('put',[3,30]),('get',[1]),('get',[2])],[None,None,None,None,99,-1]),
  sequence([1],[('put',[0,0]),('get',[0]),('put',[0,5]),('get',[0]),('put',[1,6]),('get',[0]),('get',[1])],[None,0,None,5,None,-1,6]),
  sequence([2],[('put',[1,1]),('put',[2,2]),('get',[1]),('put',[2,22]),('get',[9]),('put',[3,3]),('get',[1]),('get',[2])],[None,None,1,None,-1,None,-1,22])
 ])
})

CHAPTER['problems'].append({
 'id':295,'slug':'find-median-from-data-stream',
 'summary':'实现 MedianFinder，支持持续加入整数与查询当前全部数的中位数。奇数个取排序后的中间值，偶数个取中间两个值的平均；查询时保证至少有一个数。',
 'baseline':'每次查询都对全部数据排序需要 O(n log n)，维护有序列表则一次插入可能移动 O(n) 个元素。中位数只需要左右两半的边界值，没有必要让每一半内部完全有序。',
 'insight':'low 保存较小的一半，用取负的小顶堆模拟大顶堆；high 保存较大的一半，用普通小顶堆。保持 low 的数量等于 high，或恰好多一个；并保证 low 中每个真实值都不大于 high 中每个值。此时中位数只由两个堆顶决定。',
 'steps':['创建 low、high 两个空堆。','addNum(num)：先将 -num 压入 low。','把 low 的最大真实值移到 high，让左右边界重新分开。','若 high 比 low 多，将 high 的最小值移回 low，使 low 保存较多的那一个元素。','findMedian：low 多一个则取 -low[0]；一样多则取 (-low[0]+high[0])/2。'],
 'invariant':'每次 addNum 结束后，两堆的多重集合并集等于所有已加入的数据；len(low) 为总数的一半向上取整，len(high) 为向下取整；左半最大值不大于右半最小值。把左半最大值移右，再在需要时把右半最小值移左，都只跨越分界，既恢复大小关系，也保持元素无丢失、无重复。',
 'examples':[{'label':'插入时搬动边界值','input':'addNum(5), findMedian(), addNum(2), findMedian(), addNum(4), findMedian(), addNum(1), findMedian()','output':'None, 5.0, None, 3.5, None, 4.0, None, 3.0','frames':[
  {'title':'两个数：左右各一半','note':'加入 5、2 后，真实左半为 [2]，右半为 [5]。low 内实际存 -2，中位数为 (2+5)/2。','panels':[{'heading':'左半真实值','array':[2]},{'heading':'右半真实值','array':[5]}],'metrics':[['中位数',3.5]]},
  {'title':'加入 4 后，左边多保留一个','note':'将左侧最大候选 4 送右后，右侧会多；再把右侧最小的 4 搬回左，左半最大值为 4。图展示真实分组，不是底层堆数组排序。','panels':[{'heading':'左半真实值','array':[2,4]},{'heading':'右半真实值','array':[5]}],'metrics':[['中位数',4.0]]},
  {'title':'加入 1，把分界值 4 移到右边','note':'左半变为 {1,2}，右半为 {4,5}，数量相等，平均两个边界 2 与 4。','panels':[{'heading':'左半真实值','array':[1,2]},{'heading':'右半真实值','array':[4,5]}],'metrics':[['中位数',3.0]]}
 ]},{'label':'负数也要先恢复真实值','input':'addNum(-3), addNum(-2), findMedian(), addNum(-1), findMedian()','output':'None, None, -2.5, None, -2.0','frames':[
  {'title':'取负存储并不意味着原数据必须为正','note':'前两个数分为左 -3、右 -2，low 堆里存的是 3；计算时先还原 -low[0]。','table':{'headers':['含义','数值'],'rows':[['low[0] 的存储值',3],['左半最大真实值',-3],['high[0]',-2],['中位数',-2.5]]}}
 ]}],
 'walkthrough':['Python 3.10 的 heapq 是小顶堆。对真实值取负后，最大的真实值对应最小的负数，因此 -low[0] 就是左半最大值。','第一次插入也沿用相同三步：先入 low、移到 high、发现 high 多再移回 low。多做常数次堆操作，换来统一逻辑。','若原来两边等大，插入后最终 low 多一个；若原来 low 多一个，插入后最终两边等大。无需另写奇偶状态变量。','堆数组并非完整有序，只保证父节点不大于孩子。可视化的分组按真实数值展示，帮助看清分界；代码只要求堆性质。','若所有数均在 0..100，可以用 101 个计数格和总数定位中间秩；若仅 99% 在范围内，还必须处理落在尾部的中位数，不能直接丢弃剩余数据。'],
 'code':'''
from heapq import heappush, heappop

class MedianFinder:
    def __init__(self):
        # low 用负数模拟大顶堆，保存较小的一半；high 小顶堆保存较大的一半。
        self.low = []
        self.high = []

    def addNum(self, num: int) -> None:
        # 先加入小半区，再把其中最大值转入大半区，保持两半的大小关系。
        heappush(self.low, -num)
        heappush(self.high, -heappop(self.low))
        # 让 low 的数量等于 high 或多一个，奇数中位数就固定在 low 堆顶。
        if len(self.high) > len(self.low):
            heappush(self.low, -heappop(self.high))

    def findMedian(self) -> float:
        if len(self.low) > len(self.high):
            # 总数为奇数时，恢复负号后就是中位数。
            return float(-self.low[0])
        # 总数为偶数时，中间两个堆顶的平均数是中位数。
        return (-self.low[0] + self.high[0]) / 2
'''.strip(),
 'api':{'signature':'heappush(heap,x)、heappop(heap)；/ 与 //','description':['heapq 函数直接修改传入列表。heappop 删除并返回堆中最小的存储值，cost 为 O(log n)；读取 heap[0] 不删除，为 O(1)。','/ 保留小数，// 向下取整。中位数可能是 1.5 或 -2.5，不能用整数地板除。']},
 'code_notes':['元素从 low 移到 high 时取负还原；从 high 移到 low 时再次取负存储。','用 float 显式返回奇数个元素的中位数，与接口返回浮点数的含义一致。','findMedian 只读取堆，不弹出堆顶，因此连续查询不改变后续答案。'],
 'pitfalls':['只平衡数量、不维护左右值的大小关系。','忘记 low 存的是负数，错误地拿两个存储值相加。','使用 // 2 丢失半整数答案。','认为堆数组已经排序，直接按中间下标取值。'],
 'complexity':'当前有 n 个元素时，addNum 为 O(log(n+1))，findMedian 为 O(1)，总空间 O(n)。每次插入只执行常数次堆操作。',
 'quiz':{'question':'左半真实值 {1,2,8}、右半真实值 {3,9}，虽然数量平衡，能直接返回 8 吗？','answer':'不能。左半最大值 8 大于右半最小值 3，违反分区不变量。全部排序为 1,2,3,8,9，中位数应为 3。'},
 'tests':design('MedianFinder',[
  sequence([], [('addNum',[5]),('findMedian',[]),('addNum',[2]),('findMedian',[]),('addNum',[4]),('findMedian',[]),('addNum',[1]),('findMedian',[])],[None,5.0,None,3.5,None,4.0,None,3.0]),
  sequence([], [('addNum',[-3]),('addNum',[-2]),('findMedian',[]),('addNum',[-1]),('findMedian',[])],[None,None,-2.5,None,-2.0]),
  sequence([], [('addNum',[0]),('addNum',[0]),('findMedian',[]),('findMedian',[])],[None,None,0.0,0.0]),
  sequence([], [('addNum',[-100000]),('addNum',[100000]),('findMedian',[])],[None,None,0.0])
 ])
})

CHAPTER['problems'].append({
 'id':460,'slug':'lfu-cache',
 'summary':'实现 LFUCache：优先淘汰累计使用次数最少的键；频次并列时，淘汰其中最久未使用的键。新键频次为 1，命中的 get 和更新已有键的 put 都增加一次频次；未命中的 get 不改变状态。',
 'baseline':'给每个键存频次和时间戳，再在淘汰时扫描全部键，可以正确选择，但代价为 O(C)，无法满足平均 O(1) 的要求。需要直接找到最低频次组，并直接取出该组最旧的键。',
 'insight':'values 存 key→value，freq 存 key→频次，buckets 按频次分组。每个桶用 OrderedDict 维护从最久到最近的键顺序；min_freq 指向当前最小非空频次。命中时，键从 f 桶移到 f+1 桶末尾；淘汰时从 min_freq 桶头部删除。',
 'steps':['初始化 values、freq、buckets 与 min_freq。','_touch(key)：从旧频次桶删除，加入下一频次桶末尾，更新 freq。','旧桶清空就删除；若它是当前最小频次桶，min_freq 增为 f+1。','get 未命中返回 -1；命中则 _touch 后返回值。','put 已有键时更新值并 _touch；新键在满容量时先淘汰最低频次桶的最旧项。','新键加入频次 1 的桶末尾，并把 min_freq 设为 1。'],
 'invariant':'每个缓存键恰好属于一个频次桶，桶号等于 freq[key]，所有桶都非空。桶内从左到右按该键最近使用时间递增，min_freq 等于现存键的最小频次。一次使用只使频次 f→f+1，因此移动后放在新桶末尾；若旧最小桶清空，被移动键所在 f+1 桶必然存在，所以新的最小值正是 f+1。',
 'examples':[{'label':'先比较次数，再按组内时间淘汰','input':'capacity=2；put(1,10), put(2,20), get(1), put(3,30), get(3), put(4,40), get(1)','output':'None, None, 10, None, 30, None, -1','frames':[
  {'title':'新键都从频次 1 开始','note':'每个桶左边最久、右边最近。1 比 2 更早插入，因此在桶头。','diagram':'min_freq = 1\nf=1：[1 → 2]\nvalues：1:10，2:20'},
  {'title':'get(1) 将 1 提升到频次 2','note':'现在 2 是唯一频次 1 的键。随后 put(3,30) 必须淘汰 2，再把 3 放到频次 1。','diagram':'get(1) 后：\nf=1：[2]\nf=2：[1]\n\nput(3,30) 后：\nf=1：[3]\nf=2：[1]'},
  {'title':'get(3) 让两个键的频次相同','note':'频次 1 的桶清空并删除，min_freq 变成 2。3 刚使用过，加入 f=2 的末尾；1 在组内最久。','diagram':'min_freq = 2\nf=2：[1 → 3]\n       旧   新'},
  {'title':'插入 4，按并列规则淘汰 1','note':'从最小频次 2 的桶头弹出 1，新键 4 从频次 1 开始；min_freq 必须重新设为 1。','diagram':'min_freq = 1\nf=1：[4]\nf=2：[3]\n淘汰 key=1；get(1) → -1'}
 ]},{'label':'更新已有键也算一次使用','input':'capacity=2；put(1,10), put(2,20), put(1,99), put(3,30), get(1), get(2)','output':'None, None, None, None, 99, -1','frames':[
  {'title':'put(1,99) 同时更新值和频次','note':'1 的频次变成 2，2 仍为 1；加入 3 时淘汰 2。更新不能只改 value。','table':{'headers':['键','更新后值','更新后频次','插入 3 时'],'rows':[[1,99,2,'保留'],[2,20,1,'淘汰']]}}
 ]}],
 'walkthrough':['普通哈希表解决按键定位，但不能直接找最低频次，因此增加 freq 和 buckets；桶内还要区分同频次的先后，这正好复用 LRU 的顺序维护思想。','同一桶内，键进入桶的时刻就是它最近一次使用的时刻。下一次再使用，它会离开该桶进入更高频次桶，因此只要按进入顺序追加，桶内顺序就等于最近使用顺序。','_touch 删除最后一个最低频次键后，不能扫描所有桶求 min。该键马上进入 f+1，而其他键的频次至少为 f+1，所以直接 min_freq=f+1 足够。','插入新键时，不管旧 min_freq 多大，都要重置为 1。淘汰后到插入前的短暂状态不对外暴露，新键插入完成后恢复所有不变量。','本解用 OrderedDict 作为每个频次桶的顺序容器。上一题已经手写双向链表，这里可把每个 OrderedDict 理解为一个支持按键删除和从最旧端弹出的独立顺序结构。'],
 'code':'''
from collections import OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # values 存值，freq 存次数，buckets 按次数维护同频键的最近使用顺序。
        self.values = {}
        self.freq = {}
        self.buckets = {}
        # 记录当前最小访问频次，淘汰时直接定位对应桶。
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        # 每次读取或更新已有键，都将它从旧频次桶移动到高一频次的桶。
        old = self.freq[key]
        bucket = self.buckets[old]
        del bucket[key]
        # 旧桶为空就删除；若它是最小桶，则新的最小频次正好是 old+1。
        if not bucket:
            del self.buckets[old]
            if self.min_freq == old:
                self.min_freq = old + 1
        new = old + 1
        if new not in self.buckets:
            self.buckets[new] = OrderedDict()
        # 同频桶用 OrderedDict，刚使用的键放在末尾。
        self.buckets[new][key] = None
        self.freq[key] = new

    def get(self, key: int) -> int:
        if key not in self.values:
            return -1
        self._touch(key)
        return self.values[key]

    def put(self, key: int, value: int) -> None:
        # 零容量是额外防御分支，不存任何条目。
        if self.capacity == 0:
            return
        # 更新已有键同样算访问，必须提升频次，不能只改值。
        if key in self.values:
            self.values[key] = value
            self._touch(key)
            return
        if len(self.values) == self.capacity:
            bucket = self.buckets[self.min_freq]
            # 从最小频次桶的最前面弹出，得到同频中最久未使用的键。
            victim, _ = bucket.popitem(last=False)
            del self.values[victim]
            del self.freq[victim]
            if not bucket:
                del self.buckets[self.min_freq]
        self.values[key] = value
        self.freq[key] = 1
        if 1 not in self.buckets:
            self.buckets[1] = OrderedDict()
        self.buckets[1][key] = None
        # 新键频次从 1 开始，因此插入后全局最小频次一定是 1。
        self.min_freq = 1
'''.strip(),
 'api':{'signature':'OrderedDict；bucket.popitem(last=False)','description':['OrderedDict 从 collections 导入，保留插入顺序并支持从任意一端弹出。popitem(last=False) 删除并返回最早项的 (key,value) 元组；默认 last=True 是最近项，不能用错。','本题桶的 value 统一放 None，只需要 key 的顺序。victim, _ 解包返回元组，_ 表示不使用占位值。桶内删除、追加和端点弹出按平均 O(1) 计。']},
 'code_notes':['频次记录与真实值分开，避免把“值越小”误当成“使用越少”。','删除空桶很重要：若每次升级都留下空桶，空间会随调用次数增长，而不再受容量约束。','当前题面容量为正；capacity==0 是额外防御分支，表示零容量直接忽略写入，示例与主要复杂度按正容量说明。','get 未命中不会创建桶，不会增加频次，也不会改变 min_freq。'],
 'pitfalls':['只按频次淘汰，忘记同频次还要使用 LRU 规则。','更新已有键只改值、不增加使用次数。','新键插入后忘记 min_freq=1。','使用 popitem() 默认弹桶尾，错删同频次下刚访问的键。','每次淘汰扫描全部键，或保留无限增长的空频次桶。'],
 'complexity':'get 与 put 平均 O(1)：常数次哈希定位、桶内删除和追加；容量 C 下空间 O(C)，因为每个键只在一个桶且空桶及时删除。按整数计数和字典操作的常见算法模型分析。',
 'quiz':{'question':'最低频次是 5，且该桶只有键 A。get(A) 后为什么可直接把 min_freq 改为 6？','answer':'其他键原来至少为 6，A 这次从 5 升为 6，并确保频次 6 的桶存在。因此全体最小值正好是 6，无需扫描。'},
 'tests':design('LFUCache',[
  sequence([2],[('put',[1,10]),('put',[2,20]),('get',[1]),('put',[3,30]),('get',[3]),('put',[4,40]),('get',[1])],[None,None,10,None,30,None,-1]),
  sequence([2],[('put',[1,10]),('put',[2,20]),('put',[1,99]),('put',[3,30]),('get',[1]),('get',[2])],[None,None,None,None,99,-1]),
  sequence([1],[('put',[0,0]),('get',[0]),('get',[0]),('put',[1,9]),('get',[0]),('get',[1])],[None,0,0,None,-1,9]),
  sequence([2],[('put',[1,1]),('put',[2,2]),('get',[7]),('put',[3,3]),('get',[1]),('get',[2])],[None,None,-1,None,-1,2]),
  sequence([0],[('put',[1,1]),('get',[1])],[None,-1])
 ])
})
