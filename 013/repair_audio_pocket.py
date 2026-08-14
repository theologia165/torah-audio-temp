import json, pathlib, subprocess, re

BASE = pathlib.Path(__file__).resolve().parent
AUDIO = BASE / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)

REFS = [(9, v) for v in range(18, 30)] + [(10, v) for v in range(1, 33)]
TARGET_WPS = 0.793064
STUDY_ATEMPO = 0.609926  # preserve the accepted 013 playback speed; this repair changes boundaries only

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

# Dump the exact PocketTorah word -> label mapping used by its player.
map_lines = ["reference\tverse_word\tglobal_word\ttime\tword\n"]
gi = 0
for ch, v in REFS:
    ref = f"Genesis-{ch}-{v}"
    for vi, word in enumerate(pocket_words(ch, v), 1):
        map_lines.append(f"{ref}\t{vi}\t{gi}\t{labels[gi]:.6f}\t{word}\n")
        gi += 1
(BASE / "pocket-word-timestamps.tsv").write_text("".join(map_lines), encoding="utf-8")

# Find actual quiet gaps around nominal verse transitions. Labels are word-onset
# markers for highlighting; a clean clip boundary should fall in the adjacent
# inter-verse pause rather than on a consonant onset.
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
        ee = float(m.group(1)); silences.append((ss, ee, (ss + ee) / 2)); ss = None

idx = 0
nominal = []
for ref, count in counts:
    start = labels[idx]
    idx += count
    end = labels[idx] if idx < len(labels) else duration
    nominal.append((ref, start, end, count))

analysis = ["after_reference\tnominal_transition\tsilence_start\tsilence_end\tsilence_mid\tdelta_mid\n"]
for i in range(len(nominal)-1):
    ref, _, t, _ = nominal[i]
    candidates = [s for s in silences if abs(s[2] - t) <= 1.25]
    if candidates:
        s = min(candidates, key=lambda x: abs(x[2] - t))
        analysis.append(f"{ref}\t{t:.6f}\t{s[0]:.6f}\t{s[1]:.6f}\t{s[2]:.6f}\t{s[2]-t:+.6f}\n")
    else:
        analysis.append(f"{ref}\t{t:.6f}\t\t\t\t\n")
(BASE / "boundary-analysis.tsv").write_text("".join(analysis), encoding="utf-8")

# For this diagnostic run, preserve the nominal clips; a subsequent verified
# repair will switch boundaries to the confirmed inter-verse pauses.
bounds = nominal
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
    f"study_atempo\t{STUDY_ATEMPO:.6f}\n"
    f"reference_wps\t{TARGET_WPS:.6f}\n"
    f"original_wps\t{original_wps:.6f}\n",
    encoding="utf-8"
)

print(json.dumps({
    "verses": len(counts), "pocket_words": word_total, "labels": len(labels),
    "duration": duration, "study_atempo": STUDY_ATEMPO,
    "first_three": bounds[:3], "silences": len(silences)
}, ensure_ascii=False))
