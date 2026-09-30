# Setup

This repository builds three profile assets: an animated ASCII rendering of `source-photo.png`, a neofetch-style card, and a contribution heatmap. The supplied `ascii-art.txt` is kept as the source artwork reference; the portrait SVG is generated from the supplied PNG.

## Configure

1. Create a **public** GitHub repository named `KevalXD` if it does not already exist. Do not initialize it with a README, license, or `.gitignore`; this local folder already has an initial commit and `origin` configured.
2. Edit `config.json` to change `username`, `display_name`, or the card rows if needed. The README and config are already personalized for KevalXD.
3. `source-photo.png` is the supplied geometric avatar. Replace it with a front-facing photo if you want a photographic ASCII portrait, then rerun the photo and portrait steps below.

## Build locally

Python 3.10 or newer is recommended.

```sh
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -r scripts/requirements.txt
python scripts/prep_photo.py source-photo.png
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

Background removal and local contrast enhancement are optional. To enable them, separately install `rembg`, `opencv-python`, and `numpy`; `prep_photo.py` falls back to autocontrast without those packages. The contribution fetch requires internet access and reads the public GitHub contributions page; it does not need a token.

When ready, push the existing `main` branch with `git push -u origin main`. That push starts the **Update profile art** workflow, which fetches the public contributions calendar and commits the heatmap data and SVG. You can also run it from the Actions tab; it runs daily as well.

The SVGs animate in a browser. Static SVG-to-PNG converters may show the initial empty frame for the heatmap and the initial state of the animated card. To render the card without animation, run `STATIC=1 python scripts/make_info_card.py` (PowerShell: `$env:STATIC='1'; python scripts/make_info_card.py`).

Adjust `ascii_columns` in `config.json` to change portrait detail. Palette colors are defined in `scripts/make_ascii_svg.py` and `scripts/render_heatmap_svg.py`.
