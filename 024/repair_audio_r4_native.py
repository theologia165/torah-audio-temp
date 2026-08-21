#!/usr/bin/env python3
import json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "Vayera-3.mp3"
LABELS = ROOT / "Vayera-3.txt"
GENESIS = ROOT / "Genesis-PocketTorah.json"
OUT = ROOT / "audio"
NORMAL = ROOT / "audio-normal"
OUT.mkdir(exist_ok=True)
NORMAL.mkdir(exist_ok=True)
ATEMPO = 0.739931


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def duration(path):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)]).stdout.strip())

# PocketTorah's OWN WLC JSON structure. Never substitute MorphHB/OSHB token counts here.
data = json.loads(GENESIS.read_text(encoding="utf-8"))
chapters = data["Tanach"]["tanach"]["book"]["c"]
chapter19 = chapters[18]["v"]
verses=[]
for n in range(1,21):
    words=chapter19[n-1]["w"]
    if isinstance(words,str): words=[words]
    verses.append({"ref":f"Genesis 19:{n}","words":words})

labels=[float(x) for x in LABELS.read_text(encoding="utf-8").strip().split(",") if x.strip()]
counts=[len(v["words"]) for v in verses]
assert sum(counts)==len(labels), f"PocketTorah native words {sum(counts)} != labels {len(labels)}"
first=[]; i=0
for c in counts:
    first.append(i); i+=c

(ROOT/"source").mkdir(exist_ok=True)
(ROOT/"source"/"PocketTorah-Genesis-19-native.json").write_text(json.dumps(verses,ensure_ascii=False,indent=2),encoding="utf-8")

srcdur=duration(SRC)
rows=[]
# Keep user-confirmed 19:1 r2, 19:2 r2, 19:3 r3 untouched.
# For 19:4 onward make each clip independently: 90ms pre-roll before its OWN first word,
# and end 35ms before the next verse's OWN first word. This removes inherited long gaps
# and prevents a previous verse's final word from being split into the next clip.
for vi in range(3,20):
    first_onset=labels[first[vi]]
    last_onset=labels[first[vi]+counts[vi]-1]
    start=max(0.0,first_onset-0.090)
    if vi<19:
        next_onset=labels[first[vi+1]]
        end=next_onset-0.035
    else:
        next_onset=srcdur
        end=srcdur
    assert start < first_onset <= last_onset < end <= next_onset+1e-6, (vi+1,start,first_onset,last_onset,end,next_onset)
    verse=vi+1
    normal=NORMAL/f"024-Genesis-19-{verse}-r4.mp3"
    study=OUT/f"024-Genesis-19-{verse}-r4-study.mp3"
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(SRC),"-ss",f"{start:.6f}","-to",f"{end:.6f}","-vn","-ac","1","-codec:a","libmp3lame","-q:a","3",str(normal)])
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(normal),"-filter:a",f"atempo={ATEMPO:.6f}","-codec:a","libmp3lame","-q:a","3",str(study)])
    rows.append((verse,counts[vi],first_onset,start,last_onset,next_onset,end,verses[vi]["words"][0],verses[vi]["words"][-1]))

with (ROOT/"boundaries-r4-native.tsv").open("w",encoding="utf-8") as f:
    f.write("reference\tpockettorah_words\tfirst_word_onset\tclip_start\tlast_word_onset\tnext_verse_onset\tclip_end\tfirst_word\tlast_word\n")
    for verse,c,fo,st,lo,no,en,fw,lw in rows:
        f.write(f"Genesis-19-{verse}\t{c}\t{fo:.6f}\t{st:.6f}\t{lo:.6f}\t{no:.6f}\t{en:.6f}\t{fw}\t{lw}\n")

print("PocketTorah native counts:",counts)
print("labels:",len(labels),"native words:",sum(counts),"source duration:",srcdur)
for row in rows: print(row)
print("PASS: 19:4-20 rebuilt from PocketTorah Genesis.json native w arrays; no MorphHB/OSHB boundary counts used")
# trigger native r4 after workflow installation
