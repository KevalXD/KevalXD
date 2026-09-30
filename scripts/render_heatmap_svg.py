"""Render data/contributions.json as an animated 53x7 heatmap SVG (plays once, then freezes)."""
import json, datetime as dt
from common import ROOT, esc

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP, LEFT, TOP = 11, 3, 34, 30
STEP = CELL + GAP

def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = data["days"]
    nonzero = sorted(d["count"] for d in days if d["count"] > 0)
    p90 = nonzero[int(len(nonzero) * 0.9)] if nonzero else 10**9
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7     # Sunday-first rows
    weeks = (offset + len(days) + 6) // 7
    W = LEFT + weeks * STEP + 16
    H = TOP + 7 * STEP + 52
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="{data["total"]:,} contributions in the last year">',
         "<style>",
         ".c{opacity:0;animation:in .5s ease-out forwards}",
         "@keyframes in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}",
         "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;fill:#8b949e}",
         "</style>", f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>']
    for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(f'<text x="8" y="{TOP + i*STEP + 9}">{lab}</text>')
    last_month, last_label_w = None, -99
    for i, d in enumerate(days):
        w, r = divmod(i + offset, 7)
        date = dt.date.fromisoformat(d["date"])
        if date.month != last_month:
            last_month = date.month
            if w - last_label_w >= 3:            # avoid overlapping month labels
                o.append(f'<text x="{LEFT + w*STEP}" y="{TOP-10}">{date.strftime("%b")}</text>')
                last_label_w = w
        lvl = d["level"]
        if lvl >= 4 and d["count"] >= p90: lvl = 5
        o.append(f'<rect class="c" x="{LEFT + w*STEP}" y="{TOP + r*STEP}" width="{CELL}" height="{CELL}" rx="2.5" '
                 f'fill="{PALETTE[lvl]}" style="animation-delay:{(w + r) * 0.02:.2f}s">'
                 f'<title>{esc(d["date"])}: {d["count"]}</title></rect>')
    fy = TOP + 7 * STEP + 24
    o.append(f'<text x="{LEFT}" y="{fy}" style="fill:#c9d1d9;font-size:12px">{data["total"]:,} contributions in the last year'
             f' · streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>')
    lx = W - 16 - (len(PALETTE) * STEP + 62)
    o.append(f'<text x="{lx}" y="{fy}">Less</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 28 + i*STEP}" y="{fy-10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    o.append(f'<text x="{lx + 32 + len(PALETTE)*STEP}" y="{fy}">More</text></svg>')
    out = ROOT / "contrib-heatmap.svg"
    out.write_text("\n".join(o), encoding="utf-8")
    print("wrote", out)

if __name__ == "__main__":
    main()
