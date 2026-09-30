"""Hand-authored neofetch-style info card. STATIC=1 emits a frozen frame for previews."""
import os, textwrap
from common import ROOT, load_config, esc

BG, BAR, FG, KEY, ACC = "#0d1117", "#161b22", "#c9d1d9", "#39d353", "#58a6ff"
W, LH, PADX, KEYW, WRAP = 490, 22, 22, 104, 38

def main():
    cfg = load_config()
    static = os.environ.get("STATIC") == "1"
    host = f'{cfg["username"]}@{cfg.get("host", "github")}'
    lines = [("t", host, ""), ("t", "-" * len(host), "")]
    for k, v in cfg["card"].items():
        for i, w in enumerate(textwrap.wrap(v, WRAP) or [""]):
            lines.append(("kv", k if i == 0 else "", w))
    H = 74 + len(lines) * LH + 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="info card">',
           "<style>",
           ".l{opacity:1}" if static else ".l{opacity:0;animation:in .45s ease-out forwards}",
           "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}",
           "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}",
           "</style>",
           f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
           f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v26H0z" fill="{BAR}"/>',
           '<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="38" cy="18" r="5" fill="#ffbd2e"/><circle cx="56" cy="18" r="5" fill="#27c93f"/>',
           f'<text x="{W/2}" y="22" text-anchor="middle" fill="#8b949e">~ neofetch</text>',
           f'<text x="{PADX}" y="58" fill="{ACC}" class="l" style="animation-delay:.1s">$ neofetch</text>']
    for i, (kind, a, b) in enumerate(lines):
        yy = 74 + (i + 1) * LH
        d = f'style="animation-delay:{0.3 + i*0.12:.2f}s"'
        if kind == "t":
            out.append(f'<text x="{PADX}" y="{yy}" fill="{ACC if i == 0 else "#484f58"}" class="l" {d}>{esc(a)}</text>')
        else:
            out.append(f'<text x="{PADX}" y="{yy}" class="l" {d}><tspan fill="{KEY}" font-weight="bold">{esc(a)}</tspan>'
                       f'<tspan x="{PADX+KEYW}" fill="{FG}">{esc(b)}</tspan></text>')
    out.append("</svg>")
    p = ROOT / "info-card.svg"
    p.write_text("\n".join(out), encoding="utf-8")
    print("wrote", p)

if __name__ == "__main__":
    main()
