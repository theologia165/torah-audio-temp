import urllib.request, xml.etree.ElementTree as ET, html, pathlib, re
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
LEXNS={'l':'http://openscriptures.github.com/morphhb/namespace'}
xml=urllib.request.urlopen('https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml').read()
root=ET.fromstring(xml)
lex_xml=urllib.request.urlopen('https://raw.githubusercontent.com/openscriptures/HebrewLexicon/master/HebrewStrong.xml').read()
lex_root=ET.fromstring(lex_xml)
LEMMA={}
for entry in lex_root.findall('l:entry',LEXNS):
    eid=entry.attrib.get('id','')
    w=entry.find('l:w',LEXNS)
    if eid and w is not None and w.text:
        LEMMA[eid]=w.text.strip()
G={
8:['そして言った','神は','〜に','ノア','そして〜に','彼の息子たち','彼と共に','言って'],
9:['そして私は','見よ私が','確立する','〜を','私の契約','あなたがたと','そして〜を','あなたがたの子孫','あなたがたの後に'],
10:['そして〜を','すべての','命','生きている','それは','あなたがたと共に','鳥のうち','家畜のうち','そしてすべての','生き物','地の','あなたがたと共に','すべてのものから','出る者たち','箱舟の','すべての','生き物','地の'],
11:['そして私は確立する','〜を','私の契約','あなたがたと','そして〜ない','断たれる','すべての','肉なるもの','もはや','水によって','洪水の','そして〜ない','ある','もはや','洪水','滅ぼすため','地を'],
12:['そして言った','神は','これが','しるし','契約の','それを','私は','与える','私と','あなたがたとの間','そして間に','すべての','命','生きる','その','あなたがたと','世代のため','永遠の'],
13:['〜を','私の虹','私は置いた','雲の中に','そしてそれはなる','しるしとして','契約の','私と','そして間に','地との'],
14:['そして〜とき','私が雲らせるとき','雲を','〜の上に','地','そして現れる','その虹が','雲の中に'],
15:['そして私は覚える','〜を','私の契約','その','私と','あなたがたとの間','そして間に','すべての','命','生きる','すべての','肉なるもの','そして〜ない','なる','もはや','その水が','洪水に','滅ぼすため','すべての','肉なるもの'],
16:['そしてある','その虹が','雲の中に','そして私はそれを見る','覚えるため','契約を','永遠の','間の','神','そして間に','すべての','命','生きる','すべての','肉なるもの','その','〜の上に','地'],
17:['そして言った','神は','〜に','ノア','これが','しるし','契約の','その','私は確立した','私と','そして間に','すべての','肉なるもの','その','〜の上に','地']}
POS={'V':'動詞','N':'名詞','A':'形容詞/数詞','R':'前置詞','C':'接続詞','P':'代名詞','T':'小辞','D':'副詞'}
STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael'}
def decode(m):
    raw=m[1:] if m.startswith('H') else m
    parts=raw.split('/')
    lexical=[p for p in parts if p and not p.startswith('S')]
    core=lexical[-1] if lexical else (parts[0] if parts else '')
    pos=POS.get(core[:1],'機能語')
    stem='—'
    if core.startswith('V') and len(core)>1:
        stem=STEM.get(core[1],'—')
    return pos,stem,raw

def strong_id(s):
    raw=s.split('/')[-1].strip().split()[0] if s else ''
    m=re.search(r'(\d+)',raw)
    return 'H'+m.group(1) if m else ''

def hebrew_lemma(s):
    sid=strong_id(s)
    return LEMMA.get(sid, sid or '—')

def make(v):
    verse=root.find(f".//o:verse[@osisID='Gen.9.{v}']",NS)
    ws=verse.findall('o:w',NS)
    gloss=G[v]
    if len(ws)!=len(gloss): raise SystemExit(f'gloss mismatch {v}: {len(ws)} != {len(gloss)}')
    gloss_iter=iter(gloss)
    pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            word=(child.text or '').replace('/','')
            gl=next(gloss_iter)
            lemma=hebrew_lemma(child.attrib.get('lemma',''))
            pos,stem,infl=decode(child.attrib.get('morph',''))
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>')
        elif tag=='seg':
            t=child.attrib.get('type','')
            if t=='x-maqqef': pieces.append('<span class="pun">־</span>')
            elif t=='x-sof-pasuq': pieces.append('<span class="pun">׃</span>')
    css='''<style>html,body{margin:0;background:#fff}body{padding:20px 8px 52px;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Yu Gothic",sans-serif}.row{direction:rtl;display:flex;flex-wrap:wrap;gap:18px 13px;padding:0 8px;line-height:1.03;align-items:flex-start}.unit{position:relative;display:flex;flex-direction:column;align-items:center;min-width:34px;padding:1px 2px;outline:none}.hw{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px);direction:rtl}.gl{direction:ltr;font-size:12px;margin-top:5px;white-space:nowrap}.pun{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px)}.pop{display:none;position:fixed;z-index:50;background:white;border:1px solid #ddd;border-radius:10px;padding:9px 11px;box-shadow:0 4px 18px #0002;font-size:12px;line-height:1.5;direction:ltr;max-width:min(260px,86vw)}.pop b{display:block;font-size:1.3em}.pop .lemma{font-family:"Noto Serif Hebrew","Times New Roman",serif}.pop span{display:block}.pop b .lemma{display:inline}.unit:hover .pop,.unit:focus .pop{display:block}@media(max-width:600px){.hw,.pun{font-size:clamp(36px,11vw,44px)}.gl{font-size:12px}}</style>'''
    js='''<script>const units=[...document.querySelectorAll('.unit')];function place(u){const p=u.querySelector('.pop');p.style.display='block';const r=u.getBoundingClientRect(),pr=p.getBoundingClientRect();let x=Math.max(8,Math.min(innerWidth-pr.width-8,r.left+r.width/2-pr.width/2));let y=Math.max(8,Math.min(innerHeight-pr.height-8,r.bottom+6));p.style.left=x+'px';p.style.top=y+'px'}units.forEach(u=>{u.addEventListener('mouseenter',()=>place(u));u.addEventListener('mouseleave',()=>u.querySelector('.pop').style.display='');u.addEventListener('focus',()=>place(u));u.addEventListener('blur',()=>u.querySelector('.pop').style.display='');u.addEventListener('click',e=>{e.stopPropagation();units.forEach(x=>{if(x!==u)x.querySelector('.pop').style.display=''});place(u)})});document.addEventListener('click',()=>units.forEach(u=>u.querySelector('.pop').style.display=''));</script>'''
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+css+'<body><div class="row">'+''.join(pieces)+'</div>'+js+'</body></html>'

out=pathlib.Path('012/html'); out.mkdir(parents=True,exist_ok=True)
for v in range(8,18): (out/f'Genesis-9-{v}.html').write_text(make(v),encoding='utf-8')
