"""用小规模穷举参考解核对学习文档中的代码；补充固定例子，范围明确记录。"""
from collections import Counter
from pathlib import Path
import copy, hashlib, json, math, random
from catalog import ROOT, catalog
from build import load_content

def verify():
    rng=random.Random(20260907)
    selected_chapters={1,3,4,5,6,17}
    problems={p['id']:p for c in catalog() if c['number'] in selected_chapters and (data:=load_content(c)) for p in data['problems']}
    counts=Counter()
    methods={};namespaces={}
    for problem_id,p in problems.items():
        ns={};exec('from __future__ import annotations\n'+p['code'],ns)
        methods[problem_id]=getattr(ns['Solution'](),p['tests']['method'])
        namespaces[problem_id]=ns
    def call(id,*args):
        counts[id]+=1
        return methods[id](*copy.deepcopy(args))
    def equal(id,args,expected):
        actual=call(id,*args)
        assert actual==expected,(id,args,expected,actual)
    def intervals(a):
        return [a[l:r] for l in range(len(a)) for r in range(l+1,len(a)+1)]
    # 哈希题：用逐项扫描、排序分组及排好序的连续段作为独立参照。
    for _ in range(200):
        a=[rng.randint(-5,5) for _ in range(rng.randint(2,10))]
        i,j=rng.sample(range(len(a)),2);target=a[i]+a[j]
        pairs=[(l,r) for l in range(len(a)) for r in range(l+1,len(a)) if a[l]+a[r]==target]
        if len(pairs)==1:
            result=call(1,a,target);assert sorted(result)==list(pairs[0]),(1,a,target,result)
        s=''.join(rng.choices('abc',k=rng.randrange(8)));t=''.join(rng.choices('abc',k=rng.randrange(8)))
        equal(242,[s,t],sorted(s)==sorted(t))
        words=[''.join(rng.choices('abc',k=rng.randrange(5))) for _ in range(rng.randrange(8))]
        groups=[]
        for w in words:
            for g in groups:
                if sorted(g[0])==sorted(w):g.append(w);break
            else:groups.append([w])
        actual=call(49,words);assert sorted(map(sorted,actual))==sorted(map(sorted,groups))
        ordered=sorted(set(a));best=current=0;last=None
        for x in ordered:
            current=current+1 if last is not None and x==last+1 else 1
            best=max(best,current);last=x
        equal(128,[a],best)
    # 窗口与前缀：小输入枚举所有非空区间，允许重复、空串与负数。
    for _ in range(250):
        s=''.join(rng.choices('abc',k=rng.randrange(9)))
        subs=intervals(s)
        equal(3,[s],max([len(w) for w in subs if len(w)==len(set(w))]+[0]))
        p=''.join(rng.choices('abc',k=rng.randint(1,4)))
        equal(438,[s,p],[i for i in range(len(s)-len(p)+1) if sorted(s[i:i+len(p)])==sorted(p)])
        covers=[w for w in subs if not(Counter(p)-Counter(w))]
        answer=call(76,s,p)
        assert (not covers and answer=='') or (covers and answer in covers and len(answer)==min(map(len,covers))), (76,s,p,answer)
        a=[rng.randint(1,5) for _ in range(rng.randint(1,8))];target=rng.randint(1,16);parts=intervals(a)
        eligible=[len(w) for w in parts if sum(w)>=target]
        equal(209,[target,a],min(eligible) if eligible else 0)
        limit=rng.randint(0,30)
        equal(713,[a,limit],sum(math.prod(w)<limit for w in parts))
        equal(904,[a],max(len(w) for w in parts if len(set(w))<=2))
        distinct=rng.randint(1,5)
        equal(992,[a,distinct],sum(len(set(w))==distinct for w in parts))
        bits=[rng.randint(0,1) for _ in range(rng.randint(1,8))];budget=rng.randint(0,4);parts=intervals(bits)
        equal(1004,[bits,budget],max([len(w) for w in parts if w.count(0)<=budget]+[0]))
        equal(525,[bits],max([len(w) for w in parts if w.count(0)==w.count(1)]+[0]))
        a=[rng.randint(-3,3) for _ in range(rng.randint(2,8))];k=rng.randint(-5,5)
        equal(560,[a,k],sum(sum(w)==k for w in intervals(a)))
        equal(238,[a],[math.prod(a[:i]+a[i+1:]) for i in range(len(a))])
    # 螺旋参考用逐格转向 + visited，与正文四边收缩独立。
    def spiral_coords(m,n):
        visited=set();r=c=d=0;dirs=[(0,1),(1,0),(0,-1),(-1,0)]
        result=[]
        for _ in range(m*n):
            result.append((r,c));visited.add((r,c))
            nr,nc=r+dirs[d][0],c+dirs[d][1]
            if not(0<=nr<m and 0<=nc<n) or (nr,nc) in visited:d=(d+1)%4
            r,c=r+dirs[d][0],c+dirs[d][1]
        return result
    for m in range(1,8):
        for n in range(1,8):
            a=[[rng.randint(-3,4) for _ in range(n)] for _ in range(m)]
            equal(54,[a],[a[r][c] for r,c in spiral_coords(m,n)])
            zr={r for r in range(m) for c in range(n) if a[r][c]==0}
            zc={c for r in range(m) for c in range(n) if a[r][c]==0}
            expected=[[0 if r in zr or c in zc else a[r][c] for c in range(n)] for r in range(m)]
            b=copy.deepcopy(a);methods[73](b);counts[73]+=1;assert b==expected
    for n in range(1,15):
        expected=[[0]*n for _ in range(n)]
        for value,(r,c) in enumerate(spiral_coords(n,n),1):expected[r][c]=value
        generated=call(59,n);assert generated==expected and len({id(row) for row in generated})==n
        a=[[rng.randrange(1000) for _ in range(n)] for _ in range(n)]
        expected=[[a[n-1-c][r] for c in range(n)] for r in range(n)]
        b=copy.deepcopy(a);methods[48](b);counts[48]+=1;assert b==expected
    # 二分：参考解采用线性筛选或完整排序；不沿用正文的边界判断。
    for _ in range(300):
        a=sorted(rng.sample(range(-30,31),rng.randint(1,20)));target=rng.randint(-35,35)
        equal(704,[a,target],a.index(target) if target in a else -1)
        equal(35,[a,target],next((i for i,x in enumerate(a) if x>=target),len(a)))
        pivot=rng.randrange(len(a));rotated=a[pivot:]+a[:pivot]
        equal(153,[rotated],min(a))
        equal(33,[rotated,target],rotated.index(target) if target in rotated else -1)
        repeats=sorted(rng.choices(range(-4,5),k=rng.randrange(18)));target=rng.randint(-5,5)
        where=[i for i,x in enumerate(repeats) if x==target]
        equal(34,[repeats,target],[where[0],where[-1]] if where else [-1,-1])
        x=rng.randint(0,2147483647);answer=call(69,x);assert answer*answer<=x<(answer+1)**2
        piles=[rng.randint(1,20) for _ in range(rng.randint(1,8))];h=rng.randint(len(piles),len(piles)*20)
        speed=next(k for k in range(1,max(piles)+1) if sum(math.ceil(p/k) for p in piles)<=h)
        equal(875,[piles,h],speed)
        peak_input=rng.sample(range(-100,101),rng.randint(1,30));index=call(162,peak_input)
        assert 0<=index<len(peak_input) and (index==0 or peak_input[index]>peak_input[index-1]) and (index==len(peak_input)-1 or peak_input[index]>peak_input[index+1])
        a=sorted(rng.choices(range(-10,11),k=rng.randrange(15)));b=sorted(rng.choices(range(-10,11),k=rng.randrange(15)))
        if not a and not b:b=[0]
        merged=sorted(a+b);n=len(merged);expected=(merged[(n-1)//2]+merged[n//2])/2
        equal(4,[a,b],expected)
        m,n=rng.randint(1,7),rng.randint(1,7);flat=sorted(rng.sample(range(-100,101),m*n))
        matrix=[flat[r*n:(r+1)*n] for r in range(m)];target=rng.randint(-110,110)
        equal(74,[matrix,target],target in flat)
        # 行列都递增但行首与上一行行尾可能交错。
        rows=sorted(rng.sample(range(-30,31),m));cols=sorted(rng.sample(range(-30,31),n))
        matrix=[[r+c for c in cols] for r in rows];target=rng.randint(-65,65)
        equal(240,[matrix,target],any(target in row for row in matrix))
    # 约束题：构造满足存在性/重复次数要求的输入，再用额外空间参考解核对。
    for _ in range(250):
        values=rng.sample(range(-30,31),rng.randint(1,15));single=values[0]
        a=[single]+[x for x in values[1:] for _ in range(2)];rng.shuffle(a)
        equal(136,[a],single)
        length=rng.randint(1,25);major=rng.randint(-5,5);k=rng.randint(length//2+1,length)
        a=[major]*k+rng.choices([x for x in range(-5,6) if x!=major],k=length-k);rng.shuffle(a)
        equal(169,[a],major)
        a=rng.choices(range(-5,15),k=rng.randint(1,12))
        equal(41,[a],next(x for x in range(1,len(a)+2) if x not in a))
        n=rng.randint(1,15);duplicate=rng.randint(1,n);repeats=rng.randint(2,n+1)
        a=[duplicate]*repeats+rng.sample([x for x in range(1,n+1) if x!=duplicate],n+1-repeats);rng.shuffle(a)
        before=a[:];actual=methods[287](a);counts[287]+=1
        assert actual==duplicate and a==before,(287,before,actual,a)
        x=rng.choice([-1,1])*rng.uniform(0.5,2);power=rng.randint(-12,12);expected=x**power
        if abs(expected)<=10000:
            assert math.isclose(call(50,x,power),expected,rel_tol=1e-9,abs_tol=1e-9)
    # 对完整 7×7 等概率样本空间计数，不用随机频率近似代替公平性检查。
    histogram=Counter();rejected=0
    for a in range(1,8):
        for b in range(1,8):
            samples=iter([a,b,1,1]);used=[0]
            def rand7():
                used[0]+=1
                return next(samples)
            namespaces[470]['rand7']=rand7
            result=call(470)
            if (a-1)*7+b<=40:
                histogram[result]+=1
                assert used[0]==2
            else:
                rejected+=1
                assert used[0]==4 and result==1
    assert histogram=={i:4 for i in range(1,11)} and rejected==9
    checked=sorted(counts)
    assert set(checked)==set(problems), ('参考校验存在未覆盖的题目',set(problems)-set(checked))
    report={'status':'PASS','checked_problem_ids':checked,'cases_per_problem':dict(sorted(counts.items())),
            'total_cases':sum(counts.values()),'scope':'01、03、04、05、06、17 章的 36 题；小规模参考解与边界性质，不代表其他章节已经完成。',
            'rand10_single_round_accepted_histogram':dict(histogram),'rand10_rejected_pairs':rejected,
            'code_sha256':{str(i):hashlib.sha256(problems[i]['code'].encode()).hexdigest() for i in checked}}
    (ROOT/'algorithm-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='code_sha256'},ensure_ascii=False))

if __name__=='__main__':verify()
