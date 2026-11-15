"""Generates the site's images from the Chalkmind brand mark
(tools/chalkmind_icon.py, a copy of the app repo's tool/brand/chalkmind_icon.py).

Run from the repo root:  python3 tools/generate_images.py   (needs Pillow)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageDraw, ImageFont  # noqa: E402
from chalkmind_icon import CHALK, SPARK, _gradient, render_tile  # noqa: E402

PUBLIC = os.path.join(os.path.dirname(__file__), '..', 'public')
FONT = '/usr/share/fonts/truetype/lato/Lato-Black.ttf'
FONT_REG = '/usr/share/fonts/truetype/lato/Lato-Semibold.ttf'

# Social preview image (Open Graph), 1200x630
W, H = 1200, 630
og = _gradient(W).resize((W, W)).crop((0, 285, W, 285 + H)).convert('RGBA')
og.alpha_composite(render_tile(260), (100, 120))
d = ImageDraw.Draw(og)
d.text((410, 150), 'Chalkmind', font=ImageFont.truetype(FONT, 104), fill=CHALK)
d.text((414, 290), 'The whiteboard that understands', font=ImageFont.truetype(FONT_REG, 44), fill=(209, 250, 229))
d.text((414, 346), 'your handwriting.', font=ImageFont.truetype(FONT_REG, 44), fill=(209, 250, 229))
d.text((414, 440), 'Solve maths  \u00b7  AI tutor  \u00b7  Annotate PDFs', font=ImageFont.truetype(FONT_REG, 32), fill=SPARK)
d.text((100, 540), 'chalkmind.tech', font=ImageFont.truetype(FONT_REG, 30), fill=(160, 200, 190))
og.convert('RGB').save(os.path.join(PUBLIC, 'og-image.png'), optimize=True)

render_tile(180, rounded=False).convert('RGB').save(os.path.join(PUBLIC, 'apple-touch-icon.png'), optimize=True)
render_tile(48).save(os.path.join(PUBLIC, 'favicon-48.png'), optimize=True)
print('Site images generated in public/.')
