#!/usr/bin/env python3
"""Link every glossary term in each guide to that guide's glossary entry.

Usage:  python3 tools/link_glossary.py [--check]
Re-runnable: existing glossary links and anchors are stripped and rebuilt, so
run it after any edit to a guide or a glossary. Each guide must end with a
"## N. Glossary" section whose rows are "| **Term** | Definition |".

Aliases are derived from each term name; OVR overrides them where the automatic
form is wrong or ambiguous (single letters, words with an everyday meaning that
differs from the glossary sense), and SKIP_CTX lists phrases never to link.
"""
import os, re, sys, collections
D=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'docs')+os.sep
ROW=re.compile(r'^\|\s*(?:<a id="[^"]+"></a>)?\*\*(.+?)\*\*\s*\|(.*)\|\s*$')

# Alias overrides: term -> list of aliases (replaces automatic derivation). [] = no aliases (anchor only).
OVR = {
 'Susceptible (S)':['Susceptible'], 'Exposed (E)':['Exposed'], 'Infectious (I)':['Infectious'],
 'Recovered / Removed (R)':['Recovered'],
 'R₀ (basic reproduction number)':['R₀','R0','basic reproduction number'],
 'Rₑ / Reff (effective reproduction number)':['Rₑ','Reff','effective reproduction number','effective R'],
 'R₀ (R-nought)':['R₀','R0','R-nought'], 'Rₑ (R-effective)':['Rₑ','R-effective','effective R'],
 'Unrounded (exact) value':['unrounded'], 'Index (0–100)':['index','indices'],
 'Logarithmic (log) scale / log10':['logarithmic scale','log scale','log10','logarithmic'],
 'Multiplier / factor':['multiplier'], 'Spread':[], 'Triggered (conditional) event':['triggered event','conditional event'],
 'Modifier (`mods`)':['modifier'], 'Severity (`sev`)':['severity'], 'Bank (vaccine doses)':['bank','banked'],
 'Lag / in arrears':['lag','in arrears'], 'Data attribute (`data-mode`, `data-view`)':['data attribute'],
 'Media query (`@media`)':['media query','@media'], 'Clipboard API / `execCommand`':['Clipboard API','execCommand'],
 'Cube root (cbrt)':['cube root','cbrt'], 'Σ / Π':[], 'dp':['dp'],
 'Cumulative (cum.)':['cumulative','cum.'], 'Capture / captured':['capture','captured'],
 'Capture / capture spread':['capture','captured','capture spread'],
 'Immune / immunity':['immune','immunity'], 'Satisfaction (Public Satisfaction)':['satisfaction','Public Satisfaction'],
 'Port of entry (POE)':['port of entry','port-of-entry','POE'], 'Port of entry':['port of entry','port-of-entry'],
 'Super-spreader':['super-spreader'], 'Super-spreader cluster':['super-spreader cluster','super-spreader'],
 'Composite score':['composite score','composite'], 'Hospital load':['hospital load','Hosp. Load'],
 'Seed':['seed','seeded'], 'Calibration':['calibration','calibrated','calibrate'],
 'Overflow':['overflow','overflowing','overflowed'], 'Clamp':['clamp','clamped'], 'Shielding':['shielding','shielded'],
 'Forecast':['forecast','forecasting','forecasted'], 'Lockdown':['lockdown'],
 'Clinically vulnerable':['clinically vulnerable'], 'Headless':['headless'],
 'Force of infection (λ)':['force of infection','λ'], 'β (transmission rate)':['β','transmission rate'],
 'σ (sigma)':['σ','sigma'], 'γ (gamma)':['γ','gamma'], 'Sub-step / dt':['sub-step','dt'],
 'IFR (infection fatality ratio)':['IFR','infection fatality ratio'],
 'RNG (random number generator)':['RNG','random number generator'], 'DOM (Document Object Model)':['DOM','Document Object Model'],
 'Canvas / Canvas 2D API':['Canvas 2D API','canvas'], 'HTML / CSS / JavaScript':['HTML','CSS','JavaScript'],
 'SEIR / SEIRD-S':['SEIRD-S','SEIR'], '`logIndex`':['logIndex'], 'Epidemic modelling':['epidemic modelling'],
 'Grade band':['grade band'], 'Scheduled event':['scheduled event'], 'Reference strategy':['reference strategy'],
}
CASE_SENSITIVE={'R0','Reff','POE','IFR','RNG','DOM','HTML','CSS','JSON','CSV','SEIR','SEIRD-S','dt','dp','cbrt','logIndex',
                'execCommand','localStorage','devicePixelRatio','mulberry32','Canvas 2D API','Clipboard API','Node.js','@media','sigma','gamma'}
NO_PLURAL={'R₀','R0','Rₑ','Reff','R-nought','R-effective','λ','β','σ','γ','dt','dp','cum.','POE','IFR','RNG','DOM','HTML','CSS','JSON','CSV',
           'SEIR','SEIRD-S','satisfaction','immunity','compliance','transmission','shielding','shielded','forecasting','forecasted',
           'overflowing','overflowed','unrounded','calibrated','calibrate','banked','captured','seeded','headless','cumulative',
           'endemic','deterministic','stochastic','sigma','gamma','logarithmic','JavaScript','Node.js','@media','log10','in arrears',
           'immune','infectious','susceptible','exposed','recovered','removed','pseudo-random','non-substitutable','clinically vulnerable',
           'index','indices','effective R','Public Satisfaction','Hosp. Load','mulberry32','localStorage','devicePixelRatio','execCommand','logIndex','cbrt'}
# per-file contexts that must not be linked (regex on the matched text's surrounding line)
SKIP_CTX = {'TECHNICAL_GUIDE.md':[r'index of peak', r'seeds the city', r'decision log', r'decision-log'],
            'FACILITATOR_GUIDE.md':[r'decision log', r'Decision Log', r'seeds the city'], 'USER_GUIDE.md':[r'decision log']}

GREEK={'β':'beta','σ':'sigma','γ':'gamma','λ':'lambda','Σ':'sum','Π':'product'}
def slug(t):
    for k,v in GREEK.items():
        if t.startswith(k): t=v+' '+t
    t=re.sub(r'\s*\([^)]*\)','',t).replace('`','')
    t=t.split(' / ')[0]
    t=t.replace('₀','0').replace('ₑ','e')
    return 'g-'+re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')

def auto_aliases(term):
    if term in OVR: return OVR[term]
    base=re.sub(r'\s*\([^)]*\)','',term).strip().replace('`','')
    return [a.strip() for a in base.split(' / ') if len(a.strip())>1]

def forms(a):
    out=[a]
    if a in NO_PLURAL or not re.match(r'^[A-Za-z][A-Za-z -]*[A-Za-z]$',a): return out
    if a.endswith('y') and not a.endswith(('ay','ey','oy')): out.append(a[:-1]+'ies')
    elif a.endswith(('s','x','ch','sh')): out.append(a+'es')
    else: out.append(a+'s')
    return out

def gloss_section(md):
    m=re.search(r'^## \d+\. Glossary\s*$', md, re.M); return m.start() if m else None

def parse_terms(md):
    g=gloss_section(md); terms=[]
    for line in md[g:].splitlines():
        mm=ROW.match(line)
        if mm and mm.group(1)!='Term': terms.append((mm.group(1), mm.group(2).strip()))
    return terms

def build_index(terms):
    sl=[slug(t) for t,_ in terms]
    dup=[x for x in set(sl) if sl.count(x)>1 or x=='g-']
    assert not dup, ('slug collision', dup)
    idx={}  # alias form (key) -> (slug, term)
    for t,_ in terms:
        for a in auto_aliases(t):
            for f in forms(a):
                k = f if f in CASE_SENSITIVE or a in CASE_SENSITIVE else f.lower()
                idx.setdefault(k,(slug(t),t))
    return idx

def make_regex(idx):
    alts=sorted(idx.keys(), key=len, reverse=True)
    parts=[]
    for a in alts:
        e=re.escape(a)
        cs = a in CASE_SENSITIVE or any(a==f for f in CASE_SENSITIVE)
        parts.append(e if cs else '(?i:'+e+')')
    return re.compile(r'(?<![\w\-/#])(?:'+'|'.join(parts)+r')(?![\w\-])')

PROT=re.compile(r'(!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\([^)]*\)|`[^`]+`|<[^>]+>|https?://\S+)')

def link_text(seg, rx, idx, target, self_slug, counts, ctx_skip, line):
    def rep(m):
        w=m.group(0); key = w if w in idx else w.lower()
        if key not in idx: return w
        sl,term=idx[key]
        if sl==self_slug: return w
        counts[term]+=1
        return f'[{w}]({target}#{sl})'
    return rx.sub(rep, seg)

def process(md, terms, fname, target=''):
    idx=build_index(terms); rx=make_regex(idx)
    counts=collections.Counter()
    g=gloss_section(md)
    out=[]; infence=False; pos=0
    ctx=SKIP_CTX.get(fname,[])
    for line in md.split('\n'):
        start=pos; pos+=len(line)+1
        if line.startswith('```'): infence=not infence; out.append(line); continue
        if infence or line.startswith('#') or re.match(r'^\|[\s\-|:]+\|\s*$',line) or line.startswith('!['):
            out.append(line); continue
        self_slug=None; head=''
        if g is not None and start>=g:
            mm=ROW.match(line)
            if mm and mm.group(1)!='Term':
                self_slug=slug(mm.group(1))
                cell_end=line.index('|',1)
                head='| <a id="'+self_slug+'"></a>**'+mm.group(1)+'** '; line=line[cell_end:]
        prot = PROT if not ctx else re.compile(PROT.pattern[:-1]+'|'+'|'.join(ctx)+')')
        pieces=prot.split(line); new=[]
        for i,pc in enumerate(pieces):
            if i%2==1:
                # code span exactly equal to an alias -> link it
                code=pc[1:-1] if pc.startswith('`') else None
                key=None if code is None else (code if code in idx else (code.lower() if code.lower() in idx else None))
                if key and idx[key][0]!=self_slug:
                    sl,term=idx[key]; counts[term]+=1; new.append(f'[{pc}]({target}#{sl})')
                else: new.append(pc)
            else:
                new.append(link_text(pc, rx, idx, target, self_slug, counts, ctx, line))
        out.append(head+''.join(new))
    return '\n'.join(out), counts

def strip(md):
    md=re.sub(r'\[([^\]]*)\]\(#g-[^)]*\)', r'\1', md)
    return re.sub(r'<a id="g-[^"]*"></a>', '', md)

if __name__=='__main__':
    mode='check' if '--check' in sys.argv else 'write'
    for f in ['USER_GUIDE.md','TECHNICAL_GUIDE.md','FACILITATOR_GUIDE.md']:
        md=strip(open(D+f).read())
        if gloss_section(md) is None: print(f,'no glossary'); continue
        new,c=process(md, parse_terms(md), f)
        print(f, sum(c.values()), 'links;', len(c),'terms used of', len(parse_terms(md)))
        unused=[t for t,_ in parse_terms(md) if t not in c]; print('  unused:', unused)
        if mode=='write': open(D+f,'w').write(new)
        elif new!=open(D+f).read(): print('  OUT OF DATE: run without --check'); sys.exit(1)
