import json, pathlib, subprocess, re

BASE = pathlib.Path(__file__).resolve().parent
AUDIO = BASE / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)

REFS = [(9, v) for v in range(18, 30)] + [(10, v) for v in range(1, 33)]
TARGET_WPS = 0.793064
STUDY_ATEMPO = 0.609926

with open(BASE / "Genesis-pocket.json", encoding="utf-8") as f:
    data = json.load(f)
chapters = data["Tanach"]["tanach"]["book"]["c"]

def pocket_words(ch, v):
    verse = chapters[ch - 1]["v"][v - 1]
    words = verse.get("w", [])
    if isinstance(words, str):
        words = [words]
    return words

counts = [(f"Genesis-{ch}-{v}", len(pocket_words(ch, v))) for ch, v in REFS]
labels = [float(x) for x in (BASE / "Noach-6.txt").read_text(encoding="utf-8").strip().split(",") if x.strip()]
word_total = sum(c for _, c in counts)
if len(labels) != word_total:
    raise SystemExit(f"PocketTorah label/token mismatch: labels={len(labels)} pocket_words={word_total}")

duration = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nk=1:nw=1", str(BASE / "Noach-6.mp3")
], text=True).strip())

# PocketTorah's own word/timestamp mapping. Its app uses each label as a word-onset
# cue. Keep this map as an audit trail.
map_lines = ["reference\tverse_word\tglobal_word\ttime\tword\n"]
gi = 0
for ch, v in REFS:
    ref = f"Genesis-{ch}-{v}"
    for vi, word in enumerate(pocket_words(ch, v), 1):
        map_lines.append(f"{ref}\t{vi}\t{gi}\t{labels[gi]:.6f}\t{word}\n")
        gi += 1
(BASE / "pocket-word-timestamps.tsv").write_text("".join(map_lines), encoding="utf-8")

# Nominal transitions from the first-word labels.
idx = 0
nominal = []
for ref, count in counts:
    start = labels[idx]
    idx += count
    end = labels[idx] if idx < len(labels) else duration
    nominal.append((ref, start, end, count))

# Detect quiet inter-verse gaps. Cutting exactly on a word-onset label can retain
# the tail of the previous verse or shave the attack of the next one. Therefore,
# whenever a quiet gap exists near the nominal transition, cut at its midpoint.
proc = subprocess.run([
    "ffmpeg", "-nostdin", "-hide_banner", "-i", str(BASE / "Noach-6.mp3"),
    "-af", "silencedetect=noise=-38dB:d=0.06", "-f", "null", "-"
], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
silences = []
ss = None
for line in proc.stderr.splitlines():
    m = re.search(r"silence_start: ([0-9.]+)", line)
    if m:
        ss = float(m.group(1))
    m = re.search(r"silence_end: ([0-9.]+)", line)
    if m and ss is not None:
        ee = float(m.group(1))
        silences.append((ss, ee, (ss + ee) / 2))
        ss = None

transitions = []
analysis = ["after_reference\tnominal_transition\tchosen_transition\tsilence_start\tsilence_end\tmethod\n"]
for i in range(len(nominal)-1):
    ref, _, t, _ = nominal[i]
    candidates = [s for s in silences if abs(s[2] - t) <= 1.25]
    if candidates:
        s = min(candidates, key=lambda x: abs(x[2] - t))
        chosen = s[2]
        method = "silence_mid"
        analysis.append(f"{ref}\t{t:.6f}\t{chosen:.6f}\t{s[0]:.6f}\t{s[1]:.6f}\t{method}\n")
    else:
        chosen = t
        method = "word_onset_fallback"
        analysis.append(f"{ref}\t{t:.6f}\t{chosen:.6f}\t\t\t{method}\n")
    transitions.append(chosen)
(BASE / "boundary-analysis.tsv").write_text("".join(analysis), encoding="utf-8")

# Build contiguous verse clips: first starts at 0, last ends at source duration.
bounds = []
for i, (ref, _, _, count) in enumerate(nominal):
    start = 0.0 if i == 0 else transitions[i-1]
    end = duration if i == len(nominal)-1 else transitions[i]
    if end <= start:
        raise SystemExit(f"invalid repaired boundary {ref}: {start}..{end}")
    bounds.append((ref, start, end, count))

for ref, start, end, count in bounds:
    out = AUDIO / f"013-{ref}-study.mp3"
    af = f"atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={STUDY_ATEMPO:.6f}"
    subprocess.run([
        "ffmpeg", "-nostdin", "-y", "-loglevel", "error",
        "-i", str(BASE / "Noach-6.mp3"), "-filter:a", af,
        "-codec:a", "libmp3lame", "-q:a", "5", str(out)
    ], check=True)

(BASE / "boundaries.tsv").write_text(
    "reference\tstart\tend\twords\n" +
    "".join(f"{r}\t{s:.6f}\t{e:.6f}\t{c}\n" for r, s, e, c in bounds),
    encoding="utf-8"
)
(BASE / "verse-word-counts.tsv").write_text(
    "reference\twords\n" + "".join(f"{r}\t{c}\n" for r, c in counts),
    encoding="utf-8"
)
original_wps = word_total / duration
(BASE / "source.tsv").write_text(
    "field\tvalue\n"
    "parasha\tNoach\n"
    "aliyah\t6\n"
    "range\tGenesis 9:18-10:32\n"
    "source_audio\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Noach-6.mp3\n"
    "source_labels\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/Noach-6.txt\n"
    "token_source\thttps://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/json/Genesis.json\n"
    "boundary_method\tPocketTorah word onsets + nearest inter-verse silence midpoint\n"
    f"study_atempo\t{STUDY_ATEMPO:.6f}\n"
    f"reference_wps\t{TARGET_WPS:.6f}\n"
    f"original_wps\t{original_wps:.6f}\n",
    encoding="utf-8"
)

print(json.dumps({
    "verses": len(bounds), "pocket_words": word_total, "labels": len(labels),
    "duration": duration, "study_atempo": STUDY_ATEMPO,
    "first_three": bounds[:3],
    "fallback_transitions": sum(1 for line in analysis if "word_onset_fallback" in line)
}, ensure_ascii=False))
