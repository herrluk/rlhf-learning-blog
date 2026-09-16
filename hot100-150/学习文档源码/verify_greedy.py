"""贪心章：与买卖枚举、状态转移、显式路径、子集和全排列参照比较。"""
from collections import Counter, deque
from itertools import product, permutations, combinations
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog


def jumps(values):
    distance=[None]*len(values);distance[0]=0;queue=deque([0])
    while queue:
        i=queue.popleft()
        for j in range(i+1,min(len(values),i+values[i]+1)):
            if distance[j] is None:distance[j]=distance[i]+1;queue.append(j)
    return distance[-1]


def merged(intervals):
    # 连通分量参照；不依赖排序后逐项扩张的实现。
    remaining=set(range(len(intervals)));result=[]
    while remaining:
        start=remaining.pop();component=[start];queue=[start]
        while queue:
            i=queue.pop()
            for j in list(remaining):
                if max(intervals[i][0],intervals[j][0])<=min(intervals[i][1],intervals[j][1]):
                    remaining.remove(j);component.append(j);queue.append(j)
        result.append([min(intervals[i][0] for i in component),max(intervals[i][1] for i in component)])
    return sorted(result)


def removed(intervals):
    best=0
    for mask in range(1<<len(intervals)):
        chosen=[intervals[i] for i in range(len(intervals)) if mask>>i&1]
        if all(a[1]<=b[0] or b[1]<=a[0] for a,b in combinations(chosen,2)):best=max(best,len(chosen))
    return len(intervals)-best


def arrows(intervals):
    # 枚举所有端点组合，寻找覆盖每个闭区间的最小集合。
    points=sorted({v for pair in intervals for v in pair})
    for k in range(1,len(intervals)+1):
        for selected in combinations(points,k):
            if all(any(a<=p<=b for p in selected) for a,b in intervals):return k


def partitions(s):
    best=[]
    for mask in range(1<<(len(s)-1)):
        cuts=[0]+[i+1 for i in range(len(s)-1) if mask>>i&1]+[len(s)]
        groups=[s[a:b] for a,b in zip(cuts,cuts[1:])]
        if all(set(a).isdisjoint(b) for a,b in combinations(groups,2)) and len(groups)>len(best):best=[len(g) for g in groups]
    return best


def verify():
    problems={p['id']:p for p in load_content(catalog()[13])['problems']};objects={};counts=Counter();rng=random.Random(20260908)
    for pid,p in problems.items():
        ns={};exec(p['code'],ns);objects[pid]=ns['Solution']()
    def check(pid,args,expected):
        inputs=copy.deepcopy(args)
        actual=getattr(objects[pid],problems[pid]['tests']['method'])(*inputs)
        assert actual==expected,(pid,args,actual,expected)
        assert inputs==args,(pid,'input changed')
        if pid==56:
            assert len({id(row) for row in actual})==len(actual)
            assert not {id(row) for row in actual}&{id(row) for row in inputs[0]}
            others=copy.deepcopy(actual[1:]);actual[0][0]-=1
            assert inputs==args and actual[1:]==others,'merge result aliases input/other output'
        counts[pid]+=1
    for n in range(1,8):
        for values in product(range(3),repeat=n):
            values=list(values)
            check(121,[values],max([0]+[values[j]-values[i] for i in range(n) for j in range(i+1,n)]))
            cash,hold=0,-float('inf')
            for price in values:cash,hold=max(cash,hold+price),max(hold,cash-price)
            check(122,[values],cash)
            distance=jumps(values)
            check(55,[values],distance is not None)
            if distance is not None:check(45,[values],distance)
    interval_pool=[[a,b] for a in range(-2,3) for b in range(a+1,4)]
    for n in range(1,8):
        for _ in range(100):
            values=[list(rng.choice(interval_pool)) for _ in range(n)]
            check(56,[values],merged(values));check(435,[values],removed(values));check(452,[values],arrows(values))
    for n in range(1,9):
        for values in product('ab',repeat=n):
            s=''.join(values);check(763,[s],partitions(s))
    for _ in range(200):
        s=''.join(rng.choices('abcd',k=rng.randrange(1,11)));check(763,[s],partitions(s))
    pool=[0,1,10,100,12,121,1212,2,20,3,30,34,9,999,1000000000]
    for n in range(1,8):
        for _ in range(45):
            values=rng.choices(pool,k=n)
            wanted=max(''.join(map(str,p)) for p in permutations(values))
            check(179,[values],wanted.lstrip('0') or '0')
    for pid,p in problems.items():
        for case in p['tests']['cases']:check(pid,case['args'],case['expected'])
    check(121,[[10000]*100000],0);check(122,[[0,10000]*15000],150000000)
    check(55,[[1]*10000],True);check(45,[[1]*10000],9999)
    check(56,[[[0,10000]]*10000],[[0,10000]])
    check(435,[[[0,1]]*100000],99999);check(452,[[[-2147483648,2147483647]]*100000],1)
    check(763,['a'*500],[500]);check(179,[[0]*100],'0')
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':14,'problems':9,'cases':sum(counts.values()),'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],'note':'独立枚举/状态/图/子集/排列参照；验证区间等号、输入保留、输出对象隔离、前缀比较与有效约束上界。'}
    (ROOT/'greedy-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
