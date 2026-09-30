"""Convert source-prepped.png into a monochrome ASCII SVG that types itself in row by row."""
import sys
from PIL import Image
from common import ROOT, load_config, esc

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
CW, CH, FS = 6.0, 10.0, 10   # char cell width/height, font size
FG, BG = "#c9d1d9", "#0d1117"
ROW_DUR, STAGGER = 0.5, 0.07

def main():
    cfg = load_config()
    src = ROOT / "source-prepped.png"
    if not src.exists():
        sys.exit("source-prepped.png not found - run scripts/prep_photo.py first")
    img = Image.open(src).convert("L")
    cols = int(cfg.get("ascii_columns", 100))
    rows = max(1, round(cols * img.height / img.width * (CW / CH)))
    img = img.resize((cols, rows), Image.LANCZOS)
    px = img.load()
    n = len(RAMP) - 1
    W, H = cols * CW, rows * CH
    pad = 14
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W+2*pad:.0f} {H+2*pad:.0f}" '
             f'width="{W+2*pad:.0f}" height="{H+2*pad:.0f}" role="img" aria-label="ASCII portrait">',
             f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>']
    defs, body = ["<defs>"], []
    for r in range(rows):
        # bright pixel -> sparse glyph (index 0), dark pixel -> dense glyph
        line = "".join(RAMP[int((1 - px[c, r] / 255) * n + 0.5)] for c in range(cols))
        begin = f"{r*STAGGER:.2f}s"
        y = pad + (r + 1) * CH - 2
        defs.append(f'<clipPath id="r{r}"><rect x="{pad}" y="{pad+r*CH:.1f}" width="0" height="{CH}">'
                    f'<animate attributeName="width" from="0" to="{W:.0f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
                    f'</rect></clipPath>')
        if line.strip():
            body.append(f'<text x="{pad}" y="{y:.1f}" textLength="{W:.0f}" lengthAdjust="spacing" '
                        f'xml:space="preserve" clip-path="url(#r{r})">{esc(line)}</text>')
            body.append(f'<rect x="{pad}" y="{pad+r*CH+1:.1f}" width="{CW}" height="{CH-2}" opacity="0">'
                        f'<animate attributeName="x" from="{pad}" to="{pad+W:.0f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
                        f'<set attributeName="opacity" to="0.9" begin="{begin}"/>'
                        f'<set attributeName="opacity" to="0" begin="{r*STAGGER+ROW_DUR:.2f}s"/></rect>')
    defs.append("</defs>")
    parts += defs
    parts.append(f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}" fill="{FG}">')
    parts += body + ["</g></svg>"]
    out = ROOT / "ascii-portrait.svg"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out} ({cols}x{rows} chars)")

if __name__ == "__main__":
    main()
