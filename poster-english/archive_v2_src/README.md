# English poster (150 x 200 cm) - built from the original print file

Pipeline (all inputs are the user's original `*.pdf`, a flattened Photoshop raster at 100 ppi):
1. `pdftoppm -r 100 -png original.pdf full`  -> `full-1.png` (5906 x 7874 px)
2. `python3 -I erase_arabic.py full-1.png cleaned.jpg` - removes ONLY the Arabic text (inpainting); every picture is untouched
3. `python3 -I build_english.py cleaned.jpg english.html` - vector English text (Changa font) laid over the cleaned artwork
4. `node ../src/render.js english.html out.pdf 1500 2000` -> 150 x 200 cm PDF

Fonts: Changa (SIL OFL) in `fonts/`.
