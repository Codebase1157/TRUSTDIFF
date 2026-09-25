set -e
cd /home/claude/work
rm -rf sp && cp -r unpacked sp
python3 springer.py >/dev/null
python3 - <<'EOF'
p='/home/claude/work/sp/word/document.xml'; x=open(p,encoding='utf8').read()
old='<w:t xml:space="preserve"> and Section </w:t></w:r><w:r><w:rPr/><w:t xml:space="preserve">VII</w:t>'
new='<w:t xml:space="preserve"> and Sect. 7</w:t></w:r><w:r><w:rPr/><w:t xml:space="preserve"></w:t>'
open(p,'w',encoding='utf8').write(x.replace(old,new))
EOF
python3 content.py >/dev/null
python3 terminology.py
python3 final_fixes.py
python3 - <<'EOF'
import re, sys
sys.path.insert(0,'/home/claude/work')
from springer import _sub_in_text_nodes
p='/home/claude/work/sp/word/document.xml'; x=open(p,encoding='utf8').read()
def cap(t):
    t=re.sub(r'^(Fig\. \d+)\.(\s|$)', r'\1\2', t)
    t=re.sub(r'^(Table \d+)\.(\s|$)', r'\1\2', t)
    t=re.sub(r'^TABLE (\d+)\.(\s|$)', r'Table \1\2', t)
    return t
x,_=_sub_in_text_nodes(x,cap); open(p,'w',encoding='utf8').write(x)
EOF
cd sp && python3 - <<'EOF'
import re, glob
for f in glob.glob('word/*.xml'):
    x=open(f,encoding='utf8').read()
    if '<w:highlight' in x: open(f,'w',encoding='utf8').write(re.sub(r'<w:highlight[^>]*/>','',x))
# Springer sets headings left-aligned and bold; the IEEE template centres level 1
# in small caps and italicises levels 2 and 3.
f='word/styles.xml'; x=open(f,encoding='utf8').read()
SPEC={'Heading1':('24',), 'Heading2':('22',), 'Heading3':('20',)}
for sid,(sz,) in SPEC.items():
    m=re.search(r'(<w:style [^>]*w:styleId="%s".*?</w:style>)'%sid, x, re.S)
    s=m.group(1)
    s2=s.replace('<w:jc w:val="center"/>','<w:jc w:val="left"/>')
    s2=re.sub(r'<w:smallCaps[^>]*/>','',s2)
    s2=re.sub(r'<w:b w:val="0"/>','<w:b/>',s2)
    s2=re.sub(r'<w:i/>|<w:i w:val="(?:1|true|on)"\s*/>','<w:i w:val="0"/>',s2)
    s2=re.sub(r'<w:sz w:val="\d+"/>','<w:sz w:val="%s"/>'%sz,s2)
    x=x[:m.start(1)]+s2+x[m.end(1):]
open(f,'w',encoding='utf8').write(x)

f='word/header1.xml'; x=open(f,encoding='utf8').read()
m=re.search(r'<w:p>.*?</w:p>', x, re.S); raw=m.group(0)
ppr=re.search(r'<w:pPr>.*?</w:pPr>', raw, re.S)
rpr=re.search(r'<w:r>\s*(<w:rPr>.*?</w:rPr>)', raw, re.S)
rp=re.sub(r'<w:i/>|<w:smallCaps/>','', rpr.group(1)) if rpr else ''
new=(f'<w:p>{ppr.group(0) if ppr else ""}<w:r>{rp}<w:t xml:space="preserve">'
     'TRUST-Diff: partial-correspondence posterior diffusion</w:t></w:r></w:p>')
open(f,'w',encoding='utf8').write(x[:m.start()]+new+x[m.end():])
EOF
python3 - <<'EOF2'
import re as _re
p='/home/claude/work/sp/docProps/core.xml'; x=open(p,encoding='utf8').read()
x=_re.sub(r'<dc:title>.*?</dc:title>',
  '<dc:title>TRUST-Diff: structure-aware partial-correspondence posterior diffusion '
  'for unpaired reference-based hyperspectral image super-resolution</dc:title>', x, flags=_re.S)
x=_re.sub(r'<dc:creator>.*?</dc:creator>', '<dc:creator></dc:creator>', x, flags=_re.S)
open(p,'w',encoding='utf8').write(x)
EOF2
cd /home/claude/work/sp && rm -f ../SPRINGER.docx && zip -Xqr ../SPRINGER.docx .
