"""第 13 章：用掩码、排列、笛卡尔积、切分点枚举作独立参照。"""
from collections import Counter
from itertools import product, permutations, combinations
from math import comb
import copy, hashlib, json, random
from build import load_content
from catalog import ROOT, catalog


def all_ip(s):
    answers=[]
    for a,b,c in combinations(range(1,len(s)),3):
        parts=[s[:a],s[a:b],s[b:c],s[c:]]
        if all(1<=len(p)<=3 and (len(p)==1 or p[0]!='0') and int(p)<=255 for p in parts):answers.append('.'.join(parts))
    return answers


def palindrome_partitions(s):
    answers=[]
    for mask in range(1<<(len(s)-1)):
        cuts=[0]+[i+1 for i in range(len(s)-1) if mask>>i&1]+[len(s)]
        parts=[s[a:b] for a,b in zip(cuts,cuts[1:])]
        if all(part==part[::-1] for part in parts):answers.append(parts)
    return answers


def path_word_set(board,limit):
    # 用不可变访问位掩码和完整路径文本枚举，不修改网格，也不按目标字符剪枝。
    m,n=len(board),len(board[0]);words=set()
    for r in range(m):
        for c in range(n):
            stack=[(r,c,1<<(r*n+c),board[r][c])]
            while stack:
                r,c,mask,text=stack.pop();words.add(text)
                if len(text)==limit:continue
                for a,b in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                    if 0<=a<m and 0<=b<n and not mask>>(a*n+b)&1:
                        stack.append((a,b,mask|1<<(a*n+b),text+board[a][b]))
    return words


def verify():
    problems={p['id']:p for p in load_content(catalog()[12])['problems']};objects={};counts=Counter();rng=random.Random(20260908)
    for pid,p in problems.items():
        ns={};exec(p['code'],ns);objects[pid]=ns['Solution']()
    def check(pid,args,expected):
        inputs=copy.deepcopy(args)
        actual=getattr(objects[pid],problems[pid]['tests']['method'])(*inputs)
        assert inputs==args,(pid,'input changed')
        if pid in (78,39):
            normalized=sorted(tuple(sorted(row)) for row in actual)
            wanted=sorted(tuple(sorted(row)) for row in expected)
        elif pid in (46,47,131,51):
            normalized=sorted(tuple(row) for row in actual);wanted=sorted(tuple(row) for row in expected)
        elif pid==79:normalized,wanted=actual,expected
        else:normalized,wanted=sorted(actual),sorted(expected)
        assert normalized==wanted,(pid,args,actual,expected)
        if pid!=79:assert len(normalized)==len(set(normalized)),(pid,'duplicate output')
        # 列表结果必须彼此独立，也不得引用输入或搜索用的同一容器。
        if pid in (78,46,47,39,131,51):
            assert len({id(row) for row in actual})==len(actual),'shared answer lists'
            if actual:
                old_others=copy.deepcopy(actual[1:]);actual[0].append('changed')
                assert actual[1:]==old_others and inputs==args,'output mutation leaked'
        counts[pid]+=1
    for n in range(1,11):
        for _ in range(12):
            values=rng.sample(range(-10,11),n)
            expected=[[values[i] for i in range(n) if mask>>i&1] for mask in range(1<<n)]
            check(78,[values],expected)
    for n in range(1,7):
        for _ in range(12):
            values=rng.sample(range(-10,11),n)
            check(46,[values],list(permutations(values)))
    for n in range(1,7):
        for values in product((-1,0,1),repeat=n):
            check(47,[list(values)],list(set(permutations(values))))
    for values in [[1]*8,list(range(8)),[1,1,2,2,3,3,4,4]]:
        check(47,[values],list(set(permutations(values))))
    mapping=dict(zip('23456789',['abc','def','ghi','jkl','mno','pqrs','tuv','wxyz']))
    for n in range(1,5):
        for digits in product('23456789',repeat=n):
            s=''.join(digits);expected=[''.join(p) for p in product(*(mapping[d] for d in s))]
            check(17,[s],expected)
    for size in range(1,4):
        for values in combinations(range(2,8),size):
            for target in range(1,21):
                expected=[]
                for numbers in product(*(range(target//value+1) for value in values)):
                    if sum(value*number for value,number in zip(values,numbers))==target:
                        expected.append([value for value,number in zip(values,numbers) for _ in range(number)])
                shuffled=list(values);rng.shuffle(shuffled);check(39,[shuffled,target],expected)
    for n in range(1,9):
        expected=[]
        # 枚举左右括号数量已固定的位置集合，再验证前缀余额。
        for lefts in combinations(range(2*n),n):
            chars=[')']*(2*n)
            for i in lefts:chars[i]='('
            balance=0;valid=True
            for char in chars:
                balance+=1 if char=='(' else -1
                if balance<0:valid=False;break
            if valid:expected.append(''.join(chars))
        assert len(expected)==comb(2*n,n)//(n+1)
        check(22,[n],expected)
    for n in range(1,9):
        for chars in product('ab',repeat=n):
            s=''.join(chars);check(131,[s],palindrome_partitions(s))
    for s in ['a'*16,'abcdefghijklmnop','abbaabbaabbaabba']:
        check(131,[s],palindrome_partitions(s))
    for n in range(1,9):
        for digits in product('01',repeat=n):
            s=''.join(digits);check(93,[s],all_ip(s))
    for _ in range(400):
        s=''.join(rng.choices('0123456789',k=rng.randrange(1,21)));check(93,[s],all_ip(s))
    for m,n in [(1,1),(1,4),(2,2),(2,3)]:
        for cells in product('AB',repeat=m*n):
            board=[list(cells[r*n:(r+1)*n]) for r in range(m)]
            limit=min(5,m*n);available=path_word_set(board,limit)
            for length in range(1,limit+1):
                for chars in product('AB',repeat=length):
                    word=''.join(chars);check(79,[board,word],word in available)
    for board,word in [([list('ABCXB')],'ABCB'),([list('AAAAAA') for _ in range(6)],'A'*15),([list('AAAAAA') for _ in range(6)],'A'*14+'B')]:
        check(79,[board,word],word=='A'*15)
    queen_counts=[0,1,0,0,2,10,4,40,92,352]
    for n in range(1,10):
        expected=[]
        for cols in permutations(range(n)):
            # 两两几何距离检查，独立于主解的对角集合。
            if all(abs(cols[r]-cols[s])!=s-r for r in range(n) for s in range(r+1,n)):
                expected.append(['.'*c+'Q'+'.'*(n-c-1) for c in cols])
        assert len(expected)==queen_counts[n]
        check(51,[n],expected)
    for pid,p in problems.items():
        for case in p['tests']['cases']:check(pid,case['args'],case['expected'])
    assert set(counts)==set(problems)
    report={'status':'PASS','chapter':13,'problems':10,'cases':sum(counts.values()),'checks':[{'id':pid,'cases':counts[pid],'code_sha256':hashlib.sha256(problems[pid]['code'].encode()).hexdigest()} for pid in sorted(problems)],'note':'独立掩码、排列、笛卡尔积、候选次数、切分点和几何参照；包括输出唯一性、列表隔离、单词搜索成功/失败输入恢复与约束上界。'}
    (ROOT/'backtracking-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','note')},ensure_ascii=False))


if __name__=='__main__':verify()
