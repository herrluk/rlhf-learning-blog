"""第 09 章：小规模穷举、表达式树参照与单调结构朴素参照。"""
from collections import Counter
from fractions import Fraction
from itertools import product
import ast, copy, hashlib, json, random, re
from build import load_content
from catalog import ROOT, catalog


def verify():
    problems = {p['id']: p for p in load_content(catalog()[8])['problems']}
    methods, objects, counts = {}, {}, Counter()
    extra_calls = Counter()
    rng = random.Random(20260908)
    for pid, p in problems.items():
        ns = {}
        exec(p['code'], ns)
        objects[pid] = ns['Solution']()
        methods[pid] = getattr(objects[pid], p['tests']['method'])

    def equal(pid, args, expected):
        inputs = copy.deepcopy(args)
        result = methods[pid](*inputs)
        assert result == expected, (pid, args, expected, result)
        for index in problems[pid]['tests'].get('preserve_args', []):
            assert inputs[index] == args[index], (pid, 'input mutation')
        counts[pid] += 1
        if pid == 42:
            inputs = copy.deepcopy(args)
            assert objects[42].trapTwoPointers(*inputs) == expected
            assert inputs == args
            counts[42] += 1
            extra_calls['42.trapTwoPointers'] += 1
            inputs = copy.deepcopy(args)
            assert objects[42].trapStack(*inputs) == expected
            assert inputs == args
            counts[42] += 1
            extra_calls['42.trapStack'] += 1

    # 与正文栈匹配不同，参考法反复删除相邻的完整括号对。
    def valid_ref(s):
        while True:
            reduced = s.replace('()', '').replace('[]', '').replace('{}', '')
            if reduced == s:
                return not s
            s = reduced
    for n in range(1, 7):
        for chars in product('()[]{}', repeat=n):
            s = ''.join(chars)
            equal(20, [s], valid_ref(s))
    equal(20, ['('*5000+')'*5000], True)

    # 枚举每个左端点，维护纯计数平衡，不复用下标栈算法。
    def longest_ref(s):
        best = 0
        for left in range(len(s)):
            balance = 0
            for right in range(left, len(s)):
                balance += 1 if s[right] == '(' else -1
                if balance < 0:
                    break
                if balance == 0:
                    best = max(best, right-left+1)
        return best
    for n in range(11):
        for chars in product('()', repeat=n):
            s = ''.join(chars)
            equal(32, [s], longest_ref(s))
    for s in ['()'*15000, '('*15000+')'*15000]:
        equal(32, [s], 30000)

    # AST 只在验证器中用于独立确定语法优先级；不执行 eval。
    # Fraction 的 int 转换实现向零截断，避免参照重复正文的符号分支。
    def expression_value(node):
        if isinstance(node, ast.Expression):
            return expression_value(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -expression_value(node.operand)
        a, b = expression_value(node.left), expression_value(node.right)
        if isinstance(node.op, ast.Add):return a+b
        if isinstance(node.op, ast.Sub):return a-b
        if isinstance(node.op, ast.Mult):return a*b
        if isinstance(node.op, ast.Div):return int(Fraction(a,b))
        raise AssertionError(type(node))

    def tree(depth):
        if not depth or rng.random() < 0.3:
            number = rng.randrange(-9, 10)
            return str(number), [str(number)]
        left, lt = tree(depth-1)
        right, rt = tree(depth-1)
        op = rng.choice('+-*/')
        if op == '/' and expression_value(ast.parse(right, mode='eval')) == 0:
            op = '+'
        return '('+left+')'+op+'('+right+')', lt+rt+[op]

    def parens(depth):
        if not depth or rng.random() < 0.3:
            return str(rng.randrange(21))
        text = '('+parens(depth-1)+')'+rng.choice('+-')+'('+parens(depth-1)+')'
        return '-('+text+')' if rng.random() < 0.3 else text

    for _ in range(500):
        expression, tokens = tree(3)
        expected = expression_value(ast.parse(expression, mode='eval'))
        equal(150, [tokens], expected)
        parts = [str(rng.randrange(10))]
        for _ in range(rng.randrange(7)):
            op = rng.choice('+-*/')
            number = rng.randrange(1,10) if op == '/' else rng.randrange(10)
            parts += [op, str(number)]
        expression = ''.join(parts)
        expected = expression_value(ast.parse(expression, mode='eval'))
        spaced = ' ' * rng.randrange(3) + (' ' * rng.randrange(4)).join(parts) + ' ' * rng.randrange(3)
        equal(227, [spaced], expected)
        expression = parens(3)
        expected = expression_value(ast.parse(expression, mode='eval'))
        tokens = re.findall(r'\d+|[()+-]', expression)
        equal(224, [(' ' * rng.randrange(3)).join(tokens)], expected)
    equal(150, [['1']+['1','+']*4999], 5000)
    equal(227, ['+'.join(['1']*100000)], 100000)
    for depth in [10000,10001]:
        equal(224, ['-('*depth+'1'+')'*depth], -1 if depth%2 else 1)

    # 同时生成编码和其原文；参考结果来自生成过程，不再解析编码。
    def encoded(depth):
        pieces, values = [], []
        for _ in range(rng.randrange(1,4)):
            if depth and rng.random() < 0.5:
                child, value = encoded(depth-1)
                repeat = rng.randrange(1,6)
                pieces.append(str(repeat)+'['+child+']')
                values.append(value*repeat)
            else:
                word = ''.join(rng.choices('abc',k=rng.randrange(1,4)))
                pieces.append(word);values.append(word)
        return ''.join(pieces), ''.join(values)
    accepted = 0
    while accepted < 400:
        source, expected = encoded(3)
        if len(source) <= 30 and len(expected) <= 100000:
            equal(394, [source], expected)
            accepted += 1
    equal(394, ['300[300[a]]'], 'a'*90000)
    equal(394, ['1['*9+'a'+']'*9], 'a')

    # 单调结构参照：逐日搜索、逐列最高墙、全部区间、逐窗 max。
    for _ in range(500):
        temperatures = rng.choices(range(30,81),k=rng.randrange(1,18))
        expected = [next((j-i for j in range(i+1,len(temperatures))
                          if temperatures[j] > temperatures[i]),0)
                    for i in range(len(temperatures))]
        equal(739, [temperatures], expected)
        heights = rng.choices(range(9),k=rng.randrange(1,18))
        expected = sum(min(max(heights[:i+1]),max(heights[i:]))-height
                       for i,height in enumerate(heights))
        equal(42, [heights], expected)
        expected = max(min(heights[left:right])*(right-left)
                       for left in range(len(heights)) for right in range(left+1,len(heights)+1))
        equal(84, [heights], expected)
        values = rng.choices(range(-5,6),k=rng.randrange(1,25))
        k = rng.randrange(1,len(values)+1)
        equal(239, [values,k], [max(values[i:i+k]) for i in range(len(values)-k+1)])
    for n in [1,2,9,10000]:
        ascending = list(range(1,n+1))
        for heights in [ascending,ascending[::-1]]:
            equal(84, [heights], ((n+1)**2)//4)
            equal(42, [heights], 0)
    equal(84, [[7]*100000], 700000)
    equal(739, [[70]*100000], [0]*100000)
    equal(239, [[7]*100000,100000], [7])
    assert set(counts) == set(problems)
    report = {'status':'PASS','chapter':9,'problems':len(problems),'cases':sum(counts.values()),
              'additional_method_checks':dict(extra_calls),
              'checks':[{'id':pid,'cases':counts[pid],
                         'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()}
                        for pid in sorted(problems)],
              'note':'cases 包含接雨水两种方法的实际调用；小规模穷举与随机参照不代表全部输入穷举。'}
    (ROOT/'stacks-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__ == '__main__':
    verify()
