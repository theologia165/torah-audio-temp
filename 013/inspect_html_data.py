import urllib.request, xml.etree.ElementTree as ET, pathlib
NS={'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
xml=urllib.request.urlopen('https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml').read()
root=ET.fromstring(xml)
out=['reference\tindex\tword\tlemma\tmorph\n']
for v in range(2,33):
    verse=root.find(f".//o:verse[@osisID='Gen.10.{v}']",NS)
    for i,w in enumerate(verse.findall('o:w',NS),1):
        word=(w.text or '').replace('\t',' ').replace('\n',' ')
        out.append(f"10:{v}\t{i}\t{word}\t{w.attrib.get('lemma','')}\t{w.attrib.get('morph','')}\n")
pathlib.Path('013/morph-audit.tsv').write_text(''.join(out),encoding='utf-8')
