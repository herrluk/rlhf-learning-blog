"""全书范围与证据绑定。内容质量仍依据逐题审阅记录，不由字段存在性代替。"""
from collections import Counter
from pathlib import Path
import hashlib, html, json, re
from catalog import ROOT, OUT, catalog
from build import load_content
from verify import Extract


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    chapters=catalog();assert len(chapters)==17
    expected={p['id']:p for c in chapters for p in c['problems']}
    scopes=Counter(p['scope'] for p in expected.values())
    assert len(expected)==160 and scopes=={'Hot 100':100,'非 Hot 100':60}
    contents={c['number']:load_content(c) for c in chapters}
    assert all(contents.values())
    code_hashes={};files=[];examples=frames=0
    text_fields=('summary','baseline','insight','steps','invariant','walkthrough','code_notes','pitfalls','complexity')
    for c in chapters:
        path=OUT/c['filename'];source=path.read_text();data=contents[c['number']]
        parsed=Extract();parsed.feed(source)
        assert 'prerequisites' in parsed.ids and html.escape(data['prerequisites']) in source
        for section in data['foundational_sections']:
            assert all(html.escape(value) in source for value in [section['title']]+section['body']+[section['diagram']])
        for section in data.get('sections',[]):
            if section.get('diagram_svg'):
                svg=ROOT/'assets'/section['diagram_svg']
                assert svg.read_text() in source,(c['number'],'missing or stale embedded SVG',svg.name)
        assert set(parsed.problems)=={p['id'] for p in c['problems']}
        assert len(parsed.ids)==len(set(parsed.ids))
        assert not re.search(r'<script[^>]+src=|<link[^>]+rel=["\']stylesheet',source,re.I)
        for link in parsed.links:
            if link.startswith('#'):assert link[1:] in parsed.ids
            elif not re.match('[a-z]+:',link):assert (path.parent/link.split('#')[0]).exists()
        for p in data['problems']:
            pid=p['id'];meta=expected[pid]
            assert pid not in code_hashes
            code_hashes[pid]=hashlib.sha256(p['code'].encode()).hexdigest()
            assert parsed.codes[pid]==p['code']
            block=re.search(r'<section[^>]+data-problem="'+str(pid)+r'">(.*?)</section>',source,re.S).group(1)
            for field in ('scope','difficulty','frequency','priority'):
                assert '<span>'+html.escape(meta[field])+'</span>' in block,(pid,field)
            nav=re.search(r'<a[^>]+data-nav-problem="'+str(pid)+r'"[^>]*>(.*?)</a>',source,re.S)
            assert nav,(pid,'missing navigation entry')
            nav_label='Hot100' if meta['scope']=='Hot 100' else '非 Hot100'
            assert re.search(r'<span class="nav-scope[^\"]*">'+nav_label+r'</span>',nav.group(1)),(pid,'navigation scope label')
            for field in text_fields:
                values=p[field] if isinstance(p[field],list) else [p[field]]
                assert all(html.escape(str(value)) in block for value in values),(pid,field,'missing rendered teaching')
            assert html.escape(p['quiz']['question']) in block and html.escape(p['quiz']['answer']) in block
            assert p.get('notation'),(pid,'missing algorithm state definitions')
            if p.get('notation'):
                notation=p['notation']
                values=notation['intro']+notation['headers']+[v for row in notation['rows'] for v in row]
                assert all(html.escape(str(value)) in block for value in values),(pid,'missing notation guide')
            for section in p.get('insight_sections',[]):
                values=[section['title']]+section['body']+[section.get('diagram','')]
                if section.get('table'):
                    values+=section['table']['headers']+[str(v) for row in section['table']['rows'] for v in row]
                assert all(html.escape(value) in block for value in values),(pid,'missing insight section')
            if p.get('submission'):
                submit=p['submission']
                values=[submit['name'],submit['why'],submit.get('diagram','')]+submit['steps']
                assert all(html.escape(value) in block for value in values),(pid,'missing recommended solution explanation')
            url=meta['url'] or 'https://leetcode.cn/problems/'+p['slug']+'/'
            assert 'href="'+url+'"' in block,(pid,'source link')
            assert p['examples'] and p['tests']['cases']
            examples+=len(p['examples']);frames+=sum(len(e['frames']) for e in p['examples'])
        files.append({'chapter':c['number'],'file':c['filename'],'problems':len(data['problems']),'html_sha256':digest(path),'source_sha256':digest(ROOT/'content'/f'{c["number"]:02d}.py')})
    assert set(code_hashes)==set(expected)
    index=Extract();index.feed((OUT/'index.html').read_text())
    assert {c['filename'] for c in chapters}<=set(index.links)
    for link in index.links:
        if not link.startswith('#') and not re.match('[a-z]+:',link):assert (OUT/link).exists()
    fixed=json.loads((ROOT/'verification.json').read_text())
    assert fixed['generated_chapters']==17 and fixed['covered_problems']==160
    assert fixed['chapters']==[{k:v for k,v in entry.items() if k!='file'} for entry in files]
    reference_names=['algorithm','arrays','linked','stacks','heaps','trees','graphs','backtracking','greedy','design','dp']
    covered={};reference_evidence=[]
    for name in reference_names:
        path=ROOT/f'{name}-verification.json';report=json.loads(path.read_text());assert report['status']=='PASS'
        checks={int(pid):h for pid,h in report['code_sha256'].items()} if name=='algorithm' else {item['id']:item['code_sha256'] for item in report['checks']}
        assert not set(covered)&set(checks),(name,'duplicate coverage')
        assert all(code_hashes[pid]==h for pid,h in checks.items()),(name,'stale code')
        covered.update(checks)
        reference_evidence.append({'report':path.name,'sha256':digest(path),'problems':len(checks)})
    assert covered==code_hashes
    runtime=json.loads((ROOT/'python312-verification.json').read_text())
    assert runtime['status']=='PASS' and runtime['python_version'].startswith('3.12.')
    assert runtime['problems']==160
    assert {entry['id']:entry['code_sha256'] for entry in runtime['checks']}==code_hashes
    assert all(entry['chinese_comment_lines']>=2 for entry in runtime['checks'])
    for entry in runtime['reference_reports']:
        assert entry['sha256']==digest(ROOT/entry['file']),(entry['file'],'stale Python 3.12 runtime evidence')
    browser=json.loads((ROOT/'browser-verification.json').read_text());assert browser['status']=='PASS'
    assert len(browser['chapters'])==17 and browser['codeCount']==160
    assert browser['caseCount']==examples and browser['frameCount']==frames
    for item in browser['chapters']:assert item['html_sha256']==digest(OUT/item['file']),(item['file'],'stale browser report')
    for flag in ('offline','realClipboard','fallbackCopy','deniedCopySelection','printExpandRestore','highlightWithoutJavaScript'):assert browser[flag]
    assert browser['errors']==[] and browser['responsiveWidths']==[1440,1024,760,390,360]
    navigation=browser['navigation']
    assert navigation['hotLabels']==100 and navigation['extraLabels']==60
    for flag in ('filter','anchorJump','reloadPreference','crossChapterPreference','withoutStorage','badgesWithoutJavaScript'):assert navigation[flag]
    report={'status':'PASS','chapters':17,'problems':160,'scope_counts':dict(scopes),'fixed_cases':fixed['code_cases_passed'],'examples':examples,'frames':frames,'files':files,'index_sha256':digest(OUT/'index.html'),'outline_sha256':digest(ROOT.parent/'Hot100重新分类与面试备考大纲.md'),'content_review_sha256':digest(ROOT/'CONTENT_REVIEW.md'),'reference_reports':reference_evidence,'browser_report_sha256':digest(ROOT/'browser-verification.json'),'note':'范围、渲染文字、原题与范围标签、代码一致性、固定例子、独立参照代码集合和真实浏览器报告均对应当前产物；逐题教学和代表图示审阅见 CONTENT_REVIEW.md。'}
    report.update(python_version=runtime['python_version'],chinese_comment_lines=runtime['chinese_comment_lines'],python312_report_sha256=digest(ROOT/'python312-verification.json'))
    report['teaching_sources']=[{'file':name,'sha256':digest(ROOT/name)} for name in ('foundations.py','problem_states.py','teaching.py')]
    if contents[4].get('foundation')=='prefix-sum':
        foundation_evidence=[]
        for name in ('prefix-foundation-verification.json','prefix-browser-verification.json'):
            foundation=json.loads((ROOT/name).read_text())
            assert foundation['status']=='PASS'
            assert foundation['html_sha256']==digest(OUT/'04-前缀统计.html'),(name,'stale prefix foundation')
            foundation_evidence.append({'report':name,'sha256':digest(ROOT/name)})
        assert browser['prefixFoundation']['sha256']==digest(ROOT/'prefix-browser-verification.json')
        report['prefix_foundation']=foundation_evidence
    (ROOT/'completion-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:report[k] for k in ('status','chapters','problems','scope_counts','fixed_cases','examples','frames')},ensure_ascii=False))


if __name__=='__main__':audit()
