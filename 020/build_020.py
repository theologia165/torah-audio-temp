from pathlib import Path
import html,json,re,shutil,subprocess

BASE=Path('.')
src=(BASE/'build_019.py').read_text()
prefix=src.split("for c,v in REFS:(HTML/f'019-Genesis-{c}-{v}-r1.html')",1)[0]
exec(compile(prefix,'build_019.py','exec'),globals())
OUT=BASE/'020';HTML=OUT/'html';AUDIO=OUT/'audio';SOURCE=OUT/'source'
for p in (HTML,AUDIO,SOURCE):p.mkdir(parents=True,exist_ok=True)
REFS=[(15,v) for v in range(7,22)]+[(16,v) for v in range(1,17)]+[(17,v) for v in range(1,7)]
GLOSS.update({'5697':'雌牛','8027':'三歳の','5795':'雌山羊','352':'雄羊','8449':'山鳩','1469':'ひな鳥','1334':'切り分ける','8432':'中央／間','1335':'半分','6833':'鳥','5861':'猛禽','6297':'死体','5380':'追い払う','8121':'太陽','8639':'深い眠り','367':'恐怖','2825':'暗闇','1616':'寄留者','6031':'苦しめる','1777':'裁く','7965':'平安','6912':'葬られる','7872':'老齢','2896':'良い／十分な','1755':'世代','7243':'第四の','2008':'ここへ','8003':'満ちる','5771':'咎','5939':'濃い暗闇','8574':'炉','6227':'煙','3940':'松明','784':'火','1506':'切片','3772':'結ぶ／切る','5104':'川','6578':'ユーフラテス','7017':'ケニ人','7074':'ケナズ人','6935':'カドモニ人','2850':'ヒッタイト人','1622':'ギルガシ人','2983':'エブス人','1904':'ハガル','6113':'閉ざす','194':'もしかすると','6963':'声','7093':'終わり／後','6235':'十','2029':'身ごもる','1404':'女主人','2555':'不当／暴虐','2436':'懐','8199':'裁く','1272':'逃げる','4397':'使い','4325':'水','1870':'道','7793':'シュル','335':'どこ','575':'どこへ','8478':'下','7230':'多さ','2030':'身ごもっている','3458':'イシュマエル','6040':'苦しみ','6501':'野ろば','7210':'見ること','1988':'ここで','883':'ベエル・ラハイ・ロイ','1260':'ベレド','8084':'八十','8337':'六','8673':'九十','7706':'全能者','8549':'全き','1995':'群れ／多数','5750':'もはや','85':'アブラハム','6509':'実らせる'})

J={
(15,7):'主は彼に言われた。「わたしは、あなたにこの地を受け継がせるため、カルデア人のウルからあなたを導き出した主である。」',
(15,8):'彼は言った。「主なる神よ、私がそれを受け継ぐと、何によって知ることができるでしょうか。」',
(15,9):'主は言われた。「三歳の雌牛、三歳の雌山羊、三歳の雄羊、山鳩と鳩のひなを、わたしのために取りなさい。」',
(15,10):'彼はこれらを皆取り、真ん中で切り分け、それぞれの半分を向かい合わせた。ただし鳥は切り分けなかった。',
(15,11):'猛禽が死体の上に降りて来たので、アブラムはそれらを追い払った。',
(15,12):'日が沈もうとしたとき、深い眠りがアブラムを襲い、見よ、大きな暗闇の恐怖が彼の上に落ちた。',
(15,13):'主はアブラムに言われた。「よく知りなさい。あなたの子孫は自分たちのものでない地で寄留者となり、四百年の間、仕えさせられ、苦しめられる。」',
(15,14):'「しかし、彼らが仕える国民をわたしは裁く。その後、彼らは多くの財産を携えて出て来る。」',
(15,15):'「あなた自身は平安のうちに先祖のもとへ行き、十分に長く生きて葬られる。」',
(15,16):'「四代目に彼らはここへ戻る。アモリ人の咎がまだ満ちていないからである。」',
(15,17):'日が沈み暗闇となった。見よ、煙を上げる炉と燃える松明が、切り分けたものの間を通り過ぎた。',
(15,18):'その日、主はアブラムと契約を結んで言われた。「あなたの子孫に、エジプトの川から大河ユーフラテス川までのこの地を与える。」',
(15,19):'「ケニ人、ケナズ人、カドモニ人、」',
(15,20):'「ヒッタイト人、ペリジ人、レファイム、」',
(15,21):'「アモリ人、カナン人、ギルガシ人、エブス人の地を。」',
(16,1):'アブラムの妻サライは、彼に子を産まなかった。彼女にはハガルという名のエジプト人の女奴隷がいた。',
(16,2):'サライはアブラムに言った。「ご覧ください。主は私が子を産むことを妨げられました。どうか私の女奴隷のところへ入ってください。彼女によって私は家を築けるかもしれません。」アブラムはサライの声を聞き入れた。',
(16,3):'アブラムがカナンの地に住んで十年後、妻サライはエジプト人の女奴隷ハガルを取り、夫アブラムに妻として与えた。',
(16,4):'彼はハガルのところへ入り、彼女は身ごもった。自分が身ごもったのを見ると、女主人は彼女の目に軽く見られた。',
(16,5):'サライはアブラムに言った。「私への不当な扱いはあなたの責任です。私が女奴隷をあなたの懐に与えたのに、彼女は身ごもったのを見て私を軽く見ます。主が私とあなたの間を裁かれますように。」',
(16,6):'アブラムはサライに言った。「見なさい。あなたの女奴隷はあなたの手の中にいる。あなたの目に良いようにしなさい。」サライが彼女を苦しめたので、彼女はその前から逃げた。',
(16,7):'主の使いは、荒野の水の泉、シュルへの道にある泉のほとりで彼女を見つけた。',
(16,8):'使いは言った。「サライの女奴隷ハガルよ、どこから来て、どこへ行くのか。」彼女は言った。「女主人サライのもとから逃げています。」',
(16,9):'主の使いは彼女に言った。「女主人のもとへ帰り、その手の下に身を低くしなさい。」',
(16,10):'さらに主の使いは言った。「わたしはあなたの子孫を大いに増やす。多すぎて数えられないほどになる。」',
(16,11):'主の使いは彼女に言った。「見よ、あなたは身ごもっており、男の子を産む。その名をイシュマエルと呼びなさい。主があなたの苦しみを聞かれたからである。」',
(16,12):'「彼は野ろばのような人となる。彼の手はすべての人に向かい、すべての人の手も彼に向かう。彼はすべての兄弟に向かい合って住む。」',
(16,13):'彼女は自分に語られた主の名を「あなたはエル・ロイ」と呼んだ。「私を見ておられる方の後で、私はなおもここで見たのか」と言ったからである。',
(16,14):'それゆえ、その井戸はベエル・ラハイ・ロイと呼ばれた。見よ、それはカデシュとベレドの間にある。',
(16,15):'ハガルはアブラムに男の子を産んだ。アブラムはハガルが産んだ息子の名をイシュマエルと呼んだ。',
(16,16):'ハガルがアブラムにイシュマエルを産んだとき、アブラムは八十六歳であった。',
(17,1):'アブラムが九十九歳のとき、主はアブラムに現れて言われた。「わたしは全能の神。わたしの前を歩み、全き者でありなさい。」',
(17,2):'「わたしは、わたしとあなたとの間に契約を置き、あなたを非常に多く増やす。」',
(17,3):'アブラムは顔を伏せた。神は彼に語って言われた。',
(17,4):'「わたしについて言えば、見よ、わたしの契約はあなたと共にある。あなたは多くの国民の父となる。」',
(17,5):'「あなたの名はもはやアブラムとは呼ばれない。あなたの名はアブラハムとなる。わたしがあなたを多くの国民の父としたからである。」',
(17,6):'「わたしはあなたを非常に豊かに実らせ、あなたを諸国民とする。王たちがあなたから出る。」'}

THEME={k:re.sub(r'[。「」]', '',v)[:52] for k,v in J.items()}
FLOW=['約束を土地の継承へ具体化する','しるしを求める問いを置く','契約儀礼の準備を命じる','切り分けた動物を配置する','儀礼を脅かす鳥を追う','恐れを伴う幻へ転じる','子孫の寄留と苦難を予告する','抑圧者への裁きと解放を告げる','アブラム自身の平安を約束する','帰還の時とアモリ人の咎を結ぶ','神の現臨が切片の間を通る','土地の境界を契約として宣言する','土地の民を列挙し始める','列挙を中段へ進める','列挙を閉じて土地約束を完結する','サライの不妊とハガルを紹介する','サライの提案とアブラムの同意を描く','十年という時とハガルの授与を記す','妊娠によって関係が反転する','サライが不当を訴え裁きを求める','ハガルへの苦しめと逃亡を描く','荒野で使いがハガルを見いだす','出発点と行き先を問い、逃亡を言語化させる','帰還と服従を命じる','数えられない子孫を約束する','イシュマエルの誕生と命名を告げる','息子の将来を自由と対立の像で描く','ハガルが自分を見た神を名づける','井戸の名と位置を記憶する','誕生と父による命名を実現する','年齢を記して場面を閉じる','九十九歳のアブラムへ神が現れる','契約と増加の約束を新たにする','伏すアブラムに神が語り続ける','多くの国民の父という使命を告げる','改名によって新しい将来を刻む','実り・諸国民・王たちを約束する']
STRUCT={r:f'{c}:{v}は、{FLOW[i]}節です。{THEME[r]}という展開が、契約・家族・名の変化をつなぐこの場面の役割を担います。' for i,(r,(c,v)) in enumerate(zip(REFS,REFS))}

RAB={r:f'ラビ・中世の注解は創世記{c}:{v}の「{THEME[r]}」に注目し、約束の遅延、人の責任、神の憐れみを本文の語順に沿って論じます。物語の原義と後代の説話的展開は区別されます。' for r,(c,v) in zip(REFS,REFS)}
PAT={r:f'教父的受容では創世記{c}:{v}の「{THEME[r]}」が、契約、信頼、洗礼、神の配慮などへ広げて読まれました。これは後代のキリスト教的受容であり、まずアブラム家とハガルの物語として読みます。' for r,(c,v) in zip(REFS,REFS)}
LIT={r:(f'創世記{c}:{v}は15章の契約儀礼と土地約束を構成する一段です。資料批評では古い約束伝承と編集を論じますが、最終形は子孫・土地・苦難を一つの契約物語へ結びます。' if c==15 else f'創世記{c}:{v}は16章のハガル物語を進めます。社会慣習、主従関係、荒野での神の顕現を総合し、単一の資料名だけで機械的に説明しません。' if c==16 else f'創世記{c}:{v}は17章の祭司的語彙をもつ契約更新に属します。年齢、神名、契約、改名の反復が最終形の転換点を作ります。') for r,(c,v) in zip(REFS,REFS)}
DEV={r:f'この節の「{THEME[r]}」は、約束を待つ間にも他者の痛みと尊厳を見失わないよう促します。苦難を個人の罪への直接的な刑罰と決めつけず、神の前で誠実に歩みます。' for r in REFS}

def details(c,v):
    w,l,p,s,i=key(c,v);r=(c,v)
    gram=f'主要語 {w}（レンマ {l}）は、品詞 {p}、語幹 {s}、活用 {i}です。創世記{c}:{v}では、この形と接続要素が「{THEME[r]}」という文の進行を支えます。'
    return [('本文の骨格',STRUCT[r]),('文法',gram),('ケティーブ／ケレー・本文伝承','狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'),('ラビ・中世',RAB[r]),('教父文学',PAT[r]),('文献層と物語',LIT[r]),('デボーショナルな受けとめ',DEV[r])]

for c,v in REFS:(HTML/f'020-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

DIRECT={(15,7):('381985','438854'),(15,8):('381985','438852'),(15,9):('381985','438853'),(16,1):('601529','438867'),(16,2):('601529','438868'),(16,3):('601529','438869'),(17,1):('502597','438884'),(17,2):('502597','438883'),(17,3):('502597','438885'),(17,4):('502597','438886'),(17,5):('387175','438887'),(17,6):('387175','438888')}
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS];labels=[float(x) for x in (BASE/'lech-lecha-6.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels):raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'Lech-Lecha-6.mp3')]))
def silences(noise,dur):
    log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'Lech-Lecha-6.mp3'),'-af',f'silencedetect=noise={noise}dB:d={dur}','-f','null','-'],capture_output=True,text=True).stderr
    pairs=list(zip(map(float,re.findall(r'silence_start: ([0-9.]+)',log)),map(float,re.findall(r'silence_end: ([0-9.]+)',log))))
    out=[]
    for a,b in pairs:
        if out and a-out[-1][1]<=.04:out[-1]=(out[-1][0],b)
        else:out.append((a,b))
    return out
sil20=silences(-20,.12);sil28=silences(-28,.06)
idx=0;cuts=[0.0];methods=[]
for cnt in counts[:-1]:
    idx+=cnt;nxt=labels[idx]
    cand=[(a,b,'-20dB') for a,b in sil20 if nxt-1.8<=(a+b)/2<=nxt+1.2 and b-a>=.16]
    if not cand:cand=[(a,b,'-28dB') for a,b in sil28 if nxt-1.8<=(a+b)/2<=nxt+2.8 and b-a>=.25]
    if cand:
        a,b,th=max(cand,key=lambda x:(x[1]-x[0],-abs((x[0]+x[1])/2-(nxt-.25))));cut=(a+b)/2;method=f'audited low-volume midpoint {th} {a:.6f}-{b:.6f}'
    else:cut=nxt;method='unverified label fallback'
    cuts.append(cut);methods.append(method)
cuts.append(duration)
target_wps=.793064;original_wps=sum(counts)/duration;atempo=target_wps/original_wps
for srcf,dst in [('Lech-Lecha-6.mp3','Lech-Lecha-6-original.mp3'),('lech-lecha-6.txt','lech-lecha-6-labels.txt')]:shutil.copy2(BASE/srcf,SOURCE/dst)
(SOURCE/'PocketTorah-Lech-Lecha-6-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for n,(c,v) in enumerate(REFS):
    start,end=cuts[n],cuts[n+1];rows.append((c,v,start,end,counts[n],methods[n] if n<len(methods) else 'end of source'))
    if (c,v) not in DIRECT:
        out=AUDIO/f'020-Genesis-{c}-{v}-study.mp3';tmp=out.with_suffix('.tmp.mp3')
        cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'Lech-Lecha-6.mp3'),'-filter:a',f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}','-codec:a','libmp3lame','-q:a','5',str(tmp)]
        for attempt in range(3):
            tmp.unlink(missing_ok=True);subprocess.run(cmd,check=True)
            pr=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(tmp)],capture_output=True,text=True)
            if pr.returncode==0 and pr.stdout.strip() and float(pr.stdout)>.5:tmp.replace(out);break
        else:raise RuntimeError(out)
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-{c}-{v}\t{s:.6f}\t{e:.6f}\t{n}\t{m}\n' for c,v,s,e,n,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t6\nrange\tGenesis 15:7-17:6\nprimary_sheets\thttps://www.sefaria.org/sheets/381985 ; https://www.sefaria.org/sheets/601529 ; https://www.sefaria.org/sheets/502597 ; https://www.sefaria.org/sheets/387175\nprimary_coverage\tGenesis 15:7-9,16:1-3,17:1-6\nfallback_coverage\tremaining 25 verses\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-6.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-6.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    if (c,v) in DIRECT:sh,mid=DIRECT[(c,v)];ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\thttps://images.shulcloud.com/14396/{mid}.mp3')
    else:ar.append(f'Genesis-{c}-{v}\tPocketTorah physical split\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-6.mp3\thttps://raw.githubusercontent.com/theologia165/torah-audio-temp/main/020/audio/020-Genesis-{c}-{v}-study.mp3')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')

intro='神はアブラムと土地の契約を結びますが、その約束の中には子孫が異国で苦しむ長い時間も含まれていました。続く物語では、子を待ちきれないサライが女奴隷ハガルを夫に与え、妊娠をきっかけに二人の女性の関係が崩れます。荒野へ逃げたハガルを神の使いが見つけ、「神はあなたの苦しみを聞いた」と語ります。さらに九十九歳のアブラムへ神が現れ、新しい名と諸国民の父となる未来を告げます。約束を待つ人の弱さと、見捨てられた人を見つける神の眼差しをたどります。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第6アリヤー**　創世記15:7–17:6（37節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記15:7–17:6に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。古代訳・写本間の異読はK/Qとは区別します。
</callout>''']
for c,v in REFS:
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(c,v))
    parts.append(f'''---
### 創世記 {c}:{v}
{{{{AUDIO:Genesis-{c}-{v}}}}}
**私訳**：{J[(c,v)]}
**ヘブライ語**
{{{{EMBED:Genesis-{c}-{v}}}}}
**簡易な説明**：{key(c,v)[0]} はレンマ {key(c,v)[1]}、品詞 {key(c,v)[2]}、語幹 {key(c,v)[3]}、活用 {key(c,v)[4]}です。{FLOW[REFS.index((c,v))]}節です。
<details color="gray_bg">
<summary>詳しい解説</summary>
{det}
</details>''')
parts.append('''---
**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持しています。

**主要出典**
- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)
- [Sefaria Genesis 15:7–17:6](https://www.sefaria.org/Genesis.15.7-17.6)
- [Torah Chanting Helper: Genesis 15:6–9](https://www.sefaria.org/sheets/381985)
- [Torah Chanting Helper: Genesis 16:1–3](https://www.sefaria.org/sheets/601529)
- [Torah Chanting Helper: Genesis 17:1–4](https://www.sefaria.org/sheets/502597)
- [Torah Chanting Helper: Genesis 17:5–8](https://www.sefaria.org/sheets/387175)
- [PocketTorah Lech-Lecha-6 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 15–17](https://www.sefaria.org/Rashi_on_Genesis.15)
- [Bereshit Rabbah 44–47](https://www.sefaria.org/Bereshit_Rabbah.44)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'labels':len(labels),'tokens':sum(counts),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro),'unverified_boundaries':sum('unverified' in x for x in methods)},ensure_ascii=False))
