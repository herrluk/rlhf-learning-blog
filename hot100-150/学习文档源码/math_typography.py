"""离线数学排版；仅处理说明文字，保留代码、数据、ASCII 图的原文。"""
from functools import lru_cache
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import base64
import re

ASSETS = Path(__file__).resolve().parent / 'assets'
# 只收集数学字符。中文是天然分隔符；版本号、日期和纯数字不改写。
RUN = re.compile(r'[A-Za-z0-9_αβγθλπΣ∞][A-Za-z0-9_αβγθλπΣ∞ \t.\[\](){}+*/=<>!,:^%²³ⁿ−×÷≤≥≠→…-]*|[\[({][A-Za-z0-9_αβγθλπΣ∞ \t.\[\](){}+*/=<>!,:^%²³ⁿ−×÷≤≥≠→…-]+')
TOKENS = re.compile(r'\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*|<=|>=|!=|==|\*\*|\s+|.', re.S)
PROTECTED = re.compile(r'\b(?:Python|Hot|Hot100|CHAPTER|MODULE|LeetCode|API|HTML|PDF|JavaScript|HOW|STUDY|REPORTED|SAMPLE|INTERVIEW|CORE|RECALL|WITHOUT|THE|ANSWER|ALGORITHM|FIELD|NOTES|BFS|DFS|LRU|LFU|DP|ASCII|Unicode|UTF|IP|vs)\b')
BLOCKED = {'pre','code','script','style','textarea','button','select','option','nav','aside','a','math','svg','title'}
ELIGIBLE = {'p','li','td','th','h3','h4','h5','summary'}

def formula(source):
    """保持索引的方括号记法；指数用上标；程序标识符用正体。"""
    tokens = TOKENS.findall(source)
    pieces = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        i += 1
        if t.isspace():
            # log n、n log n 中保留函数与操作数之间的空隙。
            pieces.append('<mspace width="0.18em"></mspace>')
            continue
        if t in ('^','**') and pieces and i < len(tokens):
            while pieces and pieces[-1].startswith('<mspace'):pieces.pop()
            while i<len(tokens) and tokens[i].isspace():i+=1
            if not pieces or i==len(tokens):
                pieces.append('<mo>'+escape(t)+'</mo>');continue
            exponent=tokens[i]; i+=1
            if exponent in ('(', '{'):
                end=')' if exponent=='(' else '}'; collected=[]; depth=1
                while i<len(tokens) and depth:
                    item=tokens[i];i+=1
                    if item==exponent:depth+=1
                    if item==end:depth-=1
                    if depth:collected.append(item)
                exponent=''.join(collected)
            pieces[-1]='<msup>'+pieces[-1]+'<mrow>'+formula(exponent)+'</mrow></msup>'
        elif t in ('²','³','ⁿ') and pieces:
            pieces[-1]='<msup>'+pieces[-1]+formula({'²':'2','³':'3','ⁿ':'n'}[t])+'</msup>'
        elif re.fullmatch(r'\d+(?:\.\d+)?',t): pieces.append('<mn>'+t+'</mn>')
        elif re.fullmatch(r'[A-Za-z_][A-Za-z_0-9.]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*',t):
            if len(t)==1: pieces.append('<mi>'+t+'</mi>')
            elif t in ('log','min','max','gcd','lcm','abs','sqrt','sin','cos'):
                pieces.append('<mi mathvariant="normal">'+t+'</mi>')
            elif t in ('mn','nk','nm'): pieces.append(''.join('<mi>'+x+'</mi>' for x in t))
            else: pieces.append('<mi class="math-identifier" mathvariant="normal">'+escape(t)+'</mi>')
        else:
            symbol={'<=':'≤','>=':'≥','!=':'≠','==':'=','*':'×'}.get(t,t)
            pieces.append('<mo>'+escape(symbol)+'</mo>')
    return ''.join(pieces)

def math_html(source, display=False):
    return ('<span class="math-run'+(' math-display' if display else '')+'" data-math-source="'+escape(source)+'">'
            '<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="'+escape(source)+'"><mrow>'+formula(source)+'</mrow></math></span>')

def text_html(text, code_operators=False):
    changed=False
    def replace(match):
        nonlocal changed
        original=match.group(); core=original.rstrip(' \t.,:'); tail=original[len(core):]
        if not core or PROTECTED.search(core):return escape(original)
        if not re.search(r'[A-Za-z_αβγθλπΣ∞+*/=<>^²³ⁿ−×÷≤≥≠]',core):return escape(original)
        calls=re.findall(r'([A-Za-z_][A-Za-z_0-9.]*)\s*\(',core)
        is_code_call=any(len(name)>1 and name not in {'log','min','max','gcd','lcm','abs','sqrt','floor'} for name in calls)
        # ^ 在异或讲解和 Python 代码里是运算符，绝不能排成指数。
        if is_code_call or (any(op in core for op in ('^','**')) and (code_operators or '异或' in text or '^=' in core)):
            changed=True
            return '<code class="inline-identifier">'+escape(core)+'</code>'+escape(tail)
        # 英文短句不作为一整个公式；独立的程序标识符用等宽字。
        if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9.]*',core) and len(core)>1:
            changed=True
            return '<code class="inline-identifier">'+escape(core)+'</code>'+escape(tail)
        if re.fullmatch(r'[A-Za-z]+(?:\s+[A-Za-z]+)+',core) and 'log' not in core.split():return escape(original)
        changed=True
        return math_html(core, len(core)>48 and bool(re.search(r'=|≤|≥|<|>',core)))+escape(tail)
    result=[];end=0
    for match in RUN.finditer(text):
        result.extend((escape(text[end:match.start()]),replace(match)));end=match.end()
    result.append(escape(text[end:]))
    # 原文便于内容审计；可见内容由真正的 MathML 节点展示。
    return '<span class="notation-text" data-notation-source="'+escape(text)+'">'+''.join(result)+'</span>' if changed else escape(text)

class Typesetter(HTMLParser):
    def __init__(self, code_operators=False):
        super().__init__(convert_charrefs=False); self.parts=[];self.stack=[];self.code_operators=code_operators
    def handle_starttag(self,tag,attrs):
        self.parts.append(self.get_starttag_text())
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append((tag,dict(attrs)))
    def handle_startendtag(self,tag,attrs):self.parts.append(self.get_starttag_text())
    def handle_endtag(self,tag):
        self.parts.append('</'+tag+'>')
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:del self.stack[i:];break
    def handle_data(self,data):
        tags={t for t,a in self.stack}
        classes={x for t,a in self.stack for x in a.get('class','').split()}
        if tags&{'script','style'}:self.parts.append(data)
        elif tags&BLOCKED or 'notation-text' in classes or 'math-run' in classes:
            self.parts.append(escape(data))
        elif tags&ELIGIBLE or classes&{'equation','status'}:
            code_mode=self.code_operators or any(a.get('id') in {'q136','demo-136'} for t,a in self.stack)
            self.parts.append(text_html(unescape(data),code_mode))
        else:self.parts.append(escape(data))
    def handle_entityref(self,name):self.parts.append('&'+name+';')
    def handle_charref(self,name):self.parts.append('&#'+name+';')
    def handle_comment(self,data):self.parts.append('<!--'+data+'-->')
    def handle_decl(self,decl):self.parts.append('<!'+decl+'>')

def typeset_html(doc, code_operators=False):
    # 先合并普通文本内的字符实体，避免小于号把一个公式分成几段。
    parser=Typesetter(code_operators)
    # HTMLParser convert_charrefs=True 不会改写 script/style，且可完整读取公式。
    parser.convert_charrefs=True
    parser.feed(doc);parser.close()
    return ''.join(parser.parts)

@lru_cache(maxsize=1)
def styles():
    font=base64.b64encode((ASSETS/'DejaVuMathTeXGyre.ttf').read_bytes()).decode()
    license=(ASSETS/'MATH-FONT-LICENSE.txt').read_text().replace('*/','* /')
    return '/* '+license+' */\n@font-face{font-family:StudyMath;src:url(data:font/ttf;base64,'+font+') format("truetype");font-display:swap}\n'+(ASSETS/'math.css').read_text()

def script():return (ASSETS/'math.js').read_text()

def document(doc):
    doc=typeset_html(doc)
    return doc.replace('</style>', '\n'+styles()+'\n</style>',1)
