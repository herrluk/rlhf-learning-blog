"""第 10 章：全部完整实现与排序参照、节点身份核对。"""
from collections import Counter
from itertools import product
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog
from node_cases import run_linked_case


def verify():
    problems={p['id']:p for p in load_content(catalog()[9])['problems']}
    objects={};namespaces={};counts=Counter();method_counts=Counter()
    rng=random.Random(20260909)
    random.seed(20260909)
    for pid,p in problems.items():
        ns={};exec('from __future__ import annotations\n'+p['code'],ns)
        objects[pid]=ns['Solution']();namespaces[pid]=ns

    def check(pid,args,expected,methods=None):
        names=methods or [problems[pid]['tests']['method']]
        for name in names:
            inputs=copy.deepcopy(args)
            result=getattr(objects[pid],name)(*inputs)
            if pid in (347,973):
                assert sorted(result)==sorted(expected),(pid,name,args,result,expected)
            else:assert result==expected,(pid,name,args,result,expected)
            if pid==912:
                assert result is inputs[0] and inputs[0]==expected,'sorting must mutate and return original list'
            elif pid==215 and name in ('findKthLargest','findKthLargestQuick'):
                target=len(inputs[0])-args[1]
                assert sorted(inputs[0])==sorted(args[0])
                assert all(x<=result for x in inputs[0][:target])
                assert all(x>=result for x in inputs[0][target+1:])
            else:assert inputs==args,(pid,name,'unexpected input mutation')
            counts[pid]+=1;method_counts[str(pid)+'.'+name]+=1

    sorts=['sortArray','sortArrayMerge','sortArrayQuick']
    selects=['findKthLargest','findKthLargestQuick','findKthLargestHeap']
    frequencies=['topKFrequent','topKFrequentHeap']
    matrix_methods=['kthSmallest','kthSmallestBinary','kthSmallestHeap']
    for n in range(1,8):
        for values in product([-1,0,1],repeat=n):
            values=list(values);expected=sorted(values)
            check(912,[values],expected,sorts)
            if n<=5:
                for k in range(1,n+1):check(215,[values,k],expected[-k],selects)
    for _ in range(300):
        values=rng.choices(range(-100,101),k=rng.randrange(1,301))
        ordered=sorted(values)
        check(912,[values],ordered,sorts)
        k=rng.randrange(1,len(values)+1)
        check(215,[values,k],ordered[-k],selects)
        values=rng.choices(range(-5,6),k=rng.randrange(1,100))
        # 小规模计数与完整排序为参照，选题范围内保证边界没有频次并列。
        different=list(set(values));ordered=sorted(different,key=values.count,reverse=True)
        valid_k=[k for k in range(1,len(ordered)+1) if k==len(ordered) or values.count(ordered[k-1])>values.count(ordered[k])]
        k=rng.choice(valid_k)
        check(347,[values,k],ordered[:k],frequencies)
        n=rng.randrange(1,21);points=[];used=set()
        while len(points)<n:
            x,y=rng.randrange(-30,31),rng.randrange(-30,31);distance=x*x+y*y
            if distance not in used:used.add(distance);points.append([x,y])
        k=rng.randrange(1,n+1)
        check(973,[points,k],sorted(points,key=lambda p:p[0]**2+p[1]**2)[:k])
        lists=[sorted(rng.choices(range(-3,4),k=rng.randrange(16))) for _ in range(rng.randrange(11))]
        flat=[x for a in lists for x in a]
        order=sorted(range(len(flat)),key=lambda i:flat[i])
        run_linked_case(namespaces[23],problems[23]['tests'],{'args':[lists],'expected':sorted(flat),'expected_indices':order})
        counts[23]+=1;method_counts['23.mergeKLists']+=1
        n=rng.randrange(1,10);matrix=[]
        start=rng.randrange(-30,0)
        for r in range(n):
            row=[]
            for c in range(n):row.append(max(row[c-1] if c else start,matrix[r-1][c] if r else start)+rng.randrange(4))
            matrix.append(row)
        ordered=sorted(x for row in matrix for x in row)
        for k in {1,n*n,rng.randrange(1,n*n+1)}:check(378,[matrix,k],ordered[k-1],matrix_methods)
    for values in [list(range(50000)),list(range(50000,0,-1)),[7]*50000,[i%5 for i in range(50000)]]:
        check(912,[values],sorted(values),sorts)
    for values,k in [([7]*100000,50000),([i%20001-10000 for i in range(100000)],17)]:
        check(215,[values,k],sorted(values)[-k],selects)
    for values,k,expected in [([1,1,2,2,3],2,[1,2]),([1,2,3],3,[1,2,3])]:check(347,[values,k],expected,frequencies)
    for lists in [[[] for _ in range(10000)],[[7] for _ in range(10000)]]:
        flat=[x for a in lists for x in a]
        run_linked_case(namespaces[23],problems[23]['tests'],{'args':[lists],'expected':flat,'expected_indices':list(range(len(flat)))})
        counts[23]+=1;method_counts['23.mergeKLists']+=1
    for matrix,k,expected in [([[7]*300 for _ in range(300)],90000,7),([[r*300+c-45000 for c in range(300)] for r in range(300)],45001,0)]:
        check(378,[matrix,k],expected,matrix_methods)
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':10,'problems':6,'cases':sum(counts.values()),'method_cases':dict(method_counts),
            'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],
            'note':'全部完整变体均实际调用；随机种子固定，排序参照和性质核对不代表全部输入穷举。'}
    (ROOT/'heaps-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
