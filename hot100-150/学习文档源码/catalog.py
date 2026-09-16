from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
OUTLINE = ROOT.parent / 'Hot100重新分类与面试备考大纲.md'
OUT = ROOT.parent / '学习文档'
SHORT_NAMES = ['哈希查找与集合', '数组与字符串', '滑动窗口', '前缀统计', '矩阵模拟', '二分与有序搜索', '链表基础', '链表进阶', '栈与单调结构', '排序与堆', '二叉树', '图与网格', '回溯', '贪心与区间', '动态规划', '数据结构设计', '约束与数学']

def catalog():
    chapters = []
    text = OUTLINE.read_text()
    for section in re.split(r'(?=^## )', text, flags=re.M):
        match = re.match(r'## (\d{2})\. (.+?)（Hot 100：(\d+) 题；非 Hot 100：(\d+) 题）', section)
        if not match:
            continue
        number = int(match[1])
        chapter = dict(number=number, title=match[2], hot=int(match[3]), extra=int(match[4]), filename=f'{number:02d}-{SHORT_NAMES[number-1]}.html', problems=[])
        for line in section.splitlines():
            if not re.match(r'^\| \d+ \|', line):
                continue
            fields = [s.strip() for s in line.strip('|').split('|')]
            if len(fields) not in (6, 7) or fields[2] not in ('简单', '中等', '困难'):
                continue
            id = int(fields[0])
            linked = re.match(r'\[(.+?)\]\((.+?)\)', fields[1])
            is_extra = len(fields) == 7
            chapter['problems'].append(dict(id=id, title=linked[1] if linked else fields[1], url=linked[2] if linked else '', difficulty=fields[2], scope='非 Hot 100' if is_extra else 'Hot 100', frequency=fields[4] if is_extra else fields[3], priority=fields[5] if is_extra else fields[4], method=fields[6] if is_extra else fields[5]))
        assert len(chapter['problems']) == chapter['hot'] + chapter['extra']
        chapters.append(chapter)
    ids = [p['id'] for c in chapters for p in c['problems']]
    assert len(chapters) == 17 and len(ids) == len(set(ids)) == 160
    return chapters
