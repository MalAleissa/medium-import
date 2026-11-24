#!/usr/bin/env python3 -I
"""Builds the HTML (SVG overlay) that puts the English text on the cleaned original artwork.
usage: build_english.py <cleaned.jpg> <out.html>   (coordinates are full-res px of the 5906x7874 original)"""
import sys
BASE, OUT = sys.argv[1], sys.argv[2]
W, H = 5906, 7874
els, defs = [], []
gid = [0]

def grad(c1, c2):
    gid[0] += 1; i = f'g{gid[0]}'
    defs.append(f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    return f'url(#{i})'

def T(text, x, y, size, weight=600, fill='#000', anchor='middle', fit=None, exact=False, ls=0):
    """fit = max width (px); exact -> scale to exactly this width"""
    a = f' data-fit="{fit}"' if fit else ''
    a += ' data-exact="1"' if exact else ''
    ls_ = f' letter-spacing="{ls}"' if ls else ''
    els.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Changa" font-weight="{weight}" font-size="{size}" fill="{fill}"{ls_}{a}>{text}</text>')

GREEN_DK = '#246631'; GREEN_MID = '#66984b'; GOLD = '#b9962d'; PILL_G = '#2e8141'

# ---- header ------------------------------------------------------------------
T('Roadside Masjids', 3915, 850, 260, 700, GREEN_DK, 'end', fit=2290, exact=True)
T('Care Association', 3915, 1130, 260, 700, GREEN_DK, 'end', fit=2290, exact=True)
T('Licensed by the National Center for Non-Profit Sector Development', 3915, 1290, 70, 600, '#b49428', 'end', fit=2290, exact=True)
# emblem wordmark (inside the logo)
T('Our Masjids', 4435, 1283, 58, 700, GREEN_DK, fit=318, exact=True)
T('on the Roads', 4435, 1358, 50, 700, GREEN_DK, fit=318, exact=True)

# ---- label + title -------------------------------------------------------------
T('Join us in', 4771, 2085, 128, 600, '#ffffff', fit=820)
T('Building &amp; Maintaining', 4247, 2428, 160, 700, grad('#caa939', '#bb9a2a'), fit=1845, exact=True)
T('Roadside Masjids', 4249, 2655, 220, 700, grad('#519544', '#478638'), fit=1860, exact=True)

# ---- statistics --------------------------------------------------------------------
T('Every year, the number of', 1679, 3282, 130, 500, PILL_G, fit=1560)
T('worshippers exceeds', 1679, 3543, 130, 500, PILL_G, fit=1560)
T('men and women', 1655, 4252, 140, 500, GREEN_DK, fit=1000)

# ---- SMS section -------------------------------------------------------------------
T('By sending a text to', 4147, 3345, 90, 600, grad('#529544', '#478638'), fit=1020)
T('Send:', 4142, 3760, 104, 600, grad('#4f9241', '#458436'))
def row(cx, y0, lines, gap):
    for i, (txt, gold) in enumerate(lines):
        T(txt, cx, y0 + i * gap, 88 if gold else 80, 700 if gold else 600, GOLD if gold else GREEN_MID, fit=600)
row(4655, 3940, [('To donate', 0), ('12 Riyal', 1), ('monthly', 0), ('for yourself', 0)], 88)
row(3635, 3940, [('To donate', 0), ('1 Riyal', 1), ('daily to', 0), ('the Waqf', 0)], 88)
row(4635, 4475, [('To donate', 0), ('12 Riyal', 1), ('monthly for', 0), ('your parents', 0)], 88)
row(3612, 4530, [('To donate', 0), ('10 Riyal', 1), ('one time', 0)], 100)
gold_msg = grad('#c8aa45', '#94762c')
T('Empty', 4036, 4575, 120, 700, gold_msg, fit=430)
T('message', 4036, 4705, 120, 700, gold_msg, fit=430)

# ---- app circle -------------------------------------------------------------------------
T('About', 2168, 5012, 84, 700, '#297238', fit=178, exact=True)
T('Us', 2168, 5100, 84, 700, '#297238')

# ---- bank transfer ---------------------------------------------------------------------------
T('Or transfer to the account', 3395, 4915, 104, 600, grad('#4f9241', '#468537'), 'start', fit=1900)
for (l1, l2, y, col) in [('Al Rajhi', 'Bank', 4999, '#2f449e'), ('Alinma', 'Bank', 5131, '#492621'), ('Bank', 'Albilad', 5262, '#ce1c2f')]:
    T(l1, 5118, y, 62, 700, col, 'start', fit=330)
    T(l2, 5118, y + 58, 62, 700, col, 'start', fit=330)
T('After donating, please send a message on WhatsApp', 4250, 5724, 64, 500, '#246531', fit=1420)

# ---- donate -------------------------------------------------------------------------------------
T('Donate easily and securely', 2706, 6522, 100, 700, GOLD, 'start', fit=1318, exact=True)

fonts = ''.join(f"@font-face{{font-family:Changa;font-weight:{w};src:url(fonts/changa-latin-{w}-normal.woff2)}}" for w in (500, 600, 700, 800))
js = '''<script>
document.fonts.ready.then(()=>{
  document.querySelectorAll('text[data-fit]').forEach(t=>{
    const target=parseFloat(t.dataset.fit); let fs=parseFloat(t.getAttribute('font-size'));
    const w=t.getBBox().width;
    if(t.dataset.exact||w>target){ t.setAttribute('font-size', fs*target/w); }
  });
  document.body.dataset.ready='1';
});
</script>'''
html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}@page{{size:150cm 200cm;margin:0}}'
        f'html,body{{margin:0;background:#fff}}svg{{display:block}}</style></head><body>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="150cm" height="200cm" text-rendering="geometricPrecision">'
        f'<defs>{"".join(defs)}</defs><image href="{BASE}" x="0" y="0" width="{W}" height="{H}"/>{"".join(els)}</svg>{js}</body></html>')
open(OUT, 'w').write(html)
print('ok', len(els), 'text items')
