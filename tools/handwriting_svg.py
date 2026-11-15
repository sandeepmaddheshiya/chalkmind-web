"""SVG paths in Chalkmind's own handwriting style.

Glyphs are ported from the Chalkmind app's
lib/features/whiteboard/recognition/handwriting_stroke_generator.dart (same curves, same 0.14 forward slant),
so the landing page shows exactly how the app writes answers.
Coordinates: units of letter height; y=0 top, y=1 baseline.
"""

SLANT = 0.14
GAP = 0.11

# Each glyph: (advance, [path commands]); a command is (op, *points)
G = {
    ' ': (0.32, []),
    '1': (0.36, [[('M', .04, .22), ('Q', .18, .12, .26, 0), ('L', .26, 1)]]),
    '2': (0.56, [[('M', .04, .22), ('C', .08, .02, .48, -.06, .50, .24), ('C', .52, .46, .22, .70, .02, 1), ('Q', .30, .97, .56, 1)]]),
    '3': (0.54, [[('M', .04, .12), ('C', .18, -.04, .50, -.02, .48, .22), ('C', .46, .40, .30, .46, .18, .46),
                  ('C', .44, .46, .54, .62, .52, .76), ('C', .50, 1.02, .14, 1.06, .02, .86)]]),
    '4': (0.58, [[('M', .40, 0), ('L', .03, .66), ('L', .56, .66)], [('M', .42, .30), ('L', .42, 1)]]),
    '5': (0.54, [[('M', .12, .02), ('L', .08, .44), ('C', .26, .32, .54, .38, .53, .68), ('C', .52, .98, .16, 1.04, .02, .86)],
                 [('M', .12, .02), ('L', .50, 0)]]),
    '6': (0.56, [[('M', .46, .04), ('C', .20, .10, .04, .40, .04, .66), ('C', .04, .90, .16, 1, .30, 1),
                  ('C', .46, 1, .54, .88, .54, .74), ('C', .54, .58, .42, .48, .28, .48), ('C', .16, .48, .06, .56, .05, .68)]]),
    '8': (0.56, [[('M', .46, .14), ('C', .42, 0, .08, -.01, .08, .22), ('C', .08, .38, .26, .42, .30, .46),
                  ('C', .48, .52, .56, .64, .54, .78), ('C', .52, 1.01, .04, 1.02, .04, .76),
                  ('C', .04, .60, .20, .52, .30, .46), ('C', .40, .40, .50, .32, .46, .14)]]),
    '+': (0.52, [[('M', .26, .34), ('L', .25, .84)], [('M', .02, .60), ('Q', .26, .58, .50, .59)]]),
    '-': (0.44, [[('M', .03, .60), ('Q', .22, .58, .42, .59)]]),
    '=': (0.50, [[('M', .03, .48), ('Q', .25, .46, .48, .47)], [('M', .03, .70), ('Q', .25, .68, .48, .69)]]),
    'x': (0.48, [[('M', .04, .46), ('C', .18, .46, .30, 1, .46, 1)], [('M', .44, .46), ('L', .04, 1)]]),
    'y': (0.48, [[('M', .04, .46), ('C', .04, .82, .14, .92, .24, .92), ('C', .36, .92, .44, .80, .44, .46),
                  ('L', .44, 1.12), ('C', .44, 1.36, .18, 1.40, .06, 1.24)]]),
}


def strokes(text, x0, y0, h):
    """List of SVG 'd' strings (one per pen stroke) for [text]."""
    out, pen = [], 0.0
    for ch in text:
        adv, paths = G[ch]
        for p in paths:
            d = []
            for op, *pts in p:
                coords = []
                for i in range(0, len(pts), 2):
                    u, v = pts[i], pts[i + 1]
                    u = u + (1 - v) * SLANT  # forward slant (shear keeps curves exact)
                    coords.append(f"{x0 + (pen + u) * h:.1f} {y0 + v * h:.1f}")
                d.append(op + ' ' + ' '.join(coords))
            out.append(' '.join(d))
        pen += adv + GAP
    return out


def width(text, h):
    return sum(G[c][0] + GAP for c in text) * h


if __name__ == '__main__':
    import json
    print(json.dumps({
        'problem': strokes('2x + 6 = 14', 0, 0, 48),
        'answer': strokes('x = 4', 0, 0, 48),
    }, indent=1)[:600])
