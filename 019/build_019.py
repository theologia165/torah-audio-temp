from pathlib import Path
import html,json,re,shutil,subprocess,xml.etree.ElementTree as ET

BASE=Path('.')
src=(BASE/'build_018.py').read_text()
prefix=src.split("for c,v in REFS: (HTML/f'018-Genesis-{c}-{v}-r1.html')",1)[0]
exec(compile(prefix,'build_018.py','exec'),globals())
OUT=BASE/'019'; HTML=OUT/'html'; AUDIO=OUT/'audio'; SOURCE=OUT/'source'
for p in (HTML,AUDIO,SOURCE): p.mkdir(parents=True,exist_ok=True)
REFS=[(14,v) for v in range(21,25)]+[(15,v) for v in range(1,7)]

GLOSS.update({'7311':'上げる','2339':'糸','8288':'ひも','5275':'履物','6238':'富ませる','1107':'私以外','7535':'ただ／ただし','398':'食べる','5288':'若者たち','2506':'分け前','4236':'幻','3372':'恐れる','595':'私','4043':'盾','7939':'報い','7235':'非常に多い','136':'主','3069':'主なる神','6185':'子のない','4943':'所有／管理','461':'エリエゼル','3423':'相続する者','4578':'胎内／内から','2351':'外へ','5027':'見上げる','5608':'数える','3556':'星','3541':'このように','539':'信じる','2803':'認める／数える','6666':'義'})

J={(14,21):'ソドムの王はアブラムに言った。「人々は私に返し、財産はあなたが取ってください。」',
(14,22):'アブラムはソドムの王に言った。「私は、天と地の造り主、いと高き神、主に手を上げて誓う。」',
(14,23):'「糸一本から履物のひも一本まで、あなたのものは何一つ取らない。『私がアブラムを富ませた』とあなたが言わないためである。」',
(14,24):'「ただし、若者たちが食べたものと、私と共に行った人々、アネル、エシュコル、マムレの分け前は別である。彼らには自分たちの分け前を取らせてほしい。」',
(15,1):'これらの出来事の後、主の言葉が幻のうちにアブラムに臨んだ。「アブラムよ、恐れてはならない。わたしはあなたの盾。あなたの報いは非常に大きい。」',
(15,2):'アブラムは言った。「主なる神よ、私に何をくださるのですか。私は子のないままです。私の家を継ぐ者はダマスコのエリエゼルです。」',
(15,3):'さらにアブラムは言った。「ご覧ください。あなたは私に子孫を与えてくださいませんでした。だから、私の家の者が私を相続するのです。」',
(15,4):'すると見よ、主の言葉が彼に臨んだ。「その者があなたを相続するのではない。あなた自身から出る者があなたを相続する。」',
(15,5):'主は彼を外へ連れ出して言われた。「さあ、天を見上げ、星を数えられるなら数えてみなさい。」そして言われた。「あなたの子孫はこのようになる。」',
(15,6):'彼は主を信じた。主はそれを彼の義と認められた。'}

THEME={(14,21):'ソドム王が人々の返還と財産の譲渡を提案する',(14,22):'アブラムがいと高き神に誓いを立てる',(14,23):'ソドム王の富によって成功したと見られることを拒む',(14,24):'自分は受け取らず、同盟者の正当な分け前は守る',(15,1):'戦いの後の恐れに対して神が盾と報いを約束する',(15,2):'アブラムが子のない現実と相続の不安を率直に訴える',(15,3):'約束と現実の隔たりを家の相続人という形で言い直す',(15,4):'神が家の者でなくアブラム自身から出る相続人を約束する',(15,5):'星空を通して数えきれない子孫の約束を可視化する',(15,6):'アブラムの信頼と神による義の認定を簡潔に結ぶ'}
RAB={(14,21):'中世注解は「魂」を捕虜となった人々、「財産」を戦利品と読み、王の提案が人と物を区別している点に注目します。',(14,22):'ラシーは手を上げる行為を誓いの身振りと説明します。アブラムは勝利の源をソドムではなく天地の主へ帰します。',(14,23):'ラシーは糸と履物のひもを最小の品の対句と読みます。後の履物・糸に関する報いを語る伝承は、字義から展開した受容です。',(14,24):'中世注解はアブラム自身の辞退と同盟者の権利を区別します。自分の敬虔を他者へ一方的に課さない読みです。',(15,1):'ラシーは戦いで人を殺したことや報いを使い果たしたことへのアブラムの恐れを背景に読みます。神の「恐れるな」がその不安へ応答します。',(15,2):'ラシーと中世注解は「家の管理者」と「ダマスコのエリエゼル」の難しい構文を論じます。固有名と役割の関係には複数の説明があります。',(15,3):'アブラムの反復は不信の断言より、与えられた約束を現実の相続問題に即して問い直す訴えとして読まれます。',(15,4):'中世注解は「あなたの内から出る者」を実子の明示と理解し、エリエゼル相続の可能性を退ける応答と読みます。',(15,5):'ラシーは「外へ」を文字どおりの天幕の外と読むほか、占星術的運命観の外へ出よという説話的解釈も紹介します。',(15,6):'ラシーは「義と認めた」の主語を神とする読みを採り、ランバンらは信頼そのものと神の約束理解をめぐって議論します。'}
PAT={(14,21):'教父的受容は、人を返し財産を取れという提案を、勝利後に利益へ心を奪われる誘惑として読みました。原義では戦利品交渉です。',(14,22):'誓いは教父説教で神への忠誠の表明とされます。天地の主という称号が、地域王を越える主権を示します。',(14,23):'アブラムの辞退は教父文学で貪欲からの自由の模範となりました。ただし所有一般の否定でなく、功績の帰属を守る選択です。',(14,24):'同盟者の分け前を認める姿は、教父的倫理で自制と正義の両立として受容されました。自分の決断を他者へ強制しません。',(15,1):'「わたしはあなたの盾」は教父文学で神の保護と究極の報いとして読まれました。戦争の不安から信頼へ移る本文が基礎です。',(15,2):'アブラムの問いは、教父的祈りの伝統で疑いを隠さず神へ向ける模範となりました。問いを信仰の欠如と即断しません。',(15,3):'約束が見えない時の嘆きは、教父説教で忍耐の試練として受容されました。本文では具体的な相続問題です。',(15,4):'実子の約束は救済史的に後のキリストへ広げて読まれましたが、まずアブラム家の継承という原義を保ちます。',(15,5):'星の比喩は教父文学で諸国民へ広がる信仰者と結ばれました。これは後代の普遍化で、最初の意味は子孫約束です。',(15,6):'パウロはローマ4章とガラテヤ3章でこの節を信仰と義の議論へ用います。創世記の物語的信頼と使徒的受容を区別して読みます。'}
LIT={(14,21):'メルキ・ツェデクの祝福直後にソドム王の提案を置き、二人の王の言葉を対照させます。',(14,22):'アブラムの誓いが20節の祝福語を受け、勝利と富の源を神へ結び直します。',(14,23):'「糸から履物のひもまで」という極小表現と「何一つ」の否定が、全面的な辞退を強調します。',(14,24):'「私には何も」と「彼らには分け前を」の対照が、自制と他者の権利を同時に示します。',(15,1):'「これらの出来事の後」で戦争物語を神の言葉の場面へ接続し、恐れ・盾・報いの三語で転換します。',(15,2):'神の大きな報いに対して「何をくださるのか」と問い、財産と後継者の問題を鋭く対照させます。',(15,3):'「与えてくださらなかった」と「家の者が相続する」を並べ、約束の遅延を法的現実へ落とし込みます。',(15,4):'「見よ、主の言葉」という再導入と二度の「相続する」が、否定から新しい約束へ移します。',(15,5):'外へ連れ出す動作、天を見る命令、数える課題が、抽象的約束を身体で見るしるしへ変えます。',(15,6):'短い二つの動詞が、神の約束に対する信頼と神の評価を結び、契約物語の要所を作ります。'}
DEV={(14,21):'助けた後に何を受け取るかは、行動の意味を左右します。人を利益の手段にせず、その自由と尊厳を先に考えます。',(14,22):'成果の源を誰に帰すかで、その後の生き方が変わります。自分を大きく見せる物語から距離を取ります。',(14,23):'受け取れるものを断る自由もあります。将来の支配や誤解を招く贈り物でないかを見極めます。',(14,24):'自分の節制を他者へ強制しません。自分は辞退しても、仲間の働きと正当な権利を尊重します。',(15,1):'大きな出来事の後には恐れが戻ることがあります。強がらず、守りと報いの源へ心を向けます。',(15,2):'信仰があっても、満たされない願いを言葉にできます。神の前で正直であることから祈りが始まります。',(15,3):'約束と現実の間で、自分なりの結論を急ぐことがあります。失望を隠さず、もう一度語りかけを待ちます。',(15,4):'神の応答はアブラムの代案を否定しつつ、具体的な未来を示しました。閉じた見通しだけを最終答えにしません。',(15,5):'視野が狭くなった時、外へ出て空を見るよう促されることがあります。数えきれない未来を今日の一歩で受け取ります。',(15,6):'信頼はすべてを理解した後の結論ではありません。まだ見えない約束へ身を委ねる一歩を大切にします。'}
STRUCT={(14,21):'メルキ・ツェデクの祝福と十分の一の場面を受け、ソドム王の直接話法で戦利品交渉へ転じます。「人々」と「財産」の対句が提案の範囲を区切ります。',(14,22):'王の提案に対する返答は、拒否の理由を先に誓いとして提示します。14:19の「天地の造り主」という称号を受け直し、勝利の帰属を明確にします。',(14,23):'「糸」から「履物のひも」までという両極表現に「何一つ」を重ね、辞退を全面化します。続く理由節が、問題は品物の量でなく成功物語の帰属だと示します。',(14,24):'全面辞退に「ただし」を添え、すでに消費した食糧と同盟者の分け前を例外として切り分けます。自分の選択と仲間の権利を区別して場面を閉じます。',(15,1):'「これらの出来事の後」が戦争物語を幻の場面へ接続します。「恐れるな」「盾」「報い」が、外的勝利の後に残る内的恐れへ順に応答します。',(15,2):'神の「大きな報い」に対し、アブラムは「何をくださるのか」と問い返します。抽象的な祝福を、子の不在と家の相続という具体的問題へ絞ります。',(15,3):'前節の問いを「あなたは子孫を与えなかった」と原因の形で言い直し、「だから家の者が相続する」と現実的な結論へ進めます。反復が訴えの切実さを強めます。',(15,4):'「見よ、主の言葉」が神の再応答を際立たせます。「この者ではない」と退けた後、「あなた自身から出る者」と肯定し、相続者を対照的に特定します。',(15,5):'神はアブラムを外へ連れ出し、見る・数えるという身体的行為へ導きます。数えきれない星が、言葉だけだった子孫の約束を目に見える比喩へ変えます。',(15,6):'長い対話の後、二つの短い動詞がアブラムの応答と神の評価を結びます。信頼と「義と認める」が簡潔に並び、次の契約儀礼への要所を作ります。'}
GRAM={(14,21):'命令形 תֶּן と קַח が並行し、前者の目的語 הַנֶּפֶשׁ は集合的に「人々」を指します。לִי／לָךְ の対照が返還先と取得者を明示します。',(14,22):'הֲרִימֹתִי は完了形ですが、手を上げる誓いの遂行を表します。לַיהוָה 以下が誓いの相手を示し、קֹנֵה は「所有者／造り主」と理解されます。',(14,23):'誓約文の אִם は省略された自己呪詛を背景に、強い否定として機能します。מִחוּט וְעַד שְׂרוֹךְ־נַעַל が最小物の範囲を作り、אֶקַּח が拒否対象を結びます。',(14,24):'בִּלְעָדַי と רַק が例外を二段階で限定します。אָֽכְלוּ は関係節の完了形、יִקְחוּ は同盟者に認める取得を表す未完了形です。',(15,1):'הָיָה דְבַר־יְהוָה は神の言葉の到来を告げる定型構文です。אַל־תִּירָא は禁止、אָנֹכִי מָגֵן לָךְ はコピュラを省いた名詞文です。',(15,2):'מַה־תִּתֶּן は未完了形で将来の贈与を問います。הוֹלֵךְ עֲרִירִי は分詞を用いた継続状態で、בֶן־מֶשֶׁק בֵּיתִי は難解な同格句です。',(15,3):'לֹא נָתַתָּה は完了形で現在までの不授与を述べ、וְהִנֵּה がその帰結を提示します。בֶן־בֵּיתִי は連語形で「私の家の子」を表します。',(15,4):'関係節 אֲשֶׁר יֵצֵא מִמֵּעֶיךָ が新しい相続者を定義し、独立代名詞 הוּא が主語を強調します。二度の יִירָשְׁךָ が否定と肯定を対応させます。',(15,5):'וַיּוֹצֵא は Hiphil で「連れ出す」、הַבֶּט と סְפֹר は命令形です。אִם־תּוּכַל は可能条件、כֹּה は星の多さを子孫へ結ぶ指示的な比較語です。',(15,6):'הֶאֱמִן は Hiphil 完了形で前置詞 בְּ を伴い「信頼する」を表します。וַיַּחְשְׁבֶהָ の女性単数接尾辞はその信頼を受け、主語は文脈上主と理解されます。'}

def details(c,v):
    w,l,p,s,i=key(c,v); ref=(c,v)
    return [('本文の骨格',STRUCT[ref]),('文法',GRAM[ref]),('ケティーブ／ケレー・本文伝承','狭義のケティーブ／ケレーは確認されません。古代訳・写本間の異読はK/Qと区別します。'),('ラビ・中世',RAB[ref]),('教父文学',PAT[ref]),('文献層と物語',LIT[ref]),('デボーショナルな受けとめ',DEV[ref])]

for c,v in REFS:(HTML/f'019-Genesis-{c}-{v}-r1.html').write_text(html_for(c,v),encoding='utf-8')

DIRECT={(15,1):('382010','438846'),(15,2):('382010','438847'),(15,3):('382010','438848'),(15,4):('382010','438850'),(15,6):('381985','438851')}
pt=json.load(open(BASE/'PocketTorah-Genesis.json',encoding='utf-8-sig'))['Tanach']['tanach']['book']['c']
counts=[len(pt[c-1]['v'][v-1]['w']) for c,v in REFS]; labels=[float(x) for x in (BASE/'lech-lecha-5.txt').read_text().strip().split(',')]
if sum(counts)!=len(labels):raise SystemExit(f'PocketTorah mismatch {sum(counts)} != {len(labels)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'Lech-Lecha-5.mp3')]))
log=subprocess.run(['ffmpeg','-nostdin','-i',str(BASE/'Lech-Lecha-5.mp3'),'-af','silencedetect=noise=-38dB:d=0.10','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip(map(float,re.findall(r'silence_start: ([0-9.]+)',log)),map(float,re.findall(r'silence_end: ([0-9.]+)',log))))
# Merge adjacent detector runs. PocketTorah's inter-verse label precedes the
# audible pause, so the shared cut must be the pause midpoint, not label time.
merged=[]
for a,b in sil:
    if merged and a-merged[-1][1] <= 0.035:
        merged[-1]=(merged[-1][0],b)
    else:
        merged.append((a,b))
sil=merged
idx=0;cuts=[0.0];methods=[]
for cnt in counts[:-1]:
    idx+=cnt;last,nxt=labels[idx-1],labels[idx]
    cand=[(a,b) for a,b in sil if a<=nxt+0.60 and b>=nxt-0.15 and b-a>=0.18]
    if cand:
        a,b=max(cand,key=lambda x:((x[1]-x[0]),(x[0]+x[1])/2));cut=(a+b)/2;method=f'low-volume midpoint {a:.6f}-{b:.6f}'
    else:
        cut=nxt;method='PocketTorah next-token onset (no qualifying pause)'
    cuts.append(cut);methods.append(method)
cuts.append(duration)
target_wps=0.793064;original_wps=sum(counts)/duration;atempo=target_wps/original_wps
for srcf,dst in [('Lech-Lecha-5.mp3','Lech-Lecha-5-original.mp3'),('lech-lecha-5.txt','lech-lecha-5-labels.txt')]:shutil.copy2(BASE/srcf,SOURCE/dst)
(SOURCE/'PocketTorah-Lech-Lecha-5-tokens.json').write_text(json.dumps([{'ref':f'Genesis {c}:{v}','words':pt[c-1]['v'][v-1]['w']} for c,v in REFS],ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for n,(c,v) in enumerate(REFS):
    start,end=cuts[n],cuts[n+1];rows.append((c,v,start,end,counts[n],methods[n] if n<len(methods) else 'end of source'))
    if (c,v) not in DIRECT:
        out=AUDIO/f'019-Genesis-{c}-{v}-study.mp3';tmp=out.with_suffix('.tmp.mp3')
        cmd=['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'Lech-Lecha-5.mp3'),'-filter:a',f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}','-codec:a','libmp3lame','-q:a','5',str(tmp)]
        for attempt in range(3):
            tmp.unlink(missing_ok=True);subprocess.run(cmd,check=True)
            pr=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(tmp)],capture_output=True,text=True)
            if pr.returncode==0 and pr.stdout.strip() and float(pr.stdout)>0.5:tmp.replace(out);break
        else:raise RuntimeError(f'audio split failed: {out}')
(OUT/'boundaries.tsv').write_text('reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n'+''.join(f'Genesis-{c}-{v}\t{s:.6f}\t{e:.6f}\t{n}\t{m}\n' for c,v,s,e,n,m in rows),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\tpockettorah_tokens\n'+''.join(f'Genesis-{c}-{v}\t{n}\n' for (c,v),n in zip(REFS,counts)),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tLech-Lecha\naliyah\t5\nrange\tGenesis 14:21-15:6\nprimary_sheets\thttps://www.sefaria.org/sheets/382010 ; https://www.sefaria.org/sheets/381985\nprimary_coverage\tGenesis 15:1-4,15:6\nfallback_coverage\tGenesis 14:21-24,15:5\nfallback_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-5.mp3\nfallback_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/lech-lecha-5.txt\nfallback_tokens\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')
ar=['reference\tmethod\tevidence\tactual_notion_audio']
for c,v in REFS:
    if (c,v) in DIRECT:sh,mid=DIRECT[(c,v)];ar.append(f'Genesis-{c}-{v}\tSefaria Full Verse Chanted\thttps://www.sefaria.org/sheets/{sh}\thttps://images.shulcloud.com/14396/{mid}.mp3')
    else:ar.append(f'Genesis-{c}-{v}\tPocketTorah physical split\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Lech-Lecha-5.mp3\thttps://raw.githubusercontent.com/theologia165/torah-audio-temp/main/019/audio/019-Genesis-{c}-{v}-study.mp3')
(OUT/'audio-map.tsv').write_text('\n'.join(ar)+'\n',encoding='utf-8')

intro='戦いに勝ったアブラムへ、ソドムの王は財産を差し出します。しかし彼は、自分を富ませたのがソドムの王だと言われないため、戦利品を受け取りません。ところが場面が変わると、神からの約束があっても「私には子がいない」と率直に訴えます。神は彼を外へ連れ出し、夜空の星を数えてみよと語り、子孫の未来を示されました。手に入る富を断る強さと、満たされない願いを隠さない弱さ。その両方を抱えたアブラムの信頼が描かれます。'
parts=[f'''<callout icon="📖" color="blue_bg">
\t**レフ・レハ｜第5アリヤー**　創世記14:21–15:6（10節）　pc:語にマウス / スマホ:語をタップ
\t{intro}
</callout>
<callout icon="א" color="gray_bg">
\t**ケティーブ／ケレー**：創世記14:21–15:6に、MorphHB/WLCで表示される狭義のケティーブ／ケレーはありません。古代訳・写本間の異読はK/Qとは区別します。
</callout>''']
for c,v in REFS:
    det='\n'.join('\t**'+h+'**：'+t for h,t in details(c,v))
    parts.append(f'''---
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
- [Sefaria Genesis 14:21–15:6](https://www.sefaria.org/Genesis.14.21-15.6)
- [Torah Chanting Helper: Genesis 15:1–4](https://www.sefaria.org/sheets/382010)
- [Torah Chanting Helper: Genesis 15:6–9](https://www.sefaria.org/sheets/381985)
- [PocketTorah Lech-Lecha-5 audio and token data](https://github.com/rneiss/PocketTorah)
- [Rashi on Genesis 14–15](https://www.sefaria.org/Rashi_on_Genesis.14)
- [Bereshit Rabbah 43–44](https://www.sefaria.org/Bereshit_Rabbah.43)
- [Romans 4](https://www.sefaria.org/Romans.4)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'verses':len(REFS),'labels':len(labels),'tokens':sum(counts),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
