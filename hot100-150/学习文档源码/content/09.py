from textwrap import dedent

CHAPTER={
 'lead':'栈保存“最近尚未完成的任务”，单调结构保存“仍可能成为答案的候选”。先说明每个元素为什么入栈、什么时候离开，再写 push 和 pop。',
 'intro':['学习顺序：20 括号匹配 → 150 后缀表达式 → 394 嵌套解码 → 227 乘除优先级 → 224 括号上下文 → 32 连续有效区间 → 739 第一个更大值 → 42 水层 → 84 矩形边界 → 239 窗口候选。','普通栈的后进先出来自语法嵌套或操作数顺序；单调栈的出栈来自一个候选已能结算、或已被另一个候选完全替代。二者不能只靠同一段 while 模板来理解。','单调队列还多一个窗口过期规则：队首可能因为离开窗口而删除，队尾可能因为被新值支配而删除。两种删除的理由不同，应分开推导。'],
 'sections':[
  {'title':'先定义栈中每一项的含义','body':['20 保存尚未闭合的左括号；150 保存已算完但尚未被上层运算消费的值；394、224 保存被内层计算暂时打断的外层状态。','739 保存尚未找到更暖日子的下标；84 保存尚未结算最大覆盖范围的柱子；239 保存当前窗口中仍可能成为最大值的下标。值、下标和上下文元组不能随意混用。'],'diagram':'栈底 [ 较早等待的任务 ... 最近等待的任务 ] 栈顶\n新增任务 → append\n完成最近任务 → pop'},
  {'title':'嵌套 while 不一定是平方复杂度','body':['单调栈一次循环可能弹出很多元素，但每个下标只入栈一次，离开后不会重新入栈。因此全部出栈次数至多 n，所有内层循环加起来是 O(n)。','这叫按元素累计总成本。证明要落到“同一个元素最多做几次操作”，不能只因为看见两层循环就写 O(n²)，也不能不看字符串复制成本就把解码题直接写成 O(n)。']},
  {'title':'三个常见但不同的比较条件','body':['找严格更大温度时，只有新温度 > 栈顶温度才能结算，等温不算答案。窗口最大值中，新值 >= 旧值即可淘汰旧值，因为新值更晚过期。','柱状图采用 >= 出栈来保持高度严格递增，等高时把更宽的机会交给右侧新柱。必须说明等号的处理依据，而不是在所有单调题里机械替换比较符。']}
 ],
 'apis':[{'signature':'list.append(value) -> None\nlist.pop(index: int = -1) -> value','description':['append 在列表末尾追加一项并返回 None；pop 默认移除并返回最后一项。作为栈使用时，末尾追加为摊还 O(1)，末尾弹出为 O(1)。空列表 pop 会抛出 IndexError。','stack[-1] 只读取栈顶，不删除。列表 pop(0) 需要移动后续元素，不适合实现本章单调队列的队首删除。']},{'signature':'collections.deque(iterable=(), maxlen: int | None = None) -> deque\ndeque.popleft() -> value','description':['deque 是双端队列，append、pop、appendleft、popleft 都可在对应端进行 O(1) 操作。popleft 移除并返回队首，空队列调用会抛出 IndexError。','239 使用不设 maxlen 的 deque，显式按下标判断过期；不能依靠队列长度自动截断，因为队列保存的是候选下标，数量通常少于窗口长度。']}],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':20,'slug':'valid-parentheses',
 'summary':'输入只包含三种括号 ()、[]、{}，判断能否按类型正确嵌套闭合。闭括号必须匹配最近一个尚未闭合的同类型开括号，结束时不能有剩余开括号。',
 'baseline':'只统计各类左右括号数量，会把 ([)] 误判为有效；数量相等无法表示嵌套顺序。反复删除相邻括号对也能判断，但多次扫描和构造字符串可能达到平方时间。',
 'insight':'最后打开的括号必须最先闭合，正好符合栈的后进先出。遇到左括号先保存，遇到右括号只检查栈顶对应类型；一旦不匹配，后面字符不可能修复已经错误的闭合次序。',
 'steps':['建立右括号到对应左括号的映射，初始化空栈。','左括号入栈。','右括号到来时，若栈空或弹出的栈顶不是对应左括号，立即返回 False。','扫描结束后返回栈是否为空。'],
 'invariant':'处理任意合法前缀后，栈从底到顶恰好是尚未闭合的左括号，顺序与原输入一致。右括号只能消费最近的一个，匹配后仍留下正确的未闭合序列；不匹配则当前前缀已违反嵌套规则。最终空栈表示所有打开任务都已完成。',
 'examples':[{'label':'类型数量都相同，但嵌套顺序错误','input':'s="([)]"','output':'False','frames':[
  {'title':'依次打开圆括号、方括号','note':'栈从底到顶为 (、[，下一次闭合必须先关闭方括号。','diagram':'已读：([\n栈底 [ "(", "[" ] 栈顶'},
  {'title':'遇到 )，只能检查栈顶 [','note':'圆括号需要匹配 (，但最近的未闭合括号是 [，立即失败，不能越过它去匹配栈底。','diagram':'期望："("\n实际栈顶："["\n不匹配 → False'}
 ]},{'label':'正确嵌套与串联都允许','input':'s="([]){}"','output':'True','frames':[
  {'title':'按最近打开的顺序依次闭合','note':'[ 被 ] 弹出，( 被 ) 弹出；随后 { 入栈，再被 } 弹出。','table':{'headers':['读完字符','栈（左为底，右为顶）'],'rows':[['(','圆括号 ('],['[','圆括号 ( → 方括号 ['],[']','圆括号 ('],[')','空'],['{','花括号 {'],['}','空']]}},
  {'title':'输入结束且栈为空','note':'既没有多余右括号，也没有剩余左括号，返回 True。','diagram':'未完成的括号任务：0'}
 ]}],
 'walkthrough':['([)] 说明不能只按括号类型分别计数；一张栈同时保留类型与先后顺序。','输入只有左括号时，扫描过程不会遇到类型错误，但最终栈不空，因此仍应返回 False。','代码使用短路 or：栈空时不会再执行 pop，避免空栈异常。'],
 'code':'''
class Solution:
    def isValid(self, s: str) -> bool:
        # 右括号映射到它必须匹配的左括号。
        opening = {')': '(', ']': '[', '}': '{'}
        # 栈顶保存最近一个尚未匹配的左括号，体现括号的嵌套顺序。
        stack = []
        for ch in s:
            if ch in opening:
                # 空栈或类型不符都立即失败；短路判断避免空栈弹出。
                if not stack or stack.pop() != opening[ch]:
                    return False
            else:
                stack.append(ch)
        # 结束时还留有左括号也不合法，必须全部匹配完。
        return not stack
'''.strip(),
 'code_notes':['else 分支依赖题目只包含六种括号；若扩展成任意文本校验，需要另外定义非括号字符如何处理。','return not stack 将空栈转换成 True，非空栈转换成 False。','匹配时只弹出一个最近的左括号。'],
 'pitfalls':['只比较左右括号数量无法处理交叉嵌套。','扫描结束直接返回 True 会漏掉剩余左括号。','遇到右括号时搜索整个栈寻找同类型，会错误允许越过尚未闭合的内层。'],
 'complexity':'时间 O(n)，每个字符入栈或出栈一次；额外空间 O(n)，最坏所有字符都是左括号。',
 'quiz':{'question':'为什么 ")(" 不能由后面的左括号补救？','answer':'第一个右括号到来时没有任何已打开的左括号，前缀已经不合法。合法嵌套要求先打开再关闭，后续字符无法改变这个顺序。'},
 'tests':{'method':'isValid','cases':[{'args':['([)]'],'expected':False},{'args':['([]){}'],'expected':True},{'args':['('],'expected':False},{'args':[')('],'expected':False},{'args':['()[]{}'],'expected':True}]}
})

CHAPTER['problems'].append({
 'id':150,'slug':'evaluate-reverse-polish-notation',
 'summary':'输入是合法的逆波兰表达式：运算符放在两个操作数之后。支持加减乘除，除法向零截断，保证除数不为零。返回表达式的整数值。',
 'baseline':'把后缀表达式重新转换成带括号的中缀表达式再求值，增加了解析工作，也不需要调用 eval。后缀顺序已经保证每个运算符出现时，两个操作数的子表达式都已完成。',
 'insight':'数字入栈，运算符消费最近两个已完成值，再把新结果入栈。先弹出的是右操作数，后弹出的是左操作数。减法和除法不满足交换律，因此这个顺序是正确性的关键。',
 'steps':['初始化数值栈。不是四个运算符之一的 token 用 int 转成整数入栈，包括负数 token。','遇到运算符，先弹 right，再弹 left。','计算 left 运算 right 并入栈。除法先算绝对值整除，再按两数符号是否相反决定正负。','合法表达式结束时栈中恰好一个值，返回它。'],
 'invariant':'处理任意 token 前缀后，栈中从底到顶保存该前缀已经算出的、等待被后续运算消费的各个子表达式值。运算符出现时，最上方两个值正是按表达式顺序排列的左、右子表达式；用计算结果替代二者保留整体含义。',
 'examples':[{'label':'先出栈的是右边的数','input':'["4","13","5","/","+"]','output':'6','frames':[
  {'title':'三个数字依次入栈','note':'栈为 [4,13,5]，栈顶 5 是即将发生的除法的右操作数。','array':[4,13,5],'array_label':'操作数栈：右侧为栈顶'},
  {'title':'执行 13÷5，向零截断为 2','note':'先弹 right=5，再弹 left=13。不是 5÷13，计算后把 2 入栈。','array':[4,2],'equation':'13 ÷ 5 → 2'},
  {'title':'最后执行 4+2','note':'弹出 2、4，合并为 6，表达式结束时只剩最终结果。','array':[6]}
 ]},{'label':'负数除法的两种取整不同','input':'["-7","3","/"]','output':'-2','frames':[
  {'title':'Python // 会向下取整','note':'-7//3=-3，但题目要求向零截断，所以不能直接使用带符号的 //。','table':{'headers':['规则','结果'],'rows':[['向下取整',-3],['向零截断',-2]]}},
  {'title':'先处理绝对值，再恢复符号','note':'abs(-7)//abs(3)=2，两边符号相反，因此返回 -2。整个过程不经过浮点数。','equation':'7 // 3 = 2 → 符号相反 → -2','diagram':'left=-7，right=3\n商的绝对值=2'}
 ]}],
 'walkthrough':['token="-11" 是一个负整数，不等于单独的 "-" 运算符。用集合判断完整 token，不能仅看第一个字符。','向零截断表示丢掉小数部分，例如 -2.333… 变成 -2。先做非负整除再加符号，能准确实现这个定义。','不采用 int(left/right)，是为了让整数计算始终停留在整数域，避免把可迁移的解法依赖于浮点精度。'],
 'code':'''
class Solution:
    def evalRPN(self, tokens: list[str]) -> int:
        stack = []
        for token in tokens:
            # 数字直接入栈；负数字符串也由 int 正确解析。
            if token not in {'+', '-', '*', '/'}:
                stack.append(int(token))
                continue
            # 先弹右操作数，再弹左操作数，减法和除法不能颠倒顺序。
            right = stack.pop()
            left = stack.pop()
            if token == '+':
                value = left + right
            elif token == '-':
                value = left - right
            elif token == '*':
                value = left * right
            else:
                # Python // 向下取整；先除绝对值再恢复符号，才能向零截断。
                value = abs(left) // abs(right)
                if (left < 0) != (right < 0):
                    value = -value
            # 本次运算结果作为一个新的操作数，供外层表达式使用。
            stack.append(value)
        return stack[0]
'''.strip(),
 'code_notes':['合法表达式保证每次运算前至少有两个操作数，也保证最后只剩一个值。','(left<0)!=(right<0) 表示恰好一方为负，布尔值不同即符号相反。','整除分支的 right 非零由题目保证。'],
 'pitfalls':['弹出顺序写反会使减法、除法得到错误结果。','直接用 // 无法满足负数向零截断。','把 "-11" 拆成运算符和数字会破坏 token 已给定的边界。'],
 'complexity':'时间 O(T)，T 为全部 token 字符总量，包含数字转换；在题目整数范围内每次算术为常数成本。栈额外空间 O(m)，m 为 token 数。',
 'quiz':{'question':'["5","2","-"] 的结果为什么是 3？','answer':'栈顶 2 先弹出作为右操作数，5 后弹出作为左操作数，按 left-right 得到 5-2=3。'},
 'tests':{'method':'evalRPN','cases':[{'args':[['4','13','5','/','+']],'expected':6},{'args':[['-7','3','/']],'expected':-2},{'args':[['7','-3','/']],'expected':-2},{'args':[['-7','-3','/']],'expected':2},{'args':[['5','2','-']],'expected':3},{'args':[['2','1','+','3','*']],'expected':9},{'args':[['-11']],'expected':-11}]}
})

CHAPTER['problems'].append({
 'id':394,'slug':'decode-string',
 'summary':'按 k[片段] 规则解码，括号可以嵌套，k 可能有多位。输入格式保证合法，数字只用于重复次数，字母才是正文。',
 'baseline':'反复查找最内层括号并替换整段字符串，会重复扫描并复制许多无关前缀。顺序扫描时保存外层上下文，遇到闭括号就完成当前层，能清楚地控制每段的组装过程。',
 'insight':'进入 [ 时，外层已经累积的片段与本次重复次数都暂时不能丢弃，先一起压栈；当前层从空列表开始。遇到 ] 时，当前层先连接、重复，再作为一个完整片段交还外层。栈正好对应嵌套层次。',
 'steps':['parts 保存当前层已经完成的字符串片段，count 累积多位重复次数。','读数字时 count=count×10+本位数字。','读 [ 时压入 (parts,count)，然后建立新的空 parts 并把 count 清零。','读 ] 时弹出 parent、repeat，将当前层连接并重复 repeat 次，追加到 parent，再令 parts=parent。','读字母时直接追加到 parts；扫描结束后连接顶层片段。'],
 'invariant':'当前 parts 中各项都是本层已经完成的相邻片段，按顺序连接就是本层当前已解码前缀；栈中每一项保存对应未闭合外层的前缀与进入下一层时的重复次数。闭括号只完成最近一层，把其结果追加回父层，因而每个嵌套关系都按从内到外的顺序展开。',
 'examples':[{'label':'外层等待内层完成','input':'s="3[a2[c]]"','output':'"accaccacc"','frames':[
  {'title':'读取 3[，保存外层状态','note':'顶层前缀为空，压入 ([],3)，新当前层从空开始，随后读到 a。','diagram':'栈底 [ (顶层空前缀, 3) ] 栈顶\n当前 parts=["a"]'},
  {'title':'读取 2[，再保存一层','note':'压入 (["a"],2)，开始读取最内层 c；两次重复次数不能共用同一个未保存变量。','diagram':'栈：[ ([],3), (["a"],2) ]\n当前 parts=["c"]'},
  {'title':'第一个 ] 得到 cc，返回 a 所在层','note':'把 c 重复 2 次得到 cc，追加到父层 ["a"]，当前 parts 变成 ["a","cc"]。','diagram':'栈：[ ([],3) ]\n当前 parts=["a","cc"] → "acc"'},
  {'title':'第二个 ] 把 acc 重复三次','note':'连接当前层得到 acc，再重复 3 次，将完整结果交回顶层。','diagram':'"acc" × 3 → "accaccacc"\n栈为空，顶层 parts=["accaccacc"]'}
 ]},{'label':'多位次数必须逐位累积','input':'s="12[a]b"','output':'"aaaaaaaaaaaab"','frames':[
  {'title':'读 1 再读 2，count 变为 12','note':'不能把后读到的 2 直接覆盖成重复次数。','equation':'0×10+1=1；1×10+2=12','diagram':'count：0 → 1 → 12'},
  {'title':'闭合后还有顶层字母 b','note':'展开 12 个 a 后，b 仍属于顶层，直接追加，最终长度为 13。','diagram':'顶层 parts=["aaaaaaaaaaaa", "b"]\n连接 → "aaaaaaaaaaaab"'}
 ]}],
 'walkthrough':['parts 是列表对象，压栈保存的是这个父层列表的引用。进入内层时赋 parts=[] 创建新列表，不会清空已经保存的父层。若写 parts.clear()，反而会把父层数据一起清掉。','用列表保存字母和完整片段，最后统一 join，避免每读一个字母就复制整个当前字符串。','输出长度 L 可能远大于输入长度 n，因此时间不可能只与 n 有关。嵌套关闭时还会重复组装中间字符串，需要计入这些真实复制成本。'],
 'code':'''
class Solution:
    def decodeString(self, s: str) -> str:
        stack = []
        # parts 收集当前括号层的字符串片段，避免逐字符拼接完整字符串。
        parts = []
        count = 0
        for ch in s:
            if '0' <= ch <= '9':
                # 重复次数可能有多位，必须逐位累计。
                count = count * 10 + int(ch)
            elif ch == '[':
                # 遇到左括号时保存外层片段和重复次数，开始一个独立的内层。
                stack.append((parts, count))
                parts = []
                count = 0
            elif ch == ']':
                # 遇到右括号时完成内层，把重复后的结果追加到外层。
                parent, repeat = stack.pop()
                parent.append(''.join(parts) * repeat)
                # 回到上一层继续解析，而不是丢掉括号前的内容。
                parts = parent
            else:
                parts.append(ch)
        return ''.join(parts)
'''.strip(),
 'api':{'signature':'str.join(iterable_of_str) -> str\ntext * count -> str','description':['"".join(parts) 按顺序连接字符串片段，返回新字符串；不会原地修改 parts。所有元素必须是字符串。','字符串乘法按整数次数重复字符串，返回重复结果。本题 count 为正整数；产生长度很大的结果必须付出相应的构造成本。']},
 'code_notes':['count 在进入 [ 后清零，下一组次数从零开始累积。','parent.append 后 parts=parent 回到外层，而不是丢掉父层原前缀。','不会遍历新展开出来的字符作为编码再次解析，它们只作为正文片段连接。'],
 'pitfalls':['多位次数不能只保留最后一位。','压栈后调用 parts.clear() 会修改同一份父层列表，丢失外层前缀。','不能把复杂度写成只扫描编码一次所以 O(n)，因为复制展开字符串可能远大于 n。'],
 'complexity':'设输入长 n、输出长 L、最大嵌套深度 d。时间为 O(n + 各层实际组装字符数)，上界可写 O(n+(d+1)L)，不是无条件 O(n+L)。峰值辅助空间 O(n+L)，包括栈、片段与组装中的字符串；题目保证输出长度不超过 10⁵。',
 'quiz':{'question':'处理 2[a]3[b] 时，第一次 ] 之后为什么还能正确读取第二组？','answer':'第一次闭合把 aa 作为一个完整片段放回顶层，count 已在进入第一组时清零。接着读 3 得到新的重复次数，父层前缀 aa 会在第二个 [ 时保存，最后连接为 aabbb。'},
 'tests':{'method':'decodeString','cases':[{'args':['3[a2[c]]'],'expected':'accaccacc'},{'args':['12[a]b'],'expected':'aaaaaaaaaaaab'},{'args':['2[a]3[b]'],'expected':'aabbb'},{'args':['2[abc]3[cd]ef'],'expected':'abcabccdcdcdef'},{'args':['abc'],'expected':'abc'},{'args':['1[a1[b]]'],'expected':'ab'}]}
})

CHAPTER['problems'].append({
 'id':227,'slug':'basic-calculator-ii',
 'summary':'计算由非负整数、空格和 +、−、*、/ 构成的合法表达式，没有括号。乘除优先于加减，同优先级从左到右，除法向零截断，不能使用 eval。',
 'baseline':'把所有操作从左到右直接计算，会把 3+2*2 算成 10；先整体分词再实现完整表达式树虽然可行，但本题只有两级优先级，可以更直接地维护加法项。',
 'insight':'把减法变成加入负项，把乘除立即合并到最近一个项。这样栈里只保留已经完成乘除的带符号加法项，最后求和即可。扫描到新运算符时，才说明前一个数字读完整；此时处理的是数字前面的旧运算符。',
 'steps':['stack 保存加法项，number=0，op="+" 表示第一个数字前有隐含加号。','顺序读数字，逐位累积 number；空格跳过。','遇到运算符时按旧 op 处理 number：加号压正数，减号压负数，乘除弹出最后一项并更新后压回。','记录当前运算符为新的 op，将 number 清零。','在扫描末尾附加一个虚拟 +，触发最后数字结算；最终返回 sum(stack)。'],
 'invariant':'每次结算一个数字后，stack 的和等于已经完整处理的表达式前缀值，其中最后一项仍可与后续乘除合并。加减开启新项，乘除只修改当前项，因而高优先级不会越过加减分界；连续乘除按照遇到的顺序结算，保持左结合。',
 'examples':[{'label':'先乘除，后求各项之和','input':'s="3+2*2"','output':'7','frames':[
  {'title':'遇到 +，按初始 op=+ 结算 3','note':'数字 3 入栈，记录新 op=+，开始读取下一个数字。','array':[3],'array_label':'已保存的加法项'},
  {'title':'遇到 *，仍先按旧 + 结算 2','note':'第二个数字前的符号是 +，所以先压入 2；随后把 op 更新为 *。','array':[3,2]},
  {'title':'虚拟末尾 + 触发 2*2','note':'弹出最近项 2，与最后读到的 2 相乘后压回 4。前面的 3 不参与这次乘法。','array':[3,4]},
  {'title':'所有乘除完成后求和','note':'栈中两项为 3、4，总和为 7。','diagram':'3 + (2×2) = 3 + 4 = 7'}
 ]},{'label':'负项上的除法仍要向零截断','input':'s="14-3/2"','output':'13','frames':[
  {'title':'减法把第二项记成 -3','note':'读取到 / 时，旧 op 是 -，所以栈为 [14,-3]。','array':[14,-3]},
  {'title':'-3 除以 2 得 -1','note':'用绝对值商 3//2=1，再恢复负号。若直接 -3//2，会得到 -2，导致总和错误。','array':[14,-1],'equation':'14 + (-1) = 13'}
 ]}],
 'walkthrough':['op 表示已经读到但等待右操作数的运算符，当前遇到的字符只是结算上一项的触发器。把这两个时间点混淆，是计算器题的常见错误。','处理减法后，栈顶可能为负数。尽管输入整数都是非负，除法实现仍然必须正确处理负项。','8/3*3 应按 (8/3)*3 得到 6，不能把它改成 8/(3*3) 或先约分。逐次结算保证左结合与每一步的截断语义。'],
 'code':'''
class Solution:
    def calculate(self, s: str) -> int:
        # total 是已经结算的加减项，last 是正在处理的最后一项乘除链。
        total = last = number = 0
        op = '+'
        for i, char in enumerate(s):
            if '0' <= char <= '9':
                number = number * 10 + ord(char) - ord('0')
            # 新运算符或末尾触发结算；末尾即使是空格，也要结算最后一个数。
            if char in '+-*/' or i == len(s) - 1:
                if op == '+':
                    total += last
                    last = number
                elif op == '-':
                    total += last
                    last = -number
                elif op == '*':
                    # 乘除先更新 last，不提前并入 total，保证优先级。
                    last *= number
                else:
                    # 整数除法要求向零截断，负数不能直接使用 Python 的 //。
                    quotient = abs(last) // number
                    last = quotient if last >= 0 else -quotient
                op = char
                number = 0
        return total + last

    # 对照方法：用栈保存所有加减项，乘除立即改写栈顶。
    def calculateStack(self, s: str) -> int:
        stack = []
        number = 0
        op = '+'
        # 末尾哨兵触发最后一次结算，但会额外创建一份字符串。
        for ch in s + '+':
            if '0' <= ch <= '9':
                number = number * 10 + int(ch)
            elif ch != ' ':
                # 根据上一次运算符结算当前数字，新读到的运算符留给下一轮。
                if op == '+':
                    stack.append(number)
                elif op == '-':
                    stack.append(-number)
                elif op == '*':
                    stack.append(stack.pop() * number)
                else:
                    previous = stack.pop()
                    # 负数先取绝对值整除，再恢复符号，满足向零截断。
                    quotient = abs(previous) // number
                    stack.append(quotient if previous >= 0 else -quotient)
                op = ch
                number = 0
        return sum(stack)
'''.strip(),
 'code_notes':['默认 calculate 只保留 total、last、number 与 op，calculateStack 保留栈实现作对照。', '当前字符触发的是旧 op 的运算，不能先把 op 更新成当前字符。', "i 到最后一个字符也会结算，所以不需要 s+'+' 产生额外字符串。"],
 'pitfalls':['遇到 * 时立即把前面所有项相加再乘，会破坏优先级。','不触发最后一个数字的结算，会漏算表达式末项。','直接对负栈顶使用 // 不符合向零截断。','本题没有括号；遇到括号不能靠这段代码自动获得嵌套能力。'],
 'complexity':'默认延迟结算方法时间 O(n)、辅助空间 O(1)，不追加哨兵字符串。对照栈方法时间 O(n)、辅助空间 O(n)。',
 'quiz':{'question':'3+2*2 在读到 * 时，为什么先把 2 压栈，而不是立即乘？','answer':'此时右侧的第二个 2 尚未读取，乘法缺少右操作数。先按数字前的 + 保存当前项，再把 * 记为等待处理的 op，等下一个数字完整后才乘。'},
 'tests':{'method':'calculate','cases':[{'args':['3+2*2'],'expected':7},{'args':['14-3/2'],'expected':13},{'args':[' 3+5 / 2 '],'expected':5},{'args':['8/3*3'],'expected':6},{'args':['42'],'expected':42},{'args':['0-7/3'],'expected':-2},{'args':['1-1+1'],'expected':1}]}
,
 'submission': {'name': '只保留最后一项的延迟结算', 'why': '栈法只会修改栈顶，已经确定的更早加减项可以直接累加，所以默认方法把整个栈压缩成 total 与 last。', 'steps': ['逐位读取 number；遇到运算符或字符串末尾时，按旧运算符结算。', '加减开始新项时，把旧 last 加入 total；乘除则直接更新 last。', '扫描结束返回 total+last。'], 'diagram': '3+2*2：total=3，last=2 → last=4 → 结果 7\n后读到的 * 只修改最后一项，不会错误得到 (3+2)*2'},
})

CHAPTER['problems'].append({
 'id':224,'slug':'basic-calculator',
 'summary':'计算含整数、+、−、括号和空格的合法表达式。本题没有乘除，允许一元负号，例如 -1、-(2+3)，不允许使用 eval。',
 'baseline':'删除括号直接从左向右加减会丢失括号前负号的作用，例如 1-(2+3) 不能变成 1-2+3。每次递归处理括号也可行，但长表达式的嵌套可能触及 Python 递归限制，显式状态栈更稳妥。',
 'insight':'每层只需要 total（已结算值）、number（正在读取的数字）、sign（当前项的符号）。进入括号时，保存外层 total 和作用于整个括号的 sign，内层从零重新计算；退出括号时，把内层值整体乘外层符号，再加回外层累计值。',
 'steps':['初始化 total=0、number=0、sign=1，栈为空。','数字逐位累积。遇到 + 或 −，先把 sign×number 加到 total，再清零 number 并更新 sign。','遇到 (，压入 (total,sign)，然后将当前层重置为 total=0、sign=1、number=0。','遇到 )，先结算内层最后数字，再弹出外层状态，计算 outer_total+outer_sign×内层结果。','输入结束时，结算最外层最后数字并返回。'],
 'invariant':'当前层中，total 是已经结算的各项和，number 是尚未结算的数字前缀，sign 是它所属项的符号；栈由外到内保存尚未完成括号的外层累计值和整组符号。闭括号得到的内层完整值恰好作为外层一个操作数，整体应用外层符号，保持括号语义。',
 'examples':[{'label':'括号前负号作用于整组','input':'s="1-(2+3)"','output':'-4','frames':[
  {'title':'读到 -，外层 total=1、sign=-1','note':'数字 1 已结算，下一个操作数是整个括号。进入 ( 时保存 (1,-1)。','diagram':'外层待恢复：(total=1, sign=-1)\n内层初始化：total=0, sign=1'},
  {'title':'括号内部独立算出 5','note':'读到 + 时结算 2，读到 ) 时结算 3，内层结果为 5。','diagram':'内层：2 + 3 = 5\n栈：[ (1,-1) ]'},
  {'title':'弹出外层，整体应用负号','note':'恢复为 1+(-1)×5=-4，不能只对内部的第一个数字 2 取负。','equation':'outer_total + outer_sign × inner = 1 − 5 = -4','diagram':'1 - (2+3)\n      └─5─┘'}
 ]},{'label':'一元负号与嵌套负号','input':'s="-(-2+1)"','output':'1','frames':[
  {'title':'最前面的 - 让整组符号为负','note':'当前 number=0，结算零不改变 total，sign 改为 -1；进入括号保存 (0,-1)。','diagram':'外层：0 - ( ... )'},
  {'title':'内层开头的 - 表示 0-2','note':'内层从 total=0、sign=1 开始，读 - 后 sign=-1，随后得到 -2+1=-1。','diagram':'内层结果：-1'},
  {'title':'外层再对内层结果取负','note':'0+(-1)×(-1)=1。每一层的 sign 独立保存，不会相互覆盖。','diagram':'-( -1 ) = 1'}
 ]}],
 'walkthrough':['一元负号可以理解为当前层开头的 0 减去下一项，因此初始化 total=0、number=0 让同一套符号处理自然覆盖 -1 和 -(...)。','在 ( 前必须保存的不只是符号，还有已经算好的外层 total。只保存 sign 会丢失例子中的前缀 1。','退出 ) 后，内层已经作为一整个操作数计入外层 total，number 清零，不能在下一个符号处再结算一遍。','本题与第 227 题的重点不同：这里处理括号与一元负号，没有乘除优先级。两段代码各自对应题目允许的语法范围。'],
 'code':'''
class Solution:
    def calculate(self, s: str) -> int:
        stack = []
        # total 是本层已结算结果，number 是当前数，sign 是它前面的符号。
        total, number, sign = 0, 0, 1
        for ch in s:
            if '0' <= ch <= '9':
                number = number * 10 + int(ch)
            elif ch in '+-':
                # 遇到新加减号，先按旧符号结算已经读完的数。
                total += sign * number
                number = 0
                sign = 1 if ch == '+' else -1
            elif ch == '(':
                # 进入括号前保存外层结果与括号前的符号。
                stack.append((total, sign))
                total, number, sign = 0, 0, 1
            elif ch == ')':
                total += sign * number
                number = 0
                # 内层算完后，把整个括号看成一个数，乘外层符号再合并。
                outer_total, outer_sign = stack.pop()
                total = outer_total + outer_sign * total
                sign = 1
        # 末尾没有运算符触发结算，最后一个数还需加进去。
        return total + sign * number
'''.strip(),
 'code_notes':['空格不进入任何分支，所以只被跳过，不会改变当前数字或符号。','每个 ( 压入一对状态，每个 ) 恢复最近的一对，元组中的两个值分别有明确含义。','本题合法语法没有隐式乘法，例如 2(3+4) 不属于需要处理的输入。','显式栈代替递归调用，深层括号不会消耗 Python 递归深度。'],
 'pitfalls':['括号前的负号必须作用于整个内层值。','恢复外层时忘记加 outer_total，会丢失括号之前已算出的部分。','number 不清零会导致已经结算的数字被重复加入。','不能把题目的“允许一元负号”扩展成任意运算符连写，本题输入仍保证语法合法。'],
 'complexity':'时间 O(n)，每个字符只处理一次；额外空间 O(d)，d 为最大括号深度，最坏 O(n)。',
 'quiz':{'question':'1-(-2) 为什么得到 3？','answer':'外层保存 (1,-1)，内层单独得到 -2。退出括号时计算 1+(-1)×(-2)=3，两个负号分别属于不同层的符号。'},
 'tests':{'method':'calculate','cases':[{'args':['1-(2+3)'],'expected':-4},{'args':['-(-2+1)'],'expected':1},{'args':['1-(-2)'],'expected':3},{'args':['(1+(4+5+2)-3)+(6+8)'],'expected':23},{'args':[' 2-1 + 2 '],'expected':3},{'args':['-2147483648'],'expected':-2147483648},{'args':['0'],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':32,'slug':'longest-valid-parentheses',
 'summary':'输入只含 ( 和 )，求最长连续有效括号子串的长度。要求连续，不能把位于不同非法片段中的匹配对数简单相加。',
 'baseline':'枚举所有子串并逐一用括号匹配检查，最直接写法达到 O(n³)。第 20 题只保存括号类型也不能直接计算长度；需要保存下标，并记住当前有效片段不能跨越的边界。',
 'insight':'栈底保存最近一个无法匹配的右括号位置，初始用 -1 表示字符串开始前的边界；栈底之上保存尚未匹配的左括号下标。遇到右括号先弹出一项：若栈空，当前右括号成为新非法边界；否则从新栈顶之后到当前下标就是一个连续有效后缀，长度为 i-stack[-1]。',
 'steps':['初始化 stack=[-1]、best=0。','读到 ( 时压入下标 i。','读到 ) 时先弹栈。若栈变空，压入当前 i 作为新的非法右边界。','若栈未空，用 i-stack[-1] 更新最长长度。','扫描结束返回 best。'],
 'invariant':'栈底是最近无法被有效子串跨过的右括号边界，其上依次是未匹配左括号的位置。成功匹配一个右括号后，新栈顶要么是未匹配的左括号，要么是非法边界；它都不能被纳入以当前 i 结束的有效后缀，而它之后到 i 的所有括号已经配平，因此后缀长度正好是 i-stack[-1]。',
 'examples':[{'label':'非法右括号重置起点','input':'s=")()())"','output':'4','frames':[
  {'title':'下标 0 是无法匹配的右括号','note':'弹出初始 -1 后栈空，改为 [0]，任何后续合法子串都不能跨过这个位置。','array':[')', '(', ')', '(', ')', ')'],'active':[0],'metrics':[['栈','[0]']]},
  {'title':'下标 1、2 形成第一对','note':'1 入栈，再由 2 弹出；新栈顶为 0，长度 2-0=2，对应下标 1..2。','array':[')', '(', ')', '(', ')', ')'],'active':[1,2],'metrics':[['栈','[0]'],['best',2]]},
  {'title':'下标 3、4 与前一对连成连续片段','note':'3 入栈，4 将它弹出；新栈顶仍是 0，长度 4-0=4，自动把相邻的两对 ()() 合并统计。','array':[')', '(', ')', '(', ')', ')'],'active':[1,2,3,4],'metrics':[['best',4]]},
  {'title':'下标 5 再次成为非法边界','note':'它弹出边界 0 后使栈空，更新栈为 [5]。历史 best=4 保留，不会被当前失败重置。','array':[')', '(', ')', '(', ')', ')'],'active':[5],'metrics':[['栈','[5]'],['返回',4]]}
 ]},{'label':'未匹配左括号也是长度边界','input':'s="(()"','output':'2','frames':[
  {'title':'前两个左括号下标依次入栈','note':'栈为 [-1,0,1]，初始边界和两个未匹配左括号各有作用。','diagram':'栈底 [-1, 0, 1] 栈顶'},
  {'title':'下标 2 匹配下标 1','note':'弹出 1 后，栈顶为 0。有效后缀长度 2-0=2；不能减去 -1 把尚未匹配的下标 0 算进去。','diagram':'( [()]\n↑ 未匹配边界 0\n有效区间下标 1..2，长度 2'}
 ]}],
 'walkthrough':['初始 -1 是下标哨兵，不是实际字符。若输入 ()，下标 1 匹配后栈顶仍为 -1，长度 1-(-1)=2，省去“从头开始”的特殊分支。','栈底的非法右括号不表示一次待完成匹配，它只承担长度边界。之后遇到无法匹配的右括号时，旧边界会被弹掉并替换。','更新的是连续有效后缀长度，best 再记录所有右端点中的最大值，因此可以同时处理嵌套 (()) 和串联 ()()。'],
 'code':'''
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        best = 0
        left = right = 0
        # 正向扫描：右括号比左括号多时，这一段前缀不可能被后续修复。
        for char in s:
            if char == '(':
                left += 1
            else:
                right += 1
            if left == right:
                best = max(best, 2 * right)
            elif right > left:
                left = right = 0
        # 反向再扫一次，补上正向无法结算的多余左括号情况，如 (()。
        left = right = 0
        for char in reversed(s):
            if char == '(':
                left += 1
            else:
                right += 1
            if left == right:
                best = max(best, 2 * left)
            elif left > right:
                left = right = 0
        return best

    def longestValidParenthesesStack(self, s: str) -> int:
        # 对照栈法：栈底记录当前有效段之前的边界，-1 允许有效段从下标 0 开始。
        stack = [-1]
        best = 0
        for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            else:
                # 右括号尝试匹配最近的左括号；弹空说明当前右括号无法匹配。
                stack.pop()
                if not stack:
                    # 无法匹配的右括号成为新边界，之后的有效长度从它后面重新计算。
                    stack.append(i)
                else:
                    # 栈顶是最近的未匹配位置，它之后到当前下标构成有效后缀。
                    best = max(best, i - stack[-1])
        return best
'''.strip(),
 'code_notes':['默认使用正反两个方向的计数；reversed(s) 是反向迭代器，不创建 s[::-1] 副本。', '正向重置条件为 right>left，反向则是 left>right，两个条件不能混用。', '下标栈保留为 longestValidParenthesesStack，方便对照原先的边界推导。'],
 'pitfalls':['只计数匹配括号对，会把不连续的片段相加。','成功弹出左括号后，用被弹出位置计算长度会漏掉外层嵌套或前面串联的有效段。','初始不用 -1 却仍套用同样的长度公式，会漏算从下标 0 开始的有效子串。'],
 'complexity':'默认双向计数时间 O(n)、额外空间 O(1)。对照下标栈时间 O(n)、额外空间 O(n)。',
 'quiz':{'question':'为什么在成功匹配后要减“新的栈顶”，而不是刚刚弹出的左括号下标？','answer':'刚弹出的左括号只定位当前这对括号的开始；新的栈顶才是整个连续有效后缀之前仍未解决的边界。减去它可以包含已经配好的内层或前面相邻的有效括号。'},
 'tests':{'method':'longestValidParentheses','cases':[{'args':[')()())'],'expected':4},{'args':['(()'],'expected':2},{'args':[''],'expected':0},{'args':['()(())'],'expected':6},{'args':['((('],'expected':0},{'args':['())()'],'expected':2}]}
,
 'submission': {'name': '双向计数', 'why': '默认方法用两次扫描替代下标栈，保持线性时间并把辅助空间降到 O(1)。前面的栈边界例子对应 longestValidParenthesesStack。', 'steps': ['从左到右统计左右括号数，相等时更新有效长度，右括号过多则重置。', '从右到左再次统计，相等时更新，左括号过多则重置。', '两次扫描互补，覆盖多余左括号或多余右括号造成的边界。'], 'diagram': '(()：正向末尾计数 2≠1，漏掉后面的 ()\n反向先读 )、(，计数相等 → 找到长度 2'},
})

CHAPTER['problems'].append({
 'id':739,'slug':'daily-temperatures',
 'summary':'对每一天，返回还要等多少天才会出现严格更高的温度。后面没有更暖日子则为 0；相同温度不能作为答案。',
 'baseline':'对每一天向右逐日查找，第一个更高值即答案，最坏遇到持续降温会做 O(n²) 次比较。可以反过来思考：新一天到来时，它能解决哪些旧日子尚未找到答案的问题？',
 'insight':'栈保存还在等待更暖日子的下标，其温度从底到顶非递增。新温度比栈顶高，就为栈顶找到了右侧第一个更大值；弹出并记录距离，继续帮助更早的候选。新温度不够高时，将今天也加入等待队伍。',
 'steps':['答案数组初始化为零，栈为空。','枚举今天下标 i 与温度 t。','只要栈非空且 t>temperatures[栈顶]，弹出 old 并设置 answer[old]=i-old。','把 i 入栈；扫描结束后仍在栈中的下标没有更暖日子，保持零。'],
 'invariant':'栈中的下标递增，温度非递增，每个下标右侧到当前扫描位置之前都未出现更高温度。当前 t 能弹出 old 时，它比 old 高，而此前没有更高值，因此当前 i 就是最近答案。被结算的下标不再需要保留，剩余栈仍保持等待与单调性质。',
 'examples':[{'label':'新温度一次解决多天','input':'[73,74,75,71,69,72,76,73]','output':'[1,1,4,2,1,1,0,0]','frames':[
  {'title':'74、75 依次解决前一天','note':'下标 1 的 74 解决下标 0；下标 2 的 75 解决下标 1，两者等待天数都为 1。栈剩 [2:75]。','array':[73,74,75,71,69,72,76,73],'active':[0,1,2],'metrics':[['已知答案','[1,1,0,0,0,0,0,0]']]},
  {'title':'71、69 都继续等待','note':'温度下降时没有旧问题能被解决，栈为 [2:75,3:71,4:69]，右端是栈顶。','table':{'headers':['栈顺序','下标','温度'],'rows':[['底',2,75],['中',3,71],['顶',4,69]]}},
  {'title':'72 同时解决 69 与 71','note':'下标 5 先弹出 4，距离 1；再弹出 3，距离 2。它还不够暖，不能解决 75。','diagram':'72 > 69 → answer[4]=5−4=1\n72 > 71 → answer[3]=5−3=2\n72 < 75 → 停止弹出\n新栈：[2:75,5:72]'},
  {'title':'76 再解决 72 与 75','note':'下标 6 比两者都高，answer[5]=1、answer[2]=4。75 等了四天，说明不能只比较相邻天。','diagram':'76 > 72 → answer[5]=1\n76 > 75 → answer[2]=4\n栈：[6:76]'},
  {'title':'最后 76、73 均没有后续更暖日','note':'下标 7 的 73 入栈，扫描结束，未解决下标 6、7 保持零。','array':[1,1,4,2,1,1,0,0],'array_label':'每一天的等待天数'}
 ]}],
 'walkthrough':['保存下标才能计算等待距离；只保存温度会丢失发生日期，也难以区分多个同温度日子。','若温度相等，旧日子仍然没有遇到严格更高值，不能弹出。因此栈中允许等温元素同时存在。','一个新值可能弹出很多旧值，但每个下标只出栈一次，所有 while 循环合计至多 n 次。'],
 'code':'''
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        answer = [0] * len(temperatures)
        # 栈里存尚未等到更高温度的日期下标，温度从栈底到顶非递增。
        stack = []
        for i, temperature in enumerate(temperatures):
            # 新温度能解决栈顶的等待问题，连续弹出所有更冷的日期。
            while stack and temperature > temperatures[stack[-1]]:
                old = stack.pop()
                # 当前日期减旧日期，才是等待天数。
                answer[old] = i - old
            # 当前日期等待未来来解决；最终仍在栈中的日期保持答案 0。
            stack.append(i)
        return answer
'''.strip(),
 'code_notes':['初始零恰好表示后面没有更暖日子，因此无需扫描结束后逐项清理答案。','stack[-1] 是下标，要通过 temperatures 读取对应温度。','输入数组只读，结果另建列表。'],
 'pitfalls':['把 > 写成 >= 会把等温日误当更暖日。','记录当前温度差而非下标差，不符合返回等待天数的要求。','弹出一个就停止，会漏掉当前高温能同时解决的多个旧日子。'],
 'complexity':'时间 O(n)，每个下标入栈、出栈各至多一次；辅助栈 O(n)，答案列表另占 O(n)。',
 'quiz':{'question':'[70,70,71] 中两个 70 的答案分别是什么？','answer':'分别为 2、1。第二个 70 不会弹出第一个 70；71 到来时依次弹出两者，并根据各自下标计算不同等待距离。'},
 'tests':{'method':'dailyTemperatures','preserve_args':[0],'cases':[{'args':[[73,74,75,71,69,72,76,73]],'expected':[1,1,4,2,1,1,0,0]},{'args':[[70,70,71]],'expected':[2,1,0]},{'args':[[80,70,60]],'expected':[0,0,0]},{'args':[[30]],'expected':[0]},{'args':[[30,40,50]],'expected':[1,1,0]}]}
})

CHAPTER['problems'].append({
 'id':42,'slug':'trapping-rain-water',
 'summary':'非负整数数组表示单位宽度柱子的高度，求降雨后柱子之间最多能存多少水。本题给出单调栈主解，并在同一份代码中提供常数空间双指针解法作比较。',
 'baseline':'逐列计算左侧最高墙与右侧最高墙，再取较小者减去当前高度，若每列都重新扫描两边就是 O(n²)。预存左右最高值可以线性化但占 O(n) 空间；单调栈换成按水层结算，双指针则按可确定水位的一侧结算。',
 'insight':['单调栈保存从底到顶非递增的柱子下标。新柱比栈顶高时，栈顶可作为凹槽底 bottom；弹出后若还有栈顶 left，它是左墙，当前 i 是右墙。新增水层高度为 min(height[left],height[i])−height[bottom]，宽度为 i−left−1。','双指针保存已知左侧最高墙 left_max 和右侧最高墙 right_max。若 left_max≤right_max，左指针对应列的右边已有不低于 left_max 的墙，因此该列水位可确定为 left_max；反之确定右列。两种方法分别按横向水层和竖向水列计数。'],
 'steps':['栈解法枚举右墙 i；当新柱更高时弹出 bottom。','若弹出后栈空，说明缺少左墙，不能蓄水，结束本轮弹出。','否则用新栈顶作为 left，计算水层高和宽，累加面积，继续处理更深或更早的凹槽。','将当前下标 i 入栈。','双指针变体每轮更新两端最高墙，只结算最高墙较低的一侧并向内移动，直到全部列处理完。'],
 'invariant':['栈中保留尚未被右墙完整结算的非递增边界；弹出的底部上方、当前左右墙之间的这一层水此前没有计入。较低层先结算，后续弹出较高底部只补上更高的一层，水层互不重复。没有左墙时水会流走，不能使用宽度公式。','双指针每次结算一列：较低的已知最高墙限制该列水位，另一侧已经有足够高的墙作为保证。尚未扫描的内部柱可能抬高另一边最高值，但不能降低这个已经确定的限制，因此安全收缩一侧。'],
 'examples':[{'label':'按不重叠的水层累计','input':'height=[4,2,0,3,2,5]','output':'9','frames':[
  {'title':'4、2、0 形成下降边界','note':'栈为 [0:4,1:2,2:0]，还没有右墙，暂不结算水量。','array':[4,2,0,3,2,5],'active':[0,1,2],'metrics':[['water',0]]},
  {'title':'右墙 3 先填最底部，再补上一层','note':'i=3 时先弹 bottom=2，left=1，高 2、宽 1，水量 2；再弹 bottom=1，left=0，高 1、宽 2，再加 2。','table':{'headers':['左/底/右下标','层高','宽度','新增'],'rows':[['1 / 2 / 3',2,1,2],['0 / 1 / 3',1,2,2]]},'metrics':[['累计',4]]},
  {'title':'末尾 5 先填下标 4 上方的一格','note':'i=5 时弹出 bottom=4，左墙为下标 3，高 min(3,5)-2=1，宽 1，累计变成 5。','array':[4,2,0,3,2,5],'active':[3,4,5],'metrics':[['累计',5]]},
  {'title':'再补上高度 3 到 4 的整层','note':'弹出 bottom=3，左墙下标 0，高 min(4,5)-3=1，宽 5-0-1=4，再加 4，总量 9。网格从上到下为高度 5 到 1，■ 是柱体、≈ 是水、· 是空中；绿色标出本次新增的四格水。随后弹出 0 时没有左墙，不再增加。','grid':[['·','·','·','·','·','■'],['■','≈','≈','≈','≈','■'],['■','≈','≈','■','≈','■'],['■','■','≈','■','■','■'],['■','■','≈','■','■','■']],'active_cells':[[1,1],[1,2],[1,3],[1,4]],'table':{'headers':['水层','新增'],'rows':[['前面已算',5],['高度 3→4，跨度四列',4],['总量',9]]}}
 ]},{'label':'同一个例子按列结算','input':'height=[4,2,0,3,2,5]，使用 trapTwoPointers','output':'9','frames':[
  {'title':'右侧最高墙 5 足够高','note':'左侧依次处理前五列时 left_max=4≤right_max=5，所以每列水位都可以按 4 确定。','diagram':'已知左墙：4\n已知右墙：5\n前五列水位受左墙 4 限制'},
  {'title':'逐列水量为 0、2、4、1、2、0','note':'最后一列是高度 5 的墙，水量为 0。六列之和仍为 9，与水层划分结果一致。','table':{'headers':['列下标',0,1,2,3,4,5],'rows':[['柱高',4,2,0,3,2,5],['水量',0,2,4,1,2,0]]}}
 ]}],
 'walkthrough':['在 i=3 处，底部 0 上方先填到 2，再把跨越两列的一层从 2 填到 3，因此不是重复给同一水格计数。','宽度 i-left-1 排除了左右两根墙，只有中间的列能在这一层蓄水。','栈中相同高度允许保留，某些弹出会得到层高零，增加零水量也正确。','双指针判断依据是两侧已经见过的最高墙，而不是简单比较当前列能否形成局部凹槽。代码单独命名 trapTwoPointers，可与主方法对同一输入比较。'],
 'code':'''
class Solution:
    def trap(self, height: list[int]) -> int:
        # 推荐主解：双指针，时间 O(n)、额外空间 O(1)。
        left, right = 0, len(height) - 1
        # 分别记录已扫描的左侧最高墙和右侧最高墙。
        left_max = right_max = 0
        water = 0
        while left <= right:
            # 先把当前墙计入最高值，保证当前格的水量不会为负。
            left_max = max(left_max, height[left])
            right_max = max(right_max, height[right])
            # 右侧已知有足够高的墙，左格水位确定为 left_max，可安全结算并前进。
            if left_max <= right_max:
                water += left_max - height[left]
                left += 1
            else:
                # 反之右格水位由 right_max 决定，只移动右指针。
                water += right_max - height[right]
                right -= 1
        return water

    # 对照单调栈：按水平水层结算，同为线性时间，但需要线性辅助空间。
    def trapStack(self, height: list[int]) -> int:
        stack = []
        water = 0
        for i, current in enumerate(height):
            while stack and current > height[stack[-1]]:
                # 弹出的柱子作为这一层凹槽的底，栈中还需要保留左墙。
                bottom = stack.pop()
                # 没有左墙时无法围成水槽，不能继续计算这一层。
                if not stack:
                    break
                left = stack[-1]
                # 水层高度由两墙较矮者减槽底决定，宽度不包含左右墙本身。
                depth = min(height[left], current) - height[bottom]
                water += depth * (i - left - 1)
            stack.append(i)
        return water

    def trapTwoPointers(self, height: list[int]) -> int:
        # 保留具名接口便于对照；默认提交入口已经使用同一高效实现。
        return self.trap(height)
'''.strip(),
 'code_notes':['默认 trap 即双指针实现；trapStack 保留单调栈对照，trapTwoPointers 是同一主解的具名接口。', '先更新两端最高值，再比较哪一侧水位已经确定；结算后只移动这一侧。', '前文按水层绘制的例子说明同一总水量，主解则按列累计，二者计数角度不同。'],
 'pitfalls':['没有左墙时不能结算，即使右边出现很高的柱子也不能阻止水从左边流走。','把层高直接写成右墙减底部，会忽略较矮左墙的限制。','宽度包含左右墙会多算两列。','“容器最多水量”第 11 题只选两根边界，本题需要累计所有凹槽，不能直接复用面积最大值公式。'],
 'complexity':'推荐双指针时间 O(n)、额外空间 O(1)。对照单调栈时间 O(n)、额外空间 O(n)。',
 'quiz':{'question':'[3,2,1] 为什么接不到水？','answer':'右侧一直降低，没有足够高的右墙封住任何列。栈法没有能形成双墙的弹出；逐列的 min(左最高,右最高) 都等于本列高度，因此每列水量为零。'},
 'tests':{'method':'trap','preserve_args':[0],'cases':[{'args':[[4,2,0,3,2,5]],'expected':9},{'args':[[0,1,0,2,1,0,1,3,2,1,2,1]],'expected':6},{'args':[[3,2,1]],'expected':0},{'args':[[2,0,2]],'expected':2},{'args':[[2,2,2]],'expected':0},{'args':[[0]],'expected':0}]}
,
 'submission': {'name': '双指针结算水位', 'why': '默认 trap 使用 O(1) 辅助空间的双指针。前面的单调栈推演用于理解按水层计数，对应保留的 trapStack 对照方法。', 'steps': ['从两端向中间扫描，维护各自已见最高墙。', '当 left_max≤right_max，右边已存在不低于 left_max 的墙，因此当前位置的左格水位可以确定。', '结算较低最高墙一侧的水量，再移动该侧指针；每格只结算一次。'], 'diagram': 'left_max ≤ right_max → 左格水量 = left_max-height[left]\nleft_max > right_max → 右格水量 = right_max-height[right]'},
})

CHAPTER['problems'].append({
 'id':84,'slug':'largest-rectangle-in-histogram',
 'summary':'每根柱宽为 1，求完全落在柱状图内部的最大矩形面积。矩形可以横跨多根柱，高度由覆盖区间中的最矮柱限制。',
 'baseline':'枚举左右边界并逐步维护区间最小高度，可在 O(n²) 时间计算所有矩形。换成固定矩形高度考虑：每根柱作为限制高度时，应尽量向两边扩展到更矮柱之前。单调栈可以在右边界出现时完成这次结算。',
 'insight':'维护高度严格递增的下标栈。当前高度不高于栈顶时，弹出 top：弹出后的新栈顶是其左侧较矮边界，当前 i 是本次右侧结算位置，宽度为 i-left-1。当前更矮时，这就是 top 的最大扩展；当前等高时，先结算较窄范围，再由右侧同高柱继承更左的边界，未来覆盖更宽矩形。',
 'steps':['初始化空栈和 best=0，额外扫描一个高度为 0 的虚拟尾柱。','当前高度 <= 栈顶高度时，弹出 top。','left 为弹出后的栈顶下标，栈空则为 -1；用 heights[top]×(i-left-1) 更新答案。','持续弹出直到栈顶高度严格小于当前高度，然后将当前下标入栈。','虚拟尾柱会结算所有尚未处理的正高度柱，返回最大面积。'],
 'invariant':'栈内下标递增、柱高严格递增。对栈中一根柱，它与前一个栈元素之间已经被移除的柱都不比它低，因此前一个栈元素给出可扩展范围左侧的较矮边界。当前出现更矮柱时，弹出的柱不能再向右越过当前 i，宽度恰好确定。等高替换时，新柱继承旧柱左侧较矮边界，能在未来代表同一高度取得至少同样宽的矩形，不会丢失最优解。',
 'examples':[{'label':'更矮柱让高矩形的宽度确定','input':'heights=[2,1,5,6,2,3]','output':'10','frames':[
  {'title':'先处理 2、1，再压入 5、6','note':'下标 1 的高度 1 结算高度 2 的面积 2；随后栈为 [1:1,2:5,3:6]，高度严格递增。','array':[2,1,5,6,2,3],'active':[1,2,3],'metrics':[['best',2]]},
  {'title':'下标 4 的高度 2 先结算高度 6','note':'弹出下标 3 后 left=2，宽 4-2-1=1，面积 6。高度 6 不能跨过当前更矮的 2。','table':{'headers':['高度','左边界','右边界','宽','面积'],'rows':[[6,2,4,1,6]]}},
  {'title':'继续结算高度 5，覆盖两列','note':'再弹出下标 2，left=1，宽 4-1-1=2，面积 10，对应原下标 2、3 的两根柱。网格从上到下为高度 6 到 1，■ 为柱体、· 为空；绿色的五行两列恰好构成面积 10 的矩形。','array':[2,1,5,6,2,3],'active':[2,3],'grid':[['■' if height>=level else '·' for height in [2,1,5,6,2,3]] for level in range(6,0,-1)],'active_cells':[[row,col] for row in range(1,6) for col in [2,3]],'equation':'高度 5 × 宽度 2 = 10'},
  {'title':'虚拟尾柱结算剩余候选','note':'到 i=6、current=0 时，依次结算高度 3 的面积 3、高度 2 的面积 8、高度 1 的面积 6，均不超过 10。','table':{'headers':['被结算高度','宽','面积'],'rows':[[3,1,3],[2,4,8],[1,6,6]]}}
 ]},{'label':'等高柱把更宽机会交给右侧','input':'heights=[2,2]','output':'4','frames':[
  {'title':'第二个 2 到来，先弹出第一个 2','note':'结算第一个柱的宽度 1、面积 2；栈清空后，第二个 2 的左边界也变为 -1。','diagram':'旧候选：下标 0，高度 2，当前面积 2\n新候选：下标 1，高度 2，继承左边界 -1'},
  {'title':'虚拟尾柱让第二个 2 覆盖两列','note':'i=2、left=-1，宽度 2-(-1)-1=2，面积 4，等高替换没有漏掉跨两列的答案。','array':[2,2],'active':[0,1],'equation':'2 × 2 = 4'}
 ]}],
 'walkthrough':['栈保存下标而非高度，才能计算左右边界之间的距离。被弹出柱子的下标不直接决定宽度，新栈顶才是左侧阻挡位置。','这里使用 >= 弹出，目的是让栈高度严格递增。等高时的当前 i 不是严格更矮右边界，所以此时只做一次可行面积结算；更大范围由替代它的新同高柱负责。','虚拟尾柱只通过 current=0 表示，不向 heights 真正追加元素。它的下标 n 在最后一次入栈后不会再被读取，因而不发生 heights[n] 越界。','高度为零的矩形面积始终为零，虚拟尾柱把零高候选弹出也不影响答案。'],
 'code':'''
class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        # 栈中保存尚未确定右边界的柱子下标。
        stack = []
        best = 0
        n = len(heights)
        for i in range(n + 1):
            # 多扫描一个高度为 0 的虚拟位置，用来结算剩余柱子；不改原数组。
            current = heights[i] if i < n else 0
            # 遇到更矮或等高的柱子时，弹出旧柱并结算它能形成的矩形。
            while stack and heights[stack[-1]] >= current:
                top = stack.pop()
                # 弹出后，新栈顶是左边更矮的边界；没有则用 -1 作哨兵。
                left = stack[-1] if stack else -1
                # 矩形在左右边界之间，不包含边界本身，宽度要减 1。
                width = i - left - 1
                best = max(best, heights[top] * width)
            stack.append(i)
        return best
'''.strip(),
 'code_notes':['在循环读到 i=n 之前，栈中全是合法原下标；n 只在最后一步压入，此后循环结束。','left=-1 表示可以扩展到数组最左端，统一宽度公式。','当前柱可能一次触发多个候选结算，必须用 while 而非 if。'],
 'pitfalls':['宽度写成 i-top 会漏掉 top 左侧仍可覆盖的柱。','没有尾部结算，在单调递增输入上会漏掉绝大多数候选。','使用 >= 与使用 > 时，等高柱的不变量不同，不能只改符号而继续声称左右边界都严格更矮。','面积应乘被弹出柱的高度，而不是当前更矮柱的高度。'],
 'complexity':'时间 O(n)，每个原下标至多入栈、出栈一次；辅助空间 O(n)，原数组不变。',
 'quiz':{'question':'[1,2,3] 中最后一个原柱到来时没有弹栈，为什么算法仍能找到面积 4？','answer':'虚拟尾柱 0 会依次弹出高度 3、2、1。高度 2 被弹出时左边界为下标 0，右边界为虚拟下标 3，宽度 2，面积为 4。'},
 'tests':{'method':'largestRectangleArea','preserve_args':[0],'cases':[{'args':[[2,1,5,6,2,3]],'expected':10},{'args':[[2,2]],'expected':4},{'args':[[1,2,3]],'expected':4},{'args':[[0]],'expected':0},{'args':[[2,4]],'expected':4},{'args':[[2,0,2]],'expected':2}]}
})

CHAPTER['problems'].append({
 'id':239,'slug':'sliding-window-maximum',
 'summary':'大小固定为 k 的窗口从数组左侧逐格移动，返回每个完整窗口的最大值。1≤k≤数组长度，最大值相同的窗口也要分别输出。',
 'baseline':'对每个窗口调用 max，需要 O(nk) 时间。只记录当前最大值及其位置，在它过期后仍然可能不得不重新扫描整个窗口。单调队列同时保留若干有可能接任最大值的候选。',
 'insight':'队列保存窗口内的下标，下标递增、对应值严格递减。新值 x 到来时，队尾所有不大于 x 的旧值都可永久删除：新值至少一样大，又更晚过期，所以只要旧值还在未来窗口中，新值也一定在且不会更差。队首则按窗口左边界删除过期下标，剩余队首就是最大值。',
 'steps':['使用 deque 保存候选下标，answer 保存每个窗口结果。','处理下标 i 时，先从队首移除 <=i-k 的过期下标。','从队尾移除值 <=nums[i] 的候选，再将 i 追加到队尾。','当 i≥k−1 时，窗口已完整，记录 nums[queue[0]]。','继续移动，最后返回 answer。'],
 'invariant':'每轮处理完 i 后，队列下标都属于当前窗口，按时间递增，值严格递减。被队尾淘汰的值总有一个更晚、至少同样大的候选替代它；替代者若再被淘汰，还会有更强且更晚的替代者，因此任何可能成为最大值的机会都被保留。队首未过期且值最大，恰好是当前窗口最大值。',
 'examples':[{'label':'过期与被新值淘汰是两种删除','input':'nums=[1,3,-1,-3,5,3,6,7]，k=3','output':'[3,3,5,5,6,7]','frames':[
  {'title':'第一个窗口 [1,3,-1]','note':'3 到来时淘汰队尾 1，因为更大且更晚；-1 保留为未来候选。队列为 [1:3,2:-1]，队首给出最大值 3。','array':[1,3,-1,-3,5,3,6,7],'active':[0,1,2],'metrics':[['候选','[1:3,2:-1]'],['输出','[3]']]},
  {'title':'窗口 [3,-1,-3] 仍由 3 主导','note':'-3 比队尾 -1 小，只追加；队列为 [1:3,2:-1,3:-3]，最大值仍为 3。','array':[1,3,-1,-3,5,3,6,7],'active':[1,2,3],'metrics':[['输出','[3,3]']]},
  {'title':'5 到来，先处理旧 3 的过期','note':'i=4，窗口左端为 2；下标 1 已经过期，从队首移除。它过期是因为位置，不是因为新值大小。','diagram':'旧队列：[1:3,2:-1,3:-3]\n移除下标 <= i-k=1\n剩余：[2:-1,3:-3]'},
  {'title':'再从队尾淘汰 -3、-1','note':'5 更大且更晚，两个旧候选不可能再胜过它，全部从队尾删除，队列只剩 [4:5]。','array':[1,3,-1,-3,5,3,6,7],'active':[2,3,4],'metrics':[['候选','[4:5]'],['输出','[3,3,5]']]},
  {'title':'后续窗口最大值依次为 5、6、7','note':'3 先作为备用候选保留；6 到来淘汰 3、5；7 再淘汰 6。每个完整窗口都追加一次输出。','table':{'headers':['窗口','最大值'],'rows':[['[-3,5,3]',5],['[5,3,6]',6],['[3,6,7]',7]]}}
 ]},{'label':'相同最大值优先保留更新的下标','input':'nums=[2,2,1]，k=2','output':'[2,2]','frames':[
  {'title':'第二个 2 淘汰第一个 2','note':'两者一样大，但下标 1 比下标 0 晚过期，所以保留下标 1 不会失去未来最大值。','diagram':'队列：[0:2] → 新值 1:2 到来 → [1:2]'},
  {'title':'下一窗口仍含更新的 2','note':'窗口从 [2,2] 移到 [2,1]，下标 1 仍有效，两个窗口答案都是 2。','array':[2,2],'array_label':'两个窗口的输出'}
 ]}],
 'walkthrough':['队列长度不等于窗口长度。删除弱候选后，即使窗口已有 k 个元素，队列可能只剩一个最大值下标。','队首过期判断 i-k 是窗口左端 i-k+1 的前一个位置。小于等于 i-k 的下标都已离开当前窗口。','每个下标入队一次，之后最多从队首或队尾离开一次。即使同一轮 while 删除很多项，总删除次数仍不超过 n。','这道题属于滑动窗口，但窗口边界本身很简单；难点在于如何维护最大值，所以主分类放在单调队列。'],
 'code':'''
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: list[int], k: int) -> list[int]:
        # 双端队列只存下标，对应的值从队首到队尾严格递减。
        queue = deque()
        answer = []
        for i, value in enumerate(nums):
            # 队首下标已离开窗口时，先把它移除。
            while queue and queue[0] <= i - k:
                queue.popleft()
            # 新值更大或相等且更晚过期，旧的较小候选以后都不可能成为最大值。
            while queue and nums[queue[-1]] <= value:
                queue.pop()
            queue.append(i)
            # 凑满第一个完整窗口后，队首就是每个窗口的最大值下标。
            if i >= k - 1:
                answer.append(nums[queue[0]])
        return answer
'''.strip(),
 'code_notes':['queue[0] 和 queue[-1] 都是下标，通过 nums 读取实际值。','popleft 删除过期队首，pop 删除被支配队尾，两种方向与两种证明一一对应。','先移除过期项，再加入今天的候选，读取最大值时队列一定非空且全部有效。'],
 'pitfalls':['只存数值不存下标，重复值出现时很难准确判断哪一个已经过期。','用 list.pop(0) 实现队首删除会移动后续元素，破坏线性复杂度。','把候选数量达到 k 当成窗口形成条件，会漏掉队列被压缩后的窗口。','清空全部历史最大值时不能清空输出，answer 保存的是每个完整窗口各自的结果。'],
 'complexity':'时间 O(n)，每个下标入队出队各至多一次；辅助队列 O(k)，输出另占 O(n−k+1)。',
 'quiz':{'question':'为什么新的同值下标可以替代旧的同值下标？','answer':'它们提供相同最大值，但新下标更晚离开窗口。任何未来仍包含旧下标的窗口，也会包含较新的这个下标，因此替换不会变差。'},
 'tests':{'method':'maxSlidingWindow','preserve_args':[0],'cases':[{'args':[[1,3,-1,-3,5,3,6,7],3],'expected':[3,3,5,5,6,7]},{'args':[[2,2,1],2],'expected':[2,2]},{'args':[[1],1],'expected':[1]},{'args':[[4,3,2,1],2],'expected':[4,3,2]},{'args':[[1,2,3],3],'expected':[3]},{'args':[[-3,-1,-2],1],'expected':[-3,-1,-2]}]}
})
