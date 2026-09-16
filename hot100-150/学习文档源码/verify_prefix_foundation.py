"""第 04 章新增基础代码和成品范围检查。"""
import contextlib
import hashlib
import io
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from catalog import ROOT,OUT
from prefix_foundation import CODE

class FoundationCode(HTMLParser):
    def __init__(self):
        super().__init__();self.inside=False;self.code=''
    def handle_starttag(self,tag,attrs):
        if tag=='code' and dict(attrs).get('id')=='python-prefix-basics':self.inside=True
    def handle_endtag(self,tag):
        if tag=='code':self.inside=False
    def handle_data(self,text):
        if self.inside:self.code+=text

def main():
    assert sys.version_info[:2]==(3,12)
    file=OUT/'04-前缀统计.html';doc=file.read_text();parsed=FoundationCode();parsed.feed(doc)
    assert parsed.code==CODE
    namespace={};stdout=io.StringIO()
    with contextlib.redirect_stdout(stdout):exec(compile(parsed.code,'prefix-foundation','exec'),namespace)
    assert stdout.getvalue()=='[0, 2, 1, 4, 8]\n6\n4\n'
    arrays=[[],[-5],[2,-1,3,4],[0,0,0],[-2,5,-3,4]];queries=0
    for nums in arrays:
        before=nums.copy();prefix=namespace['build_prefix_sum'](nums)
        assert prefix==[sum(nums[:t]) for t in range(len(nums)+1)]
        assert nums==before
        saved=prefix.copy()
        for left in range(len(nums)):
            for right in range(left,len(nums)):
                assert namespace['range_sum'](prefix,left,right)==sum(nums[left:right+1])
                queries+=1
        assert prefix==saved
    for section in ('prefix-definition','prefix-construction','prefix-query','prefix-code','prefix-build-lab','prefix-query-lab'):
        assert f'id="{section}"' in doc
    report={'status':'PASS','python':sys.version.split()[0],'html_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(CODE.encode()).hexdigest(),'construction_cases':len(arrays),'query_cases':queries,'printed_examples':3,'note':'从实际 HTML 提取新增基础代码，在 Python 3.12 执行；包含空数组、负数、零与每个合法闭区间。原有 160 题代码见固定用例报告。'}
    (ROOT/'prefix-foundation-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
