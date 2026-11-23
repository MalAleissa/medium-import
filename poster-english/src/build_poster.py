#!/usr/bin/env python3
"""Generates the English roll-up banner (85 x 200 cm) as one HTML page holding a vector SVG.
1 SVG unit = 1 mm.   Usage: build_poster.py <out.html> [bleed_mm]
"""
import random, sys, math
import segno

OUT = sys.argv[1]
BLEED = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
W, H = 850, 2000
QR_URL = "https://store.msajidona.org.sa/p/48254?a=m"   # decoded from the original poster's QR code

# ---- palette (approximated from the photo of the original banner) -------------------
DG   = "#1d5c30"   # dark green (headings)
MG   = "#2e6b34"   # label green
BG_  = "#4f9a2d"   # bright green (URL pill, ground bar)
QRG  = "#3f7f22"   # QR finder green (dark enough to scan)
GOLD = "#b19a3a"
GOLD_D = "#9c8532"
GREY = "#dcdcd8"
INK  = "#1f2421"

def qr_svg(x, y, size):
    q = segno.make(QR_URL, error="q", boost_error=False)
    m = [list(r) for r in q.matrix]
    n = len(m); quiet = 2
    cell = size / (n + 2 * quiet)
    out = [f'<g transform="translate({x},{y})">',
           f'<rect width="{size}" height="{size}" rx="6" fill="#fff"/>']
    def inf(r, c):  # finder zones incl. separator
        return (r < 8 and c < 8) or (r < 8 and c >= n - 8) or (r >= n - 8 and c < 8)
    path = []
    for r in range(n):
        for c in range(n):
            if m[r][c] and not inf(r, c):
                path.append(f'M{(c+quiet)*cell:.3f} {(r+quiet)*cell:.3f}h{cell:.3f}v{cell:.3f}h-{cell:.3f}z')
    out.append(f'<path d="{"".join(path)}" fill="#141414"/>')
    for (r0, c0) in [(0, 0), (0, n - 7), (n - 7, 0)]:
        fx, fy = (c0 + quiet) * cell, (r0 + quiet) * cell
        out.append(f'<path fill-rule="evenodd" fill="{QRG}" d="M{fx} {fy}h{7*cell}v{7*cell}h-{7*cell}z '
                   f'M{fx+cell} {fy+cell}v{5*cell}h{5*cell}v-{5*cell}z"/>')
        out.append(f'<rect x="{fx+2*cell}" y="{fy+2*cell}" width="{3*cell}" height="{3*cell}" fill="{QRG}"/>')
    out.append('</g>')
    return "".join(out)

# ---- emblem (mosque + roads) ----------------------------------------------------------
def emblem(x, y, s):
    return f'''<g transform="translate({x},{y}) scale({s})">
  <!-- crescent above the minaret -->
  <path d="M24 26 a12 12 0 1 0 12 17 a9.5 9.5 0 1 1 -12 -17z" fill="{DG}"/>
  <!-- minaret (slightly tapering) + gold sliver -->
  <path d="M29 56 L36 56 L44 212 L35 212 Z" fill="{DG}"/>
  <path d="M20 66 L27 58 L30 118 L23 124 Z" fill="{GOLD}"/>
  <!-- dome arc -->
  <path d="M40 158 C64 104 152 64 228 150 L216 158 C158 100 88 120 46 168 Z" fill="{DG}"/>
  <!-- small crescent above the dome -->
  <path d="M150 52 a15 15 0 1 0 15 22 a12 12 0 1 1 -15 -22z" fill="{DG}"/>
  <!-- roads (gold swooshes) -->
  <path d="M0 238 C40 198 132 178 232 172 C142 192 62 216 0 238 Z" fill="{GOLD}"/>
  <path d="M22 248 C72 212 142 194 218 190 C152 208 92 228 22 248 Z" fill="{GOLD_D}"/>
  <!-- wordmark -->
  <text x="162" y="234" text-anchor="middle" font-family="Cairo" font-weight="800" font-size="19" fill="{DG}">Our Mosques</text>
  <text x="162" y="256" text-anchor="middle" font-family="Cairo" font-weight="700" font-size="17" fill="{GOLD_D}">on the Roads</text>
</g>'''

# ---- mosque illustration ---------------------------------------------------------------
def mosque(x, y):
    lat = '''<pattern id="lat" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="9" height="9" fill="#e8d6a0"/><path d="M0 4.5h9M4.5 0v9" stroke="#8c6b2d" stroke-width="1.3"/></pattern>
      <pattern id="lat2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="6" height="6" fill="#f0e6d0"/><path d="M0 3h6M3 0v6" stroke="#7d8697" stroke-width="1"/></pattern>'''
    defs = f'''<defs>{lat}
    <linearGradient id="sand" x1="0" x2="1"><stop offset="0" stop-color="#c8a266"/><stop offset="1" stop-color="#b78a4d"/></linearGradient>
    <linearGradient id="sandDark" x1="0" x2="1"><stop offset="0" stop-color="#8f6d44"/><stop offset="1" stop-color="#a98457"/></linearGradient>
    <linearGradient id="plaster" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8e8996"/><stop offset=".6" stop-color="#a9a4ae"/><stop offset="1" stop-color="#97929d"/></linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d58a" stop-opacity="0"/><stop offset="1" stop-color="#f3d58a" stop-opacity=".55"/></linearGradient>
    <radialGradient id="lamp"><stop offset="0" stop-color="#fff6d6"/><stop offset=".35" stop-color="#ffe9a8" stop-opacity=".9"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></radialGradient>
    </defs>'''
    g = [f'<g transform="translate({x},{y})">', defs]
    # main hall (plaster, sloping parapet)
    g.append('<polygon points="95,166 478,120 478,300 95,300" fill="url(#plaster)"/>')
    g.append('<polygon points="95,166 478,120 478,128 95,175" fill="#7f7a88"/><polygon points="95,175 478,128 478,132 95,179" fill="#c9c5cd" opacity=".7"/>')
    # right back wall
    g.append('<polygon points="560,96 612,96 612,300 560,300" fill="#9b96a2"/><rect x="560" y="96" width="52" height="6" fill="#7f7a88"/>')
    # sandstone lower cladding
    g.append('<rect x="95" y="268" width="383" height="38" fill="url(#sand)"/>')
    g.append('<rect x="165" y="222" width="190" height="84" fill="url(#sand)"/>')
    for i in range(1, 6):
        g.append(f'<line x1="165" y1="{222+i*14}" x2="355" y2="{222+i*14}" stroke="#a87f45" stroke-width=".8" opacity=".6"/>')
    for i in range(1, 12):
        g.append(f'<line x1="{165+i*16}" y1="222" x2="{165+i*16}" y2="306" stroke="#a87f45" stroke-width=".6" opacity=".35"/>')
    # up-light glow on cladding
    g.append('<rect x="95" y="230" width="383" height="76" fill="url(#glow)"/>')
    # sign on the wall
    g.append(f'<text x="258" y="186" text-anchor="middle" font-family="Cairo" font-weight="700" font-size="12.5" fill="#f2efe8">Awqaf Model Mosque</text>')
    g.append('')
    # lamps
    for lx in (184, 223):
        g.append(f'<circle cx="{lx}" cy="246" r="15" fill="url(#lamp)"/><circle cx="{lx}" cy="246" r="3.2" fill="#fffbe9"/>')
    # windows
    def win(wx, wy, ww, wh):
        return (f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh*0.34}" fill="#3b3438"/>'
                f'<rect x="{wx}" y="{wy+wh*0.34}" width="{ww}" height="{wh*0.66}" fill="#d9e2ea"/>'
                f'<rect x="{wx}" y="{wy+wh*0.34}" width="{ww}" height="{wh*0.66}" fill="none" stroke="#6d83a6" stroke-width="2"/>'
                f'<line x1="{wx+ww/2}" y1="{wy+wh*0.34}" x2="{wx+ww/2}" y2="{wy+wh}" stroke="#6d83a6" stroke-width="1.6"/>'
                f'<rect x="{wx-2.5}" y="{wy+wh}" width="{ww+5}" height="3" fill="#cfc8c2"/>')
    g.append(win(118, 206, 14, 82)); g.append(win(150, 202, 15, 86))
    g.append(win(366, 160, 28, 108)); g.append(win(424, 156, 28, 112))
    # left minaret (tall, tapering)
    g.append('<polygon points="34,6 112,20 112,300 52,300" fill="url(#sandDark)"/>')
    g.append('<polygon points="34,6 112,20 112,30 34,16" fill="#7a5c39"/>')
    for i, wy in enumerate((34, 80, 126, 172)):
        wx = 66 + i * 1.5
        g.append(f'<rect x="{wx}" y="{wy}" width="22" height="34" rx="2" fill="url(#lat2)" stroke="#6f5436" stroke-width="2"/>')
    g.append('<circle cx="98" cy="40" r="5" fill="#6f5436" opacity=".7"/>')
    # right tower (front, wide)
    g.append('<polygon points="478,28 592,6 600,300 478,300" fill="url(#sand)"/>')
    g.append('<polygon points="478,28 592,6 592,14 478,36" fill="#8c6a39"/>')
    g.append('<rect x="496" y="42" width="72" height="68" fill="#a8803f"/>')
    g.append('<rect x="501" y="47" width="62" height="58" fill="url(#lat)"/>')
    for i in range(1, 9):
        g.append(f'<line x1="478" y1="{28+i*34}" x2="598" y2="{16+i*35}" stroke="#a87f45" stroke-width=".8" opacity=".5"/>')
    g.append('<rect x="478" y="262" width="122" height="38" fill="url(#glow)"/>')
    # base stone band
    g.append('<rect x="60" y="296" width="545" height="12" fill="#4a3f36"/>')
    g.append('<rect x="60" y="300" width="545" height="4" fill="#2f2a26" opacity=".6"/>')
    # palm trees
    def palm(px, base, top, tw, fr):
        s = [f'<path d="M{px-tw} {base} L{px-tw*0.45} {top} L{px+tw*0.45} {top} L{px+tw} {base}Z" fill="#3d3228"/>']
        for k in range(1, int((base-top)/9)):
            yy = base - k*9
            s.append(f'<path d="M{px-tw*0.9} {yy} q{tw*0.9} 3 {tw*1.8} 0" stroke="#2a2119" stroke-width="1.1" fill="none" opacity=".6"/>')
        random.seed(px)
        for a in range(-80, 81, 16):
            ang = math.radians(a - 90)
            L = fr * random.uniform(.8, 1.1)
            ex, ey = px + math.cos(ang) * L, top + math.sin(ang) * L * 0.9 + L * 0.35
            cx, cy = px + math.cos(ang) * L * 0.55, top + math.sin(ang) * L * 0.9 - 6
            s.append(f'<path d="M{px} {top+2} Q{cx} {cy} {ex} {ey}" stroke="#2f3a26" stroke-width="4.2" fill="none" stroke-linecap="round"/>')
            s.append(f'<path d="M{px} {top+2} Q{cx} {cy} {ex} {ey}" stroke="#4d5a38" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-dasharray="2 2.5"/>')
        return "".join(s)
    g.append(palm(330, 306, 120, 7, 56))
    g.append(palm(106, 306, 246, 3.6, 22))
    g.append('</g>')
    return "".join(g)

# ---- bank + payment logos --------------------------------------------------------------
def logo_rajhi(x, y):  # y = row center
    return f'''<g transform="translate({x},{y-17})"><rect width="34" height="34" fill="#1d3f94"/>
    <g fill="none" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"><path d="M17 5 L26 10.5 V21.5 L17 27 L8 21.5 V10.5 Z"/><path d="M17 11 L21.5 13.7 V19.3 L17 22 L12.5 19.3 V13.7 Z"/></g></g>
    <text x="{x+44}" y="{y+8}" font-family="Cairo" font-weight="800" font-size="22" fill="#1d3f94">Al Rajhi Bank</text>'''
def logo_alinma(x, y):
    return f'''<g transform="translate({x},{y-17})"><rect width="34" height="34" fill="#3a2418"/>
    <path d="M10 6 H24 V28 H10 Z M14 10 V24 H20 V10Z" fill="#fff" fill-rule="evenodd"/></g>
    <text x="{x+44}" y="{y+8}" font-family="Cairo" font-weight="800" font-size="22" fill="#3a2418">Alinma Bank</text>'''
def logo_bilad(x, y):
    return f'''<g transform="translate({x},{y-17})"><path d="M2 2 H32 V12 Q22 8 2 18 Z" fill="#d9a21b"/>
    <path d="M2 18 Q22 6 32 20 V30 Q18 24 2 34 Z" fill="#c63a28"/></g>
    <text x="{x+44}" y="{y+8}" font-family="Cairo" font-weight="800" font-size="22" fill="#7a2a1c">Bank Albilad</text>'''
def logo_riyad(x, y):
    return f'''<text x="{x}" y="{y+8}" font-family="Cairo" font-weight="800" font-size="27" fill="#0a7a42" letter-spacing=".4">riyad bank</text>'''
def logo_snb(x, y):
    return f'''<path d="M{x+15} {y-18} l10 -8 l10 8 l-4 0 l-6 -5 l-6 5z" fill="#0a8a4a" transform="translate(-1,2)"/>
    <text x="{x}" y="{y+13}" font-family="Inter" font-weight="900" font-size="31" fill="#111" letter-spacing="-.5">SNB</text>'''

def mastercard(x, y):
    return f'''<g transform="translate({x},{y})"><circle cx="19" cy="19" r="19" fill="#eb001b"/><circle cx="41" cy="19" r="19" fill="#f79e1b"/>
    <path d="M30 4.2 a19 19 0 0 1 0 29.6 a19 19 0 0 1 0 -29.6z" fill="#ff5f00"/>
    <text x="30" y="52" text-anchor="middle" font-family="Cairo" font-weight="800" font-size="9.5" fill="#222">mastercard</text></g>'''
def visa(x, y):
    return f'<text x="{x}" y="{y+28}" font-family="Inter" font-weight="900" font-style="italic" font-size="46" fill="#1a1f71" letter-spacing="-1.5">VISA</text>'
def applepay(x, y):
    return f'''<g transform="translate({x},{y})"><path transform="translate(0,-2) scale(1.55)" fill="#111" d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/>
    <text x="40" y="35" font-family="Inter" font-weight="500" font-size="35" fill="#111" letter-spacing="-.5">Pay</text></g>'''
def mada(x, y):
    return f'''<g transform="translate({x},{y})"><path d="M0 4 H30 V13 H0Z" fill="#259bd6"/><path d="M0 15 H30 V21 H0Z" fill="#fff"/><path d="M0 22 H30 V33 H0Z" fill="#84bd00"/>
    <text x="68" y="17" text-anchor="middle" font-family="CairoAr" font-weight="700" font-size="17" fill="#222" direction="rtl">مدى</text>
    <text x="68" y="35" text-anchor="middle" font-family="Cairo" font-weight="800" font-size="17" fill="#222">mada</text></g>'''

def cursor(x, y, s=1):
    return f'''<g transform="translate({x},{y}) scale({s})">
    <circle cx="14" cy="14" r="13" fill="none" stroke="#e0453a" stroke-width="3.2"/><circle cx="14" cy="14" r="5.5" fill="#e0453a"/>
    <path d="M16 15 L52 36 L38 38 L45 56 L37 59 L30 41 L21 50 Z" fill="#e0453a" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></g>'''

def whatsapp(x, y, r=17):
    return f'''<g transform="translate({x},{y})"><circle r="{r}" fill="#3f9b3a"/>
    <path d="M-9 11 L-7.5 5 A10 10 0 1 1 -3 9.4 Z" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>
    <path d="M-4.4 -4.2 C-5.5 -1 0 5.8 5 5.2 C6.2 5 6.4 3.6 5.7 3 L3.4 1.4 C2.8 1 2.2 1.3 1.8 1.8 C0 1 -1.4 -.6 -2 -2.6 C-1.6 -3 -1.2 -3.5 -1.4 -4 L-2.4 -6.3 C-2.9 -7.2 -4 -6.4 -4.4 -4.2Z" fill="#fff"/></g>'''

# ---- background ------------------------------------------------------------------------
def bg_lattice():
    T = 170
    pat = f'''<pattern id="star" width="{T}" height="{T}" patternUnits="userSpaceOnUse">
      <g fill="none" stroke="#e4e3dc" stroke-width="1.5" stroke-linejoin="round">
        <rect x="{T/2-34}" y="{T/2-34}" width="68" height="68"/>
        <rect x="{T/2-34}" y="{T/2-34}" width="68" height="68" transform="rotate(45 {T/2} {T/2})"/>
        <path d="M0 0 L{T/2-34} {T/2-34} M{T} 0 L{T/2+34} {T/2-34} M0 {T} L{T/2-34} {T/2+34} M{T} {T} L{T/2+34} {T/2+34}"/>
        <circle cx="0" cy="0" r="22"/><circle cx="{T}" cy="0" r="22"/><circle cx="0" cy="{T}" r="22"/><circle cx="{T}" cy="{T}" r="22"/>
      </g></pattern>
      <linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
      <mask id="fadeMask"><rect x="{-BLEED}" y="{-BLEED}" width="{W+2*BLEED}" height="{H+2*BLEED}" fill="url(#fadeV)"/></mask>'''
    return pat

def bottom_triangles(y0, y1):
    """triangular lattice + green triangles that grow toward the bottom edge"""
    random.seed(11)
    S = 92.0; HH = S * math.sqrt(3) / 2
    X0, X1 = -BLEED - 2 * S, W + BLEED + 2 * S
    rows = int((y1 + BLEED - y0) / HH) + 2
    lines = []
    for r in range(rows + 1):
        lines.append(f'M{X0:.1f} {y0 + r*HH:.1f}H{X1:.1f}')
    k0 = int(X0 / S) - rows; k1 = int(X1 / S) + rows
    Hh = rows * HH
    for k in range(k0, k1):
        a = k * S
        lines.append(f'M{a:.1f} {y0:.1f}L{a + Hh/math.sqrt(3):.1f} {y0 + Hh:.1f}')
        lines.append(f'M{a:.1f} {y0:.1f}L{a - Hh/math.sqrt(3):.1f} {y0 + Hh:.1f}')
    def cy_ok(P, y0):
        return sum(p[1] for p in P)/3 > 1860
    keep_out = [(0, 1600, 850, 1822), (10, 1822, 660, 1965)]          # WhatsApp text block
    tris = []
    for r in range(rows):
        off = 0 if r % 2 == 0 else S / 2
        yt, yb = y0 + r * HH, y0 + (r + 1) * HH
        for k in range(-3, int((W + 2*BLEED) / S) + 4):
            tx = k * S + off
            for kind in ('down', 'up'):
                if kind == 'down':
                    P = [(tx, yt), (tx + S, yt), (tx + S/2, yb)]
                else:
                    P = [(tx + S/2, yb), (tx + 3*S/2, yb), (tx + S, yt)]
                cx = sum(p[0] for p in P) / 3; cy = sum(p[1] for p in P) / 3
                if random.random() > (0.62 if cy > 1860 else 0.34): continue
                prog = min(1.0, max(0.0, (cy - y0) / (y1 - y0)))
                if cy < 1860 and random.random() < .6: continue
                if any(kx0 < cx < kx1 and ky0 < cy < ky1 for kx0, ky0, kx1, ky1 in keep_out): continue
                f = 0.24 + 0.34 * prog
                rot = random.choice([0, 0, 0, 1]) * random.uniform(-25, 25) + random.choice([0, 0, 60, 120, 180]) * (1 if random.random() < .35 else 0)
                pts = []
                for (px, py) in P:
                    dx, dy = (px - cx) * f * 1.0, (py - cy) * f * 1.0
                    t = math.radians(rot)
                    pts.append(f'{cx + dx*math.cos(t) - dy*math.sin(t):.1f},{cy + dx*math.sin(t) + dy*math.cos(t):.1f}')
                tris.append(f'<polygon points="{" ".join(pts)}" fill="{DG}"/>')
    defs = (f'<clipPath id="botClip"><rect x="{-BLEED}" y="{y0}" width="{W+2*BLEED}" height="{H+BLEED-y0}"/></clipPath>'
            f'<linearGradient id="fadeB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="botMask"><rect x="{-BLEED}" y="{y0}" width="{W+2*BLEED}" height="{H+BLEED-y0}" fill="url(#fadeB)"/></mask>')
    body = (f'<g clip-path="url(#botClip)"><g mask="url(#botMask)"><path d="{"".join(lines)}" stroke="#cfcec8" stroke-width="1.3" fill="none"/></g>{"".join(tris)}</g>')
    return defs, body

# ---- compose ---------------------------------------------------------------------------
def main():
    vb = f'{-BLEED} {-BLEED} {W+2*BLEED} {H+2*BLEED}'
    bot_defs, bot_body = bottom_triangles(1715, H)
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{W+2*BLEED}mm" height="{H+2*BLEED}mm" shape-rendering="geometricPrecision" text-rendering="geometricPrecision">')
    s.append(f'<defs>{bg_lattice()}{bot_defs}</defs>')
    s.append(f'<rect x="{-BLEED}" y="{-BLEED}" width="{W+2*BLEED}" height="{H+2*BLEED}" fill="#ffffff"/>')
    s.append(f'<rect x="{-BLEED}" y="{-BLEED}" width="{W+2*BLEED}" height="{H+2*BLEED}" fill="url(#star)" mask="url(#fadeMask)" opacity=".9"/>')
    s.append(bot_body)

    # header
    s.append(emblem(48, 46, 0.86))
    s.append(f'<text x="268" y="130" font-family="Cairo" font-weight="800" font-size="54" fill="{DG}">Roadside Mosques</text>')
    s.append(f'<text x="268" y="192" font-family="Cairo" font-weight="800" font-size="54" fill="{DG}">Care Association</text>')
    s.append(f'<text x="270" y="246" font-family="Cairo" font-weight="600" font-size="23" fill="{GOLD_D}">Licensed by the National Center for</text>')
    s.append(f'<text x="270" y="276" font-family="Cairo" font-weight="600" font-size="23" fill="{GOLD_D}">Non-Profit Sector Development</text>')

    # "Join us in" label
    s.append(f'<rect x="265" y="318" width="320" height="64" rx="3" fill="{MG}"/>')
    s.append(f'<text x="425" y="367" text-anchor="middle" font-family="Cairo" font-weight="700" font-size="42" fill="#fff">Join us in</text>')
    # title
    s.append(f'<text x="425" y="466" text-anchor="middle" font-family="Cairo" font-weight="800" font-size="56" fill="{GOLD}">Building &amp; Maintaining</text>')
    s.append(f'<text x="425" y="552" text-anchor="middle" font-family="Cairo" font-weight="900" font-size="80" fill="{DG}">Roadside Mosques</text>')

    # mosque + ground bar
    s.append(mosque(118, 588))
    s.append(f'<path d="M88 886 H742 Q762 886 762 900 V914 Q762 930 742 930 H128 Q88 930 88 902 Z" fill="{BG_}"/>')

    # stats
    s.append(f'<rect x="130" y="956" width="590" height="54" rx="27" fill="{GREY}"/>')
    s.append(f'<text x="425" y="994" text-anchor="middle" font-family="Cairo" font-weight="700" font-size="35" fill="{DG}">Every year, the number of</text>')
    s.append(f'<rect x="130" y="1018" width="590" height="54" rx="27" fill="{GREY}"/>')
    s.append(f'<text x="425" y="1056" text-anchor="middle" font-family="Cairo" font-weight="700" font-size="35" fill="{DG}">worshippers exceeds</text>')
    s.append(f'<path d="M135 1094 H640 Q720 1094 720 1154 Q720 1238 640 1238 H215 Q135 1238 135 1176 Z" fill="none" stroke="{GOLD_D}" stroke-width="3.2"/>')
    s.append(f'<text x="428" y="1175" text-anchor="middle" font-family="Cairo" font-weight="900" font-size="78" fill="{DG}" letter-spacing="1">70,000,000</text>')
    s.append(f'<text x="428" y="1222" text-anchor="middle" font-family="Cairo" font-weight="600" font-size="37" fill="{INK}">men and women</text>')

    # URL + QR block (mirrored for left-to-right reading)
    s.append(f'<path d="M96 1266 H524 A38 38 0 0 1 562 1304 V1338 Q562 1342 558 1342 H96 A38 38 0 0 1 58 1304 A38 38 0 0 1 96 1266 Z" fill="{BG_}"/>')
    s.append(f'<text x="309" y="1319" text-anchor="middle" font-family="Cairo" font-weight="600" font-size="39" fill="#fff">store.msajidona.org.sa</text>')
    s.append(f'<text x="62" y="1396" font-family="Cairo" font-weight="800" font-size="40" fill="{GOLD}">Donate easily and securely</text>')
    s.append(cursor(522, 1306, 1.3))
    s.append(qr_svg(632, 1262, 170))

    # payment logos
    s.append('<g transform="translate(62,1420) scale(1.14) translate(-62,-1420)">'+mastercard(62, 1422)+visa(160, 1420)+applepay(300, 1424)+mada(432, 1424)+'</g>')

    # bank transfer
    s.append(f'<text x="58" y="1546" font-family="Cairo" font-weight="800" font-size="40" fill="{DG}">Or transfer to the account</text>')
    rows = [
        (logo_rajhi,  "SA 4680000 - 204608010888992"),
        (logo_alinma, "SA 90050000 - 68207788778000"),
        (logo_bilad,  "SA 2815000 - 999124457130007"),
        (logo_riyad,  "SA 932000000 - 2690448999940"),
        (logo_snb,    "SA 80100000 - 12300000977808"),
    ]
    y = 1584
    for fn, iban in rows:
        s.append(f'<rect x="46" y="{y-24}" width="758" height="48" rx="8" fill="#e9e8e4" opacity=".9"/>')
        s.append(fn(62, y))
        s.append(f'<text x="790" y="{y+10}" text-anchor="end" font-family="Cairo" font-weight="600" font-size="31" fill="{INK}" letter-spacing="1.2">{iban}</text>')
        y += 54

    # whatsapp
    s.append(whatsapp(78, 1892, 20))
    s.append(f'<text x="112" y="1866" font-family="Cairo" font-weight="600" font-size="21" fill="{INK}">After donating, please send a message on WhatsApp</text>')
    s.append(f'<text x="112" y="1908" font-family="Cairo" font-weight="700" font-size="40" fill="{INK}" letter-spacing="3">0550881440</text>')
    s.append('</svg>')

    fonts = '''
@font-face{font-family:Cairo;font-weight:400;src:url(../fonts/cairo-latin-400-normal.woff2)}
@font-face{font-family:Cairo;font-weight:600;src:url(../fonts/cairo-latin-600-normal.woff2)}
@font-face{font-family:Cairo;font-weight:700;src:url(../fonts/cairo-latin-700-normal.woff2)}
@font-face{font-family:Cairo;font-weight:800;src:url(../fonts/cairo-latin-800-normal.woff2)}
@font-face{font-family:Cairo;font-weight:900;src:url(../fonts/cairo-latin-900-normal.woff2)}
@font-face{font-family:CairoAr;font-weight:700;src:url(../fonts/cairo-arabic-700-normal.woff2)}
@font-face{font-family:Inter;font-weight:900;font-style:italic;src:url(../fonts/Inter-BlackItalic.otf)}
@font-face{font-family:Inter;font-weight:500;src:url(../fonts/Inter-Medium.otf)}
@font-face{font-family:Inter;font-weight:900;src:url(../fonts/Inter-Black.otf)}
'''
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}@page{{size:{W+2*BLEED}mm {H+2*BLEED}mm;margin:0}}html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}</style></head><body>{"".join(s)}</body></html>'
    open(OUT, 'w', encoding='utf-8').write(html)
main()
