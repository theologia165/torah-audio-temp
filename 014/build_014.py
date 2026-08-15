from pathlib import Path
import ast, html, json, re, shutil, subprocess, xml.etree.ElementTree as ET

BASE=Path('.')
OUT=BASE/'014'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
HTML.mkdir(parents=True,exist_ok=True); AUDIO.mkdir(parents=True,exist_ok=True); SOURCE.mkdir(parents=True,exist_ok=True)
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
root=ET.parse(BASE/'Gen.xml').getroot()

# Reuse only the reviewed ordinary-word glosses from 013, then explicitly add every
# previously uncovered lexical item in Genesis 11. No generic production fallback exists.
mod=ast.parse((BASE/'build_013.py').read_text())
GLOSS={}
for n in mod.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GLOSS' for t in n.targets):
        GLOSS=ast.literal_eval(n.value)
GLOSS.update({
'8193':'言語','1697':'言葉','5265':'旅立つ','4672':'見つける','1237':'平地','8152':'シンアル','8033':'そこ','413':'〜へ','7453':'仲間','3051':'さあ','3835':'れんがを作る','3843':'れんが','8313':'焼く','8316':'焼き上げること','68':'石','2564':'瀝青','2563':'しっくい','4026':'塔','7218':'頂','8064':'天','6435':'〜しないように','6327':'散る／散らす','5921':'〜の上に','3381':'下る','120':'人間','2005':'見よ','5971':'民','2490':'始める','6258':'今','1219':'妨げられる','2161':'企てる','1101':'混乱させる','8085':'聞き分ける','2308':'やめる','894':'バベル','3588':'なぜなら','775':'アルパクシャド','2568':'五','1323':'娘たち','7970':'三十','7974':'シェラ','702':'四','5677':'エベル','6389':'ペレグ','7466':'レウ','8286':'セルグ','7651':'七','5152':'ナホル','6242':'二十','8646':'テラ','6240':'十','7657':'七十','87':'アブラム','2039':'ハラン','3876':'ロト','4138':'生まれた地','218':'ウル','3778':'カルデア人','802':'妻','8297':'サライ','4435':'ミルカ','3252':'イスカ','6135':'不妊','369':'ない','2056':'子','3618':'嫁','854':'彼らと共に','935':'来る','2771':'ハラン','3667':'カナン'
})

# Japanese private translations, one per verse.
J={
1:'全地は一つの言語、一つの言葉を用いていた。',
2:'人々は東の方から移動し、シンアルの地に平地を見つけ、そこに住んだ。',
3:'彼らは互いに言った。「さあ、れんがを作り、十分に焼こう。」れんがが石の代わりとなり、瀝青がしっくいの代わりとなった。',
4:'彼らは言った。「さあ、町と、頂が天に届く塔を建て、自分たちの名を上げよう。全地に散らされないためだ。」',
5:'主は、人間の子らが建てていた町と塔を見るために下って来られた。',
6:'主は言われた。「見よ、彼らは一つの民で、皆が一つの言語を持つ。これは彼らの始めたことにすぎない。今や、彼らが企てることは何も妨げられないだろう。」',
7:'「さあ、われわれは下って行き、そこで彼らの言語を混乱させ、互いの言葉を聞き分けられないようにしよう。」',
8:'こうして主は彼らをそこから全地へ散らされ、彼らは町を建てることをやめた。',
9:'それゆえ、その町の名はバベルと呼ばれた。そこで主が全地の言語を混乱させ、そこから彼らを全地へ散らされたからである。',
10:'これはセムの系譜である。セムは百歳で、洪水の二年後にアルパクシャドを生んだ。',
11:'セムはアルパクシャドを生んだ後、五百年生き、息子たちと娘たちをもうけた。',
12:'アルパクシャドは三十五年生き、シェラを生んだ。',
13:'アルパクシャドはシェラを生んだ後、四百三年生き、息子たちと娘たちをもうけた。',
14:'シェラは三十年生き、エベルを生んだ。',
15:'シェラはエベルを生んだ後、四百三年生き、息子たちと娘たちをもうけた。',
16:'エベルは三十四年生き、ペレグを生んだ。',
17:'エベルはペレグを生んだ後、四百三十年生き、息子たちと娘たちをもうけた。',
18:'ペレグは三十年生き、レウを生んだ。',
19:'ペレグはレウを生んだ後、二百九年生き、息子たちと娘たちをもうけた。',
20:'レウは三十二年生き、セルグを生んだ。',
21:'レウはセルグを生んだ後、二百七年生き、息子たちと娘たちをもうけた。',
22:'セルグは三十年生き、ナホルを生んだ。',
23:'セルグはナホルを生んだ後、二百年生き、息子たちと娘たちをもうけた。',
24:'ナホルは二十九年生き、テラを生んだ。',
25:'ナホルはテラを生んだ後、百十九年生き、息子たちと娘たちをもうけた。',
26:'テラは七十年生き、アブラム、ナホル、ハランを生んだ。',
27:'これはテラの系譜である。テラはアブラム、ナホル、ハランを生み、ハランはロトを生んだ。',
28:'ハランは、生まれ故郷カルデア人のウルで、父テラの生きている間に死んだ。',
29:'アブラムとナホルは妻を迎えた。アブラムの妻の名はサライ、ナホルの妻の名はミルカで、ハランの娘であった。ハランはミルカとイスカの父である。',
30:'サライは不妊で、子がいなかった。',
31:'テラは息子アブラム、孫でハランの息子ロト、息子アブラムの妻で嫁のサライを連れ、カルデア人のウルを出てカナンの地へ向かった。彼らはハランまで来て、そこに住んだ。',
32:'テラの生涯は二百五年であった。テラはハランで死んだ。'
}

LEMMA={}
lns={'x':'http://openscriptures.github.com/morphhb/namespace'}
for e in ET.parse(BASE/'HebrewStrong.xml').getroot().findall('x:entry',lns):
    w=e.find("x:w[@xml:lang='heb']",{'x':lns['x'],'xml':'http://www.w3.org/XML/1998/namespace'})
    if w is None: w=e.find('x:w',lns)
    if w is not None and w.text: LEMMA[e.attrib['id']]=w.text

def strong_id(s):
    nums=re.findall(r'\d+',s or '')
    return nums[-1] if nums else ''
def hebrew_lemma(s):
    sid=strong_id(s)
    if not sid: return {'c':'וְ','b':'בְּ','l':'לְ','m':'מִן','k':'כְּ','d':'הַ'}.get((s or '').strip(),'מִלָּה')
    return LEMMA.get('H'+sid,'מִלָּה')

def morph_info(m):
    raw=(m or '')
    if raw.startswith('H'): raw=raw[1:]
    parts=[p for p in raw.split('/') if p]
    names=[]
    for p in parts:
        if p=='C': names.append('接続詞')
        elif p=='R': names.append('前置詞')
        elif p.startswith('Td'): names.append('定冠詞')
        elif p.startswith('To'): names.append('目的語標識')
        elif p.startswith('T'): names.append('小辞')
        elif p.startswith('Np'): names.append('固有名詞')
        elif p.startswith('Ng'): names.append('民族名詞')
        elif p.startswith('N'): names.append('名詞')
        elif p.startswith('V'): names.append('動詞')
        elif p.startswith('A'): names.append('形容詞・数詞')
        elif p.startswith('P'): names.append('代名詞')
        elif p.startswith('D'): names.append('副詞')
        elif p.startswith('S'): names.append('接尾代名詞')
        else: names.append('機能語')
    pos='＋'.join(names)
    verb=next((p for p in parts if p.startswith('V')),None)
    stem='—'; infl=[]
    STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael','o':'Polel','r':'Hithpolel'}
    FORM={'p':'完了形','q':'完了形','i':'未完了形','w':'ワウ継続形','j':'指示・命令形','v':'分詞','r':'分詞','s':'分詞','a':'不定詞','c':'不定詞連語形'}
    if verb:
        stem=STEM.get(verb[1:2],'—'); infl.append(FORM.get(verb[2:3],'動詞形')+'（'+verb+'）')
    else:
        core=next((p for p in reversed(parts) if not p.startswith(('C','R','T','S'))),parts[-1] if parts else '')
        if core.startswith('Np'): infl.append('固有名詞形')
        elif core.startswith('Ng'): infl.append('民族名詞形（'+core+'）')
        elif core.startswith('N'): infl.append('名詞形（'+core+'）')
        elif core.startswith('A'): infl.append('形容詞・数詞形（'+core+'）')
        elif core: infl.append(core)
    suff=[p for p in parts if p.startswith('S')]
    if suff: infl.append('接尾代名詞 '+','.join(suff))
    return pos,stem,'・'.join(infl) or '—'

def gloss_for(w):
    raw=w.attrib.get('lemma',''); sid=strong_id(raw)
    if not sid:
        morph=w.attrib.get('morph','')
        who='彼ら' if 'Sp3mp' in morph else ('私たち' if 'Sp1cp' in morph else ('彼女' if 'Sp3fs' in morph else '彼'))
        return {'l':'〜に／'+who+'に','m':'〜から／'+who+'から','b':'〜で／'+who+'の中で'}.get(raw,who)
    if sid not in GLOSS: raise ValueError(f'unmapped gloss H{sid}: {w.text}')
    pref=[]; first=raw.split('/')[0].strip()
    if first=='c': pref.append('そして')
    elif first=='b': pref.append('〜で')
    elif first=='l': pref.append('〜へ')
    elif first=='m': pref.append('〜から')
    elif first=='k': pref.append('〜のように')
    elif first=='d': pref.append('その')
    return ' '.join(pref+[GLOSS[sid]])

CSS='''<style>html,body{margin:0;background:#fff}body{padding:20px 8px 52px;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Yu Gothic",sans-serif}.row{direction:rtl;display:flex;flex-wrap:wrap;gap:18px 13px;padding:0 8px;line-height:1.03;align-items:flex-start}.unit{position:relative;display:flex;flex-direction:column;align-items:center;min-width:34px;padding:1px 2px;outline:none}.hw{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px);direction:rtl}.gl{direction:ltr;font-size:12px;margin-top:5px;white-space:nowrap}.pun{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px)}.pop{display:none;position:fixed;z-index:50;background:white;color:#171717;border:1px solid #ddd;border-radius:10px;padding:9px 11px;box-shadow:0 4px 18px #0002;font-size:12px;line-height:1.5;direction:ltr;max-width:min(260px,86vw)}.pop b{display:block;font-size:1em}.pop .lemma{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:1.3em}.pop span{display:block}.pop b .lemma{display:inline}.unit:hover .pop,.unit:focus .pop{display:block}@media(max-width:600px){.hw,.pun{font-size:clamp(36px,11vw,44px)}.gl{font-size:12px}}</style>'''
JS='''<script>const units=[...document.querySelectorAll('.unit')];function hide(u){u.querySelector('.pop').style.display=''}function place(u){const p=u.querySelector('.pop');p.style.display='block';p.style.visibility='hidden';const r=u.getBoundingClientRect(),pr=p.getBoundingClientRect(),m=8;let x=r.left+r.width/2-pr.width/2;let y=r.bottom+6;if(y+pr.height>innerHeight-m)y=r.top-pr.height-6;x=Math.max(m,Math.min(innerWidth-pr.width-m,x));y=Math.max(m,Math.min(innerHeight-pr.height-m,y));p.style.left=x+'px';p.style.top=y+'px';p.style.visibility='visible'}units.forEach(u=>{u.addEventListener('mouseenter',()=>place(u));u.addEventListener('mouseleave',()=>hide(u));u.addEventListener('focus',()=>place(u));u.addEventListener('blur',()=>hide(u));u.addEventListener('click',e=>{e.stopPropagation();units.forEach(x=>{if(x!==u)hide(x)});place(u)})});document.addEventListener('click',()=>units.forEach(hide));addEventListener('resize',()=>units.forEach(hide));</script>'''

def html_for(v):
    verse=root.find(f".//o:verse[@osisID='Gen.11.{v}']",NS); pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            word=(child.text or '').replace('/',''); lemma=hebrew_lemma(child.attrib.get('lemma',''))
            pos,stem,infl=morph_info(child.attrib.get('morph','')); gl=gloss_for(child)
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>')
        elif tag=='seg':
            ty=child.attrib.get('type',''); punct={'x-maqqef':'־','x-sof-pasuq':'׃','x-paseq':'׀'}.get(ty)
            if punct: pieces.append(f'<span class="pun">{punct}</span>')
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+CSS+'<body><div class="row">'+''.join(pieces)+'</div>'+JS+'</body></html>'

def key(v):
    ve=root.find(f".//o:verse[@osisID='Gen.11.{v}']",NS); ws=ve.findall('o:w',NS)
    w=next((x for x in ws if any(p.startswith('V') for p in x.attrib.get('morph','').lstrip('H').split('/'))),ws[0])
    pos,stem,infl=morph_info(w.attrib.get('morph',''))
    return (w.text or '').replace('/',''),hebrew_lemma(w.attrib.get('lemma','')),pos,stem,infl

THEME={
1:'全地の言語的一致を物語の出発点として置く',2:'人々の移動とシンアル定住を示す',3:'石の乏しい平地でれんがと瀝青を技術化する',4:'都市・塔・名・離散回避という共同企図を明示する',5:'天に届くと称する建築を主が「下って」見る逆説を置く',6:'一つの民と一つの言語が持つ力を神の評価として語る',7:'神的複数表現と、言語を混乱させる決定を記す',8:'言語混乱の結果として離散と建設中止を語る',9:'バベルの名を語呂合わせで説明し、物語を閉じる',10:'塔の物語からセムの系譜へ転換し、洪水後二年を起点にする',11:'セムの残りの生涯と次世代の広がりをまとめる',12:'アルパクシャドからシェラへの父系継承を記す',13:'アルパクシャドの生涯後半と子女をまとめる',14:'シェラからエベルへの継承を記す',15:'シェラの生涯後半と子女をまとめる',16:'エベルからペレグへの継承を記す',17:'エベルの長い生涯後半と子女をまとめる',18:'ペレグからレウへの継承を記す',19:'ペレグの生涯後半と子女をまとめる',20:'レウからセルグへの継承を記す',21:'レウの生涯後半と子女をまとめる',22:'セルグからナホルへの継承を記す',23:'セルグの生涯後半と子女をまとめる',24:'ナホルからテラへの継承を記す',25:'ナホルの生涯後半と子女をまとめる',26:'テラの三人の息子を提示してアブラム物語を準備する',27:'テラの系譜を再開し、ハランとロトを導入する',28:'ハランの早い死と故郷ウルを結びつける',29:'アブラムとナホルの婚姻関係を整理する',30:'サライの不妊を簡潔に告げ、後の約束物語の緊張を作る',31:'テラ一家のウル出発、カナン志向、ハラン定住を一文に収める',32:'テラの生涯を閉じ、アブラムへの焦点移動を完成する'}
TEXTNOTE={v:'狭義のケティーブ／ケレーは確認されません。MTの語形を本文とし、古代訳との差が論じられる場合もK/Qとは区別します。' for v in range(1,33)}
TEXTNOTE[10]='狭義のケティーブ／ケレーはありません。七十人訳とルカ3章の系譜にはカイナンを挟む伝承がありますが、これは系譜本文の異読であってK/Qではありません。'
TEXTNOTE[12]=TEXTNOTE[10]
TEXTNOTE[13]=TEXTNOTE[10]
TEXTNOTE[32]='狭義のケティーブ／ケレーはありません。MTはテラの寿命を二百五年とし、サマリア五書の百四十五年とは異なります。これは年代本文の異読で、K/Qではありません。'

def rabbi(v):
    sp={1:'ラシーは「一つの言葉」を、単なる共通語以上に共同の企てとして読みます。本文の言語的一致と、後代が補う反逆の内容を区別します。',2:'ラシーは מִקֶּדֶם を神から遠ざかる移動として受容しますが、文法上は「東から／東方へ」の方向解釈に幅があります。',3:'中世注解は、平地に石がないため人工れんがを用いたという地理的合理性に注目します。技術そのものより、その用い方が物語の焦点です。',4:'創世記ラッバ38章などは塔を偶像礼拝的反逆として展開します。原文が明記するのは、名を上げ、離散を避けようとする企てです。',5:'ラシーは神が「下る」描写から、裁定の前に事実を確かめる模範を読み取ります。これは擬人的表現の倫理的受容です。',6:'ラビ的読解は一致そのものを善とせず、目的を問います。一つの民・一つの言語という賜物が自己高揚へ向かう逆説を読みます。',7:'「われわれは下ろう」という複数形は、神の評議や謙遜の教訓として読まれてきました。文法上の複数表現と神学的展開を区別します。',8:'中世注解は、計画された都市集中に対する散布を、創世記9章の「地に満ちよ」との関係で読みます。',9:'בָּבֶל と בָּלַל の語呂合わせは、厳密な語源説明より物語的命名です。ラシーも混乱と離散の因果を重ねて読みます。',28:'イブン・エズラなどは「カルデア人のウル」の位置と、アブラムの出発地を地理的に検討します。同定には古代地理上の議論が残ります。',29:'ラシーはイスカをサライと結びつける伝承を紹介しますが、本文は二つの名を別々に記します。伝承上の同定と明示本文を区別します。',30:'中世注解は「不妊」と「子がない」の重複を強調と読み、続く神の約束の前提として受け取ります。',31:'ラシーは年代計算から、テラ存命中のアブラム出発が父への不敬と誤解されないよう物語順序を説明します。',32:'ラシーはテラの死をアブラム出発より先に記す物語的配慮を論じます。年代順と語りの順序を同一視しない読みです。'}
    if v in sp:return sp[v]
    if 10<=v<=27:return f'中世の注解者は11:{v}の年齢と父子関係を前後の系譜と照合し、洪水からアブラムまでの年代を計算します。数値を霊意だけへ解消せず、系譜の連続性を重んじます。'
    return f'ユダヤ教の受容では11:{v}をバベル物語の因果の一部として読み、共同性と権力、言語と離散の関係を問います。後代の物語的補足は原文の明示事項と区別します。'

def patristic(v):
    if v<=9:return f'アウグスティヌス『神の国』16巻などは11:{v}を、人間の高慢が言語分裂を招く物語として受容し、使徒言行録2章の多言語による一致と対照しました。この予型論は創世記の歴史的叙述とは区別されます。'
    if v<=25:return f'教父的救済史では11:{v}の系譜がルカ3章の系譜と結ばれ、諸国民の物語からアブラム、さらにキリストへ至る連続性として読まれました。数値差の問題と神学的受容は分けます。'
    return f'教父文学では11:{v}がアブラム召命への序章として読まれ、地上の家系と神の約束の歴史が交差する箇所とされました。後の召命解釈を本節の直接的意味へ逆投影しません。'

def literary(v):
    if v<=9:return f'11:{v}は11:1–9の統一と離散の物語に属します。資料批評では非祭司的語りとされることが多い一方、最終形では10章の諸国民表と12章の召命を結ぶ編集上の蝶番です。'
    if v<=26:return f'11:{v}は定型句を重ねるセム系系譜の一部で、祭司的年代体系と結びつけられます。最終形では民族全体から一つの家系へ焦点を絞り、12章を準備します。'
    return f'11:{v}は定型的系譜から家族物語へ移る終結部です。資料層を論じる際も、名前・移住・死・不妊という物語情報がアブラム物語へどう接続するかを重視します。'

def devotional(v):
    ds={1:'同じ言葉を持つことだけでは、共同体の善は保証されません。朝の歩みで、私たちの一致が誰かを支配する力でなく、互いを生かす目的へ向いているかを省みます。',2:'定住できる平地は安心を与えますが、安心が閉鎖性へ変わることもあります。居場所を感謝しつつ、神と隣人への開かれを失わないよう祈ります。',3:'技術と工夫は賜物です。れんがを作る力を自己顕示に使うのか、命を支えるために使うのか、私たちの道具の目的を問い直します。',4:'名を残したい願いと、散らされる不安が大事業を動かします。恐れに駆られた自己保存ではなく、神から与えられた名と使命に安らぎます。',5:'神が下って見られるという描写は、人の誇る高さを相対化します。判断を急がず、まず現実をよく見る神の忍耐にも倣います。',6:'協力できる力は大切ですが、力の大きさだけで計画の正しさは決まりません。何が可能かと同時に、何が隣人を生かすかを問います。',7:'言葉が通じない痛みを、相手の欠点だけに帰さず、自分の語り方を見直す機会とします。理解のために下る姿勢を求めます。',8:'中断は必ずしも失敗ではありません。自己中心的な計画を手放し、より広い世界へ送り出される転機となることがあります。',9:'混乱の記憶さえ、後に新しい出会いの地図になります。違う言葉を持つ人を恐れず、神が多様性の中で与える関係を探します。',30:'サライの痛みを、本人の罪や信仰不足へ短絡してはなりません。欠けを抱える人の尊厳を守り、まだ見えない約束を急がず共に待ちます。',31:'目標へ向かう旅が途中で止まることがあります。ハランでの停滞も無意味と決めつけず、次の召しに備える時間として受け止めます。',32:'一つの世代の終わりは、神の物語の終わりではありません。受け継いだものを感謝し、次の世代に託すべき使命を静かに見定めます。'}
    if v in ds:return ds[v]
    if 10<=v<=29:return f'11:{v}の短い系譜にも、名を持つ一人の生涯と次世代への受け渡しがあります。成果の大きさだけでなく、与えられた時を忠実につなぐ歩みを尊びます。'
    return f'11:{v}は、人の企てが崩れても神の物語が次へ進むことを示します。混乱の中でも他者の言葉を聞き直し、新しい一歩を選びます。'

def details(v):
    word,lemma,pos,stem,infl=key(v)
    return [
      ('本文の骨格',f'11:{v}は、{THEME[v]}節です。前後とのつながりの中で、諸国民からアブラムの家系へ焦点が移る流れを担います。'),
      ('文法',f'主要語 {word}（レンマ {lemma}）は、品詞 {pos}、語幹 {stem}、活用 {infl}。本節の語順と反復は「{THEME[v]}」という役割を支えます。'),
      ('ケティーブ／ケレー・本文伝承',TEXTNOTE[v]),('ラビ・中世',rabbi(v)),('教父文学',patristic(v)),('文献層と物語',literary(v)),('デボーショナルな受けとめ',devotional(v))]

# Generate 32 HTML artifacts.
for v in range(1,33):
    (HTML/f'014-Genesis-11-{v}-r1.html').write_text(html_for(v),encoding='utf-8')

# PocketTorah boundary calculation uses PocketTorah tokens only.
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))
ptv=pt['Tanach']['tanach']['book']['c'][10]['v'][:32]
counts=[len(x['w']) for x in ptv]
labels=[float(x) for x in (BASE/'Noach-7.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels): raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'Noach-7.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'Noach-7.mp3'),'-af','silencedetect=noise=-36dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
ss=list(map(float,re.findall(r'silence_start: ([0-9.]+)',log))); ee=list(map(float,re.findall(r'silence_end: ([0-9.]+)',log))); sil=list(zip(ss,ee))
idx=0; cuts=[0.0]; methods=[]
for i,c in enumerate(counts[:-1],1):
    idx+=c; last=labels[idx-1]; nxt=labels[idx]
    cand=[(a,b) for a,b in sil if a>last and a<=nxt+0.65 and b>=nxt-0.20]
    if cand:
        a,b=min(cand,key=lambda x:abs((x[0]+x[1])/2-nxt)); cut=(a+b)/2; method=f'silence {a:.6f}-{b:.6f}'
    else: cut=nxt; method='PocketTorah next-token label'
    cuts.append(cut); methods.append(method)
cuts.append(duration)
target_wps=0.793064; original_wps=sum(counts)/duration; atempo=target_wps/original_wps
shutil.copy2(BASE/'Noach-7.mp3',SOURCE/'Noach-7-original.mp3')
shutil.copy2(BASE/'Noach-7.txt',SOURCE/'Noach-7-labels.txt')
shutil.copy2(BASE/'PocketTorah-Genesis.json',SOURCE/'PocketTorah-Genesis.json')
decoded=SOURCE/'Noach-7-decoded.pcm'
subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'Noach-7.mp3'),'-f','s16le','-acodec','pcm_s16le',str(decoded)],check=True)
rows=[]
for v in range(1,33):
    start,end=cuts[v-1],cuts[v]
    out=AUDIO/f'014-Genesis-11-{v}-study.mp3'
    af=f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}'
    cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-f','s16le','-ar','44100','-ac','2','-i',str(decoded),'-filter:a',af,'-codec:a','libmp3lame','-q:a','5',str(out)]
    for attempt in range(3):
        subprocess.run(cmd,check=True)
        probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(out)],capture_output=True,text=True)
        if probe.returncode==0 and probe.stdout.strip() and float(probe.stdout.strip())>0.5: break
    else: raise RuntimeError(f'audio split failed after 3 attempts: {out}')
    rows.append((v,start,end,counts[v-1],methods[v-1] if v<32 else 'end of source'))
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-11-{v}\t{s:.6f}\t{e:.6f}\t{c}\t{m}\n' for v,s,e,c,m in rows),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tNoach\naliyah\t7\nrange\tGenesis 11:1-11:32\nsource_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Noach-7.mp3\nsource_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/Noach-7.txt\nsource_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')

intro='人々は一つの言葉と高度な技術を手にしながら、神から与えられた広がりよりも、自分たちの名と安全を守る塔を選びます。バベルで言葉が乱され、計画は止まりますが、物語はそこで終わりません。セムからテラ、アブラムへと名が静かに受け渡され、神の祝福は新しい旅へ向かいます。大きな企てと小さな系譜の対照を、語形とテアミームから味わい、力よりも使命に結ばれる共同体を考えましょう。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**ノア｜第7アリヤー**　創世記11:1–11:32（32節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記11:1–11:32に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。11:10–13のカイナンを含む系譜伝承や、11:32のテラの寿命に関するサマリア五書との差は、古代訳・写本間の本文異読として区別します。
</callout>''']
for v in range(1,33):
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(v))
    parts.append(f'''---
### 創世記 11:{v}
{{{{AUDIO:Genesis-11-{v}}}}}
**私訳**：{J[v]}
**ヘブライ語**
{{{{EMBED:Genesis-11-{v}}}}}
**簡易な説明**：{key(v)[0]} はレンマ {key(v)[1]}、品詞 {key(v)[2]}、語幹 {key(v)[3]}、活用 {key(v)[4]}です。{THEME[v]}節です。
<details color="gray_bg">
<summary>詳しい解説</summary>
{det}
</details>''')
parts.append('''---
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持して使用しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 11](https://www.sefaria.org/Genesis.11)
- [PocketTorah Noach-7 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 11](https://www.sefaria.org/Rashi_on_Genesis.11)
- [Genesis Rabbah 38](https://www.sefaria.org/Bereshit_Rabbah.38)
- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':32,'pockettorah_tokens':sum(counts),'labels':len(labels),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
