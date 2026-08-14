import html, json, pathlib, re, subprocess, unicodedata
import xml.etree.ElementTree as ET

BASE = pathlib.Path(__file__).parent
OUT = BASE / "013"
HTML = OUT / "html"
AUDIO = OUT / "audio"
HTML.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)

NS = {'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
LEXNS = {'l':'http://openscriptures.github.com/morphhb/namespace'}
root = ET.parse(BASE/'Gen.xml').getroot()
lex_root = ET.parse(BASE/'HebrewStrong.xml').getroot()

LEMMA = {}
for entry in lex_root.findall('l:entry', LEXNS):
    eid = entry.attrib.get('id','')
    w = entry.find('l:w', LEXNS)
    if eid and w is not None and w.text:
        LEMMA[eid] = w.text.strip()

refs = [(9,v) for v in range(18,30)] + [(10,v) for v in range(1,33)]

J = {
"9:18":"箱舟から出たノアの息子たちは、セム、ハム、ヤフェトであった。ハムはカナンの父である。",
"9:19":"この三人がノアの息子たちであり、彼らから全地の人々が広がった。",
"9:20":"土を耕す人ノアは、ぶどう畑を植え始めた。",
"9:21":"彼はぶどう酒を飲んで酔い、自分の天幕の中で裸になった。",
"9:22":"カナンの父ハムは父の裸を見て、外にいる二人の兄弟に告げた。",
"9:23":"セムとヤフェトは衣を取り、二人の肩に掛け、後ろ向きに歩いて父の裸を覆った。顔を背けていたので、父の裸を見なかった。",
"9:24":"ノアは酔いから覚め、末の息子が自分にしたことを知った。",
"9:25":"彼は言った。『カナンは呪われよ。兄弟たちに仕える、しもべのしもべとなれ。』",
"9:26":"また言った。『セムの神YHWHはほめたたえられよ。カナンは彼らのしもべとなれ。』",
"9:27":"神がヤフェトを広げ、セムの天幕に住まわせてくださるように。カナンは彼らのしもべとなれ。",
"9:28":"ノアは洪水の後、三百五十年生きた。",
"9:29":"ノアの全生涯は九百五十年であった。そして彼は死んだ。",
"10:1":"これはノアの息子たち、セム、ハム、ヤフェトの系譜である。洪水の後、彼らに息子たちが生まれた。",
"10:2":"ヤフェトの息子たちは、ゴメル、マゴグ、マダイ、ヤワン、トバル、メシェク、ティラス。",
"10:3":"ゴメルの息子たちは、アシュケナズ、リファト、トガルマ。",
"10:4":"ヤワンの息子たちは、エリシャ、タルシシュ、キティム、ドダニム。",
"10:5":"これらから海沿いの諸国の民が、それぞれの地、言語、氏族、国民に分かれて広がった。",
"10:6":"ハムの息子たちは、クシュ、ミツライム、プト、カナン。",
"10:7":"クシュの息子たちは、セバ、ハビラ、サブタ、ラアマ、サブテカ。ラアマの息子たちは、シェバとデダン。",
"10:8":"クシュはニムロドを生んだ。彼は地上で最初に勇士となった。",
"10:9":"彼はYHWHの前に力ある狩人であった。それゆえ『YHWHの前に力ある狩人ニムロドのように』と言われる。",
"10:10":"彼の王国の初めは、シンアルの地のバベル、エレク、アッカド、カルネであった。",
"10:11":"その地からアシュルが出て、ニネベ、レホボト・イル、カラを建てた。",
"10:12":"また、ニネベとカラの間にレセンを建てた。これが大きな町である。",
"10:13":"ミツライムは、ルディム、アナミム、レハビム、ナフトヒムを生んだ。",
"10:14":"また、パトルシム、カスルヒム――そこからペリシテ人が出た――、カフトリムを生んだ。",
"10:15":"カナンは長子シドンとヘトを生んだ。",
"10:16":"また、エブス人、エモリ人、ギルガシ人、",
"10:17":"ヒビ人、アルキ人、シニ人、",
"10:18":"アルワド人、ツェマリ人、ハマト人を生んだ。その後、カナン人の諸氏族は散らされた。",
"10:19":"カナン人の領域は、シドンからゲラルへ向かってガザまで、ソドム、ゴモラ、アドマ、ツェボイムへ向かってレシャまでであった。",
"10:20":"これらが、氏族、言語、土地、国民ごとに見たハムの息子たちである。",
"10:21":"セムにも子が生まれた。彼はエベルのすべての子孫の父であり、兄ヤフェトの弟である。",
"10:22":"セムの息子たちは、エラム、アシュル、アルパクシャド、ルド、アラム。",
"10:23":"アラムの息子たちは、ウツ、フル、ゲテル、マシュ。",
"10:24":"アルパクシャドはシェラを生み、シェラはエベルを生んだ。",
"10:25":"エベルには二人の息子が生まれた。一人の名はペレグ。彼の時代に地が分けられたからである。弟の名はヨクタン。",
"10:26":"ヨクタンは、アルモダド、シェレフ、ハツァルマベト、イェラフを生んだ。",
"10:27":"また、ハドラム、ウザル、ディクラ、",
"10:28":"オバル、アビマエル、シェバ、",
"10:29":"オフィル、ハビラ、ヨバブを生んだ。これらはみなヨクタンの息子たちである。",
"10:30":"彼らの居住地は、メシャからセファルへ向かう東の山地に及んだ。",
"10:31":"これらが、氏族、言語、土地、国民ごとに見たセムの息子たちである。",
"10:32":"これらが、系譜と国民ごとに見たノアの息子たちの諸氏族である。洪水の後、これらから諸国民が地上に分かれ広がった。",
}

GLOSS = {
'1961':'ある／なる','1121':'息子','5146':'ノア','3315':'ヤフェト','8035':'セム','2526':'ハム','3667':'カナン',
'1':'父','776':'地','3605':'すべて','4480':'〜から','8392':'箱舟','3318':'出る','376':'人','127':'土地',
'5193':'植える','3754':'ぶどう畑','8354':'飲む','3196':'ぶどう酒','7937':'酔う','1540':'裸になる','168':'天幕',
'7200':'見る','6172':'裸','5046':'告げる','251':'兄弟','3947':'取る','8071':'衣','7760':'置く','7926':'肩',
'3212':'歩く','268':'後ろ','3680':'覆う','6440':'顔','3808':'〜ない','6974':'目覚める','3045':'知る',
'6213':'行う','6996':'小さい','559':'言う','779':'呪われる','5650':'しもべ','1288':'祝福される',
'3068':'YHWH','430':'神','6601':'広げる','7931':'住む','2421':'生きる','310':'後','3999':'洪水',
'7969':'三','3967':'百','8141':'年','2572':'五十','8672':'九','4191':'死ぬ','8435':'系譜',
'3205':'生む','2992':'人名','1471':'国民','3956':'言語','4940':'氏族','589':'島／沿岸','6504':'分ける',
'4428':'王','4467':'王国','7225':'初め','1368':'勇士','6718':'狩り','6440':'前','3651':'それゆえ',
'7121':'呼ぶ','1129':'建てる','5892':'町','1419':'大きい','1366':'境界','3427':'住む','2022':'山',
'6924':'東','8034':'名','259':'一','8147':'二','3117':'日','6385':'分割される','2088':'これ／この',
'428':'これら','1931':'彼／それ','1571':'また','834':'〜するところの','853':'目的格','996':'間','5704':'〜まで',
}

POS={'V':'動詞','N':'名詞','A':'形容詞・数詞','R':'前置詞','C':'接続詞','P':'代名詞','T':'小辞','D':'副詞'}
STEM={'q':'Qal','N':'Niphal','p':'Piel','P':'Pual','h':'Hiphil','H':'Hophal','t':'Hithpael','o':'Polel','r':'Hithpolel'}
CONJ={'p':'完了形','q':'完了形','i':'未完了形','w':'ワウ継続形','j':'指示・命令形','v':'分詞','r':'分詞','s':'分詞'}

def strong_id(s):
    parts=[p for p in re.split(r'[/ ]+',s or '') if re.search(r'\d',p)]
    if not parts: return ''
    m=re.search(r'(\d+)',parts[-1])
    return 'H'+m.group(1) if m else ''

def hebrew_lemma(s):
    sid=strong_id(s)
    if sid:
        return LEMMA.get(sid, 'מִלָּה')
    prefix_lemmas={'b':'בְּ','c':'וְ','d':'הַ','k':'כְּ','l':'לְ','m':'מִן','s':'שֶׁ'}
    return prefix_lemmas.get(s or '', 'מִלָּה')

def gloss_for(w):
    raw=w.attrib.get('lemma','')
    sid=strong_id(raw).lstrip('H')
    base=GLOSS.get(sid)
    if not base:
        morph=w.attrib.get('morph','')
        base='人名・地名' if 'Np' in morph else '語'
    pref=[]
    first=raw.split('/')[0]
    if raw.startswith('c/'): pref.append('そして')
    if '/l/' in '/'+raw+'/' or raw.startswith('l/'): pref.append('〜に')
    if '/b/' in '/'+raw+'/' or raw.startswith('b/'): pref.append('〜で')
    if '/m/' in '/'+raw+'/' or raw.startswith('m/'): pref.append('〜から')
    return ' '.join(pref+[base])

def morph_info(m):
    raw=(m or '').lstrip('H')
    parts=[p for p in raw.split('/') if p]
    lexical=[p for p in parts if not p.startswith('S')]
    core=lexical[-1] if lexical else (parts[-1] if parts else '')
    pos=POS.get(core[:1],'機能語')
    stem='—'; infl=raw or '—'
    if core.startswith('V'):
        stem=STEM.get(core[1:2],'—')
        form=core[2:3]
        infl=CONJ.get(form, '動詞形')+'（'+core+'）'
    elif core.startswith('N'):
        infl='名詞形（'+core+'）'
    elif core.startswith('A'):
        infl='形容詞・数詞形（'+core+'）'
    return pos,stem,infl

def html_for(ch,v):
    verse=root.find(f".//o:verse[@osisID='Gen.{ch}.{v}']",NS)
    pieces=[]
    for child in list(verse):
        tag=child.tag.split('}')[-1]
        if tag=='w':
            word=(child.text or '').replace('/','')
            lemma=hebrew_lemma(child.attrib.get('lemma',''))
            pos,stem,infl=morph_info(child.attrib.get('morph',''))
            gl=gloss_for(child)
            pieces.append(f'<span class="unit" tabindex="0"><span class="hw">{html.escape(word)}</span><span class="gl">{html.escape(gl)}</span><span class="pop"><b>lemma：<span class="lemma" dir="rtl">{html.escape(lemma)}</span></b><span>品詞：{html.escape(pos)}</span><span>語幹：{html.escape(stem)}</span><span>活用：{html.escape(infl)}</span></span></span>')
        elif tag=='seg':
            t=child.attrib.get('type','')
            if t=='x-maqqef': pieces.append('<span class="pun">־</span>')
            elif t=='x-sof-pasuq': pieces.append('<span class="pun">׃</span>')
            elif t=='x-paseq': pieces.append('<span class="pun">׀</span>')
    css='''<style>html,body{margin:0;background:#fff}body{padding:20px 8px 52px;font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Yu Gothic",sans-serif}.row{direction:rtl;display:flex;flex-wrap:wrap;gap:18px 13px;padding:0 8px;line-height:1.03;align-items:flex-start}.unit{position:relative;display:flex;flex-direction:column;align-items:center;min-width:34px;padding:1px 2px;outline:none}.hw{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px);direction:rtl}.gl{direction:ltr;font-size:12px;margin-top:5px;white-space:nowrap}.pun{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:clamp(38px,6.2vw,46px)}.pop{display:none;position:fixed;z-index:50;background:white;color:#171717;border:1px solid #ddd;border-radius:10px;padding:9px 11px;box-shadow:0 4px 18px #0002;font-size:12px;line-height:1.5;direction:ltr;max-width:min(260px,86vw)}.pop b{display:block;font-size:1em}.pop .lemma{font-family:"Noto Serif Hebrew","Times New Roman",serif;font-size:1.3em}.pop span{display:block}.pop b .lemma{display:inline}.unit:hover .pop,.unit:focus .pop{display:block}@media(max-width:600px){.hw,.pun{font-size:clamp(36px,11vw,44px)}.gl{font-size:12px}}</style>'''
    js='''<script>const units=[...document.querySelectorAll('.unit')];function hide(u){u.querySelector('.pop').style.display=''}function place(u){const p=u.querySelector('.pop');p.style.display='block';p.style.visibility='hidden';const r=u.getBoundingClientRect(),pr=p.getBoundingClientRect(),m=8;let x=r.left+r.width/2-pr.width/2;let y=r.bottom+6;if(y+pr.height>innerHeight-m)y=r.top-pr.height-6;x=Math.max(m,Math.min(innerWidth-pr.width-m,x));y=Math.max(m,Math.min(innerHeight-pr.height-m,y));p.style.left=x+'px';p.style.top=y+'px';p.style.visibility='visible'}units.forEach(u=>{u.addEventListener('mouseenter',()=>place(u));u.addEventListener('mouseleave',()=>hide(u));u.addEventListener('focus',()=>place(u));u.addEventListener('blur',()=>hide(u));u.addEventListener('click',e=>{e.stopPropagation();units.forEach(x=>{if(x!==u)hide(x)});place(u)})});document.addEventListener('click',()=>units.forEach(hide));addEventListener('resize',()=>units.forEach(hide));</script>'''
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+css+'<body><div class="row">'+''.join(pieces)+'</div>'+js+'</body></html>'

def key_word(ch,v):
    verse=root.find(f".//o:verse[@osisID='Gen.{ch}.{v}']",NS)
    ws=verse.findall('o:w',NS)
    verbal=next((w for w in ws if '/V' in w.attrib.get('morph','') or w.attrib.get('morph','').lstrip('H').startswith('V')),ws[0])
    word=(verbal.text or '').replace('/','')
    lemma=hebrew_lemma(verbal.attrib.get('lemma',''))
    pos,stem,infl=morph_info(verbal.attrib.get('morph',''))
    return word,lemma,stem,infl

def section(ch,v):
    if ch==9:
        return 'ノア一家の洪水後の物語を、家族関係・羞恥・祝福と呪いの転換として進める'
    if v<=5: return 'ヤフェト系諸民族を列挙し、土地・言語・氏族・国民への展開を示す'
    if v<=20: return 'ハム系諸民族と王国・都市・領域を示し、民族表に物語的地理を組み込む'
    return 'セム系諸民族を列挙し、エベルとペレグを経て諸国民の分岐を総括へ導く'

def rabbi(ch,v):
    special={
    '9:20':'ラシーは וַיָּחֶל を「俗化した／自らを損なった」と読む伝統を紹介し、救済後の最初の選択を倫理的に問います。語の原義には「始めた」もあり、説教的受容と語義を区別します。',
    '9:22':'『サンヘドリン』70aなどはハムの行為を本文以上に具体化する複数の伝承を保存します。原文が明記するのは「見た」「告げた」であり、後代の推測を本文事実と同一視しません。',
    '9:23':'ラシーは単数形 וַיִּקַּח に注目し、セムが先に衣を取ったと読みます。文法上の単数と二人の協働の関係から生まれた中世的受容です。',
    '9:24':'ラシーは「小さい息子」を年齢だけでなく、価値を小さくした者という方向でも説明します。誰を指すかは物語上の難点で、解釈の幅を残します。',
    '9:25':'ラビ伝統は、行為者として語られるハムではなくカナンが呪われる理由をさまざまに説明しました。本文の沈黙を埋める受容であり、現代の民族差別へ転用してはなりません。',
    '9:27':'ラシーは「セムの天幕」を、後のトーラーと礼拝の場に結びつけます。語呂合わせ יַפְתְּ／יֶפֶת と住む動詞の関係を、受容史と原義に分けて読みます。',
    '10:8':'ラシーはニムロドを神への反逆へ人々を引き込む人物として読みます。この像は נמרד と「反逆する」の語感を生かすミドラッシュ的受容で、本文はまず勇士としての登場を語ります。',
    '10:11':'ラシーはアシュルがニムロドの企てから離れて都市を築いたと読みます。主語をアシュルと取る伝統ですが、古代訳・現代訳にはニムロドを主語とする理解もあります。',
    '10:25':'ラシーは「地が分けられた」をバベルの塔の世代と結びつけます。ペレグの名と פלג「分ける」の語呂が、11章への橋として読まれます。',
    }
    k=f'{ch}:{v}'
    if k in special:return special[k]
    if ch==9:return '中世ユダヤ注解は、ノアの家族内で起きた行為と、その後の祝福・呪いの対応を注意深く読みます。本文が述べる範囲と、行為の動機を補う後代の伝承を区別する必要があります。'
    return 'ラシーやイブン・エズラなどの中世注解は、列挙された名を既知の地域・民族へ結びつけようとします。ただし同定には時代差があり、名前の対応を確定的な現代民族系譜へ直結させません。'

def textual(ch,v):
    if (ch,v)==(9,21): return '本節の אָהֳלֹה について、MorphHB/WLCはレニングラード写本に従い、BHSとのK/Q処理差を注記します。狭義K/Qの扱い自体が版によって異なる箇所であり、単なる翻訳差と混同しません。'
    if (ch,v)==(10,4): return '狭義K/Qはありません。MTの דֹדָנִים「ドダニム」に対し、七十人訳と歴代誌上1:7は「ロダニム」に相当する形を支持します。これは写本・古代訳の異読で、K/Qではありません。'
    if (ch,v)==(10,14): return '狭義K/Qはありません。「そこからペリシテ人が出た」の係り先は統語上議論され、エレミヤ47:4やアモス9:7との比較も必要です。これは本文解釈・伝承比較の問題です。'
    if (ch,v)==(10,24): return '狭義K/Qはありません。七十人訳系とルカ3:36にはアルパクシャドとシェラの間にカイナンを置く伝承があり、MTの短い系譜との差はK/Qではなく系譜本文の異読です。'
    return 'この節にMorphHB/WLCで表示される狭義K/Qはありません。綴字・固有名・語順を古代訳や他の系譜と比較する場合も、一般の本文伝承として区別します。'

def patristic(ch,v):
    if ch==9:return '教父的受容では、ノアの弱さと息子たちの応答が節制・羞恥の保護・家族倫理の教材となりました。クリュソストモスの創世記講解などの倫理的読解は、本文の歴史的意味そのものとは区別されます。'
    if v in (1,5,20,31,32): return 'アウグスティヌス『神の国』第16巻は民族表を、人類が一つの起源から多様な諸国民へ展開する歴史として受容します。後の教会普遍性への適用は、創世記本文の地理的系譜を踏まえた受容史です。'
    return '教父文学では民族表が使徒言行録2章の諸言語や全民族への福音の背景として読まれました。ただし個々の名を後代の国民へ機械的に同定するのではなく、本文の古代地理と受容史を分けます。'

def literary(ch,v):
    if ch==9:return '9:18–29は、契約定式中心の9:1–17から家族物語へ語り口が変わり、古典的資料批評では非祭司的伝承に結びつけられることがあります。最終形では洪水後にも人間の弱さが続くことを示します。'
    if v in (8,9,10,11,12,19,25,30): return '定型的な系譜の中に、人物評価・王国・都市・境界・語源説明が挿入されます。資料層を論じる際も、神名だけでなく語彙、反復、地理叙述、11章への接続を総合します。'
    return '氏族・言語・土地・国民という枠は祭司的系譜の秩序と調和します。最終形では単なる名簿ではなく、洪水後の人類が多様な世界へ展開する構造を担います。'

def devotional(ch,v):
    if ch==9:
        return '救いを経験した家族にも弱さと傷つけ合いは残ります。この節を他者を裁く材料にせず、尊厳を守る応答と、世代を越えて残る言葉の重さを静かに受け止めます。'
    return '名簿に見える一節にも、名を持つ人々と土地の記憶があります。違いを優劣へ変えず、多様な民が同じ洪水後の世界を分かち合うという視点を受け取ります。'

def detail(ch,v):
    word,lemma,stem,infl=key_word(ch,v)
    return [
      ('本文の骨格',f'本節は{section(ch,v)}役割を担います。前後の列挙または物語動作と結びつき、創世記9:18–10:32全体の「一つの家族から諸国民へ」という動きを進めます。'),
      ('文法',f'主要語 {word}（レンマ {lemma}）は語幹 {stem}、{infl}。固有名の並列では接続詞 וְ と目的語標識 אֵת、系譜の要約では前置詞句が構造を明確にします。'),
      ('ケティーブ／ケレー・本文伝承',textual(ch,v)),
      ('ラビ・中世',rabbi(ch,v)),
      ('教父文学',patristic(ch,v)),
      ('文献層と物語',literary(ch,v)),
      ('デボーショナルな受けとめ',devotional(ch,v)),
    ]

def simple(ch,v):
    word,lemma,stem,infl=key_word(ch,v)
    return f'{word} はレンマ {lemma}、{stem}の{infl}です。本節は{section(ch,v)}流れの一部です。'

# Create HTML and audio boundaries.
counts=[]
for ch,v in refs:
    ref=f'Genesis-{ch}-{v}'
    verse=root.find(f".//o:verse[@osisID='Gen.{ch}.{v}']",NS)
    counts.append((ref,len(verse.findall('o:w',NS))))
    (HTML/f'013-{ref}-r1.html').write_text(html_for(ch,v),encoding='utf-8')

labels=[float(x) for x in (BASE/'Noach-6.txt').read_text().strip().split(',')]
if len(labels)!=sum(c for _,c in counts):
    raise SystemExit(f'label/word mismatch {len(labels)} != {sum(c for _,c in counts)}')
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(BASE/'Noach-6.mp3')]))
target_wps=0.793064
original_wps=sum(c for _,c in counts)/duration
atempo=target_wps/original_wps
idx=0; bounds=[]
for ref,count in counts:
    start=labels[idx]
    idx+=count
    end=labels[idx] if idx<len(labels) else duration
    bounds.append((ref,start,end,count))
    out=AUDIO/f'013-{ref}-study.mp3'
    af=f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={atempo:.6f}'
    subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(BASE/'Noach-6.mp3'),'-filter:a',af,'-codec:a','libmp3lame','-q:a','5',str(out)],check=True)

(OUT/'boundaries.tsv').write_text('reference\tstart\tend\twords\n'+''.join(f'{r}\t{s:.6f}\t{e:.6f}\t{c}\n' for r,s,e,c in bounds),encoding='utf-8')
(OUT/'verse-word-counts.tsv').write_text('reference\twords\n'+''.join(f'{r}\t{c}\n' for r,c in counts),encoding='utf-8')
(OUT/'source.tsv').write_text(f'field\tvalue\nparasha\tNoach\naliyah\t6\nrange\tGenesis 9:18-10:32\nsource_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Noach-6.mp3\nsource_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/Noach-6.txt\nstudy_atempo\t{atempo:.6f}\nreference_wps\t{target_wps:.6f}\noriginal_wps\t{original_wps:.6f}\n',encoding='utf-8')

intro='ノアの三人の息子から、人類の諸氏族と国々が広がっていきます。その前に置かれるノアの酩酊と家族の応答は、洪水後の世界にも人間の弱さと尊厳を守る課題が残ることを示します。続く民族表は、名簿のようでいて、土地・言語・氏族・国民という多様性を一つの家族史の中に位置づけます。語形とテアミームをたどりながら、違いを優劣へ変えず、神の世界に広がる人々の記憶を読みます。'
parts=[f'''<callout icon="📖" color="blue_bg">\n\t**ノア｜第6アリヤー**　創世記9:18–10:32（44節）　pc:語にマウス / スマホ:語をタップ\n\t{intro}\n</callout>\n<callout icon="א" color="gray_bg">\n\t**ケティーブ／ケレー**：創世記9:18–10:32では、9:21の אָהֳלֹה についてWLC/MorphHBがレニングラード写本とBHSのK/Q処理差を注記します。10:4のドダニム／ロダニム、10:24のカイナン挿入など古代訳・並行系譜の異読は、狭義のK/Qとは区別します。\n</callout>''']
for ch,v in refs:
    k=f'{ch}:{v}'; ref=f'Genesis-{ch}-{v}'
    det='\n'.join('\t**'+h+'**：'+t for h,t in detail(ch,v))
    parts.append(f'''---\n### 創世記 {ch}:{v}\n{{{{AUDIO:{ref}}}}}\n**私訳**：{J[k]}\n**ヘブライ語**\n{{{{EMBED:{ref}}}}}\n**簡易な説明**：{simple(ch,v)}\n<details color="gray_bg">\n<summary>詳しい解説</summary>\n{det}\n</details>''')
parts.append('''---\n**本文データ帰属**：Open Scriptures Hebrew Bible / MorphHB（CC BY 4.0）。表示本文はMorphHB/WLCの子音・ティベリア式母音・テアミームを保持して使用しています。\n\n**主要出典**\n- [Open Scriptures Hebrew Bible / MorphHB](https://github.com/openscriptures/morphhb)\n- [Sefaria Genesis 9:18–10:32](https://www.sefaria.org/Genesis.9.18-10.32)\n- [PocketTorah Noach-6 audio data](https://github.com/rneiss/PocketTorah)\n- [Rashi on Genesis](https://www.sefaria.org/Rashi_on_Genesis)\n- [Augustine, City of God, Book XVI](https://www.newadvent.org/fathers/120116.htm)''')
(OUT/'page-template.md').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'refs':len(refs),'words':sum(c for _,c in counts),'labels':len(labels),'duration':duration,'atempo':atempo,'html':len(list(HTML.glob('*.html'))),'audio':len(list(AUDIO.glob('*.mp3'))),'intro_chars':len(intro)},ensure_ascii=False))
