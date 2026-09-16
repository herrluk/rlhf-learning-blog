"""第 12 章：并查集、同步传播、排列枚举及深拷贝性质参照。"""
from collections import Counter
from itertools import product, permutations, combinations
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog
from graph_cases import run_graph_case, run_topological_case


def components(grid):
    m,n=len(grid),len(grid[0]);parent=list(range(m*n));sizes=[1]*(m*n)
    def find(x):
        while x!=parent[x]:x=parent[x]
        return x
    for r in range(m):
        for c in range(n):
            if not grid[r][c]:continue
            for nr,nc in ((r-1,c),(r,c-1)):
                if nr>=0 and nc>=0 and grid[nr][nc]:
                    a,b=find(r*n+c),find(nr*n+nc)
                    if a!=b:parent[a]=b;sizes[b]+=sizes[a]
    roots={find(r*n+c) for r in range(m) for c in range(n) if grid[r][c]}
    return len(roots),max((sizes[root] for root in roots),default=0)


def rot_synchronously(grid):
    grid=copy.deepcopy(grid);m,n=len(grid),len(grid[0]);minutes=0
    while any(1 in row for row in grid):
        changed=[]
        for r in range(m):
            for c in range(n):
                if grid[r][c]==1 and any(0<=a<m and 0<=b<n and grid[a][b]==2 for a,b in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))):changed.append((r,c))
        if not changed:return -1,grid
        for r,c in changed:grid[r][c]=2
        minutes+=1
    return minutes,grid


def verify():
    problems={p['id']:p for p in load_content(catalog()[11])['problems']};namespaces={};counts=Counter();rng=random.Random(20260908)
    for pid,p in problems.items():
        ns={};exec('from __future__ import annotations\n'+p['code'],ns);namespaces[pid]=ns
    def check(pid,args,expected,final_grid=None):
        tests=problems[pid]['tests'];ns=namespaces[pid]
        if pid==133:run_graph_case(ns,tests,{'args':args,'expected':expected})
        elif pid==210:run_topological_case(ns,tests,{'args':args,'expected':expected})
        else:
            original=copy.deepcopy(args);args=copy.deepcopy(args)
            actual=getattr(ns['Solution'](),tests['method'])(*args)
            assert actual==expected,(pid,original,actual,expected)
            if final_grid is not None:assert args[0]==final_grid,(pid,'final grid',args[0],final_grid)
            if pid==207:assert args==original
        counts[pid]+=1
    for m,n in [(1,1),(1,5),(2,3),(3,3)]:
        for cells in product((0,1),repeat=m*n):
            grid=[list(cells[r*n:(r+1)*n]) for r in range(m)]
            count,area=components(grid)
            check(200,[[list(map(str,row)) for row in grid]],count,[['0']*n for _ in range(m)])
            check(695,[grid],area,[[0]*n for _ in range(m)])
    for m,n in [(1,1),(1,5),(2,3),(3,3)]:
        for cells in product((0,1,2),repeat=m*n):
            grid=[list(cells[r*n:(r+1)*n]) for r in range(m)]
            expected,final_grid=rot_synchronously(grid);check(994,[grid],expected,final_grid)
    for n in range(1,5):
        possible=[(a,b) for a in range(n) for b in range(n) if a!=b]
        orders=[{value:i for i,value in enumerate(order)} for order in permutations(range(n))]
        for mask in range(1<<len(possible)):
            edges=[list(edge) for i,edge in enumerate(possible) if mask>>i&1]
            feasible=any(all(position[b]<position[a] for a,b in edges) for position in orders)
            check(207,[n,edges],feasible);check(210,[n,edges],feasible)
    for n in range(1,6):
        possible=list(combinations(range(n),2))
        for mask in range(1<<len(possible)):
            adjacency=[[] for _ in range(n)]
            for i,(a,b) in enumerate(possible):
                if mask>>i&1:adjacency[a].append(b+1);adjacency[b].append(a+1)
            seen={1};stack=[1]
            while stack:
                for other in adjacency[stack.pop()-1]:
                    if other not in seen:seen.add(other);stack.append(other)
            if len(seen)==n:check(133,[adjacency],adjacency)
    for _ in range(150):
        m,n=rng.randrange(1,11),rng.randrange(1,11)
        grid=[[rng.randrange(2) for _ in range(n)] for _ in range(m)];count,area=components(grid)
        check(200,[[list(map(str,row)) for row in grid]],count,[['0']*n for _ in range(m)])
        check(695,[grid],area,[[0]*n for _ in range(m)])
        orange=[[rng.randrange(3) for _ in range(n)] for _ in range(m)];expected,final=rot_synchronously(orange)
        check(994,[orange],expected,final)
        n=rng.randrange(2,101);order=list(range(n));rng.shuffle(order)
        edges=[[order[i],order[j]] for i in range(n) for j in range(i) if rng.random()<.08]
        check(207,[n,edges],True);check(210,[n,edges],True)
    check(200,[[['1']*300 for _ in range(300)]],1,[['0']*300 for _ in range(300)])
    check(695,[[[1]*50 for _ in range(50)]],2500,[[0]*50 for _ in range(50)])
    long_chain=[[i,i-1] for i in range(1,2000)]
    check(207,[2000,long_chain],True);check(210,[2000,long_chain],True)
    cycle=long_chain+[[0,1999]]
    check(207,[2000,cycle],False);check(210,[2000,cycle],False)
    dense=[[j+1 for j in range(100) if j!=i] for i in range(100)]
    check(133,[dense],dense)
    for pid,p in problems.items():
        for case in p['tests']['cases']:check(pid,case['args'],case['expected'])
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':12,'problems':6,'cases':sum(counts.values()),'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],'note':'网格小规模穷举对照并查集和同步分钟模拟；四节点以内有向图对照课程排列；五节点以内连通无向图检查完整深拷贝；含题目上界规模。'}
    (ROOT/'graphs-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
