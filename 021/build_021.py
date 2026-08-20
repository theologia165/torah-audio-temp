from pathlib import Path
import html,json,re,subprocess,shutil

BASE=Path('.')
src=(BASE/'build_020.py').read_text()
prefix=src.split("for c,v in REFS:(HTML/f'020-Genesis-{c}-{v}-r1.html')",1)[0]
exec(compile(prefix,'build_020.py','exec'),globals())
OUT=BASE/'021';HTML=OUT/'html';SOURCE=OUT/'source'
for p in (HTML,SOURCE):p.mkdir(parents=True,exist_ok=True)
REFS=[(17,v) for v in range(7,28)]
GLOSS.update({'4033':'寄留地','5769':'永遠','4186':'住居／寄留地','272':'所有地','8104':'守る','1285':'契約','4135':'割礼する','2145':'男性','6189':'包皮','226':'しるし','8083':'八','3117':'日','3211':'生まれた者','4736':'買い取られた者','3701':'銀','5236':'外国人','1320':'肉','5315':'いのち／人','6565':'破る','8283':'サラ','4428':'王','6711':'笑う','1121':'息子','3327':'イサク','5975':'立てる','8085':'聞く','6240':'十二','5387':'族長','4150':'定めの時','3615':'終える','4605':'上る','6106':'まさに／そのもの','7992':'十三','8337':'六','6965':'立つ／確立する'})

GLOSS.update({'5243':'割礼する','6190':'包皮','3820':'心','3863':'どうか／もし','61':'いや／確かに','312':'次の／別の'})

J={
(17,7):'「わたしは、わたしとあなたとの間、またあなたの後の子孫との間に、世代を通じてわたしの契約を立てる。永遠の契約として、あなたとあなたの後の子孫の神となる。」',
(17,8):'「わたしは、あなたとあなたの後の子孫に、あなたが寄留している地、すなわちカナンの全地を永遠の所有地として与える。わたしは彼らの神となる。」',
(17,9):'神はアブラハムに言われた。「あなたは、あなたとあなたの後の子孫が、世代を通じてわたしの契約を守りなさい。」',
(17,10):'「あなたがたが守るべき、わたしとあなたがた、またあなたの後の子孫との間の契約はこれである。あなたがたのすべての男子は割礼を受けなさい。」',
(17,11):'「あなたがたは包皮の肉に割礼を施しなさい。それが、わたしとあなたがたとの間の契約のしるしとなる。」',
(17,12):'「世代を通じて、あなたがたのすべての男子は生後八日で割礼を受けなければならない。家で生まれた者も、あなたの子孫でない外国人から銀で買い取られた者も同じである。」',
(17,13):'「あなたの家で生まれた者も、銀で買い取られた者も、必ず割礼を受けなければならない。こうして、わたしの契約はあなたがたの肉に永遠の契約として刻まれる。」',
(17,14):'「包皮の肉に割礼を受けない無割礼の男子、その人は民の中から断たれる。わたしの契約を破ったからである。」',
(17,15):'神はアブラハムに言われた。「あなたの妻サライを、もはやサライと呼んではならない。彼女の名はサラとなる。」',
(17,16):'「わたしは彼女を祝福し、彼女によってあなたに男の子を与える。わたしは彼女を祝福し、彼女は諸国民となり、諸民族の王たちが彼女から出る。」',
(17,17):'アブラハムは顔を伏せて笑い、心の中で言った。「百歳の者に子が生まれるだろうか。九十歳のサラが子を産むだろうか。」',
(17,18):'アブラハムは神に言った。「どうかイシュマエルが、あなたの御前で生きますように。」',
(17,19):'神は言われた。「いや、あなたの妻サラがあなたに男の子を産む。あなたはその名をイサクと呼びなさい。わたしは彼と、彼の後の子孫との間に、永遠の契約としてわたしの契約を立てる。」',
(17,20):'「イシュマエルについても、わたしはあなたの願いを聞いた。見よ、わたしは彼を祝福し、豊かに実らせ、非常に多く増やす。彼は十二人の族長を生み、わたしは彼を大いなる国民とする。」',
(17,21):'「しかし、わたしの契約はイサクと立てる。サラは来年のこの定めの時に、彼をあなたに産む。」',
(17,22):'神はアブラハムと語り終えると、彼のもとから上って行かれた。',
(17,23):'アブラハムはその日、息子イシュマエル、家で生まれたすべての者、銀で買い取ったすべての者、すなわち家の男子全員を取り、神が語られたとおり、その包皮の肉に割礼を施した。',
(17,24):'アブラハムが包皮の肉に割礼を受けたとき、彼は九十九歳であった。',
(17,25):'息子イシュマエルが包皮の肉に割礼を受けたとき、彼は十三歳であった。',
(17,26):'まさにその日、アブラハムと息子イシュマエルは割礼を受けた。',
(17,27):'彼の家のすべての男子、家で生まれた者も、外国人から銀で買い取られた者も、彼と共に割礼を受けた。'}

FLOW=['世代を越える永遠の契約を宣言する','カナンの地と神との関係を結ぶ','契約を守る責任をアブラハム側へ返す','契約のしるしとして男子の割礼を命じる','肉に刻まれるしるしの意味を示す','八日目と家の全男子への適用を定める','命令を強調し永遠の契約を肉に結ぶ','契約を破ることの重大さを告げる','サライをサラへ改名する','サラ自身への祝福と王たちを約束する','高齢の夫婦に子が生まれる驚きを笑いで描く','アブラハムがイシュマエルの命を願う','イサクの誕生と契約の継承を明示する','イシュマエルにも豊かな祝福を約束する','契約の継承者と誕生時期を確定する','神の語りが終わり顕現場面を閉じる','アブラハムがその日のうちに命令を実行する','アブラハムの年齢を記す','イシュマエルの年齢を記す','父子が同じ日に割礼を受けたと要約する','家のすべての男子が共に受けたと締めくくる']
THEME={r:re.sub(r'[。「」]', '',J[r])[:58] for r in REFS}

RAB={
(17,7):'ラシーは「あなたの神となる」を、契約が子孫へ継続する約束として読む。ランバンは、個人への約束が共同体の歴史へ広がる点を重視する。',
(17,8):'ラシーはカナン所有と「彼らの神となる」を結び付け、土地と契約生活の関係を読む。後代の注解は、所有を無制限な権利ではなく神への応答と結び付ける。',
(17,9):'イブン・エズラは「あなたは」という主語の強調に注目し、神の約束に人の遵守が応答する構造を読む。',
(17,10):'ラシーと中世注解は「これが契約」と割礼を同定し、しるしが抽象的観念でなく身体的実践である点を確認する。',
(17,11):'ラシーは「契約のしるし」を、契約そのものと、それを可視化する徴との関係から説明する。',
(17,12):'ラビ的伝統は「八日目」を厳密に数え、家で生まれた者と買い取られた者の範囲を法的に検討した。本文は家父長だけでなく家全体を視野に入れる。',
(17,13):'「必ず割礼を受ける」という同語反復は、中世注解でも命令の確実性を強める表現として扱われる。',
(17,14):'ラビ文献は「断たれる」を神の裁きに属する語として慎重に区別し、人が恣意的に排除を行う根拠とはしない。',
(17,15):'ラシーはサライを「私の女主人」、サラをより広い意味での「女主人」と説明し、改名を使命の拡大として読む。',
(17,16):'ラシーはサラ自身が祝福の主体であり、諸国民と王たちが彼女から出る点を強調する。',
(17,17):'ラシーはアブラハムの笑いを喜びとして、18章のサラの笑いとの差を論じる。本文上は、驚きと信頼が同時に存在する場面である。',
(17,18):'中世注解はアブラハムの言葉を、イシュマエルを見捨てたくない父の願いとして読む。神はその願いを退けず、契約継承とは別の祝福を答える。',
(17,19):'ラシーは「イサク」という名を笑いと結び付け、驚きの出来事が子の名として記憶されると読む。',
(17,20):'ラシーは「聞いた」とイシュマエルの名の語呂を指摘する。祝福は契約継承者だけに狭められず、イシュマエルにも及ぶ。',
(17,21):'ランバンはイサクとの契約を、20節のイシュマエルへの祝福を否定するのでなく、役割を区別する言葉として読む。',
(17,22):'中世注解は「上った」を神の空間的移動だけに還元せず、顕現が終わったことを示す物語表現として扱う。',
(17,23):'ラシーは「まさにその日」を、公然と遅滞なく命令を実行したことの強調として読む。',
(17,24):'年齢の明記は、老齢であってもアブラハムが命令に応答したことを示すとラビ的伝統は読む。',
(17,25):'イシュマエルの十三歳という年齢は、後代のユダヤ伝統で彼の自覚的参加を考える手掛かりとなったが、本文はまず父子の同日実行を記す。',
(17,26):'「その日」の反復をラシーは迅速な服従の強調として読む。父子が同じ日にしるしを受けたことが前景化される。',
(17,27):'家の全男子という結びは、中世注解でも契約のしるしがアブラハム個人に閉じないことを示すものとして読まれる。'}

PAT={r:(f'アウグスティヌスは『神の国』でアブラハム契約を救済史の中に位置付ける。創世記17:{r[1]}の受容では、歴史的なしるしを後代のキリスト教が洗礼や信仰へ類型的に展開したことと、本文のユダヤ的文脈を区別する。' if r[1]<=14 else f'アウグスティヌスや初期キリスト教の創世記受容は創世記17:{r[1]}を約束と成就の系列で読む。ただし、サラ・イサク・イシュマエルの歴史的役割を後代の類型だけで消さないことが必要である。') for r in REFS}

LIT={r:(f'創世記17:{r[1]}は、契約、世代、永遠、しるしという祭司的語彙が集中する単元に属する。最終形では神の約束と共同体の実践が相互に結ばれる。' if r[1]<=14 else f'創世記17:{r[1]}は、改名・子の約束・割礼の実行を一つの契約物語にまとめる。資料批評上の祭司的特徴を認めつつ、最終形の連続した展開を読む。') for r in REFS}

DEV={r:f'創世記17:{r[1]}は、神の約束が人を孤立させず、世代や家の人々との責任へ向かわせることを示す。契約の言葉を他者を排除する道具にせず、与えられた恵みに誠実に応える歩みを考えたい。' for r in REFS}

def details(c,v):
    w,l,p,s,i=key(c,v);r=(c,v)
    gram=f'主要語 {w}（レンマ {l}）は、品詞 {p}、語幹 {s}、活用 {i}です。創世記{c}:{v}では、この語形が「{FLOW[REFS.index(r)]}」という文の進行を支えます。'
    struct=f'17:{v}は、{FLOW[REFS.index(r)]}節です。「{THEME[r]}」という内容が、約束の宣言から契約のしるしの実行へ進む物語を担います。'
    return [('本文の骨格',struct),('文法',gram),('ケティーブ／ケレー・本文伝承','狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'),('ラビ・中世',RAB[r]),('教父文学',PAT[r]),('文献層と物語',LIT[r]),('デボーショナルな受けとめ',DEV[r])]

for c,v in REFS:(HTML/f'021-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

def sheet_map(path):
    d=json.load(open(path));out={};ref=None
    ss=d.get('sources',[])
    for i,s in enumerate(ss):
        if s.get('ref'):ref=s['ref']
        if 'Full Verse Chanted' in str(s.get('comment','')) and i+1<len(ss) and ss[i+1].get('media') and ref:
            m=re.fullmatch(r'Genesis 17:(\d+)',ref)
            if m:out[(17,int(m.group(1)))]=(str(d['id']),ss[i+1]['media'])
    return out
DIRECT={}
for f in sorted((BASE/'sefaria021').glob('*.json')):DIRECT.update(sheet_map(f))
if set(DIRECT)!=set(REFS):raise SystemExit(f'direct mapping incomplete: {sorted(set(REFS)-set(DIRECT))}')

pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS]
labels=[float(x) for x in (BASE/'lech-lecha-7.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels):raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
shutil.copy2(BASE/'Lech-Lecha-7.mp3',SOURCE/'Lech-Lecha-7-original.mp3')
shutil.copy2(BASE/'lech-lecha-7.txt',SOURCE/'lech-lecha-7-labels.txt')
(SOURCE/'PocketTorah-Lech-Lecha-7-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    sh,url=DIRECT[(c,v)];ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\t{url}')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')
(OUT/'source.tsv').write_text('field\tvalue\nparasha\tLech-Lecha\naliyah\t7\nrange\tGenesis 17:7-17:27\nprimary_sheets\t'+' ; '.join('https://www.sefaria.org/sheets/'+x for x in ['574276','594560','594561','594562','594563','594564'])+'\nprimary_coverage\tGenesis 17:7-27\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-7.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-7.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\n',encoding='utf-8')

intro='神はアブラハムとの約束を、子孫へ続く永遠の契約として語り、割礼をその目に見えるしるしとされます。妻サライはサラと改名され、高齢の二人に息子イサクが生まれるという驚きの知らせが届きます。アブラハムはイシュマエルの将来も願い、神はその願いにも祝福で応えます。語り終えると、アブラハムはその日のうちに家の男子全員と共に命令を実行します。約束を受け取る喜びと、すぐに応答する責任が一つにつながる場面です。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第7アリヤー**　創世記17:7–17:27（21節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記17:7–17:27に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。古代訳・写本間の異読はK/Qとは区別します。
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
- [Sefaria Genesis 17:7–27](https://www.sefaria.org/Genesis.17.7-27)
- [Torah Chanting Helper: Genesis 17:7–10](https://www.sefaria.org/sheets/574276)
- [Torah Chanting Helper: Genesis 17:11–14](https://www.sefaria.org/sheets/594560)
- [Torah Chanting Helper: Genesis 17:15–18](https://www.sefaria.org/sheets/594561)
- [Torah Chanting Helper: Genesis 17:19–22](https://www.sefaria.org/sheets/594562)
- [Torah Chanting Helper: Genesis 17:23–26](https://www.sefaria.org/sheets/594563)
- [Torah Chanting Helper: Genesis 17:27](https://www.sefaria.org/sheets/594564)
- [Rashi on Genesis 17](https://www.sefaria.org/Rashi_on_Genesis.17)
- [Genesis Rabbah 46–47](https://www.sefaria.org/Bereshit_Rabbah.46)
- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'html':len(list(HTML.glob('*.html'))),'direct':len(DIRECT),'tokens':sum(counts),'labels':len(labels),'intro_chars':len(intro)},ensure_ascii=False))
