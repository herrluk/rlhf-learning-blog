from pathlib import Path
import copy, hashlib, json, math, re, runpy, sys
from html.parser import HTMLParser
from collections import Counter
from catalog import ROOT, OUT, catalog
from build import load_content
from node_cases import run_linked_case, run_random_linked_case
from tree_cases import run_tree_case
from graph_cases import run_graph_case, run_topological_case
from design_cases import run_design_case

class Extract(HTMLParser):
    def __init__(self):
        super().__init__();self.codes={};self.current=None;self.ids=[];self.links=[];self.problems=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='section' and 'data-problem' in a:self.problems.append(int(a['data-problem']))
        if tag=='code' and 'data-solution' in a:self.current=int(a['data-solution']);self.codes[self.current]=''
    def handle_endtag(self,tag):
        if tag=='code':self.current=None
    def handle_data(self,data):
        if self.current is not None:self.codes[self.current]+=data

def normalize(value,mode):
    if mode=='groups':return sorted(sorted(v) for v in value)
    if mode=='sorted':return sorted(value)
    return value

def verify():
    chapters=catalog();all_ids=[];test_count=0;reports=[]
    for c in chapters:
        data=load_content(c)
        if data is None:continue
        path=OUT/c['filename'];assert path.exists(),path
        parsed=Extract();parsed.feed(path.read_text())
        assert len(parsed.ids)==len(set(parsed.ids)),('duplicate HTML id',path)
        assert set(parsed.problems)=={p['id'] for p in c['problems']}
        assert set(parsed.codes)==set(parsed.problems)
        for link in parsed.links:
            if link.startswith('#'):assert link[1:] in parsed.ids,(path,link)
            elif not re.match(r'^[a-z]+:',link):assert (path.parent/link.split('#')[0]).exists(),(path,link)
        for p in data['problems']:
            assert parsed.codes[p['id']]==p['code'],(p['id'],'highlight changed source')
            namespace={}
            exec(compile('from __future__ import annotations\n'+p['code'],f'problem_{p["id"]}','exec'),namespace)
            tests=p['tests']
            for case in tests['cases']:
                if tests.get('adapter')=='design':
                    run_design_case(namespace,tests,case)
                    test_count+=1
                    continue
                if tests.get('adapter') in ('graph','topological'):
                    runner=run_graph_case if tests['adapter']=='graph' else run_topological_case
                    runner(namespace,tests,case)
                    test_count+=1
                    continue
                if tests.get('adapter')=='tree':
                    run_tree_case(namespace,tests,case)
                    test_count+=1
                    continue
                if tests.get('adapter')=='random_linked':
                    run_random_linked_case(namespace,tests,case)
                    test_count+=1
                    continue
                if tests.get('adapter')=='linked':
                    run_linked_case(namespace,tests,case)
                    test_count+=1
                    continue
                args=copy.deepcopy(case['args'])
                if 'rand7_values' in case:
                    draws=iter(case['rand7_values'])
                    used=[0]
                    def rand7():
                        used[0]+=1
                        return next(draws)
                    namespace['rand7']=rand7
                obj=namespace[tests.get('class','Solution')]()
                actual=getattr(obj,tests['method'])(*args)
                mode=tests.get('compare','exact')
                if 'mutated_arg' in case:actual=args[case['mutated_arg']]
                if 'prefix' in case:actual=args[case.get('arg',0)][:actual]
                if mode=='approx':
                    assert math.isclose(actual,case['expected'],rel_tol=1e-9,abs_tol=1e-9),(p['id'],case,actual)
                else:
                    assert normalize(actual,mode)==normalize(case['expected'],mode),(p['id'],case,actual)
                if 'rand7_calls' in case:assert used[0]==case['rand7_calls'],(p['id'],'rand7 calls',used[0])
                for index in tests.get('preserve_args',[]):
                    assert args[index]==case['args'][index],(p['id'],'input was modified',index)
                for index in tests.get('permutation_args',[]):
                    assert Counter(args[index])==Counter(case['args'][index]),(p['id'],'input elements were lost or added',index)
                test_count+=1
            all_ids.append(p['id'])
        reports.append({'chapter':c['number'],'problems':len(data['problems']),'html_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'content'/f'{c["number"]:02d}.py').read_bytes()).hexdigest()})
    assert len(all_ids)==len(set(all_ids))
    report={'generated_chapters':len(reports),'covered_problems':len(all_ids),'required_chapters':17,'required_problems':160,'code_cases_passed':test_count,'chapters':reports,'note':'这些检查证明代码示例执行、HTML 高亮未改代码和生成文件覆盖；不代替逐题内容审阅与浏览器检查。'}
    (ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('chapters','note')},ensure_ascii=False))
    if len(reports)!=17:print('INCOMPLETE: other chapters remain to be authored; goal is not complete.')

if __name__=='__main__':verify()
