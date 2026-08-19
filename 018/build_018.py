from pathlib import Path
import ast, html, json, re, shutil, subprocess, xml.etree.ElementTree as ET

BASE=Path('.')
# Reuse only the proven parsing/UI helpers from 017; stop before any 017 output is written.
src=(BASE/'build_017.py').read_text()
prefix=src.split("for c,v in REFS:(HTML/f'017-Genesis-{c}-{v}-r1.html')",1)[0]
exec(compile(prefix,'build_017.py','exec'),globals())

OUT=BASE/'018'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
for p in (HTML,AUDIO,SOURCE): p.mkdir(parents=True,exist_ok=True)
REFS=[(14,v) for v in range(1,21)]

GLOSS.update({
'569':'アムラフェル','746':'アルヨク','495':'エラサル','3540':'ケドルラオメル','5867':'エラム','8413':'ティドアル','4421':'戦い',
'1298':'ベラ','1306':'ビルシャ','8134':'シンアブ','126':'アデマ','8038':'シェムエベル','6636':'ツェボイム','1106':'ベラ',
'2266':'連合する','6010':'谷','7708':'シディム','4417':'塩','5647':'仕える','4775':'反逆する','5221':'打つ','7497':'レファイム',
'6255':'アシュテロト・カルナイム','2104':'ズジム','1990':'ハム','368':'エミム','7740':'シャウェ','7156':'キルヤタイム',
'2752':'ホリ人','8165':'セイル','364':'エル／パラン','4057':'荒野','7725':'戻る／取り戻す','5880':'エン・ミシュパト',
'6946':'カデシュ','7704':'野','6003':'アマレク人','567':'アモリ人','2688':'ハツェツォン・タマル','6186':'戦列を整える',
'875':'穴／井戸','5127':'逃げる','5307':'落ちる','7604':'残った者','400':'食糧','6412':'逃れた者','5680':'ヘブライ人',
'812':'エシュコル','6063':'アネル','1992':'彼ら','1167':'所有者／同盟者','1285':'契約','7617':'捕らえられる','7324':'動員する',
'2593':'訓練された者','3211':'家に生まれた者','8083':'八','7291':'追う','1835':'ダン','2505':'分ける','3915':'夜',
'2327':'ホバ','1834':'ダマスコ','7125':'迎える','4442':'メルキ・ツェデク／正義','8004':'サレム','3899':'パン','3548':'祭司',
'410':'神','5945':'いと高き方','7069':'造り主／所有者','4042':'引き渡す','6862':'敵','3027':'手','4643':'十分の一'
})

J={
(14,1):'シンアルの王アムラフェル、エラサルの王アルヨク、エラムの王ケドルラオメル、ゴイムの王ティドアルの時代に、',
(14,2):'彼らは、ソドムの王ベラ、ゴモラの王ビルシャ、アデマの王シンアブ、ツェボイムの王シェムエベル、そしてベラ、すなわちツォアルの王と戦った。',
(14,3):'これらの者は皆、シディムの谷、すなわち塩の海に連合した。',
(14,4):'十二年、彼らはケドルラオメルに仕えたが、十三年目に反逆した。',
(14,5):'十四年目にケドルラオメルと彼に従う王たちが来て、アシュテロト・カルナイムでレファイムを、ハムでズジムを、シャウェ・キルヤタイムでエミムを打った。',
(14,6):'またセイルの山地でホリ人を打ち、荒野のそばのエル・パランまで追った。',
(14,7):'彼らは引き返してエン・ミシュパト、すなわちカデシュへ来て、アマレク人の全領域と、ハツェツォン・タマルに住むアモリ人をも打った。',
(14,8):'そこでソドムの王、ゴモラの王、アデマの王、ツェボイムの王、ベラ、すなわちツォアルの王が出陣し、シディムの谷で彼らに対して戦列を整えた。',
(14,9):'すなわち、エラムの王ケドルラオメル、ゴイムの王ティドアル、シンアルの王アムラフェル、エラサルの王アルヨクに対してであり、四人の王が五人と戦った。',
(14,10):'シディムの谷には瀝青の穴が幾つもあり、ソドムとゴモラの王たちは逃げてそこに落ち、残った者たちは山へ逃げた。',
(14,11):'彼らはソドムとゴモラのすべての財産と、すべての食糧を奪って去った。',
(14,12):'また、ソドムに住んでいたアブラムの兄弟の子ロトと、その財産を奪って去った。',
(14,13):'一人の逃れた者が来て、ヘブライ人アブラムに告げた。彼はアモリ人マムレの樫の木々のそばに住んでいた。マムレはエシュコルとアネルの兄弟で、彼らはアブラムの盟約者であった。',
(14,14):'アブラムは親族が捕らえられたと聞き、家に生まれた訓練された者三百十八人を動員して、ダンまで追跡した。',
(14,15):'彼と僕たちは夜に部隊を分けて彼らを打ち、ダマスコの北にあるホバまで追った。',
(14,16):'彼はすべての財産を取り戻し、親族ロトとその財産、女たちと人々をも取り戻した。',
(14,17):'彼がケドルラオメルとその同盟の王たちを打って帰ると、ソドムの王はシャウェの谷、すなわち王の谷へ彼を迎えに出た。',
(14,18):'サレムの王メルキ・ツェデクはパンとぶどう酒を携えて来た。彼はいと高き神の祭司であった。',
(14,19):'彼はアブラムを祝福して言った。「天と地の造り主、いと高き神によって、アブラムは祝福されよ。」',
(14,20):'「あなたの敵をあなたの手に引き渡された、いと高き神はほめたたえられよ。」アブラムは彼にすべての十分の一を与えた。'
}

THEME={
1:'東方の四王を列挙し、国際的な戦争の舞台を開く',2:'東方の四王に対する低地の五王を紹介する',3:'五王がシディムの谷に集結したことを示す',4:'十二年の服従と十三年目の反逆を時間軸で要約する',
5:'十四年目の遠征と三つの民への勝利を連続して描く',6:'遠征がセイルから荒野の境まで及んだことを示す',7:'軍勢が転進し南部の諸地域を打ったと伝える',8:'低地の五王が出陣して戦列を整える',
9:'四王対五王という戦いの構図を総括する',10:'瀝青の穴と敗走によって五王側の崩壊を描く',11:'勝者が都市の財産と食糧を奪う',12:'ロトの連行によって国際戦争をアブラムの物語へ接続する',
13:'逃亡者の報告とアブラムの地域同盟を紹介する',14:'アブラムが家の者を動員しダンまで追う',15:'夜襲と分隊行動によって敵軍を破る',16:'財産だけでなくロトと人々を救い戻す',
17:'帰還したアブラムをソドム王が迎える',18:'王であり祭司であるメルキ・ツェデクがパンとぶどう酒を携える',19:'メルキ・ツェデクが神を天と地の造り主と呼びアブラムを祝福する',20:'勝利を神の働きとしてたたえ、アブラムが十分の一を渡す'
}
RAB={
1:'中世注解は王名と地名を古代の政治地理として扱い、アブラムの家族物語が諸国の争いへ巻き込まれる導入と読みます。',2:'ラシーらは五王の名を列挙する本文に注目しますが、名前の語呂による人物評価は説話的受容であり、本文の歴史叙述とは区別されます。',3:'中世注解は「塩の海」を後代の地理的同定と理解し、語り手が読者の現在地から古い地名を説明すると読みます。',4:'ラシーは十三年目の反逆と十四年目の遠征という年代順を厳密に読み、支配関係の継続を確認します。',
5:'ラシーはレファイム等の敗北を、ケドルラオメル軍の強さを先に示し、後のアブラムの勝利を際立たせる叙述と読みます。',6:'中世注解はセイルとエル・パランを遠征経路の境界として説明し、軍事行動の広がりを地理に即して読みます。',7:'「エン・ミシュパト、すなわちカデシュ」という二重名は、中世注解で後代の名称説明として扱われます。',8:'ラシーは五王が敗北を覚悟しつつ出陣した勇気を読む一方、本文の中心は両軍が谷で対峙した事実です。',
9:'四対五の数の対照は、人数の多さが勝敗を保証しないというラビ的省察を招きました。原義では陣営の構成を明確にします。',10:'中世注解は「落ちた」を死亡ではなく穴へ落ちて逃れた可能性も含めて読み、後にソドム王が再登場する点と整合させます。',11:'ラビ的読解は食糧まで奪われたことを徹底的な略奪の印と見ます。都市の敗北が住民生活全体を襲います。',12:'ラシーはロトがソドムに住んでいたという一言を、以前の選択が危機へつながったことを示すと読みます。',
13:'ラシーは「ヘブライ人」を川の向こうから来た者、また世界の一方に立つ者という伝承と結びつけます。本文ではアブラムの社会的位置を示す呼称です。',14:'ラシーは חֲנִיכָיו を訓練された家人と説明します。三百十八をエリエゼルの数価と結ぶ伝承もありますが、字義上は人数です。',15:'中世注解は分隊と夜襲を慎重な戦術として読み、奇跡だけでなくアブラムの具体的行動を認めます。',16:'ラビ的注解は「すべて」を反復する回復の広がりに注目し、ロトだけでなく弱い立場の人々も救われた点を重視します。',
17:'中世注解は王の谷を後に王たちが集う場所として理解し、戦場から外交と礼儀の場へ移る転換点と読みます。',18:'ラシーはパンとぶどう酒を旅から戻った者へのもてなしと説明し、メルキ・ツェデクをセムと同一視する伝承も紹介します。',19:'中世注解は קֹנֵה を「造り主」と「所有者」の両義で論じ、天地の主権がアブラムの祝福の根拠になると読みます。',20:'ラシーは מִגֵּן を「引き渡した」と解し、勝利の主体を神に帰します。十分の一は感謝の応答として物語に置かれます。'
}
PAT={v:txt for v,txt in {
1:'教父的受容は諸王の争いを地上の権力の不安定さとして読みましたが、まず古代の国際紛争という物語設定です。',2:'教父説教では都市の王たちの名簿が人間的連合の限界を示す素材となりますが、固有名の過度な寓意化は原義と区別します。',3:'塩の海の地理は後代に裁きの記憶と結ばれました。教父的象徴は、ここで軍勢が集まる谷という叙述を土台とします。',4:'支配と反逆の年月は、教父的倫理読解で罪の束縛や解放への比喩となりましたが、本文は政治的服属を語ります。',5:'強大な軍勢の連勝は、後の逆転を準備します。教父的受容は力の誇りの不確かさをそこに読みました。',6:'遠征の広がりは暴力の拡散を示し、教父説教では欲望が境界を越える像として受け取られました。',7:'転進してさらに諸地域を打つ姿は、勝利が新たな暴力を生む連鎖として倫理的に読まれました。',8:'戦列を整える場面は勇気だけでなく、衝突が避けられない局面への人間的選択を考える素材となりました。',9:'教父的受容は少数と多数の逆転を神の摂理と結びつけましたが、本文の軍事構図を単純な善悪に置き換えません。',10:'穴への転落と敗走は、人間の計画が地形一つで崩れる脆さの像として説教に用いられました。',11:'財産と食糧の略奪は戦争が非戦闘員の生活を奪う現実を示し、教父的倫理では貪欲への警告となりました。',12:'ロトの捕囚は、危険に近づいた者を見捨てず救いへ向かう隣人愛の型として受容されました。',13:'知らせを運ぶ逃亡者は、苦境を伝える小さな証人の役割を示し、教父説教では共同体の相互責任へ適用されました。',14:'アブラムの出動は救出の勇気として読まれますが、暴力一般の賛美ではなく捕らわれた者を取り戻す目的に限定されます。',15:'夜襲の叙述は、教父的受容で警戒と節制の比喩となりました。これは軍事行動を霊的訓練へ移す後代の適用です。',16:'「取り戻した」の反復は救済の像として受容され、失われた人を財産と同列にせず回復へ迎える希望を示します。',17:'帰還後の出会いは、勝利後こそ人格が試される場面として説教的に読まれました。',18:'ヘブライ人への手紙7章はメルキ・ツェデクをキリスト論的に受容します。パンとぶどう酒も教会では聖餐的に読まれましたが、創世記の原義とは区別します。',19:'教父文学は天と地の造り主による祝福を普遍的な神理解と結びつけました。祝福の担い手と源を区別して読みます。',20:'十分の一は教父的受容で献げ物の模範とされましたが、本文では戦利品の分配と感謝の文脈に置かれています。'} .items()}
LIT={v:f'{THEME[v]}ことによって、創世記14章の国際戦争・救出・祝福という流れの中で場面を前進させます。14章は王名・地名・戦争年代など独特の語彙を持ち、単純にJ/Pへ機械的分類しにくい独立伝承的性格が論じられます。最終形ではロト救出とアブラムの信仰を結びます。' for v in range(1,21)}
DEV={
1:'大きな争いの陰には名を知られない多くの生活があります。権力者の物語だけでなく、巻き込まれる人々へ目を向けます。',2:'連合の数が多くても安全は保証されません。恐れに駆られた結束ではなく、正義と平和を支える関係を選びます。',3:'皆が同じ場所に集まる時、その目的を問い直します。集団の勢いに流されず、命を守る方向を探ります。',4:'長い服従の後の反発にも複雑な背景があります。抑圧と反抗の連鎖を単純な善悪だけで裁きません。',5:'勝ち続ける力は正しさの証明ではありません。強さが弱い者を踏みにじっていないかを問い続けます。',6:'争いは境界を越えて広がります。自分には遠い問題と思わず、平和のためにできる小さな働きを選びます。',7:'一度の成功がさらなる攻撃を正当化することがあります。止まる勇気と目的を問い直す知恵を求めます。',8:'対決が迫る時も、相手を記号にせず人として見る視点を失わないようにします。',9:'数や立場の有利さに心を預けず、正しい目的と手段を吟味します。',10:'思いがけない穴が計画を崩します。自分の力を過信せず、危険を見極めて助けを求めます。',11:'戦争の損失は食卓にまで及びます。奪われる側の暮らしを想像し、平和を抽象語にしません。',12:'ロトの選択に問題があっても、アブラムは彼を見捨てません。失敗した人を救う責任を手放さない姿を学びます。',13:'危機を知らせる一人の声が救出を始めます。悪い知らせを運ぶ人を責めず、耳を傾けて応答します。',14:'アブラムの行動は人を取り戻すためでした。力を用いる場面ほど、目的と限界を厳しく確かめます。',15:'勇気には準備と協力が伴います。衝動だけでなく、守るべき命のために知恵を尽くします。',16:'回復は物を返すだけで終わりません。人々が安全と尊厳を取り戻すところまで目を向けます。',17:'成功の後に誰の声を聞くかが重要です。称賛や利益に流されず、次の選択を整えます。',18:'メルキ・ツェデクは勝者へ食べ物と祝福を差し出しました。成果の場に休息と感謝を迎え入れます。',19:'祝福は人を持ち上げるだけでなく、命の源が自分を越えていることを思い出させます。',20:'アブラムは勝利を独占せず、与えられたものを返しました。成功を自分だけの手柄にせず分かち合います。'
}

def html_for(c,v):
    verse=root.find(f".//o:verse[@osisID='Gen.{c}.{v}']",NS); pieces=[]
    def unit(w):
        word=(w.text or '').replace('/',''); lemma=hebrew_lemma(w.attrib.get('lemma','')); pos,stem,infl=morph_info(w.attrib.get('morph','')); gl=gloss_for(w)
        return f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>'
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w' and child.attrib.get('type')!='x-ketiv': pieces.append(unit(child))
        elif tag=='note' and child.attrib.get('type')=='variant':
            qw=child.find('.//o:rdg[@type="x-qere"]/o:w',NS)
            if qw is not None: pieces.append(unit(qw))
        elif tag=='seg':
            punct={'x-maqqef':'־','x-sof-pasuq':'׃','x-paseq':'׀'}.get(child.attrib.get('type',''))
            if punct: pieces.append(f'<span class="pun">{punct}</span>')
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+CSS+'<body><div class="row">'+''.join(pieces)+'</div>'+JS+'</body></html>'

def details(c,v):
    w,l,p,s,i=key(c,v)
    kq='狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'
    if v in (2,8): kq='ツェボイムの綴りに狭義のケティーブ／ケレーがあります。本文表示はMorphHB/WLCのケレーを採り、子音綴りの差として扱います。古代訳・写本間の異読とは区別します。'
    return [('本文の骨格',f'14:{v}は、{THEME[v]}節です。固有名・反復・場面転換が章全体の流れを支えます。'),('文法',f'主要語 {w}（レンマ {l}）は、品詞 {p}、語幹 {s}、活用 {i}。語順と接続形がこの節の進行を作ります。'),('ケティーブ／ケレー・本文伝承',kq),('ラビ・中世',RAB[v]),('教父文学',PAT[v]),('文献層と物語',LIT[v]),('デボーショナルな受けとめ',DEV[v])]

for c,v in REFS: (HTML/f'018-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

DIRECT={
(14,1):('381870','438822'),(14,2):('381870','438823'),(14,3):('381870','438824'),(14,4):('381870','438825')}
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS]
labels=[float(x) for x in (BASE/'Lech-lecha-4.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels): raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'Lech-Lecha-4.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'Lech-Lecha-4.mp3'),'-af','silencedetect=noise=-36dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip(map(float,re.findall(r'silence_start: ([0-9.]+)',log)),map(float,re.findall(r'silence_end: ([0-9.]+)',log))))
idx=0; cuts=[0.0]; methods=[]
for cnt in counts[:-1]:
    idx+=cnt; last,nxt=labels[idx-1],labels[idx]
    cand=[(a,b) for a,b in sil if a>last and a<=nxt+0.65 and b>=nxt-0.20]
    if cand: a,b=min(cand,key=lambda x:abs((x[0]+x[1])/2-nxt)); cut=(a+b)/2; method=f'silence {a:.6f}-{b:.6f}'
    else: cut=nxt; method='PocketTorah next-token label'
    cuts.append(cut); methods.append(method)
cuts.append(duration)
target_wps=0.793064; original_wps=sum(counts)/duration; atempo=target_wps/original_wps
for srcf,dst in [('Lech-Lecha-4.mp3','Lech-Lecha-4-original.mp3'),('Lech-lecha-4.txt','Lech-lecha-4-labels.txt'),('PocketTorah-Genesis.json','PocketTorah-Genesis.json')]: shutil.copy2(BASE/srcf,SOURCE/dst)
(SOURCE/'PocketTorah-Lech-Lecha-4-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for n,(c,v) in enumerate(REFS):
    start,end=cuts[n],cuts[n+1]; rows.append((c,v,start,end,counts[n],methods[n] if n<len(methods) else 'end of source'))
    if (c,v) not in DIRECT:
        out=AUDIO/f'018-Genesis-{c}-{v}-study.mp3'; tmp=out.with_suffix('.tmp.mp3')
        cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'Lech-Lecha-4.mp3'),'-filter:a',f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}','-codec:a','libmp3lame','-q:a','5',str(tmp)]
        for attempt in range(3):
            tmp.unlink(missing_ok=True); subprocess.run(cmd,check=True)
            pr=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(tmp)],capture_output=True,text=True)
            if pr.returncode==0 and pr.stdout.strip() and float(pr.stdout)>0.5: tmp.replace(out); break
        else: raise RuntimeError(f'audio split failed: {out}')
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-{c}-{v}\t{s:.6f}\t{e:.6f}\t{n}\t{m}\n' for c,v,s,e,n,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t4\nrange\tGenesis 14:1-14:20\nprimary_sheets\thttps://www.sefaria.org/sheets/381870\nprimary_coverage\tGenesis 14:1-4\nfallback_coverage\tGenesis 14:5-20\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-4.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/Lech-lecha-4.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    if (c,v) in DIRECT: sh,mid=DIRECT[(c,v)]; ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\thttps://images.shulcloud.com/14396/{mid}.mp3')
    else: ar.append(f'Genesis-{c}-{v}\tPocketTorah physical split\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-4.mp3\thttps://raw.githubusercontent.com/theologia165/torah-audio-temp/main/018/audio/018-Genesis-{c}-{v}-study.mp3')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')

intro='東方の王たちの戦争に巻き込まれ、ロトは家族と財産ごと連れ去られます。知らせを受けたアブラムは仲間と夜の追撃に出て、捕らわれた人々を救い戻します。帰路で彼を迎えたのは、ソドムの王と、パンとぶどう酒を携えたサレムの王メルキ・ツェデクでした。武力で勝った直後、物語の中心は「誰の力で救われたのか」という祝福へ移ります。争いの中でも、人を取り戻し、成功を自分だけの手柄にしない姿が問われる場面です。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第4アリヤー**　創世記14:1–14:20（20節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記14:2と14:8のツェボイムの綴りに、MorphHB/WLCで狭義のケティーブ／ケレーがあります。表示本文はケレーを採用し、古代訳・写本間の異読とは区別します。
</callout>''']
for c,v in REFS:
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(c,v))
    parts.append(f'''---
### 創世記 {c}:{v}
{{{{AUDIO:Genesis-{c}-{v}}}}}
**私訳**：{J[(c,v)]}
**ヘブライ語**
{{{{EMBED:Genesis-{c}-{v}}}}}
**簡易な説明**：{key(c,v)[0]} はレンマ {key(c,v)[1]}、品詞 {key(c,v)[2]}、語幹 {key(c,v)[3]}、活用 {key(c,v)[4]}です。{THEME[v]}節です。
<details color="gray_bg">
<summary>詳しい解説</summary>
{det}
</details>''')
parts.append('''---
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 14](https://www.sefaria.org/Genesis.14)
- [Torah Chanting Helper: Genesis 14:1–4](https://www.sefaria.org/sheets/381870)
- [PocketTorah Lech-Lecha-4 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 14](https://www.sefaria.org/Rashi_on_Genesis.14)
- [Bereshit Rabbah 43](https://www.sefaria.org/Bereshit_Rabbah.43)
- [Hebrews 7](https://www.sefaria.org/Hebrews.7)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'labels':len(labels),'tokens':sum(counts),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
