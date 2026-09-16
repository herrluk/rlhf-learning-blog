"""Build the existing blog and algorithm book into a Pages artifact."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urlsplit
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'hot100-150'
SITE = ROOT / '_site'
REPO = os.environ.get('GITHUB_REPOSITORY', 'herrluk/rlhf-learning-blog')
EDIT = f'https://github.com/{REPO}/edit/main/'


def run(relative):
    script = BOOK / relative
    subprocess.run([sys.executable, str(script)], cwd=script.parent, check=True)


def editor_bar(document, source, home):
    url = EDIT + quote('hot100-150/' + source, safe='/')
    style = '''<style>
    .online-edit-bar{display:flex;flex-wrap:wrap;align-items:center;gap:10px 20px;margin:0 0 22px;padding:12px 16px;background:#e2f1e8;border:1px solid #bdd4c6;border-radius:10px;font-size:14px;line-height:1.7}
    .online-edit-bar a{color:#17674f;font-weight:650;text-underline-offset:3px}
    @media print{.online-edit-bar{display:none}}
    </style>'''
    bar = '<nav class="online-edit-bar" aria-label="在线阅读与编辑">'
    bar += f'<a href="{home}">← 博客首页</a>'
    bar += f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">在线编辑本页</a>'
    bar += f'<a href="{home.replace("index.html", "hot100-150/editing.html")}">编辑说明</a></nav>'
    document = document.replace('</head>', style + '</head>', 1)
    assert '<main id="main">' in document or '<main>' in document
    marker = '<main id="main">' if '<main id="main">' in document else '<main>'
    return document.replace(marker, marker + bar, 1)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def check_links():
    pages = {}
    for file in SITE.rglob('*.html'):
        parsed = Links()
        parsed.feed(file.read_text())
        pages[file.resolve()] = parsed
    count = 0
    for file, parsed in pages.items():
        for href in parsed.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (file.parent / unquote(url.path)).resolve() if url.path else file
            if target.is_dir():
                target /= 'index.html'
            assert target.is_relative_to(SITE.resolve()), (file, href, 'outside site')
            assert target.exists(), (file, href, 'missing target')
            if url.fragment and target in pages:
                assert unquote(url.fragment) in pages[target].ids, (file, href, 'missing anchor')
            count += 1
    print(f'Checked {len(pages)} HTML pages and {count} local links/anchors.')


def build():
    run('学习文档源码/build.py')
    run('学习文档源码/verify.py')
    run('高频20题源码/build_hot20.py')
    run('滑动窗口九题源码/build_window9.py')
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    # Preserve root-level pages/assets, including the existing resource blog.
    for item in ROOT.iterdir():
        if item.name.startswith('.') or item.name in {'_site', 'scripts', 'hot100-150'}:
            continue
        if item.is_file() and item.suffix.lower() in {'.html', '.css', '.js', '.png', '.svg', '.ico', '.txt', '.webp', '.jpg'}:
            shutil.copy2(item, SITE / item.name)
        elif item.is_dir():
            shutil.copytree(item, SITE / item.name)
    for name in ('.nojekyll', 'CNAME'):
        if (ROOT / name).is_file():
            shutil.copy2(ROOT / name, SITE / name)
    target = SITE / 'hot100-150'
    chapters = target / '学习文档'
    chapters.mkdir(parents=True)
    for page in (BOOK / '学习文档').glob('*.html'):
        source = 'Hot100重新分类与面试备考大纲.md' if page.name == 'index.html' else f'学习文档源码/content/{page.name[:2]}.py'
        (chapters / page.name).write_text(editor_bar(page.read_text(), source, '../../index.html'))
    for page, source in [
        ('Hot100高频20题学习手册.html', '高频20题源码/content.py'),
        ('滑动窗口九题学习指南.html', '滑动窗口九题源码/template.html'),
    ]:
        (target / page).write_text(editor_bar((BOOK / page).read_text(), source, '../index.html'))
    for name in ('Hot100重新分类与面试备考大纲.md', 'editing.html', 'index.html'):
        shutil.copy2(BOOK / name, target / name)
    check_links()
    print(f'Built website: {SITE}')


if __name__ == '__main__':
    build()
