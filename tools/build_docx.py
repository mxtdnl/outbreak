#!/usr/bin/env python3
"""Build Word (.docx) versions of the three guides in docs/ into docs/docx/.

Usage:  python3 tools/build_docx.py
Needs:  pandoc (2.x or 3.x) and Pillow.

The markdown guides are the source of truth. This script converts them for
readers who need Word files: glossary anchors become Word bookmarks, links
between guides point at the .docx files, and screenshots are sized to fit the
page.
"""
import os, re, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS  = os.path.join(ROOT, 'docs')
OUT   = os.path.join(DOCS, 'docx')
GUIDES = ['USER_GUIDE', 'FACILITATOR_GUIDE', 'TECHNICAL_GUIDE']
MAX_W_IN = 6.3          # usable width on A4 with 1in margins (~6.27in)
PX_PER_IN = 192         # screenshots are captured at 2x device pixels (96 dpi x 2)

def reference_docx(tmp):
    """Pandoc's default reference doc, adjusted: A4, Calibri, bordered tables."""
    ref = os.path.join(tmp, 'ref.docx')
    with open(ref, 'wb') as fh:
        fh.write(subprocess.check_output(['pandoc', '--print-default-data-file', 'reference.docx']))
    d = os.path.join(tmp, 'ref'); zipfile.ZipFile(ref).extractall(d)
    sp = os.path.join(d, 'word', 'styles.xml'); st = open(sp, encoding='utf-8').read()
    borders = ('<w:tblBorders>' + ''.join(
        f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="A0A8B0"/>'
        for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')) + '</w:tblBorders>')
    # Schema order inside tblPr is tblInd, tblBorders, ..., tblCellMar, so borders go straight after tblInd.
    st, n = re.subn(r'(<w:style\b[^>]*w:styleId="Table"[^>]*>.*?<w:tblPr>.*?<w:tblInd\b[^>]*/>)', r'\1' + borders, st, count=1, flags=re.S)
    if not n: sys.exit('could not find the Table style in the reference docx')
    st = st.replace('w:ascii="Cambria"', 'w:ascii="Calibri"').replace('w:hAnsi="Cambria"', 'w:hAnsi="Calibri"')
    open(sp, 'w', encoding='utf-8').write(st)
    dp = os.path.join(d, 'word', 'document.xml'); doc = open(dp, encoding='utf-8').read()
    doc = re.sub(r'<w:pgSz[^>]*/>', '<w:pgSz w:w="11906" w:h="16838"/>', doc)
    doc = re.sub(r'<w:pgMar[^>]*/>', '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
                 'w:header="708" w:footer="708" w:gutter="0"/>', doc)
    open(dp, 'w', encoding='utf-8').write(doc)
    os.remove(ref)
    with zipfile.ZipFile(ref, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(d):
            for f in files:
                full = os.path.join(base, f); z.write(full, os.path.relpath(full, d))
    return ref

def image_width(rel):
    w = Image.open(os.path.join(DOCS, rel)).size[0]
    # Full-screen JPEGs were downscaled to 2000px from a wider capture; treat them as full width.
    inches = MAX_W_IN if rel.endswith('.jpg') else min(MAX_W_IN, w / PX_PER_IN)
    return f'{inches:.2f}in'

def prepare(md):
    md = re.sub(r'\A# [^\n]*\n+', '', md)                                     # title comes from metadata instead
    # GitHub renders a list straight after a paragraph; pandoc needs a blank line first.
    md = re.sub(r'(?m)^((?![ \t]*([-*]|\d+\.) )(?!\|)(?!>)\S[^\n]*)\n([ \t]*(?:[-*]|\d+\.) )', r'\1\n\n\3', md)
    md = re.sub(r'<a id="([^"]+)"></a>', r'[]{#\1}', md)                       # glossary anchors -> bookmarks
    md = re.sub(r'\]\((USER_GUIDE|FACILITATOR_GUIDE|TECHNICAL_GUIDE)\.md', r'](\1.docx', md)   # cross-guide links
    md = re.sub(r'!\[([^\]]*)\]\((images/[^)]+)\)', lambda m: f'![{m.group(1)}]({m.group(2)}){{width={image_width(m.group(2))}}}', md)
    return md

def finalise(path):
    """Declare image types by extension and drop folder entries from the ZIP.

    Pandoc declares each image with a per-file Override, which the format allows,
    but some consumers expect a per-extension Default as well.
    """
    src = zipfile.ZipFile(path); items = [(i, src.read(i)) for i in src.infolist() if not i.filename.endswith('/')]; src.close()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, data in items:
            if info.filename == '[Content_Types].xml':
                ct = data.decode('utf-8')
                for ext, mime in (('png', 'image/png'), ('jpg', 'image/jpeg'), ('jpeg', 'image/jpeg')):
                    if f'Extension="{ext}"' not in ct:
                        ct = ct.replace('<Default ', f'<Default Extension="{ext}" ContentType="{mime}" /><Default ', 1)
                data = ct.encode('utf-8')
            z.writestr(info, data)

def check_links(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    marks = set(re.findall(r'<w:bookmarkStart[^>]*w:name="([^"]+)"', x))
    anchors = re.findall(r'<w:hyperlink[^>]*w:anchor="([^"]+)"', x)
    missing = sorted(set(a for a in anchors if a not in marks))
    return len(anchors), missing

def main():
    if not shutil.which('pandoc'): sys.exit('pandoc not found')
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ref = reference_docx(tmp)
        ok = True
        for g in GUIDES:
            src = os.path.join(tmp, g + '.md')
            open(src, 'w', encoding='utf-8').write(prepare(open(os.path.join(DOCS, g + '.md'), encoding='utf-8').read()))
            out = os.path.join(OUT, g + '.docx')
            subprocess.check_call(['pandoc', src, '-o', out, '--reference-doc', ref, '--resource-path', DOCS,
                                   '-f', 'markdown+gfm_auto_identifiers+pipe_tables+raw_html-implicit_figures-tex_math_dollars-subscript-superscript',
                                   '--metadata', 'title=' + {'USER_GUIDE': 'OUTBREAK — User Guide',
                                                            'FACILITATOR_GUIDE': 'OUTBREAK — Facilitator Guide',
                                                            'TECHNICAL_GUIDE': 'OUTBREAK — Technical Guide'}[g]])
            finalise(out)
            n, missing = check_links(out)
            print(f'{g}.docx  internal links: {n}  unresolved: {len(missing)} {missing[:10]}')
            ok &= not missing
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
