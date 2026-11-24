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
  'navy':  lambda R,G,B,l,ch: ((B - R) > 30) & (G < 118) & (l < 160),
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
 'bank_riyad_ar': ((896,966,946,979), 'navy'),
 'whatsapp_txt':  ((697,1016,852,1034), 'green'),
 'donate':        ((484,1150,742,1190), 'gold'),
}
os.makedirs(dbg, exist_ok=True) if dbg else None
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
    m8 = cv2.dilate(m8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    m8[~inbox] = 0 if mode != 'white' else m8[~inbox]
    m8 &= (inbox.astype(np.uint8) * 255) if True else m8
    fixed = cv2.inpaint(crop, m8, 7, cv2.INPAINT_TELEA)
    res[Y0:Y1, X0:X1] = fixed
    if dbg:
        side = np.concatenate([img[Y0:Y1, X0:X1], fixed], axis=1)
        s = min(1.0, 1400 / side.shape[1])
        Image.fromarray(side).resize((int(side.shape[1] * s), int(side.shape[0] * s)), Image.LANCZOS).save(f'{dbg}/{name}.png')
Image.fromarray(res).save(out, quality=96, subsampling=0, dpi=(100, 100))
print('bboxes(full-res px) of removed text:')
for n, b in info.items(): print(f'  {n:14s} {b}  w={b[2]-b[0]} h={b[3]-b[1]}')

print('colours (top25%, bottom25%) of original text:')
for n,(a,b) in cols.items(): print(f'  {n:14s} #%02x%02x%02x  #%02x%02x%02x' % (a+b))
