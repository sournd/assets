"""Build README.md from tools/README.template.md and tokens/tokens.json.

    tools/.venv/bin/python tools/build_readme.py

Fills the colour, button, contrast and interface tables from the tokens, so the README always shows
the current values, each with a colour swatch (docs/swatches/<HEX>.svg). Also makes
docs/wordmark-on-night.svg, the dark wordmark on its own surface for the README.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SW = ROOT / "docs/swatches"


def swatch(hex_value):
    """Inline swatch and code for a colour, e.g. ▪ `#3A97A3`."""
    h = hex_value.lstrip("#").upper()
    SW.mkdir(parents=True, exist_ok=True)
    (SW / f"{h}.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
        f'<rect x="0.5" y="0.5" width="15" height="15" rx="3.5" fill="#{h}" stroke="#000" stroke-opacity="0.18"/></svg>\n')
    return f'<img src="docs/swatches/{h}.svg" width="14" height="14" alt="#{h}"> `#{h}`'


def big_swatch(hex_value):
    h = hex_value.lstrip("#").upper()
    swatch(h)
    return f'<img src="docs/swatches/{h}.svg" width="40" height="40" alt="#{h}">'


def logo_colours(t):
    lg = t["logo"]
    rows = ["| | s and nd | OUR |", "|---|---|---|"]
    for mode in ("light", "dark"):
        rows.append(f"| **{mode.title()}** | {swatch(lg[mode]['s-nd'])} | {swatch(lg[mode]['OUR'])} |")
    return "\n".join(rows)


def icon_colours(t):
    i = t["icon"]
    return "\n".join(["| Tile | Bricks |", "|---|---|", f"| {swatch(i['tile'])} | {swatch(i['bricks'])} |"])


def palette(t):
    c = t["colour"]
    order = [("paper", "Paper"), ("ink", "Ink"), ("night", "Night"), ("chalk", "Chalk"),
             ("petrol", "Light petrol"), ("petrol-deep", "Deep petrol"), ("raspberry", "Raspberry"),
             ("amber", "Amber"), ("muted", "Muted"), ("border-control", "Control border"), ("divider", "Divider")]
    rows = ["| Swatch | Colour | Hex | Use |", "|---|---|---|---|"]
    for key, name in order:
        v = c[key]
        use = v["use"].replace("|", "/")
        use = use[0].upper() + use[1:]
        if "value" in v:
            sw, hexes = big_swatch(v["value"]), f'`{v["value"].upper()}`'
        else:
            sw = big_swatch(v["light"]) + " " + big_swatch(v["dark"])
            hexes = f'`{v["light"].upper()}`<br>dark `{v["dark"].upper()}`'
        rows.append(f"| {sw} | **{name}** | {hexes} | {use} |")
    rows += ["", "| Swatch | Text colour | Hex |", "|---|---|---|",
             f'| {big_swatch(c["amber"]["text-on-light"])} | Amber, as text on light | `{c["amber"]["text-on-light"]}` |',
             f'| {big_swatch(c["raspberry"]["text-on-dark"])} | Raspberry, as text on dark | `{c["raspberry"]["text-on-dark"]}` |']
    return "\n".join(rows)


def contrast(t):
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", t["contrast"]) if s.strip()]
    return "\n".join(f"- {s}" for s in sentences)


def buttons(t):
    out = []
    names = {"primary": "Primary", "secondary": "Secondary", "control": "Control", "highlight": "Highlight"}
    for mode, title in (("light", "On paper"), ("dark", "On night")):
        out.append(f"**{title}**\n")
        out.append("| Button | Rest | Hover | Pressed | Disabled | Label |")
        out.append("|---|---|---|---|---|---|")
        for kind, s in t["button"][mode].items():
            if kind == "secondary":
                rest, hover, pressed = s["border"] + " border", s["hover-fill"], s["pressed-fill"]
                cells = [f"{swatch(s['border'])} outline", swatch(s["hover-fill"]), swatch(s["pressed-fill"]),
                         swatch(s["disabled-text"]), swatch(s["text"])]
            else:
                cells = [swatch(s["rest"]), swatch(s["hover"]), swatch(s["pressed"]),
                         swatch(s["disabled-fill"]), swatch(s["text"])]
            out.append(f"| **{names[kind]}** | " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out).rstrip()


def interface(t):
    ui = t["ui"]
    rows = ["| Thing | Value |", "|---|---|"]
    for k, v in ui["radius"].items():
        rows.append(f"| Radius, {k}s | {v} |")
    labels = {"input": "Height, inputs", "primary-action": "Height, primary actions", "small": "Height, small",
              "chip": "Height, chips"}
    for k, v in ui["height"].items():
        rows.append(f"| {labels[k]} | {v} |")
    c = t["colour"]
    rows.append(f"| Control border | 1px {swatch(c['border-control']['light'])} (dark {swatch(c['border-control']['dark'])}) |")
    rows.append(f"| Divider | {swatch(c['divider']['light'])} (dark {swatch(c['divider']['dark'])}) |")
    rows.append(f"| Focus | {ui['focus']['ring']} ring, {ui['focus']['offset']} offset; ink on light, chalk on dark |")
    return "\n".join(rows)


def wordmark_on_night():
    svg = (ROOT / "marks/sournd-wordmark-dark.svg").read_text()
    inner = svg[svg.index(">") + 1: svg.rindex("</svg>")]
    pad = 220
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/wordmark-on-night.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-720 - pad} {3540 + 2 * pad} {800 + 2 * pad}">'
        f'<rect x="{-pad}" y="{-720 - pad}" width="{3540 + 2 * pad}" height="{800 + 2 * pad}" rx="90" fill="#141A1C"/>'
        f"{inner}</svg>\n")


def main():
    t = json.loads((ROOT / "tokens/tokens.json").read_text())
    if SW.exists():
        for old in SW.glob("*.svg"):
            old.unlink()
    wordmark_on_night()
    text = (ROOT / "tools/README.template.md").read_text()
    for name, fn in (("logo_colours", logo_colours), ("icon_colours", icon_colours), ("palette", palette),
                     ("contrast", contrast), ("buttons", buttons), ("interface", interface)):
        text = text.replace("{{" + name + "}}", fn(t))
    if "{{" in text:
        raise SystemExit("unfilled placeholder in the template")
    (ROOT / "README.md").write_text(text)
    print(f"README.md written, {len(list(SW.glob('*.svg')))} swatches")


if __name__ == "__main__":
    main()
