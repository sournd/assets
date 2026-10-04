"""Build everything derived from the marks, tokens and fonts (4 Oct 2026).

    tools/.venv/bin/python tools/build_marks.py      # first: marks/*.svg
    tools/.venv/bin/python tools/build_derived.py

Makes:
  fonts/*/*.woff2 + fonts/fonts.css   web fonts from the variable TTFs (both SIL OFL 1.1)
  tokens/tokens.css                   CSS custom properties from tokens/tokens.json, light + dark
  marks/png/                          icon PNGs (cut chosen by size, per the pack) and wordmark PNGs
  web/                                favicon.ico, favicon.svg, apple-touch-icon.png, icon-192/512
PNGs are rendered by headless Google Chrome from the SVGs (transparent background).
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


# ── fonts ────────────────────────────────────────────────────────────────────

FONTS = [
    # (file, css family, style, weight range, stretch range)
    ("bricolage-grotesque/BricolageGrotesque[opsz,wdth,wght].ttf", "Bricolage Grotesque", "normal", "200 800", "75% 100%"),
    ("instrument-sans/InstrumentSans[wdth,wght].ttf", "Instrument Sans", "normal", "400 700", "75% 100%"),
    ("instrument-sans/InstrumentSans-Italic[wdth,wght].ttf", "Instrument Sans", "italic", "400 700", "75% 100%"),
]


def build_fonts():
    faces = []
    for rel, family, style, weight, stretch in FONTS:
        src = ROOT / "fonts" / rel
        woff2 = src.with_suffix(".woff2")
        f = TTFont(src)
        f.flavor = "woff2"
        f.save(woff2)
        url = woff2.relative_to(ROOT / "fonts").as_posix().replace("[", "%5B").replace("]", "%5D")
        faces.append(f"@font-face {{\n  font-family: '{family}';\n  font-style: {style};\n"
                     f"  font-weight: {weight};\n  font-stretch: {stretch};\n  font-display: swap;\n"
                     f"  src: url('{url}') format('woff2');\n}}\n")
    header = ("/* sournd fonts. Bricolage Grotesque 700 for the wordmark, display and headings;\n"
              "   Instrument Sans 400 body / 500 UI / 600 labels and values. No monospace.\n"
              "   Both SIL Open Font License 1.1 (OFL.txt beside each font). */\n")
    (ROOT / "fonts/fonts.css").write_text(header + "\n".join(faces))


# ── tokens.css ───────────────────────────────────────────────────────────────

def build_tokens_css():
    t = json.loads((ROOT / "tokens/tokens.json").read_text())
    c = t["colour"]
    light, dark = {}, {}
    for name in ("paper", "ink", "night", "chalk"):
        light[name] = dark[name] = c[name]["value"]
    for name in ("petrol", "petrol-deep", "raspberry", "muted", "border-control", "divider"):
        light[name], dark[name] = c[name]["light"], c[name]["dark"]
    light["amber"] = dark["amber"] = c["amber"]["value"]
    light["amber-text"] = c["amber"]["text-on-light"]
    dark["amber-text"] = c["amber"]["value"]
    light["raspberry-text"] = c["raspberry"]["light"]
    dark["raspberry-text"] = c["raspberry"]["text-on-dark"]
    light["surface"], dark["surface"] = c["paper"]["value"], c["night"]["value"]
    light["text"], dark["text"] = c["ink"]["value"], c["chalk"]["value"]
    for theme, out in (("light", light), ("dark", dark)):
        for kind, states in t["button"][theme].items():
            for state, v in states.items():
                out[f"btn-{kind}-{state}"] = v
    ui = t["ui"]
    fixed = {
        "radius-control": ui["radius"]["control"], "radius-card": ui["radius"]["card"],
        "radius-modal": ui["radius"]["modal"], "height-input": ui["height"]["input"],
        "height-primary": ui["height"]["primary-action"], "height-small": ui["height"]["small"],
        "height-chip": ui["height"]["chip"], "border-width": ui["border"]["control"],
        "focus-ring": ui["focus"]["ring"], "focus-offset": ui["focus"]["offset"],
        "font-display": "'Bricolage Grotesque', sans-serif", "font-ui": "'Instrument Sans', sans-serif",
    }

    def block(d):
        return "".join(f"  --sournd-{k}: {v};\n" for k, v in d.items())

    css = ("/* sournd tokens, generated from tokens/tokens.json by tools/build_derived.py. Do not edit. */\n"
           f":root, [data-theme=\"light\"] {{\n  color-scheme: light;\n{block(fixed)}{block(light)}}}\n"
           f"[data-theme=\"dark\"] {{\n  color-scheme: dark;\n{block(dark)}}}\n"
           f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme=\"light\"]) {{\n    color-scheme: dark;\n"
           + "".join(f"    --sournd-{k}: {v};\n" for k, v in dark.items()) + "  }\n}\n")
    (ROOT / "tokens/tokens.css").write_text(css)


# ── DTCG design tokens (Figma variable import, Tokens Studio, Style Dictionary) ──

def build_dtcg():
    """W3C Design Tokens Community Group format: core (mode-free), light and dark sets."""
    t = json.loads((ROOT / "tokens/tokens.json").read_text())
    c, ui, ty = t["colour"], t["ui"], t["type"]

    def col(v, desc=None):
        out = {"$type": "color", "$value": v}
        if desc:
            out["$description"] = desc
        return out

    def dim(v):
        return {"$type": "dimension", "$value": v}

    core = {
        "colour": {n: col(c[n]["value"], c[n]["use"]) for n in ("paper", "ink", "night", "chalk", "amber")},
        "radius": {k: dim(v) for k, v in ui["radius"].items()},
        "height": {k: dim(v) for k, v in ui["height"].items()},
        "border": {"control": dim(ui["border"]["control"])},
        "focus": {"ring": dim(ui["focus"]["ring"]), "offset": dim(ui["focus"]["offset"])},
        "font": {
            "display": {"$type": "fontFamily", "$value": ty["display"]["family"]},
            "ui": {"$type": "fontFamily", "$value": ty["body"]["family"]},
        },
        "font-weight": {
            "display": {"$type": "fontWeight", "$value": ty["display"]["weight"]},
            "body": {"$type": "fontWeight", "$value": ty["body"]["weight"]},
            "ui": {"$type": "fontWeight", "$value": ty["ui"]["weight"]},
            "label": {"$type": "fontWeight", "$value": ty["label"]["weight"]},
        },
    }
    modes = {}
    for mode in ("light", "dark"):
        m = {"colour": {}, "button": {}}
        for n in ("petrol", "petrol-deep", "raspberry", "muted", "border-control", "divider"):
            m["colour"][n] = col(c[n][mode], c[n]["use"])
        m["colour"]["surface"] = col(c["paper"]["value"] if mode == "light" else c["night"]["value"])
        m["colour"]["text"] = col(c["ink"]["value"] if mode == "light" else c["chalk"]["value"])
        m["colour"]["amber-text"] = col(c["amber"]["text-on-light"] if mode == "light" else c["amber"]["value"])
        m["colour"]["raspberry-text"] = col(c["raspberry"]["light"] if mode == "light" else c["raspberry"]["text-on-dark"])
        for kind, states in t["button"][mode].items():
            m["button"][kind] = {state: col(v) for state, v in states.items()}
        m["logo"] = {k: col(v) for k, v in t["logo"][mode].items()}
        modes[mode] = m
    out = ROOT / "tokens/dtcg"
    out.mkdir(exist_ok=True)
    for name, data in (("core", core), ("light", modes["light"]), ("dark", modes["dark"])):
        (out / f"{name}.tokens.json").write_text(json.dumps(data, indent=2) + "\n")


# ── PNGs via headless Chrome ─────────────────────────────────────────────────

def render(svg, width, height, out):
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "r.html"
        html.write_text(f'<html><body style="margin:0;background:transparent">'
                        f'<img src="file://{svg}" width="{width}" height="{height}" style="display:block"></body></html>')
        shot = Path(tmp) / "s.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--default-background-color=00000000",
                        "--force-device-scale-factor=1", f"--window-size={width},{height}",
                        f"--screenshot={shot}", f"file://{html}"],
                       check=True, capture_output=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(shot, out)


def icon_cut(px):
    """design/SourndAppIcon.dc.html: tiny below 20px, small up to 32px, full above."""
    return "tiny" if px < 20 else "small" if px <= 32 else "full"


def build_pngs():
    marks = ROOT / "marks"
    for px in (16, 20, 24, 32, 48, 64, 128, 180, 192, 256, 512, 1024):
        render(marks / f"sournd-icon-{icon_cut(px)}.svg", px, px, marks / f"png/sournd-icon-{px}.png")
    for theme in ("light", "dark"):
        for h in (32, 64, 128, 256):
            w = round(h * 3540 / 800)
            render(marks / f"sournd-wordmark-{theme}.svg", w, h, marks / f"png/sournd-wordmark-{theme}-{h}.png")
    web = ROOT / "web"
    web.mkdir(exist_ok=True)
    png = marks / "png"
    shutil.copyfile(png / "sournd-icon-180.png", web / "apple-touch-icon.png")
    shutil.copyfile(png / "sournd-icon-192.png", web / "icon-192.png")
    shutil.copyfile(png / "sournd-icon-512.png", web / "icon-512.png")
    shutil.copyfile(marks / "sournd-icon-small.svg", web / "favicon.svg")
    subprocess.run(["magick", png / "sournd-icon-16.png", png / "sournd-icon-32.png", png / "sournd-icon-48.png",
                    web / "favicon.ico"], check=True)


def main():
    build_fonts()
    build_tokens_css()
    build_dtcg()
    build_pngs()
    import build_readme
    build_readme.main()
    for p in sorted(list((ROOT / "marks/png").glob("*.png")) + list((ROOT / "web").glob("*"))
                    + list((ROOT / "fonts").rglob("*.woff2")) + [ROOT / "fonts/fonts.css", ROOT / "tokens/tokens.css"]):
        print(f"{p.stat().st_size:>8}  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
