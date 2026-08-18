from pathlib import Path
import ast, html, json, re, shutil, subprocess, xml.etree.ElementTree as ET

BASE=Path('.'); OUT=BASE/'017'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
for p in (HTML,AUDIO,SOURCE): p.mkdir(parents=True,exist_ok=True)
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
root=ET.parse(BASE/'Gen.xml').getroot()
REFS=[(13,v) for v in range(5,19)]

GLOSS={}
for source in ('build_013.py','build_014.py','build_015.py','build_016.py'):
    mod=ast.parse((BASE/source).read_text())
    for n in ast.walk(mod):
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GLOSS' for t in n.targets):
            try:GLOSS.update(ast.literal_eval(n.value))
            except Exception:pass
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and getattr(n.func.value,'id',None)=='GLOSS' and n.func.attr=='update':
            try:GLOSS.update(ast.literal_eval(n.args[0]))
            except Exception:pass
GLOSS.update({'5375':'上げる／担う','3162':'共に','7227':'多い','3201':'できる','7379':'争い','7473':'牧する者','6522':'ペリジ人','408':'～してはならない','4808':'争い','587':'私たち','518':'もし','8040':'左','3231':'右へ行く','3225':'右','8041':'左へ行く','5869':'目','3603':'低地／円形の地域','3383':'ヨルダン','4945':'潤された','7843':'滅ぼす','5467':'ソドム','6017':'ゴモラ','1588':'園','6820':'ツォアル','977':'選ぶ','167':'天幕を移す','7451':'悪い','2400':'罪深い','6828':'北','5769':'永遠','6083':'ちり','4487':'数える','6965':'立つ','753':'長さ','7341':'幅','4471':'マムレ','2275':'ヘブロン'})

J={(13,5):'アブラムと共に旅したロトにも、羊の群れ、牛の群れ、天幕があった。',
(13,6):'その地は、彼らが共に住むには支えきれなかった。彼らの財産が多く、共に住むことができなかったからである。',
(13,7):'アブラムの家畜の牧者とロトの家畜の牧者との間に争いが起こった。その時、カナン人とペリジ人がその地に住んでいた。',
(13,8):'アブラムはロトに言った。「私とあなた、私の牧者とあなたの牧者との間に、争いがあってはならない。私たちは兄弟なのだから。」',
(13,9):'「全地があなたの前にあるではないか。どうか私から離れてほしい。あなたが左へ行けば私は右へ、右へ行けば私は左へ行こう。」',
(13,10):'ロトは目を上げ、ヨルダンの低地全体を見た。それは主がソドムとゴモラを滅ぼされる前で、ツォアルまでどこも潤い、主の園のよう、エジプトの地のようであった。',
(13,11):'ロトは自分のためにヨルダンの低地全体を選び、東へ移った。こうして二人は互いに離れた。',
(13,12):'アブラムはカナンの地に住み、ロトは低地の町々に住んで、ソドムまで天幕を移した。',
(13,13):'ソドムの人々は主に対して非常に悪く、罪深かった。',
(13,14):'ロトがアブラムから離れた後、主はアブラムに言われた。「さあ、目を上げ、あなたのいる場所から北、南、東、西を見渡しなさい。」',
(13,15):'「あなたが見ているすべての地を、わたしはあなたとあなたの子孫に永遠に与える。」',
(13,16):'「わたしはあなたの子孫を地のちりのようにする。もし人が地のちりを数えられるなら、あなたの子孫も数えられる。」',
(13,17):'「立って、その地を縦と横に歩きなさい。わたしはそれをあなたに与えるからである。」',
(13,18):'アブラムは天幕を移し、ヘブロンにあるマムレの樫の木々のそばに来て住んだ。そして、そこに主のための祭壇を築いた。'}

LEMMA={}; lns={'x':'http://openscriptures.github.com/morphhb/namespace'}
for e in ET.parse(BASE/'HebrewStrong.xml').getroot().findall('x:entry',lns):
    w=e.find("x:w[@xml:lang='heb']",{'x':lns['x'],'xml':'http://www.w3.org/XML/1998/namespace'}) or e.find('x:w',lns)
    if w is not None and w.text: LEMMA[e.attrib['id']]=w.text
def strong_id(s):
    a=re.findall(r'\d+',s or ''); return a[-1] if a else ''
def hebrew_lemma(s):
    sid=strong_id(s)
    if not sid:return {'c':'וְ','b':'בְּ','l':'לְ','m':'מִן','k':'כְּ','d':'הַ'}.get((s or '').strip(),'מִלָּה')
    return LEMMA.get('H'+sid,'מִלָּה')
def morph_info(m):
    raw=(m or '').lstrip('H'); parts=[p for p in raw.split('/') if p]; names=[]
    for p in parts:
        if p=='C':names.append('接続詞')
        elif p=='R':names.append('前置詞')
        elif p=='Rd':names.extend(['前置詞','定冠詞'])
        elif p.startswith('R'):names.append('前置詞')
        elif p.startswith('Td'):names.append('定冠詞')
        elif p.startswith('To'):names.append('目的語標識')
        elif p.startswith('T'):names.append('小辞')
        elif p.startswith('Np'):names.append('固有名詞')
        elif p.startswith('Ng'):names.append('民族名詞')
        elif p.startswith('N'):names.append('名詞')
        elif p.startswith('V'):names.append('動詞')
        elif p.startswith('A'):names.append('形容詞・数詞')
        elif p.startswith('P'):names.append('代名詞')
        elif p.startswith('D'):names.append('副詞')
        elif p.startswith('Sp'):names.append('接尾代名詞')
        elif p=='Sd':names.append('方向接尾辞')
        elif p.startswith('S'):names.append('接尾要素')
        else:names.append('機能語')
    verb=next((p for p in parts if p.startswith('V')),None); stem='—'; infl=[]
    STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael','Q':'Pual'}
    FORM={'p':'完了形','q':'ワウ継続完了形','i':'未完了形','w':'ワウ継続形','h':'勧奨形','j':'願望形','v':'命令形','r':'能動分詞','s':'受動分詞','a':'不定詞絶対形','c':'不定詞連語形'}
    if verb:stem=STEM.get(verb[1:2],'—');infl.append(FORM.get(verb[2:3],'動詞形')+'（'+verb+'）')
    else:
        core=next((p for p in reversed(parts) if not p.startswith(('C','R','T','S'))),parts[-1] if parts else '')
        if core.startswith('Np'):infl.append('固有名詞形')
        elif core.startswith('Ng'):infl.append('民族名詞形（'+core+'）')
        elif core.startswith('N'):infl.append('名詞形（'+core+'）')
        elif core.startswith('A'):infl.append('形容詞・数詞形（'+core+'）')
        elif core:infl.append(core)
    suff=[p for p in parts if p.startswith('Sp')]
    if suff:infl.append('接尾代名詞 '+','.join(suff))
    return '＋'.join(names),stem,'・'.join(infl) or '—'
def gloss_for(w):
    raw=w.attrib.get('lemma',''); sid=strong_id(raw)
    if not sid:
        m=w.attrib.get('morph',''); who='あなた' if 'Sp2' in m else '私' if 'Sp1' in m else '彼ら' if 'Sp3mp' in m else '彼女' if 'Sp3fs' in m else '彼'
        return {'l':'〜に／'+who+'に','m':'〜から／'+who+'から','b':'〜で／'+who+'の中で'}.get(raw,who)
    if sid not in GLOSS:raise ValueError(f'unmapped gloss H{sid}: {w.text}')
    pref=[]
    for x in raw.split('/')[:-1]:
        x=x.strip()
        if x=='c':pref.append('そして')
        elif x=='b':pref.append('〜で')
        elif x=='l':pref.append('〜へ')
        elif x=='m':pref.append('〜から')
        elif x=='k':pref.append('〜するとき')
        elif x=='d':pref.append('その')
    return ' '.join(pref+[GLOSS[sid]])

CSS='''<style>html,body{margin:0;background:#fff}body{padding:20px 8px 52px;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Yu Gothic",sans-serif}.row{direction:rtl;display:flex;flex-wrap:wrap;gap:18px 13px;padding:0 8px;line-height:1.03;align-items:flex-start}.unit{position:relative;display:flex;flex-direction:column;align-items:center;min-width:34px;padding:1px 2px;outline:none}.hw{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px);direction:rtl}.gl{direction:ltr;font-size:12px;margin-top:5px;white-space:nowrap}.pun{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px)}.pop{display:none;position:fixed;z-index:50;background:white;color:#171717;border:1px solid #ddd;border-radius:10px;padding:9px 11px;box-shadow:0 4px 18px #0002;font-size:12px;line-height:1.5;direction:ltr;max-width:min(260px,86vw)}.pop b{display:block;font-size:1em}.pop .lemma{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:1.3em}.pop span{display:block}.pop b .lemma{display:inline}.unit:hover .pop,.unit:focus .pop{display:block}@media(max-width:600px){.hw,.pun{font-size:clamp(36px,11vw,44px)}.gl{font-size:12px}}</style>'''
JS='''<script>const units=[...document.querySelectorAll('.unit')];function hide(u){u.querySelector('.pop').style.display=''}function place(u){const p=u.querySelector('.pop');p.style.display='block';p.style.visibility='hidden';const r=u.getBoundingClientRect(),pr=p.getBoundingClientRect(),m=8;let x=r.left+r.width/2-pr.width/2,y=r.bottom+6;if(y+pr.height>innerHeight-m)y=r.top-pr.height-6;x=Math.max(m,Math.min(innerWidth-pr.width-m,x));y=Math.max(m,Math.min(innerHeight-pr.height-m,y));p.style.left=x+'px';p.style.top=y+'px';p.style.visibility='visible'}units.forEach(u=>{u.addEventListener('mouseenter',()=>place(u));u.addEventListener('mouseleave',()=>hide(u));u.addEventListener('focus',()=>place(u));u.addEventListener('blur',()=>hide(u));u.addEventListener('click',e=>{e.stopPropagation();units.forEach(x=>{if(x!==u)hide(x)});place(u)})});document.addEventListener('click',()=>units.forEach(hide));addEventListener('resize',()=>units.forEach(hide));</script>'''
def html_for(c,v):
    verse=root.find(f".//o:verse[@osisID='Gen.{c}.{v}']",NS); pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            if child.attrib.get('type')=='x-ketiv':
                continue
            word=(child.text or '').replace('/',''); lemma=hebrew_lemma(child.attrib.get('lemma','')); pos,stem,infl=morph_info(child.attrib.get('morph','')); gl=gloss_for(child)
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>')
        elif tag=='note' and child.attrib.get('type')=='variant':
            qw=child.find('.//o:rdg[@type="x-qere"]/o:w',NS)
            if qw is not None:
                word=(qw.text or '').replace('/',''); lemma=hebrew_lemma(qw.attrib.get('lemma',''));pos,stem,infl=morph_info(qw.attrib.get('morph',''))
                pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">彼の天幕</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>')
        elif tag=='seg':
            punct={'x-maqqef':'־','x-sof-pasuq':'׃','x-paseq':'׀'}.get(child.attrib.get('type',''))
            if punct:pieces.append(f'<span class="pun">{punct}</span>')
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+CSS+'<body><div class="row">'+''.join(pieces)+'</div>'+JS+'</body></html>'
def key(c,v):
    ve=root.find(f".//o:verse[@osisID='Gen.{c}.{v}']",NS);ws=[w for w in ve.findall('o:w',NS) if w.attrib.get('type')!='x-ketiv'];w=next((x for x in ws if any(p.startswith('V') for p in x.attrib.get('morph','').lstrip('H').split('/'))),ws[0]);pos,stem,infl=morph_info(w.attrib.get('morph',''));return (w.text or '').replace('/',''),hebrew_lemma(w.attrib.get('lemma','')),pos,stem,infl

THEME={(13,5):'ロトにも家畜と天幕が増え、共同生活の圧力を導入する',(13,6):'豊かさのため同じ土地に共住できない状況を説明する',(13,7):'牧者同士の争いと先住民の存在を並べる',(13,8):'アブラムが親族関係を理由に争いの停止を提案する',(13,9):'土地の選択権をロトに譲り、平和的分離を求める',(13,10):'ロトが潤ったヨルダン低地を見て魅力を評価する',(13,11):'ロトが低地を選び、二人が互いに離れる',(13,12):'アブラムはカナンに、ロトはソドム近くに住む',(13,13):'ソドムの人々の悪を短く先取りして警告する',(13,14):'ロトとの分離後、神が全方向を見渡すよう命じる',(13,15):'見える土地をアブラムと子孫へ永遠に与えると約束する',(13,16):'子孫を地のちりにたとえ、数えきれない広がりを示す',(13,17):'土地を縦横に歩くよう命じ、約束を身体的行為に結ぶ',(13,18):'マムレに住み、祭壇を築いてアリヤーを閉じる'}
RAB={(13,5):'ラシーはロトの富がアブラムとの同行によって増したと読みます。本文はまず、双方の家畜と天幕が共住問題の背景になったことを示します。',(13,6):'中世注解は「地が彼らを担えなかった」を、牧草と水の不足による具体的な収容力の問題として読みます。',(13,7):'ラシーは牧者の争いを放牧地の所有理解と結びつけます。カナン人とペリジ人の記載は、土地がまだアブラムの所有ではないことを強調します。',(13,8):'ラシーは「兄弟」を近親者という広い用法で説明します。血縁を争い回避の根拠にするアブラムの言葉が中心です。',(13,9):'ラシーは左右の選択を、ロトがどちらを選んでもアブラムが反対側へ行く譲歩として読みます。平和のため選択権を先に渡します。',(13,10):'中世注解は「主の園」「エジプトの地」を水の豊かさの比較と読みます。同時に、滅亡前という語り手の注意が見た目だけの判断へ警告を添えます。',(13,11):'ラシーは「自分のために選んだ」という語をロトの自己中心的選択として厳しく読みます。本文では選択と東行きが分離の決定となります。',(13,12):'中世注解は「ソドムまで」を、すぐ市内に定住したのでなく、段階的に天幕を近づけた表現として読みます。',(13,13):'ラシーは「悪い」を身体・財産に関する悪、「罪深い」を神への反逆として区別する伝承を紹介します。本文は主に対する深い悪を要約します。',(13,14):'ラシーは、ロトが離れた後に神の言葉が再び臨んだ点を強調します。全方向を見渡す命令が失ったもの以上の約束を示します。',(13,15):'中世注解は「永遠」を契約的な持続性として読みます。目の前の占有ではなく、アブラムと子孫への将来の約束です。',(13,16):'ラシーは地のちりを、数の多さだけでなく広く散らされても再び集められる民の像へ展開します。本文の直喩はまず不可算性を表します。',(13,17):'中世注解は土地を歩く行為を、占有のしるし、また約束の地を知る行為として読みます。法的象徴と実際の旅を区別します。',(13,18):'ラシーらはマムレをアブラムの同盟者と関連づけます。祭壇建設は、新しい居住地での礼拝による応答です。'}
PAT={(13,5):'教父的受容は富の増加が共同体の緊張を生む点を、所有と一致の倫理として読みました。富そのものを悪とせず、関係への影響を問います。',(13,6):'教父説教では、一つの土地に共住できない状況が、外的豊かさと内的一致の違いを考える素材となりました。原義は牧畜上の限界です。',(13,7):'初期キリスト教の倫理読解は牧者同士の争いを共同体指導者の対立への警告として受容しました。これは古代牧畜社会の争いに基づく適用です。',(13,8):'教父的受容はアブラムの仲裁を、平和を先に選ぶ徳の模範としました。弱さからの回避でなく、関係維持のための譲歩として読みます。',(13,9):'教父説教では、選択権を譲るアブラムが地上的利益より平和を重んじる姿として語られます。後の約束は報酬の機械的因果とは扱いません。',(13,10):'教父たちはロトの視線を、外見の豊かさに引かれる魂の危険として寓意化しました。寓意はヨルダン低地の実際の肥沃さを土台とします。',(13,11):'ロトの東行きは、教父的受容で楽園から東へ離れる創世記のモチーフと重ねられました。これは文学的連想で、本文の地理を置き換えません。',(13,12):'ソドムへ近づく天幕は、教父説教で悪に少しずつ接近する危険の像となりました。原義上はロトの居住選択の進行です。',(13,13):'教父文学はソドムを多様な悪徳の象徴として用いましたが、後代の倫理的類型を特定の現代集団への断罪へ短絡させません。',(13,14):'教父的受容は「目を上げよ」を、損失の後に神の約束へ視線を向け直す招きとして読みました。地理的展望が霊的適用の基礎です。',(13,15):'初期キリスト教は土地と子孫の約束を救済史的に広げて読みましたが、まずアブラム家への具体的約束という本文の地平を保ちます。',(13,16):'地のちりの比喩は教父文学で諸国民へ広がる信仰者の群れと結ばれました。これは後代の受容で、原義の子孫約束と区別されます。',(13,17):'教父説教では土地を歩く命令が、約束を観念だけでなく生活で受け取る信仰の実践として語られます。',(13,18):'祭壇は教父的受容で感謝と礼拝の像となります。移動の終点を所有の誇りではなく礼拝で結ぶ点が重視されます。'}
LIT={(13,5):'12章で得た富が13章の対立要因となり、祝福が新たな課題も生むことを示します。',(13,6):'「共に住む」が反復され、土地の不足より共同生活の不可能が焦点化されます。',(13,7):'牧者の争いと先住民の一文が、約束の地での所有権の複雑さを示します。',(13,8):'アブラムの直接話法が対立を停止し、「争い」と「兄弟」を対照させます。',(13,9):'全地を前に置く表現と左右の対句が、自由な選択と分離を簡潔に構成します。',(13,10):'見る動詞、潤いの描写、滅亡予告が重なり、魅力と危険の二重視点を作ります。',(13,11):'「選ぶ」「東へ旅する」「離れる」が連続し、ロトの決断を物語の転換点にします。',(13,12):'二人の居住地を並行して示し、カナンとソドム周辺の対照を準備します。',(13,13):'語り手の評価が物語を一時停止し、後のソドム物語を先取りします。',(13,14):'ロトが「目を上げた」10節に対し、神がアブラムに「目を上げよ」と命じ、二つの視線を対照させます。',(13,15):'「見る」から「与える」へ進み、選択による取得と約束による贈与を対照させます。',(13,16):'土地の約束に子孫の約束が加わり、空間と未来が結ばれます。',(13,17):'見る行為から歩く行為へ移り、約束された土地との関係を具体化します。',(13,18):'天幕・居住・祭壇という流れが、分離後のアブラムの新しい拠点を礼拝で確定します。'}
DEV={(13,5):'豊かさが増えても、関係を守る余地が自動的に増えるとは限りません。持ち物と共同生活の釣り合いを見直します。',(13,6):'同じ場所に留まることだけが一致ではありません。関係を壊さない距離の取り方を、誠実に選ぶこともできます。',(13,7):'身内の争いは周囲にも見られています。権利を主張する前に、争いが共同体へ与える影響を考えます。',(13,8):'アブラムは勝敗より兄弟関係を先に置きました。正しさを失わず、平和へ向かう言葉を選びます。',(13,9):'自分が先に選べる時こそ、相手へ譲る自由があります。恐れで握りしめず、神の備えを信頼します。',(13,10):'目に潤って見える選択にも、見えない危険があります。魅力だけでなく、その先にある関係と方向を見ます。',(13,11):'「自分のため」の選択が他者との距離を決めます。自分の利益だけで未来を狭めていないかを省みます。',(13,12):'悪へ向かう歩みは、しばしば一度の飛躍でなく少しずつ近づく形を取ります。日々の小さな方向を確かめます。',(13,13):'悪を語る時、他者を断罪する道具にせず、自分たちの不正と弱者への態度をまず問い直します。',(13,14):'何かを手放した後にこそ、新しい景色が見えることがあります。失った一点だけでなく、神が開く広がりへ目を上げます。',(13,15):'約束は今すぐすべてを所有する保証ではなく、今日を支える信頼の言葉です。焦らず受け取ります。',(13,16):'自分には数えきれない未来も、神には見えています。小さな始まりを見下さず、次の世代へ希望を渡します。',(13,17):'信じることは、与えられた場所を実際に歩くことでもあります。今日踏み出せる一歩を選びます。',(13,18):'新しい場所に着いたアブラムは、まず祭壇を築きました。成果を誇るより、感謝を中心に据えます。'}
def details(c,v):
    w,l,p,s,i=key(c,v); ref=(c,v); kq='狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'
    return [('本文の骨格',f'{c}:{v}は、{THEME[ref]}節です。前後の反復と場面転換の中で固有の役割を担います。'),('文法',f'主要語 {w}（レンマ {l}）は、品詞 {p}、語幹 {s}、活用 {i}。語順と反復が「{THEME[ref]}」という機能を支えます。'),('ケティーブ／ケレー・本文伝承',kq),('ラビ・中世',RAB[ref]),('教父文学',PAT[ref]),('文献層と物語',LIT[ref]),('デボーショナルな受けとめ',DEV[ref])]

for c,v in REFS:(HTML/f'017-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

# PocketTorah second-method boundary data, using only PocketTorah tokens and labels.
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS]; labels=[float(x) for x in (BASE/'lech-lecha-3.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels):raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'lech-lecha-3.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'lech-lecha-3.mp3'),'-af','silencedetect=noise=-36dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip(map(float,re.findall(r'silence_start: ([0-9.]+)',log)),map(float,re.findall(r'silence_end: ([0-9.]+)',log))))
idx=0;cuts=[0.0];methods=[]
for cnt in counts[:-1]:
    idx+=cnt;last,nxt=labels[idx-1],labels[idx];cand=[(a,b) for a,b in sil if a>last and a<=nxt+0.65 and b>=nxt-0.20]
    if cand:a,b=min(cand,key=lambda x:abs((x[0]+x[1])/2-nxt));cut=(a+b)/2;method=f'silence {a:.6f}-{b:.6f}'
    else:cut=nxt;method='PocketTorah next-token label'
    cuts.append(cut);methods.append(method)
cuts.append(duration)
target_wps=0.793064;original_wps=sum(counts)/duration;atempo=target_wps/original_wps
for src,dst in [('lech-lecha-3.mp3','Lech-Lecha-3-original.mp3'),('lech-lecha-3.txt','lech-lecha-3-labels.txt'),('PocketTorah-Genesis.json','PocketTorah-Genesis.json')]:shutil.copy2(BASE/src,SOURCE/dst)
(SOURCE/'PocketTorah-Lech-Lecha-3-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for n,(c,v) in enumerate(REFS):
    start,end=cuts[n],cuts[n+1];rows.append((c,v,start,end,counts[n],methods[n] if n<len(methods) else 'end of source'))
    if (c,v) not in ((13,13),(13,14),(13,15)):
        out=AUDIO/f'017-Genesis-{c}-{v}-study.mp3';cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'lech-lecha-3.mp3'),'-filter:a',f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}','-codec:a','libmp3lame','-q:a','5',str(out)]
        for attempt in range(3):
            subprocess.run(cmd,check=True)
            probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(out)],capture_output=True,text=True)
            if probe.returncode==0 and probe.stdout.strip() and float(probe.stdout.strip())>0.5:break
        else:raise RuntimeError(f'audio split failed after 3 attempts: {out}')
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-{c}-{v}\t{s:.6f}\t{e:.6f}\t{n}\t{m}\n' for c,v,s,e,n,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t3\nrange\tGenesis 13:5-13:18\nprimary_sheets\thttps://www.sefaria.org/sheets/445683\nprimary_coverage\tGenesis 13:13-15\nfallback_coverage\tGenesis 13:5-12,13:16-18\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-3.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-3.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')
DIRECT={(13,13):('445683','438816'),(13,14):('445683','438818'),(13,15):('445683','438817')}
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    if (c,v) in DIRECT:
        sh,mid=DIRECT[(c,v)];ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\thttps://images.shulcloud.com/14396/{mid}.mp3')
    else:ar.append(f'Genesis-{c}-{v}\tPocketTorah physical split\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-3.mp3\thttps://raw.githubusercontent.com/theologia165/torah-audio-temp/main/017/audio/017-Genesis-{c}-{v}-study.mp3')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')

intro='アブラムとロトは豊かになりましたが、増えた家畜のため同じ土地に住み続けられず、牧者たちの間に争いが起こります。アブラムは平和を守るため、先に土地を選ぶ権利をロトへ譲ります。見た目に潤ったソドム周辺を選ぶロトに対し、アブラムには神が全方向を見渡すよう促し、土地と数えきれない子孫を約束します。手放すことで失うように見えても、信頼の先に新しい広がりが開かれる物語です。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第3アリヤー**　創世記13:5–13:18（14節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記13:5–18に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。古代訳・写本間の差が論じられる場合も、K/Qとは区別します。
</callout>''']
for c,v in REFS:
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(c,v));parts.append(f'''---
### 創世記 {c}:{v}
{{{{AUDIO:Genesis-{c}-{v}}}}}
**私訳**：{J[(c,v)]}
**ヘブライ語**
{{{{EMBED:Genesis-{c}-{v}}}}}
**簡易な説明**：{key(c,v)[0]} はレンマ {key(c,v)[1]}、品詞 {key(c,v)[2]}、語幹 {key(c,v)[3]}、活用 {key(c,v)[4]}です。{THEME[(c,v)]}節です。
<details color="gray_bg">
<summary>詳しい解説</summary>
{det}
</details>''')
parts.append('''---
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 13](https://www.sefaria.org/Genesis.13)
- [PocketTorah Lech-Lecha-3 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 13](https://www.sefaria.org/Rashi_on_Genesis.13)
- [Bereshit Rabbah 40](https://www.sefaria.org/Bereshit_Rabbah.40)
- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'labels':len(labels),'tokens':sum(counts),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
