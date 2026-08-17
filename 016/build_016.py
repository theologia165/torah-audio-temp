from pathlib import Path
import ast, html, json, re, shutil, subprocess, xml.etree.ElementTree as ET

BASE=Path('.'); OUT=BASE/'016'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
for p in (HTML,AUDIO,SOURCE): p.mkdir(parents=True,exist_ok=True)
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
root=ET.parse(BASE/'Gen.xml').getroot()
REFS=[(12,v) for v in range(14,21)]+[(13,v) for v in range(1,5)]

GLOSS={}
for source in ('build_013.py','build_014.py','build_015.py'):
    mod=ast.parse((BASE/source).read_text())
    for n in ast.walk(mod):
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GLOSS' for t in n.targets):
            try:GLOSS.update(ast.literal_eval(n.value))
            except Exception:pass
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and getattr(n.func.value,'id',None)=='GLOSS' and n.func.attr=='update':
            try:GLOSS.update(ast.literal_eval(n.args[0]))
            except Exception:pass
GLOSS.update({'3966':'非常に','8269':'高官たち','6547':'ファラオ','1984':'ほめる','6629':'羊','1241':'牛','2543':'ろば','8198':'女奴隷','860':'雌ろば','1581':'らくだ','5060':'打つ','5061':'災厄','4100':'なぜ／何','6680':'命じる','7971':'送り出す','5927':'上る','5973':'〜と共に','3513':'富む／重い','4735':'家畜','3701':'銀','2091':'金','4550':'旅程','8462':'初め','7223':'最初'})

J={(12,14):'アブラムがエジプトに入ると、エジプト人たちは、その女が非常に美しいのを見た。',
(12,15):'ファラオの高官たちも彼女を見て、ファラオの前で彼女をほめた。こうして、その女はファラオの宮廷へ連れて行かれた。',
(12,16):'ファラオは彼女のゆえにアブラムを厚遇した。アブラムには羊、牛、雄ろば、男奴隷、女奴隷、雌ろば、らくだが与えられた。',
(12,17):'しかし主は、アブラムの妻サライのことで、ファラオとその家を大きな災厄で打たれた。',
(12,18):'ファラオはアブラムを呼び寄せて言った。「あなたは私に何ということをしたのか。なぜ彼女があなたの妻だと知らせなかったのか。」',
(12,19):'「なぜ『私の妹です』と言ったのか。それで私は彼女を妻にしようとした。さあ、あなたの妻を連れて行け。」',
(12,20):'ファラオは彼について部下たちに命じ、彼とその妻、そして彼のすべての持ち物を送り出させた。',
(13,1):'アブラムは妻とすべての持ち物、そしてロトを伴い、エジプトからネゲブへ上った。',
(13,2):'アブラムは家畜、銀、金において非常に富んでいた。',
(13,3):'彼はネゲブからベテルまで旅程をたどり、初めに天幕のあった場所、ベテルとアイの間まで戻った。',
(13,4):'そこは、彼が最初に築いた祭壇の場所であった。アブラムはそこで主の名を呼んだ。'}

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

THEME={(12,14):'予測どおりエジプト人がサライの美しさに目を留める',(12,15):'高官の称賛から王宮への連行へ事態が進む',(12,16):'サライを通してアブラムが財産を得る不均衡を列挙する',(12,17):'沈黙していた神がサライのために介入する',(12,18):'ファラオがアブラムを呼び、隠された婚姻関係を問いただす',(12,19):'妹という説明の結果を示し、妻を返して退去を命じる',(12,20):'王命により家族と全財産が国境へ送り出される',(13,1):'一行がエジプトからネゲブへ戻る',(13,2):'アブラムの富を家畜・銀・金で要約する',(13,3):'旅程を逆にたどり、最初の天幕の場所へ帰る',(13,4):'最初の祭壇で再び主の名を呼ぶ'}
RAB={(12,14):'ラシーは「エジプト人が見た」を、隠していたサライが露見した場面として物語化します。本文の原義は、美しさが危機を現実化したことです。',(12,15):'中世注解は、高官たちの称賛が私的な視線を王権の行為へ変えた点に注意します。サライ本人の言葉が記されないことも重要です。',(12,16):'ラシーは後の13:2の富と結び、贈与の結果を読みます。財産の増加を単純な祝福とせず、サライの危険との緊張を保ちます。',(12,17):'ラシーは災厄がサライの言葉に応じて下ったという伝承を紹介します。これはサライの主体性を補う受容で、本文は主の介入を簡潔に述べます。',(12,18):'ラシーや中世注解はファラオの問いを、アブラムへの非難として読みます。異邦の王が真相を問いただす逆転が際立ちます。',(12,19):'中世注解は20章の親族説明も参照しますが、本節ではファラオが「妹」という発言の実際の危険を指摘します。',(12,20):'ラシーは護送を、危害を受けず退去させる命令と読みます。物語はアブラムの弁明より、王命による解決を前面に出します。',(13,1):'中世注解は「上る」を、低地エジプトからカナン方面への地理的移動として読みます。ロトの同行も改めて確認されます。',(13,2):'ラシーは כָּבֵד の「重い」を富の大きさとして理解します。豊かさは次の土地争いを準備する物語要素でもあります。',(13,3):'ラシーは「旅程ごとに」を、往路で泊まった場所を復路にもたどったこと、また宿代を返したこととして読む伝承を紹介します。',(13,4):'中世注解は祭壇への帰還を、旅の原点で礼拝を回復する行為として読みます。土地所有の完成ではなく、再び呼び求める姿です。'}
PAT={(12,14):'教父的受容はこの物語を信仰者の弱さの告白として読みました。後代の弁護より先に、サライが危険にさらされた原義を確認します。',(12,15):'教父説教では王宮が世俗的権力や誘惑の像として読まれることがあります。寓意は、連れて行かれる女性の具体的危険と区別されます。',(12,16):'初期キリスト教の倫理読解は、得られた富とその代価の緊張を扱いました。繁栄を神の承認と自動的に同一視しません。',(12,17):'アウグスティヌスは『神の国』16巻で妻妹物語を救済史の中に置きます。災厄は個々の病を罪の直接的刑罰とする一般則ではありません。',(12,18):'教父的受容では、異邦の王が族長を戒める場面が神の摂理の意外な手段として読まれました。本文上の倫理的逆転を保ちます。',(12,19):'アウグスティヌスは「妹」を親族語として弁護しましたが、受容史上の調和と、サライが負わされた危険は区別して読む必要があります。',(12,20):'キリスト教的受容はエジプト脱出との類似を予型的に読みました。これは後代の読解で、創世記ではまず一夫婦の危機からの退去です。',(13,1):'教父たちはエジプトからの上りを、試練から礼拝へ戻る霊的旅として受け取りました。地理的帰還を土台にした倫理的適用です。',(13,2):'教父的倫理では富そのものより、その用い方と次に生じる関係の緊張が問われます。物質的豊かさを霊的成熟と同一視しません。',(13,3):'オリゲネス的受容では、以前の旅路をたどることが回心と原点回帰の像となります。これは実際の地理的復路に基づく寓意です。',(13,4):'祭壇と主の名は、教父説教で祈りの回復として受容されました。失敗後にも礼拝へ戻れるという牧会的読みが生まれます。'}
LIT={(12,14):'12:11–13の予測が「見る」という語で現実になり、妻妹物語の緊張が加速します。',(12,15):'「見る・称賛する・連れて行く」の連鎖が、個人の美を宮廷の所有へ変える権力構造を描きます。',(12,16):'財産目録は13:2へ橋を架ける一方、サライの危険とアブラムの利益を並べ、物語倫理の不均衡を可視化します。',(12,17):'神の介入が初めて明示され、サライを危機から救い出します。災厄と王家という組合せは後の出エジプト物語を想起させます。',(12,18):'ファラオの三つの問いがアブラムの計画を反転させます。祝福の担い手が異邦の王から倫理的に問われる構図です。',(12,19):'発言の結果、意図、返還命令が短く並び、サライの身分を「妻」へ回復します。',(12,20):'「送り出す」は妻妹場面を閉じ、13:1の「上る」へ接続します。エジプト往復が一つの小さな下降・上昇物語となります。',(13,1):'人物と所有物の列挙は12:20を反復し、危機を経た一行の帰還を確認します。',(13,2):'短い要約が次のロトとの牧草地争いを準備します。富は祝福であると同時に物語上の新しい圧力です。',(13,3):'地名と「初めに」が12:8を呼び戻し、物語を失敗前の礼拝地点へ環状に戻します。',(13,4):'祭壇・主の名という12:8の語句が反復され、アリヤーは礼拝の回復で閉じます。'}
DEV={(12,14):'恐れから立てた計画が、弱い立場の人をさらに危険にすることがあります。誰が代価を負うかを見直します。',(12,15):'人を称賛の対象から所有の対象へ変える視線に抗い、一人ひとりの意思と尊厳を守ります。',(12,16):'利益が得られても、その背後で誰かが傷ついていないかを問い、繁栄だけで正しさを測りません。',(12,17):'語られない人の苦しみも神の前に見過ごされません。災害や病を個人の罪への直接的罰と決めつけず、守りと回復を求めます。',(12,18):'信仰者が外部の人から正しく問われることもあります。防御より先に、傷つけた現実へ耳を傾けます。',(12,19):'都合のよい説明が他者を危険にしたなら、返還と退去だけでなく、真実な悔い改めを求めます。',(12,20):'失敗の場から送り出されることも、やり直しへの入口になりえます。持ち物より、守られた命を大切にします。',(13,1):'遠回りや失敗の後にも、帰る道は残されています。共に歩く人を忘れず、原点へ向かいます。',(13,2):'豊かさは安心だけでなく責任も増やします。持つものが関係を圧迫しないよう、分かち合いを考えます。',(13,3):'回復は新しい場所へ急ぐことではなく、以前の道を丁寧にたどり直すことから始まる場合があります。',(13,4):'失敗を消せなくても、再び神の名を呼ぶことはできます。今日、祈りの原点へ静かに戻ります。'}
def details(c,v):
    w,l,p,s,i=key(c,v); ref=(c,v); kq='狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'
    if ref==(13,3):kq='狭義のK/Qがあります。ケティーブは אהל/ה（子音 אהל־ה）、ケレーは אָֽהֳל/וֹ֙（「彼の天幕」）です。表示本文は朗読形のケレーを示し、一般の写本差とは区別します。'
    return [('本文の骨格',f'{c}:{v}は、{THEME[ref]}節です。前後の反復と場面転換の中で固有の役割を担います。'),('文法',f'主要語 {w}（レンマ {l}）は、品詞 {p}、語幹 {s}、活用 {i}。語順と反復が「{THEME[ref]}」という機能を支えます。'),('ケティーブ／ケレー・本文伝承',kq),('ラビ・中世',RAB[ref]),('教父文学',PAT[ref]),('文献層と物語',LIT[ref]),('デボーショナルな受けとめ',DEV[ref])]

for c,v in REFS:(HTML/f'016-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

# PocketTorah second-method boundary data, using only PocketTorah tokens and labels.
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS]; labels=[float(x) for x in (BASE/'lech-lecha-2.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels):raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'lech-lecha-2.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'lech-lecha-2.mp3'),'-af','silencedetect=noise=-36dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip(map(float,re.findall(r'silence_start: ([0-9.]+)',log)),map(float,re.findall(r'silence_end: ([0-9.]+)',log))))
idx=0;cuts=[0.0];methods=[]
for cnt in counts[:-1]:
    idx+=cnt;last,nxt=labels[idx-1],labels[idx];cand=[(a,b) for a,b in sil if a>last and a<=nxt+0.65 and b>=nxt-0.20]
    if cand:a,b=min(cand,key=lambda x:abs((x[0]+x[1])/2-nxt));cut=(a+b)/2;method=f'silence {a:.6f}-{b:.6f}'
    else:cut=nxt;method='PocketTorah next-token label'
    cuts.append(cut);methods.append(method)
cuts.append(duration)
target_wps=0.793064;original_wps=sum(counts)/duration;atempo=target_wps/original_wps
for src,dst in [('lech-lecha-2.mp3','Lech-Lecha-2-original.mp3'),('lech-lecha-2.txt','lech-lecha-2-labels.txt'),('PocketTorah-Genesis.json','PocketTorah-Genesis.json')]:shutil.copy2(BASE/src,SOURCE/dst)
(SOURCE/'PocketTorah-Lech-Lecha-2-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for n,(c,v) in enumerate(REFS):
    start,end=cuts[n],cuts[n+1];rows.append((c,v,start,end,counts[n],methods[n] if n<len(methods) else 'end of source'))
    if (c,v) in ((12,19),(12,20)):
        out=AUDIO/f'016-Genesis-{c}-{v}-study.mp3';cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'lech-lecha-2.mp3'),'-filter:a',f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}','-codec:a','libmp3lame','-q:a','5',str(out)]
        subprocess.run(cmd,check=True)
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-{c}-{v}\t{s:.6f}\t{e:.6f}\t{n}\t{m}\n' for c,v,s,e,n,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t2\nrange\tGenesis 12:14-13:4\nprimary_sheets\thttps://www.sefaria.org/sheets/441357 ; https://www.sefaria.org/sheets/443968 ; https://www.sefaria.org/sheets/684292\nprimary_coverage\tGenesis 12:14-18,13:1-4\nfallback_coverage\tGenesis 12:19-20\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-2.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-2.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')
DIRECT={(12,14):('441357','438797'),(12,15):('443968','438799'),(12,16):('443968','438798'),(12,17):('443968','438800'),(12,18):('443968','438802'),(13,1):('684292','438805'),(13,2):('684292','438804'),(13,3):('684292','438806'),(13,4):('684292','438807')}
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    if (c,v) in DIRECT:
        sh,mid=DIRECT[(c,v)];ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\thttps://images.shulcloud.com/14396/{mid}.mp3')
    else:ar.append(f'Genesis-{c}-{v}\tPocketTorah physical split\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-2.mp3\thttps://raw.githubusercontent.com/theologia165/torah-audio-temp/main/016/audio/016-Genesis-{c}-{v}-study.mp3')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')

intro='サライがエジプトの王宮に連れて行かれると、アブラムの恐れから始まった計画は思わぬ危機を招きます。神はサライを守り、ファラオは真相を知って二人を国から送り出します。豊かな財産を携えてカナンへ戻ったアブラムは、旅の出発点だったベテル近くの祭壇へ帰り、再び主の名を呼びます。人の弱さが引き起こした混乱の中でも、声を奪われたサライは見捨てられません。失敗が消されないまま、それでも守られ、原点へ戻される物語です。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第2アリヤー**　創世記12:14–13:4（11節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記13:3に狭義のK/Qがあります。ケティーブは אהל/ה（子音 אהל־ה）、ケレーは אָֽהֳל/וֹ֙（「彼の天幕」）です。ほかの写本・古代訳の差とは区別します。
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
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持し、創世記13:3は朗読形のケレーを表示しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 12](https://www.sefaria.org/Genesis.12)
- [Sefaria Genesis 13](https://www.sefaria.org/Genesis.13)
- [PocketTorah Lech-Lecha-2 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 12](https://www.sefaria.org/Rashi_on_Genesis.12)
- [Rashi on Genesis 13](https://www.sefaria.org/Rashi_on_Genesis.13)
- [Bereshit Rabbah 40](https://www.sefaria.org/Bereshit_Rabbah.40)
- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'labels':len(labels),'tokens':sum(counts),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
