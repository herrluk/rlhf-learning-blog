"""保留九题原有互动，在共用算法导读、状态说明和中文注释更新时同步生成。"""
from pathlib import Path
import sys,re,json
ROOT=Path(__file__).resolve().parent
BOOK=ROOT.parent/'学习文档源码'
sys.path.insert(0,str(BOOK))
from build import load_content,esc,paragraphs,table,highlight
from catalog import catalog
from foundations import FOUNDATIONS
import math_typography as typography
OUTPUT=ROOT.parent/'滑动窗口九题学习指南.html'
IDS=[3,209,438,1004,904,76,713,992,239]

def build():
    problems={p['id']:p for c in catalog() for p in load_content(c)['problems'] if p['id'] in IDS}
    meta={p['id']:p for c in catalog() for p in c['problems'] if p['id'] in IDS}
    doc=(ROOT/'template.html').read_text()
    foundation='<section class="chapter foundations" id="prerequisites"><h2>先修：窗口、状态与单调候选</h2>'+paragraphs(FOUNDATIONS[3]['prerequisites'])
    for c,index in [(3,0),(3,1),(3,2),(9,1),(9,2)]:
        title,body,diagram=FOUNDATIONS[c]['concepts'][index]
        foundation+='<div class="foundation-concept"><h3>'+esc(title)+'</h3>'+paragraphs(body)+'<pre class="diagram">'+esc(diagram)+'</pre></div>'
    foundation+='</section>'
    marker='<section class="chapter" id="method">'
    assert marker in doc
    doc=doc.replace(marker,foundation+marker,1)
    # 删除旧 Python 入门段；保留实际影响窗口不变量的零频次删除规则。
    doc,n=re.subn(r'<h3>Python 代码里先认识这几个写法</h3>.*?</section>', '<div class="note"><strong>频次归零是否删除，取决于状态定义</strong><p>904、992 用有效键数表示窗口种类数，所以某种值归零就要删除；只更新数字而保留零次数键，会误判窗口仍含有该种元素。</p></div></section>',doc,count=1,flags=re.S)
    assert n==1
    def revise(match):
        pid=int(match.group(1));body=match.group(0);p=problems[pid]
        notation=p['notation']
        guide='<div class="notation-guide"><h3>先认清本题的状态与变量</h3>'+paragraphs(notation['intro'])+table(notation['headers'],notation['rows'])+'</div>'
        body=body.replace('<h3>从题意推导窗口规则</h3>',guide+'<h3>从题意推导窗口规则</h3>',1)
        body,count=re.subn(r'(<code class="python" data-solution="'+str(pid)+r'"[^>]*>).*?(</code>)',lambda m:m[1]+highlight(p['code'])+m[2],body,count=1,flags=re.S)
        assert count==1
        body=body.replace('Python 完整解法 · 可独立提交','Python 3.12 完整解法 · 中文注释 · 可独立提交')
        url=meta[pid]['url'] or 'https://leetcode.cn/problems/'+p['slug']+'/'
        body=re.sub(r'<h2>(.*?)</h2>',lambda m:'<h2><a class="problem-title-link" href="'+url+'" target="_blank" rel="noopener noreferrer">'+m[1]+' ↗</a></h2>',body,count=1)
        return body
    doc,n=re.subn(r'<section class="chapter problem" id="q(\d+)".*?</section>',revise,doc,flags=re.S)
    assert n==9
    doc=doc.replace('</style>', '\n'+(BOOK/'assets/book.css').read_text()+'\n</style>',1)
    # 新增导读入口；不替换旧播放器或原有九题示例。
    doc=doc.replace('<nav>', '<nav><a href="#prerequisites">前置知识与基础概念</a>',1)
    doc=doc.replace('host.dataset.step=String(index);host.dataset.answer=JSON.stringify(f.ans);','host.dataset.step=String(index);host.dataset.answer=JSON.stringify(f.ans);\n    StudyMath.typeset(view);',1)
    doc=doc.replace('<script>', '<script>'+typography.script()+'\n',1)
    OUTPUT.write_text(typography.document(doc))
    print(json.dumps({'file':str(OUTPUT),'problems':9,'bytes':OUTPUT.stat().st_size},ensure_ascii=False))

if __name__=='__main__':build()
