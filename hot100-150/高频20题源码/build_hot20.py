from pathlib import Path
import copy
import json
import sys

ROOT = Path(__file__).resolve().parent
BOOK = ROOT.parent / '学习文档源码'
sys.path.insert(1, str(BOOK))
from build import esc, paragraphs, problem_html, trace_view
from build import load_content
from catalog import catalog
from foundations import FOUNDATIONS
import math_typography as typography
from content import GROUPS, RANKED, SOURCE, BRIDGES, enrich

OUTPUT = ROOT.parent / 'Hot100高频20题学习手册.html'


def get_data():
    rank = {n: (i+1, count) for i,(n,count) in enumerate(RANKED)}
    all_problems = {}
    metadata = {}
    for chapter in catalog():
        for meta in chapter['problems']:
            if meta['id'] in rank:
                assert meta['scope'] == 'Hot 100'
                metadata[meta['id']] = copy.deepcopy(meta)
        for p in load_content(chapter)['problems']:
            if p['id'] in rank:
                all_problems[p['id']] = enrich(copy.deepcopy(p))
    order = [n for group in GROUPS for n in group['ids']]
    assert len(order) == len(set(order)) == 20 and set(order) == set(rank)
    problems = [all_problems[n] for n in order]
    for i,p in enumerate(problems,1):
        meta = metadata[p['id']]
        position, count = rank[p['id']]
        meta.update(frequency=f'样本考频 #{position} · {count} 次', priority=f'学习顺序 {i:02d} / 20')
    return problems, metadata, rank


def build():
    problems, metadata, rank = get_data()
    by_id = {p['id']:p for p in problems}
    order = [p['id'] for p in problems]
    examples = sum(len(p['examples']) for p in problems)
    frames = sum(len(e['frames']) for p in problems for e in p['examples'])

    nav = '<a class="skip-link" href="#main">跳到正文</a><aside class="sidebar"><p class="brand">ALGORITHM FIELD NOTES</p><p class="name">Hot100 · 高频 20 题</p><details class="nav-drawer" open><summary>学习目录与进度</summary><nav aria-label="学习手册导航"><a href="#top">封面与阅读方式</a><a href="#roadmap">六段学习路径</a><a href="#ranking">样本考频一览</a>'
    nav += '<div class="study-tools" hidden><label for="nav-search">查找题号 / 题名<input id="nav-search" type="search" placeholder="例如：146、链表"></label><div class="nav-order" role="group" aria-label="导航排序"><button data-order="learn" aria-pressed="true">学习顺序</button><button data-order="rank" aria-pressed="false">考频顺序</button></div><p class="progress-text" role="status" aria-live="polite">已掌握 0 / 20</p><progress id="study-progress" max="20" value="0" aria-label="已掌握题数"></progress><p class="storage-hint small">勾选后在本浏览器记住进度。</p></div>'
    nav += '<div id="problem-nav-list">'
    for i,p in enumerate(problems,1):
        n=p['id'];meta=metadata[n]
        nav += f'<a class="problem-nav-link" data-nav-problem="{n}" data-learn="{i}" data-rank="{rank[n][0]}" href="#q{n}"><span class="nav-title"><small>学习 {i:02d}</small>{n} {esc(meta["title"])}</span><span class="nav-rank">考频 #{rank[n][0]}</span><span class="done-mark" aria-label="已掌握" hidden>✓</span></a>'
    nav += '</div><p id="search-empty" class="small" hidden>没有匹配的题目，试试题号或其他关键词。</p></nav></details><p class="small nav-footnote">20 / 20 均属于 Hot100<br>考频数字为第三方样本记录</p></aside>'

    body = f'''<header class="hero" id="top"><p class="eyebrow">HOT100 · INTERVIEW CORE 20</p><h1>高频 20 题<br><span>从读懂到独立写出</span></h1><p class="lead">先定义状态，再推导操作；用逐步例子把想法对上代码。正文按前置知识排列，导航可切换样本考频顺序。</p><div class="meta"><span>20 道 Hot100</span><span>6 段学习路径</span><span>Python 3.12 · 中文注释</span><span>离线可用</span></div><div class="hero-stats"><div><b>{examples}</b><span>可切换例子</span></div><div><b>{frames}</b><span>可回退推演步骤</span></div><div><b>20</b><span>独立提交代码</span></div></div><div class="top-actions"><a class="start-link" href="#q20">开始学习 →</a><a href="#roadmap">先看学习路径</a><button id="print" type="button">打印 / 保存 PDF</button></div><p class="small source-caption">题单沿用上一轮确认的 20 题；整理日期：2026-09-12。标题跳转力扣中文站需要联网，其余阅读、代码高亮和步骤演示均内置。</p></header>'''
    body += '<section class="chapter" id="roadmap"><p class="eyebrow">HOW TO STUDY</p><h2>每题按同一条线学习</h2><ol class="reading-steps"><li><strong>先说清输入与输出。</strong>能不能改输入，是否必须连续，是否允许重复，都影响方法。</li><li><strong>先看朴素方案为何重复工作。</strong>再找可以保留的状态、可以排除的候选。</li><li><strong>单步观察一个例子。</strong>点击“下一步”前，先预测变量、指针或表格会怎样变化。</li><li><strong>折叠代码后独立实现。</strong>对照中文注释定位差异，再回答自测，解释复杂度与边界。</li></ol><div class="note"><strong>“学会”的标准</strong><p>不看答案写出完整代码，能解释关键条件为什么成立，并用空输入（题目允许时）、重复值、最短长度等边界检查。达到这个标准，再勾选“已能独立写出”。</p></div><h3>六段学习路径</h3><ol class="route-cards">'
    for i,g in enumerate(GROUPS,1):
        names=' → '.join(str(n) for n in g['ids'])
        body += f'<li><a href="#module-{i}"><span class="route-index">{i:02d}</span><strong>{esc(g["title"])}</strong><p>{esc(g["lead"])}</p><small>{names}</small></a></li>'
    body += '</ol><p class="small">代码包含该题需要的导入与节点定义。每题单独复制提交，不要把 20 份同名 Solution 类拼在一起。ListNode / TreeNode 是对象，示例中的数组或箭头是它们的显示形式。</p></section>'

    body += f'<section class="chapter" id="ranking"><p class="eyebrow">REPORTED SAMPLE · 2026.08</p><h2>考频一览：用来安排优先级</h2><p>第三方来源标注为 2026 年 8 月版，作者称样本包含华为、腾讯、字节的 6,139 篇面经。下列排名与次数沿用作者公开数据，未取得原始面经逐条复核；它们不是全行业精确考频，也不是出题概率。<a href="{SOURCE}" target="_blank" rel="noopener noreferrer">查看统计来源</a>。</p><details class="rank-details"><summary>展开 20 题样本排名与学习入口</summary><div class="scroll-table"><table><thead><tr><th>样本排名</th><th>题目（点击进入讲解）</th><th>次数</th><th>学习顺序</th></tr></thead><tbody>'
    for i,(n,count) in enumerate(RANKED,1):
        body += f'<tr><td>{i}</td><td><a href="#q{n}">{n}. {esc(metadata[n]["title"])}</a></td><td>{count}</td><td>{order.index(n)+1:02d}</td></tr>'
    body += '</tbody></table></div></details><p class="small">第 20 名 121 与来源后列的 33 同为 52 次，可视为同一档。本手册严格保留已确认的 20 道，不另外扩题。Hot100 的题单范围参照<a href="https://leetcode.cn/studyplan/top-100-liked/" target="_blank" rel="noopener noreferrer">力扣官方学习计划</a>。</p></section>'

    module_bases={1:[(9,0),(15,0),(3,0)],2:[(2,1),(14,1)],3:[(7,0),(7,1),(8,0)],4:[(10,0),(10,1),(10,2)],5:[(11,0),(11,1),(12,0),(12,1)],6:[(15,1),(15,3),(15,4)]}
    for gi,g in enumerate(GROUPS,1):
        body += f'<section class="chapter module-intro foundations" id="module-{gi}"><p class="eyebrow">MODULE {gi:02d} / 06</p><h2>{esc(g["title"])}</h2><p class="lead">{esc(g["lead"])}</p><h3>这一组题的算法前置知识</h3>'
        for chapter,index in module_bases[gi]:
            title,explanation,diagram=FOUNDATIONS[chapter]['concepts'][index]
            body+='<div class="foundation-concept"><h4>'+esc(title)+'</h4>'+paragraphs(explanation)+'<pre class="diagram">'+esc(diagram)+'</pre></div>'
        body+='<h3>把基础概念用到这一组题</h3>'+paragraphs(g['body'])+f'<pre class="diagram">{esc(g["diagram"])}</pre>'
        body += '<div class="module-links">'+''.join(f'<a href="#q{n}">{n}. {esc(metadata[n]["title"])}</a>' for n in g['ids'])+'</div></section>'
        for n in g['ids']:
            p=by_id[n]
            rendered=problem_html(p,metadata[n])
            bridge=f'<div class="learning-bridge"><strong>这题接着前面学什么</strong><p>{esc(BRIDGES[n])}</p></div>'
            rendered=rendered.replace('<h3>题目要解决什么</h3>',bridge+'<h3>题目要解决什么</h3>',1)
            rendered=rendered.replace('基础推导与对照步骤','推荐方法的操作步骤' if n in (42,215,300,5) else '先理解二维状态，再压缩空间')
            index=order.index(n)
            last=f'<a href="#q{order[index-1]}">← 上一题 {order[index-1]}</a>' if index else '<a href="#roadmap">← 学习路径</a>'
            next_link=f'<a href="#q{order[index+1]}">下一题 {order[index+1]} →</a>' if index+1<len(order) else '<a href="#review">进入复盘 →</a>'
            tail=f'<div class="study-check" hidden><label><input type="checkbox" data-mastered="{n}"> 已能独立写出，并解释正确性与边界</label></div><div class="problem-pager">{last}{next_link}</div>'
            rendered=rendered.replace('<a href="#top" class="small">回到本章目录 ↑</a>',tail)
            body += rendered

    body += '<section class="chapter" id="review"><p class="eyebrow">RECALL WITHOUT THE ANSWER</p><h2>复盘：只看题意，重新组织思路</h2><p>第一轮按学习路径建立方法；第二轮用导航切到考频顺序，折叠代码，混合重写。遇到卡点，把错误写成一句具体规则，例如“快速选择换回未知值后 i 不前进”，比只记录“粗心”更有用。</p><div class="two"><div class="method"><h3>每题问自己四件事</h3><ol><li>哪个变量表示什么，能否一口气说清？</li><li>为什么这次移动、删除或覆盖不会丢掉答案？</li><li>一个最短例子、一个重复值例子会怎样？</li><li>时间、辅助空间、输入是否改变分别是什么？</li></ol></div><div class="method"><h3>把容易混的题成对比较</h3><ul><li>121 与 53：历史最低价 vs 当前结尾最大和。</li><li>3 与 300：连续窗口 vs 可跳选的子序列。</li><li>21 与 23：两路比头 vs 多路堆选头。</li><li>102 与 236：按层出队 vs 先子后父汇总。</li><li>72 的二维表与滚动行：状态相同，存储不同。</li></ul></div></div><p>20 道是当前优先学习范围。完成后再按自己的薄弱模块继续补齐 Hot100；掌握这些题的状态和边界，比只记住题号更有迁移价值。</p></section>'
    body += f'<footer><p>每题题意为学习用简述，标题与题尾链接均指向力扣中文站原题。推荐方法说明渐近复杂度与取舍，不用一次平台运行耗时认定绝对最优。</p><p>Python 接口参考：<a href="https://docs.python.org/3.12/library/heapq.html" target="_blank" rel="noopener noreferrer">heapq</a> · <a href="https://docs.python.org/3.12/library/bisect.html" target="_blank" rel="noopener noreferrer">bisect</a> · <a href="https://docs.python.org/3.12/library/collections.html#collections.deque" target="_blank" rel="noopener noreferrer">deque</a>。<a href="{SOURCE}" target="_blank" rel="noopener noreferrer">考频统计来源</a>。</p><a href="#top">返回封面 ↑</a></footer>'

    ui={'problems':[{'id':p['id'],'examples':[dict(label=e['label'],input=e['input'],output=e['output'],frames=[trace_view(f) for f in e['frames']]) for e in p['examples']]} for p in problems]}
    css='\n'.join((BOOK/'assets'/f).read_text() for f in ('base.css','book.css'))+'\n'+(ROOT/'study.css').read_text()
    js='\n'.join((BOOK/'assets'/f).read_text() for f in ('copy.js','book.js'))+'\n'+(ROOT/'study.js').read_text()
    payload=json.dumps(ui,ensure_ascii=False).replace('</','<\\/')
    doc=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Hot100 高频 20 题 · Python 3.12 学习手册</title><style>{css}</style></head><body>{nav}<main id="main">{body}</main><noscript><p class="nojs">当前浏览器未启用 JavaScript。正文、完整代码和首帧图仍可阅读；启用后可使用逐步演示、复制和进度记录。</p></noscript><script id="book-data" type="application/json">{payload}</script><script>{js}</script></body></html>'
    doc=doc.replace('<script>'+js,'<script>'+typography.script()+'\n'+js,1)
    OUTPUT.write_text(typography.document(doc))
    print(json.dumps({'file':str(OUTPUT),'problems':20,'examples':examples,'frames':frames,'bytes':OUTPUT.stat().st_size},ensure_ascii=False))


if __name__=='__main__':
    build()
