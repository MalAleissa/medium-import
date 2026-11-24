# English poster (150 x 200 cm) - v3, built from the original print file

Input: the original `*.pdf` (a flattened Photoshop raster, 100 ppi). Pipeline:
1. `pdftoppm -r 100 -png original.pdf full`  -> `full-1.png` (5906 x 7874 px)
2. `python3 -I erase_v3.py full-1.png cleaned.jpg` - removes the Arabic text and the soft raster Latin text/QR codes (inpainting). Every picture is untouched. Writes `measure.json` (exact positions/colours of the original text).
3. `python3 -I build_v3.py cleaned.jpg measure.json poster_v3.html` - vector text layer (Tajawal) + vector QR codes over the cleaned artwork.
4. `node render.js poster_v3.html out.pdf 1500 2000` -> 150 x 200 cm PDF.

Typeface: Tajawal (SIL OFL), identified as the brand face by measuring the poster's own English line and its Arabic titles. Fonts in `fonts/`.
QR codes are regenerated as vector with the same data (checked by scanning the exported PDF).
