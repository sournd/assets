"""Build the sournd marks as plain SVG from the design specifications.

    tools/.venv/bin/python tools/build_marks.py

Sources (never edited here):
  design/SourndMark.dc.html     wordmark: glyph positions, cut-throughs, knob pointer, fader, jack
  design/SourndAppIcon.dc.html  Bricks icon: wall layout and the full / small / tiny cuts
  design/BRAND.md              colours

The wordmark's letters come from the font the component loads (Bricolage Grotesque 96pt Bold,
fonts/mark/sourndMark.woff2), outlined with fontTools; the component's masks become real geometry
(skia-pathops difference), so the SVGs need no font and no masks. The icon's FUZZ/COMP/GATE labels
are outlined from JetBrains Mono Bold, the face the component names. Needs: fonttools, brotli,
skia-pathops (tools/requirements.txt).
"""

import math
from pathlib import Path

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "marks"

# Colours: design/BRAND.md "Logo colour" and "Icon".
WORDMARK = {
    "light": {"text": "#0E7482", "ink": "#3A97A3", "detail": "#3A97A3"},
    "dark": {"text": "#3A97A3", "ink": "#6BBCC6", "detail": "#6BBCC6"},
}
ICON_FG, ICON_BG = "#F3F0EA", "#3A97A3"


# ── geometry helpers ─────────────────────────────────────────────────────────

def matrix(*ops):
    """Compose affine ops ('t', dx, dy) / ('r', degrees) left to right, SVG transform order."""
    a, b, c, d, e, f = 1, 0, 0, 1, 0, 0
    for op in ops:
        if op[0] == "t":
            m = (1, 0, 0, 1, op[1], op[2])
        else:
            r = math.radians(op[1])
            m = (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0)
        a, b, c, d, e, f = (
            a * m[0] + c * m[1], b * m[0] + d * m[1],
            a * m[2] + c * m[3], b * m[2] + d * m[3],
            a * m[4] + c * m[5] + e, b * m[4] + d * m[5] + f,
        )
    return (a, b, c, d, e, f)


def svg_path(d, transform=(1, 0, 0, 1, 0, 0)):
    p = pathops.Path()
    parse_path(d, TransformPen(p.getPen(), transform))
    return p


def rect(x, y, w, h, rx=0, transform=(1, 0, 0, 1, 0, 0)):
    if not rx:
        return svg_path(f"M{x} {y}h{w}v{h}h{-w}Z", transform)
    r = min(rx, w / 2, h / 2)
    d = (f"M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}"
         f"A{r} {r} 0 0 1 {x + w - r} {y + h}H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}"
         f"V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z")
    return svg_path(d, transform)


def union(paths):
    out = pathops.Path()
    for p in paths:
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out


def minus(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def to_d(p):
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    p.draw(pen)
    return pen.getCommands()


class Glyphs:
    def __init__(self, path):
        self.font = TTFont(path)
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm

    def path(self, ch, x, y, size):
        """One glyph with its origin at (x, y) in SVG space (y down), font-size `size`."""
        s = size / self.upem
        p = pathops.Path()
        self.gs[self.cmap[ord(ch)]].draw(TransformPen(p.getPen(), (s, 0, 0, -s, x, y)))
        return p

    def advance(self, ch, size):
        return self.font["hmtx"][self.cmap[ord(ch)]][0] * size / self.upem


# ── wordmark (SourndMark.dc.html) ────────────────────────────────────────────

def wordmark(theme):
    g = Glyphs(ROOT / "fonts/mark/sourndMark.woff2")
    col = WORDMARK[theme]
    # mask mA: knob pointer clearance through the O, jack clearance under the R
    cut_a = union([
        rect(-46, -430, 92, 270, transform=matrix(("t", 840, -330), ("r", 40))),
        rect(-95, 0, 190, 170, transform=matrix(("t", 2280.2, -120), ("r", -12.8))),
    ])
    text = minus(union(g.path(c, x, 0, 1000) for c, x in (("s", 0), ("n", 2426), ("d", 2979))), cut_a)
    ink_letters = minus(union(g.path(c, x, 0, 1000) for c, x in (("O", 510), ("U", 1170), ("R", 1795))), cut_a)
    # detail: knob pointer, and the fader (track + thumb) minus mask mB's grip line
    pointer = rect(-26, -348, 52, 253, 3, transform=matrix(("t", 840, -330), ("r", 40)))
    fader = minus(union([rect(1467, -600, 30, 106, 15), rect(1467, -386, 30, 211, 15),
                         rect(1407, -472, 150, 64, 10)]), rect(1427, -446, 110, 12))
    detail = union([pointer, fader])
    # ink: the jack plug on the R's leg
    jt = matrix(("t", 2280.2, -120), ("r", -12.8))
    jack = union([rect(-64, 19, 128, 50, transform=jt),
                  svg_path("M-45.5 88H45.5V114.5A45.5 45.5 0 0 1 -45.5 114.5Z", jt)])
    ink = union([ink_letters, jack])
    parts = [(col["text"], text), (col["ink"], ink), (col["detail"], detail)]
    body = "".join(f'<path fill="{c}" d="{to_d(p)}"/>' for c, p in parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -720 3540 800" role="img" '
            f'aria-label="sOURnd">{body}</svg>\n')


# ── icon (SourndAppIcon.dc.html) ─────────────────────────────────────────────

def sine(x0, x1, y, amp, cycles, step=4):
    """Polyline points for `cycles` of a sine from x0 to x1 around baseline y (y down)."""
    n = max(2, int((x1 - x0) / step))
    return [(x0 + (x1 - x0) * i / n, y - amp * math.sin(2 * math.pi * cycles * i / n)) for i in range(n + 1)]


def polyline(points, colour, width, extra=""):
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in points)
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')


def block_symbol(kind, cx, cy, colour, sw=18, half_w=120, amp=40):
    """Small-cut block symbols, standing in for the words (James, 4 Oct 2026).

    fuzz: a clipped, squared-off wave. comp: a wave held between dotted threshold lines.
    gate: a wave that stops at a | line and runs flat after it."""
    x0, x1 = cx - half_w, cx + half_w
    if kind == "FUZZ":
        pts, x, sign, ramp, flat = [(x0, cy)], x0, -1, 14, 26
        while x + ramp + flat <= x1 + 0.1:
            pts += [(x + ramp, cy + sign * amp), (x + ramp + flat, cy + sign * amp)]
            x += ramp + flat
            sign = -sign
        pts.append((x1, cy))
        return polyline(pts, colour, sw)
    if kind == "COMP":
        dots = ' stroke-dasharray="0.1 26"'
        return (polyline([(x0, cy - amp), (x1, cy - amp)], colour, sw * 0.7, dots)
                + polyline([(x0, cy + amp), (x1, cy + amp)], colour, sw * 0.7, dots)
                + polyline(sine(x0 + 10, x1 - 10, cy, amp * 0.62, 2.5), colour, sw))
    if kind == "GATE":
        bar = x0 + (x1 - x0) * 0.66
        return (polyline(sine(x0, bar - 18, cy, amp, 2), colour, sw)
                + polyline([(bar, cy - amp - 12), (bar, cy + amp + 12)], colour, sw)
                + polyline([(bar + 18, cy), (x1, cy)], colour, sw))
    raise ValueError(kind)


def icon(lvl, tile=True):
    P, Q = ICON_FG, ICON_BG
    els = []
    if tile:
        els.append(f'<rect width="1000" height="1000" rx="224" fill="{Q}"/>')
    if lvl == "tiny":
        # A prompt and a waveform: type it, hear it (James, 4 Oct 2026; replaces the one slot).
        els.append(polyline([(175, 370), (300, 500), (175, 630)], P, 84))
        els.append(polyline(sine(470, 830, 500, 120, 1, step=6), P, 76))
    else:
        mono = Glyphs(ROOT / "fonts/mark/JetBrainsMono-Bold.woff2")
        small = lvl == "small"
        sw, dl, gp = (14, 44, 30) if small else (7, 22, 16)

        def dashed(x, y, w, h, r):
            L = 2 * (w + h) - 8 * r + 2 * math.pi * r
            n = round(L / (dl + gp))
            dd = L / n - gp
            d = (f"M{x + r} {y}h{w - 2 * r}a{r} {r} 0 0 1 {r} {r}v{h - 2 * r}a{r} {r} 0 0 1 -{r} {r}"
                 f"h-{w - 2 * r}a{r} {r} 0 0 1 -{r} -{r}v-{h - 2 * r}a{r} {r} 0 0 1 {r} -{r}z")
            off = -(r * math.pi / 2 - dd) / 2 - (w - 2 * r) + dd / 2
            return (f'<path d="{d}" fill="none" stroke="{P}" stroke-opacity="0.55" stroke-width="{sw}" '
                    f'stroke-linecap="round" stroke-dasharray="{dd:.4f} {gp}" stroke-dashoffset="{off:.4f}"/>')

        def label(word, cx, baseline):
            size, spacing = 56, 4
            adv = [mono.advance(ch, size) + spacing for ch in word]
            x = cx - sum(adv) / 2  # textAnchor middle (CSS letter-spacing trails each glyph)
            p = pathops.Path()
            for ch, a in zip(word, adv):
                p = pathops.op(p, mono.path(ch, x, baseline, size), pathops.PathOp.UNION)
                x += a
            return f'<path fill="{P}" d="{to_d(p)}"/>'

        WX, WW, WH, WG, WY, BW = 120, 760, 150, 20, 170, 370
        ow = 18 if small else 10
        terms = {"0,1": "FUZZ", "1,1": "COMP", "3,1": "GATE"}
        for r in range(4):
            off = -(BW + WG) / 2 if r % 2 else 0
            for c in range(3):
                x = WX + off + c * (BW + WG)
                y = WY + r * (WH + WG)
                cx = max(x, WX)
                w = min(x + BW, WX + WW) - cx
                if w < 60:
                    continue
                key, my = f"{r},{c}", y + WH / 2
                if key == "2,1":  # dials (swapped with the prompt: James, 4 Oct 2026)
                    k = 56 * math.sqrt(0.5)
                    els.append(f'<g><rect x="{cx}" y="{y}" width="{w}" height="{WH}" rx="24" fill="{P}"/>'
                               f'<circle cx="{cx + 125}" cy="{my}" r="44" fill="{Q}"/><circle cx="{cx + 245}" cy="{my}" r="44" fill="{Q}"/>'
                               f'<line x1="{cx + 125}" y1="{my}" x2="{cx + 125 - k:.4f}" y2="{my - k:.4f}" stroke="{P}" stroke-width="12" stroke-linecap="round"/>'
                               f'<line x1="{cx + 245}" y1="{my}" x2="{cx + 245}" y2="{my - 56}" stroke="{P}" stroke-width="12" stroke-linecap="round"/></g>')
                elif key == "0,0":  # faders
                    kids = [f'<rect x="{cx}" y="{y}" width="{w}" height="{WH}" rx="24" fill="{P}"/>']
                    for n, v in enumerate((0.62, 0.3, 0.78)):
                        fx, t0, tl = cx + 100 + n * 85, y + 30, WH - 60
                        kids.append(f'<rect x="{fx - 6}" y="{t0}" width="12" height="{tl}" rx="6" fill="{Q}"/>')
                        kids.append(f'<rect x="{fx - 24}" y="{t0 + tl * (1 - v) - 12:.4f}" width="48" height="24" rx="5" fill="{Q}"/>')
                    els.append("<g>" + "".join(kids) + "</g>")
                elif key == "2,0":  # terminal prompt (swapped with the dials)
                    els.append(f'<g><rect x="{cx + 5}" y="{y + 5}" width="{w - 10}" height="{WH - 10}" rx="22" fill="none" stroke="{P}" stroke-width="{ow}"/>'
                               f'<path d="M{cx + w / 2 - 70} {my - 40}l52 32 -52 32" fill="none" stroke="{P}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
                               f'<rect x="{cx + w / 2 + 2}" y="{my + 18}" width="58" height="14" rx="2" fill="{P}"/></g>')
                elif key in terms and w == BW:
                    kid = f'<rect x="{cx + 5}" y="{y + 5}" width="{w - 10}" height="{WH - 10}" rx="22" fill="none" stroke="{P}" stroke-width="{ow}"/>'
                    if small:
                        kid += block_symbol(terms[key], cx + w / 2, my, P)
                    else:
                        kid += label(terms[key], cx + w / 2, my + 20)
                    els.append("<g>" + kid + "</g>")
                else:
                    els.append(dashed(cx + 4, y + 4, w - 8, WH - 8, 22))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" role="img" aria-label="sournd">'
            + "".join(els) + "</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    for theme in WORDMARK:
        (OUT / f"sournd-wordmark-{theme}.svg").write_text(wordmark(theme))
    for lvl in ("full", "small", "tiny"):
        (OUT / f"sournd-icon-{lvl}.svg").write_text(icon(lvl))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.stat().st_size:>7}  marks/{p.name}")


if __name__ == "__main__":
    main()
