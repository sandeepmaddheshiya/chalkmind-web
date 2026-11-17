"""Builds public/index.html from tools/index.template.html. Handwriting in the
illustrations comes from the app's own glyphs (tools/handwriting_svg.py).
Run from the repo root:  python3 tools/build_index.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from handwriting_svg import strokes, width
import site_parts as sp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOGO = open(os.path.join(ROOT, 'public', 'favicon.svg')).read().strip().replace(
    '<svg xmlns="http://www.w3.org/2000/svg"', '<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"').replace('id="g"', 'id="lg"').replace('url(#g)', 'url(#lg)')


def paths(ds, cls, start, step):
    out, t = [], start
    for d in ds:
        out.append(f'<path class="{cls} draw" pathLength="1" style="--d:{t:.2f}s" d="{d}"/>')
        t += step
    return '\n      '.join(out), t


# --- Hero board: "2x + 6 = 14" then the answer "x = 4" in yellow ---
p_ds = strokes('2x + 6 = 14', 36, 46, 54)
problem, t = paths(p_ds, 'chalk', 0.35, 0.26)
pill_t = t + 0.35
a_ds = strokes('x = 4', 36, 178, 54)
answer, t2 = paths(a_ds, 'chalk answer', pill_t + 0.75, 0.28)
note_t = t2 + 0.3

hero_svg = f'''<svg viewBox="0 0 520 360" role="img" aria-labelledby="board-title board-desc">
      <title id="board-title">Chalkmind solving a handwritten equation</title>
      <desc id="board-desc">The equation 2x + 6 = 14 is written by hand. Chalkmind offers the answer and writes x = 4 in yellow, with two short working steps.</desc>
      {problem}
      <g class="board-pill fade" style="--d:{pill_t:.2f}s">
        <rect x="36" y="122" width="268" height="38" rx="19"/>
        <text x="54" y="147">✓ x = 4   ·   Write answer   ·   Steps</text>
      </g>
      {answer}
      <g class="board-note fade" style="--d:{note_t:.2f}s">
        <text class="h" x="36" y="282">STEPS</text>
        <text x="36" y="308">1.  2x = 14 − 6 = 8</text>
        <text x="36" y="334">2.  x = 8 ÷ 2 = 4</text>
      </g>
    </svg>'''

# --- Geometry example: right triangle 3, 4, x = 5 ---
tri = '<path class="chalk" d="M70 230 L70 70 L280 230 Z"/><path class="chalk" d="M70 206 L94 206 L94 230" style="stroke-width:2.4"/>'
lab3 = ' '.join(f'<path class="chalk" d="{d}"/>' for d in strokes('3', 34, 132, 34))
lab4 = ' '.join(f'<path class="chalk" d="{d}"/>' for d in strokes('4', 162, 246, 34))
labx = ' '.join(f'<path class="chalk" d="{d}"/>' for d in strokes('x =', 196, 118, 34))
lab5 = ' '.join(f'<path class="chalk answer" d="{d}"/>' for d in strokes('5', 262, 118, 34))
geo_svg = f'''<svg viewBox="0 0 340 300" role="img" aria-label="A right triangle with sides 3 and 4. Chalkmind answers x = 5 in yellow.">
        {tri}{lab3}{lab4}{labx}{lab5}
      </svg>'''

html = open(os.path.join(os.path.dirname(__file__), 'index.template.html')).read()
html = html.replace('{{LOGO}}', LOGO).replace('{{HERO_BOARD}}', hero_svg).replace('{{GEOMETRY}}', geo_svg)
html = (html.replace('{{HEADER}}', sp.header()).replace('{{FOOTER}}', sp.footer())
        .replace('{{JOIN}}', sp.join_section('Be one of the first to use Chalkmind',
                 'Chalkmind is in testing before its Google Play launch. Join the early-access list and we’ll '
                 'email you an install link when it’s your turn. One email, no spam.'))
        .replace('{{CTA_HREF}}', sp.cta_href()).replace('{{CTA_LABEL}}', sp.cta_label()))
assert '{{' not in html, 'unfilled placeholder in index template'

open(os.path.join(ROOT, 'public', 'index.html'), 'w').write(html)
print('public/index.html written:', len(html.encode()), 'bytes; problem width', round(width('2x + 6 = 14', 54)))
