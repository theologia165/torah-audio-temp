import html, pathlib
import repair_html_10 as b

# Reuse the verified WLC/MorphHB text, HebrewStrong lemmas, glosses and UI from
# repair_html_10.py, but classify the full MorphHB morpheme chain rather than
# collapsing every lexical N* form to generic 「名詞」.

def segment_label(seg):
    if seg == 'C': return '接続詞'
    if seg in ('R','Rd'): return '前置詞'
    if seg == 'Td': return '定冠詞'
    if seg == 'To': return '目的語標識'
    if seg.startswith('P'): return '代名詞'
    if seg.startswith('T'): return '小辞'
    if seg.startswith('D'): return '副詞'
    return None

def lexical_label(core):
    if core.startswith('Np'): return '固有名詞'
    if core.startswith('Ng'): return '民族名詞'
    if core.startswith('N'): return '名詞'
    if core.startswith('V'): return '動詞'
    if core.startswith('A'): return '形容詞・数詞'
    if core.startswith('R'): return '前置詞'
    if core.startswith('C'): return '接続詞'
    if core.startswith('P'): return '代名詞'
    if core.startswith('T'): return '小辞'
    if core.startswith('D'): return '副詞'
    return '機能語'

def decode(m):
    raw=(m or '').lstrip('H')
    parts=[p for p in raw.split('/') if p]
    lexical=[p for p in parts if not p.startswith('S')]
    core=lexical[-1] if lexical else (parts[-1] if parts else '')
    prefixes=lexical[:-1]
    labs=[]
    for p in prefixes:
        lab=segment_label(p)
        if lab and (not labs or labs[-1] != lab): labs.append(lab)
    corelab=lexical_label(core)
    labs.append(corelab)
    pos='＋'.join(labs)
    stem='—'
    if core.startswith('V'):
        stem=b.STEM.get(core[1:2],'—')
        infl=b.CONJ.get(core[2:3],'動詞形')+'（'+core+'）'
    elif core.startswith('Np'):
        infl='固有名詞（'+core+'）'
    elif core.startswith('Ng'):
        infl='民族名詞（'+core+'）'
    elif core.startswith('N'):
        infl='名詞形（'+core+'）'
    elif core.startswith('A'):
        infl='形容詞・数詞形（'+core+'）'
    elif core.startswith('R'):
        infl='前置詞（'+core+'）'
    elif core.startswith('C'):
        infl='接続詞（'+core+'）'
    elif core.startswith('P'):
        infl='代名詞（'+core+'）'
    elif core.startswith('T'):
        infl='小辞（'+core+'）'
    elif core.startswith('D'):
        infl='副詞（'+core+'）'
    else:
        infl=core or '—'
    return pos,stem,infl

out=pathlib.Path('013/html-fixed'); out.mkdir(parents=True,exist_ok=True)
for v in range(6,33):
    verse=b.root.find(f".//o:verse[@osisID='Gen.10.{v}']",b.NS)
    ws=verse.findall('o:w',b.NS)
    gloss=b.G[v]
    if len(ws)!=len(gloss):
        raise SystemExit(f'gloss mismatch 10:{v}: {len(ws)} != {len(gloss)}')
    gi=iter(gloss); pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            word=(child.text or '').replace('/','')
            gl=next(gi)
            le=b.lemma(child.attrib.get('lemma',''))
            po,st,inf=decode(child.attrib.get('morph',''))
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(le)}</span></b><span>品詞：{html.escape(po)}</span><span>語幹：{html.escape(st)}</span><span>活用：{html.escape(inf)}</span></span></span>')
        elif tag=='seg':
            t=child.attrib.get('type','')
            if t=='x-maqqef': pieces.append('<span class="pun">־</span>')
            elif t=='x-sof-pasuq': pieces.append('<span class="pun">׃</span>')
            elif t=='x-paseq': pieces.append('<span class="pun">׀</span>')
    doc='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+b.CSS+'<body><div class="row">'+''.join(pieces)+'</div>'+b.JS+'</body></html>'
    (out/f'Genesis-10-{v}-r3.html').write_text(doc,encoding='utf-8')
print('generated 27 corrected HTML files for Genesis 10:6-32')