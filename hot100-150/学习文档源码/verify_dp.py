"""动态规划与额外完整方法：用组合、子集、路径、真实编辑图等独立参照核对。"""
from collections import Counter, deque
from functools import lru_cache
from itertools import product, combinations
from math import comb, isqrt
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog


def subsequences(values):
    return {tuple(values[i] for i in range(len(values)) if mask>>i&1) for mask in range(1<<len(values))}


def substrings(values):
    return {tuple(values[i:j]) for i in range(len(values)) for j in range(i+1,len(values)+1)}|{()}


def nonadjacent(values,circular=False):
    best=0;n=len(values)
    for mask in range(1<<n):
        if mask&(mask<<1):continue
        if circular and n>1 and mask&1 and mask>>(n-1)&1:continue
        best=max(best,sum(values[i] for i in range(n) if mask>>i&1))
    return best


def trade_pairs(prices):
    @lru_cache(None)
    def search(start):
        # 枚举完整买卖日期对；出售后从 sell+2 开始下一笔。
        return max([0]+[prices[sell]-prices[buy]+search(sell+2) for buy in range(start,len(prices)) for sell in range(buy+1,len(prices))])
    return search(0)


def minimum_coins(coins,amount):
    distance=[None]*(amount+1);distance[0]=0;queue=deque([0])
    while queue:
        value=queue.popleft()
        for coin in coins:
            new=value+coin
            if new<=amount and distance[new] is None:distance[new]=distance[value]+1;queue.append(new)
    return distance


def split_possible(s,words):
    for mask in range(1<<(len(s)-1)):
        cuts=[0]+[i+1 for i in range(len(s)-1) if mask>>i&1]+[len(s)]
        if all(s[a:b] in words for a,b in zip(cuts,cuts[1:])):return True
    return False


def grid_paths(m,n):
    paths=[]
    for downs in combinations(range(m+n-2),m-1):
        downset=set(downs);r=c=0;path=[(0,0)]
        for step in range(m+n-2):
            if step in downset:r+=1
            else:c+=1
            path.append((r,c))
        paths.append(path)
    return paths


def largest_square(matrix):
    m,n=len(matrix),len(matrix[0]);best=0
    for r in range(m):
        for c in range(n):
            for side in range(1,min(m-r,n-c)+1):
                if all(matrix[a][b]=='1' for a in range(r,r+side) for b in range(c,c+side)):best=max(best,side*side)
    return best


def verify():
    problems={p['id']:p for p in load_content(catalog()[14])['problems']};objects={};counts=Counter();method_counts=Counter();rng=random.Random(20260909)
    for pid,p in problems.items():
        ns={};exec(p['code'],ns);objects[pid]=ns['Solution']()
    def check(pid,args,expected,method=None):
        inputs=copy.deepcopy(args);method=method or problems[pid]['tests']['method']
        actual=getattr(objects[pid],method)(*inputs)
        assert actual==expected,(pid,method,args,actual,expected)
        assert inputs==args,(pid,'input changed')
        if pid in (139,416):assert type(actual) is bool
        if pid==118:
            assert len({id(row) for row in actual})==len(actual)
            others=copy.deepcopy(actual[1:]);actual[0].append(-1);assert actual[1:]==others
        counts[pid]+=1;method_counts[(pid,method)]+=1
    for n in range(1,46):check(70,[n],sum(comb(n-k,k) for k in range(n//2+1)))
    for n in range(1,31):check(118,[n],[[comb(r,c) for c in range(r+1)] for r in range(n)])
    for n in range(1,6):
        for values in product((-2,-1,0,1,2),repeat=n):
            values=list(values);sums=[];products=[]
            for a in range(n):
                total=0;multiplied=1
                for b in range(a,n):total+=values[b];multiplied*=values[b];sums.append(total);products.append(multiplied)
            check(53,[values],max(sums));check(152,[values],max(products))
    for n in range(1,8):
        for values in product((0,1,2),repeat=n):
            values=list(values)
            check(198,[values],nonadjacent(values));check(213,[values],nonadjacent(values,True))
            check(309,[values],trade_pairs(values))
            wanted=max(len(seq) for seq in subsequences(values) if all(a<b for a,b in zip(seq,seq[1:])))
            check(300,[values],wanted);check(300,[values],wanted,'lengthOfLISBinary')
    for size in range(1,5):
        for coins in combinations(range(1,9),size):
            distances=minimum_coins(coins,30)
            for amount,wanted in enumerate(distances):check(322,[list(coins),amount],-1 if wanted is None else wanted)
    squares=[i*i for i in range(1,101)];distances=minimum_coins(squares,10000)
    for n in list(range(1,301))+[999,9973,10000]:check(279,[n],distances[n])
    for n in range(1,8):
        for values in product((1,2,3),repeat=n):
            wanted=sum(values)%2==0 and any(sum(seq)*2==sum(values) for seq in subsequences(values))
            check(416,[list(values)],wanted)
    word_pool=[''.join(chars) for n in range(1,4) for chars in product('ab',repeat=n)]
    for n in range(1,8):
        for chars in product('ab',repeat=n):
            s=''.join(chars)
            for _ in range(4):
                words=rng.sample(word_pool,rng.randrange(1,8));check(139,[s,words],split_possible(s,set(words)))
    for m in range(1,101):
        for n in range(1,101):
            wanted=comb(m+n-2,m-1)
            if wanted<=2000000000:check(62,[m,n],wanted)
    for m,n in [(1,1),(1,4),(4,1),(2,2),(2,3),(3,3)]:
        paths=grid_paths(m,n)
        for bits in product((0,1),repeat=m*n):
            grid=[list(bits[r*n:(r+1)*n]) for r in range(m)]
            check(63,[grid],sum(all(grid[r][c]==0 for r,c in path) for path in paths))
            matrix=[[str(v) for v in row] for row in grid];check(221,[matrix],largest_square(matrix))
        cost_sets=product((0,1,3),repeat=m*n) if m*n<=6 else [rng.choices((0,1,3),k=m*n) for _ in range(200)]
        for cells in cost_sets:
            grid=[list(cells[r*n:(r+1)*n]) for r in range(m)]
            check(64,[grid],min(sum(grid[r][c] for r,c in path) for path in paths))
    strings=[''.join(chars) for n in range(1,6) for chars in product('ab',repeat=n)]
    subs={s:subsequences(s) for s in strings};segments={s:substrings(s) for s in strings}
    for a in strings:
        for b in strings:
            check(1143,[a,b],max(map(len,subs[a]&subs[b])))
            check(718,[[int(c=='b') for c in a],[int(c=='b') for c in b]],max(map(len,segments[a]&segments[b])))
    # 真实字符串操作图：逐次插入、删除、替换，不用二维编辑距离递推。
    short=['']+[''.join(chars) for n in range(1,4) for chars in product('ab',repeat=n)]
    for source in short:
        distance={source:0};queue=deque([source])
        while queue:
            current=queue.popleft();neighbors=set()
            for i in range(len(current)):
                neighbors.add(current[:i]+current[i+1:])
                for c in 'ab':neighbors.add(current[:i]+c+current[i+1:])
            if len(current)<3:
                for i in range(len(current)+1):
                    for c in 'ab':neighbors.add(current[:i]+c+current[i:])
            for neighbor in neighbors:
                if neighbor not in distance:distance[neighbor]=distance[current]+1;queue.append(neighbor)
        for target in short:check(72,[source,target],distance[target])
    strings=[''.join(chars) for n in range(1,9) for chars in product('ab',repeat=n)]
    strings+=[''.join(rng.choices('Aa1b',k=rng.randrange(1,16))) for _ in range(200)]
    for s in strings:
        candidates=[s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1) if s[i:j]==s[i:j][::-1]]
        wanted=max(candidates,key=len)
        check(5,[s],wanted);check(5,[s],wanted,'longestPalindromeCenter')
    boundaries=[(53,[[-1]*100000],-1),(152,[[1,-1]*10000],1),(198,[[400]*100],20000),(213,[[1000]*100],50000),(309,[[0]*5000],0),(300,[list(range(2500))],2500),(322,[[1,7,10],10000],1000),(416,[[100]*200],True),(139,['a'*300,['a'*20]],True),(63,[[[0 if c==0 or r==99 else 1 for c in range(100)] for r in range(100)]],1),(64,[[[1]*200 for _ in range(200)]],399),(221,[[['1']*300 for _ in range(300)]],90000),(1143,['a'*1000,'a'*1000],1000),(718,[[0]*1000,[0]*1000],1000),(72,['a'*500,'b'*500],500),(72,['','a'*500],500),(5,['a'*1000],'a'*1000)]
    for pid,args,wanted in boundaries:
        check(pid,args,wanted)
        if pid==300:check(pid,args,wanted,'lengthOfLISBinary')
        if pid==5:check(pid,args,wanted,'longestPalindromeCenter')
    for pid,p in problems.items():
        for case in p['tests']['cases']:
            check(pid,case['args'],case['expected'])
            if pid==300:check(pid,case['args'],case['expected'],'lengthOfLISBinary')
            if pid==5:check(pid,case['args'],case['expected'],'longestPalindromeCenter')
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':15,'problems':20,'cases':sum(counts.values()),'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],'methods':[{'id':pid,'method':name,'cases':count} for (pid,name),count in sorted(method_counts.items())],'note':'独立组合计数、连续区间、下标子集、完整买卖日期、金额 BFS、切分点、方向路径、正方形枚举、子序列/子串集合及真实字符串编辑图；包含两个完整进阶方法、输入保留、输出行隔离和合法约束边界。'}
    (ROOT/'dp-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','methods','note')},ensure_ascii=False))


if __name__=='__main__':verify()
