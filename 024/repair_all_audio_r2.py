#!/usr/bin/env python3
import json, re, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "Vayera-3.mp3"
TOKENS = ROOT / "source" / "PocketTorah-Vayera-3-tokens.json"
LABELS = ROOT / "Vayera-3.txt"
OUT = ROOT / "audio"
NORMAL = ROOT / "audio-normal"
OUT.mkdir(exist_ok=True)
NORMAL.mkdir(exist_ok=True)
ATEMPO = 0.739931


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def duration(path):
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    return float(p.stdout.strip())


verses = json.loads(TOKENS.read_text(encoding="utf-8"))
labels = [float(x) for x in LABELS.read_text(encoding="utf-8").strip().split(",") if x.strip()]
counts = [len(v["words"]) for v in verses]
assert len(verses) == 20, len(verses)
assert sum(counts) == len(labels), (sum(counts), len(labels))

first_idx=[]
i=0
for c in counts:
    first_idx.append(i)
    i += c

# 19:1 and 19:2 were confirmed good by listening, so preserve those two boundaries.
# From the end of 19:3 onward, do NOT cut at a silence midpoint: that can truncate
# the release/tail of the final Hebrew word. Instead cut only 25 ms before the
# first-token onset of the next verse. This maximizes retention of the final word
# while still preventing the next verse's first word from entering the prior clip.
cuts=[0.0, 17.618481, 37.178655]
rows=[]

# audit rows for the two preserved boundaries
for vi, cut in [(0, cuts[1]), (1, cuts[2])]:
    last_idx = first_idx[vi] + counts[vi] - 1
    next_idx = first_idx[vi+1]
    rows.append((verses[vi]["ref"], labels[last_idx], labels[next_idx], cut, "preserved after listening check"))

# boundary after verses 3..19
for vi in range(2, len(verses)-1):
    last_idx = first_idx[vi] + counts[vi] - 1
    next_idx = first_idx[vi+1]
    last_onset = labels[last_idx]
    next_onset = labels[next_idx]
    cut = next_onset - 0.025
    assert cut > last_onset, (vi+1, last_onset, cut, next_onset)
    cuts.append(cut)
    rows.append((verses[vi]["ref"], last_onset, next_onset, cut, "next-verse first-token onset minus 25 ms"))

src_dur = duration(SRC)
cuts.append(src_dur)
assert len(cuts) == 21
assert all(cuts[i] < cuts[i+1] for i in range(20))

for vi,v in enumerate(verses):
    ref = v["ref"]
    chap,verse = map(int, re.search(r"Genesis (\d+):(\d+)", ref).groups())
    start,end = cuts[vi],cuts[vi+1]
    normal = NORMAL / f"024-Genesis-{chap}-{verse}-r3.mp3"
    study = OUT / f"024-Genesis-{chap}-{verse}-r3-study.mp3"
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(SRC),"-ss",f"{start:.6f}","-to",f"{end:.6f}","-vn","-ac","1","-codec:a","libmp3lame","-q:a","3",str(normal)])
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(normal),"-filter:a",f"atempo={ATEMPO:.6f}","-codec:a","libmp3lame","-q:a","3",str(study)])
    assert duration(normal) > 0.20
    assert duration(study) > duration(normal)

with (ROOT/"boundaries-r3.tsv").open("w",encoding="utf-8") as f:
    f.write("reference\tstart\tend\tpockettorah_tokens\tlast_token_onset\tnext_verse_onset\tboundary_basis\n")
    for vi,v in enumerate(verses):
        if vi < len(verses)-1:
            last_idx = first_idx[vi]+counts[vi]-1
            next_idx = first_idx[vi+1]
            lo, no = labels[last_idx], labels[next_idx]
            basis = rows[vi][4]
        else:
            lo = labels[first_idx[vi]+counts[vi]-1]
            no = src_dur
            basis = "end of source"
        ref_key = v['ref'].replace(' ','-').replace(':','-')
        f.write(f"{ref_key}\t{cuts[vi]:.6f}\t{cuts[vi+1]:.6f}\t{counts[vi]}\t{lo:.6f}\t{no:.6f}\t{basis}\n")

for vi in range(19):
    last_idx=first_idx[vi]+counts[vi]-1
    next_idx=first_idx[vi+1]
    assert labels[last_idx] < cuts[vi+1] < labels[next_idx], (vi+1, labels[last_idx], cuts[vi+1], labels[next_idx])

print(f"source_duration={src_dur:.6f}")
print(f"labels={len(labels)} tokens={sum(counts)} verses={len(verses)}")
print("19:1 and 19:2 preserved; 19:3 onward uses next-verse onset minus 25 ms")
for r in rows[2:6]: print(r)
print("PASS: all 19 boundaries lie after the previous final-token onset and before the next first-token onset")
