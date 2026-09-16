"""检查独立 HTML 的题目、代码、可视化与可执行用例。"""
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from build_hot20 import OUTPUT, ROOT, BOOK, get_data
from content import RANKED
from verify import Extract, normalize
from node_cases import run_linked_case
from tree_cases import run_tree_case
from design_cases import run_design_case


def main():
    assert sys.version_info[:2] == (3,12), sys.version
    problems,metadata,rank=get_data()
    doc=OUTPUT.read_text()
    parsed=Extract();parsed.feed(doc)
    assert parsed.problems == [p['id'] for p in problems]
    assert set(parsed.problems)=={n for n,count in RANKED}
    assert len(parsed.ids)==len(set(parsed.ids))
    assert '160 题 · 方法与推导' not in doc
    assert not re.search(r'<(?:script|link|img)\b[^>]*(?:src|href)=',doc)
    for link in parsed.links:
        if link.startswith('#'):assert link[1:] in parsed.ids,link
        else:assert link.startswith('https://'),link
    payload=json.loads(re.search(r'<script id="book-data" type="application/json">(.*?)</script>',doc,re.S)[1])
    assert [p['id'] for p in payload['problems']]==parsed.problems
    cases=0;comments=0;code_reports=[]
    runners={'linked':run_linked_case,'tree':run_tree_case,'design':run_design_case}
    for p in problems:
        n=p['id'];source=parsed.codes[n]
        assert source==p['code'],(n,'rendered code changed')
        cn_comments=[line for line in source.splitlines() if '#' in line and re.search('[\u4e00-\u9fff]',line.split('#',1)[1])]
        assert len(cn_comments)>=2,(n,'Chinese comments')
        comments+=len(cn_comments)
        namespace={}
        exec(compile(source,f'html_problem_{n}','exec'),namespace)
        tests=p['tests']
        for case in tests['cases']:
            if tests.get('adapter') in runners:
                runners[tests['adapter']](namespace,tests,case)
            else:
                args=copy.deepcopy(case['args'])
                actual=getattr(namespace[tests.get('class','Solution')](),tests['method'])(*args)
                assert normalize(actual,tests.get('compare','exact'))==normalize(case['expected'],tests.get('compare','exact')),(n,case,actual)
                for index in tests.get('preserve_args',[]):assert args[index]==case['args'][index]
                for index in tests.get('permutation_args',[]):assert Counter(args[index])==Counter(case['args'][index])
            cases+=1
        # Every authored scene contains useful visual content and an explanatory state.
        for example in p['examples']:
            assert example['input'] and example['output'] and example['frames']
            for frame in example['frames']:
                assert frame['title'] and frame['note']
                assert any(k in frame for k in ('array','diagram','grid','table','panels'))
        code_reports.append({'id':n,'code_sha256':hashlib.sha256(source.encode()).hexdigest(),'cases':len(tests['cases']),'chinese_comments':len(cn_comments)})
    # Check the new optimized-method demonstrations reach their stated result.
    selected={p['id']:p for p in problems}
    assert selected[215]['examples'][0]['frames'][-1]['metrics']==[['第 2 大',5]]
    assert selected[42]['examples'][0]['frames'][-1]['metrics']==[['结果',9]]
    assert selected[300]['examples'][0]['frames'][-1]['metrics']==[['答案长度',4]]
    assert selected[72]['examples'][0]['frames'][-1]['array'][-1]==1
    for e in selected[5]['examples'][:2]:assert e['frames'][-1]['metrics'][0][1]==json.loads(e['output'])
    report={'status':'PASS','python':sys.version.split()[0],'file':str(OUTPUT),'html_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'problems':20,'fixed_cases':cases,'chinese_comment_lines':comments,'examples':sum(len(p['examples']) for p in problems),'frames':sum(len(e['frames']) for p in problems for e in p['examples']),'code':code_reports}
    (ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='code'},ensure_ascii=False))


if __name__=='__main__':main()
