#!/usr/bin/env python3 -I
"""v3: English text layer (Tajawal) + vector re-typeset Latin text + vector QR codes over the cleaned original.
usage: build_v3.py <cleaned.jpg> <measure.json> <out.html>"""
import sys, json, segno
BASE, MEAS, OUT = sys.argv[1:4]
M = json.load(open(MEAS))
W, H = 5906, 7874
els, defs = [], []
gid = [0]
FONT = 'Tajawal'

def grad(c1, c2):
    gid[0] += 1; i = f'g{gid[0]}'
    defs.append(f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    return f'url(#{i})'

def T(text, x, y, size, weight=500, fill='#000', anchor='middle', fit=None, exact=False):
    a = (f' data-fit="{fit}"' if fit else '') + (' data-exact="1"' if exact else '')
    els.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{fill}"{a}>{text}</text>')

def INK(inner, box, weight, fill):
    """text re-typeset as vector so that its ink fills exactly `box` (x0,y0,x1,y1) of the original raster text"""
    x0, y0, x1, y1 = box
    els.append(f'<text data-ink="{x0},{y0},{x1},{y1}" font-family="{FONT}" font-weight="{weight}" fill="{fill}" text-anchor="start">{inner}</text>')

GREEN_DK = '#246632'; GREEN_MID = '#66984b'; GOLD = '#b9962d'; PILL_G = '#2e8141'

# =============== original Latin text, re-typeset as crisp vector =====================
g_eng, g_inl = M['col_eng'], M['col_green_inline']
INK('Text to build a masjid', M['eng1'], 700, g_eng)
INK(f'Send 1 to 5112 to donate only <tspan fill="{g_inl}">12 Riyal</tspan> per day', M['eng2'], 700, g_eng)
INK('70,000,000', M['num70'], 800, M['col_70m'])
INK('0550881440', M['phone'], 500, M['col_phone'])
INK('store.msajidona.org.sa', [2770, 6190, 4032, 6320], 500, '#ffffff')
for (x0, y0, x1, y1), iban in zip(M['iban'], ['4680000 - 204608010888992', '90050000 - 68207788778000', '2815000 - 999124457130007', '932000000 - 2690448999940', '80100000 - 12300000977808']):
    INK(f'<tspan fill="{M["col_sa"]}">SA</tspan> {iban}', (x0, y0, x1, y1), 500, M['col_iban'])

# =============== QR codes as vector (same data as the originals) ======================
def qr(nm, data, ver, err, mask):
    qx, qy, qw, n = M['qr'][nm]
    q = segno.make(data, error=err, version=ver, mask=mask, micro=False, boost_error=False)
    mat = [list(r) for r in q.matrix]; assert len(mat) == n, (len(mat), n)
    s = qw / n
    def fin(r, c):
        return (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)
    d = ''.join(f'M{qx + c*s:.2f} {qy + r*s:.2f}h{s+.02:.2f}v{s+.02:.2f}h-{s+.02:.2f}z' for r in range(n) for c in range(n) if mat[r][c] and not fin(r, c))
    els.append(f'<path d="{d}" fill="#141414"/>')
    ring, inner = M['qrcol_' + nm]
    for (r0, c0) in [(0, 0), (0, n - 7), (n - 7, 0)]:
        fx, fy = qx + c0 * s, qy + r0 * s
        els.append(f'<path fill-rule="evenodd" fill="{ring}" d="M{fx:.2f} {fy:.2f}h{7*s:.2f}v{7*s:.2f}h-{7*s:.2f}z M{fx+s:.2f} {fy+s:.2f}v{5*s:.2f}h{5*s:.2f}v-{5*s:.2f}z"/>')
        els.append(f'<rect x="{fx+2*s:.2f}" y="{fy+2*s:.2f}" width="{3*s:.2f}" height="{3*s:.2f}" fill="{inner}"/>')
qr('bottom', 'https://store.msajidona.org.sa/p/48254?a=m', 3, 'm', 2)
qr('circle', 'https://msajidona-my.sharepoint.com/:b:/g/personal/marketing_msajidona_org/Eahbn6M9coROqdfzf2E2OA8B8txjdLvoPeEpcVMgsILEnw?e=yqhH92', 6, 'l', 4)

# =============== the English translation of the Arabic text ======================================
# header (right edge 3915 beside the emblem)
T('Roadside Masjids', 3915, 850, 300, 800, GREEN_DK, 'end', fit=2500, exact=True)
T('Care Association', 3915, 1135, 300, 800, GREEN_DK, 'end', fit=2500, exact=True)
T('Licensed by the National Center for Non-Profit Sector Development', 3915, 1295, 80, 700, '#b49428', 'end', fit=2500, exact=True)
T('Our Masjids', 4435, 1283, 60, 800, GREEN_DK, fit=330, exact=True)
T('on the Roads', 4435, 1358, 52, 800, GREEN_DK, fit=330, exact=True)
# label + title (the two lines are justified to one width, like the Arabic kashida lines)
T('Join us in', 4771, 2086, 130, 700, '#ffffff', fit=820)
T('Building &amp; Maintaining', 4247, 2428, 160, 800, grad('#caa939', '#bb9a2a'), fit=1845, exact=True)
T('Roadside Masjids', 4249, 2655, 220, 800, grad('#519544', '#478638'), fit=1860, exact=True)
# statistics
T('Every year, the number of', 1679, 3284, 140, 500, PILL_G, fit=1580)
T('worshippers exceeds', 1679, 3545, 140, 500, PILL_G, fit=1580)
T('men and women', 1655, 4252, 150, 500, GREEN_DK, fit=1000)
# SMS steps
T('By sending a text to', 4147, 3345, 96, 700, grad('#529544', '#478638'), fit=1040)
T('Send:', 4142, 3762, 110, 700, grad('#4f9241', '#458436'))
def row(cx, y0, lines, gap):
    for i, (txt, gold) in enumerate(lines):
        T(txt, cx, y0 + i * gap, 92 if gold else 84, 800 if gold else 500, GOLD if gold else GREEN_MID, fit=610)
row(4655, 3942, [('To donate', 0), ('12 Riyal', 1), ('monthly', 0), ('for yourself', 0)], 90)
row(3635, 3942, [('To donate', 0), ('1 Riyal', 1), ('daily to', 0), ('the Waqf', 0)], 90)
row(4635, 4478, [('To donate', 0), ('12 Riyal', 1), ('monthly for', 0), ('your parents', 0)], 90)
row(3612, 4532, [('To donate', 0), ('10 Riyal', 1), ('one time', 0)], 102)
gm = grad('#c8aa45', '#94762c')
T('Empty', 4036, 4578, 124, 800, gm, fit=440)
T('message', 4036, 4708, 124, 800, gm, fit=440)
# app circle
T('About', 2168, 5012, 88, 800, '#297238', fit=178, exact=True)
T('Us', 2168, 5100, 88, 800, '#297238')
# bank transfer heading + bank names (icons stay the original pictures)
T('Or transfer to the account', 3395, 4915, 112, 700, grad('#4f9241', '#468537'), 'start', fit=1900)
for (l1, l2, y, col) in [('Al Rajhi', 'Bank', 4999, '#2f449e'), ('Alinma', 'Bank', 5131, '#492621'), ('Bank', 'Albilad', 5262, '#ce1c2f')]:
    T(l1, 5118, y, 66, 800, col, 'start', fit=330)
    T(l2, 5118, y + 60, 66, 800, col, 'start', fit=330)
T('After donating, please send a message on WhatsApp', 4250, 5722, 70, 500, '#246531', fit=1420)
# donate
T('Donate easily and securely', 2706, 6522, 100, 800, GOLD, 'start', fit=1318, exact=True)

fonts = ''.join(f"@font-face{{font-family:{FONT};font-weight:{w};src:url(fonts/tajawal-latin-{w}-normal.woff2)}}" for w in (400, 500, 700, 800, 900))
js = '''<script>
(async()=>{
  for (const w of [400,500,700,800,900]) await document.fonts.load(w+' 100px Tajawal','Ag0');
  await document.fonts.ready;
  const cv=document.createElement('canvas').getContext('2d');
  // 1) text that must reproduce the ink box of the original raster text
  document.querySelectorAll('text[data-ink]').forEach(t=>{
    const [x0,y0,x1,y1]=t.dataset.ink.split(',').map(Number);
    cv.font=t.getAttribute('font-weight')+' 100px Tajawal';
    const txt=t.textContent, m=cv.measureText(txt);
    const asc=m.actualBoundingBoxAscent, desc=m.actualBoundingBoxDescent;
    const fs=100*(y1-y0)/(asc+desc);
    const left=m.actualBoundingBoxLeft*fs/100, inkw=(m.actualBoundingBoxLeft+m.actualBoundingBoxRight)*fs/100;
    const ls=(x1-x0-inkw)/([...txt].length-1);
    t.setAttribute('font-size',fs); t.setAttribute('letter-spacing',ls);
    t.setAttribute('x',x0+left); t.setAttribute('y',y1-desc*fs/100);
    t.dataset.ls=ls.toFixed(2); t.dataset.fs=fs.toFixed(1);
  });
  // 2) translated text: shrink (or exactly fit) to the available width
  document.querySelectorAll('text[data-fit]').forEach(t=>{
    const target=parseFloat(t.dataset.fit), fs=parseFloat(t.getAttribute('font-size')), w=t.getBBox().width;
    if(t.dataset.exact||w>target) t.setAttribute('font-size', fs*target/w);
  });
  document.body.dataset.ready='1';
})();
</script>'''
html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}@page{{size:150cm 200cm;margin:0}}'
        f'html,body{{margin:0;background:#fff}}svg{{display:block}}</style></head><body>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="150cm" height="200cm" text-rendering="geometricPrecision">'
        f'<defs>{"".join(defs)}</defs><image href="{BASE}" x="0" y="0" width="{W}" height="{H}"/>{"".join(els)}</svg>{js}</body></html>')
open(OUT, 'w').write(html)
print('ok', len(els), 'elements')
