"""Prep a photo for ASCII conversion: remove bg, boost local contrast, put on white.
Usage: python scripts/prep_photo.py source-photo.jpg   -> source-prepped.png
rembg / opencv are optional; the script degrades gracefully without them."""
import sys
from PIL import Image, ImageOps
from common import ROOT

def main(path):
    img = Image.open(path).convert("RGBA")
    try:
        from rembg import remove
        img = remove(img)
        print("background removed")
    except Exception as e:
        print("skipping background removal (rembg unavailable):", type(e).__name__)
    white = Image.new("RGBA", img.size, "white")
    white.alpha_composite(img)
    gray = white.convert("L")
    try:
        import cv2, numpy as np
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = Image.fromarray(clahe.apply(np.array(gray)))
        print("CLAHE applied")
    except Exception:
        gray = ImageOps.autocontrast(gray, cutoff=2)
        print("CLAHE unavailable, used autocontrast")
    out = ROOT / "source-prepped.png"
    gray.save(out)
    print("wrote", out)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
