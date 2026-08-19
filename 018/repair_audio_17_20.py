import pathlib, subprocess

BASE = pathlib.Path(__file__).resolve().parent
SRC = BASE / 'Lech-Lecha-4.mp3'
AUDIO = BASE / 'audio'
AUDIO.mkdir(parents=True, exist_ok=True)
ATEMPO = 0.673186

# Re-audited directly from the original PocketTorah Lech-Lecha-4 MP3.
# Each transition is the midpoint of the actual low-level inter-verse gap,
# not a PocketTorah word-label fallback.
BOUNDS = {
    17: (201.687000, 218.549550),
    18: (218.549550, 225.340300),
    19: (225.340300, 231.247500),
    20: (231.247500, 241.920000),
}
BASIS = {
    17: 'audited silence midpoint -20dB 217.896800-219.202300',
    18: 'audited silence midpoint -20dB 225.036600-225.644000',
    19: 'audited silence midpoint -20dB 230.951800-231.543200',
    20: 'end of source',
}
COUNTS = {17:20,18:11,19:9,20:11}

for v,(start,end) in BOUNDS.items():
    out = AUDIO / f'018-Genesis-14-{v}-study.mp3'
    af = f'atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={ATEMPO:.6f}'
    subprocess.run([
        'ffmpeg','-nostdin','-y','-loglevel','error','-i',str(SRC),
        '-filter:a',af,'-codec:a','libmp3lame','-q:a','5',str(out)
    ],check=True)
    dur=float(subprocess.check_output([
        'ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(out)
    ],text=True).strip())
    if dur <= 0.5:
        raise SystemExit(f'bad output duration: verse {v} {dur}')

# Patch only vv.17-20 in boundaries.tsv; preserve vv.1-16 unchanged.
p = BASE / 'boundaries.tsv'
lines = p.read_text(encoding='utf-8').splitlines()
out=[lines[0]]
for line in lines[1:]:
    ref=line.split('\t',1)[0]
    if ref.startswith('Genesis-14-'):
        v=int(ref.rsplit('-',1)[1])
        if v in BOUNDS:
            s,e=BOUNDS[v]
            out.append(f'Genesis-14-{v}\t{s:.6f}\t{e:.6f}\t{COUNTS[v]}\t{BASIS[v]}')
            continue
    out.append(line)
p.write_text('\n'.join(out)+'\n',encoding='utf-8')

(BASE/'boundary-repair-17-20.tsv').write_text(
    'reference\tstart\tend\tpockettorah_tokens\tboundary_basis\n' +
    ''.join(f'Genesis-14-{v}\t{s:.6f}\t{e:.6f}\t{COUNTS[v]}\t{BASIS[v]}\n' for v,(s,e) in BOUNDS.items()),
    encoding='utf-8'
)
print('repaired Genesis 14:17-20')
