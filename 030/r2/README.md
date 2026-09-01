# 030 r2 speed-corrected study audio

Source for every file is the existing 030 r1 per-verse MP3. r1 boundaries are LOCKED and were not recalculated, trimmed, or moved.
Playback rate is calculated from the full 030 aliyah words-per-second against the accepted 026 study-speed target; it is not a fixed percentage.
Token counting reproduces the accepted 027 method: Cantillate/MAM text, HTML stripped, whitespace tokenization. The workflow first verifies that Genesis 21:22-34 still yields the historical 027 total of 138 tokens.
Leading silence is measured and logged after time stretching, but is not used to recut a locked verse boundary.
