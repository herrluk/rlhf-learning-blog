"""第 11 章：小树穷举、独立路径参照、真实节点身份和深树输入。"""
from collections import Counter, deque
from functools import lru_cache
import hashlib, json, random
from build import load_content
from catalog import ROOT, catalog
from tree_cases import make_tree, tree_values, run_tree_case


class RefNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def traversals(node):
    if node is None:return [],[],[]
    lp,li,lo=traversals(node.left);rp,ri,ro=traversals(node.right)
    return [node.val]+lp+rp,li+[node.val]+ri,lo+ro+[node.val]


def paths(node, prefix=None):
    if node is None:return []
    prefix=(prefix or [])+[node.val]
    if node.left is None and node.right is None:return [prefix]
    return paths(node.left,prefix)+paths(node.right,prefix)


def height(node):
    return 0 if node is None else 1+max(height(node.left),height(node.right))


def balanced(node):
    return node is None or (abs(height(node.left)-height(node.right))<=1 and balanced(node.left) and balanced(node.right))


def mirror_equal(a,b):
    if a is None or b is None:return a is b
    return a.val==b.val and mirror_equal(a.left,b.right) and mirror_equal(a.right,b.left)


def mirror(node):
    return None if node is None else RefNode(node.val,mirror(node.right),mirror(node.left))


def levels(node):
    result=[]
    def visit(node,depth):
        if node is None:return
        if depth==len(result):result.append([])
        result[depth].append(node.val)
        visit(node.left,depth+1);visit(node.right,depth+1)
    visit(node,0)
    return result


def complete(node):
    indices=[]
    def visit(node,index):
        if node is not None:
            indices.append(index);visit(node.left,2*index);visit(node.right,2*index+1)
    visit(node,1)
    return not indices or max(indices)==len(indices)


def graph_metrics(nodes):
    if not nodes:return 0,None
    neighbors={node:[] for node in nodes}
    for node in nodes:
        for child in (node.left,node.right):
            if child is not None:neighbors[node].append(child);neighbors[child].append(node)
    diameter=0;best=float('-inf')
    for start in nodes:
        stack=[(start,None,0,0)]
        while stack:
            node,parent,distance,total=stack.pop();total+=node.val
            diameter=max(diameter,distance);best=max(best,total)
            for nxt in neighbors[node]:
                if nxt is not parent:stack.append((nxt,node,distance+1,total))
    return diameter,best


def downward_count(nodes,target):
    count=0
    for start in nodes:
        stack=[(start,0)]
        while stack:
            node,total=stack.pop();total+=node.val;count+=total==target
            for child in (node.left,node.right):
                if child is not None:stack.append((child,total))
    return count


@lru_cache(None)
def shapes(n):
    if n==0:return (None,)
    return tuple((left,right) for size in range(n) for left in shapes(size) for right in shapes(n-1-size))


def from_shape(shape, values):
    if shape is None:return None
    node=RefNode(next(values));node.left=from_shape(shape[0],values);node.right=from_shape(shape[1],values)
    return node


def random_tree(n,rng):
    if not n:return None
    root=RefNode(rng.randrange(-4,5));slots=[(root,'left'),(root,'right')]
    for _ in range(n-1):
        i=rng.randrange(len(slots));parent,side=slots.pop(i)
        child=RefNode(rng.randrange(-4,5));setattr(parent,side,child)
        slots.extend([(child,'left'),(child,'right')])
    return root


def verify():
    problems={p['id']:p for p in load_content(catalog()[10])['problems']}
    namespaces={};counts=Counter();methods=Counter();rng=random.Random(20260908)
    for pid,p in problems.items():
        ns={};exec('from __future__ import annotations\n'+p['code'],ns);namespaces[pid]=ns

    def check(pid,args,expected,method=None,**case_options):
        tests=dict(problems[pid]['tests'])
        if method:tests['method']=method
        run_tree_case(namespaces[pid],tests,dict(args=args,expected=expected,**case_options))
        counts[pid]+=1;methods[str(pid)+'.'+tests['method']]+=1

    samples=[]
    for n in range(7):
        for shape in shapes(n):samples.append(from_shape(shape,iter((i%3)-1 for i in range(n))))
    samples.extend(random_tree(rng.randrange(41),rng) for _ in range(300))
    for sample in samples:
        raw,_=tree_values(sample);root,nodes,slots=make_tree(RefNode,raw)
        pre,ino,post=traversals(root);by_level=levels(root);all_paths=paths(root)
        check(144,[raw],pre);check(94,[raw],ino);check(145,[raw],post)
        check(102,[raw],by_level)
        check(103,[raw],[row if i%2==0 else row[::-1] for i,row in enumerate(by_level)])
        check(199,[raw],[row[-1] for row in by_level])
        check(958,[raw],complete(root));check(104,[raw],height(root));check(110,[raw],balanced(root))
        check(101,[raw],root is None or mirror_equal(root.left,root.right))
        check(226,[raw],tree_values(mirror(root))[0])
        check(98,[raw],all(a<b for a,b in zip(ino,ino[1:])))
        diameter,max_sum=graph_metrics(nodes)
        check(543,[raw],diameter)
        if nodes:check(124,[raw],max_sum)
        for target in {-2,0,3,rng.randrange(-10,11)}:
            wanted=[p for p in all_paths if sum(p)==target]
            check(112,[raw,target],bool(wanted));check(113,[raw,target],wanted)
            check(437,[raw,target],downward_count(nodes,target))
        check(114,[raw],pre);check(114,[raw],pre,method='flattenStack')
        check(297,[raw],raw)
        if height(root)<=10:
            digits=[None if value is None else abs(value)%10 for value in raw]
            digit_root,_,_=make_tree(RefNode,digits)
            digit_sum=sum(int(''.join(str(v) for v in path)) for path in paths(digit_root))
            if digit_sum<=2147483647:check(129,[digits],digit_sum)
        if len(nodes)>1:
            parents={root:None}
            for node in nodes:
                for child in (node.left,node.right):
                    if child is not None:parents[child]=node
            a,b=rng.sample(list(slots),2);ancestors=set();node=slots[a]
            while node is not None:ancestors.add(node);node=parents[node]
            node=slots[b]
            while node not in ancestors:node=parents[node]
            expected=next(slot for slot,value in slots.items() if value is node)
            unique_values=iter(range(len(nodes)))
            lca_raw=[None if value is None else next(unique_values) for value in raw]
            check(236,[lca_raw,a,b],expected)
        # 换为唯一值后，用两种遍历独立定义应恢复的整棵树。
        for i,node in enumerate(nodes):node.val=i-len(nodes)//2
        unique_raw,_=tree_values(root);unique_pre,unique_in,_=traversals(root)
        check(105,[unique_pre,unique_in],unique_raw)

    # 平衡构造按性质验收，不把某个中点选择当成唯一合法答案。
    for n in list(range(257))+[10000]:
        values=list(range(n));before=values[:]
        root=namespaces[108]['Solution']().sortedArrayToBST(values)
        serialized,ids=tree_values(root)
        assert len(ids)==n and values==before
        _,ordered,_=traversals(root)
        assert ordered==values and balanced(root),(108,n,serialized)
        counts[108]+=1;methods['108.sortedArrayToBST']+=1
        if n:
            for k in {1,n,(n+1)//2}:
                check(230,[serialized,k],values[k-1])
            check(98,[serialized],True)

    # 定向边界与题目规模内长链：这些主解不依赖 Python 调用栈。
    for p in problems.values():
        for case in p['tests']['cases']:
            check(p['id'],case['args'],case['expected'])
    check(297,[[1,None,2,3]],[1,None,2,3],serialized='1,#,2,3,#,#,#')
    check(297,[[]],[],serialized='#')
    def chain(n,value=1,left=False):
        raw=[value]
        for _ in range(n-1):raw.extend([value,None] if left else [None,value])
        if left and n>1:raw.pop()
        return raw
    check(104,[chain(10000)],10000)
    check(110,[chain(5000)],False)
    check(543,[chain(10000)],9999)
    check(124,[chain(30000)],30000)
    check(124,[chain(30000,-1)],-1)
    check(112,[chain(5000,0),0],True)
    check(113,[chain(5000,0),0],[[0]*5000])
    check(437,[chain(1000,0),0],500500)
    lca_raw=[0]
    for value in range(1,100000):lca_raw.extend([None,value])
    check(236,[lca_raw,1000,199998],1000)
    check(297,[chain(10000,-1000)],chain(10000,-1000))
    for left in (False,True):
        raw=chain(2000,left=left)
        check(114,[raw],[1]*2000);check(114,[raw],[1]*2000,method='flattenStack')
    ascending=list(range(3000));raw=[0]
    for x in ascending[1:]:raw.extend([None,x])
    check(105,[ascending,ascending],raw)
    ascending=list(range(10000));raw=[0]
    for x in ascending[1:]:raw.extend([None,x])
    check(230,[raw,10000],9999);check(98,[raw],True)
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':11,'problems':24,'cases':sum(counts.values()),'method_cases':dict(methods),
            'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],
            'note':'197 种六节点以内形状、300 棵固定种子随机小树、独立路径枚举、构造性质、身份/只读/原地约定与题目规模内长链；不代表全部输入穷举。'}
    (ROOT/'trees-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
