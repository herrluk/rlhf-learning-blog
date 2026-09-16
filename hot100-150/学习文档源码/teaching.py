"""将逐题状态说明和算法先修材料接入所有学习文档。"""
import ast
import re
from foundations import FOUNDATIONS
from problem_states import STATES, rows_for


def annotate(code, rows):
    """在状态首次建立处补中文含义，原有操作原因注释和可执行语法保持不变。"""
    tree=ast.parse(code)
    lines=code.splitlines()
    additions={}
    for label,meaning in rows:
        # 公式、分区组合、对照方法混合说明留在代码前的变量表，避免跨作用域误注释。
        if not re.fullmatch(r'(?:self\.)?[A-Za-z_]\w*',label):
            continue
        targets=[]
        for node in ast.walk(tree):
            if isinstance(node,(ast.Assign,ast.AnnAssign)):
                assigned=node.targets if isinstance(node,ast.Assign) else [node.target]
                if any(ast.unparse(t)==label for t in assigned):targets.append(node)
        if not targets:continue
        first=min(targets,key=lambda node:node.lineno)
        at=first.lineno-1
        # 保留原有紧邻注释，已有该状态的命名说明时无需再添加。
        preceding=[];start=at
        while start>0 and lines[start-1].lstrip().startswith('#'):
            start-=1;preceding.append(lines[start])
        if preceding:continue
        indent=lines[at][:len(lines[at])-len(lines[at].lstrip())]
        # 避免主解初始化处夹入对照实现的存储定义。
        if any(word in meaning for word in ('对照法','对照方案')):continue
        text=label+'：'+meaning
        # 在中文句界处分行，保持复制后的代码可读。
        parts=re.findall(r'[^。；]+[。；]?',text)
        comments=[]
        for part in parts:
            if comments and len(comments[-1])+len(part)<=66:comments[-1]+=part
            else:comments.append(part)
        additions.setdefault(start,[]).extend(indent+'# '+part for part in comments)
    result=[]
    for i,line in enumerate(lines):
        result.extend(additions.get(i,[]));result.append(line)
    updated='\n'.join(result)
    assert ast.dump(ast.parse(code),include_attributes=False)==ast.dump(ast.parse(updated),include_attributes=False)
    return updated


def apply_teaching(data, chapter):
    foundation=FOUNDATIONS[chapter]
    data['prerequisites']=foundation['prerequisites']
    data['foundational_sections']=[dict(title=t,body=[body],diagram=diagram) for t,body,diagram in foundation['concepts']]
    # 通用 API 签名不再占据导读位置，算法所需的数据结构性质在前置概念中解释。
    data['apis']=[]
    for p in data['problems']:
        pid=p['id']
        if pid in STATES:
            rows=rows_for(pid)
            p['notation']={'intro':['先约定本题状态的含义，再看它如何更新。下表中的区间、次数、位置和最优值应与后面的推导及代码一起理解。'],
                           'headers':['状态 / 符号','在这道题中代表什么，为什么保存它'], 'rows':rows}
            p['code']=annotate(p['code'],rows)
        else:assert pid==525 and p.get('notation')
        p.pop('api',None)
        if pid==22:
            p['steps']=['opened、closed 分别表示已放入的左右括号数，初始都是 0。','opened<n 时可以加入左括号；closed<opened 时才能加入右括号，确保每个前缀都能继续完成。','一次选择后递归处理下一位置，返回时撤销刚加入的括号。','path 长度达到 2n 时，已经各有 n 个左右括号，保存完整答案。']
        if pid==525:
            p['code']=p['code'].replace('# in 检查字典里是否已有“当前差值”这个键。','# 相同差值的旧前缀与当前前缀之间，新增的 0 和 1 数量相等。')
    # 与当前学习目标无关的入门语法段删去；会影响输入结构的语义继续保留。
    for section in data.get('sections',[]):
        if chapter==7:
            section['body']=[s for s in section['body'] if not s.startswith('Python 的 and')]
        if chapter==4 and section['title'].startswith('8.'):
            section['body'][1]='balance 是累计的“1 的数量减去 0 的数量”；first 保存“差值 → 最早结束下标”。后续用两个同差值前缀配对，求中间区间的长度。'
            section['body'][2]='first={0:-1} 记录差值为 0 的空前缀，其结束位置约定为 −1。这个位置让从数组开头出发的合法区间也能使用统一长度公式；第 525 题用 [0,1] 完整推导。'
    return data
