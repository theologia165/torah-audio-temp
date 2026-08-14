import json, pathlib, subprocess

BASE = pathlib.Path(__file__).resolve().parent
AUDIO = BASE / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)

REFS = [(9, v) for v in range(18, 30)] + [(10, v) for v in range(1, 33)]
TARGET_WPS = 0.793064
STUDY_ATEMPO = 0.609926  # preserve the accepted 013 playback speed; this repair changes boundaries only

with open(BASE / "Genesis-pocket.json", encoding="utf-8") as f:
    data = json.load(f)
chapters = data["Tanach"]["tanach"]["book"]["c"]

def pocket_count(ch, v):
    verse = chapters[ch - 1]["v"][v - 1]
    words = verse.get("w", [])
    if isinstance(words, str):
        words = [words]
    return len(words)

counts = [(f"Genesis-{ch}-{v}", pocket_count(ch, v)) for ch, v in REFS]
labels = [float(x) for x in (BASE / "Noach-6.txt").read_text(encoding="utf-8").strip().split(",") if x.strip()]
word_total = sum(c for _, c in counts)
if len(labels) != word_total:
    raise SystemExit(f"PocketTorah label/token mismatch: labels={len(labels)} pocket_words={word_total}")

duration = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nk=1:nw=1", str(BASE / "Noach-6.mp3")
], text=True).strip())

idx = 0
bounds = []
for ref, count in counts:
    start = labels[idx]
    idx += count
    end = labels[idx] if idx < len(labels) else duration
    if end <= start:
        raise SystemExit(f"invalid boundary {ref}: {start}..{end}")
    bounds.append((ref, start, end, count))
    out = AUDIO / f"013-{ref}-study.mp3"
    af = f"atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={STUDY_ATEMPO:.6f}"
    subprocess.run([
        "ffmpeg", "-nostdin", "-y", "-loglevel", "error",
        "-i", str(BASE / "Noach-6.mp3"), "-filter:a", af,
        "-codec:a", "libmp3lame", "-q:a", "5", str(out)
    ], check=True)

if idx != len(labels):
    raise SystemExit(f"unused labels: consumed={idx} labels={len(labels)}")

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
    "verses": len(counts),
    "pocket_words": word_total,
    "labels": len(labels),
    "duration": duration,
    "study_atempo": STUDY_ATEMPO,
    "first_three": bounds[:3],
    "last": bounds[-1]
}, ensure_ascii=False))
