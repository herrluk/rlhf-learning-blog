"""链表章的结构验证：值、节点顺序、共享、环入口、输入恢复均实际检查。"""
from collections import Counter
import hashlib, json, random
from build import load_content
from catalog import ROOT, catalog
from node_cases import run_linked_case, run_random_linked_case


def verify():
    selected = {7,8}
    problems = {p['id']: p for c in catalog() if c['number'] in selected
                for p in load_content(c)['problems']}
    namespaces, counts = {}, Counter()
    rng = random.Random(20260908)
    for pid, p in problems.items():
        ns = {}
        exec('from __future__ import annotations\n' + p['code'], ns)
        namespaces[pid] = ns

    def check(pid, case):
        runner=run_random_linked_case if problems[pid]['tests'].get('adapter')=='random_linked' else run_linked_case
        runner(namespaces[pid], problems[pid]['tests'], case)
        counts[pid] += 1

    for _ in range(250):
        a = rng.choices(range(4), k=rng.randrange(30))
        check(206, {'args': [a], 'expected': a[::-1], 'expected_indices': list(range(len(a)))[::-1]})
        indices = list(range(len(a)))
        for i in range(0, len(a)-1, 2):
            indices[i], indices[i+1] = indices[i+1], indices[i]
        check(24, {'args': [a], 'expected': [a[i] for i in indices], 'expected_indices': indices})
        sorted_a = sorted(a)
        indices = [i for i in range(len(a)) if i == 0 or sorted_a[i] != sorted_a[i-1]]
        check(83, {'args': [sorted_a], 'expected': sorted(set(a)), 'expected_indices': indices})
        left = sorted(rng.choices(range(-3, 4), k=rng.randrange(15)))
        right = sorted(rng.choices(range(-3, 4), k=rng.randrange(15)))
        combined = left + right
        indices = sorted(range(len(combined)), key=lambda i: combined[i])
        check(21, {'args': [left, right], 'expected': sorted(combined), 'expected_indices': indices})
        a = a or [0]
        n = rng.randrange(1, len(a)+1)
        indices = [i for i in range(len(a)) if i != len(a)-n]
        check(19, {'args': [a, n], 'expected': [a[i] for i in indices], 'expected_indices': indices})
        check(876, {'args': [a], 'expected': len(a)//2})
        check(234, {'args': [a], 'expected': a == a[::-1]})
        for pal in [a+a[::-1], a+[9]+a[::-1]]:
            check(234, {'args': [pal], 'expected': True})
        x, y = rng.randrange(10**30), rng.randrange(10**30)
        digits = lambda value: [int(ch) for ch in str(value)[::-1]]
        check(2, {'args': [digits(x), digits(y)], 'expected': digits(x+y)})
        shared = rng.choices(range(1, 4), k=rng.randrange(9))
        pa = rng.choices(range(1, 4), k=rng.randrange(9))
        pb = rng.choices(range(1, 4), k=rng.randrange(9))
        if not shared:
            pa, pb = pa or [1], pb or [1]
        check(160, {'args': [pa, pb, shared], 'expected': 'shared' if shared else None})

    # 同样的节点值，系统变化尾节点指向位置，防止值比较掩盖身份错误。
    for length in range(51):
        values = [7] * length
        for pos in range(-1, length):
            check(141, {'args': [values], 'cycle_pos': pos, 'expected': pos >= 0})
            check(142, {'args': [values], 'cycle_pos': pos, 'expected': pos if pos >= 0 else None})
    # 题目大规模输入下使用迭代；恢复检查也覆盖不匹配的提前退出路径。
    for values in [[1]*100000, [1]*99999+[2]]:
        check(234, {'args': [values], 'expected': values == values[::-1]})
    # 区间和分组反转按节点原下标验证，不允许偷偷交换 val。
    for length in range(1,31):
        values=[i%3 for i in range(length)]
        for left in range(1,length+1):
            for right in range(left,length+1):
                order=list(range(length))
                order[left-1:right]=order[left-1:right][::-1]
                check(92,{'args':[values,left,right],'expected':[values[i] for i in order],'expected_indices':order})
        for k in range(1,length+1):
            order=list(range(length))
            for start in range(0,length-k+1,k):order[start:start+k]=order[start:start+k][::-1]
            check(25,{'args':[values,k],'expected':[values[i] for i in order],'expected_indices':order})
        order=[]
        for left in range((length+1)//2):
            order.append(left)
            right=length-1-left
            if left!=right:order.append(right)
        check(143,{'args':[values],'expected':[values[i] for i in order],'expected_indices':order})
    for _ in range(300):
        values=rng.choices(range(-5,6),k=rng.randrange(100))
        order=sorted(range(len(values)),key=lambda i:values[i])
        check(148,{'args':[values],'expected':sorted(values),'expected_indices':order})
        values.sort();frequencies=Counter(values)
        order=[i for i,value in enumerate(values) if frequencies[value]==1]
        check(82,{'args':[values],'expected':[values[i] for i in order],'expected_indices':order})
        n=rng.randrange(40)
        spec=[[rng.randrange(3),rng.choice([None]+list(range(n)))] for _ in range(n)]
        check(138,{'args':[spec],'expected':spec})
    for n in [1,2,17,256,1000]:
        for spec in [[[7,i] for i in range(n)],[[7,(i+1)%n] for i in range(n)],[[7,None] for i in range(n)]]:
            check(138,{'args':[spec],'expected':spec})
    values=list(range(50000,0,-1))
    check(148,{'args':[values],'expected':values[::-1],'expected_indices':list(range(len(values)))[::-1]})
    values=[i%1000+1 for i in range(50000)]
    order=[]
    for left in range(len(values)//2):order.extend([left,len(values)-1-left])
    check(143,{'args':[values],'expected':[values[i] for i in order],'expected_indices':order})
    assert set(counts) == set(problems), ('missing coverage', set(problems)-set(counts))
    report = {'status': 'PASS', 'chapters': sorted(selected), 'problems': len(problems),
              'cases': sum(counts.values()),
              'checks': [{'id': pid, 'cases': counts[pid],
                          'code_sha256': hashlib.sha256(problems[pid]['code'].encode()).hexdigest()}
                         for pid in sorted(problems)],
              'note': '身份和连接检查使用原节点引用；环入口覆盖长度 0..50 的所有构造位置；不声称覆盖所有合法输入。'}
    (ROOT/'linked-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ('checks', 'note')}, ensure_ascii=False))


if __name__ == '__main__':
    verify()
