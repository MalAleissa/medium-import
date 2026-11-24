#!/usr/bin/env python3 -I
"""Erase only the Arabic text from the original 150x200 cm poster raster (inpaint), keep every picture.
usage: erase_arabic.py <orig_full_rgb.png> <out.jpg> [debug_dir]"""
import sys, os, numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, out = sys.argv[1], sys.argv[2]
dbg = sys.argv[3] if len(sys.argv) > 3 else None
K = 5906 / 1064.0   # preview(1064 wide) -> full-res px
img = np.array(Image.open(src).convert('RGB'))
H, W = img.shape[:2]

def feats(c):
    c = c.astype(np.int16); R, G, B = c[..., 0], c[..., 1], c[..., 2]
    lum = (0.299 * R + 0.587 * G + 0.114 * B)
    chroma = c.max(-1) - c.min(-1)
    return R, G, B, lum, chroma

MODES = {
  'dark':  lambda R,G,B,l,ch: (l < 205) | (ch > 30),
  'green': lambda R,G,B,l,ch: ((G - R) > 14) & (ch > 22),
  'dkgreen': lambda R,G,B,l,ch: ((G - R) > 14) & (ch > 22) & (l < 150),
  'gold':  lambda R,G,B,l,ch: (R > 140) & ((R - G) > 8) & ((R - G) < 75) & ((G - B) > 25),
  'white': lambda R,G,B,l,ch: (l > 205) & (ch < 70),
  'navy':  lambda R,G,B,l,ch: ((B - R) > 30) & (G < 118) & (l < 175),
  'purple': lambda R,G,B,l,ch: ((B - R) > 18) & ((G - R) < 6) & (ch > 16),
  'blue':  lambda R,G,B,l,ch: ((B - R) > 25) | ((l < 150) & (ch > 20)),
  'brown': lambda R,G,B,l,ch: (l < 170) & ((R - B) > 8),
  'red':   lambda R,G,B,l,ch: ((R - G) > 60) & ((R - B) > 40),
  'greengold': lambda R,G,B,l,ch: (((G - R) > 14) & (ch > 22)) | ((R > 140) & ((R - G) > 8) & ((R - G) < 75) & ((G - B) > 25)),
}
# name: (preview box x0,y0,x1,y1, mode)
REGIONS = {
 'header_title':  ((252,135,732,204), 'green'),
 'header_sub':    ((305,205,675,232), 'gold'),
 'emblem_text':   ((760,214,834,250), 'green'),
 'label':         ((777,353,942,383), 'white'),
 'title_gold':    ((592,402,940,446), 'gold'),
 'title_green':   ((592,447,940,490), 'green'),
 'pill1':         ((150,560,455,602), 'green'),
 'pill2':         ((150,607,455,650), 'green'),
 'worshippers':   ((222,738,375,779), 'green'),
 'sms_title':     ((648,585,832,612), 'green'),
 'sms_send':      ((720,658,778,686), 'green'),
 'row_tr':        ((796,698,893,759), 'greengold'),
 'row_tl':        ((612,696,693,759), 'greengold'),
 'row_br':        ((788,792,886,858), 'greengold'),
 'row_bl':        ((613,790,692,858), 'greengold'),
 'empty_msg':     ((692,792,763,858), 'gold'),
 'app_text':      ((373.8,894,406,928), 'dkgreen'),
 'transfer':      ((784,868,950,893), 'green'),
 'bank_rajhi':    ((912,896,945,917), 'blue'),
 'bank_alinma':   ((912,920,945,940), 'brown'),
 'bank_bilad':    ((912,942,945,963), 'red'),
 'bank_riyad_ar': ((896,964,946,976), 'navy'),
 'bank_riyad_dots': ((896,972,946,982), 'purple'),
 'whatsapp_txt':  ((697,1016,852,1034), 'green'),
 'donate':        ((484,1150,742,1190), 'gold'),
 'eng_line1':     ((545,500,1000,527), 'dark'),
 'eng_line2':     ((545,528,1000,560), 'dark'),
 'num_70m':       ((195,688,400,742), 'dark'),
 'phone_digits':  ((690,1034,822,1054), 'dark'),
 'url_text':      ((493,1108,729,1142), 'white'),
}
os.makedirs(dbg, exist_ok=True) if dbg else None
import json
res = img.copy()
info = {}
cols = {}
for name, (box, mode) in REGIONS.items():
    x0, y0, x1, y1 = [int(round(v * K)) for v in box]
    pad = 60
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    crop = res[Y0:Y1, X0:X1].copy()
    R, G, B, l, ch = feats(crop)
    m = MODES[mode](R, G, B, l, ch)
    inbox = np.zeros(m.shape, bool); inbox[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
    m &= inbox
    ys, xs = np.where(m)
    if len(xs) == 0: print('!! empty mask', name); continue
    ys_,xs_=ys,xs
    top=ys_<=np.percentile(ys_,25); bot=ys_>=np.percentile(ys_,75)
    cols[name]=(tuple(int(v) for v in np.median(crop[ys_[top],xs_[top]],axis=0)), tuple(int(v) for v in np.median(crop[ys_[bot],xs_[bot]],axis=0)))
    info[name] = (int(xs.min() + X0), int(ys.min() + Y0), int(xs.max() + X0), int(ys.max() + Y0))
    m8 = m.astype(np.uint8) * 255
    m8 = cv2.dilate(m8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25) if name == 'url_text' else ((5, 5) if name == 'bank_riyad_dots' else (13, 13))))
    m8[~inbox] = 0 if mode != 'white' else m8[~inbox]
    m8 &= (inbox.astype(np.uint8) * 255) if True else m8
    fixed = cv2.inpaint(crop, m8, 7, cv2.INPAINT_TELEA)
    res[Y0:Y1, X0:X1] = fixed
    if dbg:
        side = np.concatenate([img[Y0:Y1, X0:X1], fixed], axis=1)
        s = min(1.0, 1400 / side.shape[1])
        Image.fromarray(side).resize((int(side.shape[1] * s), int(side.shape[0] * s)), Image.LANCZOS).save(f'{dbg}/{name}.png')

# ---- IBAN rows: find digit bands, erase text on the grey bars ------------------
img2 = res
sub = img2[4950:5640, 3380:4945]
lumv = sub.mean(-1); chv = sub.max(-1) - sub.min(-1)
mk = (lumv < 150) | (chv > 60)
rows = mk.sum(1) > 3; bands = []; st = None
for i, v in enumerate(rows):
    if v and st is None: st = i
    if (not v) and st is not None:
        if i - st > 25: bands.append((st + 4950, i - 1 + 4950))
        st = None
assert len(bands) == 5, bands
ib = []
for (a, b) in bands:
    colsx = np.where(mk[a - 4950:b - 4950 + 1].any(0))[0]
    ib.append((int(colsx.min() + 3380), int(a), int(colsx.max() + 3380), int(b)))
for (x0, y0, x1, y1) in ib:
    X0, Y0, X1, Y1 = x0 - 70, y0 - 40, x1 + 70, y1 + 40
    crop = res[Y0:Y1, X0:X1].copy()
    R, G, B, l, ch = feats(crop)
    m = ((l < 195) | (ch > 40)) & ((G - R) < 20)     # grey digits + gold SA only (keeps the teal riyad logo)
    inb = np.zeros(m.shape, bool); inb[30:-30, 55:(4950 - X0)] = True
    m &= inb
    m8 = cv2.dilate(m.astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    res[Y0:Y1, X0:X1] = cv2.inpaint(crop, m8, 6, cv2.INPAINT_TELEA)
meas = {'iban': ib}
# gold of 'SA' and greys sampled from the ORIGINAL pixels
o = img
def med(box, f):
    x0, y0, x1, y1 = box; c = o[y0:y1, x0:x1]; R, G, B, l, ch = feats(c); m = f(R, G, B, l, ch)
    return '#%02x%02x%02x' % tuple(int(v) for v in np.median(c[m], axis=0))
x0, y0, x1, y1 = ib[0]
meas['col_sa']   = med((x0, y0, x0 + 90, y1), lambda R,G,B,l,ch: (R > 140) & ((R - B) > 60))
meas['col_iban'] = med((x0 + 150, y0, x1, y1), lambda R,G,B,l,ch: l < 150)
meas['col_green_inline'] = med((4660, 2968, 5062, 3072), lambda R,G,B,l,ch: ch > 45)
meas['col_eng'] = med((3063, 2968, 4500, 3072), lambda R,G,B,l,ch: l < 150)
meas['col_70m'] = med((1173, 3897, 2141, 4054), lambda R,G,B,l,ch: l < 150)
meas['col_phone'] = med((3871, 5755, 4512, 5806), lambda R,G,B,l,ch: l < 150)
# ink boxes (from the original) of the retyped Latin items
for k, (nm, bx) in {'eng1': ('eng_line1', None), 'eng2': ('eng_line2', None), 'num70': ('num_70m', None), 'phone': ('phone_digits', None), 'url': ('url_text', None)}.items():
    meas[k] = list(info[nm])
# QR codes: bounding boxes (checked earlier by decoding) -> white-out, drawn as vector later
QR = {'bottom': (1816, 6111, 671, 29), 'circle': (969, 4963, 489, 41)}
for nm, (qx, qy, qw, n) in QR.items():
    res[qy - 14:qy + qw + 14, qx - 14:qx + qw + 14] = 255
meas['qr'] = QR
# finder colours of the original codes
for nm, (qx, qy, qw, n) in QR.items():
    m_ = qw / n
    ring = o[int(qy + 3.5 * m_), int(qx + 0.5 * m_)]; inner = o[int(qy + 3.5 * m_), int(qx + 3.5 * m_)]
    meas['qrcol_' + nm] = ['#%02x%02x%02x' % tuple(int(v) for v in ring), '#%02x%02x%02x' % tuple(int(v) for v in inner)]
json.dump(meas, open(os.path.join(os.path.dirname(os.path.abspath(out)), 'measure.json'), 'w'))
print('measure:', {k: v for k, v in meas.items() if k not in ('iban',)}); print('iban bands', ib)

Image.fromarray(res).save(out, quality=96, subsampling=0, dpi=(100, 100))
print('bboxes(full-res px) of removed text:')
for n, b in info.items(): print(f'  {n:14s} {b}  w={b[2]-b[0]} h={b[3]-b[1]}')

print('colours (top25%, bottom25%) of original text:')
for n,(a,b) in cols.items(): print(f'  {n:14s} #%02x%02x%02x  #%02x%02x%02x' % (a+b))
