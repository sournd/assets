# sournd — brand pack

The brand pack is `sournd Brand Pack.dc.html`: idea, wordmark, icon, colour, type. That is the deliverable, with `sournd UI Kit.dc.html` as its companion: forms, selects, menus, tabs, cards, tables, badges, alerts, toasts, modal, tooltip, popover, progress, empty states, nav, audio controls and Lucide icons — each in light and dark. `sournd Brand.dc.html` and `sournd Directions (archive).dc.html` are earlier working files kept for reference only; don't extend them.

## Decisions (owner's words, 4 Oct 2026)
- Positioning, visual idea, tone (warm, direct, confident) and tagline ("Making what you need to make music") are written on the pack cover — use verbatim.
- Wordmark: sOURnd, Bricolage Grotesque Bold, one weight. O knob pointer, U fader, R jack leg. Real cut-throughs. Running text: "sournd". Component: `SourndMark.dc.html`.
- Logo colour: two petrols. Light: s/nd #0E7482, OUR #3A97A3. Dark: s/nd #3A97A3, OUR #6BBCC6. No accent in the logo.
- Icon: the Bricks tile — paper #F3F0EA bricks on light petrol #3A97A3, same tile in light and dark. Dashed empty slots, FUZZ/COMP/GATE outlined, faders block, dials block, terminal prompt. Cuts: full / small (no words) / tiny (one slot). Component: `SourndAppIcon.dc.html` (earlier U and O versions: `SourndAppIconU`, `SourndAppIconO`).
- Palette: Paper #F3F0EA, Ink #1D2226, Night #141A1C, Chalk #EDF0EE. Light petrol #3A97A3 (dark #6BBCC6) is THE primary accent — buttons, links, selection, focus, icon tile — with paper text on it (3.0:1 — owner accepts, below AA; use 500 weight ≥15px). Paper text on raspberry too; ink text on amber, and ink on the dark-mode primary #6BBCC6. Raspberry is the secondary accent; Chalk is dark-mode text only. Deep petrol #0E7482 is logo-only; #0F5C68 is retired. Raspberry #9E1F4A (dark #E0577F) controls only. Amber #F4A340 (text on light #9A4A0B) highlights.
- Type: Bricolage Grotesque 700 only, normal tracking, for wordmark/display/headings. Instrument Sans 400 body / 500 UI / 600 labels and values (tabular figures) for everything else. No monospace anywhere — owner's call.

- UI kit rules: 6px radius on controls/inputs, 10px cards, 12px modals. 40px inputs, 44px primary actions, 32px small, 28px chips. 1px #7F868A control borders, #D9D5CC dividers (dark #6F7B7E / #283235). Focus: 2px ring, 3px offset. Status is always a symbol and a word. Icons: Lucide, 2px stroke. Knob pointers, fader thumbs and playhead are raspberry.

## Conventions
- Keep the pack to design: no status chips, product screens, platform or business items.
- `reference/` holds screenshots of earlier rounds and inspiration images.
