# 027 r2 verified-boundary audio

Source: PocketTorah `Vayera-6.mp3` (CC-BY-SA), exactly identified by the Sefaria Project `Vayera-6.json` mapping for Genesis 21:22–34.

r2 corrects r1's problem: official PocketTorah/Sefaria verse times sometimes begin inside the inter-verse pause and therefore produce long leading silence or can sit before the actual decay fully ends after MP3 decoding. For each of the 12 shared verse boundaries, r2 uses the actual source waveform's detected inter-verse silence and an individually selected cut near the pause end. Every adopted cut is strictly inside that actual silence. `boundaries-r2.tsv` records the official label time, actual pause, adopted cut, adjacent Hebrew words, and verification flags. All 13 files are then regenerated from the same locked shared boundaries and FULL AUDITed.
