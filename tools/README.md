# Changing the brand

Only needed when the brand itself changes. Everything these tools make is committed, so nobody
installing the package runs them.

1. Update the specification in `design/` if it changed.
2. `python3 -m venv tools/.venv && tools/.venv/bin/pip install -r tools/requirements.txt` (once).
3. `tools/.venv/bin/python tools/build_marks.py` rebuilds the wordmark and icon SVGs from the font
   outlines in `fonts/mark/`.
4. `tools/.venv/bin/python tools/build_derived.py` rebuilds the PNGs, favicons, woff2 fonts,
   `fonts.css` and `tokens.css` (needs Google Chrome and ImageMagick).
5. `npm run check`, then commit the results.
