"""Render data/contributions.json as a gold-on-midnight 53x7 heatmap SVG.

Motion (all plain SVG/CSS, so it also plays inside a GitHub README <img>):
  * cells drop in as a diagonal wave, once
  * a soft gold light sweeps across the grid on a loop
  * active cells "pop" as the light passes over them
  * your best day wears a pulsing ring

STATIC=1 emits a frozen frame (for PNG previews / converters that ignore animation).
"""
import json, os, datetime as dt
from common import ROOT, esc

# empty -> peak. Level 5 is the glow reserved for the top 10% of days.
PALETTE = ["#161C2E", "#4B4020", "#7A6524", "#B8962E", "#D4AF37", "#F5D77A"]
BG, BORDER = "#0B0F1A", "#1B2236"
TEXT, TEXT_STRONG, RING = "#8E93A6", "#E8E4D8", "#F5D77A"
CELL, GAP, LEFT, TOP = 11, 3, 34, 30
STEP = CELL + GAP
SWEEP_BEGIN, SWEEP_PERIOD, SWEEP_TRAVEL, SWEEP_W = 2.2, 7.0, 4.2, 120


def main():
    static = os.environ.get("STATIC") == "1"
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = data["days"]
    nonzero = sorted(d["count"] for d in days if d["count"] > 0)
    p90 = nonzero[int(len(nonzero) * 0.9)] if nonzero else 10**9
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7          # Sunday-first rows
    weeks = (offset + len(days) + 6) // 7
    grid_w = weeks * STEP
    W = LEFT + grid_w + 16
    H = TOP + 7 * STEP + 70
    best = data["best_day"]

    css = ["text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;fill:%s}" % TEXT]
    if not static:
        css += [
            ".c{opacity:0;animation:in .5s ease-out forwards}",
            "@keyframes in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}",
            ".a{transform-box:fill-box;transform-origin:center}",
            "@keyframes pop{0%{transform:scale(1)}5%{transform:scale(1.5)}14%{transform:scale(1)}100%{transform:scale(1)}}",
            "@media (prefers-reduced-motion:reduce){.c,.a{animation:none;opacity:1}.s{display:none}}",
        ]

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="{data["total"]:,} contributions in the last year">',
         "<style>" + "".join(css) + "</style>",
         "<defs>"
         f'<linearGradient id="sw" x1="0" x2="1" y1="0" y2="0">'
         f'<stop offset="0" stop-color="{RING}" stop-opacity="0"/>'
         f'<stop offset="0.5" stop-color="{RING}" stop-opacity="0.18"/>'
         f'<stop offset="1" stop-color="{RING}" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="grid"><rect x="{LEFT-2}" y="{TOP-2}" width="{grid_w+2}" height="{7*STEP+2}"/></clipPath>'
         "</defs>",
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>']

    for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(f'<text x="8" y="{TOP + i*STEP + 9}">{lab}</text>')

    last_month, last_label_w = None, -99
    best_xy = None
    for i, d in enumerate(days):
        w, r = divmod(i + offset, 7)
        date = dt.date.fromisoformat(d["date"])
        if date.month != last_month:
            last_month = date.month
            if w - last_label_w >= 3:            # avoid overlapping month labels
                o.append(f'<text x="{LEFT + w*STEP}" y="{TOP-10}">{date.strftime("%b")}</text>')
                last_label_w = w
        lvl = d["level"]
        if lvl >= 4 and d["count"] >= p90:
            lvl = 5
        x, y = LEFT + w * STEP, TOP + r * STEP
        if d["date"] == best["date"] and best["count"] > 0:
            best_xy = (x, y)
        cls, style = "c", f"animation-delay:{(w + r) * 0.02:.2f}s"
        if static:
            cls, style = "", ""
        elif lvl >= 1:
            # pop timing is locked to when the sweep reaches this column
            t_hit = (x + CELL / 2 - LEFT + SWEEP_W / 2) / (grid_w + SWEEP_W) * SWEEP_TRAVEL
            pop_delay = max(0.0, SWEEP_BEGIN + t_hit - 0.35)
            cls = "c a"
            style = (f"animation:in .5s ease-out {(w + r) * 0.02:.2f}s forwards,"
                     f"pop {SWEEP_PERIOD}s linear {pop_delay:.2f}s infinite")
        attrs = f' class="{cls}"' if cls else ""
        attrs += f' style="{style}"' if style else ""
        o.append(f'<rect{attrs} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[lvl]}">'
                 f'<title>{esc(d["date"])}: {d["count"]}</title></rect>')

    if best_xy and not static:
        bx, by = best_xy
        o.append(f'<rect x="{bx-2}" y="{by-2}" width="{CELL+4}" height="{CELL+4}" rx="4" fill="none" stroke="{RING}" stroke-width="1.2">'
                 f'<animate attributeName="stroke-opacity" values="1;0.15;1" dur="2.4s" begin="1.5s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-width" values="1.2;2.4;1.2" dur="2.4s" begin="1.5s" repeatCount="indefinite"/></rect>')
    elif best_xy:
        bx, by = best_xy
        o.append(f'<rect x="{bx-2}" y="{by-2}" width="{CELL+4}" height="{CELL+4}" rx="4" fill="none" stroke="{RING}" stroke-width="1.5"/>')

    if not static:
        end_x = LEFT + grid_w
        o.append(f'<g class="s" clip-path="url(#grid)" pointer-events="none">'
                 f'<rect x="0" y="{TOP-2}" width="{SWEEP_W}" height="{7*STEP+2}" fill="url(#sw)" transform="translate({LEFT-SWEEP_W} 0)">'
                 f'<animateTransform attributeName="transform" type="translate" '
                 f'values="{LEFT-SWEEP_W} 0;{end_x} 0;{end_x} 0" keyTimes="0;{SWEEP_TRAVEL/SWEEP_PERIOD:.3f};1" '
                 f'dur="{SWEEP_PERIOD}s" begin="{SWEEP_BEGIN}s" repeatCount="indefinite"/></rect></g>')

    fy = TOP + 7 * STEP + 24
    o.append(f'<text x="{LEFT}" y="{fy}" style="fill:{TEXT_STRONG};font-size:12px">{data["total"]:,} contributions in the last year'
             f' · streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>')
    if best["count"] > 0:
        bd = dt.date.fromisoformat(best["date"]).strftime("%b %d").replace(" 0", " ")
        o.append(f'<text x="{LEFT}" y="{fy+20}" style="fill:{RING}">peak day: {best["count"]} contributions on {bd}</text>')
    lx = W - 16 - (len(PALETTE) * STEP + 62)
    o.append(f'<text x="{lx}" y="{fy}">Less</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 28 + i*STEP}" y="{fy-10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    o.append(f'<text x="{lx + 32 + len(PALETTE)*STEP}" y="{fy}">More</text></svg>')

    out = ROOT / ("contrib-heatmap-static.svg" if static else "contrib-heatmap.svg")
    out.write_text("\n".join(o), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
