import json, math, pathlib, re, struct, subprocess

BASE = pathlib.Path(__file__).resolve().parent
SRC = BASE / 'Lech-Lecha-4.mp3'
LAB = BASE / 'Lech-lecha-4.txt'
TOK = BASE / 'Genesis-pocket.json'

with open(TOK, encoding='utf-8') as f:
    pt = json.load(f)['Tanach']['tanach']['book']['c']
labels = [float(x) for x in LAB.read_text().strip().split(',') if x.strip()]
refs = [(14,v) for v in range(1,21)]
counts = [len(pt[c-1]['v'][v-1]['w']) for c,v in refs]
assert sum(counts) == len(labels)

# Map each PocketTorah token to its official word-onset label.
rows=[]; gi=0
for (c,v),cnt in zip(refs,counts):
    for wi,w in enumerate(pt[c-1]['v'][v-1]['w'],1):
        rows.append((gi,c,v,wi,labels[gi],w))
        gi += 1

# Boundaries after vv.17,18,19 based on cumulative PocketTorah token counts.
cum=[]; s=0
for v,cnt in enumerate(counts,1):
    s += cnt
    cum.append(s)
nominals = {17: labels[cum[16]] if cum[16] < len(labels) else None,
            18: labels[cum[17]] if cum[17] < len(labels) else None,
            19: labels[cum[18]] if cum[18] < len(labels) else None}

# Decode just the relevant tail to 16 kHz mono signed 16-bit PCM.
region_start=195.0; region_end=242.0; rate=16000
pcm = subprocess.check_output([
    'ffmpeg','-nostdin','-hide_banner','-loglevel','error','-ss',str(region_start),
    '-to',str(region_end),'-i',str(SRC),'-ac','1','-ar',str(rate),'-f','s16le','-'
])
samples = struct.unpack('<%dh' % (len(pcm)//2), pcm)

def rms_at(t, win=0.030):
    a=max(0,int((t-region_start-win/2)*rate)); b=min(len(samples),int((t-region_start+win/2)*rate))
    if b<=a: return 1e9
    ss=0
    for x in samples[a:b]: ss += x*x
    return math.sqrt(ss/(b-a))

def dbfs(r):
    return -120.0 if r <= 0 else 20*math.log10(r/32768.0)

out=['after_verse\tnominal\tcandidate_time\tdbfs30ms\tdistance\tnearby_label_index\tlabel_ref\tlabel_word\tlabel_text\n']
for av,nom in nominals.items():
    # Search local RMS minima at 5 ms resolution in ±2.5 s.
    cand=[]
    step=0.005
    n=int(5.0/step)+1
    vals=[]
    for i in range(n):
        t=nom-2.5+i*step
        vals.append((t,dbfs(rms_at(t))))
    for i in range(1,len(vals)-1):
        if vals[i][1] <= vals[i-1][1] and vals[i][1] <= vals[i+1][1]:
            cand.append(vals[i])
    cand=sorted(cand,key=lambda z:(z[1],abs(z[0]-nom)))[:30]
    for t,db in cand:
        nearest=min(rows,key=lambda r:abs(r[4]-t))
        out.append(f'{av}\t{nom:.6f}\t{t:.6f}\t{db:.3f}\t{t-nom:+.6f}\t{nearest[0]}\tGenesis-{nearest[1]}-{nearest[2]}\t{nearest[3]}\t{nearest[5]}\n')
(BASE/'boundary-audit-17-20.tsv').write_text(''.join(out),encoding='utf-8')

# Multi-threshold silencedetect audit in the same region.
sout=['threshold_db\tduration\tsilence_start\tsilence_end\tmidpoint\n']
for th in (-20,-24,-28,-30,-32,-34,-36,-38,-40,-42):
    for dur in (0.02,0.04,0.06,0.10):
        p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-ss',str(region_start),'-to',str(region_end),'-i',str(SRC),
                          '-af',f'silencedetect=noise={th}dB:d={dur}','-f','null','-'],capture_output=True,text=True)
        starts=[]
        for line in p.stderr.splitlines():
            m=re.search(r'silence_start: ([0-9.]+)',line)
            if m: starts.append(float(m.group(1))+region_start)
            m=re.search(r'silence_end: ([0-9.]+)',line)
            if m and starts:
                e=float(m.group(1))+region_start; a=starts.pop(0)
                if 199.0 <= (a+e)/2 <= 241.0:
                    sout.append(f'{th}\t{dur:.2f}\t{a:.6f}\t{e:.6f}\t{(a+e)/2:.6f}\n')
(BASE/'silence-audit-17-20.tsv').write_text(''.join(sout),encoding='utf-8')

# Explicit label context around vv17-20.
lout=['global_index\treference\tverse_word\ttime\tword\n']
for gi,c,v,wi,t,w in rows:
    if v>=16:
        lout.append(f'{gi}\tGenesis-{c}-{v}\t{wi}\t{t:.6f}\t{w}\n')
(BASE/'label-context-16-20.tsv').write_text(''.join(lout),encoding='utf-8')
print(json.dumps({'nominals':nominals,'counts17_20':counts[16:20]},ensure_ascii=False))
