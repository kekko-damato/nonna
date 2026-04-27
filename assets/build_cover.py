"""Generate the Nonna social preview cover.

Reads `assets/cover-raw.png` (the GPT-generated illustration), overlays the
"Nonna" wordmark, tagline, and repo URL on the empty right third, and writes
`assets/cover.png` as a 1280x640 PNG ready for upload to GitHub social preview.

Usage:
    python3 assets/build_cover.py

Requirements: Pillow (`pip install pillow` if missing).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent
INPUT = ASSETS / "cover-raw.png"
OUTPUT = ASSETS / "cover.png"

# macOS system font paths (.ttc = TrueType collection, multiple weights inside)
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"

# Color palette (RGBA tuples)
CREAM = (245, 239, 230, 255)
CREAM_MUTED = (245, 239, 230, 210)
URL_COLOR = (200, 169, 104, 200)

TARGET = (1280, 640)  # GitHub social preview spec
TEXT_LEFT = 880       # start of text column (right third)
RIGHT_MARGIN = 50

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing {INPUT}. Save the GPT-generated illustration to that path first."
    )

# Load + crop/resize to 1280x640 (center-crop if aspect ratio differs)
img = Image.open(INPUT).convert("RGBA")
W, H = img.size
target_ratio = TARGET[0] / TARGET[1]
img_ratio = W / H

if abs(img_ratio - target_ratio) < 0.01:
    img = img.resize(TARGET, Image.LANCZOS)
elif img_ratio > target_ratio:
    new_W = int(H * target_ratio)
    left = (W - new_W) // 2
    img = img.crop((left, 0, left + new_W, H)).resize(TARGET, Image.LANCZOS)
else:
    new_H = int(W / target_ratio)
    top = (H - new_H) // 2
    img = img.crop((0, top, W, top + new_H)).resize(TARGET, Image.LANCZOS)

overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)


def load_font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size, index=index)
    except (OSError, IndexError):
        return ImageFont.truetype(path, size)


# Wordmark "Nonna" — Didot Bold 110pt, cream
wordmark_font = load_font(DIDOT, 110, index=2)
draw.text((TEXT_LEFT, 195), "Nonna", font=wordmark_font, fill=CREAM)

# Tagline — Helvetica Neue Light 24pt, slightly muted cream, two lines
tagline_font = load_font(HELVETICA, 24, index=2)
draw.text((TEXT_LEFT + 4, 360), "tells you the truth", font=tagline_font, fill=CREAM_MUTED)
draw.text((TEXT_LEFT + 4, 394), "because she loves you", font=tagline_font, fill=CREAM_MUTED)

# Repo URL — bottom-right, Helvetica Neue 14pt, gold-muted
url_font = load_font(HELVETICA, 14)
url_text = "github.com/kekko-damato/nonna"
url_bbox = draw.textbbox((0, 0), url_text, font=url_font)
url_width = url_bbox[2] - url_bbox[0]
draw.text(
    (TARGET[0] - url_width - RIGHT_MARGIN, 605),
    url_text,
    font=url_font,
    fill=URL_COLOR,
)

result = Image.alpha_composite(img, overlay).convert("RGB")
result.save(OUTPUT, "PNG", optimize=True)
print(f"Saved {OUTPUT}: {result.size[0]}x{result.size[1]}")
