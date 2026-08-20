#!/usr/bin/env python3
import json, re, subprocess, pathlib, statistics

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


def silences(start, end, threshold):
    # Analyze only the interval from the onset of the previous verse's final token
    # to the onset of the next verse's first token. Official labels are word onsets,
    # not cut positions.
    span = end - start
    p = subprocess.run([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info",
        "-ss", f"{start:.6f}", "-to", f"{end:.6f}", "-i", str(SRC),
        "-af", f"silencedetect=noise={threshold}dB:d=0.035", "-f", "null", "-"
    ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    txt = p.stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", txt)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", txt)]
    segs=[]
    for i,s in enumerate(starts):
        e = ends[i] if i < len(ends) else span
        if e > s:
            segs.append((s,e))
    return segs


def choose_boundary(last_onset, next_onset):
    span = next_onset - last_onset
    # The desired inter-verse pause is the LAST credible low-volume interval
    # before the next verse begins. Reject early dips inside the final word.
    for threshold in (-34, -31, -28, -25, -22, -20):
        segs = silences(last_onset, next_onset, threshold)
        credible=[]
        for s,e in segs:
            mid=(s+e)/2
            # Require the candidate to be in the latter 45% of the last-word→next-word interval,
            # or to reach the final 120 ms before the next onset.
            if mid >= span*0.55 or e >= span-0.12:
                credible.append((s,e))
        if credible:
            # Last interval is most likely the actual pause immediately before next verse.
            s,e = credible[-1]
            cut = last_onset + (s+e)/2
            # Never cross into next onset; never cut implausibly close to final-word onset.
            cut = min(cut, next_onset-0.015)
            cut = max(cut, last_onset + min(0.12, span*0.35))
            return cut, f"silence midpoint {threshold}dB {last_onset+s:.6f}-{last_onset+e:.6f}; last-token onset {last_onset:.6f}; next-verse onset {next_onset:.6f}"
    # Conservative fallback: official next-word onset minus a tiny safety margin.
    # This preserves the complete final word rather than cutting at an internal dip.
    cut = max(last_onset + span*0.80, next_onset-0.025)
    return cut, f"fallback next-verse onset minus 25ms; last-token onset {last_onset:.6f}; next-verse onset {next_onset:.6f}"


verses = json.loads(TOKENS.read_text(encoding="utf-8"))
labels = [float(x) for x in LABELS.read_text(encoding="utf-8").strip().split(",") if x.strip()]
counts = [len(v["words"]) for v in verses]
assert len(verses) == 20, len(verses)
assert sum(counts) == len(labels), (sum(counts), len(labels))

# Global label index for the first token of each verse.
first_idx=[]
i=0
for c in counts:
    first_idx.append(i)
    i += c

cuts=[0.0]
rows=[]
for vi in range(len(verses)-1):
    last_idx = first_idx[vi] + counts[vi] - 1
    next_idx = first_idx[vi+1]
    last_onset = labels[last_idx]
    next_onset = labels[next_idx]
    cut,basis = choose_boundary(last_onset,next_onset)
    cuts.append(cut)
    rows.append((verses[vi]["ref"], last_onset, next_onset, cut, basis))

src_dur = duration(SRC)
cuts.append(src_dur)
assert len(cuts) == 21
assert all(cuts[i] < cuts[i+1] for i in range(20))

# Build clips. Use accurate seek after input and re-encode. Every clip begins at 0:00.
for vi,v in enumerate(verses):
    ref = v["ref"]
    chap,verse = map(int, re.search(r"Genesis (\d+):(\d+)", ref).groups())
    start,end = cuts[vi],cuts[vi+1]
    normal = NORMAL / f"024-Genesis-{chap}-{verse}-r2.mp3"
    study = OUT / f"024-Genesis-{chap}-{verse}-r2-study.mp3"
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(SRC),"-ss",f"{start:.6f}","-to",f"{end:.6f}","-vn","-ac", "1", "-codec:a","libmp3lame","-q:a","3",str(normal)])
    run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-i",str(normal),"-filter:a",f"atempo={ATEMPO:.6f}","-codec:a","libmp3lame","-q:a","3",str(study)])
    assert duration(normal) > 0.20
    assert duration(study) > duration(normal)

# Detailed audit tables.
with (ROOT/"boundaries-r2.tsv").open("w",encoding="utf-8") as f:
    f.write("reference\tstart\tend\tpockettorah_tokens\tlast_token_onset\tnext_verse_onset\tboundary_basis\n")
    for vi,v in enumerate(verses):
        if vi < len(verses)-1:
            last_idx = first_idx[vi]+counts[vi]-1
            next_idx = first_idx[vi+1]
            _,_,_,_,basis = rows[vi]
            lo, no = labels[last_idx], labels[next_idx]
        else:
            lo = labels[first_idx[vi]+counts[vi]-1]
            no = src_dur
            basis = "end of source"
        f.write(f"{v['ref'].replace(' ','-')}\t{cuts[vi]:.6f}\t{cuts[vi+1]:.6f}\t{counts[vi]}\t{lo:.6f}\t{no:.6f}\t{basis}\n")

with (ROOT/"boundary-repair-r2.tsv").open("w",encoding="utf-8") as f:
    f.write("reference\tlast_token_onset\tnext_verse_onset\tnew_cut\told_cut_if_known\n")
    old={
    1:17.185900,2:36.001800,3:47.077350,4:62.011800,5:74.870100,6:86.020000,7:88.842400,8:111.088000,9:129.174500,10:142.048500,11:154.166500,12:166.252500,13:178.923000,14:196.434500,15:211.392000,16:231.232000,17:248.968000,18:252.612500,19:276.625000}
    for vi,(ref,lo,no,cut,basis) in enumerate(rows, start=1):
        f.write(f"{ref}\t{lo:.6f}\t{no:.6f}\t{cut:.6f}\t{old.get(vi,'')}\n")

# Human-auditable key checks: cuts must occur after the final token onset for every verse.
for vi in range(19):
    last_idx=first_idx[vi]+counts[vi]-1
    next_idx=first_idx[vi+1]
    assert labels[last_idx] < cuts[vi+1] < labels[next_idx], (vi+1, labels[last_idx], cuts[vi+1], labels[next_idx])

print(f"source_duration={src_dur:.6f}")
print(f"labels={len(labels)} tokens={sum(counts)} verses={len(verses)}")
print("first three corrected boundaries:")
for r in rows[:3]: print(r)
print("last three corrected boundaries:")
for r in rows[-3:]: print(r)
print("PASS: every shared boundary is after the previous verse's final-token onset and before the next verse's first-token onset")
