"""设计章：独立朴素模型逐操作核对，并审计长期状态和实例隔离。"""
from collections import Counter, deque
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog
from design_cases import run_design_case


def verify():
    problems={p['id']:p for p in load_content(catalog()[15])['problems']};spaces={};counts=Counter();sequences=Counter();rng=random.Random(20260909)
    for pid,p in problems.items():
        ns={};exec(p['code'],ns);spaces[pid]=ns

    def exercise(pid,constructor,operations,inspect_every=1):
        obj=spaces[pid][problems[pid]['tests']['class']](*constructor)
        model=[] if pid in (155,232,295) else set() if pid==208 else {}
        timestamp=0;seen_inputs=[]
        def inspect():
            if pid==155:
                assert obj.values==model
                running=[]
                for value in model:running.append(min(value,running[-1]) if running else value)
                assert obj.mins==running and obj.values is not obj.mins
            elif pid==232:assert list(reversed(obj.outgoing))+obj.incoming==model
            elif pid==208:
                stack=[(obj.root,'')];nodes=set();maps=set();words=set()
                prefixes={w[:i] for w in model for i in range(1,len(w)+1)}|{''}
                actual_prefixes=set()
                while stack:
                    node,prefix=stack.pop()
                    assert id(node) not in nodes and id(node.children) not in maps
                    nodes.add(id(node));maps.add(id(node.children));actual_prefixes.add(prefix)
                    if node.is_word:words.add(prefix)
                    for char,child in node.children.items():
                        assert len(char)==1;stack.append((child,prefix+char))
                assert words==model and actual_prefixes==prefixes
            elif pid==146:
                assert set(obj.nodes)==set(model)
                assert obj.head.prev is None and obj.tail.next is None
                node=obj.head;visited=set();order=[]
                while node is not obj.tail:
                    assert id(node) not in visited;visited.add(id(node))
                    child=node.next;assert child is not None and child.prev is node
                    node=child
                    if node is not obj.tail:
                        assert obj.nodes[node.key] is node and node.value==model[node.key][0]
                        order.append(node.key)
                assert order==sorted(model,key=lambda key:model[key][2],reverse=True)
                assert len(order)<=constructor[0]
            elif pid==295:
                assert sorted([-x for x in obj.low]+obj.high)==sorted(model)
                assert len(obj.low) in (len(obj.high),len(obj.high)+1)
                for heap in (obj.low,obj.high):
                    assert all(heap[(i-1)//2]<=heap[i] for i in range(1,len(heap)))
                if obj.high:assert -obj.low[0]<=obj.high[0]
            else:
                assert obj.values=={key:item[0] for key,item in model.items()}
                assert obj.freq=={key:item[1] for key,item in model.items()}
                grouped={}
                for key in sorted(model,key=lambda key:model[key][2]):grouped.setdefault(model[key][1],[]).append(key)
                assert {f:list(bucket) for f,bucket in obj.buckets.items()}==grouped
                assert all(obj.buckets.values()) and len(obj.buckets)<=len(model)
                assert obj.min_freq==(min(item[1] for item in model.values()) if model else 0)
                assert len(model)<=constructor[0]
        inspect()
        for index,(method,args) in enumerate(operations):
            expected=None;timestamp+=1
            if pid==155:
                if method=='push':model.append(args[0])
                elif method=='pop':model.pop()
                elif method=='top':expected=model[-1]
                else:expected=min(model)
            elif pid==232:
                if method=='push':model.append(args[0])
                elif method=='pop':expected=model.pop(0)
                elif method=='peek':expected=model[0]
                else:expected=not model
            elif pid==208:
                if method=='insert':model.add(args[0])
                elif method=='search':expected=args[0] in model
                else:expected=any(word.startswith(args[0]) for word in model)
            elif pid==295:
                if method=='addNum':model.append(args[0])
                else:
                    ordered=sorted(model);n=len(ordered);expected=(ordered[(n-1)//2]+ordered[n//2])/2
            else:
                key=args[0]
                if method=='get':
                    expected=model[key][0] if key in model else -1
                    if key in model:model[key][1]+=1;model[key][2]=timestamp
                elif constructor[0]>0:
                    if key in model:model[key]=[args[1],model[key][1]+1,timestamp]
                    else:
                        if len(model)==constructor[0]:
                            victim=min(model,key=lambda key:(model[key][1],model[key][2]) if pid==460 else model[key][2])
                            del model[victim]
                        model[key]=[args[1],1,timestamp]
            copied=copy.deepcopy(args);actual=getattr(obj,method)(*copied)
            assert actual==expected,(pid,index,method,args,actual,expected)
            if isinstance(expected,bool):assert type(actual) is bool
            assert args==copied
            if index%inspect_every==0 or index==len(operations)-1:inspect()
            counts[pid]+=1
        sequences[pid]+=1
        return obj

    for _ in range(120):
        operations=[];size=0
        for i in range(100):
            method=rng.choice(['push','pop','top','getMin']) if size else 'push'
            args=[rng.randrange(-5,6)] if method=='push' else []
            if method=='push':size+=1
            if method=='pop':size-=1
            operations.append((method,args))
        exercise(155,[],operations)
        operations=[];size=0
        for i in range(100):
            method=rng.choice(['push','pop','peek','empty']) if size else rng.choice(['push','empty'])
            args=[rng.randrange(1,10)] if method=='push' else []
            if method=='push':size+=1
            if method=='pop':size-=1
            operations.append((method,args))
        exercise(232,[],operations)
    for _ in range(70):
        pool=[''.join(rng.choices('abc',k=rng.randrange(1,9))) for i in range(30)];operations=[]
        for i in range(100):
            word=rng.choice(pool);method=rng.choice(['insert','search','startsWith'])
            if method=='startsWith':word=word[:rng.randrange(1,len(word)+1)]
            operations.append((method,[word]))
        exercise(208,[],operations)
    for capacity in range(1,9):
        for _ in range(35):
            operations=[]
            for i in range(120):
                key=rng.randrange(12)
                operations.append(('put',[key,rng.randrange(1000)]) if rng.random()<.55 else ('get',[key]))
            for pid in (146,460):exercise(pid,[capacity],operations)
    exercise(460,[0],[('put',[1,1]),('get',[1])]*30)
    for _ in range(120):
        operations=[];size=0
        for i in range(120):
            if not size or rng.random()<.65:operations.append(('addNum',[rng.randrange(-20,21)]));size+=1
            else:operations.append(('findMedian',[]))
        exercise(295,[],operations)
    # 长序列与边界；状态审计抽样，返回值逐条比较。
    exercise(155,[],[('push',[-2147483648 if i%2 else 2147483647]) for i in range(15000)]+[('pop',[]) for i in range(15000)],inspect_every=1000)
    exercise(232,[],[('push',[i%9+1]) for i in range(50)]+[('pop',[]) for i in range(50)])
    word='a'*2000
    exercise(208,[],[('insert',[word]),('startsWith',[word[:-1]]),('search',[word[:-1]]),('search',[word])])
    exercise(295,[],[('addNum',[-100000 if i%2 else 100000]) for i in range(49999)]+[('findMedian',[])],inspect_every=5000)
    # 同一键不断晋升频次应只留下一个非空桶；LRU 同时检查反复摘插不生成新节点。
    for pid in (146,460):exercise(pid,[1],[('put',[7,70])]+[('get',[7]) for i in range(199999)],inspect_every=5000)
    exercise(146,[3000],[('put',[i,i]) for i in range(3000)]+[('put',[3000,8]),('get',[0]),('get',[1])],inspect_every=500)
    exercise(460,[10000],[('put',[i,i]) for i in range(10000)]+[('put',[10000,8]),('get',[0]),('get',[1])],inspect_every=1000)
    # 同一个代码命名空间中的两个实例交错调用，验证可变状态没有写成共享类属性。
    for pid in problems:
        cls=spaces[pid][problems[pid]['tests']['class']];args=[2] if pid in (146,460) else []
        first,second=cls(*args),cls(*args)
        if pid==155:first.push(5);second.push(9);assert first.top()==5 and second.top()==9
        elif pid==232:first.push(5);assert second.empty();second.push(9);assert first.pop()==5 and second.pop()==9
        elif pid==208:first.insert('alpha');assert not second.search('alpha');second.insert('beta');assert not first.search('beta')
        elif pid==295:first.addNum(5);second.addNum(9);assert first.findMedian()==5 and second.findMedian()==9
        else:first.put(1,5);second.put(1,9);assert first.get(1)==5 and second.get(1)==9
        counts[pid]+=1
    for pid,p in problems.items():
        for case in p['tests']['cases']:
            run_design_case(spaces[pid],p['tests'],case)
            counts[pid]+=len(case['operations']);sequences[pid]+=1
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':16,'problems':6,'cases':sum(counts.values()),'operation_sequences':sum(sequences.values()),'checks':[{'id':pid,'cases':counts[pid],'operation_sequences':sequences[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],'note':'cases 统计公开操作核对和实例隔离检查；列表/set/时间戳扫描/完整排序独立参照，另审计链表双向连接与字典节点对应、Trie 路径、两堆分区和非空频次桶。固定例子计入操作数。'}
    (ROOT/'design-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
