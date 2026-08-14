import urllib.request, xml.etree.ElementTree as ET, html, pathlib, re
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
LEXNS={'l':'http://openscriptures.github.com/morphhb/namespace'}
root=ET.fromstring(urllib.request.urlopen('https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml').read())
lex_root=ET.fromstring(urllib.request.urlopen('https://raw.githubusercontent.com/openscriptures/HebrewLexicon/master/HebrewStrong.xml').read())
LEMMA={}
for e in lex_root.findall('l:entry',LEXNS):
    eid=e.attrib.get('id',''); w=e.find('l:w',LEXNS)
    if eid and w is not None and w.text: LEMMA[eid]=w.text.strip()
G={
2:['息子たち','ヤフェト','ゴメル','そしてマゴグ','そしてマダイ','そしてヤワン','そしてトバル','そしてメシェク','そしてティラス'],
3:['そして息子たち','ゴメル','アシュケナズ','そしてリファト','そしてトガルマ'],
4:['そして息子たち','ヤワン','エリシャ','そしてタルシシュ','キティム','そしてドダニム'],
5:['これらから','分かれた','沿岸の民々が','諸国民の','彼らの地々で','それぞれ','その言語に従って','彼らの氏族ごとに','彼らの国民の中で'],
6:['そして息子たち','ハム','クシュ','そしてミツライム','そしてプト','そしてカナン'],
7:['そして息子たち','クシュ','セバ','そしてハビラ','そしてサブタ','そしてラアマ','そしてサブテカ','そして息子たち','ラアマ','シェバ','そしてデダン'],
8:['そしてクシュ','生んだ','〜を','ニムロド','彼は','始めた','〜となることを','勇士','地上で'],
9:['彼は','であった','力ある','狩人','YHWHの前で','YHWH','それゆえ','こう','言われる','ニムロドのように','力ある','狩人','YHWHの前で','YHWH'],
10:['そして〜となった','初め','彼の王国の','バベル','そしてエレク','そしてアッカド','そしてカルネ','地で','シンアル'],
11:['〜から','その地','その','出た','アシュル','そして建てた','〜を','ニネベ','そして〜を','レホボト','イル','そして〜を','カラ'],
12:['そして〜を','レセン','〜の間に','ニネベ','そして〜の間に','カラ','それは','その町','大きな'],
13:['そしてミツライム','生んだ','〜を','ルディム','そして〜を','アナミム','そして〜を','レハビム','そして〜を','ナフトヒム'],
14:['そして〜を','パトルシム','そして〜を','カスルヒム','そこから','出た','そこから','ペリシテ人','そして〜を','カフトリム'],
15:['そしてカナン','生んだ','〜を','シドン','彼の長子','そして〜を','ヘト'],
16:['そして〜を','エブス人','そして〜を','エモリ人','そして〜を','ギルガシ人'],
17:['そして〜を','ヒビ人','そして〜を','アルキ人','そして〜を','シニ人'],
18:['そして〜を','アルワド人','そして〜を','ツェマリ人','そして〜を','ハマト人','そしてその後','散らされた','氏族たち','カナン人の'],
19:['そして〜となった','境界','カナン人の','シドンから','向かって','ゲラルへ','〜まで','ガザ','向かって','ソドムへ','そしてゴモラ','そしてアドマ','そしてツェボイム','〜まで','レシャ'],
20:['これらが','息子たち','ハムの','彼らの氏族ごとに','彼らの言語ごとに','彼らの地々で','彼らの国民ごとに'],
21:['そしてセムにも','生まれた','また','彼に','父','すべての','子らの','エベル','兄弟','ヤフェトの','年長の'],
22:['息子たち','セムの','エラム','そしてアシュル','そしてアルパクシャド','そしてルド','そしてアラム'],
23:['そして息子たち','アラム','ウツ','そしてフル','そしてゲテル','そしてマシュ'],
24:['そしてアルパクシャド','生んだ','〜を','シェラ','そしてシェラ','生んだ','〜を','エベル'],
25:['そしてエベルに','生まれた','二人の','息子たち','名','一人の','ペレグ','なぜなら','彼の時代に','分けられた','地が','そして名','彼の兄弟の','ヨクタン'],
26:['そしてヨクタン','生んだ','〜を','アルモダド','そして〜を','シェレフ','そして〜を','ハツァルマベト','そして〜を','イェラフ'],
27:['そして〜を','ハドラム','そして〜を','ウザル','そして〜を','ディクラ'],
28:['そして〜を','オバル','そして〜を','アビマエル','そして〜を','シェバ'],
29:['そして〜を','オフィル','そして〜を','ハビラ','そして〜を','ヨバブ','すべて','これらは','息子たち','ヨクタンの'],
30:['そして〜であった','彼らの住む所','メシャから','向かって','セファルへ','山地','東の'],
31:['これらが','息子たち','セムの','彼らの氏族ごとに','彼らの言語ごとに','彼らの地々で','彼らの国民ごとに'],
32:['これらが','氏族たち','息子たち','ノアの','彼らの系譜ごとに','彼らの国民の中で','そしてこれらから','分かれた','諸国民が','地上で','〜の後','洪水']}
POS={'V':'動詞','N':'名詞','A':'形容詞・数詞','R':'前置詞','C':'接続詞','P':'代名詞','T':'小辞','D':'副詞'}
STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael','o':'Polel','r':'Hithpolel'}
CONJ={'p':'完了形','q':'完了形','i':'未完了形','w':'ワウ継続形','j':'指示・命令形','v':'分詞','r':'分詞','s':'分詞','c':'不定詞連語形'}
def sid(s):
    nums=re.findall(r'\d+',s or '')
    return 'H'+nums[-1] if nums else ''
def lemma(s):
    x=sid(s); return LEMMA.get(x,x or '—')
def decode(m):
    raw=(m or '').lstrip('H'); parts=[p for p in raw.split('/') if p]
    core=next((p for p in reversed(parts) if not p.startswith('S')), parts[-1] if parts else '')
    pos=POS.get(core[:1],'機能語'); stem='—'; infl=core or '—'
    if core.startswith('V'):
        stem=STEM.get(core[1:2],'—'); infl=CONJ.get(core[2:3],'動詞形')+'（'+core+'）'
    elif core.startswith('N'): infl='名詞形（'+core+'）'
    elif core.startswith('A'): infl='形容詞・数詞形（'+core+'）'
    elif core.startswith('R'): infl='前置詞（'+core+'）'
    elif core.startswith('C'): infl='接続詞（'+core+'）'
    elif core.startswith('P'): infl='代名詞（'+core+'）'
    elif core.startswith('T'): infl='小辞（'+core+'）'
    elif core.startswith('D'): infl='副詞（'+core+'）'
    return pos,stem,infl
CSS='''<style>html,body{margin:0;background:#fff}body{padding:20px 8px 52px;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Yu Gothic",sans-serif}.row{direction:rtl;display:flex;flex-wrap:wrap;gap:18px 13px;padding:0 8px;line-height:1.03;align-items:flex-start}.unit{position:relative;display:flex;flex-direction:column;align-items:center;min-width:34px;padding:1px 2px;outline:none}.hw{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px);direction:rtl}.gl{direction:ltr;font-size:12px;margin-top:5px;white-space:nowrap}.pun{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px)}.pop{display:none;position:fixed;z-index:50;background:white;color:#171717;border:1px solid #ddd;border-radius:10px;padding:9px 11px;box-shadow:0 4px 18px #0002;font-size:12px;line-height:1.5;direction:ltr;max-width:min(260px,86vw)}.pop b{display:block}.pop .lemma{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:1.3em}.pop span{display:block}.pop b .lemma{display:inline}.unit:hover .pop,.unit:focus .pop{display:block}@media(max-width:600px){.hw,.pun{font-size:clamp(36px,11vw,44px)}.gl{font-size:12px}}</style>'''
JS='''<script>const U=[...document.querySelectorAll('.unit')];function h(u){u.querySelector('.pop').style.display=''}function p(u){const q=u.querySelector('.pop');q.style.display='block';q.style.visibility='hidden';const r=u.getBoundingClientRect(),z=q.getBoundingClientRect(),m=8;let x=r.left+r.width/2-z.width/2,y=r.bottom+6;if(y+z.height>innerHeight-m)y=r.top-z.height-6;x=Math.max(m,Math.min(innerWidth-z.width-m,x));y=Math.max(m,Math.min(innerHeight-z.height-m,y));q.style.left=x+'px';q.style.top=y+'px';q.style.visibility='visible'}U.forEach(u=>{u.addEventListener('mouseenter',()=>p(u));u.addEventListener('mouseleave',()=>h(u));u.addEventListener('focus',()=>p(u));u.addEventListener('blur',()=>h(u));u.addEventListener('click',e=>{e.stopPropagation();U.forEach(x=>{if(x!==u)h(x)});p(u)})});document.addEventListener('click',()=>U.forEach(h));addEventListener('resize',()=>U.forEach(h));</script>'''
out=pathlib.Path('013/html-fixed'); out.mkdir(parents=True,exist_ok=True)
for v in range(2,33):
    verse=root.find(f".//o:verse[@osisID='Gen.10.{v}']",NS); ws=verse.findall('o:w',NS)
    if len(ws)!=len(G[v]): raise SystemExit(f'gloss mismatch 10:{v} {len(ws)} != {len(G[v])}')
    gi=iter(G[v]); pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            word=(child.text or '').replace('/',''); gl=next(gi); le=lemma(child.attrib.get('lemma','')); po,st,inf=decode(child.attrib.get('morph',''))
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(le)}</span></b><span>品詞：{html.escape(po)}</span><span>語幹：{html.escape(st)}</span><span>活用：{html.escape(inf)}</span></span></span>')
        elif tag=='seg':
            t=child.attrib.get('type','')
            if t=='x-maqqef': pieces.append('<span class="pun">־</span>')
            elif t=='x-sof-pasuq': pieces.append('<span class="pun">׃</span>')
            elif t=='x-paseq': pieces.append('<span class="pun">׀</span>')
    doc='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+CSS+'<body><div class="row">'+''.join(pieces)+'</div>'+JS+'</body></html>'
    (out/f'Genesis-10-{v}-r2.html').write_text(doc,encoding='utf-8')
print('generated',31)
