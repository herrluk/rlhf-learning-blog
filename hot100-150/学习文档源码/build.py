from pathlib import Path
import builtins, html, io, json, keyword, re, runpy, token, tokenize
from catalog import ROOT, OUT, catalog
import math_typography as typography

def esc(value):
    return html.escape(str(value))

def highlight(source):
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    def position(pair):
        return offsets[min(pair[0]-1, len(offsets)-1)] + pair[1]
    result, cursor, declaration = [], 0, None
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    for i,t in enumerate(tokens):
        start, end = position(t.start), min(position(t.end), len(source))
        if start < cursor or start >= len(source) or end <= start:
            continue
        result.append(esc(source[cursor:start]))
        kind = None
        if t.type == token.NAME:
            if keyword.iskeyword(t.string):
                kind = 'keyword'
                declaration = t.string if t.string in ('class','def') else None
            elif declaration:
                kind = 'class' if declaration == 'class' else 'function'
                declaration = None
            elif t.string in vars(builtins): kind = 'builtin'
            elif i+1 < len(tokens) and tokens[i+1].string == '(': kind = 'function'
        elif t.type == token.STRING: kind = 'string'
        elif t.type == token.COMMENT: kind = 'comment'
        elif t.type == token.NUMBER: kind = 'number'
        elif t.type == token.OP: kind = 'operator'
        value = esc(source[start:end])
        result.append(f'<span class="py-{kind}">{value}</span>' if kind else value)
        cursor = end
    return ''.join(result) + esc(source[cursor:])

def paragraphs(items):
    if isinstance(items, str): items = [items]
    return ''.join(f'<p>{esc(p)}</p>' for p in items)

def listing(items):
    return '<ol>' + ''.join(f'<li>{esc(p)}</li>' for p in items) + '</ol>'

def table(headers, rows):
    return '<div class="scroll-table" tabindex="0" role="region" aria-label="可横向滚动的表格"><table><thead><tr>' + ''.join(f'<th>{esc(h)}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join(f'<td>{esc(v)}</td>' for v in row)+'</tr>' for row in rows) + '</tbody></table></div><p class="small array-hint">窄屏可左右滑动查看完整表格。</p>'

def scene(frame):
    output = ''
    if frame.get('heading'): output += f'<h4>{esc(frame["heading"])}</h4>'
    if 'array' in frame:
        cells = ''
        for i,v in enumerate(frame['array']):
            labels = [k for k,p in frame.get('pointers',{}).items() if p == i]
            cells += f'<div class="cell{" in" if i in frame.get("active",[]) else ""}{" changed" if i==frame.get("changed") else ""}"><div class="index">{i}</div><div class="value">{esc(v)}</div><div class="pointer">{esc(" · ".join(labels))}</div></div>'
        output += f'<div class="array-scroll" role="img" aria-label="{esc(frame.get("array_label",str(frame["array"])))}"><div class="array">{cells or "空数组"}</div></div>'
        output += '<div class="small array-hint">上方数字为下标；窄屏可左右滑动查看完整数组。</div>'
    if 'grid' in frame:
        output += '<div class="matrix" role="img" aria-label="矩阵状态">'
        for ri,row in enumerate(frame['grid']):
            output += '<div class="matrix-row">'
            for ci,value in enumerate(row):
                active = [ri,ci] in frame.get('active_cells',[])
                output += f'<span class="matrix-cell{" selected" if active else ""}">{esc(value)}</span>'
            output += '</div>'
        output += '</div>'
        output += '<p class="small array-hint">行从上到下，列从左到右；超宽矩阵可左右滑动查看。</p>'
    if frame.get('diagram'): output += f'<pre class="diagram">{esc(frame["diagram"])}</pre>'
    if frame.get('metrics'): output += '<div class="state">'+''.join(f'<span class="metric">{esc(k)}<b>{esc(v)}</b></span>' for k,v in frame['metrics'])+'</div>'
    if frame.get('table'): output += table(frame['table']['headers'],frame['table']['rows'])
    if frame.get('panels'): output += '<div class="split-demos">'+''.join('<div>'+scene(f)+'</div>' for f in frame['panels'])+'</div>'
    if frame.get('equation'): output += f'<div class="equation">{esc(frame["equation"])}</div>'
    return output

def trace_view(frame):
    return typography.typeset_html(scene(frame)+f'<div class="status" role="status" aria-live="polite"><strong>{esc(frame["title"])}</strong><p>{esc(frame["note"])}</p></div>',code_operators=frame.get('notation_mode')=='code')

def code_block(id, source):
    return f'<div class="code-block"><div class="code-toolbar"><span class="code-language">Python 3.12 · 中文注释</span><button type="button" class="copy-code" data-copy-code="{id}" aria-label="复制第 {id} 题完整代码（含中文注释）" hidden>复制代码</button></div><pre><code class="python" data-solution="{id}" id="python-{id}">{highlight(source)}</code></pre><p class="copy-status" role="status" aria-live="polite"></p></div>'

def problem_html(p,meta):
    id=p['id']; examples=p['examples']
    url=meta['url'] or 'https://leetcode.cn/problems/'+p['slug']+'/'
    out=f'<section class="chapter problem" id="q{id}" data-problem="{id}"><div class="meta"><span>{esc(meta["scope"])}</span><span>{esc(meta["difficulty"])}</span><span>{esc(meta["frequency"])}</span><span>{meta["priority"]}</span></div><h2><a class="problem-title-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer" title="在新标签页打开力扣中文站原题">{id}. {esc(meta["title"])}<span class="external-link-icon" aria-hidden="true"> ↗</span></a></h2>'
    if p.get('submission'):
        out+='<p class="small">Python 3.12 推荐提交：'+esc(p['submission']['name'])+'。本题同时保留基础推导，代码前另有推荐方法说明。</p>'
    out+='<h3>题目要解决什么</h3>'+paragraphs(p['summary'])
    if p.get('notation'):
        out+='<div class="notation-guide"><h3>先认清本题的状态与变量</h3>'+paragraphs(p['notation']['intro'])
        out+=table(p['notation']['headers'],p['notation']['rows'])+'</div>'
    out+='<h3>从朴素解法到关键观察</h3>'+paragraphs(p['baseline'])+paragraphs(p['insight'])
    for section in p.get('insight_sections',[]):
        out+='<div class="reasoning-step"><h4>'+esc(section['title'])+'</h4>'+paragraphs(section['body'])
        if section.get('diagram'):out+='<pre class="diagram">'+esc(section['diagram'])+'</pre>'
        if section.get('table'):out+=table(section['table']['headers'],section['table']['rows'])
        out+='</div>'
    out+='<h3>'+('基础推导与对照步骤' if p.get('submission') else '一步一步推导算法')+'</h3>'+listing(p['steps'])
    out+='<div class="note"><strong>为什么这样做是正确的</strong>'+paragraphs(p['invariant'])+'</div>'
    options=''.join(f'<option value="{i}">{esc(e["label"])}</option>' for i,e in enumerate(examples))
    out+=f'<div class="demo" id="demo-{id}"><div class="demo-head"><h3>可视化推演</h3><label for="case-{id}">例子<select id="case-{id}">{options}</select></label></div><p class="example-io"><strong>输入：</strong>{esc(examples[0]["input"])}<br><strong>输出：</strong>{esc(examples[0]["output"])}</p><div class="visual">{trace_view(examples[0]["frames"][0])}</div><div class="control-row"><button data-action="first" type="button">回到开头</button><button data-action="prev" type="button">上一步</button><button data-action="play" type="button" aria-pressed="false">自动播放</button><button data-action="next" type="button" class="primary">下一步</button><button data-action="last" type="button">看结果</button></div><div class="timeline"><input type="range" min="0" max="{len(examples[0]["frames"])-1}" value="0" aria-label="第 {id} 题演示进度"><span class="counter"></span></div></div>'
    out+='<h3>对照例子理解关键步骤</h3>'+listing(p['walkthrough'])
    if p.get('submission'):
        submit=p['submission']
        out+='<div class="submission-guide"><h3>推荐提交解法：'+esc(submit['name'])+'</h3>'+paragraphs(submit['why'])+listing(submit['steps'])
        if submit.get('diagram'):out+='<pre class="diagram">'+esc(submit['diagram'])+'</pre>'
        out+='</div>'
    out+='<details class="solution" open><summary>Python 3.12 完整解法 · 中文注释 · 可独立提交</summary>'
    if p.get('api'): out+='<div class="api"><pre>'+esc(p['api']['signature'])+'</pre>'+paragraphs(p['api']['description'])+'</div>'
    out+=code_block(id,p['code'])+'</details>'
    out+='<h3>代码与思路怎样对应</h3>'+listing(p['code_notes'])
    out+=p.get('supplement_html','')
    out+='<div class="pitfall"><strong>常见错误与边界</strong>'+listing(p['pitfalls'])+'</div>'
    out+='<p><strong>复杂度：</strong>'+esc(p['complexity'])+'</p>'
    if p.get('alternative'):out+='<h3>另一种解法与迁移</h3>'+paragraphs(p['alternative'])
    out+='<details class="quiz"><summary>自测：'+esc(p['quiz']['question'])+'</summary>'+paragraphs(p['quiz']['answer'])+'</details>'
    out+=f'<p class="source">原题：<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{id}. {esc(meta["title"])}</a></p><a href="#top" class="small">回到本章目录 ↑</a></section>'
    return out

def shell(title,nav,body,data=None):
    css='\n'.join((ROOT/'assets'/p).read_text() for p in ('base.css','book.css'))
    js='\n'.join((ROOT/'assets'/p).read_text() for p in ('copy.js','book.js')) if data is not None else ''
    if data and data.get('foundation')=='prefix-sum':
        css+='\n'+(ROOT/'assets/prefix.css').read_text()
        js+='\n'+(ROOT/'assets/prefix.js').read_text()
    data_tag='<script id="book-data" type="application/json">'+json.dumps(data or {},ensure_ascii=False).replace('</','<\\/')+'</script>'
    js=typography.script()+'\n'+js
    return typography.document(f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{esc(title)}</title><style>{css}</style></head><body><div class="layout"><aside class="sidebar"><p class="brand">ALGORITHM STUDY BOOK</p><p class="name">160 题 · 方法与推导</p>{nav}</aside><main id="main">{body}</main></div>{data_tag}<script>{js}</script></body></html>')

def load_content(c):
    file=ROOT/'content'/f'{c["number"]:02d}.py'
    if not file.exists():return None
    data=runpy.run_path(str(file))['CHAPTER']
    from teaching import apply_teaching
    data=apply_teaching(data,c['number'])
    expected={p['id'] for p in c['problems']}
    actual=[p['id'] for p in data['problems']]
    assert len(actual)==len(set(actual)) and set(actual)==expected, (c['number'],'coverage',expected-set(actual),set(actual)-expected)
    for p in data['problems']:
        if p['id']==136:
            for example in p['examples']:
                for frame in example['frames']:frame['notation_mode']='code'
        for field in ('summary','baseline','insight','steps','invariant','examples','walkthrough','code','code_notes','pitfalls','complexity','quiz','tests'):
            assert p.get(field), (p['id'],'missing',field)
        for e in p['examples']:
            assert e['frames'] and e['input'] is not None and e['output'] is not None
            for frame in e['frames']:
                assert frame.get('title') and frame.get('note')
                assert any(k in frame for k in ('array','diagram','table','panels','grid')), (p['id'],'missing visual')
    return data

def build():
    OUT.mkdir(exist_ok=True)
    chapters=catalog();content={c['number']:load_content(c) for c in chapters}
    ready=[c for c in chapters if content[c['number']]]
    n=sum(len(c['problems']) for c in ready)
    for c in ready:
        data=content[c['number']];meta={p['id']:p for p in c['problems']}
        nav='<nav aria-label="本章导航"><a href="index.html">← 全部章节</a><a href="#prerequisites">前置知识与基础概念</a><a href="#method">本章方法</a>'
        if data.get('foundation')=='prefix-sum':
            nav+='<div class="prefix-nav"><a href="#prefix-definition">先修：前缀和是什么</a><a href="#prefix-construction">构建前缀表</a><a href="#prefix-query">区间求和演示</a><a href="#prefix-code">基础代码</a></div>'
        nav+='<div class="nav-filters" role="group" aria-label="题目导航筛选" hidden><button type="button" data-nav-filter="all" aria-pressed="true">全部题目</button><button type="button" data-nav-filter="hot" aria-pressed="false">只看 Hot100</button></div><p class="nav-summary" role="status" aria-live="polite" hidden></p>'
        for p in data['problems']:
            is_hot=meta[p['id']]['scope']=='Hot 100'
            scope='hot' if is_hot else 'extra'
            label='Hot100' if is_hot else '非 Hot100'
            nav+=f'<a class="problem-nav-link" data-nav-problem="{p["id"]}" data-nav-scope="{scope}" href="#q{p["id"]}"><span class="nav-title">{p["id"]} {esc(meta[p["id"]]["title"])}</span><span class="nav-scope nav-scope-{scope}">{label}</span></a>'
        nav+='</nav>'
        body=f'<header class="hero" id="top"><p class="eyebrow">CHAPTER {c["number"]:02d} / 17</p><h1>{esc(c["title"])}</h1><p class="lead">{esc(data["lead"])}</p><div class="meta"><span>Hot 100 · {c["hot"]} 题</span><span>非 Hot 100 · {c["extra"]} 题</span><span>离线高亮与复制</span></div><div class="top-actions"><a href="index.html">返回总目录</a><button id="print" type="button">打印 / 保存为 PDF</button></div><p class="small">考频标签沿用大纲的经验估计，不是实际面试次数或命中概率。</p></header>'
        body+='<section class="chapter foundations" id="prerequisites"><h2>前置知识与基础概念</h2><div class="note"><strong>进入这一章之前</strong>'+paragraphs(data['prerequisites'])+'</div>'
        for section in data['foundational_sections']:
            body+='<div class="foundation-concept"><h3>'+esc(section['title'])+'</h3>'+paragraphs(section['body'])+'<pre class="diagram">'+esc(section['diagram'])+'</pre></div>'
            if c['number']==5 and section['title']=='矩阵坐标与移动方向':
                body+='<div class="formula-card"><p>矩阵大小与合法坐标</p>'+typography.math_html('m × n',True)+typography.math_html('0 ≤ r < m, 0 ≤ c < n',True)+'<p>行下标与行数比较，列下标与列数比较。</p></div>'
        if data.get('foundation')=='prefix-sum':
            from prefix_foundation import render as render_prefix_foundation
            body+=render_prefix_foundation(highlight)
        body+='</section><section class="chapter" id="method"><h2>从基础概念走到本章方法</h2>'+paragraphs(data['intro'])
        for section in data.get('sections',[]):
            body+='<h3>'+esc(section['title'])+'</h3>'+paragraphs(section['body'])
            if section.get('diagram'):body+='<pre class="diagram">'+esc(section['diagram'])+'</pre>'
            if section.get('diagram_svg'):
                asset=section['diagram_svg']
                assert Path(asset).name==asset and asset.endswith('.svg')
                body+='<figure class="svg-diagram" style="margin:22px 0">'+(ROOT/'assets'/asset).read_text()+'</figure>'
        for api in data.get('apis',[]):body+='<div class="api"><pre>'+esc(api['signature'])+'</pre>'+paragraphs(api['description'])+'</div>'
        body+='<div class="note"><strong>本章学习路径</strong><p>'+esc(' → '.join(str(p['id'])+' '+meta[p['id']]['title'] for p in data['problems']))+'</p></div></section>'
        body+=''.join(problem_html(p,meta[p['id']]) for p in data['problems'])
        body+='<footer><p>题意为学习用途简述；每题均提供原题链接。示例推演用于解释算法，代码可单独复制提交。打印会自动展开代码与自测答案。</p><p>关联章节：'+ ' · '.join(f'<a href="{x["filename"]}">{x["number"]:02d} {esc(x["title"])}</a>' for x in ready if x['number']!=c['number'])+'</p><a href="index.html">返回全部章节</a></footer>'
        ui = {'problems': [{'id':p['id'], 'examples':[dict(label=e['label'],input=e['input'],output=e['output'],frames=[trace_view(f) for f in e['frames']]) for e in p['examples']]} for p in data['problems']]}
        if data.get('foundation'):
            ui['foundation']=data['foundation']
        (OUT/c['filename']).write_text(shell(c['title'],nav,body,ui))
    tiles=''
    for c in chapters:
        exists=content[c['number']] is not None
        title=f'{c["number"]:02d}. {esc(c["title"])}'
        title=f'<a href="{c["filename"]}">{title}</a>' if exists else title
        tiles+=f'<li class="chapter-entry"><h3>{title}</h3><p>{len(c["problems"])} 题 · Hot 100 {c["hot"]} / 扩展 {c["extra"]}</p><span class="tag">{"已生成，进入阅读" if exists else "待编写"}</span></li>'
    body=f'<header class="hero" id="top"><p class="eyebrow">HOT 100 + INTERVIEW PRACTICE</p><h1>算法学习文档</h1><p class="lead">按 17 个专题，从问题与例子推导算法。每题讲清楚为什么这样做，再对照代码理解实现。</p><div class="meta"><span>160 道题</span><span>100 道主线 + 60 道扩展</span><span>已生成 {len(ready)} / 17 章 · {n} / 160 题</span></div></header><section class="chapter"><h2>按章节阅读</h2><p>各章可单独离线打开；代码具有语法高亮与复制按钮，例子可逐步播放。章节内按前置关系安排主线与扩展题。</p><ul class="chapter-list">{tiles}</ul></section><footer><a href="../Hot100重新分类与面试备考大纲.md">查看完整分类与优先级大纲</a><p>高频、常考为备考经验估计。阅读顺序兼顾前置知识，不等同于面试频次排序。</p></footer>'
    body=body.replace('<footer>','<section class="chapter"><h2>阅读顺序与独立手册</h2><p>先看专题前置知识与基础概念，再明确每题状态和变量，最后对照推导、演示与中文算法注释实现。默认掌握 Python 基础语法。</p><p><a href="../Hot100高频20题学习手册.html">Hot100 高频 20 题学习手册</a> · <a href="../滑动窗口九题学习指南.html">滑动窗口九题学习指南</a></p><p>两本独立手册已同步算法前置知识、状态说明与中文注释。</p></section><footer>',1)
    (OUT/'index.html').write_text(shell('算法学习文档 · 17 章 160 题','<a href="#top">章节总目录</a>',body))
    progress='# 当前制作进展\n\n目标保持为 17 章、160 题的详细 HTML 学习文档。下表“已生成”只说明章节存在，不替代代码、内容与浏览器审阅。\n\n'
    progress+=f'已生成：{len(ready)} / 17 章，{n} / 160 题。\n\n| 章 | 名称 | 题数 | 状态 |\n| --- | --- | ---: | --- |\n'
    for c in chapters:progress+=f'| {c["number"]:02d} | {c["title"]} | {len(c["problems"])} | {"已生成，需结合验证记录审阅" if content[c["number"]] else "待编写"} |\n'
    progress+='\n全部章节已生成。内容审阅见 CONTENT_REVIEW.md，最终范围与证据见 COMPLETION_AUDIT.md；修改后须重新核对代码、HTML 与验证报告摘要，生成状态本身不代表验证结果。\n' if len(ready)==17 and n==160 else '\n继续撰写未完成章节，并核对代码、可视化、复制、手机布局与打印。局部通过不等于完成整个目标。\n'
    (ROOT/'PROGRESS.md').write_text(progress)
    print(f'Generated {len(ready)}/17 chapters, {n}/160 problems; index: {OUT / "index.html"}')

if __name__ == '__main__':build()
