from pathlib import Path
import ast, html, json, re, shutil, subprocess, xml.etree.ElementTree as ET

BASE=Path('.')
OUT=BASE/'015'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
HTML.mkdir(parents=True,exist_ok=True); AUDIO.mkdir(parents=True,exist_ok=True); SOURCE.mkdir(parents=True,exist_ok=True)
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
root=ET.parse(BASE/'Gen.xml').getroot()

# Reuse the reviewed glosses from 013 and 014, then explicitly add every
# previously uncovered lexical item in Genesis 12:1-13. No generic production fallback exists.
GLOSS={}
for source in ('build_013.py','build_014.py'):
    mod=ast.parse((BASE/source).read_text())
    for n in mod.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GLOSS' for t in n.targets):
            try: GLOSS.update(ast.literal_eval(n.value))
            except Exception: pass
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and getattr(n.value.func.value,'id',None)=='GLOSS' and n.value.func.attr=='update':
            try: GLOSS.update(ast.literal_eval(n.value.args[0]))
            except Exception: pass
GLOSS.update({
'1004':'家','1431':'大きくする','1293':'祝福','7043':'軽んじる／呪う','1696':'語る','7399':'財産','7408':'獲得する','5315':'命／人','5674':'通り過ぎる','4725':'場所','7927':'シェケム','436':'樫の木','4176':'モレ','3669':'カナン人','227':'その時','2233':'子孫','5414':'与える','2063':'この','4196':'祭壇','6275':'移る','2022':'山','1008':'ベテル','5186':'張る','3220':'西／海','5857':'アイ','1980':'進む','5045':'ネゲブ','7458':'飢饉','4714':'エジプト','1481':'寄留する','3515':'重い／激しい','7126':'近づく','2009':'見よ','4994':'どうか','3303':'美しい','4758':'姿','859':'あなた','4713':'エジプト人','2026':'殺す','269':'姉妹','4616':'〜するために','3190':'よくなる','5668':'〜のために','1558':'〜ゆえに'
})

# Japanese private translations, one per verse.
J={
1:'主はアブラムに言われた。「あなたは、あなたの地、親族、父の家を離れ、わたしが示す地へ行きなさい。」',
2:'「わたしはあなたを大いなる国民とし、あなたを祝福し、あなたの名を大きくする。あなたは祝福となりなさい。」',
3:'「あなたを祝福する者を、わたしは祝福する。あなたを軽んじる者を、わたしは呪う。地のすべての氏族は、あなたによって祝福を受ける。」',
4:'アブラムは主が語られたとおりに出発し、ロトも彼と共に行った。アブラムがハランを出た時、七十五歳であった。',
5:'アブラムは妻サライ、甥ロト、彼らが得たすべての財産、ハランで加えた人々を連れ、カナンの地へ向けて出発した。そして彼らはカナンの地に入った。',
6:'アブラムはその地を通り、シェケムの場所、モレの樫の木まで来た。その時、カナン人がその地にいた。',
7:'主はアブラムに現れて言われた。「あなたの子孫に、この地を与える。」アブラムは、彼に現れた主のため、そこに祭壇を築いた。',
8:'彼はそこからベテルの東の山地へ移り、天幕を張った。西にベテル、東にアイがあった。彼はそこで主のために祭壇を築き、主の名を呼んだ。',
9:'アブラムは旅を続け、さらにネゲブへ向かった。',
10:'その地に飢饉が起こった。飢饉がその地で激しかったので、アブラムはエジプトに寄留するため下って行った。',
11:'彼がエジプトに入ろうと近づいた時、妻サライに言った。「見よ、あなたが姿の美しい女であることを、私は知っている。」',
12:'「エジプト人があなたを見ると、『これは彼の妻だ』と言い、私を殺して、あなたを生かしておくだろう。」',
13:'「どうか、私の妹だと言ってほしい。そうすれば、あなたのゆえに私に良いことがあり、あなたのおかげで私の命は生き延びるだろう。」'
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
        elif p=='Rd': names.extend(['前置詞','定冠詞'])
        elif p.startswith('R'): names.append('前置詞')
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
        elif p.startswith('Sp'): names.append('接尾代名詞')
        elif p=='Sd': names.append('方向接尾辞')
        elif p.startswith('S'): names.append('接尾要素')
        else: names.append('機能語')
    pos='＋'.join(names)
    verb=next((p for p in parts if p.startswith('V')),None)
    stem='—'; infl=[]
    STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael','o':'Polel','r':'Hithpolel'}
    FORM={'p':'完了形','q':'ワウ継続完了形','i':'未完了形','w':'ワウ継続形','h':'勧奨形','j':'願望形','v':'命令形','r':'能動分詞','s':'受動分詞','a':'不定詞絶対形','c':'不定詞連語形'}
    if verb:
        stem=STEM.get(verb[1:2],'—'); infl.append(FORM.get(verb[2:3],'動詞形')+'（'+verb+'）')
    else:
        core=next((p for p in reversed(parts) if not p.startswith(('C','R','T','S'))),parts[-1] if parts else '')
        if core.startswith('Np'): infl.append('固有名詞形')
        elif core.startswith('Ng'): infl.append('民族名詞形（'+core+'）')
        elif core.startswith('N'): infl.append('名詞形（'+core+'）')
        elif core.startswith('A'): infl.append('形容詞・数詞形（'+core+'）')
        elif core: infl.append(core)
    suff=[p for p in parts if p.startswith('Sp')]
    if suff: infl.append('接尾代名詞 '+','.join(suff))
    return pos,stem,'・'.join(infl) or '—'

def gloss_for(w):
    raw=w.attrib.get('lemma',''); sid=strong_id(raw)
    if not sid:
        morph=w.attrib.get('morph','')
        who=('あなた' if 'Sp2ms' in morph else 'あなた' if 'Sp2fs' in morph else
             '私' if 'Sp1cs' in morph else '彼ら' if 'Sp3mp' in morph else
             '私たち' if 'Sp1cp' in morph else '彼女' if 'Sp3fs' in morph else '彼')
        return {'l':'〜に／'+who+'に','m':'〜から／'+who+'から','b':'〜で／'+who+'の中で'}.get(raw,who)
    if sid not in GLOSS: raise ValueError(f'unmapped gloss H{sid}: {w.text}')
    pref=[]
    for first in raw.split('/')[:-1]:
        first=first.strip()
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
    verse=root.find(f".//o:verse[@osisID='Gen.12.{v}']",NS); pieces=[]
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
    ve=root.find(f".//o:verse[@osisID='Gen.12.{v}']",NS); ws=ve.findall('o:w',NS)
    w=next((x for x in ws if any(p.startswith('V') for p in x.attrib.get('morph','').lstrip('H').split('/'))),ws[0])
    pos,stem,infl=morph_info(w.attrib.get('morph',''))
    return (w.text or '').replace('/',''),hebrew_lemma(w.attrib.get('lemma','')),pos,stem,infl

THEME={1:'地・親族・父の家を離れ、神が示す地へ行く召命を告げる',2:'国民・祝福・名という約束を重ね、受け手自身を祝福の担い手とする',3:'祝福と呪いを対照させ、地の全氏族へ祝福が及ぶ目的を示す',4:'アブラムが命令どおり七十五歳でハランを出る応答を記す',5:'家族・財産・人々を伴う出発とカナン到着を二段階で語る',6:'シェケムとモレの樫の木に到着し、先住のカナン人を明記する',7:'子孫への土地の約束に対し、アブラムが祭壇を築いて応答する',8:'ベテルとアイの間で天幕と祭壇を設け、主の名を呼ぶ',9:'定住せず旅を続け、南のネゲブへ進む',10:'激しい飢饉によって約束の地からエジプトへ下る危機を導入する',11:'エジプト到着前、サライの美しさを理由にアブラムの恐れが言葉になる',12:'妻が見られた時の殺害と生存を予測し、危機の構図を示す',13:'サライに妹と名乗るよう求め、自分の安全を彼女の言葉に委ねる'}
TEXTNOTE={v:'狭義のケティーブ／ケレーは確認されません。MTの語形を本文とし、古代訳・写本上の差が論じられる場合もK/Qとは区別します。' for v in range(1,14)}

RABBI={
1:'ラシーは לֶךְ־לְךָ を「あなた自身のため、あなたの益のため」と読み、故郷からの離脱に約束された善を重ねます。文法上は命令形＋与格的代名詞という強調表現です。',
2:'ラシーは「名を大きくする」をアブラムの名が広く知られる約束として読みます。祝福を私的成功に閉じず、次節の諸氏族へ続く流れが重要です。',
3:'ラシーは「あなたによって祝福する」を、人々が「アブラムのようであれ」と祝う表現として説明します。祝福の媒介という本文の広がりと、後代の定型句の説明を区別します。',
4:'ラシーはアブラムの出発を、命令への即時の応答として読みます。ロトの同行は本人への直接命令とは別に記され、物語は同行者を後の葛藤へつなげます。',
5:'ラシーは「彼らがハランで作った人々」を、アブラムとサライが信仰へ導いた人々と読む伝承を紹介します。語の通常義「得る／作る」と受容史的解釈は区別します。',
6:'ラシーは「その時カナン人が地にいた」を、カナン人がセム系の支配地を征服しつつあったという歴史像に結びつけます。本文自体は先住者の存在を短く示します。',
7:'中世注解は「あなたの子孫に」という約束が、まだ子のないアブラムに与えられた点を強調します。祭壇は、出現と土地の約束への感謝の応答として読まれます。',
8:'ラシーはアブラムがベテル周辺で祭壇を築いたことを、後にアイで生じる出来事を見越した祈りと結びつけます。これは後代的受容で、節の明示内容は礼拝と旅です。',
9:'イブン・エズラらは「行きつつ旅する」という重ねた表現を継続的移動と読みます。ネゲブは方角であると同時に地域名として理解されます。',
10:'ラシーは約束の地で直ちに飢饉が起きたことを、アブラムの信頼が試される出来事として読みます。災害を個人の罪への直接的刑罰とは扱いません。',
11:'ラシーは「今、私は知った」を、旅の途中で改めてサライの美しさを認識した表現として説明します。後代の物語的説明と、危機を予測する会話の機能を分けます。',
12:'中世注解は、エジプト人が夫を殺して妻を奪うというアブラムの恐れを、旅人の無防備さの中で検討します。本文はその判断を称賛せず、次の行動の動機として提示します。',
13:'ラシーは「妹」という言い方を、親族関係を広く表す語法や後の20章との関係で説明します。ただし本節では、サライに危険を負わせる依頼であることを消しません。'}

PATRISTIC={
1:'オリゲネスの『創世記講話』は故郷・親族・父の家を離れる召命を、古い生き方からの霊的出発として受容しました。この寓意的適用は、アブラムの具体的移住という原義と区別されます。',
2:'教父的受容では、アブラムへの約束を救済史の新しい始まりとして読み、後の諸国民への祝福へ結びました。個人的繁栄だけでなく、他者へ流れる祝福として理解します。',
3:'アウグスティヌス『神の国』16巻はアブラムの約束を諸国民へ広がる祝福としてキリスト教的に受容します。この読解は創世記本文の家族・民族的地平を置き換えるものではありません。',
4:'教父説教ではアブラムの出発が信仰による従順の模範とされ、ヘブライ11章と結ばれました。後の新約的受容と、創世記が語る実際の旅を区別します。',
5:'初期キリスト教の読解は、アブラムと共に旅する家族と人々を信仰共同体の像として扱うことがあります。予型論を本文の社会的・家族的現実と混同しません。',
6:'教父的地理読解ではシェケムなどの場所が霊的旅程として寓意化されました。まず本文が、約束の地にすでに他者が住む緊張を明記することを確認します。',
7:'祭壇は教父文学で祈りや礼拝の型として受容されました。土地所有の即時実現ではなく、約束を聞いた旅人の応答として読む点が重要です。',
8:'主の名を呼ぶ行為は、教父説教で旅の只中の公的礼拝として語られます。天幕の仮住まいと祭壇の持続する関係が霊的受容を支えます。',
9:'絶えず進むアブラムは、教父的受容で信仰者の巡礼の像となりました。これはネゲブへ向かう地理的移動を土台にした倫理的適用です。',
10:'教父たちは飢饉下のエジプト行きを信仰の試練として読みましたが、飢饉を被災者個人の罪に直結させる読みは本文にありません。',
11:'教父的倫理読解では、アブラムの信仰と恐れが同じ人物に同居することが論じられます。英雄を無傷に描かず、危機の会話を物語の緊張として受け取ります。',
12:'アウグスティヌス『神の国』16巻は、この妻妹物語を弁護的に扱います。後代の倫理的調和と、サライが負う危険を描く本文の緊張は区別して読む必要があります。',
13:'アウグスティヌスは「妹」を親族関係として虚偽ではないと説明しました。受容史上の弁護を紹介しつつ、現代の読者はサライの同意や安全が語られない点にも注意します。'}

LITERARY={
1:'12:1は11章の系譜からアブラム物語へ転じる大きな節目です。資料批評では非祭司的語りに置かれることが多いものの、最終形では創世記1–11章の全人類的課題への新しい応答を開始します。',
2:'12:2は命令に続く約束群の前半です。「大いなる」を反復し、バベルで人々が自ら得ようとした名と、神が与える名を最終形の対照として読めます。',
3:'12:3は約束群の頂点で、アブラムの選びを地の全氏族へ開きます。選びと普遍的祝福を対立させず、一つの家族を通して諸家族へ向かう構造です。',
4:'12:4は神の発話から人間の応答へ切り替わります。祭司的年代情報と結びつけられる年齢表示も、最終形では出発の具体性を支えます。',
5:'12:5は11:31の未完のカナン行きを実現させます。「出た／来た」の対応によって、目的地への到着を簡潔に強調します。',
6:'12:6は移動の道筋と先住者を同時に置き、土地の約束が空白地への進入ではないことを示します。地名列は後のイスラエル物語とも響き合います。',
7:'12:7は最初の神顕現、子孫への土地の約束、祭壇建設を一つに結びます。約束と礼拝が対応し、所有はまだ実現していません。',
8:'12:8は地理表現を重ね、天幕・祭壇・主の名という巡礼生活を描きます。定住より移動が前景にあり、礼拝地点が物語地図を作ります。',
9:'12:9の短い反復表現は旅の継続を要約し、次の飢饉とエジプト行きへ場面を移します。物語の速度が一度上がります。',
10:'12:10は約束直後に危機を置く反転点です。12:1–9の召命と礼拝から、12:10–20の妻妹物語へ移り、信頼と生存の緊張を試します。',
11:'12:11は地の飢饉という外的危機を、夫婦間の会話と恐れという内的危機へ移します。見る／美しいという語が次節の予測を準備します。',
12:'12:12は「私を殺す／あなたを生かす」の対照で、アブラムの恐れを鋭く表現します。資料層の分類だけでなく、誰が危険を負うかという物語倫理が重要です。',
13:'12:13は依頼、目的、期待される結果を連ねます。次節以降の展開を動かす発話であり、祝福を受けた者の脆さを隠さず描きます。'}

DEVOTIONAL={
1:'神の導きは、行き先の全貌より先に一歩を求めることがあります。慣れた場所を軽んじず、それでも今手放すべきものと、信頼して進む方向を静かに見分けます。',
2:'祝福は自分だけの所有物ではなく、誰かを生かすために託されます。今日受け取る力や名誉が、周囲へ平安を運ぶものとなるよう願います。',
3:'選ばれることは他者を排除する特権ではなく、広い祝福に仕える責任です。身近な関係から、誰かが祝福を味わえる言葉と行動を選びます。',
4:'アブラムは完全な確信の物語ではなく、語られた言葉に応じて歩き始めます。年齢や遅さを理由にせず、今日できる小さな従順を大切にします。',
5:'召しへの応答には家族や生活の現実が伴います。自分だけの決断として急がず、共に旅する人の声と負担を丁寧に扱います。',
6:'約束の地にも、すでに暮らす人々がいました。神の導きを自分だけの所有権とせず、先にいる隣人の尊厳を認めて歩みます。',
7:'約束がまだ見えない時、アブラムは祭壇を築きました。結果を先取りするのでなく、与えられた言葉を覚えるしるしを日々の中に持ちます。',
8:'天幕は移り、祭壇は旅のたびに築かれます。環境が変わっても、神を呼び求める中心を失わない一日を始めます。',
9:'短い一節にも、止まらず進む旅があります。大きな成果が見えない日も、正しい方向への小さな歩みを軽んじません。',
10:'信仰の旅にも飢饉は起こります。苦難を失敗や罰と決めつけず、命を守る現実的判断と神への信頼を共に求めます。',
11:'恐れは時に、愛する人を守るより自分を守る計画へ向かわせます。恐れを隠さず語りつつ、その負担を誰かに押しつけていないか省みます。',
12:'危機の予測が現実的でも、他者の命を手段にしてよいことにはなりません。弱い立場の人が負う危険を見落とさない判断を求めます。',
13:'聖書は信仰者の弱さを美化せず語ります。自分の安全のために他者へ沈黙や偽装を求めていないかを問い、誠実さと保護の道を選びます。'}

def details(v):
    word,lemma,pos,stem,infl=key(v)
    return [
      ('本文の骨格',f'12:{v}は、{THEME[v]}節です。召命・約束・旅・危機というアリヤー全体の流れの中で固有の役割を担います。'),
      ('文法',f'主要語 {word}（レンマ {lemma}）は、品詞 {pos}、語幹 {stem}、活用 {infl}。本節の語順と反復は「{THEME[v]}」という役割を支えます。'),
      ('ケティーブ／ケレー・本文伝承',TEXTNOTE[v]),('ラビ・中世',RABBI[v]),('教父文学',PATRISTIC[v]),('文献層と物語',LITERARY[v]),('デボーショナルな受けとめ',DEVOTIONAL[v])]

# Generate 13 HTML artifacts.
for v in range(1,14):
    (HTML/f'015-Genesis-12-{v}-r1.html').write_text(html_for(v),encoding='utf-8')

# PocketTorah boundary calculation uses PocketTorah tokens only.
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))
ptv=pt['Tanach']['tanach']['book']['c'][11]['v'][:13]
counts=[len(x['w']) for x in ptv]
labels=[float(x) for x in (BASE/'lech-lecha-1.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels): raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'lech-lecha-1.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'lech-lecha-1.mp3'),'-af','silencedetect=noise=-36dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
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
shutil.copy2(BASE/'lech-lecha-1.mp3',SOURCE/'Lech-Lecha-1-original.mp3')
shutil.copy2(BASE/'lech-lecha-1.txt',SOURCE/'lech-lecha-1-labels.txt')
shutil.copy2(BASE/'PocketTorah-Genesis.json',SOURCE/'PocketTorah-Genesis.json')
decoded=SOURCE/'Lech-Lecha-1-decoded.pcm'
subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'lech-lecha-1.mp3'),'-f','s16le','-acodec','pcm_s16le',str(decoded)],check=True)
rows=[]
for v in range(1,14):
    start,end=cuts[v-1],cuts[v]
    out=AUDIO/f'015-Genesis-12-{v}-study.mp3'
    af=f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}'
    cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-f','s16le','-ar','44100','-ac','2','-i',str(decoded),'-filter:a',af,'-codec:a','libmp3lame','-q:a','5',str(out)]
    for attempt in range(3):
        subprocess.run(cmd,check=True)
        probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(out)],capture_output=True,text=True)
        if probe.returncode==0 and probe.stdout.strip() and float(probe.stdout.strip())>0.5: break
    else: raise RuntimeError(f'audio split failed after 3 attempts: {out}')
    rows.append((v,start,end,counts[v-1],methods[v-1] if v<13 else 'end of source'))
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-12-{v}\t{s:.6f}\t{e:.6f}\t{c}\t{m}\n' for v,s,e,c,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-12-{v}\t{counts[v-1]}\n' for v in range(1,14)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t1\nrange\tGenesis 12:1-12:13\nsource_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-1.mp3\nsource_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-1.txt\nsource_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')

intro='アブラムは、行き先の全貌を知らないまま、故郷と親族を離れて神が示す地へ向かいます。約束された祝福は彼一人の成功ではなく、地のすべての家族へ届くためのものでした。カナンに着いた彼は祭壇を築き、なお旅を続けます。しかし飢饉でエジプトへ下ると、恐れから妻サライに「妹」と名乗るよう求めます。信頼して踏み出す勇気と、危機の中で現れる弱さの両方を隠さない、アブラムの旅の始まりです。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第1アリヤー**　創世記12:1–12:13（13節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記12:1–12:13に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。古代訳・写本間の語順や表現の差が論じられる場合も、ケティーブ／ケレーとは区別します。
</callout>''']
for v in range(1,14):
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(v))
    parts.append(f'''---
### 創世記 12:{v}
{{{{AUDIO:Genesis-12-{v}}}}}
**私訳**：{J[v]}
**ヘブライ語**
{{{{EMBED:Genesis-12-{v}}}}}
**簡易な説明**：{key(v)[0]} はレンマ {key(v)[1]}、品詞 {key(v)[2]}、語幹 {key(v)[3]}、活用 {key(v)[4]}です。{THEME[v]}節です。
<details color="gray_bg">
<summary>詳しい解説</summary>
{det}
</details>''')
parts.append('''---
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持して使用しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 12](https://www.sefaria.org/Genesis.12)
- [PocketTorah Lech-Lecha-1 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 12](https://www.sefaria.org/Rashi_on_Genesis.12)
- [Bereshit Rabbah 39](https://www.sefaria.org/Bereshit_Rabbah.39)
- [Origen, Homilies on Genesis](https://archive.org/details/homiliesongenes00orig)
- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':13,'pockettorah_tokens':sum(counts),'labels':len(labels),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
